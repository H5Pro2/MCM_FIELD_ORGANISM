"""Focused S1-OI acceptance for the passive halving amount evaluator."""

from __future__ import annotations

import ast
from dataclasses import fields, replace
from pathlib import Path
import unittest

from mcm_field_organism.g2_d3_halving_amount import (
    G2D3HalvingAmountEvaluationReceipt,
    OPERATOR_CONTRACT_DIGEST,
    build_g2_d3_halving_amount_registry,
    evaluate_g2_d3_continuation_halving_amount,
)
from mcm_field_organism.g2_d3_schema_validator import build_g2_d3_validation_registry
from mcm_field_organism.g2_d3_transient_boundary_validator import (
    build_g2_d3_transient_boundary_registry,
)
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes
from tests.g2_d3_s1oi_fixtures import (
    NEGATIVE_EXPECTED,
    NEGATIVE_FIXTURES,
    NEGATIVE_INPUT_DIGESTS,
    POSITIVE_EXPECTED,
    POSITIVE_FIXTURES,
    POSITIVE_INPUT_DIGESTS,
    fixture_input_digests,
)


class G2D3S1OIAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.amount_registry = build_g2_d3_halving_amount_registry()
        cls.boundary_registry = build_g2_d3_transient_boundary_registry()
        cls.d3_registry = build_g2_d3_validation_registry()

    def evaluate(self, fixture):
        boundary_raw, d3_raw, formation_enabled = fixture
        return evaluate_g2_d3_continuation_halving_amount(
            boundary_raw,
            d3_raw,
            formation_enabled,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )

    def test_01_fixture_inputs_are_digest_bound(self) -> None:
        for name, fixture in POSITIVE_FIXTURES.items():
            with self.subTest(name=name):
                self.assertEqual(POSITIVE_INPUT_DIGESTS[name], fixture_input_digests(fixture))
        for name, fixture in NEGATIVE_FIXTURES.items():
            with self.subTest(name=name):
                self.assertEqual(NEGATIVE_INPUT_DIGESTS[name], fixture_input_digests(fixture))

    def test_02_nine_valid_controls_have_exact_events_and_amounts(self) -> None:
        self.assertEqual(9, len(POSITIVE_FIXTURES))
        for name, fixture in POSITIVE_FIXTURES.items():
            with self.subTest(name=name):
                receipt = self.evaluate(fixture)
                expected_event, expected_amount = POSITIVE_EXPECTED[name]
                self.assertEqual("valid", receipt.evaluation_status)
                self.assertEqual((), receipt.failure_reasons)
                self.assertEqual(expected_event, receipt.event_role)
                self.assertEqual(expected_amount, receipt.computed_repartition_amount)

    def test_03_xx_and_yy_are_bit_identical_halving_amounts(self) -> None:
        xx = self.evaluate(POSITIVE_FIXTURES["OG_V_XX_ON"])
        yy = self.evaluate(POSITIVE_FIXTURES["OG_V_YY_ON"])
        self.assertEqual(0.25, xx.computed_repartition_amount)
        self.assertEqual(xx.computed_repartition_amount, yy.computed_repartition_amount)

    def test_04_ablation_empty_residual_and_integer_switch_are_exact_zero(self) -> None:
        for name in ("OG_V_XX_OFF", "OG_V_C1_XX_ON", "OG_V_INTEGER_XY_ON"):
            with self.subTest(name=name):
                receipt = self.evaluate(POSITIVE_FIXTURES[name])
                self.assertEqual("valid", receipt.evaluation_status)
                self.assertEqual(0.0, receipt.computed_repartition_amount)
                self.assertNotIn("numeric_domain_validation", receipt.completed_checks)

    def test_05_five_mutations_fail_with_exact_single_codes(self) -> None:
        self.assertEqual(5, len(NEGATIVE_FIXTURES))
        for name, fixture in NEGATIVE_FIXTURES.items():
            with self.subTest(name=name):
                receipt = self.evaluate(fixture)
                self.assertEqual("invalid", receipt.evaluation_status)
                self.assertEqual(NEGATIVE_EXPECTED[name], receipt.failure_reasons)
                self.assertEqual("not_computable", receipt.computed_repartition_amount)

    def test_06_source_failure_blocks_event_values_and_amount(self) -> None:
        receipt = self.evaluate(NEGATIVE_FIXTURES["OG_I_SOURCE"])
        self.assertEqual("not_computable", receipt.event_role)
        self.assertEqual("not_computable", receipt.source_d3_anatomy_record_digest)
        self.assertEqual("not_computable", receipt.source_boundary_record_digest)
        self.assertEqual("not_computable", receipt.source_bound_unconfigured)
        self.assertEqual("not_computable", receipt.source_bound_configured)
        self.assertEqual("not_computable", receipt.computed_repartition_amount)

    def test_07_numeric_failures_are_prerequisite_gated(self) -> None:
        expected_last_phase = {
            "OG_I_NUMERIC_DOMAIN": "numeric_domain_validation",
            "OG_I_HALVING_INVARIANT": "halving_evaluation",
            "OG_I_TARGET_REPRESENTATION": "exact_ledger_preview",
            "OG_I_EXACT_LEDGER": "exact_ledger_preview",
        }
        for name, last_phase in expected_last_phase.items():
            with self.subTest(name=name):
                receipt = self.evaluate(NEGATIVE_FIXTURES[name])
                self.assertIn(last_phase, receipt.completed_checks)
                self.assertEqual(NEGATIVE_EXPECTED[name], receipt.failure_reasons)

    def test_08_digest_roles_and_receipt_digest_are_separate(self) -> None:
        receipt = self.evaluate(POSITIVE_FIXTURES["OG_V_XX_ON"])
        digests = {
            receipt.boundary_input_bytes_digest,
            receipt.d3_input_bytes_digest,
            receipt.source_boundary_validation_receipt_digest,
            receipt.source_d3_validation_receipt_digest,
            receipt.source_d3_anatomy_record_digest,
            receipt.source_boundary_record_digest,
            receipt.operator_contract_digest,
            receipt.amount_evaluation_receipt_digest,
        }
        self.assertEqual(8, len(digests))
        self.assertEqual(OPERATOR_CONTRACT_DIGEST, receipt.operator_contract_digest)
        payload = receipt.canonical_payload()
        digest = payload.pop("amount_evaluation_receipt_digest")
        from mcm_field_organism.kfs1_schema_validator import sha256_hex

        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))

    def test_09_same_inputs_produce_identical_receipts(self) -> None:
        first = self.evaluate(POSITIVE_FIXTURES["OG_V_XX_ON"])
        second = self.evaluate(POSITIVE_FIXTURES["OG_V_XX_ON"])
        self.assertEqual(first, second)
        self.assertEqual(first.canonical_payload(), second.canonical_payload())

    def test_10_inputs_and_registries_remain_unchanged(self) -> None:
        fixture = POSITIVE_FIXTURES["OG_V_XX_ON"]
        boundary_raw, d3_raw, _ = fixture
        amount_registry = self.amount_registry
        boundary_registry = self.boundary_registry
        d3_registry = self.d3_registry
        self.evaluate(fixture)
        self.assertIs(boundary_raw, fixture[0])
        self.assertIs(d3_raw, fixture[1])
        self.assertEqual(amount_registry, self.amount_registry)
        self.assertEqual(boundary_registry, self.boundary_registry)
        self.assertEqual(d3_registry, self.d3_registry)

    def test_11_wrong_api_inputs_fail_and_receipt_is_not_reusable(self) -> None:
        boundary_raw, d3_raw, enabled = POSITIVE_FIXTURES["OG_V_XX_ON"]
        args = (self.amount_registry, self.boundary_registry, self.d3_registry)
        with self.assertRaises(TypeError):
            evaluate_g2_d3_continuation_halving_amount(bytearray(boundary_raw), d3_raw, enabled, *args)
        with self.assertRaises(TypeError):
            evaluate_g2_d3_continuation_halving_amount(boundary_raw, bytearray(d3_raw), enabled, *args)
        with self.assertRaises(TypeError):
            evaluate_g2_d3_continuation_halving_amount(boundary_raw, d3_raw, 1, *args)
        with self.assertRaises(ValueError):
            evaluate_g2_d3_continuation_halving_amount(
                boundary_raw,
                d3_raw,
                enabled,
                replace(self.amount_registry, receipt_schema_version="changed"),
                self.boundary_registry,
                self.d3_registry,
            )
        with self.assertRaises(ValueError):
            evaluate_g2_d3_continuation_halving_amount(
                boundary_raw,
                d3_raw,
                enabled,
                self.amount_registry,
                replace(self.boundary_registry, schema_version="changed"),
                self.d3_registry,
            )
        with self.assertRaises(ValueError):
            evaluate_g2_d3_continuation_halving_amount(
                boundary_raw,
                d3_raw,
                enabled,
                self.amount_registry,
                self.boundary_registry,
                replace(self.d3_registry, schema_version="changed"),
            )
        receipt = self.evaluate(POSITIVE_FIXTURES["OG_V_XX_ON"])
        with self.assertRaises(TypeError):
            evaluate_g2_d3_continuation_halving_amount(
                receipt, d3_raw, enabled, *args
            )

    def test_12_module_surface_has_no_stateful_or_runtime_path(self) -> None:
        source_path = Path(__file__).parents[1] / "mcm_field_organism" / "g2_d3_halving_amount.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        self.assertEqual(
            {
                "__future__",
                "dataclasses",
                "fractions",
                "json",
                "math",
                "typing",
                "g2_d3_schema_validator",
                "g2_d3_transient_boundary_validator",
                "kfs1_schema_validator",
            },
            {name.rsplit(".", 1)[-1] for name in imported},
        )
        imported_surface = " ".join(imported).lower()
        for forbidden in (
            "admissibility",
            "field",
            "transfer",
            "runner",
            "audio",
            "video",
            "browser",
            "socket",
            "requests",
        ):
            self.assertNotIn(forbidden, imported_surface)
        lowered = source.lower()
        self.assertNotIn("open(", lowered)
        self.assertNotIn("write_text", lowered)
        self.assertNotIn("write_bytes", lowered)
        receipt_fields = {item.name for item in fields(G2D3HalvingAmountEvaluationReceipt)}
        for forbidden_field in (
            "post_d3_state",
            "target_bound_unconfigured",
            "target_bound_configured",
            "commit_status",
            "field_state",
            "o3_value",
        ):
            self.assertNotIn(forbidden_field, receipt_fields)


if __name__ == "__main__":
    unittest.main()
