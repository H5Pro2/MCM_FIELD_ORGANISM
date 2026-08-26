from __future__ import annotations

import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_completion_aligned_refinement import (
    E1CompletionAlignedRefinementError,
    build_e1_completion_aligned_refinement_plans,
)
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
)
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


def _sequence() -> ReceptorTimeSequence:
    frames = []
    for index, (start, end, value) in enumerate(
        ((0, 8, 0.25), (8, 16, -0.5))
    ):
        frames.append(
            OrganismTimedReceptorFrame(
                ReceptorContactFrame(
                    modality_id="synthetic",
                    geometry_id="synthetic.one",
                    snapshot_id=f"synthetic.{index}",
                    clock_id="synthetic.source",
                    window_start_tick=index,
                    window_end_tick=index + 1,
                    carrier_ids=("carrier.one",),
                    values=(value,),
                ),
                CommonFieldTime("organism.synthetic", start, end),
            )
        )
    return ReceptorTimeSequence(
        "synthetic",
        "synthetic.one",
        "organism.synthetic",
        tuple(frames),
    )


class E1CompletionAlignedRefinementTests(unittest.TestCase):
    def test_r1_r2_r4_split_only_completion_aligned_intervals(self) -> None:
        result = build_e1_completion_aligned_refinement_plans(
            (_sequence(),),
            horizon_start_tick=0,
            horizon_end_tick=16,
            ticks_per_second=8.0,
        )

        self.assertEqual(("r1", "r2", "r4"), tuple(
            item.refinement_id for item in result.plans
        ))
        self.assertEqual((2, 4, 8), tuple(
            len(item.proposal_steps) for item in result.plans
        ))
        self.assertEqual((8, 16), result.completion_ticks)
        for plan in result.plans:
            self.assertEqual(0, plan.proposal_steps[0].start_tick)
            self.assertEqual(16, plan.proposal_steps[-1].end_tick)

    def test_each_support_stays_once_at_original_completion(self) -> None:
        result = build_e1_completion_aligned_refinement_plans(
            (_sequence(),),
            horizon_start_tick=0,
            horizon_end_tick=16,
            ticks_per_second=8.0,
        )

        for plan in result.plans:
            self.assertEqual(2, plan.handoff.source_event_count)
            self.assertEqual(2, plan.handoff.assigned_event_count)
            self.assertTrue(plan.handoff.every_in_horizon_event_assigned_once)
            observed = tuple(
                group.completion_tick
                for batch in plan.handoff.batches
                for group in batch.completion_groups
            )
            self.assertEqual((8, 16), observed)

    def test_source_contact_integrals_are_exactly_invariant(self) -> None:
        result = build_e1_completion_aligned_refinement_plans(
            (_sequence(),),
            horizon_start_tick=0,
            horizon_end_tick=16,
            ticks_per_second=8.0,
        )

        evidence = tuple(
            (
                item.source_contact_digest,
                item.source_signed_integral,
                item.source_absolute_integral,
                item.source_quadratic_integral,
            )
            for item in result.plans
        )
        self.assertEqual(1, len(set(evidence)))
        self.assertEqual(-0.25, result.plans[0].source_signed_integral)
        self.assertEqual(0.75, result.plans[0].source_absolute_integral)
        self.assertEqual(0.3125, result.plans[0].source_quadratic_integral)

    def test_plan_digest_is_repeatable(self) -> None:
        args = {
            "horizon_start_tick": 0,
            "horizon_end_tick": 16,
            "ticks_per_second": 8.0,
        }
        first = build_e1_completion_aligned_refinement_plans((_sequence(),), **args)
        second = build_e1_completion_aligned_refinement_plans((_sequence(),), **args)

        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(64, len(first.digest()))

    def test_nondivisible_completion_interval_fails_closed(self) -> None:
        sequence = _sequence()
        shifted = ReceptorTimeSequence(
            sequence.modality_id,
            sequence.geometry_id,
            sequence.clock_id,
            (
                OrganismTimedReceptorFrame(
                    sequence.frames[0].frame,
                    CommonFieldTime("organism.synthetic", 0, 7),
                ),
                OrganismTimedReceptorFrame(
                    sequence.frames[1].frame,
                    CommonFieldTime("organism.synthetic", 7, 16),
                ),
            ),
        )
        with self.assertRaisesRegex(
            E1CompletionAlignedRefinementError,
            "not exactly divisible",
        ):
            build_e1_completion_aligned_refinement_plans(
                (shifted,),
                horizon_start_tick=0,
                horizon_end_tick=16,
                ticks_per_second=8.0,
            )

    def test_completion_outside_horizon_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            E1CompletionAlignedRefinementError,
            "inside the full horizon",
        ):
            build_e1_completion_aligned_refinement_plans(
                (_sequence(),),
                horizon_start_tick=0,
                horizon_end_tick=12,
                ticks_per_second=8.0,
            )

    def test_planner_has_no_field_execution_and_remains_private(self) -> None:
        source = inspect.getsource(build_e1_completion_aligned_refinement_plans)
        for forbidden in (
            "run_e1_asynchronous_field",
            "advance_e1_local_edge_plasticity",
            "produce_e1_a0_av_histories",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1CompletionAlignedRefinementPlan",
            "build_e1_completion_aligned_refinement_plans",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
