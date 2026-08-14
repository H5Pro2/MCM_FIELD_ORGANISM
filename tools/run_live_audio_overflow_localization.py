from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    AuditoryProbeConfig,
    BroadbandHearingPath,
    LogSpectralConfig,
    LogSpectralReceptor,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    OpenCVVideoFrameSource,
    SoundDeviceInputSource,
    VisualGridConfig,
    capture_live_audio_video_neutral_session,
)
from mcm_field_organism.live_audio_video_field import (
    _capture_live_receptor_windows,
    _live_visual_receptor,
)


def audio_device(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


def diagnostics_payload(diagnostics) -> dict[str, int]:
    payload = asdict(diagnostics)
    payload["overflow_count"] = diagnostics.overflow_count
    return payload


def run_audio_only(*, device: int | str, duration_seconds: int) -> dict[str, object]:
    spectral = LogSpectralConfig()
    config = AuditoryProbeConfig(
        sample_rate=spectral.sample_rate,
        frame_size=spectral.hop_size,
    )
    frame_count = round(duration_seconds / config.dt)
    first_tick = None
    last_tick = None
    with SoundDeviceInputSource(device=device, config=config) as source:
        for _ in range(frame_count):
            _, start_tick, end_tick = source.read_timed_frame()
            if first_tick is None:
                first_tick = start_tick
            last_tick = end_tick
        diagnostics = source.overflow_diagnostics()
    return {
        "arm": "audio_adapter_only",
        "audio_frames": frame_count,
        "visual_frames": 0,
        "capture_span_seconds": (last_tick - first_tick) / 1_000_000_000.0,
        **diagnostics_payload(diagnostics),
    }


def run_receptors_only(
    *,
    camera_device: int,
    audio_device_id: int | str,
    duration_seconds: int,
    camera_startup_frames: int,
) -> dict[str, object]:
    visual_config = VisualGridConfig()
    spectral = LogSpectralConfig()
    audio_config = AuditoryProbeConfig(
        sample_rate=spectral.sample_rate,
        frame_size=spectral.hop_size,
    )
    auditory_path = BroadbandHearingPath(LogSpectralReceptor(spectral))
    audio_frames = 0
    visual_frames = 0
    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        visual_receptor = _live_visual_receptor(visual_config, startup)
        with SoundDeviceInputSource(device=audio_device_id, config=audio_config) as source:
            for sequences in _capture_live_receptor_windows(
                source,
                video_source,
                auditory_path,
                visual_receptor,
                window_seconds=1.0,
                window_count=duration_seconds,
            ):
                for sequence in sequences:
                    if sequence.modality_id == "auditory":
                        audio_frames += len(sequence.frames)
                    elif sequence.modality_id == "visual":
                        visual_frames += len(sequence.frames)
            diagnostics = source.overflow_diagnostics()
    return {
        "arm": "audio_video_receptors_only",
        "audio_frames": audio_frames,
        "visual_frames": visual_frames,
        **diagnostics_payload(diagnostics),
    }


def run_with_field(
    *,
    camera_device: int,
    audio_device_id: int | str,
    duration_seconds: int,
    camera_startup_frames: int,
    transport_horizon_seconds: float = 1.0,
) -> dict[str, object]:
    diagnostics = []
    observations = []
    timings = []
    result = capture_live_audio_video_neutral_session(
        camera_device=camera_device,
        audio_device=audio_device_id,
        field_config=NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=NeutralFastAfterimageConfig(0.5),
        window_seconds=1.0,
        window_count=duration_seconds,
        max_windows=duration_seconds,
        camera_startup_frames=camera_startup_frames,
        window_observer=observations.append,
        audio_diagnostics_observer=diagnostics.append,
        field_timing_observer=timings.append,
        audio_transport_horizon_seconds=transport_horizon_seconds,
    )
    return {
        "arm": "audio_video_with_field",
        "audio_frames": sum(item.auditory_receptor_count for item in observations),
        "visual_frames": sum(item.visual_receptor_count for item in observations),
        "baseline_failure_windows": [
            item.window_index
            for item in observations
            if not item.exact_baseline_digest_matches
        ],
        "checkpoint_count": result.checkpoint_count,
        "transport_horizon_seconds": transport_horizon_seconds,
        "nonadvancing_windows": [
            item.window_index
            for item in observations
            if item.window_end_tick <= item.window_start_tick
        ],
        "primary_field_seconds": [item.primary_field_seconds for item in timings],
        "exact_baseline_seconds": [item.exact_baseline_seconds for item in timings],
        "total_field_seconds": [item.total_field_seconds for item in timings],
        **diagnostics_payload(diagnostics[0]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Localize live audio overflow causes.")
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--duration-seconds", type=int, default=30)
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    args = parser.parse_args()
    if args.duration_seconds <= 0 or args.duration_seconds > 30:
        raise ValueError("duration must be between 1 and 30 seconds")

    arms = (
        run_audio_only(device=args.audio_device, duration_seconds=args.duration_seconds),
        run_receptors_only(
            camera_device=args.camera_device,
            audio_device_id=args.audio_device,
            duration_seconds=args.duration_seconds,
            camera_startup_frames=args.camera_startup_frames,
        ),
        run_with_field(
            camera_device=args.camera_device,
            audio_device_id=args.audio_device,
            duration_seconds=args.duration_seconds,
            camera_startup_frames=args.camera_startup_frames,
        ),
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
