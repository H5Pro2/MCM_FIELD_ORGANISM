from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_p0_identifiability_audit import (
    audit_e1_repetition_pilot_p0_identifiability,
)
from tests.test_e1_repetition_pilot_real_preflight import (
    E1RepetitionPilotRealPreflightTests,
)


class E1RepetitionPilotP0IdentifiabilityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1RepetitionPilotRealPreflightTests.setUpClass()
        cls.contract = E1RepetitionPilotRealPreflightTests.contract
        cls.plans = E1RepetitionPilotRealPreflightTests.plans

    def test_digest_only_p0_result_is_not_quantitatively_identifiable(self) -> None:
        result = audit_e1_repetition_pilot_p0_identifiability(
            self.contract, self.plans
        )
        self.assertEqual(
            "P0_MAGNITUDE_NOT_IDENTIFIABLE_FROM_EC34_SCHEMA",
            result.decision,
        )
        self.assertTrue(result.corrected_runner_implementation_permitted)
        self.assertFalse(result.field_execution_permitted)

    def test_n1_and_n2_timing_roles_are_separated(self) -> None:
        result = audit_e1_repetition_pilot_p0_identifiability(
            self.contract, self.plans
        )
        checks = dict(result.checks)
        self.assertTrue(checks["n1-schedules-time-identical"])
        self.assertTrue(checks["n2-schedules-time-distinct"])
        self.assertTrue(checks["n2-exposure-and-final-completion-matched"])

    def test_audit_contains_no_field_execution_or_result_input(self) -> None:
        source = inspect.getsource(audit_e1_repetition_pilot_p0_identifiability)
        for forbidden in (
            "run_neutral_asynchronous_field",
            "run_e1_repetition_pilot_once_in_memory",
            "E1RepetitionPilotOnceRawResult",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
