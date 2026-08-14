from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.run_live_audio_overflow_localization import audio_device, run_with_field


def summarize_arm(arm: dict[str, object]) -> dict[str, object]:
    primary = arm.pop("primary_field_seconds")
    baseline = arm.pop("exact_baseline_seconds")
    total = arm.pop("total_field_seconds")
    arm.update(
        {
            "primary_field_seconds_min": min(primary),
            "primary_field_seconds_max": max(primary),
            "primary_field_seconds_mean": sum(primary) / len(primary),
            "exact_baseline_seconds_min": min(baseline),
            "exact_baseline_seconds_max": max(baseline),
            "exact_baseline_seconds_mean": sum(baseline) / len(baseline),
            "total_field_seconds_min": min(total),
            "total_field_seconds_max": max(total),
            "total_field_seconds_mean": sum(total) / len(total),
            "queue_occupancy_fraction": (
                arm["transport_max_occupancy_frames"]
                / arm["transport_capacity_frames"]
            ),
        }
    )
    return arm


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe bounded live audio transport capacity.")
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--duration-seconds", type=int, default=30)
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    args = parser.parse_args()
    if args.duration_seconds <= 0 or args.duration_seconds > 30:
        raise ValueError("duration must be between 1 and 30 seconds")

    arms = []
    for horizon in (1.0, 2.0, 4.0):
        arms.append(
            summarize_arm(
                run_with_field(
                    camera_device=args.camera_device,
                    audio_device_id=args.audio_device,
                    duration_seconds=args.duration_seconds,
                    camera_startup_frames=args.camera_startup_frames,
                    transport_horizon_seconds=horizon,
                )
            )
        )
    print(
        json.dumps(
            {
                "duration_seconds_per_arm": args.duration_seconds,
                "arms": arms,
                "raw_sensor_payload_retained": False,
                "field_mechanism_changed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
