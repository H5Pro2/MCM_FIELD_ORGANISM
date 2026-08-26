from __future__ import annotations

import unittest

from mcm_field_organism.preregistered_long_observation_probe import (
    DURATIONS,
    TOLERANCE,
    run_preregistered_long_observation_probe,
)


class PreregisteredLongObservationProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_preregistered_long_observation_probe()

    def test_contracts_and_all_duration_stages_are_complete(self) -> None:
        self.assertTrue(self.result.time_contract_valid)
        self.assertTrue(self.result.contact_contract_valid)
        self.assertEqual(DURATIONS, tuple(item.duration_seconds for item in self.result.durations))

    def test_all_ticks_match_the_additive_null_model(self) -> None:
        self.assertTrue(self.result.all_cases_additive)
        for item in self.result.durations:
            self.assertLessEqual(item.maximum_activation_superposition_error, TOLERANCE)
            self.assertLessEqual(item.maximum_afterimage_superposition_error, TOLERANCE)

    def test_joint_repeat_is_exactly_reproducible(self) -> None:
        self.assertTrue(self.result.all_cases_reproducible)
        self.assertTrue(all(item.joint_repeat_digests_equal for item in self.result.durations))

    def test_aligned_holdout_is_equal(self) -> None:
        self.assertTrue(self.result.all_holdouts_equal)
        self.assertTrue(all(item.holdout_digests_equal for item in self.result.durations))

    def test_stop_line_and_execution_boundary_are_preserved(self) -> None:
        self.assertEqual(
            "known_current_additive_one_step_fast_effects_only",
            self.result.stop_line,
        )
        self.assertFalse(self.result.observer_writeback_performed)
        self.assertFalse(self.result.runtime_changed)


if __name__ == "__main__":
    unittest.main()
