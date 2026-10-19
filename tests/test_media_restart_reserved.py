"""Prepared focused reserve/restore checks. Entry requires a bound ready preflight."""
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from tools import _media_restart_checkpoint as c
from tools import _media_restart_evidence as e
from tools import _media_restart_reservations as r
from tools import _media_restart_player as p
from tools import _media_restart_work as w
from tests.media_restart_neutral import NeutralWorker

ROOT = Path(os.environ.get("MEDIA_RESTART_QUAL_OUT", "reports/media-restart-qualification-20260913-03"))


def bound():
    binding = json.loads((ROOT/"preregistration.json").read_bytes())
    w.require(binding["ready"], "QUALIFICATION_PREFLIGHT_REJECTED")
    return c.p.decode(binding["manifest"]), e.Store(ROOT, binding["external"], future=binding["future"])


def child(folder, cut, origin):
    manifest, store = bound()
    binding = NS(manifest=manifest, source=Path(manifest.source.path), output=ROOT/folder,
                 claim=ROOT/(folder+".claim"), mode="NEUTRAL_CONNECTION")
    app = p.Player(binding, store, selected_checkpoint=None if origin == "-" else ROOT/origin)
    def boundary():
        if cut and len(app.session.runtime.rows) == cut:
            app.stop_event.set()
    app._after_event = boundary
    with patch.object(c, "QUALIFIED", True), patch.object(w, "WorkerDecoder", NeutralWorker):
        app.start()
        app.thread.join(180)
        status = json.loads(app.status())
        w.require(not app.thread.is_alive(), "NEUTRAL_SESSION_TIMEOUT")
        w.require(status["phase"] == ("SUSPENDED" if cut else "RECORDING_COMPLETE"),
                  "NEUTRAL_NATIVE_STATUS", status)
        store.publish(ROOT/(folder+"-process.json"), dict(pid=os.getpid(), closed=app.session.closed,
            gate=c.MAIN_GATE, phase=status["phase"], completed=status["completed"]))


class Reserved(unittest.TestCase):
    def error(self, code, call):
        with self.assertRaises(w.RestartError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_01_all_positions_same_reservation_basis(self):
        future = r.bind([dict(name="log", paths=["stdout", "stderr"], limit=1024, closed_by="result"),
                         dict(name="result", paths=["result"], limit=128, closed_by="result")])
        for position in range(21):
            for written in (0, 512, 1024):
                with self.subTest(position=position, written=written):
                    rows = [dict(path="stdout", bytes=written, category="metadata")]
                    physical = dict(metadata=written, total=written)
                    ledger = dict(files=rows, totals=physical, limits=dict(metadata=131072, total=4194304))
                    a = r.assess(ledger, future, e.FAILURE_RESERVE)
                    self.assertEqual(a["charged"]["metadata"], 1024+128+e.FAILURE_RESERVE)
                    # A committed result releases both the log tail and its own
                    # unused space. The temporary result copy remains physical.
                    ledger["files"] += [dict(path="result", bytes=64, category="metadata"),
                                        dict(path="result.pending", bytes=64, category="metadata")]
                    ledger["totals"] = dict(metadata=written+128, total=written+128)
                    b = r.assess(ledger, future, e.FAILURE_RESERVE)
                    self.assertEqual(b["future_bytes"], 0)
                    self.assertEqual(b["charged"]["metadata"], written+128+e.FAILURE_RESERVE)

    def test_02_boundary_and_reserved_primary(self):
        future = [dict(name="report", paths=["REPORT.md"], limit=1024, closed_by="REPORT.md")]
        store = e.Store(ROOT/"reserve-controls", future=future)
        original = store.ledger
        for over in (0, 1):
            with self.subTest(excess=over):
                actual = original()["totals"]["metadata"]
                filler = e.LIMITS["metadata"]-actual-1024-e.FAILURE_RESERVE-4+over
                def ledger(extra=()):
                    return original([dict(path="synthetic-boundary", bytes=filler, category="metadata"), *extra])
                with patch.object(store, "ledger", side_effect=ledger):
                    path = store.root/(str(over)+".json")
                    if not over:
                        store._write(path, b"{}", "metadata")
                    else:
                        store.context = dict(phase="PLAYER_CLOSE", event=20, completed=20)
                        exc = self.error("MEDIA_STORE_BUDGET", lambda: store._write(path, b"{}", "metadata"))
                        self.assertEqual(exc.details["prospective"]["metadata"], 131073)
                        store.failure(store.root/"failure.json", dict(status="NOT_EVALUABLE", primary=exc.details))
                        proof = store.read(store.root/"failure.json")
                        self.assertEqual(proof["primary"]["primary_code"], "MEDIA_STORE_BUDGET")

    def test_03_reservation_binding_and_overrun(self):
        value = dict(name="log", paths=["stderr"], limit=12, closed_by="result")
        bound_groups = r.bind([value])
        value["paths"].append("foreign")
        self.assertEqual(bound_groups[0].paths, ("stderr",))
        ledger = dict(files=[dict(path="stderr", bytes=13, category="metadata")],
                      totals=dict(metadata=13, total=13), limits=dict(metadata=131072, total=4194304))
        result = r.assess(ledger, bound_groups, e.FAILURE_RESERVE)
        self.assertIn("reservation:log", result["violations"])
        self.assertEqual(result["occupied"]["metadata"], 13)
        self.error("MEDIA_RESERVATION_OVERLAP", lambda: r.bind([value, {**value, "name": "other"}]))

    def test_04_native_stages(self):
        _, store = bound()
        for folder, cut, origin in [("reference", 0, "-"), ("early-save", 1, "-"),
                ("early-restore", 0, "early-save/checkpoint.json"), ("late-save", 19, "-"),
                ("late-restore", 0, "late-save/checkpoint.json")]:
            with (ROOT/(folder+".stdout")).open("xb") as stdout, (ROOT/(folder+".stderr")).open("xb") as stderr:
                result = subprocess.run([sys.executable, "-m", "tests.test_media_restart_reserved", "child",
                    folder, str(cut), origin], stdout=stdout, stderr=stderr, timeout=240)
            self.assertEqual(result.returncode, 0, folder)
            status = store.read(ROOT/(folder+"-process.json"))
            self.assertEqual(status["phase"], "SUSPENDED" if cut else "RECORDING_COMPLETE")
            self.assertTrue(status["closed"])
            self.assertFalse(status["gate"])

    def compare(self, arm):
        manifest, store = bound()
        result = p.verify_comparison(store, manifest, "reference", arm+"-save", arm+"-restore")
        self.assertEqual(result["status"], "RECORDING_COMPLETE")
        for key in ("evaluation_allowed", "core_equal", "selections_equal", "final_field_equal"):
            self.assertTrue(result[key], key)
        self.assertEqual(len(result["rows"]), 20)
        self.assertTrue(all(row["equal"] for row in result["rows"]))
        ref = store.read(ROOT/"reference/record.json")
        saved = store.read(ROOT/(arm+"-save")/"checkpoint.json")
        resumed = store.read(ROOT/(arm+"-restore")/"record.json")
        self.assertEqual(ref["accounting"]["materializer"], resumed["accounting"]["materializer"])
        account = resumed["accounting"]["work"]
        self.assertEqual(account["prior"], saved["accounting"]["work"]["totals"])
        self.assertNotEqual(resumed["process_id"], saved["process_id"])
        for key in w.KEYS:
            self.assertEqual(account["totals"][key], account["prior"][key]+sum(v[key] for v in account["parts"].values()))
            self.assertLessEqual(account["totals"][key], account["limits"][key])
        self.assertFalse(store.budget()["violations"])

    def test_05_early_all_comparisons(self):
        self.compare("early")

    def test_06_late_all_comparisons(self):
        self.compare("late")


if __name__ == "__main__":
    if sys.argv[1:2] == ["child"]:
        child(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    else:
        unittest.main()
