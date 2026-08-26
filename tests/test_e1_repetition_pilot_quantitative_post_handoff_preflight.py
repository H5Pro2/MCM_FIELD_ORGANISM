from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_quantitative_post_handoff_preflight import (
    audit_e1_repetition_pilot_quantitative_post_handoff_preflight,
)
from mcm_field_organism.e1_repetition_pilot_quantitative_real_handoff_fixture import (
    run_quantitative_real_p0_handoff_fixture,
)
from tests.test_e1_repetition_pilot_quantitative_real_handoff_fixture import (
    E1RepetitionPilotQuantitativeRealHandoffFixtureTests,
)


class E1RepetitionPilotQuantitativePostHandoffPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1RepetitionPilotQuantitativeRealHandoffFixtureTests.setUpClass()
        source = E1RepetitionPilotQuantitativeRealHandoffFixtureTests
        cls.previous = source.preflight
        cls.plans = source.plans
        cls.initial_field = source.initial_field
        cls.fixture = run_quantitative_real_p0_handoff_fixture(
            cls.previous, cls.plans.pairs[1], cls.initial_field
        )
        from tests.test_e1_repetition_pilot_quantitative_real_preflight import (
            E1RepetitionPilotQuantitativeRealPreflightTests,
        )
        upstream = E1RepetitionPilotQuantitativeRealPreflightTests
        cls.pilot_contract = upstream.pilot_contract
        cls.integration_contract = upstream.integration_contract

    def test_small_handoff_confirmed_but_full_runner_missing(self) -> None:
        result = audit_e1_repetition_pilot_quantitative_post_handoff_preflight(
            self.pilot_contract,
            self.integration_contract,
            self.previous,
            self.fixture,
        )
        self.assertEqual(
            "SMALL_HANDOFF_CONFIRMED_FULL_RUNNER_MISSING", result.decision
        )
        self.assertTrue(result.small_real_handoff_confirmed)
        self.assertTrue(result.full_runner_implementation_permitted)
        self.assertFalse(result.full_runner_integrated)
        self.assertFalse(result.pilot_execution_permitted)

    def test_preflight_has_no_execution_or_authorization_input(self) -> None:
        source = inspect.getsource(
            audit_e1_repetition_pilot_quantitative_post_handoff_preflight
        )
        for forbidden in (
            "run_neutral_asynchronous_field",
            "run_e1_repetition_pilot_once_in_memory",
            "E1PilotOnceAuthorization",
            "owner_authorized",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
