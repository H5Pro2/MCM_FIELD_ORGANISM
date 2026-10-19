"""Private restart-aware player with explicit selected-file admission."""
from dataclasses import asdict
import json
from pathlib import Path
import threading

from tools import _s2oe_local_player as old
from tools import _media_restart_checkpoint as checkpoint
from tools import _media_restart_work as work
from tools import _media_restart_admission as admission_rules

VERSION = "media.restart-player.v1"


class Player(old.Player):
    def __init__(self, binding, store, *, selected_checkpoint=None):
        super().__init__(binding)
        self.store, self.selected_checkpoint = store, selected_checkpoint
        self.state.update(phase="READY_NEUTRAL_ONLY" if binding.mode == admission_rules.NEUTRAL
                          else "REAL_AUTHORIZATION_REQUIRED", origin=None, checkpoint=None,
                          next_ordinal=1, storage_status="NOT_SAVED")

    def _authorize(self):
        work.require(checkpoint.QUALIFIED, "RESTART_PLAYER_NOT_ADMITTED")
        admission_rules.validate(self.binding.manifest, self.binding.mode,
                                 getattr(self.binding, "admission", None))
        work.require(not self.binding.output.exists(), "RESTART_PLAYER_OUTPUT_USED")
        self.store.publish(self.binding.claim, dict(version=VERSION, manifest=self.binding.manifest.manifest_digest,
            checkpoint=None if self.selected_checkpoint is None else str(self.selected_checkpoint), uses=1))

    def _open_session(self):
        checkpoint.MAIN_GATE = True
        try:
            return checkpoint.Session(self.binding.manifest, self.binding.output, self.store,
                                      checkpoint=self.selected_checkpoint, mode=self.binding.mode,
                                      admission=getattr(self.binding, "admission", None))
        finally:
            checkpoint.MAIN_GATE = False

    def _run(self):
        try:
            self.session = self._open_session()
            with self.lock:
                self.state["origin"] = self.session.origin
                self.state["completed"] = len(self.session.runtime.rows)
            while len(self.session.runtime.rows) < len(self.binding.manifest.events):
                if self.stop_event.is_set():
                    break
                raw = self.session.next()
                row = json.loads(raw)
                shown = old.projection(checkpoint.b.canonical(row["step"]))
                with self.lock:
                    n = len(self.session.runtime.rows)
                    self.state.update(completed=n, next_ordinal=n+1, last=shown,
                        runtime_snapshot=asdict(self.session.runtime.subject.snapshot()))
                self._after_event()
            if len(self.session.runtime.rows) == len(self.binding.manifest.events):
                self.session.close()
                self.state.update(phase="RECORDING_COMPLETE", closure_cause="COMPLETED")
            else:
                self.session.suspend()
                self.state.update(phase="SUSPENDED", checkpoint=self.session.saved,
                                  storage_status="SAVED_AND_CHECKED", closure_cause="ORDERLY_SUSPEND")
        except Exception as exc:
            primary = None if self.session is None else self.session.failure
            self.state.update(phase="NOT_EVALUABLE", error=(primary["code"] if primary else getattr(exc, "code", type(exc).__name__)),
                              storage_status="NOT_SAVED", closure_cause="TECHNICAL_ERROR")
            if self.session is not None and not self.session.closed:
                try:
                    self.session.fail(exc)
                except Exception as secondary:
                    self.state["closure_error"] = type(secondary).__name__
        finally:
            checkpoint.MAIN_GATE = False
            # A session failure is the sole authoritative error closure. Do not
            # spend its reserved space on a second player publication.
            if self.binding.output.exists() and not (self.session and self.session.failure):
                try:
                    closed_phase = self.session.phase
                    self.session.phase = "PLAYER_CLOSE"
                    self.session.publish(self.binding.output/"player-close.json", dict(self.state, gate=False))
                    self.session.phase = closed_phase
                except Exception as exc:
                    self.state.update(phase="NOT_EVALUABLE", error=getattr(exc, "code", type(exc).__name__),
                                      closure_cause="TECHNICAL_ERROR")
                    self.session.fail(exc)

    def stop(self, reason="USER_STOP"):
        work.require(reason in ("USER_STOP", "SERVER_SHUTDOWN"), "RESTART_STOP_REASON")
        work.require(self.session is None or self.session.restarts == 0 or self.session.closed,
                     "MEDIA_SECOND_RESTART")
        self.stop_event.set()
        if self.thread is not None and self.thread is not threading.current_thread():
            self.thread.join(old.m.oc.STOP_SECONDS + 60 if hasattr(old.m.oc, "STOP_SECONDS") else 65)
            work.require(not self.thread.is_alive(), "RESTART_BOUNDARY_WAIT_TIMEOUT")
        return self.status()


def verify_comparison(store, manifest, reference, saved, restored, *,
        scope="Neutral endpoints; no proof of arbitrary codec batch size or internal work cap."):
    """Read-only native validation and equality. No decoder or state advance."""
    store.verify_budget_profile()
    if store.profile is not None:
        work.require(not store.budget()["violations"], "RESTART_VERIFICATION_BUDGET")
    claim = store.root/(restored+"-verification.claim")
    store.publish(claim, dict(uses=1, manifest=manifest.manifest_digest))
    a = store.read(store.root/reference/"record.json")
    cut = store.read(store.root/saved/"checkpoint.json")
    b = store.read(store.root/restored/"record.json")
    checkpoint.validate(cut, manifest)
    work.require(a["status"] == b["status"] == "RECORDING_COMPLETE"
                 and b["origin"] == cut["checkpoint_digest"], "RESTART_TOTAL_BINDING")
    config = checkpoint.r.nn.profile.build_config()
    for row in (a, b):
        checkpoint.c.verify.verify_core(row["core"], config, manifest)
        checkpoint.account_validate(row["accounting"], manifest, 20)
        work.require(row["ends"]["video_eof"] and row["ends"]["audio_eof"], "RESTART_EOF")
    work.require(b["accounting"]["work"]["prior"] == cut["accounting"]["work"]["totals"], "RESTART_PRIOR_LOST")
    work.require(b["process_id"] != cut["process_id"], "RESTART_PROCESS_NOT_CHANGED")
    replay_proofs = [store.read(store.root/restored/("replay-%02d.json" % n))
                     for n in range(cut["next_ordinal"])]
    work.replay.verify(replay_proofs, manifest.source, cut["next_ordinal"]-1,
        cut["accounting"]["work"]["totals"], b["accounting"]["work"], b["replay"])
    rows = []
    for ordinal, (left, right) in enumerate(zip(a["core"]["rows"], b["core"]["rows"], strict=True), 1):
        rows.append(dict(ordinal=ordinal, equal=checkpoint.b.canonical(left) == checkpoint.b.canonical(right)))
    result = checkpoint.b.sealed(dict(status="RECORDING_COMPLETE", evaluation_allowed=True,
        core_equal=checkpoint.b.canonical(a["core"]) == checkpoint.b.canonical(b["core"]),
        selections_equal=a["selections"] == b["selections"], rows=rows,
        final_field_equal=checkpoint.b.canonical(a["field"]) == checkpoint.b.canonical(b["field"]),
        replay_confirmations=len(replay_proofs), replay_verified=True,
        read_only=True, sources_reused=True,
        scope=scope), "verification_digest")
    store.publish(store.root/(restored+"-verification.json"), result)
    return result
