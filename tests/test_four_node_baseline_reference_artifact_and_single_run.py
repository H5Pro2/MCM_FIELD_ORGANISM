"""S1-TD synthetic v2 tests. Defined here; first execution is reserved for S1-TE."""

from __future__ import annotations

import ast
from dataclasses import replace
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from mcm_field_organism.four_node_baseline_reference_artifact import (
    AUTHORIZATION, INPUT_FILES,
    build_baseline_reference_artifact_bytes,
    build_baseline_reference_input_file_digests,
    build_baseline_reference_source_inventory, parse_baseline_reference_artifact,
)
from mcm_field_organism.four_node_baseline_reference_comparator import (
    COMPUTABLE, INVALID, SOURCE_ARTIFACT_DIGEST, SOURCE_MATRIX_RESULT_DIGEST,
    compare_four_node_baseline_reference,
    build_comparator_input, build_profile,
    validate_four_node_baseline_reference_result,
)
from mcm_field_organism.four_node_matrix_artifact import (
    FourNodeSourceFileDigest, FourNodeSourceInventory, canonical_json_bytes,
)
from mcm_field_organism import four_node_baseline_reference_single_run as runner
from tests.test_four_node_baseline_reference_comparator import synthetic_input


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = (
    ("python_implementation", "CPython"), ("python_major_minor_micro", "3.14.0"),
    ("platform_system", "Synthetic"), ("platform_machine", "fixture"),
)
INPUTS = tuple((path, str(index) * 64) for index, path in enumerate(INPUT_FILES, 1))
IDENTITY = (
    ("source_artifact_file_sha256", "1" * 64), ("source_artifact_digest", SOURCE_ARTIFACT_DIGEST),
    ("matrix_result_digest", SOURCE_MATRIX_RESULT_DIGEST), ("manifest_file_sha256", "2" * 64),
    ("registration_file_sha256", "3" * 64), ("fresh_manifest_digest", "6" * 64),
    ("matrix_registration_digest", "7" * 64), ("exposure_fixture_digest", "8" * 64),
    ("axis_digest", "9" * 64), ("comparator_input_digest", synthetic_input().input_digest),
)


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _inventory(suffix: str = "b") -> FourNodeSourceInventory:
    files = (FourNodeSourceFileDigest("mcm_field_organism/synthetic_atlas_source.py", suffix * 64),)
    return FourNodeSourceInventory(files, _digest(tuple((item.relative_path, item.sha256) for item in files)))


def _identity(source):
    return IDENTITY[:-1] + (("comparator_input_digest", source.input_digest),)


def _result(source=None):
    return compare_four_node_baseline_reference(synthetic_input() if source is None else source)


def _replace_checkpoint(source, profile_indexes, plan_role, checkpoint_role, **changes):
    profiles = list(source.profiles)
    for profile_index in profile_indexes:
        profile = profiles[profile_index]
        checkpoints = list(profile.checkpoints)
        checkpoint_index = next(
            index for index, item in enumerate(checkpoints)
            if (item.plan_role, item.checkpoint_role) == (plan_role, checkpoint_role)
        )
        checkpoints[checkpoint_index] = replace(checkpoints[checkpoint_index], **changes)
        profiles[profile_index] = build_profile(
            profile.role_position, profile.model_role, profile.configuration_digest,
            tuple(checkpoints),
        )
    return build_comparator_input(source.artifact_digest, source.matrix_result_digest, tuple(profiles))


def _nullable_input():
    source = synthetic_input()
    return _replace_checkpoint(
        source, range(14), "C_GAP", "POST_COMPETITION",
        receptor_contact=(None, None, None, None),
    )


def _artifact_bytes(source=None) -> bytes:
    source = synthetic_input() if source is None else source
    return build_baseline_reference_artifact_bytes(
        _result(source), _inventory(), INPUTS, _identity(source),
        authorization=AUTHORIZATION, runtime_identity=RUNTIME,
    )


def _project(parent: Path) -> Path:
    project = parent / "project"
    (project / "reports").mkdir(parents=True)
    return project


def _preflight(project: Path):
    root, paths = runner._paths(project)
    return root, paths, _inventory(), INPUTS, synthetic_input(), IDENTITY


class FourNodeBaselineReferenceArtifactAndSingleRunTests(unittest.TestCase):
    def test_01_result_contains_complete_profile_and_pair_provenance(self):
        result = _result()
        self.assertEqual((len(result.profiles), len(result.pairs)), (14, 91))
        self.assertTrue(all(len(item.left_checkpoint_digests) == 40 for item in result.pairs))

    def test_02_fully_numeric_receptor_provenance_remains_valid(self):
        result = _result()
        validate_four_node_baseline_reference_result(result)
        self.assertEqual(result.status, COMPUTABLE)

    def test_03_bound_all_null_receptor_provenance_roundtrips(self):
        source = _nullable_input()
        result = _result(source)
        raw = _artifact_bytes(source)
        self.assertEqual((result.status, parse_baseline_reference_artifact(raw).result), (COMPUTABLE, result))
        self.assertIn(b'"receptor_contact":[null,null,null,null]', raw)

    def test_04_mixed_null_receptor_provenance_is_invalid(self):
        source = _replace_checkpoint(
            synthetic_input(), (0,), "C_GAP", "POST_COMPETITION",
            receptor_contact=(None, 0.0, None, 0.0),
        )
        self.assertEqual(_result(source).status, INVALID)

    def test_05_all_null_receptor_provenance_at_other_location_is_invalid(self):
        source = _replace_checkpoint(
            synthetic_input(), (0,), "F_A", "POST_PROBE_READOUT",
            receptor_contact=(None, None, None, None),
        )
        self.assertEqual(_result(source).status, INVALID)

    def test_06_none_in_activation_or_afterimage_is_invalid(self):
        for channel in ("activation", "afterimage"):
            with self.subTest(channel=channel):
                source = _replace_checkpoint(
                    synthetic_input(), (0,), "F_A", "POST_PROBE_READOUT",
                    **{channel: (None, 0.0, 0.0, 0.0)},
                )
                self.assertEqual(_result(source).status, INVALID)

    def test_07_absence_and_explicit_zero_contact_remain_distinct(self):
        source = _replace_checkpoint(
            synthetic_input(), (0,), "C_GAP", "POST_COMPETITION",
            receptor_contact=(None, None, None, None),
        )
        self.assertEqual(_result(source).status, INVALID)

    def test_08_artifact_is_deterministic_and_retains_pair_provenance(self):
        first, second = _artifact_bytes(), _artifact_bytes()
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertIn(b'"left_checkpoint_digests"', first)

    def test_09_source_inventory_is_deterministic_and_local(self):
        first = build_baseline_reference_source_inventory(ROOT)
        self.assertEqual(first, build_baseline_reference_source_inventory(ROOT))
        self.assertTrue(all(item.relative_path.startswith("mcm_field_organism/") for item in first.files))

    def test_10_input_file_digest_axis_is_fixed(self):
        records = build_baseline_reference_input_file_digests(ROOT)
        self.assertEqual(tuple(path for path, _ in records), INPUT_FILES)

    def test_11_wrong_authorization_stops_without_run_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = _project(Path(temporary))
            with self.assertRaises(runner.FourNodeBaselineReferenceSingleRunError):
                runner.run_baseline_reference_atlas_once(project, "wrong")
            self.assertFalse(any((project / path).exists() for path in (runner.RESULT, runner.ATTEMPT, runner.LOCK, runner.STAGING)))

    def test_12_preserved_s1tb_belege_do_not_block_new_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = _project(Path(temporary))
            old_attempt = project / "reports/s1tb_baseline_reference_atlas_once_v1.attempt.json"
            old_lock = project / "reports/s1tb_baseline_reference_atlas_once_v1.lock"
            old_attempt.write_bytes(b"preserved-attempt")
            old_lock.write_bytes(b"preserved-lock")
            _, paths = runner._paths(project)
            self.assertEqual((old_attempt.read_bytes(), old_lock.read_bytes()), (b"preserved-attempt", b"preserved-lock"))
            self.assertFalse(any(path.exists() for path in (paths.result, paths.attempt, paths.lock, paths.staging)))

    def test_13_success_calls_comparator_once_and_publishes(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = _project(Path(temporary))
            comparator = Mock(return_value=_result())
            with (
                patch.object(runner, "_preflight", return_value=_preflight(project)),
                patch.object(runner, "build_baseline_reference_source_inventory", return_value=_inventory()),
                patch.object(runner, "build_baseline_reference_input_file_digests", return_value=INPUTS),
                patch.object(runner, "four_node_runtime_identity", return_value=RUNTIME),
                patch.object(runner, "compare_four_node_baseline_reference", comparator),
            ):
                artifact = runner.run_baseline_reference_atlas_once(project, AUTHORIZATION)
            comparator.assert_called_once()
            self.assertTrue((project / runner.RESULT).is_file())
            self.assertEqual(artifact.result, _result())

    def test_14_not_computable_keeps_attempt_and_lock_without_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = _project(Path(temporary))
            with (
                patch.object(runner, "_preflight", return_value=_preflight(project)),
                patch.object(runner, "compare_four_node_baseline_reference", return_value=compare_four_node_baseline_reference(None)),
            ):
                with self.assertRaises(runner.FourNodeBaselineReferenceSingleRunError):
                    runner.run_baseline_reference_atlas_once(project, AUTHORIZATION)
            self.assertTrue((project / runner.ATTEMPT).is_file() and (project / runner.LOCK).is_file())
            self.assertFalse((project / runner.RESULT).exists())

    def test_15_started_exception_keeps_attempt_and_lock(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = _project(Path(temporary))
            with (
                patch.object(runner, "_preflight", return_value=_preflight(project)),
                patch.object(runner, "compare_four_node_baseline_reference", side_effect=RuntimeError("synthetic")),
            ):
                with self.assertRaises(runner.FourNodeBaselineReferenceSingleRunError):
                    runner.run_baseline_reference_atlas_once(project, AUTHORIZATION)
            self.assertTrue((project / runner.ATTEMPT).exists() and (project / runner.LOCK).exists())

    def test_16_source_drift_blocks_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = _project(Path(temporary))
            with (
                patch.object(runner, "_preflight", return_value=_preflight(project)),
                patch.object(runner, "build_baseline_reference_source_inventory", return_value=_inventory("c")),
                patch.object(runner, "build_baseline_reference_input_file_digests", return_value=INPUTS),
                patch.object(runner, "compare_four_node_baseline_reference", return_value=_result()),
            ):
                with self.assertRaises(runner.FourNodeBaselineReferenceSingleRunError):
                    runner.run_baseline_reference_atlas_once(project, AUTHORIZATION)
            self.assertFalse((project / runner.RESULT).exists())

    def test_17_result_link_failure_leaves_no_partial_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = _project(Path(temporary))
            with (
                patch.object(runner, "_preflight", return_value=_preflight(project)),
                patch.object(runner, "build_baseline_reference_source_inventory", return_value=_inventory()),
                patch.object(runner, "build_baseline_reference_input_file_digests", return_value=INPUTS),
                patch.object(runner, "four_node_runtime_identity", return_value=RUNTIME),
                patch.object(runner.os, "link", side_effect=OSError("synthetic")),
                patch.object(runner, "compare_four_node_baseline_reference", return_value=_result()),
            ):
                with self.assertRaises(runner.FourNodeBaselineReferenceSingleRunError):
                    runner.run_baseline_reference_atlas_once(project, AUTHORIZATION)
            self.assertFalse((project / runner.RESULT).exists())

    def test_18_runner_has_no_direct_model_producer_import(self):
        path = ROOT / "mcm_field_organism" / "four_node_baseline_reference_single_run.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertFalse(any("model_invocation" in item or "matrix_lifecycle" in item for item in imports))

    def test_19_cli_declares_only_authorization_option(self):
        path = ROOT / "mcm_field_organism" / "four_node_baseline_reference_single_run.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        options = [node.args[0].value for node in ast.walk(tree) if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument"
                   and node.args and isinstance(node.args[0], ast.Constant)]
        self.assertEqual(options, ["--authorization"])

    def test_20_output_paths_are_fixed_under_reports(self):
        self.assertEqual(
            (runner.RESULT, runner.ATTEMPT, runner.LOCK, runner.STAGING),
            ("reports/s1tg_baseline_reference_atlas_once_v2.json",
             "reports/s1tg_baseline_reference_atlas_once_v2.attempt.json",
             "reports/s1tg_baseline_reference_atlas_once_v2.lock",
             "reports/.s1tg_baseline_reference_atlas_once_v2.json.staging"),
        )


if __name__ == "__main__":
    unittest.main()
