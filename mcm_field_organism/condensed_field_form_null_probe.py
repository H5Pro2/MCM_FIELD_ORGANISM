"""Passive null probe for view-spanning condensed field form.

All form families and transformations belong to the external research driver.
The visual MCM runtime receives only completed receptor contact.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
from typing import Callable, Iterable

import numpy as np

from .carrier_baselines import run_independent_history
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .mcm_neuron_layer import MCMNeuronDrive, receptor_projection_baseline
from .sensor_mcm_field import CommonFieldTime
from .visual_mcm_interface import build_visual_mcm_interface


class CondensedFieldFormNullProbeError(ValueError):
    """Raised when Methodik 035 leaves its preregistered passive domain."""


FORM_A_BASE = ((1, 1), (2, 1), (3, 1), (3, 2))
FORM_B_BASE = ((1, 1), (1, 2), (1, 3), (2, 2))
FORM_HOLDOUT = ((1, 3), (2, 3), (3, 2), (3, 3))
BRANCH_IDS = ("history_a", "history_b", "history_permuted", "history_zero")
LEAKY_TAUS = (1.0, 2.0, 4.0)
RECURRENT_RHOS = (0.25, 0.5, 0.75)

_GRID_SIZE = 5
_SOURCE_SIZE = 10
_CHANNEL_COUNT = 3
_ACTIVE_CHANNEL = 0
_CLOCK_ID = "organism.field_form_null"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _l1(left: Iterable[float], right: Iterable[float]) -> float:
    left_vector = tuple(float(value) for value in left)
    right_vector = tuple(float(value) for value in right)
    if len(left_vector) != len(right_vector):
        raise CondensedFieldFormNullProbeError("L1 vectors must have equal geometry")
    return sum(
        abs(left_value - right_value)
        for left_value, right_value in zip(left_vector, right_vector, strict=True)
    )


def _rotate_once(
    coordinates: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((column, 4 - row) for row, column in coordinates))


def _mirror(
    coordinates: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((row, 4 - column) for row, column in coordinates))


def _rotations(
    coordinates: Iterable[tuple[int, int]],
) -> tuple[tuple[tuple[int, int], ...], ...]:
    current = tuple(sorted(coordinates))
    result = []
    for _ in range(4):
        result.append(current)
        current = _rotate_once(current)
    return tuple(result)


def _d4(
    coordinates: Iterable[tuple[int, int]],
) -> tuple[tuple[tuple[int, int], ...], ...]:
    candidates = set(_rotations(coordinates))
    candidates.update(_mirror(item) for item in _rotations(coordinates))
    return tuple(sorted(candidates))


def _validate_coordinates(
    coordinates: Iterable[tuple[int, int]],
    role: str,
) -> tuple[tuple[int, int], ...]:
    result = tuple(sorted(tuple(item) for item in coordinates))
    if len(result) != 4 or len(set(result)) != 4:
        raise CondensedFieldFormNullProbeError(f"{role} must contain four unique cells")
    if any(
        len(item) != 2
        or isinstance(item[0], bool)
        or isinstance(item[1], bool)
        or not isinstance(item[0], int)
        or not isinstance(item[1], int)
        or not 0 <= item[0] < _GRID_SIZE
        or not 0 <= item[1] < _GRID_SIZE
        for item in result
    ):
        raise CondensedFieldFormNullProbeError(
            f"{role} must stay inside the preregistered 5x5 grid"
        )
    return result


def _frame(
    coordinates: Iterable[tuple[int, int]],
    *,
    channel: int = _ACTIVE_CHANNEL,
) -> np.ndarray:
    coordinates = _validate_coordinates(coordinates, "frame coordinates")
    if (
        isinstance(channel, bool)
        or not isinstance(channel, int)
        or not 0 <= channel < _CHANNEL_COUNT
    ):
        raise CondensedFieldFormNullProbeError("channel must identify one visual channel")
    frame = np.zeros((_SOURCE_SIZE, _SOURCE_SIZE, _CHANNEL_COUNT), dtype=np.uint8)
    for row, column in coordinates:
        frame[row * 2 : (row + 1) * 2, column * 2 : (column + 1) * 2, channel] = 255
    return frame


def _zero_frame() -> np.ndarray:
    return np.zeros((_SOURCE_SIZE, _SOURCE_SIZE, _CHANNEL_COUNT), dtype=np.uint8)


def _config() -> VisualGridConfig:
    return VisualGridConfig(
        source_width=_SOURCE_SIZE,
        source_height=_SOURCE_SIZE,
        grid_columns=_GRID_SIZE,
        grid_rows=_GRID_SIZE,
        frames_per_second=1.0,
    )


def _branch_coordinates(
    branch_id: str,
) -> tuple[tuple[tuple[int, int], ...], ...]:
    if branch_id == "history_a":
        return _rotations(FORM_A_BASE)
    if branch_id == "history_b":
        return _rotations(FORM_B_BASE)
    if branch_id == "history_permuted":
        return tuple(reversed(_rotations(FORM_A_BASE)))
    if branch_id == "history_zero":
        return ()
    raise CondensedFieldFormNullProbeError(f"unknown branch: {branch_id}")


def _contact_vectors(
    branch_id: str,
    receptor: LocalChannelGridReceptor,
    *,
    channel: int = _ACTIVE_CHANNEL,
    holdout: tuple[tuple[int, int], ...] = FORM_HOLDOUT,
) -> tuple[tuple[float, ...], ...]:
    history = _branch_coordinates(branch_id)
    frames_in = (
        tuple(_frame(item, channel=channel) for item in history)
        if history
        else tuple(_zero_frame() for _ in range(4))
    )
    frames_in = frames_in + (_zero_frame(), _frame(holdout, channel=channel))
    return tuple(
        receptor.analyze(frame, frame_index=index).channel_values
        for index, frame in enumerate(frames_in)
    )


def _local_input_payload(drive: MCMNeuronDrive) -> dict[str, object]:
    return {
        "neuron_id": drive.previous.neuron_id,
        "position": list(drive.previous.position),
        "previous_activation": drive.previous.activation,
        "previous_afterimage": drive.previous.afterimage,
        "receptor_contact": drive.perception.receptor_contact,
        "samples": [
            {
                "relative_position": list(sample.relative_position),
                "source_tick": sample.source_tick,
                "activation": sample.activation,
                "afterimage": sample.afterimage,
            }
            for sample in drive.perception.local_samples
        ],
    }


@dataclass(frozen=True, slots=True)
class FieldFormBranchObservation:
    branch_id: str
    history_contact_energy: float
    pre_holdout_activation_max: float
    pre_holdout_afterimage_max: float
    holdout_activation: tuple[float, ...]
    holdout_afterimage: tuple[float, ...]
    holdout_window_digest: str
    holdout_local_input_digest: str
    holdout_previous_field_max: float


@dataclass(frozen=True, slots=True)
class FieldFormPairComparison:
    left_branch_id: str
    right_branch_id: str
    activation_l1: float
    afterimage_l1: float
    window_digest_equal: bool
    local_input_digest_equal: bool


@dataclass(frozen=True, slots=True)
class FixedTraceBaselineComparison:
    baseline_id: str
    parameter: float
    left_branch_id: str
    right_branch_id: str
    natural_holdout_l1: float
    exact_reset_holdout_l1: float


@dataclass(frozen=True, slots=True)
class TemplateBaselineObservation:
    branch_id: str
    minimum_transformed_l1: float


@dataclass(frozen=True, slots=True)
class CondensedFieldFormNullProbeResult:
    branches: tuple[FieldFormBranchObservation, ...]
    pair_comparisons: tuple[FieldFormPairComparison, ...]
    leaky_baselines: tuple[FixedTraceBaselineComparison, ...]
    recurrent_baselines: tuple[FixedTraceBaselineComparison, ...]
    template_baselines: tuple[TemplateBaselineObservation, ...]
    all_pre_holdout_fast_states_zero: bool
    all_holdout_windows_equal: bool
    all_holdout_local_inputs_equal: bool
    leaky_exact_resets_equal: bool
    recurrent_exact_resets_equal: bool
    fixed_edge_holdouts_equal: bool
    template_separates_related_from_control: bool
    reflection_equivariant: bool
    channel_permutation_equivariant: bool
    unequal_holdout_detected: bool
    observer_is_neutral: bool
    order_is_neutral: bool
    repeated_run_is_neutral: bool
    retains_raw_frames: bool = False
    writes_back: bool = False
    releases_persistence: bool = False

    def canonical_payload(self) -> dict[str, object]:
        return asdict(self)

    def digest(self) -> str:
        return _digest(self.canonical_payload())


BranchObserver = Callable[[FieldFormBranchObservation], object]


def _run_branch(
    branch_id: str,
    *,
    channel: int = _ACTIVE_CHANNEL,
    holdout: tuple[tuple[int, int], ...] = FORM_HOLDOUT,
    mirror_all: bool = False,
    observer: BranchObserver | None = None,
) -> FieldFormBranchObservation:
    config = _config()
    coordinates = _branch_coordinates(branch_id)
    if mirror_all:
        coordinates = tuple(_mirror(item) for item in coordinates)
        holdout = _mirror(holdout)
    frames_in = (
        tuple(_frame(item, channel=channel) for item in coordinates)
        if coordinates
        else tuple(_zero_frame() for _ in range(4))
    )
    frames_in = frames_in + (_zero_frame(), _frame(holdout, channel=channel))

    interface = build_visual_mcm_interface(config)
    outputs = []
    holdout_drives: list[MCMNeuronDrive] = []
    history_energy = 0.0
    for index, frame in enumerate(frames_in):
        observed: list[MCMNeuronDrive] = []

        def transition(drive: MCMNeuronDrive):
            observed.append(drive)
            return receptor_projection_baseline(drive)

        interface, output = interface.advance(
            frame,
            CommonFieldTime(_CLOCK_ID, index, index + 1),
            transition,
        )
        outputs.append(output)
        if index < 4:
            history_energy += sum(output.field_window.activation)
        if index == 5:
            holdout_drives = observed

    pre_holdout = outputs[4].field_window
    holdout_window = outputs[5].field_window
    local_payload = tuple(
        _local_input_payload(drive)
        for drive in sorted(holdout_drives, key=lambda item: item.previous.neuron_id)
    )
    previous_values = tuple(
        value
        for drive in holdout_drives
        for value in (
            drive.previous.activation,
            drive.previous.afterimage,
            *(sample.activation for sample in drive.perception.local_samples),
            *(sample.afterimage for sample in drive.perception.local_samples),
        )
    )
    observation = FieldFormBranchObservation(
        branch_id=branch_id,
        history_contact_energy=history_energy,
        pre_holdout_activation_max=max(abs(value) for value in pre_holdout.activation),
        pre_holdout_afterimage_max=max(abs(value) for value in pre_holdout.afterimage),
        holdout_activation=holdout_window.activation,
        holdout_afterimage=holdout_window.afterimage,
        holdout_window_digest=holdout_window.digest(),
        holdout_local_input_digest=_digest(local_payload),
        holdout_previous_field_max=max((abs(value) for value in previous_values), default=0.0),
    )
    before = _digest(asdict(observation))
    if observer is not None:
        observer(observation)
    if _digest(asdict(observation)) != before:
        raise CondensedFieldFormNullProbeError(
            "observer changed an immutable branch observation"
        )
    return observation


def _pair_comparisons(
    branches: tuple[FieldFormBranchObservation, ...],
) -> tuple[FieldFormPairComparison, ...]:
    by_id = {branch.branch_id: branch for branch in branches}
    left = by_id["history_a"]
    result = []
    for right_id in ("history_b", "history_permuted", "history_zero"):
        right = by_id[right_id]
        result.append(
            FieldFormPairComparison(
                left_branch_id=left.branch_id,
                right_branch_id=right.branch_id,
                activation_l1=_l1(left.holdout_activation, right.holdout_activation),
                afterimage_l1=_l1(left.holdout_afterimage, right.holdout_afterimage),
                window_digest_equal=(
                    left.holdout_window_digest == right.holdout_window_digest
                ),
                local_input_digest_equal=(
                    left.holdout_local_input_digest == right.holdout_local_input_digest
                ),
            )
        )
    return tuple(result)


def _recurrent_history(
    contacts: tuple[tuple[float, ...], ...],
    rho: float,
) -> tuple[float, ...]:
    state = (0.0,) * len(contacts[0])
    for contact in contacts:
        state = tuple(
            rho * previous + current
            for previous, current in zip(state, contact, strict=True)
        )
    return state


def _fixed_trace_baselines(
    branch_ids: tuple[str, ...],
) -> tuple[
    tuple[FixedTraceBaselineComparison, ...],
    tuple[FixedTraceBaselineComparison, ...],
]:
    receptor = LocalChannelGridReceptor(_config())
    contacts = {
        branch_id: _contact_vectors(branch_id, receptor)
        for branch_id in branch_ids
    }
    pairs = (
        ("history_a", "history_b"),
        ("history_a", "history_permuted"),
        ("history_a", "history_zero"),
    )
    zero = (0.0,) * _config().carrier_count
    holdout = contacts["history_a"][-1]
    leaky = []
    for tau in LEAKY_TAUS:
        natural = {
            branch_id: run_independent_history(
                branch_contacts,
                dt=1.0,
                tau=tau,
            )[-1].afterimage
            for branch_id, branch_contacts in contacts.items()
        }
        reset = run_independent_history(
            (holdout,),
            dt=1.0,
            tau=tau,
            initial_afterimage=zero,
        )[-1].afterimage
        for left_id, right_id in pairs:
            leaky.append(
                FixedTraceBaselineComparison(
                    baseline_id="b1.leaky",
                    parameter=tau,
                    left_branch_id=left_id,
                    right_branch_id=right_id,
                    natural_holdout_l1=_l1(natural[left_id], natural[right_id]),
                    exact_reset_holdout_l1=_l1(reset, reset),
                )
            )

    recurrent = []
    for rho in RECURRENT_RHOS:
        natural = {
            branch_id: _recurrent_history(branch_contacts, rho)
            for branch_id, branch_contacts in contacts.items()
        }
        reset = _recurrent_history((holdout,), rho)
        for left_id, right_id in pairs:
            recurrent.append(
                FixedTraceBaselineComparison(
                    baseline_id="b2.recurrence",
                    parameter=rho,
                    left_branch_id=left_id,
                    right_branch_id=right_id,
                    natural_holdout_l1=_l1(natural[left_id], natural[right_id]),
                    exact_reset_holdout_l1=_l1(reset, reset),
                )
            )
    return tuple(leaky), tuple(recurrent)


def _fixed_edge_step(values: tuple[float, ...]) -> tuple[float, ...]:
    if len(values) != _config().carrier_count:
        raise CondensedFieldFormNullProbeError("fixed edge input has wrong geometry")
    result = []
    for row in range(_GRID_SIZE):
        for column in range(_GRID_SIZE):
            for channel in range(_CHANNEL_COUNT):
                neighbors = []
                for row_delta, column_delta in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    source_row = row + row_delta
                    source_column = column + column_delta
                    if (
                        0 <= source_row < _GRID_SIZE
                        and 0 <= source_column < _GRID_SIZE
                    ):
                        index = (
                            (source_row * _GRID_SIZE + source_column) * _CHANNEL_COUNT
                            + channel
                        )
                        neighbors.append(values[index])
                center = (row * _GRID_SIZE + column) * _CHANNEL_COUNT + channel
                result.append((values[center] + sum(neighbors)) / (1 + len(neighbors)))
    return tuple(result)


def _field_values_in_position_order(values: tuple[float, ...]) -> tuple[float, ...]:
    expected_width = _config().carrier_count
    if len(values) != expected_width:
        raise CondensedFieldFormNullProbeError("field vector has wrong geometry")
    lexical_ids = tuple(sorted(f"field.visual.n{index}" for index in range(expected_width)))
    by_id = dict(zip(lexical_ids, values, strict=True))
    return tuple(by_id[f"field.visual.n{index}"] for index in range(expected_width))


def _template_score(branch_id: str) -> float:
    receptor = LocalChannelGridReceptor(_config())
    holdout = receptor.analyze(_frame(FORM_HOLDOUT), frame_index=0).channel_values
    history = _branch_coordinates(branch_id)
    if not history:
        history = ((),)
    candidates = []
    for coordinates in history:
        if coordinates:
            variants = _d4(coordinates)
            candidates.extend(
                receptor.analyze(_frame(item), frame_index=0).channel_values
                for item in variants
            )
        else:
            candidates.append(
                receptor.analyze(_zero_frame(), frame_index=0).channel_values
            )
    return min(_l1(candidate, holdout) for candidate in candidates)


def _unmirror_activation(values: tuple[float, ...]) -> tuple[float, ...]:
    result = [0.0] * len(values)
    for row in range(_GRID_SIZE):
        for column in range(_GRID_SIZE):
            for channel in range(_CHANNEL_COUNT):
                source = (row * _GRID_SIZE + (4 - column)) * _CHANNEL_COUNT + channel
                target = (row * _GRID_SIZE + column) * _CHANNEL_COUNT + channel
                result[target] = values[source]
    return tuple(result)


def _unchannel_activation(
    values: tuple[float, ...],
    source_channel: int,
) -> tuple[float, ...]:
    result = [0.0] * len(values)
    for row in range(_GRID_SIZE):
        for column in range(_GRID_SIZE):
            source = (row * _GRID_SIZE + column) * _CHANNEL_COUNT + source_channel
            target = (row * _GRID_SIZE + column) * _CHANNEL_COUNT + _ACTIVE_CHANNEL
            result[target] = values[source]
    return tuple(result)


def _core_payload(
    branches: tuple[FieldFormBranchObservation, ...],
    pair_comparisons: tuple[FieldFormPairComparison, ...],
    leaky: tuple[FixedTraceBaselineComparison, ...],
    recurrent: tuple[FixedTraceBaselineComparison, ...],
    templates: tuple[TemplateBaselineObservation, ...],
) -> dict[str, object]:
    return {
        "branches": [asdict(item) for item in branches],
        "pair_comparisons": [asdict(item) for item in pair_comparisons],
        "leaky": [asdict(item) for item in leaky],
        "recurrent": [asdict(item) for item in recurrent],
        "templates": [asdict(item) for item in templates],
    }


def run_condensed_field_form_null_probe(
    *,
    branch_order: Iterable[str] = BRANCH_IDS,
    observer: BranchObserver | None = None,
    _verify_controls: bool = True,
) -> CondensedFieldFormNullProbeResult:
    """Execute Methodik 035 without adding state to the MCM runtime."""

    order = tuple(branch_order)
    if len(order) != len(BRANCH_IDS) or set(order) != set(BRANCH_IDS):
        raise CondensedFieldFormNullProbeError(
            "branch_order must contain every preregistered branch exactly once"
        )
    if set(_d4(FORM_A_BASE)).intersection(_d4(FORM_B_BASE)):
        raise CondensedFieldFormNullProbeError(
            "preregistered form families must remain non-congruent"
        )
    if tuple(sorted(FORM_HOLDOUT)) in _rotations(FORM_A_BASE):
        raise CondensedFieldFormNullProbeError(
            "holdout must not repeat a preregistered history rotation"
        )

    collected = tuple(_run_branch(branch_id, observer=observer) for branch_id in order)
    branches = tuple(sorted(collected, key=lambda item: item.branch_id))
    comparisons = _pair_comparisons(branches)
    leaky, recurrent = _fixed_trace_baselines(tuple(item.branch_id for item in branches))
    templates = tuple(
        TemplateBaselineObservation(
            branch_id=branch_id,
            minimum_transformed_l1=_template_score(branch_id),
        )
        for branch_id in sorted(BRANCH_IDS)
    )

    holdout_window_values = next(
        item.holdout_activation for item in branches if item.branch_id == "history_a"
    )
    holdout = _field_values_in_position_order(holdout_window_values)
    fixed_edge = _fixed_edge_step(holdout)
    fixed_edge_equal = all(
        _fixed_edge_step(
            _field_values_in_position_order(item.holdout_activation)
        )
        == fixed_edge
        for item in branches
    )

    reflected = tuple(
        sorted(
            (_run_branch(branch_id, mirror_all=True) for branch_id in BRANCH_IDS),
            key=lambda item: item.branch_id,
        )
    )
    reflection_equivariant = all(
        _field_values_in_position_order(original.holdout_activation)
        == _unmirror_activation(
            _field_values_in_position_order(mirrored.holdout_activation)
        )
        and original.holdout_afterimage == mirrored.holdout_afterimage
        for original, mirrored in zip(branches, reflected, strict=True)
    )

    channel_two = tuple(
        sorted(
            (_run_branch(branch_id, channel=2) for branch_id in BRANCH_IDS),
            key=lambda item: item.branch_id,
        )
    )
    channel_equivariant = all(
        _field_values_in_position_order(original.holdout_activation)
        == _unchannel_activation(
            _field_values_in_position_order(permuted.holdout_activation),
            2,
        )
        and original.holdout_afterimage == permuted.holdout_afterimage
        for original, permuted in zip(branches, channel_two, strict=True)
    )

    unequal = _run_branch("history_a", holdout=FORM_B_BASE)
    unequal_detected = (
        _l1(holdout_window_values, unequal.holdout_activation) > 0.0
    )

    core = _core_payload(branches, comparisons, leaky, recurrent, templates)
    observer_neutral = True
    order_neutral = True
    repetition_neutral = True
    if _verify_controls:
        without_observer = run_condensed_field_form_null_probe(
            branch_order=order,
            observer=None,
            _verify_controls=False,
        )
        reversed_order = run_condensed_field_form_null_probe(
            branch_order=reversed(order),
            observer=None,
            _verify_controls=False,
        )
        repeated = run_condensed_field_form_null_probe(
            branch_order=order,
            observer=None,
            _verify_controls=False,
        )
        baseline_core = _core_payload(
            without_observer.branches,
            without_observer.pair_comparisons,
            without_observer.leaky_baselines,
            without_observer.recurrent_baselines,
            without_observer.template_baselines,
        )
        observer_neutral = core == baseline_core
        order_neutral = core == _core_payload(
            reversed_order.branches,
            reversed_order.pair_comparisons,
            reversed_order.leaky_baselines,
            reversed_order.recurrent_baselines,
            reversed_order.template_baselines,
        )
        repetition_neutral = core == _core_payload(
            repeated.branches,
            repeated.pair_comparisons,
            repeated.leaky_baselines,
            repeated.recurrent_baselines,
            repeated.template_baselines,
        )

    template_by_id = {
        item.branch_id: item.minimum_transformed_l1 for item in templates
    }
    result = CondensedFieldFormNullProbeResult(
        branches=branches,
        pair_comparisons=comparisons,
        leaky_baselines=leaky,
        recurrent_baselines=recurrent,
        template_baselines=templates,
        all_pre_holdout_fast_states_zero=all(
            item.pre_holdout_activation_max == 0.0
            and item.pre_holdout_afterimage_max == 0.0
            and item.holdout_previous_field_max == 0.0
            for item in branches
        ),
        all_holdout_windows_equal=all(
            item.activation_l1 == 0.0
            and item.afterimage_l1 == 0.0
            and item.window_digest_equal
            for item in comparisons
        ),
        all_holdout_local_inputs_equal=all(
            item.local_input_digest_equal for item in comparisons
        ),
        leaky_exact_resets_equal=all(
            item.exact_reset_holdout_l1 == 0.0 for item in leaky
        ),
        recurrent_exact_resets_equal=all(
            item.exact_reset_holdout_l1 == 0.0 for item in recurrent
        ),
        fixed_edge_holdouts_equal=fixed_edge_equal,
        template_separates_related_from_control=(
            template_by_id["history_a"] == 0.0
            and template_by_id["history_permuted"] == 0.0
            and template_by_id["history_b"] > 0.0
            and template_by_id["history_zero"] > 0.0
        ),
        reflection_equivariant=reflection_equivariant,
        channel_permutation_equivariant=channel_equivariant,
        unequal_holdout_detected=unequal_detected,
        observer_is_neutral=observer_neutral,
        order_is_neutral=order_neutral,
        repeated_run_is_neutral=repetition_neutral,
    )
    controls = {
        "all_pre_holdout_fast_states_zero": result.all_pre_holdout_fast_states_zero,
        "all_holdout_windows_equal": result.all_holdout_windows_equal,
        "all_holdout_local_inputs_equal": result.all_holdout_local_inputs_equal,
        "leaky_exact_resets_equal": result.leaky_exact_resets_equal,
        "recurrent_exact_resets_equal": result.recurrent_exact_resets_equal,
        "fixed_edge_holdouts_equal": result.fixed_edge_holdouts_equal,
        "template_separates_related_from_control": (
            result.template_separates_related_from_control
        ),
        "reflection_equivariant": result.reflection_equivariant,
        "channel_permutation_equivariant": result.channel_permutation_equivariant,
        "unequal_holdout_detected": result.unequal_holdout_detected,
        "observer_is_neutral": result.observer_is_neutral,
        "order_is_neutral": result.order_is_neutral,
        "repeated_run_is_neutral": result.repeated_run_is_neutral,
    }
    failed = tuple(name for name, passed in controls.items() if not passed)
    if failed:
        raise CondensedFieldFormNullProbeError(
            f"Methodik 035 controls did not close exactly: {', '.join(failed)}"
        )
    return result


def condensed_field_form_null_probe_public_roles() -> tuple[str, ...]:
    classes = (
        FieldFormBranchObservation,
        FieldFormPairComparison,
        FixedTraceBaselineComparison,
        TemplateBaselineObservation,
        CondensedFieldFormNullProbeResult,
    )
    return tuple(item.name for cls in classes for item in fields(cls))
