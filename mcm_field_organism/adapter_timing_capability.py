"""Passive capability audit for acquisition timing exposed by sensor backends."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
import statistics


class AdapterTimingCapabilityError(ValueError):
    """Raised when timing evidence is malformed or insufficient."""


@dataclass(frozen=True, slots=True)
class AudioCallbackTiming:
    input_buffer_adc_time_seconds: float
    stream_current_time_seconds: float
    organism_callback_time_seconds: float


@dataclass(frozen=True, slots=True)
class AudioAdapterTimingCapability:
    callback_count: int
    reported_input_latency_seconds: float
    adc_time_exposed: bool
    adc_time_strictly_monotonic: bool
    adc_time_usable_as_source_clock: bool
    stream_current_time_exposed: bool
    stream_current_time_strictly_monotonic: bool
    stream_current_time_usable_as_source_clock: bool
    adc_step_minimum_seconds: float
    adc_step_median_seconds: float
    adc_step_maximum_seconds: float
    adc_to_stream_current_median_seconds: float | None
    stream_to_organism_offset_span_seconds: float | None
    blocking_adapter_exposes_adc_time: bool
    organism_support_is_mapped: bool


@dataclass(frozen=True, slots=True)
class VideoFrameTiming:
    position_milliseconds: float
    presentation_timestamp: float
    exposure_setting: float
    organism_read_start_seconds: float
    organism_read_end_seconds: float


@dataclass(frozen=True, slots=True)
class VideoAdapterTimingCapability:
    frame_count: int
    backend_id: str
    position_time_available: bool
    position_time_strictly_monotonic: bool
    presentation_time_available: bool
    presentation_time_strictly_monotonic: bool
    exposure_setting_available: bool
    exposure_duration_available: bool
    read_minimum_seconds: float
    read_median_seconds: float
    read_maximum_seconds: float
    organism_support_is_mapped: bool


def _finite(value: float, role: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise AdapterTimingCapabilityError(f"{role} must be finite")
    return result


def _strictly_increasing(values: tuple[float, ...]) -> bool:
    return all(later > earlier for earlier, later in zip(values, values[1:]))


def audit_audio_callback_timing(
    timings: tuple[AudioCallbackTiming, ...],
    *,
    reported_input_latency_seconds: float,
) -> AudioAdapterTimingCapability:
    """Audit backend timing without turning it into field support."""

    if len(timings) < 3:
        raise AdapterTimingCapabilityError(
            "audio timing audit requires at least three callbacks"
        )
    latency = _finite(reported_input_latency_seconds, "reported input latency")
    if latency < 0.0:
        raise AdapterTimingCapabilityError(
            "reported input latency must not be negative"
        )

    adc = tuple(
        _finite(item.input_buffer_adc_time_seconds, "input buffer ADC time")
        for item in timings
    )
    current = tuple(
        _finite(item.stream_current_time_seconds, "stream current time")
        for item in timings
    )
    organism = tuple(
        _finite(item.organism_callback_time_seconds, "organism callback time")
        for item in timings
    )
    adc_steps = tuple(later - earlier for earlier, later in zip(adc, adc[1:]))
    adc_monotonic = _strictly_increasing(adc)
    current_monotonic = _strictly_increasing(current)
    stream_offsets = (
        tuple(
            organism_time - stream_time
            for organism_time, stream_time in zip(organism, current, strict=True)
        )
        if current_monotonic
        else ()
    )
    return AudioAdapterTimingCapability(
        callback_count=len(timings),
        reported_input_latency_seconds=latency,
        adc_time_exposed=True,
        adc_time_strictly_monotonic=adc_monotonic,
        adc_time_usable_as_source_clock=adc_monotonic,
        stream_current_time_exposed=True,
        stream_current_time_strictly_monotonic=current_monotonic,
        stream_current_time_usable_as_source_clock=current_monotonic,
        adc_step_minimum_seconds=min(adc_steps),
        adc_step_median_seconds=float(statistics.median(adc_steps)),
        adc_step_maximum_seconds=max(adc_steps),
        adc_to_stream_current_median_seconds=(
            float(
                statistics.median(
                    current_time - adc_time
                    for adc_time, current_time in zip(adc, current, strict=True)
                )
            )
            if adc_monotonic and current_monotonic
            else None
        ),
        stream_to_organism_offset_span_seconds=(
            max(stream_offsets) - min(stream_offsets)
            if stream_offsets
            else None
        ),
        blocking_adapter_exposes_adc_time=False,
        organism_support_is_mapped=False,
    )


def audit_video_frame_timing(
    timings: tuple[VideoFrameTiming, ...],
    *,
    backend_id: str,
) -> VideoAdapterTimingCapability:
    """Audit live-video metadata without treating settings as capture timing."""

    if len(timings) < 3:
        raise AdapterTimingCapabilityError(
            "video timing audit requires at least three frames"
        )
    if not backend_id:
        raise AdapterTimingCapabilityError("backend_id must not be empty")

    positions = tuple(
        _finite(item.position_milliseconds, "video position time")
        for item in timings
    )
    presentations = tuple(
        _finite(item.presentation_timestamp, "video presentation timestamp")
        for item in timings
    )
    exposures = tuple(
        _finite(item.exposure_setting, "video exposure setting")
        for item in timings
    )
    durations = tuple(
        _finite(item.organism_read_end_seconds, "video read end")
        - _finite(item.organism_read_start_seconds, "video read start")
        for item in timings
    )
    if any(duration < 0.0 for duration in durations):
        raise AdapterTimingCapabilityError("video read duration must not be negative")

    usable_positions = tuple(value for value in positions if value >= 0.0)
    usable_presentations = tuple(value for value in presentations if value >= 0.0)
    return VideoAdapterTimingCapability(
        frame_count=len(timings),
        backend_id=backend_id,
        position_time_available=len(usable_positions) == len(positions),
        position_time_strictly_monotonic=(
            len(usable_positions) == len(positions)
            and _strictly_increasing(usable_positions)
        ),
        presentation_time_available=(
            len(usable_presentations) == len(presentations)
        ),
        presentation_time_strictly_monotonic=(
            len(usable_presentations) == len(presentations)
            and _strictly_increasing(usable_presentations)
        ),
        exposure_setting_available=all(value != -1.0 for value in exposures),
        exposure_duration_available=False,
        read_minimum_seconds=min(durations),
        read_median_seconds=float(statistics.median(durations)),
        read_maximum_seconds=max(durations),
        organism_support_is_mapped=False,
    )


def adapter_timing_capability_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            AudioAdapterTimingCapability,
            VideoAdapterTimingCapability,
        )
        for item in fields(contract)
    )
