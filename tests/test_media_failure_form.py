"""Focused administrative closure tests, with an independent literal schema."""
import copy
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from reports import run_selected_media_restart_once as entry
from tools import _media_restart_evidence as e

OUT = Path(os.environ["MEDIA_FAILURE_FORM_OUT"])
OBS = []


def guard(event, args):
    if event == "open" and isinstance(args[0], (str, bytes)):
        if os.fsdecode(args[0]).lower().endswith((".mp4", ".pcm", ".rgb", ".wav", ".mp3", ".mkv")):
            raise AssertionError("PAYLOAD_FORBIDDEN")
    if event == "subprocess.Popen":
        raise AssertionError("PROCESS_FORBIDDEN")


sys.addaudithook(guard)


class FailureFormTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        patch.object(entry.c.media, "NativeRuntime", side_effect=AssertionError("RUNTIME_FORBIDDEN")).start()
        patch.object(entry.w, "WorkerDecoder", side_effect=AssertionError("DECODER_FORBIDDEN")).start()
        self.assertFalse(entry.c.MAIN_GATE)
        self.assertFalse(entry.c.QUALIFIED)
        self.store = e.Store(OUT/self._testMethodName)
        self.path = self.store.root/"failure.json"

    @classmethod
    def tearDownClass(cls):
        with (OUT/"observations.json").open("xb") as stream:
            stream.write(e.canonical(OBS))

    def fixture(self):
        case = json.loads((entry.ROOT/"reports/MEDIA_RESTART_DRAIN_METADATA_CASE_20260913.json").read_bytes())
        raw = (entry.ROOT/case["source_failure"]["path"]).read_bytes()
        self.assertEqual(e.sha(raw), case["source_failure"]["sha256"])
        value = json.loads(raw)
        totals = dict.fromkeys(("field", "formations", "generations", "metadata", "native", "nj", "shared", "sources", "total", "verification"), 0)
        totals.update(metadata=102021, total=102021)
        synthetic = dict(files=[], totals=totals, limits=e.LIMITS)
        future = [dict(name=name, paths=[name+".json"], limit=8192, closed_by=name+".json")
                  for name in ("logs", "closure")]
        probe = e.Store(self.store.root/"probe", future=future)
        probe.context = dict(phase="DRAIN", event=20, completed=20)
        with patch.object(probe, "ledger", return_value=synthetic):
            with self.assertRaises(entry.w.RestartError) as caught:
                probe._write(probe.root/"index.json", b"x"*3872, "metadata")
        self.assertEqual(caught.exception.code, "MEDIA_STORE_BUDGET")
        value["failure"]["details"] = caught.exception.details
        return value, json.loads(raw)

    def check_shape(self, value):
        # Literal expected schema, not inferred from Store.failure or fixture().
        self.assertEqual(set(value), {"status", "failure", "gate"})
        self.assertEqual(set(value["failure"]), {"code", "completed", "details", "phase", "progress", "resources"})
        self.assertEqual(value["status"], "NOT_EVALUABLE")
        self.assertIs(value["gate"], False)
        failure = value["failure"]
        self.assertEqual((failure["code"], failure["phase"], failure["completed"]), ("MEDIA_STORE_BUDGET", "DRAIN", 20))
        details = failure["details"]
        for key, expected in dict(primary_code="MEDIA_STORE_BUDGET", phase="DRAIN", completed=20,
            evidence_class="metadata", requested_bytes=3872, requested_growth=7744,
            publication_copies=2).items():
            self.assertEqual(details[key], expected)
        self.assertEqual(details["current"]["metadata"], 102021)
        self.assertEqual(details["prospective"]["metadata"], 134341)
        self.assertEqual(details["limits"]["metadata"], 131072)

    def test_01_full_form_size_publication_primary(self):
        value, historical = self.fixture()
        self.check_shape(value)
        self.assertEqual(value["failure"]["resources"], historical["failure"]["resources"])
        self.assertEqual(value["failure"]["progress"], historical["failure"]["progress"])
        before = copy.deepcopy(value)
        raw = e.canonical(value)
        self.assertLessEqual(len(raw), 4096)
        self.store.failure(self.path, value)
        self.assertEqual(self.path.read_bytes(), raw)
        self.check_shape(self.store.read(self.path))
        self.assertEqual(self.store.read(self.path), before)
        self.assertEqual(value, before)
        OBS.append(dict(test=1, bytes=len(raw), limit=4096, published=True, primary_preserved=True))

    def test_02_same_path_only_one_write(self):
        value, _ = self.fixture()
        self.check_shape(value)
        with patch.object(self.store, "_write", wraps=self.store._write) as write:
            self.store.failure(self.path, value)
            original = self.path.read_bytes()
            self.store.failure(self.path, copy.deepcopy(value))
        self.assertEqual(write.call_count, 1)
        self.assertEqual(self.path.read_bytes(), original)
        OBS.append(dict(test=2, writes=write.call_count))

    def test_03_second_path_rejected(self):
        value, _ = self.fixture()
        self.check_shape(value)
        self.store.failure(self.path, value)
        original = self.path.read_bytes()
        other = self.store.root/"second.json"
        with self.assertRaises(entry.w.RestartError) as caught:
            self.store.failure(other, value)
        self.assertEqual(caught.exception.code, "MEDIA_SECOND_FAILURE_PUBLICATION")
        self.assertFalse(other.exists())
        self.assertEqual(self.path.read_bytes(), original)

    def test_04_independent_schema_detects_old_double_wrapper(self):
        value, _ = self.fixture()
        self.check_shape(value)
        for corrupt in (dict(value, details=copy.deepcopy(value["failure"]["details"])),
                        {key: val for key, val in value.items() if key != "failure"}):
            with self.subTest(keys=list(corrupt)):
                with self.assertRaises(AssertionError):
                    self.check_shape(corrupt)
        self.assertFalse(self.path.exists())
