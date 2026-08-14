from types import SimpleNamespace

import pytest

from tools.run_live_two_phase_field_probe import (
    summarize_captured_windows,
    summarize_timing,
)


def _sequence(modality: str, intervals: tuple[tuple[int, int], ...]):
    return SimpleNamespace(
        modality_id=modality,
        frames=tuple(
            SimpleNamespace(
                field_time=SimpleNamespace(
                    window_start_tick=start,
                    window_end_tick=end,
                )
            )
            for start, end in intervals
        ),
    )


def test_captured_summary_requires_both_modalities_and_advancing_time() -> None:
    windows = (
        (_sequence("auditory", ((1, 2), (2, 3))), _sequence("visual", ((1, 3),))),
        (_sequence("auditory", ((3, 4),)), _sequence("visual", ((3, 5),))),
    )

    result = summarize_captured_windows(windows)

    assert result == {
        "window_count": 2,
        "audio_frames": 3,
        "visual_frames": 2,
        "incomplete_windows": [],
        "nonadvancing_frames": [],
        "nonadvancing_windows": [],
    }


def test_timing_summary_reduces_raw_per_window_lists() -> None:
    arm = {
        "primary_field_seconds": [0.2, 0.4],
        "exact_baseline_seconds": [0.1, 0.3],
        "total_field_seconds": [0.3, 0.7],
    }

    result = summarize_timing(arm)

    assert result["primary_field_seconds_mean"] == pytest.approx(0.3)
    assert result["exact_baseline_seconds_max"] == 0.3
    assert result["total_field_seconds_min"] == 0.3
    assert "primary_field_seconds" not in result
