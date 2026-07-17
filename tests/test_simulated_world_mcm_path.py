from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    InterventionCause,
    SimulatedEffectorResetState,
    SimulatedWorldMCMPathError,
    SimulatedWorldReceptorFrame,
    SimulatedWorldState,
    WORLD_CAUSES,
    WORLD_DELTAS,
    WORLD_POSITIONS,
    reset_simulated_effector_world,
    run_simulated_world_mcm_path_probe,
    simulated_world_mcm_path_public_roles,
    simulated_world_receptor_to_contact_frame,
)


class SimulatedWorldMCMPathTests(unittest.TestCase):
    def test_complete_preregistered_branch_and_pair_family_is_present(self) -> None:
        result = run_simulated_world_mcm_path_probe()
        self.assertEqual(42, len(result.observations))
        self.assertEqual(21, len(result.cause_pairs))

    def test_all_signal_stages_are_exactly_lossless(self) -> None:
        result = run_simulated_world_mcm_path_probe()
        self.assertTrue(result.all_simulated_to_adapter_lossless)
        self.assertTrue(result.all_adapter_to_field_lossless)
        self.assertTrue(result.all_afterimages_zero)
        self.assertTrue(result.all_distributor_states_equal)
        self.assertTrue(result.all_carrier_counts_seven)

    def test_all_causes_collapse_after_outer_provenance(self) -> None:
        result = run_simulated_world_mcm_path_probe()
        self.assertTrue(result.all_cause_pairs_collapse_after_provenance)
        for pair in result.cause_pairs:
            self.assertTrue(pair.provenance_distinct)
            self.assertTrue(pair.simulated_receptor_equal)
            self.assertTrue(pair.adapted_receptor_equal)
            self.assertTrue(pair.field_window_equal)
            self.assertTrue(pair.constellation_equal)

    def test_wrap_targets_reach_the_correct_activation_carrier(self) -> None:
        result = run_simulated_world_mcm_path_probe()
        self.assertTrue(result.wrap_targets_correct)
        targets = {
            (item.start_position, item.delta, item.next_position)
            for item in result.observations
            if (item.start_position, item.delta) in ((0, -1), (6, 1))
        }
        self.assertEqual({(0, -1, 6), (6, 1, 0)}, targets)

    def test_adapter_has_only_contact_and_time_as_source_roles(self) -> None:
        frame = SimulatedWorldReceptorFrame(
            source_tick=4,
            contact_values=(0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0),
        )
        adapted = simulated_world_receptor_to_contact_frame(frame)
        self.assertEqual("simulated.contact", adapted.modality_id)
        self.assertEqual("simulated.ring7.receptor.v1", adapted.geometry_id)
        self.assertEqual("simulated.world", adapted.clock_id)
        self.assertEqual((4, 5), (adapted.window_start_tick, adapted.window_end_tick))
        self.assertEqual(frame.contact_values, adapted.values)
        self.assertNotIn("cause", adapted.__dataclass_fields__)
        self.assertNotIn("delta", adapted.__dataclass_fields__)

    def test_reset_status_cannot_be_adapted_without_a_regular_world_read(self) -> None:
        reset = reset_simulated_effector_world(
            SimulatedWorldState(tick=9, position=4)
        )
        self.assertIsInstance(reset, SimulatedEffectorResetState)
        with self.assertRaises(SimulatedWorldMCMPathError):
            simulated_world_receptor_to_contact_frame(reset)  # type: ignore[arg-type]

    def test_observer_and_order_are_neutral(self) -> None:
        observed = []
        reference = run_simulated_world_mcm_path_probe()
        permuted = run_simulated_world_mcm_path_probe(
            position_order=reversed(WORLD_POSITIONS),
            delta_order=reversed(WORLD_DELTAS),
            cause_order=reversed(WORLD_CAUSES),
            observer=observed.append,
        )
        self.assertEqual(reference, permuted)
        self.assertEqual(reference.digest(), permuted.digest())
        self.assertTrue(permuted.observer_is_neutral)
        self.assertTrue(permuted.order_is_neutral)
        self.assertEqual(42, len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].delta = 0  # type: ignore[misc]

    def test_invalid_adapter_and_probe_inputs_are_rejected(self) -> None:
        invalid_calls = (
            lambda: simulated_world_receptor_to_contact_frame(object()),
            lambda: run_simulated_world_mcm_path_probe(position_order=(0, 1)),
            lambda: run_simulated_world_mcm_path_probe(delta_order=(-1, 0, 0)),
            lambda: run_simulated_world_mcm_path_probe(
                cause_order=(InterventionCause.EXTERNAL,) * 2
            ),
            lambda: run_simulated_world_mcm_path_probe(
                cause_order=("unknown", InterventionCause.EXTERNAL)  # type: ignore[arg-type]
            ),
        )
        for call in invalid_calls:
            with self.assertRaises(SimulatedWorldMCMPathError):
                call()

    def test_result_cannot_claim_ring_topology_writeback_or_field_rule(self) -> None:
        result = run_simulated_world_mcm_path_probe()
        self.assertFalse(result.ring_topology_preserved)
        self.assertFalse(result.writes_back)
        self.assertFalse(result.field_rule_released)
        with self.assertRaises(SimulatedWorldMCMPathError):
            replace(result, ring_topology_preserved=True)
        with self.assertRaises(SimulatedWorldMCMPathError):
            replace(result, writes_back=True)
        with self.assertRaises(SimulatedWorldMCMPathError):
            replace(result, field_rule_released=True)

    def test_public_results_expose_no_action_or_semantic_roles(self) -> None:
        forbidden = {
            "action_value",
            "winner",
            "reward",
            "target",
            "success",
            "semantic_label",
            "learning_rate",
            "receptor_gain",
        }
        for roles in simulated_world_mcm_path_public_roles():
            self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
