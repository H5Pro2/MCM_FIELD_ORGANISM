"""Focused S1-NR acceptance for the isolated G2/D3 validator."""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.g2_d3_schema_validator import (
    build_g2_d3_validation_registry,
    validate_g2_d3_anatomy_record,
    validate_g2_d3_f1_pair,
)
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1nr_fixtures import (
    D3_V_C0,
    D3_V_C1,
    D3_V_C1_AGGREGATE_CONTROL,
    D3_V_C1_IDENTITY_CONTROL,
    D3_V_MIXED,
    PAIR_EXPECTED,
    PAIR_MUTATIONS,
    POSITIVE_INPUT_DIGESTS,
    SINGLE_EXPECTED,
    SINGLE_MUTATIONS,
)


class G2D3S1NRAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = build_g2_d3_validation_registry()

    def test_01_positive_records_are_valid_and_digest_bound(self) -> None:
        fixtures = {
            "D3_V_C0": D3_V_C0,
            "D3_V_C1": D3_V_C1,
            "D3_V_MIXED": D3_V_MIXED,
            "D3_V_C1_IDENTITY_CONTROL": D3_V_C1_IDENTITY_CONTROL,
            "D3_V_C1_AGGREGATE_CONTROL": D3_V_C1_AGGREGATE_CONTROL,
        }
        for name, raw in fixtures.items():
            with self.subTest(name=name):
                receipt = validate_g2_d3_anatomy_record(raw, self.registry)
                self.assertEqual("valid", receipt.validation_status)
                self.assertEqual((), receipt.failure_reasons)
                self.assertEqual(POSITIVE_INPUT_DIGESTS[name], sha256_hex(raw))

    def test_02_positive_pair_is_comparable_and_ablatable(self) -> None:
        receipt = validate_g2_d3_f1_pair(D3_V_C0, D3_V_C1, self.registry)
        self.assertEqual("valid", receipt.validation_status)
        self.assertEqual((), receipt.failure_reasons)
        self.assertEqual(
            "bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e",
            receipt.aggregate_projection_digest,
        )

    def test_03_single_mutations_fail_with_exact_codes(self) -> None:
        self.assertEqual(18, len(SINGLE_MUTATIONS))
        for name, raw in SINGLE_MUTATIONS.items():
            with self.subTest(name=name):
                receipt = validate_g2_d3_anatomy_record(raw, self.registry)
                self.assertEqual("invalid", receipt.validation_status)
                self.assertEqual(SINGLE_EXPECTED[name], receipt.failure_reasons)

    def test_04_pair_mutations_fail_with_exact_codes(self) -> None:
        self.assertEqual(6, len(PAIR_MUTATIONS))
        for name, pair in PAIR_MUTATIONS.items():
            with self.subTest(name=name):
                receipt = validate_g2_d3_f1_pair(*pair, self.registry)
                self.assertEqual("invalid", receipt.validation_status)
                self.assertEqual(PAIR_EXPECTED[name], receipt.failure_reasons)

    def test_05_failures_are_sorted_unique_and_deterministic(self) -> None:
        first = validate_g2_d3_f1_pair(*PAIR_MUTATIONS["D3_P_AGGREGATE"], self.registry)
        second = validate_g2_d3_f1_pair(*PAIR_MUTATIONS["D3_P_AGGREGATE"], self.registry)
        self.assertEqual(tuple(sorted(set(first.failure_reasons))), first.failure_reasons)
        self.assertEqual(first, second)

    def test_06_inputs_and_registry_remain_unchanged(self) -> None:
        raw = D3_V_C0
        registry = self.registry
        validate_g2_d3_anatomy_record(raw, registry)
        self.assertIs(raw, D3_V_C0)
        self.assertEqual(registry, self.registry)
        with self.assertRaises(ValueError):
            validate_g2_d3_anatomy_record(raw, replace(registry, schema_version="changed"))

    def test_07_noncanonical_values_are_not_normalized(self) -> None:
        with self.assertRaises(ValueError):
            canonical_json_bytes(-0.0)
        receipt = validate_g2_d3_anatomy_record(SINGLE_MUTATIONS["D3_I_NEGATIVE_ZERO"], self.registry)
        self.assertEqual(("D3_NONCANONICAL_SERIALIZATION",), receipt.failure_reasons)

    def test_08_digest_roles_and_receipts_are_separate(self) -> None:
        receipt = validate_g2_d3_anatomy_record(D3_V_C0, self.registry)
        values = {
            receipt.input_bytes_digest,
            receipt.computed_resource_account_digest,
            receipt.computed_aggregate_projection_digest,
            receipt.computed_anatomy_record_digest,
            receipt.validation_receipt_digest,
        }
        self.assertEqual(5, len(values))
        payload = receipt.canonical_payload()
        digest = payload.pop("validation_receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))

    def test_09_api_types_fail_before_partial_receipts(self) -> None:
        with self.assertRaises(TypeError):
            validate_g2_d3_anatomy_record(bytearray(D3_V_C0), self.registry)
        with self.assertRaises(TypeError):
            validate_g2_d3_f1_pair(D3_V_C0, bytearray(D3_V_C1), self.registry)

    def test_10_import_and_runtime_surface_stays_isolated(self) -> None:
        source_path = Path(__file__).parents[1] / "mcm_field_organism" / "g2_d3_schema_validator.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        self.assertEqual(
            {"__future__", "dataclasses", "json", "math", "typing", "kfs1_schema_validator"},
            {name.rsplit(".", 1)[-1] for name in imported},
        )
        imported_surface = " ".join(imported).lower()
        for forbidden in ("runner", "audio", "video", "browser", "socket", "requests"):
            self.assertNotIn(forbidden, imported_surface)
        self.assertNotIn("open(", source.lower())


if __name__ == "__main__":
    unittest.main()
