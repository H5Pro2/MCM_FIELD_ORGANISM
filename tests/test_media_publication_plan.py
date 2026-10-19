"""Administrative regression only; no payload, decoder or state execution."""
import copy
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from reports import run_selected_media_restart_once as entry
from tools import _media_publication_plan as p
from tools import _media_restart_evidence as e
from tools import _media_restart_reservations as r

OUT = Path(os.environ["MEDIA_PUBLICATION_QUAL_OUT"])
CASE = json.loads((entry.ROOT/"reports/MEDIA_RESTART_DRAIN_METADATA_CASE_20260913.json").read_bytes())
OBS = []
FUTURE = [dict(name="logs", paths=["stdout.log", "stderr.log"], limit=8192, closed_by="result.json"),
          dict(name="closure", paths=["result.json", "REPORT.md", "balance.json"], limit=8192, closed_by="balance.json")]
GROUPS = r.bind(FUTURE)


def no_payload(event, args):
    if event == "open" and isinstance(args[0], (str, bytes)):
        name = os.fsdecode(args[0]).lower()
        if name.endswith((".mp4", ".pcm", ".rgb", ".wav", ".mp3", ".mkv")):
            raise AssertionError("PAYLOAD_ACCESS_FORBIDDEN")
    if event == "subprocess.Popen":
        raise AssertionError("CHILD_PROCESS_FORBIDDEN")


sys.addaudithook(no_payload)


def ledger(metadata=0):
    totals = dict.fromkeys(p.CATEGORIES, 0)
    totals.update(metadata=metadata, shared=0, total=metadata)
    return dict(files=[dict(path="existing", category="metadata", bytes=metadata)], totals=totals, limits=e.LIMITS)


def binding(entries, scope="NEUTRAL_ADMIN"):
    return dict(version=p.VERSION, scope=scope, positions=[dict(id=key, category=category, count=count,
        lower=low, upper=high) for key, category, count, low, high in entries])


def saved_plan():
    sizes = [88, 142, 1051, 416, 3462, 2330, 2230, 2330]
    assert sum(sizes) == CASE["created_metadata_sum"]
    return p.Plan.bind(binding([(f"created-{i}", "metadata", 1, size, size) for i, size in enumerate(sizes)]
        + [("offered-index", "metadata", 1, CASE["candidate"]["bytes"], CASE["candidate"]["bytes"]) ]))


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        patch.object(entry.c.media, "NativeRuntime", side_effect=AssertionError("RUNTIME_FORBIDDEN")).start()
        patch.object(entry.w, "WorkerDecoder", side_effect=AssertionError("DECODER_FORBIDDEN")).start()
        patch.object(entry.c, "Session", side_effect=AssertionError("SESSION_FORBIDDEN")).start()
        self.assertFalse(entry.c.MAIN_GATE)
        self.assertFalse(entry.c.QUALIFIED)

    @classmethod
    def tearDownClass(cls):
        with (OUT/"observations.json").open("xb") as stream:
            stream.write(e.canonical(OBS))

    def error(self, code, call, kind=p.PlanError):
        with self.assertRaises(kind) as caught:
            call()
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_01_saved_case_rejected_before_media(self):
        error = self.error("PUBLICATION_PREFLIGHT_BUDGET", lambda: saved_plan().preflight(
            ledger(CASE["active_metadata_sum"]), GROUPS, GROUPS, e.FAILURE_BYTES))
        self.assertEqual(error.details["role"], "offered-index")
        decision = error.details["decision"]
        self.assertEqual(decision["success"]["charged"]["metadata"], 134341)
        self.assertEqual(decision["success"]["charged"]["metadata"]-e.LIMITS["metadata"], 3269)
        OBS.append(dict(test=1, base=89972, created=12049, copies=7744, reserves=24576,
                        sum=134341, limit=131072, rejection="BEFORE_MEDIA"))

    def test_02_measured_write_uses_same_ledger(self):
        store = e.Store(OUT/"measured", future=FUTURE)
        with patch.object(store, "ledger", return_value=ledger(102021)):
            error = self.error("MEDIA_STORE_BUDGET", lambda: store._write(store.root/"index.json",
                b"x"*3872, "metadata"), entry.w.RestartError)
        self.assertEqual(error.details["prospective"]["metadata"], 134341)
        self.assertEqual(error.details["requested_growth"], 7744)
        self.assertFalse((store.root/"index.json").exists())
        self.assertFalse((store.root/"index.json.pending").exists())

    def test_03_exact_limit_is_valid(self):
        plan = p.Plan.bind(binding([("index", "metadata", 1, 3872, 3872)]))
        result = plan.preflight(ledger(98752), GROUPS, GROUPS, 4096)
        self.assertEqual(result[-1]["decision"]["success"]["charged"]["metadata"], 131072)
        self.assertEqual(result[-1]["decision"]["violations"], [])

    def test_04_one_byte_over_is_rejected(self):
        plan = p.Plan.bind(binding([("index", "metadata", 1, 3872, 3872)]))
        error = self.error("PUBLICATION_PREFLIGHT_BUDGET", lambda: plan.preflight(
            ledger(98753), GROUPS, GROUPS, 4096))
        self.assertEqual(error.details["decision"]["success"]["charged"]["metadata"], 131073)

    def test_05_missing_position_and_order(self):
        full = [(key, cat, count, 0, None) for key, (cat, count) in p.full_layout().items()]
        for i in range(len(full)):
            with self.subTest(missing=full[i][0]):
                self.error("PUBLICATION_POSITION_MISSING", lambda i=i: p.Plan.bind(
                    binding(full[:i]+full[i+1:], "FULL_RESTART")))
        swapped = full.copy()
        swapped[0], swapped[1] = swapped[1], swapped[0]
        self.error("PUBLICATION_ORDER_INVALID", lambda: p.Plan.bind(binding(swapped, "FULL_RESTART")))
        OBS.append(dict(test=5, independently_removed_positions=len(full)))

    def test_06_unknown_upper_is_not_zero(self):
        full = binding([(key, cat, count, 0, None) for key, (cat, count) in p.full_layout().items()], "FULL_RESTART")
        plan = p.Plan.bind(full)
        self.error("PUBLICATION_PLAN_UNBOUNDED", lambda: plan.preflight(ledger(), GROUPS, GROUPS, 4096))

    def test_07_error_alternatives_and_protected_reserve(self):
        rows = [dict(path="candidate.pending", category="metadata", bytes=3872),
                dict(path="candidate", category="metadata", bytes=3872)]
        result = p.transaction(ledger(102021), rows, GROUPS, GROUPS, 4096)
        self.assertEqual([x["charged"]["metadata"] for x in result["failure"]], [126597, 130469, 134341])
        self.assertEqual([x["primary_failure_reserve"] for x in result["failure"]], [0, 0, 0])
        self.assertEqual(result["success"]["primary_failure_reserve"], 8192)
        self.assertEqual(result["success"]["charged"]["metadata"], 134341)
        OBS.append(dict(test=7, failure_peaks=[126597, 130469, 134341], success_peak=134341,
                        paths_are_alternatives=True))

    def test_08_reservation_consumption_keeps_physical_copies(self):
        groups = r.bind([dict(name="closure", paths=["result.json"], limit=100, closed_by="closed")])
        result = p.transaction(ledger(10), [dict(path="result.json.pending", category="metadata", bytes=40),
            dict(path="result.json", category="metadata", bytes=40)], groups, groups, 4096)
        self.assertEqual(result["success"]["occupied"]["metadata"], 90)
        self.assertEqual(result["success"]["future_bytes"], 60)
        self.assertEqual(result["success"]["charged"]["metadata"], 8342)
        self.assertEqual(result["failure"][1]["charged"]["metadata"], 8342)

    def test_09_lossless_administrative_roles(self):
        value = dict(core=dict(binding=dict(profile="synthetic-fixed"), initial=dict(status="administrative")))
        original = copy.deepcopy(value)
        keys = ["record.json#/core/binding", "record.json#/core/initial", "record.json#/core", "record.json"]
        plan = binding([(key, "metadata", 1, 0, 1024) for key in keys])
        store = e.Store(OUT/"roundtrip", publication_plan=plan)
        store.preflight()
        store.publish(store.root/"record.json", value)
        self.assertEqual(store.read(store.root/"record.json"), original)
        self.assertEqual(value, original)
        self.error("PUBLICATION_POSITION_MISSING", lambda: store.publish(store.root/"foreign.json", {}))
        self.assertFalse((store.root/"foreign.json").exists())

    def test_10_entry_rejects_missing_plan_before_source(self):
        data = dict(version=entry.VERSION, limits=e.LIMITS, stages=list(entry.STAGES))
        with patch.object(entry, "bound_json", return_value=data), \
             patch.object(entry.c.p, "decode", side_effect=AssertionError("MANIFEST_REACHED")) as decode:
            self.error("PUBLICATION_PLAN_REQUIRED", lambda: entry.load("unused", "unused", "unused", "unused"))
        decode.assert_not_called()

    def test_11_parent_preflight_blocks_launch(self):
        plan = binding([(key, cat, count, 0, None) for key, (cat, count) in p.full_layout().items()], "FULL_RESTART")
        data = dict(future=FUTURE, publication_plan=plan)
        with patch.object(entry, "load", return_value=(data, None, None, OUT/"entry", [])), \
             patch.object(entry, "launch", side_effect=AssertionError("MEDIA_LAUNCH_REACHED")) as launch:
            self.error("PUBLICATION_PLAN_UNBOUNDED", lambda: entry.execute("x", "x", "x", "x"))
        launch.assert_not_called()
        self.assertFalse((OUT/"entry/run.claim").exists())
        self.assertFalse(entry.c.MAIN_GATE)
        self.assertFalse(entry.c.QUALIFIED)

    def test_12_full_diagnostic_and_one_failure_publication(self):
        store = e.Store(OUT/"failure", future=FUTURE)
        store.context = dict(phase="DRAIN", event=20, completed=20)
        with patch.object(store, "ledger", return_value=ledger(102021)):
            error = self.error("MEDIA_STORE_BUDGET", lambda: store._write(store.root/"index.json",
                b"x"*3872, "metadata"), entry.w.RestartError)
        historical = entry.ROOT/CASE["source_failure"]["path"]
        raw = historical.read_bytes()
        self.assertEqual(e.sha(raw), CASE["source_failure"]["sha256"])
        fixture = json.loads(raw)
        fixture["details"] = error.details
        self.assertLessEqual(len(e.canonical(fixture)), 4096)
        store.failure(store.root/"failure.json", fixture)
        before = (store.root/"failure.json").read_bytes()
        store.failure(store.root/"failure.json", fixture)
        self.assertEqual((store.root/"failure.json").read_bytes(), before)
        self.assertEqual(store.read(store.root/"failure.json")["details"]["prospective"]["metadata"], 134341)
        OBS.append(dict(test=12, diagnostic_bytes=len(before), failure_publications=1,
                        payload_calls=0, state_processing_calls=0))
