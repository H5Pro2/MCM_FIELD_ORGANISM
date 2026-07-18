from __future__ import annotations

import unittest

from mcm_field_organism import (
    AsynchronousReceptorEventError,
    CommonFieldTime,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorTimeSequence,
    asynchronous_receptor_event_public_roles,
    audit_asynchronous_receptor_events,
)


def sequence(
    modality: str,
    intervals: tuple[tuple[int, int], ...],
    *,
    clock_id: str = "organism.test",
) -> ReceptorTimeSequence:
    frames = tuple(
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
            CommonFieldTime(clock_id, start, end),
        )
        for index, (start, end) in enumerate(intervals)
    )
    return ReceptorTimeSequence(
        modality,
        f"{modality}.geometry.v1",
        clock_id,
        frames,
    )


class AsynchronousReceptorEventAuditTests(unittest.TestCase):
    def test_every_native_state_remains_one_completion_event(self) -> None:
        audit = audit_asynchronous_receptor_events(
            (
                sequence("auditory", ((0, 2), (2, 4), (4, 6))),
                sequence("visual", ((0, 5),)),
            )
        )
        self.assertEqual((('auditory', 3), ('visual', 1)), audit.event_counts)
        self.assertEqual(4, audit.total_event_count)
        self.assertEqual(0.75, audit.event_share("auditory"))
        self.assertEqual((2, 4, 5, 6), tuple(
            group.completion_tick for group in audit.completion_groups
        ))

    def test_equal_completion_times_form_one_unordered_mixed_group(self) -> None:
        audit = audit_asynchronous_receptor_events(
            (
                sequence("auditory", ((0, 5),)),
                sequence("visual", ((1, 5),)),
            )
        )
        self.assertEqual(1, len(audit.completion_groups))
        self.assertEqual(1, audit.mixed_completion_group_count)
        self.assertEqual(("auditory", "visual"), audit.completion_groups[0].modality_ids)

    def test_sequence_declaration_order_does_not_change_result(self) -> None:
        auditory = sequence("auditory", ((0, 2), (2, 4)))
        visual = sequence("visual", ((0, 3),))
        self.assertEqual(
            audit_asynchronous_receptor_events((auditory, visual)),
            audit_asynchronous_receptor_events((visual, auditory)),
        )

    def test_different_organism_clocks_are_rejected(self) -> None:
        with self.assertRaisesRegex(AsynchronousReceptorEventError, "one organism clock"):
            audit_asynchronous_receptor_events(
                (
                    sequence("auditory", ((0, 2),)),
                    sequence("visual", ((0, 2),), clock_id="other.clock"),
                )
            )

    def test_public_roles_hold_no_field_step_or_fusion_rule(self) -> None:
        roles = set(asynchronous_receptor_event_public_roles())
        forbidden = {
            "field_tick",
            "selected_event",
            "mean_value",
            "interpolation",
            "held_value",
            "weight",
            "priority",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
