import pytest

from tools.run_live_process_decoupling_probe import summarize_process_results


def test_process_summary_reports_backlog_latency_and_exact_baseline() -> None:
    captures = [
        {
            "window_index": 0,
            "modalities": ("auditory", "visual"),
            "audio_frames": 100,
            "visual_frames": 10,
            "window_start_tick": 1_000_000_000,
            "window_end_tick": 2_000_000_000,
            "nonadvancing_frame_count": 0,
            "worker_backlog_windows": 1,
            "driver_input_overflow_count": 0,
            "transport_queue_overflow_count": 0,
            "audio_transport_max_occupancy_frames": 5,
        },
        {
            "window_index": 1,
            "modalities": ("auditory", "visual"),
            "audio_frames": 100,
            "visual_frames": 10,
            "window_start_tick": 2_000_000_000,
            "window_end_tick": 3_000_000_000,
            "nonadvancing_frame_count": 0,
            "worker_backlog_windows": 1,
            "driver_input_overflow_count": 0,
            "transport_queue_overflow_count": 0,
            "audio_transport_max_occupancy_frames": 6,
        },
    ]
    results = [
        {
            "window_index": 0,
            "submitted_tick": 2_000_000_000,
            "received_tick": 2_100_000_000,
            "completed_tick": 2_700_000_000,
            "primary_field_seconds": 0.3,
            "exact_baseline_seconds": 0.3,
            "baseline_matches": True,
        },
        {
            "window_index": 1,
            "submitted_tick": 3_000_000_000,
            "received_tick": 3_100_000_000,
            "completed_tick": 3_800_000_000,
            "primary_field_seconds": 0.35,
            "exact_baseline_seconds": 0.35,
            "baseline_matches": True,
        },
    ]

    summary = summarize_process_results(
        captures,
        results,
        max_backlog=1,
        capture_end_backlog=1,
        queue_capacity=4,
    )

    assert summary["audio_frames"] == 200
    assert summary["worker_max_backlog_windows"] == 1
    assert summary["worker_capture_end_backlog_windows"] == 1
    assert summary["worker_post_drain_backlog_windows"] == 0
    assert summary["end_to_end_seconds_max"] == 0.8
    assert summary["worker_queue_wait_seconds_max"] == 0.1
    assert summary["baseline_failure_windows"] == []
    profile = summary["ten_window_profiles"][0]
    assert profile["window_start"] == 0
    assert profile["window_end"] == 1
    assert profile["audio_frames"] == 200
    assert profile["worker_max_backlog_windows"] == 1
    assert profile["audio_transport_max_occupancy_through_interval"] == 6
    assert profile["end_to_end_seconds_mean"] == pytest.approx(0.75)
    assert profile["total_field_seconds_mean"] == pytest.approx(0.65)
    assert profile["baseline_failure_count"] == 0
