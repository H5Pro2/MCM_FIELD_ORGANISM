"""S1-EC61 zero-step fixture for the n2/r2 execution coordinator."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .e1_common_probe_n2_r2_object_handoff import E1CommonProbeN2R2ObjectHandoff
from .e1_common_probe_real_binding_contract import E1CommonProbeRealSlotBinding
from .e1_common_probe_real_wrappers import (
    E1CommonProbeFreshField,
    E1CommonProbeResolvedSlot,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest, _state_payload
from .shared_mcm_field import SharedMCMField


class E1CommonProbeN2R2ExecutionCoordinatorFixtureError(ValueError):
    """Raised when EC61 changes routing or crosses zero-step scope."""


S1_EC61_COORDINATOR_ID = "e1.common-probe-n2-r2-execution-coordinator.s1ec61.v1"
S1_EC61_EC59_HANDOFF_DIGEST = (
    "5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb"
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1CoordinatorFormationReceipt:
    state_role: str
    output_state: E1LocalEdgePlasticityState = field(repr=False, compare=False)
    output_state_digest: str
    field_steps_executed: int
    receipt_digest: str

    def __post_init__(self) -> None:
        values = {
            "state_role": self.state_role,
            "output_state_digest": self.output_state_digest,
            "field_steps_executed": self.field_steps_executed,
        }
        if (
            not self.state_role
            or not isinstance(self.output_state, E1LocalEdgePlasticityState)
            or self.output_state_digest != _digest(_state_payload(self.output_state))
            or self.field_steps_executed != 0
            or self.receipt_digest != _digest(values)
        ):
            raise E1CommonProbeN2R2ExecutionCoordinatorFixtureError(
                "S1-EC61 formation receipt crossed zero-step scope"
            )


@dataclass(frozen=True, slots=True)
class E1CoordinatorProbeReceipt:
    binding_digest: str
    selected_state_digest: str | None
    backreaction_enabled: bool
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    field_steps_executed: int
    receipt_digest: str

    def __post_init__(self) -> None:
        values = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if (
            not _valid_digest(self.binding_digest)
            or (self.selected_state_digest is not None and not _valid_digest(self.selected_state_digest))
            or not isinstance(self.backreaction_enabled, bool)
            or not self.activation
            or len(self.activation) != len(self.afterimage)
            or self.field_steps_executed != 0
            or self.receipt_digest != _digest(values)
        ):
            raise E1CommonProbeN2R2ExecutionCoordinatorFixtureError(
                "S1-EC61 probe receipt crossed zero-step scope"
            )


FormationKernel = Callable[
    [E1CommonProbeResolvedSlot, SharedMCMField, E1LocalEdgePlasticityState],
    E1CoordinatorFormationReceipt,
]
FreshFieldKernel = Callable[
    [E1CommonProbeRealSlotBinding, SharedMCMField],
    E1CommonProbeFreshField,
]
ProbeKernel = Callable[
    [E1CommonProbeResolvedSlot, E1CommonProbeFreshField, E1LocalEdgePlasticityState | None],
    E1CoordinatorProbeReceipt,
]


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2ExecutionCoordinatorFixtureResult:
    coordinator_id: str
    source_handoff_digest: str
    roles: tuple[str, ...]
    formation_state_roles: tuple[str, ...]
    formation_receipt_digests: tuple[str, ...]
    probe_receipt_digests: tuple[str, ...]
    formation_count: int
    fresh_field_count: int
    probe_count: int
    all_formation_states_object_separate: bool
    all_fresh_fields_identical_and_object_separate: bool
    all_state_routes_exact: bool
    all_backreaction_routes_exact: bool
    field_steps_executed: int
    real_wrapper_binding_permitted: bool
    real_wrapper_execution_permitted: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str
    formations: tuple[E1CoordinatorFormationReceipt, ...] = field(repr=False, compare=False)
    fresh_fields: tuple[E1CommonProbeFreshField, ...] = field(repr=False, compare=False)
    probes: tuple[E1CoordinatorProbeReceipt, ...] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        metadata = _result_metadata(self)
        if (
            self.coordinator_id != S1_EC61_COORDINATOR_ID
            or self.source_handoff_digest != S1_EC61_EC59_HANDOFF_DIGEST
            or (self.formation_count, self.fresh_field_count, self.probe_count) != (4, 8, 8)
            or len(self.formation_receipt_digests) != 4
            or len(self.probe_receipt_digests) != 8
            or self.formation_receipt_digests != tuple(item.receipt_digest for item in self.formations)
            or self.probe_receipt_digests != tuple(item.receipt_digest for item in self.probes)
            or any(value is not True for value in (
                self.all_formation_states_object_separate,
                self.all_fresh_fields_identical_and_object_separate,
                self.all_state_routes_exact,
                self.all_backreaction_routes_exact,
                self.real_wrapper_binding_permitted,
            ))
            or self.field_steps_executed != 0
            or any(value is not False for value in (
                self.real_wrapper_execution_permitted,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.result_digest != _digest(metadata)
        ):
            raise E1CommonProbeN2R2ExecutionCoordinatorFixtureError(
                "S1-EC61 result changed or crossed zero-step scope"
            )


def _result_metadata(
    result: E1CommonProbeN2R2ExecutionCoordinatorFixtureResult,
) -> dict[str, object]:
    return {
        name: getattr(result, name)
        for name in (
            "coordinator_id",
            "source_handoff_digest",
            "roles",
            "formation_state_roles",
            "formation_receipt_digests",
            "probe_receipt_digests",
            "formation_count",
            "fresh_field_count",
            "probe_count",
            "all_formation_states_object_separate",
            "all_fresh_fields_identical_and_object_separate",
            "all_state_routes_exact",
            "all_backreaction_routes_exact",
            "field_steps_executed",
            "real_wrapper_binding_permitted",
            "real_wrapper_execution_permitted",
            "persistence_performed",
            "research_decision_permitted",
            "memory_claim_permitted",
        )
    }


def run_e1_common_probe_n2_r2_execution_coordinator_fixture(
    handoff: E1CommonProbeN2R2ObjectHandoff,
    *,
    formation_kernel: FormationKernel,
    fresh_field_kernel: FreshFieldKernel,
    probe_kernel: ProbeKernel,
) -> E1CommonProbeN2R2ExecutionCoordinatorFixtureResult:
    """Coordinate four formations and eight probes through zero-step doubles."""

    if (
        not isinstance(handoff, E1CommonProbeN2R2ObjectHandoff)
        or handoff.handoff_digest != S1_EC61_EC59_HANDOFF_DIGEST
        or not all(callable(item) for item in (formation_kernel, fresh_field_kernel, probe_kernel))
    ):
        raise E1CommonProbeN2R2ExecutionCoordinatorFixtureError(
            "S1-EC61 requires EC59 and three injected kernels"
        )
    handoff.__post_init__()
    formations = tuple(
        formation_kernel(slot, handoff.initial_field, handoff.initial_state)
        for slot in handoff.formation_slots
    )
    if any(
        not isinstance(receipt, E1CoordinatorFormationReceipt)
        or receipt.state_role != slot.binding.state_role
        for receipt, slot in zip(formations, handoff.formation_slots, strict=True)
    ):
        raise E1CommonProbeN2R2ExecutionCoordinatorFixtureError(
            "S1-EC61 formation routing changed"
        )
    states = {item.state_role: item for item in formations}
    fresh_fields = []
    probes = []
    selected_states = []
    for slot in handoff.resolved_slots:
        fresh = fresh_field_kernel(slot.binding, handoff.initial_field)
        if (
            not isinstance(fresh, E1CommonProbeFreshField)
            or fresh.binding_digest != slot.binding.binding_digest
            or fresh.initial_field_digest != handoff.initial_field_digest
        ):
            raise E1CommonProbeN2R2ExecutionCoordinatorFixtureError(
                "S1-EC61 fresh-field routing changed"
            )
        selected = None if slot.binding.state_role is None else states[slot.binding.state_role]
        state = None if selected is None else selected.output_state
        probe = probe_kernel(slot, fresh, state)
        if (
            not isinstance(probe, E1CoordinatorProbeReceipt)
            or probe.binding_digest != slot.binding.binding_digest
            or probe.selected_state_digest != (None if selected is None else selected.output_state_digest)
            or probe.backreaction_enabled is not slot.binding.backreaction_enabled
        ):
            raise E1CommonProbeN2R2ExecutionCoordinatorFixtureError(
                "S1-EC61 probe routing changed"
            )
        fresh_fields.append(fresh)
        probes.append(probe)
        selected_states.append(state)
    initial_digests = {_initial_field_digest(item.field) for item in fresh_fields}
    values = {
        "coordinator_id": S1_EC61_COORDINATOR_ID,
        "source_handoff_digest": handoff.handoff_digest,
        "roles": handoff.roles,
        "formation_state_roles": handoff.formation_state_roles,
        "formation_receipt_digests": tuple(item.receipt_digest for item in formations),
        "probe_receipt_digests": tuple(item.receipt_digest for item in probes),
        "formation_count": len(formations),
        "fresh_field_count": len(fresh_fields),
        "probe_count": len(probes),
        "all_formation_states_object_separate": len({id(item.output_state) for item in formations}) == 4,
        "all_fresh_fields_identical_and_object_separate": initial_digests == {handoff.initial_field_digest} and len({id(item.field) for item in fresh_fields}) == 8,
        "all_state_routes_exact": all(
            state is (None if slot.binding.state_role is None else states[slot.binding.state_role].output_state)
            for slot, state in zip(handoff.resolved_slots, selected_states, strict=True)
        ),
        "all_backreaction_routes_exact": all(
            probe.backreaction_enabled is slot.binding.backreaction_enabled
            for slot, probe in zip(handoff.resolved_slots, probes, strict=True)
        ),
        "field_steps_executed": sum(item.field_steps_executed for item in (*formations, *probes)),
        "real_wrapper_binding_permitted": True,
        "real_wrapper_execution_permitted": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeN2R2ExecutionCoordinatorFixtureResult(
        **values,
        result_digest=_digest(values),
        formations=formations,
        fresh_fields=tuple(fresh_fields),
        probes=tuple(probes),
    )
