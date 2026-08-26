from __future__ import annotations

import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_completion_aligned_refinement import (
    build_e1_completion_aligned_refinement_plans,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.e1_refined_chain_producer_composition import (
    compose_synthetic_e1_refined_chain_result,
)
from mcm_field_organism.e1_refined_formation_runner import (
    run_synthetic_e1_refined_formation,
)
from mcm_field_organism.e1_refined_seven_arm_probe_runner import (
    E1RefinedSevenArmProbeRunnerError,
    run_synthetic_e1_refined_seven_arm_probe,
)
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from mcm_field_organism.receptor_time_model import ReceptorTimeSequence
from tests.test_e1_a0_av_history_producer import contract, field, source


def _formation():
    permutation = source()
    ab = build_e1_completion_aligned_refinement_plans(
        permutation.history_ab, horizon_start_tick=0,
        horizon_end_tick=2_000_000, ticks_per_second=1_000_000.0,
    )
    ba = build_e1_completion_aligned_refinement_plans(
        permutation.history_ba, horizon_start_tick=0,
        horizon_end_tick=2_000_000, ticks_per_second=1_000_000.0,
    )
    initial = field()
    return run_synthetic_e1_refined_formation(
        permutation, ab, ba, initial,
        build_neutral_e1_state(initial.layer, contract()),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


def _probe_sequences():
    histories = source().history_ab
    return tuple(
        ReceptorTimeSequence(
            item.modality_id,
            item.geometry_id,
            item.clock_id,
            (item.frames[0],),
        )
        for item in histories
    )


def _run(formed):
    return run_synthetic_e1_refined_seven_arm_probe(
        formed,
        field,
        _probe_sequences(),
        (MCMFieldStepTime("organism.e1.av-history", 0, 1_000_000, 1_000_000.0),),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


class E1RefinedSevenArmProbeRunnerTests(unittest.TestCase):
    def test_runner_returns_seven_fields_and_keeps_states_frozen(self) -> None:
        formed = _formation().refinements[0]
        before = (formed.b_ab, formed.b_ba)
        result = _run(formed)

        self.assertEqual(7, len(result.field_digests))
        self.assertIs(before[0], formed.b_ab)
        self.assertIs(before[1], formed.b_ba)
        self.assertEqual(0.0, result.probe_ablation_residual)
        self.assertEqual(0.0, result.fixed_adapter_residual)
        self.assertTrue(result.supports_assigned_once)

    def test_three_refinements_compose_into_s1dx_result(self) -> None:
        formation = _formation()
        result = compose_synthetic_e1_refined_chain_result(formation, _run)

        self.assertEqual(3, len(result.refinements))
        self.assertTrue(all(dict(result.controls).values()))
        self.assertIn(result.technical_decision, {
            "NUMERICALLY_UNDECIDABLE",
            "NO_REFINED_WORLD_FORMATION_EFFECT",
            "REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT",
        })

    def test_nonseparate_fields_fail_before_probe(self) -> None:
        shared = field()
        with self.assertRaisesRegex(
            E1RefinedSevenArmProbeRunnerError,
            "object-separated",
        ):
            run_synthetic_e1_refined_seven_arm_probe(
                _formation().refinements[0],
                lambda: shared,
                _probe_sequences(),
                (MCMFieldStepTime("organism.e1.av-history", 0, 1_000_000, 1_000_000.0),),
                NeutralLocalFieldSubstrateConfig(1.0),
                NeutralFastAfterimageConfig(0.5),
            )

    def test_incomplete_support_horizon_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            E1RefinedSevenArmProbeRunnerError,
            "supports",
        ):
            run_synthetic_e1_refined_seven_arm_probe(
                _formation().refinements[0], field, _probe_sequences(),
                (MCMFieldStepTime("organism.e1.av-history", 0, 500_000, 1_000_000.0),),
                NeutralLocalFieldSubstrateConfig(1.0),
                NeutralFastAfterimageConfig(0.5),
            )

    def test_runner_is_private(self) -> None:
        for role in (
            "E1RefinedSevenArmProbeRunnerError",
            "run_synthetic_e1_refined_seven_arm_probe",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
