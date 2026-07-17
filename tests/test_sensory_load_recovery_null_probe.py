from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    SENSORY_NULL_FAMILY_IDS,
    SENSORY_NULL_HISTORY_IDS,
    SENSORY_NULL_RECOVERY_STEPS,
    SensoryLoadRecoveryNullProbeError,
    run_sensory_load_recovery_null_probe,
    sensory_load_recovery_null_public_roles,
)


class SensoryLoadRecoveryNullProbeTests(unittest.TestCase):
    def test_three_families_collapse_after_all_controlled_histories(self) -> None:
        result = run_sensory_load_recovery_null_probe()
        self.assertEqual(36, result.observation_count)
        self.assertTrue(result.exact_receptor_collision)
        self.assertEqual(0.0, result.max_value_difference)
        self.assertEqual(0.0, result.max_local_difference)
        self.assertEqual(0.0, result.max_neighbor_difference)
        self.assertEqual(0.0, result.max_magnitude_difference)

    def test_histories_are_distinct_before_the_identical_probe(self) -> None:
        result = run_sensory_load_recovery_null_probe()
        for family_id in SENSORY_NULL_FAMILY_IDS:
            for recovery_id, _ in SENSORY_NULL_RECOVERY_STEPS:
                group = tuple(
                    observation
                    for observation in result.observations
                    if observation.family_id == family_id
                    and observation.recovery_id == recovery_id
                )
                self.assertEqual(
                    set(SENSORY_NULL_HISTORY_IDS),
                    {observation.history_id for observation in group},
                )
                self.assertEqual(
                    4,
                    len(
                        {
                            observation.history_receptor_digest
                            for observation in group
                        }
                    ),
                )
                self.assertEqual(
                    1,
                    len(
                        {
                            observation.receptor_digest
                            for observation in group
                        }
                    ),
                )

    def test_recovery_profiles_change_time_but_not_history_collision(self) -> None:
        result = run_sensory_load_recovery_null_probe()
        expected = dict(SENSORY_NULL_RECOVERY_STEPS)
        for observation in result.observations:
            self.assertEqual(
                expected[observation.recovery_id],
                observation.recovery_steps,
            )
            self.assertEqual(
                observation.history_steps + observation.recovery_steps,
                observation.probe_tick,
            )

    def test_order_permutations_produce_the_same_canonical_result(self) -> None:
        reference = run_sensory_load_recovery_null_probe()
        reversed_run = run_sensory_load_recovery_null_probe(
            family_order=reversed(SENSORY_NULL_FAMILY_IDS),
            history_order=reversed(SENSORY_NULL_HISTORY_IDS),
            recovery_order=reversed(
                tuple(dict(SENSORY_NULL_RECOVERY_STEPS))
            ),
        )
        self.assertEqual(reference, reversed_run)
        self.assertEqual(reference.digest(), reversed_run.digest())

    def test_observer_is_passive_and_observations_are_immutable(self) -> None:
        observed = []
        with_observer = run_sensory_load_recovery_null_probe(
            observer=observed.append
        )
        without_observer = run_sensory_load_recovery_null_probe()
        self.assertEqual(without_observer, with_observer)
        self.assertEqual(36, len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].history_id = "changed"  # type: ignore[misc]

    def test_fixed_gain_and_static_clipping_preserve_the_null_collision(
        self,
    ) -> None:
        result = run_sensory_load_recovery_null_probe()
        self.assertTrue(result.fixed_gain_collision)
        self.assertTrue(result.static_clipping_collision)
        self.assertFalse(result.writes_back)
        self.assertFalse(result.mechanism_released)
        with self.assertRaises(SensoryLoadRecoveryNullProbeError):
            replace(result, writes_back=True)
        with self.assertRaises(SensoryLoadRecoveryNullProbeError):
            replace(result, mechanism_released=True)

    def test_invalid_or_incomplete_program_orders_are_rejected(self) -> None:
        invalid_calls = (
            lambda: run_sensory_load_recovery_null_probe(
                family_order=("auditory",),
            ),
            lambda: run_sensory_load_recovery_null_probe(
                history_order=SENSORY_NULL_HISTORY_IDS[:-1],
            ),
            lambda: run_sensory_load_recovery_null_probe(
                recovery_order=("r0", "r1", "r1"),
            ),
        )
        for call in invalid_calls:
            with self.assertRaises(SensoryLoadRecoveryNullProbeError):
                call()

    def test_public_results_retain_no_raw_sensor_payload_or_mechanism(self) -> None:
        observation_roles, result_roles = (
            sensory_load_recovery_null_public_roles()
        )
        forbidden = {
            "raw_audio",
            "raw_video",
            "frame",
            "samples",
            "pixels",
            "image",
            "gain_value",
            "sensitivity",
            "adaptation_rate",
            "threshold",
            "target",
            "memory",
            "semantic_label",
            "object_class",
        }
        self.assertTrue(forbidden.isdisjoint(observation_roles))
        self.assertTrue(forbidden.isdisjoint(result_roles))


if __name__ == "__main__":
    unittest.main()
