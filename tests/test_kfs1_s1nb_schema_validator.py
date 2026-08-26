from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
import inspect
import unittest

from mcm_field_organism.kfs1_schema_validator import (
    KFS1ValidationReceipt,
    build_kfs1_validation_registry,
    canonical_json_bytes,
    sha256_hex,
    validate_kfs1_record,
)
from tests.kfs1_s1nb_fixtures import FIXTURE_EXPECTATIONS, FIXTURES


class KFS1S1NBSchemaValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = build_kfs1_validation_registry()
        cls.receipts = {
            fixture.fixture_id: validate_kfs1_record(fixture.raw_bytes, cls.registry)
            for fixture in FIXTURES
        }

    def test_t01_positive_fixtures_are_valid_and_digest_stable(self) -> None:
        for fixture_id in ("V_ANATOMY_MIN_01", "V_MEASUREMENT_MIN_01"):
            expected = FIXTURE_EXPECTATIONS[fixture_id]
            receipt = self.receipts[fixture_id]
            self.assertEqual("valid", receipt.validation_status)
            self.assertEqual((), receipt.failure_reasons)
            self.assertEqual(expected.input_bytes_digest, receipt.input_bytes_digest)
            self.assertEqual(expected.computed_record_digest, receipt.computed_record_digest)

    def test_t02_all_single_defects_have_the_bound_primary_code(self) -> None:
        fixtures = [fixture for fixture in FIXTURES if fixture.fixture_id.startswith("I_") and not fixture.fixture_id.startswith("I_MULTI_")]
        self.assertEqual(18, len(fixtures))
        for fixture in fixtures:
            receipt = self.receipts[fixture.fixture_id]
            self.assertEqual("invalid", receipt.validation_status, fixture.fixture_id)
            self.assertEqual(fixture.failure_reasons, receipt.failure_reasons, fixture.fixture_id)
            self.assertEqual(fixture.computed_record_digest, receipt.computed_record_digest, fixture.fixture_id)

    def test_t03_multiple_defects_are_safe_unique_and_sorted(self) -> None:
        fixtures = [fixture for fixture in FIXTURES if fixture.fixture_id.startswith("I_MULTI_")]
        self.assertEqual(3, len(fixtures))
        for fixture in fixtures:
            receipt = self.receipts[fixture.fixture_id]
            reasons = receipt.failure_reasons
            self.assertEqual(fixture.failure_reasons, reasons, fixture.fixture_id)
            self.assertEqual(tuple(sorted(set(reasons))), reasons)
            self.assertEqual(fixture.computed_record_digest, receipt.computed_record_digest, fixture.fixture_id)

    def test_t04_repeated_validation_is_bit_identical(self) -> None:
        fixture = FIXTURE_EXPECTATIONS["V_ANATOMY_MIN_01"]
        first = validate_kfs1_record(fixture.raw_bytes, self.registry)
        second = validate_kfs1_record(fixture.raw_bytes, self.registry)
        self.assertEqual(first, second)
        self.assertEqual(first.validation_receipt_digest, second.validation_receipt_digest)

    def test_t05_inputs_registry_and_receipt_are_immutable(self) -> None:
        fixture = FIXTURE_EXPECTATIONS["V_MEASUREMENT_MIN_01"]
        before = bytes(fixture.raw_bytes)
        registry_before = self.registry
        receipt = validate_kfs1_record(fixture.raw_bytes, self.registry)
        self.assertEqual(before, fixture.raw_bytes)
        self.assertEqual(registry_before, self.registry)
        with self.assertRaises(FrozenInstanceError):
            receipt.validation_status = "invalid"  # type: ignore[misc]
        with self.assertRaises(ValueError):
            validate_kfs1_record(fixture.raw_bytes, replace(self.registry, failure_codes=()))

    def test_t06_noncanonical_bytes_are_not_normalized(self) -> None:
        fixture = FIXTURE_EXPECTATIONS["I_SERIALIZATION_01"]
        receipt = self.receipts[fixture.fixture_id]
        self.assertEqual(sha256_hex(fixture.raw_bytes), receipt.input_bytes_digest)
        self.assertEqual(("NONCANONICAL_SERIALIZATION",), receipt.failure_reasons)
        with self.assertRaises(ValueError):
            canonical_json_bytes(-0.0)

    def test_t07_missing_prerequisite_has_no_invented_followup(self) -> None:
        receipt = self.receipts["I_EXPOSURE_MISSING_01"]
        self.assertEqual(("EXPOSURE_HISTORY_MISSING_OR_MISMATCHED",), receipt.failure_reasons)
        self.assertEqual("not_computable", receipt.computed_record_digest)

    def test_t08_digest_roles_are_separate_and_not_self_referential(self) -> None:
        anatomy = self.receipts["V_ANATOMY_MIN_01"]
        measurement = self.receipts["V_MEASUREMENT_MIN_01"]
        self.assertNotEqual(anatomy.input_bytes_digest, anatomy.computed_record_digest)
        self.assertNotEqual(anatomy.computed_record_digest, anatomy.validation_receipt_digest)
        self.assertNotEqual(measurement.computed_record_digest, measurement.validation_receipt_digest)

    def test_t09_mismatched_exposure_is_not_comparable(self) -> None:
        receipt = self.receipts["I_EXPOSURE_MISMATCH_01"]
        self.assertEqual("invalid", receipt.validation_status)
        self.assertEqual(("EXPOSURE_HISTORY_MISSING_OR_MISMATCHED",), receipt.failure_reasons)

    def test_t10_module_has_no_runtime_or_media_imports(self) -> None:
        import mcm_field_organism.kfs1_schema_validator as module

        source = inspect.getsource(module)
        tree = ast.parse(source)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        forbidden = ("dynamic_substrate", "audio", "video", "browser", "tools")
        self.assertFalse(any(part in name for name in imported for part in forbidden))

    def test_t11_validator_has_no_file_or_report_output(self) -> None:
        source = inspect.getsource(validate_kfs1_record)
        for forbidden in ("open(", "write_", "Path(", "report", "requests"):
            self.assertNotIn(forbidden, source)

    def test_t12_no_dynamic_or_result_api_is_reachable(self) -> None:
        import mcm_field_organism.kfs1_schema_validator as module

        public = set(module.__all__)
        for forbidden in ("run", "step", "advance", "update", "learn", "score", "classify"):
            self.assertNotIn(forbidden, public)
        self.assertEqual(23, len(FIXTURES))
        self.assertTrue(all(isinstance(value, KFS1ValidationReceipt) for value in self.receipts.values()))


if __name__ == "__main__":
    unittest.main()
