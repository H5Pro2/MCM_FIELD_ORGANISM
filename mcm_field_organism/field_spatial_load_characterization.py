"""Spatial load and recovery characterization on the synthetic AV field."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math

from ._synthetic_av_field_fixture import (
    SYNTHETIC_AUDITORY_CARRIER_IDS,
    SYNTHETIC_VISUAL_CONFIG,
    run_synthetic_av_load_recovery,
)
from .shared_mcm_field import SharedMCMFieldSnapshot


FIELD_SPATIAL_LOAD_PATTERN_IDS = (
    "auditory_modality",
    "distributed_av",
    "local_auditory",
    "local_visual",
)
FIELD_SPATIAL_LOAD_DURATIONS_SECONDS = (0.1, 1.0, 4.0)
FIELD_SPATIAL_RECOVERY_DURATIONS_SECONDS = (0.0, 1.0, 4.0)
_SUPPORT_SECONDS = 0.1


class FieldSpatialLoadCharacterizationError(ValueError):
    """Raised when the fixed spatial matrix is incomplete."""


def _finite_nonnegative(value: object, role: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise FieldSpatialLoadCharacterizationError(
            f"{role} must be finite and non-negative"
        )
    return result


@dataclass(frozen=True, slots=True)
class FieldSpatialLoadObservation:
    pattern_id: str
    load_duration_seconds: float
    recovery_duration_seconds: float
    auditory_input_count: int
    visual_input_count: int
    stimulated_neuron_count: int
    field_neuron_count: int
    load_activation_l1: float
    load_activation_linf: float
    load_auditory_linf: float
    load_visual_linf: float
    load_stimulated_linf: float
    load_unstimulated_linf: float
    load_cross_modal_transfer_linf: float
    normalized_boundary_distance: float
    recovery_activation_linf: float
    recovery_auditory_linf: float
    recovery_visual_linf: float
    recovery_fraction_linf: float
    source_event_count: int
    normalized_boundary_reached: bool
    writes_back: bool = False
    adaptive_regulation_applied: bool = False

    def __post_init__(self) -> None:
        if self.pattern_id not in FIELD_SPATIAL_LOAD_PATTERN_IDS:
            raise FieldSpatialLoadCharacterizationError("unknown load pattern")
        if self.load_duration_seconds not in FIELD_SPATIAL_LOAD_DURATIONS_SECONDS:
            raise FieldSpatialLoadCharacterizationError("unknown load duration")
        if self.recovery_duration_seconds not in FIELD_SPATIAL_RECOVERY_DURATIONS_SECONDS:
            raise FieldSpatialLoadCharacterizationError("unknown recovery duration")
        expected_counts = {
            "auditory_modality": (8, 0, 8),
            "distributed_av": (8, 18, 26),
            "local_auditory": (1, 0, 1),
            "local_visual": (0, 1, 1),
        }[self.pattern_id]
        if (
            self.auditory_input_count,
            self.visual_input_count,
            self.stimulated_neuron_count,
        ) != expected_counts:
            raise FieldSpatialLoadCharacterizationError(
                "spatial input inventory changed"
            )
        if self.field_neuron_count != 26:
            raise FieldSpatialLoadCharacterizationError(
                "shared AV field neuron inventory changed"
            )
        for role in (
            "load_activation_l1",
            "load_activation_linf",
            "load_auditory_linf",
            "load_visual_linf",
            "load_stimulated_linf",
            "load_unstimulated_linf",
            "load_cross_modal_transfer_linf",
            "normalized_boundary_distance",
            "recovery_activation_linf",
            "recovery_auditory_linf",
            "recovery_visual_linf",
            "recovery_fraction_linf",
        ):
            object.__setattr__(self, role, _finite_nonnegative(getattr(self, role), role))
        if self.load_activation_linf > 1.0 or self.recovery_activation_linf > 1.0:
            raise FieldSpatialLoadCharacterizationError(
                "activation left the normalized field domain"
            )
        expected_distance = max(0.0, 1.0 - self.load_activation_linf)
        if self.normalized_boundary_distance != expected_distance:
            raise FieldSpatialLoadCharacterizationError(
                "boundary distance is inconsistent"
            )
        expected_fraction = self.recovery_activation_linf / self.load_activation_linf
        if not math.isclose(
            self.recovery_fraction_linf,
            expected_fraction,
            rel_tol=0.0,
            abs_tol=1e-15,
        ):
            raise FieldSpatialLoadCharacterizationError(
                "recovery fraction is inconsistent"
            )
        expected_events = 2 * round(
            (self.load_duration_seconds + self.recovery_duration_seconds)
            / _SUPPORT_SECONDS
        )
        if self.source_event_count != expected_events:
            raise FieldSpatialLoadCharacterizationError(
                "source event inventory is inconsistent"
            )
        if self.normalized_boundary_reached != (self.load_activation_linf == 1.0):
            raise FieldSpatialLoadCharacterizationError(
                "boundary decision is inconsistent"
            )
        if self.writes_back or self.adaptive_regulation_applied:
            raise FieldSpatialLoadCharacterizationError(
                "spatial characterization cannot regulate the field"
            )


@dataclass(frozen=True, slots=True)
class FieldSpatialLoadCharacterization:
    observations: tuple[FieldSpatialLoadObservation, ...]
    pattern_ids: tuple[str, ...]
    minimum_boundary_pattern_id: str
    minimum_boundary_distance: float
    any_cross_modal_transfer_observed: bool
    all_recovery_nonincreasing: bool
    characterization_decision: str
    writes_back: bool = False
    adaptive_regulation_applied: bool = False

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        expected_keys = {
            (pattern_id, load_duration, recovery_duration)
            for pattern_id in FIELD_SPATIAL_LOAD_PATTERN_IDS
            for load_duration in FIELD_SPATIAL_LOAD_DURATIONS_SECONDS
            for recovery_duration in FIELD_SPATIAL_RECOVERY_DURATIONS_SECONDS
        }
        actual_keys = {
            (
                item.pattern_id,
                item.load_duration_seconds,
                item.recovery_duration_seconds,
            )
            for item in observations
        }
        if len(observations) != len(expected_keys) or actual_keys != expected_keys:
            raise FieldSpatialLoadCharacterizationError(
                "spatial characterization matrix is incomplete"
            )
        canonical = tuple(
            sorted(
                observations,
                key=lambda item: (
                    item.pattern_id,
                    item.load_duration_seconds,
                    item.recovery_duration_seconds,
                ),
            )
        )
        if observations != canonical:
            raise FieldSpatialLoadCharacterizationError(
                "spatial observations must use canonical order"
            )
        if tuple(self.pattern_ids) != FIELD_SPATIAL_LOAD_PATTERN_IDS:
            raise FieldSpatialLoadCharacterizationError("pattern inventory changed")
        loads = tuple(
            item for item in observations if item.recovery_duration_seconds == 0.0
        )
        minimum = min(loads, key=lambda item: item.normalized_boundary_distance)
        if (
            self.minimum_boundary_pattern_id != minimum.pattern_id
            or self.minimum_boundary_distance != minimum.normalized_boundary_distance
        ):
            raise FieldSpatialLoadCharacterizationError(
                "minimum boundary summary is inconsistent"
            )
        cross_modal = any(
            item.load_cross_modal_transfer_linf > 0.0 for item in loads
        )
        if self.any_cross_modal_transfer_observed != cross_modal:
            raise FieldSpatialLoadCharacterizationError(
                "cross-modal summary is inconsistent"
            )
        recovery_nonincreasing = _recovery_nonincreasing(observations)
        if self.all_recovery_nonincreasing != recovery_nonincreasing:
            raise FieldSpatialLoadCharacterizationError(
                "recovery summary is inconsistent"
            )
        if self.characterization_decision != "SPATIAL_LOAD_SPREAD_CHARACTERIZED":
            raise FieldSpatialLoadCharacterizationError(
                "spatial characterization decision changed"
            )
        if self.writes_back or self.adaptive_regulation_applied:
            raise FieldSpatialLoadCharacterizationError(
                "spatial result cannot release regulation"
            )
        object.__setattr__(self, "observations", observations)

    @property
    def observation_count(self) -> int:
        return len(self.observations)


def _pattern_values(
    pattern_id: str,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    auditory = [0.0] * len(SYNTHETIC_AUDITORY_CARRIER_IDS)
    visual = [0.0] * len(SYNTHETIC_VISUAL_CONFIG.carrier_ids)
    if pattern_id == "local_auditory":
        auditory[4] = 1.0
    elif pattern_id == "auditory_modality":
        auditory = [1.0] * len(auditory)
    elif pattern_id == "local_visual":
        visual[4] = 1.0
    elif pattern_id == "distributed_av":
        auditory = [1.0] * len(auditory)
        visual = [1.0] * len(visual)
    else:
        raise FieldSpatialLoadCharacterizationError("unknown load pattern")
    return tuple(auditory), tuple(visual)


def _stimulated_neuron_ids(
    pattern_id: str,
    snapshot: SharedMCMFieldSnapshot,
) -> frozenset[str]:
    auditory_values, visual_values = _pattern_values(pattern_id)
    result = {
        f"organism.mcm_field.auditory.n{index}"
        for index, value in enumerate(auditory_values)
        if value != 0.0
    }
    result.update(
        f"organism.mcm_field.visual.n{index}"
        for index, value in enumerate(visual_values)
        if value != 0.0
    )
    if not result.issubset(snapshot.neuron_ids):
        raise FieldSpatialLoadCharacterizationError(
            "stimulated neuron identities differ from shared field"
        )
    return frozenset(result)


def _max_for_ids(
    snapshot: SharedMCMFieldSnapshot,
    neuron_ids: frozenset[str],
) -> float:
    return max(
        (
            abs(value)
            for neuron_id, value in zip(
                snapshot.neuron_ids,
                snapshot.activation,
                strict=True,
            )
            if neuron_id in neuron_ids
        ),
        default=0.0,
    )


def _modality_ids(
    snapshot: SharedMCMFieldSnapshot,
    modality_id: str,
) -> frozenset[str]:
    marker = f".{modality_id}."
    return frozenset(
        neuron_id for neuron_id in snapshot.neuron_ids if marker in neuron_id
    )


def _run_observation(
    pattern_id: str,
    load_duration: float,
    recovery_duration: float,
) -> FieldSpatialLoadObservation:
    auditory_values, visual_values = _pattern_values(pattern_id)
    load_snapshot, recovery_snapshot, source_event_count = (
        run_synthetic_av_load_recovery(
            "spatial",
            auditory_values,
            visual_values,
            load_duration,
            recovery_duration,
            support_seconds=_SUPPORT_SECONDS,
        )
    )
    stimulated = _stimulated_neuron_ids(pattern_id, load_snapshot)
    all_ids = frozenset(load_snapshot.neuron_ids)
    unstimulated = all_ids - stimulated
    auditory_ids = _modality_ids(load_snapshot, "auditory")
    visual_ids = _modality_ids(load_snapshot, "visual")
    load_linf = _max_for_ids(load_snapshot, all_ids)
    recovery_linf = _max_for_ids(recovery_snapshot, all_ids)
    if pattern_id in {"local_auditory", "auditory_modality"}:
        cross_modal = _max_for_ids(load_snapshot, visual_ids)
    elif pattern_id == "local_visual":
        cross_modal = _max_for_ids(load_snapshot, auditory_ids)
    else:
        cross_modal = 0.0
    return FieldSpatialLoadObservation(
        pattern_id=pattern_id,
        load_duration_seconds=load_duration,
        recovery_duration_seconds=recovery_duration,
        auditory_input_count=sum(value != 0.0 for value in auditory_values),
        visual_input_count=sum(value != 0.0 for value in visual_values),
        stimulated_neuron_count=len(stimulated),
        field_neuron_count=len(all_ids),
        load_activation_l1=math.fsum(abs(value) for value in load_snapshot.activation),
        load_activation_linf=load_linf,
        load_auditory_linf=_max_for_ids(load_snapshot, auditory_ids),
        load_visual_linf=_max_for_ids(load_snapshot, visual_ids),
        load_stimulated_linf=_max_for_ids(load_snapshot, stimulated),
        load_unstimulated_linf=_max_for_ids(load_snapshot, unstimulated),
        load_cross_modal_transfer_linf=cross_modal,
        normalized_boundary_distance=max(0.0, 1.0 - load_linf),
        recovery_activation_linf=recovery_linf,
        recovery_auditory_linf=_max_for_ids(recovery_snapshot, auditory_ids),
        recovery_visual_linf=_max_for_ids(recovery_snapshot, visual_ids),
        recovery_fraction_linf=recovery_linf / load_linf,
        source_event_count=source_event_count,
        normalized_boundary_reached=load_linf == 1.0,
    )


def _recovery_nonincreasing(
    observations: tuple[FieldSpatialLoadObservation, ...],
) -> bool:
    for pattern_id in FIELD_SPATIAL_LOAD_PATTERN_IDS:
        for load_duration in FIELD_SPATIAL_LOAD_DURATIONS_SECONDS:
            values = tuple(
                item.recovery_activation_linf
                for item in observations
                if item.pattern_id == pattern_id
                and item.load_duration_seconds == load_duration
            )
            if any(later > earlier for earlier, later in zip(values, values[1:])):
                return False
    return True


def run_field_spatial_load_characterization() -> FieldSpatialLoadCharacterization:
    """Run the fixed spatial matrix without changing sensitivity."""

    observations = tuple(
        _run_observation(pattern_id, load_duration, recovery_duration)
        for pattern_id in FIELD_SPATIAL_LOAD_PATTERN_IDS
        for load_duration in FIELD_SPATIAL_LOAD_DURATIONS_SECONDS
        for recovery_duration in FIELD_SPATIAL_RECOVERY_DURATIONS_SECONDS
    )
    loads = tuple(
        item for item in observations if item.recovery_duration_seconds == 0.0
    )
    minimum = min(loads, key=lambda item: item.normalized_boundary_distance)
    return FieldSpatialLoadCharacterization(
        observations=observations,
        pattern_ids=FIELD_SPATIAL_LOAD_PATTERN_IDS,
        minimum_boundary_pattern_id=minimum.pattern_id,
        minimum_boundary_distance=minimum.normalized_boundary_distance,
        any_cross_modal_transfer_observed=any(
            item.load_cross_modal_transfer_linf > 0.0 for item in loads
        ),
        all_recovery_nonincreasing=_recovery_nonincreasing(observations),
        characterization_decision="SPATIAL_LOAD_SPREAD_CHARACTERIZED",
    )


def field_spatial_load_characterization_json_value(
    result: FieldSpatialLoadCharacterization,
) -> dict[str, object]:
    if not isinstance(result, FieldSpatialLoadCharacterization):
        raise FieldSpatialLoadCharacterizationError(
            "JSON projection requires a spatial characterization result"
        )
    return asdict(result)


def field_spatial_load_characterization_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            FieldSpatialLoadObservation,
            FieldSpatialLoadCharacterization,
        )
        for item in fields(contract)
    )
