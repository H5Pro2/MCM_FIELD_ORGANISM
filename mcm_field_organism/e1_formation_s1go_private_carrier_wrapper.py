"""S1-GO private six-arm wrapper using the explicit S1-GN carrier."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_REFINEMENT_BATCH_COUNTS,
    S1_GF_ROLE_ORDER,
    S1_GF_TOTAL_BATCH_COUNT,
)
from .e1_formation_s1fw_synthetic_live_state_handoff import _adapter_digest
from .e1_formation_s1gh_fresh_field_bridge import (
    E1FormationS1GHFreshFieldBinding,
    E1FormationS1GHFreshFieldBridgeResult,
)
from .e1_formation_s1gi_fixed_adapter_output_converter import (
    E1FormationS1GIFixedAdapterCommonProbeReceipt,
    E1FormationS1GIFixedAdapterRealOutput,
    build_e1_formation_s1gi_synthetic_typed_output,
    convert_e1_formation_s1gi_fixed_adapter_output,
)
from .e1_formation_s1gj_synthetic_fixed_adapter_receipt_integration import (
    S1_GJ_TOTAL_SUPPORT_COUNT,
)
from .e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    E1FormationS1GKFixedAdapterRealWrapperContract,
)
from .e1_formation_s1gl_private_fixed_adapter_wrapper import (
    E1FormationS1GLSyntheticOnlyGate,
)
from .e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
    E1FormationS1GNLiveFieldCarrierTransition,
    advance_e1_formation_s1gn_live_field_carrier_synthetically,
    build_e1_formation_s1gn_initial_live_field_carrier,
    e1_formation_s1gn_current_field_digest,
)
from .e1_refined_formation_runner import _digest, _state_payload
from .receptor_proposal_handoff import ReceptorProposalBatch


class E1FormationS1GOPrivateCarrierWrapperError(ValueError):
    """Raised when the carrier wrapper loses route, state, or atomicity."""


S1_GO_WRAPPER_ID = "e1.private-carrier-wrapper.s1go.v1"
S1_GO_DECISION = (
    "PRIVATE_SIX_ARM_CARRIER_WRAPPER_SYNTHETICALLY_VALIDATED_"
    "REAL_BATCH_ADAPTER_CLOSED"
)


CarrierTransition = Callable[
    [
        E1FormationS1GHFreshFieldBinding,
        ReceptorProposalBatch,
        E1FormationS1GNLiveFieldCarrier,
    ],
    E1FormationS1GNLiveFieldCarrierTransition,
]
TerminalOutputFactory = Callable[
    [E1FormationS1GHFreshFieldBinding, E1FormationS1GNLiveFieldCarrier],
    E1FormationS1GIFixedAdapterRealOutput,
]


def build_e1_formation_s1go_synthetic_terminal_output(
    fresh: E1FormationS1GHFreshFieldBinding,
    carrier: E1FormationS1GNLiveFieldCarrier,
) -> E1FormationS1GIFixedAdapterRealOutput:
    """Read terminal vectors from the explicitly carried, unchanged field."""

    if not isinstance(fresh, E1FormationS1GHFreshFieldBinding) or not isinstance(
        carrier, E1FormationS1GNLiveFieldCarrier
    ):
        raise E1FormationS1GOPrivateCarrierWrapperError(
            "S1-GO terminal output requires one fresh binding and carrier"
        )
    fresh.__post_init__()
    carrier.__post_init__()
    plan = fresh.invocation.context.probe_plan
    if (
        carrier.fresh_binding is not fresh
        or carrier.current_field is not fresh.fresh_field
        or carrier.binding_digest != fresh.binding_digest
        or carrier.completed_batch_count != len(plan.handoff.batches)
        or carrier.accounted_source_support_count
        != plan.handoff.source_event_count
        or carrier.actual_field_steps_executed != 0
        or carrier.current_field_digest
        != e1_formation_s1gn_current_field_digest(carrier.current_field)
    ):
        raise E1FormationS1GOPrivateCarrierWrapperError(
            "S1-GO terminal carrier is incomplete or crossed synthetic scope"
        )
    activation = tuple(
        neuron.activation for neuron in carrier.current_field.layer.neurons
    )
    afterimage = tuple(
        neuron.afterimage for neuron in carrier.current_field.layer.neurons
    )
    return build_e1_formation_s1gi_synthetic_typed_output(
        fresh,
        activation,
        afterimage,
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GOPrivateCarrierWrapperResult:
    wrapper_id: str
    source_s1gk_contract_digest: str
    source_s1gh_result_digest: str
    gate_digest: str
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    transition_digests: tuple[str, ...]
    terminal_carrier_digests: tuple[str, ...]
    terminal_output_digests: tuple[str, ...]
    common_receipt_digests: tuple[str, ...]
    arm_count: int
    carrier_transition_calls: int
    accounted_field_steps: int
    actual_field_steps_executed: int
    source_support_count: int
    terminal_carrier_count: int
    terminal_output_count: int
    common_receipt_count: int
    all_batches_consumed_once_in_order: bool
    all_field_objects_carried_explicitly: bool
    all_terminal_carriers_complete: bool
    all_outputs_match_carried_field_vectors: bool
    all_outputs_and_receipts_bound: bool
    fresh_fields_preserved: bool
    source_states_preserved: bool
    fixed_adapters_preserved: bool
    atomic_return_complete: bool
    legacy_token_wrapper_called: bool
    real_batch_adapter_called: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    result_digest: str
    terminal_carriers: tuple[E1FormationS1GNLiveFieldCarrier, ...] = field(
        repr=False,
        compare=False,
    )
    outputs: tuple[E1FormationS1GIFixedAdapterRealOutput, ...] = field(
        repr=False,
        compare=False,
    )
    receipts: tuple[E1FormationS1GIFixedAdapterCommonProbeReceipt, ...] = field(
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        carriers = tuple(self.terminal_carriers)
        outputs = tuple(self.outputs)
        receipts = tuple(self.receipts)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name
            not in {
                "terminal_carriers",
                "outputs",
                "receipts",
                "result_digest",
            }
        }
        if (
            self.wrapper_id != S1_GO_WRAPPER_ID
            or any(
                len(value) != 64
                for value in (
                    self.source_s1gk_contract_digest,
                    self.source_s1gh_result_digest,
                    self.gate_digest,
                )
            )
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or len(self.transition_digests) != S1_GF_TOTAL_BATCH_COUNT
            or self.terminal_carrier_digests
            != tuple(item.carrier_digest for item in carriers)
            or self.terminal_output_digests
            != tuple(item.output_digest for item in outputs)
            or self.common_receipt_digests
            != tuple(item.receipt_digest for item in receipts)
            or self.arm_count != 6
            or self.carrier_transition_calls != S1_GF_TOTAL_BATCH_COUNT
            or self.accounted_field_steps != S1_GF_TOTAL_BATCH_COUNT
            or self.actual_field_steps_executed != 0
            or self.source_support_count != S1_GJ_TOTAL_SUPPORT_COUNT
            or (
                self.terminal_carrier_count,
                self.terminal_output_count,
                self.common_receipt_count,
            )
            != (6, 6, 6)
            or len(carriers) != 6
            or len(outputs) != 6
            or len(receipts) != 6
            or any(
                value is not True
                for value in (
                    self.all_batches_consumed_once_in_order,
                    self.all_field_objects_carried_explicitly,
                    self.all_terminal_carriers_complete,
                    self.all_outputs_match_carried_field_vectors,
                    self.all_outputs_and_receipts_bound,
                    self.fresh_fields_preserved,
                    self.source_states_preserved,
                    self.fixed_adapters_preserved,
                    self.atomic_return_complete,
                )
            )
            or any(
                value is not False
                for value in (
                    self.legacy_token_wrapper_called,
                    self.real_batch_adapter_called,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision != S1_GO_DECISION
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GOPrivateCarrierWrapperError(
                "S1-GO aggregate changed or opened real execution"
            )
        object.__setattr__(self, "terminal_carriers", carriers)
        object.__setattr__(self, "outputs", outputs)
        object.__setattr__(self, "receipts", receipts)


def run_e1_formation_s1go_private_carrier_wrapper(
    contract: E1FormationS1GKFixedAdapterRealWrapperContract,
    bridge: E1FormationS1GHFreshFieldBridgeResult,
    gate: E1FormationS1GLSyntheticOnlyGate,
    *,
    carrier_transition: CarrierTransition = (
        advance_e1_formation_s1gn_live_field_carrier_synthetically
    ),
    terminal_output_factory: TerminalOutputFactory = (
        build_e1_formation_s1go_synthetic_terminal_output
    ),
) -> E1FormationS1GOPrivateCarrierWrapperResult:
    """Run all six synthetic arms with explicit live-field carriers."""

    if (
        not isinstance(contract, E1FormationS1GKFixedAdapterRealWrapperContract)
        or not isinstance(bridge, E1FormationS1GHFreshFieldBridgeResult)
        or not isinstance(gate, E1FormationS1GLSyntheticOnlyGate)
        or not callable(carrier_transition)
        or not callable(terminal_output_factory)
    ):
        raise E1FormationS1GOPrivateCarrierWrapperError(
            "S1-GO requires typed sources and carrier functions"
        )
    contract.__post_init__()
    bridge.__post_init__()
    gate.__post_init__()
    fresh_bindings = tuple(bridge.fresh_bindings)
    role_order = tuple(
        (item.refinement_id, item.role_id) for item in fresh_bindings
    )
    if (
        contract.source_s1gh_result_digest != bridge.result_digest
        or contract.real_wrapper_implementation_permitted is not True
        or contract.execution_permitted is not False
        or gate.real_batch_adapter_permitted is not False
        or gate.real_field_execution_permitted is not False
        or role_order != contract.role_order
        or role_order != S1_GF_ROLE_ORDER
        or len(fresh_bindings) != gate.expected_arm_count
    ):
        raise E1FormationS1GOPrivateCarrierWrapperError(
            "S1-GO contract, bridge, gate, or role order changed"
        )

    fields_before = tuple(
        e1_formation_s1gn_current_field_digest(item.fresh_field)
        for item in fresh_bindings
    )
    states_before = tuple(
        _digest(_state_payload(item.invocation.source_state))
        for item in fresh_bindings
    )
    adapters_before = tuple(
        _adapter_digest(item.invocation.fixed_adapter) for item in fresh_bindings
    )
    pending_transitions = []
    pending_carriers = []
    pending_outputs = []
    pending_receipts = []
    try:
        for fresh in fresh_bindings:
            plan = fresh.invocation.context.probe_plan
            carrier = build_e1_formation_s1gn_initial_live_field_carrier(fresh)
            for expected_index, batch in enumerate(plan.handoff.batches):
                transition = carrier_transition(fresh, batch, carrier)
                if not isinstance(
                    transition, E1FormationS1GNLiveFieldCarrierTransition
                ):
                    raise E1FormationS1GOPrivateCarrierWrapperError(
                        "S1-GO transition returned no typed S1-GN transition"
                    )
                transition.__post_init__()
                if (
                    transition.previous_carrier is not carrier
                    or transition.next_carrier.fresh_binding is not fresh
                    or transition.binding_digest != fresh.binding_digest
                    or transition.batch_index != expected_index
                    or transition.batch_step_start_tick
                    != batch.step_time.start_tick
                    or transition.batch_step_end_tick != batch.step_time.end_tick
                    or transition.batch_source_support_count != batch.event_count
                    or transition.actual_field_steps_executed != 0
                ):
                    raise E1FormationS1GOPrivateCarrierWrapperError(
                        "S1-GO carrier route, order, support, or scope changed"
                    )
                pending_transitions.append(transition)
                carrier = transition.next_carrier
            output = terminal_output_factory(fresh, carrier)
            if not isinstance(output, E1FormationS1GIFixedAdapterRealOutput):
                raise E1FormationS1GOPrivateCarrierWrapperError(
                    "S1-GO terminal factory returned no typed S1-GI output"
                )
            output.__post_init__()
            if (
                output.binding_digest != fresh.binding_digest
                or output.field_execution_kind != "synthetic-typed-real-output"
                or output.actual_field_steps_executed != 0
            ):
                raise E1FormationS1GOPrivateCarrierWrapperError(
                    "S1-GO terminal output crossed synthetic scope"
                )
            receipt = convert_e1_formation_s1gi_fixed_adapter_output(fresh, output)
            pending_carriers.append(carrier)
            pending_outputs.append(output)
            pending_receipts.append(receipt)
    except E1FormationS1GOPrivateCarrierWrapperError:
        raise
    except Exception as exc:
        raise E1FormationS1GOPrivateCarrierWrapperError(
            "S1-GO carrier wrapper aborted; no aggregate returned"
        ) from exc

    transitions = tuple(pending_transitions)
    carriers = tuple(pending_carriers)
    outputs = tuple(pending_outputs)
    receipts = tuple(pending_receipts)
    fields_after = tuple(
        e1_formation_s1gn_current_field_digest(item.fresh_field)
        for item in fresh_bindings
    )
    states_after = tuple(
        _digest(_state_payload(item.invocation.source_state))
        for item in fresh_bindings
    )
    adapters_after = tuple(
        _adapter_digest(item.invocation.fixed_adapter) for item in fresh_bindings
    )
    refinement_steps = tuple(
        (
            refinement,
            sum(
                transition.previous_carrier.fresh_binding.refinement_id
                == refinement
                for transition in transitions
            ),
        )
        for refinement in ("r2", "r4", "r8")
    )
    values = {
        "wrapper_id": S1_GO_WRAPPER_ID,
        "source_s1gk_contract_digest": contract.contract_digest,
        "source_s1gh_result_digest": bridge.result_digest,
        "gate_digest": gate.gate_digest,
        "role_order": role_order,
        "refinement_step_counts": refinement_steps,
        "transition_digests": tuple(
            item.transition_digest for item in transitions
        ),
        "terminal_carrier_digests": tuple(
            item.carrier_digest for item in carriers
        ),
        "terminal_output_digests": tuple(item.output_digest for item in outputs),
        "common_receipt_digests": tuple(
            item.receipt_digest for item in receipts
        ),
        "arm_count": len(fresh_bindings),
        "carrier_transition_calls": len(transitions),
        "accounted_field_steps": sum(
            item.accounted_field_steps for item in transitions
        ),
        "actual_field_steps_executed": sum(
            item.actual_field_steps_executed for item in transitions
        ),
        "source_support_count": sum(
            item.batch_source_support_count for item in transitions
        ),
        "terminal_carrier_count": len(carriers),
        "terminal_output_count": len(outputs),
        "common_receipt_count": len(receipts),
        "all_batches_consumed_once_in_order": len(transitions)
        == gate.expected_batch_kernel_calls,
        "all_field_objects_carried_explicitly": all(
            transition.previous_carrier.current_field
            is transition.next_carrier.current_field
            for transition in transitions
        ),
        "all_terminal_carriers_complete": all(
            carrier.completed_batch_count
            == len(fresh.invocation.context.probe_plan.handoff.batches)
            and carrier.accounted_source_support_count
            == fresh.invocation.context.probe_plan.handoff.source_event_count
            and carrier.actual_field_steps_executed == 0
            for fresh, carrier in zip(fresh_bindings, carriers, strict=True)
        ),
        "all_outputs_match_carried_field_vectors": all(
            output.activation
            == tuple(
                neuron.activation
                for neuron in carrier.current_field.layer.neurons
            )
            and output.afterimage
            == tuple(
                neuron.afterimage
                for neuron in carrier.current_field.layer.neurons
            )
            for carrier, output in zip(carriers, outputs, strict=True)
        ),
        "all_outputs_and_receipts_bound": all(
            fresh.binding_digest
            == carrier.binding_digest
            == output.binding_digest
            == receipt.binding_digest
            for fresh, carrier, output, receipt in zip(
                fresh_bindings,
                carriers,
                outputs,
                receipts,
                strict=True,
            )
        ),
        "fresh_fields_preserved": fields_before == fields_after,
        "source_states_preserved": states_before == states_after,
        "fixed_adapters_preserved": adapters_before == adapters_after,
        "atomic_return_complete": len(carriers) == len(outputs) == len(receipts) == 6,
        "legacy_token_wrapper_called": False,
        "real_batch_adapter_called": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": S1_GO_DECISION,
        "reason": (
            "six-arm-wrapper-consumed-2800-batches-through-explicit-s1gn-"
            "carriers-and-returned-six-field-bound-synthetic-outputs;legacy-"
            "token-wrapper-real-adapter-persistence-and-claims-remain-closed"
        ),
    }
    payload = {
        name: value
        for name, value in values.items()
        if name not in {"terminal_carriers", "outputs", "receipts"}
    }
    return E1FormationS1GOPrivateCarrierWrapperResult(
        **values,
        result_digest=_digest(payload),
        terminal_carriers=carriers,
        outputs=outputs,
        receipts=receipts,
    )
