"""Focused S1-OS acceptance for pure two-step G2/D3 composition."""

from __future__ import annotations

import ast
from dataclasses import fields, replace
import json
from pathlib import Path
import unittest

from mcm_field_organism.g2_d3_halving_amount import build_g2_d3_halving_amount_registry
from mcm_field_organism.g2_d3_schema_validator import build_g2_d3_validation_registry
from mcm_field_organism.g2_d3_target_projection import build_g2_d3_target_commit_registry
from mcm_field_organism.g2_d3_transient_boundary_validator import (
    build_g2_d3_transient_boundary_registry,
)
from mcm_field_organism.g2_d3_two_step_composition import (
    COMPOSITION_CONTRACT_DIGEST,
    FAILURE_CODES,
    G2D3TwoStepCompositionReceipt,
    build_g2_d3_two_step_composition_registry,
    compose_g2_d3_two_step_continuation,
)
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1om_fixtures import D3_OL_SECOND_TARGET
from tests.g2_d3_s1os_fixtures import (
    ALL_FIXTURES,
    DEFENSIVE_CODES,
    EXPECTED_FAILURES,
    INPUT_DIGESTS,
    INVALID_FIXTURES,
    SECOND_X,
    SECOND_Y,
    VALID_FIXTURES,
    fixture_input_digests,
)


class G2D3S1OSAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sequence_registry = build_g2_d3_two_step_composition_registry()
        cls.target_registry = build_g2_d3_target_commit_registry()
        cls.amount_registry = build_g2_d3_halving_amount_registry()
        cls.boundary_registry = build_g2_d3_transient_boundary_registry()
        cls.d3_registry = build_g2_d3_validation_registry()

    def compose(self, fixture):
        first, second, initial, enabled = fixture
        return compose_g2_d3_two_step_continuation(
            first,
            second,
            initial,
            enabled,
            self.sequence_registry,
            self.target_registry,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )

    def test_01_all_fixture_and_boundary_digests_are_bound(self) -> None:
        self.assertEqual(9, len(ALL_FIXTURES))
        self.assertEqual(set(ALL_FIXTURES), set(INPUT_DIGESTS))
        for name, fixture in ALL_FIXTURES.items():
            with self.subTest(name=name):
                self.assertEqual(INPUT_DIGESTS[name], fixture_input_digests(fixture))
        self.assertEqual(
            "7d499f00806f6a7e9afea9119aad09b5a74b736881a7a93bd61142fcce8e8ab0",
            json.loads(SECOND_X)["boundary_record_digest"],
        )
        self.assertEqual(
            "b9756269da497da0c64a0e63e5a64f1c98497118b4ad9f61f74eafcd0786d9c0",
            json.loads(SECOND_Y)["boundary_record_digest"],
        )
        self.assertEqual(
            "a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab",
            sha256_hex(D3_OL_SECOND_TARGET),
        )

    def test_02_xxx_and_yyy_have_exact_chains_and_final_bytes(self) -> None:
        expected_roles = {"OR_V_XXX": "OP_CHAIN_XXX", "OR_V_YYY": "OP_CHAIN_YYY"}
        for name, fixture in VALID_FIXTURES.items():
            with self.subTest(name=name):
                result = self.compose(fixture)
                self.assertEqual("valid", result.receipt.validation_status)
                self.assertEqual("TWO_STEP_COMPOSED", result.receipt.composition_status)
                self.assertEqual((), result.receipt.failure_reasons)
                self.assertEqual(expected_roles[name], result.receipt.chain_role)
                self.assertEqual(D3_OL_SECOND_TARGET, result.final_d3_raw_bytes)

    def test_03_chains_have_identical_intermediate_and_final_d3_digests(self) -> None:
        xxx = self.compose(VALID_FIXTURES["OR_V_XXX"])
        yyy = self.compose(VALID_FIXTURES["OR_V_YYY"])
        self.assertEqual(
            xxx.receipt.intermediate_d3_input_bytes_digest,
            yyy.receipt.intermediate_d3_input_bytes_digest,
        )
        self.assertEqual(
            xxx.receipt.intermediate_anatomy_record_digest,
            yyy.receipt.intermediate_anatomy_record_digest,
        )
        self.assertEqual(xxx.final_d3_raw_bytes, yyy.final_d3_raw_bytes)
        self.assertEqual(xxx.receipt.final_anatomy_record_digest, yyy.receipt.final_anatomy_record_digest)
        self.assertNotEqual(xxx.receipt.composition_receipt_digest, yyy.receipt.composition_receipt_digest)

    def test_04_passive_receipt_digest_and_fields_are_closed(self) -> None:
        receipt = self.compose(VALID_FIXTURES["OR_V_XXX"]).receipt
        self.assertEqual(COMPOSITION_CONTRACT_DIGEST, receipt.composition_contract_digest)
        self.assertEqual(receipt.first_current_contact_digest, receipt.second_prior_contact_digest)
        payload = receipt.canonical_payload()
        digest = payload.pop("composition_receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))
        receipt_fields = {item.name for item in fields(G2D3TwoStepCompositionReceipt)}
        for forbidden in (
            "intermediate_d3_raw_bytes",
            "final_d3_raw_bytes",
            "projection_receipt",
            "commit_receipt",
        ):
            self.assertNotIn(forbidden, receipt_fields)

    def test_05_unknown_first_and_initial_stop_at_chain_binding(self) -> None:
        for name in ("OR_I_UNKNOWN_FIRST", "OR_I_UNKNOWN_INITIAL"):
            with self.subTest(name=name):
                result = self.compose(INVALID_FIXTURES[name])
                self.assertEqual(("OQ_UNKNOWN_CHAIN_BINDING",), result.receipt.failure_reasons)
                self.assertEqual("not_computable", result.final_d3_raw_bytes)
                self.assertNotIn("first_projection", result.receipt.completed_checks)

    def test_06_disabled_formation_stops_before_first_projection(self) -> None:
        result = self.compose(INVALID_FIXTURES["OR_I_FORMATION_DISABLED"])
        self.assertEqual(("OQ_FORMATION_DISABLED",), result.receipt.failure_reasons)
        self.assertEqual("OP_CHAIN_XXX", result.receipt.chain_role)
        self.assertNotIn("first_projection", result.receipt.completed_checks)

    def test_07_invalid_second_boundary_stops_after_first_commit(self) -> None:
        result = self.compose(INVALID_FIXTURES["OR_I_SECOND_INVALID"])
        self.assertEqual(("OQ_SECOND_BOUNDARY_INVALID",), result.receipt.failure_reasons)
        self.assertIn("first_commit", result.receipt.completed_checks)
        self.assertIn("second_boundary_validation", result.receipt.completed_checks)
        self.assertNotIn("second_projection", result.receipt.completed_checks)

    def test_08_old_source_binding_has_exact_single_failure(self) -> None:
        result = self.compose(INVALID_FIXTURES["OR_I_SECOND_SOURCE_C0"])
        self.assertEqual(("OQ_SECOND_SOURCE_BINDING_MISMATCH",), result.receipt.failure_reasons)
        self.assertIn("second_source_binding_gate", result.receipt.completed_checks)
        self.assertNotIn("second_contact_link_gate", result.receipt.completed_checks)
        self.assertNotIn("second_projection", result.receipt.completed_checks)

    def test_09_crossed_and_reset_contacts_have_exact_link_failure(self) -> None:
        for name in ("OR_I_SECOND_CONTACT_CROSS", "OR_I_SECOND_CONTACT_RESET"):
            with self.subTest(name=name):
                result = self.compose(INVALID_FIXTURES[name])
                self.assertEqual(("OQ_SECOND_CONTACT_LINK_MISMATCH",), result.receipt.failure_reasons)
                self.assertIn("second_contact_link_gate", result.receipt.completed_checks)
                self.assertNotIn("second_projection", result.receipt.completed_checks)

    def test_10_external_failures_follow_prerequisite_gating(self) -> None:
        expected_last = {
            "OR_I_UNKNOWN_FIRST": "chain_binding",
            "OR_I_FORMATION_DISABLED": "chain_binding",
            "OR_I_SECOND_INVALID": "second_boundary_validation",
            "OR_I_SECOND_SOURCE_C0": "second_source_binding_gate",
            "OR_I_SECOND_CONTACT_CROSS": "second_contact_link_gate",
        }
        for name, last in expected_last.items():
            with self.subTest(name=name):
                result = self.compose(INVALID_FIXTURES[name])
                checks = result.receipt.completed_checks
                self.assertEqual(last, checks[-3])
                self.assertEqual(("persistence_guard", "composition_receipt"), checks[-2:])

    def test_11_all_codes_registered_without_fake_defensive_fixtures(self) -> None:
        self.assertEqual(11, len(FAILURE_CODES))
        self.assertEqual(FAILURE_CODES, self.sequence_registry.failure_codes)
        self.assertEqual(6, len(DEFENSIVE_CODES))
        self.assertTrue(set(DEFENSIVE_CODES).issubset(FAILURE_CODES))
        self.assertTrue(set(DEFENSIVE_CODES).isdisjoint(EXPECTED_FAILURES.values()))
        source_path = Path(__file__).parents[1] / "mcm_field_organism" / "g2_d3_two_step_composition.py"
        source = source_path.read_text(encoding="utf-8")
        for code in DEFENSIVE_CODES:
            self.assertIn(f'return fail("{code}")', source)

    def test_12_determinism_inputs_and_registries_are_immutable(self) -> None:
        fixture = VALID_FIXTURES["OR_V_XXX"]
        original_registries = (
            self.sequence_registry,
            self.target_registry,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )
        first = self.compose(fixture)
        second = self.compose(fixture)
        self.assertEqual(first, second)
        self.assertIs(fixture, VALID_FIXTURES["OR_V_XXX"])
        self.assertEqual(
            original_registries,
            (
                self.sequence_registry,
                self.target_registry,
                self.amount_registry,
                self.boundary_registry,
                self.d3_registry,
            ),
        )

    def test_13_wrong_api_inputs_registries_and_receipts_fail_before_result(self) -> None:
        first, second, initial, enabled = VALID_FIXTURES["OR_V_XXX"]
        tail = (
            enabled,
            self.sequence_registry,
            self.target_registry,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )
        for inputs in (
            (bytearray(first), second, initial),
            (first, bytearray(second), initial),
            (first, second, bytearray(initial)),
        ):
            with self.assertRaises(TypeError):
                compose_g2_d3_two_step_continuation(*inputs, *tail)
        with self.assertRaises(TypeError):
            compose_g2_d3_two_step_continuation(
                first, second, initial, 1,
                self.sequence_registry, self.target_registry, self.amount_registry,
                self.boundary_registry, self.d3_registry,
            )
        with self.assertRaises(ValueError):
            compose_g2_d3_two_step_continuation(
                first, second, initial, enabled,
                replace(self.sequence_registry, receipt_schema_version="changed"),
                self.target_registry, self.amount_registry, self.boundary_registry, self.d3_registry,
            )
        valid = self.compose(VALID_FIXTURES["OR_V_XXX"])
        with self.assertRaises(TypeError):
            compose_g2_d3_two_step_continuation(valid.receipt, second, initial, *tail)

    def test_14_module_surface_has_no_runtime_or_field_path(self) -> None:
        source_path = Path(__file__).parents[1] / "mcm_field_organism" / "g2_d3_two_step_composition.py"
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


if __name__ == "__main__":
    unittest.main()
