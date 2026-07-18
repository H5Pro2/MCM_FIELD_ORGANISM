"""Synthetic ground-truth contract for temporal field-effect candidates."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .receptor_rate_invariance_probe import (
    ContactRateRepresentation,
    TimedContactSegment,
)


@dataclass(frozen=True, slots=True)
class RepresentationRefinementEvidence:
    dense_segment_count: int
    sparse_segment_count: int
    dense_supported_path: tuple[TimedContactSegment, ...]
    sparse_supported_path: tuple[TimedContactSegment, ...]
    same_supported_path: bool


@dataclass(frozen=True, slots=True)
class OrderedPathEvidence:
    first_supported_path: tuple[TimedContactSegment, ...]
    second_supported_path: tuple[TimedContactSegment, ...]
    shared_endpoint: float
    first_duration_weighted_contact: float
    second_duration_weighted_contact: float
    endpoints_equal: bool
    duration_weighted_contacts_equal: bool
    ordered_paths_distinct: bool


@dataclass(frozen=True, slots=True)
class TemporalEffectFunctionalContractResult:
    representation_refinement: RepresentationRefinementEvidence
    ordered_path: OrderedPathEvidence
    require_equal_consequence_for_same_supported_path: bool
    require_candidate_access_to_ordered_path: bool
    field_effect_equation_selected: bool
    runtime_candidate_released: bool


@dataclass(frozen=True, slots=True)
class TemporalEffectContractWorlds:
    dense_constant: ContactRateRepresentation
    sparse_constant: ContactRateRepresentation
    first_order: ContactRateRepresentation
    second_order: ContactRateRepresentation


def normalize_supported_contact_path(
    representation: ContactRateRepresentation,
) -> tuple[TimedContactSegment, ...]:
    """Merge only equal adjacent synthetic supports for ground-truth comparison."""

    if not isinstance(representation, ContactRateRepresentation):
        raise TypeError("normalization requires ContactRateRepresentation")
    normalized: list[TimedContactSegment] = []
    for segment in representation.segments:
        if normalized and normalized[-1].contact == segment.contact:
            previous = normalized[-1]
            normalized[-1] = TimedContactSegment(
                previous.start_tick,
                segment.end_tick,
                previous.contact,
            )
        else:
            normalized.append(segment)
    return tuple(normalized)


def duration_weighted_contact(
    representation: ContactRateRepresentation,
) -> float:
    """Observer baseline; it is not a proposed field integration rule."""

    weighted = sum(
        (segment.end_tick - segment.start_tick) * segment.contact
        for segment in representation.segments
    )
    return weighted / representation.end_tick


def _constant_representation(
    representation_id: str,
    boundaries: tuple[int, ...],
) -> ContactRateRepresentation:
    return ContactRateRepresentation(
        representation_id,
        tuple(
            TimedContactSegment(start, end, 0.5)
            for start, end in zip(boundaries, boundaries[1:])
        ),
    )


def temporal_effect_contract_worlds() -> TemporalEffectContractWorlds:
    """Return the immutable synthetic worlds registered by contract 019."""

    return TemporalEffectContractWorlds(
        dense_constant=_constant_representation(
            "constant.dense",
            tuple(range(0, 11)),
        ),
        sparse_constant=_constant_representation(
            "constant.sparse",
            (0, 5, 10),
        ),
        first_order=ContactRateRepresentation(
            "order.first",
            (
                TimedContactSegment(0, 3, 0.2),
                TimedContactSegment(3, 6, 0.8),
                TimedContactSegment(6, 9, 0.5),
            ),
        ),
        second_order=ContactRateRepresentation(
            "order.second",
            (
                TimedContactSegment(0, 3, 0.8),
                TimedContactSegment(3, 6, 0.2),
                TimedContactSegment(6, 9, 0.5),
            ),
        ),
    )


def run_temporal_effect_functional_contract(
) -> TemporalEffectFunctionalContractResult:
    """Register invariance and order observability without a field candidate."""

    worlds = temporal_effect_contract_worlds()
    dense = worlds.dense_constant
    sparse = worlds.sparse_constant
    dense_path = normalize_supported_contact_path(dense)
    sparse_path = normalize_supported_contact_path(sparse)

    first_order = worlds.first_order
    second_order = worlds.second_order
    first_path = normalize_supported_contact_path(first_order)
    second_path = normalize_supported_contact_path(second_order)
    first_weighted = duration_weighted_contact(first_order)
    second_weighted = duration_weighted_contact(second_order)
    endpoint = first_order.segments[-1].contact

    return TemporalEffectFunctionalContractResult(
        representation_refinement=RepresentationRefinementEvidence(
            dense_segment_count=len(dense.segments),
            sparse_segment_count=len(sparse.segments),
            dense_supported_path=dense_path,
            sparse_supported_path=sparse_path,
            same_supported_path=dense_path == sparse_path,
        ),
        ordered_path=OrderedPathEvidence(
            first_supported_path=first_path,
            second_supported_path=second_path,
            shared_endpoint=endpoint,
            first_duration_weighted_contact=first_weighted,
            second_duration_weighted_contact=second_weighted,
            endpoints_equal=(
                endpoint == second_order.segments[-1].contact
            ),
            duration_weighted_contacts_equal=(
                first_weighted == second_weighted
            ),
            ordered_paths_distinct=first_path != second_path,
        ),
        require_equal_consequence_for_same_supported_path=True,
        require_candidate_access_to_ordered_path=True,
        field_effect_equation_selected=False,
        runtime_candidate_released=False,
    )


def temporal_effect_functional_contract_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            RepresentationRefinementEvidence,
            OrderedPathEvidence,
            TemporalEffectFunctionalContractResult,
            TemporalEffectContractWorlds,
        )
        for item in fields(contract)
    )
