"""Passive baselines for temporal measures of causal receptor deliveries."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math


class ReceptorDeliveryModelProbeError(ValueError):
    """Raised when a delivery representation is incomplete or inconsistent."""


@dataclass(frozen=True, slots=True)
class TimedReceptorDelivery:
    completion_tick: int
    contact: float
    source_window_seconds: float | None = None
    source_advance_seconds: float | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.completion_tick, bool)
            or not isinstance(self.completion_tick, int)
            or self.completion_tick < 0
        ):
            raise ReceptorDeliveryModelProbeError(
                "completion_tick must be a non-negative integer"
            )
        contact = float(self.contact)
        if not math.isfinite(contact) or abs(contact) > 1.0:
            raise ReceptorDeliveryModelProbeError(
                "contact must remain in the normalized receptor domain"
            )
        object.__setattr__(self, "contact", contact)
        for role in ("source_window_seconds", "source_advance_seconds"):
            value = getattr(self, role)
            if value is None:
                continue
            numeric = float(value)
            if not math.isfinite(numeric) or numeric <= 0.0:
                raise ReceptorDeliveryModelProbeError(
                    f"{role} must be finite and positive when known"
                )
            object.__setattr__(self, role, numeric)


@dataclass(frozen=True, slots=True)
class ReceptorDeliveryRepresentation:
    representation_id: str
    horizon_end_tick: int
    tick_seconds: float
    deliveries: tuple[TimedReceptorDelivery, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.representation_id, str) or not self.representation_id:
            raise ReceptorDeliveryModelProbeError(
                "representation_id must not be empty"
            )
        if (
            isinstance(self.horizon_end_tick, bool)
            or not isinstance(self.horizon_end_tick, int)
            or self.horizon_end_tick <= 0
        ):
            raise ReceptorDeliveryModelProbeError(
                "horizon_end_tick must be a positive integer"
            )
        tick_seconds = float(self.tick_seconds)
        if not math.isfinite(tick_seconds) or tick_seconds <= 0.0:
            raise ReceptorDeliveryModelProbeError(
                "tick_seconds must be finite and positive"
            )
        deliveries = tuple(self.deliveries)
        if not deliveries or any(
            not isinstance(item, TimedReceptorDelivery) for item in deliveries
        ):
            raise ReceptorDeliveryModelProbeError(
                "representation requires timed receptor deliveries"
            )
        ticks = tuple(item.completion_tick for item in deliveries)
        if ticks[0] != 0 or ticks[-1] >= self.horizon_end_tick or any(
            later <= earlier for earlier, later in zip(ticks, ticks[1:])
        ):
            raise ReceptorDeliveryModelProbeError(
                "deliveries must increase strictly from tick zero inside the horizon"
            )
        object.__setattr__(self, "tick_seconds", tick_seconds)
        object.__setattr__(self, "deliveries", deliveries)


@dataclass(frozen=True, slots=True)
class DeliveryModelTotals:
    representation_id: str
    delivery_count: int
    point_event_total: float
    hold_integral: float
    source_window_total: float | None
    source_advance_total: float | None


@dataclass(frozen=True, slots=True)
class DeliveryModelComparison:
    family_id: str
    dense: DeliveryModelTotals
    sparse: DeliveryModelTotals
    point_event_difference: float
    hold_integral_difference: float
    source_window_difference: float | None
    source_advance_difference: float | None


@dataclass(frozen=True, slots=True)
class ReceptorDeliveryModelProbeResult:
    known_audio_support: DeliveryModelComparison
    unknown_video_support: DeliveryModelComparison


def _optional_weighted_total(
    deliveries: tuple[TimedReceptorDelivery, ...],
    role: str,
) -> float | None:
    weights = tuple(getattr(item, role) for item in deliveries)
    if any(weight is None for weight in weights):
        return None
    return sum(
        item.contact * float(weight)
        for item, weight in zip(deliveries, weights, strict=True)
    )


def delivery_model_totals(
    representation: ReceptorDeliveryRepresentation,
) -> DeliveryModelTotals:
    """Calculate four explicit input measures without selecting one."""

    if not isinstance(representation, ReceptorDeliveryRepresentation):
        raise ReceptorDeliveryModelProbeError(
            "delivery model requires one receptor representation"
        )
    deliveries = representation.deliveries
    boundaries = tuple(item.completion_tick for item in deliveries[1:]) + (
        representation.horizon_end_tick,
    )
    hold_integral = sum(
        item.contact
        * (boundary - item.completion_tick)
        * representation.tick_seconds
        for item, boundary in zip(deliveries, boundaries, strict=True)
    )
    return DeliveryModelTotals(
        representation_id=representation.representation_id,
        delivery_count=len(deliveries),
        point_event_total=sum(item.contact for item in deliveries),
        hold_integral=hold_integral,
        source_window_total=_optional_weighted_total(
            deliveries, "source_window_seconds"
        ),
        source_advance_total=_optional_weighted_total(
            deliveries, "source_advance_seconds"
        ),
    )


def compare_delivery_models(
    family_id: str,
    dense: ReceptorDeliveryRepresentation,
    sparse: ReceptorDeliveryRepresentation,
) -> DeliveryModelComparison:
    """Compare equal histories represented at two technical delivery rates."""

    if not family_id:
        raise ReceptorDeliveryModelProbeError("family_id must not be empty")
    if (
        dense.horizon_end_tick != sparse.horizon_end_tick
        or dense.tick_seconds != sparse.tick_seconds
    ):
        raise ReceptorDeliveryModelProbeError(
            "delivery representations must share one physical horizon"
        )
    left = delivery_model_totals(dense)
    right = delivery_model_totals(sparse)

    def difference(first: float | None, second: float | None) -> float | None:
        return None if first is None or second is None else abs(first - second)

    return DeliveryModelComparison(
        family_id=family_id,
        dense=left,
        sparse=right,
        point_event_difference=abs(left.point_event_total - right.point_event_total),
        hold_integral_difference=abs(left.hold_integral - right.hold_integral),
        source_window_difference=difference(
            left.source_window_total, right.source_window_total
        ),
        source_advance_difference=difference(
            left.source_advance_total, right.source_advance_total
        ),
    )


def _constant_representation(
    representation_id: str,
    *,
    step_ticks: int,
    source_window_seconds: float | None,
    source_advance_seconds: float | None,
) -> ReceptorDeliveryRepresentation:
    return ReceptorDeliveryRepresentation(
        representation_id=representation_id,
        horizon_end_tick=100,
        tick_seconds=0.01,
        deliveries=tuple(
            TimedReceptorDelivery(
                completion_tick=tick,
                contact=1.0,
                source_window_seconds=source_window_seconds,
                source_advance_seconds=source_advance_seconds,
            )
            for tick in range(0, 100, step_ticks)
        ),
    )


def run_receptor_delivery_model_probe() -> ReceptorDeliveryModelProbeResult:
    """Falsify candidate measures on one constant one-second contact."""

    audio_dense = _constant_representation(
        "audio.dense",
        step_ticks=1,
        source_window_seconds=0.1,
        source_advance_seconds=0.01,
    )
    audio_sparse = _constant_representation(
        "audio.sparse",
        step_ticks=5,
        source_window_seconds=0.1,
        source_advance_seconds=0.05,
    )
    video_dense = _constant_representation(
        "video.dense",
        step_ticks=1,
        source_window_seconds=None,
        source_advance_seconds=None,
    )
    video_sparse = _constant_representation(
        "video.sparse",
        step_ticks=5,
        source_window_seconds=None,
        source_advance_seconds=None,
    )
    return ReceptorDeliveryModelProbeResult(
        known_audio_support=compare_delivery_models(
            "known_audio_support", audio_dense, audio_sparse
        ),
        unknown_video_support=compare_delivery_models(
            "unknown_video_support", video_dense, video_sparse
        ),
    )


def receptor_delivery_model_probe_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            TimedReceptorDelivery,
            ReceptorDeliveryRepresentation,
            DeliveryModelTotals,
            DeliveryModelComparison,
            ReceptorDeliveryModelProbeResult,
        )
        for item in fields(contract)
    )
