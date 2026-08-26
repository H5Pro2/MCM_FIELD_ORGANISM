from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_once_runner import (
    E1PilotOnceAuthorization,
    E1RepetitionPilotOnceRunnerError,
    S1_EC34_AUTHORIZATION_SCOPE,
    run_e1_repetition_pilot_once_in_memory,
)


class E1RepetitionPilotOnceRunnerTests(unittest.TestCase):
    def test_authorization_is_consumed_exactly_once(self) -> None:
        authorization = E1PilotOnceAuthorization(
            S1_EC34_AUTHORIZATION_SCOPE, 25_368
        )
        authorization.consume()
        self.assertTrue(authorization.consumed)
        with self.assertRaises(E1RepetitionPilotOnceRunnerError):
            authorization.consume()

    def test_wrong_scope_is_rejected(self) -> None:
        authorization = E1PilotOnceAuthorization("wrong", 25_368)
        with self.assertRaises(E1RepetitionPilotOnceRunnerError):
            authorization.consume()

    def test_runner_contains_no_persistence_path(self) -> None:
        source = inspect.getsource(run_e1_repetition_pilot_once_in_memory)
        for forbidden in (
            "write_text",
            "write_bytes",
            "open(",
            "Path(",
            "json.dump",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
