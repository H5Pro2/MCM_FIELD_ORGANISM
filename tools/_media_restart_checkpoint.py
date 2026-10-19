"""Private full-file checkpoint boundary with explicit selected-file admission."""
from dataclasses import asdict
import json
import os
from pathlib import Path
from threading import Event, Lock

from tools import _memory_checkpoint as c
from tools import _s2oe_media_session as media
from tools import _media_restart_work as work
from tools import _media_restart_admission as admission_rules

VERSION = "media.system-checkpoint.v3-window-replay"
MAIN_GATE = False
QUALIFIED = False
b, r, p = c.b, c.r, media.p
require = work.require


def account_validate(value, manifest, completed):
    require(set(value) == {"version", "completed", "materializer", "work", "restarts"}
            and value["version"] == work.VERSION and value["completed"] == completed
            and type(value["restarts"]) is int and value["restarts"] in (0, 1), "MEDIA_ACCOUNT_FORM")
    require(value["materializer"] == dict(payloads=2*completed, audio=completed,
            nj=completed, visual=completed, materialized_events=completed), "MEDIA_ACCOUNT_POSITION")
    v = value["work"]
    require(set(v) == {"version", "prior", "parts", "totals", "limits", "frame_evidence_complete", "frame_limits"}
            and v["version"] == work.VERSION and v["limits"] == work.limits(manifest.source.size)
            and set(v["parts"]) == {"regular", "replay"}
            and v["frame_evidence_complete"] is True
            and v["frame_limits"] == "POST_BATCH_ABORT_NOT_INTERNAL_WORK_MAXIMUM", "MEDIA_WORK_FORM")
    for row in (v["prior"], v["totals"], *v["parts"].values()):
        require(set(row) == set(work.KEYS) and all(type(x) is int and x >= 0 for x in row.values()),
                "MEDIA_WORK_FORM")
    require(all(v["totals"][k] == v["prior"][k] + sum(x[k] for x in v["parts"].values())
                and v["totals"][k] <= v["limits"][k] for k in work.KEYS), "MEDIA_WORK_TOTAL")
    require(value["restarts"] != 0 or (v["prior"] == work.empty()
            and v["parts"]["replay"] == work.empty()), "MEDIA_WORK_INITIAL")


def validate(value, manifest):
    """Native reconstruction and independent prefix verification, without media IO."""
    try:
        p.validate(manifest)
        require(manifest.schema == p.FULL_VERSION, "MEDIA_RESTORE_MODE")
        require(set(value) == {"schema", "manifest", "code_digest", "process_id", "next_ordinal",
                "stream", "field", "field_wrapper", "prefix", "births", "chain", "accounting",
                "selections", "main_gate", "checkpoint_digest"}, "MEDIA_CHECKPOINT_FORM")
        require(value == c.seal({k: v for k, v in value.items() if k != "checkpoint_digest"}),
                "MEDIA_CHECKPOINT_DIGEST")
        require(value["schema"] == VERSION and value["main_gate"] is False
                and value["manifest"] == c.copy_json(asdict(manifest))
                and value["code_digest"] == manifest.code_digest, "MEDIA_CHECKPOINT_BINDING")
        c.checked_size(value, c.TOTAL_CAP, "checkpoint_file")
        c.validate_field_form(value["field"])
        c.checked_size(value["field"], c.FIELD_CAP, "FIELD_CHECKPOINT.v1")
        prefix = value["prefix"]
        n = len(prefix["rows"])
        require(0 < n < len(manifest.events) and value["next_ordinal"] == n+1
                and len(value["selections"]) == n, "MEDIA_CHECKPOINT_POSITION")
        config = r.nn.profile.build_config()
        proof = c.verify.verify_core(prefix, config, manifest)
        require(proof["evaluation_allowed"], "MEDIA_CHECKPOINT_PREFIX")
        for event, selection, source in zip(manifest.events[:n], value["selections"],
                                             prefix["source_receipts"], strict=True):
            expected = p.selection_receipt(manifest, event, selection["frame_pts"],
                selection["next_frame_pts"], source["nj"]["pcm_digest"], source["rgb_digest"])
            require(selection == expected, "MEDIA_CHECKPOINT_SELECTION")
        row = prefix["rows"][-1]
        memory = c.verify.fv.old.decode_state(b.state_wire.decode(prefix["states"][row["memory"]]), config)
        snapshot = c.SharedMCMFieldSnapshot.from_json(b.canonical(value["field"]))
        field = r.ng.field._field_state(c.restore_shared_mcm_field(snapshot),
            value["field_wrapper"]["last_end_tick"], value["field_wrapper"]["step_count"])
        require(r.ng.field_record(field) == value["field_wrapper"] == row["field"], "MEDIA_CHECKPOINT_FIELD")
        stream = r.ng.stream.PerceptionStreamStateV1(**value["stream"], memory_state=memory, field_state=field)
        r.ng.stream._validate_stream_state(stream)
        require(stream.status == "OPEN" and stream.stream_id == manifest.run_id
                and stream.next_ordinal == n+1 and stream.processed_event_count == n
                and stream.field_state_digest == field.state_digest
                and stream.memory_state_digest == memory.state_digest
                and stream.last_event_digest == prefix["inputs"][-1]["event"]["event_digest"],
                "MEDIA_CHECKPOINT_STREAM")
        for key in ("field_attempt_count", "memory_formation_attempt_count", "scan_attempt_count"):
            require(getattr(stream, key) == row["post"][key], "MEDIA_CHECKPOINT_COUNTER")
        require(value["births"] == row["current_births"] and value["chain"] == row["chain_digest"],
                "MEDIA_CHECKPOINT_GENERATION")
        account_validate(value["accounting"], manifest, n)
        require(value["accounting"]["restarts"] == 0, "MEDIA_SECOND_RESTART")
        return stream, config
    except work.RestartError:
        raise
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise work.RestartError("MEDIA_CHECKPOINT_COMPONENT", dict(cause=str(exc))) from exc


def restore(value, manifest):
    state, config = validate(value, manifest)
    require(type(value["process_id"]) is int and value["process_id"] != os.getpid(), "MEDIA_RESTORE_PROCESS")
    runtime = media.NativeRuntime.__new__(media.NativeRuntime)
    runtime.expected, runtime.manifest = p.validate(manifest), manifest
    runtime.config, runtime.run_id = config, manifest.run_id
    prefix = c.copy_json(value["prefix"])
    runtime.packed, runtime.source, runtime.rows = prefix["inputs"], prefix["source_receipts"], prefix["rows"]
    runtime.inputs = [b.Input(c.verify.ngv.decode_input(x, config), b.canonical(s).decode("ascii"))
                      for x, s in zip(runtime.packed, runtime.source, strict=True)]
    runtime.binding = r.ng.build_binding(config, "ALL_BANDS_24")
    runtime.fb = r.ng.ObservedBranch(r.ng.field.build_s2lo_field_adapter(b.CLOCK), state.field_state)
    runtime.mb, runtime.scans = r.MemoryBranch(config, manifest.run_id, state.memory_state), {}
    require(not prefix["scans"], "MEDIA_FULL_FILE_SCANS")
    processor = r.ng.stream.RoleFreePerceptionStreamProcessor(field_adapter=runtime.fb,
        memory_adapter=runtime.mb,
        auditory_scan=r.ng.AudioAdapter(runtime.binding, config, False, runtime.scans),
        auditory_baseline=r.ng.AudioAdapter(runtime.binding, config, True, runtime.scans),
        visual_scan=r.ng.VisualAdapter(config, False, runtime.scans),
        visual_baseline=r.ng.VisualAdapter(config, True, runtime.scans))
    rc = r.ng.runtime.build_minimal_runtime_config(runtime_id=manifest.run_id,
        max_event_count=len(manifest.events), source_binding_digest=manifest.manifest_digest,
        component_binding_digest=runtime.binding.binding_digest)
    runtime.subject = c.ResumedRuntimeV1(rc, processor, state)
    runtime.rc, runtime.initial = asdict(rc), prefix["initial"]
    runtime.states = b.StateEvidencePool()
    for key, packed in prefix["states"].items():
        runtime.states[key] = b.state_wire.decode(packed)
    runtime.births, runtime.chain = list(value["births"]), value["chain"]
    runtime.failed = runtime.closed = False
    runtime.failure, runtime.phase = None, "EVIDENCE"
    return runtime


class Session:
    """Finite admitted sequence; controlled suspend is not cancellation."""
    def __init__(self, manifest, directory, store, *, checkpoint=None,
                 mode=admission_rules.NEUTRAL, admission=None):
        require(MAIN_GATE, "MEDIA_RESTART_GATE")
        require(QUALIFIED, "MEDIA_RESTART_NOT_QUALIFIED")
        require(bool(store.future), "MEDIA_RESERVATION_BINDING_MISSING")
        p.validate(manifest)
        require(manifest.schema == p.FULL_VERSION, "MEDIA_RESTART_MODE")
        admission_rules.validate(manifest, mode, admission)
        self.manifest = manifest
        self.directory, self.store = Path(directory), store
        self.lock, self.stop_requested = Lock(), Event()
        self.closed, self.saved, self.failure = False, None, None
        self.origin, self.restarts = None, 0
        self.materializer = self.runtime = None
        self.phase = "OPEN"
        prior, n, receipts = None, 0, []
        if checkpoint is None:
            self.runtime = media.NativeRuntime(manifest)
        else:
            value = store.read(checkpoint)
            self.runtime = restore(value, manifest)
            # Consume before opening any media: failed restore cannot reset its budget.
            try:
                store.publish(Path(str(checkpoint)+".consumed"), dict(checkpoint=value["checkpoint_digest"], uses=1))
            except Exception:
                self.runtime.close()
                raise
            self.origin, self.restarts = value["checkpoint_digest"], 1
            prior, n, receipts = value["accounting"]["work"]["totals"], value["next_ordinal"]-1, value["selections"]
        try:
            decoder = work.WorkerDecoder(manifest.source, prior=prior, next_window=n, resumed=bool(n))
            self.materializer = media.Materializer(manifest, decoder)
            decoder.replay_sink = self._replay_confirmation
            if n:
                self.materializer.counts = dict(value["accounting"]["materializer"])
                self.materializer.receipts = c.copy_json(receipts)
        except Exception as exc:
            self.fail(exc)
            raise

    def _replay_confirmation(self, proof):
        # Only administrative evidence; no runtime/materializer call on replay.
        self.publish(self.directory/("replay-%02d.json" % proof["receipt"]["window"]), proof)

    def accounting(self):
        decoder = self.materializer.decoder
        account = decoder.resources.get("restart_work", decoder.work_account)
        return c.copy_json(dict(version=work.VERSION, completed=len(self.runtime.rows),
            materializer=self.materializer.counts, work=account, restarts=self.restarts))

    def publish(self, path, value):
        self.store.context = dict(phase=self.phase,
            event=None if self.runtime is None or not self.runtime.rows else len(self.runtime.rows),
            completed=0 if self.runtime is None else len(self.runtime.rows))
        self.store.publish(path, value)

    def status(self):
        with self.lock:
            return b.canonical(dict(version=VERSION, origin=self.origin,
                next_ordinal=len(self.runtime.rows)+1, completed=len(self.runtime.rows),
                phase=self.phase, closed=self.closed, checkpoint=self.saved,
                failure=self.failure, restarts=self.restarts))

    def request_suspend(self):
        require(self.restarts == 0, "MEDIA_SECOND_RESTART")
        self.stop_requested.set()

    def next(self):
        with self.lock:
            require(not self.closed and not self.stop_requested.is_set(), "MEDIA_NEXT_BLOCKED")
            n = len(self.runtime.rows)
            require(n < len(self.manifest.events), "MEDIA_END")
            try:
                self.phase = "MATERIALIZATION"
                item = self.materializer.next(self.manifest.events[n])
                self.phase = "EVENT"
                row = self.runtime.process(item)
                require(not self.runtime.failed, "MEDIA_RUNTIME_FAILED")
                self.phase = "EVIDENCE"
                return b.canonical(row)
            except Exception as exc:
                self.fail(exc)
                raise

    def suspend(self):
        self.request_suspend()
        with self.lock:
            require(not self.closed and 0 < len(self.runtime.rows) < len(self.manifest.events), "MEDIA_SUSPEND_POSITION")
            try:
                self.phase = "CHECKPOINT"
                state = self.runtime.subject._state
                unsigned = dict(schema=VERSION, manifest=asdict(self.manifest),
                    code_digest=self.manifest.code_digest, process_id=os.getpid(),
                    next_ordinal=len(self.runtime.rows)+1,
                    stream={**state.payload_without_digest(), "state_digest": state.state_digest},
                    field=self.runtime.fb.state.field.snapshot().canonical_payload(),
                    field_wrapper=r.ng.field_record(self.runtime.fb.state),
                    prefix=c.prefix_record(self.runtime), births=self.runtime.births, chain=self.runtime.chain,
                    accounting=self.accounting(), selections=self.materializer.receipts, main_gate=False)
                self.store.context = dict(phase=self.phase, event=len(self.runtime.rows),
                                          completed=len(self.runtime.rows))
                self.store.encode(unsigned, "checkpoint")
                value = c.seal(unsigned)
                value = c.copy_json(value)
                validate(value, self.manifest)
                path = self.directory/"checkpoint.json"
                self.publish(path, value)
                stored = self.store.read(path)
                require(stored == c.copy_json(value), "MEDIA_CHECKPOINT_PUBLICATION")
                validate(stored, self.manifest)
                self.materializer.decoder.close()
                self.runtime.close()
                self.saved, self.closed, self.phase = stored["checkpoint_digest"], True, "SUSPENDED"
                return self.status_unlocked()
            except Exception as exc:
                self.fail(exc)
                raise

    def status_unlocked(self):
        return b.canonical(dict(phase=self.phase, checkpoint=self.saved, closed=self.closed,
            completed=len(self.runtime.rows), origin=self.origin))

    def close(self):
        with self.lock:
            if self.closed:
                return self.status_unlocked()
            try:
                require(len(self.runtime.rows) == len(self.manifest.events), "MEDIA_INCOMPLETE")
                self.phase = "DRAIN"
                ends = self.materializer.decoder.drain()
                account = self.accounting()
                account_validate(account, self.manifest, len(self.manifest.events))
                core = self.runtime.record()
                self.materializer.decoder.close()
                self.runtime.close()
                result = dict(status="RECORDING_COMPLETE", core=core, accounting=account,
                    selections=self.materializer.receipts, ends=ends, origin=self.origin, gate=False,
                    field=self.runtime.fb.state.field.snapshot().canonical_payload(), process_id=os.getpid())
                result["replay"] = self.materializer.decoder.replay_summary()
                self.publish(self.directory/"record.json", result)
                self.closed, self.phase = True, "RECORDING_COMPLETE"
                return self.status_unlocked()
            except Exception as exc:
                self.fail(exc)
                raise

    def fail(self, exc):
        if self.failure is not None:
            return
        self.failure = dict(code=getattr(exc, "code", type(exc).__name__), phase=self.phase,
            completed=0 if self.runtime is None else len(self.runtime.rows),
            details=getattr(exc, "details", None))
        if self.runtime is not None:
            try:
                snapshot = self.runtime.subject.snapshot()
                n = len(self.runtime.rows)
                self.failure["progress"] = dict(manifest=self.manifest.manifest_digest,
                    last_event=None if not n else self.manifest.events[n-1].event_id,
                    chain=self.runtime.chain, memory=snapshot.memory_state_digest,
                    stream=snapshot.stream_state_digest,
                    field=self.runtime.fb.state.field_component_digest,
                    field_state=self.runtime.fb.state.state_digest,
                    field_steps=self.runtime.fb.state.step_count)
            except Exception as secondary:
                self.failure["progress_unavailable"] = type(secondary).__name__
        if self.materializer is not None:
            try:
                self.materializer.decoder.close()
            except Exception as secondary:
                self.failure["decoder_close_error"] = type(secondary).__name__
            self.failure["resources"] = c.copy_json(self.materializer.decoder.resources)
        if self.runtime is not None:
            try:
                self.runtime.close()
            except Exception as secondary:
                self.failure["runtime_close_error"] = type(secondary).__name__
        self.closed, self.phase = True, "NOT_EVALUABLE"
        self.store.failure(self.directory/"failure.json", dict(status=self.phase, failure=self.failure, gate=False))
