from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
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


@dataclass(frozen=True, slots=True)
class AudioTimingCapture:
    timings: tuple[AudioCallbackTiming, ...]
    callback_frame_counts: tuple[int, ...]
    input_overflow_flags: tuple[bool, ...]
    reported_input_latency_seconds: float
    backend_id: str


def validate_audio_capture(
    capture: AudioTimingCapture,
    *,
    expected_frame_count: int | None,
) -> None:
    callback_count = len(capture.timings)
    if len(capture.callback_frame_counts) != callback_count:
        raise RuntimeError("audio callback frame metadata is incomplete")
    if len(capture.input_overflow_flags) != callback_count:
        raise RuntimeError("audio callback overflow metadata is incomplete")
    if expected_frame_count is not None and any(
        count != expected_frame_count for count in capture.callback_frame_counts
    ):
        raise RuntimeError("audio callback frame count differs from configured hop size")
    if any(capture.input_overflow_flags):
        raise RuntimeError("audio input overflow observed")


def callback_metadata_rows(capture: AudioTimingCapture) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    previous: AudioCallbackTiming | None = None
    for index, (timing, frames, overflow) in enumerate(
        zip(
            capture.timings,
            capture.callback_frame_counts,
            capture.input_overflow_flags,
            strict=True,
        )
    ):
        rows.append(
            {
                "callback_index": index,
                "input_buffer_adc_time_seconds": (
                    timing.input_buffer_adc_time_seconds
                ),
                "stream_current_time_seconds": timing.stream_current_time_seconds,
                "organism_callback_time_seconds": (
                    timing.organism_callback_time_seconds
                ),
                "frame_count": frames,
                "input_overflow": overflow,
                "adc_delta_seconds": (
                    None
                    if previous is None
                    else timing.input_buffer_adc_time_seconds
                    - previous.input_buffer_adc_time_seconds
                ),
                "stream_delta_seconds": (
                    None
                    if previous is None
                    else timing.stream_current_time_seconds
                    - previous.stream_current_time_seconds
                ),
            }
        )
        previous = timing
    return tuple(rows)


def capture_audio_timing(
    *,
    device: int | str,
    callback_count: int,
    blocksize: int = 480,
) -> AudioTimingCapture:
    import sounddevice as sd

    config = LogSpectralConfig()
    observations: list[AudioCallbackTiming] = []
    callback_frame_counts: list[int] = []
    input_overflow_flags: list[bool] = []
    complete = threading.Event()

    def callback(indata, frames, time_info, status) -> None:
        del indata
        if len(observations) >= callback_count:
            return
        observations.append(
            AudioCallbackTiming(
                float(time_info.inputBufferAdcTime),
                float(time_info.currentTime),
                time.monotonic(),
            )
        )
        callback_frame_counts.append(int(frames))
        input_overflow_flags.append(bool(status.input_overflow))
        if len(observations) >= callback_count:
            complete.set()

    with sd.InputStream(
        device=device,
        channels=1,
        dtype="float32",
        samplerate=config.sample_rate,
        blocksize=blocksize,
        callback=callback,
    ) as stream:
        if not complete.wait(timeout=5.0):
            raise RuntimeError("audio callback timing probe timed out")
        latency = float(stream.latency)
    return AudioTimingCapture(
        timings=tuple(observations),
        callback_frame_counts=tuple(callback_frame_counts),
        input_overflow_flags=tuple(input_overflow_flags),
        reported_input_latency_seconds=latency,
        backend_id=sd.get_portaudio_version()[1],
    )


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
    parser.add_argument("--camera-device", type=int)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--audio-only", action="store_true")
    parser.add_argument("--audio-callbacks", type=int, default=20)
    parser.add_argument("--audio-blocksize", type=int, choices=(0, 480), default=480)
    parser.add_argument("--video-frames", type=int, default=10)
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()

    if args.runs <= 0:
        raise ValueError("--runs must be positive")
    if not args.audio_only and args.camera_device is None:
        parser.error("--camera-device is required unless --audio-only is set")
    runs = []
    portaudio = ""
    for run_index in range(args.runs):
        audio_capture = capture_audio_timing(
            device=args.audio_device,
            callback_count=args.audio_callbacks,
            blocksize=args.audio_blocksize,
        )
        audio_config = LogSpectralConfig()
        validate_audio_capture(
            audio_capture,
            expected_frame_count=(
                audio_config.hop_size if args.audio_blocksize != 0 else None
            ),
        )
        portaudio = audio_capture.backend_id
        run = {
            "run_index": run_index,
            "audio": {
                **asdict(
                    audit_audio_callback_timing(
                        audio_capture.timings,
                        reported_input_latency_seconds=(
                            audio_capture.reported_input_latency_seconds
                        ),
                    )
                ),
                "callback_frame_counts": audio_capture.callback_frame_counts,
                "input_overflow_flags": audio_capture.input_overflow_flags,
                "configured_hop_size": audio_config.hop_size,
                "configured_callback_blocksize": args.audio_blocksize,
                "callback_metadata": callback_metadata_rows(audio_capture),
            },
        }
        if not args.audio_only:
            video_observations, video_backend = capture_video_timing(
                device_index=args.camera_device,
                frame_count=args.video_frames,
                startup_frame_count=args.camera_startup_frames,
            )
            run["video"] = asdict(
                audit_video_frame_timing(
                    video_observations,
                    backend_id=video_backend,
                )
            )
        runs.append(run)
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
