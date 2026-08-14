"""S1-EC53 typed contact-aware real-adapter skeleton with zero-step kernels."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .e1_common_probe_real_binding_contract import (
    E1CommonProbeRealBindingContract,
    E1CommonProbeRealSlotBinding,
    S1_EC52_FORMATION_STATE_ROLES,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeTypedRealAdapterFixtureError(ValueError):
    """Raised when EC53 leaves its typed zero-step adapter boundary."""


S1_EC53_ADAPTER_ID = "e1.common-probe-typed-real-adapter.s1ec53.v1"
S1_EC53_EC52_CONTRACT_DIGEST = (
    "291ea70c96ad26b3f6e696588ebd55d3e6f7163967b45de9a689bd731cb7bf7b"
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64


@dataclass(frozen=True, slots=True)
class E1RealPlanReceipt:
    contact_count: int
    refinement_id: str
    repeated_plan_digest: str
    continuous_plan_digest: str
    probe_plan_digest: str
    field_steps_executed: int
    receipt_digest: str

    def __post_init__(self) -> None:
        if (
            self.contact_count not in (1, 2)
            or self.refinement_id not in ("r2", "r4", "r8")
            or any(not _valid_digest(value) for value in (
                self.repeated_plan_digest,
                self.continuous_plan_digest,
                self.probe_plan_digest,
            ))
            or self.field_steps_executed != 0
        ):
            raise E1CommonProbeTypedRealAdapterFixtureError(
                "S1-EC53 plan receipt changed"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "receipt_digest"}
        if self.receipt_digest != _digest(payload):
            raise E1CommonProbeTypedRealAdapterFixtureError(
                "S1-EC53 plan receipt digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1RealFormationReceipt:
    contact_count: int
    refinement_id: str
    state_role: str
    formation_schedule: str
    formation_arm_id: str
    plan_digest: str
    output_state_digest: str
    field_steps_executed: int
    receipt_digest: str

    def __post_init__(self) -> None:
        side = "ab" if self.state_role.endswith("-ab") else "ba"
        ablated = self.state_role.startswith("formation-ablated")
        if (
            self.contact_count not in (1, 2)
            or self.refinement_id not in ("r2", "r4", "r8")
            or self.state_role not in S1_EC52_FORMATION_STATE_ROLES
            or self.formation_schedule != (
                "repeated" if side == "ab" else "continuous"
            )
            or self.formation_arm_id != side + (
                "_formation_ablated" if ablated else ""
            )
            or not _valid_digest(self.plan_digest)
            or not _valid_digest(self.output_state_digest)
            or self.field_steps_executed != 0
        ):
            raise E1CommonProbeTypedRealAdapterFixtureError(
                "S1-EC53 formation receipt changed"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "receipt_digest"}
        if self.receipt_digest != _digest(payload):
            raise E1CommonProbeTypedRealAdapterFixtureError(
                "S1-EC53 formation receipt digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1RealFreshFieldReceipt:
    slot_binding_digest: str
    slot_id: str
    initial_field_digest: str
    field_object_token: str
    field_steps_executed: int
    receipt_digest: str

    def __post_init__(self) -> None:
        if (
            not _valid_digest(self.slot_binding_digest)
            or not self.slot_id
            or not _valid_digest(self.initial_field_digest)
            or not self.field_object_token
            or self.field_steps_executed != 0
        ):
            raise E1CommonProbeTypedRealAdapterFixtureError(
                "S1-EC53 fresh-field receipt changed"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "receipt_digest"}
        if self.receipt_digest != _digest(payload):
            raise E1CommonProbeTypedRealAdapterFixtureError(
                "S1-EC53 fresh-field receipt digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1RealProbeReceipt:
    slot_binding_digest: str
    probe_kernel: str
    selected_state_digest: str | None
    backreaction_enabled: bool
    fresh_field_receipt_digest: str
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    field_steps_executed: int
    receipt_digest: str

    def __post_init__(self) -> None:
        is_p0 = self.probe_kernel == "advance_neutral_fast_shared_field_transient"
        if (
            not _valid_digest(self.slot_binding_digest)
            or self.probe_kernel not in (
                "advance_neutral_fast_shared_field_transient",
                "advance_frozen_e1_fast_shared_field_transient",
            )
            or (self.selected_state_digest is None) is not is_p0
            or (self.selected_state_digest is not None and not _valid_digest(self.selected_state_digest))
            or not isinstance(self.backreaction_enabled, bool)
            or (is_p0 and self.backreaction_enabled is not False)
            or not _valid_digest(self.fresh_field_receipt_digest)
            or not self.activation
            or len(self.activation) != len(self.afterimage)
            or self.field_steps_executed != 0
        ):
            raise E1CommonProbeTypedRealAdapterFixtureError(
                "S1-EC53 probe receipt changed"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "receipt_digest"}
        if self.receipt_digest != _digest(payload):
            raise E1CommonProbeTypedRealAdapterFixtureError(
                "S1-EC53 probe receipt digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeTypedRealAdapterFixtureResult:
    adapter_id: str
    source_contract_digest: str
    plan_receipt_digests: tuple[str, ...]
    formation_receipt_digests: tuple[str, ...]
    fresh_field_receipt_digests: tuple[str, ...]
    probe_receipt_digests: tuple[str, ...]
    plan_receipt_count: int
    formation_receipt_count: int
    fresh_field_receipt_count: int
    probe_receipt_count: int
    all_plan_routes_exact: bool
    all_state_routes_exact: bool
    all_fresh_fields_identical_and_object_separate: bool
    all_probe_routes_exact: bool
    field_steps_executed: int
    typed_real_adapter_implemented: bool
    real_kernel_execution_permitted: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.adapter_id != S1_EC53_ADAPTER_ID
            or self.source_contract_digest != S1_EC53_EC52_CONTRACT_DIGEST
            or len(self.plan_receipt_digests) != 6
            or len(self.formation_receipt_digests) != 24
            or len(self.fresh_field_receipt_digests) != 48
            or len(self.probe_receipt_digests) != 48
            or (
                self.plan_receipt_count,
                self.formation_receipt_count,
                self.fresh_field_receipt_count,
                self.probe_receipt_count,
            ) != (6, 24, 48, 48)
            or any(value is not True for value in (
                self.all_plan_routes_exact,
                self.all_state_routes_exact,
                self.all_fresh_fields_identical_and_object_separate,
                self.all_probe_routes_exact,
                self.typed_real_adapter_implemented,
            ))
            or self.field_steps_executed != 0
            or any(value is not False for value in (
                self.real_kernel_execution_permitted,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
        ):
            raise E1CommonProbeTypedRealAdapterFixtureError(
                "S1-EC53 result changed or crossed zero-step scope"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "result_digest"}
        if self.result_digest != _digest(payload):
            raise E1CommonProbeTypedRealAdapterFixtureError(
                "S1-EC53 result digest changed"
            )


PlanKernel = Callable[[int, str, str], E1RealPlanReceipt]
FormationKernel = Callable[[int, str, str, E1RealPlanReceipt], E1RealFormationReceipt]
FreshFieldKernel = Callable[[E1CommonProbeRealSlotBinding], E1RealFreshFieldReceipt]
ProbeKernel = Callable[[E1CommonProbeRealSlotBinding, E1RealFreshFieldReceipt, str | None], E1RealProbeReceipt]


def _plan_kernel(contact: int, refinement: str, probe_digest: str) -> E1RealPlanReceipt:
    values = {
        "contact_count": contact,
        "refinement_id": refinement,
        "repeated_plan_digest": _digest((contact, refinement, "repeated")),
        "continuous_plan_digest": _digest((contact, refinement, "continuous")),
        "probe_plan_digest": _digest((refinement, probe_digest)),
        "field_steps_executed": 0,
    }
    return E1RealPlanReceipt(**values, receipt_digest=_digest(values))


def _formation_kernel(contact: int, refinement: str, state_role: str, plan: E1RealPlanReceipt) -> E1RealFormationReceipt:
    side = "ab" if state_role.endswith("-ab") else "ba"
    ablated = state_role.startswith("formation-ablated")
    values = {
        "contact_count": contact,
        "refinement_id": refinement,
        "state_role": state_role,
        "formation_schedule": "repeated" if side == "ab" else "continuous",
        "formation_arm_id": side + ("_formation_ablated" if ablated else ""),
        "plan_digest": plan.repeated_plan_digest if side == "ab" else plan.continuous_plan_digest,
        "output_state_digest": _digest((contact, refinement, state_role, "state")),
        "field_steps_executed": 0,
    }
    return E1RealFormationReceipt(**values, receipt_digest=_digest(values))


def _fresh_field_kernel(slot: E1CommonProbeRealSlotBinding) -> E1RealFreshFieldReceipt:
    slot_id = f"n{slot.contact_count}:{slot.refinement_id}:{slot.role_id}"
    values = {
        "slot_binding_digest": slot.binding_digest,
        "slot_id": slot_id,
        "initial_field_digest": _digest("ec53-identical-initial-field"),
        "field_object_token": f"object:{slot_id}",
        "field_steps_executed": 0,
    }
    return E1RealFreshFieldReceipt(**values, receipt_digest=_digest(values))


def _probe_kernel(slot: E1CommonProbeRealSlotBinding, field: E1RealFreshFieldReceipt, state_digest: str | None) -> E1RealProbeReceipt:
    values = {
        "slot_binding_digest": slot.binding_digest,
        "probe_kernel": slot.probe_kernel,
        "selected_state_digest": state_digest,
        "backreaction_enabled": slot.backreaction_enabled,
        "fresh_field_receipt_digest": field.receipt_digest,
        "activation": (0.0, 0.0, 0.0),
        "afterimage": (0.0, 0.0, 0.0),
        "field_steps_executed": 0,
    }
    return E1RealProbeReceipt(**values, receipt_digest=_digest(values))


def run_e1_common_probe_typed_real_adapter_fixture(
    contract: E1CommonProbeRealBindingContract,
    *,
    plan_kernel: PlanKernel = _plan_kernel,
    formation_kernel: FormationKernel = _formation_kernel,
    fresh_field_kernel: FreshFieldKernel = _fresh_field_kernel,
    probe_kernel: ProbeKernel = _probe_kernel,
) -> E1CommonProbeTypedRealAdapterFixtureResult:
    """Exercise the typed adapter only through injected zero-step receipts."""

    if not isinstance(contract, E1CommonProbeRealBindingContract):
        raise E1CommonProbeTypedRealAdapterFixtureError("S1-EC53 requires the typed EC52 contract")
    contract.__post_init__()
    if contract.contract_digest != S1_EC53_EC52_CONTRACT_DIGEST or contract.real_adapter_implementation_permitted is not True or contract.field_execution_permitted is not False or not all(callable(x) for x in (plan_kernel, formation_kernel, fresh_field_kernel, probe_kernel)):
        raise E1CommonProbeTypedRealAdapterFixtureError("S1-EC53 upstream binding or injected kernel changed")
    plans = {}
    formations = {}
    fields = []
    probes = []
    for contact in contract.contact_counts:
        for refinement in contract.refinements:
            plan = plan_kernel(contact, refinement, contract.probe_source_digest)
            if not isinstance(plan, E1RealPlanReceipt) or (plan.contact_count, plan.refinement_id) != (contact, refinement):
                raise E1CommonProbeTypedRealAdapterFixtureError("S1-EC53 plan kernel returned the wrong receipt")
            plan.__post_init__()
            plans[(contact, refinement)] = plan
            for state_role in contract.formation_state_roles:
                formed = formation_kernel(contact, refinement, state_role, plan)
                if not isinstance(formed, E1RealFormationReceipt) or (formed.contact_count, formed.refinement_id, formed.state_role) != (contact, refinement, state_role):
                    raise E1CommonProbeTypedRealAdapterFixtureError("S1-EC53 formation kernel returned the wrong receipt")
                formed.__post_init__()
                formations[(contact, refinement, state_role)] = formed
    for slot in contract.slot_bindings:
        fresh = fresh_field_kernel(slot)
        if not isinstance(fresh, E1RealFreshFieldReceipt) or fresh.slot_binding_digest != slot.binding_digest:
            raise E1CommonProbeTypedRealAdapterFixtureError("S1-EC53 fresh-field kernel returned the wrong receipt")
        fresh.__post_init__()
        state_digest = None if slot.state_role is None else formations[(slot.contact_count, slot.refinement_id, slot.state_role)].output_state_digest
        probe = probe_kernel(slot, fresh, state_digest)
        if not isinstance(probe, E1RealProbeReceipt) or probe.slot_binding_digest != slot.binding_digest:
            raise E1CommonProbeTypedRealAdapterFixtureError("S1-EC53 probe kernel returned the wrong receipt")
        probe.__post_init__()
        fields.append(fresh)
        probes.append(probe)
    values = {
        "adapter_id": S1_EC53_ADAPTER_ID,
        "source_contract_digest": contract.contract_digest,
        "plan_receipt_digests": tuple(x.receipt_digest for x in plans.values()),
        "formation_receipt_digests": tuple(x.receipt_digest for x in formations.values()),
        "fresh_field_receipt_digests": tuple(x.receipt_digest for x in fields),
        "probe_receipt_digests": tuple(x.receipt_digest for x in probes),
        "plan_receipt_count": len(plans),
        "formation_receipt_count": len(formations),
        "fresh_field_receipt_count": len(fields),
        "probe_receipt_count": len(probes),
        "all_plan_routes_exact": len(plans) == 6,
        "all_state_routes_exact": all(
            probe.selected_state_digest == (None if slot.state_role is None else formations[(slot.contact_count, slot.refinement_id, slot.state_role)].output_state_digest)
            for slot, probe in zip(contract.slot_bindings, probes, strict=True)
        ),
        "all_fresh_fields_identical_and_object_separate": len({x.initial_field_digest for x in fields}) == 1 and len({x.field_object_token for x in fields}) == 48,
        "all_probe_routes_exact": all(
            (probe.probe_kernel, probe.backreaction_enabled) == (slot.probe_kernel, slot.backreaction_enabled)
            for slot, probe in zip(contract.slot_bindings, probes, strict=True)
        ),
        "field_steps_executed": sum(x.field_steps_executed for x in (*plans.values(), *formations.values(), *fields, *probes)),
        "typed_real_adapter_implemented": True,
        "real_kernel_execution_permitted": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeTypedRealAdapterFixtureResult(**values, result_digest=_digest(values))
