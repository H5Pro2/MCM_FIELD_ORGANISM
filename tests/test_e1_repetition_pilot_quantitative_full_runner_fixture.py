from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_quantitative_full_runner_fixture import (
    E1RepetitionPilotQuantitativeFullRunnerFixtureError,
    run_quantitative_full_runner_fixture,
)
from mcm_field_organism.e1_repetition_pilot_quantitative_post_handoff_preflight import (
    audit_e1_repetition_pilot_quantitative_post_handoff_preflight,
)
from tests.test_e1_repetition_pilot_quantitative_post_handoff_preflight import (
    E1RepetitionPilotQuantitativePostHandoffPreflightTests,
)
from tests.test_e1_repetition_pilot_quantitative_p0_schema import (
    E1RepetitionPilotQuantitativeP0SchemaTests,
)


class E1RepetitionPilotQuantitativeFullRunnerFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1RepetitionPilotQuantitativePostHandoffPreflightTests.setUpClass()
        source = E1RepetitionPilotQuantitativePostHandoffPreflightTests
        cls.pilot_contract = source.pilot_contract
        cls.integration_contract = source.integration_contract
        cls.preflight = audit_e1_repetition_pilot_quantitative_post_handoff_preflight(
            source.pilot_contract,
            source.integration_contract,
            source.previous,
            source.fixture,
        )
        E1RepetitionPilotQuantitativeP0SchemaTests.setUpClass()
        cls.template = E1RepetitionPilotQuantitativeP0SchemaTests.snapshot

    def test_all_roles_handoffs_and_profiles_are_integrated(self) -> None:
        result = run_quantitative_full_runner_fixture(
            self.pilot_contract,
            self.integration_contract,
            self.preflight,
            self.template,
        )
        self.assertEqual(36, result.arm_receipt_count)
        self.assertEqual(12, result.p0_snapshot_handoff_count)
        self.assertEqual(6, result.p0_pair_count)
        self.assertEqual(2, result.p0_profile_count)
        self.assertTrue(result.full_runner_integrated)
        self.assertEqual(0, result.executed_field_step_count)

    def test_handoffs_occur_before_ablation_and_active_roles(self) -> None:
        result = run_quantitative_full_runner_fixture(
            self.pilot_contract,
            self.integration_contract,
            self.preflight,
            self.template,
        )
        self.assertTrue(result.handoff_immediately_after_p0_roles)
        self.assertTrue(result.profiles_after_complete_trios)

    def test_invalid_arm_kernel_fails_closed(self) -> None:
        def invalid_arm_kernel(batch, arm_id):
            return None

        with self.assertRaises(E1RepetitionPilotQuantitativeFullRunnerFixtureError):
            run_quantitative_full_runner_fixture(
                self.pilot_contract,
                self.integration_contract,
                self.preflight,
                self.template,
                arm_kernel=invalid_arm_kernel,
            )

    def test_runner_contains_no_real_field_authorization_or_writes(self) -> None:
        source = inspect.getsource(run_quantitative_full_runner_fixture)
        for forbidden in (
            "run_neutral_asynchronous_field",
            "run_prepared_real_formation_arm_in_memory",
            "E1PilotOnceAuthorization",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
