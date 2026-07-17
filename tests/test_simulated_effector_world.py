from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    CYCLE_DIRECTIONS,
    INVERSE_SEQUENCE_IDS,
    InterventionCause,
    RESET_TICKS,
    SimulatedEffectorWorldError,
    SimulatedEffectorWorldContractResult,
    SimulatedWorldReceptorFrame,
    SimulatedWorldState,
    SimulatedWorldTransition,
    WORLD_CAUSES,
    WORLD_DELTAS,
    WORLD_POSITIONS,
    WorldIntervention,
    advance_simulated_world,
    advance_simulated_world_interventions,
    receptor_frame_from_world,
    reset_simulated_effector_world,
    run_simulated_effector_world_contract_probe,
    simulated_effector_world_public_roles,
)


class SimulatedEffectorWorldTests(unittest.TestCase):
    def test_complete_preregistered_family_is_present(self) -> None:
        result = run_simulated_effector_world_contract_probe()
        self.assertEqual(42, len(result.observations))
        self.assertEqual(21, len(result.cause_pairs))
        self.assertEqual(28, len(result.sequences))
        self.assertEqual(14, len(result.resets))

    def test_n0_zero_intervention_is_stable(self) -> None:
        result = run_simulated_effector_world_contract_probe()
        self.assertTrue(result.n0_zero_is_stable)

    def test_n1_to_n4_reversibility_and_cycles_hold(self) -> None:
        result = run_simulated_effector_world_contract_probe()
        self.assertTrue(result.n1_plus_minus_returns)
        self.assertTrue(result.n2_minus_plus_returns)
        self.assertTrue(result.n3_positive_cycles_return)
        self.assertTrue(result.n4_negative_cycles_return)

    def test_n5_cause_changes_provenance_not_world_or_receptor(self) -> None:
        result = run_simulated_effector_world_contract_probe()
        self.assertTrue(result.n5_cause_is_sensor_neutral)
        for pair in result.cause_pairs:
            self.assertTrue(pair.provenance_distinct)
            self.assertTrue(pair.world_consequence_equal)
            self.assertTrue(pair.receptor_equal)

    def test_receptor_frame_contains_only_the_completed_world_contact(self) -> None:
        for position in WORLD_POSITIONS:
            frame = receptor_frame_from_world(
                SimulatedWorldState(tick=7, position=position)
            )
            self.assertEqual(7, frame.source_tick)
            self.assertEqual(1, frame.contact_values.count(1.0))
            self.assertEqual(1.0, frame.contact_values[position])

    def test_n6_and_n7_observer_and_order_are_neutral(self) -> None:
        observed = []
        reference = run_simulated_effector_world_contract_probe()
        permuted = run_simulated_effector_world_contract_probe(
            position_order=reversed(WORLD_POSITIONS),
            delta_order=reversed(WORLD_DELTAS),
            cause_order=reversed(WORLD_CAUSES),
            inverse_order=reversed(INVERSE_SEQUENCE_IDS),
            cycle_order=reversed(CYCLE_DIRECTIONS),
            reset_tick_order=reversed(RESET_TICKS),
            observer=observed.append,
        )
        self.assertEqual(reference, permuted)
        self.assertEqual(reference.digest(), permuted.digest())
        self.assertTrue(permuted.n6_observer_is_neutral)
        self.assertTrue(permuted.n7_order_is_neutral)
        self.assertEqual(168, len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].effort = 2  # type: ignore[misc]

    def test_observer_mutation_is_detected(self) -> None:
        def mutate(transition: SimulatedWorldTransition) -> None:
            object.__setattr__(transition, "effort", 2)

        with self.assertRaises(SimulatedEffectorWorldError):
            advance_simulated_world(
                SimulatedWorldState(tick=0, position=0),
                WorldIntervention(
                    source_tick=0,
                    delta=1,
                    cause=InterventionCause.EXTERNAL,
                ),
                observer=mutate,
            )

    def test_n8_reset_is_reproducible_and_creates_no_receptor(self) -> None:
        result = run_simulated_effector_world_contract_probe()
        self.assertTrue(result.n8_reset_is_reproducible)
        resets = {
            reset_simulated_effector_world(
                SimulatedWorldState(tick=tick, position=position)
            )
            for tick in RESET_TICKS
            for position in WORLD_POSITIONS
        }
        self.assertEqual(1, len(resets))
        reset = resets.pop()
        self.assertEqual(SimulatedWorldState(tick=0, position=0), reset.world)

    def test_invalid_world_contract_inputs_are_rejected(self) -> None:
        invalid_calls = (
            lambda: SimulatedWorldState(tick=0, position=7),
            lambda: SimulatedWorldState(tick=0, position=1.0),
            lambda: WorldIntervention(
                source_tick=0,
                delta=2,
                cause=InterventionCause.EXTERNAL,
            ),
            lambda: WorldIntervention(
                source_tick=0,
                delta=0.5,
                cause=InterventionCause.EXTERNAL,
            ),
            lambda: WorldIntervention(
                source_tick=0,
                delta=0,
                cause="unknown",  # type: ignore[arg-type]
            ),
            lambda: advance_simulated_world(
                SimulatedWorldState(tick=1, position=0),
                WorldIntervention(
                    source_tick=0,
                    delta=0,
                    cause=InterventionCause.EXTERNAL,
                ),
            ),
            lambda: advance_simulated_world_interventions(
                SimulatedWorldState(tick=0, position=0),
                (),
            ),
            lambda: advance_simulated_world_interventions(
                SimulatedWorldState(tick=0, position=0),
                (
                    WorldIntervention(0, 1, InterventionCause.EXTERNAL),
                    WorldIntervention(0, -1, InterventionCause.EXTERNAL),
                ),
            ),
            lambda: SimulatedWorldReceptorFrame(
                source_tick=1,
                contact_values=(0.0,) * 7,
            ),
        )
        for call in invalid_calls:
            with self.assertRaises(SimulatedEffectorWorldError):
                call()

    def test_passive_result_cannot_claim_mcm_write_or_autonomy(self) -> None:
        result = run_simulated_effector_world_contract_probe()
        self.assertFalse(result.writes_to_mcm)
        self.assertFalse(result.autonomous)
        with self.assertRaises(SimulatedEffectorWorldError):
            replace(result, writes_to_mcm=True)
        with self.assertRaises(SimulatedEffectorWorldError):
            replace(result, autonomous=True)

    def test_invalid_probe_orders_are_rejected(self) -> None:
        invalid_calls = (
            lambda: run_simulated_effector_world_contract_probe(
                position_order=(0, 1)
            ),
            lambda: run_simulated_effector_world_contract_probe(
                delta_order=(-1, 0, 0)
            ),
            lambda: run_simulated_effector_world_contract_probe(
                cause_order=(InterventionCause.EXTERNAL,) * 2
            ),
            lambda: run_simulated_effector_world_contract_probe(
                inverse_order=("plus-minus", "plus-minus")
            ),
            lambda: run_simulated_effector_world_contract_probe(
                cycle_order=(1, 1)
            ),
            lambda: run_simulated_effector_world_contract_probe(
                reset_tick_order=(0, 0)
            ),
        )
        for call in invalid_calls:
            with self.assertRaises(SimulatedEffectorWorldError):
                call()

    def test_public_receptor_roles_do_not_leak_cause_or_delta(self) -> None:
        role_groups = simulated_effector_world_public_roles()
        receptor_roles = role_groups[2]
        self.assertEqual(("source_tick", "contact_values"), receptor_roles)
        forbidden = {
            "activation",
            "afterimage",
            "neuron_id",
            "action_value",
            "winner",
            "reward",
            "target",
            "success",
            "semantic_label",
            "learning_rate",
        }
        for roles in role_groups:
            self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
