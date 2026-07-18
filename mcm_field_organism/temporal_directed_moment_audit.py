"""Passive audit of one directed temporal-moment null observer."""

from __future__ import annotations

from dataclasses import dataclass, fields
from math import fsum, isclose

from .receptor_rate_invariance_probe import (
    ContactRateRepresentation,
    TimedContactSegment,
)
from .temporal_compact_summary_collision_audit import (
    temporal_adversarial_paths,
)
from .temporal_effect_functional_contract import (
    normalize_supported_contact_path,
    temporal_effect_contract_worlds,
)


@dataclass(frozen=True, slots=True)
class TemporalMomentCollisionPaths:
    first: ContactRateRepresentation
    second: ContactRateRepresentation


@dataclass(frozen=True, slots=True)
class TemporalDirectedMomentAuditResult:
    dense_constant_moment: float
    sparse_constant_moment: float
    representation_invariance_rechecked: bool
    reversal_first_moment: float
    reversal_second_moment: float
    reversal_paths_distinguished: bool
    reversal_antisymmetry_observed: bool
    collision_first_moment: float
    collision_second_moment: float
    collision_paths_distinct: bool
    collision_moments_equal: bool
    observer_width: int
    observer_width_fixed: bool
    unique_order_encoding_proven: bool
    field_effect_performed: bool
    runtime_candidate_released: bool


def centered_first_temporal_moment(
    representation: ContactRateRepresentation,
) -> float:
    """Integrate supported contact around time center; observer only."""

    path = normalize_supported_contact_path(representation)
    total_duration = path[-1].end_tick
    center = total_duration / 2.0
    integral = fsum(
        segment.contact
        * (
            (segment.end_tick - center) ** 2
            - (segment.start_tick - center) ** 2
        )
        / 2.0
        for segment in path
    )
    return integral / (total_duration * total_duration)


def temporal_moment_collision_paths() -> TemporalMomentCollisionPaths:
    """Return distinct paths with equal support, mean, and first moment."""

    first_values = (0.5, 0.2, 0.3, 0.8, 0.7, 0.5)
    second_values = (0.5, 0.3, 0.2, 0.7, 0.8, 0.5)

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

    return TemporalMomentCollisionPaths(
        first=build("moment.collision.first", first_values),
        second=build("moment.collision.second", second_values),
    )


def run_temporal_directed_moment_audit(
) -> TemporalDirectedMomentAuditResult:
    """Probe refinement, reversal, and collision without field dynamics."""

    contract_worlds = temporal_effect_contract_worlds()
    dense_moment = centered_first_temporal_moment(
        contract_worlds.dense_constant
    )
    sparse_moment = centered_first_temporal_moment(
        contract_worlds.sparse_constant
    )

    reversal_paths = temporal_adversarial_paths()
    reversal_first = centered_first_temporal_moment(reversal_paths.first)
    reversal_second = centered_first_temporal_moment(
        reversal_paths.reversed_inner_order
    )

    collision_paths = temporal_moment_collision_paths()
    collision_first = centered_first_temporal_moment(collision_paths.first)
    collision_second = centered_first_temporal_moment(collision_paths.second)
    collision_first_path = normalize_supported_contact_path(
        collision_paths.first
    )
    collision_second_path = normalize_supported_contact_path(
        collision_paths.second
    )

    return TemporalDirectedMomentAuditResult(
        dense_constant_moment=dense_moment,
        sparse_constant_moment=sparse_moment,
        representation_invariance_rechecked=isclose(
            dense_moment,
            sparse_moment,
            rel_tol=0.0,
            abs_tol=1e-15,
        ),
        reversal_first_moment=reversal_first,
        reversal_second_moment=reversal_second,
        reversal_paths_distinguished=not isclose(
            reversal_first,
            reversal_second,
            rel_tol=0.0,
            abs_tol=1e-15,
        ),
        reversal_antisymmetry_observed=isclose(
            reversal_first,
            -reversal_second,
            rel_tol=0.0,
            abs_tol=1e-15,
        ),
        collision_first_moment=collision_first,
        collision_second_moment=collision_second,
        collision_paths_distinct=(
            collision_first_path != collision_second_path
        ),
        collision_moments_equal=isclose(
            collision_first,
            collision_second,
            rel_tol=0.0,
            abs_tol=1e-15,
        ),
        observer_width=1,
        observer_width_fixed=True,
        unique_order_encoding_proven=False,
        field_effect_performed=False,
        runtime_candidate_released=False,
    )


def temporal_directed_moment_audit_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            TemporalMomentCollisionPaths,
            TemporalDirectedMomentAuditResult,
        )
        for item in fields(contract)
    )
