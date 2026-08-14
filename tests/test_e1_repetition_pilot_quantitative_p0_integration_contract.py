from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_p0_identifiability_audit import (
    audit_e1_repetition_pilot_p0_identifiability,
)
from mcm_field_organism.e1_repetition_pilot_quantitative_p0_integration_contract import (
    E1RepetitionPilotQuantitativeP0IntegrationContractError,
    build_e1_repetition_pilot_quantitative_p0_integration_contract,
)
from tests.test_e1_repetition_pilot_real_preflight import (
    E1RepetitionPilotRealPreflightTests,
)


class E1RepetitionPilotQuantitativeP0IntegrationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1RepetitionPilotRealPreflightTests.setUpClass()
        cls.pilot_contract = E1RepetitionPilotRealPreflightTests.contract
        cls.plans = E1RepetitionPilotRealPreflightTests.plans
        cls.audit = audit_e1_repetition_pilot_p0_identifiability(
            cls.pilot_contract, cls.plans
        )

    def test_six_batches_require_twelve_fresh_p0_snapshots(self) -> None:
        result = build_e1_repetition_pilot_quantitative_p0_integration_contract(
            self.pilot_contract, self.audit
        )
        self.assertEqual(6, len(result.handoffs))
        self.assertEqual(12, result.total_p0_snapshot_count)
        self.assertTrue(result.runner_implementation_permitted)
        self.assertFalse(result.field_execution_permitted)

    def test_old_ec34_result_and_authorization_are_rejected(self) -> None:
        result = build_e1_repetition_pilot_quantitative_p0_integration_contract(
            self.pilot_contract, self.audit
        )
        self.assertFalse(result.old_ec34_result_accepted)
        self.assertFalse(result.old_ec34_authorization_reusable)

    def test_schema_roles_include_components_and_linf(self) -> None:
        result = build_e1_repetition_pilot_quantitative_p0_integration_contract(
            self.pilot_contract, self.audit
        )
        self.assertIn("activation_contrast", result.required_schema_roles)
        self.assertIn("afterimage_contrast", result.required_schema_roles)
        self.assertIn("activation_linf", result.required_schema_roles)
        self.assertIn("afterimage_linf", result.required_schema_roles)

    def test_changed_audit_is_rejected_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            replace(self.audit, audit_digest="0" * 64)

    def test_builder_contains_no_execution_or_authorization_input(self) -> None:
        source = inspect.getsource(
            build_e1_repetition_pilot_quantitative_p0_integration_contract
        )
        for forbidden in (
            "run_neutral_asynchronous_field",
            "E1PilotOnceAuthorization",
            "owner_authorized",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
