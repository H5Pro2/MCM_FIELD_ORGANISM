from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    audit_auditory_temporal_support,
    audit_visual_temporal_support,
    capture_live_common_receptor_window_audit,
)
from mcm_field_organism.finite_video_path import VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig


def audio_device(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit receptor source windows against organism read times."
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
    sequences = {item.modality_id: item for item in captured.sequences}
    audio = audit_auditory_temporal_support(
        sequences["auditory"],
        sample_rate=LogSpectralConfig().sample_rate,
    )
    visual = audit_visual_temporal_support(
        sequences["visual"],
        nominal_frames_per_second=VisualGridConfig().frames_per_second,
    )

    def payload(audit):
        return {
            "source_clock_id": audit.source_clock_id,
            "source_window_role": audit.source_window_role,
            "source_window_width_ticks": audit.source_window_width_ticks,
            "source_stride_ticks": audit.source_stride_ticks,
            "source_window_seconds": audit.source_window_seconds,
            "nominal_output_period_seconds": audit.nominal_output_period_seconds,
            "source_overlap_fraction": audit.source_overlap_fraction,
            "organism_read_seconds": {
                "minimum": audit.organism_read_minimum_seconds,
                "median": audit.organism_read_median_seconds,
                "maximum": audit.organism_read_maximum_seconds,
            },
            "organism_support_is_mapped": audit.organism_support_is_mapped,
            "organism_read_interval_is_world_support": (
                audit.organism_read_interval_is_world_support
            ),
        }

    print(json.dumps(
        {
            "auditory": payload(audio),
            "visual": payload(visual),
            "field_advance_performed": False,
            "hold_or_support_extrapolation_applied": False,
            "raw_sensor_payload_retained": False,
        },
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
