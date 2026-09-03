from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools import _s2ks_real_partial_cue_fixtures as fixtures
from tools import _s2ks_real_partial_cue_runner as runner
from tools import _s2ks_real_partial_cue_verifier as verifier
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile


ROOT = Path(__file__).resolve().parents[1]


def _write(root: Path, record: dict[str, object]) -> Path:
    directory = root / "s2ks-neutral-record"
    runner.write_atomic_result(directory.resolve(), record)
    return directory.resolve()


def _reseal(record: dict[str, object]) -> dict[str, object]:
    payload = {key: value for key, value in record.items() if key != "record_digest"}
    return runner._sealed(payload)


class S2KSRealPartialCueRunnerQualificationTests(unittest.TestCase):
    def test_01_bound_plan_has_five_histories_59_formations_and_eight_cues(self) -> None:
        self.assertEqual((15, 14, 2, 11, 17), tuple(len(value) for value in fixtures.HISTORIES.values()))
        self.assertEqual(59, fixtures.FORMATION_COUNT)
        self.assertEqual(8, len(fixtures.CASE_EXECUTION))
        self.assertEqual(set(fixtures.CASE_ORDER), set(runner.EVALUATION_TARGETS))
        self.assertTrue(all(len(fixtures.evaluation_target_masked_values(recipe)) == 256 for recipe in runner.EVALUATION_TARGETS.values()))
        self.assertEqual(0, runner.neutral_qualification_record(ROOT)["memory_formation_calls"])

    def test_02_no_full_probe_or_context_projection_path_exists(self) -> None:
        for relative in (
            "tools/_s2ks_real_partial_cue_fixtures.py",
            "tools/_s2ks_real_partial_cue_runner.py",
            "tools/_s2ks_real_partial_cue_verifier.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8")
            tree = ast.parse(source)
            names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
            self.assertNotIn("bind_s2jv_probe", names)
            self.assertNotIn("probe_s2jv_composite_read_only", names)
            self.assertNotIn("project_two_area_perceptual_context_336", names)
        self.assertEqual(0, runner.neutral_qualification_record(ROOT)["plan"]["full_probe_count"])

    def test_03_occluded_rgb_is_the_only_analyzed_cue_source(self) -> None:
        profile = build_s2jw_default_live_profile()
        config = runner._build_config()
        cue, receipt = fixtures.materialize_masked_cue(
            profile=profile, history_id="neutral", cue_id="cue-neutral-a",
            ordinal=0, visible_recipe_id="FT", config_digest=config.config_digest,
        )
        image = fixtures.occluded_visual_image("FT")
        grid = image.reshape(8, 135, 12, 160, 3)
        means = grid.mean(axis=(1, 3)).reshape(-1)
        self.assertEqual(127.5, means[0])
        self.assertTrue(np.all(means[32:] == fixtures.OCCLUDER_BYTE))
        self.assertEqual(tuple(range(32)), cue.visible_positions)
        self.assertTrue(all(cue.values[index] is None for index in range(32, 288)))
        self.assertEqual(receipt.occluded_rgb_digest, hashlib.sha256(image.tobytes(order="C")).hexdigest())

    def test_04_byte_block_recipes_materialize_exact_bound_carrier_values(self) -> None:
        def values(recipe: str) -> np.ndarray:
            image = fixtures.visual_image(recipe)
            return image.reshape(8, 135, 12, 160, 3).mean(axis=(1, 3)).reshape(-1) / 255.0
        self.assertEqual((0.75, 0.0), (values("FC0")[0], values("FC0")[32]))
        self.assertEqual((0.25, 1.0), (values("FC1")[0], values("FC1")[32]))
        self.assertEqual((1.0, 0.0), (values("FU")[0], values("FU")[32]))
        self.assertEqual((0.25, 0.0), (values("FV")[0], values("FV")[32]))
        self.assertEqual((0.5, 1.0), (values("FT")[0], values("FT")[32]))
        self.assertTrue(np.all(values("S0") == 0.0))
        self.assertTrue(np.all(values("S1")[:32] == 0.0))
        self.assertTrue(np.all(values("S1")[32:] == 1.0))

    def test_05_neutral_pipeline_scans_all_slots_without_formation(self) -> None:
        record = runner.neutral_qualification_record(ROOT)
        case = record["cases"][0]
        self.assertEqual("ABSTAIN_NO_CONTEXT", case["primary"]["decision"])
        self.assertEqual(case["primary"], case["baseline"])
        self.assertEqual(16, case["primary"]["total_slot_scans"])
        self.assertLessEqual(case["primary"]["total_value_comparisons"], 800)
        self.assertTrue(case["read_only"])

    def test_06_main_gate_is_closed(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(runner.S2KSRunnerError, "gate is closed"):
                runner.run_main_once(Path(temporary).resolve(), ROOT, runner.AUTHORIZED_RUN_ID)
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)

    def test_07_atomic_record_and_independent_verification_succeed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _write(Path(temporary), runner.neutral_qualification_record(ROOT))
            finding = verifier.verify_s2ks_result(directory, ROOT)
        self.assertEqual(("RECORDING_COMPLETE", None, ()), (finding.status, finding.functional_status, finding.issues))

    def test_08_reuse_and_non_path_inputs_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary).resolve() / "record"
            runner.write_atomic_result(directory, runner.neutral_qualification_record(ROOT))
            with self.assertRaises(runner.S2KSRunnerError):
                runner.write_atomic_result(directory, runner.neutral_qualification_record(ROOT))
            finding = verifier.verify_s2ks_result(str(directory), ROOT)  # type: ignore[arg-type]
            self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_09_digest_and_case_mutations_are_rejected(self) -> None:
        for mutation in ("digest", "case"):
            record = copy.deepcopy(runner.neutral_qualification_record(ROOT))
            if mutation == "digest":
                record["record_digest"] = "0" * 64
            else:
                record["cases"][0]["poststate_digest"] = "0" * 64
                record = _reseal(record)
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                finding = verifier.verify_s2ks_result(_write(Path(temporary), record), ROOT)
                self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_10_missing_extra_and_raw_artifacts_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            empty = root / "empty"
            empty.mkdir()
            self.assertEqual("NOT_EVALUABLE", verifier.verify_s2ks_result(empty.resolve(), ROOT).status)
            directory = _write(root, runner.neutral_qualification_record(ROOT))
            (directory / "extra.json").write_text("{}", encoding="ascii")
            self.assertEqual("NOT_EVALUABLE", verifier.verify_s2ks_result(directory, ROOT).status)
        record = runner.neutral_qualification_record(ROOT)
        record["raw_bytes"] = [0]
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual("NOT_EVALUABLE", verifier.verify_s2ks_result(_write(Path(temporary), _reseal(record)), ROOT).status)

    def test_11_source_hash_mutation_is_rejected(self) -> None:
        for mutation in ("changed", "missing"):
            record = runner.neutral_qualification_record(ROOT)
            first = next(iter(record["source_hashes"]))
            if mutation == "changed":
                record["source_hashes"][first] = "0" * 64
            else:
                del record["source_hashes"][first]
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                finding = verifier.verify_s2ks_result(_write(Path(temporary), _reseal(record)), ROOT)
            self.assertEqual("NOT_EVALUABLE", finding.status)

    def test_12_private_surface_and_result_exclude_raw_or_target_values(self) -> None:
        record = runner.neutral_qualification_record(ROOT)
        encoded = json.dumps(record, sort_keys=True)
        for forbidden in ("raw_payload", "rgb_bytes", "pcm_samples", "target_values", "visual_values", "auditory_values"):
            self.assertNotIn(f'"{forbidden}"', encoded)
        self.assertEqual((), fixtures.__all__)
        self.assertEqual((), runner.__all__)
        self.assertEqual((), verifier.__all__)


if __name__ == "__main__":
    unittest.main()
