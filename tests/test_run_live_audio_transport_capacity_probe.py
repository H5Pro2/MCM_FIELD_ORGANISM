import pytest

from tools.run_live_audio_transport_capacity_probe import summarize_arm


def test_summary_reports_timing_ranges_and_queue_fraction() -> None:
    arm = {
        "transport_capacity_frames": 200,
        "transport_max_occupancy_frames": 150,
        "primary_field_seconds": [0.2, 0.4],
        "exact_baseline_seconds": [0.1, 0.3],
        "total_field_seconds": [0.3, 0.7],
    }

    result = summarize_arm(arm)

    assert result["primary_field_seconds_mean"] == pytest.approx(0.3)
    assert result["exact_baseline_seconds_max"] == 0.3
    assert result["total_field_seconds_min"] == 0.3
    assert result["queue_occupancy_fraction"] == 0.75
    assert "primary_field_seconds" not in result
