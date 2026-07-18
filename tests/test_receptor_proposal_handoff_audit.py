from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorProposalHandoffError,
    ReceptorTimeSequence,
    handoff_receptor_completion_groups,
    receptor_proposal_handoff_audit_public_roles,
    run_receptor_proposal_handoff_audit,
)
from mcm_field_organism.receptor_proposal_handoff_audit import (
    _sequence,
    _steps,
)


class ReceptorProposalHandoffAuditTests(unittest.TestCase):
    def test_coarse_and_fine_segmentations_preserve_every_dock_sequence(self) -> None:
        result = run_receptor_proposal_handoff_audit()
        self.assertTrue(result.coarse_preserves_dock_order)
        self.assertTrue(result.fine_preserves_dock_order)
        self.assertTrue(result.coarse_preserves_reduced_frames)
        self.assertTrue(result.fine_preserves_reduced_frames)
        self.assertTrue(result.segmentations_reconstruct_same_dock_sequences)
        self.assertTrue(result.coarse.every_in_horizon_event_assigned_once)
        self.assertTrue(result.fine.every_in_horizon_event_assigned_once)

    def test_equal_completion_times_remain_one_unordered_group(self) -> None:
        result = handoff_receptor_completion_groups(
            (
                _sequence("auditory", (2,)),
                _sequence("visual", (2,)),
            ),
            _steps((0, 4)),
        )
        self.assertEqual(1, len(result.batches[0].completion_groups))
        self.assertEqual(
            ("auditory", "visual"),
            result.batches[0].completion_groups[0].modality_ids,
        )
        self.assertEqual(
            (0.25, 0.25),
            tuple(
                item.frame.values[0]
                for item in result.batches[0].completion_groups[0].timed_frames
            ),
        )

    def test_boundary_event_belongs_once_to_the_ending_span(self) -> None:
        result = handoff_receptor_completion_groups(
            (_sequence("auditory", (3, 6)),),
            _steps((0, 3, 6)),
        )
        self.assertEqual((1, 1), tuple(batch.event_count for batch in result.batches))
        self.assertTrue(result.every_in_horizon_event_assigned_once)

    def test_read_crossing_a_boundary_is_handed_off_at_completion(self) -> None:
        frame = ReceptorContactFrame(
            modality_id="visual",
            geometry_id="visual.geometry.v1",
            snapshot_id="visual.receptor.crossing",
            clock_id="visual.source",
            window_start_tick=0,
            window_end_tick=1,
            carrier_ids=("visual.carrier.0",),
            values=(0.75,),
        )
        sequence = ReceptorTimeSequence(
            "visual",
            "visual.geometry.v1",
            "organism.test",
            (
                OrganismTimedReceptorFrame(
                    frame,
                    CommonFieldTime("organism.test", 2, 4),
                ),
            ),
        )
        result = handoff_receptor_completion_groups(
            (sequence,),
            _steps((0, 3, 6)),
        )
        self.assertEqual(
            (0, 1),
            tuple(batch.event_count for batch in result.batches),
        )
        self.assertEqual((frame,), result.frames_for("visual"))

    def test_sequence_declaration_order_does_not_change_handoff(self) -> None:
        auditory = _sequence("auditory", (1, 3, 5))
        visual = _sequence("visual", (2, 4, 6))
        steps = _steps((0, 3, 6))
        self.assertEqual(
            handoff_receptor_completion_groups((auditory, visual), steps),
            handoff_receptor_completion_groups((visual, auditory), steps),
        )

    def test_empty_modality_count_remains_explicit(self) -> None:
        result = handoff_receptor_completion_groups(
            (
                _sequence("auditory", (1, 2)),
                _sequence("visual", (4,)),
            ),
            _steps((0, 3, 6)),
        )
        self.assertEqual(
            (("auditory", 2), ("visual", 0)),
            result.batches[0].modality_event_counts,
        )
        self.assertEqual(
            (("auditory", 0), ("visual", 1)),
            result.batches[1].modality_event_counts,
        )

    def test_events_outside_the_horizon_remain_explicit(self) -> None:
        result = handoff_receptor_completion_groups(
            (_sequence("auditory", (1, 3, 7)),),
            _steps((1, 4, 6)),
        )
        self.assertEqual(
            ("auditory.receptor.0",),
            result.completed_before_or_at_start_snapshot_ids,
        )
        self.assertEqual(
            ("auditory.receptor.2",),
            result.completed_after_horizon_snapshot_ids,
        )
        self.assertEqual(1, result.assigned_event_count)

    def test_noncontiguous_or_clock_mismatched_steps_are_rejected(self) -> None:
        sequence = (_sequence("auditory", (2,)),)
        with self.assertRaisesRegex(ReceptorProposalHandoffError, "contiguous"):
            handoff_receptor_completion_groups(
                sequence,
                (
                    MCMFieldStepTime("organism.test", 0, 1, 10.0),
                    MCMFieldStepTime("organism.test", 2, 3, 10.0),
                ),
            )
        with self.assertRaisesRegex(ReceptorProposalHandoffError, "clock"):
            handoff_receptor_completion_groups(
                sequence,
                (MCMFieldStepTime("other.clock", 0, 3, 10.0),),
            )

    def test_public_roles_add_no_selection_reduction_hold_or_field_state(self) -> None:
        forbidden = {
            "selected_event",
            "latest_contact",
            "held_contact",
            "mean_contact",
            "fused_contact",
            "activation",
            "afterimage",
            "memory",
            "topology",
            "weight",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                receptor_proposal_handoff_audit_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
