from __future__ import annotations

from dataclasses import replace

import pytest

from mcm_field_organism.visual_mcm_effector_sequence import (
    VisualMCMEffectorSequenceError,
    prepare_visual_mcm_effector_sequence,
    visual_mcm_effector_sequence_public_roles,
)
from mcm_field_organism import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    build_shared_mcm_field,
    project_visual_mcm_effector_surface,
    receptor_projection_baseline,
)
from tests.test_visual_mcm_effector_surface import OFFSETS, POSITIONS


def frames(*windows_and_values: tuple[int, int, float]):
    anatomy = ReceptorDockAnatomy(
        modality_id="controlled",
        dock_id="dock.controlled",
        positions=POSITIONS,
    )
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(anatomy.dock_id, anatomy.modality_id, "controlled.receptor.v1")
    )
    reference = ReceptorContactFrame(
        modality_id=anatomy.modality_id,
        geometry_id="controlled.receptor.v1",
        snapshot_id="controlled.reference",
        clock_id="controlled.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=tuple(
            f"controlled.carrier.{index}" for index in range(len(POSITIONS))
        ),
        values=(0.0,) * len(POSITIONS),
    )
    field = build_shared_mcm_field(
        (reference,),
        {anatomy.modality_id: anatomy},
        sample_offsets=OFFSETS,
    )
    result = []
    for index, (start, end, value) in enumerate(windows_and_values):
        contact = replace(
            reference,
            snapshot_id=f"controlled.snapshot.{index}",
            window_start_tick=start,
            window_end_tick=end,
            values=(value,) * len(POSITIONS),
        )
        distribution = distributor.distribute(
            (contact,),
            CommonFieldTime("organism.test", start, end),
        )
        field = field.advance(distribution, receptor_projection_baseline)
        result.append(project_visual_mcm_effector_surface(field.snapshot()))
    return tuple(result)


def test_fixed_sequence_preserves_every_completed_frame_in_time_order() -> None:
    sequence_frames = frames((0, 10, -0.5), (10, 20, 0.0), (20, 30, 0.5))

    plan = prepare_visual_mcm_effector_sequence(sequence_frames, frame_duration_ms=200)

    assert plan.frame_digests == tuple(item.digest() for item in sequence_frames)
    assert plan.source_ticks == (1, 2, 3)
    assert plan.source_windows == ((0, 10), (10, 20), (20, 30))
    assert plan.total_duration_ms == 600
    assert not plan.writes_back
    assert not plan.camera_connected
    assert not plan.adaptive_timing
    assert not plan.content_selection
    assert not plan.stateful


def test_same_inputs_are_bitwise_reproducible() -> None:
    sequence_frames = frames((0, 10, -1.0), (10, 20, 1.0))

    first = prepare_visual_mcm_effector_sequence(sequence_frames, frame_duration_ms=250)
    second = prepare_visual_mcm_effector_sequence(sequence_frames, frame_duration_ms=250)

    assert first == second
    assert first.digest() == second.digest()


@pytest.mark.parametrize(
    "sequence_frames",
    [
        lambda: (
            lambda items: (items[0], replace(items[1], source_tick=items[0].source_tick))
        )(frames((0, 10, 0.0), (10, 20, 0.0))),
        lambda: (
            lambda items: (
                items[0],
                replace(items[1], source_window_start_tick=5),
            )
        )(frames((0, 10, 0.0), (10, 20, 0.0))),
    ],
)
def test_non_monotone_or_overlapping_field_time_is_rejected(sequence_frames) -> None:
    with pytest.raises(VisualMCMEffectorSequenceError):
        prepare_visual_mcm_effector_sequence(sequence_frames(), frame_duration_ms=200)


def test_rate_count_and_total_duration_are_bounded() -> None:
    valid = frames((0, 10, 0.0))
    with pytest.raises(VisualMCMEffectorSequenceError):
        prepare_visual_mcm_effector_sequence(valid, frame_duration_ms=99)
    too_many = frames(
        *((index * 10, (index + 1) * 10, 0.0) for index in range(11))
    )
    with pytest.raises(VisualMCMEffectorSequenceError):
        prepare_visual_mcm_effector_sequence(too_many, frame_duration_ms=100)
    ten = too_many[:10]
    with pytest.raises(VisualMCMEffectorSequenceError):
        prepare_visual_mcm_effector_sequence(ten, frame_duration_ms=3_001)


def test_runtime_extensions_and_semantic_roles_are_absent() -> None:
    plan = prepare_visual_mcm_effector_sequence(
        frames((0, 10, 0.0)),
        frame_duration_ms=200,
    )
    for role in (
        "writes_back",
        "camera_connected",
        "adaptive_timing",
        "content_selection",
        "stateful",
    ):
        with pytest.raises(VisualMCMEffectorSequenceError):
            replace(plan, **{role: True})

    roles = set(visual_mcm_effector_sequence_public_roles())
    assert roles.isdisjoint(
        {"action", "winner", "reward", "target", "meaning", "memory", "label"}
    )
