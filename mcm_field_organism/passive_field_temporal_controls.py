"""Passive receptor-rate and future-event controls for field candidates."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, fields
from typing import Iterable

from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import MCMNeuronTransition
from .passive_field_segmentation_comparison import (
    BoundaryDistributionFactory,
    FieldFactory,
    PassiveFieldEndpoint,
    PassiveFieldSegmentationComparison,
    PassiveFieldSegmentationError,
    TransitionFactory,
    compare_passive_field_segmentations,
)
from .receptor_time_alignment import ReceptorTimeSequence


class PassiveFieldTemporalControlError(ValueError):
    """Raised when temporal control branches do not isolate one axis."""


@dataclass(frozen=True, slots=True)
class PassiveReceptorRateComparison:
    """Same source support under two technical completion multiplicities."""

    reference: PassiveFieldSegmentationComparison
    repeated: PassiveFieldSegmentationComparison
    reference_event_count: int
    repeated_event_count: int
    coarse_endpoints_equal: bool
    fine_endpoints_equal: bool


@dataclass(frozen=True, slots=True)
class PassiveFutureEventCausalityComparison:
    """Same completed past with and without a later completed event."""

    cutoff_tick: int
    control: PassiveFieldSegmentationComparison
    with_future: PassiveFieldSegmentationComparison
    coarse_prefix_endpoints_equal: bool
    fine_prefix_endpoints_equal: bool
    coarse_final_endpoints_equal: bool
    fine_final_endpoints_equal: bool


@dataclass(frozen=True, slots=True)
class PassiveSimultaneousOrderComparison:
    """Same simultaneous completions under reversed sequence declaration."""

    simultaneous_completion_ticks: tuple[int, ...]
    declared_order: PassiveFieldSegmentationComparison
    reversed_order: PassiveFieldSegmentationComparison
    coarse_traces_equal: bool
    fine_traces_equal: bool


def _sequences(
    values: Iterable[ReceptorTimeSequence],
    role: str,
) -> tuple[ReceptorTimeSequence, ...]:
    result = tuple(values)
    if not result or any(not isinstance(item, ReceptorTimeSequence) for item in result):
        raise PassiveFieldTemporalControlError(
            f"{role} requires receptor time sequences"
        )
    identities = tuple(
        (item.modality_id, item.geometry_id, item.clock_id) for item in result
    )
    if len(set(identities)) != len(identities):
        raise PassiveFieldTemporalControlError(
            f"{role} sequence identities must be unique"
        )
    return tuple(sorted(result, key=lambda item: item.modality_id))


def _source_signature(item) -> tuple[object, ...]:
    frame = item.frame
    return (
        frame.modality_id,
        frame.geometry_id,
        frame.clock_id,
        frame.window_start_tick,
        frame.window_end_tick,
        frame.carrier_ids,
        frame.values,
    )


def _source_support_counts(
    sequences: tuple[ReceptorTimeSequence, ...],
) -> Counter[tuple[object, ...]]:
    return Counter(
        _source_signature(item)
        for sequence in sequences
        for item in sequence.frames
    )


def _same_sequence_anatomy(
    first: tuple[ReceptorTimeSequence, ...],
    second: tuple[ReceptorTimeSequence, ...],
) -> bool:
    return tuple(
        (item.modality_id, item.geometry_id, item.clock_id) for item in first
    ) == tuple(
        (item.modality_id, item.geometry_id, item.clock_id) for item in second
    )


def _transition_factory(
    value: TransitionFactory,
) -> TransitionFactory:
    if not callable(value):
        raise PassiveFieldTemporalControlError(
            "temporal control requires one explicit transition factory"
        )

    def build() -> MCMNeuronTransition:
        transition = value()
        if not callable(transition):
            raise PassiveFieldTemporalControlError(
                "transition factory must return one explicit transition"
            )
        return transition

    return build


def compare_passive_receptor_rate(
    reference_sequences: Iterable[ReceptorTimeSequence],
    repeated_sequences: Iterable[ReceptorTimeSequence],
    coarse_steps: Iterable[MCMFieldStepTime],
    fine_steps: Iterable[MCMFieldStepTime],
    *,
    field_factory: FieldFactory,
    transition_factory: TransitionFactory,
    distribution_factory: BoundaryDistributionFactory,
) -> PassiveReceptorRateComparison:
    """Compare extra completions that add no new reduced source support."""

    reference_in = _sequences(reference_sequences, "reference branch")
    repeated_in = _sequences(repeated_sequences, "repeated branch")
    if not _same_sequence_anatomy(reference_in, repeated_in):
        raise PassiveFieldTemporalControlError(
            "rate branches must use identical receptor sequence anatomy"
        )
    reference_support = _source_support_counts(reference_in)
    repeated_support = _source_support_counts(repeated_in)
    if set(reference_support) != set(repeated_support):
        raise PassiveFieldTemporalControlError(
            "rate branches must contain identical reduced source support"
        )
    if any(
        repeated_support[signature] < count
        for signature, count in reference_support.items()
    ):
        raise PassiveFieldTemporalControlError(
            "repeated branch cannot remove source-support observations"
        )
    reference_event_count = sum(reference_support.values())
    repeated_event_count = sum(repeated_support.values())
    if repeated_event_count <= reference_event_count:
        raise PassiveFieldTemporalControlError(
            "repeated branch must add technical completions"
        )

    coarse_steps_in = tuple(coarse_steps)
    fine_steps_in = tuple(fine_steps)
    checked_transition_factory = _transition_factory(transition_factory)
    try:
        reference = compare_passive_field_segmentations(
            reference_in,
            coarse_steps_in,
            fine_steps_in,
            field_factory=field_factory,
            transition_factory=checked_transition_factory,
            distribution_factory=distribution_factory,
        )
        repeated = compare_passive_field_segmentations(
            repeated_in,
            coarse_steps_in,
            fine_steps_in,
            field_factory=field_factory,
            transition_factory=checked_transition_factory,
            distribution_factory=distribution_factory,
        )
    except PassiveFieldSegmentationError as exc:
        raise PassiveFieldTemporalControlError(
            f"passive receptor-rate comparison failed: {exc}"
        ) from exc
    if (
        reference.coarse.initial_field_digest
        != repeated.coarse.initial_field_digest
    ):
        raise PassiveFieldTemporalControlError(
            "rate branches must rebuild the same initial field"
        )
    return PassiveReceptorRateComparison(
        reference=reference,
        repeated=repeated,
        reference_event_count=reference_event_count,
        repeated_event_count=repeated_event_count,
        coarse_endpoints_equal=(
            reference.coarse.endpoint == repeated.coarse.endpoint
        ),
        fine_endpoints_equal=(
            reference.fine.endpoint == repeated.fine.endpoint
        ),
    )


def _completed_history(
    sequences: tuple[ReceptorTimeSequence, ...],
    cutoff_tick: int,
) -> tuple[tuple[str, tuple[object, ...]], ...]:
    return tuple(
        (
            sequence.modality_id,
            tuple(
                item
                for item in sequence.frames
                if item.field_time.window_end_tick <= cutoff_tick
            ),
        )
        for sequence in sequences
    )


def _future_event_count(
    sequences: tuple[ReceptorTimeSequence, ...],
    cutoff_tick: int,
) -> int:
    return sum(
        item.field_time.window_end_tick > cutoff_tick
        for sequence in sequences
        for item in sequence.frames
    )


def _prefix_endpoints(
    comparison: PassiveFieldSegmentationComparison,
    cutoff_tick: int,
    segmentation: str,
) -> tuple[PassiveFieldEndpoint, ...]:
    branch = (
        comparison.coarse if segmentation == "coarse" else comparison.fine
    )
    ending_ticks = tuple(step.step_time.end_tick for step in branch.steps)
    if cutoff_tick not in ending_ticks:
        raise PassiveFieldTemporalControlError(
            f"{segmentation} segmentation must end one step at cutoff_tick"
        )
    return tuple(
        step.endpoint
        for step in branch.steps
        if step.step_time.end_tick <= cutoff_tick
    )


def compare_passive_future_event_causality(
    control_sequences: Iterable[ReceptorTimeSequence],
    with_future_sequences: Iterable[ReceptorTimeSequence],
    coarse_steps: Iterable[MCMFieldStepTime],
    fine_steps: Iterable[MCMFieldStepTime],
    *,
    cutoff_tick: int,
    field_factory: FieldFactory,
    transition_factory: TransitionFactory,
    distribution_factory: BoundaryDistributionFactory,
) -> PassiveFutureEventCausalityComparison:
    """Check that a later completion cannot alter an earlier field prefix."""

    if isinstance(cutoff_tick, bool) or not isinstance(cutoff_tick, int):
        raise PassiveFieldTemporalControlError("cutoff_tick must be an integer")
    control_in = _sequences(control_sequences, "causality control")
    future_in = _sequences(with_future_sequences, "future branch")
    if not _same_sequence_anatomy(control_in, future_in):
        raise PassiveFieldTemporalControlError(
            "causality branches must use identical receptor sequence anatomy"
        )
    if _completed_history(control_in, cutoff_tick) != _completed_history(
        future_in,
        cutoff_tick,
    ):
        raise PassiveFieldTemporalControlError(
            "causality branches must have identical completed history at cutoff"
        )
    if _future_event_count(control_in, cutoff_tick) != 0:
        raise PassiveFieldTemporalControlError(
            "causality control cannot contain events completed after cutoff"
        )
    if _future_event_count(future_in, cutoff_tick) == 0:
        raise PassiveFieldTemporalControlError(
            "future branch requires an event completed after cutoff"
        )

    coarse_steps_in = tuple(coarse_steps)
    fine_steps_in = tuple(fine_steps)
    checked_transition_factory = _transition_factory(transition_factory)
    try:
        control = compare_passive_field_segmentations(
            control_in,
            coarse_steps_in,
            fine_steps_in,
            field_factory=field_factory,
            transition_factory=checked_transition_factory,
            distribution_factory=distribution_factory,
        )
        with_future = compare_passive_field_segmentations(
            future_in,
            coarse_steps_in,
            fine_steps_in,
            field_factory=field_factory,
            transition_factory=checked_transition_factory,
            distribution_factory=distribution_factory,
        )
    except PassiveFieldSegmentationError as exc:
        raise PassiveFieldTemporalControlError(
            f"passive future-event comparison failed: {exc}"
        ) from exc
    if control.coarse.initial_field_digest != with_future.coarse.initial_field_digest:
        raise PassiveFieldTemporalControlError(
            "causality branches must rebuild the same initial field"
        )
    control_coarse_prefix = _prefix_endpoints(control, cutoff_tick, "coarse")
    future_coarse_prefix = _prefix_endpoints(with_future, cutoff_tick, "coarse")
    control_fine_prefix = _prefix_endpoints(control, cutoff_tick, "fine")
    future_fine_prefix = _prefix_endpoints(with_future, cutoff_tick, "fine")
    return PassiveFutureEventCausalityComparison(
        cutoff_tick=cutoff_tick,
        control=control,
        with_future=with_future,
        coarse_prefix_endpoints_equal=(
            control_coarse_prefix == future_coarse_prefix
        ),
        fine_prefix_endpoints_equal=(control_fine_prefix == future_fine_prefix),
        coarse_final_endpoints_equal=(
            control.coarse.endpoint == with_future.coarse.endpoint
        ),
        fine_final_endpoints_equal=(
            control.fine.endpoint == with_future.fine.endpoint
        ),
    )


def compare_passive_simultaneous_order(
    sequences: Iterable[ReceptorTimeSequence],
    coarse_steps: Iterable[MCMFieldStepTime],
    fine_steps: Iterable[MCMFieldStepTime],
    *,
    field_factory: FieldFactory,
    transition_factory: TransitionFactory,
    distribution_factory: BoundaryDistributionFactory,
) -> PassiveSimultaneousOrderComparison:
    """Reverse declaration order without ordering simultaneous field causes."""

    sequences_in = tuple(sequences)
    if len(sequences_in) < 2 or any(
        not isinstance(item, ReceptorTimeSequence) for item in sequences_in
    ):
        raise PassiveFieldTemporalControlError(
            "simultaneous-order control requires at least two receptor sequences"
        )
    identities = tuple(
        (item.modality_id, item.geometry_id, item.clock_id)
        for item in sequences_in
    )
    if len(set(identities)) != len(identities):
        raise PassiveFieldTemporalControlError(
            "simultaneous-order sequence identities must be unique"
        )
    completions: dict[int, set[str]] = {}
    for sequence in sequences_in:
        for item in sequence.frames:
            completions.setdefault(
                item.field_time.window_end_tick,
                set(),
            ).add(sequence.modality_id)
    simultaneous_ticks = tuple(
        tick
        for tick, modalities in sorted(completions.items())
        if len(modalities) > 1
    )
    if not simultaneous_ticks:
        raise PassiveFieldTemporalControlError(
            "simultaneous-order control requires a shared completion tick"
        )

    coarse_steps_in = tuple(coarse_steps)
    fine_steps_in = tuple(fine_steps)
    checked_transition_factory = _transition_factory(transition_factory)
    try:
        declared = compare_passive_field_segmentations(
            sequences_in,
            coarse_steps_in,
            fine_steps_in,
            field_factory=field_factory,
            transition_factory=checked_transition_factory,
            distribution_factory=distribution_factory,
        )
        reversed_order = compare_passive_field_segmentations(
            tuple(reversed(sequences_in)),
            coarse_steps_in,
            fine_steps_in,
            field_factory=field_factory,
            transition_factory=checked_transition_factory,
            distribution_factory=distribution_factory,
        )
    except PassiveFieldSegmentationError as exc:
        raise PassiveFieldTemporalControlError(
            f"passive simultaneous-order comparison failed: {exc}"
        ) from exc
    if (
        declared.coarse.initial_field_digest
        != reversed_order.coarse.initial_field_digest
    ):
        raise PassiveFieldTemporalControlError(
            "simultaneous-order branches must rebuild the same initial field"
        )
    return PassiveSimultaneousOrderComparison(
        simultaneous_completion_ticks=simultaneous_ticks,
        declared_order=declared,
        reversed_order=reversed_order,
        coarse_traces_equal=(declared.coarse == reversed_order.coarse),
        fine_traces_equal=(declared.fine == reversed_order.fine),
    )


def passive_field_temporal_controls_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            PassiveReceptorRateComparison,
            PassiveFutureEventCausalityComparison,
            PassiveSimultaneousOrderComparison,
        )
        for item in fields(contract)
    )
