"""Passive locally continuous deformation world for the unchanged MCM field."""

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


class LocalDeformationWorldError(ValueError):
    """Raised when the deformation world violates its preregistration."""


GROUP_IDS = tuple(f"g{index}" for index in range(8))
STAGE_IDS = tuple(f"d{index}" for index in range(6))
HOLDOUT_POSITIONS = (2, 6, 10)
ORDER_VARIANTS = ("forward", "reverse")
WORLD_VARIANTS = ("a", "b")
FORM_ANCHORS = {
    "f0": ((0, 1), (4, 3), (8, 9), (12, 11)),
    "f1": ((0, 0), (4, 6), (8, 8), (12, 12)),
    "f2": ((0, 2), (4, 4), (8, 10), (12, 12)),
    "f3": ((0, 0), (4, 4), (8, 6), (12, 12)),
}
FORBIDDEN_DEFORMATION_RUNTIME_ROLES = frozenset(
    {
        "group_id",
        "stage_id",
        "form_id",
        "anchor_id",
        "holdout_position",
        "expected_exit",
        "interpolation_weight",
        "switch_time",
        "reward",
    }
)

_STAGE_X = {
    "d0": (),
    "d1": (0,),
    "d2": (0, 12),
    "d3": (0, 4, 8),
    "d4": (0, 4, 8, 12),
}
_OCCLUSION_TICKS = (3, 5, 8)
_GAP_TICKS = (3, 6, 9)
_GRID_COLUMNS = 13
_CLOCK_ID = "organism.local_deformation_world"
_RECEPTOR_GEOMETRY_ID = "visual.local_columns.13.v1"
_CARRIER_IDS = tuple(f"visual.column.{index}" for index in range(_GRID_COLUMNS))
_SAMPLE_OFFSETS = ((-1,), (1,))


@dataclass(frozen=True, slots=True)
class DeformationContact:
    ingress: int
    exit: int
    occlusion_ticks: int
    gap_ticks: int
    pixel_value: int

    def __post_init__(self) -> None:
        if self.ingress not in range(_GRID_COLUMNS):
            raise LocalDeformationWorldError("contact ingress outside world")
        if self.exit not in range(_GRID_COLUMNS):
            raise LocalDeformationWorldError("contact exit outside world")
        if self.occlusion_ticks <= 0 or self.gap_ticks <= 0:
            raise LocalDeformationWorldError("contact durations must be positive")


@dataclass(frozen=True, slots=True)
class LocalDeformationObservation:
    group_id: str
    stage_id: str
    world_variant: str
    order_variant: str
    duration_shift: int
    holdout_ingress: int
    holdout_exit: int
    target_form: str
    completed_contacts: int
    identifiable_holdout: bool
    local_pairing_valid: bool
    first_tick: int
    last_tick: int
    pre_holdout_layer_digest: str
    pre_holdout_snapshot_digest: str
    pre_holdout_activation: tuple[float, ...]
    pre_holdout_afterimage: tuple[float, ...]
    receptor_sequence_digest: str
    continuous_state: bool

    def __post_init__(self) -> None:
        if self.group_id not in GROUP_IDS:
            raise LocalDeformationWorldError("unknown group")
        if self.stage_id not in STAGE_IDS:
            raise LocalDeformationWorldError("unknown stage")
        if self.world_variant not in WORLD_VARIANTS:
            raise LocalDeformationWorldError("unknown world variant")
        if self.order_variant not in ORDER_VARIANTS:
            raise LocalDeformationWorldError("unknown order")
        if self.holdout_ingress not in HOLDOUT_POSITIONS:
            raise LocalDeformationWorldError("invalid holdout ingress")
        if self.target_form not in FORM_ANCHORS:
            raise LocalDeformationWorldError("unknown target form")
        if not self.continuous_state:
            raise LocalDeformationWorldError("world branch must remain continuous")


@dataclass(frozen=True, slots=True)
class LocalDeformationWorldResult:
    observations: tuple[LocalDeformationObservation, ...]
    groups_complete: bool
    stages_complete: bool
    orders_complete: bool
    holdouts_complete: bool
    forms_non_affine: bool
    d5_margins_preserved: bool
    d5_pairing_destroyed: bool
    continuous_state_preserved: bool
    forbidden_metadata_reaches_runtime: bool
    observer_is_neutral: bool
    writes_back: bool
    adds_memory_role: bool
    changes_field_transition: bool

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        if not observations:
            raise LocalDeformationWorldError("result requires observations")
        if observations != tuple(sorted(observations, key=_observation_key)):
            raise LocalDeformationWorldError("observations must use canonical order")
        if self.writes_back or self.adds_memory_role or self.changes_field_transition:
            raise LocalDeformationWorldError("passive world cannot release runtime behavior")
        object.__setattr__(self, "observations", observations)

    def digest(self) -> str:
        encoded = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def _form_value(form_id: str, x: int) -> int:
    anchors = FORM_ANCHORS[form_id]
    for left, right in zip(anchors, anchors[1:]):
        x0, y0 = left
        x1, y1 = right
        if x0 <= x <= x1:
            numerator = y0 * (x1 - x) + y1 * (x - x0)
            if numerator % (x1 - x0):
                raise LocalDeformationWorldError("world value must remain integral")
            return numerator // (x1 - x0)
    raise LocalDeformationWorldError("position outside deformation form")


def _contact(x: int, y: int, index: int, duration_shift: int) -> DeformationContact:
    duration_index = (index + duration_shift) % 3
    return DeformationContact(
        ingress=x,
        exit=y,
        occlusion_ticks=_OCCLUSION_TICKS[duration_index],
        gap_ticks=_GAP_TICKS[duration_index],
        pixel_value=(153, 204, 255)[index % 3],
    )


def _form_contacts(
    form_id: str,
    xs: tuple[int, ...],
    start_index: int,
    duration_shift: int,
    order_variant: str,
) -> tuple[DeformationContact, ...]:
    ordered = xs if order_variant == "forward" else tuple(reversed(xs))
    return tuple(
        _contact(x, _form_value(form_id, x), start_index + index, duration_shift)
        for index, x in enumerate(ordered)
    )


def _d5_contacts(duration_shift: int, order_variant: str) -> tuple[DeformationContact, ...]:
    xs = (0, 4, 8, 12)
    ys = (10, 2, 12, 4)
    pairs = tuple(zip(xs, ys))
    if order_variant == "reverse":
        pairs = tuple(reversed(pairs))
    return tuple(
        _contact(x, y, index, duration_shift)
        for index, (x, y) in enumerate(pairs)
    )


def _branch_history(
    group_id: str,
    stage_id: str,
    world_variant: str,
    order_variant: str,
    duration_shift: int,
) -> tuple[tuple[DeformationContact, ...], str, bool]:
    if group_id == "g7":
        if stage_id != "d5":
            raise LocalDeformationWorldError("G7 is the D5 pairing control")
        return _d5_contacts(duration_shift, order_variant), "f2", False
    if stage_id == "d5":
        raise LocalDeformationWorldError("D5 belongs only to G7")

    current_x = _STAGE_X[stage_id]
    histories: list[tuple[str, tuple[int, ...]]] = []
    target = "f0"
    if group_id == "g0":
        target = "f0" if world_variant == "a" else "f1"
    elif group_id == "g1":
        target = "f2" if world_variant == "a" else "f3"
    elif group_id == "g2":
        histories.append(("f0" if world_variant == "a" else "f1", (0, 4, 8, 12)))
        target = "f2"
    elif group_id == "g3":
        histories.append(("f1" if world_variant == "a" else "f0", (0, 4, 8, 12)))
        target = "f3"
    elif group_id == "g4":
        histories.extend(
            (
                ("f0" if world_variant == "a" else "f1", (0, 4, 8, 12)),
                ("f2", (0, 4, 8, 12)),
            )
        )
        target = "f3"
    elif group_id == "g5":
        histories.append(("f0" if world_variant == "a" else "f1", (0, 4, 8, 12)))
        target = "f2"
    elif group_id == "g6":
        histories.append(("f0" if world_variant == "a" else "f1", (0, 4, 8, 12)))
        target = "f2"
    else:
        raise LocalDeformationWorldError("unknown history group")

    events: list[DeformationContact] = []
    for form_id, xs in histories:
        events.extend(
            _form_contacts(
                form_id,
                xs,
                len(events),
                (duration_shift + (1 if group_id == "g6" else 0)) % 3,
                order_variant,
            )
        )
    events.extend(
        _form_contacts(
            target,
            current_x,
            len(events),
            duration_shift,
            order_variant,
        )
    )
    return tuple(events), target, True


def _receptor_frame(
    contact: DeformationContact,
    column: int | None,
    frame_index: int,
) -> ReceptorContactFrame:
    values = [0.0] * _GRID_COLUMNS
    if column is not None:
        values[column] = contact.pixel_value / 255.0
    return ReceptorContactFrame(
        modality_id="visual",
        geometry_id=_RECEPTOR_GEOMETRY_ID,
        snapshot_id=f"visual.deformation.{frame_index}",
        clock_id="video.frame",
        window_start_tick=frame_index,
        window_end_tick=frame_index + 1,
        carrier_ids=_CARRIER_IDS,
        values=tuple(values),
    )


@lru_cache(maxsize=1)
def _empty_field():
    reference = _receptor_frame(_contact(0, 1, 0, 0), None, 0)
    return build_shared_mcm_field(
        (reference,),
        {
            "visual": ReceptorDockAnatomy(
                "visual",
                "dock.visual",
                tuple((column,) for column in range(_GRID_COLUMNS)),
            )
        },
        sample_offsets=_SAMPLE_OFFSETS,
        geometry_id="organism.local_deformation.grid.v1",
    )


@lru_cache(maxsize=1)
def _distributor() -> ReceptorDistributor:
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock("dock.visual", "visual", _RECEPTOR_GEOMETRY_ID))
    return distributor


def _columns(
    contact: DeformationContact,
    *,
    include_exit: bool = True,
) -> tuple[int | None, ...]:
    ingress = (contact.ingress, contact.ingress)
    hidden = (None,) * contact.occlusion_ticks
    exit_columns = (contact.exit, contact.exit)
    gap = (None,) * contact.gap_ticks
    return ingress + hidden + (exit_columns if include_exit else ()) + (gap if include_exit else ())


def _advance_frame(field, contact, column, frame_index: int, chain: bytes):
    receptor_frame = _receptor_frame(contact, column, frame_index)
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
def _prefix_state(events: tuple[DeformationContact, ...]):
    if not events:
        return _empty_field(), 0, hashlib.sha256(b"").digest()
    field, frame_index, chain = _prefix_state(events[:-1])
    for column in _columns(events[-1]):
        field, frame_index, chain = _advance_frame(
            field, events[-1], column, frame_index, chain
        )
    return field, frame_index, chain


def _holdout_identifiable(stage_id: str, ingress: int) -> bool:
    return stage_id == "d4" or (stage_id == "d3" and ingress in (2, 6))


def _run_branch(
    group_id: str,
    stage_id: str,
    world_variant: str,
    order_variant: str,
    duration_shift: int,
    holdout_ingress: int,
) -> LocalDeformationObservation:
    events, target_form, pairing_valid = _branch_history(
        group_id, stage_id, world_variant, order_variant, duration_shift
    )
    holdout = _contact(
        holdout_ingress,
        _form_value(target_form, holdout_ingress),
        len(events),
        duration_shift,
    )
    field, frame_index, chain = _prefix_state(events)
    for column in _columns(holdout, include_exit=False):
        field, frame_index, chain = _advance_frame(
            field, holdout, column, frame_index, chain
        )
    snapshot = field.snapshot()
    layer_digest = field.layer.digest()
    snapshot_digest = snapshot.digest()
    activation = snapshot.activation
    afterimage = snapshot.afterimage
    for column in (holdout.exit, holdout.exit) + (None,) * holdout.gap_ticks:
        field, frame_index, chain = _advance_frame(
            field, holdout, column, frame_index, chain
        )
    return LocalDeformationObservation(
        group_id=group_id,
        stage_id=stage_id,
        world_variant=world_variant,
        order_variant=order_variant,
        duration_shift=duration_shift,
        holdout_ingress=holdout_ingress,
        holdout_exit=holdout.exit,
        target_form=target_form,
        completed_contacts=len(events),
        identifiable_holdout=_holdout_identifiable(stage_id, holdout_ingress),
        local_pairing_valid=pairing_valid,
        first_tick=0,
        last_tick=frame_index,
        pre_holdout_layer_digest=layer_digest,
        pre_holdout_snapshot_digest=snapshot_digest,
        pre_holdout_activation=activation,
        pre_holdout_afterimage=afterimage,
        receptor_sequence_digest=chain.hex(),
        continuous_state=True,
    )


def _observation_key(item: LocalDeformationObservation) -> tuple[object, ...]:
    return (
        item.group_id,
        item.stage_id,
        item.world_variant,
        item.order_variant,
        item.duration_shift,
        item.holdout_ingress,
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


def _forms_are_non_affine() -> bool:
    return all(
        2 * anchors[1][1] != anchors[0][1] + anchors[2][1]
        for anchors in FORM_ANCHORS.values()
    )


@lru_cache(maxsize=1)
def _canonical_world_result() -> LocalDeformationWorldResult:
    observations = []
    for group_id in GROUP_IDS:
        stages = ("d5",) if group_id == "g7" else STAGE_IDS[:-1]
        for stage_id in stages:
            variants = WORLD_VARIANTS if group_id in ("g0", "g1", "g5") else ("a",)
            for world_variant in variants:
                for order_variant in ORDER_VARIANTS:
                    duration_shifts = (0, 1) if group_id == "g6" else (0,)
                    for duration_shift in duration_shifts:
                        for ingress in HOLDOUT_POSITIONS:
                            observations.append(
                                _run_branch(
                                    group_id,
                                    stage_id,
                                    world_variant,
                                    order_variant,
                                    duration_shift,
                                    ingress,
                                )
                            )
    ordered = tuple(sorted(observations, key=_observation_key))
    d5_forward, _, _ = _branch_history("g7", "d5", "a", "forward", 0)
    f2 = FORM_ANCHORS["f2"]
    return LocalDeformationWorldResult(
        observations=ordered,
        groups_complete={item.group_id for item in ordered} == set(GROUP_IDS),
        stages_complete={item.stage_id for item in ordered} == set(STAGE_IDS),
        orders_complete={item.order_variant for item in ordered} == set(ORDER_VARIANTS),
        holdouts_complete={item.holdout_ingress for item in ordered} == set(HOLDOUT_POSITIONS),
        forms_non_affine=_forms_are_non_affine(),
        d5_margins_preserved=(
            {item.ingress for item in d5_forward} == {x for x, _ in f2}
            and {item.exit for item in d5_forward} == {y for _, y in f2}
        ),
        d5_pairing_destroyed={(item.ingress, item.exit) for item in d5_forward} != set(f2),
        continuous_state_preserved=all(
            item.first_tick == 0 and item.last_tick > 0 for item in ordered
        ),
        forbidden_metadata_reaches_runtime=bool(
            _runtime_role_names() & FORBIDDEN_DEFORMATION_RUNTIME_ROLES
        ),
        observer_is_neutral=True,
        writes_back=False,
        adds_memory_role=False,
        changes_field_transition=False,
    )


DeformationWorldObserver = Callable[[LocalDeformationObservation], object]


def run_local_deformation_world_probe(
    *,
    groups: Iterable[str] = GROUP_IDS,
    observer: DeformationWorldObserver | None = None,
) -> LocalDeformationWorldResult:
    """Run the canonical passive deformation world without field changes."""

    selected = tuple(groups)
    if len(selected) != len(GROUP_IDS) or set(selected) != set(GROUP_IDS):
        raise LocalDeformationWorldError("groups must contain G0 through G7 exactly once")
    result = _canonical_world_result()
    if observer is not None:
        for observation in result.observations:
            before = hash(observation)
            observer(observation)
            if hash(observation) != before:
                raise LocalDeformationWorldError("observer changed immutable observation")
    return result


def local_deformation_world_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            DeformationContact,
            LocalDeformationObservation,
            LocalDeformationWorldResult,
        )
        for item in fields(contract)
    )
