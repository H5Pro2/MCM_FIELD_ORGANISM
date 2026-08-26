"""S1-EC66 synthetic positive-step coordinator for the bounded n2/r2 run."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .e1_common_probe_n2_r2_object_handoff import E1CommonProbeN2R2ObjectHandoff
from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    E1PositiveStepFormationReceipt,
    E1PositiveStepProbeReceipt,
    S1_EC63_ROLE_STATE_ROUTES,
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


class E1CommonProbeN2R2PositiveStepCoordinatorFixtureError(ValueError):
    """Raised when EC66 changes routes, accounting, or synthetic scope."""


S1_EC66_COORDINATOR_ID = "e1.common-probe-n2-r2-positive-step-coordinator.s1ec66.v1"
S1_EC66_EC59_HANDOFF_DIGEST = (
    "5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb"
)
S1_EC66_EC63_FIXTURE_DIGEST = (
    "a1dce7d6ee522f5953556bc7ae4b090a21687bece3c23ac07bbc81f68fda400a"
)


FormationKernel = Callable[
    [E1CommonProbeResolvedSlot, SharedMCMField, E1LocalEdgePlasticityState],
    E1PositiveStepFormationReceipt,
]
FreshFieldKernel = Callable[
    [E1CommonProbeRealSlotBinding, SharedMCMField],
    E1CommonProbeFreshField,
]
ProbeKernel = Callable[
    [E1CommonProbeResolvedSlot, E1CommonProbeFreshField, E1PositiveStepFormationReceipt | None],
    E1PositiveStepProbeReceipt,
]


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2PositiveStepCoordinatorFixtureResult:
    coordinator_id: str
    source_handoff_digest: str
    source_ec63_fixture_digest: str
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
    real_adapter_binding_permitted: bool
    real_adapter_execution_permitted: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str
    formations: tuple[E1PositiveStepFormationReceipt, ...] = field(repr=False, compare=False)
    fresh_fields: tuple[E1CommonProbeFreshField, ...] = field(repr=False, compare=False)
    probes: tuple[E1PositiveStepProbeReceipt, ...] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        metadata = _result_metadata(self)
        if (
            self.coordinator_id != S1_EC66_COORDINATOR_ID
            or self.source_handoff_digest != S1_EC66_EC59_HANDOFF_DIGEST
            or self.source_ec63_fixture_digest != S1_EC66_EC63_FIXTURE_DIGEST
            or self.execution_mode != "synthetic-contract"
            or (self.formation_count, self.fresh_field_count, self.probe_count) != (4, 8, 8)
            or self.formation_receipt_digests != tuple(item.receipt_digest for item in self.formations)
            or self.probe_receipt_digests != tuple(item.receipt_digest for item in self.probes)
            or (self.accounted_formation_steps, self.accounted_probe_steps, self.accounted_total_steps) != (1608, 1600, 3208)
            or self.actual_field_steps_executed != 0
            or any(value is not True for value in (
                self.all_state_routes_exact,
                self.all_backreaction_routes_exact,
                self.all_fresh_fields_identical_and_object_separate,
                self.real_adapter_binding_permitted,
            ))
            or any(value is not False for value in (
                self.real_adapter_execution_permitted,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.result_digest != _digest(metadata)
        ):
            raise E1CommonProbeN2R2PositiveStepCoordinatorFixtureError(
                "S1-EC66 result changed or crossed synthetic scope"
            )


def _result_metadata(
    result: E1CommonProbeN2R2PositiveStepCoordinatorFixtureResult,
) -> dict[str, object]:
    return {
        name: getattr(result, name)
        for name in (
            "coordinator_id",
            "source_handoff_digest",
            "source_ec63_fixture_digest",
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
            "real_adapter_binding_permitted",
            "real_adapter_execution_permitted",
            "persistence_performed",
            "research_decision_permitted",
            "memory_claim_permitted",
        )
    }


def run_e1_common_probe_n2_r2_positive_step_coordinator_fixture(
    handoff: E1CommonProbeN2R2ObjectHandoff,
    *,
    source_ec63_fixture_digest: str,
    formation_kernel: FormationKernel,
    fresh_field_kernel: FreshFieldKernel,
    probe_kernel: ProbeKernel,
) -> E1CommonProbeN2R2PositiveStepCoordinatorFixtureResult:
    """Coordinate positive synthetic receipts without invoking real adapters."""

    if (
        not isinstance(handoff, E1CommonProbeN2R2ObjectHandoff)
        or handoff.handoff_digest != S1_EC66_EC59_HANDOFF_DIGEST
        or source_ec63_fixture_digest != S1_EC66_EC63_FIXTURE_DIGEST
        or not all(callable(item) for item in (formation_kernel, fresh_field_kernel, probe_kernel))
    ):
        raise E1CommonProbeN2R2PositiveStepCoordinatorFixtureError(
            "S1-EC66 requires EC59, EC63, and three injected kernels"
        )
    handoff.__post_init__()
    formations = tuple(
        formation_kernel(slot, handoff.initial_field, handoff.initial_state)
        for slot in handoff.formation_slots
    )
    if any(
        not isinstance(receipt, E1PositiveStepFormationReceipt)
        or receipt.state_role != slot.binding.state_role
        or receipt.execution_mode != "synthetic-contract"
        for receipt, slot in zip(formations, handoff.formation_slots, strict=True)
    ):
        raise E1CommonProbeN2R2PositiveStepCoordinatorFixtureError(
            "S1-EC66 formation receipt route or mode changed"
        )
    states = {item.state_role: item for item in formations}
    routes = dict(S1_EC63_ROLE_STATE_ROUTES)
    fresh_fields = []
    probes = []
    for slot in handoff.resolved_slots:
        fresh = fresh_field_kernel(slot.binding, handoff.initial_field)
        if (
            not isinstance(fresh, E1CommonProbeFreshField)
            or fresh.binding_digest != slot.binding.binding_digest
            or fresh.initial_field_digest != handoff.initial_field_digest
        ):
            raise E1CommonProbeN2R2PositiveStepCoordinatorFixtureError(
                "S1-EC66 fresh-field route changed"
            )
        state_role = routes[slot.binding.role_id]
        formation = None if state_role is None else states[state_role]
        probe = probe_kernel(slot, fresh, formation)
        expected_digest = None if formation is None else formation.output_state_digest
        if (
            not isinstance(probe, E1PositiveStepProbeReceipt)
            or probe.role_id != slot.binding.role_id
            or probe.binding_digest != slot.binding.binding_digest
            or probe.selected_state_role != state_role
            or probe.selected_state_digest != expected_digest
            or probe.backreaction_enabled is not slot.binding.backreaction_enabled
            or probe.execution_mode != "synthetic-contract"
        ):
            raise E1CommonProbeN2R2PositiveStepCoordinatorFixtureError(
                "S1-EC66 probe receipt route or mode changed"
            )
        fresh_fields.append(fresh)
        probes.append(probe)
    initial_digests = {_initial_field_digest(item.field) for item in fresh_fields}
    values = {
        "coordinator_id": S1_EC66_COORDINATOR_ID,
        "source_handoff_digest": handoff.handoff_digest,
        "source_ec63_fixture_digest": source_ec63_fixture_digest,
        "execution_mode": "synthetic-contract",
        "roles": handoff.roles,
        "formation_state_roles": handoff.formation_state_roles,
        "formation_receipt_digests": tuple(item.receipt_digest for item in formations),
        "probe_receipt_digests": tuple(item.receipt_digest for item in probes),
        "formation_count": len(formations),
        "fresh_field_count": len(fresh_fields),
        "probe_count": len(probes),
        "accounted_formation_steps": sum(item.accounted_field_steps for item in formations),
        "accounted_probe_steps": sum(item.accounted_field_steps for item in probes),
        "accounted_total_steps": sum(item.accounted_field_steps for item in (*formations, *probes)),
        "actual_field_steps_executed": 0,
        "all_state_routes_exact": all(
            probe.selected_state_role == routes[slot.binding.role_id]
            for slot, probe in zip(handoff.resolved_slots, probes, strict=True)
        ),
        "all_backreaction_routes_exact": all(
            probe.backreaction_enabled is slot.binding.backreaction_enabled
            for slot, probe in zip(handoff.resolved_slots, probes, strict=True)
        ),
        "all_fresh_fields_identical_and_object_separate": initial_digests == {handoff.initial_field_digest} and len({id(item.field) for item in fresh_fields}) == 8,
        "real_adapter_binding_permitted": True,
        "real_adapter_execution_permitted": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeN2R2PositiveStepCoordinatorFixtureResult(
        **values,
        result_digest=_digest(values),
        formations=formations,
        fresh_fields=tuple(fresh_fields),
        probes=tuple(probes),
    )
