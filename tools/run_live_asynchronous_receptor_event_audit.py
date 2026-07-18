from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    audit_asynchronous_receptor_events,
    capture_live_common_receptor_window_audit,
)


def audio_device(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit asynchronous native receptor completion events."
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
    audit = audit_asynchronous_receptor_events(captured.sequences)
    payload = {
        "clock_id": audit.clock_id,
        "event_counts": dict(audit.event_counts),
        "event_shares": {
            modality_id: audit.event_share(modality_id)
            for modality_id in audit.modality_ids
        },
        "completion_group_count": len(audit.completion_groups),
        "mixed_completion_group_count": audit.mixed_completion_group_count,
        "exclusive_completion_group_counts": dict(
            audit.exclusive_completion_group_counts
        ),
        "field_advance_performed": False,
        "selection_fusion_or_rate_equalization_applied": False,
        "raw_sensor_payload_retained": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
