from types import SimpleNamespace

import pytest

from tools.run_live_audio_video_long_stability import (
    evaluate_failure_criteria,
    summarize_long_stability,
)


def observation(index: int):
    return SimpleNamespace(
        window_index=index,
        window_start_tick=index * 10,
        window_end_tick=(index + 1) * 10,
        auditory_receptor_count=100,
        visual_receptor_count=15,
        exact_baseline_digest_matches=True,
        exact_baseline_activation_max_error=0.0,
        exact_baseline_afterimage_max_error=0.0,
    )


def profile(index: int, modality: str):
    return SimpleNamespace(
        window_index=index,
        modality_id=modality,
        frame_count=100 if modality == "auditory" else 15,
        carrier_ids=(f"{modality}.0",),
    )


def test_summary_preserves_ten_six_window_blocks_and_open_failures() -> None:
    observations = [observation(index) for index in range(60)]
    profiles = [
        profile(index, modality)
        for index in range(60)
        for modality in ("auditory", "visual")
    ]
    result = summarize_long_stability(observations, profiles)

    assert len(result["blocks"]) == 10
    assert result["blocks"][0]["auditory_states"] == 600
    assert result["blocks"][-1]["visual_states"] == 90
    assert result["empty_modality_windows"] == []
    assert result["carrier_identity_changes"] == []
    assert result["baseline_failure_windows"] == []


def test_summary_rejects_incomplete_blocks() -> None:
    with pytest.raises(ValueError, match="complete blocks"):
        summarize_long_stability([observation(0)], [], block_size=6)


def test_failure_criteria_report_audio_overflow_independently() -> None:
    summary = {
        "empty_modality_windows": [],
        "nonadvancing_windows": [],
        "carrier_identity_changes": [],
        "baseline_failure_windows": [],
    }

    result = evaluate_failure_criteria(summary, audio_overflow_count=1094)

    assert result["failure_criteria"] == {
        "empty_modality_window": False,
        "audio_overflow": True,
        "nonadvancing_timestamp": False,
        "changed_carrier_identity": False,
        "field_baseline_deviation": False,
    }
    assert result["all_failure_criteria_clear"] is False
