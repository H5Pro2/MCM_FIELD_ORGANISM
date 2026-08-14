"""S1-EC52 static real-interface binding for the contact-aware common probe."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import inspect
from pathlib import Path

from .e1_common_probe_contact_axis_fixture import S1_EC51_FIXTURE_ID
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_confirmation_prepared_real_formation_kernel import (
    run_prepared_real_formation_arm_in_memory,
)
from .e1_frozen_state_transfer_contract import _fixed_probe_sequences, _probe_digest
from .e1_frozen_transient_probe import advance_frozen_e1_fast_shared_field_transient
from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_release_contract import (
    S1_EC29_CONTACT_COUNTS,
    S1_EC29_PLAN_SET_DIGEST,
    S1_EC29_REFINEMENTS,
)
from .neutral_local_field_substrate import advance_neutral_fast_shared_field_transient


class E1CommonProbeRealBindingContractError(ValueError):
    """Raised when EC52 changes a real interface or releases execution."""


S1_EC52_CONTRACT_ID = "e1.common-probe-real-binding.s1ec52.v1"
S1_EC52_EC51_RESULT_DIGEST = (
    "913c9ee7bf379a6e2f0a4d9bb8ef1d04e15260bcf80673ebb150a0426d321129"
)
S1_EC52_FORMATION_STATE_ROLES = (
    "active-ab",
    "active-ba",
    "formation-ablated-ab",
    "formation-ablated-ba",
)


def _source_digest(filename: str) -> str:
    path = Path(__file__).with_name(filename)
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CommonProbeRealSlotBinding:
    contact_count: int
    refinement_id: str
    role_id: str
    formation_schedule: str
    formation_arm_id: str | None
    state_role: str | None
    probe_kernel: str
    backreaction_enabled: bool
    fresh_field_strategy: str
    probe_source_digest: str
    binding_digest: str

    def __post_init__(self) -> None:
        is_p0 = self.role_id.startswith("p0-reset-")
        side = "ab" if self.role_id.endswith("-ab") else "ba"
        expected_schedule = "none" if is_p0 else (
            "repeated" if side == "ab" else "continuous"
        )
        formation_ablated = "formation-ablated" in self.role_id
        expected_arm = None if is_p0 else side + (
            "_formation_ablated" if formation_ablated else ""
        )
        expected_state = None if is_p0 else (
            f"formation-ablated-{side}" if formation_ablated else f"active-{side}"
        )
        expected_backreaction = not is_p0 and "probe-feedback-ablated" not in self.role_id
        if (
            self.contact_count not in S1_EC29_CONTACT_COUNTS
            or self.refinement_id not in S1_EC29_REFINEMENTS
            or self.role_id not in S1_EC45_PROBE_ROLES
            or self.formation_schedule != expected_schedule
            or self.formation_arm_id != expected_arm
            or self.state_role != expected_state
            or self.probe_kernel != (
                "advance_neutral_fast_shared_field_transient"
                if is_p0 else "advance_frozen_e1_fast_shared_field_transient"
            )
            or self.backreaction_enabled is not expected_backreaction
            or self.fresh_field_strategy
            != "deepcopy-identical-prepared-initial-field-per-slot"
            or len(self.probe_source_digest) != 64
        ):
            raise E1CommonProbeRealBindingContractError(
                "S1-EC52 real slot binding changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "binding_digest"
        }
        if self.binding_digest != _digest(payload):
            raise E1CommonProbeRealBindingContractError(
                "S1-EC52 slot binding digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeRealBindingContract:
    contract_id: str
    source_fixture_id: str
    source_fixture_digest: str
    source_plan_set_digest: str
    probe_source_digest: str
    implementation_digests: tuple[tuple[str, str], ...]
    contact_counts: tuple[int, ...]
    refinements: tuple[str, ...]
    roles: tuple[str, ...]
    formation_state_roles: tuple[str, ...]
    slot_bindings: tuple[E1CommonProbeRealSlotBinding, ...]
    formation_state_count: int
    probe_slot_count: int
    common_probe_source_for_all_slots: bool
    contact_axis_bound_to_plan_pairs: bool
    active_state_reused_only_across_matching_probe_modes: bool
    fresh_field_per_probe_slot_required: bool
    identical_probe_plan_per_refinement_required: bool
    real_adapter_implementation_permitted: bool
    field_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        expected_order = tuple(
            (contact, refinement, role)
            for contact in S1_EC29_CONTACT_COUNTS
            for refinement in S1_EC29_REFINEMENTS
            for role in S1_EC45_PROBE_ROLES
        )
        if (
            self.contract_id != S1_EC52_CONTRACT_ID
            or self.source_fixture_id != S1_EC51_FIXTURE_ID
            or self.source_fixture_digest != S1_EC52_EC51_RESULT_DIGEST
            or self.source_plan_set_digest != S1_EC29_PLAN_SET_DIGEST
            or len(self.probe_source_digest) != 64
            or tuple(role for role, _ in self.implementation_digests) != (
                "formation", "neutral-probe", "frozen-e1-probe",
                "repetition-planner", "fixed-probe-source",
            )
            or any(len(value) != 64 for _, value in self.implementation_digests)
            or self.contact_counts != (1, 2)
            or self.refinements != ("r2", "r4", "r8")
            or self.roles != S1_EC45_PROBE_ROLES
            or self.formation_state_roles != S1_EC52_FORMATION_STATE_ROLES
            or tuple(
                (item.contact_count, item.refinement_id, item.role_id)
                for item in self.slot_bindings
            ) != expected_order
            or self.formation_state_count != 24
            or self.probe_slot_count != 48
            or any(value is not True for value in (
                self.common_probe_source_for_all_slots,
                self.contact_axis_bound_to_plan_pairs,
                self.active_state_reused_only_across_matching_probe_modes,
                self.fresh_field_per_probe_slot_required,
                self.identical_probe_plan_per_refinement_required,
                self.real_adapter_implementation_permitted,
            ))
            or any(value is not False for value in (
                self.field_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision != "REAL_INTERFACES_BOUND_ADAPTER_IMPLEMENTATION_MISSING"
            or not self.reason
        ):
            raise E1CommonProbeRealBindingContractError(
                "S1-EC52 changed or crossed its static binding scope"
            )
        for item in self.slot_bindings:
            item.__post_init__()
            if item.probe_source_digest != self.probe_source_digest:
                raise E1CommonProbeRealBindingContractError(
                    "S1-EC52 slot probe sources differ"
                )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"slot_bindings", "contract_digest"}
        }
        payload["slot_binding_digests"] = tuple(
            item.binding_digest for item in self.slot_bindings
        )
        if self.contract_digest != _digest(payload):
            raise E1CommonProbeRealBindingContractError(
                "S1-EC52 contract digest changed"
            )


def build_e1_common_probe_real_binding_contract(
) -> E1CommonProbeRealBindingContract:
    """Bind real callable identities and all 48 slots without invoking them."""

    formation_parameters = tuple(
        inspect.signature(run_prepared_real_formation_arm_in_memory).parameters
    )
    neutral_parameters = tuple(
        inspect.signature(advance_neutral_fast_shared_field_transient).parameters
    )
    frozen_parameters = tuple(
        inspect.signature(advance_frozen_e1_fast_shared_field_transient).parameters
    )
    if formation_parameters != (
        "arm_id", "refinement_id", "sequences", "proposal_steps",
        "initial_field", "initial_state", "formation_enabled",
    ) or neutral_parameters[:2] != ("field", "distribution") or (
        frozen_parameters[:2] != ("field", "frozen_e1_state")
        or "backreaction_enabled" not in frozen_parameters
    ):
        raise E1CommonProbeRealBindingContractError(
            "S1-EC52 real callable signature changed"
        )
    probe_digest = _probe_digest(_fixed_probe_sequences())
    slots = []
    for contact_count in S1_EC29_CONTACT_COUNTS:
        for refinement in S1_EC29_REFINEMENTS:
            for role in S1_EC45_PROBE_ROLES:
                is_p0 = role.startswith("p0-reset-")
                side = "ab" if role.endswith("-ab") else "ba"
                formation_ablated = "formation-ablated" in role
                values = {
                    "contact_count": contact_count,
                    "refinement_id": refinement,
                    "role_id": role,
                    "formation_schedule": "none" if is_p0 else (
                        "repeated" if side == "ab" else "continuous"
                    ),
                    "formation_arm_id": None if is_p0 else side + (
                        "_formation_ablated" if formation_ablated else ""
                    ),
                    "state_role": None if is_p0 else (
                        f"formation-ablated-{side}"
                        if formation_ablated else f"active-{side}"
                    ),
                    "probe_kernel": (
                        "advance_neutral_fast_shared_field_transient"
                        if is_p0
                        else "advance_frozen_e1_fast_shared_field_transient"
                    ),
                    "backreaction_enabled": (
                        not is_p0 and "probe-feedback-ablated" not in role
                    ),
                    "fresh_field_strategy": (
                        "deepcopy-identical-prepared-initial-field-per-slot"
                    ),
                    "probe_source_digest": probe_digest,
                }
                slots.append(E1CommonProbeRealSlotBinding(
                    **values,
                    binding_digest=_digest(values),
                ))
    values = {
        "contract_id": S1_EC52_CONTRACT_ID,
        "source_fixture_id": S1_EC51_FIXTURE_ID,
        "source_fixture_digest": S1_EC52_EC51_RESULT_DIGEST,
        "source_plan_set_digest": S1_EC29_PLAN_SET_DIGEST,
        "probe_source_digest": probe_digest,
        "implementation_digests": tuple(
            (role, _source_digest(filename))
            for role, filename in (
                ("formation", "e1_confirmation_prepared_real_formation_kernel.py"),
                ("neutral-probe", "neutral_local_field_substrate.py"),
                ("frozen-e1-probe", "e1_frozen_transient_probe.py"),
                ("repetition-planner", "e1_repetition_formation_planner.py"),
                ("fixed-probe-source", "e1_frozen_state_transfer_contract.py"),
            )
        ),
        "contact_counts": S1_EC29_CONTACT_COUNTS,
        "refinements": S1_EC29_REFINEMENTS,
        "roles": S1_EC45_PROBE_ROLES,
        "formation_state_roles": S1_EC52_FORMATION_STATE_ROLES,
        "slot_bindings": tuple(slots),
        "formation_state_count": (
            len(S1_EC29_CONTACT_COUNTS)
            * len(S1_EC29_REFINEMENTS)
            * len(S1_EC52_FORMATION_STATE_ROLES)
        ),
        "probe_slot_count": len(slots),
        "common_probe_source_for_all_slots": True,
        "contact_axis_bound_to_plan_pairs": True,
        "active_state_reused_only_across_matching_probe_modes": True,
        "fresh_field_per_probe_slot_required": True,
        "identical_probe_plan_per_refinement_required": True,
        "real_adapter_implementation_permitted": True,
        "field_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "REAL_INTERFACES_BOUND_ADAPTER_IMPLEMENTATION_MISSING",
        "reason": (
            "contact-aware-formation-and-common-probe-callable-identities-bound;"
            "typed-real-adapter-not-yet-implemented-or-released"
        ),
    }
    payload = {
        name: value
        for name, value in values.items()
        if name != "slot_bindings"
    }
    payload["slot_binding_digests"] = tuple(item.binding_digest for item in slots)
    return E1CommonProbeRealBindingContract(
        **values,
        contract_digest=_digest(payload),
    )
