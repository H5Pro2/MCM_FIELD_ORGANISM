from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_quantitative_final_preflight import (
    audit_e1_repetition_pilot_quantitative_final_preflight,
)
from mcm_field_organism.e1_repetition_pilot_quantitative_full_runner_fixture import (
    run_quantitative_full_runner_fixture,
)
from mcm_field_organism.e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
)
from tests.test_e1_repetition_pilot_quantitative_full_runner_fixture import (
    E1RepetitionPilotQuantitativeFullRunnerFixtureTests,
)


class E1RepetitionPilotQuantitativeFinalPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1RepetitionPilotQuantitativeFullRunnerFixtureTests.setUpClass()
        source = E1RepetitionPilotQuantitativeFullRunnerFixtureTests
        cls.pilot_contract = source.pilot_contract
        cls.integration_contract = source.integration_contract
        cls.previous = source.preflight
        cls.runner_fixture = run_quantitative_full_runner_fixture(
            source.pilot_contract,
            source.integration_contract,
            source.preflight,
            source.template,
        )
        cls.resources = E1PilotRealResourceSnapshot(6 * 1024**3, 200 * 1024**3)

    def test_technical_ready_but_new_authorization_missing(self) -> None:
        result = audit_e1_repetition_pilot_quantitative_final_preflight(
            self.pilot_contract,
            self.integration_contract,
            self.previous,
            self.runner_fixture,
            self.resources,
        )
        self.assertEqual("TECHNISCH_BEREIT_NEUE_FREIGABE_FEHLT", result.decision)
        self.assertTrue(result.technical_execution_ready)
        self.assertFalse(result.owner_execution_authorized)
        self.assertFalse(result.pilot_execution_permitted)

    def test_insufficient_disk_requires_correction(self) -> None:
        resources = replace(self.resources, free_disk_bytes=1024**3 - 1)
        result = audit_e1_repetition_pilot_quantitative_final_preflight(
            self.pilot_contract,
            self.integration_contract,
            self.previous,
            self.runner_fixture,
            resources,
        )
        self.assertEqual("KORREKTUR", result.decision)
        self.assertFalse(result.technical_execution_ready)

    def test_preflight_cannot_execute_or_accept_authorization(self) -> None:
        source = inspect.getsource(
            audit_e1_repetition_pilot_quantitative_final_preflight
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
