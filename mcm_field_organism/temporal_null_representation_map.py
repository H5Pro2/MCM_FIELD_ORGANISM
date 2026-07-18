"""Passive null-representation map for temporal functional contract 019."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
from typing import Callable

from .receptor_rate_invariance_probe import ContactRateRepresentation
from .temporal_effect_functional_contract import (
    duration_weighted_contact,
    normalize_supported_contact_path,
    temporal_effect_contract_worlds,
)


Payload = tuple[object, ...]
Representation = Callable[[ContactRateRepresentation], Payload]


@dataclass(frozen=True, slots=True)
class TemporalNullRepresentationEvaluation:
    representation_id: str
    dense_payload: str
    sparse_payload: str
    first_order_payload: str
    second_order_payload: str
    dense_payload_item_count: int
    sparse_payload_item_count: int
    first_order_payload_item_count: int
    second_order_payload_item_count: int
    representation_invariant: bool
    ordered_paths_accessible: bool
    satisfies_both_contract_axes: bool
    fixed_width_in_controls: bool


@dataclass(frozen=True, slots=True)
class TemporalNullRepresentationMapResult:
    evaluations: tuple[TemporalNullRepresentationEvaluation, ...]
    representation_invariant_ids: tuple[str, ...]
    order_accessible_ids: tuple[str, ...]
    satisfies_both_ids: tuple[str, ...]
    minimal_representation_proven: bool
    runtime_candidate_released: bool


def _event_count(representation: ContactRateRepresentation) -> Payload:
    return (len(representation.segments),)


def _endpoint(representation: ContactRateRepresentation) -> Payload:
    return (representation.segments[-1].contact,)


def _duration_weighted_mean(
    representation: ContactRateRepresentation,
) -> Payload:
    return (duration_weighted_contact(representation),)


def _supported_path(representation: ContactRateRepresentation) -> Payload:
    return tuple(
        (segment.start_tick, segment.end_tick, segment.contact)
        for segment in normalize_supported_contact_path(representation)
    )


def _payload_text(payload: Payload) -> str:
    return json.dumps(payload, allow_nan=False, separators=(",", ":"))


def _evaluate(
    representation_id: str,
    observer: Representation,
) -> TemporalNullRepresentationEvaluation:
    worlds = temporal_effect_contract_worlds()
    dense = observer(worlds.dense_constant)
    sparse = observer(worlds.sparse_constant)
    first = observer(worlds.first_order)
    second = observer(worlds.second_order)
    invariant = dense == sparse
    order_accessible = first != second
    counts = tuple(len(payload) for payload in (dense, sparse, first, second))
    return TemporalNullRepresentationEvaluation(
        representation_id=representation_id,
        dense_payload=_payload_text(dense),
        sparse_payload=_payload_text(sparse),
        first_order_payload=_payload_text(first),
        second_order_payload=_payload_text(second),
        dense_payload_item_count=counts[0],
        sparse_payload_item_count=counts[1],
        first_order_payload_item_count=counts[2],
        second_order_payload_item_count=counts[3],
        representation_invariant=invariant,
        ordered_paths_accessible=order_accessible,
        satisfies_both_contract_axes=invariant and order_accessible,
        fixed_width_in_controls=len(set(counts)) == 1,
    )


def run_temporal_null_representation_map(
) -> TemporalNullRepresentationMapResult:
    """Evaluate information loss only; perform no field transition."""

    evaluations = tuple(
        _evaluate(representation_id, observer)
        for representation_id, observer in (
            ("event_count", _event_count),
            ("endpoint", _endpoint),
            ("duration_weighted_mean", _duration_weighted_mean),
            ("full_supported_path", _supported_path),
        )
    )
    return TemporalNullRepresentationMapResult(
        evaluations=evaluations,
        representation_invariant_ids=tuple(
            item.representation_id
            for item in evaluations
            if item.representation_invariant
        ),
        order_accessible_ids=tuple(
            item.representation_id
            for item in evaluations
            if item.ordered_paths_accessible
        ),
        satisfies_both_ids=tuple(
            item.representation_id
            for item in evaluations
            if item.satisfies_both_contract_axes
        ),
        minimal_representation_proven=False,
        runtime_candidate_released=False,
    )


def temporal_null_representation_map_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            TemporalNullRepresentationEvaluation,
            TemporalNullRepresentationMapResult,
        )
        for item in fields(contract)
    )
