from mcm_field_organism.asynchronous_audio_video_rate_probe import (
    RATE_PAIRS,
    run_asynchronous_audio_video_rate_probe,
)


def test_rate_partition_and_order_cases_are_measured_deterministically() -> None:
    result = run_asynchronous_audio_video_rate_probe()

    assert len(result.cases) == len(RATE_PAIRS)
    assert result.deterministic
    assert all(case.reproduction_exact for case in result.cases)
    assert all(case.permutation_layer_equal for case in result.cases)
