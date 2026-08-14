"""S1-FV static contract for live-state handoff and ten probe roles."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_formation_s1fp_common_probe_contract import (
    S1_FP_PROBE_ROLES,
    S1_FP_REFINEMENTS,
)
from .e1_formation_s1fu_real_adapter_connection_audit import (
    E1FormationS1FURealAdapterConnectionAudit,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FVLiveStateTenRoleContractError(ValueError):
    """Raised when S1-FV changes a route or opens implementation/execution."""


S1_FV_CONTRACT_ID = "e1.live-state-ten-role-handoff-contract.s1fv.v1"
S1_FV_SOURCE_STATE_ROUTES = (
    ("active-ab", "ab"),
    ("active-ba", "ba"),
    ("formation-ablated-ab", "ab_formation_ablated"),
    ("formation-ablated-ba", "ba_formation_ablated"),
)


def _route(role: str) -> tuple[str, str | None, str | None, bool, bool]:
    side = "ab" if role.endswith("-ab") else "ba"
    if role.startswith("p0-reset-"):
        return "neutral-p0", None, None, False, False
    if role.startswith("e1-active-"):
        return "frozen-e1-feedback-enabled", f"active-{side}", side, True, False
    if role.startswith("e1-probe-feedback-ablated-"):
        return "frozen-e1-feedback-disabled", f"active-{side}", side, False, False
    if role.startswith("e1-formation-ablated-"):
        return (
            "frozen-formation-ablated-feedback-enabled",
            f"formation-ablated-{side}",
            f"{side}_formation_ablated",
            True,
            False,
        )
    if role.startswith("fixed-adapter-"):
        return "fixed-adapter-derived-from-state", f"active-{side}", side, False, True
    raise E1FormationS1FVLiveStateTenRoleContractError(
        "S1-FV received an unknown probe role"
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1FVProbeSlotBinding:
    refinement_id: str
    role_id: str
    probe_mode: str
    source_state_role: str | None
    source_formation_arm_id: str | None
    live_state_object_required: bool
    backreaction_enabled: bool
    fixed_adapter_derivation_required: bool
    fresh_object_separated_field_required: bool
    source_state_mutation_permitted: bool
    legacy_contact_axis: str | None
    binding_digest: str

    def __post_init__(self) -> None:
        mode, state_role, arm_id, backreaction, fixed = _route(self.role_id)
        live_required = state_role is not None
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "binding_digest"
        }
        if (
            self.refinement_id not in S1_FP_REFINEMENTS
            or self.role_id not in S1_FP_PROBE_ROLES
            or self.probe_mode != mode
            or self.source_state_role != state_role
            or self.source_formation_arm_id != arm_id
            or self.live_state_object_required is not live_required
            or self.backreaction_enabled is not backreaction
            or self.fixed_adapter_derivation_required is not fixed
            or self.fresh_object_separated_field_required is not True
            or self.source_state_mutation_permitted is not False
            or self.legacy_contact_axis is not None
            or self.binding_digest != _digest(payload)
        ):
            raise E1FormationS1FVLiveStateTenRoleContractError(
                "S1-FV probe slot route changed"
            )


def _build_slot(refinement: str, role: str) -> E1FormationS1FVProbeSlotBinding:
    mode, state_role, arm_id, backreaction, fixed = _route(role)
    values = {
        "refinement_id": refinement,
        "role_id": role,
        "probe_mode": mode,
        "source_state_role": state_role,
        "source_formation_arm_id": arm_id,
        "live_state_object_required": state_role is not None,
        "backreaction_enabled": backreaction,
        "fixed_adapter_derivation_required": fixed,
        "fresh_object_separated_field_required": True,
        "source_state_mutation_permitted": False,
        "legacy_contact_axis": None,
    }
    return E1FormationS1FVProbeSlotBinding(
        **values,
        binding_digest=_digest(values),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1FVLiveStateTenRoleContract:
    contract_id: str
    source_s1fu_audit_digest: str
    refinements: tuple[str, ...]
    probe_roles: tuple[str, ...]
    source_state_routes: tuple[tuple[str, str], ...]
    slot_bindings: tuple[E1FormationS1FVProbeSlotBinding, ...]
    live_state_object_count: int
    identity_control_result_count: int
    probe_slot_count: int
    state_consuming_probe_slot_count: int
    p0_probe_slot_count: int
    fixed_adapter_derivation_count: int
    exact_live_object_identity_required: bool
    digest_only_handoff_permitted: bool
    captured_vector_reconstruction_permitted: bool
    source_state_frozen_across_all_dependent_probes: bool
    fixed_adapter_must_derive_from_exact_source_state: bool
    fixed_adapter_derivation_may_mutate_source_state: bool
    identity_control_may_feed_probe: bool
    legacy_contact_axis_required: bool
    synthetic_handoff_implementation_permitted: bool
    real_adapter_implementation_permitted: bool
    owner_authorization_present: bool
    execution_permitted: bool
    field_execution_performed: bool
    persistence_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        expected_slots = tuple(
            _build_slot(refinement, role)
            for refinement in S1_FP_REFINEMENTS
            for role in S1_FP_PROBE_ROLES
        )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"slot_bindings", "contract_digest"}
        }
        payload["slot_binding_digests"] = tuple(
            item.binding_digest for item in self.slot_bindings
        )
        if (
            self.contract_id != S1_FV_CONTRACT_ID
            or len(self.source_s1fu_audit_digest) != 64
            or self.refinements != S1_FP_REFINEMENTS
            or self.probe_roles != S1_FP_PROBE_ROLES
            or self.source_state_routes != S1_FV_SOURCE_STATE_ROUTES
            or self.slot_bindings != expected_slots
            or (self.live_state_object_count, self.identity_control_result_count)
            != (12, 3)
            or (
                self.probe_slot_count,
                self.state_consuming_probe_slot_count,
                self.p0_probe_slot_count,
                self.fixed_adapter_derivation_count,
            )
            != (30, 24, 6, 6)
            or any(
                value is not True
                for value in (
                    self.exact_live_object_identity_required,
                    self.source_state_frozen_across_all_dependent_probes,
                    self.fixed_adapter_must_derive_from_exact_source_state,
                    self.synthetic_handoff_implementation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.digest_only_handoff_permitted,
                    self.captured_vector_reconstruction_permitted,
                    self.fixed_adapter_derivation_may_mutate_source_state,
                    self.identity_control_may_feed_probe,
                    self.legacy_contact_axis_required,
                    self.real_adapter_implementation_permitted,
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.persistence_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "TEN_ROLE_LIVE_STATE_HANDOFF_BOUND_IMPLEMENTATION_MISSING"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1FVLiveStateTenRoleContractError(
                "S1-FV live-state handoff contract changed or opened execution"
            )


def prepare_e1_formation_s1fv_live_state_ten_role_contract(
    audit: E1FormationS1FURealAdapterConnectionAudit,
) -> E1FormationS1FVLiveStateTenRoleContract:
    """Bind all live-state routes without constructing or running an adapter."""

    if not isinstance(audit, E1FormationS1FURealAdapterConnectionAudit):
        raise E1FormationS1FVLiveStateTenRoleContractError(
            "S1-FV requires the typed S1-FU audit"
        )
    audit.__post_init__()
    if (
        audit.new_live_state_handoff_required is not True
        or audit.new_ten_role_slot_binding_required is not True
        or audit.new_fixed_adapter_wrapper_required is not True
        or audit.execution_permitted is not False
    ):
        raise E1FormationS1FVLiveStateTenRoleContractError(
            "S1-FV requires the closed S1-FU connection gap"
        )
    slots = tuple(
        _build_slot(refinement, role)
        for refinement in S1_FP_REFINEMENTS
        for role in S1_FP_PROBE_ROLES
    )
    values = {
        "contract_id": S1_FV_CONTRACT_ID,
        "source_s1fu_audit_digest": audit.audit_digest,
        "refinements": S1_FP_REFINEMENTS,
        "probe_roles": S1_FP_PROBE_ROLES,
        "source_state_routes": S1_FV_SOURCE_STATE_ROUTES,
        "slot_bindings": slots,
        "live_state_object_count": 12,
        "identity_control_result_count": 3,
        "probe_slot_count": len(slots),
        "state_consuming_probe_slot_count": sum(
            item.live_state_object_required for item in slots
        ),
        "p0_probe_slot_count": sum(
            item.source_state_role is None for item in slots
        ),
        "fixed_adapter_derivation_count": sum(
            item.fixed_adapter_derivation_required for item in slots
        ),
        "exact_live_object_identity_required": True,
        "digest_only_handoff_permitted": False,
        "captured_vector_reconstruction_permitted": False,
        "source_state_frozen_across_all_dependent_probes": True,
        "fixed_adapter_must_derive_from_exact_source_state": True,
        "fixed_adapter_derivation_may_mutate_source_state": False,
        "identity_control_may_feed_probe": False,
        "legacy_contact_axis_required": False,
        "synthetic_handoff_implementation_permitted": True,
        "real_adapter_implementation_permitted": False,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "persistence_permitted": False,
        "claims_permitted": False,
        "decision": "TEN_ROLE_LIVE_STATE_HANDOFF_BOUND_IMPLEMENTATION_MISSING",
        "reason": (
            "twelve-live-formation-state-objects-route-to-twenty-four-state-"
            "consuming-slots;six-p0-slots-have-no-state;six-fixed-adapters-"
            "derive-from-active-live-states;implementation-and-execution-closed"
        ),
    }
    digest_payload = {
        name: value for name, value in values.items() if name != "slot_bindings"
    }
    digest_payload["slot_binding_digests"] = tuple(
        item.binding_digest for item in slots
    )
    return E1FormationS1FVLiveStateTenRoleContract(
        **values,
        contract_digest=_digest(digest_payload),
    )
