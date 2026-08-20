"""Focused S1-OC acceptance for the transient G2/D3 boundary validator."""

from __future__ import annotations

import ast
from dataclasses import replace
import json
from pathlib import Path
import unittest

from mcm_field_organism.g2_d3_schema_validator import build_g2_d3_validation_registry
from mcm_field_organism.g2_d3_transient_boundary_validator import (
    VALIDATOR_CONTRACT_DIGEST,
    build_g2_d3_transient_boundary_registry,
    validate_g2_d3_transient_boundary,
)
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1nr_fixtures import D3_V_C0
from tests.g2_d3_s1oc_fixtures import (
    HISTORIES,
    HISTORY_DIGESTS,
    HISTORY_EVENTS,
    NEGATIVE_EXPECTED,
    NEGATIVE_FIXTURES,
    NEGATIVE_INPUT_DIGESTS,
    OA_V_FIRST_X,
    POSITIVE_DIGESTS,
    POSITIVE_EVENTS,
    POSITIVE_FIXTURES,
)


class G2D3S1OCAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.boundary_registry = build_g2_d3_transient_boundary_registry()
        cls.d3_registry = build_g2_d3_validation_registry()

    def validate(self, boundary_raw: bytes, d3_raw: bytes = D3_V_C0):
        return validate_g2_d3_transient_boundary(
            boundary_raw,
            d3_raw,
            self.boundary_registry,
            self.d3_registry,
        )

    def test_01_positive_fixtures_and_histories_are_digest_bound(self) -> None:
        for name, raw in POSITIVE_FIXTURES.items():
            with self.subTest(name=name):
                record = json.loads(raw)
                expected_boundary, expected_input = POSITIVE_DIGESTS[name]
                self.assertEqual(expected_boundary, record["boundary_record_digest"])
                self.assertEqual(expected_input, sha256_hex(raw))
        for history_name, history in HISTORIES.items():
            for ordinal, raw in enumerate(history):
                with self.subTest(history=history_name, ordinal=ordinal):
                    expected_boundary, expected_input = HISTORY_DIGESTS[history_name][ordinal]
                    self.assertEqual(expected_boundary, json.loads(raw)["boundary_record_digest"])
                    self.assertEqual(expected_input, sha256_hex(raw))
        for name, (raw, _) in NEGATIVE_FIXTURES.items():
            with self.subTest(mutation=name):
                self.assertEqual(NEGATIVE_INPUT_DIGESTS[name], sha256_hex(raw))

    def test_02_six_table_fixtures_have_exact_event_roles(self) -> None:
        for name, raw in POSITIVE_FIXTURES.items():
            with self.subTest(name=name):
                receipt = self.validate(raw)
                self.assertEqual("valid", receipt.validation_status)
                self.assertEqual((), receipt.failure_reasons)
                self.assertEqual(POSITIVE_EVENTS[name], receipt.event_role)

    def test_03_h0_has_first_contact_then_three_switches(self) -> None:
        events = tuple(self.validate(raw).event_role for raw in HISTORIES["H0"])
        self.assertEqual(HISTORY_EVENTS["H0"], events)

    def test_04_h1_and_mirror_have_the_same_bound_event_sequence(self) -> None:
        for name in ("H1", "H1M"):
            with self.subTest(name=name):
                events = tuple(self.validate(raw).event_role for raw in HISTORIES[name])
                self.assertEqual(HISTORY_EVENTS[name], events)
        self.assertEqual(HISTORY_EVENTS["H1"], HISTORY_EVENTS["H1M"])

    def test_05_all_mutations_fail_with_exact_safe_codes(self) -> None:
        self.assertEqual(17, len(NEGATIVE_FIXTURES))
        for name, (boundary_raw, d3_raw) in NEGATIVE_FIXTURES.items():
            with self.subTest(name=name):
                receipt = self.validate(boundary_raw, d3_raw)
                self.assertEqual("invalid", receipt.validation_status)
                self.assertEqual(NEGATIVE_EXPECTED[name], receipt.failure_reasons)
                self.assertEqual("not_computable", receipt.event_role)

    def test_06_invalid_d3_source_blocks_event_classification(self) -> None:
        boundary_raw, d3_raw = NEGATIVE_FIXTURES["OA_I_D3_SOURCE_INVALID"]
        receipt = self.validate(boundary_raw, d3_raw)
        self.assertEqual(("OA_D3_SOURCE_RECORD_INVALID",), receipt.failure_reasons)
        self.assertEqual("not_computable", receipt.event_role)
        self.assertEqual("not_computable", receipt.source_d3_anatomy_record_digest)

    def test_07_digest_roles_and_receipt_digest_are_separate(self) -> None:
        receipt = self.validate(OA_V_FIRST_X)
        digests = {
            receipt.boundary_input_bytes_digest,
            receipt.d3_input_bytes_digest,
            receipt.source_d3_validation_receipt_digest,
            receipt.source_d3_anatomy_record_digest,
            receipt.computed_current_contact_digest,
            receipt.computed_boundary_record_digest,
            receipt.validator_contract_digest,
            receipt.boundary_validation_receipt_digest,
        }
        self.assertEqual(8, len(digests))
        self.assertEqual(VALIDATOR_CONTRACT_DIGEST, receipt.validator_contract_digest)
        payload = receipt.canonical_payload()
        digest = payload.pop("boundary_validation_receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))

    def test_08_same_bytes_and_registries_produce_identical_receipts(self) -> None:
        first = self.validate(OA_V_FIRST_X)
        second = self.validate(OA_V_FIRST_X)
        self.assertEqual(first, second)
        self.assertEqual(first.canonical_payload(), second.canonical_payload())

    def test_09_inputs_and_registries_remain_unchanged(self) -> None:
        boundary_raw = OA_V_FIRST_X
        d3_raw = D3_V_C0
        boundary_registry = self.boundary_registry
        d3_registry = self.d3_registry
        self.validate(boundary_raw, d3_raw)
        self.assertIs(boundary_raw, OA_V_FIRST_X)
        self.assertIs(d3_raw, D3_V_C0)
        self.assertEqual(boundary_registry, self.boundary_registry)
        self.assertEqual(d3_registry, self.d3_registry)

    def test_10_wrong_api_types_and_registries_fail_before_receipts(self) -> None:
        with self.assertRaises(TypeError):
            validate_g2_d3_transient_boundary(
                bytearray(OA_V_FIRST_X), D3_V_C0, self.boundary_registry, self.d3_registry
            )
        with self.assertRaises(TypeError):
            validate_g2_d3_transient_boundary(
                OA_V_FIRST_X, bytearray(D3_V_C0), self.boundary_registry, self.d3_registry
            )
        with self.assertRaises(ValueError):
            validate_g2_d3_transient_boundary(
                OA_V_FIRST_X,
                D3_V_C0,
                replace(self.boundary_registry, schema_version="changed"),
                self.d3_registry,
            )
        with self.assertRaises(ValueError):
            validate_g2_d3_transient_boundary(
                OA_V_FIRST_X,
                D3_V_C0,
                self.boundary_registry,
                replace(self.d3_registry, schema_version="changed"),
            )

    def test_11_receipt_is_passive_and_cannot_be_used_as_follow_input(self) -> None:
        receipt = self.validate(OA_V_FIRST_X)
        self.assertNotIn(b"event_role", OA_V_FIRST_X)
        with self.assertRaises(TypeError):
            validate_g2_d3_transient_boundary(
                receipt, D3_V_C0, self.boundary_registry, self.d3_registry
            )

    def test_12_module_surface_is_isolated(self) -> None:
        source_path = (
            Path(__file__).parents[1]
            / "mcm_field_organism"
            / "g2_d3_transient_boundary_validator.py"
        )
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
        for forbidden in (
            "admissibility",
            "field",
            "transfer",
            "runner",
            "audio",
            "video",
            "socket",
            "requests",
        ):
            self.assertNotIn(forbidden, imported_surface)
        lowered = source.lower()
        self.assertNotIn("open(", lowered)
        self.assertNotIn("write_text", lowered)
        self.assertNotIn("write_bytes", lowered)


if __name__ == "__main__":
    unittest.main()
