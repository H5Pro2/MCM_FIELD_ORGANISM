from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import threading
import time


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.adapter_timing_capability import (
    AudioCallbackTiming,
    VideoFrameTiming,
    audit_audio_callback_timing,
    audit_video_frame_timing,
)
from mcm_field_organism.finite_video_path import VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig


def audio_device(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value


def capture_audio_timing(
    *,
    device: int | str,
    callback_count: int,
) -> tuple[tuple[AudioCallbackTiming, ...], float, str]:
    import sounddevice as sd

    config = LogSpectralConfig()
    observations: list[AudioCallbackTiming] = []
    complete = threading.Event()

    def callback(indata, frames, time_info, status) -> None:
        del indata, frames, status
        if len(observations) >= callback_count:
            return
        observations.append(
            AudioCallbackTiming(
                float(time_info.inputBufferAdcTime),
                float(time_info.currentTime),
                time.monotonic(),
            )
        )
        if len(observations) >= callback_count:
            complete.set()

    with sd.InputStream(
        device=device,
        channels=1,
        dtype="float32",
        samplerate=config.sample_rate,
        blocksize=config.hop_size,
        callback=callback,
    ) as stream:
        if not complete.wait(timeout=5.0):
            raise RuntimeError("audio callback timing probe timed out")
        latency = float(stream.latency)
    return tuple(observations), latency, sd.get_portaudio_version()[1]


def capture_video_timing(
    *,
    device_index: int,
    frame_count: int,
    startup_frame_count: int,
) -> tuple[tuple[VideoFrameTiming, ...], str]:
    import cv2

    config = VisualGridConfig()
    capture = cv2.VideoCapture(device_index, cv2.CAP_DSHOW)
    if not capture.isOpened():
        raise RuntimeError(f"cannot open explicit camera device {device_index}")
    try:
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.source_width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.source_height)
        capture.set(cv2.CAP_PROP_FPS, config.frames_per_second)
        backend = capture.getBackendName()
        for _ in range(startup_frame_count):
            ok, _ = capture.read()
            if not ok:
                raise RuntimeError("camera startup read failed")
        observations = []
        for _ in range(frame_count):
            read_start = time.monotonic()
            ok, _ = capture.read()
            read_end = time.monotonic()
            if not ok:
                raise RuntimeError("camera timing read failed")
            observations.append(
                VideoFrameTiming(
                    position_milliseconds=float(capture.get(cv2.CAP_PROP_POS_MSEC)),
                    presentation_timestamp=float(capture.get(cv2.CAP_PROP_PTS)),
                    exposure_setting=float(capture.get(cv2.CAP_PROP_EXPOSURE)),
                    organism_read_start_seconds=read_start,
                    organism_read_end_seconds=read_end,
                )
            )
        return tuple(observations), backend
    finally:
        capture.release()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe timing metadata exposed by explicit live adapters."
    )
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--audio-callbacks", type=int, default=20)
    parser.add_argument("--video-frames", type=int, default=10)
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()

    if args.runs <= 0:
        raise ValueError("--runs must be positive")
    runs = []
    portaudio = ""
    for run_index in range(args.runs):
        audio_observations, latency, portaudio = capture_audio_timing(
            device=args.audio_device,
            callback_count=args.audio_callbacks,
        )
        video_observations, video_backend = capture_video_timing(
            device_index=args.camera_device,
            frame_count=args.video_frames,
            startup_frame_count=args.camera_startup_frames,
        )
        runs.append(
            {
                "run_index": run_index,
                "audio": asdict(
                    audit_audio_callback_timing(
                        audio_observations,
                        reported_input_latency_seconds=latency,
                    )
                ),
                "video": asdict(
                    audit_video_frame_timing(
                        video_observations,
                        backend_id=video_backend,
                    )
                ),
            }
        )
    print(
        json.dumps(
            {
                "audio_backend": portaudio,
                "runs": runs,
                "field_advance_performed": False,
                "raw_sensor_payload_retained": False,
                "support_mapping_applied": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
