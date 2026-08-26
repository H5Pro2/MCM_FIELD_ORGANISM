"""S1-EC49 injectable eight-role common-probe adapter, synthetic fixture only."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .e1_common_probe_acceptance_contract import E1CommonProbeAcceptanceContract
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_real_kernel_audit import E1CommonProbeRealKernelAudit
from .e1_common_probe_synthetic_runner_fixture import (
    E1CommonProbeSyntheticRunnerFixtureResult,
    E1SyntheticCommonProbeSample,
    S1_EC47_REFINEMENTS,
    build_synthetic_common_probe_sample,
    run_e1_common_probe_synthetic_runner_fixture,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEightRoleAdapterFixtureError(ValueError):
    """Raised when EC49 leaves its injected zero-field adapter boundary."""


S1_EC49_ADAPTER_ID = "e1.common-probe-eight-role-adapter.s1ec49.v1"
S1_EC49_EC46_CONTRACT_DIGEST = (
    "672239cddf2a1e8a8856a5bd2570ebaf0a9bdda5f52fb45aa0306e2570dd144b"
)
S1_EC49_EC48_AUDIT_DIGEST = (
    "8f7d15694e909c159e5bc8afad313490af1276acfec73b4d79f2af2173c9be7a"
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeFormationHandoff:
    refinement_id: str
    active_ab_state_digest: str
    active_ba_state_digest: str
    formation_ablated_ab_state_digest: str
    formation_ablated_ba_state_digest: str
    field_steps_executed: int
    synthetic: bool
    handoff_digest: str

    def __post_init__(self) -> None:
        state_digests = (
            self.active_ab_state_digest,
            self.active_ba_state_digest,
            self.formation_ablated_ab_state_digest,
            self.formation_ablated_ba_state_digest,
        )
        if (
            self.refinement_id not in S1_EC47_REFINEMENTS
            or any(len(value) != 64 for value in state_digests)
            or len(set(state_digests)) != 4
            or self.field_steps_executed != 0
            or self.synthetic is not True
        ):
            raise E1CommonProbeEightRoleAdapterFixtureError(
                "S1-EC49 formation handoff changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "handoff_digest"
        }
        if self.handoff_digest != _digest(payload):
            raise E1CommonProbeEightRoleAdapterFixtureError(
                "S1-EC49 formation handoff digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeResetSlot:
    refinement_id: str
    role_id: str
    slot_id: str
    initial_field_digest: str
    field_steps_executed: int
    synthetic: bool
    slot_digest: str

    def __post_init__(self) -> None:
        if (
            self.refinement_id not in S1_EC47_REFINEMENTS
            or self.role_id not in S1_EC45_PROBE_ROLES
            or self.slot_id != f"{self.refinement_id}:{self.role_id}"
            or len(self.initial_field_digest) != 64
            or self.field_steps_executed != 0
            or self.synthetic is not True
        ):
            raise E1CommonProbeEightRoleAdapterFixtureError(
                "S1-EC49 reset slot changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "slot_digest"
        }
        if self.slot_digest != _digest(payload):
            raise E1CommonProbeEightRoleAdapterFixtureError(
                "S1-EC49 reset slot digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeRoleReceipt:
    refinement_id: str
    role_id: str
    kernel_kind: str
    selected_state_digest: str | None
    backreaction_enabled: bool
    reset_slot_digest: str
    sample_digest: str
    field_steps_executed: int
    synthetic: bool
    receipt_digest: str

    def __post_init__(self) -> None:
        is_p0 = self.role_id.startswith("p0-reset-")
        expected_backreaction = (
            not is_p0 and "probe-feedback-ablated" not in self.role_id
        )
        if (
            self.refinement_id not in S1_EC47_REFINEMENTS
            or self.role_id not in S1_EC45_PROBE_ROLES
            or self.kernel_kind != ("neutral-p0" if is_p0 else "frozen-e1")
            or (self.selected_state_digest is None) is not is_p0
            or (
                self.selected_state_digest is not None
                and len(self.selected_state_digest) != 64
            )
            or self.backreaction_enabled is not expected_backreaction
            or len(self.reset_slot_digest) != 64
            or len(self.sample_digest) != 64
            or self.field_steps_executed != 0
            or self.synthetic is not True
        ):
            raise E1CommonProbeEightRoleAdapterFixtureError(
                "S1-EC49 role receipt changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if self.receipt_digest != _digest(payload):
            raise E1CommonProbeEightRoleAdapterFixtureError(
                "S1-EC49 receipt digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEightRoleAdapterFixtureResult:
    adapter_id: str
    source_contract_digest: str
    source_audit_digest: str
    formation_handoff_digests: tuple[str, ...]
    reset_slot_digests: tuple[str, ...]
    role_receipt_digests: tuple[str, ...]
    integrated_fixture_digest: str
    integrated_synthetic_decision: str
    formation_handoff_count: int
    reset_slot_count: int
    role_receipt_count: int
    all_reset_fields_identical_and_slots_separate: bool
    all_state_routes_exact: bool
    all_backreaction_routes_exact: bool
    field_steps_executed: int
    adapter_integration_complete: bool
    pilot_execution_performed: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.adapter_id != S1_EC49_ADAPTER_ID
            or self.source_contract_digest != S1_EC49_EC46_CONTRACT_DIGEST
            or self.source_audit_digest != S1_EC49_EC48_AUDIT_DIGEST
            or len(self.formation_handoff_digests) != 3
            or len(self.reset_slot_digests) != 24
            or len(self.role_receipt_digests) != 24
            or len(self.integrated_fixture_digest) != 64
            or self.integrated_synthetic_decision
            != "NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE"
            or self.formation_handoff_count != 3
            or self.reset_slot_count != 24
            or self.role_receipt_count != 24
            or any(value is not True for value in (
                self.all_reset_fields_identical_and_slots_separate,
                self.all_state_routes_exact,
                self.all_backreaction_routes_exact,
                self.adapter_integration_complete,
            ))
            or self.field_steps_executed != 0
            or any(value is not False for value in (
                self.pilot_execution_performed,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
        ):
            raise E1CommonProbeEightRoleAdapterFixtureError(
                "S1-EC49 result changed or crossed zero-field scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if self.result_digest != _digest(payload):
            raise E1CommonProbeEightRoleAdapterFixtureError(
                "S1-EC49 result digest changed"
            )


FormationKernel = Callable[[str], E1CommonProbeFormationHandoff]
ResetKernel = Callable[[str, str], E1CommonProbeResetSlot]
ProbeKernel = Callable[
    [str, str, str | None, bool], E1SyntheticCommonProbeSample
]


def build_synthetic_formation_handoff(
    refinement_id: str,
) -> E1CommonProbeFormationHandoff:
    values = {
        "refinement_id": refinement_id,
        "active_ab_state_digest": _digest((refinement_id, "active-ab")),
        "active_ba_state_digest": _digest((refinement_id, "active-ba")),
        "formation_ablated_ab_state_digest": _digest((refinement_id, "ablated-ab")),
        "formation_ablated_ba_state_digest": _digest((refinement_id, "ablated-ba")),
        "field_steps_executed": 0,
        "synthetic": True,
    }
    return E1CommonProbeFormationHandoff(
        **values,
        handoff_digest=_digest(values),
    )


def build_synthetic_reset_slot(
    refinement_id: str,
    role_id: str,
) -> E1CommonProbeResetSlot:
    values = {
        "refinement_id": refinement_id,
        "role_id": role_id,
        "slot_id": f"{refinement_id}:{role_id}",
        "initial_field_digest": _digest("ec49-identical-reset-field"),
        "field_steps_executed": 0,
        "synthetic": True,
    }
    return E1CommonProbeResetSlot(**values, slot_digest=_digest(values))


def build_synthetic_probe_sample(
    refinement_id: str,
    role_id: str,
    selected_state_digest: str | None,
    backreaction_enabled: bool,
) -> E1SyntheticCommonProbeSample:
    del selected_state_digest, backreaction_enabled
    return build_synthetic_common_probe_sample(role_id, refinement_id)


def _selected_state(
    role_id: str,
    handoff: E1CommonProbeFormationHandoff,
) -> str | None:
    if role_id.startswith("p0-reset-"):
        return None
    side = "ab" if role_id.endswith("-ab") else "ba"
    if "formation-ablated" in role_id:
        return getattr(handoff, f"formation_ablated_{side}_state_digest")
    return getattr(handoff, f"active_{side}_state_digest")


def run_e1_common_probe_eight_role_adapter_fixture(
    contract: E1CommonProbeAcceptanceContract,
    audit: E1CommonProbeRealKernelAudit,
    *,
    formation_kernel: FormationKernel = build_synthetic_formation_handoff,
    reset_kernel: ResetKernel = build_synthetic_reset_slot,
    probe_kernel: ProbeKernel = build_synthetic_probe_sample,
) -> E1CommonProbeEightRoleAdapterFixtureResult:
    """Route all eight roles through injected kernels with zero real steps."""

    if (
        not isinstance(contract, E1CommonProbeAcceptanceContract)
        or not isinstance(audit, E1CommonProbeRealKernelAudit)
    ):
        raise E1CommonProbeEightRoleAdapterFixtureError(
            "S1-EC49 requires typed EC46 and EC48 inputs"
        )
    contract.__post_init__()
    audit.__post_init__()
    if (
        contract.contract_digest != S1_EC49_EC46_CONTRACT_DIGEST
        or audit.audit_digest != S1_EC49_EC48_AUDIT_DIGEST
        or audit.narrow_adapter_implementation_permitted is not True
        or audit.field_execution_permitted is not False
        or not all(callable(item) for item in (
            formation_kernel, reset_kernel, probe_kernel
        ))
    ):
        raise E1CommonProbeEightRoleAdapterFixtureError(
            "S1-EC49 upstream binding or injected kernel changed"
        )
    handoffs = []
    slots = []
    receipts = []
    samples = {}
    for refinement in S1_EC47_REFINEMENTS:
        handoff = formation_kernel(refinement)
        if not isinstance(handoff, E1CommonProbeFormationHandoff):
            raise E1CommonProbeEightRoleAdapterFixtureError(
                "S1-EC49 formation kernel returned no typed handoff"
            )
        handoff.__post_init__()
        if handoff.refinement_id != refinement:
            raise E1CommonProbeEightRoleAdapterFixtureError(
                "S1-EC49 formation handoff occupies the wrong slot"
            )
        handoffs.append(handoff)
        for role in S1_EC45_PROBE_ROLES:
            slot = reset_kernel(refinement, role)
            if not isinstance(slot, E1CommonProbeResetSlot):
                raise E1CommonProbeEightRoleAdapterFixtureError(
                    "S1-EC49 reset kernel returned no typed slot"
                )
            slot.__post_init__()
            if (slot.refinement_id, slot.role_id) != (refinement, role):
                raise E1CommonProbeEightRoleAdapterFixtureError(
                    "S1-EC49 reset slot identity changed"
                )
            selected = _selected_state(role, handoff)
            backreaction = (
                not role.startswith("p0-reset-")
                and "probe-feedback-ablated" not in role
            )
            sample = probe_kernel(refinement, role, selected, backreaction)
            if not isinstance(sample, E1SyntheticCommonProbeSample):
                raise E1CommonProbeEightRoleAdapterFixtureError(
                    "S1-EC49 probe kernel returned no typed sample"
                )
            sample.__post_init__()
            if (sample.refinement_id, sample.role_id) != (refinement, role):
                raise E1CommonProbeEightRoleAdapterFixtureError(
                    "S1-EC49 sample identity changed"
                )
            receipt_values = {
                "refinement_id": refinement,
                "role_id": role,
                "kernel_kind": (
                    "neutral-p0" if role.startswith("p0-reset-") else "frozen-e1"
                ),
                "selected_state_digest": selected,
                "backreaction_enabled": backreaction,
                "reset_slot_digest": slot.slot_digest,
                "sample_digest": sample.sample_digest,
                "field_steps_executed": 0,
                "synthetic": True,
            }
            receipts.append(E1CommonProbeRoleReceipt(
                **receipt_values,
                receipt_digest=_digest(receipt_values),
            ))
            slots.append(slot)
            samples[(refinement, role)] = sample

    integrated: E1CommonProbeSyntheticRunnerFixtureResult = (
        run_e1_common_probe_synthetic_runner_fixture(
            contract,
            sample_kernel=lambda role, refinement: samples[(refinement, role)],
        )
    )
    initial_digests = {item.initial_field_digest for item in slots}
    slot_ids = {item.slot_id for item in slots}
    values = {
        "adapter_id": S1_EC49_ADAPTER_ID,
        "source_contract_digest": contract.contract_digest,
        "source_audit_digest": audit.audit_digest,
        "formation_handoff_digests": tuple(item.handoff_digest for item in handoffs),
        "reset_slot_digests": tuple(item.slot_digest for item in slots),
        "role_receipt_digests": tuple(item.receipt_digest for item in receipts),
        "integrated_fixture_digest": integrated.result_digest,
        "integrated_synthetic_decision": integrated.synthetic_decision,
        "formation_handoff_count": len(handoffs),
        "reset_slot_count": len(slots),
        "role_receipt_count": len(receipts),
        "all_reset_fields_identical_and_slots_separate": (
            len(initial_digests) == 1 and len(slot_ids) == 24
        ),
        "all_state_routes_exact": all(
            item.selected_state_digest == _selected_state(
                item.role_id,
                handoffs[S1_EC47_REFINEMENTS.index(item.refinement_id)],
            )
            for item in receipts
        ),
        "all_backreaction_routes_exact": all(
            item.backreaction_enabled is (
                not item.role_id.startswith("p0-reset-")
                and "probe-feedback-ablated" not in item.role_id
            )
            for item in receipts
        ),
        "field_steps_executed": sum(
            item.field_steps_executed for item in (*handoffs, *slots, *receipts)
        ),
        "adapter_integration_complete": True,
        "pilot_execution_performed": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeEightRoleAdapterFixtureResult(
        **values,
        result_digest=_digest(values),
    )
