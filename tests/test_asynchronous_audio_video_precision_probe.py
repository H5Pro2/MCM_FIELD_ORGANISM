import math

from mcm_field_organism.asynchronous_audio_video_precision_probe import (
    run_asynchronous_audio_video_precision_probe,
)


def test_precision_probe_reports_signal_null_and_basis_controls() -> None:
    result = run_asynchronous_audio_video_precision_probe()

    assert len(result.cases) == 3
    assert result.neuron_count > 0
    assert result.deterministic
    assert result.numpy_orthogonality_linf > 0.0
    assert result.fsum_orthogonality_linf > 0.0
    values = tuple(
        value
        for case in result.cases
        for value in (
            case.signal_activation_linf,
            case.signal_afterimage_linf,
            case.null_activation_linf,
            case.null_afterimage_linf,
        )
    )
    assert all(math.isfinite(value) and value >= 0.0 for value in values)
    assert any(value > 0.0 for value in values)


def test_precision_probe_preserves_declared_rate_order() -> None:
    result = run_asynchronous_audio_video_precision_probe()

    assert tuple((case.audio_rate_hz, case.video_rate_hz) for case in result.cases) == (
        (50.0, 5.0),
        (100.0, 10.0),
        (200.0, 20.0),
    )
    assert tuple(case.fine_step_count for case in result.cases) == (46, 91, 182)
