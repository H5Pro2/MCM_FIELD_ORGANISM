"""Technical event-density accounting on an invariant zero-contact AV field."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math
from statistics import median
import time

from ._synthetic_av_field_fixture import (
    SYNTHETIC_AUDITORY_CARRIER_IDS,
    SYNTHETIC_AV_CLOCK_ID,
    SYNTHETIC_AV_TICKS_PER_SECOND,
    SYNTHETIC_VISUAL_CONFIG,
    build_synthetic_av_field,
    synthetic_av_repeated_sequences,
)
from .field_step_time import MCMFieldStepTime
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import NeutralLocalFieldSubstrateConfig
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


FIELD_EVENT_DENSITY_IDS = (
    "density_10_hz_per_modality",
    "density_100_hz_per_modality",
    "density_1000_hz_per_modality",
)
FIELD_EVENT_DENSITY_SUPPORT_SECONDS = (0.1, 0.01, 0.001)
FIELD_EVENT_DENSITY_INPUT_AMPLITUDES = (0.0, 0.1)
FIELD_EVENT_DENSITY_DURATION_SECONDS = 1.0
FIELD_EVENT_DENSITY_REPETITIONS = 5


class FieldEventDensityResourceCharacterizationError(ValueError):
    """Raised when the fixed technical resource matrix is inconsistent."""


def _finite_nonnegative(value: object, role: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise FieldEventDensityResourceCharacterizationError(
            f"{role} must be finite and non-negative"
        )
    return result


@dataclass(frozen=True, slots=True)
class FieldEventDensityResourceObservation:
    density_id: str
    input_amplitude: float
    support_seconds: float
    duration_seconds: float
    repetitions: int
    support_count_per_modality: int
    source_event_count: int
    completion_group_count: int
    proposal_batch_count: int
    projected_local_contact_count: int
    field_neuron_count: int
    final_activation_l1: float
    final_activation_linf: float
    final_afterimage_linf: float
    reference_activation_delta_linf: float
    endpoint_digest: str
    repeated_endpoints_equal: bool
    runtime_seconds_min: float
    runtime_seconds_median: float
    runtime_seconds_max: float
    process_seconds_min: float
    process_seconds_median: float
    process_seconds_max: float
    writes_back: bool = False
    adaptive_regulation_applied: bool = False

    def __post_init__(self) -> None:
        if self.density_id not in FIELD_EVENT_DENSITY_IDS:
            raise FieldEventDensityResourceCharacterizationError(
                "unknown event density"
            )
        if self.input_amplitude not in FIELD_EVENT_DENSITY_INPUT_AMPLITUDES:
            raise FieldEventDensityResourceCharacterizationError(
                "unknown input amplitude"
            )
        index = FIELD_EVENT_DENSITY_IDS.index(self.density_id)
        if self.support_seconds != FIELD_EVENT_DENSITY_SUPPORT_SECONDS[index]:
            raise FieldEventDensityResourceCharacterizationError(
                "support differs from fixed density"
            )
        if (
            self.duration_seconds != FIELD_EVENT_DENSITY_DURATION_SECONDS
            or self.repetitions != FIELD_EVENT_DENSITY_REPETITIONS
        ):
            raise FieldEventDensityResourceCharacterizationError(
                "duration or repetition inventory changed"
            )
        expected_supports = round(self.duration_seconds / self.support_seconds)
        expected_events = 2 * expected_supports
        expected_contacts = expected_supports * (
            len(SYNTHETIC_AUDITORY_CARRIER_IDS)
            + len(SYNTHETIC_VISUAL_CONFIG.carrier_ids)
        )
        if (
            self.support_count_per_modality != expected_supports
            or self.source_event_count != expected_events
            or self.completion_group_count != expected_supports
            or self.proposal_batch_count != 1
            or self.projected_local_contact_count != expected_contacts
            or self.field_neuron_count != 26
        ):
            raise FieldEventDensityResourceCharacterizationError(
                "technical workload inventory is inconsistent"
            )
        for role in (
            "final_activation_l1",
            "final_activation_linf",
            "final_afterimage_linf",
            "reference_activation_delta_linf",
            "runtime_seconds_min",
            "runtime_seconds_median",
            "runtime_seconds_max",
            "process_seconds_min",
            "process_seconds_median",
            "process_seconds_max",
        ):
            object.__setattr__(self, role, _finite_nonnegative(getattr(self, role), role))
        if not (
            self.runtime_seconds_min
            <= self.runtime_seconds_median
            <= self.runtime_seconds_max
            and self.process_seconds_min
            <= self.process_seconds_median
            <= self.process_seconds_max
        ):
            raise FieldEventDensityResourceCharacterizationError(
                "runtime summaries are not ordered"
            )
        if not self.endpoint_digest or not self.repeated_endpoints_equal:
            raise FieldEventDensityResourceCharacterizationError(
                "technical repetitions must share one complete endpoint"
            )
        if self.writes_back or self.adaptive_regulation_applied:
            raise FieldEventDensityResourceCharacterizationError(
                "resource characterization cannot regulate the field"
            )


@dataclass(frozen=True, slots=True)
class FieldEventDensityResourceCharacterization:
    observations: tuple[FieldEventDensityResourceObservation, ...]
    density_ids: tuple[str, ...]
    duration_seconds: float
    repetitions_per_density: int
    source_event_growth_factor: float
    projected_contact_growth_factor: float
    zero_contact_endpoints_equal: bool
    active_contact_max_density_delta_linf: float
    active_contact_density_invariant: bool
    resource_limit_observed: bool
    characterization_decision: str
    writes_back: bool = False
    adaptive_regulation_applied: bool = False

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        expected_keys = tuple(
            (amplitude, density_id)
            for amplitude in FIELD_EVENT_DENSITY_INPUT_AMPLITUDES
            for density_id in FIELD_EVENT_DENSITY_IDS
        )
        actual_keys = tuple(
            (item.input_amplitude, item.density_id) for item in observations
        )
        if actual_keys != expected_keys or tuple(self.density_ids) != FIELD_EVENT_DENSITY_IDS:
            raise FieldEventDensityResourceCharacterizationError(
                "event density matrix is incomplete or unordered"
            )
        if (
            self.duration_seconds != FIELD_EVENT_DENSITY_DURATION_SECONDS
            or self.repetitions_per_density != FIELD_EVENT_DENSITY_REPETITIONS
        ):
            raise FieldEventDensityResourceCharacterizationError(
                "resource characterization inventory changed"
            )
        zero = tuple(item for item in observations if item.input_amplitude == 0.0)
        active = tuple(item for item in observations if item.input_amplitude == 0.1)
        first = zero[0]
        last = zero[-1]
        event_growth = last.source_event_count / first.source_event_count
        contact_growth = (
            last.projected_local_contact_count
            / first.projected_local_contact_count
        )
        zero_endpoints_equal = (
            len({item.endpoint_digest for item in zero}) == 1
            and all(
                item.final_activation_l1 == 0.0
                and item.final_activation_linf == 0.0
                and item.final_afterimage_linf == 0.0
                and item.reference_activation_delta_linf == 0.0
                for item in zero
            )
        )
        active_max_delta = max(
            item.reference_activation_delta_linf for item in active
        )
        active_invariant = active_max_delta <= 1e-12
        if (
            self.source_event_growth_factor != event_growth
            or self.projected_contact_growth_factor != contact_growth
            or self.zero_contact_endpoints_equal != zero_endpoints_equal
            or self.active_contact_max_density_delta_linf != active_max_delta
            or self.active_contact_density_invariant != active_invariant
        ):
            raise FieldEventDensityResourceCharacterizationError(
                "resource summary is inconsistent"
            )
        if self.resource_limit_observed:
            raise FieldEventDensityResourceCharacterizationError(
                "successful bounded matrix cannot claim a resource limit"
            )
        expected_decision = (
            "FIELD_ENDPOINT_INVARIANT_ACROSS_BOUND_EVENT_DENSITIES"
            if zero_endpoints_equal and active_invariant
            else "FIELD_ENDPOINT_DENSITY_DEPENDENCE_OBSERVED"
        )
        if self.characterization_decision != expected_decision:
            raise FieldEventDensityResourceCharacterizationError(
                "characterization decision is inconsistent"
            )
        if self.writes_back or self.adaptive_regulation_applied:
            raise FieldEventDensityResourceCharacterizationError(
                "resource characterization cannot release regulation"
            )
        object.__setattr__(self, "observations", observations)

    @property
    def observation_count(self) -> int:
        return len(self.observations)


def _run_density(
    density_id: str,
    support_seconds: float,
    input_amplitude: float,
    reference_activation: tuple[float, ...] | None,
) -> tuple[FieldEventDensityResourceObservation, tuple[float, ...]]:
    duration_ticks = round(
        FIELD_EVENT_DENSITY_DURATION_SECONDS * SYNTHETIC_AV_TICKS_PER_SECOND
    )
    support_ticks = round(support_seconds * SYNTHETIC_AV_TICKS_PER_SECOND)
    sequences = synthetic_av_repeated_sequences(
        density_id,
        0,
        duration_ticks,
        support_ticks,
        tuple(input_amplitude for _ in SYNTHETIC_AUDITORY_CARRIER_IDS),
        tuple(input_amplitude for _ in SYNTHETIC_VISUAL_CONFIG.carrier_ids),
    )
    step = MCMFieldStepTime(
        SYNTHETIC_AV_CLOCK_ID,
        0,
        duration_ticks,
        SYNTHETIC_AV_TICKS_PER_SECOND,
    )
    runtime_samples = []
    process_samples = []
    runs = []
    for _ in range(FIELD_EVENT_DENSITY_REPETITIONS):
        field = build_synthetic_av_field(sequences)
        process_start = time.process_time_ns()
        runtime_start = time.perf_counter_ns()
        run = run_neutral_asynchronous_field(
            field,
            sequences,
            (step,),
            NeutralLocalFieldSubstrateConfig(1.0),
        )
        runtime_samples.append((time.perf_counter_ns() - runtime_start) / 1e9)
        process_samples.append((time.process_time_ns() - process_start) / 1e9)
        runs.append(run)
    digests = tuple(run.field.snapshot().digest() for run in runs)
    reference = runs[0]
    snapshot = reference.field.snapshot()
    reference_delta = (
        0.0
        if reference_activation is None
        else max(
            abs(value - reference_value)
            for value, reference_value in zip(
                snapshot.activation,
                reference_activation,
                strict=True,
            )
        )
    )
    completion_group_count = sum(
        len(batch.completion_groups) for batch in reference.handoff.batches
    )
    projected_contacts = 0
    for batch in reference.handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(
            batch,
            reference.field.docks,
        )
        projected = project_transient_docks_to_neuron_inputs(
            trajectory,
            reference.field.docks,
        )
        projected_contacts += projected.contact_count
    observation = FieldEventDensityResourceObservation(
        density_id=density_id,
        input_amplitude=input_amplitude,
        support_seconds=support_seconds,
        duration_seconds=FIELD_EVENT_DENSITY_DURATION_SECONDS,
        repetitions=FIELD_EVENT_DENSITY_REPETITIONS,
        support_count_per_modality=len(sequences[0].frames),
        source_event_count=reference.handoff.assigned_event_count,
        completion_group_count=completion_group_count,
        proposal_batch_count=len(reference.handoff.batches),
        projected_local_contact_count=projected_contacts,
        field_neuron_count=len(snapshot.neuron_ids),
        final_activation_l1=math.fsum(abs(value) for value in snapshot.activation),
        final_activation_linf=max(abs(value) for value in snapshot.activation),
        final_afterimage_linf=max(abs(value) for value in snapshot.afterimage),
        reference_activation_delta_linf=reference_delta,
        endpoint_digest=digests[0],
        repeated_endpoints_equal=len(set(digests)) == 1,
        runtime_seconds_min=min(runtime_samples),
        runtime_seconds_median=median(runtime_samples),
        runtime_seconds_max=max(runtime_samples),
        process_seconds_min=min(process_samples),
        process_seconds_median=median(process_samples),
        process_seconds_max=max(process_samples),
    )
    return observation, snapshot.activation


def run_field_event_density_resource_characterization(
) -> FieldEventDensityResourceCharacterization:
    """Run the fixed zero-contact density matrix without adaptive behavior."""

    observations_out = []
    for input_amplitude in FIELD_EVENT_DENSITY_INPUT_AMPLITUDES:
        reference_activation = None
        for density_id, support_seconds in zip(
            FIELD_EVENT_DENSITY_IDS,
            FIELD_EVENT_DENSITY_SUPPORT_SECONDS,
            strict=True,
        ):
            observation, activation = _run_density(
                density_id,
                support_seconds,
                input_amplitude,
                reference_activation,
            )
            if reference_activation is None:
                reference_activation = activation
            observations_out.append(observation)
    observations = tuple(observations_out)
    zero = tuple(item for item in observations if item.input_amplitude == 0.0)
    active = tuple(item for item in observations if item.input_amplitude == 0.1)
    first = zero[0]
    last = zero[-1]
    zero_endpoints_equal = (
        len({item.endpoint_digest for item in zero}) == 1
        and all(
            item.final_activation_l1 == 0.0
            and item.final_activation_linf == 0.0
            and item.final_afterimage_linf == 0.0
            and item.reference_activation_delta_linf == 0.0
            for item in zero
        )
    )
    active_max_delta = max(
        item.reference_activation_delta_linf for item in active
    )
    active_invariant = active_max_delta <= 1e-12
    return FieldEventDensityResourceCharacterization(
        observations=observations,
        density_ids=FIELD_EVENT_DENSITY_IDS,
        duration_seconds=FIELD_EVENT_DENSITY_DURATION_SECONDS,
        repetitions_per_density=FIELD_EVENT_DENSITY_REPETITIONS,
        source_event_growth_factor=(
            last.source_event_count / first.source_event_count
        ),
        projected_contact_growth_factor=(
            last.projected_local_contact_count
            / first.projected_local_contact_count
        ),
        zero_contact_endpoints_equal=zero_endpoints_equal,
        active_contact_max_density_delta_linf=active_max_delta,
        active_contact_density_invariant=active_invariant,
        resource_limit_observed=False,
        characterization_decision=(
            "FIELD_ENDPOINT_INVARIANT_ACROSS_BOUND_EVENT_DENSITIES"
            if zero_endpoints_equal and active_invariant
            else "FIELD_ENDPOINT_DENSITY_DEPENDENCE_OBSERVED"
        ),
    )


def field_event_density_resource_characterization_json_value(
    result: FieldEventDensityResourceCharacterization,
) -> dict[str, object]:
    if not isinstance(result, FieldEventDensityResourceCharacterization):
        raise FieldEventDensityResourceCharacterizationError(
            "JSON projection requires an event-density resource result"
        )
    return asdict(result)


def field_event_density_resource_characterization_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            FieldEventDensityResourceObservation,
            FieldEventDensityResourceCharacterization,
        )
        for item in fields(contract)
    )
