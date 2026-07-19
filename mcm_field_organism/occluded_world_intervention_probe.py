"""Deterministic passive V0/V1/H0/H1/P0 occlusion-world probe."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
from typing import Callable, Iterable

import numpy as np

from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import (
    MCMNeuronDrive,
    MCMNeuronOutput,
    receptor_projection_baseline,
)
from .receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
    from_visual_receptor_state,
)
from .receptor_distributor import (
    ReceptorDistribution,
    ReceptorDistributor,
    ReceptorDock,
)
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMFieldSnapshot,
    build_shared_mcm_field,
)


class OccludedWorldInterventionError(ValueError):
    """Raised when Lauf 095 leaves its preregistered passive boundary."""


INTERVENTION_BRANCH_IDS = ("v0", "v1", "h0", "h1")
OCCLUDED_WORLD_POSITIONS = frozenset({3, 4, 5})
FORBIDDEN_INTERVENTION_RUNTIME_ROLES = frozenset(
    {
        "branch_id",
        "phase_id",
        "event_id",
        "intervention_id",
        "intervention_sign",
        "provenance",
        "consequence",
        "null_consequence",
        "expected_exit",
        "holdout",
        "world_position",
        "world_direction",
        "world_seed",
        "test_order",
        "observer_call_count",
        "noise_id",
    }
)

_GRID_COLUMNS = 9
_CELL_PIXELS = 2
_CLOCK_ID = "organism.occluded_intervention"
_GEOMETRY_ID = "organism.occluded_intervention.grid.v1"
_SAMPLE_OFFSETS = ((0, -1, 0), (0, 1, 0))


@dataclass(frozen=True, slots=True)
class OccludedInterventionWorldState:
    tick: int
    position: int
    direction: int

    def __post_init__(self) -> None:
        if isinstance(self.tick, bool) or not isinstance(self.tick, int) or self.tick < 0:
            raise OccludedWorldInterventionError("tick must be a non-negative integer")
        if (
            isinstance(self.position, bool)
            or not isinstance(self.position, int)
            or self.position not in range(_GRID_COLUMNS)
        ):
            raise OccludedWorldInterventionError("position lies outside the world")
        if self.direction not in (-1, 1):
            raise OccludedWorldInterventionError("direction must be -1 or +1")


@dataclass(frozen=True, slots=True)
class OccludedInterventionFrame:
    frame_index: int
    world_position: int
    world_direction: int
    visible_contact: int | None
    receptor_digest: str
    field_digest: str
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class OccludedInterventionBranch:
    branch_id: str
    intervention_sign: int
    frames: tuple[OccludedInterventionFrame, ...]
    branch_digest: str

    def __post_init__(self) -> None:
        if self.branch_id not in INTERVENTION_BRANCH_IDS:
            raise OccludedWorldInterventionError("unknown intervention branch")
        if self.intervention_sign not in (-1, 1):
            raise OccludedWorldInterventionError("intervention sign must be -1 or +1")


@dataclass(frozen=True, slots=True)
class ObserverProvenance:
    event_id: str
    branch_id: str
    completed_branch_digest: str


@dataclass(frozen=True, slots=True)
class OccludedWorldInterventionResult:
    branches: tuple[OccludedInterventionBranch, ...]
    observer_provenance: tuple[ObserverProvenance, ...]
    null_consequence_preserves_direction: bool
    reversal_uses_same_world_rule: bool
    visible_consequence_reaches_current_field: bool
    hidden_consequence_remains_contact_free: bool
    holdouts_follow_world_state: bool
    mirrored_branches_are_equivariant: bool
    paired_budgets_equal: bool
    receptor_projection_explains_all_field_states: bool
    provenance_is_observer_only: bool
    recontact_carries_no_event_id: bool
    observer_is_neutral: bool
    writes_back: bool
    adds_memory_role: bool
    changes_field_transition: bool
    adds_noise: bool
    adds_variance: bool
    adds_rest_dynamics: bool

    def __post_init__(self) -> None:
        expected = tuple(sorted(INTERVENTION_BRANCH_IDS))
        if tuple(branch.branch_id for branch in self.branches) != expected:
            raise OccludedWorldInterventionError("branches must be complete and canonical")
        if any(
            (
                self.writes_back,
                self.adds_memory_role,
                self.changes_field_transition,
                self.adds_noise,
                self.adds_variance,
                self.adds_rest_dynamics,
            )
        ):
            raise OccludedWorldInterventionError(
                "passive intervention probe cannot release new behavior"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _config() -> VisualGridConfig:
    return VisualGridConfig(
        source_width=_GRID_COLUMNS * _CELL_PIXELS,
        source_height=_CELL_PIXELS,
        grid_columns=_GRID_COLUMNS,
        grid_rows=1,
        frames_per_second=10.0,
    )


def _positions() -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (0, column, channel)
        for column in range(_GRID_COLUMNS)
        for channel in range(3)
    )


def _image(position: int, config: VisualGridConfig) -> np.ndarray:
    frame = np.zeros(
        (config.source_height, config.source_width, 3),
        dtype=np.uint8,
    )
    if position not in OCCLUDED_WORLD_POSITIONS:
        start = position * _CELL_PIXELS
        frame[:, start : start + _CELL_PIXELS, 0] = 255
    return frame


def _new_field(config: VisualGridConfig):
    receptor = LocalChannelGridReceptor(config)
    reference = from_visual_receptor_state(
        receptor.analyze(
            np.zeros((config.source_height, config.source_width, 3), dtype=np.uint8),
            frame_index=0,
        )
    )
    anatomy = ReceptorDockAnatomy(
        modality_id="visual",
        dock_id="dock.visual",
        positions=_positions(),
    )
    field = build_shared_mcm_field(
        (reference,),
        {"visual": anatomy},
        sample_offsets=_SAMPLE_OFFSETS,
        geometry_id=_GEOMETRY_ID,
    )
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock("dock.visual", "visual", config.geometry_id))
    return receptor, field, distributor


def _step(state: OccludedInterventionWorldState, sign: int) -> OccludedInterventionWorldState:
    if sign not in (-1, 1):
        raise OccludedWorldInterventionError("world sign must be -1 or +1")
    direction = sign * state.direction
    return OccludedInterventionWorldState(
        tick=state.tick + 1,
        position=state.position + direction,
        direction=direction,
    )


def _states(branch_id: str) -> tuple[OccludedInterventionWorldState, ...]:
    if branch_id == "v0":
        initial = OccludedInterventionWorldState(0, 1, 1)
        return initial, _step(initial, 1)
    if branch_id == "v1":
        initial = OccludedInterventionWorldState(0, 1, 1)
        return initial, _step(initial, -1)
    if branch_id not in ("h0", "h1"):
        raise OccludedWorldInterventionError("unknown intervention branch")

    states = [OccludedInterventionWorldState(0, 2, 1)]
    states.append(_step(states[-1], 1))
    states.append(_step(states[-1], 1))
    states.append(_step(states[-1], 1 if branch_id == "h0" else -1))
    states.append(_step(states[-1], 1))
    states.append(_step(states[-1], 1))
    return tuple(states)


def _contact(values: tuple[float, ...]) -> int | None:
    active = [
        position[1]
        for position, value in zip(_positions(), values, strict=True)
        if value != 0.0
    ]
    if len(active) > 1:
        raise OccludedWorldInterventionError(
            "one-row world permits one active receptor carrier"
        )
    return active[0] if active else None


def _run_branch(branch_id: str) -> OccludedInterventionBranch:
    config = _config()
    receptor, field, distributor = _new_field(config)
    frames = []

    for frame_index, world in enumerate(_states(branch_id)):
        receptor_state = receptor.analyze(
            _image(world.position, config),
            frame_index=frame_index,
        )
        receptor_frame = from_visual_receptor_state(receptor_state)
        distribution = distributor.distribute(
            (receptor_frame,),
            CommonFieldTime(
                _CLOCK_ID,
                frame_index * 10,
                (frame_index + 1) * 10,
            ),
        )
        field = field.advance(distribution, receptor_projection_baseline)
        snapshot = field.snapshot()
        frames.append(
            OccludedInterventionFrame(
                frame_index=frame_index,
                world_position=world.position,
                world_direction=world.direction,
                visible_contact=_contact(receptor_state.channel_values),
                receptor_digest=_digest(
                    (
                        receptor_state.geometry_id,
                        receptor_state.frame_index,
                        receptor_state.channel_values,
                        receptor_state.contact.value,
                    )
                ),
                field_digest=snapshot.digest(),
                activation=snapshot.activation,
                afterimage=snapshot.afterimage,
            )
        )

    frames_tuple = tuple(frames)
    return OccludedInterventionBranch(
        branch_id=branch_id,
        intervention_sign=1 if branch_id in ("v0", "h0") else -1,
        frames=frames_tuple,
        branch_digest=_digest(
            tuple(
                (
                    frame.world_position,
                    frame.world_direction,
                    frame.visible_contact,
                    frame.receptor_digest,
                    frame.field_digest,
                    frame.activation,
                    frame.afterimage,
                )
                for frame in frames_tuple
            )
        ),
    )


def _runtime_roles() -> set[str]:
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


InterventionObserver = Callable[[OccludedInterventionBranch], object]


def run_occluded_world_intervention_probe(
    *,
    branch_order: Iterable[str] = INTERVENTION_BRANCH_IDS,
    observer: InterventionObserver | None = None,
) -> OccludedWorldInterventionResult:
    """Run only the preregistered deterministic causal-transport family."""

    supplied = tuple(branch_order)
    if len(supplied) != len(INTERVENTION_BRANCH_IDS) or set(supplied) != set(
        INTERVENTION_BRANCH_IDS
    ):
        raise OccludedWorldInterventionError(
            "branch_order must contain every branch exactly once"
        )

    observed = []
    observer_neutral = True
    for branch_id in supplied:
        branch = _run_branch(branch_id)
        before = hash(branch)
        if observer is not None:
            observer(branch)
        observer_neutral &= hash(branch) == before
        observed.append(branch)

    branches = tuple(sorted(observed, key=lambda item: item.branch_id))
    by_id = {branch.branch_id: branch for branch in branches}
    v0, v1, h0, h1 = (by_id[item] for item in INTERVENTION_BRANCH_IDS)

    provenance = tuple(
        ObserverProvenance(
            event_id=f"observer.event.{index}",
            branch_id=branch.branch_id,
            completed_branch_digest=branch.branch_digest,
        )
        for index, branch in enumerate(branches)
    )
    duplicate_provenance = tuple(
        ObserverProvenance(
            event_id=f"observer.duplicate.{index}",
            branch_id=branch_id,
            completed_branch_digest=_run_branch(branch_id).branch_digest,
        )
        for index, branch_id in enumerate(sorted(INTERVENTION_BRANCH_IDS))
    )

    all_frames = tuple(frame for branch in branches for frame in branch.frames)
    baseline_exact = all(
        frame.afterimage == tuple(0.0 for _ in frame.afterimage)
        and frame.activation.count(1.0) == (0 if frame.visible_contact is None else 1)
        and sum(frame.activation) == (0.0 if frame.visible_contact is None else 1.0)
        for frame in all_frames
    )
    runtime_roles = _runtime_roles()
    provenance_neutral = (
        all(
            first.completed_branch_digest == second.completed_branch_digest
            for first, second in zip(provenance, duplicate_provenance, strict=True)
        )
        and FORBIDDEN_INTERVENTION_RUNTIME_ROLES.isdisjoint(runtime_roles)
    )

    return OccludedWorldInterventionResult(
        branches=branches,
        observer_provenance=provenance,
        null_consequence_preserves_direction=(
            v0.frames[-1].world_direction == 1
            and h0.frames[3].world_direction == 1
        ),
        reversal_uses_same_world_rule=(
            v1.frames[-1].world_direction == -1
            and h1.frames[3].world_direction == -1
            and v1.frames[-1].world_position == 0
            and h1.frames[3].world_position == 3
        ),
        visible_consequence_reaches_current_field=(
            v0.frames[-1].visible_contact == 2
            and v1.frames[-1].visible_contact == 0
            and v0.frames[-1].activation != v1.frames[-1].activation
        ),
        hidden_consequence_remains_contact_free=(
            h0.frames[3].visible_contact is None
            and h1.frames[3].visible_contact is None
            and h0.frames[3].activation == h1.frames[3].activation
        ),
        holdouts_follow_world_state=(
            tuple(frame.visible_contact for frame in h0.frames[4:]) == (6, 7)
            and tuple(frame.visible_contact for frame in h1.frames[4:]) == (2, 1)
        ),
        mirrored_branches_are_equivariant=(
            tuple(frame.visible_contact for frame in h0.frames[4:])
            == tuple(
                _GRID_COLUMNS - 1 - frame.visible_contact
                for frame in h1.frames[4:]
                if frame.visible_contact is not None
            )
        ),
        paired_budgets_equal=(
            len(v0.frames) == len(v1.frames) == 2
            and len(h0.frames) == len(h1.frames) == 6
            and sum(frame.visible_contact is not None for frame in h0.frames)
            == sum(frame.visible_contact is not None for frame in h1.frames)
            == 3
        ),
        receptor_projection_explains_all_field_states=baseline_exact,
        provenance_is_observer_only=provenance_neutral,
        recontact_carries_no_event_id="event_id" not in runtime_roles,
        observer_is_neutral=observer_neutral,
        writes_back=False,
        adds_memory_role=False,
        changes_field_transition=False,
        adds_noise=False,
        adds_variance=False,
        adds_rest_dynamics=False,
    )


def occluded_world_intervention_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            OccludedInterventionWorldState,
            OccludedInterventionFrame,
            OccludedInterventionBranch,
            ObserverProvenance,
            OccludedWorldInterventionResult,
        )
        for item in fields(contract)
    )
