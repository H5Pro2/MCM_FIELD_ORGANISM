from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_quantitative_p0_runner_fixture import (
    run_quantitative_p0_handoff_runner_fixture,
)
from mcm_field_organism.e1_repetition_pilot_quantitative_real_preflight import (
    audit_e1_repetition_pilot_quantitative_real_preflight,
)
from mcm_field_organism.e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
)
from tests.test_e1_repetition_pilot_quantitative_p0_runner_fixture import (
    E1RepetitionPilotQuantitativeP0RunnerFixtureTests,
)


class E1RepetitionPilotQuantitativeRealPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1RepetitionPilotQuantitativeP0RunnerFixtureTests.setUpClass()
        source = E1RepetitionPilotQuantitativeP0RunnerFixtureTests
        cls.integration_contract = source.contract
        cls.template = source.template
        cls.runner_fixture = run_quantitative_p0_handoff_runner_fixture(
            cls.integration_contract, cls.template
        )
        from tests.test_e1_repetition_pilot_quantitative_p0_integration_contract import (
            E1RepetitionPilotQuantitativeP0IntegrationContractTests,
        )
        cls.pilot_contract = (
            E1RepetitionPilotQuantitativeP0IntegrationContractTests.pilot_contract
        )
        cls.resources = E1PilotRealResourceSnapshot(6 * 1024**3, 200 * 1024**3)

    def test_base_ready_but_real_handoff_and_authorization_missing(self) -> None:
        result = audit_e1_repetition_pilot_quantitative_real_preflight(
            self.pilot_contract,
            self.integration_contract,
            self.runner_fixture,
            self.resources,
        )
        self.assertEqual("VORBEREITET_REAL_HANDOFF_FEHLT", result.decision)
        self.assertTrue(result.real_runner_implementation_permitted)
        self.assertFalse(result.real_quantitative_handoff_implemented)
        self.assertFalse(result.owner_execution_authorized)
        self.assertFalse(result.pilot_execution_permitted)

    def test_insufficient_memory_requires_correction(self) -> None:
        resources = replace(self.resources, free_memory_bytes=4 * 1024**3 - 1)
        result = audit_e1_repetition_pilot_quantitative_real_preflight(
            self.pilot_contract,
            self.integration_contract,
            self.runner_fixture,
            resources,
        )
        self.assertEqual("KORREKTUR", result.decision)
        self.assertFalse(result.real_runner_implementation_permitted)

    def test_preflight_cannot_execute_or_accept_authorization(self) -> None:
        source = inspect.getsource(
            audit_e1_repetition_pilot_quantitative_real_preflight
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
