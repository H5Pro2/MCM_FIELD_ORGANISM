from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.live_audio_video_field import capture_live_audio_video_time_audit
from mcm_field_organism.receptor_marker_audit import audit_receptor_markers


def audio_device(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit visible and audible transients in reduced receptor states."
    )
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--duration-seconds", type=float, default=10.0)
    parser.add_argument("--baseline-seconds", type=float, default=3.0)
    parser.add_argument("--marker-delay-seconds", type=float, default=1.0)
    parser.add_argument("--marker-count", type=int, default=3)
    parser.add_argument("--minimum-separation-seconds", type=float, default=1.2)
    parser.add_argument(
        "--ready-gate",
        type=Path,
        help="Wait for this file after device startup and remove it before capture.",
    )
    args = parser.parse_args()

    def wait_until_released(startup) -> None:
        if args.ready_gate is None:
            return
        print(json.dumps({
            "capture_ready": True,
            "camera_startup_consumed_frames": startup.consumed_frames,
            "gate": str(args.ready_gate),
        }), flush=True)
        while not args.ready_gate.is_file():
            time.sleep(0.05)
        args.ready_gate.unlink()

    captured = capture_live_audio_video_time_audit(
        camera_device=args.camera_device,
        audio_device=args.audio_device,
        nominal_duration_seconds=args.duration_seconds,
        capture_ready_observer=wait_until_released,
    )
    audit = audit_receptor_markers(
        captured.receptor_time_audit.sequences,
        baseline_seconds=args.baseline_seconds,
        marker_delay_seconds=args.marker_delay_seconds,
        expected_marker_count=args.marker_count,
        minimum_separation_seconds=args.minimum_separation_seconds,
    )
    print(json.dumps({
        "protocol": {
            "duration_seconds": args.duration_seconds,
            "quiet_baseline_seconds": args.baseline_seconds,
            "unscored_transition_seconds": args.marker_delay_seconds,
            "expected_marker_count": args.marker_count,
            "minimum_marker_separation_seconds": args.minimum_separation_seconds,
        },
        "clock_id": audit.clock_id,
        "thresholds": dict(audit.thresholds),
        "responses": {
            modality: [
                {"organism_tick": item.organism_tick, "score": item.score}
                for item in items
            ]
            for modality, items in audit.responses
        },
        "complete_order_pairing": audit.complete_order_pairing,
        "visual_minus_auditory_nanoseconds": audit.visual_minus_auditory_nanoseconds,
        "selection_note": "ranked reduced-state changes; order pairing only when both modalities have the preregistered count",
        "raw_sensor_payload_retained": False,
        "field_mechanism_changed": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
