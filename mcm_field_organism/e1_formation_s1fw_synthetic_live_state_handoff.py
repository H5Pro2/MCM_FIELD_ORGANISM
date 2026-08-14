"""S1-FW synthetic live-state handoff for all ten common-probe roles."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import asdict, dataclass, field

from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
)
from .e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIPreparedInputs,
)
from .e1_formation_s1fj_synthetic_coordinator import (
    E1FormationS1FJSyntheticInventory,
)
from .e1_formation_s1fv_live_state_ten_role_contract import (
    E1FormationS1FVLiveStateTenRoleContract,
    E1FormationS1FVProbeSlotBinding,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_formation_runner import _digest, _state_payload
from .e1_weighted_field_adapter import (
    E1WeightedFieldAdapterResult,
    compute_e1_weighted_edge_rates,
)
from .neutral_local_field_substrate import NeutralLocalFieldSubstrateConfig


class E1FormationS1FWSyntheticLiveStateHandoffError(ValueError):
    """Raised when S1-FW loses identity, mutates state, or opens a field path."""


S1_FW_COORDINATOR_ID = "e1.synthetic-live-state-ten-role-handoff.s1fw.v1"
AdapterFactory = Callable[
    [object, E1LocalEdgePlasticityState, NeutralLocalFieldSubstrateConfig],
    E1WeightedFieldAdapterResult,
]


def _adapter_digest(adapter: E1WeightedFieldAdapterResult) -> str:
    return _digest(asdict(adapter))


@dataclass(frozen=True, slots=True)
class E1FormationS1FWLiveStateSource:
    refinement_id: str
    state_role: str
    formation_arm_id: str
    source_result: E1PreparedRealFormationArmResult = field(repr=False)
    state: E1LocalEdgePlasticityState = field(repr=False)
    state_digest: str
    source_digest: str

    def __post_init__(self) -> None:
        payload = {
            "refinement_id": self.refinement_id,
            "state_role": self.state_role,
            "formation_arm_id": self.formation_arm_id,
            "source_result_digest": self.source_result.result_digest,
            "state_digest": self.state_digest,
        }
        if (
            not isinstance(self.source_result, E1PreparedRealFormationArmResult)
            or not isinstance(self.state, E1LocalEdgePlasticityState)
            or self.source_result.refinement_id != self.refinement_id
            or self.source_result.arm_id != self.formation_arm_id
            or self.state is not self.source_result.output_state
            or self.state_digest != self.source_result.output_state_digest
            or self.state_digest != _digest(_state_payload(self.state))
            or self.source_digest != _digest(payload)
        ):
            raise E1FormationS1FWSyntheticLiveStateHandoffError(
                "S1-FW live-state source lost exact object identity"
            )


@dataclass(frozen=True, slots=True)
class E1FormationS1FWSyntheticSlotHandoff:
    binding: E1FormationS1FVProbeSlotBinding
    source: E1FormationS1FWLiveStateSource | None = field(repr=False)
    state: E1LocalEdgePlasticityState | None = field(repr=False)
    fixed_adapter: E1WeightedFieldAdapterResult | None = field(repr=False)
    state_digest: str | None
    fixed_adapter_digest: str | None
    state_object_identity_preserved: bool
    field_steps_executed: int
    handoff_digest: str

    def __post_init__(self) -> None:
        has_state = self.binding.live_state_object_required
        fixed = self.binding.fixed_adapter_derivation_required
        payload = {
            "binding_digest": self.binding.binding_digest,
            "source_digest": None if self.source is None else self.source.source_digest,
            "state_digest": self.state_digest,
            "fixed_adapter_digest": self.fixed_adapter_digest,
            "state_object_identity_preserved": self.state_object_identity_preserved,
            "field_steps_executed": self.field_steps_executed,
        }
        if (
            not isinstance(self.binding, E1FormationS1FVProbeSlotBinding)
            or (self.source is not None) is not has_state
            or (self.state is not None) is not has_state
            or (self.fixed_adapter is not None) is not fixed
            or (self.fixed_adapter_digest is not None) is not fixed
            or (self.state_digest is not None) is not has_state
            or self.state_object_identity_preserved is not True
            or self.field_steps_executed != 0
            or self.handoff_digest != _digest(payload)
        ):
            raise E1FormationS1FWSyntheticLiveStateHandoffError(
                "S1-FW slot handoff changed or contains field execution"
            )
        if has_state and (
            self.state is not self.source.state  # type: ignore[union-attr]
            or self.state_digest != self.source.state_digest  # type: ignore[union-attr]
        ):
            raise E1FormationS1FWSyntheticLiveStateHandoffError(
                "S1-FW slot did not receive the exact live state object"
            )
        if fixed and (
            self.fixed_adapter_digest != _adapter_digest(self.fixed_adapter)  # type: ignore[arg-type]
            or self.fixed_adapter.backreaction_enabled is not True  # type: ignore[union-attr]
        ):
            raise E1FormationS1FWSyntheticLiveStateHandoffError(
                "S1-FW fixed adapter derivation changed"
            )


@dataclass(frozen=True, slots=True)
class E1FormationS1FWSyntheticLiveStateHandoffResult:
    coordinator_id: str
    source_contract_digest: str
    source_inventory_digest: str
    live_sources: tuple[E1FormationS1FWLiveStateSource, ...] = field(repr=False)
    slot_handoffs: tuple[E1FormationS1FWSyntheticSlotHandoff, ...] = field(repr=False)
    live_state_object_count: int
    unique_live_state_object_count: int
    slot_handoff_count: int
    state_consuming_slot_count: int
    p0_slot_count: int
    fixed_adapter_count: int
    usage_counts: tuple[tuple[str, str, int], ...]
    source_state_digests_preserved: bool
    exact_object_identity_preserved: bool
    all_routes_complete: bool
    field_steps_executed: int
    real_probe_adapter_called: bool
    persistence_performed: bool
    owner_authorization_present: bool
    execution_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    result_digest: str

    def __post_init__(self) -> None:
        sources = tuple(self.live_sources)
        handoffs = tuple(self.slot_handoffs)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"live_sources", "slot_handoffs", "result_digest"}
        }
        payload["source_digests"] = tuple(item.source_digest for item in sources)
        payload["handoff_digests"] = tuple(item.handoff_digest for item in handoffs)
        if (
            self.coordinator_id != S1_FW_COORDINATOR_ID
            or len(self.source_contract_digest) != 64
            or len(self.source_inventory_digest) != 64
            or len(sources) != 12
            or len(handoffs) != 30
            or (self.live_state_object_count, self.unique_live_state_object_count)
            != (12, 12)
            or (
                self.slot_handoff_count,
                self.state_consuming_slot_count,
                self.p0_slot_count,
                self.fixed_adapter_count,
            )
            != (30, 24, 6, 6)
            or tuple(count for _, _, count in self.usage_counts)
            != (3, 3, 1, 1) * 3
            or any(
                value is not True
                for value in (
                    self.source_state_digests_preserved,
                    self.exact_object_identity_preserved,
                    self.all_routes_complete,
                )
            )
            or self.field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.real_probe_adapter_called,
                    self.persistence_performed,
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "SYNTHETIC_LIVE_STATE_TEN_ROLE_HANDOFF_CONFIRMED_REAL_ADAPTER_CLOSED"
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1FWSyntheticLiveStateHandoffError(
                "S1-FW result changed or opened execution"
            )
        object.__setattr__(self, "live_sources", sources)
        object.__setattr__(self, "slot_handoffs", handoffs)


def _default_adapter_factory(
    layer: object,
    state: E1LocalEdgePlasticityState,
    config: NeutralLocalFieldSubstrateConfig,
) -> E1WeightedFieldAdapterResult:
    return compute_e1_weighted_edge_rates(
        layer,  # type: ignore[arg-type]
        state,
        config,
        backreaction_enabled=True,
    )


def coordinate_e1_formation_s1fw_synthetically(
    contract: E1FormationS1FVLiveStateTenRoleContract,
    inventory: E1FormationS1FJSyntheticInventory,
    inputs: E1FormationS1FIPreparedInputs,
    *,
    adapter_factory: AdapterFactory = _default_adapter_factory,
) -> E1FormationS1FWSyntheticLiveStateHandoffResult:
    """Route exact state objects and derive adapters without advancing a field."""

    if not isinstance(contract, E1FormationS1FVLiveStateTenRoleContract):
        raise E1FormationS1FWSyntheticLiveStateHandoffError(
            "S1-FW requires the typed S1-FV contract"
        )
    if not isinstance(inventory, E1FormationS1FJSyntheticInventory) or not isinstance(
        inputs, E1FormationS1FIPreparedInputs
    ):
        raise E1FormationS1FWSyntheticLiveStateHandoffError(
            "S1-FW requires typed S1-FJ results and S1-FI inputs"
        )
    if not callable(adapter_factory):
        raise E1FormationS1FWSyntheticLiveStateHandoffError(
            "S1-FW requires a callable pure adapter factory"
        )
    contract.__post_init__()
    inventory.__post_init__()
    inputs.__post_init__()
    if (
        inventory.source_input_manifest_digest != inputs.input_manifest_digest
        or inventory.field_steps_executed != 0
        or contract.execution_permitted is not False
    ):
        raise E1FormationS1FWSyntheticLiveStateHandoffError(
            "S1-FW source bindings changed or opened execution"
        )
    by_key = {
        (item.refinement_id, item.arm_id): item for item in inventory.results
    }
    sources = []
    source_by_key = {}
    for refinement in contract.refinements:
        for state_role, arm_id in contract.source_state_routes:
            result = by_key[(refinement, arm_id)]
            values = {
                "refinement_id": refinement,
                "state_role": state_role,
                "formation_arm_id": arm_id,
                "source_result": result,
                "state": result.output_state,
                "state_digest": result.output_state_digest,
            }
            digest_payload = {
                "refinement_id": refinement,
                "state_role": state_role,
                "formation_arm_id": arm_id,
                "source_result_digest": result.result_digest,
                "state_digest": result.output_state_digest,
            }
            source = E1FormationS1FWLiveStateSource(
                **values,
                source_digest=_digest(digest_payload),
            )
            sources.append(source)
            source_by_key[(refinement, state_role)] = source
    source_tuple = tuple(sources)
    before = tuple(_digest(_state_payload(item.state)) for item in source_tuple)
    config = NeutralLocalFieldSubstrateConfig(1.0)
    handoffs = []
    for binding in contract.slot_bindings:
        source = (
            None
            if binding.source_state_role is None
            else source_by_key[(binding.refinement_id, binding.source_state_role)]
        )
        state = None if source is None else source.state
        adapter = (
            adapter_factory(inputs.initial_field.layer, state, config)
            if binding.fixed_adapter_derivation_required and state is not None
            else None
        )
        if adapter is not None and not isinstance(adapter, E1WeightedFieldAdapterResult):
            raise E1FormationS1FWSyntheticLiveStateHandoffError(
                "S1-FW adapter factory returned no typed fixed adapter"
            )
        values = {
            "binding": binding,
            "source": source,
            "state": state,
            "fixed_adapter": adapter,
            "state_digest": None if source is None else source.state_digest,
            "fixed_adapter_digest": None if adapter is None else _adapter_digest(adapter),
            "state_object_identity_preserved": source is None or state is source.state,
            "field_steps_executed": 0,
        }
        digest_payload = {
            "binding_digest": binding.binding_digest,
            "source_digest": None if source is None else source.source_digest,
            "state_digest": values["state_digest"],
            "fixed_adapter_digest": values["fixed_adapter_digest"],
            "state_object_identity_preserved": values[
                "state_object_identity_preserved"
            ],
            "field_steps_executed": 0,
        }
        handoffs.append(
            E1FormationS1FWSyntheticSlotHandoff(
                **values,
                handoff_digest=_digest(digest_payload),
            )
        )
    handoff_tuple = tuple(handoffs)
    after = tuple(_digest(_state_payload(item.state)) for item in source_tuple)
    usage = Counter(
        (item.binding.refinement_id, item.binding.source_state_role)
        for item in handoff_tuple
        if item.binding.source_state_role is not None
    )
    usage_counts = tuple(
        (refinement, state_role, usage[(refinement, state_role)])
        for refinement in contract.refinements
        for state_role, _ in contract.source_state_routes
    )
    values = {
        "coordinator_id": S1_FW_COORDINATOR_ID,
        "source_contract_digest": contract.contract_digest,
        "source_inventory_digest": inventory.fixture_digest,
        "live_sources": source_tuple,
        "slot_handoffs": handoff_tuple,
        "live_state_object_count": len(source_tuple),
        "unique_live_state_object_count": len({id(item.state) for item in source_tuple}),
        "slot_handoff_count": len(handoff_tuple),
        "state_consuming_slot_count": sum(item.state is not None for item in handoff_tuple),
        "p0_slot_count": sum(item.state is None for item in handoff_tuple),
        "fixed_adapter_count": sum(item.fixed_adapter is not None for item in handoff_tuple),
        "usage_counts": usage_counts,
        "source_state_digests_preserved": before == after,
        "exact_object_identity_preserved": all(
            item.source is None or item.state is item.source.state
            for item in handoff_tuple
        ),
        "all_routes_complete": tuple(item.binding for item in handoff_tuple)
        == contract.slot_bindings,
        "field_steps_executed": sum(item.field_steps_executed for item in handoff_tuple),
        "real_probe_adapter_called": False,
        "persistence_performed": False,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "claims_permitted": False,
        "decision": (
            "SYNTHETIC_LIVE_STATE_TEN_ROLE_HANDOFF_CONFIRMED_"
            "REAL_ADAPTER_CLOSED"
        ),
        "reason": (
            "twelve-exact-live-state-objects-routed-to-thirty-slots;all-source-"
            "digests-preserved;six-fixed-adapters-derived-without-field-step"
        ),
    }
    digest_payload = {
        name: value
        for name, value in values.items()
        if name not in {"live_sources", "slot_handoffs"}
    }
    digest_payload["source_digests"] = tuple(
        item.source_digest for item in source_tuple
    )
    digest_payload["handoff_digests"] = tuple(
        item.handoff_digest for item in handoff_tuple
    )
    return E1FormationS1FWSyntheticLiveStateHandoffResult(
        **values,
        result_digest=_digest(digest_payload),
    )
