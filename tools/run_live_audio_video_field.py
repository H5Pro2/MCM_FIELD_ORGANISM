from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import capture_live_audio_video_field


def audio_device(value: str) -> int | str:
    stripped = value.strip()
    if not stripped:
        raise argparse.ArgumentTypeError("audio device cannot be empty")
    try:
        return int(stripped)
    except ValueError:
        return stripped


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Capture one finite auditory-visual receptor contact into the "
            "shared MCM field without retaining raw sensor payload."
        )
    )
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--duration-seconds", type=float, default=1.0)
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    args = parser.parse_args()

    result = capture_live_audio_video_field(
        camera_device=args.camera_device,
        audio_device=args.audio_device,
        duration_seconds=args.duration_seconds,
        camera_startup_frames=args.camera_startup_frames,
    )
    run = result.field_run
    field = run.shared_field_result
    starts = [
        item.capture_start_tick for item in run.timed_receptor_frames
    ]
    ends = [item.capture_end_tick for item in run.timed_receptor_frames]
    payload = {
        "camera_startup": {
            "consumed_frames": result.camera_startup.consumed_frames,
            "active_frames": result.camera_startup.active_frames,
            "reported_width": result.camera_startup.reported_width,
            "reported_height": result.camera_startup.reported_height,
            "reported_frames_per_second": (
                result.camera_startup.reported_frames_per_second
            ),
        },
        "receptor_contact": {
            "modalities": [
                item.frame.modality_id
                for item in run.timed_receptor_frames
            ],
            "overlap_nanoseconds": min(ends) - max(starts),
            "auditory_snapshots": run.auditory_summary.output_snapshots,
            "visual_states": run.visual_summary.output_states,
            "auditory_overflows": run.auditory_summary.overflow_count,
        },
        "shared_field": {
            "field_id": field.field_state.field_id,
            "geometry_id": field.field_state.geometry_id,
            "tick": field.field_state.tick,
            "neuron_count": len(field.field_state.neuron_ids),
            "active_neuron_count": sum(
                value != 0.0 for value in field.field_state.activation
            ),
            "digest": field.field_state.digest(),
        },
        "raw_sensor_payload_retained": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
