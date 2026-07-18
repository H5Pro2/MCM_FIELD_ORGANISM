"""Passive rate-invariance baselines for one fully specified contact history."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

from .carrier_baselines import independent_leaky_step


class ReceptorRateInvarianceProbeError(ValueError):
    """Raised when a controlled contact representation is incomplete."""


@dataclass(frozen=True, slots=True)
class TimedContactSegment:
    start_tick: int
    end_tick: int
    contact: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.start_tick, bool)
            or isinstance(self.end_tick, bool)
            or not isinstance(self.start_tick, int)
            or not isinstance(self.end_tick, int)
            or self.start_tick < 0
            or self.end_tick <= self.start_tick
        ):
            raise ReceptorRateInvarianceProbeError(
                "contact segment requires a positive tick interval"
            )
        contact = float(self.contact)
        if not math.isfinite(contact) or abs(contact) > 1.0:
            raise ReceptorRateInvarianceProbeError(
                "contact must stay within the normalized field domain"
            )
        object.__setattr__(self, "contact", contact)


@dataclass(frozen=True, slots=True)
class ContactRateRepresentation:
    representation_id: str
    segments: tuple[TimedContactSegment, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.representation_id, str) or not self.representation_id:
            raise ReceptorRateInvarianceProbeError(
                "representation_id must be non-empty"
            )
        segments = tuple(self.segments)
        if not segments or any(
            not isinstance(segment, TimedContactSegment) for segment in segments
        ):
            raise ReceptorRateInvarianceProbeError(
                "rate representation requires timed contact segments"
            )
        if segments[0].start_tick != 0 or any(
            earlier.end_tick != later.start_tick
            for earlier, later in zip(segments, segments[1:])
        ):
            raise ReceptorRateInvarianceProbeError(
                "contact segments must cover one contiguous history from tick zero"
            )
        object.__setattr__(self, "segments", segments)

    @property
    def end_tick(self) -> int:
        return self.segments[-1].end_tick


@dataclass(frozen=True, slots=True)
class RateInvarianceObservation:
    tau_seconds: float
    physical_time_dense_end: float
    physical_time_sparse_end: float
    physical_time_difference: float
    event_count_dense_end: float
    event_count_sparse_end: float
    event_count_difference: float


@dataclass(frozen=True, slots=True)
class ReceptorRateInvarianceProbeResult:
    tick_seconds: float
    dense_segment_count: int
    sparse_segment_count: int
    observations: tuple[RateInvarianceObservation, ...]
    omitted_contact_reference_end: float
    omitted_contact_sparse_end: float
    omitted_contact_difference: float

    @property
    def physical_time_baseline_is_rate_invariant(self) -> bool:
        return all(
            observation.physical_time_difference <= 1e-14
            for observation in self.observations
        )

    @property
    def event_count_baseline_is_rate_invariant(self) -> bool:
        return all(
            observation.event_count_difference <= 1e-14
            for observation in self.observations
        )


def _end_afterimage(
    representation: ContactRateRepresentation,
    *,
    tick_seconds: float,
    tau_seconds: float,
    use_physical_duration: bool,
) -> float:
    afterimage = (0.0,)
    for segment in representation.segments:
        dt = (
            (segment.end_tick - segment.start_tick) * tick_seconds
            if use_physical_duration
            else 1.0
        )
        frame = independent_leaky_step(
            afterimage,
            (segment.contact,),
            dt=dt,
            tau=tau_seconds,
        )
        afterimage = frame.afterimage
    return afterimage[0]


def _piecewise_representation(
    representation_id: str,
    *,
    segment_width_ticks: int,
) -> ContactRateRepresentation:
    segments = tuple(
        TimedContactSegment(
            start,
            start + segment_width_ticks,
            0.8 if start < 10 else 0.0,
        )
        for start in range(0, 20, segment_width_ticks)
    )
    return ContactRateRepresentation(representation_id, segments)


def run_receptor_rate_invariance_probe() -> ReceptorRateInvarianceProbeResult:
    """Compare elapsed-time and event-count baselines without field runtime."""

    tick_seconds = 0.1
    dense = _piecewise_representation("dense", segment_width_ticks=1)
    sparse = _piecewise_representation("sparse", segment_width_ticks=5)
    observations = []
    for tau_seconds in (0.25, 1.0, 4.0):
        physical_dense = _end_afterimage(
            dense,
            tick_seconds=tick_seconds,
            tau_seconds=tau_seconds,
            use_physical_duration=True,
        )
        physical_sparse = _end_afterimage(
            sparse,
            tick_seconds=tick_seconds,
            tau_seconds=tau_seconds,
            use_physical_duration=True,
        )
        count_dense = _end_afterimage(
            dense,
            tick_seconds=tick_seconds,
            tau_seconds=tau_seconds,
            use_physical_duration=False,
        )
        count_sparse = _end_afterimage(
            sparse,
            tick_seconds=tick_seconds,
            tau_seconds=tau_seconds,
            use_physical_duration=False,
        )
        observations.append(
            RateInvarianceObservation(
                tau_seconds=tau_seconds,
                physical_time_dense_end=physical_dense,
                physical_time_sparse_end=physical_sparse,
                physical_time_difference=abs(physical_dense - physical_sparse),
                event_count_dense_end=count_dense,
                event_count_sparse_end=count_sparse,
                event_count_difference=abs(count_dense - count_sparse),
            )
        )

    pulse_reference = ContactRateRepresentation(
        "pulse.reference",
        tuple(
            TimedContactSegment(tick, tick + 1, 1.0 if tick == 9 else 0.0)
            for tick in range(20)
        ),
    )
    pulse_omitted = ContactRateRepresentation(
        "pulse.omitted",
        (
            TimedContactSegment(0, 5, 0.0),
            TimedContactSegment(5, 10, 0.0),
            TimedContactSegment(10, 15, 0.0),
            TimedContactSegment(15, 20, 0.0),
        ),
    )
    reference_end = _end_afterimage(
        pulse_reference,
        tick_seconds=tick_seconds,
        tau_seconds=1.0,
        use_physical_duration=True,
    )
    omitted_end = _end_afterimage(
        pulse_omitted,
        tick_seconds=tick_seconds,
        tau_seconds=1.0,
        use_physical_duration=True,
    )
    return ReceptorRateInvarianceProbeResult(
        tick_seconds=tick_seconds,
        dense_segment_count=len(dense.segments),
        sparse_segment_count=len(sparse.segments),
        observations=tuple(observations),
        omitted_contact_reference_end=reference_end,
        omitted_contact_sparse_end=omitted_end,
        omitted_contact_difference=abs(reference_end - omitted_end),
    )


def receptor_rate_invariance_probe_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            TimedContactSegment,
            ContactRateRepresentation,
            RateInvarianceObservation,
            ReceptorRateInvarianceProbeResult,
        )
        for item in fields(cls)
    )
