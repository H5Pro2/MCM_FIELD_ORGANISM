from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    build_shared_mcm_field,
)
from mcm_field_organism.current_api import (
    MCMLocalDevelopmentContract,
    S1BCausalTwoStageError,
    run_s1b_causal_two_stage,
)


EQUATION_ID = "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1"
FIELD_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)
ACTIVE_CONTRACT = MCMLocalDevelopmentContract(EQUATION_ID, 8.0, 0.25)
NULL_CONTRACT = MCMLocalDevelopmentContract(EQUATION_ID, 8.0, 0.0)


def frame(modality_id: str, index: int, value: float) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality_id,
        geometry_id=f"{modality_id}.w6e.geometry.v1",
        snapshot_id=f"{modality_id}.w6e.snapshot.{index}",
        clock_id=f"{modality_id}.w6e.source",
        window_start_tick=index,
        window_end_tick=index + 1,
        carrier_ids=(f"{modality_id}.carrier.0",),
        values=(value,),
    )


def sequence(
    modality_id: str,
    events: tuple[tuple[int, float], ...],
    *,
    snapshot_offset: int = 0,
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality_id,
        f"{modality_id}.w6e.geometry.v1",
        "organism.w6e.test",
        tuple(
            OrganismTimedReceptorFrame(
                frame(modality_id, snapshot_offset + index, value),
                CommonFieldTime(
                    "organism.w6e.test",
                    completion_tick - 1,
                    completion_tick,
                ),
            )
            for index, (completion_tick, value) in enumerate(events)
        ),
    )


def history_a() -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    return (
        sequence("auditory", ((2, 0.8), (5, 0.4), (9, -0.2))),
        sequence("visual", ((4, 0.6), (7, 0.2), (9, -0.3))),
    )


def history_b() -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    return (
        sequence(
            "auditory",
            ((2, -0.7), (5, -0.3), (9, 0.5)),
            snapshot_offset=100,
        ),
        sequence(
            "visual",
            ((4, -0.5), (7, -0.1), (9, 0.4)),
            snapshot_offset=100,
        ),
    )


def probe() -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    return (
        sequence("auditory", ((14, 0.2), (18, -0.1)), snapshot_offset=200),
        sequence("visual", ((15, 0.3), (18, 0.1)), snapshot_offset=200),
    )


def fresh_field():
    auditory = frame("auditory", 1000, 0.0)
    visual = frame("visual", 1000, 0.0)
    return build_shared_mcm_field(
        (auditory, visual),
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


def run(*, second_history=None):
    return run_s1b_causal_two_stage(
        fresh_field(),
        history_a(),
        history_b() if second_history is None else second_history,
        probe(),
        (MCMFieldStepTime("organism.w6e.test", 0, 12, 10.0),),
        (MCMFieldStepTime("organism.w6e.test", 12, 20, 10.0),),
        FIELD_CONFIG,
        ACTIVE_CONTRACT,
        NULL_CONTRACT,
        AFTERIMAGE_CONFIG,
    )


class S1BCausalTwoStageTests(unittest.TestCase):
    def test_complete_four_arm_check_observes_constructed_l_feedback(self) -> None:
        result = run()

        self.assertEqual(
            "LOCAL_L_STATE_CAUSALLY_ALTERS_LATER_S_TRAJECTORY_IN_S1B_REFERENCE",
            result.technical_decision,
        )
        self.assertTrue(result.fast_r_n_equal)
        self.assertTrue(result.fast_r_x_equal)
        self.assertTrue(result.null_formation_equal)
        self.assertTrue(result.null_probe_equal)
        self.assertGreater(result.l_a_linf, result.tolerance)
        self.assertGreater(result.l_ab_linf, result.tolerance)
        self.assertGreater(max(result.d_rn_s, result.d_rx_s), result.tolerance)
        self.assertEqual(
            ("retained", "neutralized", "swapped", "null"),
            tuple(trace.arm_id for trace in result.traces),
        )
        supports = {
            tuple(sample.completion_tick for sample in trace.samples)
            for trace in result.traces
        }
        self.assertEqual(1, len(supports))

    def test_identical_donor_stops_before_probe(self) -> None:
        result = run(second_history=history_a())

        self.assertEqual("STOP_NONINFORMATIVE_FORMATION", result.technical_decision)
        self.assertLessEqual(result.l_ab_linf, result.tolerance)
        self.assertEqual(0, result.probe_support_count)
        self.assertEqual((), result.traces)
        self.assertIsNone(result.null_probe_equal)

    def test_result_is_deterministic_and_immutable(self) -> None:
        first = run()
        second = run()

        self.assertEqual(first, second)
        with self.assertRaises(FrozenInstanceError):
            first.d_rn_s = 0.0  # type: ignore[misc]

    def test_temporally_different_donor_is_rejected_before_execution(self) -> None:
        mismatched = (
            sequence("auditory", ((3, -0.7), (5, -0.3), (9, 0.5))),
            sequence("visual", ((4, -0.5), (7, -0.1), (9, 0.4))),
        )
        with self.assertRaisesRegex(
            S1BCausalTwoStageError,
            "identical geometry and temporal support",
        ):
            run(second_history=mismatched)


if __name__ == "__main__":
    unittest.main()
