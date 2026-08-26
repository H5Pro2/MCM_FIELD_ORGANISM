"""S1-GH atomic fresh-field bridge for six fixed-adapter invocations."""

from __future__ import annotations

from collections.abc import Callable
import copy
from dataclasses import dataclass, field

from .e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIPreparedInputs,
)
from .e1_formation_s1gd_fixed_adapter_invocation_binding import (
    E1FormationS1GDFixedAdapterInvocation,
    E1FormationS1GDFixedAdapterInvocationBindingResult,
)
from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_ROLE_ORDER,
)
from .e1_formation_s1fw_synthetic_live_state_handoff import _adapter_digest
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest, _state_payload
from .shared_mcm_field import SharedMCMField


class E1FormationS1GHFreshFieldBridgeError(ValueError):
    """Raised when fresh fields lose identity, neutrality, or atomicity."""


S1_GH_BRIDGE_ID = "e1.fixed-adapter-fresh-field-bridge.s1gh.v1"
FieldCopier = Callable[[SharedMCMField], SharedMCMField]


@dataclass(frozen=True, slots=True)
class E1FormationS1GHFreshFieldBinding:
    invocation: E1FormationS1GDFixedAdapterInvocation = field(repr=False)
    source_initial_field: SharedMCMField = field(repr=False, compare=False)
    fresh_field: SharedMCMField = field(repr=False, compare=False)
    refinement_id: str
    role_id: str
    invocation_digest: str
    binding_digest: str
    source_input_manifest_digest: str
    initial_field_digest: str
    ordered_neuron_ids: tuple[str, ...]
    source_field_object_separate: bool
    source_layer_object_separate: bool
    source_docks_object_separate: bool
    neutral_initial_state_preserved: bool
    fresh_binding_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name
            not in {
                "invocation",
                "source_initial_field",
                "fresh_field",
                "fresh_binding_digest",
            }
        }
        if (
            not isinstance(self.invocation, E1FormationS1GDFixedAdapterInvocation)
            or not isinstance(self.source_initial_field, SharedMCMField)
            or not isinstance(self.fresh_field, SharedMCMField)
            or (self.refinement_id, self.role_id) not in S1_GF_ROLE_ORDER
            or self.refinement_id
            != self.invocation.context.binding.refinement_id
            or self.role_id != self.invocation.context.binding.role_id
            or self.invocation_digest != self.invocation.invocation_digest
            or self.binding_digest != self.invocation.binding_digest
            or len(self.source_input_manifest_digest) != 64
            or self.initial_field_digest
            != _initial_field_digest(self.source_initial_field)
            or self.initial_field_digest != _initial_field_digest(self.fresh_field)
            or self.ordered_neuron_ids
            != tuple(item.neuron_id for item in self.fresh_field.layer.neurons)
            or not self.ordered_neuron_ids
            or len(set(self.ordered_neuron_ids)) != len(self.ordered_neuron_ids)
            or any(
                value is not True
                for value in (
                    self.source_field_object_separate,
                    self.source_layer_object_separate,
                    self.source_docks_object_separate,
                    self.neutral_initial_state_preserved,
                )
            )
            or self.fresh_field is self.source_initial_field
            or self.fresh_field.layer is self.source_initial_field.layer
            or self.fresh_field.docks is self.source_initial_field.docks
            or self.fresh_field.layer.tick != 0
            or self.fresh_field.last_distribution is not None
            or self.fresh_field.substrate is not None
            or self.fresh_binding_digest != _digest(payload)
        ):
            raise E1FormationS1GHFreshFieldBridgeError(
                "S1-GH fresh field lost its source, binding, or neutral state"
            )


@dataclass(frozen=True, slots=True)
class E1FormationS1GHFreshFieldBridgeResult:
    bridge_id: str
    source_s1gd_result_digest: str
    source_s1fi_input_manifest_digest: str
    source_initial_field_digest: str
    fresh_bindings: tuple[E1FormationS1GHFreshFieldBinding, ...] = field(
        repr=False
    )
    fresh_binding_digests: tuple[str, ...]
    role_order: tuple[tuple[str, str], ...]
    fresh_field_count: int
    unique_fresh_field_object_count: int
    unique_fresh_layer_object_count: int
    all_initial_field_digests_identical: bool
    all_invocations_bound_once_in_order: bool
    all_fresh_fields_object_separate: bool
    source_states_preserved: bool
    fixed_adapters_preserved: bool
    atomic_bridge_complete: bool
    probe_plans_consumed: int
    probe_batches_consumed: int
    field_steps_executed: int
    field_kernel_called: bool
    observed_vectors_present: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    result_digest: str

    def __post_init__(self) -> None:
        bindings = tuple(self.fresh_bindings)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"fresh_bindings", "result_digest"}
        }
        if (
            self.bridge_id != S1_GH_BRIDGE_ID
            or any(
                len(value) != 64
                for value in (
                    self.source_s1gd_result_digest,
                    self.source_s1fi_input_manifest_digest,
                    self.source_initial_field_digest,
                )
            )
            or len(bindings) != 6
            or self.fresh_binding_digests
            != tuple(item.fresh_binding_digest for item in bindings)
            or self.role_order != S1_GF_ROLE_ORDER
            or (
                self.fresh_field_count,
                self.unique_fresh_field_object_count,
                self.unique_fresh_layer_object_count,
            )
            != (6, 6, 6)
            or any(
                value is not True
                for value in (
                    self.all_initial_field_digests_identical,
                    self.all_invocations_bound_once_in_order,
                    self.all_fresh_fields_object_separate,
                    self.source_states_preserved,
                    self.fixed_adapters_preserved,
                    self.atomic_bridge_complete,
                )
            )
            or any(
                value != 0
                for value in (
                    self.probe_plans_consumed,
                    self.probe_batches_consumed,
                    self.field_steps_executed,
                )
            )
            or any(
                value is not False
                for value in (
                    self.field_kernel_called,
                    self.observed_vectors_present,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "SIX_FRESH_FIELDS_ATOMICALLY_BOUND_REAL_KERNEL_REMAINS_CLOSED"
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GHFreshFieldBridgeError(
                "S1-GH aggregate changed or opened probe execution"
            )
        object.__setattr__(self, "fresh_bindings", bindings)


def bind_e1_formation_s1gh_fresh_fields(
    bindings: E1FormationS1GDFixedAdapterInvocationBindingResult,
    inputs: E1FormationS1FIPreparedInputs,
    *,
    field_copier: FieldCopier = copy.deepcopy,
) -> E1FormationS1GHFreshFieldBridgeResult:
    """Bind six deep fresh fields without consuming plans or field batches."""

    if (
        not isinstance(bindings, E1FormationS1GDFixedAdapterInvocationBindingResult)
        or not isinstance(inputs, E1FormationS1FIPreparedInputs)
        or not callable(field_copier)
    ):
        raise E1FormationS1GHFreshFieldBridgeError(
            "S1-GH requires typed bindings, inputs, and field copier"
        )
    bindings.__post_init__()
    inputs.__post_init__()
    invocations = tuple(bindings.invocations)
    role_order = tuple(
        (item.context.binding.refinement_id, item.context.binding.role_id)
        for item in invocations
    )
    if (
        role_order != S1_GF_ROLE_ORDER
        or bindings.wrapper_implementation_permitted is not False
        or len(invocations) != 6
    ):
        raise E1FormationS1GHFreshFieldBridgeError(
            "S1-GH source invocation order changed or opened execution"
        )
    source_field = inputs.initial_field
    source_digest = _initial_field_digest(source_field)
    states_before = tuple(_digest(_state_payload(item.source_state)) for item in invocations)
    adapters_before = tuple(_adapter_digest(item.fixed_adapter) for item in invocations)
    pending = []
    try:
        for invocation in invocations:
            fresh = field_copier(source_field)
            if not isinstance(fresh, SharedMCMField):
                raise E1FormationS1GHFreshFieldBridgeError(
                    "S1-GH copier returned no shared field"
                )
            values = {
                "invocation": invocation,
                "source_initial_field": source_field,
                "fresh_field": fresh,
                "refinement_id": invocation.context.binding.refinement_id,
                "role_id": invocation.context.binding.role_id,
                "invocation_digest": invocation.invocation_digest,
                "binding_digest": invocation.binding_digest,
                "source_input_manifest_digest": inputs.input_manifest_digest,
                "initial_field_digest": source_digest,
                "ordered_neuron_ids": tuple(
                    item.neuron_id for item in fresh.layer.neurons
                ),
                "source_field_object_separate": fresh is not source_field,
                "source_layer_object_separate": fresh.layer is not source_field.layer,
                "source_docks_object_separate": fresh.docks is not source_field.docks,
                "neutral_initial_state_preserved": (
                    fresh.layer.tick == 0
                    and fresh.last_distribution is None
                    and fresh.substrate is None
                    and _initial_field_digest(fresh) == source_digest
                ),
            }
            digest_payload = {
                name: value
                for name, value in values.items()
                if name
                not in {
                    "invocation",
                    "source_initial_field",
                    "fresh_field",
                }
            }
            pending.append(
                E1FormationS1GHFreshFieldBinding(
                    **values,
                    fresh_binding_digest=_digest(digest_payload),
                )
            )
    except E1FormationS1GHFreshFieldBridgeError:
        raise
    except Exception as exc:
        raise E1FormationS1GHFreshFieldBridgeError(
            "S1-GH field copier aborted; no aggregate returned"
        ) from exc

    fresh_bindings = tuple(pending)
    fresh_fields = tuple(item.fresh_field for item in fresh_bindings)
    fresh_layers = tuple(item.layer for item in fresh_fields)
    states_after = tuple(_digest(_state_payload(item.source_state)) for item in invocations)
    adapters_after = tuple(_adapter_digest(item.fixed_adapter) for item in invocations)
    values = {
        "bridge_id": S1_GH_BRIDGE_ID,
        "source_s1gd_result_digest": bindings.result_digest,
        "source_s1fi_input_manifest_digest": inputs.input_manifest_digest,
        "source_initial_field_digest": source_digest,
        "fresh_bindings": fresh_bindings,
        "fresh_binding_digests": tuple(
            item.fresh_binding_digest for item in fresh_bindings
        ),
        "role_order": role_order,
        "fresh_field_count": len(fresh_fields),
        "unique_fresh_field_object_count": len({id(item) for item in fresh_fields}),
        "unique_fresh_layer_object_count": len({id(item) for item in fresh_layers}),
        "all_initial_field_digests_identical": {
            _initial_field_digest(item) for item in fresh_fields
        }
        == {source_digest},
        "all_invocations_bound_once_in_order": tuple(
            item.invocation for item in fresh_bindings
        )
        == invocations,
        "all_fresh_fields_object_separate": (
            len({id(item) for item in fresh_fields}) == 6
            and len({id(item) for item in fresh_layers}) == 6
            and all(item is not source_field for item in fresh_fields)
            and all(item is not source_field.layer for item in fresh_layers)
        ),
        "source_states_preserved": states_before == states_after,
        "fixed_adapters_preserved": adapters_before == adapters_after,
        "atomic_bridge_complete": len(fresh_bindings) == 6,
        "probe_plans_consumed": 0,
        "probe_batches_consumed": 0,
        "field_steps_executed": 0,
        "field_kernel_called": False,
        "observed_vectors_present": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": "SIX_FRESH_FIELDS_ATOMICALLY_BOUND_REAL_KERNEL_REMAINS_CLOSED",
        "reason": (
            "six-deep-digest-identical-object-separated-neutral-fields-bound-"
            "once-to-exact-s1gd-invocations;no-plan-batch-or-kernel-consumed"
        ),
    }
    payload = {
        name: value for name, value in values.items() if name != "fresh_bindings"
    }
    return E1FormationS1GHFreshFieldBridgeResult(
        **values,
        result_digest=_digest(payload),
    )
