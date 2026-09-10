"""Fresh neutral sessions only; no historical payloads, replay or main caller run."""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import weakref
import numpy as np
from tools import _s2oc_private_caller_session as s

b = s.b
OUT = Path(os.environ["S2OC_QUAL_DIR"])
CODE = os.environ["S2OC_OB_CODE"]
MET = dict(audio=0, nj=0, visual=0, batch_calls=0, opened=0, verifications=0)


def manifest(name, kinds):
    events = []
    for n, kind in enumerate(kinds, 1):
        ps = {}
        for field, file in (("pcm", "audio.bin"), ("rgb", "cue.bin" if kind == b.V else "visual.bin")):
            needed = kind != (b.V if field == "pcm" else b.A)
            raw = CallerSessionTests.files[file]
            ps[field] = b.Payload(f"{name}-{field}-{n}", raw[0], raw[1], raw[2]) if needed else None
        events.append(b.Event(f"{name}-event-{n}", n, kind, **b.expected_times(n, kind), **ps))
    return b.build_manifest(name, tuple(events), CODE)


def opened(name, kinds=(b.AV,)):
    m = manifest(name, kinds)
    s.MAIN_GATE = True
    c = s.open_session(m, OUT/name, mode="NEUTRAL")
    MET["opened"] += 1
    return c, m


def finish(c):
    record = json.loads(c.close())
    proof = s.verify_session_once(c._path)
    return record, proof


class CallerSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="oc-neutral-", dir=b.ROOT/"reports/s2oc")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.raw_root = Path(cls.temp.name).resolve()
        cls.files = {}
        for name in ("audio.bin", "visual.bin", "cue.bin"):
            if name == "audio.bin":
                data = np.full(4800, 0.046875, dtype="<f4").tobytes()
            else:
                frame = np.empty((1080, 1920, 3), dtype=np.uint8)
                frame[:] = (30, 90, 150)
                if name == "cue.bin":
                    cells = frame.reshape(8, 135, 12, 160, 3)
                    for i in range(32, 288):
                        cell, ch = divmod(i, 3); row, col = divmod(cell, 12)
                        cells[row, :, col, :, ch] = 0
                    del cells
                data = frame.tobytes(); del frame
            path = cls.raw_root/name
            path.write_bytes(data)
            cls.files[name] = (path.relative_to(b.ROOT).as_posix(), hashlib.sha256(data).hexdigest(), len(data))
            del data
        original_open = Path.open
        def guarded(path, mode="r", *args, **kw):
            if "r" in mode and path.suffix in (".bin", ".pcm", ".rgb"):
                if not path.resolve().is_relative_to(cls.raw_root):
                    raise AssertionError("REAL_PAYLOAD_FORBIDDEN")
            if "r" in mode and path.suffix == ".json" and path.resolve().is_relative_to(b.ROOT/"reports"):
                if not path.resolve().is_relative_to(OUT):
                    raise AssertionError("HISTORICAL_JSON_FORBIDDEN")
            return original_open(path, mode, *args, **kw)
        cls.views = []
        audio = b.r.half.spectral.LogSpectralReceptor.analyze
        visual = b.LocalChannelGridReceptor.analyze
        nj = b.r.half.project_auditory_half_v1
        verify = s.verifier.verify_once
        def a(self, values):
            MET["audio"] += 1; cls.views.append(weakref.ref(values)); return audio(self, values)
        def v(self, values, **kw):
            MET["visual"] += 1; cls.views.append(weakref.ref(values)); return visual(self, values, **kw)
        def project(*args, **kw):
            MET["nj"] += 1; return nj(*args, **kw)
        def verify_count(*args, **kw):
            MET["verifications"] += 1; return verify(*args, **kw)
        for obj, name, fn in ((Path, "open", guarded), (b.r.half.spectral.LogSpectralReceptor, "analyze", a),
            (b.LocalChannelGridReceptor, "analyze", v), (b.r.half, "project_auditory_half_v1", project),
            (s.verifier, "verify_once", verify_count)):
            p = patch.object(obj, name, fn); p.start(); cls.addClassCleanup(p.stop)

    @property
    def complete(self):
        cls = type(self)
        if not hasattr(cls, "main_attempted"):
            cls.main_attempted = True; cls.main_data = None
            m = manifest("oc-equality", (b.AV, b.A, b.AV, b.V))
            MET["batch_calls"] += 1; b.MAIN_GATE = True
            batch = b.run_once(m, OUT/"batch", mode="NEUTRAL")
            s.verifier.verify_once(OUT/"batch")
            s.MAIN_GATE = True; c = s.open_session(m, OUT/"session", mode="NEUTRAL"); MET["opened"] += 1
            results = []; pauses = []; trace = []
            read = b.read_payload
            for e in m.events:
                before = asdict(c._runtime.subject.snapshot())
                time.sleep(0.001)
                pauses.append(before == asdict(c._runtime.subject.snapshot()))
                allowed = {p.source_id for p in (e.pcm, e.rgb) if p is not None}
                def current_only(p):
                    if p.source_id not in allowed: raise AssertionError("FUTURE_PAYLOAD_FORBIDDEN")
                    trace.append((e.ordinal, p.source_id)); return read(p)
                with patch.object(b, "read_payload", current_only):
                    results.append(c.process(e))
            record, proof = finish(c)
            cls.main_data = dict(batch=batch, record=record, proof=proof, results=results, pauses=pauses, trace=trace, session=c, manifest=m)
        self.assertIsNotNone(cls.main_data, "The one comparison attempt failed; no retry")
        return cls.main_data

    def reject(self, code, fn):
        with self.assertRaises(s.S2OCError) as error: fn()
        self.assertEqual(error.exception.code, code)

    def unchanged_rejection(self, c, event, code):
        before = asdict(c._runtime.subject.snapshot()), dict(c._materializer.counts)
        with patch.object(b, "read_payload", side_effect=AssertionError("PAYLOAD_ACCESS_FORBIDDEN")):
            self.reject(code, lambda: c.process(event))
        self.assertEqual(before, (asdict(c._runtime.subject.snapshot()), dict(c._materializer.counts)))

    def test_01_same_inputs_every_event(self):
        x = self.complete
        self.assertEqual(x["batch"]["status"], "RECORDING_COMPLETE")
        self.assertEqual(x["record"]["status"], "RECORDING_COMPLETE")
        for key in ("inputs", "source_receipts"):
            with self.subTest(binding=key):
                self.assertEqual(b.canonical(x["batch"]["execution"][key]), b.canonical(x["record"]["execution"][key]))

    def test_02_field_memory_and_native_states_equal(self):
        x = self.complete
        for n, (a, z) in enumerate(zip(x["batch"]["execution"]["rows"], x["record"]["execution"]["rows"], strict=True), 1):
            with self.subTest(ordinal=n):
                self.assertEqual(b.canonical((a["pre"], a["post"], a["field"], a["memory"])),
                                 b.canonical((z["pre"], z["post"], z["field"], z["memory"])))
        with self.subTest(binding="native state wire"):
            self.assertEqual(b.canonical(x["batch"]["execution"]["states"]), b.canonical(x["record"]["execution"]["states"]))

    def test_03_generations_equal(self):
        x = self.complete
        self.assertEqual([r["generations"] for r in x["batch"]["execution"]["rows"]],
                         [r["generations"] for r in x["record"]["execution"]["rows"]])

    def test_04_entire_record_scans_and_close_equal(self):
        x = self.complete
        self.assertEqual(b.canonical(x["batch"]), b.canonical(x["record"]))
        self.assertEqual(x["record"]["execution"]["final"]["status"], "CLOSED")

    def test_05_immutable_results_no_owner_alias(self):
        x = self.complete
        for result, row in zip(x["results"], x["record"]["execution"]["rows"], strict=True):
            self.assertIs(type(result), bytes)
            self.assertEqual(result, b.canonical(row["step"]))
            with self.assertRaises(TypeError): result[0] = 0
        self.assertTrue(all(ref() is None for ref in self.views))

    def test_06_no_future_access_and_waiting_changes_no_time(self):
        x = self.complete
        self.assertTrue(all(x["pauses"]))
        self.assertEqual([n for n, _ in x["trace"]], [1, 1, 2, 3, 3, 4])
        self.assertEqual(x["record"]["counts"], dict(audio=3, nj=3, visual=3, payloads=6, materialized_events=4))

    def test_07_duplicate_without_change(self):
        c, m = opened("oc-duplicate")
        c.process(m.events[0]); self.unchanged_rejection(c, m.events[0], "SESSION_DUPLICATE"); finish(c)

    def test_08_out_of_order_without_access(self):
        c, m = opened("oc-order", (b.AV, b.A))
        self.unchanged_rejection(c, m.events[1], "SESSION_ORDER_INVALID"); finish(c)

    def test_09_complete_event_binding_before_access(self):
        c, m = opened("oc-changed")
        e = replace(m.events[0], pcm=replace(m.events[0].pcm, sha256="f"*64))
        self.unchanged_rejection(c, e, "SESSION_EVENT_BINDING_INVALID")
        with patch.object(s, "package_balance", side_effect=s.S2OCError("SESSION_PACKAGE_LIMIT")):
            self.unchanged_rejection(c, m.events[0], "SESSION_PACKAGE_LIMIT")
        finish(c)

    def test_10_manifest_copy_has_no_caller_alias(self):
        c, m = opened("oc-manifest")
        frozen = c._manifest_bytes
        object.__setattr__(m, "run_id", "external-mutation")
        self.assertEqual(c._manifest_bytes, frozen)
        self.assertNotEqual(c._manifest.run_id, m.run_id)
        finish(c)

    def test_11_after_close_rejected(self):
        x = self.complete
        self.unchanged_rejection(x["session"], x["manifest"].events[-1], "SESSION_CLOSED")

    def test_12_exhausted_manifest_and_valid_abstention(self):
        c, m = opened("oc-exhausted", (b.V,))
        result = json.loads(c.process(m.events[0]))
        self.assertEqual(result["context_status"], "ABSTAIN_NO_CONTEXT")
        self.unchanged_rejection(c, replace(m.events[0], ordinal=2), "SESSION_EXHAUSTED")
        record, proof = finish(c); self.assertTrue(proof["evaluation_allowed"])

    def test_13_early_close_is_incomplete(self):
        c, m = opened("oc-incomplete")
        record, proof = finish(c)
        self.assertEqual((record["status"], record["failure"]["code"], record["failure"]["completed_events"]),
                         ("NOT_EVALUABLE", "INCOMPLETE", 0))
        self.assertEqual(record["failure"]["final"]["status"], "CLOSED")
        self.assertFalse(proof["evaluation_allowed"])

    def test_14_repeated_close_no_second_publication(self):
        x = self.complete; c = x["session"]
        before = {p.name: p.read_bytes() for p in c._path.iterdir() if p.is_file()}
        with patch.object(b.r.ng.ne, "atomic_write", side_effect=AssertionError("SECOND_WRITE_FORBIDDEN")):
            self.assertEqual(c.close(), b.canonical(x["record"]))
        self.assertEqual(before, {p.name: p.read_bytes() for p in c._path.iterdir() if p.is_file()})

    def test_15_reentry_protects_materialization_and_processing(self):
        c, m = opened("oc-reentrant")
        read = b.read_payload
        def guarded(p):
            self.unchanged_rejection(c, m.events[0], "SESSION_BUSY")
            self.reject("SESSION_BUSY", c.close)
            return read(p)
        process = c._runtime.process
        def guarded_process(item):
            self.unchanged_rejection(c, m.events[0], "SESSION_BUSY")
            self.reject("SESSION_BUSY", c.close)
            return process(item)
        with patch.object(b, "read_payload", guarded), patch.object(c._runtime, "process", guarded_process):
            c.process(m.events[0])
        record, proof = finish(c); self.assertEqual(record["counts"]["materialized_events"], 1)

    def test_16_payload_failure_before_analysis(self):
        m = manifest("oc-payload", (b.AV, b.A))
        e = replace(m.events[1], pcm=replace(m.events[1].pcm, sha256="f"*64))
        m = b.build_manifest(m.run_id, (m.events[0], e), CODE)
        s.MAIN_GATE = True; c = s.open_session(m, OUT/"oc-payload", mode="NEUTRAL"); MET["opened"] += 1
        earlier = c.process(m.events[0])
        before = asdict(c._runtime.subject.snapshot())
        self.reject("PAYLOAD_HASH_INVALID", lambda: c.process(e))
        record, proof = finish(c)
        with self.subTest(control="error code"):
            self.assertEqual(record["failure"]["code"], "PAYLOAD_HASH_INVALID")
        with self.subTest(control="analysis count"):
            self.assertEqual(record["counts"]["audio"], 1)
        with self.subTest(control="completed events"):
            self.assertEqual(record["failure"]["completed_events"], 1)
        with self.subTest(control="current materialization phase"):
            self.assertEqual(record["failure"]["phase"], "PAYLOAD_HASH")
        with self.subTest(control="preserved field and memory"):
            final = record["failure"]["final"]
            self.assertEqual((before["field_state_digest"], before["memory_state_digest"]),
                             (final["field_state_digest"], final["memory_state_digest"]))
        with self.subTest(control="earlier immutable result"):
            binding = json.loads((c._path/"session.json").read_bytes())
            self.assertEqual(b.canonical(binding["failed_prefix_steps"][0]), earlier)
        with self.subTest(control="no partial evaluation"):
            self.assertFalse(proof["evaluation_allowed"])

    def test_17_memory_failure_preserves_field(self):
        c, m = opened("oc-memory")
        with patch.object(b.r.memory, "_advance_tspm_candidate", side_effect=b.S2OBError("NEUTRAL_MEMORY_FAILURE")):
            self.reject("BRANCH_FAILURE", lambda: c.process(m.events[0]))
        record, proof = finish(c); x = record["execution"]
        self.assertEqual(x["initial"]["memory"], x["final"]["memory_state_digest"])
        self.assertEqual(x["rows"][0]["step"]["perception_status"], "FIELD_CONTACT_RECORDED")
        self.assertFalse(proof["evaluation_allowed"])

    def test_18_field_failure_preserves_memory(self):
        c, m = opened("oc-field")
        def fail(*args, **kw): raise b.S2OBError("NEUTRAL_FIELD_FAILURE")
        c._runtime.subject._processor._field = fail
        self.reject("BRANCH_FAILURE", lambda: c.process(m.events[0]))
        record, proof = finish(c)
        self.assertEqual(record["execution"]["rows"][0]["step"]["memory_status"], "FORMATION_COMMITTED")
        self.assertFalse(proof["evaluation_allowed"])

    def test_19_scan_failure_read_only_field_progress(self):
        c, m = opened("oc-scan-error", (b.AV, b.A))
        c.process(m.events[0])
        def fail(*args, **kw): raise b.S2OBError("NEUTRAL_SCAN_FAILURE")
        c._runtime.subject._processor._auditory_scan = fail
        self.reject("BRANCH_FAILURE", lambda: c.process(m.events[1]))
        record, proof = finish(c); rows = record["execution"]["rows"]
        self.assertEqual(rows[0]["memory"], rows[1]["memory"])
        self.assertEqual(rows[1]["field"]["step_count"], 2)
        self.assertFalse(proof["evaluation_allowed"])

    def test_20_combined_metadata_and_global_budgets(self):
        x = self.complete
        binding = json.loads((x["session"]._path/"session.json").read_bytes())
        inv = s.sources()
        with self.subTest(limit="metadata"):
            self.reject("SESSION_PACKAGE_LIMIT", lambda: s.package_balance(x["record"], {**binding, "extra":"x"*65536}, inv))
        with self.subTest(limit="global sum entry, not reachable complete ledger"):
            with self.assertRaises(s.S2OCError) as e: s.package_balance(x["record"], binding, inv, proof_bytes=4335858)
            self.assertIn("TOTAL_LIMIT", e.exception.balance["violations"])

    def test_21_result_binding_tampering(self):
        x = self.complete
        binding = json.loads((x["session"]._path/"session.json").read_bytes())
        binding["returned_results"][0]["sha256"] = "f"*64
        binding = b.sealed({k:v for k,v in binding.items() if k != "session_digest"}, "session_digest")
        self.reject("SESSION_RESULTS_INVALID", lambda: s.verify_binding(binding, x["record"], s.sources()))

    def test_22_source_binding_tampering(self):
        x = self.complete
        binding = json.loads((x["session"]._path/"session.json").read_bytes())
        self.reject("SESSION_BINDING_INVALID", lambda: s.verify_binding(binding, x["record"], dict(schema="foreign")))

    def test_23_gate_and_output_conflict_no_initialization(self):
        m = manifest("oc-conflict", (b.AV,))
        self.reject("SESSION_GATE_CLOSED", lambda: s.open_session(m, OUT/"forbidden", mode="NEUTRAL"))
        s.MAIN_GATE = True
        with patch.object(b, "CallerRuntime", side_effect=AssertionError("RUNTIME_INIT_FORBIDDEN")):
            self.reject("SESSION_OUTPUT_CONFLICT", lambda: s.open_session(m, OUT/"session", mode="NEUTRAL"))
        self.assertFalse(s.MAIN_GATE)

    def test_24_complete_hull_and_read_only_verification(self):
        x = self.complete
        proof = json.loads((x["session"]._path/"verification.json").read_bytes())
        self.assertTrue(proof["read_only"] and proof["core"]["baseline_equal"])
        self.assertEqual(proof["core"]["field_contacts"], 1008)
        binding = json.loads((x["session"]._path/"session.json").read_bytes())
        self.assertFalse(s.package_balance(x["record"], binding, s.sources())["violations"])
        self.assertFalse(s.MAIN_GATE or b.MAIN_GATE)


def tearDownModule():
    b.r.ng.ne.atomic_write(OUT/"metrics.json", dict(**MET, gates=bool(s.MAIN_GATE or b.MAIN_GATE)), 4096)


if __name__ == "__main__": unittest.main()
