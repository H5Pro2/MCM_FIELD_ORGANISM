from __future__ import annotations

import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_refinement_planner import (
    E1ConfirmationRefinementPlannerError,
    build_e1_confirmation_refinement_plans,
)
from mcm_field_organism.e1_refined_confirmation_contract import (
    build_e1_refined_confirmation_contract,
)
from tests.test_e1_completion_aligned_refinement import _sequence


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"


def _contract():
    return build_e1_refined_confirmation_contract(REPORTS, UPSTREAM)


def _plans():
    return build_e1_confirmation_refinement_plans(
        _contract(),
        (_sequence(),),
        horizon_start_tick=0,
        horizon_end_tick=16,
        ticks_per_second=8.0,
    )


class E1ConfirmationRefinementPlannerTests(unittest.TestCase):
    def test_r2_r4_r8_split_only_completion_intervals(self) -> None:
        result = _plans()

        self.assertEqual(("r2", "r4", "r8"), tuple(
            item.refinement_id for item in result.plans
        ))
        self.assertEqual((4, 8, 16), tuple(
            len(item.proposal_steps) for item in result.plans
        ))
        self.assertEqual((8, 16), result.completion_ticks)

    def test_supports_remain_once_at_original_completion(self) -> None:
        result = _plans()

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

    def test_contact_evidence_and_integrals_are_exactly_invariant(self) -> None:
        result = _plans()
        evidence = tuple(
            (
                item.source_contact_digest,
                item.source_signed_integral,
                item.source_absolute_integral,
                item.source_quadratic_integral,
                item.handoff_digest,
            )
            for item in result.plans
        )

        self.assertEqual(1, len(set(evidence)))
        self.assertEqual((-0.25, 0.75, 0.3125), evidence[0][1:4])

    def test_plan_set_is_repeatable_and_r8_has_new_digest(self) -> None:
        first = _plans()
        second = _plans()

        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(3, len({item.digest() for item in first.plans}))

    def test_nondivisible_r8_interval_fails_closed(self) -> None:
        sequence = _sequence()
        from mcm_field_organism.receptor_contract import CommonFieldTime
        from mcm_field_organism.receptor_time_model import (
            OrganismTimedReceptorFrame,
            ReceptorTimeSequence,
        )
        shifted = ReceptorTimeSequence(
            sequence.modality_id,
            sequence.geometry_id,
            sequence.clock_id,
            (
                OrganismTimedReceptorFrame(
                    sequence.frames[0].frame,
                    CommonFieldTime("organism.synthetic", 0, 12),
                ),
                OrganismTimedReceptorFrame(
                    sequence.frames[1].frame,
                    CommonFieldTime("organism.synthetic", 12, 32),
                ),
            ),
        )
        with self.assertRaisesRegex(
            E1ConfirmationRefinementPlannerError,
            "not exactly divisible",
        ):
            build_e1_confirmation_refinement_plans(
                _contract(),
                (shifted,),
                horizon_start_tick=0,
                horizon_end_tick=32,
                ticks_per_second=8.0,
            )

    def test_invalid_contract_fails_before_source_planning(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationRefinementPlannerError,
            "current S1-EB contract",
        ):
            build_e1_confirmation_refinement_plans(
                None,
                (_sequence(),),
                horizon_start_tick=0,
                horizon_end_tick=16,
                ticks_per_second=8.0,
            )

    def test_planner_has_no_field_execution_and_remains_private(self) -> None:
        source = inspect.getsource(build_e1_confirmation_refinement_plans)
        for forbidden in (
            "run_e1_asynchronous_field",
            "advance_e1_local_edge_plasticity",
            "produce_e1_canonical_refined_chain_result",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1ConfirmationRefinementPlan",
            "build_e1_confirmation_refinement_plans",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
