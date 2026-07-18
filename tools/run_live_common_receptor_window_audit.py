from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import capture_live_common_receptor_window_audit


def audio_device(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit native receptor occupancy in predeclared organism windows."
    )
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--window-seconds", type=float, default=1.0)
    parser.add_argument("--window-count", type=int, default=3)
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    args = parser.parse_args()

    result = capture_live_common_receptor_window_audit(
        camera_device=args.camera_device,
        audio_device=args.audio_device,
        window_seconds=args.window_seconds,
        window_count=args.window_count,
        camera_startup_frames=args.camera_startup_frames,
    )
    captured = result.receptor_window_audit
    audit = captured.audit
    payload = {
        "camera_startup": {
            "consumed_frames": result.camera_startup.consumed_frames,
            "active_frames": result.camera_startup.active_frames,
        },
        "schedule": {
            "clock_id": captured.schedule.clock_id,
            "window_count": len(captured.schedule.windows),
            "window_width_nanoseconds": (
                captured.schedule.windows[0].field_time.window_end_tick
                - captured.schedule.windows[0].field_time.window_start_tick
            ),
        },
        "native_completed_states": {
            sequence.modality_id: len(sequence.frames)
            for sequence in captured.sequences
        },
        "window_occupancy": [
            {
                "window_index": item.window_index,
                "modality_counts": dict(item.modality_counts),
            }
            for item in audit.occupancies
        ],
        "boundary_crossing_states": len(audit.crossing_snapshot_ids),
        "outside_states": len(audit.outside_snapshot_ids),
        "exact_windows": list(audit.exact_window_indices),
        "every_window_exactly_one_per_modality": (
            audit.every_window_has_exactly_one_state_per_modality
        ),
        "selection_averaging_interpolation_or_hold_applied": False,
        "raw_sensor_payload_retained": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
