from __future__ import annotations

import argparse
import json
import multiprocessing
from pathlib import Path
from queue import Empty
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    AuditoryProbeConfig,
    BroadbandHearingPath,
    LocalChannelGridReceptor,
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
from tools.run_live_two_phase_field_probe import summarize_timing


def _window_payload(index, sequences) -> dict[str, object]:
    all_frames = tuple(
        frame for sequence in sequences for frame in sequence.frames
    )
    return {
        "window_index": index,
        "modalities": tuple(sequence.modality_id for sequence in sequences),
        "audio_frames": len(sequences[0].frames),
        "visual_frames": len(sequences[1].frames),
        "window_start_tick": min(
            frame.field_time.window_start_tick for frame in all_frames
        ),
        "window_end_tick": max(
            frame.field_time.window_end_tick for frame in all_frames
        ),
        "nonadvancing_frame_count": sum(
            frame.field_time.window_end_tick
            <= frame.field_time.window_start_tick
            for frame in all_frames
        ),
    }


def _field_worker(input_queue, result_queue, visual_config, window_count) -> None:
    try:
        visual_receptor = LocalChannelGridReceptor(visual_config)
        field_config = NeutralLocalFieldSubstrateConfig(1.0)
        afterimage_config = NeutralFastAfterimageConfig(0.5)
        current = None
        while True:
            payload = input_queue.get()
            if payload is None:
                break
            index, sequences, submitted_tick = payload
            received_tick = time.monotonic_ns()
            baseline_initial = (
                None
                if current is None
                else restore_shared_mcm_field(
                    SharedMCMFieldSnapshot.from_json(
                        current.snapshot().to_json()
                    )
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
            primary_seconds = time.perf_counter() - started
            current = captured.field_run.field
            checkpoint_after = index + 1 < window_count
            if checkpoint_after:
                current = restore_shared_mcm_field(
                    SharedMCMFieldSnapshot.from_json(
                        current.snapshot().to_json()
                    )
                )
            started = time.perf_counter()
            exact_baseline = advance_audio_video_receptor_sequences(
                sequences,
                visual_receptor,
                field_config,
                afterimage_config=afterimage_config,
                initial_field=baseline_initial,
            )
            baseline_seconds = time.perf_counter() - started
            observation = _observe_live_field_window(
                index,
                captured,
                exact_baseline,
                checkpoint_restored=checkpoint_after,
            )
            result_queue.put(
                {
                    "kind": "window",
                    "window_index": index,
                    "submitted_tick": submitted_tick,
                    "received_tick": received_tick,
                    "completed_tick": time.monotonic_ns(),
                    "primary_field_seconds": primary_seconds,
                    "exact_baseline_seconds": baseline_seconds,
                    "baseline_matches": (
                        observation.exact_baseline_digest_matches
                        and observation.exact_baseline_activation_max_error == 0.0
                        and observation.exact_baseline_afterimage_max_error == 0.0
                    ),
                }
            )
    except BaseException:
        result_queue.put({"kind": "error", "traceback": traceback.format_exc()})


def summarize_process_results(
    captures: list[dict[str, object]],
    results: list[dict[str, object]],
    *,
    max_backlog: int,
    capture_end_backlog: int,
    queue_capacity: int,
) -> dict[str, object]:
    ordered_captures = sorted(captures, key=lambda item: item["window_index"])
    ordered_results = sorted(results, key=lambda item: item["window_index"])
    result_by_index = {item["window_index"]: item for item in ordered_results}
    previous_end = None
    nonadvancing_windows = []
    end_to_end = []
    queue_wait = []
    for capture in ordered_captures:
        index = capture["window_index"]
        end_tick = capture["window_end_tick"]
        if previous_end is not None and end_tick <= previous_end:
            nonadvancing_windows.append(index)
        previous_end = end_tick
        result = result_by_index.get(index)
        if result is not None:
            end_to_end.append((result["completed_tick"] - end_tick) / 1e9)
            queue_wait.append(
                (result["received_tick"] - result["submitted_tick"]) / 1e9
            )
    primary = [item["primary_field_seconds"] for item in ordered_results]
    baseline = [item["exact_baseline_seconds"] for item in ordered_results]
    return {
        "window_count": len(ordered_captures),
        "worker_result_count": len(ordered_results),
        "audio_frames": sum(item["audio_frames"] for item in ordered_captures),
        "visual_frames": sum(item["visual_frames"] for item in ordered_captures),
        "incomplete_windows": [
            item["window_index"]
            for item in ordered_captures
            if item["modalities"] != ("auditory", "visual")
        ],
        "nonadvancing_frame_count": sum(
            item["nonadvancing_frame_count"] for item in ordered_captures
        ),
        "nonadvancing_windows": nonadvancing_windows,
        "baseline_failure_windows": [
            item["window_index"]
            for item in ordered_results
            if not item["baseline_matches"]
        ],
        "worker_queue_capacity_windows": queue_capacity,
        "worker_max_backlog_windows": max_backlog,
        "worker_capture_end_backlog_windows": capture_end_backlog,
        "worker_post_drain_backlog_windows": len(captures) - len(results),
        "end_to_end_seconds_min": min(end_to_end),
        "end_to_end_seconds_max": max(end_to_end),
        "end_to_end_seconds_mean": sum(end_to_end) / len(end_to_end),
        "worker_queue_wait_seconds_max": max(queue_wait),
        "primary_field_seconds": primary,
        "exact_baseline_seconds": baseline,
        "total_field_seconds": [
            first + second
            for first, second in zip(primary, baseline, strict=True)
        ],
        "ten_window_profiles": _ten_window_profiles(
            ordered_captures, ordered_results
        ),
    }


def _ten_window_profiles(captures, results) -> list[dict[str, object]]:
    result_by_index = {item["window_index"]: item for item in results}
    profiles = []
    previous_driver = 0
    previous_transport = 0
    for offset in range(0, len(captures), 10):
        group = captures[offset : offset + 10]
        group_results = [
            result_by_index[item["window_index"]]
            for item in group
            if item["window_index"] in result_by_index
        ]
        last = group[-1]
        driver_total = last["driver_input_overflow_count"]
        transport_total = last["transport_queue_overflow_count"]
        latencies = [
            (result["completed_tick"] - capture["window_end_tick"]) / 1e9
            for capture in group
            for result in group_results
            if result["window_index"] == capture["window_index"]
        ]
        field_totals = [
            result["primary_field_seconds"]
            + result["exact_baseline_seconds"]
            for result in group_results
        ]
        profiles.append(
            {
                "window_start": group[0]["window_index"],
                "window_end": last["window_index"],
                "audio_frames": sum(item["audio_frames"] for item in group),
                "visual_frames": sum(item["visual_frames"] for item in group),
                "worker_max_backlog_windows": max(
                    item["worker_backlog_windows"] for item in group
                ),
                "driver_overflow_increment": driver_total - previous_driver,
                "transport_overflow_increment": (
                    transport_total - previous_transport
                ),
                "audio_transport_max_occupancy_through_interval": last[
                    "audio_transport_max_occupancy_frames"
                ],
                "end_to_end_seconds_mean": sum(latencies) / len(latencies),
                "end_to_end_seconds_max": max(latencies),
                "total_field_seconds_mean": (
                    sum(field_totals) / len(field_totals)
                ),
                "total_field_seconds_max": max(field_totals),
                "baseline_failure_count": sum(
                    not item["baseline_matches"] for item in group_results
                ),
            }
        )
        previous_driver = driver_total
        previous_transport = transport_total
    return profiles


def run_process_decoupled(
    *,
    camera_device: int,
    audio_device_id: int | str,
    duration_seconds: int,
    camera_startup_frames: int,
    worker_queue_capacity: int = 4,
) -> dict[str, object]:
    visual_config = VisualGridConfig()
    spectral = LogSpectralConfig()
    audio_config = AuditoryProbeConfig(
        sample_rate=spectral.sample_rate,
        frame_size=spectral.hop_size,
    )
    auditory_path = BroadbandHearingPath(LogSpectralReceptor(spectral))
    context = multiprocessing.get_context("spawn")
    input_queue = context.Queue(maxsize=worker_queue_capacity)
    result_queue = context.Queue()
    captures = []
    results = []
    max_backlog = 0
    capture_end_backlog = 0

    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        visual_receptor = _live_visual_receptor(visual_config, startup)
        worker = context.Process(
            target=_field_worker,
            args=(
                input_queue,
                result_queue,
                visual_receptor.config,
                duration_seconds,
            ),
        )
        worker.start()
        try:
            with SoundDeviceInputSource(
                device=audio_device_id,
                config=audio_config,
                transport_horizon_seconds=1.0,
            ) as audio_source:
                for index, sequences in enumerate(
                    _capture_live_receptor_windows(
                        audio_source,
                        video_source,
                        auditory_path,
                        visual_receptor,
                        window_seconds=1.0,
                        window_count=duration_seconds,
                    )
                ):
                    capture = _window_payload(index, sequences)
                    captures.append(capture)
                    input_queue.put((index, sequences, time.monotonic_ns()))
                    while True:
                        try:
                            result = result_queue.get_nowait()
                        except Empty:
                            break
                        if result["kind"] == "error":
                            raise RuntimeError(result["traceback"])
                        results.append(result)
                    backlog = len(captures) - len(results)
                    current_diagnostics = audio_source.overflow_diagnostics()
                    capture.update(
                        {
                            "worker_backlog_windows": backlog,
                            "driver_input_overflow_count": (
                                current_diagnostics.driver_input_overflow_count
                            ),
                            "transport_queue_overflow_count": (
                                current_diagnostics.transport_queue_overflow_count
                            ),
                            "audio_transport_max_occupancy_frames": (
                                current_diagnostics.transport_max_occupancy_frames
                            ),
                        }
                    )
                    max_backlog = max(max_backlog, backlog)
                diagnostics = audio_source.overflow_diagnostics()
                capture_end_backlog = len(captures) - len(results)
            camera_capture_frame_count = video_source.capture_frames_read
            input_queue.put(None)
            while len(results) < duration_seconds:
                result = result_queue.get(timeout=30.0)
                if result["kind"] == "error":
                    raise RuntimeError(result["traceback"])
                results.append(result)
                max_backlog = max(max_backlog, len(captures) - len(results))
            worker.join(timeout=10.0)
            if worker.is_alive() or worker.exitcode != 0:
                raise RuntimeError("field worker did not finish cleanly")
        finally:
            if worker.is_alive():
                worker.terminate()
                worker.join()
            input_queue.close()
            result_queue.close()

    return {
        "arm": "process_decoupled_audio_video_with_field",
        **summarize_process_results(
            captures,
            results,
            max_backlog=max_backlog,
            capture_end_backlog=capture_end_backlog,
            queue_capacity=worker_queue_capacity,
        ),
        **diagnostics_payload(diagnostics),
        "camera_capture_frame_count": camera_capture_frame_count,
        "raw_sensor_payload_retained": False,
        "field_mechanism_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare same-process and process-decoupled live field execution."
    )
    parser.add_argument("--camera-device", type=int, required=True)
    parser.add_argument("--audio-device", type=audio_device, required=True)
    parser.add_argument("--duration-seconds", type=int, default=30)
    parser.add_argument("--camera-startup-frames", type=int, default=10)
    parser.add_argument("--process-only", action="store_true")
    args = parser.parse_args()
    maximum = 120 if args.process_only else 30
    if args.duration_seconds <= 0 or args.duration_seconds > maximum:
        raise ValueError(f"duration must be between 1 and {maximum} seconds")

    arms = []
    if not args.process_only:
        arms.append(
            summarize_timing(
                run_with_field(
                    camera_device=args.camera_device,
                    audio_device_id=args.audio_device,
                    duration_seconds=args.duration_seconds,
                    camera_startup_frames=args.camera_startup_frames,
                    transport_horizon_seconds=1.0,
                )
            )
        )
    arms.append(
        summarize_timing(
            run_process_decoupled(
                camera_device=args.camera_device,
                audio_device_id=args.audio_device,
                duration_seconds=args.duration_seconds,
                camera_startup_frames=args.camera_startup_frames,
            )
        )
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
    multiprocessing.freeze_support()
    raise SystemExit(main())
