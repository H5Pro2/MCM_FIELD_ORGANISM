from mcm_field_organism import AudioOverflowDiagnostics
from tools.run_live_audio_overflow_localization import diagnostics_payload


def test_diagnostics_payload_preserves_separate_causes_and_total() -> None:
    result = diagnostics_payload(AudioOverflowDiagnostics(3, 7, 100, 81))

    assert result == {
        "driver_input_overflow_count": 3,
        "transport_queue_overflow_count": 7,
        "transport_capacity_frames": 100,
        "transport_max_occupancy_frames": 81,
        "overflow_count": 10,
    }
