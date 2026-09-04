from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools import _s2ld_auditory_partial_cue_fixtures as fixtures
from tools import _s2ld_auditory_partial_cue_runner as runner
from tools import _s2ld_auditory_partial_cue_verifier as verifier


ROOT = Path(__file__).resolve().parents[1]


def _reseal(record: dict[str, object]) -> dict[str, object]:
    payload = {key: value for key, value in record.items() if key != "record_digest"}
    return runner._sealed(payload)


def _write(root: Path, record: dict[str, object], name: str = "s2ld-neutral-record") -> Path:
    directory = (root / name).resolve()
    runner.write_atomic_result(directory, record)
    return directory


class S2LDAuditoryPartialCueRunnerQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.product_hashes_before = {
            relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            for relative in runner.SOURCE_PATHS
            if relative.startswith("tools/_s2ld_")
        }
        cls.record = runner.neutral_qualification_record(ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        after = {
            relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            for relative in runner.SOURCE_PATHS
            if relative.startswith("tools/_s2ld_")
        }
        if after != cls.product_hashes_before:
            raise AssertionError("S2-LD product hashes changed during qualification")

    def test_01_bound_main_shape_is_30_formations_and_six_cues(self) -> None:
        self.assertEqual((1, 13, 14, 2), tuple(len(value) for value in fixtures.HISTORIES.values()))
        self.assertEqual(30, fixtures.FORMATION_COUNT)
        self.assertEqual(30, runner.FORMATION_COUNT_BOUND)
        self.assertEqual(6, len(fixtures.CASE_EXECUTION))
        self.assertEqual(fixtures.CASE_ORDER, tuple(runner.EXPECTED_CASES))
        self.assertEqual(85, runner.MAIN_FUNCTIONAL_OPERATION_COUNT)
        self.assertLessEqual(runner.MAIN_FUNCTIONAL_OPERATION_COUNT, runner.MAIN_FUNCTIONAL_OPERATION_LIMIT)

    def test_02_pcm_recipes_are_literal_and_digest_bound(self) -> None:
        for role in ("L", "P", "M", "H", "D_FAR"):
            with self.subTest(role=role):
                values = fixtures.auditory_pcm(role)
                self.assertEqual(4_800, len(values))
                self.assertTrue(all(-1.0 <= value <= 1.0 for value in values))
        self.assertNotEqual(fixtures.auditory_pcm("L"), fixtures.auditory_pcm("D_FAR"))

    def test_03_neutral_cue_uses_real_pcm_receptor_and_native_audio_time(self) -> None:
        case = self.record["cases"][0]
        source = case["cue_source"]
        self.assertEqual("audio.sample", source["auditory_source_clock_id"])
        self.assertEqual((0, 4_800), (source["auditory_window_start_tick"], source["auditory_window_end_tick"]))
        self.assertEqual(source["cue_digest"], case["cue_digest"])
        self.assertRegex(source["pcm_payload_digest"], r"^[0-9a-f]{64}$")
        self.assertRegex(source["receptor_values_digest"], r"^[0-9a-f]{64}$")
        self.assertRegex(source["observed_values_digest"], r"^[0-9a-f]{64}$")

    def test_04_neutral_scan_is_complete_read_only_and_baseline_equal(self) -> None:
        case = self.record["cases"][0]
        self.assertEqual("ABSTAIN_NO_CONTEXT", case["primary"]["decision"])
        self.assertEqual(case["primary"], case["baseline"])
        self.assertEqual(20, case["primary"]["total_slot_scans"])
        self.assertLessEqual(case["primary"]["total_value_comparisons"], 528)
        self.assertEqual(0, case["primary"]["memory_receptor_consumer_context_or_field_calls"])
        self.assertTrue(case["read_only"])
        self.assertEqual(case["prestate_digest"], case["poststate_digest"])
        self.assertEqual(0, self.record["memory_formation_calls"])

    def test_05_main_gate_is_closed_and_resets_without_side_effect(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            with self.assertRaisesRegex(runner.S2LDRunnerError, "gate is closed"):
                runner.run_main_once(root, ROOT, runner.AUTHORIZED_RUN_ID)
            self.assertEqual([], list(root.iterdir()))
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)

    def test_06_qualification_plan_contains_no_history_or_full_probe(self) -> None:
        self.assertEqual(
            {
                "fresh_memory_state_count": 1,
                "formation_count": 0,
                "masked_cue_count": 1,
                "full_probe_count": 0,
                "primary_decision_count": 1,
                "baseline_decision_count": 1,
                "functional_operation_count": 5,
            },
            self.record["plan"],
        )
        self.assertEqual([], self.record["formations"])
        self.assertIsNone(self.record["functional_evaluation"])

    def test_07_atomic_result_and_independent_verification_succeed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write(Path(temporary), copy.deepcopy(self.record))
            finding = verifier.verify_s2ld_result(directory, ROOT)
            self.assertEqual({"result.json"}, {item.name for item in directory.iterdir()})
            self.assertLessEqual((directory / "result.json").stat().st_size, runner.MAX_RESULT_BYTES)
        self.assertEqual(("RECORDING_COMPLETE", None, ()), (finding.status, finding.functional_status, finding.issues))

    def test_08_reuse_string_path_and_oversize_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = _write(root, copy.deepcopy(self.record))
            with self.assertRaises(runner.S2LDRunnerError):
                runner.write_atomic_result(directory, copy.deepcopy(self.record))
            self.assertEqual("NOT_EVALUABLE", verifier.verify_s2ld_result(str(directory), ROOT).status)  # type: ignore[arg-type]
            oversize = copy.deepcopy(self.record)
            oversize["padding"] = "x" * runner.MAX_RESULT_BYTES
            with self.assertRaises(runner.S2LDRunnerError):
                runner.write_atomic_result((root / "oversize").resolve(), _reseal(oversize))
            self.assertFalse((root / "oversize").exists())

    def test_09_record_and_cue_digest_mutations_are_rejected(self) -> None:
        for mutation in ("record", "cue"):
            record = copy.deepcopy(self.record)
            if mutation == "record":
                record["record_digest"] = "0" * 64
            else:
                record["cases"][0]["cue_source"]["cue_digest"] = "0" * 64
                record = _reseal(record)
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                finding = verifier.verify_s2ld_result(_write(Path(temporary), record), ROOT)
            self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_10_missing_extra_and_raw_artifacts_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            empty = (root / "empty").resolve()
            empty.mkdir()
            self.assertEqual("NOT_EVALUABLE", verifier.verify_s2ld_result(empty, ROOT).status)
            directory = _write(root, copy.deepcopy(self.record), "extra")
            (directory / "extra.json").write_text("{}", encoding="ascii")
            self.assertEqual("NOT_EVALUABLE", verifier.verify_s2ld_result(directory, ROOT).status)
        raw = copy.deepcopy(self.record)
        raw["pcm_samples"] = [0.0]
        with tempfile.TemporaryDirectory() as temporary:
            finding = verifier.verify_s2ld_result(_write(Path(temporary), _reseal(raw)), ROOT)
        self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_11_plan_count_and_read_only_mutations_are_rejected(self) -> None:
        mutations = []
        changed_plan = copy.deepcopy(self.record)
        changed_plan["plan"]["formation_count"] = 1
        mutations.append(changed_plan)
        changed_count = copy.deepcopy(self.record)
        changed_count["memory_formation_calls"] = 1
        mutations.append(changed_count)
        changed_state = copy.deepcopy(self.record)
        changed_state["cases"][0]["poststate_digest"] = "0" * 64
        mutations.append(changed_state)
        for ordinal, record in enumerate(mutations):
            with self.subTest(ordinal=ordinal), tempfile.TemporaryDirectory() as temporary:
                finding = verifier.verify_s2ld_result(_write(Path(temporary), _reseal(record)), ROOT)
            self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_12_source_set_and_source_digest_mutations_are_rejected(self) -> None:
        for mutation in ("missing", "changed"):
            record = copy.deepcopy(self.record)
            first = next(iter(record["source_hashes"]))
            if mutation == "missing":
                del record["source_hashes"][first]
            else:
                record["source_hashes"][first] = "0" * 64
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                finding = verifier.verify_s2ld_result(_write(Path(temporary), _reseal(record)), ROOT)
            self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_13_static_surface_has_no_full_probe_context_or_field_path(self) -> None:
        for relative in (
            "tools/_s2ld_auditory_partial_cue_fixtures.py",
            "tools/_s2ld_auditory_partial_cue_runner.py",
            "tools/_s2ld_auditory_partial_cue_verifier.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8")
            tree = ast.parse(source)
            names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
            self.assertNotIn("bind_s2jv_probe", names)
            self.assertNotIn("probe_s2jv_composite_read_only", names)
            self.assertNotIn("project_two_area_perceptual_context_336", names)
        self.assertEqual(0, self.record["plan"]["full_probe_count"])

    def test_14_private_output_is_bounded_and_contains_no_raw_or_target_values(self) -> None:
        encoded = json.dumps(self.record, sort_keys=True)
        for forbidden in (
            '"raw_payload"',
            '"rgb_bytes"',
            '"pcm_samples"',
            '"target_values"',
            '"auditory_values"',
            '"visual_values"',
            '"observed_values"',
            '"proposed_values"',
        ):
            self.assertNotIn(forbidden, encoded)
        self.assertLess(len(encoded.encode("ascii")), runner.MAX_RESULT_BYTES)
        self.assertEqual((), fixtures.__all__)
        self.assertEqual((), runner.__all__)
        self.assertEqual((), verifier.__all__)


if __name__ == "__main__":
    unittest.main()
