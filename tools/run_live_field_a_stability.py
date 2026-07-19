from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    capture_live_audio_video_neutral_session,
)


def audio_device(value: str) -> int | str:
    stripped = value.strip()
    if not stripped:
        raise argparse.ArgumentTypeError("audio device cannot be empty")
    try:
        return int(stripped)
    except ValueError:
        return stripped


def _mean_profile(profiles: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    if not profiles or not profiles[0]:
        raise ValueError("profile collection cannot be empty")
    width = len(profiles[0])
    if any(len(profile) != width for profile in profiles):
        raise ValueError("profiles must share one field width")
    return tuple(
        sum(profile[index] for profile in profiles) / len(profiles)
        for index in range(width)
    )


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if not left or len(left) != len(right):
        raise ValueError("field profiles must be non-empty and equally sized")
    return sum(
        abs(first - second)
        for first, second in zip(left, right, strict=True)
    ) / len(left)


def _late_block_metrics(
    blocks: tuple[tuple[tuple[float, ...], ...], ...],
    *,
    late_window_count: int,
) -> dict[str, object]:
    if len(blocks) != 3:
        raise ValueError("A stability requires exactly three blocks")
    if (
        isinstance(late_window_count, bool)
        or not isinstance(late_window_count, int)
        or late_window_count < 1
        or any(len(block) < late_window_count for block in blocks)
    ):
        raise ValueError("late window count must fit every A block")
    late_blocks = tuple(block[-late_window_count:] for block in blocks)
    means = tuple(_mean_profile(block) for block in late_blocks)
    internal = tuple(
        sum(_mean_l1(profile, mean) for profile in block) / len(block)
        for block, mean in zip(late_blocks, means, strict=True)
    )
    return {
        "late_window_count": late_window_count,
        "internal_l1": internal,
        "block_2_vs_block_1_l1": _mean_l1(means[1], means[0]),
        "block_3_vs_block_1_l1": _mean_l1(means[2], means[0]),
        "block_3_vs_block_2_l1": _mean_l1(means[2], means[1]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Observe three bounded blocks of one externally held live A world "
            "without retaining sensor payload or writing into the field."
        )
    )
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--block-windows", type=int, default=21)
    parser.add_argument("--late-windows", type=int, default=7)
    parser.add_argument("--camera-startup-frames", type=int, default=30)
    args = parser.parse_args()
    if args.block_windows < 1:
        parser.error("block-windows must be positive")
    if args.late_windows < 1 or args.late_windows > args.block_windows:
        parser.error("late-windows must fit one block")

    observations = []
    field_states = []
    receptor_profiles = []
    window_count = 3 * args.block_windows
    result = capture_live_audio_video_neutral_session(
        camera_device=args.camera_device,
        audio_device=args.audio_device,
        field_config=NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=NeutralFastAfterimageConfig(0.5),
        window_seconds=1.0,
        window_count=window_count,
        max_windows=window_count,
        camera_startup_frames=args.camera_startup_frames,
        window_observer=observations.append,
        field_state_observer=field_states.append,
        receptor_profile_observer=receptor_profiles.append,
    )

    state_blocks = tuple(
        tuple(
            field_states[index].layer.neurons
            for index in range(start, start + args.block_windows)
        )
        for start in range(0, window_count, args.block_windows)
    )
    activation_blocks = tuple(
        tuple(
            tuple(float(neuron.activation) for neuron in neurons)
            for neurons in block
        )
        for block in state_blocks
    )
    afterimage_blocks = tuple(
        tuple(
            tuple(float(neuron.afterimage) for neuron in neurons)
            for neurons in block
        )
        for block in state_blocks
    )
    receptor_metrics = {}
    for modality_id in ("auditory", "visual"):
        modality_profiles = tuple(
            item
            for item in receptor_profiles
            if item.modality_id == modality_id
        )
        if len(modality_profiles) != window_count:
            raise RuntimeError(
                f"{modality_id} must provide one reduced profile per window"
            )
        carrier_ids = modality_profiles[0].carrier_ids
        if any(item.carrier_ids != carrier_ids for item in modality_profiles):
            raise RuntimeError(
                f"{modality_id} carrier identities changed during A stability"
            )
        blocks = tuple(
            tuple(
                modality_profiles[index].mean_values
                for index in range(start, start + args.block_windows)
            )
            for start in range(0, window_count, args.block_windows)
        )
        receptor_metrics[modality_id] = {
            "carrier_count": len(carrier_ids),
            "frame_count": sum(item.frame_count for item in modality_profiles),
            "reduced_profile": _late_block_metrics(
                blocks,
                late_window_count=args.late_windows,
            ),
        }
    payload = {
        "window_count": result.field_session.window_count,
        "source_support_count": result.field_session.source_support_count,
        "camera_frame_count": result.camera_capture_frame_count,
        "audio_overflow_count": result.audio_overflow_count,
        "checkpoint_count": result.checkpoint_count,
        "activation": _late_block_metrics(
            activation_blocks,
            late_window_count=args.late_windows,
        ),
        "afterimage": _late_block_metrics(
            afterimage_blocks,
            late_window_count=args.late_windows,
        ),
        "receptors": receptor_metrics,
        "exact_baseline": {
            "activation_max_error": max(
                item.exact_baseline_activation_max_error
                for item in observations
            ),
            "afterimage_max_error": max(
                item.exact_baseline_afterimage_max_error
                for item in observations
            ),
            "matching_digest_count": sum(
                item.exact_baseline_digest_matches for item in observations
            ),
        },
        "external_a_controlled_by_runtime": False,
        "raw_sensor_payload_retained": False,
        "writes_back": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
