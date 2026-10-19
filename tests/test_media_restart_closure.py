"""Focused v2 closure qualification; no historical decoder suite replay."""
from copy import deepcopy
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
from tools import _media_restart_player as p
from tools import _media_restart_work as w
from tests.media_restart_neutral import NeutralWorker

OUT = Path(os.environ["MEDIA_RESTART_QUAL_OUT"])


class Closure(unittest.TestCase):
    def error(self, code, call):
        with self.assertRaises(w.RestartError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def bound(self):
        binding = json.loads((OUT/"preregistration.json").read_bytes())
        return c.p.decode(binding["manifest"]), e.Store(OUT, binding["external"])

    def test_01_independent_reference_resolution(self):
        store = e.Store(OUT/"reference-controls")
        supplied = {"core": {"states": {"x": {"hex": "0x0.0000000000001p-1022"}},
                    "inputs": [{"a": -0.0}], "rows": [{"ordinal": 1}], "scans": []},
                    "selections": [{"ordinal": 1, "frame_pts": 1001}]}
        before = e.canonical(supplied)
        a, b = store.pack(supplied), store.pack(json.loads(before))
        self.assertEqual(a, b)
        self.assertIn("$media_object", a["core"])
        # An independent reader, not Store.resolve, checks every nested object.
        def resolve(node):
            if isinstance(node, dict) and "$media_object" in node:
                raw = (store.root/"objects"/(node["$media_object"]+".json")).read_bytes()
                self.assertEqual(e.sha(raw), node["$media_object"])
                self.assertEqual(len(raw), node["bytes"])
                value = json.loads(raw)
                self.assertEqual(value["class"], node["class"])
                return resolve(value["value"])
            if isinstance(node, dict):
                return {k: resolve(v) for k, v in node.items()}
            if isinstance(node, list):
                return [resolve(v) for v in node]
            return node
        self.assertEqual(e.canonical(resolve(a)), before)
        detached = store.resolve(a)
        detached["core"]["rows"][0]["ordinal"] = 99
        self.assertEqual(e.canonical(store.resolve(a)), before)
        self.assertEqual(e.canonical(supplied), before)

    def test_02_changed_reference_rejections(self):
        store = e.Store(OUT/"reference-rejections")
        packed = store.pack({"core": {"rows": [{"ordinal": 1}]}})
        ref = packed["core"]
        cases = [("MEDIA_REFERENCE_CLASS", {**ref, "class": "native"}),
                 ("MEDIA_REFERENCE_DIGEST", {**ref, "bytes": ref["bytes"]+1}),
                 ("MEDIA_REFERENCE_MISSING", {**ref, "$media_object": "0"*64})]
        for code, changed in cases:
            with self.subTest(code=code):
                self.error(code, lambda: store.resolve({"core": changed}))

    def test_03_budget_boundary_all_progress_positions(self):
        store = e.Store(OUT/"budget-controls")
        base = store.ledger
        # Virtual metadata contributions isolate the boundary; no large filler
        # files or fabricated native memory are used.
        for completed in range(21):
            for over in (0, 1):
                with self.subTest(completed=completed, excess=over):
                    path = store.root/(str(completed)+"-"+str(over)+".json")
                    raw = b"{}"
                    actual = base()["totals"]["metadata"]
                    filler = e.LIMITS["metadata"]-e.FAILURE_RESERVE-e.ADMIN_CLOSURE_RESERVE-2*len(raw)-actual+over
                    def ledger(extra=()):
                        return base([dict(path="virtual-boundary", bytes=filler, category="metadata"), *extra])
                    store.context = dict(phase="EVIDENCE", event=completed, completed=completed)
                    with patch.object(store, "ledger", side_effect=ledger):
                        if over:
                            exc = self.error("MEDIA_STORE_BUDGET", lambda: store._write(path, raw, "metadata"))
                            d = exc.details
                            self.assertEqual(d["prospective"]["metadata"], e.LIMITS["metadata"]+1)
                            self.assertEqual(d["current"]["metadata"]+d["requested_growth"]+
                                             d["reserved_failure_bytes"]+d["reserved_administrative_closure_bytes"],
                                             d["prospective"]["metadata"])
                            self.assertEqual(d["completed"], completed)
                            self.assertEqual(d["violations"], ["metadata"])
                            self.assertFalse(path.exists())
                        else:
                            store._write(path, raw, "metadata")

    def test_04_reserved_primary_failure_after_native_formation(self):
        manifest, store = self.bound()
        with patch.object(c, "MAIN_GATE", True), patch.object(c, "QUALIFIED", True), \
                patch.object(w, "WorkerDecoder", NeutralWorker):
            session = c.Session(manifest, OUT/"primary-failure", store)
        try:
            session.next()
            self.assertFalse(session.runtime.failed)
            self.assertEqual(len(session.runtime.rows), 1)
            field = e.canonical(session.runtime.fb.state.field.snapshot().canonical_payload())
            state = session.runtime.subject._state.state_digest
            base = store.ledger
            filler = e.LIMITS["metadata"]-e.FAILURE_RESERVE-e.ADMIN_CLOSURE_RESERVE-1-base()["totals"]["metadata"]
            def ledger(extra=()):
                return base([dict(path="virtual-occupation", bytes=filler, category="metadata"), *extra])
            with patch.object(store, "ledger", side_effect=ledger):
                exc = self.error("MEDIA_STORE_BUDGET", lambda: session.publish(
                    OUT/"primary-failure/regular.json", {"complete": True}))
                session.fail(exc)
            proof = store.read(OUT/"primary-failure/failure.json")
            self.assertEqual(proof["status"], "NOT_EVALUABLE")
            detail = proof["failure"]["details"]
            self.assertEqual(detail["primary_code"], "MEDIA_STORE_BUDGET")
            self.assertEqual(detail["phase"], "EVIDENCE")
            self.assertEqual(detail["event"], 1)
            self.assertEqual(detail["evidence_class"], "metadata")
            self.assertIn("requested_growth", detail)
            self.assertIn("limits", detail)
            self.assertEqual(detail["current"]["metadata"]+detail["requested_growth"]+
                             detail["reserved_failure_bytes"]+detail["reserved_administrative_closure_bytes"],
                             detail["prospective"]["metadata"])
            self.assertEqual(field, e.canonical(session.runtime.fb.state.field.snapshot().canonical_payload()))
            self.assertEqual(state, session.runtime.subject._state.state_digest)
            before = (OUT/"primary-failure/failure.json").read_bytes()
            session.fail(w.RestartError("MEDIA_INCOMPLETE"))
            session.close()
            self.assertEqual((OUT/"primary-failure/failure.json").read_bytes(), before)
            self.assertTrue(session.closed)
        finally:
            if not session.closed:
                session.fail(w.RestartError("NEUTRAL_TEST_CLEANUP"))

    def test_05_native_stages(self):
        _, store = self.bound()
        stages = [("reference", 0, "-"), ("early-save", 1, "-"),
                  ("early-restore", 0, "early-save/checkpoint.json"),
                  ("late-save", 19, "-"), ("late-restore", 0, "late-save/checkpoint.json")]
        for folder, cut, origin in stages:
            with (OUT/(folder+".stdout")).open("xb") as stdout, (OUT/(folder+".stderr")).open("xb") as stderr:
                result = subprocess.run([sys.executable, "-m", "tests.media_restart_neutral", "session",
                    folder, str(cut), origin], stdout=stdout, stderr=stderr, timeout=240)
            self.assertEqual(result.returncode, 0, folder+": native technical status failed")
            status = store.read(OUT/(folder+"-process.json"))
            self.assertEqual(status["phase"], "SUSPENDED" if cut else "RECORDING_COMPLETE")
            self.assertTrue(status["closed"])
            self.assertFalse(status["gate"])

    def compare(self, arm):
        manifest, store = self.bound()
        proof = p.verify_comparison(store, manifest, "reference", arm+"-save", arm+"-restore")
        self.assertEqual(proof["status"], "RECORDING_COMPLETE")
        self.assertTrue(proof["evaluation_allowed"])
        for key in ("core_equal", "selections_equal", "final_field_equal"):
            self.assertTrue(proof[key], key)
        self.assertEqual(len(proof["rows"]), 20)
        self.assertTrue(all(row["equal"] for row in proof["rows"]))
        ref = store.read(OUT/"reference/record.json")
        restored = store.read(OUT/(arm+"-restore")/"record.json")
        cut = store.read(OUT/(arm+"-save")/"checkpoint.json")
        self.assertEqual(ref["accounting"]["materializer"], restored["accounting"]["materializer"])
        work = restored["accounting"]["work"]
        self.assertEqual(work["prior"], cut["accounting"]["work"]["totals"])
        for key in w.KEYS:
            self.assertEqual(work["totals"][key], work["prior"][key]+sum(v[key] for v in work["parts"].values()))
            self.assertLessEqual(work["totals"][key], work["limits"][key])
        self.assertGreater(work["parts"]["replay"]["video_frames"], 0)
        self.assertNotEqual(restored["process_id"], cut["process_id"])
        self.assertFalse(store.ledger()["violations"])

    def test_06_early_comparisons(self):
        self.compare("early")

    def test_07_late_comparisons(self):
        self.compare("late")

    def test_08_position_rejection(self):
        manifest, store = self.bound()
        for arm in ("early", "late"):
            with self.subTest(arm=arm):
                cp = store.read(OUT/(arm+"-save")/"checkpoint.json")
                cp["next_ordinal"] += 1
                cp = c.c.seal({k: v for k, v in cp.items() if k != "checkpoint_digest"})
                self.error("MEDIA_CHECKPOINT_POSITION", lambda: c.validate(cp, manifest))

    def test_09_source_rejection(self):
        manifest, store = self.bound()
        for arm in ("early", "late"):
            with self.subTest(arm=arm):
                cp = store.read(OUT/(arm+"-save")/"checkpoint.json")
                cp["manifest"]["source"]["sha256"] = "0"*64
                cp = c.c.seal({k: v for k, v in cp.items() if k != "checkpoint_digest"})
                self.error("MEDIA_CHECKPOINT_BINDING", lambda: c.validate(cp, manifest))

    def test_10_consumed_checkpoint(self):
        manifest, store = self.bound()
        for arm in ("early", "late"):
            with self.subTest(arm=arm), patch.object(c, "MAIN_GATE", True), patch.object(c, "QUALIFIED", True):
                self.error("MEDIA_PUBLICATION_CONFLICT", lambda: c.Session(manifest, OUT/(arm+"-reused"), store,
                           checkpoint=OUT/(arm+"-save")/"checkpoint.json"))

    def test_11_player_preserves_primary_closure(self):
        manifest, _ = self.bound()
        store = e.Store(OUT/"player-error-control")
        output = store.root/"session"
        output.mkdir()
        binding = NS(manifest=manifest, source=Path(manifest.source.path), output=output,
                     claim=store.root/"claim", mode="NEUTRAL_CONNECTION")
        app = p.Player(binding, store)
        primary = dict(code="MEDIA_STORE_BUDGET", phase="EVIDENCE", completed=1)
        def rejected():
            raise OSError("secondary closure unavailable")
        fake = NS(origin=None, runtime=NS(rows=[]), next=rejected, failure=primary, closed=True)
        with patch.object(app, "_open_session", return_value=fake), patch.object(store, "publish") as publish:
            app._run()
        self.assertEqual(json.loads(app.status())["error"], "MEDIA_STORE_BUDGET")
        self.assertEqual(json.loads(app.status())["phase"], "NOT_EVALUABLE")
        publish.assert_not_called()
        self.assertFalse(c.MAIN_GATE)


if __name__ == "__main__":
    unittest.main()
