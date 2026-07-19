from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    BroadbandHearingPath,
    CommonFieldTime,
    LocalChannelGridReceptor,
    LogSpectralConfig,
    LogSpectralReceptor,
    MCMFieldStepTime,
    NeutralFastAfterimageConfig,
    NeutralFieldSessionWindow,
    NeutralLocalFieldSubstrateConfig,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorTimeSequence,
    VisualGridConfig,
    audio_video_dock_anatomies,
    build_shared_mcm_field,
    from_visual_receptor_state,
    run_neutral_field_session,
)
from tools.run_live_field_a_stability import _late_block_metrics


TICKS_PER_SECOND = 3000.0
AUDITORY_EVENTS_PER_WINDOW = 100
VISUAL_EVENTS_PER_WINDOW = 15


def _deterministic_visual_frame(config: VisualGridConfig) -> np.ndarray:
    frame = np.empty(
        (config.source_height, config.source_width, 3),
        dtype=np.uint8,
    )
    cell_height = config.source_height // config.grid_rows
    cell_width = config.source_width // config.grid_columns
    for row in range(config.grid_rows):
        for column in range(config.grid_columns):
            frame[
                row * cell_height : (row + 1) * cell_height,
                column * cell_width : (column + 1) * cell_width,
            ] = (
                (31 + row * 23 + column * 7) % 256,
                (67 + row * 11 + column * 19) % 256,
                (101 + row * 17 + column * 13) % 256,
            )
    frame.setflags(write=False)
    return frame


def _control_windows(
    *,
    window_count: int,
    visual_config: VisualGridConfig,
) -> tuple[NeutralFieldSessionWindow, ...]:
    if (
        isinstance(window_count, bool)
        or not isinstance(window_count, int)
        or window_count < 1
    ):
        raise ValueError("window_count must be a positive integer")
    visual_state = LocalChannelGridReceptor(visual_config).analyze(
        _deterministic_visual_frame(visual_config),
        frame_index=0,
    )
    visual_reference = from_visual_receptor_state(visual_state)
    auditory_path = BroadbandHearingPath(
        LogSpectralReceptor(LogSpectralConfig())
    )
    auditory_geometry = auditory_path.geometry_id
    auditory_carriers = auditory_path.receptor.channel_ids

    windows = []
    for window_index in range(window_count):
        start = window_index * int(TICKS_PER_SECOND)
        end = (window_index + 1) * int(TICKS_PER_SECOND)
        auditory_frames = tuple(
            OrganismTimedReceptorFrame(
                ReceptorContactFrame(
                    modality_id="auditory",
                    geometry_id=auditory_geometry,
                    snapshot_id=(
                        f"auditory.control.{window_index}.{event_index}"
                    ),
                    clock_id="auditory.control",
                    window_start_tick=(
                        window_index * AUDITORY_EVENTS_PER_WINDOW + event_index
                    ),
                    window_end_tick=(
                        window_index * AUDITORY_EVENTS_PER_WINDOW
                        + event_index
                        + 1
                    ),
                    carrier_ids=auditory_carriers,
                    values=(0.0,) * len(auditory_carriers),
                ),
                CommonFieldTime(
                    "organism.deterministic",
                    start + event_index * 30,
                    start + (event_index + 1) * 30,
                ),
            )
            for event_index in range(AUDITORY_EVENTS_PER_WINDOW)
        )
        visual_frames = tuple(
            OrganismTimedReceptorFrame(
                ReceptorContactFrame(
                    modality_id="visual",
                    geometry_id=visual_reference.geometry_id,
                    snapshot_id=f"visual.control.{window_index}.{event_index}",
                    clock_id="visual.control",
                    window_start_tick=(
                        window_index * VISUAL_EVENTS_PER_WINDOW + event_index
                    ),
                    window_end_tick=(
                        window_index * VISUAL_EVENTS_PER_WINDOW
                        + event_index
                        + 1
                    ),
                    carrier_ids=visual_reference.carrier_ids,
                    values=visual_reference.values,
                ),
                CommonFieldTime(
                    "organism.deterministic",
                    start + event_index * 200,
                    start + (event_index + 1) * 200,
                ),
            )
            for event_index in range(VISUAL_EVENTS_PER_WINDOW)
        )
        windows.append(
            NeutralFieldSessionWindow(
                (
                    ReceptorTimeSequence(
                        "auditory",
                        auditory_geometry,
                        "organism.deterministic",
                        auditory_frames,
                    ),
                    ReceptorTimeSequence(
                        "visual",
                        visual_reference.geometry_id,
                        "organism.deterministic",
                        visual_frames,
                    ),
                ),
                (
                    MCMFieldStepTime(
                        "organism.deterministic",
                        start,
                        end,
                        TICKS_PER_SECOND,
                    ),
                ),
            )
        )
    return tuple(windows)


def _run_control(
    windows: tuple[NeutralFieldSessionWindow, ...],
    visual_config: VisualGridConfig,
):
    reference_frames = tuple(
        sequence.frames[0].frame
        for sequence in windows[0].receptor_sequences
    )
    field = build_shared_mcm_field(
        reference_frames,
        audio_video_dock_anatomies(
            auditory_carrier_count=len(reference_frames[0].carrier_ids),
            visual_grid_columns=visual_config.grid_columns,
            visual_grid_rows=visual_config.grid_rows,
        ),
        sample_offsets=((-1, 0), (0, -1), (0, 1), (1, 0)),
    )
    states = []
    result = run_neutral_field_session(
        field,
        windows,
        NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=NeutralFastAfterimageConfig(0.5),
        max_windows=len(windows),
        observer=lambda _index, snapshot: states.append(snapshot),
    )
    return result, tuple(states)


def _state_blocks(states, block_windows: int, role: str):
    return tuple(
        tuple(
            tuple(float(getattr(neuron, role)) for neuron in state.layer.neurons)
            for state in states[start : start + block_windows]
        )
        for start in range(0, len(states), block_windows)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run one deterministic visual receptor lage through the unchanged "
            "shared field without camera, raw retention or writeback."
        )
    )
    parser.add_argument("--block-windows", type=int, default=21)
    parser.add_argument("--late-windows", type=int, default=7)
    args = parser.parse_args()
    if args.block_windows < 1:
        parser.error("block-windows must be positive")
    if args.late_windows < 1 or args.late_windows > args.block_windows:
        parser.error("late-windows must fit one block")

    visual_config = VisualGridConfig()
    window_count = 3 * args.block_windows
    windows = _control_windows(
        window_count=window_count,
        visual_config=visual_config,
    )
    first, first_states = _run_control(windows, visual_config)
    second, second_states = _run_control(windows, visual_config)
    digest_matches = tuple(
        left.digest() == right.digest()
        for left, right in zip(first_states, second_states, strict=True)
    )
    visual_profiles = tuple(
        window.receptor_sequences[1].frames[0].frame.values
        for window in windows
    )
    visual_reference = visual_profiles[0]
    payload = {
        "window_count": first.window_count,
        "source_support_count": first.source_support_count,
        "activation": _late_block_metrics(
            _state_blocks(first_states, args.block_windows, "activation"),
            late_window_count=args.late_windows,
        ),
        "afterimage": _late_block_metrics(
            _state_blocks(first_states, args.block_windows, "afterimage"),
            late_window_count=args.late_windows,
        ),
        "visual_receptor": {
            "carrier_count": len(visual_reference),
            "repeat_max_error": max(
                abs(value - reference)
                for profile in visual_profiles
                for value, reference in zip(
                    profile,
                    visual_reference,
                    strict=True,
                )
            ),
        },
        "exact_repeat": {
            "matching_digest_count": sum(digest_matches),
            "final_digest_matches": (
                first.field.snapshot().digest()
                == second.field.snapshot().digest()
            ),
        },
        "raw_sensor_payload_retained": False,
        "writes_back": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
