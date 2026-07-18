from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    MCMFieldStepTime,
    capture_live_common_receptor_window_audit,
    handoff_receptor_completion_groups,
)


def audio_device(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit live completion handoff into declared proposal spans."
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
    steps = tuple(
        MCMFieldStepTime(
            window.field_time.clock_id,
            window.field_time.window_start_tick,
            window.field_time.window_end_tick,
            1_000_000_000.0,
        )
        for window in captured.schedule.windows
    )
    result = handoff_receptor_completion_groups(captured.sequences, steps)
    payload = {
        "source_event_count": result.source_event_count,
        "assigned_event_count": result.assigned_event_count,
        "completed_before_or_at_start_count": len(
            result.completed_before_or_at_start_snapshot_ids
        ),
        "completed_after_horizon_count": len(
            result.completed_after_horizon_snapshot_ids
        ),
        "every_in_horizon_event_assigned_once": (
            result.every_in_horizon_event_assigned_once
        ),
        "batch_modality_event_counts": [
            dict(batch.modality_event_counts) for batch in result.batches
        ],
        "field_advance_performed": False,
        "event_selection_or_reduction_applied": False,
        "raw_sensor_payload_retained": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
