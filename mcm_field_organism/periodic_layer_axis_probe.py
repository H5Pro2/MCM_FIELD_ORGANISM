"""Methodik-033 probe for an optional periodic MCM neuron-layer axis."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import json
from typing import Callable, Iterable

from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import (
    MCMNeuronDrive,
    MCMNeuronLayer,
    MCMNeuronLayerError,
    MCMNeuronOutput,
    PeriodicSamplingAxis,
    hold_state_baseline,
    receptor_projection_baseline,
)
from .periodic_sampling_probe import (
    RING_OFFSETS,
    RING_SIZE,
    SIGNATURE_ACTIVATION,
    SIGNATURE_AFTERIMAGE,
    SIGNATURE_CONTACTS,
    _perception_digest,
    _transformation_digest,
    periodic_reference_perceptions,
    run_periodic_sampling_probe,
)
from .sensor_mcm_field import CommonFieldTime, build_receptor_aligned_mcm_field
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


class PeriodicLayerAxisProbeError(ValueError):
    """Raised when the Methodik-033 integration probe is invalid."""


BEFUND_035_DIGEST = (
    "1c717cd79cb0a571cfe4e32439c8ba2484b0672da6555765855a5ef811ebbdc5"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class PeriodicLayerTargetObservation:
    target_position: int
    runtime_perception_digest: str
    reference_perception_digest: str
    runtime_matches_reference: bool
    added_wrap_samples: int

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class PeriodicLayerWorldObservation:
    start_position: int
    delta: int
    cause: str
    next_position: int
    provenance_digest: str
    reference_sampling_digest: str
    runtime_sampling_digest: str
    runtime_matches_reference: bool

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class PeriodicLayerCausePair:
    start_position: int
    delta: int
    provenance_distinct: bool
    runtime_sampling_equal: bool

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class PeriodicLayerTransformObservation:
    rotation: int
    orientation: int
    runtime_sampling_digest: str
    reference_sampling_digest: str
    runtime_matches_reference: bool
    canonical_equals_base: bool

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class PeriodicLayerAxisProbeResult:
    targets: tuple[PeriodicLayerTargetObservation, ...]
    world_observations: tuple[PeriodicLayerWorldObservation, ...]
    cause_pairs: tuple[PeriodicLayerCausePair, ...]
    transformations: tuple[PeriodicLayerTransformObservation, ...]
    legacy_digest_unchanged: bool
    explicit_open_equals_legacy: bool
    runtime_matches_reference: bool
    exactly_two_wrap_samples: bool
    interior_runtime_unchanged: bool
    hold_baseline_fast_state_equal: bool
    receptor_baseline_fast_state_equal: bool
    all_world_branches_match_reference: bool
    all_cause_pairs_collapse: bool
    all_transformations_equivariant: bool
    negative_families_rejected: bool
    anatomy_preserved_on_advance: bool
    atomic_failure_preserves_source: bool
    observer_is_neutral: bool
    order_is_neutral: bool
    repeated_run_is_neutral: bool
    productive_world_path_activated: bool = False
    stores_relationships: bool = False
    releases_field_rule: bool = False

    def __post_init__(self) -> None:
        if len(self.targets) != 7:
            raise PeriodicLayerAxisProbeError(
                "result must contain all seven target observations"
            )
        if len(self.world_observations) != 42 or len(self.cause_pairs) != 21:
            raise PeriodicLayerAxisProbeError(
                "result must contain all world branches and cause pairs"
            )
        if len(self.transformations) != 14:
            raise PeriodicLayerAxisProbeError(
                "result must contain all rigid ring transformations"
            )
        if (
            self.productive_world_path_activated
            or self.stores_relationships
            or self.releases_field_rule
        ):
            raise PeriodicLayerAxisProbeError(
                "integration probe cannot activate the world path, relationships, or a field rule"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "targets": [item.canonical_payload() for item in self.targets],
            "world_observations": [
                item.canonical_payload() for item in self.world_observations
            ],
            "cause_pairs": [
                item.canonical_payload() for item in self.cause_pairs
            ],
            "transformations": [
                item.canonical_payload() for item in self.transformations
            ],
            "legacy_digest_unchanged": self.legacy_digest_unchanged,
            "explicit_open_equals_legacy": self.explicit_open_equals_legacy,
            "runtime_matches_reference": self.runtime_matches_reference,
            "exactly_two_wrap_samples": self.exactly_two_wrap_samples,
            "interior_runtime_unchanged": self.interior_runtime_unchanged,
            "hold_baseline_fast_state_equal": (
                self.hold_baseline_fast_state_equal
            ),
            "receptor_baseline_fast_state_equal": (
                self.receptor_baseline_fast_state_equal
            ),
            "all_world_branches_match_reference": (
                self.all_world_branches_match_reference
            ),
            "all_cause_pairs_collapse": self.all_cause_pairs_collapse,
            "all_transformations_equivariant": (
                self.all_transformations_equivariant
            ),
            "negative_families_rejected": self.negative_families_rejected,
            "anatomy_preserved_on_advance": self.anatomy_preserved_on_advance,
            "atomic_failure_preserves_source": (
                self.atomic_failure_preserves_source
            ),
            "observer_is_neutral": self.observer_is_neutral,
            "order_is_neutral": self.order_is_neutral,
            "repeated_run_is_neutral": self.repeated_run_is_neutral,
            "productive_world_path_activated": (
                self.productive_world_path_activated
            ),
            "stores_relationships": self.stores_relationships,
            "releases_field_rule": self.releases_field_rule,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


TargetObserver = Callable[[PeriodicLayerTargetObservation], object]


def _layer(
    *,
    periodic: bool,
    rotation: int = 0,
    orientation: int = 1,
    activation: tuple[float, ...] = SIGNATURE_ACTIVATION,
    afterimage: tuple[float, ...] = SIGNATURE_AFTERIMAGE,
    reverse_neurons: bool = False,
    reverse_offsets: bool = False,
) -> MCMNeuronLayer:
    neurons = []
    for logical_position in WORLD_POSITIONS:
        physical_position = (orientation * logical_position + rotation) % RING_SIZE
        neurons.append(
            MCMNeuron(
                neuron_id=f"signature.n{logical_position}",
                field_id="simulated.signature",
                modality_id="simulated.contact",
                geometry_id=(
                    "simulated.field.ring7.v1"
                    if periodic
                    else "simulated.field.line7.v1"
                ),
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
        neurons=tuple(reversed(neurons)) if reverse_neurons else tuple(neurons),
        sample_offsets=(
            tuple(reversed(RING_OFFSETS)) if reverse_offsets else RING_OFFSETS
        ),
        periodic_axes=(
            (PeriodicSamplingAxis(axis_index=0, origin=0, size=RING_SIZE),)
            if periodic
            else ()
        ),
    )


def _contacts(values: tuple[float, ...]) -> dict[str, float]:
    return {
        f"signature.n{position}": values[position]
        for position in WORLD_POSITIONS
    }


def _runtime_perceptions(
    layer: MCMNeuronLayer,
    contacts: dict[str, float],
    transition: Callable[[MCMNeuronDrive], MCMNeuronOutput] = hold_state_baseline,
) -> tuple[MCMNeuronLayer, tuple[tuple[str, MCMFieldPerception], ...]]:
    captured: dict[str, MCMFieldPerception] = {}

    def capture(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        captured[drive.previous.neuron_id] = drive.perception
        return transition(drive)

    advanced = layer.advance(contacts, capture)
    perceptions = tuple(
        sorted(
            captured.items(),
            key=lambda item: layer.neuron(item[0]).position,
        )
    )
    return advanced, perceptions


def _fast_state(layer: MCMNeuronLayer) -> tuple[tuple[str, float, float], ...]:
    return tuple(
        sorted(
            (neuron.neuron_id, neuron.activation, neuron.afterimage)
            for neuron in layer.neurons
        )
    )


def _sample_keys(
    perceptions: tuple[tuple[str, MCMFieldPerception], ...],
) -> dict[int, tuple[tuple[tuple[int, ...], str], ...]]:
    result = {}
    for neuron_id, perception in perceptions:
        target = int(neuron_id.rsplit("n", 1)[1])
        result[target] = tuple(
            (
                sample.relative_position,
                sample.sample_id.removeprefix("sample."),
            )
            for sample in perception.local_samples
        )
    return result


def _target_observations(
    open_perceptions: tuple[tuple[str, MCMFieldPerception], ...],
    runtime_perceptions: tuple[tuple[str, MCMFieldPerception], ...],
    reference_perceptions: tuple[tuple[str, MCMFieldPerception], ...],
    observer: TargetObserver | None,
) -> tuple[PeriodicLayerTargetObservation, ...]:
    open_by_id = dict(open_perceptions)
    runtime_by_id = dict(runtime_perceptions)
    reference_by_id = dict(reference_perceptions)
    observations = []
    for position in WORLD_POSITIONS:
        neuron_id = f"signature.n{position}"
        runtime = runtime_by_id[neuron_id]
        reference = reference_by_id[neuron_id]
        open_keys = {
            (sample.relative_position, sample.sample_id)
            for sample in open_by_id[neuron_id].local_samples
        }
        added = sum(
            (sample.relative_position, sample.sample_id) not in open_keys
            for sample in runtime.local_samples
        )
        observation = PeriodicLayerTargetObservation(
            target_position=position,
            runtime_perception_digest=_digest(runtime.canonical_payload()),
            reference_perception_digest=_digest(reference.canonical_payload()),
            runtime_matches_reference=(runtime == reference),
            added_wrap_samples=added,
        )
        before = observation.digest()
        if observer is not None:
            observer(observation)
        if observation.digest() != before:
            raise PeriodicLayerAxisProbeError(
                "observer changed an immutable target observation"
            )
        observations.append(observation)
    return tuple(observations)


def _world_family(
) -> tuple[
    tuple[PeriodicLayerWorldObservation, ...],
    tuple[PeriodicLayerCausePair, ...],
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
                layer = _layer(
                    periodic=True,
                    activation=window.activation,
                    afterimage=window.afterimage,
                )
                contacts = _contacts(window.activation)
                _, runtime = _runtime_perceptions(layer, contacts)
                reference = periodic_reference_perceptions(
                    layer,
                    contacts,
                    axis_size=RING_SIZE,
                )
                runtime_digest = _perception_digest(runtime)
                reference_digest = _perception_digest(reference)
                observations.append(
                    PeriodicLayerWorldObservation(
                        start_position=start_position,
                        delta=delta,
                        cause=cause.value,
                        next_position=transition.next_world.position,
                        provenance_digest=transition.provenance_digest(),
                        reference_sampling_digest=reference_digest,
                        runtime_sampling_digest=runtime_digest,
                        runtime_matches_reference=(
                            runtime_digest == reference_digest
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
        (item.start_position, item.delta, item.cause): item
        for item in canonical
    }
    pairs = []
    for position in WORLD_POSITIONS:
        for delta in WORLD_DELTAS:
            external = by_key[(position, delta, "external")]
            effector = by_key[(position, delta, "effector")]
            pairs.append(
                PeriodicLayerCausePair(
                    start_position=position,
                    delta=delta,
                    provenance_distinct=(
                        external.provenance_digest != effector.provenance_digest
                    ),
                    runtime_sampling_equal=(
                        external.runtime_sampling_digest
                        == effector.runtime_sampling_digest
                    ),
                )
            )
    return canonical, tuple(pairs)


def _negative_families_rejected() -> bool:
    base_neurons = _layer(periodic=False).neurons
    invalid_calls = (
        lambda: PeriodicSamplingAxis(axis_index=True, origin=0, size=7),
        lambda: PeriodicSamplingAxis(axis_index=0, origin=False, size=7),
        lambda: PeriodicSamplingAxis(axis_index=0, origin=0, size=True),
        lambda: PeriodicSamplingAxis(axis_index=0, origin=0, size=1),
        lambda: MCMNeuronLayer(
            layer_id="invalid.axis",
            neurons=base_neurons,
            sample_offsets=RING_OFFSETS,
            periodic_axes=(PeriodicSamplingAxis(1, 0, 7),),
        ),
        lambda: MCMNeuronLayer(
            layer_id="invalid.duplicate",
            neurons=base_neurons,
            sample_offsets=RING_OFFSETS,
            periodic_axes=(
                PeriodicSamplingAxis(0, 0, 7),
                PeriodicSamplingAxis(0, 0, 7),
            ),
        ),
        lambda: MCMNeuronLayer(
            layer_id="invalid.interval",
            neurons=base_neurons,
            sample_offsets=RING_OFFSETS,
            periodic_axes=(PeriodicSamplingAxis(0, 1, 7),),
        ),
        lambda: MCMNeuronLayer(
            layer_id="invalid.missing",
            neurons=tuple(neuron for neuron in base_neurons if neuron.position != (3,)),
            sample_offsets=RING_OFFSETS,
            periodic_axes=(PeriodicSamplingAxis(0, 0, 7),),
        ),
        lambda: MCMNeuronLayer(
            layer_id="invalid.alias",
            neurons=tuple(neuron for neuron in base_neurons if neuron.position in ((0,), (1,))),
            sample_offsets=RING_OFFSETS,
            periodic_axes=(PeriodicSamplingAxis(0, 0, 2),),
        ),
    )
    for call in invalid_calls:
        try:
            call()
        except MCMNeuronLayerError:
            continue
        return False
    return True


def _atomic_failure_preserves_source(layer: MCMNeuronLayer) -> bool:
    before = layer.digest()

    def fail_on_center(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        if drive.previous.position == (3,):
            raise RuntimeError("controlled atomic failure")
        return hold_state_baseline(drive)

    try:
        layer.advance(_contacts(SIGNATURE_CONTACTS), fail_on_center)
    except RuntimeError:
        return layer.digest() == before
    return False


def run_periodic_layer_axis_probe(
    *,
    reverse_neurons: bool = False,
    reverse_offsets: bool = False,
    observer: TargetObserver | None = None,
    _verify_controls: bool = True,
) -> PeriodicLayerAxisProbeResult:
    """Run the complete integration comparison fixed by Methodik 033."""

    open_layer = _layer(periodic=False)
    explicit_open = MCMNeuronLayer(
        layer_id=open_layer.layer_id,
        neurons=open_layer.neurons,
        sample_offsets=open_layer.sample_offsets,
        periodic_axes=(),
    )
    periodic_layer = _layer(
        periodic=True,
        reverse_neurons=reverse_neurons,
        reverse_offsets=reverse_offsets,
    )
    contacts = _contacts(SIGNATURE_CONTACTS)
    _, open_perceptions = _runtime_perceptions(open_layer, contacts)
    advanced_periodic, runtime_perceptions = _runtime_perceptions(
        periodic_layer,
        contacts,
    )
    reference_perceptions = periodic_reference_perceptions(
        periodic_layer,
        contacts,
        axis_size=RING_SIZE,
    )
    targets = _target_observations(
        open_perceptions,
        runtime_perceptions,
        reference_perceptions,
        observer,
    )
    open_keys = _sample_keys(open_perceptions)
    runtime_keys = _sample_keys(runtime_perceptions)

    transforms = []
    base_digest = _transformation_digest(
        periodic_layer,
        runtime_perceptions,
        1,
    )
    for orientation in (1, -1):
        for rotation in WORLD_POSITIONS:
            transformed = _layer(
                periodic=True,
                rotation=rotation,
                orientation=orientation,
            )
            transformed_contacts = _contacts(SIGNATURE_CONTACTS)
            _, runtime = _runtime_perceptions(
                transformed,
                transformed_contacts,
            )
            reference = periodic_reference_perceptions(
                transformed,
                transformed_contacts,
                axis_size=RING_SIZE,
            )
            runtime_digest = _transformation_digest(
                transformed,
                runtime,
                orientation,
            )
            reference_digest = _transformation_digest(
                transformed,
                reference,
                orientation,
            )
            transforms.append(
                PeriodicLayerTransformObservation(
                    rotation=rotation,
                    orientation=orientation,
                    runtime_sampling_digest=runtime_digest,
                    reference_sampling_digest=reference_digest,
                    runtime_matches_reference=(runtime == reference),
                    canonical_equals_base=(runtime_digest == base_digest),
                )
            )

    open_hold, _ = _runtime_perceptions(
        open_layer,
        contacts,
        hold_state_baseline,
    )
    periodic_hold, _ = _runtime_perceptions(
        periodic_layer,
        contacts,
        hold_state_baseline,
    )
    open_receptor, _ = _runtime_perceptions(
        open_layer,
        contacts,
        receptor_projection_baseline,
    )
    periodic_receptor, _ = _runtime_perceptions(
        periodic_layer,
        contacts,
        receptor_projection_baseline,
    )
    world_observations, cause_pairs = _world_family()
    wrap_count = sum(item.added_wrap_samples for item in targets)
    legacy_provisional = run_periodic_sampling_probe(_verify_controls=False)
    legacy_digest = replace(
        legacy_provisional,
        observer_is_neutral=True,
        order_is_neutral=True,
        repeated_run_is_neutral=True,
    ).digest()
    provisional = PeriodicLayerAxisProbeResult(
        targets=targets,
        world_observations=world_observations,
        cause_pairs=cause_pairs,
        transformations=tuple(transforms),
        legacy_digest_unchanged=(
            legacy_digest == BEFUND_035_DIGEST
        ),
        explicit_open_equals_legacy=(
            open_layer == explicit_open
            and open_layer.digest() == explicit_open.digest()
        ),
        runtime_matches_reference=all(
            item.runtime_matches_reference for item in targets
        ),
        exactly_two_wrap_samples=(wrap_count == 2),
        interior_runtime_unchanged=all(
            runtime_keys[position] == open_keys[position]
            for position in range(1, 6)
        ),
        hold_baseline_fast_state_equal=(
            _fast_state(open_hold) == _fast_state(periodic_hold)
        ),
        receptor_baseline_fast_state_equal=(
            _fast_state(open_receptor) == _fast_state(periodic_receptor)
        ),
        all_world_branches_match_reference=all(
            item.runtime_matches_reference for item in world_observations
        ),
        all_cause_pairs_collapse=all(
            pair.provenance_distinct and pair.runtime_sampling_equal
            for pair in cause_pairs
        ),
        all_transformations_equivariant=all(
            item.runtime_matches_reference and item.canonical_equals_base
            for item in transforms
        ),
        negative_families_rejected=_negative_families_rejected(),
        anatomy_preserved_on_advance=(
            advanced_periodic.periodic_axes == periodic_layer.periodic_axes
            and {
                neuron.geometry_id for neuron in advanced_periodic.neurons
            }
            == {"simulated.field.ring7.v1"}
        ),
        atomic_failure_preserves_source=(
            _atomic_failure_preserves_source(periodic_layer)
        ),
        observer_is_neutral=False,
        order_is_neutral=False,
        repeated_run_is_neutral=False,
    )
    if not _verify_controls:
        return provisional

    reference = run_periodic_layer_axis_probe(_verify_controls=False)
    repeated = run_periodic_layer_axis_probe(_verify_controls=False)
    passive_observer = run_periodic_layer_axis_probe(
        observer=lambda item: None,
        _verify_controls=False,
    )
    collected: list[PeriodicLayerTargetObservation] = []
    collecting = run_periodic_layer_axis_probe(
        observer=collected.append,
        _verify_controls=False,
    )
    reversed_order = run_periodic_layer_axis_probe(
        reverse_neurons=True,
        reverse_offsets=True,
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
            and len(collected) == 7
        ),
        order_is_neutral=(
            current_digest == reference_digest == reversed_order.digest()
        ),
        repeated_run_is_neutral=(
            current_digest == reference_digest == repeated.digest()
        ),
    )


def periodic_layer_axis_public_roles() -> tuple[tuple[str, ...], ...]:
    classes = (
        PeriodicSamplingAxis,
        PeriodicLayerTargetObservation,
        PeriodicLayerWorldObservation,
        PeriodicLayerCausePair,
        PeriodicLayerTransformObservation,
        PeriodicLayerAxisProbeResult,
    )
    return tuple(tuple(item.name for item in fields(cls)) for cls in classes)
