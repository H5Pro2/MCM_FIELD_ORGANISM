"""Focused S1-OO acceptance for pure atomic G2/D3 commit selection."""

from __future__ import annotations

import ast
from dataclasses import fields, replace
from pathlib import Path
import unittest

from mcm_field_organism.g2_d3_halving_amount import build_g2_d3_halving_amount_registry
from mcm_field_organism.g2_d3_schema_validator import build_g2_d3_validation_registry
from mcm_field_organism.g2_d3_target_projection import (
    COMMIT_CONTRACT_DIGEST,
    G2D3AtomicCommitReceipt,
    build_g2_d3_target_commit_registry,
    verify_and_commit_g2_d3_projected_target,
)
from mcm_field_organism.g2_d3_transient_boundary_validator import (
    build_g2_d3_transient_boundary_registry,
)
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1oo_fixtures import (
    ALL_FIXTURES,
    COMMIT_FAILURE_FIXTURES,
    INPUT_DIGESTS,
    RECOMPUTE_FAILURE_FIXTURES,
    VALID_FIXTURES,
    fixture_input_digests,
)


class G2D3S1OOAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.target_registry = build_g2_d3_target_commit_registry()
        cls.amount_registry = build_g2_d3_halving_amount_registry()
        cls.boundary_registry = build_g2_d3_transient_boundary_registry()
        cls.d3_registry = build_g2_d3_validation_registry()

    def commit(self, fixture):
        boundary, source, current, proposed, enabled = fixture
        return verify_and_commit_g2_d3_projected_target(
            boundary,
            source,
            current,
            proposed,
            enabled,
            self.target_registry,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )

    def test_01_all_input_digests_are_bound(self) -> None:
        self.assertEqual(14, len(ALL_FIXTURES))
        self.assertEqual(set(ALL_FIXTURES), set(INPUT_DIGESTS))
        for name, fixture in ALL_FIXTURES.items():
            with self.subTest(name=name):
                self.assertEqual(INPUT_DIGESTS[name], fixture_input_digests(fixture))

    def test_02_five_valid_controls_have_exact_status_and_bytes(self) -> None:
        expected_status = {
            "ON_V_NO_CHANGE_FIRST_X": "NO_CHANGE_COMMITTED",
            "ON_V_NO_CHANGE_XY": "NO_CHANGE_COMMITTED",
            "ON_V_PROJECTED_XX": "PROJECTED_COMMITTED",
            "ON_V_PROJECTED_YY": "PROJECTED_COMMITTED",
            "ON_V_PROJECTED_SECOND": "PROJECTED_COMMITTED",
        }
        self.assertEqual(5, len(VALID_FIXTURES))
        for name, fixture in VALID_FIXTURES.items():
            with self.subTest(name=name):
                result = self.commit(fixture)
                self.assertEqual("valid", result.receipt.validation_status)
                self.assertEqual((), result.receipt.failure_reasons)
                self.assertEqual(expected_status[name], result.receipt.commit_status)
                expected = fixture[2] if name.startswith("ON_V_NO_CHANGE") else fixture[3]
                self.assertEqual(expected, result.committed_d3_raw_bytes)

    def test_03_null_commits_return_current_byte_objects(self) -> None:
        for name in ("ON_V_NO_CHANGE_FIRST_X", "ON_V_NO_CHANGE_XY"):
            with self.subTest(name=name):
                fixture = VALID_FIXTURES[name]
                self.assertIsNot(fixture[1], fixture[2])
                self.assertIsNot(fixture[2], fixture[3])
                result = self.commit(fixture)
                self.assertIs(fixture[2], result.committed_d3_raw_bytes)

    def test_04_positive_commits_return_proposed_byte_objects(self) -> None:
        for name in ("ON_V_PROJECTED_XX", "ON_V_PROJECTED_YY", "ON_V_PROJECTED_SECOND"):
            with self.subTest(name=name):
                fixture = VALID_FIXTURES[name]
                result = self.commit(fixture)
                self.assertIs(fixture[3], result.committed_d3_raw_bytes)
                self.assertEqual(sha256_hex(fixture[3]), result.receipt.committed_d3_input_bytes_digest)

    def test_05_five_recomputation_failures_are_single_gated(self) -> None:
        self.assertEqual(5, len(RECOMPUTE_FAILURE_FIXTURES))
        for name, fixture in RECOMPUTE_FAILURE_FIXTURES.items():
            with self.subTest(name=name):
                result = self.commit(fixture)
                self.assertEqual("not_computable", result.committed_d3_raw_bytes)
                self.assertEqual("not_computable", result.receipt.commit_status)
                self.assertEqual(
                    ("OK_COMMIT_PROJECTION_RECOMPUTATION_FAILED",),
                    result.receipt.failure_reasons,
                )
                self.assertNotIn("proposed_target_validation", result.receipt.completed_checks)

    def test_06_invalid_proposed_target_fails_before_comparison(self) -> None:
        result = self.commit(COMMIT_FAILURE_FIXTURES["ON_I_PROPOSED_INVALID"])
        self.assertEqual(("OK_COMMIT_PROPOSED_TARGET_INVALID",), result.receipt.failure_reasons)
        self.assertIn("proposed_target_validation", result.receipt.completed_checks)
        self.assertNotIn("proposed_target_comparison", result.receipt.completed_checks)
        self.assertEqual("not_computable", result.receipt.current_anatomy_record_digest)

    def test_07_valid_wrong_proposed_target_fails_without_repair(self) -> None:
        fixture = COMMIT_FAILURE_FIXTURES["ON_I_PROPOSED_MISMATCH"]
        result = self.commit(fixture)
        self.assertEqual(("OK_COMMIT_PROPOSED_TARGET_MISMATCH",), result.receipt.failure_reasons)
        self.assertEqual("not_computable", result.committed_d3_raw_bytes)
        self.assertIn("proposed_target_comparison", result.receipt.completed_checks)
        self.assertNotIn("current_source_validation", result.receipt.completed_checks)
        self.assertNotEqual(result.receipt.expected_target_d3_input_bytes_digest, sha256_hex(fixture[3]))

    def test_08_invalid_current_source_fails_before_stale_gate(self) -> None:
        result = self.commit(COMMIT_FAILURE_FIXTURES["ON_I_CURRENT_INVALID"])
        self.assertEqual(("OK_COMMIT_CURRENT_SOURCE_INVALID",), result.receipt.failure_reasons)
        self.assertIn("current_source_validation", result.receipt.completed_checks)
        self.assertNotIn("stale_source_gate", result.receipt.completed_checks)
        self.assertEqual("not_computable", result.receipt.current_anatomy_record_digest)

    def test_09_stale_source_has_distinct_status_and_no_bytes(self) -> None:
        result = self.commit(COMMIT_FAILURE_FIXTURES["ON_I_STALE_SOURCE"])
        self.assertEqual("STALE_SOURCE", result.receipt.commit_status)
        self.assertEqual(("OK_COMMIT_STALE_SOURCE",), result.receipt.failure_reasons)
        self.assertEqual("not_computable", result.committed_d3_raw_bytes)
        self.assertNotEqual(
            result.receipt.source_anatomy_record_digest,
            result.receipt.current_anatomy_record_digest,
        )
        self.assertNotIn("atomic_selection", result.receipt.completed_checks)

    def test_10_failure_completed_checks_follow_bound_order(self) -> None:
        expected_last = {
            "ON_I_RECOMPUTE_SOURCE": "source_projection_recomputation",
            "ON_I_PROPOSED_INVALID": "proposed_target_validation",
            "ON_I_PROPOSED_MISMATCH": "proposed_target_comparison",
            "ON_I_CURRENT_INVALID": "current_source_validation",
            "ON_I_STALE_SOURCE": "stale_source_gate",
        }
        for name, last in expected_last.items():
            with self.subTest(name=name):
                result = self.commit(ALL_FIXTURES[name])
                checks = result.receipt.completed_checks
                self.assertEqual(last, checks[-3])
                self.assertEqual(("persistence_guard", "commit_receipt"), checks[-2:])

    def test_11_digest_roles_and_commit_receipt_digest_are_bound(self) -> None:
        result = self.commit(VALID_FIXTURES["ON_V_PROJECTED_XX"])
        receipt = result.receipt
        self.assertEqual(COMMIT_CONTRACT_DIGEST, receipt.commit_contract_digest)
        self.assertEqual(receipt.source_d3_input_bytes_digest, receipt.current_d3_input_bytes_digest)
        self.assertEqual(receipt.expected_target_d3_input_bytes_digest, receipt.proposed_target_d3_input_bytes_digest)
        self.assertNotEqual(receipt.source_anatomy_record_digest, receipt.proposed_target_anatomy_record_digest)
        payload = receipt.canonical_payload()
        digest = payload.pop("commit_receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))

    def test_12_same_inputs_produce_identical_results(self) -> None:
        first = self.commit(VALID_FIXTURES["ON_V_PROJECTED_XX"])
        second = self.commit(VALID_FIXTURES["ON_V_PROJECTED_XX"])
        self.assertEqual(first, second)
        self.assertEqual(first.receipt.canonical_payload(), second.receipt.canonical_payload())

    def test_13_inputs_registries_and_api_boundary_are_closed(self) -> None:
        fixture = VALID_FIXTURES["ON_V_PROJECTED_XX"]
        original_registries = (
            self.target_registry,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )
        self.commit(fixture)
        self.assertIs(fixture, VALID_FIXTURES["ON_V_PROJECTED_XX"])
        self.assertEqual(
            original_registries,
            (self.target_registry, self.amount_registry, self.boundary_registry, self.d3_registry),
        )
        boundary, source, current, proposed, enabled = fixture
        tail = (enabled, self.target_registry, self.amount_registry, self.boundary_registry, self.d3_registry)
        bad_inputs = (
            (bytearray(boundary), source, current, proposed),
            (boundary, bytearray(source), current, proposed),
            (boundary, source, bytearray(current), proposed),
            (boundary, source, current, bytearray(proposed)),
        )
        for inputs in bad_inputs:
            with self.assertRaises(TypeError):
                verify_and_commit_g2_d3_projected_target(*inputs, *tail)
        with self.assertRaises(TypeError):
            verify_and_commit_g2_d3_projected_target(
                boundary, source, current, proposed, 1,
                self.target_registry, self.amount_registry, self.boundary_registry, self.d3_registry,
            )
        with self.assertRaises(ValueError):
            verify_and_commit_g2_d3_projected_target(
                boundary, source, current, proposed, enabled,
                replace(self.target_registry, commit_receipt_schema_version="changed"),
                self.amount_registry, self.boundary_registry, self.d3_registry,
            )
        valid = self.commit(fixture)
        with self.assertRaises(TypeError):
            verify_and_commit_g2_d3_projected_target(
                valid.receipt, source, current, proposed, *tail
            )

    def test_14_module_surface_has_no_runtime_publication_path(self) -> None:
        source_path = Path(__file__).parents[1] / "mcm_field_organism" / "g2_d3_target_projection.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        imported_surface = " ".join(imported).lower()
        for forbidden in (
            "admissibility", "field", "transfer", "runner", "audio", "video",
            "browser", "socket", "requests",
        ):
            self.assertNotIn(forbidden, imported_surface)
        lowered = source.lower()
        self.assertNotIn("open(", lowered)
        self.assertNotIn("write_text", lowered)
        self.assertNotIn("write_bytes", lowered)
        receipt_fields = {item.name for item in fields(G2D3AtomicCommitReceipt)}
        for forbidden_field in ("raw_bytes", "field_state", "o3_value", "runtime_state"):
            self.assertNotIn(forbidden_field, receipt_fields)


if __name__ == "__main__":
    unittest.main()
