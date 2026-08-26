"""S1-GL private six-arm wrapper behind a synthetic-only execution gate."""

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
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest, _state_payload
from .receptor_proposal_handoff import ReceptorProposalBatch


class E1FormationS1GLPrivateFixedAdapterWrapperError(ValueError):
    """Raised when S1-GL crosses its injected synthetic-only boundary."""


S1_GL_WRAPPER_ID = "e1.private-fixed-adapter-wrapper.s1gl.v1"
S1_GL_GATE_ID = "e1.private-wrapper-synthetic-only-gate.s1gl.v1"


@dataclass(frozen=True, slots=True)
class E1FormationS1GLSyntheticOnlyGate:
    gate_id: str
    synthetic: bool
    expected_arm_count: int
    expected_batch_kernel_calls: int
    injected_batch_kernel_required: bool
    injected_terminal_factory_required: bool
    real_batch_adapter_permitted: bool
    real_field_execution_permitted: bool
    retry_permitted: bool
    persistence_permitted: bool
    gate_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "gate_digest"
        }
        if (
            self.gate_id != S1_GL_GATE_ID
            or self.synthetic is not True
            or self.expected_arm_count != 6
            or self.expected_batch_kernel_calls != S1_GF_TOTAL_BATCH_COUNT
            or self.injected_batch_kernel_required is not True
            or self.injected_terminal_factory_required is not True
            or any(
                value is not False
                for value in (
                    self.real_batch_adapter_permitted,
                    self.real_field_execution_permitted,
                    self.retry_permitted,
                    self.persistence_permitted,
                )
            )
            or self.gate_digest != _digest(payload)
        ):
            raise E1FormationS1GLPrivateFixedAdapterWrapperError(
                "S1-GL gate changed or opened real execution"
            )


def build_e1_formation_s1gl_synthetic_only_gate(
) -> E1FormationS1GLSyntheticOnlyGate:
    """Build the only gate accepted by the S1-GL wrapper."""

    values = {
        "gate_id": S1_GL_GATE_ID,
        "synthetic": True,
        "expected_arm_count": 6,
        "expected_batch_kernel_calls": S1_GF_TOTAL_BATCH_COUNT,
        "injected_batch_kernel_required": True,
        "injected_terminal_factory_required": True,
        "real_batch_adapter_permitted": False,
        "real_field_execution_permitted": False,
        "retry_permitted": False,
        "persistence_permitted": False,
    }
    return E1FormationS1GLSyntheticOnlyGate(
        **values,
        gate_digest=_digest(values),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GLSyntheticBatchReceipt:
    binding_digest: str
    refinement_id: str
    role_id: str
    batch_index: int
    step_start_tick: int
    step_end_tick: int
    source_support_count: int
    current_field_token_digest: str
    next_field_token_digest: str
    accounted_field_steps: int
    actual_field_steps_executed: int
    synthetic: bool
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if (
            any(
                len(value) != 64
                for value in (
                    self.binding_digest,
                    self.current_field_token_digest,
                    self.next_field_token_digest,
                )
            )
            or (self.refinement_id, self.role_id) not in S1_GF_ROLE_ORDER
            or self.batch_index < 0
            or self.step_start_tick < 0
            or self.step_end_tick <= self.step_start_tick
            or self.source_support_count < 0
            or self.accounted_field_steps != 1
            or self.actual_field_steps_executed != 0
            or self.synthetic is not True
            or self.receipt_digest != _digest(payload)
        ):
            raise E1FormationS1GLPrivateFixedAdapterWrapperError(
                "S1-GL batch receipt changed or reports real execution"
            )


def build_e1_formation_s1gl_synthetic_batch_receipt(
    fresh: E1FormationS1GHFreshFieldBinding,
    batch: ReceptorProposalBatch,
    current_field_token_digest: str,
) -> E1FormationS1GLSyntheticBatchReceipt:
    """Advance only a synthetic digest token for one bound batch."""

    next_token = _digest(
        (
            "s1gl-synthetic-field-token",
            fresh.binding_digest,
            current_field_token_digest,
            batch.batch_index,
            batch.step_time.start_tick,
            batch.step_time.end_tick,
            batch.event_count,
        )
    )
    values = {
        "binding_digest": fresh.binding_digest,
        "refinement_id": fresh.refinement_id,
        "role_id": fresh.role_id,
        "batch_index": batch.batch_index,
        "step_start_tick": batch.step_time.start_tick,
        "step_end_tick": batch.step_time.end_tick,
        "source_support_count": batch.event_count,
        "current_field_token_digest": current_field_token_digest,
        "next_field_token_digest": next_token,
        "accounted_field_steps": 1,
        "actual_field_steps_executed": 0,
        "synthetic": True,
    }
    return E1FormationS1GLSyntheticBatchReceipt(
        **values,
        receipt_digest=_digest(values),
    )


def build_e1_formation_s1gl_synthetic_terminal_output(
    fresh: E1FormationS1GHFreshFieldBinding,
    terminal_field_token_digest: str,
) -> E1FormationS1GIFixedAdapterRealOutput:
    """Build deterministic synthetic terminal vectors from a validated token."""

    if len(terminal_field_token_digest) != 64:
        raise E1FormationS1GLPrivateFixedAdapterWrapperError(
            "S1-GL terminal token is not a digest"
        )
    size = len(fresh.ordered_neuron_ids)
    seed = int(terminal_field_token_digest[:8], 16) / 0xFFFFFFFF
    activation = tuple(
        seed * (index + 1) / (2.0 * size) for index in range(size)
    )
    afterimage = tuple(-value / 2.0 for value in activation)
    return build_e1_formation_s1gi_synthetic_typed_output(
        fresh,
        activation,
        afterimage,
    )


BatchKernel = Callable[
    [E1FormationS1GHFreshFieldBinding, ReceptorProposalBatch, str],
    E1FormationS1GLSyntheticBatchReceipt,
]
TerminalOutputFactory = Callable[
    [E1FormationS1GHFreshFieldBinding, str],
    E1FormationS1GIFixedAdapterRealOutput,
]


@dataclass(frozen=True, slots=True)
class E1FormationS1GLPrivateFixedAdapterWrapperResult:
    wrapper_id: str
    source_s1gk_contract_digest: str
    source_s1gh_result_digest: str
    gate_digest: str
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    batch_receipt_digests: tuple[str, ...]
    terminal_output_digests: tuple[str, ...]
    common_receipt_digests: tuple[str, ...]
    arm_count: int
    injected_batch_kernel_calls: int
    accounted_field_steps: int
    actual_field_steps_executed: int
    source_support_count: int
    terminal_output_count: int
    common_receipt_count: int
    all_batches_consumed_once_in_order: bool
    all_field_tokens_contiguous: bool
    all_outputs_and_receipts_bound: bool
    fresh_fields_preserved: bool
    source_states_preserved: bool
    fixed_adapters_preserved: bool
    atomic_return_complete: bool
    real_batch_adapter_called: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    result_digest: str
    outputs: tuple[E1FormationS1GIFixedAdapterRealOutput, ...] = field(
        repr=False,
        compare=False,
    )
    receipts: tuple[E1FormationS1GIFixedAdapterCommonProbeReceipt, ...] = field(
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        outputs = tuple(self.outputs)
        receipts = tuple(self.receipts)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"outputs", "receipts", "result_digest"}
        }
        if (
            self.wrapper_id != S1_GL_WRAPPER_ID
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
            or len(self.batch_receipt_digests) != S1_GF_TOTAL_BATCH_COUNT
            or self.terminal_output_digests
            != tuple(item.output_digest for item in outputs)
            or self.common_receipt_digests
            != tuple(item.receipt_digest for item in receipts)
            or self.arm_count != 6
            or self.injected_batch_kernel_calls != S1_GF_TOTAL_BATCH_COUNT
            or self.accounted_field_steps != S1_GF_TOTAL_BATCH_COUNT
            or self.actual_field_steps_executed != 0
            or self.source_support_count != S1_GJ_TOTAL_SUPPORT_COUNT
            or (self.terminal_output_count, self.common_receipt_count) != (6, 6)
            or len(outputs) != 6
            or len(receipts) != 6
            or any(
                value is not True
                for value in (
                    self.all_batches_consumed_once_in_order,
                    self.all_field_tokens_contiguous,
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
                    self.real_batch_adapter_called,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "PRIVATE_SIX_ARM_WRAPPER_SYNTHETICALLY_VALIDATED_REAL_BATCH_ADAPTER_CLOSED"
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GLPrivateFixedAdapterWrapperError(
                "S1-GL aggregate changed or opened real execution"
            )
        object.__setattr__(self, "outputs", outputs)
        object.__setattr__(self, "receipts", receipts)


def run_e1_formation_s1gl_private_fixed_adapter_wrapper(
    contract: E1FormationS1GKFixedAdapterRealWrapperContract,
    bridge: E1FormationS1GHFreshFieldBridgeResult,
    gate: E1FormationS1GLSyntheticOnlyGate,
    *,
    batch_kernel: BatchKernel,
    terminal_output_factory: TerminalOutputFactory,
) -> E1FormationS1GLPrivateFixedAdapterWrapperResult:
    """Exercise wrapper control flow using injected synthetic functions only."""

    if (
        not isinstance(contract, E1FormationS1GKFixedAdapterRealWrapperContract)
        or not isinstance(bridge, E1FormationS1GHFreshFieldBridgeResult)
        or not isinstance(gate, E1FormationS1GLSyntheticOnlyGate)
        or not callable(batch_kernel)
        or not callable(terminal_output_factory)
    ):
        raise E1FormationS1GLPrivateFixedAdapterWrapperError(
            "S1-GL requires typed sources and two injected synthetic functions"
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
        or role_order != contract.role_order
        or role_order != S1_GF_ROLE_ORDER
        or len(fresh_bindings) != gate.expected_arm_count
    ):
        raise E1FormationS1GLPrivateFixedAdapterWrapperError(
            "S1-GL contract, bridge, or role order changed"
        )
    fields_before = tuple(
        _initial_field_digest(item.fresh_field) for item in fresh_bindings
    )
    states_before = tuple(
        _digest(_state_payload(item.invocation.source_state))
        for item in fresh_bindings
    )
    adapters_before = tuple(
        _adapter_digest(item.invocation.fixed_adapter) for item in fresh_bindings
    )
    pending_batch_receipts = []
    pending_outputs = []
    pending_receipts = []
    try:
        for fresh in fresh_bindings:
            plan = fresh.invocation.context.probe_plan
            current_token = _digest(
                (
                    "s1gl-initial-field-token",
                    fresh.binding_digest,
                    fresh.initial_field_digest,
                )
            )
            for expected_index, batch in enumerate(plan.handoff.batches):
                batch_result = batch_kernel(fresh, batch, current_token)
                if not isinstance(
                    batch_result, E1FormationS1GLSyntheticBatchReceipt
                ):
                    raise E1FormationS1GLPrivateFixedAdapterWrapperError(
                        "S1-GL batch kernel returned no typed synthetic receipt"
                    )
                batch_result.__post_init__()
                if (
                    batch_result.binding_digest != fresh.binding_digest
                    or (batch_result.refinement_id, batch_result.role_id)
                    != (fresh.refinement_id, fresh.role_id)
                    or batch_result.batch_index != expected_index
                    or batch_result.current_field_token_digest != current_token
                    or batch_result.step_start_tick != batch.step_time.start_tick
                    or batch_result.step_end_tick != batch.step_time.end_tick
                    or batch_result.source_support_count != batch.event_count
                ):
                    raise E1FormationS1GLPrivateFixedAdapterWrapperError(
                        "S1-GL batch route, order, support, or token changed"
                    )
                pending_batch_receipts.append(batch_result)
                current_token = batch_result.next_field_token_digest
            output = terminal_output_factory(fresh, current_token)
            if not isinstance(output, E1FormationS1GIFixedAdapterRealOutput):
                raise E1FormationS1GLPrivateFixedAdapterWrapperError(
                    "S1-GL terminal factory returned no typed S1-GI output"
                )
            output.__post_init__()
            if (
                output.binding_digest != fresh.binding_digest
                or output.field_execution_kind != "synthetic-typed-real-output"
                or output.actual_field_steps_executed != 0
            ):
                raise E1FormationS1GLPrivateFixedAdapterWrapperError(
                    "S1-GL terminal output crossed synthetic scope"
                )
            receipt = convert_e1_formation_s1gi_fixed_adapter_output(fresh, output)
            pending_outputs.append(output)
            pending_receipts.append(receipt)
    except E1FormationS1GLPrivateFixedAdapterWrapperError:
        raise
    except Exception as exc:
        raise E1FormationS1GLPrivateFixedAdapterWrapperError(
            "S1-GL injected wrapper function aborted; no aggregate returned"
        ) from exc

    batch_receipts = tuple(pending_batch_receipts)
    outputs = tuple(pending_outputs)
    receipts = tuple(pending_receipts)
    fields_after = tuple(
        _initial_field_digest(item.fresh_field) for item in fresh_bindings
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
            sum(item.refinement_id == refinement for item in batch_receipts),
        )
        for refinement in ("r2", "r4", "r8")
    )
    values = {
        "wrapper_id": S1_GL_WRAPPER_ID,
        "source_s1gk_contract_digest": contract.contract_digest,
        "source_s1gh_result_digest": bridge.result_digest,
        "gate_digest": gate.gate_digest,
        "role_order": role_order,
        "refinement_step_counts": refinement_steps,
        "batch_receipt_digests": tuple(
            item.receipt_digest for item in batch_receipts
        ),
        "terminal_output_digests": tuple(item.output_digest for item in outputs),
        "common_receipt_digests": tuple(item.receipt_digest for item in receipts),
        "arm_count": len(fresh_bindings),
        "injected_batch_kernel_calls": len(batch_receipts),
        "accounted_field_steps": sum(
            item.accounted_field_steps for item in batch_receipts
        ),
        "actual_field_steps_executed": sum(
            item.actual_field_steps_executed for item in batch_receipts
        ),
        "source_support_count": sum(
            item.source_support_count for item in batch_receipts
        ),
        "terminal_output_count": len(outputs),
        "common_receipt_count": len(receipts),
        "all_batches_consumed_once_in_order": len(batch_receipts)
        == gate.expected_batch_kernel_calls,
        "all_field_tokens_contiguous": all(
            previous.next_field_token_digest == current.current_field_token_digest
            for previous, current in zip(batch_receipts, batch_receipts[1:])
            if previous.binding_digest == current.binding_digest
        ),
        "all_outputs_and_receipts_bound": all(
            fresh.binding_digest == output.binding_digest == receipt.binding_digest
            for fresh, output, receipt in zip(
                fresh_bindings, outputs, receipts, strict=True
            )
        ),
        "fresh_fields_preserved": fields_before == fields_after,
        "source_states_preserved": states_before == states_after,
        "fixed_adapters_preserved": adapters_before == adapters_after,
        "atomic_return_complete": len(outputs) == len(receipts) == 6,
        "real_batch_adapter_called": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "PRIVATE_SIX_ARM_WRAPPER_SYNTHETICALLY_VALIDATED_"
            "REAL_BATCH_ADAPTER_CLOSED"
        ),
        "reason": (
            "private-six-arm-wrapper-consumed-2800-batches-through-injected-"
            "synthetic-kernel-and-produced-six-bound-outputs-and-receipts;"
            "real-batch-adapter-field-execution-retry-and-persistence-closed"
        ),
    }
    payload = {
        name: value
        for name, value in values.items()
        if name not in {"outputs", "receipts"}
    }
    return E1FormationS1GLPrivateFixedAdapterWrapperResult(
        **values,
        result_digest=_digest(payload),
        outputs=outputs,
        receipts=receipts,
    )
