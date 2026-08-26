from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_memory_function_gap_audit import (
    audit_e1_memory_function_gaps,
)
from mcm_field_organism.e1_repetition_formation_contract import (
    build_e1_repetition_formation_contract,
)
from mcm_field_organism.e1_repetition_formation_planner import (
    build_e1_repetition_formation_plans,
)
from tests.test_e1_confirmation_typed_prepared_inputs import UPSTREAM


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = ROOT / "synthetic_runs" / "s1ec19_full_published_once_v1"
REPORT = (
    ROOT
    / "synthetic_runs"
    / "s1ec23_full_published_probe_once_v1"
    / "e1_full_published_probe_s1ec23_once_v1.json"
)


class E1RepetitionFormationPlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(
            descriptor, SOURCE_DIRECTORY
        )
        cls.bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        gap = audit_e1_memory_function_gaps(REPORT)
        cls.contract = build_e1_repetition_formation_contract(gap, cls.bundle)
        cls.result = build_e1_repetition_formation_plans(
            cls.contract, cls.bundle
        )

    def test_all_contact_pairs_are_exposure_matched(self) -> None:
        for pair in self.result.pairs:
            self.assertTrue(pair.source_payloads_value_identical)
            self.assertTrue(pair.total_exposure_identical)
            self.assertTrue(pair.horizon_identical)
            self.assertTrue(pair.all_supports_assigned_once)
            self.assertEqual(
                pair.repeated_plans.source_event_count,
                pair.continuous_plans.source_event_count,
            )

    def test_n2_separates_only_organism_time(self) -> None:
        pair = self.result.pairs[1]
        repeated = pair.repeated_sequences[0].frames
        continuous = pair.continuous_sequences[0].frames
        episode_frames = len(repeated) // 2

        self.assertEqual(
            2_000_000,
            repeated[episode_frames].field_time.window_start_tick,
        )
        self.assertEqual(1_000_000, continuous[0].field_time.window_start_tick)
        self.assertEqual(
            2_000_000,
            continuous[episode_frames].field_time.window_start_tick,
        )
        self.assertEqual(
            repeated[episode_frames].frame.values,
            continuous[episode_frames].frame.values,
        )
        self.assertNotEqual(
            repeated[0].frame.window_start_tick,
            repeated[episode_frames].frame.window_start_tick,
        )
        self.assertEqual(
            2_000_000,
            repeated[episode_frames].frame.window_start_tick
            - repeated[0].frame.window_start_tick,
        )
        self.assertEqual(((1_000_000, 2_000_000),), pair.neutral_gap_intervals)

    def test_r2_r4_r8_handoffs_assign_every_support_once(self) -> None:
        for pair in self.result.pairs:
            for plan_set in (pair.repeated_plans, pair.continuous_plans):
                self.assertEqual(
                    ("r2", "r4", "r8"),
                    tuple(item.refinement_id for item in plan_set.plans),
                )
                self.assertTrue(all(
                    item.handoff.every_in_horizon_event_assigned_once
                    for item in plan_set.plans
                ))
            self.assertEqual(
                pair.repeated_plans.completion_ticks[-1],
                pair.continuous_plans.completion_ticks[-1],
            )
            self.assertEqual(
                tuple(len(item.proposal_steps) for item in pair.repeated_plans.plans),
                tuple(len(item.proposal_steps) for item in pair.continuous_plans.plans),
            )

    def test_one_contact_sources_differ_only_by_technical_identity(self) -> None:
        pair = self.result.pairs[0]
        repeated = pair.repeated_sequences
        continuous = pair.continuous_sequences

        for left_sequence, right_sequence in zip(
            repeated, continuous, strict=True
        ):
            for left, right in zip(
                left_sequence.frames, right_sequence.frames, strict=True
            ):
                self.assertEqual(left.field_time, right.field_time)
                self.assertEqual(left.frame.values, right.frame.values)
                self.assertEqual(left.frame.carrier_ids, right.frame.carrier_ids)
                self.assertNotEqual(left.frame.snapshot_id, right.frame.snapshot_id)

    def test_planner_has_no_e1_or_field_execution(self) -> None:
        source = inspect.getsource(build_e1_repetition_formation_plans)
        for forbidden in (
            "advance_e1",
            "advance_transient",
            "execute_",
            "run_full",
            "write_text",
            "write_bytes",
            "_atomic_publish",
        ):
            self.assertNotIn(forbidden, source)
        self.assertFalse(self.result.field_execution_performed)
        self.assertFalse(self.result.e1_state_constructed)

    def test_protected_report_remains_unchanged(self) -> None:
        before = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        build_e1_repetition_formation_plans(self.contract, self.bundle)
        after = hashlib.sha256(REPORT.read_bytes()).hexdigest()

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
