from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time


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
    SharedMCMFieldSnapshot,
    SoundDeviceInputSource,
    VisualGridConfig,
    restore_shared_mcm_field,
)
from mcm_field_organism.audio_video_neutral_field_runtime import (
    advance_audio_video_receptor_sequences,
)
from mcm_field_organism.live_audio_video_field import (
    _capture_live_receptor_windows,
    _live_visual_receptor,
    _observe_live_field_window,
)
from tools.run_live_audio_overflow_localization import (
    audio_device,
    diagnostics_payload,
    run_with_field,
)


def summarize_captured_windows(windows) -> dict[str, object]:
    windows_in = tuple(windows)
    modality_counts = {"auditory": 0, "visual": 0}
    incomplete_windows = []
    nonadvancing_frames = []
    nonadvancing_windows = []
    previous_end = None
    for window_index, sequences in enumerate(windows_in):
        modalities = tuple(sequence.modality_id for sequence in sequences)
        if modalities != ("auditory", "visual"):
            incomplete_windows.append(window_index)
        starts = []
        ends = []
        for sequence in sequences:
            modality_counts[sequence.modality_id] = (
                modality_counts.get(sequence.modality_id, 0) + len(sequence.frames)
            )
            for frame_index, item in enumerate(sequence.frames):
                start = item.field_time.window_start_tick
                end = item.field_time.window_end_tick
                starts.append(start)
                ends.append(end)
                if end <= start:
                    nonadvancing_frames.append(
                        (window_index, sequence.modality_id, frame_index)
                    )
        window_start = min(starts)
        window_end = max(ends)
        if window_end <= window_start or (
            previous_end is not None and window_end <= previous_end
        ):
            nonadvancing_windows.append(window_index)
        previous_end = window_end
    return {
        "window_count": len(windows_in),
        "audio_frames": modality_counts["auditory"],
        "visual_frames": modality_counts["visual"],
        "incomplete_windows": incomplete_windows,
        "nonadvancing_frames": nonadvancing_frames,
        "nonadvancing_windows": nonadvancing_windows,
    }


def replay_captured_windows(windows, visual_receptor) -> dict[str, object]:
    field_config = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage_config = NeutralFastAfterimageConfig(0.5)
    current = None
    observations = []
    primary_seconds = []
    baseline_seconds = []
    checkpoint_count = 0
    windows_in = tuple(windows)
    for index, sequences in enumerate(windows_in):
        baseline_initial = (
            None
            if current is None
            else restore_shared_mcm_field(
                SharedMCMFieldSnapshot.from_json(current.snapshot().to_json())
            )
        )
        started = time.perf_counter()
        captured = advance_audio_video_receptor_sequences(
            sequences,
            visual_receptor,
            field_config,
            afterimage_config=afterimage_config,
            initial_field=current,
        )
        primary_seconds.append(time.perf_counter() - started)
        current = captured.field_run.field
        checkpoint_after = index + 1 < len(windows_in)
        if checkpoint_after:
            current = restore_shared_mcm_field(
                SharedMCMFieldSnapshot.from_json(current.snapshot().to_json())
            )
            checkpoint_count += 1
        started = time.perf_counter()
        exact_baseline = advance_audio_video_receptor_sequences(
            sequences,
            visual_receptor,
            field_config,
            afterimage_config=afterimage_config,
            initial_field=baseline_initial,
        )
        baseline_seconds.append(time.perf_counter() - started)
        observations.append(
            _observe_live_field_window(
                index,
                captured,
                exact_baseline,
                checkpoint_restored=checkpoint_after,
            )
        )
    return {
        "checkpoint_count": checkpoint_count,
        "baseline_failure_windows": [
            item.window_index
            for item in observations
            if not item.exact_baseline_digest_matches
            or item.exact_baseline_activation_max_error != 0.0
            or item.exact_baseline_afterimage_max_error != 0.0
        ],
        "primary_field_seconds": primary_seconds,
        "exact_baseline_seconds": baseline_seconds,
        "total_field_seconds": [
            primary + baseline
            for primary, baseline in zip(
                primary_seconds, baseline_seconds, strict=True
            )
        ],
    }


def run_two_phase(
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
    capture_started = time.perf_counter()
    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        visual_receptor = _live_visual_receptor(visual_config, startup)
        with SoundDeviceInputSource(
            device=audio_device_id,
            config=audio_config,
            transport_horizon_seconds=1.0,
        ) as audio_source:
            windows = tuple(
                _capture_live_receptor_windows(
                    audio_source,
                    video_source,
                    auditory_path,
                    visual_receptor,
                    window_seconds=1.0,
                    window_count=duration_seconds,
                )
            )
            diagnostics = audio_source.overflow_diagnostics()
        camera_capture_frame_count = video_source.capture_frames_read
    capture_seconds = time.perf_counter() - capture_started

    replay_started = time.perf_counter()
    replay = replay_captured_windows(windows, visual_receptor)
    replay_seconds = time.perf_counter() - replay_started
    return {
        "arm": "two_phase_capture_then_field",
        **summarize_captured_windows(windows),
        **diagnostics_payload(diagnostics),
        **replay,
        "camera_capture_frame_count": camera_capture_frame_count,
        "capture_seconds": capture_seconds,
        "field_replay_seconds": replay_seconds,
        "devices_closed_before_field_replay": True,
        "raw_sensor_payload_retained": False,
    }


def summarize_timing(arm: dict[str, object]) -> dict[str, object]:
    for key in (
        "primary_field_seconds",
        "exact_baseline_seconds",
        "total_field_seconds",
    ):
        values = arm.pop(key)
        arm[f"{key}_min"] = min(values)
        arm[f"{key}_max"] = max(values)
        arm[f"{key}_mean"] = sum(values) / len(values)
    return arm


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare online and two-phase live audio-video field execution."
    )
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--duration-seconds", type=int, default=30)
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    args = parser.parse_args()
    if args.duration_seconds <= 0 or args.duration_seconds > 30:
        raise ValueError("duration must be between 1 and 30 seconds")

    online = summarize_timing(
        run_with_field(
            camera_device=args.camera_device,
            audio_device_id=args.audio_device,
            duration_seconds=args.duration_seconds,
            camera_startup_frames=args.camera_startup_frames,
            transport_horizon_seconds=1.0,
        )
    )
    two_phase = summarize_timing(
        run_two_phase(
            camera_device=args.camera_device,
            audio_device_id=args.audio_device,
            duration_seconds=args.duration_seconds,
            camera_startup_frames=args.camera_startup_frames,
        )
    )
    print(
        json.dumps(
            {
                "duration_seconds_per_arm": args.duration_seconds,
                "arms": [online, two_phase],
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
