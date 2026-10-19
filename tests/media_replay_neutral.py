"""Synthetic decoder frames and native late restart, never selected media."""
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace as NS
from unittest.mock import patch

from tests.media_restart_neutral import NeutralDecoder
from tools import _media_restart_work as w


class NeutralWorker(w.WorkerDecoder):
    @staticmethod
    def _launch(command, **kwargs):
        return subprocess.Popen([sys.executable, "-B", "-m", "tests.media_replay_neutral", "worker"], **kwargs)


def session(role):
    from tools import _media_restart_checkpoint as c
    from tools import _media_restart_evidence as e
    from tools import _media_restart_player as p
    out = Path(os.environ["MEDIA_REPLAY_QUAL_OUT"])
    q = json.loads((out/"preregistration.json").read_bytes())
    manifest = c.p.decode(q["manifest"])
    root = out/"native"
    store = e.Store(root, future=q["native_future"], budget_profile=q["budget_profile"],
                    publication_plan=q["publication_plan"])
    if role == "suspend19":
        store.publish_profile()
    bind = NS(manifest=manifest, source=Path(manifest.source.path), output=root/role,
              claim=root/(role+".claim"), mode="NEUTRAL_CONNECTION")
    app = p.Player(bind, store, selected_checkpoint=root/"suspend19/checkpoint.json" if role == "restore20" else None)
    seen = []
    sink = c.Session._replay_confirmation
    def observe(session, proof):
        before = session.runtime.subject.snapshot()
        w.require(len(session.runtime.rows) == 19, "NEUTRAL_REPLAY_EXTRA_FORMATION")
        sink(session, proof)
        w.require(session.runtime.subject.snapshot() == before, "NEUTRAL_REPLAY_CHANGED_STATE")
        seen.append(proof["receipt"]["window"])
    def boundary():
        if role == "suspend19" and len(app.session.runtime.rows) == 19:
            app.stop_event.set()
    app._after_event = boundary
    with patch.object(c, "QUALIFIED", True), patch.object(w, "WorkerDecoder", NeutralWorker), \
         patch.object(c.Session, "_replay_confirmation", observe):
        try:
            app.start()
            app.thread.join(180)
            w.require(not app.thread.is_alive(), "NEUTRAL_TIMEOUT")
            status = json.loads(app.status())
            w.require(status["phase"] == ("SUSPENDED" if role == "suspend19" else "RECORDING_COMPLETE"),
                      "NEUTRAL_STATUS", status)
            if role == "restore20":
                w.require(seen == list(range(20)), "NEUTRAL_REPLAY_COVERAGE")
                record = store.read(root/role/"record.json")
                cp = store.read(root/"suspend19/checkpoint.json")
                proofs = [store.read(root/role/("replay-%02d.json" % n)) for n in range(20)]
                w.replay.verify(proofs, manifest.source, 19, cp["accounting"]["work"]["totals"],
                                record["accounting"]["work"], record["replay"])
                w.require(record["accounting"]["materializer"]["materialized_events"] == 20,
                          "NEUTRAL_MATERIALIZER_COUNT")
                w.require(record["ends"]["audio_eof"] and record["ends"]["video_eof"], "NEUTRAL_EOF")
            store.publish(root/(role+"-process.json"), dict(pid=os.getpid(), phase=status["phase"],
                closed=app.session.closed, gate=c.MAIN_GATE, confirmations=seen,
                completed=len(app.session.runtime.rows), replay_formation_calls=0))
        finally:
            c.MAIN_GATE = c.QUALIFIED = False


if __name__ == "__main__":
    if sys.argv[1:] == ["worker"]:
        w.worker.worker_main(decoder_factory=NeutralDecoder, evidence_factory=w.evidence, operation_handler=w.operation)
    elif len(sys.argv) == 2 and sys.argv[1] in ("suspend19", "restore20"):
        session(sys.argv[1])
    else:
        raise SystemExit("Neutral only")
