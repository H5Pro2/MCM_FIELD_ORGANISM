"""Focused S1-NW acceptance for the pure validated O3 operator."""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.g2_d3_admissibility import (
    OPERATOR_CONTRACT_DIGEST,
    evaluate_g2_d3_local_admissible_engagement,
)
from mcm_field_organism.g2_d3_schema_validator import (
    build_g2_d3_validation_registry,
)
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1nr_fixtures import (
    D3_V_C0,
    D3_V_C1,
    D3_V_C1_AGGREGATE_CONTROL,
    D3_V_C1_IDENTITY_CONTROL,
    D3_V_MIXED,
    SINGLE_MUTATIONS,
)


class G2D3S1NWAdmissibilityAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = build_g2_d3_validation_registry()

    def evaluate(self, raw_bytes: bytes):
        return evaluate_g2_d3_local_admissible_engagement(raw_bytes, self.registry)

    def test_01_five_positive_records_have_exact_values(self) -> None:
        expected = (
            (D3_V_C0, 0.5),
            (D3_V_C1, 0.0),
            (D3_V_MIXED, 0.25),
            (D3_V_C1_IDENTITY_CONTROL, 0.0),
            (D3_V_C1_AGGREGATE_CONTROL, 0.0),
        )
        for raw_bytes, value in expected:
            with self.subTest(value=value, digest=sha256_hex(raw_bytes)):
                receipt = self.evaluate(raw_bytes)
                self.assertEqual("valid", receipt.evaluation_status)
                self.assertEqual((), receipt.failure_reasons)
                self.assertEqual(value, receipt.local_admissible_engagement)

    def test_02_c0_c1_has_bound_negative_delta(self) -> None:
        c0 = self.evaluate(D3_V_C0)
        c1 = self.evaluate(D3_V_C1)
        self.assertEqual(-0.5, c1.local_admissible_engagement - c0.local_admissible_engagement)

    def test_03_pure_c1_ablation_has_c0_value_and_zero_delta(self) -> None:
        c0 = self.evaluate(D3_V_C0)
        ablated_c1 = self.evaluate(D3_V_C0)
        self.assertEqual(c0.local_admissible_engagement, ablated_c1.local_admissible_engagement)
        self.assertEqual(0.0, ablated_c1.local_admissible_engagement - c0.local_admissible_engagement)

    def test_04_invalid_sources_fail_closed_without_values(self) -> None:
        for mutation in ("D3_I_RECORD_DIGEST", "D3_I_NEGATIVE", "D3_I_NEGATIVE_ZERO"):
            with self.subTest(mutation=mutation):
                receipt = self.evaluate(SINGLE_MUTATIONS[mutation])
                self.assertEqual("invalid", receipt.evaluation_status)
                self.assertEqual(("D3_ADMISSIBILITY_SOURCE_RECORD_INVALID",), receipt.failure_reasons)
                self.assertEqual("not_computable", receipt.free)
                self.assertEqual("not_computable", receipt.bound_configured)
                self.assertEqual("not_computable", receipt.local_admissible_engagement)

    def test_05_aggregate_shape_is_rejected_without_default(self) -> None:
        aggregate = b'{"blocked":0.0,"bound":0.5,"free":0.5}'
        receipt = self.evaluate(aggregate)
        self.assertEqual("invalid", receipt.evaluation_status)
        self.assertEqual("not_computable", receipt.bound_configured)
        self.assertEqual("not_computable", receipt.local_admissible_engagement)

    def test_06_same_input_produces_bit_identical_receipts(self) -> None:
        first = self.evaluate(D3_V_MIXED)
        second = self.evaluate(D3_V_MIXED)
        self.assertEqual(first, second)

    def test_07_input_and_registry_are_not_mutated(self) -> None:
        raw_bytes = D3_V_C0
        registry = self.registry
        self.evaluate(raw_bytes)
        self.assertIs(raw_bytes, D3_V_C0)
        self.assertEqual(registry, self.registry)

    def test_08_digest_roles_are_separate_and_receipt_digest_is_bound(self) -> None:
        receipt = self.evaluate(D3_V_C0)
        digests = {
            receipt.input_bytes_digest,
            receipt.source_validation_receipt_digest,
            receipt.source_anatomy_record_digest,
            receipt.operator_contract_digest,
            receipt.admissibility_receipt_digest,
        }
        self.assertEqual(5, len(digests))
        self.assertEqual(OPERATOR_CONTRACT_DIGEST, receipt.operator_contract_digest)
        payload = receipt.canonical_payload()
        digest = payload.pop("admissibility_receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))

    def test_09_wrong_api_types_and_registry_fail_before_receipt(self) -> None:
        with self.assertRaises(TypeError):
            evaluate_g2_d3_local_admissible_engagement(bytearray(D3_V_C0), self.registry)
        with self.assertRaises(ValueError):
            evaluate_g2_d3_local_admissible_engagement(
                D3_V_C0,
                replace(self.registry, schema_version="changed"),
            )

    def test_10_module_import_surface_is_isolated(self) -> None:
        source_path = Path(__file__).parents[1] / "mcm_field_organism" / "g2_d3_admissibility.py"
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
                "json",
                "typing",
                "g2_d3_schema_validator",
                "kfs1_schema_validator",
            },
            {name.rsplit(".", 1)[-1] for name in imported},
        )
        imported_surface = " ".join(imported).lower()
        for forbidden in ("field", "transfer", "runner", "audio", "video", "socket", "requests"):
            self.assertNotIn(forbidden, imported_surface)
        self.assertNotIn("open(", source.lower())


if __name__ == "__main__":
    unittest.main()
