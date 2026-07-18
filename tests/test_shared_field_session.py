from __future__ import annotations

from dataclasses import fields
import unittest

from mcm_field_organism import (
    CapturedCommonReceptorWindowAudit,
    CommonFieldTime,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    SharedFieldSessionError,
    SharedFieldSessionResult,
    SharedFieldSessionWindow,
    audit_receptor_window_assignment,
    build_common_receptor_windows,
    build_shared_mcm_field,
    receptor_projection_baseline,
    restore_shared_mcm_field,
    run_captured_shared_mcm_field_session,
    run_shared_mcm_field_session,
    session_windows_from_common_receptor_capture,
)


FIELD_SAMPLE_OFFSETS = ((-1, 0), (0, -1), (0, 1), (1, 0))


def frame(
    modality: str,
    snapshot_index: int,
    values: tuple[float, ...],
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality,
        geometry_id=f"{modality}.receptor.v1",
        snapshot_id=f"{modality}.snapshot.{snapshot_index}",
        clock_id=f"{modality}.source",
        window_start_tick=snapshot_index * 10,
        window_end_tick=(snapshot_index + 1) * 10,
        carrier_ids=tuple(
            f"{modality}.carrier.{index}" for index in range(len(values))
        ),
        values=values,
    )


def field():
    auditory = frame("auditory", 0, (0.1, 0.2))
    visual = frame("visual", 0, (0.3, 0.4, 0.5))
    anatomies = {
        "auditory": ReceptorDockAnatomy(
            "auditory",
            "dock.auditory",
            ((0, 0), (0, 1)),
        ),
        "visual": ReceptorDockAnatomy(
            "visual",
            "dock.visual",
            ((1, 0), (1, 1), (1, 2)),
        ),
    }
    return build_shared_mcm_field(
        (auditory, visual),
        anatomies,
        sample_offsets=FIELD_SAMPLE_OFFSETS,
    )


def windows() -> tuple[SharedFieldSessionWindow, ...]:
    values = (
        ((0.1, 0.2), (0.3, 0.4, 0.5)),
        ((0.2, 0.3), (0.4, 0.5, 0.6)),
        ((0.3, 0.4), (0.5, 0.6, 0.7)),
    )
    return tuple(
        SharedFieldSessionWindow(
            CommonFieldTime(
                "organism.session",
                100 + index * 10,
                110 + index * 10,
            ),
            (
                frame("auditory", index, auditory_values),
                frame("visual", index, visual_values),
            ),
        )
        for index, (auditory_values, visual_values) in enumerate(values)
    )


def captured_windows(
    *,
    auditory_intervals=((101, 105), (111, 115), (121, 125)),
    visual_intervals=((105, 109), (115, 119), (125, 129)),
) -> CapturedCommonReceptorWindowAudit:
    schedule = build_common_receptor_windows(
        anchor_tick=100,
        window_width_ticks=10,
        window_count=3,
        clock_id="organism.session",
    )
    values = {
        "auditory": ((0.1, 0.2), (0.2, 0.3), (0.3, 0.4)),
        "visual": (
            (0.3, 0.4, 0.5),
            (0.4, 0.5, 0.6),
            (0.5, 0.6, 0.7),
        ),
    }

    def sequence(modality, intervals):
        timed_frames = tuple(
            OrganismTimedReceptorFrame(
                frame(modality, index, values[modality][index]),
                CommonFieldTime("organism.session", start, end),
            )
            for index, (start, end) in enumerate(intervals)
        )
        return ReceptorTimeSequence(
            modality,
            f"{modality}.receptor.v1",
            "organism.session",
            timed_frames,
        )

    sequences = tuple(
        sorted(
            (
                sequence("auditory", auditory_intervals),
                sequence("visual", visual_intervals),
            ),
            key=lambda item: item.modality_id,
        )
    )
    return CapturedCommonReceptorWindowAudit(
        schedule,
        sequences,
        audit_receptor_window_assignment(sequences, schedule),
    )


class SharedFieldSessionTests(unittest.TestCase):
    def test_exact_common_receptor_capture_advances_the_bounded_session(self) -> None:
        capture = captured_windows()
        bridged = session_windows_from_common_receptor_capture(capture)
        result = run_captured_shared_mcm_field_session(
            field(),
            capture,
            receptor_projection_baseline,
            max_steps=3,
        )

        self.assertEqual(windows(), bridged)
        self.assertEqual(3, result.step_count)
        self.assertEqual(
            run_shared_mcm_field_session(
                field(),
                windows(),
                receptor_projection_baseline,
                max_steps=3,
            ).final_field.snapshot().digest(),
            result.final_field.snapshot().digest(),
        )

    def test_ambiguous_missing_crossing_and_outside_states_are_not_selected(self) -> None:
        captures = (
            captured_windows(
                auditory_intervals=((101, 103), (104, 106), (111, 115))
            ),
            captured_windows(visual_intervals=((105, 109), (125, 129))),
            captured_windows(auditory_intervals=((108, 112), (121, 125))),
            captured_windows(
                visual_intervals=((105, 109), (115, 119), (135, 139))
            ),
        )
        for capture in captures:
            with self.subTest(audit=capture.audit):
                with self.assertRaisesRegex(
                    SharedFieldSessionError,
                    "exactly one complete state",
                ):
                    session_windows_from_common_receptor_capture(capture)

    def test_three_windows_advance_one_unchanged_field_layer(self) -> None:
        result = run_shared_mcm_field_session(
            field(),
            windows(),
            receptor_projection_baseline,
            max_steps=3,
        )

        self.assertEqual(3, result.step_count)
        self.assertEqual((1, 2, 3), tuple(step.field_state.tick for step in result.steps))
        self.assertEqual(
            windows()[-1].frames[0].values + windows()[-1].frames[1].values,
            result.final_field.snapshot().activation,
        )
        self.assertEqual(
            1,
            len({step.field_state.neuron_ids for step in result.steps}),
        )
        self.assertEqual(
            1,
            len({step.field_state.dock_neuron_ids for step in result.steps}),
        )

    def test_receptor_declaration_order_does_not_change_the_session(self) -> None:
        reversed_windows = tuple(
            SharedFieldSessionWindow(window.field_time, tuple(reversed(window.frames)))
            for window in windows()
        )
        forward = run_shared_mcm_field_session(
            field(),
            windows(),
            receptor_projection_baseline,
            max_steps=3,
        )
        reversed_result = run_shared_mcm_field_session(
            field(),
            reversed_windows,
            receptor_projection_baseline,
            max_steps=3,
        )

        self.assertEqual(
            forward.final_field.snapshot().digest(),
            reversed_result.final_field.snapshot().digest(),
        )

    def test_snapshot_resume_matches_uninterrupted_session(self) -> None:
        full = run_shared_mcm_field_session(
            field(),
            windows(),
            receptor_projection_baseline,
            max_steps=3,
        )
        prefix = run_shared_mcm_field_session(
            field(),
            windows()[:1],
            receptor_projection_baseline,
            max_steps=1,
        )
        restored = restore_shared_mcm_field(prefix.final_field.snapshot())
        suffix = run_shared_mcm_field_session(
            restored,
            windows()[1:],
            receptor_projection_baseline,
            max_steps=2,
        )

        self.assertEqual(
            full.final_field.snapshot().digest(),
            suffix.final_field.snapshot().digest(),
        )

    def test_gap_missing_modality_and_explicit_bound_are_rejected(self) -> None:
        gap = (
            windows()[0],
            SharedFieldSessionWindow(
                CommonFieldTime("organism.session", 120, 130),
                windows()[1].frames,
            ),
        )
        with self.assertRaisesRegex(SharedFieldSessionError, "contiguous"):
            run_shared_mcm_field_session(
                field(),
                gap,
                receptor_projection_baseline,
                max_steps=2,
            )

        missing = SharedFieldSessionWindow(
            windows()[0].field_time,
            (windows()[0].frames[0],),
        )
        with self.assertRaisesRegex(SharedFieldSessionError, "every attached modality"):
            run_shared_mcm_field_session(
                field(),
                (missing,),
                receptor_projection_baseline,
                max_steps=1,
            )

        with self.assertRaisesRegex(SharedFieldSessionError, "explicit maximum"):
            run_shared_mcm_field_session(
                field(),
                windows(),
                receptor_projection_baseline,
                max_steps=2,
            )

    def test_observer_receives_completed_states_without_runtime_roles(self) -> None:
        observed = []
        result = run_shared_mcm_field_session(
            field(),
            windows(),
            receptor_projection_baseline,
            max_steps=3,
            observer=observed.append,
        )

        self.assertEqual(result.steps, tuple(observed))
        roles = {item.name for item in fields(SharedFieldSessionResult)}
        self.assertTrue(
            {
                "meaning",
                "memory",
                "reward",
                "topology",
                "selected_pattern",
                "raw_audio",
                "raw_video",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
