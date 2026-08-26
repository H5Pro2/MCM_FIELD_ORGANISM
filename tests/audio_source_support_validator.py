"""Test-only validator for preregistered passive audio source metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SyntheticAudioHopMetadata:
    sample_start: int
    sample_end: int
    frame_count: int
    sample_rate: int
    adc_start_tick: int | None
    adc_end_tick: int | None
    organism_callback_tick: int
    adc_time_exposed: bool = True
    adc_semantics_proven: bool = True
    input_overflow: bool = False
    queue_loss: bool = False
    support_role: str = "new_hop"


@dataclass(frozen=True, slots=True)
class AudioSourceSupportValidation:
    accepted_count: int
    rejected_index: int | None
    rejection_reason: str | None

    @property
    def accepted(self) -> bool:
        return self.rejected_index is None


def validate_audio_source_support(
    frames: tuple[SyntheticAudioHopMetadata, ...],
    *,
    sample_rate: int,
    hop_size: int,
    source_ticks_per_second: int,
) -> AudioSourceSupportValidation:
    """Validate one finite sequence and stop permanently at its first defect."""

    if sample_rate <= 0 or hop_size <= 0 or source_ticks_per_second <= 0:
        raise ValueError("validator configuration must be positive")
    if (hop_size * source_ticks_per_second) % sample_rate:
        raise ValueError("hop duration must be exact on the source clock")
    expected_adc_width = hop_size * source_ticks_per_second // sample_rate

    previous_sample_end: int | None = None
    previous_adc_start: int | None = None
    previous_adc_end: int | None = None

    for index, frame in enumerate(frames):
        reason: str | None = None
        if frame.support_role != "new_hop":
            reason = "analysis_window_is_not_new_source_support"
        elif frame.queue_loss:
            reason = "queue_loss"
        elif frame.input_overflow:
            reason = "input_overflow"
        elif not frame.adc_time_exposed:
            reason = "backend_adc_time_not_exposed"
        elif not frame.adc_semantics_proven:
            reason = "backend_adc_semantics_not_proven"
        elif frame.adc_start_tick is None or frame.adc_end_tick is None:
            reason = "adc_time_missing_or_invalid"
        elif frame.sample_rate != sample_rate:
            reason = "sample_rate_changed"
        elif frame.frame_count != hop_size:
            reason = "frame_count_does_not_match_hop"
        elif frame.sample_end - frame.sample_start != frame.frame_count:
            reason = "sample_interval_does_not_match_frame_count"
        elif frame.adc_end_tick - frame.adc_start_tick != expected_adc_width:
            reason = "adc_interval_does_not_match_hop_duration"
        elif previous_sample_end is not None and frame.sample_start != previous_sample_end:
            reason = "sample_sequence_discontinuity"
        elif previous_adc_start is not None and frame.adc_start_tick <= previous_adc_start:
            reason = "adc_time_not_strictly_monotonic"
        elif previous_adc_end is not None and frame.adc_start_tick < previous_adc_end:
            reason = "adc_interval_overlap"
        elif previous_adc_end is not None and frame.adc_start_tick > previous_adc_end:
            reason = "adc_interval_gap"

        if reason is not None:
            return AudioSourceSupportValidation(index, index, reason)

        previous_sample_end = frame.sample_end
        previous_adc_start = frame.adc_start_tick
        previous_adc_end = frame.adc_end_tick

    return AudioSourceSupportValidation(len(frames), None, None)
