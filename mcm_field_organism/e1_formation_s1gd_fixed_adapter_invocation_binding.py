"""S1-GD atomic binding of six fixed-adapter invocation object sets."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_formation_s1fw_synthetic_live_state_handoff import (
    E1FormationS1FWSyntheticLiveStateHandoffResult,
    E1FormationS1FWSyntheticSlotHandoff,
    _adapter_digest,
)
from .e1_formation_s1gb_fixed_adapter_wrapper_contract import (
    E1FormationS1GBFixedAdapterWrapperContract,
)
from .e1_formation_s1gc_ten_role_probe_context_bridge import (
    E1FormationS1GCFixedAdapterProbeContext,
    E1FormationS1GCTenRoleProbeContextBridgeResult,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_formation_runner import _digest, _state_payload
from .e1_weighted_field_adapter import E1WeightedFieldAdapterResult


class E1FormationS1GDFixedAdapterInvocationBindingError(ValueError):
    """Raised when S1-GD loses exact identity or opens the wrapper path."""


S1_GD_BINDING_ID = "e1.fixed-adapter-invocation-binding.s1gd.v1"


@dataclass(frozen=True, slots=True)
class E1FormationS1GDFixedAdapterInvocation:
    context: E1FormationS1GCFixedAdapterProbeContext = field(repr=False)
    handoff: E1FormationS1FWSyntheticSlotHandoff = field(repr=False)
    source_state: E1LocalEdgePlasticityState = field(repr=False, compare=False)
    fixed_adapter: E1WeightedFieldAdapterResult = field(repr=False, compare=False)
    binding_digest: str
    context_digest: str
    handoff_digest: str
    source_state_digest: str
    fixed_adapter_digest: str
    exact_binding_object_identity_preserved: bool
    exact_state_object_identity_preserved: bool
    exact_adapter_object_identity_preserved: bool
    invocation_digest: str

    def __post_init__(self) -> None:
        payload = {
            "binding_digest": self.binding_digest,
            "context_digest": self.context_digest,
            "handoff_digest": self.handoff_digest,
            "source_state_digest": self.source_state_digest,
            "fixed_adapter_digest": self.fixed_adapter_digest,
            "exact_binding_object_identity_preserved": (
                self.exact_binding_object_identity_preserved
            ),
            "exact_state_object_identity_preserved": (
                self.exact_state_object_identity_preserved
            ),
            "exact_adapter_object_identity_preserved": (
                self.exact_adapter_object_identity_preserved
            ),
        }
        if (
            not isinstance(self.context, E1FormationS1GCFixedAdapterProbeContext)
            or not isinstance(self.handoff, E1FormationS1FWSyntheticSlotHandoff)
            or not isinstance(self.source_state, E1LocalEdgePlasticityState)
            or not isinstance(self.fixed_adapter, E1WeightedFieldAdapterResult)
            or self.context.binding is not self.handoff.binding
            or self.source_state is not self.handoff.state
            or self.fixed_adapter is not self.handoff.fixed_adapter
            or self.handoff.source is None
            or self.source_state is not self.handoff.source.state
            or self.binding_digest != self.context.binding.binding_digest
            or self.binding_digest != self.handoff.binding.binding_digest
            or self.context_digest != self.context.context_digest
            or self.handoff_digest != self.handoff.handoff_digest
            or self.source_state_digest != self.handoff.state_digest
            or self.source_state_digest != _digest(_state_payload(self.source_state))
            or self.fixed_adapter_digest != self.handoff.fixed_adapter_digest
            or self.fixed_adapter_digest != _adapter_digest(self.fixed_adapter)
            or any(
                value is not True
                for value in (
                    self.exact_binding_object_identity_preserved,
                    self.exact_state_object_identity_preserved,
                    self.exact_adapter_object_identity_preserved,
                )
            )
            or self.invocation_digest != _digest(payload)
        ):
            raise E1FormationS1GDFixedAdapterInvocationBindingError(
                "S1-GD invocation lost exact context, state, or adapter identity"
            )


@dataclass(frozen=True, slots=True)
class E1FormationS1GDFixedAdapterInvocationBindingResult:
    binding_id: str
    source_s1gb_contract_digest: str
    source_s1gc_result_digest: str
    source_s1fw_result_digest: str
    invocations: tuple[E1FormationS1GDFixedAdapterInvocation, ...] = field(
        repr=False
    )
    invocation_digests: tuple[str, ...]
    invocation_count: int
    refinement_invocation_counts: tuple[tuple[str, int], ...]
    all_contexts_and_handoffs_consumed_once: bool
    source_states_preserved: bool
    fixed_adapters_preserved: bool
    atomic_binding_complete: bool
    wrapper_implementation_permitted: bool
    wrapper_called: bool
    field_steps_executed: int
    persistence_performed: bool
    execution_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    result_digest: str

    def __post_init__(self) -> None:
        invocations = tuple(self.invocations)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"invocations", "result_digest"}
        }
        if (
            self.binding_id != S1_GD_BINDING_ID
            or any(
                len(value) != 64
                for value in (
                    self.source_s1gb_contract_digest,
                    self.source_s1gc_result_digest,
                    self.source_s1fw_result_digest,
                )
            )
            or len(invocations) != 6
            or self.invocation_digests
            != tuple(item.invocation_digest for item in invocations)
            or self.invocation_count != 6
            or self.refinement_invocation_counts
            != (("r2", 2), ("r4", 2), ("r8", 2))
            or any(
                value is not True
                for value in (
                    self.all_contexts_and_handoffs_consumed_once,
                    self.source_states_preserved,
                    self.fixed_adapters_preserved,
                    self.atomic_binding_complete,
                )
            )
            or any(
                value is not False
                for value in (
                    self.wrapper_implementation_permitted,
                    self.wrapper_called,
                    self.persistence_performed,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision
            != "SIX_FIXED_ADAPTER_INVOCATIONS_ATOMICALLY_BOUND_WRAPPER_CLOSED"
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GDFixedAdapterInvocationBindingError(
                "S1-GD aggregate changed or opened wrapper execution"
            )
        object.__setattr__(self, "invocations", invocations)


def bind_e1_formation_s1gd_fixed_adapter_invocations(
    wrapper_contract: E1FormationS1GBFixedAdapterWrapperContract,
    contexts: E1FormationS1GCTenRoleProbeContextBridgeResult,
    handoffs: E1FormationS1FWSyntheticLiveStateHandoffResult,
) -> E1FormationS1GDFixedAdapterInvocationBindingResult:
    """Join exact objects atomically without constructing a field or wrapper."""

    if not isinstance(wrapper_contract, E1FormationS1GBFixedAdapterWrapperContract):
        raise E1FormationS1GDFixedAdapterInvocationBindingError(
            "S1-GD requires the typed S1-GB contract"
        )
    if not isinstance(contexts, E1FormationS1GCTenRoleProbeContextBridgeResult):
        raise E1FormationS1GDFixedAdapterInvocationBindingError(
            "S1-GD requires the typed S1-GC bridge"
        )
    if not isinstance(handoffs, E1FormationS1FWSyntheticLiveStateHandoffResult):
        raise E1FormationS1GDFixedAdapterInvocationBindingError(
            "S1-GD requires the typed S1-FW handoff"
        )
    wrapper_contract.__post_init__()
    contexts.__post_init__()
    handoffs.__post_init__()
    if (
        contexts.source_s1gb_contract_digest != wrapper_contract.contract_digest
        or contexts.source_s1fv_contract_digest != handoffs.source_contract_digest
        or wrapper_contract.fixed_adapter_wrapper_implementation_permitted is not False
        or contexts.execution_permitted is not False
        or handoffs.execution_permitted is not False
    ):
        raise E1FormationS1GDFixedAdapterInvocationBindingError(
            "S1-GD source chain changed or opened execution"
        )
    fixed_handoffs = tuple(
        item for item in handoffs.slot_handoffs if item.fixed_adapter is not None
    )
    by_digest = {item.binding.binding_digest: item for item in fixed_handoffs}
    state_before = tuple(
        _digest(_state_payload(item.state)) for item in fixed_handoffs
    )
    adapter_before = tuple(
        _adapter_digest(item.fixed_adapter) for item in fixed_handoffs
    )
    pending = []
    for context in contexts.contexts:
        handoff = by_digest.get(context.binding.binding_digest)
        if handoff is None or context.binding is not handoff.binding:
            raise E1FormationS1GDFixedAdapterInvocationBindingError(
                "S1-GD context and handoff do not share the exact binding object"
            )
        values = {
            "context": context,
            "handoff": handoff,
            "source_state": handoff.state,
            "fixed_adapter": handoff.fixed_adapter,
            "binding_digest": context.binding.binding_digest,
            "context_digest": context.context_digest,
            "handoff_digest": handoff.handoff_digest,
            "source_state_digest": handoff.state_digest,
            "fixed_adapter_digest": handoff.fixed_adapter_digest,
            "exact_binding_object_identity_preserved": context.binding is handoff.binding,
            "exact_state_object_identity_preserved": handoff.state is handoff.source.state,
            "exact_adapter_object_identity_preserved": handoff.fixed_adapter is by_digest[context.binding.binding_digest].fixed_adapter,
        }
        digest_payload = {
            name: value
            for name, value in values.items()
            if name not in {"context", "handoff", "source_state", "fixed_adapter"}
        }
        pending.append(
            E1FormationS1GDFixedAdapterInvocation(
                **values,
                invocation_digest=_digest(digest_payload),
            )
        )
    invocation_tuple = tuple(pending)
    state_after = tuple(
        _digest(_state_payload(item.state)) for item in fixed_handoffs
    )
    adapter_after = tuple(
        _adapter_digest(item.fixed_adapter) for item in fixed_handoffs
    )
    counts = tuple(
        (
            refinement,
            sum(
                item.context.binding.refinement_id == refinement
                for item in invocation_tuple
            ),
        )
        for refinement in ("r2", "r4", "r8")
    )
    values = {
        "binding_id": S1_GD_BINDING_ID,
        "source_s1gb_contract_digest": wrapper_contract.contract_digest,
        "source_s1gc_result_digest": contexts.result_digest,
        "source_s1fw_result_digest": handoffs.result_digest,
        "invocations": invocation_tuple,
        "invocation_digests": tuple(
            item.invocation_digest for item in invocation_tuple
        ),
        "invocation_count": len(invocation_tuple),
        "refinement_invocation_counts": counts,
        "all_contexts_and_handoffs_consumed_once": (
            tuple(item.context for item in invocation_tuple) == contexts.contexts
            and tuple(item.handoff for item in invocation_tuple) == fixed_handoffs
        ),
        "source_states_preserved": state_before == state_after,
        "fixed_adapters_preserved": adapter_before == adapter_after,
        "atomic_binding_complete": len(invocation_tuple) == 6,
        "wrapper_implementation_permitted": False,
        "wrapper_called": False,
        "field_steps_executed": 0,
        "persistence_performed": False,
        "execution_permitted": False,
        "claims_permitted": False,
        "decision": (
            "SIX_FIXED_ADAPTER_INVOCATIONS_ATOMICALLY_BOUND_WRAPPER_CLOSED"
        ),
        "reason": (
            "six-context-handoff-pairs-share-exact-binding-state-and-adapter-"
            "objects;all-digests-preserved;wrapper-not-called"
        ),
    }
    payload = {name: value for name, value in values.items() if name != "invocations"}
    return E1FormationS1GDFixedAdapterInvocationBindingResult(
        **values,
        result_digest=_digest(payload),
    )
