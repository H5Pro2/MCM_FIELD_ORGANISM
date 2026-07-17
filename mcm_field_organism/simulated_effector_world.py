"""Immutable passive world contract from Methodik 030."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from enum import Enum
import hashlib
import json
from typing import Callable, Iterable


class SimulatedEffectorWorldError(ValueError):
    """Raised when the simulated world contract is violated."""


class InterventionCause(str, Enum):
    EXTERNAL = "external"
    EFFECTOR = "effector"


WORLD_POSITIONS = tuple(range(7))
WORLD_DELTAS = (-1, 0, 1)
WORLD_CAUSES = (InterventionCause.EXTERNAL, InterventionCause.EFFECTOR)
INVERSE_SEQUENCE_IDS = ("plus-minus", "minus-plus")
CYCLE_DIRECTIONS = (-1, 1)
RESET_TICKS = (0, 11)

WorldTransitionObserver = Callable[["SimulatedWorldTransition"], object]


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _tick(value: object, role: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SimulatedEffectorWorldError(
            f"{role} must be a non-negative integer"
        )
    return value


def _position(value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value not in WORLD_POSITIONS
    ):
        raise SimulatedEffectorWorldError("position must be an integer in 0..6")
    return value


def _delta(value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value not in WORLD_DELTAS
    ):
        raise SimulatedEffectorWorldError("delta must be one of -1, 0, +1")
    return value


def _cause(value: object) -> InterventionCause:
    if isinstance(value, InterventionCause):
        return value
    try:
        return InterventionCause(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise SimulatedEffectorWorldError("unknown intervention cause") from exc


@dataclass(frozen=True, slots=True)
class SimulatedWorldState:
    tick: int
    position: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "tick", _tick(self.tick, "tick"))
        object.__setattr__(self, "position", _position(self.position))

    def canonical_payload(self) -> dict[str, object]:
        return {"tick": self.tick, "position": self.position}

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class WorldIntervention:
    source_tick: int
    delta: int
    cause: InterventionCause

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_tick",
            _tick(self.source_tick, "source_tick"),
        )
        object.__setattr__(self, "delta", _delta(self.delta))
        object.__setattr__(self, "cause", _cause(self.cause))

    def canonical_payload(self) -> dict[str, object]:
        return {
            "source_tick": self.source_tick,
            "delta": self.delta,
            "cause": self.cause.value,
        }


@dataclass(frozen=True, slots=True)
class SimulatedWorldReceptorFrame:
    source_tick: int
    contact_values: tuple[float, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_tick",
            _tick(self.source_tick, "source_tick"),
        )
        values = tuple(self.contact_values)
        if len(values) != 7 or any(value not in (0.0, 1.0) for value in values):
            raise SimulatedEffectorWorldError(
                "receptor contacts must contain seven binary values"
            )
        if values.count(1.0) != 1:
            raise SimulatedEffectorWorldError(
                "receptor contacts must be exactly one-hot"
            )
        object.__setattr__(self, "contact_values", values)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "source_tick": self.source_tick,
            "contact_values": self.contact_values,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class SimulatedWorldTransition:
    previous_world: SimulatedWorldState
    intervention: WorldIntervention
    next_world: SimulatedWorldState
    effort: int

    def __post_init__(self) -> None:
        if not isinstance(self.previous_world, SimulatedWorldState):
            raise SimulatedEffectorWorldError(
                "previous_world must be a simulated world state"
            )
        if not isinstance(self.intervention, WorldIntervention):
            raise SimulatedEffectorWorldError(
                "intervention must be a world intervention"
            )
        if not isinstance(self.next_world, SimulatedWorldState):
            raise SimulatedEffectorWorldError(
                "next_world must be a simulated world state"
            )
        if self.intervention.source_tick != self.previous_world.tick:
            raise SimulatedEffectorWorldError(
                "intervention source_tick must match the previous world"
            )
        if self.next_world.tick != self.previous_world.tick + 1:
            raise SimulatedEffectorWorldError(
                "next world must advance exactly one tick"
            )
        expected_position = (
            self.previous_world.position + self.intervention.delta
        ) % 7
        if self.next_world.position != expected_position:
            raise SimulatedEffectorWorldError(
                "next position violates the ring translation"
            )
        if (
            isinstance(self.effort, bool)
            or not isinstance(self.effort, int)
            or self.effort != abs(self.intervention.delta)
        ):
            raise SimulatedEffectorWorldError("effort must equal abs(delta)")

    def provenance_payload(self) -> dict[str, object]:
        return {
            "previous_world": self.previous_world.canonical_payload(),
            "intervention": self.intervention.canonical_payload(),
            "next_world": self.next_world.canonical_payload(),
            "effort": self.effort,
        }

    def world_consequence_payload(self) -> dict[str, object]:
        return {
            "previous_world": self.previous_world.canonical_payload(),
            "next_world": self.next_world.canonical_payload(),
        }

    def provenance_digest(self) -> str:
        return _digest(self.provenance_payload())

    def world_consequence_digest(self) -> str:
        return _digest(self.world_consequence_payload())


@dataclass(frozen=True, slots=True)
class SimulatedEffectorResetState:
    world: SimulatedWorldState
    last_cause: str
    last_delta: int
    last_effort: int

    def __post_init__(self) -> None:
        if self.world != SimulatedWorldState(tick=0, position=0):
            raise SimulatedEffectorWorldError(
                "reset world must use tick zero and position zero"
            )
        if (
            self.last_cause != "none"
            or self.last_delta != 0
            or self.last_effort != 0
        ):
            raise SimulatedEffectorWorldError(
                "reset provenance must be neutral"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "world": self.world.canonical_payload(),
            "last_cause": self.last_cause,
            "last_delta": self.last_delta,
            "last_effort": self.last_effort,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def receptor_frame_from_world(
    world: SimulatedWorldState,
) -> SimulatedWorldReceptorFrame:
    if not isinstance(world, SimulatedWorldState):
        raise SimulatedEffectorWorldError(
            "receptor source must be a completed world state"
        )
    return SimulatedWorldReceptorFrame(
        source_tick=world.tick,
        contact_values=tuple(
            1.0 if index == world.position else 0.0
            for index in WORLD_POSITIONS
        ),
    )


def advance_simulated_world(
    previous_world: SimulatedWorldState,
    intervention: WorldIntervention,
    *,
    observer: WorldTransitionObserver | None = None,
) -> SimulatedWorldTransition:
    if not isinstance(previous_world, SimulatedWorldState):
        raise SimulatedEffectorWorldError(
            "previous_world must be a simulated world state"
        )
    if not isinstance(intervention, WorldIntervention):
        raise SimulatedEffectorWorldError(
            "intervention must be a world intervention"
        )
    transition = SimulatedWorldTransition(
        previous_world=previous_world,
        intervention=intervention,
        next_world=SimulatedWorldState(
            tick=previous_world.tick + 1,
            position=(previous_world.position + intervention.delta) % 7,
        ),
        effort=abs(intervention.delta),
    )
    before = transition.provenance_digest()
    if observer is not None:
        observer(transition)
    if transition.provenance_digest() != before:
        raise SimulatedEffectorWorldError(
            "observer changed an immutable world transition"
        )
    return transition


def advance_simulated_world_interventions(
    previous_world: SimulatedWorldState,
    interventions: Iterable[WorldIntervention],
    *,
    observer: WorldTransitionObserver | None = None,
) -> SimulatedWorldTransition:
    items = tuple(interventions)
    if len(items) != 1:
        raise SimulatedEffectorWorldError(
            "one world interval requires exactly one intervention"
        )
    return advance_simulated_world(
        previous_world,
        items[0],
        observer=observer,
    )


def reset_simulated_effector_world(
    previous_world: SimulatedWorldState,
) -> SimulatedEffectorResetState:
    if not isinstance(previous_world, SimulatedWorldState):
        raise SimulatedEffectorWorldError(
            "reset source must be a simulated world state"
        )
    return SimulatedEffectorResetState(
        world=SimulatedWorldState(tick=0, position=0),
        last_cause="none",
        last_delta=0,
        last_effort=0,
    )


@dataclass(frozen=True, slots=True)
class SimulatedEffectorWorldObservation:
    start_position: int
    delta: int
    cause: str
    next_position: int
    effort: int
    provenance_digest: str
    world_consequence_digest: str
    receptor_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class SimulatedEffectorCausePair:
    start_position: int
    delta: int
    provenance_distinct: bool
    world_consequence_equal: bool
    receptor_equal: bool

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class SimulatedEffectorSequenceObservation:
    sequence_id: str
    start_position: int
    deltas: tuple[int, ...]
    end_position: int
    end_tick: int
    total_effort: int
    returned_to_start: bool

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class SimulatedEffectorResetObservation:
    previous_tick: int
    previous_position: int
    reset_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class SimulatedEffectorWorldContractResult:
    observations: tuple[SimulatedEffectorWorldObservation, ...]
    cause_pairs: tuple[SimulatedEffectorCausePair, ...]
    sequences: tuple[SimulatedEffectorSequenceObservation, ...]
    resets: tuple[SimulatedEffectorResetObservation, ...]
    n0_zero_is_stable: bool
    n1_plus_minus_returns: bool
    n2_minus_plus_returns: bool
    n3_positive_cycles_return: bool
    n4_negative_cycles_return: bool
    n5_cause_is_sensor_neutral: bool
    n6_observer_is_neutral: bool
    n7_order_is_neutral: bool
    n8_reset_is_reproducible: bool
    writes_to_mcm: bool = False
    autonomous: bool = False

    def __post_init__(self) -> None:
        if self.writes_to_mcm or self.autonomous:
            raise SimulatedEffectorWorldError(
                "the passive contract cannot write to MCM or act autonomously"
            )
        if (
            len(self.observations) != 42
            or len(self.cause_pairs) != 21
            or len(self.sequences) != 28
            or len(self.resets) != 14
        ):
            raise SimulatedEffectorWorldError(
                "contract result must contain the complete preregistered family"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "observations": [item.canonical_payload() for item in self.observations],
            "cause_pairs": [item.canonical_payload() for item in self.cause_pairs],
            "sequences": [item.canonical_payload() for item in self.sequences],
            "resets": [item.canonical_payload() for item in self.resets],
            "n0_zero_is_stable": self.n0_zero_is_stable,
            "n1_plus_minus_returns": self.n1_plus_minus_returns,
            "n2_minus_plus_returns": self.n2_minus_plus_returns,
            "n3_positive_cycles_return": self.n3_positive_cycles_return,
            "n4_negative_cycles_return": self.n4_negative_cycles_return,
            "n5_cause_is_sensor_neutral": self.n5_cause_is_sensor_neutral,
            "n6_observer_is_neutral": self.n6_observer_is_neutral,
            "n7_order_is_neutral": self.n7_order_is_neutral,
            "n8_reset_is_reproducible": self.n8_reset_is_reproducible,
            "writes_to_mcm": self.writes_to_mcm,
            "autonomous": self.autonomous,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _validated_order(
    values: Iterable[object],
    expected: tuple[object, ...],
    role: str,
) -> tuple[object, ...]:
    result = tuple(values)
    if len(result) != len(expected) or set(result) != set(expected):
        raise SimulatedEffectorWorldError(
            f"{role} must contain each preregistered value exactly once"
        )
    return result


def _run_sequence(
    start_position: int,
    deltas: tuple[int, ...],
    sequence_id: str,
    observer: WorldTransitionObserver | None,
) -> SimulatedEffectorSequenceObservation:
    world = SimulatedWorldState(tick=0, position=start_position)
    total_effort = 0
    for delta in deltas:
        transition = advance_simulated_world(
            world,
            WorldIntervention(
                source_tick=world.tick,
                delta=delta,
                cause=InterventionCause.EXTERNAL,
            ),
            observer=observer,
        )
        world = transition.next_world
        total_effort += transition.effort
    return SimulatedEffectorSequenceObservation(
        sequence_id=sequence_id,
        start_position=start_position,
        deltas=deltas,
        end_position=world.position,
        end_tick=world.tick,
        total_effort=total_effort,
        returned_to_start=world.position == start_position,
    )


def run_simulated_effector_world_contract_probe(
    *,
    position_order: Iterable[int] = WORLD_POSITIONS,
    delta_order: Iterable[int] = WORLD_DELTAS,
    cause_order: Iterable[InterventionCause] = WORLD_CAUSES,
    inverse_order: Iterable[str] = INVERSE_SEQUENCE_IDS,
    cycle_order: Iterable[int] = CYCLE_DIRECTIONS,
    reset_tick_order: Iterable[int] = RESET_TICKS,
    observer: WorldTransitionObserver | None = None,
    _verify_controls: bool = True,
) -> SimulatedEffectorWorldContractResult:
    """Execute the closed passive contract from Methodik 030."""

    position_order = _validated_order(
        position_order,
        WORLD_POSITIONS,
        "position_order",
    )
    delta_order = _validated_order(delta_order, WORLD_DELTAS, "delta_order")
    cause_order = tuple(_cause(value) for value in cause_order)
    cause_order = _validated_order(cause_order, WORLD_CAUSES, "cause_order")
    inverse_order = _validated_order(
        inverse_order,
        INVERSE_SEQUENCE_IDS,
        "inverse_order",
    )
    cycle_order = _validated_order(
        cycle_order,
        CYCLE_DIRECTIONS,
        "cycle_order",
    )
    reset_tick_order = _validated_order(
        reset_tick_order,
        RESET_TICKS,
        "reset_tick_order",
    )

    observations = []
    for position in position_order:
        for delta in delta_order:
            for cause in cause_order:
                transition = advance_simulated_world(
                    SimulatedWorldState(tick=0, position=int(position)),
                    WorldIntervention(
                        source_tick=0,
                        delta=int(delta),
                        cause=cause,
                    ),
                    observer=observer,
                )
                receptor = receptor_frame_from_world(transition.next_world)
                observations.append(
                    SimulatedEffectorWorldObservation(
                        start_position=int(position),
                        delta=int(delta),
                        cause=cause.value,
                        next_position=transition.next_world.position,
                        effort=transition.effort,
                        provenance_digest=transition.provenance_digest(),
                        world_consequence_digest=(
                            transition.world_consequence_digest()
                        ),
                        receptor_digest=receptor.digest(),
                    )
                )

    canonical_observations = tuple(
        sorted(
            observations,
            key=lambda item: (item.start_position, item.delta, item.cause),
        )
    )
    observation_map = {
        (item.start_position, item.delta, item.cause): item
        for item in canonical_observations
    }
    cause_pairs = []
    for position in WORLD_POSITIONS:
        for delta in WORLD_DELTAS:
            external = observation_map[(position, delta, "external")]
            effector = observation_map[(position, delta, "effector")]
            cause_pairs.append(
                SimulatedEffectorCausePair(
                    start_position=position,
                    delta=delta,
                    provenance_distinct=(
                        external.provenance_digest != effector.provenance_digest
                    ),
                    world_consequence_equal=(
                        external.world_consequence_digest
                        == effector.world_consequence_digest
                    ),
                    receptor_equal=(
                        external.receptor_digest == effector.receptor_digest
                    ),
                )
            )

    inverse_deltas = {
        "plus-minus": (1, -1),
        "minus-plus": (-1, 1),
    }
    sequences = []
    for position in position_order:
        for sequence_id in inverse_order:
            sequences.append(
                _run_sequence(
                    int(position),
                    inverse_deltas[str(sequence_id)],
                    f"inverse.{sequence_id}",
                    observer,
                )
            )
        for direction in cycle_order:
            sequences.append(
                _run_sequence(
                    int(position),
                    (int(direction),) * 7,
                    f"cycle.{int(direction):+d}",
                    observer,
                )
            )
    canonical_sequences = tuple(
        sorted(
            sequences,
            key=lambda item: (item.sequence_id, item.start_position),
        )
    )

    resets = []
    for tick in reset_tick_order:
        for position in position_order:
            previous = SimulatedWorldState(tick=int(tick), position=int(position))
            reset = reset_simulated_effector_world(previous)
            resets.append(
                SimulatedEffectorResetObservation(
                    previous_tick=previous.tick,
                    previous_position=previous.position,
                    reset_digest=reset.digest(),
                )
            )
    canonical_resets = tuple(
        sorted(resets, key=lambda item: (item.previous_tick, item.previous_position))
    )

    zero_observations = tuple(
        item for item in canonical_observations if item.delta == 0
    )
    plus_minus = tuple(
        item
        for item in canonical_sequences
        if item.sequence_id == "inverse.plus-minus"
    )
    minus_plus = tuple(
        item
        for item in canonical_sequences
        if item.sequence_id == "inverse.minus-plus"
    )
    positive_cycles = tuple(
        item
        for item in canonical_sequences
        if item.sequence_id == "cycle.+1"
    )
    negative_cycles = tuple(
        item
        for item in canonical_sequences
        if item.sequence_id == "cycle.-1"
    )
    n5 = all(
        item.provenance_distinct
        and item.world_consequence_equal
        and item.receptor_equal
        for item in cause_pairs
    )
    provisional = SimulatedEffectorWorldContractResult(
        observations=canonical_observations,
        cause_pairs=tuple(cause_pairs),
        sequences=canonical_sequences,
        resets=canonical_resets,
        n0_zero_is_stable=all(
            item.next_position == item.start_position and item.effort == 0
            for item in zero_observations
        ),
        n1_plus_minus_returns=all(
            item.returned_to_start
            and item.end_tick == 2
            and item.total_effort == 2
            for item in plus_minus
        ),
        n2_minus_plus_returns=all(
            item.returned_to_start
            and item.end_tick == 2
            and item.total_effort == 2
            for item in minus_plus
        ),
        n3_positive_cycles_return=all(
            item.returned_to_start
            and item.end_tick == 7
            and item.total_effort == 7
            for item in positive_cycles
        ),
        n4_negative_cycles_return=all(
            item.returned_to_start
            and item.end_tick == 7
            and item.total_effort == 7
            for item in negative_cycles
        ),
        n5_cause_is_sensor_neutral=n5,
        n6_observer_is_neutral=False,
        n7_order_is_neutral=False,
        n8_reset_is_reproducible=(
            len({item.reset_digest for item in canonical_resets}) == 1
        ),
    )
    if not _verify_controls:
        return provisional

    reference = run_simulated_effector_world_contract_probe(
        _verify_controls=False,
    )
    passive_observer = run_simulated_effector_world_contract_probe(
        observer=lambda transition: None,
        _verify_controls=False,
    )
    reversed_order = run_simulated_effector_world_contract_probe(
        position_order=reversed(WORLD_POSITIONS),
        delta_order=reversed(WORLD_DELTAS),
        cause_order=reversed(WORLD_CAUSES),
        inverse_order=reversed(INVERSE_SEQUENCE_IDS),
        cycle_order=reversed(CYCLE_DIRECTIONS),
        reset_tick_order=reversed(RESET_TICKS),
        _verify_controls=False,
    )
    current_digest = provisional.digest()
    reference_digest = reference.digest()
    return replace(
        provisional,
        n6_observer_is_neutral=(
            current_digest == reference_digest == passive_observer.digest()
        ),
        n7_order_is_neutral=(
            current_digest == reference_digest == reversed_order.digest()
        ),
    )


def simulated_effector_world_public_roles(
) -> tuple[tuple[str, ...], ...]:
    classes = (
        SimulatedWorldState,
        WorldIntervention,
        SimulatedWorldReceptorFrame,
        SimulatedWorldTransition,
        SimulatedEffectorResetState,
        SimulatedEffectorWorldObservation,
        SimulatedEffectorCausePair,
        SimulatedEffectorSequenceObservation,
        SimulatedEffectorResetObservation,
        SimulatedEffectorWorldContractResult,
    )
    return tuple(tuple(item.name for item in fields(cls)) for cls in classes)
