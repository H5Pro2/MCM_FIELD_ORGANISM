"""S1-GX synthetic preflight for a later S1-GU real-mode run."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_REFINEMENT_BATCH_COUNTS,
    S1_GF_ROLE_ORDER,
    S1_GF_TOTAL_BATCH_COUNT,
)
from .e1_formation_s1gh_fresh_field_bridge import (
    E1FormationS1GHFreshFieldBridgeResult,
)
from .e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    E1FormationS1GKFixedAdapterRealWrapperContract,
)
from .e1_formation_s1gt_six_arm_release_scope_contract import (
    E1FormationS1GTSixArmReleaseScopeContract,
)
from .e1_formation_s1gv_real_mode_binding_contract import (
    E1FormationS1GVRealModeBindingContract,
)
from .e1_formation_s1gw_real_mode_gate import (
    E1FormationS1GWRealModeGate,
    s1gw_real_mode_transition_for_later_injection,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GXRealModePreflightError(ValueError):
    """Raised when S1-GX would execute or widen the real-mode run scope."""


S1_GX_PREFLIGHT_ID = "e1.s1gu-real-mode-preflight.s1gx.v1"
S1_GX_DECISION = "S1GU_REAL_MODE_PREFLIGHT_BOUND_CALLABLE_NOT_EXECUTED"


@dataclass(frozen=True, slots=True)
class E1FormationS1GXRealModePreflight:
    preflight_id: str
    source_s1gt_contract_digest: str
    source_s1gv_contract_digest: str
    source_s1gw_gate_digest: str
    source_s1gk_contract_digest: str
    source_s1gh_result_digest: str
    selected_transition_name: str
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    expected_arm_count: int
    expected_transition_count: int
    expected_field_step_count: int
    expected_source_support_count: int
    expected_output_count: int
    expected_receipt_count: int
    callable_selected: bool
    callable_executed: bool
    s1gu_runner_executed: bool
    real_mode_execution_permitted: bool
    owner_authorization_present: bool
    field_execution_performed: bool
    full_chain_opened: bool
    persistence_performed: bool
    retry_permitted: bool
    claims_permitted: bool
    memory_decision_permitted: bool
    decision: str
    preflight_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if (
            self.preflight_id != S1_GX_PREFLIGHT_ID
            or any(
                len(value) != 64
                for value in (
                    self.source_s1gt_contract_digest,
                    self.source_s1gv_contract_digest,
                    self.source_s1gw_gate_digest,
                    self.source_s1gk_contract_digest,
                    self.source_s1gh_result_digest,
                )
            )
            or self.selected_transition_name
            != "advance_e1_formation_s1gs_real_single_batch_transition"
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or self.expected_arm_count != 6
            or self.expected_transition_count != S1_GF_TOTAL_BATCH_COUNT
            or self.expected_field_step_count != S1_GF_TOTAL_BATCH_COUNT
            or self.expected_source_support_count != 660
            or self.expected_output_count != 6
            or self.expected_receipt_count != 6
            or self.callable_selected is not True
            or any(
                value is not False
                for value in (
                    self.callable_executed,
                    self.s1gu_runner_executed,
                    self.real_mode_execution_permitted,
                    self.owner_authorization_present,
                    self.field_execution_performed,
                    self.full_chain_opened,
                    self.persistence_performed,
                    self.retry_permitted,
                    self.claims_permitted,
                    self.memory_decision_permitted,
                )
            )
            or self.decision != S1_GX_DECISION
            or self.preflight_digest != _digest(payload)
        ):
            raise E1FormationS1GXRealModePreflightError(
                "S1-GX preflight executed, widened scope, or permitted claims"
            )


def preflight_e1_formation_s1gx_real_mode(
    scope: E1FormationS1GTSixArmReleaseScopeContract,
    real_mode_contract: E1FormationS1GVRealModeBindingContract,
    gate: E1FormationS1GWRealModeGate,
    source_contract: E1FormationS1GKFixedAdapterRealWrapperContract,
    bridge: E1FormationS1GHFreshFieldBridgeResult,
) -> E1FormationS1GXRealModePreflight:
    """Check the later real-mode wiring without executing the selected callable."""

    if (
        not isinstance(scope, E1FormationS1GTSixArmReleaseScopeContract)
        or not isinstance(real_mode_contract, E1FormationS1GVRealModeBindingContract)
        or not isinstance(gate, E1FormationS1GWRealModeGate)
        or not isinstance(source_contract, E1FormationS1GKFixedAdapterRealWrapperContract)
        or not isinstance(bridge, E1FormationS1GHFreshFieldBridgeResult)
    ):
        raise E1FormationS1GXRealModePreflightError(
            "S1-GX requires typed S1-GT, S1-GV, S1-GW, S1-GK, and S1-GH inputs"
        )
    scope.__post_init__()
    real_mode_contract.__post_init__()
    gate.__post_init__()
    source_contract.__post_init__()
    bridge.__post_init__()
    selected = s1gw_real_mode_transition_for_later_injection(gate)
    role_order = tuple((item.refinement_id, item.role_id) for item in bridge.fresh_bindings)
    if (
        real_mode_contract.source_s1gt_contract_digest != scope.contract_digest
        or gate.source_s1gv_contract_digest != real_mode_contract.contract_digest
        or scope.source_s1gk_contract_digest != source_contract.contract_digest
        or source_contract.source_s1gh_result_digest != bridge.result_digest
        or role_order != S1_GF_ROLE_ORDER
        or role_order != scope.role_order
        or real_mode_contract.role_order != S1_GF_ROLE_ORDER
        or gate.role_order != S1_GF_ROLE_ORDER
        or any(
            value is not False
            for value in (
                scope.execution_permitted,
                real_mode_contract.real_mode_execution_permitted,
                gate.real_mode_execution_permitted,
                source_contract.execution_permitted,
            )
        )
    ):
        raise E1FormationS1GXRealModePreflightError(
            "S1-GX source chain, role order, or closed execution boundary changed"
        )
    values = {
        "preflight_id": S1_GX_PREFLIGHT_ID,
        "source_s1gt_contract_digest": scope.contract_digest,
        "source_s1gv_contract_digest": real_mode_contract.contract_digest,
        "source_s1gw_gate_digest": gate.gate_digest,
        "source_s1gk_contract_digest": source_contract.contract_digest,
        "source_s1gh_result_digest": bridge.result_digest,
        "selected_transition_name": selected.__name__,
        "role_order": S1_GF_ROLE_ORDER,
        "refinement_step_counts": S1_GF_REFINEMENT_BATCH_COUNTS,
        "expected_arm_count": 6,
        "expected_transition_count": S1_GF_TOTAL_BATCH_COUNT,
        "expected_field_step_count": S1_GF_TOTAL_BATCH_COUNT,
        "expected_source_support_count": 660,
        "expected_output_count": 6,
        "expected_receipt_count": 6,
        "callable_selected": True,
        "callable_executed": False,
        "s1gu_runner_executed": False,
        "real_mode_execution_permitted": False,
        "owner_authorization_present": False,
        "field_execution_performed": False,
        "full_chain_opened": False,
        "persistence_performed": False,
        "retry_permitted": False,
        "claims_permitted": False,
        "memory_decision_permitted": False,
        "decision": S1_GX_DECISION,
    }
    return E1FormationS1GXRealModePreflight(
        **values,
        preflight_digest=_digest(values),
    )
