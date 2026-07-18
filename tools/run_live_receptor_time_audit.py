from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import capture_live_audio_video_time_audit


def audio_device(value: str) -> int | str:
    stripped = value.strip()
    if not stripped:
        raise argparse.ArgumentTypeError("audio device cannot be empty")
    try:
        return int(stripped)
    except ValueError:
        return stripped


def sequence_timing(sequence) -> dict[str, object]:
    durations = [
        item.field_time.window_end_tick
        - item.field_time.window_start_tick
        for item in sequence.frames
    ]
    return {
        "modality_id": sequence.modality_id,
        "completed_states": len(sequence.frames),
        "capture_span_nanoseconds": (
            sequence.frames[-1].field_time.window_end_tick
            - sequence.frames[0].field_time.window_start_tick
        ),
        "read_duration_nanoseconds": {
            "minimum": min(durations),
            "median": int(statistics.median(durations)),
            "maximum": max(durations),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit every reduced auditory and visual receptor state on one "
            "organism clock without interpolation or forced pairing."
        )
    )
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument(
        "--nominal-duration-seconds",
        type=float,
        default=1.0,
    )
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    args = parser.parse_args()

    result = capture_live_audio_video_time_audit(
        camera_device=args.camera_device,
        audio_device=args.audio_device,
        nominal_duration_seconds=args.nominal_duration_seconds,
        camera_startup_frames=args.camera_startup_frames,
    )
    audit = result.receptor_time_audit.audit
    payload = {
        "camera_startup": {
            "consumed_frames": result.camera_startup.consumed_frames,
            "active_frames": result.camera_startup.active_frames,
        },
        "organism_clock_id": audit.clock_id,
        "sequences": [
            sequence_timing(sequence)
            for sequence in result.receptor_time_audit.sequences
        ],
        "alignment": {
            "overlap_count": len(audit.overlaps),
            "unambiguous_overlap_count": len(
                audit.unambiguous_overlaps
            ),
            "ambiguous_snapshot_count": len(
                audit.ambiguous_snapshot_ids
            ),
            "unmatched_snapshot_count": len(
                audit.unmatched_snapshot_ids
            ),
            "complete_one_to_one": (
                audit.has_complete_one_to_one_alignment
            ),
            "selection_or_interpolation_applied": False,
        },
        "raw_sensor_payload_retained": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
