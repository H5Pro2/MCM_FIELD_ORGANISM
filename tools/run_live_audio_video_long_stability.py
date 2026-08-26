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
    try:
        return int(value)
    except ValueError:
        return value


def summarize_long_stability(observations, profiles, *, block_size: int = 6):
    if not observations or len(observations) % block_size:
        raise ValueError("observations must form complete blocks")
    profile_map = {
        (item.window_index, item.modality_id): item for item in profiles
    }
    modalities = ("auditory", "visual")
    empty = []
    carrier_changes = []
    nonadvancing = []
    baseline_failures = []
    blocks = []
    reference_carriers = {}
    for modality in modalities:
        first = profile_map.get((0, modality))
        if first is not None:
            reference_carriers[modality] = first.carrier_ids
    for item in observations:
        if item.window_end_tick <= item.window_start_tick:
            nonadvancing.append(item.window_index)
        if not item.exact_baseline_digest_matches or (
            item.exact_baseline_activation_max_error != 0.0
            or item.exact_baseline_afterimage_max_error != 0.0
        ):
            baseline_failures.append(item.window_index)
        for modality in modalities:
            profile = profile_map.get((item.window_index, modality))
            if profile is None or profile.frame_count < 1:
                empty.append((item.window_index, modality))
            elif profile.carrier_ids != reference_carriers.get(modality):
                carrier_changes.append((item.window_index, modality))
    for start in range(0, len(observations), block_size):
        group = observations[start : start + block_size]
        blocks.append(
            {
                "block_index": start // block_size,
                "window_start": start,
                "window_end": start + block_size - 1,
                "auditory_states": sum(x.auditory_receptor_count for x in group),
                "visual_states": sum(x.visual_receptor_count for x in group),
                "baseline_matches": sum(x.exact_baseline_digest_matches for x in group),
            }
        )
    return {
        "blocks": blocks,
        "empty_modality_windows": empty,
        "nonadvancing_windows": nonadvancing,
        "carrier_identity_changes": carrier_changes,
        "baseline_failure_windows": baseline_failures,
    }


def evaluate_failure_criteria(summary, *, audio_overflow_count: int):
    criteria = {
        "empty_modality_window": bool(summary["empty_modality_windows"]),
        "audio_overflow": audio_overflow_count > 0,
        "nonadvancing_timestamp": bool(summary["nonadvancing_windows"]),
        "changed_carrier_identity": bool(summary["carrier_identity_changes"]),
        "field_baseline_deviation": bool(summary["baseline_failure_windows"]),
    }
    return {
        "failure_criteria": criteria,
        "all_failure_criteria_clear": not any(criteria.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a bounded 60-window live stability audit.")
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    args = parser.parse_args()

    observations = []
    profiles = []
    result = capture_live_audio_video_neutral_session(
        camera_device=args.camera_device,
        audio_device=args.audio_device,
        field_config=NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=NeutralFastAfterimageConfig(0.5),
        window_seconds=1.0,
        window_count=60,
        max_windows=60,
        camera_startup_frames=args.camera_startup_frames,
        window_observer=observations.append,
        receptor_profile_observer=profiles.append,
    )
    summary = summarize_long_stability(observations, profiles)
    summary.update(
        evaluate_failure_criteria(
            summary,
            audio_overflow_count=result.audio_overflow_count,
        )
    )
    summary.update(
        {
            "window_count": result.field_session.window_count,
            "camera_frame_count": result.camera_capture_frame_count,
            "audio_overflow_count": result.audio_overflow_count,
            "checkpoint_count": result.checkpoint_count,
            "raw_sensor_payload_retained": False,
            "writes_back": False,
        }
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
