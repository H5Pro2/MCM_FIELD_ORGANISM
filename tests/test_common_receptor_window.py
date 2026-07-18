from __future__ import annotations

from dataclasses import fields
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    CommonReceptorWindowError,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorTimeSequence,
    audit_receptor_window_assignment,
    build_common_receptor_windows,
    common_receptor_window_public_roles,
)


def sequence(modality: str, intervals: tuple[tuple[int, int], ...], *, clock_id="organism.test"):
    frames = []
    for index, (start, end) in enumerate(intervals):
        frame = ReceptorContactFrame(
            modality_id=modality,
            geometry_id=f"{modality}.geometry.v1",
            snapshot_id=f"{modality}.receptor.{index}",
            clock_id=f"{modality}.source",
            window_start_tick=index,
            window_end_tick=index + 1,
            carrier_ids=(f"{modality}.carrier.0",),
            values=(0.25,),
        )
        frames.append(
            OrganismTimedReceptorFrame(
                frame,
                CommonFieldTime(clock_id, start, end),
            )
        )
    return ReceptorTimeSequence(
        modality,
        f"{modality}.geometry.v1",
        clock_id,
        tuple(frames),
    )


class CommonReceptorWindowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schedule = build_common_receptor_windows(
            anchor_tick=100,
            window_width_ticks=10,
            window_count=2,
            clock_id="organism.test",
        )

    def test_exactly_one_native_state_per_modality_is_explicit(self) -> None:
        audit = audit_receptor_window_assignment(
            (
                sequence("auditory", ((101, 105), (111, 115))),
                sequence("visual", ((105, 109), (115, 119))),
            ),
            self.schedule,
        )
        self.assertEqual((0, 1), audit.exact_window_indices)
        self.assertTrue(audit.every_window_has_exactly_one_state_per_modality)
        self.assertEqual(4, len(audit.assignments))

    def test_multiple_and_missing_states_are_counts_not_selected_pairs(self) -> None:
        audit = audit_receptor_window_assignment(
            (
                sequence("auditory", ((101, 104), (105, 109), (111, 115))),
                sequence("visual", ((101, 109), (121, 125))),
            ),
            self.schedule,
        )
        self.assertEqual(2, audit.occupancies[0].count_for("auditory"))
        self.assertEqual(1, audit.occupancies[0].count_for("visual"))
        self.assertEqual(1, audit.occupancies[1].count_for("auditory"))
        self.assertEqual(0, audit.occupancies[1].count_for("visual"))
        self.assertEqual((), audit.exact_window_indices)
        self.assertEqual(("visual.receptor.1",), audit.outside_snapshot_ids)

    def test_boundary_crossing_read_is_not_assigned(self) -> None:
        audit = audit_receptor_window_assignment(
            (
                sequence("auditory", ((108, 112),)),
                sequence("visual", ((101, 109),)),
            ),
            self.schedule,
        )
        self.assertEqual(("auditory.receptor.0",), audit.crossing_snapshot_ids)
        self.assertEqual(1, len(audit.assignments))

    def test_sequence_declaration_order_does_not_change_audit(self) -> None:
        auditory = sequence("auditory", ((101, 105), (111, 115)))
        visual = sequence("visual", ((105, 109), (115, 119)))
        self.assertEqual(
            audit_receptor_window_assignment((auditory, visual), self.schedule),
            audit_receptor_window_assignment((visual, auditory), self.schedule),
        )

    def test_clock_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(CommonReceptorWindowError, "one organism clock"):
            audit_receptor_window_assignment(
                (sequence("auditory", ((101, 105),), clock_id="other.clock"),),
                self.schedule,
            )

    def test_invalid_schedule_values_are_rejected(self) -> None:
        for kwargs in (
            {"anchor_tick": 0, "window_width_ticks": 10, "window_count": 1},
            {"anchor_tick": 1, "window_width_ticks": 0, "window_count": 1},
            {"anchor_tick": 1, "window_width_ticks": 10, "window_count": 0},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(CommonReceptorWindowError):
                    build_common_receptor_windows(**kwargs)

    def test_public_roles_contain_no_reduction_or_selection_state(self) -> None:
        roles = set(common_receptor_window_public_roles())
        forbidden = {
            "raw_audio",
            "raw_video",
            "samples",
            "image",
            "selected_pair",
            "mean_value",
            "interpolation",
            "held_value",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
