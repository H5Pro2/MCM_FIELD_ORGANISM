"""S1-FA rigorous EC46 decision bounds from retained refinement norms."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

from .e1_common_probe_acceptance_contract import S1_EC46_DECISIONS
from .e1_common_probe_ec87_r2_ec46_complement_contract import S1_EC87_R2_SCALARS
from .e1_common_probe_ec97_ec46_data_sufficiency_audit import (
    S1_EC97_AUDIT_ID,
    S1_EC97_R4_R8_ACTIVE_SCALARS,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeS1FANormIntervalDecisionError(ValueError):
    """Raised when S1-FA exceeds rigorous norm bounds or opens execution."""


S1_FA_AUDIT_ID = "e1.common-probe-norm-interval-decision.s1fa.v1"
S1_FA_RELATIVE_REFINEMENT_LIMIT = 0.01
S1_FA_ABSOLUTE_CONTROL_TOLERANCE = 1e-12


def _serializable_decision_payload(
    values: dict[str, object],
) -> dict[str, object]:
    payload = dict(values)
    payload["components"] = tuple(
        asdict(component) for component in payload["components"]  # type: ignore[union-attr]
    )
    return payload


@dataclass(frozen=True, slots=True)
class E1CommonProbeS1FAComponentBounds:
    component: str
    r2_norm: float
    r4_norm: float
    r8_norm: float
    coarse_distance_lower_bound: float
    coarse_distance_upper_bound: float
    fine_distance_lower_bound: float
    fine_distance_upper_bound: float
    fine_relative_lower_bound: float
    relative_refinement_limit: float
    relative_convergence_possible: bool

    def __post_init__(self) -> None:
        values = (self.r2_norm, self.r4_norm, self.r8_norm)
        if (
            self.component not in {"activation", "afterimage"}
            or any(not math.isfinite(value) or value < 0.0 for value in values)
            or self.coarse_distance_lower_bound != abs(self.r2_norm - self.r4_norm)
            or self.coarse_distance_upper_bound != self.r2_norm + self.r4_norm
            or self.fine_distance_lower_bound != abs(self.r4_norm - self.r8_norm)
            or self.fine_distance_upper_bound != self.r4_norm + self.r8_norm
            or self.r8_norm <= 0.0
            or self.fine_relative_lower_bound
            != self.fine_distance_lower_bound / self.r8_norm
            or self.relative_refinement_limit != S1_FA_RELATIVE_REFINEMENT_LIMIT
            or self.relative_convergence_possible
            is not (
                self.fine_relative_lower_bound
                <= self.relative_refinement_limit
            )
        ):
            raise E1CommonProbeS1FANormIntervalDecisionError(
                "S1-FA component bounds changed or exceeded norm inequalities"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeS1FANormIntervalDecision:
    audit_id: str
    source_ec97_audit_id: str
    components: tuple[E1CommonProbeS1FAComponentBounds, ...]
    norm_distance_rule: str
    exact_vectors_available: bool
    exact_coarse_distances_computable: bool
    exact_fine_distances_computable: bool
    posthoc_vector_reconstruction_permitted: bool
    all_controls_known_within_tolerance: bool
    both_r8_signals_above_tolerance: bool
    relative_convergence_possible: bool
    numerically_clear_decision_possible: bool
    ec46_decision_identifiable_from_bounds: bool
    ec46_decision: str
    field_execution_permitted: bool
    rerun_permitted: bool
    persistence_performed: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = _serializable_decision_payload({
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        })
        if (
            self.audit_id != S1_FA_AUDIT_ID
            or self.source_ec97_audit_id != S1_EC97_AUDIT_ID
            or tuple(item.component for item in self.components)
            != ("activation", "afterimage")
            or self.norm_distance_rule != "abs(norm(v)-norm(w))<=norm(v-w)<=norm(v)+norm(w)"
            or any(
                value is not False
                for value in (
                    self.exact_vectors_available,
                    self.exact_coarse_distances_computable,
                    self.exact_fine_distances_computable,
                    self.posthoc_vector_reconstruction_permitted,
                    self.relative_convergence_possible,
                    self.numerically_clear_decision_possible,
                    self.field_execution_permitted,
                    self.rerun_permitted,
                    self.persistence_performed,
                    self.memory_claim_permitted,
                )
            )
            or any(
                value is not True
                for value in (
                    self.all_controls_known_within_tolerance,
                    self.both_r8_signals_above_tolerance,
                    self.ec46_decision_identifiable_from_bounds,
                )
            )
            or self.ec46_decision
            != "NUMERICALLY_UNDECIDABLE_COMMON_PROBE_DIFFERENCE"
            or self.ec46_decision not in S1_EC46_DECISIONS
            or self.decision != "EC46_CLEAR_OUTCOME_EXCLUDED_BY_RIGOROUS_NORM_BOUNDS"
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1CommonProbeS1FANormIntervalDecisionError(
                "S1-FA decision changed, invented vectors, or opened execution"
            )
        for component in self.components:
            component.__post_init__()
        if any(component.relative_convergence_possible for component in self.components):
            raise E1CommonProbeS1FANormIntervalDecisionError(
                "S1-FA requires both lower bounds above the EC46 limit"
            )


def _component_bounds(
    component: str,
    r2_norm: float,
    r4_norm: float,
    r8_norm: float,
) -> E1CommonProbeS1FAComponentBounds:
    coarse_lower = abs(r2_norm - r4_norm)
    fine_lower = abs(r4_norm - r8_norm)
    relative_lower = fine_lower / r8_norm
    return E1CommonProbeS1FAComponentBounds(
        component=component,
        r2_norm=r2_norm,
        r4_norm=r4_norm,
        r8_norm=r8_norm,
        coarse_distance_lower_bound=coarse_lower,
        coarse_distance_upper_bound=r2_norm + r4_norm,
        fine_distance_lower_bound=fine_lower,
        fine_distance_upper_bound=r4_norm + r8_norm,
        fine_relative_lower_bound=relative_lower,
        relative_refinement_limit=S1_FA_RELATIVE_REFINEMENT_LIMIT,
        relative_convergence_possible=(
            relative_lower <= S1_FA_RELATIVE_REFINEMENT_LIMIT
        ),
    )


def audit_e1_common_probe_s1fa_norm_interval_decision(
) -> E1CommonProbeS1FANormIntervalDecision:
    """Resolve only the EC46 decision class without reconstructing vectors."""

    r2_active = next(
        item for item in S1_EC87_R2_SCALARS if item[0] == "e1-active-order"
    )
    r4 = next(item for item in S1_EC97_R4_R8_ACTIVE_SCALARS if item[0] == "r4")
    r8 = next(item for item in S1_EC97_R4_R8_ACTIVE_SCALARS if item[0] == "r8")
    components = (
        _component_bounds("activation", r2_active[1], r4[1], r8[1]),
        _component_bounds("afterimage", r2_active[2], r4[2], r8[2]),
    )
    values = {
        "audit_id": S1_FA_AUDIT_ID,
        "source_ec97_audit_id": S1_EC97_AUDIT_ID,
        "components": components,
        "norm_distance_rule": (
            "abs(norm(v)-norm(w))<=norm(v-w)<=norm(v)+norm(w)"
        ),
        "exact_vectors_available": False,
        "exact_coarse_distances_computable": False,
        "exact_fine_distances_computable": False,
        "posthoc_vector_reconstruction_permitted": False,
        "all_controls_known_within_tolerance": True,
        "both_r8_signals_above_tolerance": all(
            item.r8_norm > S1_FA_ABSOLUTE_CONTROL_TOLERANCE
            for item in components
        ),
        "relative_convergence_possible": False,
        "numerically_clear_decision_possible": False,
        "ec46_decision_identifiable_from_bounds": True,
        "ec46_decision": "NUMERICALLY_UNDECIDABLE_COMMON_PROBE_DIFFERENCE",
        "field_execution_permitted": False,
        "rerun_permitted": False,
        "persistence_performed": False,
        "memory_claim_permitted": False,
        "decision": "EC46_CLEAR_OUTCOME_EXCLUDED_BY_RIGOROUS_NORM_BOUNDS",
        "reason": (
            "reverse-triangle-lower-bounds-for-r4-r8-exceed-one-percent-of-r8-"
            "for-activation-and-afterimage;exact-vectors-remain-unavailable"
        ),
    }
    return E1CommonProbeS1FANormIntervalDecision(
        **values,
        audit_digest=_digest(_serializable_decision_payload(values)),
    )
