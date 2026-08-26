"""Synthetic load and recovery characterization of the unchanged AV field."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math
from typing import Iterable

from ._synthetic_av_field_fixture import (
    SYNTHETIC_AUDITORY_CARRIER_IDS,
    SYNTHETIC_AV_CLOCK_ID,
    SYNTHETIC_AV_TICKS_PER_SECOND,
    SYNTHETIC_VISUAL_CONFIG,
    build_synthetic_av_field,
    synthetic_av_sequences,
)
from .field_step_time import MCMFieldStepTime
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)


FIELD_LOAD_BASELINE_IDS = (
    "fixed_gain_0_5",
    "fixed_leaky_1_0",
    "static_clip_0_5",
    "unmodified",
)
FIELD_LOAD_AMPLITUDES = (0.25, 0.5, 1.0)
FIELD_LOAD_DURATIONS_SECONDS = (0.1, 1.0, 4.0)
FIELD_RECOVERY_DURATIONS_SECONDS = (0.0, 0.1, 1.0, 4.0)

class FieldLoadRecoveryCharacterizationError(ValueError):
    """Raised when the fixed characterization matrix is incomplete."""


def _finite_nonnegative(value: object, role: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise FieldLoadRecoveryCharacterizationError(
            f"{role} must be finite and non-negative"
        )
    return result


@dataclass(frozen=True, slots=True)
class FieldLoadRecoveryObservation:
    baseline_id: str
    input_amplitude: float
    applied_amplitude: float
    load_duration_seconds: float
    recovery_duration_seconds: float
    load_activation_l1: float
    load_activation_linf: float
    load_afterimage_linf: float
    normalized_boundary_distance: float
    recovery_activation_l1: float
    recovery_activation_linf: float
    recovery_afterimage_linf: float
    recovery_fraction_linf: float
    field_neuron_count: int
    source_event_count: int
    normalized_boundary_reached: bool
    writes_back: bool = False
    adaptive_regulation_applied: bool = False

    def __post_init__(self) -> None:
        if self.baseline_id not in FIELD_LOAD_BASELINE_IDS:
            raise FieldLoadRecoveryCharacterizationError("unknown baseline")
        for role in (
            "input_amplitude",
            "applied_amplitude",
            "load_duration_seconds",
            "recovery_duration_seconds",
            "load_activation_l1",
            "load_activation_linf",
            "load_afterimage_linf",
            "normalized_boundary_distance",
            "recovery_activation_l1",
            "recovery_activation_linf",
            "recovery_afterimage_linf",
            "recovery_fraction_linf",
        ):
            object.__setattr__(self, role, _finite_nonnegative(getattr(self, role), role))
        if self.input_amplitude not in FIELD_LOAD_AMPLITUDES:
            raise FieldLoadRecoveryCharacterizationError("unknown input amplitude")
        if self.load_duration_seconds not in FIELD_LOAD_DURATIONS_SECONDS:
            raise FieldLoadRecoveryCharacterizationError("unknown load duration")
        if self.recovery_duration_seconds not in FIELD_RECOVERY_DURATIONS_SECONDS:
            raise FieldLoadRecoveryCharacterizationError("unknown recovery duration")
        expected_applied = _applied_amplitude(
            self.baseline_id,
            self.input_amplitude,
        )
        if self.applied_amplitude != expected_applied:
            raise FieldLoadRecoveryCharacterizationError(
                "applied amplitude differs from fixed baseline"
            )
        if self.load_activation_linf > 1.0 or self.recovery_activation_linf > 1.0:
            raise FieldLoadRecoveryCharacterizationError(
                "activation left the normalized field domain"
            )
        expected_distance = max(0.0, 1.0 - self.load_activation_linf)
        if self.normalized_boundary_distance != expected_distance:
            raise FieldLoadRecoveryCharacterizationError(
                "normalized boundary distance is inconsistent"
            )
        expected_fraction = self.recovery_activation_linf / self.load_activation_linf
        if not math.isclose(
            self.recovery_fraction_linf,
            expected_fraction,
            rel_tol=0.0,
            abs_tol=1e-15,
        ):
            raise FieldLoadRecoveryCharacterizationError(
                "recovery fraction is inconsistent"
            )
        expected_events = 2 if self.recovery_duration_seconds == 0.0 else 4
        if self.field_neuron_count != 26:
            raise FieldLoadRecoveryCharacterizationError(
                "shared AV field neuron inventory changed"
            )
        if self.source_event_count != expected_events:
            raise FieldLoadRecoveryCharacterizationError(
                "source event inventory is inconsistent"
            )
        if self.normalized_boundary_reached != (self.load_activation_linf == 1.0):
            raise FieldLoadRecoveryCharacterizationError(
                "boundary decision is inconsistent"
            )
        if self.writes_back or self.adaptive_regulation_applied:
            raise FieldLoadRecoveryCharacterizationError(
                "passive characterization cannot regulate the field"
            )


@dataclass(frozen=True, slots=True)
class FieldLoadRecoveryCharacterization:
    observations: tuple[FieldLoadRecoveryObservation, ...]
    unmodified_min_boundary_distance: float
    unmodified_boundary_reached: bool
    unmodified_recovery_nonincreasing: bool
    baseline_ids: tuple[str, ...]
    characterization_decision: str
    writes_back: bool = False
    adaptive_regulation_applied: bool = False

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        expected_keys = {
            (baseline_id, amplitude, load_duration, recovery_duration)
            for baseline_id in FIELD_LOAD_BASELINE_IDS
            for amplitude in FIELD_LOAD_AMPLITUDES
            for load_duration in FIELD_LOAD_DURATIONS_SECONDS
            for recovery_duration in FIELD_RECOVERY_DURATIONS_SECONDS
        }
        actual_keys = {
            (
                item.baseline_id,
                item.input_amplitude,
                item.load_duration_seconds,
                item.recovery_duration_seconds,
            )
            for item in observations
        }
        if len(observations) != len(expected_keys) or actual_keys != expected_keys:
            raise FieldLoadRecoveryCharacterizationError(
                "characterization matrix is incomplete"
            )
        canonical = tuple(
            sorted(
                observations,
                key=lambda item: (
                    item.baseline_id,
                    item.input_amplitude,
                    item.load_duration_seconds,
                    item.recovery_duration_seconds,
                ),
            )
        )
        if observations != canonical:
            raise FieldLoadRecoveryCharacterizationError(
                "observations must use canonical order"
            )
        unmodified = tuple(
            item for item in observations if item.baseline_id == "unmodified"
        )
        minimum_distance = min(item.normalized_boundary_distance for item in unmodified)
        boundary_reached = any(item.normalized_boundary_reached for item in unmodified)
        recovery_nonincreasing = _recovery_nonincreasing(unmodified)
        if self.unmodified_min_boundary_distance != minimum_distance:
            raise FieldLoadRecoveryCharacterizationError(
                "minimum boundary distance is inconsistent"
            )
        if self.unmodified_boundary_reached != boundary_reached:
            raise FieldLoadRecoveryCharacterizationError(
                "boundary summary is inconsistent"
            )
        if self.unmodified_recovery_nonincreasing != recovery_nonincreasing:
            raise FieldLoadRecoveryCharacterizationError(
                "recovery summary is inconsistent"
            )
        if tuple(self.baseline_ids) != FIELD_LOAD_BASELINE_IDS:
            raise FieldLoadRecoveryCharacterizationError("baseline inventory changed")
        expected_decision = (
            "NORMALIZED_BOUNDARY_REACHED_IN_BOUND_MATRIX"
            if boundary_reached
            else "NORMALIZED_BOUNDARY_NOT_REACHED_IN_BOUND_MATRIX"
        )
        if self.characterization_decision != expected_decision:
            raise FieldLoadRecoveryCharacterizationError(
                "characterization decision is inconsistent"
            )
        if self.writes_back or self.adaptive_regulation_applied:
            raise FieldLoadRecoveryCharacterizationError(
                "characterization result cannot release regulation"
            )
        object.__setattr__(self, "observations", observations)

    @property
    def observation_count(self) -> int:
        return len(self.observations)


def _applied_amplitude(baseline_id: str, amplitude: float) -> float:
    if baseline_id == "fixed_gain_0_5":
        return amplitude * 0.5
    if baseline_id == "static_clip_0_5":
        return min(amplitude, 0.5)
    return amplitude


def _linf(values: Iterable[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def _l1(values: Iterable[float]) -> float:
    return math.fsum(abs(value) for value in values)


def _run_observation(
    baseline_id: str,
    amplitude: float,
    load_duration: float,
    recovery_duration: float,
) -> FieldLoadRecoveryObservation:
    applied = _applied_amplitude(baseline_id, amplitude)
    load_end = round(load_duration * SYNTHETIC_AV_TICKS_PER_SECOND)
    load_sequences = synthetic_av_sequences(
        "load",
        0,
        load_end,
        tuple(applied for _ in SYNTHETIC_AUDITORY_CARRIER_IDS),
        tuple(applied for _ in SYNTHETIC_VISUAL_CONFIG.carrier_ids),
    )
    field = build_synthetic_av_field(load_sequences)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = None
    dissipation = None
    if baseline_id == "fixed_leaky_1_0":
        afterimage = NeutralFastAfterimageConfig(1.0)
        dissipation = NeutralFieldDissipationConfig(1.0)
    load = run_neutral_asynchronous_field(
        field,
        load_sequences,
        (
            MCMFieldStepTime(
                SYNTHETIC_AV_CLOCK_ID,
                0,
                load_end,
                SYNTHETIC_AV_TICKS_PER_SECOND,
            ),
        ),
        substrate,
        afterimage_config=afterimage,
        dissipation_config=dissipation,
    )
    load_snapshot = load.field.snapshot()
    recovered_field = load.field
    source_event_count = load.handoff.assigned_event_count
    if recovery_duration > 0.0:
        recovery_end = load_end + round(
            recovery_duration * SYNTHETIC_AV_TICKS_PER_SECOND
        )
        recovery_sequences = synthetic_av_sequences(
            "recovery",
            load_end,
            recovery_end,
            tuple(0.0 for _ in SYNTHETIC_AUDITORY_CARRIER_IDS),
            tuple(0.0 for _ in SYNTHETIC_VISUAL_CONFIG.carrier_ids),
        )
        recovery = run_neutral_asynchronous_field(
            recovered_field,
            recovery_sequences,
            (
                MCMFieldStepTime(
                    SYNTHETIC_AV_CLOCK_ID,
                    load_end,
                    recovery_end,
                    SYNTHETIC_AV_TICKS_PER_SECOND,
                ),
            ),
            substrate,
            afterimage_config=afterimage,
            dissipation_config=dissipation,
        )
        recovered_field = recovery.field
        source_event_count += recovery.handoff.assigned_event_count
    recovery_snapshot = recovered_field.snapshot()
    load_linf = _linf(load_snapshot.activation)
    recovery_linf = _linf(recovery_snapshot.activation)
    return FieldLoadRecoveryObservation(
        baseline_id=baseline_id,
        input_amplitude=amplitude,
        applied_amplitude=applied,
        load_duration_seconds=load_duration,
        recovery_duration_seconds=recovery_duration,
        load_activation_l1=_l1(load_snapshot.activation),
        load_activation_linf=load_linf,
        load_afterimage_linf=_linf(load_snapshot.afterimage),
        normalized_boundary_distance=max(0.0, 1.0 - load_linf),
        recovery_activation_l1=_l1(recovery_snapshot.activation),
        recovery_activation_linf=recovery_linf,
        recovery_afterimage_linf=_linf(recovery_snapshot.afterimage),
        recovery_fraction_linf=recovery_linf / load_linf,
        field_neuron_count=len(load_snapshot.neuron_ids),
        source_event_count=source_event_count,
        normalized_boundary_reached=load_linf == 1.0,
    )


def _recovery_nonincreasing(
    observations: tuple[FieldLoadRecoveryObservation, ...],
) -> bool:
    for amplitude in FIELD_LOAD_AMPLITUDES:
        for load_duration in FIELD_LOAD_DURATIONS_SECONDS:
            group = tuple(
                item
                for item in observations
                if item.input_amplitude == amplitude
                and item.load_duration_seconds == load_duration
            )
            ordered = tuple(
                item.recovery_activation_linf
                for item in sorted(
                    group,
                    key=lambda item: item.recovery_duration_seconds,
                )
            )
            if any(later > earlier for earlier, later in zip(ordered, ordered[1:])):
                return False
    return True


def run_field_load_recovery_characterization() -> FieldLoadRecoveryCharacterization:
    """Run the fixed synthetic matrix without adapting any runtime state."""

    observations = tuple(
        _run_observation(baseline_id, amplitude, load_duration, recovery_duration)
        for baseline_id in FIELD_LOAD_BASELINE_IDS
        for amplitude in FIELD_LOAD_AMPLITUDES
        for load_duration in FIELD_LOAD_DURATIONS_SECONDS
        for recovery_duration in FIELD_RECOVERY_DURATIONS_SECONDS
    )
    unmodified = tuple(
        item for item in observations if item.baseline_id == "unmodified"
    )
    boundary_reached = any(item.normalized_boundary_reached for item in unmodified)
    return FieldLoadRecoveryCharacterization(
        observations=observations,
        unmodified_min_boundary_distance=min(
            item.normalized_boundary_distance for item in unmodified
        ),
        unmodified_boundary_reached=boundary_reached,
        unmodified_recovery_nonincreasing=_recovery_nonincreasing(unmodified),
        baseline_ids=FIELD_LOAD_BASELINE_IDS,
        characterization_decision=(
            "NORMALIZED_BOUNDARY_REACHED_IN_BOUND_MATRIX"
            if boundary_reached
            else "NORMALIZED_BOUNDARY_NOT_REACHED_IN_BOUND_MATRIX"
        ),
    )


def field_load_recovery_characterization_json_value(
    result: FieldLoadRecoveryCharacterization,
) -> dict[str, object]:
    if not isinstance(result, FieldLoadRecoveryCharacterization):
        raise FieldLoadRecoveryCharacterizationError(
            "JSON projection requires a characterization result"
        )
    return asdict(result)


def field_load_recovery_characterization_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            FieldLoadRecoveryObservation,
            FieldLoadRecoveryCharacterization,
        )
        for item in fields(contract)
    )
