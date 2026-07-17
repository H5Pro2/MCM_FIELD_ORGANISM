from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    FIELD_INERTIA_AMPLITUDES,
    FIELD_INERTIA_BRANCH_IDS,
    FIELD_INERTIA_PAUSE_STEPS,
    FIELD_INERTIA_TAUS,
    LocalFieldInertiaProbeError,
    local_field_inertia_public_roles,
    run_local_field_inertia_probe,
)


class LocalFieldInertiaProbeTests(unittest.TestCase):
    def test_all_preregistered_pairs_are_present(self) -> None:
        result = run_local_field_inertia_probe()
        self.assertEqual(27, result.parameter_pair_count)
        self.assertEqual(54, len(result.observations))

    def test_field_orientation_is_readable_and_mirrored(self) -> None:
        result = run_local_field_inertia_probe()
        self.assertTrue(result.all_previous_centers_equal)
        self.assertTrue(result.all_perceptions_distinct)
        self.assertTrue(result.all_orientations_mirrored)

    def test_existing_transition_outputs_are_exactly_inert(self) -> None:
        result = run_local_field_inertia_probe()
        self.assertTrue(result.all_hold_outputs_collide)
        self.assertTrue(result.all_projection_outputs_collide)
        self.assertEqual(0.0, result.max_hold_activation_difference)
        self.assertEqual(0.0, result.max_hold_afterimage_difference)
        self.assertEqual(0.0, result.max_projection_activation_difference)
        self.assertEqual(0.0, result.max_projection_afterimage_difference)

    def test_full_next_neurons_retain_distinct_perception_provenance(self) -> None:
        result = run_local_field_inertia_probe()
        self.assertTrue(result.all_next_neuron_provenance_distinct)
        for index in range(0, len(result.observations), 2):
            forward, reverse = result.observations[index : index + 2]
            self.assertNotEqual(
                forward.perception_digest,
                reverse.perception_digest,
            )
            self.assertEqual(
                forward.hold_output_digest,
                reverse.hold_output_digest,
            )
            self.assertNotEqual(
                forward.hold_neuron_digest,
                reverse.hold_neuron_digest,
            )

    def test_exact_reset_is_neutral(self) -> None:
        self.assertTrue(run_local_field_inertia_probe().all_resets_neutral)

    def test_order_and_observer_do_not_change_canonical_result(self) -> None:
        observed = []
        reference = run_local_field_inertia_probe()
        permuted = run_local_field_inertia_probe(
            amplitude_order=reversed(FIELD_INERTIA_AMPLITUDES),
            tau_order=reversed(FIELD_INERTIA_TAUS),
            pause_order=reversed(FIELD_INERTIA_PAUSE_STEPS),
            branch_order=reversed(FIELD_INERTIA_BRANCH_IDS),
            observer=observed.append,
        )
        self.assertEqual(reference, permuted)
        self.assertEqual(reference.digest(), permuted.digest())
        self.assertEqual(54, len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].branch_id = "changed"  # type: ignore[misc]

    def test_result_cannot_claim_writeback_or_mechanism_release(self) -> None:
        result = run_local_field_inertia_probe()
        self.assertFalse(result.writes_back)
        self.assertFalse(result.mechanism_released)
        with self.assertRaises(LocalFieldInertiaProbeError):
            replace(result, writes_back=True)
        with self.assertRaises(LocalFieldInertiaProbeError):
            replace(result, mechanism_released=True)

    def test_invalid_parameter_orders_are_rejected(self) -> None:
        invalid_calls = (
            lambda: run_local_field_inertia_probe(amplitude_order=(1.0,)),
            lambda: run_local_field_inertia_probe(tau_order=(1.0, 2.0, 2.0)),
            lambda: run_local_field_inertia_probe(pause_order=(0, 1)),
            lambda: run_local_field_inertia_probe(
                branch_order=("forward", "forward")
            ),
        )
        for call in invalid_calls:
            with self.assertRaises(LocalFieldInertiaProbeError):
                call()

    def test_public_roles_contain_no_new_field_rule_or_semantics(self) -> None:
        observation_roles, result_roles = local_field_inertia_public_roles()
        forbidden = {
            "raw_input",
            "world_frame",
            "gain",
            "threshold",
            "coupling",
            "weight",
            "learning_rate",
            "target",
            "reward",
            "semantic_label",
            "movement_class",
            "direction_command",
        }
        self.assertTrue(forbidden.isdisjoint(observation_roles))
        self.assertTrue(forbidden.isdisjoint(result_roles))


if __name__ == "__main__":
    unittest.main()
