from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
import inspect
import unittest

from mcm_field_organism.kfs1_schema_validator import (
    TRANSITION_ALPHABET,
    TRANSITION_FAILURE_CODES,
    build_kfs1_validation_registry,
    validate_kfs1_record,
    validate_kfs1_transition_record,
)
from tests.kfs1_s1nb_fixtures import FIXTURE_EXPECTATIONS
from tests.kfs1_s1ne_transition_fixtures import (
    CHAIN_BROKEN,
    CHAIN_FIRST,
    CHAIN_SECOND,
    POSITIVE_EVENTS,
    TRANSITION_EXPECTATIONS,
    TRANSITION_FIXTURES,
    _canonical,
)


class KFS1S1NETransitionValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = build_kfs1_validation_registry()
        cls.receipts = {
            fixture.fixture_id: validate_kfs1_transition_record(
                fixture.raw_bytes, cls.registry
            )
            for fixture in TRANSITION_FIXTURES
        }

    def test_t01_all_seven_alphabet_records_are_valid(self) -> None:
        self.assertEqual(7, len(POSITIVE_EVENTS))
        self.assertEqual(7, len(TRANSITION_ALPHABET))
        for fixture_id in POSITIVE_EVENTS:
            receipt = self.receipts[fixture_id]
            expected = TRANSITION_EXPECTATIONS[fixture_id]
            self.assertEqual("valid", receipt.validation_status, fixture_id)
            self.assertEqual((), receipt.failure_reasons, fixture_id)
            self.assertEqual(expected.input_bytes_digest, receipt.input_bytes_digest)
            self.assertEqual(expected.computed_record_digest, receipt.computed_record_digest)

    def test_t02_all_eighteen_error_codes_are_isolated(self) -> None:
        invalid = [fixture for fixture in TRANSITION_FIXTURES if fixture.fixture_id.startswith("I_")]
        self.assertEqual(18, len(invalid))
        self.assertEqual(18, len(TRANSITION_FAILURE_CODES))
        for fixture in invalid:
            receipt = self.receipts[fixture.fixture_id]
            self.assertEqual("invalid", receipt.validation_status, fixture.fixture_id)
            self.assertEqual(fixture.failure_reasons, receipt.failure_reasons, fixture.fixture_id)
            self.assertEqual(fixture.computed_record_digest, receipt.computed_record_digest, fixture.fixture_id)

    def test_t03_direct_predecessor_chain_is_valid(self) -> None:
        receipt = validate_kfs1_transition_record(
            _canonical(CHAIN_SECOND), self.registry, _canonical(CHAIN_FIRST)
        )
        self.assertEqual("valid", receipt.validation_status)
        self.assertEqual((), receipt.failure_reasons)

    def test_t04_broken_predecessor_chain_fails_closed(self) -> None:
        receipt = validate_kfs1_transition_record(
            _canonical(CHAIN_BROKEN), self.registry, _canonical(CHAIN_FIRST)
        )
        self.assertEqual(
            ("EVENT_ORDER_OR_PREDECESSOR_MISMATCH",), receipt.failure_reasons
        )

    def test_t05_validation_is_deterministic_and_input_preserving(self) -> None:
        raw = TRANSITION_EXPECTATIONS["V_LOCAL_CONTACT_BIND"].raw_bytes
        first = validate_kfs1_transition_record(raw, self.registry)
        second = validate_kfs1_transition_record(raw, self.registry)
        self.assertEqual(first, second)
        self.assertEqual(raw, TRANSITION_EXPECTATIONS["V_LOCAL_CONTACT_BIND"].raw_bytes)
        with self.assertRaises(FrozenInstanceError):
            first.validation_status = "invalid"  # type: ignore[misc]

    def test_t06_digest_roles_remain_separate(self) -> None:
        receipt = self.receipts["V_LOCAL_CONTACT_BIND"]
        self.assertNotEqual(receipt.input_bytes_digest, receipt.computed_record_digest)
        self.assertNotEqual(receipt.computed_record_digest, receipt.validation_receipt_digest)

    def test_t07_noncanonical_input_is_not_repaired(self) -> None:
        receipt = self.receipts["I_NONCANONICAL"]
        self.assertEqual(("NONCANONICAL_TRANSITION_SERIALIZATION",), receipt.failure_reasons)
        self.assertEqual(
            TRANSITION_EXPECTATIONS["I_NONCANONICAL"].input_bytes_digest,
            receipt.input_bytes_digest,
        )

    def test_t08_registry_binds_exact_alphabet_triggers_and_codes(self) -> None:
        self.assertEqual(TRANSITION_ALPHABET, self.registry.transition_alphabet)
        self.assertEqual(TRANSITION_FAILURE_CODES, self.registry.transition_failure_codes)
        self.assertEqual(4, len(self.registry.transition_trigger_observations))
        self.assertEqual(3, len(self.registry.transition_start_ledger_digests))

    def test_t09_existing_anatomy_and_measurement_validation_remains_valid(self) -> None:
        for fixture_id in ("V_ANATOMY_MIN_01", "V_MEASUREMENT_MIN_01"):
            fixture = FIXTURE_EXPECTATIONS[fixture_id]
            receipt = validate_kfs1_record(fixture.raw_bytes, self.registry)
            self.assertEqual("valid", receipt.validation_status)

    def test_t10_module_has_no_runtime_or_media_imports(self) -> None:
        import mcm_field_organism.kfs1_schema_validator as module

        tree = ast.parse(inspect.getsource(module))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        forbidden = ("dynamic_substrate", "audio", "video", "browser", "tools")
        self.assertFalse(any(part in name for name in imported for part in forbidden))

    def test_t11_transition_validator_has_no_output_side_effect_api(self) -> None:
        source = inspect.getsource(validate_kfs1_transition_record)
        for forbidden in ("open(", "write_", "Path(", "report", "requests"):
            self.assertNotIn(forbidden, source)

    def test_t12_no_transition_generation_or_field_step_is_exposed(self) -> None:
        import mcm_field_organism.kfs1_schema_validator as module

        public = set(module.__all__)
        for forbidden in ("run", "step", "advance", "update", "generate", "apply"):
            self.assertNotIn(forbidden, public)
        self.assertEqual(25, len(TRANSITION_FIXTURES))


if __name__ == "__main__":
    unittest.main()
