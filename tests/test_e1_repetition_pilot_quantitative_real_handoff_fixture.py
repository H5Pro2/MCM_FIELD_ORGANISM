from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_quantitative_real_handoff_fixture import (
    E1RepetitionPilotQuantitativeRealHandoffFixtureError,
    run_quantitative_real_p0_handoff_fixture,
)
from mcm_field_organism.e1_repetition_pilot_quantitative_real_preflight import (
    audit_e1_repetition_pilot_quantitative_real_preflight,
)
from mcm_field_organism.e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
)
from tests.test_e1_repetition_pilot_quantitative_real_preflight import (
    E1RepetitionPilotQuantitativeRealPreflightTests,
)
from tests.test_e1_repetition_pilot_real_adapter_fixture import (
    E1RepetitionPilotRealAdapterFixtureTests,
)


class E1RepetitionPilotQuantitativeRealHandoffFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1RepetitionPilotQuantitativeRealPreflightTests.setUpClass()
        source = E1RepetitionPilotQuantitativeRealPreflightTests
        cls.preflight = audit_e1_repetition_pilot_quantitative_real_preflight(
            source.pilot_contract,
            source.integration_contract,
            source.runner_fixture,
            E1PilotRealResourceSnapshot(6990774272, 236112711680),
        )
        E1RepetitionPilotRealAdapterFixtureTests.setUpClass()
        cls.plans = E1RepetitionPilotRealAdapterFixtureTests.plans
        cls.initial_field = E1RepetitionPilotRealAdapterFixtureTests.values.initial_field

    def test_two_real_p0_snapshots_are_collected_immediately(self) -> None:
        result = run_quantitative_real_p0_handoff_fixture(
            self.preflight, self.plans.pairs[1], self.initial_field
        )
        self.assertEqual(16, result.total_field_steps_executed)
        self.assertTrue(result.real_quantitative_handoff_implemented)
        self.assertTrue(result.snapshots_collected_before_field_discard)
        self.assertFalse(result.full_pilot_executed)

    def test_quantitative_pair_retains_real_components(self) -> None:
        result = run_quantitative_real_p0_handoff_fixture(
            self.preflight, self.plans.pairs[1], self.initial_field
        )
        self.assertEqual(2, result.quantitative_pair.contact_count)
        self.assertEqual("r2", result.quantitative_pair.refinement_id)
        self.assertGreaterEqual(result.quantitative_pair.activation_linf, 0.0)
        self.assertGreaterEqual(result.quantitative_pair.afterimage_linf, 0.0)

    def test_n1_pair_is_rejected(self) -> None:
        with self.assertRaises(E1RepetitionPilotQuantitativeRealHandoffFixtureError):
            run_quantitative_real_p0_handoff_fixture(
                self.preflight, self.plans.pairs[0], self.initial_field
            )

    def test_fixture_contains_no_authorization_or_persistence(self) -> None:
        source = inspect.getsource(run_quantitative_real_p0_handoff_fixture)
        for forbidden in (
            "E1PilotOnceAuthorization",
            "run_e1_repetition_pilot_once_in_memory",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
