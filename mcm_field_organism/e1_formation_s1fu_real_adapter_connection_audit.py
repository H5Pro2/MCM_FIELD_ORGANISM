"""S1-FU static audit of reusable adapters and missing fresh-chain wiring."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_acceptance_contract import decide_common_probe_evidence
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_real_wrappers import (
    build_e1_common_probe_fresh_field,
    run_e1_common_probe_real_probe_wrapper,
)
from .e1_confirmation_small_five_arm_formation import (
    run_small_five_arm_formation_in_memory,
)
from .e1_formation_s1fd_state_convergence_evaluator import (
    evaluate_e1_formation_s1fd_state_convergence,
)
from .e1_formation_s1ff_in_memory_capture_adapter import (
    capture_e1_formation_s1ff_in_memory,
)
from .e1_formation_s1fi_fresh_capture_preflight import (
    prepare_e1_formation_s1fi_inputs,
    read_e1_formation_s1fi_resource_snapshot,
)
from .e1_formation_s1fl_real_coordinator import E1FormationS1FLCoordinatorResult
from .e1_formation_s1fp_common_probe_contract import S1_FP_PROBE_ROLES
from .e1_formation_s1fs_fresh_chain_one_shot_contract import (
    E1FormationS1FSFreshChainOneShotContract,
)
from .e1_formation_s1ft_synthetic_fresh_chain_preflight import (
    E1FormationS1FTSyntheticFreshChainPreflight,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FURealAdapterConnectionAuditError(ValueError):
    """Raised when S1-FU overstates reuse or opens execution."""


S1_FU_AUDIT_ID = "e1.fresh-chain-real-adapter-connection-audit.s1fu.v1"
S1_FU_UNCHANGED_REUSABLE = (
    ("prepare_e1_formation_s1fi_inputs", "typed-fresh-formation-inputs"),
    ("read_e1_formation_s1fi_resource_snapshot", "real-windows-memory-snapshot"),
    ("run_small_five_arm_formation_in_memory", "r2-r4-r8-five-arm-formation"),
    ("capture_e1_formation_s1ff_in_memory", "fifteen-live-result-capture"),
    ("evaluate_e1_formation_s1fd_state_convergence", "formation-control-evaluation"),
    ("decide_common_probe_evidence", "post-return-ec46-decision"),
)
S1_FU_ADAPTABLE = (
    (
        "build_e1_common_probe_fresh_field",
        "field-copy-logic-reusable-new-ten-role-binding-required",
    ),
    (
        "run_e1_common_probe_real_probe_wrapper",
        "eight-role-kernel-routing-reusable-new-slot-type-required",
    ),
    (
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "kernel-reusable-real-fixed-adapter-wrapper-missing",
    ),
)
S1_FU_MISSING = (
    "s1fp-ten-role-real-slot-binding-without-old-contact-axis",
    "typed-live-e1-state-handoff-from-formation-to-probe",
    "real-fixed-adapter-probe-wrapper-and-receipt",
    "45-call-step-runtime-and-fail-closed-coordinator",
    "atomic-raw-vector-result-compositor-before-ec46-evaluation",
)
S1_FU_CHECK_NAMES = (
    "s1fs-and-positive-s1ft-bound-but-closed",
    "fresh-input-preparer-signature-compatible",
    "real-resource-reader-signature-compatible",
    "five-arm-formation-signature-compatible",
    "capture-and-formation-evaluator-signatures-compatible",
    "old-probe-role-gap-is-exactly-two-fixed-adapter-roles",
    "fresh-field-and-eight-role-probe-wrapper-signatures-compatible",
    "fixed-adapter-kernel-present-but-not-routed-by-real-wrapper",
    "s1fl-result-does-not-export-live-formation-states",
    "ec46-decision-signature-compatible",
    "audit-does-not-call-production-path",
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
class E1FormationS1FURealAdapterConnectionAudit:
    audit_id: str
    source_s1fs_contract_digest: str
    source_s1ft_preflight_digest: str
    unchanged_reusable_components: tuple[tuple[str, str], ...]
    adaptable_components: tuple[tuple[str, str], ...]
    missing_components: tuple[str, ...]
    old_probe_roles: tuple[str, ...]
    required_probe_roles: tuple[str, ...]
    missing_probe_roles: tuple[str, ...]
    s1fl_result_fields: tuple[str, ...]
    live_state_export_present: bool
    unchanged_reusable_count: int
    adaptable_count: int
    missing_count: int
    checks: tuple[tuple[str, bool], ...]
    static_audit_passed: bool
    new_field_mechanic_required: bool
    new_live_state_handoff_required: bool
    new_ten_role_slot_binding_required: bool
    new_fixed_adapter_wrapper_required: bool
    new_atomic_coordinator_required: bool
    real_runner_implementation_permitted: bool
    owner_authorization_present: bool
    execution_permitted: bool
    field_execution_performed: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        passed = all(value for _, value in self.checks)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if (
            self.audit_id != S1_FU_AUDIT_ID
            or self.unchanged_reusable_components != S1_FU_UNCHANGED_REUSABLE
            or self.adaptable_components != S1_FU_ADAPTABLE
            or self.missing_components != S1_FU_MISSING
            or self.old_probe_roles != S1_EC45_PROBE_ROLES
            or self.required_probe_roles != S1_FP_PROBE_ROLES
            or self.missing_probe_roles != ("fixed-adapter-ab", "fixed-adapter-ba")
            or self.live_state_export_present is not False
            or (self.unchanged_reusable_count, self.adaptable_count, self.missing_count)
            != (6, 3, 5)
            or tuple(name for name, _ in self.checks) != S1_FU_CHECK_NAMES
            or self.static_audit_passed is not passed
            or self.new_field_mechanic_required is not False
            or any(
                value is not True
                for value in (
                    self.new_live_state_handoff_required,
                    self.new_ten_role_slot_binding_required,
                    self.new_fixed_adapter_wrapper_required,
                    self.new_atomic_coordinator_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.real_runner_implementation_permitted,
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "EXISTING_KERNELS_REUSABLE_LIVE_STATE_HANDOFF_AND_TEN_ROLE_COORDINATION_MISSING"
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1FormationS1FURealAdapterConnectionAuditError(
                "S1-FU adapter connection audit changed or opened execution"
            )


def audit_e1_formation_s1fu_real_adapter_connections(
    contract: E1FormationS1FSFreshChainOneShotContract,
    preflight: E1FormationS1FTSyntheticFreshChainPreflight,
) -> E1FormationS1FURealAdapterConnectionAudit:
    """Inspect existing interfaces without invoking any field or resource path."""

    if not isinstance(contract, E1FormationS1FSFreshChainOneShotContract) or not isinstance(
        preflight, E1FormationS1FTSyntheticFreshChainPreflight
    ):
        raise E1FormationS1FURealAdapterConnectionAuditError(
            "S1-FU requires typed S1-FS and S1-FT inputs"
        )
    contract.__post_init__()
    preflight.__post_init__()
    result_fields = tuple(E1FormationS1FLCoordinatorResult.__dataclass_fields__)
    live_field_names = {"arm_results", "live_states", "formed_states", "e1_states"}
    missing_roles = tuple(
        role for role in S1_FP_PROBE_ROLES if role not in S1_EC45_PROBE_ROLES
    )
    probe_source = inspect.getsource(run_e1_common_probe_real_probe_wrapper)
    audit_source = inspect.getsource(
        audit_e1_formation_s1fu_real_adapter_connections
    )
    production_calls = {
        "prepare_e1_formation_s1fi_inputs",
        "read_e1_formation_s1fi_resource_snapshot",
        "run_small_five_arm_formation_in_memory",
        "capture_e1_formation_s1ff_in_memory",
        "evaluate_e1_formation_s1fd_state_convergence",
        "build_e1_common_probe_fresh_field",
        "run_e1_common_probe_real_probe_wrapper",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "decide_common_probe_evidence",
        "open",
        "write_text",
        "write_bytes",
    }
    checks = (
        (
            S1_FU_CHECK_NAMES[0],
            preflight.source_contract_digest == contract.contract_digest
            and preflight.synthetic_preflight_passed is True
            and preflight.execution_permitted is False,
        ),
        (
            S1_FU_CHECK_NAMES[1],
            tuple(inspect.signature(prepare_e1_formation_s1fi_inputs).parameters)
            == ("upstream_report_path",),
        ),
        (
            S1_FU_CHECK_NAMES[2],
            tuple(inspect.signature(read_e1_formation_s1fi_resource_snapshot).parameters)
            == (),
        ),
        (
            S1_FU_CHECK_NAMES[3],
            tuple(inspect.signature(run_small_five_arm_formation_in_memory).parameters)
            == (
                "refinement_id",
                "history_ab",
                "history_ba",
                "ab_proposal_steps",
                "ba_proposal_steps",
                "initial_field",
                "initial_state",
            ),
        ),
        (
            S1_FU_CHECK_NAMES[4],
            tuple(inspect.signature(capture_e1_formation_s1ff_in_memory).parameters)
            == ("results", "contract")
            and tuple(
                inspect.signature(evaluate_e1_formation_s1fd_state_convergence).parameters
            )
            == ("states", "contract"),
        ),
        (
            S1_FU_CHECK_NAMES[5],
            missing_roles == ("fixed-adapter-ab", "fixed-adapter-ba"),
        ),
        (
            S1_FU_CHECK_NAMES[6],
            tuple(inspect.signature(build_e1_common_probe_fresh_field).parameters)
            == ("binding", "initial_field")
            and tuple(inspect.signature(run_e1_common_probe_real_probe_wrapper).parameters)
            == ("resolved", "fresh", "frozen_state"),
        ),
        (
            S1_FU_CHECK_NAMES[7],
            callable(advance_fixed_e1_adapter_fast_shared_field_transient)
            and "advance_fixed_e1_adapter_fast_shared_field_transient"
            not in probe_source,
        ),
        (
            S1_FU_CHECK_NAMES[8],
            live_field_names.isdisjoint(result_fields),
        ),
        (
            S1_FU_CHECK_NAMES[9],
            tuple(inspect.signature(decide_common_probe_evidence).parameters)
            == (
                "active_s",
                "active_h",
                "coarse_s",
                "coarse_h",
                "fine_s",
                "fine_h",
                "p0_reset_s",
                "p0_reset_h",
                "feedback_ablation_s",
                "feedback_ablation_h",
                "formation_ablation_s",
                "formation_ablation_h",
            ),
        ),
        (S1_FU_CHECK_NAMES[10], _called_names(audit_source).isdisjoint(production_calls)),
    )
    passed = all(value for _, value in checks)
    values = {
        "audit_id": S1_FU_AUDIT_ID,
        "source_s1fs_contract_digest": contract.contract_digest,
        "source_s1ft_preflight_digest": preflight.preflight_digest,
        "unchanged_reusable_components": S1_FU_UNCHANGED_REUSABLE,
        "adaptable_components": S1_FU_ADAPTABLE,
        "missing_components": S1_FU_MISSING,
        "old_probe_roles": S1_EC45_PROBE_ROLES,
        "required_probe_roles": S1_FP_PROBE_ROLES,
        "missing_probe_roles": missing_roles,
        "s1fl_result_fields": result_fields,
        "live_state_export_present": not live_field_names.isdisjoint(result_fields),
        "unchanged_reusable_count": len(S1_FU_UNCHANGED_REUSABLE),
        "adaptable_count": len(S1_FU_ADAPTABLE),
        "missing_count": len(S1_FU_MISSING),
        "checks": checks,
        "static_audit_passed": passed,
        "new_field_mechanic_required": False,
        "new_live_state_handoff_required": True,
        "new_ten_role_slot_binding_required": True,
        "new_fixed_adapter_wrapper_required": True,
        "new_atomic_coordinator_required": True,
        "real_runner_implementation_permitted": False,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "EXISTING_KERNELS_REUSABLE_LIVE_STATE_HANDOFF_AND_"
            "TEN_ROLE_COORDINATION_MISSING"
        ),
        "reason": (
            "formation-resource-capture-evaluation-and-ec46-components-reuse;"
            "old-real-probe-binding-covers-eight-of-ten-roles;s1fl-does-not-"
            "export-live-states;new-field-physics-not-required"
        ),
    }
    return E1FormationS1FURealAdapterConnectionAudit(
        **values,
        audit_digest=_digest(values),
    )
