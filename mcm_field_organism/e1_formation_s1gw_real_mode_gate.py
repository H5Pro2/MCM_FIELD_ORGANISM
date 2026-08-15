"""S1-GW explicit real-mode gate for S1-GU."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_REFINEMENT_BATCH_COUNTS,
    S1_GF_ROLE_ORDER,
    S1_GF_TOTAL_BATCH_COUNT,
)
from .e1_formation_s1gs_real_single_batch_transition import (
    advance_e1_formation_s1gs_real_single_batch_transition,
)
from .e1_formation_s1gu_six_arm_counting_adapter import CarrierTransition
from .e1_formation_s1gv_real_mode_binding_contract import (
    E1FormationS1GVRealModeBindingContract,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GWRealModeGateError(ValueError):
    """Raised when S1-GW accepts real mode without the closed S1-GV contract."""


S1_GW_GATE_ID = "e1.s1gu-real-mode-gate.s1gw.v1"
S1_GW_DECISION = "S1GU_REAL_MODE_GATE_BOUND_EXECUTION_STILL_CLOSED"


@dataclass(frozen=True, slots=True)
class E1FormationS1GWRealModeGate:
    gate_id: str
    source_s1gv_contract_digest: str
    accepted_transition_name: str
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    planned_real_transition_count: int
    planned_field_step_count: int
    planned_source_support_count: int
    s1gv_contract_required: bool
    s1gs_transition_selected: bool
    real_mode_execution_permitted: bool
    owner_authorization_present: bool
    field_execution_performed: bool
    full_chain_opened: bool
    persistence_performed: bool
    retry_permitted: bool
    claims_permitted: bool
    memory_decision_permitted: bool
    decision: str
    gate_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "gate_digest"
        }
        if (
            self.gate_id != S1_GW_GATE_ID
            or len(self.source_s1gv_contract_digest) != 64
            or self.accepted_transition_name
            != "advance_e1_formation_s1gs_real_single_batch_transition"
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or self.planned_real_transition_count != S1_GF_TOTAL_BATCH_COUNT
            or self.planned_field_step_count != S1_GF_TOTAL_BATCH_COUNT
            or self.planned_source_support_count != 660
            or self.s1gv_contract_required is not True
            or self.s1gs_transition_selected is not True
            or any(
                value is not False
                for value in (
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
            or self.decision != S1_GW_DECISION
            or self.gate_digest != _digest(payload)
        ):
            raise E1FormationS1GWRealModeGateError(
                "S1-GW gate opened execution, changed transition, or permitted claims"
            )


def build_e1_formation_s1gw_real_mode_gate(
    contract: E1FormationS1GVRealModeBindingContract,
) -> E1FormationS1GWRealModeGate:
    """Accept S1-GS for later S1-GU injection without executing it."""

    if not isinstance(contract, E1FormationS1GVRealModeBindingContract):
        raise E1FormationS1GWRealModeGateError(
            "S1-GW requires the typed S1-GV real-mode contract"
        )
    contract.__post_init__()
    if (
        contract.real_mode_execution_permitted is not False
        or contract.field_execution_performed is not False
        or contract.claims_permitted is not False
        or contract.memory_decision_permitted is not False
        or contract.planned_real_transition_count != S1_GF_TOTAL_BATCH_COUNT
    ):
        raise E1FormationS1GWRealModeGateError(
            "S1-GW source contract is not closed for real-mode execution"
        )
    values = {
        "gate_id": S1_GW_GATE_ID,
        "source_s1gv_contract_digest": contract.contract_digest,
        "accepted_transition_name": (
            "advance_e1_formation_s1gs_real_single_batch_transition"
        ),
        "role_order": S1_GF_ROLE_ORDER,
        "refinement_step_counts": S1_GF_REFINEMENT_BATCH_COUNTS,
        "planned_real_transition_count": S1_GF_TOTAL_BATCH_COUNT,
        "planned_field_step_count": S1_GF_TOTAL_BATCH_COUNT,
        "planned_source_support_count": 660,
        "s1gv_contract_required": True,
        "s1gs_transition_selected": True,
        "real_mode_execution_permitted": False,
        "owner_authorization_present": False,
        "field_execution_performed": False,
        "full_chain_opened": False,
        "persistence_performed": False,
        "retry_permitted": False,
        "claims_permitted": False,
        "memory_decision_permitted": False,
        "decision": S1_GW_DECISION,
    }
    return E1FormationS1GWRealModeGate(**values, gate_digest=_digest(values))


def s1gw_real_mode_transition_for_later_injection(
    gate: E1FormationS1GWRealModeGate,
) -> CarrierTransition:
    """Return the real transition callable only behind the closed S1-GW gate."""

    if not isinstance(gate, E1FormationS1GWRealModeGate):
        raise E1FormationS1GWRealModeGateError(
            "S1-GW transition selection requires one typed gate"
        )
    gate.__post_init__()
    if (
        gate.real_mode_execution_permitted is not False
        or gate.field_execution_performed is not False
        or gate.claims_permitted is not False
    ):
        raise E1FormationS1GWRealModeGateError(
            "S1-GW gate cannot select a transition after execution opens"
        )
    return advance_e1_formation_s1gs_real_single_batch_transition
