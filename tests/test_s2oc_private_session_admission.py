"""One targeted CALLER qualification; no historical tests or real caller media."""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from tools import _s2oc_private_session_admission as s

b = s.b
OUT = Path(os.environ["OC_ADMISSION_OUT"])
ADMISSION = Path(os.environ["OC_ADMISSION_ROOT"])
PIN = os.environ["OC_ADMISSION_PIN"]
MET = dict(audio=0, nj=0, visual=0, sessions=0, verifications=0)


class AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="oc-admission-neutral-", dir=b.ROOT/"reports/s2oc")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.files = {}
        for name, raw in (("pcm.bin", np.full(4800, 0.03125, dtype="<f4").tobytes()),
                          ("rgb.bin", np.tile(np.array([36, 84, 132], dtype=np.uint8), 1920*1080).tobytes())):
            (cls.root/name).write_bytes(raw)
            cls.files[name] = ((cls.root/name).relative_to(b.ROOT).as_posix(), hashlib.sha256(raw).hexdigest(), len(raw))
        cls.inv = s.inventory()
        original = b.read_payload
        def guarded(p):
            if not (b.ROOT/p.path).resolve().is_relative_to(cls.root):
                raise AssertionError("NON_NEUTRAL_PAYLOAD_FORBIDDEN")
            return original(p)
        for obj, name, fn in ((b, "read_payload", guarded),):
            pt = patch.object(obj, name, fn); pt.start(); cls.addClassCleanup(pt.stop)
        for obj, name, key in ((b.r.half.spectral.LogSpectralReceptor, "analyze", "audio"),
                               (b.LocalChannelGridReceptor, "analyze", "visual"),
                               (b.r.half, "project_auditory_half_v1", "nj")):
            original_call = getattr(obj, name)
            def counted(*args, _call=original_call, _key=key, **kw):
                MET[_key] += 1
                return _call(*args, **kw)
            pt = patch.object(obj, name, counted); pt.start(); cls.addClassCleanup(pt.stop)

    @classmethod
    def tearDownClass(cls):
        s.MAIN_GATE = b.MAIN_GATE = s.old.MAIN_GATE = False
        s.save(OUT/"metrics.json", dict(**MET, gates=False))

    def manifest(self, name):
        rows = []
        for n, kind in enumerate((b.AV, b.A), 1):
            pcm = b.Payload(f"{name}-pcm-{n}", *self.files["pcm.bin"])
            rgb = b.Payload(f"{name}-rgb-{n}", *self.files["rgb.bin"]) if kind == b.AV else None
            rows.append(b.Event(f"{name}-event-{n}", n, kind, **b.expected_times(n, kind), pcm=pcm, rgb=rgb))
        return b.build_manifest(name, tuple(rows), b.digest(self.inv["ob"]))

    def rejected(self, code, directory=None, pin=PIN):
        with patch.object(b, "read_payload", side_effect=AssertionError("PAYLOAD_FORBIDDEN")), \
             patch.object(b, "CallerRuntime", side_effect=AssertionError("RUNTIME_FORBIDDEN")):
            s.MAIN_GATE = True
            with self.assertRaises(s.AdmissionError) as ctx:
                s.open_session(self.manifest("admit-invalid"), OUT/"must-not-exist",
                    admission_directory=directory or ADMISSION, admission_sha256=pin)
            self.assertEqual(ctx.exception.code, code)
            self.assertFalse(s.MAIN_GATE)
            self.assertFalse((OUT/"must-not-exist").exists())

    def altered(self, change, *, inventory_change=False):
        path = self.root/self._testMethodName
        path.mkdir()
        a = json.loads((ADMISSION/"admission.json").read_bytes())
        inv = deepcopy(self.inv)
        change(inv if inventory_change else a)
        iraw = b.canonical(inv)
        a["inventory_sha256"] = s.raw_hash(iraw)
        a = b.sealed({k:v for k,v in a.items() if k != "admission_digest"}, "admission_digest")
        raw = b.canonical(a)
        (path/"inventory.json").write_bytes(iraw)
        (path/"admission.json").write_bytes(raw)
        return path, s.raw_hash(raw)

    def test_01_real_caller_without_archive_reads(self):
        m = self.manifest("admit-caller-one")
        original_open = Path.open
        def no_archive(path, *args, **kw):
            if path.resolve().is_relative_to(s.old.QUAL_DIR) or path.resolve().is_relative_to(b.QUAL_DIR):
                raise AssertionError("ARCHIVE_READ_AT_SESSION_START")
            return original_open(path, *args, **kw)
        with patch.object(Path, "open", no_archive):
            s.MAIN_GATE = True
            c = s.open_session(m, OUT/"caller", admission_directory=ADMISSION, admission_sha256=PIN)
            MET["sessions"] += 1
            for event in m.events:
                result = c.process(event)
                self.assertIs(type(result), bytes)
            record = json.loads(c.close())
            proof, balance = s.verify_session_once(c._path)
            MET["verifications"] += 1
        self.assertEqual(record["mode"], "CALLER")
        self.assertEqual(record["status"], "RECORDING_COMPLETE")
        self.assertTrue(proof["evaluation_allowed"])
        self.assertFalse(balance["violations"])
        self.assertEqual(record["counts"]["audio"], 2)
        self.assertEqual(proof["core"]["core"]["field_contacts"], 384)
        self.assertEqual(proof["core"]["core"]["scan_receipts"], 2)
        self.assertLess(c._last_budget["structured_budget_error_bytes"], c._last_budget["remaining_error_metadata"])
        s.save(OUT/"caller-budget.json", dict(preflight=c._preflight, progress=c._last_budget, actual=balance))

    def test_02_missing_admission(self):
        self.rejected("ADMISSION_INVALID", self.root/"missing")

    def test_03_wrong_trusted_pin(self):
        self.rejected("ADMISSION_INTEGRITY_INVALID", pin="0"*64)

    def test_04_changed_profile_even_with_new_pin(self):
        path, pin = self.altered(lambda a:a.update(profile_digest="0"*64))
        self.rejected("ADMISSION_BINDING_INVALID", path, pin)

    def test_05_changed_software(self):
        path, pin = self.altered(lambda inv:inv["connector"].update({s.OWN[0]:["0"*64,1]}), inventory_change=True)
        self.rejected("ADMISSION_CODE_CHANGED", path, pin)

    def test_06_incomplete_coverage(self):
        path, pin = self.altered(lambda a:a["coverage"].pop())
        self.rejected("ADMISSION_COVERAGE_INVALID", path, pin)

    def test_07_archive_digest_is_not_admission(self):
        a = json.loads((ADMISSION/"admission.json").read_bytes())
        self.rejected("ADMISSION_INTEGRITY_INVALID", pin=a["archive"]["sha256"])

    def test_08_no_extra_qualification_reserve(self):
        a, inv, refs = s.read_admission(ADMISSION, PIN)
        record = dict(execution=None, manifest=asdict(self.manifest("budget-empty")))
        binding = dict(failed_prefix_steps=[])
        result = s.ledger(record, binding, refs)
        expected = len(b.canonical(record))+len(b.canonical(binding))+sum(x[2] for x in refs)+512+262144
        self.assertEqual(result["totals"]["total"], expected)
        self.assertNotIn(4096, result["contributions"].values())

    def test_09_metadata_overflow_keeps_contributions(self):
        value = s.ledger(dict(execution=None, text="x"*65536), {}, ())
        self.assertEqual(value["violations"], ["METADATA_LIMIT"])
        self.assertGreater(value["contributions"]["record"], 65536)
        self.assertEqual(value["totals"]["total"], value["contributions"]["record"]+2+512+262144)

    def test_10_all_violations_retained(self):
        value = s.ledger(dict(execution=None), {}, (("sources","large",4194304),))
        self.assertEqual(set(value["violations"]), {"SOURCES_LIMIT","SHARED_LIMIT","TOTAL_LIMIT"})
        self.assertEqual(value["contributions"]["references"], [["sources","large",4194304]])

    def test_11_manifest_native_bounds(self):
        a, inv, refs = s.read_admission(ADMISSION, PIN)
        p = s.preflight(self.manifest("budget-counts"), refs)
        self.assertEqual(p["native"], dict(states=196608,inputs=32768,steps=32768,scans=65534,nj=2048,formations=1536,generations=1536))
        self.assertFalse(p["violations"])
        self.assertEqual(p["totals"]["metadata"], 65536)

    def test_12_error_after_committed_formation(self):
        m = self.manifest("admit-error-one")
        s.MAIN_GATE = True
        c = s.open_session(m, OUT/"failure", admission_directory=ADMISSION, admission_sha256=PIN)
        MET["sessions"] += 1
        first = c.process(m.events[0])
        prior = asdict(c._runtime.subject.snapshot())
        def failed(event):
            c._materializer.phase = "PAYLOAD_HASH"
            raise b.S2OBError("PAYLOAD_HASH_INVALID")
        with patch.object(c._materializer, "next", failed):
            with self.assertRaises(s.old.S2OCError) as ctx:
                c.process(m.events[1])
        self.assertEqual(ctx.exception.code, "PAYLOAD_HASH_INVALID")
        raw = c.close()
        record = json.loads(raw)
        self.assertEqual(record["failure"]["phase"], "PAYLOAD_HASH")
        self.assertEqual(record["failure"]["completed_events"], 1)
        final = record["failure"]["final"]
        self.assertEqual((prior["field_state_digest"], prior["memory_state_digest"]),
                         (final["field_state_digest"], final["memory_state_digest"]))
        binding = json.loads((c._path/"session.json").read_bytes())
        self.assertEqual(first, b.canonical(binding["failed_prefix_steps"][0]))
        proof, balance = s.verify_session_once(c._path)
        MET["verifications"] += 1
        self.assertFalse(proof["evaluation_allowed"])
        self.assertFalse(balance["violations"])
        self.assertEqual(raw, c.close())
        s.save(OUT/"failure-budget.json", balance)

    def test_13_inventory_integrity(self):
        path, pin = self.altered(lambda a:None)
        with (path/"inventory.json").open("ab") as f:f.write(b" ")
        self.rejected("ADMISSION_INVENTORY_INVALID", path, pin)

    def test_14_different_connector_version(self):
        path, pin = self.altered(lambda a:a.update(version="unsupported"))
        self.rejected("ADMISSION_BINDING_INVALID", path, pin)

    def test_15_shared_closure_proof_cap(self):
        x = s.ledger(dict(execution=None), {}, (), proof_bytes=262145)
        self.assertEqual(x["violations"], ["VERIFICATION_LIMIT"])

    def test_16_source_cap_before_runtime(self):
        m = self.manifest("budget-source")
        with self.assertRaises(s.AdmissionError) as ctx:
            s.preflight(m, (("sources", "too-large", 174081),))
        self.assertEqual(ctx.exception.code, "PREFLIGHT_LIMIT")
        self.assertIn("SOURCES_LIMIT", ctx.exception.balance["violations"])
        self.assertEqual(ctx.exception.balance["totals"]["sources"], 174081)
