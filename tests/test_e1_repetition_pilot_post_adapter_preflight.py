from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_post_adapter_preflight import (
    audit_e1_repetition_pilot_post_adapter_preflight,
)
from mcm_field_organism.e1_repetition_pilot_real_adapter_fixture import (
    run_e1_repetition_pilot_real_adapter_fixture,
)
from mcm_field_organism.e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
    audit_e1_repetition_pilot_real_preflight,
)
from tests.test_e1_repetition_pilot_real_preflight import (
    E1RepetitionPilotRealPreflightTests,
)


class E1RepetitionPilotPostAdapterPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1RepetitionPilotRealPreflightTests.setUpClass()
        cls.contract = E1RepetitionPilotRealPreflightTests.contract
        cls.plans = E1RepetitionPilotRealPreflightTests.plans
        cls.runner_fixture = E1RepetitionPilotRealPreflightTests.runner_fixture
        cls.resources = E1PilotRealResourceSnapshot(8121556992, 236527480832)
        cls.previous = audit_e1_repetition_pilot_real_preflight(
            cls.contract, cls.plans, cls.runner_fixture, cls.resources
        )

        from tests.test_e1_repetition_pilot_real_adapter_fixture import (
            E1RepetitionPilotRealAdapterFixtureTests,
        )

        E1RepetitionPilotRealAdapterFixtureTests.setUpClass()
        values = E1RepetitionPilotRealAdapterFixtureTests.values
        cls.adapter = run_e1_repetition_pilot_real_adapter_fixture(
            cls.plans.pairs[1], values.initial_field, values.initial_state
        )

    def test_adapter_is_confirmed_but_execution_remains_locked(self) -> None:
        result = audit_e1_repetition_pilot_post_adapter_preflight(
            self.contract, self.previous, self.adapter, self.resources
        )
        self.assertEqual("ADAPTER_BESTAETIGT_FREIGABE_FEHLT", result.decision)
        self.assertTrue(result.technical_release_ready)
        self.assertTrue(result.adapter_implemented)
        self.assertFalse(result.owner_execution_authorized)
        self.assertFalse(result.pilot_execution_permitted)

    def test_insufficient_disk_requires_correction(self) -> None:
        resources = replace(self.resources, free_disk_bytes=1024**3 - 1)
        result = audit_e1_repetition_pilot_post_adapter_preflight(
            self.contract, self.previous, self.adapter, resources
        )
        self.assertEqual("KORREKTUR", result.decision)
        self.assertFalse(result.technical_release_ready)

    def test_preflight_cannot_run_fields_or_accept_authorization(self) -> None:
        source = inspect.getsource(audit_e1_repetition_pilot_post_adapter_preflight)
        for forbidden in (
            "run_neutral_asynchronous_field",
            "run_prepared_real_formation_arm_in_memory",
            "owner_authorized",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_adapter_fixture_is_exactly_bound(self) -> None:
        with self.assertRaises(ValueError):
            replace(self.adapter, result_digest="0" * 64)


if __name__ == "__main__":
    unittest.main()
