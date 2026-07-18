"""Passive collision audit for a fixed temporal summary bundle."""

from __future__ import annotations

from dataclasses import dataclass, fields
from math import fsum

from .receptor_rate_invariance_probe import (
    ContactRateRepresentation,
    TimedContactSegment,
)
from .temporal_effect_functional_contract import (
    normalize_supported_contact_path,
    temporal_effect_contract_worlds,
)


@dataclass(frozen=True, slots=True)
class TemporalAdversarialPaths:
    first: ContactRateRepresentation
    reversed_inner_order: ContactRateRepresentation


@dataclass(frozen=True, slots=True)
class TemporalCompactSummary:
    segment_count: int
    total_duration: int
    first_contact: float
    last_contact: float
    duration_weighted_mean: float
    duration_weighted_second_moment: float
    minimum_contact: float
    maximum_contact: float
    total_variation: float
    positive_variation: float
    negative_variation: float
    adjacent_product_sum: float
    turning_count: int


@dataclass(frozen=True, slots=True)
class TemporalCompactSummaryCollisionAuditResult:
    first_supported_path: tuple[TimedContactSegment, ...]
    reversed_supported_path: tuple[TimedContactSegment, ...]
    first_summary: TemporalCompactSummary
    reversed_summary: TemporalCompactSummary
    paths_are_exact_time_reversals: bool
    supported_paths_distinct: bool
    summaries_equal: bool
    representation_invariance_rechecked: bool
    summary_width: int
    summary_width_fixed: bool
    all_compact_representations_falsified: bool
    field_effect_performed: bool
    runtime_candidate_released: bool


def temporal_adversarial_paths() -> TemporalAdversarialPaths:
    """Return equal-endpoint paths with reversed inner temporal order."""

    first_values = (0.5, 0.2, 0.8, 0.3, 0.7, 0.5)
    reversed_values = tuple(reversed(first_values))

    def build(
        representation_id: str,
        values: tuple[float, ...],
    ) -> ContactRateRepresentation:
        return ContactRateRepresentation(
            representation_id,
            tuple(
                TimedContactSegment(tick, tick + 1, contact)
                for tick, contact in enumerate(values)
            ),
        )

    return TemporalAdversarialPaths(
        first=build("adversarial.first", first_values),
        reversed_inner_order=build(
            "adversarial.reversed",
            reversed_values,
        ),
    )


def compact_temporal_summary(
    representation: ContactRateRepresentation,
) -> TemporalCompactSummary:
    """Observe fixed-width path statistics without proposing field dynamics."""

    path = normalize_supported_contact_path(representation)
    contacts = tuple(segment.contact for segment in path)
    durations = tuple(
        segment.end_tick - segment.start_tick
        for segment in path
    )
    changes = tuple(
        current - previous
        for previous, current in zip(contacts, contacts[1:])
    )
    total_duration = sum(durations)
    weighted_sum = fsum(
        duration * contact
        for duration, contact in zip(durations, contacts)
    )
    weighted_second_moment = fsum(
        duration * contact * contact
        for duration, contact in zip(durations, contacts)
    )
    signs = tuple(
        1 if change > 0.0 else -1 if change < 0.0 else 0
        for change in changes
    )
    nonzero_signs = tuple(sign for sign in signs if sign)

    return TemporalCompactSummary(
        segment_count=len(path),
        total_duration=total_duration,
        first_contact=contacts[0],
        last_contact=contacts[-1],
        duration_weighted_mean=weighted_sum / total_duration,
        duration_weighted_second_moment=(
            weighted_second_moment / total_duration
        ),
        minimum_contact=min(contacts),
        maximum_contact=max(contacts),
        total_variation=fsum(abs(change) for change in changes),
        positive_variation=fsum(
            change for change in changes if change > 0.0
        ),
        negative_variation=fsum(
            -change for change in changes if change < 0.0
        ),
        adjacent_product_sum=fsum(
            previous * current
            for previous, current in zip(contacts, contacts[1:])
        ),
        turning_count=sum(
            first != second
            for first, second in zip(nonzero_signs, nonzero_signs[1:])
        ),
    )


def run_temporal_compact_summary_collision_audit(
) -> TemporalCompactSummaryCollisionAuditResult:
    """Test one broad fixed summary bundle against a reversal collision."""

    paths = temporal_adversarial_paths()
    first_path = normalize_supported_contact_path(paths.first)
    reversed_path = normalize_supported_contact_path(
        paths.reversed_inner_order
    )
    first_contacts = tuple(item.contact for item in first_path)
    reversed_contacts = tuple(item.contact for item in reversed_path)
    first_summary = compact_temporal_summary(paths.first)
    reversed_summary = compact_temporal_summary(
        paths.reversed_inner_order
    )
    contract_worlds = temporal_effect_contract_worlds()
    summary_width = len(fields(TemporalCompactSummary))

    return TemporalCompactSummaryCollisionAuditResult(
        first_supported_path=first_path,
        reversed_supported_path=reversed_path,
        first_summary=first_summary,
        reversed_summary=reversed_summary,
        paths_are_exact_time_reversals=(
            first_contacts == tuple(reversed(reversed_contacts))
        ),
        supported_paths_distinct=first_path != reversed_path,
        summaries_equal=first_summary == reversed_summary,
        representation_invariance_rechecked=(
            compact_temporal_summary(contract_worlds.dense_constant)
            == compact_temporal_summary(contract_worlds.sparse_constant)
        ),
        summary_width=summary_width,
        summary_width_fixed=True,
        all_compact_representations_falsified=False,
        field_effect_performed=False,
        runtime_candidate_released=False,
    )


def temporal_compact_summary_collision_audit_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            TemporalAdversarialPaths,
            TemporalCompactSummary,
            TemporalCompactSummaryCollisionAuditResult,
        )
        for item in fields(contract)
    )
