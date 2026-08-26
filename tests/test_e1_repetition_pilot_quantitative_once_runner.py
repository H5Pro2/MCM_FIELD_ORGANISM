from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_quantitative_once_runner import (
    E1QuantitativePilotOnceAuthorization,
    E1RepetitionPilotQuantitativeOnceRunnerError,
    S1_EC44_AUTHORIZATION_SCOPE,
    run_e1_repetition_pilot_quantitative_once_in_memory,
)


class E1RepetitionPilotQuantitativeOnceRunnerTests(unittest.TestCase):
    def test_exact_authorization_is_consumed_once(self) -> None:
        authorization = E1QuantitativePilotOnceAuthorization(
            S1_EC44_AUTHORIZATION_SCOPE,
            25_368,
        )
        authorization.consume()
        self.assertTrue(authorization.consumed)
        with self.assertRaises(E1RepetitionPilotQuantitativeOnceRunnerError):
            authorization.consume()

    def test_changed_scope_or_step_count_is_rejected(self) -> None:
        for scope, steps in (
            ("changed", 25_368),
            (S1_EC44_AUTHORIZATION_SCOPE, 25_367),
        ):
            with self.subTest(scope=scope, steps=steps):
                authorization = E1QuantitativePilotOnceAuthorization(scope, steps)
                with self.assertRaises(
                    E1RepetitionPilotQuantitativeOnceRunnerError
                ):
                    authorization.consume()

    def test_runner_is_in_memory_and_handoffs_p0_immediately(self) -> None:
        source = inspect.getsource(
            run_e1_repetition_pilot_quantitative_once_in_memory
        )
        for forbidden in (
            "open(",
            "write_text",
            "write_bytes",
            "json.dump",
            "Path(",
            "retry",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn('if role_id == "p0_continuous":', source)
        self.assertIn("collect_quantitative_p0_pair", source)
        self.assertLess(
            source.index("collect_quantitative_p0_pair"),
            source.index('states["repeated_active"]'),
        )
        for claim in (
            '"result_decision_permitted": False',
            '"memory_claim_permitted": False',
            '"field_time_claim_permitted": False',
            '"organization_claim_permitted": False',
            '"ai_claim_permitted": False',
        ):
            self.assertIn(claim, source)


if __name__ == "__main__":
    unittest.main()
