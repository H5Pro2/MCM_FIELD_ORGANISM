"""One focused suite; historical series are not imported or rerun."""
from copy import deepcopy
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from tools import _media_restart_checkpoint as c
from tools import _media_restart_work as w
from tools import _media_restart_evidence as e
from tools import _media_restart_player as p
from tests.media_restart_neutral import NeutralWorker

OUT = Path(os.environ["MEDIA_RESTART_QUAL_OUT"])


class Connection(unittest.TestCase):
    def error(self, code, call):
        with self.assertRaises(w.RestartError) as raised:
            call()
        self.assertEqual(raised.exception.code, code)

    def store(self, label):
        return e.Store(OUT/label)

    def test_01_full_batch_overflow(self):
        for modality, key, cap in (("video", "video_frames", 2048), ("audio", "audio_frames", 4096)):
            with self.subTest(modality=modality):
                d = w.Decoder.__new__(w.Decoder)
                d.work = w.Work(8192, {**w.empty(), key: cap-1})
                d.counters = dict(packets=0, video_frames=0, audio_frames=0)
                d.progress = lambda *args: None
                frame = NS(pts=0, time_base=Fraction(1, 30000))
                container = NS(demux=lambda stream: iter([NS(size=1, decode=lambda: [frame, frame, frame])]))
                delivered = []
                self.error("RESTART_WORK_LIMIT", lambda: delivered.extend(d._frames(container, None, modality)))
                self.assertEqual(delivered, [])
                self.assertEqual(d.work.totals()[key], cap+2)
                self.assertTrue(d.work.payload()["frame_evidence_complete"])

    def test_02_flush_batch_count(self):
        d = w.Decoder.__new__(w.Decoder)
        d.work, d.counters = w.Work(8192), dict(packets=0, video_frames=0, audio_frames=0)
        d.progress = lambda *args: None
        frame = NS(pts=0, time_base=Fraction(1, 30000))
        container = NS(demux=lambda _: iter([NS(size=0, decode=lambda: [frame, frame])]))
        self.assertEqual(len(list(d._frames(container, None, "video"))), 2)
        self.assertEqual(d.work.totals()["video_frames"], 2)

    def test_03_native_call_failure_unknown(self):
        d = w.Decoder.__new__(w.Decoder)
        d.work, d.counters = w.Work(8192), dict(packets=0, video_frames=0, audio_frames=0)
        d.progress = lambda *args: None
        def fail():
            raise RuntimeError("bound native failure")
        with self.assertRaisesRegex(RuntimeError, "bound native failure"):
            list(d._frames(NS(demux=lambda _: iter([NS(size=1, decode=fail)])), None, "video"))
        self.assertFalse(d.work.payload()["frame_evidence_complete"])
        self.assertEqual(d.work.totals()["packets"], 1)

    def test_04_pre_call_limits_and_equality(self):
        for key, cap in w.limits(8192).items():
            with self.subTest(key=key):
                account = w.Work(8192, {**w.empty(), key: cap-1})
                account.before(key, 1)
                account.charge(key, 1)
                self.error("RESTART_WORK_LIMIT", lambda: account.before(key, 1))

    def test_05_hash_failure_keeps_reads(self):
        path = OUT/"wrong-source.bin"
        path.write_bytes(b"abc")
        source = NS(path=path, size=3, sha256="0"*64)
        account, counters = w.Work(3), dict(container_read_bytes=0)
        self.error("RESTART_SOURCE_HASH", lambda: w.CountedFile(source, counters, account))
        self.assertEqual(account.totals()["container_read_bytes"], 3)

    def test_06_shared_values_independent(self):
        store = self.store("shared-control")
        original = {"states": {"x": {"value": [0.0, -0.0, 5e-324]}}}
        second = deepcopy(original)
        a, b = store.pack(original), store.pack(second)
        self.assertEqual(a, b)
        self.assertEqual(len(list((store.root/"objects").iterdir())), 1)
        resolved = store.resolve(a)
        self.assertEqual(e.canonical(resolved), e.canonical(original))
        resolved["states"]["x"]["value"][0] = 9
        self.assertEqual(store.resolve(a), original)
        self.assertEqual(second, original)

    def test_07_missing_reference(self):
        store = self.store("missing-control")
        self.error("MEDIA_REFERENCE_MISSING", lambda: store.resolve({"$media_object": "0"*64,
                   "class": "native", "bytes": 10}))

    def test_08_reference_integrity_and_class(self):
        store = self.store("integrity-control")
        ref = store.intern({"a": 1}, "native")
        self.error("MEDIA_REFERENCE_CLASS", lambda: store.resolve({**ref, "class": "field"}))
        self.error("MEDIA_REFERENCE_DIGEST", lambda: store.resolve({**ref, "bytes": ref["bytes"]+1}))

    def test_09_failed_publication_not_saved(self):
        store = self.store("publication-control")
        with patch.object(e.os, "link", side_effect=OSError("bound publication failure")):
            with self.assertRaisesRegex(OSError, "bound publication failure"):
                store.publish(store.root/"target.json", {"complete": True})
        self.assertFalse((store.root/"target.json").exists())
        self.assertTrue((store.root/"target.json.pending").exists())

    def test_10_historical_worker_response(self):
        # Historical protocol default has no optional restart evidence.
        import inspect
        self.assertIsNone(inspect.signature(w.worker.worker_main).parameters["evidence_factory"].default)
        from io import BytesIO
        source = NS()
        # Exact unchanged encoding of a legacy-shaped response.
        value = {"sequence": 1, "counters": {"packets": 0}, "decoder_versions": None}
        self.assertEqual(w.worker.read_message(BytesIO(w.worker.encode(value))), value)
        spec = c.p.decode(json.loads((OUT/"preregistration.json").read_bytes())["manifest"])
        legacy = w.worker.WorkerDecoder(spec.source, diagnostic_arm="COMMIT_1024", mode=w.old.FULL_MODE)
        try:
            self.assertNotIn("restart_work", legacy.resources)
            self.assertEqual(legacy.counters["container_read_bytes"], 0)
        finally:
            legacy.close()

    def test_11_real_worker_error_evidence(self):
        spec = c.p.decode(json.loads((OUT/"preregistration.json").read_bytes())["manifest"])
        worker = NeutralWorker(spec.source)
        try:
            worker.process.kill()
            worker.process.wait(timeout=10)
            with self.assertRaises(w.worker.WorkerError):
                worker.select(1, 0)
            self.assertFalse(worker.resources["frame_evidence_complete"])
        finally:
            worker.close()
        self.assertTrue(worker.resources["worker_closed"])

    def test_12_native_early_and_late(self):
        prereg = json.loads((OUT/"preregistration.json").read_bytes())
        spec, store = c.p.decode(prereg["manifest"]), e.Store(OUT, prereg["external"])
        commands = [("reference", 0, "-"), ("early-save", 1, "-"),
                    ("early-restore", 0, "early-save/checkpoint.json"),
                    ("late-save", 19, "-"), ("late-restore", 0, "late-save/checkpoint.json")]
        for folder, cut, origin in commands:
            with self.subTest(role=folder):
                with (OUT/(folder+".stdout")).open("xb") as stdout, (OUT/(folder+".stderr")).open("xb") as stderr:
                    result = subprocess.run([sys.executable, "-m", "tests.media_restart_neutral", "session",
                                             folder, str(cut), origin], stdout=stdout, stderr=stderr, timeout=240)
                self.assertEqual(result.returncode, 0, folder)
                stage = store.read(OUT/(folder+"-process.json"))
                self.assertEqual(stage["phase"], "SUSPENDED" if cut else "RECORDING_COMPLETE")
                self.assertTrue(stage["closed"])
                self.assertFalse(stage["gate"])
            if result.returncode != 0:
                return
        for arm in ("early", "late"):
            proof = p.verify_comparison(store, spec, "reference", arm+"-save", arm+"-restore")
            self.assertEqual(proof["status"], "RECORDING_COMPLETE")
            self.assertTrue(proof["core_equal"] and proof["selections_equal"] and proof["final_field_equal"])
            cp = store.read(OUT/(arm+"-save")/"checkpoint.json")
            bad = deepcopy(cp)
            bad["next_ordinal"] += 1
            bad = c.c.seal({k: v for k, v in bad.items() if k != "checkpoint_digest"})
            self.error("MEDIA_CHECKPOINT_POSITION", lambda: c.validate(bad, spec))
            changed = deepcopy(cp)
            changed["manifest"]["source"]["sha256"] = "0"*64
            changed = c.c.seal({k: v for k, v in changed.items() if k != "checkpoint_digest"})
            self.error("MEDIA_CHECKPOINT_BINDING", lambda: c.validate(changed, spec))
            with patch.object(c, "MAIN_GATE", True), patch.object(c, "QUALIFIED", True):
                with self.assertRaises(w.RestartError) as caught:
                    c.Session(spec, OUT/(arm+"-reused"), store, checkpoint=OUT/(arm+"-save")/"checkpoint.json")
                self.assertEqual(caught.exception.code, "MEDIA_PUBLICATION_CONFLICT")
        self.assertFalse(store.ledger()["violations"])


if __name__ == "__main__":
    unittest.main()
