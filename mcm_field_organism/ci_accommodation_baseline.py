"""Bounded local C_i accommodation baseline without semantic or memory roles."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .shared_mcm_field import SharedMCMFieldSnapshot


class CIAccommodationBaselineError(ValueError):
    """Raised when the technical C_i baseline leaves its declared domain."""


@dataclass(frozen=True, slots=True)
class CIAccommodationConfig:
    """Fixed engineering parameters for one bounded C_i baseline arm."""

    alpha: float
    beta: float

    def __post_init__(self) -> None:
        for role in ("alpha", "beta"):
            value = getattr(self, role)
            if isinstance(value, bool) or not math.isfinite(float(value)) or value < 0.0:
                raise CIAccommodationBaselineError(
                    f"{role} must be finite and non-negative"
                )


@dataclass(frozen=True, slots=True)
class CIState:
    """Bounded local dispositions with technical identities only."""

    component_ids: tuple[str, ...]
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        component_ids = tuple(self.component_ids)
        values = tuple(float(value) for value in self.values)
        if not component_ids or len(component_ids) != len(values):
            raise CIAccommodationBaselineError(
                "C_i state requires matching non-empty component arrays"
            )
        if len(set(component_ids)) != len(component_ids) or any(
            not isinstance(item, str) or not item for item in component_ids
        ):
            raise CIAccommodationBaselineError("C_i component ids must be unique")
        if any(not math.isfinite(value) or not -1.0 <= value <= 1.0 for value in values):
            raise CIAccommodationBaselineError("C_i values must stay within [-1, 1]")
        object.__setattr__(self, "component_ids", component_ids)
        object.__setattr__(self, "values", values)


@dataclass(frozen=True, slots=True)
class CIAdvanceResult:
    """One passive C_i baseline step and its conjugate technical response."""

    state: CIState
    exchange: tuple[float, ...]
    backreaction: tuple[float, ...]


def advance_ci_accommodation(
    state: CIState,
    exposure: tuple[float, ...],
    config: CIAccommodationConfig,
    dt: float,
) -> CIAdvanceResult:
    """Advance C_i once without storing raw input or semantic metadata."""

    if not isinstance(state, CIState):
        raise CIAccommodationBaselineError("state must be one CIState")
    if not isinstance(config, CIAccommodationConfig):
        raise CIAccommodationBaselineError("config must be one CIAccommodationConfig")
    if isinstance(dt, bool) or not math.isfinite(float(dt)) or dt <= 0.0:
        raise CIAccommodationBaselineError("dt must be finite and positive")
    if config.alpha * dt > 0.25:
        raise CIAccommodationBaselineError(
            "dt is too large for the bounded explicit C_i baseline step"
        )
    exposure = tuple(float(value) for value in exposure)
    if len(exposure) != len(state.values) or any(
        not math.isfinite(value) or not -1.0 <= value <= 1.0 for value in exposure
    ):
        raise CIAccommodationBaselineError(
            "exposure must match C_i and stay within [-1, 1]"
        )

    exchange = tuple(
        config.alpha * (1.0 - value * value) * (incoming - value)
        for value, incoming in zip(state.values, exposure, strict=True)
    )
    next_values = tuple(
        value + dt * delta
        for value, delta in zip(state.values, exchange, strict=True)
    )
    if any(not -1.0 <= value <= 1.0 for value in next_values):
        raise CIAccommodationBaselineError("bounded C_i step left the declared domain")
    return CIAdvanceResult(
        state=CIState(state.component_ids, next_values),
        exchange=exchange,
        backreaction=tuple(-config.beta * delta for delta in exchange),
    )


def advance_ci_from_field_snapshot(
    snapshot: SharedMCMFieldSnapshot,
    state: CIState,
    config: CIAccommodationConfig,
    dt: float,
) -> CIAdvanceResult:
    """Use only current activation values as technical C_i exposure input."""

    if not isinstance(snapshot, SharedMCMFieldSnapshot):
        raise CIAccommodationBaselineError(
            "snapshot must be one shared field snapshot"
        )
    neuron_ids = tuple(neuron.neuron_id for neuron in snapshot.layer.neurons)
    if neuron_ids != state.component_ids:
        raise CIAccommodationBaselineError(
            "snapshot neurons and C_i components must match"
        )
    exposure = tuple(neuron.activation for neuron in snapshot.layer.neurons)
    return advance_ci_accommodation(state, exposure, config, dt)


def advance_ci_null_exposure(
    state: CIState,
    config: CIAccommodationConfig,
    dt: float,
) -> CIAdvanceResult:
    """Advance C_i in the passive-null arm with explicit E_i equal to zero."""

    if not isinstance(state, CIState):
        raise CIAccommodationBaselineError(
            "null exposure requires one complete C_i state"
        )
    return advance_ci_accommodation(
        state,
        tuple(0.0 for _ in state.component_ids),
        config,
        dt,
    )


def apply_ci_backreaction(
    activation: tuple[float, ...],
    advance: CIAdvanceResult,
    dt: float,
) -> tuple[float, ...]:
    """Project one technical C_i backreaction onto a fast activation vector."""

    if not isinstance(advance, CIAdvanceResult):
        raise CIAccommodationBaselineError("advance must be one CIAdvanceResult")
    if isinstance(dt, bool) or not math.isfinite(float(dt)) or dt <= 0.0:
        raise CIAccommodationBaselineError("dt must be finite and positive")
    activation = tuple(float(value) for value in activation)
    if len(activation) != len(advance.backreaction) or any(
        not math.isfinite(value) for value in activation
    ):
        raise CIAccommodationBaselineError(
            "activation and C_i backreaction must have matching finite values"
        )
    projected = tuple(
        value + dt * response
        for value, response in zip(activation, advance.backreaction, strict=True)
    )
    if any(not math.isfinite(value) for value in projected):
        raise CIAccommodationBaselineError("C_i backreaction produced a non-finite value")
    return projected


__all__ = (
    "CIAccommodationBaselineError",
    "CIAccommodationConfig",
    "CIState",
    "CIAdvanceResult",
    "advance_ci_accommodation",
    "advance_ci_from_field_snapshot",
    "advance_ci_null_exposure",
    "apply_ci_backreaction",
)
