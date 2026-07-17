"""Passive two-step ring-field path comparison from Methodik 034."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import json
from typing import Callable, Iterable

from .mcm_distributor import MCMDistributor, MCMFieldWindow
from .mcm_neuron import MCMFieldSample
from .mcm_neuron_layer import (
    MCMNeuronLayer,
    PeriodicSamplingAxis,
    receptor_projection_baseline,
)
from .sensor_mcm_field import (
    CommonFieldTime,
    ReceptorContactFrame,
    SensorMCMField,
    build_receptor_aligned_mcm_field,
)
from .simulated_effector_world import (
    WORLD_CAUSES,
    WORLD_DELTAS,
    WORLD_POSITIONS,
    InterventionCause,
    SimulatedWorldState,
    WorldIntervention,
    advance_simulated_world,
    receptor_frame_from_world,
)
from .simulated_world_mcm_path import (
    run_simulated_world_mcm_path_probe,
    simulated_world_receptor_to_contact_frame,
)


class SimulatedRingFieldPathProbeError(ValueError):
    """Raised when the Methodik-034 two-step comparison is invalid."""


METHODIK_031_OPEN_DIGEST = (
    "48e7b056b16f6c1dce1efe0def8e26ea732202f525d05952affda10dc80626ff"
)
RING_AXIS = PeriodicSamplingAxis(axis_index=0, origin=0, size=7)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validated_order(
    values: Iterable[object],
    expected: tuple[object, ...],
    role: str,
) -> tuple[object, ...]:
    result = tuple(values)
    if len(result) != len(expected) or set(result) != set(expected):
        raise SimulatedRingFieldPathProbeError(
            f"{role} must contain each preregistered value exactly once"
        )
    return result


def _normalized_window_payload(window: MCMFieldWindow) -> dict[str, object]:
    payload = window.canonical_payload()
    payload.pop("geometry_id")
    return payload


def _normalized_constellation_payload(
    payload: dict[str, object],
) -> dict[str, object]:
    states = payload["states"]
    if not isinstance(states, list):
        raise SimulatedRingFieldPathProbeError(
            "constellation payload must contain a state list"
        )
    normalized_states = []
    for state in states:
        if not isinstance(state, dict):
            raise SimulatedRingFieldPathProbeError(
                "constellation state payload must be a mapping"
            )
        state_out = dict(state)
        state_out.pop("geometry_id")
        normalized_states.append(state_out)
    return {"clock_id": payload["clock_id"], "states": normalized_states}


@dataclass(frozen=True, slots=True)
class RingWrapSampleObservation:
    target_position: int
    offset: int
    source_position: int
    source_tick: int
    activation: float
    afterimage: float

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class RingFieldPathStepComparison:
    step: int
    receptor_digest: str
    open_window_digest: str
    ring_window_digest: str
    normalized_open_window_digest: str
    normalized_ring_window_digest: str
    open_constellation_digest: str
    ring_constellation_digest: str
    normalized_open_constellation_digest: str
    normalized_ring_constellation_digest: str
    full_window_digests_distinct: bool
    normalized_windows_equal: bool
    full_constellation_digests_distinct: bool
    normalized_constellations_equal: bool
    fast_state_equal: bool
    geometry_ids_distinct: bool
    only_two_wrap_samples_differ: bool
    wrap_samples: tuple[RingWrapSampleObservation, ...]

    def __post_init__(self) -> None:
        if self.step not in (1, 2):
            raise SimulatedRingFieldPathProbeError("step must be one or two")
        if len(self.wrap_samples) != 2:
            raise SimulatedRingFieldPathProbeError(
                "each periodic step must expose exactly two wrap samples"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "step": self.step,
            "receptor_digest": self.receptor_digest,
            "open_window_digest": self.open_window_digest,
            "ring_window_digest": self.ring_window_digest,
            "normalized_open_window_digest": self.normalized_open_window_digest,
            "normalized_ring_window_digest": self.normalized_ring_window_digest,
            "open_constellation_digest": self.open_constellation_digest,
            "ring_constellation_digest": self.ring_constellation_digest,
            "normalized_open_constellation_digest": (
                self.normalized_open_constellation_digest
            ),
            "normalized_ring_constellation_digest": (
                self.normalized_ring_constellation_digest
            ),
            "full_window_digests_distinct": self.full_window_digests_distinct,
            "normalized_windows_equal": self.normalized_windows_equal,
            "full_constellation_digests_distinct": (
                self.full_constellation_digests_distinct
            ),
            "normalized_constellations_equal": (
                self.normalized_constellations_equal
            ),
            "fast_state_equal": self.fast_state_equal,
            "geometry_ids_distinct": self.geometry_ids_distinct,
            "only_two_wrap_samples_differ": self.only_two_wrap_samples_differ,
            "wrap_samples": [
                sample.canonical_payload() for sample in self.wrap_samples
            ],
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class SimulatedRingFieldBranchObservation:
    start_position: int
    delta: int
    cause: str
    held_position: int
    first_provenance_digest: str
    hold_provenance_digest: str
    first_receptor_digest: str
    hold_receptor_digest: str
    step_one: RingFieldPathStepComparison
    step_two: RingFieldPathStepComparison

    def canonical_payload(self) -> dict[str, object]:
        return {
            "start_position": self.start_position,
            "delta": self.delta,
            "cause": self.cause,
            "held_position": self.held_position,
            "first_provenance_digest": self.first_provenance_digest,
            "hold_provenance_digest": self.hold_provenance_digest,
            "first_receptor_digest": self.first_receptor_digest,
            "hold_receptor_digest": self.hold_receptor_digest,
            "step_one": self.step_one.canonical_payload(),
            "step_two": self.step_two.canonical_payload(),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class SimulatedRingFieldCausePair:
    start_position: int
    delta: int
    first_provenance_distinct: bool
    hold_provenance_distinct: bool
    first_receptor_equal: bool
    hold_receptor_equal: bool
    step_one_equal: bool
    step_two_equal: bool

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class SimulatedRingFieldTransformObservation:
    rotation: int
    orientation: int
    step_one_digest: str
    step_two_digest: str
    step_one_equals_reference: bool
    step_two_equals_reference: bool

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class SimulatedRingFieldPathProbeResult:
    branches: tuple[SimulatedRingFieldBranchObservation, ...]
    cause_pairs: tuple[SimulatedRingFieldCausePair, ...]
    transformations: tuple[SimulatedRingFieldTransformObservation, ...]
    historical_open_digest_unchanged: bool
    all_steps_have_two_wrap_samples: bool
    step_one_wraps_are_initial_zero: bool
    active_source_six_count: int
    active_source_zero_count: int
    inactive_branch_count: int
    active_wrap_counts_exact: bool
    all_fast_states_equal: bool
    all_full_digests_geometry_distinct: bool
    all_normalized_states_equal: bool
    all_cause_pairs_collapse: bool
    all_transformations_equivariant: bool
    reset_is_clean: bool
    observer_is_neutral: bool
    order_is_neutral: bool
    repeated_run_is_neutral: bool
    writes_back: bool = False
    releases_field_rule: bool = False
    connects_effector: bool = False

    def __post_init__(self) -> None:
        if len(self.branches) != 42 or len(self.cause_pairs) != 21:
            raise SimulatedRingFieldPathProbeError(
                "result must contain all 42 branches and 21 cause pairs"
            )
        if len(self.transformations) != 14:
            raise SimulatedRingFieldPathProbeError(
                "result must contain all 14 ring transformations"
            )
        if self.writes_back or self.releases_field_rule or self.connects_effector:
            raise SimulatedRingFieldPathProbeError(
                "passive path cannot write back, release a field rule, or connect an effector"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "branches": [branch.canonical_payload() for branch in self.branches],
            "cause_pairs": [pair.canonical_payload() for pair in self.cause_pairs],
            "transformations": [
                item.canonical_payload() for item in self.transformations
            ],
            "historical_open_digest_unchanged": (
                self.historical_open_digest_unchanged
            ),
            "all_steps_have_two_wrap_samples": (
                self.all_steps_have_two_wrap_samples
            ),
            "step_one_wraps_are_initial_zero": (
                self.step_one_wraps_are_initial_zero
            ),
            "active_source_six_count": self.active_source_six_count,
            "active_source_zero_count": self.active_source_zero_count,
            "inactive_branch_count": self.inactive_branch_count,
            "active_wrap_counts_exact": self.active_wrap_counts_exact,
            "all_fast_states_equal": self.all_fast_states_equal,
            "all_full_digests_geometry_distinct": (
                self.all_full_digests_geometry_distinct
            ),
            "all_normalized_states_equal": self.all_normalized_states_equal,
            "all_cause_pairs_collapse": self.all_cause_pairs_collapse,
            "all_transformations_equivariant": (
                self.all_transformations_equivariant
            ),
            "reset_is_clean": self.reset_is_clean,
            "observer_is_neutral": self.observer_is_neutral,
            "order_is_neutral": self.order_is_neutral,
            "repeated_run_is_neutral": self.repeated_run_is_neutral,
            "writes_back": self.writes_back,
            "releases_field_rule": self.releases_field_rule,
            "connects_effector": self.connects_effector,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


BranchObserver = Callable[[SimulatedRingFieldBranchObservation], object]


def _build_field(
    receptor: ReceptorContactFrame,
    *,
    periodic: bool,
    reverse_neurons: bool = False,
    reverse_offsets: bool = False,
) -> SensorMCMField:
    field = build_receptor_aligned_mcm_field(
        receptor,
        positions=tuple((position,) for position in WORLD_POSITIONS),
        sample_offsets=(
            tuple(reversed(((-1,), (1,))))
            if reverse_offsets
            else ((-1,), (1,))
        ),
        dock_id="simulated",
        layer_id="simulated.layer",
        field_id="simulated.field",
        field_geometry_id=(
            "simulated.field.ring7.v1"
            if periodic
            else "simulated.field.line7.v1"
        ),
        periodic_axes=(RING_AXIS,) if periodic else (),
    )
    if not reverse_neurons:
        return field
    return replace(
        field,
        layer=MCMNeuronLayer(
            layer_id=field.layer.layer_id,
            neurons=tuple(reversed(field.layer.neurons)),
            sample_offsets=field.layer.sample_offsets,
            periodic_axes=field.layer.periodic_axes,
        ),
    )


def _field_time(frame: ReceptorContactFrame) -> CommonFieldTime:
    return CommonFieldTime(
        clock_id="organism.simulated",
        window_start_tick=frame.window_start_tick,
        window_end_tick=frame.window_end_tick,
    )


def _distribute(field: SensorMCMField, window: MCMFieldWindow):
    distributor = MCMDistributor()
    distributor.attach(field.distributor_dock())
    return distributor.distribute((window,))


def _sample_key(sample: MCMFieldSample) -> tuple[tuple[int, ...], str]:
    return sample.relative_position, sample.sample_id


def _wrap_samples(
    open_field: SensorMCMField,
    ring_field: SensorMCMField,
) -> tuple[tuple[RingWrapSampleObservation, ...], bool]:
    open_by_position = {
        neuron.position[0]: neuron for neuron in open_field.layer.neurons
    }
    ring_by_position = {
        neuron.position[0]: neuron for neuron in ring_field.layer.neurons
    }
    source_positions = {
        neuron.neuron_id: neuron.position[0] for neuron in ring_field.layer.neurons
    }
    added = []
    common_equal = True
    for position in WORLD_POSITIONS:
        open_samples = {
            _sample_key(sample): sample
            for sample in open_by_position[position].perception.local_samples
        }
        ring_samples = {
            _sample_key(sample): sample
            for sample in ring_by_position[position].perception.local_samples
        }
        if any(ring_samples.get(key) != sample for key, sample in open_samples.items()):
            common_equal = False
        for key, sample in ring_samples.items():
            if key in open_samples:
                continue
            source_id = sample.sample_id.removeprefix("sample.")
            added.append(
                RingWrapSampleObservation(
                    target_position=position,
                    offset=sample.relative_position[0],
                    source_position=source_positions[source_id],
                    source_tick=sample.source_tick,
                    activation=sample.activation,
                    afterimage=sample.afterimage,
                )
            )
    canonical = tuple(
        sorted(
            added,
            key=lambda item: (
                item.target_position,
                item.offset,
                item.source_position,
            ),
        )
    )
    addresses = {
        (item.target_position, item.offset, item.source_position)
        for item in canonical
    }
    return canonical, common_equal and addresses == {(0, -1, 6), (6, 1, 0)}


def _step_comparison(
    step: int,
    receptor: ReceptorContactFrame,
    open_field: SensorMCMField,
    ring_field: SensorMCMField,
) -> RingFieldPathStepComparison:
    open_window = open_field.field_window()
    ring_window = ring_field.field_window()
    open_constellation = _distribute(open_field, open_window)
    ring_constellation = _distribute(ring_field, ring_window)
    open_normalized = _digest(_normalized_window_payload(open_window))
    ring_normalized = _digest(_normalized_window_payload(ring_window))
    open_constellation_normalized = _digest(
        _normalized_constellation_payload(open_constellation.canonical_payload())
    )
    ring_constellation_normalized = _digest(
        _normalized_constellation_payload(ring_constellation.canonical_payload())
    )
    wrap_samples, only_two = _wrap_samples(open_field, ring_field)
    receptor_digest = _digest(
        {
            "modality_id": receptor.modality_id,
            "geometry_id": receptor.geometry_id,
            "snapshot_id": receptor.snapshot_id,
            "clock_id": receptor.clock_id,
            "window_start_tick": receptor.window_start_tick,
            "window_end_tick": receptor.window_end_tick,
            "carrier_ids": receptor.carrier_ids,
            "values": receptor.values,
        }
    )
    return RingFieldPathStepComparison(
        step=step,
        receptor_digest=receptor_digest,
        open_window_digest=open_window.digest(),
        ring_window_digest=ring_window.digest(),
        normalized_open_window_digest=open_normalized,
        normalized_ring_window_digest=ring_normalized,
        open_constellation_digest=open_constellation.digest(),
        ring_constellation_digest=ring_constellation.digest(),
        normalized_open_constellation_digest=open_constellation_normalized,
        normalized_ring_constellation_digest=ring_constellation_normalized,
        full_window_digests_distinct=open_window.digest() != ring_window.digest(),
        normalized_windows_equal=open_normalized == ring_normalized,
        full_constellation_digests_distinct=(
            open_constellation.digest() != ring_constellation.digest()
        ),
        normalized_constellations_equal=(
            open_constellation_normalized == ring_constellation_normalized
        ),
        fast_state_equal=(
            open_window.activation == ring_window.activation
            and open_window.afterimage == ring_window.afterimage
            and open_window.carrier_ids == ring_window.carrier_ids
            and open_window.window_start_tick == ring_window.window_start_tick
            and open_window.window_end_tick == ring_window.window_end_tick
        ),
        geometry_ids_distinct=(
            open_window.geometry_id == "simulated.field.line7.v1"
            and ring_window.geometry_id == "simulated.field.ring7.v1"
        ),
        only_two_wrap_samples_differ=only_two,
        wrap_samples=wrap_samples,
    )


def _run_branch(
    start_position: int,
    delta: int,
    cause: InterventionCause,
    *,
    reverse_neurons: bool = False,
    reverse_offsets: bool = False,
) -> SimulatedRingFieldBranchObservation:
    first_transition = advance_simulated_world(
        SimulatedWorldState(tick=0, position=start_position),
        WorldIntervention(source_tick=0, delta=delta, cause=cause),
    )
    first_receptor = simulated_world_receptor_to_contact_frame(
        receptor_frame_from_world(first_transition.next_world)
    )
    open_field = _build_field(
        first_receptor,
        periodic=False,
        reverse_neurons=reverse_neurons,
        reverse_offsets=reverse_offsets,
    ).advance(first_receptor, _field_time(first_receptor), receptor_projection_baseline)
    ring_field = _build_field(
        first_receptor,
        periodic=True,
        reverse_neurons=reverse_neurons,
        reverse_offsets=reverse_offsets,
    ).advance(first_receptor, _field_time(first_receptor), receptor_projection_baseline)
    step_one = _step_comparison(1, first_receptor, open_field, ring_field)

    hold_transition = advance_simulated_world(
        first_transition.next_world,
        WorldIntervention(source_tick=1, delta=0, cause=cause),
    )
    hold_receptor = simulated_world_receptor_to_contact_frame(
        receptor_frame_from_world(hold_transition.next_world)
    )
    open_field = open_field.advance(
        hold_receptor,
        _field_time(hold_receptor),
        receptor_projection_baseline,
    )
    ring_field = ring_field.advance(
        hold_receptor,
        _field_time(hold_receptor),
        receptor_projection_baseline,
    )
    step_two = _step_comparison(2, hold_receptor, open_field, ring_field)
    return SimulatedRingFieldBranchObservation(
        start_position=start_position,
        delta=delta,
        cause=cause.value,
        held_position=hold_transition.next_world.position,
        first_provenance_digest=first_transition.provenance_digest(),
        hold_provenance_digest=hold_transition.provenance_digest(),
        first_receptor_digest=step_one.receptor_digest,
        hold_receptor_digest=step_two.receptor_digest,
        step_one=step_one,
        step_two=step_two,
    )


def _logical_sampling_digest(field: SensorMCMField, orientation: int) -> str:
    payload = []
    for neuron in field.layer.neurons:
        target_logical = int(neuron.neuron_id.rsplit("n", 1)[1])
        for sample in neuron.perception.local_samples:
            source_id = sample.sample_id.removeprefix("sample.")
            source_logical = int(source_id.rsplit("n", 1)[1])
            payload.append(
                {
                    "target_logical": target_logical,
                    "offset_logical": orientation * sample.relative_position[0],
                    "source_logical": source_logical,
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


def _transformed_ring_field(rotation: int, orientation: int) -> tuple[str, str]:
    first = ReceptorContactFrame(
        modality_id="simulated.contact",
        geometry_id="simulated.ring7.receptor.v1",
        snapshot_id="simulated.receptor.tick.1",
        clock_id="simulated.world",
        window_start_tick=1,
        window_end_tick=2,
        carrier_ids=tuple(f"contact.p{position}" for position in WORLD_POSITIONS),
        values=(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0),
    )
    positions = tuple(
        ((orientation * logical + rotation) % 7,)
        for logical in WORLD_POSITIONS
    )
    field = build_receptor_aligned_mcm_field(
        first,
        positions=positions,
        sample_offsets=((-1,), (1,)),
        dock_id="simulated",
        layer_id="simulated.layer",
        field_id="simulated.field",
        field_geometry_id="simulated.field.ring7.v1",
        periodic_axes=(RING_AXIS,),
    ).advance(first, _field_time(first), receptor_projection_baseline)
    step_one = _logical_sampling_digest(field, orientation)
    second = replace(
        first,
        snapshot_id="simulated.receptor.tick.2",
        window_start_tick=2,
        window_end_tick=3,
    )
    field = field.advance(second, _field_time(second), receptor_projection_baseline)
    return step_one, _logical_sampling_digest(field, orientation)


def _reset_is_clean() -> bool:
    receptor = ReceptorContactFrame(
        modality_id="simulated.contact",
        geometry_id="simulated.ring7.receptor.v1",
        snapshot_id="simulated.receptor.tick.0",
        clock_id="simulated.world",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=tuple(f"contact.p{position}" for position in WORLD_POSITIONS),
        values=(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    )
    field = _build_field(receptor, periodic=True)
    return (
        field.layer.tick == 0
        and field.layer.periodic_axes == (RING_AXIS,)
        and all(
            neuron.activation == 0.0
            and neuron.afterimage == 0.0
            and neuron.perception.local_samples == ()
            for neuron in field.layer.neurons
        )
    )


def run_simulated_ring_field_path_probe(
    *,
    position_order: Iterable[int] = WORLD_POSITIONS,
    delta_order: Iterable[int] = WORLD_DELTAS,
    cause_order: Iterable[InterventionCause] = WORLD_CAUSES,
    reverse_neurons: bool = False,
    reverse_offsets: bool = False,
    observer: BranchObserver | None = None,
    _verify_controls: bool = True,
) -> SimulatedRingFieldPathProbeResult:
    """Run the complete passive Methodik-034 comparison."""

    positions = _validated_order(position_order, WORLD_POSITIONS, "position_order")
    deltas = _validated_order(delta_order, WORLD_DELTAS, "delta_order")
    try:
        normalized_causes = tuple(InterventionCause(value) for value in cause_order)
    except (TypeError, ValueError) as exc:
        raise SimulatedRingFieldPathProbeError(
            "cause_order contains an unknown cause"
        ) from exc
    causes = _validated_order(normalized_causes, WORLD_CAUSES, "cause_order")

    branches = []
    for position in positions:
        for delta in deltas:
            for cause in causes:
                branch = _run_branch(
                    int(position),
                    int(delta),
                    cause,  # type: ignore[arg-type]
                    reverse_neurons=reverse_neurons,
                    reverse_offsets=reverse_offsets,
                )
                before = branch.digest()
                if observer is not None:
                    observer(branch)
                if branch.digest() != before:
                    raise SimulatedRingFieldPathProbeError(
                        "observer changed an immutable branch observation"
                    )
                branches.append(branch)
    canonical_branches = tuple(
        sorted(
            branches,
            key=lambda item: (item.start_position, item.delta, item.cause),
        )
    )
    by_key = {
        (branch.start_position, branch.delta, branch.cause): branch
        for branch in canonical_branches
    }
    cause_pairs = []
    for position in WORLD_POSITIONS:
        for delta in WORLD_DELTAS:
            external = by_key[(position, delta, "external")]
            effector = by_key[(position, delta, "effector")]
            cause_pairs.append(
                SimulatedRingFieldCausePair(
                    start_position=position,
                    delta=delta,
                    first_provenance_distinct=(
                        external.first_provenance_digest
                        != effector.first_provenance_digest
                    ),
                    hold_provenance_distinct=(
                        external.hold_provenance_digest
                        != effector.hold_provenance_digest
                    ),
                    first_receptor_equal=(
                        external.first_receptor_digest
                        == effector.first_receptor_digest
                    ),
                    hold_receptor_equal=(
                        external.hold_receptor_digest
                        == effector.hold_receptor_digest
                    ),
                    step_one_equal=external.step_one.digest() == effector.step_one.digest(),
                    step_two_equal=external.step_two.digest() == effector.step_two.digest(),
                )
            )

    reference_one, reference_two = _transformed_ring_field(0, 1)
    transformations = []
    for orientation in (1, -1):
        for rotation in WORLD_POSITIONS:
            step_one, step_two = _transformed_ring_field(rotation, orientation)
            transformations.append(
                SimulatedRingFieldTransformObservation(
                    rotation=rotation,
                    orientation=orientation,
                    step_one_digest=step_one,
                    step_two_digest=step_two,
                    step_one_equals_reference=step_one == reference_one,
                    step_two_equals_reference=step_two == reference_two,
                )
            )

    source_six_count = 0
    source_zero_count = 0
    inactive_count = 0
    for branch in canonical_branches:
        active = [
            sample
            for sample in branch.step_two.wrap_samples
            if sample.activation == 1.0
        ]
        if not active:
            inactive_count += 1
        for sample in active:
            if sample.target_position == 0 and sample.source_position == 6:
                source_six_count += 1
            if sample.target_position == 6 and sample.source_position == 0:
                source_zero_count += 1

    historical = run_simulated_world_mcm_path_probe(_verify_controls=False)
    historical_digest = replace(
        historical,
        observer_is_neutral=True,
        order_is_neutral=True,
    ).digest()
    provisional = SimulatedRingFieldPathProbeResult(
        branches=canonical_branches,
        cause_pairs=tuple(cause_pairs),
        transformations=tuple(transformations),
        historical_open_digest_unchanged=historical_digest == METHODIK_031_OPEN_DIGEST,
        all_steps_have_two_wrap_samples=all(
            branch.step_one.only_two_wrap_samples_differ
            and branch.step_two.only_two_wrap_samples_differ
            for branch in canonical_branches
        ),
        step_one_wraps_are_initial_zero=all(
            sample.source_tick == 0
            and sample.activation == 0.0
            and sample.afterimage == 0.0
            for branch in canonical_branches
            for sample in branch.step_one.wrap_samples
        ),
        active_source_six_count=source_six_count,
        active_source_zero_count=source_zero_count,
        inactive_branch_count=inactive_count,
        active_wrap_counts_exact=(
            source_six_count == 6
            and source_zero_count == 6
            and inactive_count == 30
        ),
        all_fast_states_equal=all(
            branch.step_one.fast_state_equal and branch.step_two.fast_state_equal
            for branch in canonical_branches
        ),
        all_full_digests_geometry_distinct=all(
            branch.step_one.full_window_digests_distinct
            and branch.step_one.full_constellation_digests_distinct
            and branch.step_one.geometry_ids_distinct
            and branch.step_two.full_window_digests_distinct
            and branch.step_two.full_constellation_digests_distinct
            and branch.step_two.geometry_ids_distinct
            for branch in canonical_branches
        ),
        all_normalized_states_equal=all(
            branch.step_one.normalized_windows_equal
            and branch.step_one.normalized_constellations_equal
            and branch.step_two.normalized_windows_equal
            and branch.step_two.normalized_constellations_equal
            for branch in canonical_branches
        ),
        all_cause_pairs_collapse=all(
            pair.first_provenance_distinct
            and pair.hold_provenance_distinct
            and pair.first_receptor_equal
            and pair.hold_receptor_equal
            and pair.step_one_equal
            and pair.step_two_equal
            for pair in cause_pairs
        ),
        all_transformations_equivariant=all(
            item.step_one_equals_reference and item.step_two_equals_reference
            for item in transformations
        ),
        reset_is_clean=_reset_is_clean(),
        observer_is_neutral=False,
        order_is_neutral=False,
        repeated_run_is_neutral=False,
    )
    if not _verify_controls:
        return provisional

    reference = run_simulated_ring_field_path_probe(_verify_controls=False)
    repeated = run_simulated_ring_field_path_probe(_verify_controls=False)
    passive_observer = run_simulated_ring_field_path_probe(
        observer=lambda branch: None,
        _verify_controls=False,
    )
    collected: list[SimulatedRingFieldBranchObservation] = []
    collecting = run_simulated_ring_field_path_probe(
        observer=collected.append,
        _verify_controls=False,
    )
    reversed_order = run_simulated_ring_field_path_probe(
        position_order=reversed(WORLD_POSITIONS),
        delta_order=reversed(WORLD_DELTAS),
        cause_order=reversed(WORLD_CAUSES),
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
            and len(collected) == 42
        ),
        order_is_neutral=current_digest == reference_digest == reversed_order.digest(),
        repeated_run_is_neutral=current_digest == reference_digest == repeated.digest(),
    )


def simulated_ring_field_path_public_roles() -> tuple[tuple[str, ...], ...]:
    classes = (
        RingWrapSampleObservation,
        RingFieldPathStepComparison,
        SimulatedRingFieldBranchObservation,
        SimulatedRingFieldCausePair,
        SimulatedRingFieldTransformObservation,
        SimulatedRingFieldPathProbeResult,
    )
    return tuple(tuple(item.name for item in fields(cls)) for cls in classes)
