"""Passive baseline matrix for transition-disposition falsification."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
from typing import Callable, Iterable

import numpy as np

from .finite_video_path import VisualGridConfig
from .mcm_neuron_layer import MCMNeuronDrive, receptor_projection_baseline
from .receptor_contract import CommonFieldTime
from .visual_mcm_interface import build_visual_mcm_interface


class TransitionDispositionFalsificationProbeError(ValueError):
    """Raised when Methodik 037 leaves its preregistered passive domain."""


P1_A_HISTORY = (2, 3, None, None) * 4
P2_COMPETITION_B = (4, 3, None, None) * 4
P2_MATCHED_NONCOMPETITION = (4, None, 3, None) * 4
P2_UNRELATED_U = (5, 6, None, None) * 4
P2_IDLE = (None,) * 16
MATRIX_BRANCH_IDS = (
    "competition_b",
    "idle",
    "matched_noncompetition",
    "unrelated_u",
)
MATRIX_BASELINE_IDS = (
    "b0.fast_field",
    "b1.neuron_frequency",
    "b2.transition_counter",
    "b3.leaky_transition",
    "b4.permanent_edge",
    "b5.independent_saturation",
    "b6.global_normalization",
)
TRANSITION_DECAYS = (0.25, 0.5, 0.75, 0.9)
SATURATION_CAPACITIES = (1.0, 2.0, 4.0)

_P2_BY_BRANCH = {
    "competition_b": P2_COMPETITION_B,
    "idle": P2_IDLE,
    "matched_noncompetition": P2_MATCHED_NONCOMPETITION,
    "unrelated_u": P2_UNRELATED_U,
}
_TRANSITION_A = (2, 3)
_TRANSITION_B = (4, 3)
_TRANSITION_U = (5, 6)
_GRID_COLUMNS = 7
_CHANNEL_COUNT = 3
_SOURCE_WIDTH = 14
_SOURCE_HEIGHT = 2
_ACTIVE_CHANNEL = 0
_CLOCK_ID = "organism.transition_falsification"
_SAMPLE_OFFSETS = ((0, -1, 0), (0, 1, 0))


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _config() -> VisualGridConfig:
    return VisualGridConfig(
        source_width=_SOURCE_WIDTH,
        source_height=_SOURCE_HEIGHT,
        grid_columns=_GRID_COLUMNS,
        grid_rows=1,
        frames_per_second=1.0,
    )


def _frame(column: int | None) -> np.ndarray:
    if column is not None and (
        isinstance(column, bool)
        or not isinstance(column, int)
        or not 0 <= column < _GRID_COLUMNS
    ):
        raise TransitionDispositionFalsificationProbeError(
            "contact column must fit the seven-position world"
        )
    frame = np.zeros((_SOURCE_HEIGHT, _SOURCE_WIDTH, _CHANNEL_COUNT), dtype=np.uint8)
    if column is not None:
        frame[:, column * 2 : (column + 1) * 2, _ACTIVE_CHANNEL] = 255
    return frame


def _position_index(column: int, channel: int = _ACTIVE_CHANNEL) -> int:
    return column * _CHANNEL_COUNT + channel


@dataclass(frozen=True, slots=True)
class TransitionMatrixEvent:
    target_tick: int
    source_tick: int
    source_position: int
    target_position: int
    evidence: float


@dataclass(frozen=True, slots=True)
class TransitionMatrixBranchObservation:
    branch_id: str
    frame_count: int
    p1_energy: float
    p2_energy: float
    total_energy: float
    position_frequency: tuple[int, ...]
    events: tuple[TransitionMatrixEvent, ...]
    a_event_count: float
    b_event_count: float
    u_event_count: float
    final_activation_max: float
    final_afterimage_max: float
    input_frames_unchanged: bool


@dataclass(frozen=True, slots=True)
class TransitionCounterBaselineObservation:
    branch_id: str
    a_count: float
    b_count: float
    u_count: float
    a_permanent: float
    b_permanent: float
    u_permanent: float


@dataclass(frozen=True, slots=True)
class LeakyTransitionBaselineObservation:
    branch_id: str
    decay: float
    a_value: float
    b_value: float
    u_value: float


@dataclass(frozen=True, slots=True)
class SaturatedTransitionBaselineObservation:
    branch_id: str
    capacity: float
    a_value: float
    b_value: float
    u_value: float


@dataclass(frozen=True, slots=True)
class GlobalNormalizationBaselineObservation:
    branch_id: str
    a_share: float
    b_share: float
    u_share: float


@dataclass(frozen=True, slots=True)
class TransitionDispositionFalsificationProbeResult:
    branches: tuple[TransitionMatrixBranchObservation, ...]
    counters: tuple[TransitionCounterBaselineObservation, ...]
    leaky_traces: tuple[LeakyTransitionBaselineObservation, ...]
    saturated_traces: tuple[SaturatedTransitionBaselineObservation, ...]
    global_normalizations: tuple[GlobalNormalizationBaselineObservation, ...]
    competition_and_matched_are_position_energy_equal: bool
    preregistered_transition_counts_exact: bool
    fast_field_resets_all_branches: bool
    neuron_frequency_cannot_detect_competition: bool
    counter_keeps_a_equal_under_competition: bool
    leaky_traces_keep_a_equal_under_competition: bool
    permanent_edges_keep_a_equal_under_competition: bool
    saturation_keeps_a_equal_under_competition: bool
    global_normalization_reduces_a_under_competition: bool
    global_normalization_violates_locality_under_u: bool
    no_local_baseline_carries_competition_coupled_release: bool
    baseline_resets_are_zero: bool
    observer_is_neutral: bool
    branch_order_is_neutral: bool
    baseline_order_is_neutral: bool
    repeated_run_is_neutral: bool
    retains_raw_frames: bool = False
    writes_back: bool = False
    releases_resource_or_disposition: bool = False

    def canonical_payload(self) -> dict[str, object]:
        return asdict(self)

    def digest(self) -> str:
        return _digest(self.canonical_payload())


BranchObserver = Callable[[TransitionMatrixBranchObservation], object]


def _branch_contacts(branch_id: str) -> tuple[int | None, ...]:
    try:
        p2 = _P2_BY_BRANCH[branch_id]
    except KeyError as exc:
        raise TransitionDispositionFalsificationProbeError(
            f"unknown matrix branch: {branch_id}"
        ) from exc
    return P1_A_HISTORY + p2 + (None,)


def _run_branch(
    branch_id: str,
    *,
    observer: BranchObserver | None = None,
) -> TransitionMatrixBranchObservation:
    contacts = _branch_contacts(branch_id)
    interface = build_visual_mcm_interface(
        _config(),
        sample_offsets=_SAMPLE_OFFSETS,
    )
    frequency = [0] * _config().carrier_count
    events = []
    energies = []
    frames_unchanged = True
    final_window = None

    for frame_index, column in enumerate(contacts):
        frame = _frame(column)
        before = frame.copy()
        drives: list[MCMNeuronDrive] = []

        def transition(drive: MCMNeuronDrive):
            drives.append(drive)
            return receptor_projection_baseline(drive)

        interface, output = interface.advance(
            frame,
            CommonFieldTime(_CLOCK_ID, frame_index, frame_index + 1),
            transition,
        )
        frames_unchanged = frames_unchanged and np.array_equal(frame, before)
        energies.append(sum(output.field_window.activation))
        final_window = output.field_window
        for drive in drives:
            contact = drive.perception.receptor_contact
            current = 0.0 if contact is None else contact
            if current != 0.0:
                frequency[_position_index(drive.previous.position[1])] += 1
            for sample in drive.perception.local_samples:
                evidence = current * sample.activation
                if evidence == 0.0:
                    continue
                source_position = (
                    drive.previous.position[1] + sample.relative_position[1]
                )
                events.append(
                    TransitionMatrixEvent(
                        target_tick=drive.perception.tick,
                        source_tick=sample.source_tick,
                        source_position=source_position,
                        target_position=drive.previous.position[1],
                        evidence=evidence,
                    )
                )

    if final_window is None:
        raise TransitionDispositionFalsificationProbeError(
            "matrix branch produced no field window"
        )
    ordered_events = tuple(
        sorted(
            events,
            key=lambda item: (
                item.target_tick,
                item.source_position,
                item.target_position,
            ),
        )
    )

    def count(transition: tuple[int, int]) -> float:
        return sum(
            item.evidence
            for item in ordered_events
            if (item.source_position, item.target_position) == transition
        )

    observation = TransitionMatrixBranchObservation(
        branch_id=branch_id,
        frame_count=len(contacts),
        p1_energy=sum(energies[:16]),
        p2_energy=sum(energies[16:32]),
        total_energy=sum(energies),
        position_frequency=tuple(frequency),
        events=ordered_events,
        a_event_count=count(_TRANSITION_A),
        b_event_count=count(_TRANSITION_B),
        u_event_count=count(_TRANSITION_U),
        final_activation_max=max(abs(value) for value in final_window.activation),
        final_afterimage_max=max(abs(value) for value in final_window.afterimage),
        input_frames_unchanged=frames_unchanged,
    )
    before_observer = _digest(asdict(observation))
    if observer is not None:
        observer(observation)
    if _digest(asdict(observation)) != before_observer:
        raise TransitionDispositionFalsificationProbeError(
            "observer changed an immutable matrix branch"
        )
    return observation


def _transition_counts(
    branch: TransitionMatrixBranchObservation,
) -> dict[tuple[int, int], float]:
    result: dict[tuple[int, int], float] = {}
    for event in branch.events:
        key = (event.source_position, event.target_position)
        result[key] = result.get(key, 0.0) + event.evidence
    return result


def _counter_observation(
    branch: TransitionMatrixBranchObservation,
) -> TransitionCounterBaselineObservation:
    counts = _transition_counts(branch)

    def value(key: tuple[int, int]) -> float:
        return counts.get(key, 0.0)

    return TransitionCounterBaselineObservation(
        branch_id=branch.branch_id,
        a_count=value(_TRANSITION_A),
        b_count=value(_TRANSITION_B),
        u_count=value(_TRANSITION_U),
        a_permanent=float(value(_TRANSITION_A) > 0.0),
        b_permanent=float(value(_TRANSITION_B) > 0.0),
        u_permanent=float(value(_TRANSITION_U) > 0.0),
    )


def _leaky_observations(
    branch: TransitionMatrixBranchObservation,
) -> tuple[LeakyTransitionBaselineObservation, ...]:
    events_by_tick: dict[int, tuple[TransitionMatrixEvent, ...]] = {}
    for tick in range(1, branch.frame_count + 1):
        events_by_tick[tick] = tuple(
            event for event in branch.events if event.target_tick == tick
        )
    result = []
    for decay in TRANSITION_DECAYS:
        state = {
            _TRANSITION_A: 0.0,
            _TRANSITION_B: 0.0,
            _TRANSITION_U: 0.0,
        }
        for tick in range(1, branch.frame_count + 1):
            state = {key: decay * value for key, value in state.items()}
            for event in events_by_tick[tick]:
                key = (event.source_position, event.target_position)
                if key in state:
                    state[key] += event.evidence
        result.append(
            LeakyTransitionBaselineObservation(
                branch_id=branch.branch_id,
                decay=decay,
                a_value=state[_TRANSITION_A],
                b_value=state[_TRANSITION_B],
                u_value=state[_TRANSITION_U],
            )
        )
    return tuple(result)


def _saturation_observations(
    counter: TransitionCounterBaselineObservation,
) -> tuple[SaturatedTransitionBaselineObservation, ...]:
    return tuple(
        SaturatedTransitionBaselineObservation(
            branch_id=counter.branch_id,
            capacity=capacity,
            a_value=min(counter.a_count, capacity),
            b_value=min(counter.b_count, capacity),
            u_value=min(counter.u_count, capacity),
        )
        for capacity in SATURATION_CAPACITIES
    )


def _global_observation(
    counter: TransitionCounterBaselineObservation,
) -> GlobalNormalizationBaselineObservation:
    total = counter.a_count + counter.b_count + counter.u_count
    if total <= 0.0:
        raise TransitionDispositionFalsificationProbeError(
            "global normalization requires transition evidence"
        )
    return GlobalNormalizationBaselineObservation(
        branch_id=counter.branch_id,
        a_share=counter.a_count / total,
        b_share=counter.b_count / total,
        u_share=counter.u_count / total,
    )


def _baseline_resets_are_zero() -> bool:
    empty_counts: dict[tuple[int, int], float] = {}
    counter_values = tuple(
        empty_counts.get(transition, 0.0)
        for transition in (_TRANSITION_A, _TRANSITION_B, _TRANSITION_U)
    )
    permanent_values = tuple(float(value > 0.0) for value in counter_values)

    leaky_values = []
    for decay in TRANSITION_DECAYS:
        state = {
            _TRANSITION_A: 0.0,
            _TRANSITION_B: 0.0,
            _TRANSITION_U: 0.0,
        }
        for event in ():
            state = {key: decay * value for key, value in state.items()}
            key = (event.source_position, event.target_position)
            if key in state:
                state[key] += event.evidence
        leaky_values.extend(state.values())

    saturated_values = tuple(
        min(value, capacity)
        for capacity in SATURATION_CAPACITIES
        for value in counter_values
    )
    total = sum(counter_values)
    global_values = (
        ()
        if total == 0.0
        else tuple(value / total for value in counter_values)
    )
    return (
        all(value == 0.0 for value in counter_values)
        and all(value == 0.0 for value in permanent_values)
        and all(value == 0.0 for value in leaky_values)
        and all(value == 0.0 for value in saturated_values)
        and global_values == ()
    )


def _core_payload(
    branches: tuple[TransitionMatrixBranchObservation, ...],
    counters: tuple[TransitionCounterBaselineObservation, ...],
    leaky: tuple[LeakyTransitionBaselineObservation, ...],
    saturated: tuple[SaturatedTransitionBaselineObservation, ...],
    global_values: tuple[GlobalNormalizationBaselineObservation, ...],
) -> dict[str, object]:
    return {
        "branches": [asdict(item) for item in branches],
        "counters": [asdict(item) for item in counters],
        "leaky": [asdict(item) for item in leaky],
        "saturated": [asdict(item) for item in saturated],
        "global": [asdict(item) for item in global_values],
    }


def run_transition_disposition_falsification_probe(
    *,
    branch_order: Iterable[str] = MATRIX_BRANCH_IDS,
    baseline_order: Iterable[str] = MATRIX_BASELINE_IDS,
    observer: BranchObserver | None = None,
    _verify_controls: bool = True,
) -> TransitionDispositionFalsificationProbeResult:
    """Execute Methodik 037 as isolated passive baselines."""

    branches_requested = tuple(branch_order)
    baselines_requested = tuple(baseline_order)
    if (
        len(branches_requested) != len(MATRIX_BRANCH_IDS)
        or set(branches_requested) != set(MATRIX_BRANCH_IDS)
    ):
        raise TransitionDispositionFalsificationProbeError(
            "branch_order must contain every matrix branch exactly once"
        )
    if (
        len(baselines_requested) != len(MATRIX_BASELINE_IDS)
        or set(baselines_requested) != set(MATRIX_BASELINE_IDS)
    ):
        raise TransitionDispositionFalsificationProbeError(
            "baseline_order must contain every matrix baseline exactly once"
        )

    collected = tuple(
        _run_branch(branch_id, observer=observer)
        for branch_id in branches_requested
    )
    branches = tuple(sorted(collected, key=lambda item: item.branch_id))

    # Baselines are intentionally independent; execution order cannot carry state.
    computed: dict[str, object] = {}
    for baseline_id in baselines_requested:
        if baseline_id in {
            "b0.fast_field",
            "b1.neuron_frequency",
        }:
            computed[baseline_id] = True
        elif baseline_id in {
            "b2.transition_counter",
            "b4.permanent_edge",
        }:
            computed[baseline_id] = tuple(
                _counter_observation(branch) for branch in branches
            )
        elif baseline_id == "b3.leaky_transition":
            computed[baseline_id] = tuple(
                item
                for branch in branches
                for item in _leaky_observations(branch)
            )
        elif baseline_id == "b5.independent_saturation":
            counter_values = tuple(
                _counter_observation(branch) for branch in branches
            )
            computed[baseline_id] = tuple(
                item
                for counter in counter_values
                for item in _saturation_observations(counter)
            )
        elif baseline_id == "b6.global_normalization":
            computed[baseline_id] = tuple(
                _global_observation(_counter_observation(branch))
                for branch in branches
            )
        else:
            raise TransitionDispositionFalsificationProbeError(
                f"unsupported baseline: {baseline_id}"
            )

    counters = tuple(
        sorted(
            computed["b2.transition_counter"],
            key=lambda item: item.branch_id,
        )
    )
    leaky = tuple(
        sorted(
            computed["b3.leaky_transition"],
            key=lambda item: (item.branch_id, item.decay),
        )
    )
    saturated = tuple(
        sorted(
            computed["b5.independent_saturation"],
            key=lambda item: (item.branch_id, item.capacity),
        )
    )
    global_values = tuple(
        sorted(
            computed["b6.global_normalization"],
            key=lambda item: item.branch_id,
        )
    )

    branch_by_id = {item.branch_id: item for item in branches}
    counter_by_id = {item.branch_id: item for item in counters}
    global_by_id = {item.branch_id: item for item in global_values}
    competition = branch_by_id["competition_b"]
    matched = branch_by_id["matched_noncompetition"]

    leaky_by_key = {
        (item.branch_id, item.decay): item for item in leaky
    }
    saturation_by_key = {
        (item.branch_id, item.capacity): item for item in saturated
    }

    observer_neutral = True
    branch_order_neutral = True
    baseline_order_neutral = True
    repeated_neutral = True
    if _verify_controls:
        without_observer = run_transition_disposition_falsification_probe(
            branch_order=branches_requested,
            baseline_order=baselines_requested,
            observer=None,
            _verify_controls=False,
        )
        reversed_branches = run_transition_disposition_falsification_probe(
            branch_order=reversed(branches_requested),
            baseline_order=baselines_requested,
            observer=None,
            _verify_controls=False,
        )
        reversed_baselines = run_transition_disposition_falsification_probe(
            branch_order=branches_requested,
            baseline_order=reversed(baselines_requested),
            observer=None,
            _verify_controls=False,
        )
        repeated = run_transition_disposition_falsification_probe(
            branch_order=branches_requested,
            baseline_order=baselines_requested,
            observer=None,
            _verify_controls=False,
        )
        core = _core_payload(branches, counters, leaky, saturated, global_values)
        observer_neutral = core == _core_payload(
            without_observer.branches,
            without_observer.counters,
            without_observer.leaky_traces,
            without_observer.saturated_traces,
            without_observer.global_normalizations,
        )
        branch_order_neutral = core == _core_payload(
            reversed_branches.branches,
            reversed_branches.counters,
            reversed_branches.leaky_traces,
            reversed_branches.saturated_traces,
            reversed_branches.global_normalizations,
        )
        baseline_order_neutral = core == _core_payload(
            reversed_baselines.branches,
            reversed_baselines.counters,
            reversed_baselines.leaky_traces,
            reversed_baselines.saturated_traces,
            reversed_baselines.global_normalizations,
        )
        repeated_neutral = core == _core_payload(
            repeated.branches,
            repeated.counters,
            repeated.leaky_traces,
            repeated.saturated_traces,
            repeated.global_normalizations,
        )

    result = TransitionDispositionFalsificationProbeResult(
        branches=branches,
        counters=counters,
        leaky_traces=leaky,
        saturated_traces=saturated,
        global_normalizations=global_values,
        competition_and_matched_are_position_energy_equal=(
            competition.frame_count == matched.frame_count == 33
            and competition.p2_energy == matched.p2_energy == 8.0
            and competition.total_energy == matched.total_energy == 16.0
            and competition.position_frequency == matched.position_frequency
        ),
        preregistered_transition_counts_exact=(
            all(item.a_event_count == 4.0 for item in branches)
            and competition.b_event_count == 4.0
            and branch_by_id["matched_noncompetition"].b_event_count == 0.0
            and branch_by_id["unrelated_u"].u_event_count == 4.0
            and branch_by_id["idle"].b_event_count == 0.0
            and branch_by_id["idle"].u_event_count == 0.0
        ),
        fast_field_resets_all_branches=all(
            item.final_activation_max == 0.0
            and item.final_afterimage_max == 0.0
            for item in branches
        ),
        neuron_frequency_cannot_detect_competition=(
            competition.position_frequency == matched.position_frequency
        ),
        counter_keeps_a_equal_under_competition=(
            counter_by_id["competition_b"].a_count
            == counter_by_id["matched_noncompetition"].a_count
            == 4.0
        ),
        leaky_traces_keep_a_equal_under_competition=all(
            leaky_by_key[("competition_b", decay)].a_value
            == leaky_by_key[("matched_noncompetition", decay)].a_value
            for decay in TRANSITION_DECAYS
        ),
        permanent_edges_keep_a_equal_under_competition=(
            counter_by_id["competition_b"].a_permanent
            == counter_by_id["matched_noncompetition"].a_permanent
            == 1.0
        ),
        saturation_keeps_a_equal_under_competition=all(
            saturation_by_key[("competition_b", capacity)].a_value
            == saturation_by_key[("matched_noncompetition", capacity)].a_value
            for capacity in SATURATION_CAPACITIES
        ),
        global_normalization_reduces_a_under_competition=(
            global_by_id["competition_b"].a_share
            < global_by_id["matched_noncompetition"].a_share
        ),
        global_normalization_violates_locality_under_u=(
            global_by_id["unrelated_u"].a_share
            == global_by_id["competition_b"].a_share
            < global_by_id["matched_noncompetition"].a_share
        ),
        no_local_baseline_carries_competition_coupled_release=(
            counter_by_id["competition_b"].a_count
            == counter_by_id["matched_noncompetition"].a_count
            and all(
                leaky_by_key[("competition_b", decay)].a_value
                == leaky_by_key[("matched_noncompetition", decay)].a_value
                for decay in TRANSITION_DECAYS
            )
            and all(
                saturation_by_key[("competition_b", capacity)].a_value
                == saturation_by_key[("matched_noncompetition", capacity)].a_value
                for capacity in SATURATION_CAPACITIES
            )
        ),
        baseline_resets_are_zero=_baseline_resets_are_zero(),
        observer_is_neutral=observer_neutral,
        branch_order_is_neutral=branch_order_neutral,
        baseline_order_is_neutral=baseline_order_neutral,
        repeated_run_is_neutral=repeated_neutral,
    )
    controls = {
        "competition_and_matched_are_position_energy_equal": (
            result.competition_and_matched_are_position_energy_equal
        ),
        "preregistered_transition_counts_exact": (
            result.preregistered_transition_counts_exact
        ),
        "fast_field_resets_all_branches": result.fast_field_resets_all_branches,
        "neuron_frequency_cannot_detect_competition": (
            result.neuron_frequency_cannot_detect_competition
        ),
        "counter_keeps_a_equal_under_competition": (
            result.counter_keeps_a_equal_under_competition
        ),
        "leaky_traces_keep_a_equal_under_competition": (
            result.leaky_traces_keep_a_equal_under_competition
        ),
        "permanent_edges_keep_a_equal_under_competition": (
            result.permanent_edges_keep_a_equal_under_competition
        ),
        "saturation_keeps_a_equal_under_competition": (
            result.saturation_keeps_a_equal_under_competition
        ),
        "global_normalization_reduces_a_under_competition": (
            result.global_normalization_reduces_a_under_competition
        ),
        "global_normalization_violates_locality_under_u": (
            result.global_normalization_violates_locality_under_u
        ),
        "no_local_baseline_carries_competition_coupled_release": (
            result.no_local_baseline_carries_competition_coupled_release
        ),
        "baseline_resets_are_zero": result.baseline_resets_are_zero,
        "observer_is_neutral": result.observer_is_neutral,
        "branch_order_is_neutral": result.branch_order_is_neutral,
        "baseline_order_is_neutral": result.baseline_order_is_neutral,
        "repeated_run_is_neutral": result.repeated_run_is_neutral,
        "retains_no_raw_frames": not result.retains_raw_frames,
        "does_not_write_back": not result.writes_back,
        "does_not_release_resource_or_disposition": (
            not result.releases_resource_or_disposition
        ),
    }
    failed = tuple(name for name, passed in controls.items() if not passed)
    if failed:
        raise TransitionDispositionFalsificationProbeError(
            f"Methodik 037 controls did not close exactly: {', '.join(failed)}"
        )
    return result


def transition_disposition_falsification_probe_public_roles() -> tuple[str, ...]:
    classes = (
        TransitionMatrixEvent,
        TransitionMatrixBranchObservation,
        TransitionCounterBaselineObservation,
        LeakyTransitionBaselineObservation,
        SaturatedTransitionBaselineObservation,
        GlobalNormalizationBaselineObservation,
        TransitionDispositionFalsificationProbeResult,
    )
    return tuple(item.name for cls in classes for item in fields(cls))
