from __future__ import annotations

from dataclasses import replace

import pytest

from mcm_field_organism.visual_mcm_effector_sequence import (
    prepare_visual_mcm_effector_sequence,
)
from mcm_field_organism.visual_mcm_effector_sequence_presenter import (
    NEUTRAL_GRAY16,
    VisualMCMEffectorSequencePresentationError,
    prepare_visual_mcm_effector_sequence_presentation,
    present_visual_mcm_effector_sequence_plan,
    visual_mcm_effector_sequence_presentation_public_roles,
)
from tests.test_visual_mcm_effector_sequence import frames


class RecordingBackend:
    def __init__(self, *, stop_after_wait: int | None = None, fail_render: int | None = None):
        self.stop_after_wait = stop_after_wait
        self.fail_render = fail_render
        self.renders = []
        self.waits = []
        self.closed = False

    def render(self, raster, cell_pixels):
        render_number = len(self.renders) + 1
        if render_number == self.fail_render:
            self.fail_render = None
            raise RuntimeError("controlled output failure")
        self.renders.append((raster, cell_pixels))

    def wait(self, duration_ms):
        self.waits.append(duration_ms)
        return self.stop_after_wait == len(self.waits)

    def close(self):
        self.closed = True


def prepared(values=(-0.5, 0.0, 0.5), *, frame_duration_ms=200):
    source_frames = frames(
        *((index * 10, (index + 1) * 10, value) for index, value in enumerate(values))
    )
    sequence = prepare_visual_mcm_effector_sequence(
        source_frames,
        frame_duration_ms=frame_duration_ms,
    )
    plan = prepare_visual_mcm_effector_sequence_presentation(
        sequence,
        source_frames,
        cell_pixels=8,
    )
    return source_frames, sequence, plan


def test_preparation_preserves_sequence_order_and_fixed_timing() -> None:
    source_frames, sequence, plan = prepared()

    assert plan.source_sequence_digest == sequence.digest()
    assert plan.source_frame_digests == tuple(frame.digest() for frame in source_frames)
    assert plan.frame_duration_ms == 200
    assert plan.neutral_duration_ms == 100
    assert plan.total_runtime_ms == 700
    assert len(plan.gray16_rasters) == 3
    assert all(
        value == NEUTRAL_GRAY16
        for row in plan.neutral_gray16_raster
        for value in row
    )


def test_changed_or_reordered_frames_are_rejected() -> None:
    source_frames, sequence, _plan = prepared()

    with pytest.raises(VisualMCMEffectorSequencePresentationError):
        prepare_visual_mcm_effector_sequence_presentation(
            sequence,
            tuple(reversed(source_frames)),
        )
    with pytest.raises(VisualMCMEffectorSequencePresentationError):
        prepare_visual_mcm_effector_sequence_presentation(
            sequence,
            source_frames[:-1],
        )


def test_neutral_output_is_included_in_hard_runtime_boundary() -> None:
    source_frames = frames(*((index, index + 1, 0.0) for index in range(10)))
    sequence = prepare_visual_mcm_effector_sequence(
        source_frames,
        frame_duration_ms=3_000,
    )

    with pytest.raises(VisualMCMEffectorSequencePresentationError):
        prepare_visual_mcm_effector_sequence_presentation(sequence, source_frames)


def test_completed_sequence_uses_fixed_waits_then_neutral_output() -> None:
    _frames, _sequence, plan = prepared()
    backend = RecordingBackend()

    observation = present_visual_mcm_effector_sequence_plan(plan, _backend=backend)

    assert [item[0] for item in backend.renders[:-1]] == list(plan.gray16_rasters)
    assert backend.renders[-1][0] == plan.neutral_gray16_raster
    assert backend.waits == [200, 200, 200, 100]
    assert backend.closed
    assert observation.frames_presented == 3
    assert observation.termination == "completed"
    assert observation.neutral_output_applied


def test_manual_stop_neutralizes_without_presenting_later_frames() -> None:
    _frames, _sequence, plan = prepared()
    backend = RecordingBackend(stop_after_wait=1)

    observation = present_visual_mcm_effector_sequence_plan(plan, _backend=backend)

    assert backend.renders == [
        (plan.gray16_rasters[0], plan.cell_pixels),
        (plan.neutral_gray16_raster, plan.cell_pixels),
    ]
    assert backend.waits == [200, 100]
    assert backend.closed
    assert observation.frames_presented == 1
    assert observation.termination == "manual_stop"


def test_output_error_attempts_neutral_output_and_closes_backend() -> None:
    _frames, _sequence, plan = prepared()
    backend = RecordingBackend(fail_render=2)

    with pytest.raises(RuntimeError, match="controlled output failure"):
        present_visual_mcm_effector_sequence_plan(plan, _backend=backend)

    assert backend.renders[-1][0] == plan.neutral_gray16_raster
    assert backend.waits == [200, 100]
    assert backend.closed


def test_adaptive_stateful_and_semantic_roles_are_absent() -> None:
    _frames, _sequence, plan = prepared()
    for role in (
        "writes_back",
        "camera_connected",
        "adaptive_timing",
        "content_selection",
        "stateful",
        "random_source",
    ):
        with pytest.raises(VisualMCMEffectorSequencePresentationError):
            replace(plan, **{role: True})

    roles = set(visual_mcm_effector_sequence_presentation_public_roles())
    assert roles.isdisjoint(
        {"action", "winner", "reward", "target", "meaning", "memory", "label"}
    )
