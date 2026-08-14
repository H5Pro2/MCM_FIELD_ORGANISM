"""S1-FR static resource and causal-matrix audit for the fresh E1 chain."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_s1fb_discretization_scaling_audit import (
    S1_FB_REFINEMENT_BUDGETS,
)
from .e1_formation_s1fp_common_probe_contract import (
    E1FormationS1FPCommonProbeContract,
    S1_FP_PROBE_ROLES,
    S1_FP_REFINEMENTS,
)
from .e1_formation_s1fc_state_convergence_contract import (
    S1_FC_FORMATION_ROLES,
)
from .e1_formation_s1fq_synthetic_common_probe_coordinator import (
    E1FormationS1FQSyntheticCoordinatorResult,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FRStaticResourceMatrixAuditError(ValueError):
    """Raised when S1-FR changes scope, accounting, or causal coverage."""


S1_FR_AUDIT_ID = "e1.fresh-chain-static-resource-matrix-audit.s1fr.v1"
S1_FR_CONTRAST_OPERANDS = (
    ("p0-reset-order", ("p0-reset-ab", "p0-reset-ba")),
    ("e1-active-order", ("e1-active-ab", "e1-active-ba")),
    (
        "e1-probe-feedback-ablated-order",
        (
            "e1-probe-feedback-ablated-ab",
            "e1-probe-feedback-ablated-ba",
        ),
    ),
    (
        "e1-formation-ablated-order",
        ("e1-formation-ablated-ab", "e1-formation-ablated-ba"),
    ),
    (
        "active-ab-vs-fixed-adapter-ab",
        ("e1-active-ab", "fixed-adapter-ab"),
    ),
    (
        "active-ba-vs-fixed-adapter-ba",
        ("e1-active-ba", "fixed-adapter-ba"),
    ),
)
S1_FR_REFINEMENT_ROLES = (
    ("r2", "coarse-r2-to-r4-residual"),
    ("r4", "coarse-and-fine-bridge"),
    ("r8", "fine-residual-and-active-signal-endpoint"),
)
S1_FR_EXPECTED_BUDGETS = (
    ("r2", 2, 400, 5, 2_000, 200, 10, 2_000, 4_000),
    ("r4", 4, 800, 5, 4_000, 400, 10, 4_000, 8_000),
    ("r8", 8, 1_600, 5, 8_000, 800, 10, 8_000, 16_000),
)


def _called_names(source: str) -> frozenset[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return frozenset(names)


@dataclass(frozen=True, slots=True)
class E1FormationS1FRStaticResourceMatrixAudit:
    audit_id: str
    source_contract_digest: str
    source_integration_digest: str
    formation_roles: tuple[str, ...]
    probe_roles: tuple[str, ...]
    contrast_operands: tuple[tuple[str, tuple[str, ...]], ...]
    refinement_roles: tuple[tuple[str, str], ...]
    budgets: tuple[tuple[str, int, int, int, int, int, int, int, int], ...]
    formation_call_count: int
    probe_call_count: int
    total_field_call_count: int
    formation_field_steps: int
    probe_field_steps: int
    total_field_steps: int
    field_node_count: int
    state_edge_count: int
    conservative_node_step_units: int
    conservative_edge_step_units: int
    retained_formation_state_count: int
    retained_binding_count: int
    minimum_free_memory_bytes: int
    exact_peak_ram_estimate_available: bool
    minimum_causally_complete_probe_role_count: int
    minimum_causally_complete_probe_slot_count: int
    removable_probe_roles: tuple[str, ...]
    removable_refinements: tuple[str, ...]
    causally_equivalent_matrix_reduction_available: bool
    owner_authorization_present: bool
    execution_permitted: bool
    field_execution_performed: bool
    persistence_performed: bool
    claims_permitted: bool
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
            self.audit_id != S1_FR_AUDIT_ID
            or self.formation_roles != S1_FC_FORMATION_ROLES
            or self.probe_roles != S1_FP_PROBE_ROLES
            or self.contrast_operands != S1_FR_CONTRAST_OPERANDS
            or self.refinement_roles != S1_FR_REFINEMENT_ROLES
            or self.budgets != S1_FR_EXPECTED_BUDGETS
            or (
                self.formation_call_count,
                self.probe_call_count,
                self.total_field_call_count,
            )
            != (15, 30, 45)
            or (
                self.formation_field_steps,
                self.probe_field_steps,
                self.total_field_steps,
            )
            != (14_000, 14_000, 28_000)
            or (self.field_node_count, self.state_edge_count) != (84, 145)
            or self.conservative_node_step_units != 2_352_000
            or self.conservative_edge_step_units != 4_060_000
            or self.retained_formation_state_count != 15
            or self.retained_binding_count != 2_175
            or self.minimum_free_memory_bytes != 4 * 1024**3
            or self.exact_peak_ram_estimate_available is not False
            or (
                self.minimum_causally_complete_probe_role_count,
                self.minimum_causally_complete_probe_slot_count,
            )
            != (10, 30)
            or self.removable_probe_roles != ()
            or self.removable_refinements != ()
            or self.causally_equivalent_matrix_reduction_available is not False
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision != "FULL_45_ARM_MATRIX_REQUIRED_STATIC_BUDGET_BOUND"
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1FormationS1FRStaticResourceMatrixAuditError(
                "S1-FR resource or causal-matrix audit changed"
            )


def audit_e1_formation_s1fr_static_resources_and_matrix(
    contract: E1FormationS1FPCommonProbeContract,
    integration: E1FormationS1FQSyntheticCoordinatorResult,
) -> E1FormationS1FRStaticResourceMatrixAudit:
    """Derive the complete fresh-chain budget without running a field."""

    if not isinstance(contract, E1FormationS1FPCommonProbeContract) or not isinstance(
        integration, E1FormationS1FQSyntheticCoordinatorResult
    ):
        raise E1FormationS1FRStaticResourceMatrixAuditError(
            "S1-FR requires typed S1-FP and S1-FQ inputs"
        )
    contract.__post_init__()
    integration.__post_init__()
    if (
        integration.source_contract_digest != contract.contract_digest
        or integration.formation_result_count != 15
        or integration.probe_sample_count != 30
        or integration.field_steps_executed != 0
    ):
        raise E1FormationS1FRStaticResourceMatrixAuditError(
            "S1-FR source integration differs from the bound zero-step chain"
        )

    formation_steps = {"r2": 400, "r4": 800, "r8": 1_600}
    probe_steps = {
        refinement: probe
        for refinement, _, _, probe in S1_FB_REFINEMENT_BUDGETS
    }
    budgets = tuple(
        (
            refinement,
            factor,
            formation_steps[refinement],
            len(S1_FC_FORMATION_ROLES),
            formation_steps[refinement] * len(S1_FC_FORMATION_ROLES),
            probe_steps[refinement],
            len(S1_FP_PROBE_ROLES),
            probe_steps[refinement] * len(S1_FP_PROBE_ROLES),
            formation_steps[refinement] * len(S1_FC_FORMATION_ROLES)
            + probe_steps[refinement] * len(S1_FP_PROBE_ROLES),
        )
        for refinement, factor in zip(S1_FP_REFINEMENTS, (2, 4, 8), strict=True)
    )
    contrast_roles = {
        role for _, operands in S1_FR_CONTRAST_OPERANDS for role in operands
    }
    removable_probe_roles = tuple(
        role for role in S1_FP_PROBE_ROLES if role not in contrast_roles
    )
    refinement_roles = dict(S1_FR_REFINEMENT_ROLES)
    removable_refinements = tuple(
        refinement
        for refinement in S1_FP_REFINEMENTS
        if refinement not in refinement_roles
    )
    if budgets != S1_FR_EXPECTED_BUDGETS:
        raise E1FormationS1FRStaticResourceMatrixAuditError(
            "S1-FR plan-derived budget changed"
        )

    forbidden_calls = {
        "run_e1_formation_s1fl_once",
        "run_small_five_arm_formation_in_memory",
        "advance_neutral_fast_shared_field_transient",
        "advance_frozen_e1_fast_shared_field_transient",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "open",
        "write_text",
        "write_bytes",
    }
    if not _called_names(
        inspect.getsource(audit_e1_formation_s1fr_static_resources_and_matrix)
    ).isdisjoint(forbidden_calls):
        raise E1FormationS1FRStaticResourceMatrixAuditError(
            "S1-FR called an execution or writer path"
        )

    total_steps = sum(item[8] for item in budgets)
    values = {
        "audit_id": S1_FR_AUDIT_ID,
        "source_contract_digest": contract.contract_digest,
        "source_integration_digest": integration.result_digest,
        "formation_roles": S1_FC_FORMATION_ROLES,
        "probe_roles": S1_FP_PROBE_ROLES,
        "contrast_operands": S1_FR_CONTRAST_OPERANDS,
        "refinement_roles": S1_FR_REFINEMENT_ROLES,
        "budgets": budgets,
        "formation_call_count": 15,
        "probe_call_count": 30,
        "total_field_call_count": 45,
        "formation_field_steps": sum(item[4] for item in budgets),
        "probe_field_steps": sum(item[7] for item in budgets),
        "total_field_steps": total_steps,
        "field_node_count": 84,
        "state_edge_count": 145,
        "conservative_node_step_units": total_steps * 84,
        "conservative_edge_step_units": total_steps * 145,
        "retained_formation_state_count": 15,
        "retained_binding_count": 15 * 145,
        "minimum_free_memory_bytes": 4 * 1024**3,
        "exact_peak_ram_estimate_available": False,
        "minimum_causally_complete_probe_role_count": len(contrast_roles),
        "minimum_causally_complete_probe_slot_count": (
            len(contrast_roles) * len(S1_FP_REFINEMENTS)
        ),
        "removable_probe_roles": removable_probe_roles,
        "removable_refinements": removable_refinements,
        "causally_equivalent_matrix_reduction_available": False,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": "FULL_45_ARM_MATRIX_REQUIRED_STATIC_BUDGET_BOUND",
        "reason": (
            "all-ten-probe-roles-feed-required-contrasts;all-three-refinements-"
            "feed-coarse-and-fine-ec46-residuals;full-chain-is-45-calls-and-"
            "28000-steps;no-execution-or-authorization-opened"
        ),
    }
    return E1FormationS1FRStaticResourceMatrixAudit(
        **values,
        audit_digest=_digest(values),
    )
