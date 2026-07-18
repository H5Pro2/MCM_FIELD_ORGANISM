from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    FieldTimePartitionError,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorTimeSequence,
    field_time_partition_public_roles,
    partition_receptor_completion_time,
)


def sequence(
    modality: str,
    intervals: tuple[tuple[int, int], ...],
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality,
        f"{modality}.geometry.v1",
        "organism.test",
        tuple(
            OrganismTimedReceptorFrame(
                ReceptorContactFrame(
                    modality_id=modality,
                    geometry_id=f"{modality}.geometry.v1",
                    snapshot_id=f"{modality}.receptor.{index}",
                    clock_id=f"{modality}.source",
                    window_start_tick=index,
                    window_end_tick=index + 1,
                    carrier_ids=(f"{modality}.carrier.0",),
                    values=(0.25,),
                ),
                CommonFieldTime("organism.test", start, end),
            )
            for index, (start, end) in enumerate(intervals)
        ),
    )


class FieldTimePartitionTests(unittest.TestCase):
    def test_completion_boundaries_form_one_gapless_horizon(self) -> None:
        result = partition_receptor_completion_time(
            (
                sequence("auditory", ((0, 2), (2, 4), (4, 6))),
                sequence("visual", ((0, 5),)),
            ),
            horizon_start_tick=0,
            horizon_end_tick=8,
            ticks_per_second=10.0,
        )
        self.assertEqual(
            ((0, 2), (2, 4), (4, 5), (5, 6), (6, 8)),
            tuple(
                (item.step_time.start_tick, item.step_time.end_tick)
                for item in result.slices
            ),
        )
        self.assertEqual(8, result.covered_ticks)
        self.assertEqual(4, result.eventful_slice_count)
        self.assertEqual(1, result.empty_slice_count)

    def test_equal_completion_events_share_the_same_boundary(self) -> None:
        result = partition_receptor_completion_time(
            (
                sequence("auditory", ((0, 5),)),
                sequence("visual", ((1, 5),)),
            ),
            horizon_start_tick=0,
            horizon_end_tick=6,
            ticks_per_second=10.0,
        )
        self.assertEqual(2, len(result.slices[0].completion_events))
        self.assertEqual(
            ("auditory", "visual"),
            tuple(
                event.modality_id
                for event in result.slices[0].completion_events
            ),
        )

    def test_events_outside_the_horizon_remain_explicit(self) -> None:
        result = partition_receptor_completion_time(
            (sequence("auditory", ((0, 2), (2, 5), (5, 9))),),
            horizon_start_tick=2,
            horizon_end_tick=7,
            ticks_per_second=10.0,
        )
        self.assertEqual(
            ("auditory.receptor.0",),
            result.completed_before_or_at_start_snapshot_ids,
        )
        self.assertEqual(
            ("auditory.receptor.2",),
            result.completed_after_horizon_snapshot_ids,
        )

    def test_sequence_declaration_order_does_not_change_partition(self) -> None:
        auditory = sequence("auditory", ((0, 2), (2, 4)))
        visual = sequence("visual", ((0, 3),))
        kwargs = {
            "horizon_start_tick": 0,
            "horizon_end_tick": 5,
            "ticks_per_second": 10.0,
        }
        self.assertEqual(
            partition_receptor_completion_time((auditory, visual), **kwargs),
            partition_receptor_completion_time((visual, auditory), **kwargs),
        )

    def test_invalid_horizon_is_rejected(self) -> None:
        with self.assertRaisesRegex(FieldTimePartitionError, "horizon"):
            partition_receptor_completion_time(
                (sequence("auditory", ((0, 2),)),),
                horizon_start_tick=2,
                horizon_end_tick=2,
                ticks_per_second=10.0,
            )

    def test_public_roles_have_no_hold_selection_or_field_state(self) -> None:
        roles = set(field_time_partition_public_roles())
        forbidden = {
            "held_contact",
            "selected_event",
            "interpolation",
            "activation",
            "afterimage",
            "field_state",
            "priority",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
