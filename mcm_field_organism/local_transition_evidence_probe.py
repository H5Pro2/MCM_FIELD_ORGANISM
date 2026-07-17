"""Passive local transition-evidence probe for Methodik 036."""

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


class LocalTransitionEvidenceProbeError(ValueError):
    """Raised when the passive probe leaves its preregistered domain."""


CONTINUOUS_FORWARD = (1, 2, 3, 4, 5)
CONTINUOUS_REVERSE = (5, 4, 3, 2, 1)
PERMUTED_CONTACTS = (1, 4, 2, 5, 3)
INTERRUPTED_CONTACTS = (1, None, 2, None, 3, None, 4, None, 5)
STATIONARY_CONTACTS = (3, 3, 3, 3, 3)
SEQUENCE_IDS = (
    "continuous_forward",
    "continuous_reverse",
    "interrupted",
    "permuted",
    "stationary",
)

_SEQUENCES = {
    "continuous_forward": CONTINUOUS_FORWARD,
    "continuous_reverse": CONTINUOUS_REVERSE,
    "interrupted": INTERRUPTED_CONTACTS,
    "permuted": PERMUTED_CONTACTS,
    "stationary": STATIONARY_CONTACTS,
}
_SAMPLE_OFFSETS = (
    (-1, 0, 0),
    (1, 0, 0),
    (0, -1, 0),
    (0, 1, 0),
)
_GRID_ROWS = 3
_GRID_COLUMNS = 7
_CHANNEL_COUNT = 3
_SOURCE_HEIGHT = 6
_SOURCE_WIDTH = 14
_ACTIVE_ROW = 1
_ACTIVE_CHANNEL = 0
_CLOCK_ID = "organism.local_transition"


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
        grid_rows=_GRID_ROWS,
        frames_per_second=1.0,
    )


def _frame(column: int | None, *, channel: int = _ACTIVE_CHANNEL) -> np.ndarray:
    if column is not None and (
        isinstance(column, bool)
        or not isinstance(column, int)
        or not 0 <= column < _GRID_COLUMNS
    ):
        raise LocalTransitionEvidenceProbeError(
            "contact column must fit the preregistered grid"
        )
    if (
        isinstance(channel, bool)
        or not isinstance(channel, int)
        or not 0 <= channel < _CHANNEL_COUNT
    ):
        raise LocalTransitionEvidenceProbeError("channel must identify one visual channel")
    result = np.zeros((_SOURCE_HEIGHT, _SOURCE_WIDTH, _CHANNEL_COUNT), dtype=np.uint8)
    if column is not None:
        result[2:4, column * 2 : (column + 1) * 2, channel] = 255
    return result


def _position_index(position: tuple[int, int, int]) -> int:
    row, column, channel = position
    return (row * _GRID_COLUMNS + column) * _CHANNEL_COUNT + channel


@dataclass(frozen=True, slots=True)
class LocalTransitionEvent:
    target_tick: int
    source_tick: int
    target_position: tuple[int, int, int]
    relative_source_position: tuple[int, int, int]
    current_contact: float
    prior_local_activation: float


@dataclass(frozen=True, slots=True)
class LocalTransitionSequenceObservation:
    sequence_id: str
    frame_count: int
    total_energy: float
    frame_energies: tuple[float, ...]
    position_frequency: tuple[int, ...]
    self_overlap_total: float
    local_transition_total: float
    baseline_transition_total: float
    source_negative_column_events: int
    source_positive_column_events: int
    other_local_events: int
    events: tuple[LocalTransitionEvent, ...]
    runtime_matches_fixed_neighbor_baseline: bool
    afterimage_is_zero: bool
    input_frames_unchanged: bool


@dataclass(frozen=True, slots=True)
class LocalTransitionEvidenceProbeResult:
    sequences: tuple[LocalTransitionSequenceObservation, ...]
    primary_energy_equal: bool
    primary_position_frequency_equal: bool
    primary_self_overlap_zero: bool
    expected_event_counts_exact: bool
    all_runtime_events_match_fixed_neighbor_baseline: bool
    interruption_removes_events: bool
    stationary_separates_self_from_neighbor: bool
    time_reversal_is_symmetric: bool
    spatial_reflection_is_equivariant: bool
    channel_permutation_is_equivariant: bool
    offset_order_is_neutral: bool
    observation_order_is_neutral: bool
    observer_is_neutral: bool
    sequence_order_is_neutral: bool
    repeated_run_is_neutral: bool
    retains_raw_frames: bool = False
    writes_back: bool = False
    releases_disposition: bool = False

    def canonical_payload(self) -> dict[str, object]:
        return asdict(self)

    def digest(self) -> str:
        return _digest(self.canonical_payload())


SequenceObserver = Callable[[LocalTransitionSequenceObservation], object]


def _expected_events(
    contacts: tuple[int | None, ...],
    *,
    mirror: bool,
    channel: int,
) -> tuple[LocalTransitionEvent, ...]:
    effective = tuple(
        None if column is None else (6 - column if mirror else column)
        for column in contacts
    )
    events = []
    for frame_index, (previous, current) in enumerate(
        zip(effective, effective[1:], strict=False),
        start=1,
    ):
        if previous is None or current is None or abs(previous - current) != 1:
            continue
        target_tick = frame_index + 1
        events.append(
            LocalTransitionEvent(
                target_tick=target_tick,
                source_tick=target_tick - 1,
                target_position=(_ACTIVE_ROW, current, channel),
                relative_source_position=(0, previous - current, 0),
                current_contact=1.0,
                prior_local_activation=1.0,
            )
        )
    return tuple(events)


def _run_sequence(
    sequence_id: str,
    *,
    mirror: bool = False,
    channel: int = _ACTIVE_CHANNEL,
    sample_offsets: Iterable[Iterable[int]] = _SAMPLE_OFFSETS,
    reverse_observation_order: bool = False,
    observer: SequenceObserver | None = None,
) -> LocalTransitionSequenceObservation:
    try:
        contacts = tuple(_SEQUENCES[sequence_id])
    except KeyError as exc:
        raise LocalTransitionEvidenceProbeError(
            f"unknown sequence: {sequence_id}"
        ) from exc
    effective_contacts = tuple(
        None if column is None else (6 - column if mirror else column)
        for column in contacts
    )
    interface = build_visual_mcm_interface(
        _config(),
        sample_offsets=tuple(tuple(offset) for offset in sample_offsets),
    )
    frame_energies = []
    frequency = [0] * _config().carrier_count
    self_overlap = 0.0
    local_total = 0.0
    events: list[LocalTransitionEvent] = []
    afterimage_zero = True
    frames_unchanged = True

    for frame_index, column in enumerate(effective_contacts):
        frame = _frame(column, channel=channel)
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
        frame_energy = sum(output.field_window.activation)
        frame_energies.append(frame_energy)
        afterimage_zero = afterimage_zero and all(
            value == 0.0 for value in output.field_window.afterimage
        )
        ordered_drives = sorted(drives, key=lambda item: item.previous.neuron_id)
        if reverse_observation_order:
            ordered_drives.reverse()
        for drive in ordered_drives:
            contact = drive.perception.receptor_contact
            current = 0.0 if contact is None else contact
            if current != 0.0:
                frequency[_position_index(drive.previous.position)] += 1
            self_overlap += current * drive.previous.activation
            for sample in drive.perception.local_samples:
                evidence = current * sample.activation
                local_total += evidence
                if evidence == 0.0:
                    continue
                events.append(
                    LocalTransitionEvent(
                        target_tick=drive.perception.tick,
                        source_tick=sample.source_tick,
                        target_position=tuple(drive.previous.position),
                        relative_source_position=tuple(sample.relative_position),
                        current_contact=current,
                        prior_local_activation=sample.activation,
                    )
                )

    ordered_events = tuple(
        sorted(
            events,
            key=lambda item: (
                item.target_tick,
                item.target_position,
                item.relative_source_position,
            ),
        )
    )
    expected = _expected_events(contacts, mirror=mirror, channel=channel)
    negative = sum(
        item.relative_source_position == (0, -1, 0) for item in ordered_events
    )
    positive = sum(
        item.relative_source_position == (0, 1, 0) for item in ordered_events
    )
    observation = LocalTransitionSequenceObservation(
        sequence_id=sequence_id,
        frame_count=len(contacts),
        total_energy=sum(frame_energies),
        frame_energies=tuple(frame_energies),
        position_frequency=tuple(frequency),
        self_overlap_total=self_overlap,
        local_transition_total=local_total,
        baseline_transition_total=float(len(expected)),
        source_negative_column_events=negative,
        source_positive_column_events=positive,
        other_local_events=len(ordered_events) - negative - positive,
        events=ordered_events,
        runtime_matches_fixed_neighbor_baseline=ordered_events == expected,
        afterimage_is_zero=afterimage_zero,
        input_frames_unchanged=frames_unchanged,
    )
    before_observer = _digest(asdict(observation))
    if observer is not None:
        observer(observation)
    if _digest(asdict(observation)) != before_observer:
        raise LocalTransitionEvidenceProbeError(
            "observer changed an immutable sequence observation"
        )
    return observation


def _canonical_reflected_observation(
    observation: LocalTransitionSequenceObservation,
) -> dict[str, object]:
    frequency = [0] * len(observation.position_frequency)
    for row in range(_GRID_ROWS):
        for column in range(_GRID_COLUMNS):
            for channel in range(_CHANNEL_COUNT):
                source = _position_index((row, 6 - column, channel))
                target = _position_index((row, column, channel))
                frequency[target] = observation.position_frequency[source]
    events = tuple(
        sorted(
            (
                LocalTransitionEvent(
                    target_tick=item.target_tick,
                    source_tick=item.source_tick,
                    target_position=(
                        item.target_position[0],
                        6 - item.target_position[1],
                        item.target_position[2],
                    ),
                    relative_source_position=(
                        item.relative_source_position[0],
                        -item.relative_source_position[1],
                        item.relative_source_position[2],
                    ),
                    current_contact=item.current_contact,
                    prior_local_activation=item.prior_local_activation,
                )
                for item in observation.events
            ),
            key=lambda item: (
                item.target_tick,
                item.target_position,
                item.relative_source_position,
            ),
        )
    )
    return {
        "sequence_id": observation.sequence_id,
        "frame_count": observation.frame_count,
        "total_energy": observation.total_energy,
        "frame_energies": observation.frame_energies,
        "position_frequency": tuple(frequency),
        "self_overlap_total": observation.self_overlap_total,
        "local_transition_total": observation.local_transition_total,
        "baseline_transition_total": observation.baseline_transition_total,
        "events": events,
    }


def _canonical_channel_observation(
    observation: LocalTransitionSequenceObservation,
    source_channel: int,
) -> dict[str, object]:
    frequency = [0] * len(observation.position_frequency)
    for row in range(_GRID_ROWS):
        for column in range(_GRID_COLUMNS):
            source = _position_index((row, column, source_channel))
            target = _position_index((row, column, _ACTIVE_CHANNEL))
            frequency[target] = observation.position_frequency[source]
    events = tuple(
        LocalTransitionEvent(
            target_tick=item.target_tick,
            source_tick=item.source_tick,
            target_position=(
                item.target_position[0],
                item.target_position[1],
                _ACTIVE_CHANNEL,
            ),
            relative_source_position=item.relative_source_position,
            current_contact=item.current_contact,
            prior_local_activation=item.prior_local_activation,
        )
        for item in observation.events
    )
    return {
        "sequence_id": observation.sequence_id,
        "frame_count": observation.frame_count,
        "total_energy": observation.total_energy,
        "frame_energies": observation.frame_energies,
        "position_frequency": tuple(frequency),
        "self_overlap_total": observation.self_overlap_total,
        "local_transition_total": observation.local_transition_total,
        "baseline_transition_total": observation.baseline_transition_total,
        "events": events,
    }


def _comparison_payload(
    observation: LocalTransitionSequenceObservation,
) -> dict[str, object]:
    return {
        "sequence_id": observation.sequence_id,
        "frame_count": observation.frame_count,
        "total_energy": observation.total_energy,
        "frame_energies": observation.frame_energies,
        "position_frequency": observation.position_frequency,
        "self_overlap_total": observation.self_overlap_total,
        "local_transition_total": observation.local_transition_total,
        "baseline_transition_total": observation.baseline_transition_total,
        "events": observation.events,
    }


def _core_payload(
    sequences: tuple[LocalTransitionSequenceObservation, ...],
) -> tuple[dict[str, object], ...]:
    return tuple(_comparison_payload(item) for item in sequences)


def run_local_transition_evidence_probe(
    *,
    sequence_order: Iterable[str] = SEQUENCE_IDS,
    observer: SequenceObserver | None = None,
    _verify_controls: bool = True,
) -> LocalTransitionEvidenceProbeResult:
    """Execute Methodik 036 without adding a field state or transition rule."""

    order = tuple(sequence_order)
    if len(order) != len(SEQUENCE_IDS) or set(order) != set(SEQUENCE_IDS):
        raise LocalTransitionEvidenceProbeError(
            "sequence_order must contain every preregistered sequence exactly once"
        )
    collected = tuple(
        _run_sequence(sequence_id, observer=observer) for sequence_id in order
    )
    sequences = tuple(sorted(collected, key=lambda item: item.sequence_id))
    by_id = {item.sequence_id: item for item in sequences}
    primary = tuple(
        by_id[sequence_id]
        for sequence_id in (
            "continuous_forward",
            "continuous_reverse",
            "permuted",
        )
    )

    reflected = tuple(
        sorted(
            (_run_sequence(sequence_id, mirror=True) for sequence_id in SEQUENCE_IDS),
            key=lambda item: item.sequence_id,
        )
    )
    reflected_equal = all(
        _comparison_payload(original)
        == _canonical_reflected_observation(mirrored)
        for original, mirrored in zip(sequences, reflected, strict=True)
    )

    channel_two = tuple(
        sorted(
            (_run_sequence(sequence_id, channel=2) for sequence_id in SEQUENCE_IDS),
            key=lambda item: item.sequence_id,
        )
    )
    channel_equal = all(
        _comparison_payload(original)
        == _canonical_channel_observation(permuted, 2)
        for original, permuted in zip(sequences, channel_two, strict=True)
    )

    reversed_offsets = tuple(
        sorted(
            (
                _run_sequence(
                    sequence_id,
                    sample_offsets=reversed(_SAMPLE_OFFSETS),
                )
                for sequence_id in SEQUENCE_IDS
            ),
            key=lambda item: item.sequence_id,
        )
    )
    offset_neutral = _core_payload(sequences) == _core_payload(reversed_offsets)

    reversed_observation = tuple(
        sorted(
            (
                _run_sequence(sequence_id, reverse_observation_order=True)
                for sequence_id in SEQUENCE_IDS
            ),
            key=lambda item: item.sequence_id,
        )
    )
    observation_neutral = _core_payload(sequences) == _core_payload(
        reversed_observation
    )

    observer_neutral = True
    sequence_order_neutral = True
    repeated_neutral = True
    if _verify_controls:
        without_observer = run_local_transition_evidence_probe(
            sequence_order=order,
            observer=None,
            _verify_controls=False,
        )
        reversed_order = run_local_transition_evidence_probe(
            sequence_order=reversed(order),
            observer=None,
            _verify_controls=False,
        )
        repeated = run_local_transition_evidence_probe(
            sequence_order=order,
            observer=None,
            _verify_controls=False,
        )
        observer_neutral = _core_payload(sequences) == _core_payload(
            without_observer.sequences
        )
        sequence_order_neutral = _core_payload(sequences) == _core_payload(
            reversed_order.sequences
        )
        repeated_neutral = _core_payload(sequences) == _core_payload(
            repeated.sequences
        )

    forward = by_id["continuous_forward"]
    reverse = by_id["continuous_reverse"]
    permuted = by_id["permuted"]
    interrupted = by_id["interrupted"]
    stationary = by_id["stationary"]
    result = LocalTransitionEvidenceProbeResult(
        sequences=sequences,
        primary_energy_equal=(
            len({item.total_energy for item in primary}) == 1
            and all(item.total_energy == 5.0 for item in primary)
        ),
        primary_position_frequency_equal=(
            len({item.position_frequency for item in primary}) == 1
        ),
        primary_self_overlap_zero=all(
            item.self_overlap_total == 0.0 for item in primary
        ),
        expected_event_counts_exact=(
            forward.local_transition_total == 4.0
            and forward.source_negative_column_events == 4
            and forward.source_positive_column_events == 0
            and reverse.local_transition_total == 4.0
            and reverse.source_negative_column_events == 0
            and reverse.source_positive_column_events == 4
            and permuted.local_transition_total == 0.0
            and interrupted.local_transition_total == 0.0
            and stationary.local_transition_total == 0.0
        ),
        all_runtime_events_match_fixed_neighbor_baseline=all(
            item.runtime_matches_fixed_neighbor_baseline for item in sequences
        ),
        interruption_removes_events=(
            interrupted.total_energy == 5.0
            and interrupted.self_overlap_total == 0.0
            and interrupted.local_transition_total == 0.0
        ),
        stationary_separates_self_from_neighbor=(
            stationary.total_energy == 5.0
            and stationary.self_overlap_total == 4.0
            and stationary.local_transition_total == 0.0
        ),
        time_reversal_is_symmetric=(
            forward.local_transition_total == reverse.local_transition_total
            and forward.source_negative_column_events
            == reverse.source_positive_column_events
            and forward.source_positive_column_events
            == reverse.source_negative_column_events
        ),
        spatial_reflection_is_equivariant=reflected_equal,
        channel_permutation_is_equivariant=channel_equal,
        offset_order_is_neutral=offset_neutral,
        observation_order_is_neutral=observation_neutral,
        observer_is_neutral=observer_neutral,
        sequence_order_is_neutral=sequence_order_neutral,
        repeated_run_is_neutral=repeated_neutral,
    )
    controls = {
        "primary_energy_equal": result.primary_energy_equal,
        "primary_position_frequency_equal": result.primary_position_frequency_equal,
        "primary_self_overlap_zero": result.primary_self_overlap_zero,
        "expected_event_counts_exact": result.expected_event_counts_exact,
        "all_runtime_events_match_fixed_neighbor_baseline": (
            result.all_runtime_events_match_fixed_neighbor_baseline
        ),
        "interruption_removes_events": result.interruption_removes_events,
        "stationary_separates_self_from_neighbor": (
            result.stationary_separates_self_from_neighbor
        ),
        "time_reversal_is_symmetric": result.time_reversal_is_symmetric,
        "spatial_reflection_is_equivariant": result.spatial_reflection_is_equivariant,
        "channel_permutation_is_equivariant": (
            result.channel_permutation_is_equivariant
        ),
        "offset_order_is_neutral": result.offset_order_is_neutral,
        "observation_order_is_neutral": result.observation_order_is_neutral,
        "observer_is_neutral": result.observer_is_neutral,
        "sequence_order_is_neutral": result.sequence_order_is_neutral,
        "repeated_run_is_neutral": result.repeated_run_is_neutral,
        "retains_no_raw_frames": not result.retains_raw_frames,
        "does_not_write_back": not result.writes_back,
        "does_not_release_disposition": not result.releases_disposition,
    }
    failed = tuple(name for name, passed in controls.items() if not passed)
    if failed:
        raise LocalTransitionEvidenceProbeError(
            f"Methodik 036 controls did not close exactly: {', '.join(failed)}"
        )
    return result


def local_transition_evidence_probe_public_roles() -> tuple[str, ...]:
    classes = (
        LocalTransitionEvent,
        LocalTransitionSequenceObservation,
        LocalTransitionEvidenceProbeResult,
    )
    return tuple(item.name for cls in classes for item in fields(cls))
