from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    capture_live_common_receptor_window_audit,
    partition_receptor_completion_time,
)


def audio_device(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Partition one live horizon at native completion boundaries."
    )
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--window-seconds", type=float, default=1.0)
    parser.add_argument("--window-count", type=int, default=3)
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    args = parser.parse_args()

    captured = capture_live_common_receptor_window_audit(
        camera_device=args.camera_device,
        audio_device=args.audio_device,
        window_seconds=args.window_seconds,
        window_count=args.window_count,
        camera_startup_frames=args.camera_startup_frames,
    ).receptor_window_audit
    partition = partition_receptor_completion_time(
        captured.sequences,
        horizon_start_tick=captured.schedule.start_tick,
        horizon_end_tick=captured.schedule.end_tick,
        ticks_per_second=1_000_000_000.0,
    )
    durations = [item.step_time.elapsed_ticks for item in partition.slices]
    modality_events: dict[str, int] = {}
    for item in partition.slices:
        for event in item.completion_events:
            modality_events[event.modality_id] = (
                modality_events.get(event.modality_id, 0) + 1
            )
    payload = {
        "clock_id": partition.clock_id,
        "horizon_ticks": (
            partition.horizon_end_tick - partition.horizon_start_tick
        ),
        "covered_ticks": partition.covered_ticks,
        "slice_count": len(partition.slices),
        "eventful_slice_count": partition.eventful_slice_count,
        "empty_slice_count": partition.empty_slice_count,
        "slice_duration_nanoseconds": {
            "minimum": min(durations),
            "median": int(statistics.median(durations)),
            "maximum": max(durations),
        },
        "in_horizon_events": modality_events,
        "before_or_at_start_events": len(
            partition.completed_before_or_at_start_snapshot_ids
        ),
        "after_horizon_events": len(
            partition.completed_after_horizon_snapshot_ids
        ),
        "field_advance_performed": False,
        "hold_selection_interpolation_or_reconstruction_applied": False,
        "raw_sensor_payload_retained": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
