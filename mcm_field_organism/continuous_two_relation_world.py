"""Continuous passive R0/R1 world without memory or field writeback."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from functools import lru_cache
import hashlib
import json
from typing import Callable, Iterable

from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import (
    MCMNeuronDrive,
    MCMNeuronOutput,
    receptor_projection_baseline,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistribution, ReceptorDistributor, ReceptorDock
from .shared_mcm_field import ReceptorDockAnatomy, SharedMCMFieldSnapshot, build_shared_mcm_field


class ContinuousTwoRelationWorldError(ValueError):
    """Raised when the continuous world violates its preregistration."""


CONTROL_IDS = tuple(f"k{index}" for index in range(8))
EXPERIENCE_LEVELS = (0, 1, 2, 4, 8)
SWITCH_CONTACT_COUNTS = (6, 8, 10)
ORDER_VARIANTS = ("forward", "mirrored", "reversed", "reversed_mirrored")
HOLDOUT_INGRESS_SIGNS = (-1, 1)
RELATION_IDS = ("r0", "r1")
FORBIDDEN_CONTINUOUS_WORLD_RUNTIME_ROLES = frozenset(
    {
        "control_id",
        "experience_count",
        "relation_id",
        "switch_contact_count",
        "order_variant",
        "expected_exit",
        "world_seed",
        "phase",
    }
)

_BASE_ORDER = (1, -1, -1, 1, -1, 1, 1, -1, 1, -1)
_OCCLUSION_TICKS = (3, 5, 8)
_GAP_TICKS = (2, 4, 7)
_HOLDOUT_OCCLUSION_TICKS = (4, 7, 10)
_HOLDOUT_GAP_TICKS = (3, 6, 9)
_GRID_COLUMNS = 7
_CLOCK_ID = "organism.continuous_two_relation_world"
_RECEPTOR_GEOMETRY_ID = "visual.local_columns.v1"
_CARRIER_IDS = tuple(f"visual.column.{index}" for index in range(_GRID_COLUMNS))
_SAMPLE_OFFSETS = ((-1,), (1,))


@dataclass(frozen=True, slots=True)
class ContinuousWorldObservation:
    control_id: str
    experience_count: int
    return_experience_count: int
    switch_contact_count: int
    order_variant: str
    duration_shift: int
    holdout_ingress: int
    holdout_relation: str | None
    holdout_exit: int
    completed_contacts: int
    first_tick: int
    last_tick: int
    pre_holdout_layer_digest: str
    pre_holdout_snapshot_digest: str
    pre_holdout_activation: tuple[float, ...]
    pre_holdout_afterimage: tuple[float, ...]
    receptor_sequence_digest: str
    continuous_state: bool
    observer_cue_present: bool

    def __post_init__(self) -> None:
        if self.control_id not in CONTROL_IDS:
            raise ContinuousTwoRelationWorldError("unknown control")
        if self.order_variant not in ORDER_VARIANTS:
            raise ContinuousTwoRelationWorldError("unknown order variant")
        if self.switch_contact_count not in SWITCH_CONTACT_COUNTS:
            raise ContinuousTwoRelationWorldError("invalid switch contact count")
        if self.holdout_ingress not in HOLDOUT_INGRESS_SIGNS:
            raise ContinuousTwoRelationWorldError("invalid holdout ingress")
        if self.holdout_exit not in HOLDOUT_INGRESS_SIGNS:
            raise ContinuousTwoRelationWorldError("invalid holdout exit")
        if self.holdout_relation not in (*RELATION_IDS, None):
            raise ContinuousTwoRelationWorldError("invalid holdout relation")
        if not self.continuous_state:
            raise ContinuousTwoRelationWorldError("world branch must remain continuous")


@dataclass(frozen=True, slots=True)
class ContinuousTwoRelationWorldResult:
    observations: tuple[ContinuousWorldObservation, ...]
    controls_complete: bool
    experience_levels_complete: bool
    switch_positions_complete: bool
    orders_complete: bool
    holdout_sides_complete: bool
    r0_relation_exact: bool
    r1_relation_exact: bool
    k4_pairing_destroyed: bool
    k2_has_no_new_experience: bool
    k6_has_no_return_experience: bool
    continuous_state_preserved: bool
    forbidden_metadata_reaches_runtime: bool
    observer_is_neutral: bool
    writes_back: bool
    adds_memory_role: bool
    changes_field_transition: bool

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        if not observations:
            raise ContinuousTwoRelationWorldError("result requires observations")
        if observations != tuple(sorted(observations, key=_observation_key)):
            raise ContinuousTwoRelationWorldError("observations must use canonical order")
        if self.writes_back or self.adds_memory_role or self.changes_field_transition:
            raise ContinuousTwoRelationWorldError("passive world cannot release runtime behavior")
        object.__setattr__(self, "observations", observations)

    def digest(self) -> str:
        encoded = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class _Event:
    ingress: int
    relation: str | None
    exit_sign: int
    occlusion_ticks: int
    gap_ticks: int
    pixel_value: int
    cue: bool = False


def _observation_key(item: ContinuousWorldObservation) -> tuple[object, ...]:
    return (
        item.control_id,
        item.experience_count,
        item.return_experience_count,
        item.switch_contact_count,
        item.order_variant,
        item.duration_shift,
        item.holdout_ingress,
    )


def _receptor_frame(event: _Event, column: int | None, frame_index: int) -> ReceptorContactFrame:
    values = [0.0] * _GRID_COLUMNS
    if column is not None:
        values[column] = event.pixel_value / 255.0
    return ReceptorContactFrame(
        modality_id="visual",
        geometry_id=_RECEPTOR_GEOMETRY_ID,
        snapshot_id=f"visual.world.{frame_index}",
        clock_id="video.frame",
        window_start_tick=frame_index,
        window_end_tick=frame_index + 1,
        carrier_ids=_CARRIER_IDS,
        values=tuple(values),
    )


@lru_cache(maxsize=1)
def _empty_field():
    reference_event = _Event(1, "r0", 1, 3, 2, 153)
    reference = _receptor_frame(reference_event, None, 0)
    field = build_shared_mcm_field(
        (reference,),
        {
            "visual": ReceptorDockAnatomy(
                "visual",
                "dock.visual",
                tuple((column,) for column in range(_GRID_COLUMNS)),
            )
        },
        sample_offsets=_SAMPLE_OFFSETS,
        geometry_id="organism.continuous_two_relation.grid.v1",
    )
    return field


@lru_cache(maxsize=1)
def _distributor() -> ReceptorDistributor:
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock("dock.visual", "visual", _RECEPTOR_GEOMETRY_ID))
    return distributor


def _order(variant: str) -> tuple[int, ...]:
    values = _BASE_ORDER
    if "reversed" in variant:
        values = tuple(reversed(values))
    if "mirrored" in variant:
        values = tuple(-value for value in values)
    return values


def _exit_for(relation: str, ingress: int) -> int:
    return ingress if relation == "r0" else -ingress


def _event(ingress: int, relation: str, index: int, duration_shift: int) -> _Event:
    duration_index = (index + duration_shift) % 3
    return _Event(
        ingress=ingress,
        relation=relation,
        exit_sign=_exit_for(relation, ingress),
        occlusion_ticks=_OCCLUSION_TICKS[duration_index],
        gap_ticks=_GAP_TICKS[duration_index],
        pixel_value=(153, 204, 255)[index % 3],
    )


def _holdout(ingress: int, relation: str | None, index: int, cue: bool = False) -> _Event:
    exit_sign = _exit_for(relation, ingress) if relation is not None else (-ingress if index % 2 else ingress)
    return _Event(
        ingress=ingress,
        relation=relation,
        exit_sign=exit_sign,
        occlusion_ticks=_HOLDOUT_OCCLUSION_TICKS[index % 3],
        gap_ticks=_HOLDOUT_GAP_TICKS[index % 3],
        pixel_value=(179, 217, 235)[index % 3],
        cue=cue,
    )


def _branch_events(
    control_id: str,
    experience_count: int,
    return_experience_count: int,
    switch_count: int,
    order_variant: str,
    duration_shift: int,
    holdout_ingress: int,
) -> tuple[tuple[_Event, ...], _Event]:
    order = _order(order_variant)
    events: list[_Event] = []
    if control_id == "k1":
        events.extend(_event(order[i], "r1", i, duration_shift) for i in range(switch_count))
        return tuple(events), _holdout(holdout_ingress, "r1", experience_count)

    events.extend(_event(order[i], "r0", i, duration_shift) for i in range(switch_count))
    if control_id == "k0":
        return tuple(events), _holdout(holdout_ingress, "r0", experience_count)
    if control_id == "k4":
        # Margins remain balanced across mirrored order variants; local pairing does not.
        permuted = tuple(reversed(order))
        events.extend(
            _Event(
                ingress=order[i],
                relation=None,
                exit_sign=permuted[i],
                occlusion_ticks=_OCCLUSION_TICKS[(i + duration_shift) % 3],
                gap_ticks=_GAP_TICKS[(i + duration_shift) % 3],
                pixel_value=(153, 204, 255)[i % 3],
            )
            for i in range(switch_count)
        )
        return tuple(events), _holdout(
            holdout_ingress,
            None,
            ORDER_VARIANTS.index(order_variant),
        )

    new_count = experience_count if control_id in ("k3", "k5", "k7") else 0
    events.extend(
        _event(order[i % len(order)], "r1", switch_count + i, duration_shift)
        for i in range(new_count if control_id != "k7" else 8)
    )
    if control_id in ("k2", "k3", "k5"):
        return tuple(events), _holdout(holdout_ingress, "r1", experience_count, control_id == "k5")

    # K6/K7 include a carried R1 section before the unannounced return to R0.
    if control_id == "k6":
        events.extend(
            _event(order[i % len(order)], "r1", switch_count + i, duration_shift)
            for i in range(8)
        )
    if control_id == "k7":
        events.extend(
            _event(order[i % len(order)], "r0", switch_count + 8 + i, duration_shift)
            for i in range(return_experience_count)
        )
    return tuple(events), _holdout(holdout_ingress, "r0", return_experience_count)


def _columns(event: _Event, *, include_exit: bool = True) -> tuple[int | None, ...]:
    ingress = (0, 1) if event.ingress == 1 else (6, 5)
    cue = ((3,) if event.cue else ())
    hidden = (None,) * event.occlusion_ticks
    exit_columns = (5, 6) if event.exit_sign == 1 else (1, 0)
    gap = (None,) * event.gap_ticks
    return ingress + cue + hidden + (exit_columns if include_exit else ()) + (gap if include_exit else ())


WorldObserver = Callable[[ContinuousWorldObservation], object]


def _advance_frame(field, event: _Event, column: int | None, frame_index: int, chain: bytes):
    receptor_frame = _receptor_frame(event, column, frame_index)
    payload = repr((frame_index, receptor_frame.values)).encode("ascii")
    next_chain = hashlib.sha256(chain + payload).digest()
    distribution = _distributor().distribute(
        (receptor_frame,),
        CommonFieldTime(_CLOCK_ID, frame_index * 10, (frame_index + 1) * 10),
    )
    return (
        field.advance(distribution, receptor_projection_baseline),
        frame_index + 1,
        next_chain,
    )


@lru_cache(maxsize=None)
def _prefix_state(events: tuple[_Event, ...]):
    if not events:
        return _empty_field(), 0, hashlib.sha256(b"").digest()
    field, frame_index, chain = _prefix_state(events[:-1])
    for column in _columns(events[-1]):
        field, frame_index, chain = _advance_frame(
            field,
            events[-1],
            column,
            frame_index,
            chain,
        )
    return field, frame_index, chain


def _run_branch(
    control_id: str,
    experience_count: int,
    return_experience_count: int,
    switch_count: int,
    order_variant: str,
    duration_shift: int,
    holdout_ingress: int,
) -> ContinuousWorldObservation:
    events, holdout = _branch_events(
        control_id,
        experience_count,
        return_experience_count,
        switch_count,
        order_variant,
        duration_shift,
        holdout_ingress,
    )
    field, frame_index, sequence_chain = _prefix_state(events)

    def advance(event: _Event, column: int | None) -> None:
        nonlocal field, frame_index, sequence_chain
        field, frame_index, sequence_chain = _advance_frame(
            field,
            event,
            column,
            frame_index,
            sequence_chain,
        )

    for column in _columns(holdout, include_exit=False):
        advance(holdout, column)
    snapshot = field.snapshot()
    pre_layer_digest = field.layer.digest()
    pre_snapshot_digest = snapshot.digest()
    pre_activation = snapshot.activation
    pre_afterimage = snapshot.afterimage
    for column in ((5, 6) if holdout.exit_sign == 1 else (1, 0)) + (None,) * holdout.gap_ticks:
        advance(holdout, column)

    return ContinuousWorldObservation(
        control_id=control_id,
        experience_count=experience_count,
        return_experience_count=return_experience_count,
        switch_contact_count=switch_count,
        order_variant=order_variant,
        duration_shift=duration_shift,
        holdout_ingress=holdout_ingress,
        holdout_relation=holdout.relation,
        holdout_exit=holdout.exit_sign,
        completed_contacts=len(events),
        first_tick=0,
        last_tick=frame_index,
        pre_holdout_layer_digest=pre_layer_digest,
        pre_holdout_snapshot_digest=pre_snapshot_digest,
        pre_holdout_activation=pre_activation,
        pre_holdout_afterimage=pre_afterimage,
        receptor_sequence_digest=sequence_chain.hex(),
        continuous_state=True,
        observer_cue_present=holdout.cue,
    )


def _runtime_role_names() -> set[str]:
    return {
        item.name
        for contract in (
            ReceptorContactFrame,
            ReceptorDistribution,
            MCMFieldPerception,
            MCMNeuron,
            MCMNeuronDrive,
            MCMNeuronOutput,
            SharedMCMFieldSnapshot,
        )
        for item in fields(contract)
    }


@lru_cache(maxsize=1)
def _canonical_world_result() -> ContinuousTwoRelationWorldResult:
    """Build the immutable canonical matrix once per process."""

    observations: list[ContinuousWorldObservation] = []
    for control_id in CONTROL_IDS:
        levels = EXPERIENCE_LEVELS if control_id in ("k3", "k7") else (0,)
        for level in levels:
            for switch_count in SWITCH_CONTACT_COUNTS:
                for order_variant in ORDER_VARIANTS:
                    for duration_shift in (0, 1):
                        for ingress in HOLDOUT_INGRESS_SIGNS:
                            observation = _run_branch(
                                control_id,
                                level if control_id == "k3" else 0,
                                level if control_id == "k7" else 0,
                                switch_count,
                                order_variant,
                                duration_shift,
                                ingress,
                            )
                            observations.append(observation)

    ordered = tuple(sorted(observations, key=_observation_key))
    ids = {item.control_id for item in ordered}
    k4 = [item for item in ordered if item.control_id == "k4"]
    return ContinuousTwoRelationWorldResult(
        observations=ordered,
        controls_complete=ids == set(CONTROL_IDS),
        experience_levels_complete={item.experience_count for item in ordered if item.control_id == "k3"} == set(EXPERIENCE_LEVELS),
        switch_positions_complete={item.switch_contact_count for item in ordered} == set(SWITCH_CONTACT_COUNTS),
        orders_complete={item.order_variant for item in ordered} == set(ORDER_VARIANTS),
        holdout_sides_complete={item.holdout_ingress for item in ordered} == set(HOLDOUT_INGRESS_SIGNS),
        r0_relation_exact=all(item.holdout_exit == item.holdout_ingress for item in ordered if item.holdout_relation == "r0"),
        r1_relation_exact=all(item.holdout_exit == -item.holdout_ingress for item in ordered if item.holdout_relation == "r1"),
        k4_pairing_destroyed={item.holdout_exit for item in k4 if item.holdout_ingress == 1} == {-1, 1},
        k2_has_no_new_experience=all(item.experience_count == 0 for item in ordered if item.control_id == "k2"),
        k6_has_no_return_experience=all(item.return_experience_count == 0 for item in ordered if item.control_id == "k6"),
        continuous_state_preserved=all(item.continuous_state and item.first_tick == 0 and item.last_tick > 0 for item in ordered),
        forbidden_metadata_reaches_runtime=bool(_runtime_role_names() & FORBIDDEN_CONTINUOUS_WORLD_RUNTIME_ROLES),
        observer_is_neutral=True,
        writes_back=False,
        adds_memory_role=False,
        changes_field_transition=False,
    )


def run_continuous_two_relation_world_probe(
    *,
    controls: Iterable[str] = CONTROL_IDS,
    observer: WorldObserver | None = None,
) -> ContinuousTwoRelationWorldResult:
    """Run the canonical passive world matrix without changing field mechanics."""

    selected = tuple(controls)
    if len(selected) != len(CONTROL_IDS) or set(selected) != set(CONTROL_IDS):
        raise ContinuousTwoRelationWorldError(
            "controls must contain K0 through K7 exactly once"
        )
    result = _canonical_world_result()
    if observer is not None:
        for observation in result.observations:
            before = hash(observation)
            observer(observation)
            if hash(observation) != before:
                raise ContinuousTwoRelationWorldError(
                    "observer changed an immutable world observation"
                )
    return result


def continuous_two_relation_world_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (ContinuousWorldObservation, ContinuousTwoRelationWorldResult)
        for item in fields(contract)
    )
