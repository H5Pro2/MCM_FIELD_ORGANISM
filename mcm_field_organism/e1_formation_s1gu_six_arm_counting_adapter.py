"""S1-GU bounded six-arm fixed-adapter adapter with injected transitions."""

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
    E1FormationS1GHFreshFieldBridgeResult,
)
from .e1_formation_s1gi_fixed_adapter_output_converter import (
    E1FormationS1GIFixedAdapterCommonProbeReceipt,
    E1FormationS1GIFixedAdapterRealOutput,
    convert_e1_formation_s1gi_fixed_adapter_output,
)
from .e1_formation_s1gj_synthetic_fixed_adapter_receipt_integration import (
    S1_GJ_TOTAL_SUPPORT_COUNT,
)
from .e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    E1FormationS1GKFixedAdapterRealWrapperContract,
)
from .e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
    advance_e1_formation_s1gn_live_field_carrier_synthetically,
    build_e1_formation_s1gn_initial_live_field_carrier,
    e1_formation_s1gn_current_field_digest,
)
from .e1_formation_s1go_private_carrier_wrapper import (
    CarrierTransition,
    TerminalOutputFactory,
    build_e1_formation_s1go_synthetic_terminal_output,
)
from .e1_formation_s1gq_carrier_transition_schema import (
    E1FormationS1GQCarrierTransitionEnvelope,
    bind_e1_formation_s1gq_carrier_transition_envelope,
)
from .e1_formation_s1gt_six_arm_release_scope_contract import (
    E1FormationS1GTSixArmReleaseScopeContract,
)
from .e1_refined_formation_runner import _digest, _state_payload


class E1FormationS1GUSixArmCountingAdapterError(ValueError):
    """Raised when S1-GU widens scope, opens execution, or returns partial output."""


S1_GU_ADAPTER_ID = "e1.fixed-adapter-six-arm-counting-adapter.s1gu.v1"
S1_GU_DECISION = (
    "SIX_ARM_COUNTING_ADAPTER_VALIDATED_WITH_INJECTED_TRANSITIONS_REAL_KERNEL_CLOSED"
)
S1_GU_REAL_DECISION = "SIX_ARM_REAL_FIXED_ADAPTER_PROBE_COMPLETED_ATOMICALLY"


def _s1gu_execution_mode(
    transition_kind_counts: tuple[tuple[str, int], ...],
    actual_field_steps_executed: int,
) -> tuple[bool, str, str]:
    synthetic = (
        transition_kind_counts
        == (("synthetic-no-field-advance", S1_GF_TOTAL_BATCH_COUNT),)
        and actual_field_steps_executed == 0
    )
    real = (
        transition_kind_counts
        == (("real-field-advance", S1_GF_TOTAL_BATCH_COUNT),)
        and actual_field_steps_executed == S1_GF_TOTAL_BATCH_COUNT
    )
    if not (synthetic or real):
        raise E1FormationS1GUSixArmCountingAdapterError(
            "S1-GU mixed or partially executed transition modes"
        )
    if real:
        return (
            True,
            S1_GU_REAL_DECISION,
            "bounded-six-arm-real-fixed-adapter-probe-completed-2800-field-"
            "steps-and-660-supports-with-six-atomic-in-memory-outputs-and-"
            "receipts;source-states-adapters-persistence-claims-and-memory-"
            "decision-remained-unchanged-or-closed",
        )
    return (
        False,
        S1_GU_DECISION,
        "bounded-six-arm-adapter-consumed-2800-injected-transitions-and-"
        "660-supports-with-six-atomic-typed-outputs;default-injection-is-"
        "counting-only-and-real-kernel-full-chain-persistence-claims-remain-closed",
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GUSixArmCountingAdapterResult:
    adapter_id: str
    source_s1gt_contract_digest: str
    source_s1gk_contract_digest: str
    source_s1gh_result_digest: str
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    transition_digests: tuple[str, ...]
    transition_envelope_digests: tuple[str, ...]
    terminal_carrier_digests: tuple[str, ...]
    terminal_output_digests: tuple[str, ...]
    common_receipt_digests: tuple[str, ...]
    arm_count: int
    transition_call_count: int
    accounted_field_steps: int
    actual_field_steps_executed: int
    source_support_count: int
    terminal_carrier_count: int
    terminal_output_count: int
    common_receipt_count: int
    transition_kind_counts: tuple[tuple[str, int], ...]
    all_batches_consumed_once_in_order: bool
    all_transitions_validated_by_shared_envelope: bool
    all_outputs_and_receipts_bound: bool
    source_states_preserved: bool
    fixed_adapters_preserved: bool
    atomic_return_complete: bool
    real_kernel_called_by_adapter: bool
    full_chain_opened: bool
    persistence_performed: bool
    claims_permitted: bool
    memory_decision_permitted: bool
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
        real_mode, expected_decision, _ = _s1gu_execution_mode(
            self.transition_kind_counts,
            self.actual_field_steps_executed,
        )
        expected_execution_kind = (
            "real-in-memory-fixed-adapter-probe"
            if real_mode
            else "synthetic-typed-real-output"
        )
        if (
            self.adapter_id != S1_GU_ADAPTER_ID
            or any(
                len(value) != 64
                for value in (
                    self.source_s1gt_contract_digest,
                    self.source_s1gk_contract_digest,
                    self.source_s1gh_result_digest,
                )
            )
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or len(self.transition_digests) != S1_GF_TOTAL_BATCH_COUNT
            or len(self.transition_envelope_digests) != S1_GF_TOTAL_BATCH_COUNT
            or self.terminal_carrier_digests
            != tuple(item.carrier_digest for item in carriers)
            or self.terminal_output_digests
            != tuple(item.output_digest for item in outputs)
            or self.common_receipt_digests
            != tuple(item.receipt_digest for item in receipts)
            or self.arm_count != 6
            or self.transition_call_count != S1_GF_TOTAL_BATCH_COUNT
            or self.accounted_field_steps != S1_GF_TOTAL_BATCH_COUNT
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
            or sum(count for _, count in self.transition_kind_counts)
            != S1_GF_TOTAL_BATCH_COUNT
            or any(
                item.field_execution_kind != expected_execution_kind
                for item in outputs
            )
            or any(
                value is not True
                for value in (
                    self.all_batches_consumed_once_in_order,
                    self.all_transitions_validated_by_shared_envelope,
                    self.all_outputs_and_receipts_bound,
                    self.source_states_preserved,
                    self.fixed_adapters_preserved,
                    self.atomic_return_complete,
                )
            )
            or self.real_kernel_called_by_adapter is not real_mode
            or any(
                value is not False
                for value in (
                    self.full_chain_opened,
                    self.persistence_performed,
                    self.claims_permitted,
                    self.memory_decision_permitted,
                )
            )
            or self.decision != expected_decision
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GUSixArmCountingAdapterError(
                "S1-GU changed budget, atomicity, execution, or claim boundary"
            )
        object.__setattr__(self, "terminal_carriers", carriers)
        object.__setattr__(self, "outputs", outputs)
        object.__setattr__(self, "receipts", receipts)


def run_e1_formation_s1gu_six_arm_counting_adapter(
    scope: E1FormationS1GTSixArmReleaseScopeContract,
    source_contract: E1FormationS1GKFixedAdapterRealWrapperContract,
    bridge: E1FormationS1GHFreshFieldBridgeResult,
    *,
    carrier_transition: CarrierTransition = (
        advance_e1_formation_s1gn_live_field_carrier_synthetically
    ),
    terminal_output_factory: TerminalOutputFactory = (
        build_e1_formation_s1go_synthetic_terminal_output
    ),
) -> E1FormationS1GUSixArmCountingAdapterResult:
    """Consume the bounded six-arm shape with injected transitions only."""

    if (
        not isinstance(scope, E1FormationS1GTSixArmReleaseScopeContract)
        or not isinstance(source_contract, E1FormationS1GKFixedAdapterRealWrapperContract)
        or not isinstance(bridge, E1FormationS1GHFreshFieldBridgeResult)
        or not callable(carrier_transition)
        or not callable(terminal_output_factory)
    ):
        raise E1FormationS1GUSixArmCountingAdapterError(
            "S1-GU requires typed scope, source contract, bridge, and injections"
        )
    scope.__post_init__()
    source_contract.__post_init__()
    bridge.__post_init__()
    fresh_bindings = tuple(bridge.fresh_bindings)
    role_order = tuple((item.refinement_id, item.role_id) for item in fresh_bindings)
    if (
        scope.source_s1gk_contract_digest != source_contract.contract_digest
        or scope.execution_permitted is not False
        or source_contract.execution_permitted is not False
        or scope.fixed_adapter_arm_count != 6
        or role_order != scope.role_order
        or role_order != source_contract.role_order
        or source_contract.source_s1gh_result_digest != bridge.result_digest
        or len(fresh_bindings) != 6
    ):
        raise E1FormationS1GUSixArmCountingAdapterError(
            "S1-GU source scope, bridge, or role order changed"
        )

    states_before = tuple(
        _digest(_state_payload(item.invocation.source_state)) for item in fresh_bindings
    )
    adapters_before = tuple(
        _adapter_digest(item.invocation.fixed_adapter) for item in fresh_bindings
    )
    pending_envelopes = []
    pending_carriers = []
    pending_outputs = []
    pending_receipts = []
    try:
        for fresh in fresh_bindings:
            carrier = build_e1_formation_s1gn_initial_live_field_carrier(fresh)
            for expected_index, batch in enumerate(
                fresh.invocation.context.probe_plan.handoff.batches
            ):
                transition = carrier_transition(fresh, batch, carrier)
                envelope = bind_e1_formation_s1gq_carrier_transition_envelope(
                    transition
                )
                if not isinstance(envelope, E1FormationS1GQCarrierTransitionEnvelope):
                    raise E1FormationS1GUSixArmCountingAdapterError(
                        "S1-GU transition returned no S1-GQ envelope"
                    )
                envelope.__post_init__()
                if (
                    envelope.previous_carrier is not carrier
                    or envelope.next_carrier.fresh_binding is not fresh
                    or envelope.binding_digest != fresh.binding_digest
                    or envelope.batch_index != expected_index
                    or envelope.batch_step_start_tick != batch.step_time.start_tick
                    or envelope.batch_step_end_tick != batch.step_time.end_tick
                    or envelope.batch_source_support_count != batch.event_count
                    or envelope.accounted_field_steps != 1
                    or envelope.persistence_performed is not False
                    or envelope.claims_permitted is not False
                ):
                    raise E1FormationS1GUSixArmCountingAdapterError(
                        "S1-GU transition route, order, support, or scope changed"
                    )
                pending_envelopes.append(envelope)
                carrier = envelope.next_carrier
            output = terminal_output_factory(fresh, carrier)
            if not isinstance(output, E1FormationS1GIFixedAdapterRealOutput):
                raise E1FormationS1GUSixArmCountingAdapterError(
                    "S1-GU terminal factory returned no typed output"
                )
            output.__post_init__()
            receipt = convert_e1_formation_s1gi_fixed_adapter_output(fresh, output)
            pending_carriers.append(carrier)
            pending_outputs.append(output)
            pending_receipts.append(receipt)
    except E1FormationS1GUSixArmCountingAdapterError:
        raise
    except Exception as exc:
        raise E1FormationS1GUSixArmCountingAdapterError(
            "S1-GU aborted; no partial aggregate returned"
        ) from exc

    envelopes = tuple(pending_envelopes)
    carriers = tuple(pending_carriers)
    outputs = tuple(pending_outputs)
    receipts = tuple(pending_receipts)
    states_after = tuple(
        _digest(_state_payload(item.invocation.source_state)) for item in fresh_bindings
    )
    adapters_after = tuple(
        _adapter_digest(item.invocation.fixed_adapter) for item in fresh_bindings
    )
    refinement_steps = tuple(
        (
            refinement,
            sum(
                envelope.previous_carrier.fresh_binding.refinement_id == refinement
                for envelope in envelopes
            ),
        )
        for refinement in ("r2", "r4", "r8")
    )
    kind_counts = tuple(
        (kind, sum(envelope.transition_kind == kind for envelope in envelopes))
        for kind in ("synthetic-no-field-advance", "real-field-advance")
        if any(envelope.transition_kind == kind for envelope in envelopes)
    )
    actual_field_steps = sum(
        item.actual_field_steps_executed for item in envelopes
    )
    real_mode, decision, reason = _s1gu_execution_mode(
        kind_counts,
        actual_field_steps,
    )
    values = {
        "adapter_id": S1_GU_ADAPTER_ID,
        "source_s1gt_contract_digest": scope.contract_digest,
        "source_s1gk_contract_digest": source_contract.contract_digest,
        "source_s1gh_result_digest": bridge.result_digest,
        "role_order": role_order,
        "refinement_step_counts": refinement_steps,
        "transition_digests": tuple(item.transition_digest for item in envelopes),
        "transition_envelope_digests": tuple(
            item.envelope_digest for item in envelopes
        ),
        "terminal_carrier_digests": tuple(item.carrier_digest for item in carriers),
        "terminal_output_digests": tuple(item.output_digest for item in outputs),
        "common_receipt_digests": tuple(item.receipt_digest for item in receipts),
        "arm_count": len(fresh_bindings),
        "transition_call_count": len(envelopes),
        "accounted_field_steps": sum(item.accounted_field_steps for item in envelopes),
        "actual_field_steps_executed": actual_field_steps,
        "source_support_count": sum(
            item.batch_source_support_count for item in envelopes
        ),
        "terminal_carrier_count": len(carriers),
        "terminal_output_count": len(outputs),
        "common_receipt_count": len(receipts),
        "transition_kind_counts": kind_counts,
        "all_batches_consumed_once_in_order": len(envelopes)
        == scope.planned_real_transition_count,
        "all_transitions_validated_by_shared_envelope": all(
            isinstance(item, E1FormationS1GQCarrierTransitionEnvelope)
            for item in envelopes
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
        "source_states_preserved": states_before == states_after,
        "fixed_adapters_preserved": adapters_before == adapters_after,
        "atomic_return_complete": len(carriers) == len(outputs) == len(receipts) == 6,
        "real_kernel_called_by_adapter": real_mode,
        "full_chain_opened": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "memory_decision_permitted": False,
        "decision": decision,
        "reason": reason,
    }
    payload = {
        name: value
        for name, value in values.items()
        if name not in {"terminal_carriers", "outputs", "receipts"}
    }
    return E1FormationS1GUSixArmCountingAdapterResult(
        **values,
        result_digest=_digest(payload),
        terminal_carriers=carriers,
        outputs=outputs,
        receipts=receipts,
    )
