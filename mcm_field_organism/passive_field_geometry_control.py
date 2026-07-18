"""Passive reflection-equivariance control for local field candidates."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

from .field_step_time import MCMFieldStepTime
from .passive_field_segmentation_comparison import (
    BoundaryDistributionFactory,
    FieldFactory,
    PassiveFieldEndpoint,
    PassiveFieldSegmentationComparison,
    PassiveFieldSegmentationError,
    TransitionFactory,
    _initial_field_digest,
    compare_passive_field_segmentations,
)
from .receptor_contract import technical_identifier
from .receptor_time_alignment import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField


class PassiveFieldGeometryControlError(ValueError):
    """Raised when two branches do not form one strict field reflection."""


@dataclass(frozen=True, slots=True)
class PassiveCarrierReflection:
    modality_id: str
    reference_carrier_id: str
    reflected_carrier_id: str

    def __post_init__(self) -> None:
        for role in (
            "modality_id",
            "reference_carrier_id",
            "reflected_carrier_id",
        ):
            object.__setattr__(
                self,
                role,
                technical_identifier(getattr(self, role), role),
            )


@dataclass(frozen=True, slots=True)
class PassiveNeuronReflection:
    reference_neuron_id: str
    reflected_neuron_id: str

    def __post_init__(self) -> None:
        for role in ("reference_neuron_id", "reflected_neuron_id"):
            object.__setattr__(
                self,
                role,
                technical_identifier(getattr(self, role), role),
            )


@dataclass(frozen=True, slots=True)
class PassiveFieldGeometryComparison:
    reflection_axis: int
    reflection_coordinate_sum: int
    reference: PassiveFieldSegmentationComparison
    reflected: PassiveFieldSegmentationComparison
    coarse_traces_equivariant: bool
    fine_traces_equivariant: bool


def _sequences(
    values: Iterable[ReceptorTimeSequence],
    role: str,
) -> tuple[ReceptorTimeSequence, ...]:
    supplied = tuple(values)
    if not supplied or any(
        not isinstance(item, ReceptorTimeSequence) for item in supplied
    ):
        raise PassiveFieldGeometryControlError(
            f"{role} requires receptor time sequences"
        )
    result = tuple(sorted(supplied, key=lambda item: item.modality_id))
    identities = tuple(
        (item.modality_id, item.geometry_id, item.clock_id) for item in result
    )
    if len(set(identities)) != len(identities):
        raise PassiveFieldGeometryControlError(
            f"{role} sequence identities must be unique"
        )
    return result


def _carrier_maps(
    correspondences: tuple[PassiveCarrierReflection, ...],
) -> dict[str, dict[str, str]]:
    if not correspondences or any(
        not isinstance(item, PassiveCarrierReflection)
        for item in correspondences
    ):
        raise PassiveFieldGeometryControlError(
            "geometry control requires carrier reflections"
        )
    result: dict[str, dict[str, str]] = {}
    reflected_by_modality: dict[str, set[str]] = {}
    for item in correspondences:
        mapping = result.setdefault(item.modality_id, {})
        if item.reference_carrier_id in mapping:
            raise PassiveFieldGeometryControlError(
                "reference carrier reflection must be unique"
            )
        reflected = reflected_by_modality.setdefault(item.modality_id, set())
        if item.reflected_carrier_id in reflected:
            raise PassiveFieldGeometryControlError(
                "reflected carrier reflection must be bijective"
            )
        mapping[item.reference_carrier_id] = item.reflected_carrier_id
        reflected.add(item.reflected_carrier_id)
    return result


def _validate_reflected_sequences(
    reference: tuple[ReceptorTimeSequence, ...],
    reflected: tuple[ReceptorTimeSequence, ...],
    carrier_maps: dict[str, dict[str, str]],
) -> None:
    if tuple(
        (item.modality_id, item.geometry_id, item.clock_id) for item in reference
    ) != tuple(
        (item.modality_id, item.geometry_id, item.clock_id) for item in reflected
    ):
        raise PassiveFieldGeometryControlError(
            "reflected sequences must preserve modality, geometry, and clock"
        )
    if set(carrier_maps) != {item.modality_id for item in reference}:
        raise PassiveFieldGeometryControlError(
            "carrier reflections must cover every receptor modality"
        )
    for first_sequence, second_sequence in zip(reference, reflected, strict=True):
        if len(first_sequence.frames) != len(second_sequence.frames):
            raise PassiveFieldGeometryControlError(
                "reflected sequences must contain the same event count"
            )
        mapping = carrier_maps[first_sequence.modality_id]
        for first, second in zip(
            first_sequence.frames,
            second_sequence.frames,
            strict=True,
        ):
            first_frame = first.frame
            second_frame = second.frame
            if (
                first.field_time != second.field_time
                or first_frame.clock_id != second_frame.clock_id
                or first_frame.window_start_tick != second_frame.window_start_tick
                or first_frame.window_end_tick != second_frame.window_end_tick
            ):
                raise PassiveFieldGeometryControlError(
                    "reflection must preserve source and organism time"
                )
            if set(mapping) != set(first_frame.carrier_ids) or set(
                mapping.values()
            ) != set(second_frame.carrier_ids):
                raise PassiveFieldGeometryControlError(
                    "carrier reflection must cover every frame carrier bijectively"
                )
            first_values = dict(zip(first_frame.carrier_ids, first_frame.values, strict=True))
            second_values = dict(
                zip(second_frame.carrier_ids, second_frame.values, strict=True)
            )
            if any(
                first_values[source] != second_values[target]
                for source, target in mapping.items()
            ):
                raise PassiveFieldGeometryControlError(
                    "reflected values must move with their carrier correspondence"
                )


def _fresh_field(factory: FieldFactory, role: str) -> SharedMCMField:
    if not callable(factory):
        raise PassiveFieldGeometryControlError(f"{role} must be callable")
    field = factory()
    if not isinstance(field, SharedMCMField) or field.last_distribution is not None:
        raise PassiveFieldGeometryControlError(
            f"{role} must return one fresh shared MCM field"
        )
    return field


def _neuron_map(
    correspondences: tuple[PassiveNeuronReflection, ...],
) -> dict[str, str]:
    if not correspondences or any(
        not isinstance(item, PassiveNeuronReflection)
        for item in correspondences
    ):
        raise PassiveFieldGeometryControlError(
            "geometry control requires neuron reflections"
        )
    result = {item.reference_neuron_id: item.reflected_neuron_id for item in correspondences}
    if len(result) != len(correspondences) or len(set(result.values())) != len(result):
        raise PassiveFieldGeometryControlError(
            "neuron reflection must be complete and bijective"
        )
    return result


def _dock_neuron_by_carrier(
    field: SharedMCMField,
) -> dict[tuple[str, str], str]:
    return {
        (dock.dock_map.modality_id, carrier_id): neuron_id
        for dock in field.docks
        for carrier_id, neuron_id in dock.dock_map.pairs
    }


def _validate_field_reflection(
    reference: SharedMCMField,
    reflected: SharedMCMField,
    neuron_map: dict[str, str],
    carrier_maps: dict[str, dict[str, str]],
    reflection_axis: int,
) -> int:
    reference_neurons = {item.neuron_id: item for item in reference.layer.neurons}
    reflected_neurons = {item.neuron_id: item for item in reflected.layer.neurons}
    if set(neuron_map) != set(reference_neurons) or set(neuron_map.values()) != set(
        reflected_neurons
    ):
        raise PassiveFieldGeometryControlError(
            "neuron reflection must cover both complete fields"
        )
    dimension = len(next(iter(reference_neurons.values())).position)
    if (
        isinstance(reflection_axis, bool)
        or not isinstance(reflection_axis, int)
        or reflection_axis < 0
        or reflection_axis >= dimension
    ):
        raise PassiveFieldGeometryControlError(
            "reflection_axis must address the shared field geometry"
        )
    coordinate_sums = set()
    moved = False
    for source_id, target_id in neuron_map.items():
        source = reference_neurons[source_id]
        target = reflected_neurons[target_id]
        if len(source.position) != len(target.position):
            raise PassiveFieldGeometryControlError(
                "reflected neurons must use the same geometry dimension"
            )
        if any(
            source.position[index] != target.position[index]
            for index in range(dimension)
            if index != reflection_axis
        ):
            raise PassiveFieldGeometryControlError(
                "reflection may change only the declared geometry axis"
            )
        coordinate_sums.add(
            source.position[reflection_axis] + target.position[reflection_axis]
        )
        moved = moved or source.position != target.position
        if (
            source.activation != target.activation
            or source.afterimage != target.afterimage
        ):
            raise PassiveFieldGeometryControlError(
                "corresponding initial neuron states must be equal"
            )
    if len(coordinate_sums) != 1 or not moved:
        raise PassiveFieldGeometryControlError(
            "neuron correspondence must form one non-identity reflection"
        )

    expected_offsets = {
        tuple(
            -value if index == reflection_axis else value
            for index, value in enumerate(offset)
        )
        for offset in reference.layer.sample_offsets
    }
    if expected_offsets != set(reflected.layer.sample_offsets):
        raise PassiveFieldGeometryControlError(
            "local sample offsets must reflect with the field geometry"
        )

    reference_docks = _dock_neuron_by_carrier(reference)
    reflected_docks = _dock_neuron_by_carrier(reflected)
    expected_reference_carriers = {
        (modality_id, carrier_id)
        for modality_id, mapping in carrier_maps.items()
        for carrier_id in mapping
    }
    expected_reflected_carriers = {
        (modality_id, carrier_id)
        for modality_id, mapping in carrier_maps.items()
        for carrier_id in mapping.values()
    }
    if (
        expected_reference_carriers != set(reference_docks)
        or expected_reflected_carriers != set(reflected_docks)
    ):
        raise PassiveFieldGeometryControlError(
            "carrier reflection must cover both complete dock anatomies"
        )
    expected_pairs = {
        (modality_id, reflected_carrier): neuron_map[
            reference_docks[(modality_id, reference_carrier)]
        ]
        for modality_id, mapping in carrier_maps.items()
        for reference_carrier, reflected_carrier in mapping.items()
    }
    if expected_pairs != reflected_docks:
        raise PassiveFieldGeometryControlError(
            "carrier and neuron reflections must describe the same dock anatomy"
        )
    return next(iter(coordinate_sums))


def _endpoint_equivariant(
    reference: PassiveFieldEndpoint,
    reflected: PassiveFieldEndpoint,
    neuron_map: dict[str, str],
) -> bool:
    first = {item.neuron_id: item for item in reference.neurons}
    second = {item.neuron_id: item for item in reflected.neurons}
    return set(first) == set(neuron_map) and set(second) == set(neuron_map.values()) and all(
        first[source].activation == second[target].activation
        and first[source].afterimage == second[target].afterimage
        for source, target in neuron_map.items()
    )


def _traces_equivariant(
    reference,
    reflected,
    neuron_map: dict[str, str],
) -> bool:
    if len(reference.steps) != len(reflected.steps):
        return False
    return all(
        first.step_index == second.step_index
        and first.step_time == second.step_time
        and first.event_count == second.event_count
        and first.modality_event_counts == second.modality_event_counts
        and first.technical_layer_tick == second.technical_layer_tick
        and _endpoint_equivariant(first.endpoint, second.endpoint, neuron_map)
        for first, second in zip(reference.steps, reflected.steps, strict=True)
    ) and _endpoint_equivariant(reference.endpoint, reflected.endpoint, neuron_map)


def compare_passive_field_reflection(
    reference_sequences: Iterable[ReceptorTimeSequence],
    reflected_sequences: Iterable[ReceptorTimeSequence],
    coarse_steps: Iterable[MCMFieldStepTime],
    fine_steps: Iterable[MCMFieldStepTime],
    *,
    reference_field_factory: FieldFactory,
    reflected_field_factory: FieldFactory,
    transition_factory: TransitionFactory,
    distribution_factory: BoundaryDistributionFactory,
    carrier_reflections: Iterable[PassiveCarrierReflection],
    neuron_reflections: Iterable[PassiveNeuronReflection],
    reflection_axis: int,
) -> PassiveFieldGeometryComparison:
    """Compare one field history with its explicit spatial reflection."""

    reference_in = _sequences(reference_sequences, "reference reflection branch")
    reflected_in = _sequences(reflected_sequences, "reflected branch")
    carrier_maps = _carrier_maps(tuple(carrier_reflections))
    _validate_reflected_sequences(reference_in, reflected_in, carrier_maps)
    neuron_map = _neuron_map(tuple(neuron_reflections))
    reference_initial = _fresh_field(
        reference_field_factory,
        "reference_field_factory",
    )
    reflected_initial = _fresh_field(
        reflected_field_factory,
        "reflected_field_factory",
    )
    coordinate_sum = _validate_field_reflection(
        reference_initial,
        reflected_initial,
        neuron_map,
        carrier_maps,
        reflection_axis,
    )
    reference_digest = _initial_field_digest(reference_initial)
    reflected_digest = _initial_field_digest(reflected_initial)

    def checked_factory(factory: FieldFactory, expected_digest: str) -> FieldFactory:
        def build() -> SharedMCMField:
            field = _fresh_field(factory, "reflection field factory")
            if _initial_field_digest(field) != expected_digest:
                raise PassiveFieldGeometryControlError(
                    "reflection field factory changed its initial field"
                )
            return field

        return build

    coarse_steps_in = tuple(coarse_steps)
    fine_steps_in = tuple(fine_steps)
    try:
        reference = compare_passive_field_segmentations(
            reference_in,
            coarse_steps_in,
            fine_steps_in,
            field_factory=checked_factory(
                reference_field_factory,
                reference_digest,
            ),
            transition_factory=transition_factory,
            distribution_factory=distribution_factory,
        )
        reflected = compare_passive_field_segmentations(
            reflected_in,
            coarse_steps_in,
            fine_steps_in,
            field_factory=checked_factory(
                reflected_field_factory,
                reflected_digest,
            ),
            transition_factory=transition_factory,
            distribution_factory=distribution_factory,
        )
    except PassiveFieldSegmentationError as exc:
        raise PassiveFieldGeometryControlError(
            f"passive field reflection failed: {exc}"
        ) from exc
    return PassiveFieldGeometryComparison(
        reflection_axis=reflection_axis,
        reflection_coordinate_sum=coordinate_sum,
        reference=reference,
        reflected=reflected,
        coarse_traces_equivariant=_traces_equivariant(
            reference.coarse,
            reflected.coarse,
            neuron_map,
        ),
        fine_traces_equivariant=_traces_equivariant(
            reference.fine,
            reflected.fine,
            neuron_map,
        ),
    )


def passive_field_geometry_control_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            PassiveCarrierReflection,
            PassiveNeuronReflection,
            PassiveFieldGeometryComparison,
        )
        for item in fields(contract)
    )
