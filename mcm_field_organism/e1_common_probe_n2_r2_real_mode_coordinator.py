"""S1-EC67 unreleased real-mode coordinator for the bounded n2/r2 run."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
import inspect

from .e1_common_probe_n2_r2_object_handoff import E1CommonProbeN2R2ObjectHandoff
from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    E1PositiveStepFormationReceipt,
    E1PositiveStepProbeReceipt,
    S1_EC63_ROLE_STATE_ROUTES,
)
from .e1_common_probe_n2_r2_real_call_adapters import (
    build_e1_common_probe_real_fresh_field_adapter,
    run_e1_common_probe_real_formation_receipt_adapter,
    run_e1_common_probe_real_probe_receipt_adapter,
)
from .e1_common_probe_real_binding_contract import E1CommonProbeRealSlotBinding
from .e1_common_probe_real_wrappers import (
    E1CommonProbeFreshField,
    E1CommonProbeResolvedSlot,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest
from .shared_mcm_field import SharedMCMField


class E1CommonProbeN2R2RealModeCoordinatorError(ValueError):
    """Raised when EC67 is unreleased or leaves its exact real-mode scope."""


S1_EC67_COORDINATOR_ID = "e1.common-probe-n2-r2-real-mode-coordinator.s1ec67.v1"
S1_EC67_AUDIT_ID = "e1.common-probe-n2-r2-real-mode-coordinator-audit.s1ec67.v1"
S1_EC67_EC59_HANDOFF_DIGEST = (
    "5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb"
)
S1_EC67_EC65_AUDIT_DIGEST = (
    "dba7a309bf49dfb57881883a049c80d7c58ea5a98f74ef0744167b2a26d718af"
)
S1_EC67_EC66_FIXTURE_DIGEST = (
    "bc07f3059139ef40a364f5fdbc61787aa68ca63722c26039410fee593e2359a7"
)


FormationAdapter = Callable[
    [E1CommonProbeResolvedSlot, SharedMCMField, E1LocalEdgePlasticityState],
    E1PositiveStepFormationReceipt,
]
FreshFieldAdapter = Callable[
    [E1CommonProbeRealSlotBinding, SharedMCMField],
    E1CommonProbeFreshField,
]
ProbeAdapter = Callable[
    [E1CommonProbeResolvedSlot, E1CommonProbeFreshField, E1PositiveStepFormationReceipt | None],
    E1PositiveStepProbeReceipt,
]


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2RealModeCoordinatorResult:
    coordinator_id: str
    source_handoff_digest: str
    source_ec65_audit_digest: str
    source_ec66_fixture_digest: str
    execution_mode: str
    roles: tuple[str, ...]
    formation_state_roles: tuple[str, ...]
    formation_receipt_digests: tuple[str, ...]
    probe_receipt_digests: tuple[str, ...]
    formation_count: int
    fresh_field_count: int
    probe_count: int
    accounted_formation_steps: int
    accounted_probe_steps: int
    accounted_total_steps: int
    actual_field_steps_executed: int
    all_state_routes_exact: bool
    all_backreaction_routes_exact: bool
    all_fresh_fields_identical_and_object_separate: bool
    all_formation_states_object_separate: bool
    preflight_and_owner_released: bool
    persistence_performed: bool
    research_decision_permitted: bool
    ec46_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str
    formations: tuple[E1PositiveStepFormationReceipt, ...] = field(repr=False, compare=False)
    fresh_fields: tuple[E1CommonProbeFreshField, ...] = field(repr=False, compare=False)
    probes: tuple[E1PositiveStepProbeReceipt, ...] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        metadata = _result_metadata(self)
        if (
            self.coordinator_id != S1_EC67_COORDINATOR_ID
            or self.source_handoff_digest != S1_EC67_EC59_HANDOFF_DIGEST
            or self.source_ec65_audit_digest != S1_EC67_EC65_AUDIT_DIGEST
            or self.source_ec66_fixture_digest != S1_EC67_EC66_FIXTURE_DIGEST
            or self.execution_mode != "real-wrapper"
            or (self.formation_count, self.fresh_field_count, self.probe_count) != (4, 8, 8)
            or self.formation_receipt_digests != tuple(item.receipt_digest for item in self.formations)
            or self.probe_receipt_digests != tuple(item.receipt_digest for item in self.probes)
            or (self.accounted_formation_steps, self.accounted_probe_steps, self.accounted_total_steps) != (1608, 1600, 3208)
            or self.actual_field_steps_executed != 3208
            or any(value is not True for value in (
                self.all_state_routes_exact,
                self.all_backreaction_routes_exact,
                self.all_fresh_fields_identical_and_object_separate,
                self.all_formation_states_object_separate,
                self.preflight_and_owner_released,
            ))
            or any(value is not False for value in (
                self.persistence_performed,
                self.research_decision_permitted,
                self.ec46_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.result_digest != _digest(metadata)
        ):
            raise E1CommonProbeN2R2RealModeCoordinatorError(
                "S1-EC67 real result changed or crossed bounded scope"
            )


def _result_metadata(
    result: E1CommonProbeN2R2RealModeCoordinatorResult,
) -> dict[str, object]:
    return {
        name: getattr(result, name)
        for name in (
            "coordinator_id",
            "source_handoff_digest",
            "source_ec65_audit_digest",
            "source_ec66_fixture_digest",
            "execution_mode",
            "roles",
            "formation_state_roles",
            "formation_receipt_digests",
            "probe_receipt_digests",
            "formation_count",
            "fresh_field_count",
            "probe_count",
            "accounted_formation_steps",
            "accounted_probe_steps",
            "accounted_total_steps",
            "actual_field_steps_executed",
            "all_state_routes_exact",
            "all_backreaction_routes_exact",
            "all_fresh_fields_identical_and_object_separate",
            "all_formation_states_object_separate",
            "preflight_and_owner_released",
            "persistence_performed",
            "research_decision_permitted",
            "ec46_decision_permitted",
            "memory_claim_permitted",
        )
    }


def run_e1_common_probe_n2_r2_real_mode_coordinator(
    handoff: E1CommonProbeN2R2ObjectHandoff,
    *,
    preflight_and_owner_released: bool,
    formation_adapter: FormationAdapter = run_e1_common_probe_real_formation_receipt_adapter,
    fresh_field_adapter: FreshFieldAdapter = build_e1_common_probe_real_fresh_field_adapter,
    probe_adapter: ProbeAdapter = run_e1_common_probe_real_probe_receipt_adapter,
) -> E1CommonProbeN2R2RealModeCoordinatorResult:
    """Run the exact real 4/8 path only after an external one-shot release."""

    if preflight_and_owner_released is not True:
        raise E1CommonProbeN2R2RealModeCoordinatorError(
            "S1-EC67 requires preflight and explicit owner release"
        )
    if (
        not isinstance(handoff, E1CommonProbeN2R2ObjectHandoff)
        or handoff.handoff_digest != S1_EC67_EC59_HANDOFF_DIGEST
        or formation_adapter is not run_e1_common_probe_real_formation_receipt_adapter
        or fresh_field_adapter is not build_e1_common_probe_real_fresh_field_adapter
        or probe_adapter is not run_e1_common_probe_real_probe_receipt_adapter
    ):
        raise E1CommonProbeN2R2RealModeCoordinatorError(
            "S1-EC67 requires the exact EC59 handoff and EC65 adapters"
        )
    handoff.__post_init__()
    formations = tuple(
        formation_adapter(slot, handoff.initial_field, handoff.initial_state)
        for slot in handoff.formation_slots
    )
    if any(
        not isinstance(receipt, E1PositiveStepFormationReceipt)
        or receipt.state_role != slot.binding.state_role
        or receipt.execution_mode != "real-wrapper"
        for receipt, slot in zip(formations, handoff.formation_slots, strict=True)
    ):
        raise E1CommonProbeN2R2RealModeCoordinatorError(
            "S1-EC67 formation adapter route or mode changed"
        )
    states = {item.state_role: item for item in formations}
    routes = dict(S1_EC63_ROLE_STATE_ROUTES)
    fresh_fields = []
    probes = []
    for slot in handoff.resolved_slots:
        fresh = fresh_field_adapter(slot.binding, handoff.initial_field)
        if (
            not isinstance(fresh, E1CommonProbeFreshField)
            or fresh.binding_digest != slot.binding.binding_digest
            or fresh.initial_field_digest != handoff.initial_field_digest
        ):
            raise E1CommonProbeN2R2RealModeCoordinatorError(
                "S1-EC67 fresh-field adapter route changed"
            )
        state_role = routes[slot.binding.role_id]
        formation = None if state_role is None else states[state_role]
        probe = probe_adapter(slot, fresh, formation)
        expected_digest = None if formation is None else formation.output_state_digest
        if (
            not isinstance(probe, E1PositiveStepProbeReceipt)
            or probe.role_id != slot.binding.role_id
            or probe.binding_digest != slot.binding.binding_digest
            or probe.selected_state_role != state_role
            or probe.selected_state_digest != expected_digest
            or probe.backreaction_enabled is not slot.binding.backreaction_enabled
            or probe.execution_mode != "real-wrapper"
        ):
            raise E1CommonProbeN2R2RealModeCoordinatorError(
                "S1-EC67 probe adapter route or mode changed"
            )
        fresh_fields.append(fresh)
        probes.append(probe)
    initial_digests = {_initial_field_digest(item.field) for item in fresh_fields}
    formation_steps = sum(item.accounted_field_steps for item in formations)
    probe_steps = sum(item.accounted_field_steps for item in probes)
    values = {
        "coordinator_id": S1_EC67_COORDINATOR_ID,
        "source_handoff_digest": handoff.handoff_digest,
        "source_ec65_audit_digest": S1_EC67_EC65_AUDIT_DIGEST,
        "source_ec66_fixture_digest": S1_EC67_EC66_FIXTURE_DIGEST,
        "execution_mode": "real-wrapper",
        "roles": handoff.roles,
        "formation_state_roles": handoff.formation_state_roles,
        "formation_receipt_digests": tuple(item.receipt_digest for item in formations),
        "probe_receipt_digests": tuple(item.receipt_digest for item in probes),
        "formation_count": len(formations),
        "fresh_field_count": len(fresh_fields),
        "probe_count": len(probes),
        "accounted_formation_steps": formation_steps,
        "accounted_probe_steps": probe_steps,
        "accounted_total_steps": formation_steps + probe_steps,
        "actual_field_steps_executed": formation_steps + probe_steps,
        "all_state_routes_exact": all(
            probe.selected_state_role == routes[slot.binding.role_id]
            for slot, probe in zip(handoff.resolved_slots, probes, strict=True)
        ),
        "all_backreaction_routes_exact": all(
            probe.backreaction_enabled is slot.binding.backreaction_enabled
            for slot, probe in zip(handoff.resolved_slots, probes, strict=True)
        ),
        "all_fresh_fields_identical_and_object_separate": initial_digests == {handoff.initial_field_digest} and len({id(item.field) for item in fresh_fields}) == 8,
        "all_formation_states_object_separate": len({id(item.output_state) for item in formations}) == 4,
        "preflight_and_owner_released": True,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "ec46_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeN2R2RealModeCoordinatorResult(
        **values,
        result_digest=_digest(values),
        formations=formations,
        fresh_fields=tuple(fresh_fields),
        probes=tuple(probes),
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2RealModeCoordinatorAudit:
    audit_id: str
    source_ec65_audit_digest: str
    source_ec66_fixture_digest: str
    checks: tuple[tuple[str, bool], ...]
    real_mode_coordinator_implemented: bool
    preflight_required_before_adapter_calls: bool
    new_real_preflight_permitted: bool
    coordinator_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.audit_id != S1_EC67_AUDIT_ID
            or self.source_ec65_audit_digest != S1_EC67_EC65_AUDIT_DIGEST
            or self.source_ec66_fixture_digest != S1_EC67_EC66_FIXTURE_DIGEST
            or any(value is not True for _, value in self.checks)
            or any(value is not True for value in (
                self.real_mode_coordinator_implemented,
                self.preflight_required_before_adapter_calls,
                self.new_real_preflight_permitted,
            ))
            or any(value is not False for value in (
                self.coordinator_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision != "REAL_MODE_COORDINATOR_IMPLEMENTED_NOT_PREFLIGHTED_NOT_RELEASED"
        ):
            raise E1CommonProbeN2R2RealModeCoordinatorError(
                "S1-EC67 audit changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1CommonProbeN2R2RealModeCoordinatorError(
                "S1-EC67 audit digest changed"
            )


def audit_e1_common_probe_n2_r2_real_mode_coordinator(
) -> E1CommonProbeN2R2RealModeCoordinatorAudit:
    """Audit real coordinator source without invoking it or any adapter."""

    source = inspect.getsource(run_e1_common_probe_n2_r2_real_mode_coordinator)
    release_guard = source.find("if preflight_and_owner_released is not True:")
    first_adapter_call = source.find("formation_adapter(")
    checks = (
        ("release-guard-precedes-all-adapter-calls", 0 <= release_guard < first_adapter_call),
        ("exact-ec65-adapter-identities-required", all(token in source for token in ("formation_adapter is not run_e1_common_probe_real_formation_receipt_adapter", "fresh_field_adapter is not build_e1_common_probe_real_fresh_field_adapter", "probe_adapter is not run_e1_common_probe_real_probe_receipt_adapter"))),
        ("real-wrapper-mode-required-for-formation-and-probe", source.count('execution_mode != "real-wrapper"') == 2),
        ("exact-positive-step-accounting-returned", '"actual_field_steps_executed": formation_steps + probe_steps' in source),
        ("no-persistence-decision-or-claim", all(token in source for token in ('"persistence_performed": False', '"research_decision_permitted": False', '"ec46_decision_permitted": False', '"memory_claim_permitted": False'))),
        ("coordinator-has-no-write-path", all(token not in source for token in ("write_text", "write_bytes", "open("))),
    )
    values = {
        "audit_id": S1_EC67_AUDIT_ID,
        "source_ec65_audit_digest": S1_EC67_EC65_AUDIT_DIGEST,
        "source_ec66_fixture_digest": S1_EC67_EC66_FIXTURE_DIGEST,
        "checks": checks,
        "real_mode_coordinator_implemented": True,
        "preflight_required_before_adapter_calls": True,
        "new_real_preflight_permitted": True,
        "coordinator_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "REAL_MODE_COORDINATOR_IMPLEMENTED_NOT_PREFLIGHTED_NOT_RELEASED",
    }
    return E1CommonProbeN2R2RealModeCoordinatorAudit(
        **values,
        audit_digest=_digest(values),
    )
