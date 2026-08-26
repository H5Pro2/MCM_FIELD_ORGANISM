"""Equal-contact-mass spatial counterbaseline on the synthetic AV field."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math

from ._synthetic_av_field_fixture import (
    SYNTHETIC_AUDITORY_CARRIER_IDS,
    SYNTHETIC_VISUAL_CONFIG,
    run_synthetic_av_load_recovery,
)
from .shared_mcm_field import SharedMCMFieldSnapshot


FIELD_CONTACT_MASS_PATTERN_IDS = (
    "auditory_distributed_mass1",
    "av_distributed_mass1",
    "local_auditory_mass1",
    "local_visual_mass1",
    "visual_distributed_mass1",
)
FIELD_CONTACT_MASS_LOAD_DURATIONS_SECONDS = (0.1, 1.0, 4.0)
FIELD_CONTACT_MASS_RECOVERY_DURATIONS_SECONDS = (0.0, 1.0, 4.0)
FIELD_CONTACT_MASS_TOTAL = 1.0
_SUPPORT_SECONDS = 0.1


class FieldContactMassCounterbaselineError(ValueError):
    """Raised when the equal-mass counterbaseline is incomplete."""


def _finite_nonnegative(value: object, role: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise FieldContactMassCounterbaselineError(
            f"{role} must be finite and non-negative"
        )
    return result


@dataclass(frozen=True, slots=True)
class FieldContactMassObservation:
    pattern_id: str
    load_duration_seconds: float
    recovery_duration_seconds: float
    auditory_input_count: int
    visual_input_count: int
    active_contact_count: int
    per_contact_amplitude: float
    total_contact_mass: float
    field_neuron_count: int
    load_activation_l1: float
    load_activation_linf: float
    load_auditory_linf: float
    load_visual_linf: float
    load_stimulated_linf: float
    load_unstimulated_linf: float
    normalized_boundary_distance: float
    recovery_activation_linf: float
    recovery_fraction_linf: float
    source_event_count: int
    normalized_boundary_reached: bool
    writes_back: bool = False
    adaptive_regulation_applied: bool = False

    def __post_init__(self) -> None:
        if self.pattern_id not in FIELD_CONTACT_MASS_PATTERN_IDS:
            raise FieldContactMassCounterbaselineError("unknown mass pattern")
        if self.load_duration_seconds not in FIELD_CONTACT_MASS_LOAD_DURATIONS_SECONDS:
            raise FieldContactMassCounterbaselineError("unknown load duration")
        if self.recovery_duration_seconds not in FIELD_CONTACT_MASS_RECOVERY_DURATIONS_SECONDS:
            raise FieldContactMassCounterbaselineError("unknown recovery duration")
        counts = {
            "auditory_distributed_mass1": (8, 0, 8),
            "av_distributed_mass1": (8, 18, 26),
            "local_auditory_mass1": (1, 0, 1),
            "local_visual_mass1": (0, 1, 1),
            "visual_distributed_mass1": (0, 18, 18),
        }[self.pattern_id]
        if (
            self.auditory_input_count,
            self.visual_input_count,
            self.active_contact_count,
        ) != counts:
            raise FieldContactMassCounterbaselineError(
                "equal-mass input inventory changed"
            )
        if self.field_neuron_count != 26:
            raise FieldContactMassCounterbaselineError(
                "shared AV field neuron inventory changed"
            )
        for role in (
            "per_contact_amplitude",
            "total_contact_mass",
            "load_activation_l1",
            "load_activation_linf",
            "load_auditory_linf",
            "load_visual_linf",
            "load_stimulated_linf",
            "load_unstimulated_linf",
            "normalized_boundary_distance",
            "recovery_activation_linf",
            "recovery_fraction_linf",
        ):
            object.__setattr__(self, role, _finite_nonnegative(getattr(self, role), role))
        expected_amplitude = 1.0 / self.active_contact_count
        if self.per_contact_amplitude != expected_amplitude:
            raise FieldContactMassCounterbaselineError(
                "per-contact amplitude is not mass matched"
            )
        if not math.isclose(
            self.total_contact_mass,
            FIELD_CONTACT_MASS_TOTAL,
            rel_tol=0.0,
            abs_tol=1e-15,
        ):
            raise FieldContactMassCounterbaselineError(
                "total contact mass differs from one"
            )
        if self.load_activation_linf > 1.0 or self.recovery_activation_linf > 1.0:
            raise FieldContactMassCounterbaselineError(
                "activation left the normalized field domain"
            )
        if self.normalized_boundary_distance != max(
            0.0,
            1.0 - self.load_activation_linf,
        ):
            raise FieldContactMassCounterbaselineError(
                "boundary distance is inconsistent"
            )
        if not math.isclose(
            self.recovery_fraction_linf,
            self.recovery_activation_linf / self.load_activation_linf,
            rel_tol=0.0,
            abs_tol=1e-15,
        ):
            raise FieldContactMassCounterbaselineError(
                "recovery fraction is inconsistent"
            )
        expected_events = 2 * round(
            (self.load_duration_seconds + self.recovery_duration_seconds)
            / _SUPPORT_SECONDS
        )
        if self.source_event_count != expected_events:
            raise FieldContactMassCounterbaselineError(
                "source event inventory is inconsistent"
            )
        if self.normalized_boundary_reached != (self.load_activation_linf == 1.0):
            raise FieldContactMassCounterbaselineError(
                "boundary decision is inconsistent"
            )
        if self.writes_back or self.adaptive_regulation_applied:
            raise FieldContactMassCounterbaselineError(
                "counterbaseline cannot regulate the field"
            )


@dataclass(frozen=True, slots=True)
class FieldContactMassCounterbaseline:
    observations: tuple[FieldContactMassObservation, ...]
    pattern_ids: tuple[str, ...]
    total_contact_mass: float
    long_load_highest_pattern_id: str
    long_load_highest_linf: float
    long_load_lowest_pattern_id: str
    long_load_lowest_linf: float
    all_recovery_nonincreasing: bool
    characterization_decision: str
    writes_back: bool = False
    adaptive_regulation_applied: bool = False

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        expected_keys = {
            (pattern_id, load_duration, recovery_duration)
            for pattern_id in FIELD_CONTACT_MASS_PATTERN_IDS
            for load_duration in FIELD_CONTACT_MASS_LOAD_DURATIONS_SECONDS
            for recovery_duration in FIELD_CONTACT_MASS_RECOVERY_DURATIONS_SECONDS
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
            raise FieldContactMassCounterbaselineError(
                "equal-mass matrix is incomplete"
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
            raise FieldContactMassCounterbaselineError(
                "equal-mass observations must use canonical order"
            )
        if tuple(self.pattern_ids) != FIELD_CONTACT_MASS_PATTERN_IDS:
            raise FieldContactMassCounterbaselineError("pattern inventory changed")
        if self.total_contact_mass != FIELD_CONTACT_MASS_TOTAL:
            raise FieldContactMassCounterbaselineError("mass summary changed")
        long_loads = tuple(
            item
            for item in observations
            if item.load_duration_seconds == 4.0
            and item.recovery_duration_seconds == 0.0
        )
        highest = max(long_loads, key=lambda item: item.load_activation_linf)
        lowest = min(long_loads, key=lambda item: item.load_activation_linf)
        if (
            self.long_load_highest_pattern_id != highest.pattern_id
            or self.long_load_highest_linf != highest.load_activation_linf
            or self.long_load_lowest_pattern_id != lowest.pattern_id
            or self.long_load_lowest_linf != lowest.load_activation_linf
        ):
            raise FieldContactMassCounterbaselineError(
                "long-load summary is inconsistent"
            )
        recovery_nonincreasing = _recovery_nonincreasing(observations)
        if self.all_recovery_nonincreasing != recovery_nonincreasing:
            raise FieldContactMassCounterbaselineError(
                "recovery summary is inconsistent"
            )
        difference = highest.load_activation_linf - lowest.load_activation_linf
        expected_decision = (
            "EQUAL_CONTACT_MASS_GEOMETRY_DIFFERENCE_OBSERVED"
            if difference > 1e-12
            else "EQUAL_CONTACT_MASS_GEOMETRY_INDIFFERENT"
        )
        if self.characterization_decision != expected_decision:
            raise FieldContactMassCounterbaselineError(
                "counterbaseline decision is inconsistent"
            )
        if self.writes_back or self.adaptive_regulation_applied:
            raise FieldContactMassCounterbaselineError(
                "counterbaseline cannot release regulation"
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
    if pattern_id == "local_auditory_mass1":
        auditory[4] = 1.0
    elif pattern_id == "local_visual_mass1":
        visual[4] = 1.0
    elif pattern_id == "auditory_distributed_mass1":
        auditory = [1.0 / len(auditory)] * len(auditory)
    elif pattern_id == "visual_distributed_mass1":
        visual = [1.0 / len(visual)] * len(visual)
    elif pattern_id == "av_distributed_mass1":
        value = 1.0 / (len(auditory) + len(visual))
        auditory = [value] * len(auditory)
        visual = [value] * len(visual)
    else:
        raise FieldContactMassCounterbaselineError("unknown mass pattern")
    return tuple(auditory), tuple(visual)


def _ids(snapshot: SharedMCMFieldSnapshot, modality_id: str) -> frozenset[str]:
    marker = f".{modality_id}."
    return frozenset(
        neuron_id for neuron_id in snapshot.neuron_ids if marker in neuron_id
    )


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


def _stimulated_ids(
    snapshot: SharedMCMFieldSnapshot,
    auditory_values: tuple[float, ...],
    visual_values: tuple[float, ...],
) -> frozenset[str]:
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
        raise FieldContactMassCounterbaselineError(
            "stimulated identities differ from shared field"
        )
    return frozenset(result)


def _run_observation(
    pattern_id: str,
    load_duration: float,
    recovery_duration: float,
) -> FieldContactMassObservation:
    auditory_values, visual_values = _pattern_values(pattern_id)
    load_snapshot, recovery_snapshot, source_event_count = (
        run_synthetic_av_load_recovery(
            "mass",
            auditory_values,
            visual_values,
            load_duration,
            recovery_duration,
            support_seconds=_SUPPORT_SECONDS,
        )
    )
    all_ids = frozenset(load_snapshot.neuron_ids)
    auditory_ids = _ids(load_snapshot, "auditory")
    visual_ids = _ids(load_snapshot, "visual")
    stimulated = _stimulated_ids(load_snapshot, auditory_values, visual_values)
    unstimulated = all_ids - stimulated
    load_linf = _max_for_ids(load_snapshot, all_ids)
    recovery_linf = _max_for_ids(recovery_snapshot, all_ids)
    active_count = len(stimulated)
    total_mass = math.fsum(abs(value) for value in auditory_values + visual_values)
    return FieldContactMassObservation(
        pattern_id=pattern_id,
        load_duration_seconds=load_duration,
        recovery_duration_seconds=recovery_duration,
        auditory_input_count=sum(value != 0.0 for value in auditory_values),
        visual_input_count=sum(value != 0.0 for value in visual_values),
        active_contact_count=active_count,
        per_contact_amplitude=1.0 / active_count,
        total_contact_mass=total_mass,
        field_neuron_count=len(all_ids),
        load_activation_l1=math.fsum(abs(value) for value in load_snapshot.activation),
        load_activation_linf=load_linf,
        load_auditory_linf=_max_for_ids(load_snapshot, auditory_ids),
        load_visual_linf=_max_for_ids(load_snapshot, visual_ids),
        load_stimulated_linf=_max_for_ids(load_snapshot, stimulated),
        load_unstimulated_linf=_max_for_ids(load_snapshot, unstimulated),
        normalized_boundary_distance=max(0.0, 1.0 - load_linf),
        recovery_activation_linf=recovery_linf,
        recovery_fraction_linf=recovery_linf / load_linf,
        source_event_count=source_event_count,
        normalized_boundary_reached=load_linf == 1.0,
    )


def _recovery_nonincreasing(
    observations: tuple[FieldContactMassObservation, ...],
) -> bool:
    for pattern_id in FIELD_CONTACT_MASS_PATTERN_IDS:
        for load_duration in FIELD_CONTACT_MASS_LOAD_DURATIONS_SECONDS:
            values = tuple(
                item.recovery_activation_linf
                for item in observations
                if item.pattern_id == pattern_id
                and item.load_duration_seconds == load_duration
            )
            if any(later > earlier for earlier, later in zip(values, values[1:])):
                return False
    return True


def run_field_contact_mass_counterbaseline() -> FieldContactMassCounterbaseline:
    """Run the fixed equal-mass matrix without sensitivity changes."""

    observations = tuple(
        _run_observation(pattern_id, load_duration, recovery_duration)
        for pattern_id in FIELD_CONTACT_MASS_PATTERN_IDS
        for load_duration in FIELD_CONTACT_MASS_LOAD_DURATIONS_SECONDS
        for recovery_duration in FIELD_CONTACT_MASS_RECOVERY_DURATIONS_SECONDS
    )
    long_loads = tuple(
        item
        for item in observations
        if item.load_duration_seconds == 4.0
        and item.recovery_duration_seconds == 0.0
    )
    highest = max(long_loads, key=lambda item: item.load_activation_linf)
    lowest = min(long_loads, key=lambda item: item.load_activation_linf)
    return FieldContactMassCounterbaseline(
        observations=observations,
        pattern_ids=FIELD_CONTACT_MASS_PATTERN_IDS,
        total_contact_mass=FIELD_CONTACT_MASS_TOTAL,
        long_load_highest_pattern_id=highest.pattern_id,
        long_load_highest_linf=highest.load_activation_linf,
        long_load_lowest_pattern_id=lowest.pattern_id,
        long_load_lowest_linf=lowest.load_activation_linf,
        all_recovery_nonincreasing=_recovery_nonincreasing(observations),
        characterization_decision=(
            "EQUAL_CONTACT_MASS_GEOMETRY_DIFFERENCE_OBSERVED"
            if highest.load_activation_linf - lowest.load_activation_linf > 1e-12
            else "EQUAL_CONTACT_MASS_GEOMETRY_INDIFFERENT"
        ),
    )


def field_contact_mass_counterbaseline_json_value(
    result: FieldContactMassCounterbaseline,
) -> dict[str, object]:
    if not isinstance(result, FieldContactMassCounterbaseline):
        raise FieldContactMassCounterbaselineError(
            "JSON projection requires an equal-mass result"
        )
    return asdict(result)


def field_contact_mass_counterbaseline_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (FieldContactMassObservation, FieldContactMassCounterbaseline)
        for item in fields(contract)
    )
