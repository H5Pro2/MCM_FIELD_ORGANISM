"""Passive occluded-continuation world probe without memory or writeback."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
import math
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


class OccludedContinuationWorldError(ValueError):
    """Raised when the passive world family violates its preregistration."""


WORLD_GROUP_IDS = ("w0", "w1", "w2", "w3", "w4")
WORLD_CASE_IDS = ("base", "holdout.row_channel", "holdout.amplitude")
WORLD_DIRECTIONS = (-1, 1)
FORBIDDEN_RUNTIME_WORLD_ROLES = frozenset(
    {
        "branch_id",
        "case_id",
        "direction",
        "exit_direction",
        "hidden_position",
        "occlusion",
        "world_seed",
        "expected_exit",
        "holdout",
    }
)

_GRID_ROWS = 3
_GRID_COLUMNS = 7
_CELL_PIXELS = 2
_CLOCK_ID = "organism.occluded_world"
_SAMPLE_OFFSETS = (
    (-1, 0, 0),
    (1, 0, 0),
    (0, -1, 0),
    (0, 1, 0),
)


@dataclass(frozen=True, slots=True)
class OccludedWorldCase:
    case_id: str
    row: int
    channel: int
    pixel_value: int

    def __post_init__(self) -> None:
        if self.case_id not in WORLD_CASE_IDS:
            raise OccludedContinuationWorldError("unknown world case")
        if self.row not in range(_GRID_ROWS):
            raise OccludedContinuationWorldError("world row lies outside the grid")
        if self.channel not in range(3):
            raise OccludedContinuationWorldError("world channel lies outside RGB")
        if (
            isinstance(self.pixel_value, bool)
            or not isinstance(self.pixel_value, int)
            or self.pixel_value <= 0
            or self.pixel_value > 255
        ):
            raise OccludedContinuationWorldError(
                "pixel_value must be an integer in 1..255"
            )


@dataclass(frozen=True, slots=True)
class OccludedContinuationBranch:
    group_id: str
    case_id: str
    history_direction: int
    exit_direction: int | None
    alignment_frame_index: int
    first_exit_frame_index: int | None
    history_contacts: tuple[tuple[int, int, int], ...]
    alignment_contact: tuple[int, int, int] | None
    first_exit_contact: tuple[int, int, int] | None
    alignment_layer_digest: str
    alignment_snapshot_digest: str
    alignment_activation: tuple[float, ...]
    alignment_afterimage: tuple[float, ...]
    receptor_sequence_digest: str

    def __post_init__(self) -> None:
        if self.group_id not in WORLD_GROUP_IDS:
            raise OccludedContinuationWorldError("unknown world group")
        if self.case_id not in WORLD_CASE_IDS:
            raise OccludedContinuationWorldError("unknown branch case")
        if self.history_direction not in WORLD_DIRECTIONS:
            raise OccludedContinuationWorldError("invalid history direction")
        if self.exit_direction not in (*WORLD_DIRECTIONS, None):
            raise OccludedContinuationWorldError("invalid exit direction")
        if self.alignment_frame_index < 0:
            raise OccludedContinuationWorldError(
                "alignment frame index must be non-negative"
            )
        if (
            self.first_exit_frame_index is not None
            and self.first_exit_frame_index <= self.alignment_frame_index
        ):
            raise OccludedContinuationWorldError(
                "first exit must follow the alignment boundary"
            )


@dataclass(frozen=True, slots=True)
class OccludedContinuationWorldResult:
    branches: tuple[OccludedContinuationBranch, ...]
    w0_world_dependency_present: bool
    w0_alignment_exact: bool
    w1_dependency_absent: bool
    w2_current_trace_distinct: bool
    w3_short_occlusion_trace_distinct: bool
    w4_contact_free_null_equal: bool
    transformations_equivariant: bool
    holdout_sequences_novel: bool
    current_state_baselines_collide: bool
    finite_leaky_residual_present: bool
    transition_counter_explains_world: bool
    fixed_automaton_explains_world: bool
    exact_replay_absent: bool
    forbidden_metadata_reaches_runtime: bool
    observer_is_neutral: bool
    writes_back: bool
    adds_memory_role: bool
    changes_field_transition: bool

    def __post_init__(self) -> None:
        branches = tuple(self.branches)
        if not branches:
            raise OccludedContinuationWorldError(
                "world result requires observed branches"
            )
        if branches != tuple(
            sorted(
                branches,
                key=lambda item: (
                    item.group_id,
                    item.case_id,
                    item.history_direction,
                    -2 if item.exit_direction is None else item.exit_direction,
                ),
            )
        ):
            raise OccludedContinuationWorldError(
                "world branches must use canonical order"
            )
        if self.writes_back or self.adds_memory_role or self.changes_field_transition:
            raise OccludedContinuationWorldError(
                "passive world probe cannot release runtime behavior"
            )
        object.__setattr__(self, "branches", branches)

    def digest(self) -> str:
        encoded = json.dumps(
            asdict(self),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class _BranchTrace:
    group_id: str
    case: OccludedWorldCase
    history_direction: int
    exit_direction: int | None
    contacts: tuple[tuple[int, int, int] | None, ...]
    layer_digests: tuple[str, ...]
    snapshot_digests: tuple[str, ...]
    activations: tuple[tuple[float, ...], ...]
    afterimages: tuple[tuple[float, ...], ...]
    receptor_sequence_digest: str


_CASES = {
    "base": OccludedWorldCase("base", row=1, channel=0, pixel_value=255),
    "holdout.row_channel": OccludedWorldCase(
        "holdout.row_channel", row=0, channel=1, pixel_value=153
    ),
    "holdout.amplitude": OccludedWorldCase(
        "holdout.amplitude", row=2, channel=2, pixel_value=204
    ),
}


def _validated_order(
    supplied: Iterable[object],
    expected: tuple[object, ...],
    role: str,
) -> tuple[object, ...]:
    result = tuple(supplied)
    if len(result) != len(expected) or set(result) != set(expected):
        raise OccludedContinuationWorldError(
            f"{role} must contain every preregistered value exactly once"
        )
    return result


def _config() -> VisualGridConfig:
    return VisualGridConfig(
        source_width=_GRID_COLUMNS * _CELL_PIXELS,
        source_height=_GRID_ROWS * _CELL_PIXELS,
        grid_columns=_GRID_COLUMNS,
        grid_rows=_GRID_ROWS,
        frames_per_second=10.0,
    )


def _positions(config: VisualGridConfig) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (row, column, channel)
        for row in range(config.grid_rows)
        for column in range(config.grid_columns)
        for channel in range(3)
    )


def _image(
    case: OccludedWorldCase,
    column: int | None,
    config: VisualGridConfig,
) -> np.ndarray:
    frame = np.zeros(
        (config.source_height, config.source_width, 3),
        dtype=np.uint8,
    )
    if column is None:
        return frame
    if column not in range(config.grid_columns):
        raise OccludedContinuationWorldError("visible column lies outside the grid")
    row_start = case.row * _CELL_PIXELS
    column_start = column * _CELL_PIXELS
    frame[
        row_start : row_start + _CELL_PIXELS,
        column_start : column_start + _CELL_PIXELS,
        case.channel,
    ] = case.pixel_value
    return frame


def _columns(
    group_id: str,
    history_direction: int,
    exit_direction: int | None,
) -> tuple[int | None, ...]:
    ingress = (0, 1) if history_direction == 1 else (6, 5)
    if group_id == "w0":
        exit_columns = (5, 6) if history_direction == 1 else (1, 0)
        return ingress + (None, None, None) + exit_columns
    if group_id == "w1":
        if exit_direction is None:
            raise OccludedContinuationWorldError("w1 requires an exit direction")
        exit_columns = (5, 6) if exit_direction == 1 else (1, 0)
        return ingress + (None, None, None) + exit_columns
    if group_id == "w2":
        return tuple(range(7)) if history_direction == 1 else tuple(reversed(range(7)))
    if group_id == "w3":
        exit_columns = (5, 6) if history_direction == 1 else (1, 0)
        return ingress + (None,) + exit_columns
    if group_id == "w4":
        return (None,) * 7
    raise OccludedContinuationWorldError("unknown world group")


def _new_field(config: VisualGridConfig):
    receptor = LocalChannelGridReceptor(config)
    reference_state = receptor.analyze(
        np.zeros((config.source_height, config.source_width, 3), dtype=np.uint8),
        frame_index=0,
    )
    reference = from_visual_receptor_state(reference_state)
    anatomy = ReceptorDockAnatomy(
        modality_id="visual",
        dock_id="dock.visual",
        positions=_positions(config),
    )
    field = build_shared_mcm_field(
        (reference,),
        {"visual": anatomy},
        sample_offsets=_SAMPLE_OFFSETS,
        geometry_id="organism.occluded.grid.v1",
    )
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock("dock.visual", "visual", config.geometry_id)
    )
    return receptor, field, distributor


def _contact_position(
    values: tuple[float, ...],
    positions: tuple[tuple[int, int, int], ...],
) -> tuple[int, int, int] | None:
    active = [position for position, value in zip(positions, values, strict=True) if value]
    if len(active) > 1:
        raise OccludedContinuationWorldError(
            "minimal world permits one active local receptor carrier"
        )
    return active[0] if active else None


def _run_trace(
    group_id: str,
    case: OccludedWorldCase,
    history_direction: int,
    exit_direction: int | None,
) -> _BranchTrace:
    config = _config()
    positions = _positions(config)
    receptor, field, distributor = _new_field(config)
    contacts = []
    layer_digests = []
    snapshot_digests = []
    activations = []
    afterimages = []
    sequence = hashlib.sha256()

    for frame_index, column in enumerate(
        _columns(group_id, history_direction, exit_direction)
    ):
        state = receptor.analyze(
            _image(case, column, config),
            frame_index=frame_index,
        )
        receptor_frame = from_visual_receptor_state(state)
        sequence.update(
            repr(
                (
                    state.geometry_id,
                    state.frame_index,
                    state.channel_values,
                    state.contact.value,
                )
            ).encode("ascii")
        )
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
        contacts.append(_contact_position(state.channel_values, positions))
        layer_digests.append(field.layer.digest())
        snapshot_digests.append(snapshot.digest())
        activations.append(snapshot.activation)
        afterimages.append(snapshot.afterimage)

    return _BranchTrace(
        group_id=group_id,
        case=case,
        history_direction=history_direction,
        exit_direction=exit_direction,
        contacts=tuple(contacts),
        layer_digests=tuple(layer_digests),
        snapshot_digests=tuple(snapshot_digests),
        activations=tuple(activations),
        afterimages=tuple(afterimages),
        receptor_sequence_digest=sequence.hexdigest(),
    )


def _first_equal_hidden_index(first: _BranchTrace, second: _BranchTrace) -> int:
    for index, (first_digest, second_digest) in enumerate(
        zip(first.layer_digests, second.layer_digests, strict=True)
    ):
        if (
            index >= 2
            and first.contacts[index] is None
            and second.contacts[index] is None
            and first_digest == second_digest
        ):
            return index
    raise OccludedContinuationWorldError(
        "preregistered branches never reach exact hidden-state alignment"
    )


def _declared_alignment_index(
    group_id: str,
    first: _BranchTrace,
    second: _BranchTrace,
) -> int:
    if group_id in ("w0", "w1"):
        return _first_equal_hidden_index(first, second)
    if group_id == "w2":
        return 3
    if group_id == "w3":
        return 2
    return 3


def _branch_observation(
    trace: _BranchTrace,
    alignment_index: int,
) -> OccludedContinuationBranch:
    first_exit_index = next(
        (
            index
            for index in range(alignment_index + 1, len(trace.contacts))
            if trace.contacts[index] is not None
        ),
        None,
    )
    history_contacts = tuple(
        contact for contact in trace.contacts[:2] if contact is not None
    )
    return OccludedContinuationBranch(
        group_id=trace.group_id,
        case_id=trace.case.case_id,
        history_direction=trace.history_direction,
        exit_direction=trace.exit_direction,
        alignment_frame_index=alignment_index,
        first_exit_frame_index=first_exit_index,
        history_contacts=history_contacts,
        alignment_contact=trace.contacts[alignment_index],
        first_exit_contact=(
            None if first_exit_index is None else trace.contacts[first_exit_index]
        ),
        alignment_layer_digest=trace.layer_digests[alignment_index],
        alignment_snapshot_digest=trace.snapshot_digests[alignment_index],
        alignment_activation=trace.activations[alignment_index],
        alignment_afterimage=trace.afterimages[alignment_index],
        receptor_sequence_digest=trace.receptor_sequence_digest,
    )


def _mirror_contact(
    contact: tuple[int, int, int] | None,
) -> tuple[int, int, int] | None:
    if contact is None:
        return None
    return contact[0], _GRID_COLUMNS - 1 - contact[1], contact[2]


def _leaky_trace(trace: _BranchTrace, alignment_index: int) -> float:
    value = 0.0
    decay = 0.5
    for contact in trace.contacts[: alignment_index + 1]:
        signed_position = (
            0.0
            if contact is None
            else (2.0 * contact[1] / (_GRID_COLUMNS - 1)) - 1.0
        )
        value = decay * value + signed_position
    return value


def _motion_sign(trace: _BranchTrace) -> int:
    contacts = [contact for contact in trace.contacts[:2] if contact is not None]
    if len(contacts) != 2:
        raise OccludedContinuationWorldError(
            "motion baseline requires two visible history contacts"
        )
    delta = contacts[1][1] - contacts[0][1]
    return 1 if delta > 0 else -1


def _exit_sign(trace: _BranchTrace, alignment_index: int) -> int:
    contact = next(
        contact
        for contact in trace.contacts[alignment_index + 1 :]
        if contact is not None
    )
    return 1 if contact[1] > (_GRID_COLUMNS - 1) / 2 else -1


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


WorldObserver = Callable[[OccludedContinuationBranch], object]


def run_occluded_continuation_world_probe(
    *,
    case_order: Iterable[str] = WORLD_CASE_IDS,
    direction_order: Iterable[int] = WORLD_DIRECTIONS,
    observer: WorldObserver | None = None,
) -> OccludedContinuationWorldResult:
    """Run only the preregistered outer world and passive leak observer."""

    cases = tuple(
        _CASES[case_id]
        for case_id in _validated_order(case_order, WORLD_CASE_IDS, "case_order")
    )
    supplied_directions = _validated_order(
        direction_order,
        WORLD_DIRECTIONS,
        "direction_order",
    )
    if any(
        isinstance(direction, bool) or not isinstance(direction, int)
        for direction in supplied_directions
    ):
        raise OccludedContinuationWorldError(
            "direction_order must contain integer directions"
        )
    directions = tuple(supplied_directions)
    traces: list[_BranchTrace] = []
    observations: list[OccludedContinuationBranch] = []
    by_group_case: dict[tuple[str, str], list[_BranchTrace]] = {}

    for case in cases:
        for group_id in ("w0", "w2", "w3", "w4"):
            group_traces = [
                _run_trace(
                    group_id,
                    case,
                    direction,
                    direction if group_id != "w4" else None,
                )
                for direction in directions
            ]
            traces.extend(group_traces)
            by_group_case[(group_id, case.case_id)] = group_traces
        w1_traces = [
            _run_trace("w1", case, history_direction, exit_direction)
            for history_direction in directions
            for exit_direction in directions
        ]
        traces.extend(w1_traces)
        by_group_case[("w1", case.case_id)] = w1_traces

    alignments: dict[tuple[str, str], int] = {}
    for key, group_traces in by_group_case.items():
        group_id, _ = key
        negative = next(
            trace for trace in group_traces if trace.history_direction == -1
        )
        positive = next(
            trace for trace in group_traces if trace.history_direction == 1
        )
        alignments[key] = _declared_alignment_index(
            group_id,
            negative,
            positive,
        )

    observer_neutral = True
    for trace in traces:
        observation = _branch_observation(
            trace,
            alignments[(trace.group_id, trace.case.case_id)],
        )
        before = hash(observation)
        if observer is not None:
            observer(observation)
        observer_neutral &= hash(observation) == before
        observations.append(observation)

    ordered = tuple(
        sorted(
            observations,
            key=lambda item: (
                item.group_id,
                item.case_id,
                item.history_direction,
                -2 if item.exit_direction is None else item.exit_direction,
            ),
        )
    )

    w0_pairs = [
        by_group_case[("w0", case.case_id)]
        for case in cases
    ]
    w0_alignment = all(
        first.layer_digests[alignments[("w0", first.case.case_id)]]
        == second.layer_digests[alignments[("w0", first.case.case_id)]]
        and first.snapshot_digests[alignments[("w0", first.case.case_id)]]
        == second.snapshot_digests[alignments[("w0", first.case.case_id)]]
        for first, second in w0_pairs
    )
    w0_dependency = all(
        _motion_sign(trace)
        == _exit_sign(trace, alignments[("w0", trace.case.case_id)])
        for pair in w0_pairs
        for trace in pair
    )
    w1_independent = all(
        {
            trace.exit_direction
            for trace in by_group_case[("w1", case.case_id)]
            if trace.history_direction == direction
        }
        == set(WORLD_DIRECTIONS)
        for case in cases
        for direction in WORLD_DIRECTIONS
    )
    w2_distinct = all(
        pair[0].layer_digests[3] != pair[1].layer_digests[3]
        for pair in (
            by_group_case[("w2", case.case_id)] for case in cases
        )
    )
    w3_distinct = all(
        pair[0].layer_digests[2] != pair[1].layer_digests[2]
        for pair in (
            by_group_case[("w3", case.case_id)] for case in cases
        )
    )
    w4_equal = all(
        pair[0].layer_digests == pair[1].layer_digests
        for pair in (
            by_group_case[("w4", case.case_id)] for case in cases
        )
    )
    equivariant = all(
        tuple(_mirror_contact(contact) for contact in pair[0].contacts)
        == pair[1].contacts
        for pair in w0_pairs
    )
    w0_traces = [trace for pair in w0_pairs for trace in pair]
    sequence_digests = {
        trace.receptor_sequence_digest for trace in w0_traces
    }
    holdouts_novel = len(sequence_digests) == len(w0_traces)
    current_collide = all(
        first.contacts[index] is None
        and second.contacts[index] is None
        and first.activations[index] == second.activations[index]
        and first.afterimages[index] == second.afterimages[index]
        for first, second in w0_pairs
        for index in (alignments[("w0", first.case.case_id)],)
    )
    leaky_residual = all(
        not math.isclose(
            _leaky_trace(first, alignments[("w0", first.case.case_id)]),
            _leaky_trace(second, alignments[("w0", first.case.case_id)]),
            rel_tol=0.0,
            abs_tol=0.0,
        )
        for first, second in w0_pairs
    )
    transition_explains = w0_dependency
    automaton_explains = w0_dependency

    metadata_leak = bool(
        _runtime_role_names() & FORBIDDEN_RUNTIME_WORLD_ROLES
    )

    return OccludedContinuationWorldResult(
        branches=ordered,
        w0_world_dependency_present=w0_dependency,
        w0_alignment_exact=w0_alignment,
        w1_dependency_absent=w1_independent,
        w2_current_trace_distinct=w2_distinct,
        w3_short_occlusion_trace_distinct=w3_distinct,
        w4_contact_free_null_equal=w4_equal,
        transformations_equivariant=equivariant,
        holdout_sequences_novel=holdouts_novel,
        current_state_baselines_collide=current_collide,
        finite_leaky_residual_present=leaky_residual,
        transition_counter_explains_world=transition_explains,
        fixed_automaton_explains_world=automaton_explains,
        exact_replay_absent=holdouts_novel,
        forbidden_metadata_reaches_runtime=metadata_leak,
        observer_is_neutral=observer_neutral,
        writes_back=False,
        adds_memory_role=False,
        changes_field_transition=False,
    )


def occluded_continuation_world_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            OccludedWorldCase,
            OccludedContinuationBranch,
            OccludedContinuationWorldResult,
        )
        for item in fields(contract)
    )
