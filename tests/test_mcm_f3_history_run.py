from __future__ import annotations

from dataclasses import replace
import unittest

import numpy as np

from mcm_field_organism import (
    MCMSubstrateArmContract,
    MCMSubstrateMass,
    MCMSubstrateState,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    activate_mcm_f3_field,
    build_shared_mcm_field,
)
from mcm_field_organism.mcm_f3_history_run import (
    ablate_mcm_f3_eta,
    align_mcm_f3_fast_state,
    mcm_f3_history_preregistration,
    neutralize_mcm_f3_mass,
    transfer_mcm_f3_mass,
)


def field():
    frame = ReceptorContactFrame(
        "auditory", "auditory.fixture", "fixture.0", "fixture.clock", 0, 1,
        ("carrier.0", "carrier.1"), (0.0, 0.0),
    )
    base = build_shared_mcm_field(
        (frame,),
        {"auditory": ReceptorDockAnatomy("auditory", "dock.auditory", ((0,), (1,)))},
        sample_offsets=((-1,), (1,)),
    )
    active = activate_mcm_f3_field(base, MCMSubstrateArmContract("p1.active", 1.0, 0.5, 1.0))
    neurons = tuple(
        replace(item, activation=value, afterimage=-value)
        for item, value in zip(active.layer.neurons, (0.25, -0.4), strict=True)
    )
    masses = (
        MCMSubstrateMass(active.substrate.neuron_ids[0], 0.7),
        MCMSubstrateMass(active.substrate.neuron_ids[1], 0.3),
    )
    return replace(
        active,
        layer=replace(active.layer, neurons=neurons),
        substrate=MCMSubstrateState(
            active.substrate.arm,
            masses,
            active.substrate.edge_inventory_digest,
        ),
    )


class MCMF3HistoryRunTests(unittest.TestCase):
    def test_interventions_change_only_their_declared_state_roles(self) -> None:
        original = field()
        aligned = align_mcm_f3_fast_state(original)
        neutral = neutralize_mcm_f3_mass(aligned)
        eta_null = ablate_mcm_f3_eta(aligned)

        self.assertTrue(all(item.activation == item.afterimage == 0.0 for item in aligned.layer.neurons))
        self.assertEqual(original.substrate.masses, aligned.substrate.masses)
        self.assertEqual((0.5, 0.5), tuple(item.mass for item in neutral.substrate.masses))
        self.assertEqual(aligned.layer, neutral.layer)
        self.assertEqual(aligned.substrate.masses, eta_null.substrate.masses)
        self.assertEqual(0.0, eta_null.substrate.arm.eta)

    def test_complete_mass_transfer_preserves_target_fast_state_and_budget(self) -> None:
        target = align_mcm_f3_fast_state(field())
        source = replace(
            target,
            substrate=MCMSubstrateState(
                target.substrate.arm,
                (
                    MCMSubstrateMass(target.substrate.neuron_ids[0], 0.2),
                    MCMSubstrateMass(target.substrate.neuron_ids[1], 0.8),
                ),
                target.substrate.edge_inventory_digest,
            ),
        )
        transferred = transfer_mcm_f3_mass(target, source)

        self.assertEqual(target.layer, transferred.layer)
        self.assertEqual(source.substrate.masses, transferred.substrate.masses)
        self.assertAlmostEqual(1.0, transferred.substrate.total_mass)

    def test_preregistration_keeps_lauf_188_parameters_and_nonclaims(self) -> None:
        plan = mcm_f3_history_preregistration()

        self.assertEqual((1.0, 0.5, 1.0), (
            plan.active_arm.lambda_sm_per_second,
            plan.active_arm.kappa,
            plan.active_arm.eta,
        ))
        self.assertEqual(4, plan.refinement)
        self.assertFalse(plan.memory_claim_allowed)
        self.assertFalse(plan.ai_claim_allowed)


if __name__ == "__main__":
    unittest.main()
