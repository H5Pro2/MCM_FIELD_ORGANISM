from __future__ import annotations

import ast
from dataclasses import fields, replace
import hashlib
import json
from functools import lru_cache
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from mcm_field_organism import four_node_cell_lifecycle as cell_module
from mcm_field_organism import four_node_matrix_lifecycle as matrix_module
from mcm_field_organism.four_node_matrix_artifact import (
    AUTHORIZATION,
    FourNodeMatrixArtifactError,
    FourNodeSourceFileDigest,
    FourNodeSourceInventory,
    build_four_node_input_file_digests,
    build_four_node_matrix_artifact_bytes,
    build_four_node_source_inventory,
    canonical_json_bytes,
    parse_four_node_matrix_artifact,
)
from mcm_field_organism.four_node_matrix_lifecycle import (
    FourNodeMatrixLifecycleError,
    validate_four_node_matrix_result,
)
from mcm_field_organism.four_node_matrix_single_run import (
    ATTEMPT,
    LOCK,
    RESULT,
    STAGING,
    FourNodeMatrixSingleRunError,
    run_four_node_matrix_once,
)
from tests.test_four_node_matrix_lifecycle import _synthetic_matrix


ROOT = Path(__file__).resolve().parents[1]
RUNNER_MODULE = "mcm_field_organism.four_node_matrix_single_run"
RUNTIME = (
    ("python_implementation", "CPython"),
    ("python_major_minor_micro", "3.13.0"),
    ("platform_system", "Synthetic"),
    ("platform_machine", "fixture"),
)
INPUTS = (
    ("reports/s1rk_four_node_fresh_manifest.json", "1" * 64),
    ("reports/s1sd_four_node_fresh_matrix_registration.json", "2" * 64),
)


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _inventory(suffix: str = "0") -> FourNodeSourceInventory:
    files = (
        FourNodeSourceFileDigest(
            "mcm_field_organism/synthetic_matrix_source.py",
            suffix * 64,
        ),
    )
    return FourNodeSourceInventory(
        files,
        _digest(tuple((item.relative_path, item.sha256) for item in files)),
    )


@lru_cache(maxsize=1)
def _valid_matrix():
    source, _ = _synthetic_matrix()
    checkpoints = []
    for record in source.ordered_checkpoint_records:
        payload = {
            item.name: getattr(record, item.name)
            for item in fields(record)
            if item.name != "checkpoint_digest"
        }
        checkpoints.append(
            replace(record, checkpoint_digest=cell_module._digest(payload))
        )

    summaries = []
    offset = 0
    previous_chain = "MATRIX_CHAIN_ORIGIN"
    for source_summary in source.ordered_cell_summaries:
        count = len(source_summary.ordered_checkpoint_digests)
        records = checkpoints[offset : offset + count]
        offset += count
        checkpoint_digests = tuple(item.checkpoint_digest for item in records)
        chain = matrix_module._digest(
            {
                "previous_matrix_chain_digest": previous_chain,
                "cell_ordinal": source_summary.cell_ordinal,
                "model_role_position": source_summary.model_role_position,
                "model_role": source_summary.model_role,
                "plan_position": source_summary.plan_position,
                "plan_role": source_summary.plan_role,
                "cell_identity": matrix_module._identity_payload(
                    source_summary.cell_identity
                ),
                "cell_result_digest": source_summary.cell_result_digest,
                "terminal_event_chain_digest": (
                    source_summary.terminal_event_chain_digest
                ),
                "ordered_checkpoint_digests": checkpoint_digests,
            }
        )
        summary = replace(
            source_summary,
            ordered_checkpoint_digests=checkpoint_digests,
            matrix_chain_digest=chain,
            cell_summary_digest="",
        )
        summary = replace(
            summary,
            cell_summary_digest=matrix_module._digest(
                matrix_module._summary_payload(summary)
            ),
        )
        summaries.append(summary)
        previous_chain = chain
    return matrix_module._publish(
        replace(
            source,
            ordered_cell_summaries=tuple(summaries),
            ordered_checkpoint_records=tuple(checkpoints),
            terminal_matrix_chain_digest_or_none=previous_chain,
            matrix_result_digest="",
        )
    )


def _artifact_bytes() -> bytes:
    return build_four_node_matrix_artifact_bytes(
        _valid_matrix(),
        _inventory(),
        INPUTS,
        authorization=AUTHORIZATION,
        runtime_identity=RUNTIME,
    )


def _project_copy(parent: Path) -> Path:
    project = parent / "project"
    reports = project / "reports"
    reports.mkdir(parents=True)
    for relative, _ in INPUTS:
        shutil.copyfile(ROOT / relative, project / relative)
    return project


class FourNodeMatrixArtifactAndSingleRunTests(unittest.TestCase):
    def test_matrix_validator_accepts_complete_synthetic_result(self) -> None:
        validate_four_node_matrix_result(_valid_matrix())

    def test_matrix_validator_rejects_changed_result_digest(self) -> None:
        with self.assertRaises(FourNodeMatrixLifecycleError):
            validate_four_node_matrix_result(
                replace(_valid_matrix(), matrix_result_digest="0" * 64)
            )

    def test_matrix_validator_rejects_changed_checkpoint_digest(self) -> None:
        result = _valid_matrix()
        records = (replace(result.ordered_checkpoint_records[0], checkpoint_digest="0" * 64),) + result.ordered_checkpoint_records[1:]
        with self.assertRaises(FourNodeMatrixLifecycleError):
            validate_four_node_matrix_result(
                replace(result, ordered_checkpoint_records=records)
            )

    def test_artifact_is_deterministic_canonical_and_roundtrips(self) -> None:
        first = _artifact_bytes()
        second = _artifact_bytes()
        parsed = parse_four_node_matrix_artifact(first)
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertEqual(_valid_matrix(), parsed.matrix_result)

    def test_artifact_rejects_wrong_authorization(self) -> None:
        with self.assertRaises(FourNodeMatrixArtifactError):
            build_four_node_matrix_artifact_bytes(
                _valid_matrix(),
                _inventory(),
                INPUTS,
                authorization="different",
                runtime_identity=RUNTIME,
            )

    def test_artifact_rejects_unknown_missing_and_duplicate_fields(self) -> None:
        raw = _artifact_bytes()
        root = json.loads(raw)
        root["unknown"] = None
        with self.assertRaises(FourNodeMatrixArtifactError):
            parse_four_node_matrix_artifact(canonical_json_bytes(root, trailing_lf=True))
        root = json.loads(raw)
        root.pop("source_contract_id")
        with self.assertRaises(FourNodeMatrixArtifactError):
            parse_four_node_matrix_artifact(canonical_json_bytes(root, trailing_lf=True))
        duplicate = raw.replace(b'{"artifact_digest":', b'{"schema_id":"duplicate","artifact_digest":', 1)
        with self.assertRaises(FourNodeMatrixArtifactError):
            parse_four_node_matrix_artifact(duplicate)

    def test_artifact_rejects_noncanonical_bytes(self) -> None:
        raw = _artifact_bytes()
        with self.assertRaises(FourNodeMatrixArtifactError):
            parse_four_node_matrix_artifact(raw.replace(b'":', b'": ', 1))

    def test_artifact_excludes_carry_and_private_payloads(self) -> None:
        raw = _artifact_bytes()
        self.assertNotIn(b"final_carry_or_none", raw)
        self.assertNotIn(b"private_payload", raw)
        self.assertIn(b"final_carry_digest", raw)

    def test_source_inventory_is_deterministic_and_local(self) -> None:
        first = build_four_node_source_inventory(ROOT)
        second = build_four_node_source_inventory(ROOT)
        self.assertEqual(first, second)
        self.assertTrue(first.files)
        self.assertTrue(
            all(item.relative_path.startswith("mcm_field_organism/") for item in first.files)
        )

    def test_input_file_digests_bind_the_fixed_axis(self) -> None:
        records = build_four_node_input_file_digests(ROOT)
        self.assertEqual(tuple(path for path, _ in INPUTS), tuple(path for path, _ in records))
        self.assertTrue(all(len(digest) == 64 for _, digest in records))

    def test_wrong_authorization_stops_without_run_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = _project_copy(Path(temporary))
            with patch(f"{RUNNER_MODULE}.execute_four_node_matrix") as producer:
                with self.assertRaises(FourNodeMatrixSingleRunError):
                    run_four_node_matrix_once(project, "wrong")
            producer.assert_not_called()
            self.assertFalse(any((project / path).exists() for path in (RESULT, ATTEMPT, LOCK, STAGING)))

    def test_existing_fixed_path_stops_before_producer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = _project_copy(Path(temporary))
            (project / RESULT).write_text("occupied", encoding="ascii")
            with patch(f"{RUNNER_MODULE}.execute_four_node_matrix") as producer:
                with self.assertRaises(FourNodeMatrixSingleRunError):
                    run_four_node_matrix_once(project, AUTHORIZATION)
            producer.assert_not_called()

    def test_success_calls_one_producer_and_publishes_one_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = _project_copy(Path(temporary))
            inventory = _inventory()
            with (
                patch(f"{RUNNER_MODULE}.build_four_node_source_inventory", side_effect=(inventory, inventory)),
                patch(f"{RUNNER_MODULE}.build_four_node_input_file_digests", side_effect=(INPUTS, INPUTS)),
                patch(f"{RUNNER_MODULE}.execute_four_node_matrix", return_value=_valid_matrix()) as producer,
                patch(f"{RUNNER_MODULE}.four_node_runtime_identity", return_value=RUNTIME),
            ):
                artifact = run_four_node_matrix_once(project, AUTHORIZATION)
            producer.assert_called_once()
            self.assertEqual(_valid_matrix().matrix_result_digest, artifact.matrix_result.matrix_result_digest)
            self.assertTrue((project / RESULT).is_file())
            self.assertFalse(any((project / path).exists() for path in (ATTEMPT, LOCK, STAGING)))

    def test_started_producer_failure_leaves_attempt_and_lock_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = _project_copy(Path(temporary))
            inventory = _inventory()
            with (
                patch(f"{RUNNER_MODULE}.build_four_node_source_inventory", return_value=inventory),
                patch(f"{RUNNER_MODULE}.build_four_node_input_file_digests", return_value=INPUTS),
                patch(f"{RUNNER_MODULE}.execute_four_node_matrix", side_effect=RuntimeError("closed")),
            ):
                with self.assertRaises(FourNodeMatrixSingleRunError):
                    run_four_node_matrix_once(project, AUTHORIZATION)
            self.assertTrue((project / ATTEMPT).is_file())
            self.assertTrue((project / LOCK).is_file())
            self.assertFalse((project / RESULT).exists())
            self.assertFalse((project / STAGING).exists())

    def test_post_run_source_drift_blocks_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = _project_copy(Path(temporary))
            with (
                patch(f"{RUNNER_MODULE}.build_four_node_source_inventory", side_effect=(_inventory(), _inventory("3"))),
                patch(f"{RUNNER_MODULE}.build_four_node_input_file_digests", side_effect=(INPUTS, INPUTS)),
                patch(f"{RUNNER_MODULE}.execute_four_node_matrix", return_value=_valid_matrix()) as producer,
            ):
                with self.assertRaises(FourNodeMatrixSingleRunError):
                    run_four_node_matrix_once(project, AUTHORIZATION)
            producer.assert_called_once()
            self.assertFalse((project / RESULT).exists())
            self.assertTrue((project / ATTEMPT).exists())
            self.assertTrue((project / LOCK).exists())

    def test_published_result_blocks_a_second_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = _project_copy(Path(temporary))
            (project / RESULT).write_bytes(_artifact_bytes())
            with patch(f"{RUNNER_MODULE}.execute_four_node_matrix") as producer:
                with self.assertRaises(FourNodeMatrixSingleRunError):
                    run_four_node_matrix_once(project, AUTHORIZATION)
            producer.assert_not_called()

    def test_attempt_records_are_canonical_and_digest_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = _project_copy(Path(temporary))
            with (
                patch(f"{RUNNER_MODULE}.build_four_node_source_inventory", return_value=_inventory()),
                patch(f"{RUNNER_MODULE}.build_four_node_input_file_digests", return_value=INPUTS),
                patch(f"{RUNNER_MODULE}.execute_four_node_matrix", side_effect=RuntimeError("closed")),
            ):
                with self.assertRaises(FourNodeMatrixSingleRunError):
                    run_four_node_matrix_once(project, AUTHORIZATION)
            for relative, digest_field in ((ATTEMPT, "attempt_digest"), (LOCK, "lock_digest")):
                raw = (project / relative).read_bytes()
                value = json.loads(raw)
                digest = value.pop(digest_field)
                self.assertEqual(_digest(value), digest)
                self.assertEqual(canonical_json_bytes({**value, digest_field: digest}, trailing_lf=True), raw)

    def test_runner_has_no_forbidden_execution_imports_or_calls(self) -> None:
        path = ROOT / "mcm_field_organism" / "four_node_matrix_single_run.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue(imports.isdisjoint({"subprocess", "threading", "socket", "requests", "git"}))
        self.assertFalse(any("comparator" in name.lower() for name in calls))


if __name__ == "__main__":
    unittest.main()
