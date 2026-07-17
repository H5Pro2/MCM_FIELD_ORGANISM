"""Passive Methodik-032 comparison of open and periodic local field sampling."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import json
from typing import Callable, Iterable, Mapping

from .mcm_neuron import MCMFieldPerception, MCMFieldSample, MCMNeuron
from .mcm_neuron_layer import (
    MCMNeuronDrive,
    MCMNeuronLayer,
    MCMNeuronOutput,
    advance_mcm_neuron,
    hold_state_baseline,
    receptor_projection_baseline,
)
from .receptor_contract import CommonFieldTime
from .sensor_mcm_field import build_receptor_aligned_mcm_field
from .simulated_effector_world import (
    WORLD_CAUSES,
    WORLD_DELTAS,
    WORLD_POSITIONS,
    SimulatedWorldState,
    WorldIntervention,
    advance_simulated_world,
    receptor_frame_from_world,
)
from .simulated_world_mcm_path import simulated_world_receptor_to_contact_frame


class PeriodicSamplingProbeError(ValueError):
    """Raised when the passive periodic reference violates its contract."""


RING_SIZE = 7
RING_OFFSETS = ((-1,), (1,))
SIGNATURE_ACTIVATION = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
SIGNATURE_AFTERIMAGE = (0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0)
SIGNATURE_CONTACTS = (0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validated_permutation(
    values: Iterable[int],
    expected: tuple[int, ...],
    role: str,
) -> tuple[int, ...]:
    result = tuple(values)
    if len(result) != len(expected) or set(result) != set(expected):
        raise PeriodicSamplingProbeError(
            f"{role} must contain each preregistered value exactly once"
        )
    return result


def _validated_offsets(
    values: Iterable[Iterable[int]],
    expected: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    try:
        result = tuple(tuple(offset) for offset in values)
    except TypeError as exc:
        raise PeriodicSamplingProbeError(
            "offset_order must contain coordinate tuples"
        ) from exc
    if len(result) != len(expected) or set(result) != set(expected):
        raise PeriodicSamplingProbeError(
            "offset_order must contain each layer offset exactly once"
        )
    return result


@dataclass(frozen=True, slots=True)
class PeriodicSampleAddress:
    target_position: int
    offset: int
    source_position: int
    source_neuron_id: str
    source_field_id: str
    source_tick: int
    activation: float
    afterimage: float

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class PeriodicTargetComparison:
    target_position: int
    open_samples: tuple[PeriodicSampleAddress, ...]
    periodic_samples: tuple[PeriodicSampleAddress, ...]
    added_samples: tuple[PeriodicSampleAddress, ...]

    def canonical_payload(self) -> dict[str, object]:
        return {
            "target_position": self.target_position,
            "open_samples": [
                sample.canonical_payload() for sample in self.open_samples
            ],
            "periodic_samples": [
                sample.canonical_payload() for sample in self.periodic_samples
            ],
            "added_samples": [
                sample.canonical_payload() for sample in self.added_samples
            ],
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class PeriodicWorldSamplingObservation:
    start_position: int
    delta: int
    cause: str
    next_position: int
    provenance_digest: str
    open_sampling_digest: str
    periodic_sampling_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class PeriodicWorldCausePair:
    start_position: int
    delta: int
    provenance_distinct: bool
    open_sampling_equal: bool
    periodic_sampling_equal: bool

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class PeriodicTransformObservation:
    rotation: int
    orientation: int
    canonical_sampling_digest: str
    equals_reference: bool

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class PeriodicSamplingProbeResult:
    comparisons: tuple[PeriodicTargetComparison, ...]
    world_observations: tuple[PeriodicWorldSamplingObservation, ...]
    cause_pairs: tuple[PeriodicWorldCausePair, ...]
    transformations: tuple[PeriodicTransformObservation, ...]
    open_reference_exact: bool
    exactly_two_wrap_samples: bool
    interior_samples_equal: bool
    wrap_payload_exact: bool
    all_transformations_equivariant: bool
    ambiguous_geometry_rejected: bool
    all_cause_pairs_collapse: bool
    hold_baseline_fast_state_equal: bool
    receptor_baseline_fast_state_equal: bool
    source_layer_immutable: bool
    observer_is_neutral: bool
    order_is_neutral: bool
    repeated_run_is_neutral: bool
    writes_runtime: bool = False
    stores_relationships: bool = False
    releases_field_rule: bool = False

    def __post_init__(self) -> None:
        if len(self.comparisons) != 7:
            raise PeriodicSamplingProbeError(
                "result must contain all seven target comparisons"
            )
        if len(self.world_observations) != 42 or len(self.cause_pairs) != 21:
            raise PeriodicSamplingProbeError(
                "result must contain all 42 world branches and 21 cause pairs"
            )
        if len(self.transformations) != 14:
            raise PeriodicSamplingProbeError(
                "result must contain all 14 rigid ring transformations"
            )
        if self.writes_runtime or self.stores_relationships or self.releases_field_rule:
            raise PeriodicSamplingProbeError(
                "passive reference cannot write runtime, relationships, or a field rule"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "comparisons": [
                comparison.canonical_payload() for comparison in self.comparisons
            ],
            "world_observations": [
                observation.canonical_payload()
                for observation in self.world_observations
            ],
            "cause_pairs": [pair.canonical_payload() for pair in self.cause_pairs],
            "transformations": [
                transformation.canonical_payload()
                for transformation in self.transformations
            ],
            "open_reference_exact": self.open_reference_exact,
            "exactly_two_wrap_samples": self.exactly_two_wrap_samples,
            "interior_samples_equal": self.interior_samples_equal,
            "wrap_payload_exact": self.wrap_payload_exact,
            "all_transformations_equivariant": (
                self.all_transformations_equivariant
            ),
            "ambiguous_geometry_rejected": self.ambiguous_geometry_rejected,
            "all_cause_pairs_collapse": self.all_cause_pairs_collapse,
            "hold_baseline_fast_state_equal": (
                self.hold_baseline_fast_state_equal
            ),
            "receptor_baseline_fast_state_equal": (
                self.receptor_baseline_fast_state_equal
            ),
            "source_layer_immutable": self.source_layer_immutable,
            "observer_is_neutral": self.observer_is_neutral,
            "order_is_neutral": self.order_is_neutral,
            "repeated_run_is_neutral": self.repeated_run_is_neutral,
            "writes_runtime": self.writes_runtime,
            "stores_relationships": self.stores_relationships,
            "releases_field_rule": self.releases_field_rule,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


ComparisonObserver = Callable[[PeriodicTargetComparison], object]


def _signature_layer(
    *,
    rotation: int = 0,
    orientation: int = 1,
    activation: tuple[float, ...] = SIGNATURE_ACTIVATION,
    afterimage: tuple[float, ...] = SIGNATURE_AFTERIMAGE,
) -> MCMNeuronLayer:
    if rotation not in WORLD_POSITIONS or orientation not in (-1, 1):
        raise PeriodicSamplingProbeError("unknown rigid ring transformation")
    if len(activation) != RING_SIZE or len(afterimage) != RING_SIZE:
        raise PeriodicSamplingProbeError("signature state must contain seven values")
    neurons = []
    for logical_position in WORLD_POSITIONS:
        physical_position = (orientation * logical_position + rotation) % RING_SIZE
        neurons.append(
            MCMNeuron(
                neuron_id=f"signature.n{logical_position}",
                field_id="simulated.signature",
                modality_id="simulated.contact",
                geometry_id="simulated.field.line7.v1",
                position=(physical_position,),
                activation=activation[logical_position],
                afterimage=afterimage[logical_position],
                perception=MCMFieldPerception(
                    tick=0,
                    receptor_contact=0.0,
                    local_samples=(),
                ),
            )
        )
    return MCMNeuronLayer(
        layer_id="simulated.signature.layer",
        neurons=tuple(neurons),
        sample_offsets=RING_OFFSETS,
    )


def periodic_reference_perceptions(
    layer: MCMNeuronLayer,
    receptor_contacts: Mapping[str, float],
    *,
    axis_size: int,
    target_order: Iterable[int] | None = None,
    offset_order: Iterable[Iterable[int]] | None = None,
) -> tuple[tuple[str, MCMFieldPerception], ...]:
    """Build immutable periodic perceptions without advancing the layer."""

    if not isinstance(layer, MCMNeuronLayer):
        raise PeriodicSamplingProbeError("layer must be a completed MCM neuron layer")
    if isinstance(axis_size, bool) or not isinstance(axis_size, int) or axis_size < 2:
        raise PeriodicSamplingProbeError("axis_size must be an integer of at least two")
    if any(len(neuron.position) != 1 for neuron in layer.neurons):
        raise PeriodicSamplingProbeError(
            "periodic reference currently accepts exactly one-dimensional layers"
        )
    positions = tuple(sorted(neuron.position[0] for neuron in layer.neurons))
    expected_positions = tuple(range(axis_size))
    if positions != expected_positions:
        raise PeriodicSamplingProbeError(
            "layer positions must cover the complete canonical periodic axis"
        )
    if any(len(offset) != 1 for offset in layer.sample_offsets):
        raise PeriodicSamplingProbeError(
            "periodic reference offsets must share the one-dimensional axis"
        )

    targets = _validated_permutation(
        expected_positions if target_order is None else target_order,
        expected_positions,
        "target_order",
    )
    offsets = _validated_offsets(
        layer.sample_offsets if offset_order is None else offset_order,
        layer.sample_offsets,
    )
    contacts = dict(receptor_contacts)
    required = set(layer.docked_neuron_ids)
    if set(contacts) != required:
        raise PeriodicSamplingProbeError(
            "receptor contacts must match the layer dock anatomy exactly"
        )

    position_map = {neuron.position[0]: neuron for neuron in layer.neurons}
    perceptions = []
    for target_position in targets:
        target = position_map[target_position]
        mapped_positions = tuple(
            (target_position + offset[0]) % axis_size for offset in offsets
        )
        if len(set(mapped_positions)) != len(mapped_positions):
            raise PeriodicSamplingProbeError(
                "periodic offsets alias the same source for one target"
            )
        samples = []
        for offset, source_position in zip(offsets, mapped_positions, strict=True):
            source = position_map[source_position]
            samples.append(
                MCMFieldSample(
                    sample_id=f"sample.{source.neuron_id}",
                    source_field_id=source.field_id,
                    source_tick=source.tick,
                    relative_position=offset,
                    activation=source.activation,
                    afterimage=source.afterimage,
                )
            )
        perceptions.append(
            (
                target.neuron_id,
                MCMFieldPerception(
                    tick=layer.tick + 1,
                    receptor_contact=(
                        contacts[target.neuron_id]
                        if target.neuron_id in required
                        else None
                    ),
                    local_samples=tuple(samples),
                ),
            )
        )
    return tuple(
        sorted(
            perceptions,
            key=lambda item: layer.neuron(item[0]).position,
        )
    )


def _open_perceptions(
    layer: MCMNeuronLayer,
    contacts: Mapping[str, float],
) -> tuple[tuple[str, MCMFieldPerception], ...]:
    captured: dict[str, MCMFieldPerception] = {}

    def capture(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        captured[drive.previous.neuron_id] = drive.perception
        return MCMNeuronOutput(
            activation=drive.previous.activation,
            afterimage=drive.previous.afterimage,
        )

    layer.advance(contacts, capture)
    return tuple(
        sorted(
            captured.items(),
            key=lambda item: layer.neuron(item[0]).position,
        )
    )


def _address(
    target: MCMNeuron,
    sample: MCMFieldSample,
    neurons_by_id: Mapping[str, MCMNeuron],
) -> PeriodicSampleAddress:
    prefix = "sample."
    if not sample.sample_id.startswith(prefix):
        raise PeriodicSamplingProbeError("sample identity does not expose its source")
    source_id = sample.sample_id[len(prefix) :]
    source = neurons_by_id.get(source_id)
    if source is None:
        raise PeriodicSamplingProbeError("sample source is outside the frozen layer")
    return PeriodicSampleAddress(
        target_position=target.position[0],
        offset=sample.relative_position[0],
        source_position=source.position[0],
        source_neuron_id=source.neuron_id,
        source_field_id=sample.source_field_id,
        source_tick=sample.source_tick,
        activation=sample.activation,
        afterimage=sample.afterimage,
    )


def _comparisons(
    layer: MCMNeuronLayer,
    contacts: Mapping[str, float],
    *,
    target_order: Iterable[int] | None = None,
    offset_order: Iterable[Iterable[int]] | None = None,
    observer: ComparisonObserver | None = None,
) -> tuple[PeriodicTargetComparison, ...]:
    open_by_id = dict(_open_perceptions(layer, contacts))
    periodic_by_id = dict(
        periodic_reference_perceptions(
            layer,
            contacts,
            axis_size=RING_SIZE,
            target_order=target_order,
            offset_order=offset_order,
        )
    )
    neurons_by_id = {neuron.neuron_id: neuron for neuron in layer.neurons}
    comparisons = []
    for target in sorted(layer.neurons, key=lambda neuron: neuron.position):
        open_samples = tuple(
            _address(target, sample, neurons_by_id)
            for sample in open_by_id[target.neuron_id].local_samples
        )
        periodic_samples = tuple(
            _address(target, sample, neurons_by_id)
            for sample in periodic_by_id[target.neuron_id].local_samples
        )
        open_keys = {
            (sample.offset, sample.source_neuron_id) for sample in open_samples
        }
        added = tuple(
            sample
            for sample in periodic_samples
            if (sample.offset, sample.source_neuron_id) not in open_keys
        )
        comparison = PeriodicTargetComparison(
            target_position=target.position[0],
            open_samples=open_samples,
            periodic_samples=periodic_samples,
            added_samples=added,
        )
        before = comparison.digest()
        if observer is not None:
            observer(comparison)
        if comparison.digest() != before:
            raise PeriodicSamplingProbeError(
                "observer changed an immutable target comparison"
            )
        comparisons.append(comparison)
    return tuple(comparisons)


def _perception_digest(
    perceptions: tuple[tuple[str, MCMFieldPerception], ...],
) -> str:
    return _digest(
        [
            {
                "neuron_id": neuron_id,
                "perception": perception.canonical_payload(),
            }
            for neuron_id, perception in perceptions
        ]
    )


def _transformation_digest(
    layer: MCMNeuronLayer,
    perceptions: tuple[tuple[str, MCMFieldPerception], ...],
    orientation: int,
) -> str:
    neurons_by_id = {neuron.neuron_id: neuron for neuron in layer.neurons}
    payload = []
    for target_id, perception in perceptions:
        target_logical = int(target_id.rsplit("n", 1)[1])
        for sample in perception.local_samples:
            source_id = sample.sample_id.removeprefix("sample.")
            source_logical = int(source_id.rsplit("n", 1)[1])
            payload.append(
                {
                    "target_logical": target_logical,
                    "offset_logical": orientation * sample.relative_position[0],
                    "source_logical": source_logical,
                    "source_field_id": neurons_by_id[source_id].field_id,
                    "source_tick": sample.source_tick,
                    "activation": sample.activation,
                    "afterimage": sample.afterimage,
                }
            )
    return _digest(
        sorted(
            payload,
            key=lambda item: (
                item["target_logical"],
                item["offset_logical"],
                item["source_logical"],
            ),
        )
    )


def _fast_states_from_layer(layer: MCMNeuronLayer) -> tuple[tuple[str, float, float], ...]:
    return tuple(
        sorted(
            (
                neuron.neuron_id,
                neuron.activation,
                neuron.afterimage,
            )
            for neuron in layer.neurons
        )
    )


def _fast_states_from_periodic(
    layer: MCMNeuronLayer,
    perceptions: tuple[tuple[str, MCMFieldPerception], ...],
    transition: Callable[[MCMNeuronDrive], MCMNeuronOutput],
) -> tuple[tuple[str, float, float], ...]:
    return tuple(
        sorted(
            (
                neuron_id,
                advanced.activation,
                advanced.afterimage,
            )
            for neuron_id, perception in perceptions
            for advanced in (
                advance_mcm_neuron(layer.neuron(neuron_id), perception, transition),
            )
        )
    )


def _world_sampling_family(
) -> tuple[
    tuple[PeriodicWorldSamplingObservation, ...],
    tuple[PeriodicWorldCausePair, ...],
]:
    observations = []
    for start_position in WORLD_POSITIONS:
        for delta in WORLD_DELTAS:
            for cause in WORLD_CAUSES:
                transition = advance_simulated_world(
                    SimulatedWorldState(tick=0, position=start_position),
                    WorldIntervention(
                        source_tick=0,
                        delta=delta,
                        cause=cause,
                    ),
                )
                simulated_receptor = receptor_frame_from_world(
                    transition.next_world
                )
                receptor = simulated_world_receptor_to_contact_frame(
                    simulated_receptor
                )
                field = build_receptor_aligned_mcm_field(
                    receptor,
                    positions=tuple((position,) for position in WORLD_POSITIONS),
                    sample_offsets=RING_OFFSETS,
                    dock_id="simulated",
                    layer_id="simulated.layer",
                    field_id="simulated.field",
                    field_geometry_id="simulated.field.line7.v1",
                ).advance(
                    receptor,
                    CommonFieldTime(
                        clock_id="organism.simulated",
                        window_start_tick=simulated_receptor.source_tick,
                        window_end_tick=simulated_receptor.source_tick + 1,
                    ),
                    receptor_projection_baseline,
                )
                window = field.field_window()
                layer = _signature_layer(
                    activation=window.activation,
                    afterimage=window.afterimage,
                )
                contacts = {
                    f"signature.n{position}": window.activation[position]
                    for position in WORLD_POSITIONS
                }
                observations.append(
                    PeriodicWorldSamplingObservation(
                        start_position=start_position,
                        delta=delta,
                        cause=cause.value,
                        next_position=transition.next_world.position,
                        provenance_digest=transition.provenance_digest(),
                        open_sampling_digest=_perception_digest(
                            _open_perceptions(layer, contacts)
                        ),
                        periodic_sampling_digest=_perception_digest(
                            periodic_reference_perceptions(
                                layer,
                                contacts,
                                axis_size=RING_SIZE,
                            )
                        ),
                    )
                )
    canonical = tuple(
        sorted(
            observations,
            key=lambda item: (item.start_position, item.delta, item.cause),
        )
    )
    by_key = {
        (item.start_position, item.delta, item.cause): item for item in canonical
    }
    pairs = []
    for position in WORLD_POSITIONS:
        for delta in WORLD_DELTAS:
            external = by_key[(position, delta, "external")]
            effector = by_key[(position, delta, "effector")]
            pairs.append(
                PeriodicWorldCausePair(
                    start_position=position,
                    delta=delta,
                    provenance_distinct=(
                        external.provenance_digest != effector.provenance_digest
                    ),
                    open_sampling_equal=(
                        external.open_sampling_digest
                        == effector.open_sampling_digest
                    ),
                    periodic_sampling_equal=(
                        external.periodic_sampling_digest
                        == effector.periodic_sampling_digest
                    ),
                )
            )
    return canonical, tuple(pairs)


def _ambiguous_geometry_rejected() -> bool:
    layer = MCMNeuronLayer(
        layer_id="simulated.ambiguous.layer",
        neurons=tuple(
            MCMNeuron(
                neuron_id=f"ambiguous.n{position}",
                field_id="simulated.ambiguous",
                modality_id="simulated.contact",
                geometry_id="simulated.field.ring2.reference.v1",
                position=(position,),
                activation=float(position),
                afterimage=0.0,
                perception=MCMFieldPerception(
                    tick=0,
                    receptor_contact=0.0,
                    local_samples=(),
                ),
            )
            for position in range(2)
        ),
        sample_offsets=RING_OFFSETS,
    )
    contacts = {f"ambiguous.n{position}": 0.0 for position in range(2)}
    try:
        periodic_reference_perceptions(layer, contacts, axis_size=2)
    except PeriodicSamplingProbeError:
        return True
    return False


def run_periodic_sampling_probe(
    *,
    target_order: Iterable[int] = WORLD_POSITIONS,
    offset_order: Iterable[Iterable[int]] = RING_OFFSETS,
    observer: ComparisonObserver | None = None,
    _verify_controls: bool = True,
) -> PeriodicSamplingProbeResult:
    """Run the complete passive comparison fixed by Methodik 032."""

    targets = _validated_permutation(target_order, WORLD_POSITIONS, "target_order")
    offsets = _validated_offsets(offset_order, RING_OFFSETS)
    layer = _signature_layer()
    source_digest = layer.digest()
    contacts = {
        f"signature.n{position}": SIGNATURE_CONTACTS[position]
        for position in WORLD_POSITIONS
    }
    comparisons = _comparisons(
        layer,
        contacts,
        target_order=targets,
        offset_order=offsets,
        observer=observer,
    )
    open_by_id = dict(_open_perceptions(layer, contacts))
    periodic = periodic_reference_perceptions(
        layer,
        contacts,
        axis_size=RING_SIZE,
        target_order=targets,
        offset_order=offsets,
    )
    periodic_by_id = dict(periodic)

    expected_open = {
        0: ((1, 1),),
        1: ((-1, 0), (1, 2)),
        2: ((-1, 1), (1, 3)),
        3: ((-1, 2), (1, 4)),
        4: ((-1, 3), (1, 5)),
        5: ((-1, 4), (1, 6)),
        6: ((-1, 5),),
    }
    observed_open = {
        comparison.target_position: tuple(
            (sample.offset, sample.source_position)
            for sample in comparison.open_samples
        )
        for comparison in comparisons
    }
    added = tuple(
        sample
        for comparison in comparisons
        for sample in comparison.added_samples
    )
    expected_added = {
        (0, -1, 6, "signature.n6", 0.6, 0.0),
        (6, 1, 0, "signature.n0", 0.0, 0.6),
    }
    observed_added = {
        (
            sample.target_position,
            sample.offset,
            sample.source_position,
            sample.source_neuron_id,
            sample.activation,
            sample.afterimage,
        )
        for sample in added
    }
    interiors_equal = all(
        comparisons[position].open_samples == comparisons[position].periodic_samples
        for position in range(1, 6)
    )

    reference_transform_layer = _signature_layer()
    reference_transform_digest = _transformation_digest(
        reference_transform_layer,
        periodic_reference_perceptions(
            reference_transform_layer,
            contacts,
            axis_size=RING_SIZE,
        ),
        1,
    )
    transformations = []
    for orientation in (1, -1):
        for rotation in WORLD_POSITIONS:
            transformed_layer = _signature_layer(
                rotation=rotation,
                orientation=orientation,
            )
            transformed_contacts = {
                f"signature.n{position}": SIGNATURE_CONTACTS[position]
                for position in WORLD_POSITIONS
            }
            transformed_digest = _transformation_digest(
                transformed_layer,
                periodic_reference_perceptions(
                    transformed_layer,
                    transformed_contacts,
                    axis_size=RING_SIZE,
                ),
                orientation,
            )
            transformations.append(
                PeriodicTransformObservation(
                    rotation=rotation,
                    orientation=orientation,
                    canonical_sampling_digest=transformed_digest,
                    equals_reference=(
                        transformed_digest == reference_transform_digest
                    ),
                )
            )

    open_hold = layer.advance(contacts, hold_state_baseline)
    periodic_hold = _fast_states_from_periodic(
        layer,
        periodic,
        hold_state_baseline,
    )
    open_receptor = layer.advance(contacts, receptor_projection_baseline)
    periodic_receptor = _fast_states_from_periodic(
        layer,
        periodic,
        receptor_projection_baseline,
    )
    world_observations, cause_pairs = _world_sampling_family()
    provisional = PeriodicSamplingProbeResult(
        comparisons=comparisons,
        world_observations=world_observations,
        cause_pairs=cause_pairs,
        transformations=tuple(transformations),
        open_reference_exact=(observed_open == expected_open),
        exactly_two_wrap_samples=(len(added) == 2),
        interior_samples_equal=interiors_equal,
        wrap_payload_exact=(observed_added == expected_added),
        all_transformations_equivariant=all(
            transformation.equals_reference
            for transformation in transformations
        ),
        ambiguous_geometry_rejected=_ambiguous_geometry_rejected(),
        all_cause_pairs_collapse=all(
            pair.provenance_distinct
            and pair.open_sampling_equal
            and pair.periodic_sampling_equal
            for pair in cause_pairs
        ),
        hold_baseline_fast_state_equal=(
            _fast_states_from_layer(open_hold) == periodic_hold
        ),
        receptor_baseline_fast_state_equal=(
            _fast_states_from_layer(open_receptor) == periodic_receptor
        ),
        source_layer_immutable=(source_digest == layer.digest()),
        observer_is_neutral=False,
        order_is_neutral=False,
        repeated_run_is_neutral=False,
    )
    if not _verify_controls:
        return provisional

    reference = run_periodic_sampling_probe(_verify_controls=False)
    repeated = run_periodic_sampling_probe(_verify_controls=False)
    passive_observer = run_periodic_sampling_probe(
        observer=lambda comparison: None,
        _verify_controls=False,
    )
    collecting_observations: list[PeriodicTargetComparison] = []
    collecting = run_periodic_sampling_probe(
        observer=collecting_observations.append,
        _verify_controls=False,
    )
    reversed_order = run_periodic_sampling_probe(
        target_order=reversed(WORLD_POSITIONS),
        offset_order=reversed(RING_OFFSETS),
        _verify_controls=False,
    )
    current_digest = provisional.digest()
    reference_digest = reference.digest()
    return replace(
        provisional,
        observer_is_neutral=(
            current_digest
            == reference_digest
            == passive_observer.digest()
            == collecting.digest()
            and len(collecting_observations) == 7
        ),
        order_is_neutral=(
            current_digest == reference_digest == reversed_order.digest()
        ),
        repeated_run_is_neutral=(
            current_digest == reference_digest == repeated.digest()
        ),
    )


def periodic_sampling_public_roles() -> tuple[tuple[str, ...], ...]:
    classes = (
        PeriodicSampleAddress,
        PeriodicTargetComparison,
        PeriodicWorldSamplingObservation,
        PeriodicWorldCausePair,
        PeriodicTransformObservation,
        PeriodicSamplingProbeResult,
    )
    return tuple(tuple(item.name for item in fields(cls)) for cls in classes)
