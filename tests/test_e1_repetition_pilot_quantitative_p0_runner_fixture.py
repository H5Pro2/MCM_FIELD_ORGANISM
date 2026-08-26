from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_quantitative_p0_integration_contract import (
    build_e1_repetition_pilot_quantitative_p0_integration_contract,
)
from mcm_field_organism.e1_repetition_pilot_quantitative_p0_runner_fixture import (
    E1RepetitionPilotQuantitativeP0RunnerFixtureError,
    run_quantitative_p0_handoff_runner_fixture,
)
from tests.test_e1_repetition_pilot_quantitative_p0_integration_contract import (
    E1RepetitionPilotQuantitativeP0IntegrationContractTests,
)
from tests.test_e1_repetition_pilot_quantitative_p0_schema import (
    E1RepetitionPilotQuantitativeP0SchemaTests,
)


class E1RepetitionPilotQuantitativeP0RunnerFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1RepetitionPilotQuantitativeP0IntegrationContractTests.setUpClass()
        source = E1RepetitionPilotQuantitativeP0IntegrationContractTests
        cls.contract = build_e1_repetition_pilot_quantitative_p0_integration_contract(
            source.pilot_contract, source.audit
        )
        E1RepetitionPilotQuantitativeP0SchemaTests.setUpClass()
        cls.template = E1RepetitionPilotQuantitativeP0SchemaTests.snapshot

    def test_all_handoffs_and_profiles_are_collected(self) -> None:
        result = run_quantitative_p0_handoff_runner_fixture(
            self.contract, self.template
        )
        self.assertEqual(12, result.snapshot_handoff_count)
        self.assertEqual(6, result.pair_collection_count)
        self.assertEqual(2, result.profile_count)
        self.assertFalse(result.field_execution_performed)

    def test_no_authorization_or_persistence_is_used(self) -> None:
        result = run_quantitative_p0_handoff_runner_fixture(
            self.contract, self.template
        )
        self.assertFalse(result.authorization_consumed)
        self.assertFalse(result.persistence_performed)
        self.assertFalse(result.result_decision_permitted)

    def test_invalid_kernel_fails_before_partial_result(self) -> None:
        def invalid_kernel(handoff, template):
            return (template,)

        with self.assertRaises(E1RepetitionPilotQuantitativeP0RunnerFixtureError):
            run_quantitative_p0_handoff_runner_fixture(
                self.contract, self.template, kernel=invalid_kernel
            )

    def test_runner_contains_no_real_field_or_authorization_path(self) -> None:
        source = inspect.getsource(run_quantitative_p0_handoff_runner_fixture)
        for forbidden in (
            "run_neutral_asynchronous_field",
            "run_prepared_real_formation_arm_in_memory",
            "E1PilotOnceAuthorization",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
