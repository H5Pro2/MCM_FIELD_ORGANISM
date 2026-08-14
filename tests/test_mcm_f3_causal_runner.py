from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMF3CausalRunnerError,
    MCMFieldStepTime,
    MCMSubstrateArmContract,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    build_shared_mcm_field,
    run_mcm_f3_causal_comparison,
    run_neutral_asynchronous_field,
)


def frame(modality: str, index: int, value: float) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality,
        geometry_id=f"{modality}.geometry.v1",
        snapshot_id=f"{modality}.snapshot.{index}",
        clock_id=f"{modality}.source",
        window_start_tick=index,
        window_end_tick=index + 1,
        carrier_ids=(f"{modality}.carrier.0",),
        values=(value,),
    )


def sequence(
    modality: str,
    events: tuple[tuple[int, float], ...],
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality,
        f"{modality}.geometry.v1",
        "organism.f3",
        tuple(
            OrganismTimedReceptorFrame(
                frame(modality, index, value),
                CommonFieldTime("organism.f3", completion - 1, completion),
            )
            for index, (completion, value) in enumerate(events)
        ),
    )


def sequences() -> tuple[ReceptorTimeSequence, ...]:
    return (
        sequence("auditory", ((2, 0.9), (7, -0.4))),
        sequence("visual", ((4, -0.7), (9, 0.6))),
    )


def proposal_steps() -> tuple[MCMFieldStepTime, ...]:
    return (
        MCMFieldStepTime("organism.f3", 0, 5, 10.0),
        MCMFieldStepTime("organism.f3", 5, 10, 10.0),
    )


def base_field():
    return build_shared_mcm_field(
        (frame("auditory", 100, 0.0), frame("visual", 100, 0.0)),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,),),
            ),
            "visual": ReceptorDockAnatomy(
                "visual",
                "dock.visual",
                ((1,),),
            ),
        },
        sample_offsets=((-1,), (1,)),
    )


def active_arm() -> MCMSubstrateArmContract:
    return MCMSubstrateArmContract("p1.active", 0.5, 0.4, 0.75)


def run():
    return run_mcm_f3_causal_comparison(
        base_field(),
        sequences(),
        proposal_steps(),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
        active_arm(),
    )


def state_vector(arm) -> np.ndarray:
    return np.asarray(
        [
            *(neuron.activation for neuron in arm.field.layer.neurons),
            *(neuron.afterimage for neuron in arm.field.layer.neurons),
            *(item.mass for item in arm.field.substrate.masses),
        ],
        dtype=np.float64,
    )


class MCMF3CausalRunnerTests(unittest.TestCase):
    def test_every_fixed_arm_uses_the_one_complete_handoff(self) -> None:
        result = run()

        self.assertEqual(4, result.source_support_count)
        self.assertTrue(result.handoff.every_in_horizon_event_assigned_once)
        self.assertEqual(
            (
                "p0.exact",
                "p1.n",
                "p1.2n",
                "p1.4n",
                "b.eta-null",
                "b.kappa-null",
                "b.kappa-inverted",
            ),
            tuple(arm.arm_key for arm in result.arms),
        )
        self.assertTrue(all(len(arm.diagnostics) == 2 for arm in result.arms))
        self.assertTrue(
            all(
                arm.field.last_distribution.field_time.window_end_tick == 10
                for arm in result.arms
            )
        )

    def test_p0_arm_matches_the_existing_neutral_asynchronous_runner(self) -> None:
        comparison = run()
        neutral = run_neutral_asynchronous_field(
            base_field(),
            sequences(),
            proposal_steps(),
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
        )

        self.assertEqual(
            neutral.field.snapshot().digest(),
            comparison.arm("p0.exact").field.snapshot().fast_state_projection_digest(),
        )

    def test_comparison_is_exactly_repeatable(self) -> None:
        first = run()
        second = run()

        self.assertEqual(
            tuple(arm.field.snapshot().digest() for arm in first.arms),
            tuple(arm.field.snapshot().digest() for arm in second.arms),
        )
        self.assertEqual(
            tuple(arm.diagnostics for arm in first.arms),
            tuple(arm.diagnostics for arm in second.arms),
        )

    def test_p1_refinement_is_ordered_and_baselines_remain_separate(self) -> None:
        result = run()
        p1_n = result.arm("p1.n")
        p1_2n = result.arm("p1.2n")
        p1_4n = result.arm("p1.4n")
        coarse_error = np.linalg.norm(state_vector(p1_n) - state_vector(p1_2n))
        fine_error = np.linalg.norm(state_vector(p1_2n) - state_vector(p1_4n))

        self.assertGreater(coarse_error, 0.0)
        self.assertGreater(fine_error, 0.0)
        self.assertLess(fine_error, coarse_error)
        self.assertFalse(
            np.array_equal(
                state_vector(p1_4n),
                state_vector(result.arm("b.eta-null")),
            )
        )
        self.assertEqual(
            (0.5, 0.5),
            result.arm("b.kappa-null").field.snapshot().substrate_mass,
        )
        self.assertFalse(
            np.array_equal(
                state_vector(p1_4n),
                state_vector(result.arm("b.kappa-inverted")),
            )
        )

    def test_every_arm_preserves_mass_and_keeps_diagnostics_out_of_snapshots(self) -> None:
        result = run()

        for arm in result.arms:
            with self.subTest(arm=arm.arm_key):
                self.assertAlmostEqual(1.0, arm.field.substrate.total_mass, places=12)
                self.assertGreaterEqual(
                    min(item.mass for item in arm.field.substrate.masses),
                    0.0,
                )
                encoded = arm.field.snapshot().to_json()
                self.assertNotIn("diagnostics", encoded)
                self.assertNotIn("substep_count", encoded)

    def test_duplicate_source_support_is_rejected_before_any_arm_runs(self) -> None:
        duplicated = (sequences()[0], sequences()[0])
        with self.assertRaisesRegex(MCMF3CausalRunnerError, "duplicate"):
            run_mcm_f3_causal_comparison(
                base_field(),
                duplicated,
                proposal_steps(),
                NeutralLocalFieldSubstrateConfig(1.0),
                NeutralFastAfterimageConfig(0.5),
                active_arm(),
            )


if __name__ == "__main__":
    unittest.main()
