"""S1-FD synthetic evaluator for E1 formation-state convergence."""

from __future__ import annotations

from dataclasses import dataclass, field
import math

from .e1_formation_s1fc_state_convergence_contract import (
    E1FormationS1FCStateConvergenceContract,
    S1_FC_FORMATION_ROLES,
    audit_e1_formation_s1fc_state_convergence_contract,
)
from .e1_refined_confirmation_contract import S1_EB_REFINEMENTS
from .e1_refined_formation_runner import _digest


class E1FormationS1FDStateConvergenceEvaluatorError(ValueError):
    """Raised when an S1-FD synthetic state inventory is invalid."""


S1_FD_EVALUATOR_ID = "e1.formation-state-convergence-evaluator.s1fd.v1"
S1_FD_COMPONENTS = ("active-ab", "active-ba", "active-order")


def _finite_tuple(values: tuple[float, ...], role: str) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if not result or any(not math.isfinite(value) for value in result):
        raise E1FormationS1FDStateConvergenceEvaluatorError(
            f"S1-FD {role} must be a nonempty finite vector"
        )
    return result


def _linf(values: tuple[float, ...]) -> float:
    return max(abs(value) for value in values)


def _subtract(
    left: tuple[float, ...], right: tuple[float, ...]
) -> tuple[float, ...]:
    return tuple(a - b for a, b in zip(left, right, strict=True))


@dataclass(frozen=True, slots=True)
class E1FormationS1FDSyntheticStateVector:
    refinement_id: str
    formation_role: str
    edge_inventory_digest: str
    ordered_edge_ids: tuple[str, ...]
    ordered_binding_vector: tuple[float, ...] = field(repr=False)
    state_digest: str
    source_formation_result_digest: str
    resource_budget_error: float

    def __post_init__(self) -> None:
        edge_ids = tuple(self.ordered_edge_ids)
        values = _finite_tuple(self.ordered_binding_vector, "binding")
        resource_error = float(self.resource_budget_error)
        valid_refinements = tuple(name for name, _ in S1_EB_REFINEMENTS)
        state_payload = {
            "refinement_id": self.refinement_id,
            "formation_role": self.formation_role,
            "edge_inventory_digest": self.edge_inventory_digest,
            "ordered_edge_ids": edge_ids,
            "ordered_binding_vector": values,
            "source_formation_result_digest": self.source_formation_result_digest,
            "resource_budget_error": resource_error,
        }
        if (
            self.refinement_id not in valid_refinements
            or self.formation_role not in S1_FC_FORMATION_ROLES
            or not edge_ids
            or len(set(edge_ids)) != len(edge_ids)
            or len(values) != len(edge_ids)
            or self.edge_inventory_digest != _digest(edge_ids)
            or not self.source_formation_result_digest
            or not math.isfinite(resource_error)
            or resource_error < 0.0
            or self.state_digest != _digest(state_payload)
        ):
            raise E1FormationS1FDStateConvergenceEvaluatorError(
                "S1-FD synthetic state vector differs from its bound payload"
            )
        object.__setattr__(self, "ordered_edge_ids", edge_ids)
        object.__setattr__(self, "ordered_binding_vector", values)
        object.__setattr__(self, "resource_budget_error", resource_error)


def build_e1_formation_s1fd_synthetic_state_vector(
    *,
    refinement_id: str,
    formation_role: str,
    ordered_edge_ids: tuple[str, ...],
    ordered_binding_vector: tuple[float, ...],
    resource_budget_error: float = 0.0,
) -> E1FormationS1FDSyntheticStateVector:
    """Build one digest-bound synthetic vector without running formation."""

    edge_ids = tuple(ordered_edge_ids)
    values = _finite_tuple(tuple(ordered_binding_vector), "binding")
    source_digest = _digest(
        {
            "source": "s1fd-synthetic-fixture",
            "refinement_id": refinement_id,
            "formation_role": formation_role,
        }
    )
    state_payload = {
        "refinement_id": refinement_id,
        "formation_role": formation_role,
        "edge_inventory_digest": _digest(edge_ids),
        "ordered_edge_ids": edge_ids,
        "ordered_binding_vector": values,
        "source_formation_result_digest": source_digest,
        "resource_budget_error": float(resource_budget_error),
    }
    return E1FormationS1FDSyntheticStateVector(
        **state_payload,
        state_digest=_digest(state_payload),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1FDConvergenceComponent:
    component: str
    coarse_linf: float
    fine_linf: float
    r8_linf: float
    fine_relative_to_r8: float
    converged: bool
    component_digest: str

    def __post_init__(self) -> None:
        values = (
            self.coarse_linf,
            self.fine_linf,
            self.r8_linf,
            self.fine_relative_to_r8,
        )
        expected = (
            self.fine_linf <= self.coarse_linf
            and self.fine_relative_to_r8 <= 0.01
        )
        payload = {
            "component": self.component,
            "coarse_linf": self.coarse_linf,
            "fine_linf": self.fine_linf,
            "r8_linf": self.r8_linf,
            "fine_relative_to_r8": self.fine_relative_to_r8,
            "converged": expected,
        }
        if (
            self.component not in S1_FD_COMPONENTS
            or any(not math.isfinite(value) or value < 0.0 for value in values)
            or self.converged is not expected
            or self.component_digest != _digest(payload)
        ):
            raise E1FormationS1FDStateConvergenceEvaluatorError(
                "S1-FD convergence component differs"
            )


@dataclass(frozen=True, slots=True)
class E1FormationS1FDStateConvergenceResult:
    evaluator_id: str
    contract_digest: str
    state_digests: tuple[str, ...]
    components: tuple[E1FormationS1FDConvergenceComponent, ...]
    maximum_identity_error: float
    maximum_ablation_linf: float
    maximum_resource_budget_error: float
    r8_order_linf: float
    controls_valid: bool
    order_state_distinguishable: bool
    all_components_converged: bool
    decision: str
    field_execution_performed: bool
    real_state_capture_performed: bool
    persistence_performed: bool
    memory_claim_allowed: bool
    result_digest: str

    def __post_init__(self) -> None:
        components = tuple(self.components)
        controls_valid = max(
            self.maximum_identity_error,
            self.maximum_ablation_linf,
            self.maximum_resource_budget_error,
        ) <= 1e-12
        distinguishable = self.r8_order_linf > 1e-12
        converged = all(component.converged for component in components)
        if not controls_valid:
            decision = "INVALID_FORMATION_STATE_CONTROLS"
        elif not distinguishable:
            decision = "NO_DISTINGUISHABLE_FORMATION_ORDER_STATE"
        elif not converged:
            decision = "FORMATION_STATE_NOT_CONVERGED"
        else:
            decision = "FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY"
        payload = {
            "evaluator_id": self.evaluator_id,
            "contract_digest": self.contract_digest,
            "state_digests": self.state_digests,
            "component_digests": tuple(item.component_digest for item in components),
            "maximum_identity_error": self.maximum_identity_error,
            "maximum_ablation_linf": self.maximum_ablation_linf,
            "maximum_resource_budget_error": self.maximum_resource_budget_error,
            "r8_order_linf": self.r8_order_linf,
            "controls_valid": controls_valid,
            "order_state_distinguishable": distinguishable,
            "all_components_converged": converged,
            "decision": decision,
            "field_execution_performed": False,
            "real_state_capture_performed": False,
            "persistence_performed": False,
            "memory_claim_allowed": False,
        }
        if (
            self.evaluator_id != S1_FD_EVALUATOR_ID
            or len(self.state_digests) != 15
            or tuple(item.component for item in components) != S1_FD_COMPONENTS
            or self.controls_valid is not controls_valid
            or self.order_state_distinguishable is not distinguishable
            or self.all_components_converged is not converged
            or self.decision != decision
            or any(
                value is not False
                for value in (
                    self.field_execution_performed,
                    self.real_state_capture_performed,
                    self.persistence_performed,
                    self.memory_claim_allowed,
                )
            )
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1FDStateConvergenceEvaluatorError(
                "S1-FD result binding differs"
            )
        object.__setattr__(self, "components", components)


def evaluate_e1_formation_s1fd_state_convergence(
    states: tuple[E1FormationS1FDSyntheticStateVector, ...],
    contract: E1FormationS1FCStateConvergenceContract | None = None,
) -> E1FormationS1FDStateConvergenceResult:
    """Evaluate exactly 15 supplied vectors without producing field state."""

    source = contract or audit_e1_formation_s1fc_state_convergence_contract()
    if not isinstance(source, E1FormationS1FCStateConvergenceContract):
        raise E1FormationS1FDStateConvergenceEvaluatorError(
            "S1-FD requires the typed S1-FC contract"
        )
    source.__post_init__()
    states = tuple(states)
    expected = tuple(
        (refinement_id, role)
        for refinement_id, _ in source.refinements
        for role in source.formation_roles
    )
    if (
        len(states) != source.required_state_vector_count
        or not all(isinstance(item, E1FormationS1FDSyntheticStateVector) for item in states)
        or tuple((item.refinement_id, item.formation_role) for item in states)
        != expected
    ):
        raise E1FormationS1FDStateConvergenceEvaluatorError(
            "S1-FD requires the canonical atomic 15-vector inventory"
        )
    for item in states:
        item.__post_init__()
    edge_order = states[0].ordered_edge_ids
    if any(item.ordered_edge_ids != edge_order for item in states[1:]):
        raise E1FormationS1FDStateConvergenceEvaluatorError(
            "S1-FD edge order differs across states"
        )

    by_key = {
        (item.refinement_id, item.formation_role): item
        for item in states
    }
    active_ab = {
        refinement: by_key[(refinement, "active-ab")].ordered_binding_vector
        for refinement, _ in source.refinements
    }
    active_ba = {
        refinement: by_key[(refinement, "active-ba")].ordered_binding_vector
        for refinement, _ in source.refinements
    }
    active_order = {
        refinement: _subtract(active_ab[refinement], active_ba[refinement])
        for refinement, _ in source.refinements
    }

    components = []
    for name, vectors in (
        ("active-ab", active_ab),
        ("active-ba", active_ba),
        ("active-order", active_order),
    ):
        coarse = _linf(_subtract(vectors["r2"], vectors["r4"]))
        fine = _linf(_subtract(vectors["r4"], vectors["r8"]))
        r8_linf = _linf(vectors["r8"])
        relative = fine / max(r8_linf, source.absolute_control_tolerance)
        converged = fine <= coarse and relative <= source.relative_refinement_limit
        payload = {
            "component": name,
            "coarse_linf": coarse,
            "fine_linf": fine,
            "r8_linf": r8_linf,
            "fine_relative_to_r8": relative,
            "converged": converged,
        }
        components.append(
            E1FormationS1FDConvergenceComponent(
                name, coarse, fine, r8_linf, relative, converged, _digest(payload)
            )
        )

    identity_error = max(
        _linf(
            _subtract(
                by_key[(refinement, "identity-ab")].ordered_binding_vector,
                active_ab[refinement],
            )
        )
        for refinement, _ in source.refinements
    )
    ablation_linf = max(
        _linf(by_key[(refinement, role)].ordered_binding_vector)
        for refinement, _ in source.refinements
        for role in ("formation-ablated-ab", "formation-ablated-ba")
    )
    resource_error = max(item.resource_budget_error for item in states)
    r8_order_linf = _linf(active_order["r8"])
    controls_valid = max(identity_error, ablation_linf, resource_error) <= 1e-12
    distinguishable = r8_order_linf > 1e-12
    all_converged = all(item.converged for item in components)
    if not controls_valid:
        decision = "INVALID_FORMATION_STATE_CONTROLS"
    elif not distinguishable:
        decision = "NO_DISTINGUISHABLE_FORMATION_ORDER_STATE"
    elif not all_converged:
        decision = "FORMATION_STATE_NOT_CONVERGED"
    else:
        decision = "FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY"
    component_tuple = tuple(components)
    values = {
        "evaluator_id": S1_FD_EVALUATOR_ID,
        "contract_digest": source.contract_digest,
        "state_digests": tuple(item.state_digest for item in states),
        "components": component_tuple,
        "maximum_identity_error": identity_error,
        "maximum_ablation_linf": ablation_linf,
        "maximum_resource_budget_error": resource_error,
        "r8_order_linf": r8_order_linf,
        "controls_valid": controls_valid,
        "order_state_distinguishable": distinguishable,
        "all_components_converged": all_converged,
        "decision": decision,
        "field_execution_performed": False,
        "real_state_capture_performed": False,
        "persistence_performed": False,
        "memory_claim_allowed": False,
    }
    digest_payload = dict(values)
    digest_payload["component_digests"] = tuple(
        item.component_digest for item in component_tuple
    )
    del digest_payload["components"]
    return E1FormationS1FDStateConvergenceResult(
        **values,
        result_digest=_digest(digest_payload),
    )
