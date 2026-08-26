"""S1-EC57 zero-step fixture for the bounded n2/r2 eight-role runner."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_real_binding_contract import E1CommonProbeRealBindingContract
from .e1_common_probe_small_real_result_audit import E1CommonProbeSmallRealResultAudit
from .e1_common_probe_typed_real_adapter_fixture import (
    E1RealFormationReceipt,
    E1RealFreshFieldReceipt,
    E1RealPlanReceipt,
    E1RealProbeReceipt,
    _formation_kernel,
    _fresh_field_kernel,
    _plan_kernel,
    _probe_kernel,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeN2R2RunnerFixtureError(ValueError):
    """Raised when EC57 leaves n2/r2, executes, or decides evidence."""


S1_EC57_RUNNER_ID = "e1.common-probe-n2-r2-runner.s1ec57.v1"
S1_EC57_EC52_CONTRACT_DIGEST = (
    "291ea70c96ad26b3f6e696588ebd55d3e6f7163967b45de9a689bd731cb7bf7b"
)
S1_EC57_EC56_AUDIT_DIGEST = (
    "959703db814d753744de67de65c216365ced4761fdfeb5f874916c94cba0340d"
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2RunnerFixtureResult:
    runner_id: str
    source_contract_digest: str
    source_audit_digest: str
    contact_count: int
    refinement_id: str
    roles: tuple[str, ...]
    plan_receipt_digest: str
    formation_receipt_digests: tuple[str, ...]
    fresh_field_receipt_digests: tuple[str, ...]
    probe_receipt_digests: tuple[str, ...]
    formation_state_count: int
    probe_slot_count: int
    planned_formation_steps: int
    planned_probe_steps: int
    planned_total_steps: int
    executed_field_steps: int
    all_state_routes_exact: bool
    all_probe_routes_exact: bool
    all_fresh_fields_identical_and_separate: bool
    bounded_runner_implemented: bool
    real_execution_permitted: bool
    ec46_decision_permitted: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.runner_id != S1_EC57_RUNNER_ID
            or self.source_contract_digest != S1_EC57_EC52_CONTRACT_DIGEST
            or self.source_audit_digest != S1_EC57_EC56_AUDIT_DIGEST
            or (self.contact_count, self.refinement_id) != (2, "r2")
            or self.roles != S1_EC45_PROBE_ROLES
            or len(self.plan_receipt_digest) != 64
            or len(self.formation_receipt_digests) != 4
            or len(self.fresh_field_receipt_digests) != 8
            or len(self.probe_receipt_digests) != 8
            or (self.formation_state_count, self.probe_slot_count) != (4, 8)
            or self.planned_formation_steps != 1608
            or self.planned_probe_steps != 1600
            or self.planned_total_steps != 3208
            or self.executed_field_steps != 0
            or any(value is not True for value in (
                self.all_state_routes_exact,
                self.all_probe_routes_exact,
                self.all_fresh_fields_identical_and_separate,
                self.bounded_runner_implemented,
            ))
            or any(value is not False for value in (
                self.real_execution_permitted,
                self.ec46_decision_permitted,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
        ):
            raise E1CommonProbeN2R2RunnerFixtureError(
                "S1-EC57 result changed or crossed zero-step scope"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "result_digest"}
        if self.result_digest != _digest(payload):
            raise E1CommonProbeN2R2RunnerFixtureError(
                "S1-EC57 result digest changed"
            )


PlanKernel = Callable[[int, str, str], E1RealPlanReceipt]
FormationKernel = Callable[[int, str, str, E1RealPlanReceipt], E1RealFormationReceipt]
FreshKernel = Callable[[object], E1RealFreshFieldReceipt]
ProbeKernel = Callable[[object, E1RealFreshFieldReceipt, str | None], E1RealProbeReceipt]


def run_e1_common_probe_n2_r2_runner_fixture(
    contract: E1CommonProbeRealBindingContract,
    audit: E1CommonProbeSmallRealResultAudit,
    *,
    plan_kernel: PlanKernel = _plan_kernel,
    formation_kernel: FormationKernel = _formation_kernel,
    fresh_field_kernel: FreshKernel = _fresh_field_kernel,
    probe_kernel: ProbeKernel = _probe_kernel,
) -> E1CommonProbeN2R2RunnerFixtureResult:
    """Wire only the eight n2/r2 slots through injected zero-step kernels."""

    if not isinstance(contract, E1CommonProbeRealBindingContract) or not isinstance(audit, E1CommonProbeSmallRealResultAudit):
        raise E1CommonProbeN2R2RunnerFixtureError("S1-EC57 requires typed EC52 and EC56 inputs")
    contract.__post_init__()
    audit.__post_init__()
    if contract.contract_digest != S1_EC57_EC52_CONTRACT_DIGEST or audit.audit_digest != S1_EC57_EC56_AUDIT_DIGEST or audit.next_fixture_implementation_permitted is not True or audit.next_fixture_execution_permitted is not False or not all(callable(x) for x in (plan_kernel, formation_kernel, fresh_field_kernel, probe_kernel)):
        raise E1CommonProbeN2R2RunnerFixtureError("S1-EC57 upstream binding or kernel changed")
    slots = tuple(
        item for item in contract.slot_bindings
        if (item.contact_count, item.refinement_id) == (2, "r2")
    )
    if tuple(item.role_id for item in slots) != S1_EC45_PROBE_ROLES:
        raise E1CommonProbeN2R2RunnerFixtureError("S1-EC57 n2/r2 slot order changed")
    plan = plan_kernel(2, "r2", contract.probe_source_digest)
    if not isinstance(plan, E1RealPlanReceipt):
        raise E1CommonProbeN2R2RunnerFixtureError("S1-EC57 plan receipt is untyped")
    plan.__post_init__()
    formations = {}
    for state_role in contract.formation_state_roles:
        receipt = formation_kernel(2, "r2", state_role, plan)
        if not isinstance(receipt, E1RealFormationReceipt) or receipt.state_role != state_role:
            raise E1CommonProbeN2R2RunnerFixtureError("S1-EC57 formation receipt changed")
        receipt.__post_init__()
        formations[state_role] = receipt
    fields = []
    probes = []
    for slot in slots:
        fresh = fresh_field_kernel(slot)
        if not isinstance(fresh, E1RealFreshFieldReceipt) or fresh.slot_binding_digest != slot.binding_digest:
            raise E1CommonProbeN2R2RunnerFixtureError("S1-EC57 fresh-field receipt changed")
        fresh.__post_init__()
        state_digest = None if slot.state_role is None else formations[slot.state_role].output_state_digest
        probe = probe_kernel(slot, fresh, state_digest)
        if not isinstance(probe, E1RealProbeReceipt) or probe.slot_binding_digest != slot.binding_digest:
            raise E1CommonProbeN2R2RunnerFixtureError("S1-EC57 probe receipt changed")
        probe.__post_init__()
        fields.append(fresh)
        probes.append(probe)
    values = {
        "runner_id": S1_EC57_RUNNER_ID,
        "source_contract_digest": contract.contract_digest,
        "source_audit_digest": audit.audit_digest,
        "contact_count": 2,
        "refinement_id": "r2",
        "roles": S1_EC45_PROBE_ROLES,
        "plan_receipt_digest": plan.receipt_digest,
        "formation_receipt_digests": tuple(x.receipt_digest for x in formations.values()),
        "fresh_field_receipt_digests": tuple(x.receipt_digest for x in fields),
        "probe_receipt_digests": tuple(x.receipt_digest for x in probes),
        "formation_state_count": len(formations),
        "probe_slot_count": len(probes),
        "planned_formation_steps": audit.next_formation_step_count,
        "planned_probe_steps": audit.next_probe_step_count,
        "planned_total_steps": audit.next_total_field_steps,
        "executed_field_steps": sum(x.field_steps_executed for x in (*formations.values(), *fields, *probes)),
        "all_state_routes_exact": all(
            probe.selected_state_digest == (None if slot.state_role is None else formations[slot.state_role].output_state_digest)
            for slot, probe in zip(slots, probes, strict=True)
        ),
        "all_probe_routes_exact": all(
            (probe.probe_kernel, probe.backreaction_enabled) == (slot.probe_kernel, slot.backreaction_enabled)
            for slot, probe in zip(slots, probes, strict=True)
        ),
        "all_fresh_fields_identical_and_separate": len({x.initial_field_digest for x in fields}) == 1 and len({x.field_object_token for x in fields}) == 8,
        "bounded_runner_implemented": True,
        "real_execution_permitted": False,
        "ec46_decision_permitted": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeN2R2RunnerFixtureResult(**values, result_digest=_digest(values))
