"""S1-HG audit of the frozen-E1 prediction against the fixed adapter."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_confirmation_chain_composition import (
    compose_synthetic_e1_confirmation_chain,
)
from .e1_frozen_transient_probe import (
    _advance_with_fixed_adapter,
    advance_fixed_e1_adapter_fast_shared_field_transient,
    advance_frozen_e1_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1HGFrozenFixedPredictionAuditError(ValueError):
    """Raised when the frozen/fixed equivalence evidence is weakened."""


S1_HG_AUDIT_ID = "e1.frozen-fixed-distinct-prediction-audit.s1hg.v1"
S1_HG_S1HF_RESULT_DIGEST = (
    "1e28219de2439e3cde5278aedb787cad1ffc2e3086b9890769ac875d7df01d91"
)
S1_HG_ACTIVATION_LINF = (
    ("r2", 3.145442008349597e-07),
    ("r4", 3.1155455250050923e-07),
    ("r8", 3.114299929989073e-07),
)
S1_HG_AFTERIMAGE_LINF = (
    ("r2", 2.1826650970727807e-07),
    ("r4", 2.1618997246477395e-07),
    ("r8", 2.1608402354413025e-07),
)
S1_HG_CHECK_NAMES = (
    "frozen-and-fixed-paths-call-same-field-integrator",
    "frozen-path-derives-adapter-deterministically-from-frozen-state",
    "frozen-path-returns-the-same-unmodified-state-object",
    "canonical-composition-requires-bit-exact-active-fixed-equality",
    "lauf-198-measured-convergent-nonzero-fixed-adapter-baseline",
)
S1_HG_DECISION = "STOPP_ACTIVE_FROZEN_E1_VS_FIXED_ADAPTER_NO_DISTINCT_PREDICTION"


def _called_names(function: object) -> frozenset[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(inspect.getsource(function))):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return frozenset(names)


@dataclass(frozen=True, slots=True)
class E1FormationS1HGFrozenFixedPredictionAudit:
    audit_id: str
    source_s1hf_result_digest: str
    activation_linf_ab_ba: tuple[tuple[str, float], ...]
    afterimage_linf_ab_ba: tuple[tuple[str, float], ...]
    shared_field_integrator_name: str
    checks: tuple[tuple[str, bool], ...]
    planned_full_chain_call_count: int
    planned_full_chain_field_step_count: int
    frozen_state_changes_during_probe: bool
    active_frozen_e1_has_distinct_prediction: bool
    full_matrix_execution_informative: bool
    fixed_adapter_baseline_real_and_nonzero: bool
    frozen_probe_branch_stopped: bool
    overall_project_stopped: bool
    new_substrate_direction_requires_owner_decision: bool
    additional_field_execution_performed: bool
    persistence_performed: bool
    claims_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if (
            self.audit_id != S1_HG_AUDIT_ID
            or self.source_s1hf_result_digest != S1_HG_S1HF_RESULT_DIGEST
            or self.activation_linf_ab_ba != S1_HG_ACTIVATION_LINF
            or self.afterimage_linf_ab_ba != S1_HG_AFTERIMAGE_LINF
            or self.shared_field_integrator_name != "_advance_with_fixed_adapter"
            or tuple(name for name, _ in self.checks) != S1_HG_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.planned_full_chain_call_count != 45
            or self.planned_full_chain_field_step_count != 28000
            or any(
                value is not False
                for value in (
                    self.frozen_state_changes_during_probe,
                    self.active_frozen_e1_has_distinct_prediction,
                    self.full_matrix_execution_informative,
                    self.overall_project_stopped,
                    self.additional_field_execution_performed,
                    self.persistence_performed,
                    self.claims_permitted,
                    self.memory_claim_permitted,
                )
            )
            or any(
                value is not True
                for value in (
                    self.fixed_adapter_baseline_real_and_nonzero,
                    self.frozen_probe_branch_stopped,
                    self.new_substrate_direction_requires_owner_decision,
                )
            )
            or self.decision != S1_HG_DECISION
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1FormationS1HGFrozenFixedPredictionAuditError(
                "S1-HG weakened the stopped frozen/fixed prediction boundary"
            )


def audit_e1_formation_s1hg_frozen_fixed_distinct_prediction(
) -> E1FormationS1HGFrozenFixedPredictionAudit:
    """Decide whether frozen E1 can differ from its exact fixed adapter."""

    frozen_source = inspect.getsource(advance_frozen_e1_fast_shared_field_transient)
    composition_source = inspect.getsource(compose_synthetic_e1_confirmation_chain)
    frozen_calls = _called_names(advance_frozen_e1_fast_shared_field_transient)
    fixed_calls = _called_names(
        advance_fixed_e1_adapter_fast_shared_field_transient
    )
    checks = (
        (
            S1_HG_CHECK_NAMES[0],
            "_advance_with_fixed_adapter" in frozen_calls
            and "_advance_with_fixed_adapter" in fixed_calls
            and callable(_advance_with_fixed_adapter),
        ),
        (
            S1_HG_CHECK_NAMES[1],
            "compute_e1_weighted_edge_rates" in frozen_calls,
        ),
        (
            S1_HG_CHECK_NAMES[2],
            "FrozenTransientE1ProbeResult(\n        next_field, frozen_e1_state, adapter\n    )"
            in frozen_source,
        ),
        (
            S1_HG_CHECK_NAMES[3],
            'metrics["fixed_adapter_residual"] == 0.0' in composition_source,
        ),
        (
            S1_HG_CHECK_NAMES[4],
            all(value > 1e-12 for _, value in S1_HG_ACTIVATION_LINF)
            and all(value > 1e-12 for _, value in S1_HG_AFTERIMAGE_LINF)
            and abs(S1_HG_ACTIVATION_LINF[2][1] - S1_HG_ACTIVATION_LINF[1][1])
            < abs(S1_HG_ACTIVATION_LINF[1][1] - S1_HG_ACTIVATION_LINF[0][1])
            and abs(S1_HG_AFTERIMAGE_LINF[2][1] - S1_HG_AFTERIMAGE_LINF[1][1])
            < abs(S1_HG_AFTERIMAGE_LINF[1][1] - S1_HG_AFTERIMAGE_LINF[0][1]),
        ),
    )
    if any(value is not True for _, value in checks):
        raise E1FormationS1HGFrozenFixedPredictionAuditError(
            "S1-HG source or Lauf-198 evidence does not support the audit"
        )
    values = {
        "audit_id": S1_HG_AUDIT_ID,
        "source_s1hf_result_digest": S1_HG_S1HF_RESULT_DIGEST,
        "activation_linf_ab_ba": S1_HG_ACTIVATION_LINF,
        "afterimage_linf_ab_ba": S1_HG_AFTERIMAGE_LINF,
        "shared_field_integrator_name": "_advance_with_fixed_adapter",
        "checks": checks,
        "planned_full_chain_call_count": 45,
        "planned_full_chain_field_step_count": 28000,
        "frozen_state_changes_during_probe": False,
        "active_frozen_e1_has_distinct_prediction": False,
        "full_matrix_execution_informative": False,
        "fixed_adapter_baseline_real_and_nonzero": True,
        "frozen_probe_branch_stopped": True,
        "overall_project_stopped": False,
        "new_substrate_direction_requires_owner_decision": True,
        "additional_field_execution_performed": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "memory_claim_permitted": False,
        "decision": S1_HG_DECISION,
        "reason": (
            "frozen-e1-derives-one-deterministic-adapter-from-an-unchanged-"
            "state-and-uses-the-identical-field-integrator-as-the-real-"
            "fixed-adapter-baseline;the-current-45-call-matrix-therefore-has-"
            "no-distinct-active-frozen-e1-prediction-and-must-not-be-run"
        ),
    }
    return E1FormationS1HGFrozenFixedPredictionAudit(
        **values,
        audit_digest=_digest(values),
    )
