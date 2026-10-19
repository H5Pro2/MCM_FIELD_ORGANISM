"""Focused starter controls plus one real, newly bound neutral session."""
from copy import deepcopy
from dataclasses import asdict
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from reports.s2od import start_terminal_basic_once as st
from reports.s2od import qualify_native_start_once as qualification

c, s, b = st.client, st.s, st.b
od = st.od
OUT = Path(os.environ["OD_START_OUT"])
METRICS = {"audio": 0, "nj": 0, "visual": 0, "verifications": 0, "native_complete": False}


class Controls:
    def __init__(self, fail=False):
        self.ended = False
        self.session = None
        self.calls = []
        self.gates = []
        self.fail = fail
        self.closes = self.verifications = 0

    def command(self, name):
        self.calls.append(name)
        self.gates.append(od.MAIN_GATE)
        if name == "open":
            self.session = object()
        elif name in ("abort", "close") or self.fail:
            self.ended = True
            self.closes += 1
            self.verifications += 1
            if self.fail:
                raise c.ClientError("PRIMARY_NEUTRAL")
        return name


def feed(values):
    it = iter(values)
    def read(prompt):
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    return read


class StarterTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        od.MAIN_GATE = False
        s.prior.save(OUT / "metrics.json", dict(METRICS, gates=False))

    def tearDown(self):
        od.MAIN_GATE = False

    def test_01_commands(self):
        t = Controls()
        hashes = st.drive(t, ("open", "next", "status", "close"),
                          feed(("next", "open", "next", "open", "status", "close")), lambda text: None)
        self.assertEqual(t.calls, ["open", "next", "status", "close"])
        self.assertEqual(t.gates, [True, False, False, False])
        self.assertEqual(hashes, [st.hash_text("next")])
        self.assertEqual((t.closes, t.verifications), (1, 1))

    def test_02_eof_before_open(self):
        t = Controls()
        self.assertEqual(st.drive(t, st.COMMANDS, feed(()), print), [])
        self.assertEqual(t.calls, [])
        self.assertFalse(od.MAIN_GATE)

    def test_03_eof_after_open(self):
        t = Controls()
        st.drive(t, st.COMMANDS, feed(("open",)), lambda text: None)
        self.assertEqual(t.calls, ["open", "abort"])
        self.assertEqual((t.closes, t.verifications), (1, 1))

    def test_04_primary_error(self):
        t = Controls(fail=True)
        with self.assertRaises(c.ClientError) as found:
            st.drive(t, st.COMMANDS, feed(("open", "next")), lambda text: None)
        self.assertEqual(found.exception.code, "PRIMARY_NEUTRAL")
        self.assertEqual((t.closes, t.verifications), (1, 1))
        self.assertFalse(od.MAIN_GATE)

    def test_05_display_failure_closes(self):
        t = Controls()
        def write(text):
            raise OSError("neutral terminal unavailable")
        with self.assertRaises(OSError):
            st.drive(t, st.COMMANDS, feed(("open",)), write)
        self.assertEqual(t.calls, ["open", "abort"])
        self.assertEqual(t.verifications, 1)

    def test_06_independent_projection(self):
        step = dict(perception_status="P", memory_status="M", context_status="C",
                    hypothesis={"area": "A_RECENT", "values": [0.25]}, error_codes=[])
        original = deepcopy(step)
        with patch.object(c, "render_step", side_effect=AssertionError("renderer forbidden")):
            shown = json.loads(st.independent_display(step, 2, 7))
        self.assertEqual(shown, dict(progress="2/7", perception="P", memory="M", context="C",
                                    hypothesis=step["hypothesis"], errors=[]))
        self.assertEqual(step, original)

    def assessment_fixture(self, complete=True):
        step = dict(perception_status="P", memory_status="READ_ONLY", context_status="ABSTAIN_NO_CONTEXT",
                    hypothesis=None, error_codes=[])
        common = {"manifest": {"events": [{}]}}
        record = dict(status="RECORDING_COMPLETE" if complete else "NOT_EVALUABLE", record_digest="r",
                      execution={"rows": [{"step": step}]})
        session = {"session_digest": "q"}
        proof = dict(common_sha256=s.sha(b.canonical(common)), session_digest="q",
                     evaluation_allowed=complete, core={"record_digest": "r"})
        return step, common, record, session, b.sealed(proof, "verification_digest")

    def test_07_display_mismatch_visible(self):
        step, common, record, session, proof = self.assessment_fixture()
        with patch.object(s, "read_json", return_value=proof), patch.object(s, "unpack", return_value=(record, session)), \
             patch.object(st, "evaluate", return_value={"status": "CONFIRMED"}), \
             patch.object(c.verification, "verify_once", side_effect=AssertionError("second verifier")):
            result = st.assess(common, {}, ["0" * 64])
        self.assertEqual(result["display_equal"], [False])
        self.assertEqual(result["functional"]["status"], "CONFIRMED")

    def test_08_no_premature_evaluation(self):
        step, common, record, session, proof = self.assessment_fixture(False)
        with patch.object(s, "read_json", return_value=proof), patch.object(s, "unpack", return_value=(record, session)), \
             patch.object(st, "evaluate", side_effect=AssertionError("evaluation forbidden")):
            self.assertIsNone(st.assess(common, {}, []))

    def test_09_authorization_closed(self):
        release = b.sealed(dict(run_id=st.RUN_ID, execution_authorized=False), "release_digest")
        with patch.object(s, "read_json", return_value=release):
            with self.assertRaises(c.ClientError) as found:
                st.load_release()
        self.assertEqual(found.exception.code, "START_NOT_AUTHORIZED")
        self.assertFalse(od.MAIN_GATE)

    def test_10_changed_starter(self):
        release = b.sealed(dict(run_id=st.RUN_ID, execution_authorized=True, starter=[]), "release_digest")
        with patch.object(s, "read_json", return_value=release):
            with self.assertRaises(c.ClientError) as found:
                st.load_release()
        self.assertEqual(found.exception.code, "START_SOURCE_CHANGED")

    def test_11_reserved_forms(self):
        prepared = s.read_json(OUT / "preparation.json")
        self.assertFalse(prepared["violations"])
        self.assertLessEqual(prepared["assessment_shape_bytes"], st.CAPS["evaluation"])
        self.assertEqual(len(prepared["run_positions"]), 8)
        self.assertEqual(len(prepared["native_positions"]), 3)
        self.assertEqual(prepared["qualification_metadata_limit"], 73728)
        for session_bytes, extra_bytes, expected in (
                (65536, 8192, []), (65536, 8193, ["QUALIFICATION_METADATA_LIMIT"]),
                (65537, 0, ["SESSION_METADATA_LIMIT"])):
            with self.subTest(session=session_bytes, qualification_extra=extra_bytes):
                totals = dict.fromkeys(od.LIMITS, 0)
                totals.update(metadata=session_bytes, total=session_bytes)
                checked = qualification.qualification_totals(totals, [("metadata", "neutral-extra", extra_bytes)])
                self.assertEqual(checked["violations"], expected)
                self.assertEqual(checked["totals"]["metadata"], session_bytes+extra_bytes)
                self.assertEqual(checked["session"], totals)
        self.assertEqual(b.LIMITS["sources"], 174080)
        self.assertEqual(dict(od.LIMITS), dict(b.LIMITS, sources=196608))
        for size, expected in ((196608, []), (196609, ["SOURCES_LIMIT"])):
            with self.subTest(source_bytes=size):
                totals = dict.fromkeys(od.LIMITS, 0)
                totals.update(sources=size, shared=size, total=size)
                self.assertEqual(od.violations(totals), expected)
        with self.subTest(shared_limit_unchanged=True):
            totals = dict.fromkeys(od.LIMITS, 0)
            totals.update(sources=196608, shared=262145, total=262145)
            self.assertEqual(od.violations(totals), ["SHARED_LIMIT"])
        common = s.read_json(OUT / "native-common.json")
        self.assertEqual(od.validate_policy(common), s.sha(b.canonical(od.policy())))
        for altered in ([], [["metadata", "missing/od-budget.json", 0, "0"*64]]):
            with self.subTest(policy=altered):
                changed = deepcopy(common)
                changed["references"] = [r for r in changed["references"] if Path(r[1]).name != od.POLICY_NAME] + altered
                if not altered:
                    with self.assertRaises(c.ClientError) as found:
                        od.validate_policy(changed)
                    self.assertEqual(found.exception.code, "OD_BUDGET_BINDING_INVALID")
                else:
                    with patch.object(s, "file_reference", return_value=[]):
                        with self.assertRaises(c.ClientError) as found:
                            od.validate_policy(changed)
                    self.assertEqual(found.exception.code, "OD_BUDGET_BINDING_INVALID")

    def test_12_native_session(self):
        native = OUT / "native"
        binding = OUT / "native-common.json"
        common = s.read_json(binding)
        inv_path = b.ROOT / "reports/s2oc" / s.QUAL_ID / "inventory.json"
        inputs = b.ROOT / "sources/s2od-neutral" / st.QUAL_ID
        inputs.mkdir(parents=True, exist_ok=False)
        for name, raw in (("window.pcm", b"\0" * 19200), ("frame.rgb", bytes((36,84,132)) * (1920*1080))):
            path = inputs / name
            path.write_bytes(raw)
            spec = next(p for e in common["manifest"]["events"] for p in (e["pcm"], e["rgb"])
                        if p is not None and p["path"] == path.relative_to(b.ROOT).as_posix())
            self.assertEqual(s.sha(raw), spec["sha256"])
            del raw
        original_open = Path.open
        def guard(path, mode="r", *args, **kwargs):
            if "r" in mode and path.suffix in (".pcm", ".rgb", ".bin"):
                if not path.resolve().is_relative_to(inputs):
                    raise AssertionError("NON_NEUTRAL_PAYLOAD_FORBIDDEN")
            return original_open(path, mode, *args, **kwargs)
        calls = []
        patches = [patch.object(Path, "open", guard)]
        for owner, name, metric in ((b.r.half.spectral.LogSpectralReceptor, "analyze", "audio"),
                                  (b.LocalChannelGridReceptor, "analyze", "visual"),
                                  (b.r.half, "project_auditory_half_v1", "nj"),
                                  (od, "verify_once", "verifications")):
            original = getattr(owner, name)
            def count(*args, _original=original, _metric=metric, **kwargs):
                METRICS[_metric] += 1
                return _original(*args, **kwargs)
            patches.append(patch.object(owner, name, count))
        try:
            for p in patches:
                p.start()
            terminal = od.TerminalClient(binding, s.sha(b.canonical(common)), inv_path, native)
            commands = ("open", "next", "status", "next", "status", "close")
            hashes = st.drive(terminal, commands, feed(commands), calls.append)
            proof = s.read_json(native / "verification.json")
            self.assertTrue(proof["evaluation_allowed"])
            record, session = s.unpack(s.read_json(native / "record.json"), s.read_json(native / "session.json"), common)
            self.assertEqual(record["status"], "RECORDING_COMPLETE")
            rows = record["execution"]["rows"]
            self.assertEqual(hashes, [st.hash_text(st.independent_display(row["step"], n, 2)) for n,row in enumerate(rows,1)])
            self.assertEqual(rows[1]["pre"]["memory_state_digest"], rows[1]["memory"])
            self.assertIsNotNone(rows[0]["formation"])
            plan = dict(evaluation_digest="0"*64, decisions=[], formations=[])
            result = st.assess(common, plan, hashes, native)
            self.assertTrue(all(result["display_equal"]))
            self.assertEqual(METRICS, dict(audio=2,nj=2,visual=1,verifications=1,native_complete=False))
            balance = st.finish(common, native, result, None)
            self.assertFalse(balance["violations"])
            self.assertTrue(terminal.ended)
            with self.assertRaises(c.ClientError):
                terminal.command("open")
            self.assertEqual(METRICS["verifications"], 1)
            METRICS["native_complete"] = True
        finally:
            od.MAIN_GATE = False
            for p in reversed(patches):
                p.stop()
