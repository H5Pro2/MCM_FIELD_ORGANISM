from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import capture_live_common_receptor_window_audit
from mcm_field_organism.asynchronous_dock_adjacency_audit import (
    audit_asynchronous_dock_adjacency,
)


def audio_device(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit live same-dock adjacency without advancing the field."
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
    result = audit_asynchronous_dock_adjacency(captured.sequences)
    payload = {
        "completion_group_count": result.completion_group_count,
        "measures": [
            {
                "modality_id": item.modality_id,
                "event_count": item.event_count,
                "within_dock_pair_count": item.within_dock_pair_count,
                "globally_adjacent_pair_count": (
                    item.globally_adjacent_pair_count
                ),
                "interrupted_pair_count": item.interrupted_pair_count,
                "globally_adjacent_pair_fraction": (
                    item.globally_adjacent_pair_fraction
                ),
            }
            for item in result.measures
        ],
        "field_advance_performed": False,
        "contact_persistence_added": False,
        "raw_sensor_payload_retained": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
