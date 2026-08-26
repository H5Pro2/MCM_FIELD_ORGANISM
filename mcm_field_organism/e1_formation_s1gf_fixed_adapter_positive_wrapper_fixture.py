"""S1-GF synthetic positive fixed-adapter wrapper structure fixture."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .e1_formation_s1gd_fixed_adapter_invocation_binding import (
    E1FormationS1GDFixedAdapterInvocation,
    E1FormationS1GDFixedAdapterInvocationBindingResult,
)
from .e1_formation_s1fw_synthetic_live_state_handoff import _adapter_digest
from .e1_refined_formation_runner import _digest, _state_payload
from .receptor_proposal_handoff import ReceptorProposalBatch


class E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(ValueError):
    """Raised when S1-GF changes order, accounting, or synthetic scope."""


S1_GF_FIXTURE_ID = "e1.fixed-adapter-positive-wrapper-fixture.s1gf.v1"
S1_GF_GATE_ID = "e1.synthetic-positive-counting-gate.s1gf.v1"
S1_GF_ROLE_ORDER = (
    ("r2", "fixed-adapter-ab"),
    ("r2", "fixed-adapter-ba"),
    ("r4", "fixed-adapter-ab"),
    ("r4", "fixed-adapter-ba"),
    ("r8", "fixed-adapter-ab"),
    ("r8", "fixed-adapter-ba"),
)
S1_GF_REFINEMENT_BATCH_COUNTS = (("r2", 400), ("r4", 800), ("r8", 1600))
S1_GF_TOTAL_BATCH_COUNT = 2800


@dataclass(frozen=True, slots=True)
class E1FormationS1GFSyntheticPositiveGate:
    gate_id: str
    synthetic: bool
    expected_invocation_count: int
    expected_batch_count: int
    positive_plan_consumption_permitted: bool
    injected_fake_kernel_required: bool
    real_kernel_permitted: bool
    field_object_permitted: bool
    observed_vectors_permitted: bool
    persistence_permitted: bool
    gate_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "gate_digest"
        }
        if (
            self.gate_id != S1_GF_GATE_ID
            or self.synthetic is not True
            or self.expected_invocation_count != 6
            or self.expected_batch_count != S1_GF_TOTAL_BATCH_COUNT
            or self.positive_plan_consumption_permitted is not True
            or self.injected_fake_kernel_required is not True
            or any(
                value is not False
                for value in (
                    self.real_kernel_permitted,
                    self.field_object_permitted,
                    self.observed_vectors_permitted,
                    self.persistence_permitted,
                )
            )
            or self.gate_digest != _digest(payload)
        ):
            raise E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(
                "S1-GF gate changed or opened a real execution path"
            )


def build_e1_formation_s1gf_synthetic_positive_gate(
) -> E1FormationS1GFSyntheticPositiveGate:
    """Build the exact gate for positive synthetic batch accounting."""

    values = {
        "gate_id": S1_GF_GATE_ID,
        "synthetic": True,
        "expected_invocation_count": 6,
        "expected_batch_count": S1_GF_TOTAL_BATCH_COUNT,
        "positive_plan_consumption_permitted": True,
        "injected_fake_kernel_required": True,
        "real_kernel_permitted": False,
        "field_object_permitted": False,
        "observed_vectors_permitted": False,
        "persistence_permitted": False,
    }
    return E1FormationS1GFSyntheticPositiveGate(
        **values,
        gate_digest=_digest(values),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GFCountingReceipt:
    source_invocation_digest: str
    binding_digest: str
    refinement_id: str
    role_id: str
    batch_index: int
    step_start_tick: int
    step_end_tick: int
    accounted_field_steps: int
    actual_field_steps_executed: int
    synthetic: bool
    observed_vectors_present: bool
    persistence_performed: bool
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
                for value in (self.source_invocation_digest, self.binding_digest)
            )
            or (self.refinement_id, self.role_id) not in S1_GF_ROLE_ORDER
            or self.batch_index < 0
            or self.step_start_tick < 0
            or self.step_end_tick <= self.step_start_tick
            or self.accounted_field_steps != 1
            or self.actual_field_steps_executed != 0
            or self.synthetic is not True
            or self.observed_vectors_present is not False
            or self.persistence_performed is not False
            or self.receipt_digest != _digest(payload)
        ):
            raise E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(
                "S1-GF counting receipt changed or reports real work"
            )


def build_e1_formation_s1gf_counting_receipt(
    invocation: E1FormationS1GDFixedAdapterInvocation,
    batch: ReceptorProposalBatch,
) -> E1FormationS1GFCountingReceipt:
    """Return one synthetic receipt without constructing or advancing a field."""

    values = {
        "source_invocation_digest": invocation.invocation_digest,
        "binding_digest": invocation.binding_digest,
        "refinement_id": invocation.context.binding.refinement_id,
        "role_id": invocation.context.binding.role_id,
        "batch_index": batch.batch_index,
        "step_start_tick": batch.step_time.start_tick,
        "step_end_tick": batch.step_time.end_tick,
        "accounted_field_steps": 1,
        "actual_field_steps_executed": 0,
        "synthetic": True,
        "observed_vectors_present": False,
        "persistence_performed": False,
    }
    return E1FormationS1GFCountingReceipt(
        **values,
        receipt_digest=_digest(values),
    )


CountingKernel = Callable[
    [E1FormationS1GDFixedAdapterInvocation, ReceptorProposalBatch],
    E1FormationS1GFCountingReceipt,
]


@dataclass(frozen=True, slots=True)
class E1FormationS1GFFixedAdapterPositiveWrapperFixtureResult:
    fixture_id: str
    source_s1gd_result_digest: str
    gate_digest: str
    role_order: tuple[tuple[str, str], ...]
    role_batch_counts: tuple[tuple[str, str, int], ...]
    refinement_batch_counts: tuple[tuple[str, int], ...]
    receipt_digests: tuple[str, ...]
    invocation_count: int
    positive_batches_consumed: int
    injected_fake_kernel_calls: int
    accounted_field_steps: int
    actual_field_steps_executed: int
    all_batches_consumed_once_in_order: bool
    source_states_preserved: bool
    fixed_adapters_preserved: bool
    aggregate_return_is_atomic: bool
    real_kernel_called: bool
    field_object_constructed: bool
    observed_vectors_present: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    result_digest: str
    receipts: tuple[E1FormationS1GFCountingReceipt, ...] = field(
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        receipts = tuple(self.receipts)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"receipts", "result_digest"}
        }
        if (
            self.fixture_id != S1_GF_FIXTURE_ID
            or len(self.source_s1gd_result_digest) != 64
            or len(self.gate_digest) != 64
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_batch_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or len(self.role_batch_counts) != 6
            or len(receipts) != S1_GF_TOTAL_BATCH_COUNT
            or self.receipt_digests
            != tuple(item.receipt_digest for item in receipts)
            or self.invocation_count != 6
            or any(
                value != S1_GF_TOTAL_BATCH_COUNT
                for value in (
                    self.positive_batches_consumed,
                    self.injected_fake_kernel_calls,
                    self.accounted_field_steps,
                )
            )
            or self.actual_field_steps_executed != 0
            or any(
                value is not True
                for value in (
                    self.all_batches_consumed_once_in_order,
                    self.source_states_preserved,
                    self.fixed_adapters_preserved,
                    self.aggregate_return_is_atomic,
                )
            )
            or any(
                value is not False
                for value in (
                    self.real_kernel_called,
                    self.field_object_constructed,
                    self.observed_vectors_present,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "FIXED_ADAPTER_POSITIVE_STRUCTURE_SYNTHETICALLY_VALIDATED_REAL_PATH_CLOSED"
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(
                "S1-GF aggregate changed or crossed synthetic scope"
            )
        object.__setattr__(self, "receipts", receipts)


def run_e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture(
    bindings: E1FormationS1GDFixedAdapterInvocationBindingResult,
    gate: E1FormationS1GFSyntheticPositiveGate,
    *,
    counting_kernel: CountingKernel,
) -> E1FormationS1GFFixedAdapterPositiveWrapperFixtureResult:
    """Consume all positive plans through an injected zero-work fake kernel."""

    if (
        not isinstance(bindings, E1FormationS1GDFixedAdapterInvocationBindingResult)
        or not isinstance(gate, E1FormationS1GFSyntheticPositiveGate)
        or not callable(counting_kernel)
    ):
        raise E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(
            "S1-GF requires typed bindings, gate, and injected counting kernel"
        )
    bindings.__post_init__()
    gate.__post_init__()
    invocations = tuple(bindings.invocations)
    observed_role_order = tuple(
        (item.context.binding.refinement_id, item.context.binding.role_id)
        for item in invocations
    )
    if (
        bindings.wrapper_implementation_permitted is not False
        or observed_role_order != S1_GF_ROLE_ORDER
        or len(invocations) != gate.expected_invocation_count
    ):
        raise E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(
            "S1-GF source chain or six-role order changed"
        )

    role_batch_counts = []
    for invocation in invocations:
        invocation.__post_init__()
        plan = invocation.context.probe_plan
        batches = tuple(plan.handoff.batches)
        if (
            len(batches) != len(plan.proposal_steps)
            or any(
                batch.batch_index != index
                or batch.step_time != plan.proposal_steps[index]
                for index, batch in enumerate(batches)
            )
        ):
            raise E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(
                "S1-GF probe batches changed order or lost proposal steps"
            )
        role_batch_counts.append(
            (
                invocation.context.binding.refinement_id,
                invocation.context.binding.role_id,
                len(batches),
            )
        )
    if sum(item[2] for item in role_batch_counts) != gate.expected_batch_count:
        raise E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(
            "S1-GF positive batch budget changed"
        )

    states_before = tuple(_digest(_state_payload(item.source_state)) for item in invocations)
    adapters_before = tuple(_adapter_digest(item.fixed_adapter) for item in invocations)
    pending = []
    try:
        for invocation in invocations:
            for batch in invocation.context.probe_plan.handoff.batches:
                receipt = counting_kernel(invocation, batch)
                if not isinstance(receipt, E1FormationS1GFCountingReceipt):
                    raise E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(
                        "S1-GF injected kernel returned no typed counting receipt"
                    )
                receipt.__post_init__()
                expected = (
                    invocation.invocation_digest,
                    invocation.binding_digest,
                    invocation.context.binding.refinement_id,
                    invocation.context.binding.role_id,
                    batch.batch_index,
                    batch.step_time.start_tick,
                    batch.step_time.end_tick,
                )
                observed = (
                    receipt.source_invocation_digest,
                    receipt.binding_digest,
                    receipt.refinement_id,
                    receipt.role_id,
                    receipt.batch_index,
                    receipt.step_start_tick,
                    receipt.step_end_tick,
                )
                if observed != expected:
                    raise E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(
                        "S1-GF counting receipt route or order changed"
                    )
                pending.append(receipt)
    except E1FormationS1GFFixedAdapterPositiveWrapperFixtureError:
        raise
    except Exception as exc:
        raise E1FormationS1GFFixedAdapterPositiveWrapperFixtureError(
            "S1-GF injected counting kernel aborted; no aggregate returned"
        ) from exc

    receipts = tuple(pending)
    states_after = tuple(_digest(_state_payload(item.source_state)) for item in invocations)
    adapters_after = tuple(_adapter_digest(item.fixed_adapter) for item in invocations)
    refinement_counts = tuple(
        (
            refinement,
            sum(item.refinement_id == refinement for item in receipts),
        )
        for refinement in ("r2", "r4", "r8")
    )
    values = {
        "fixture_id": S1_GF_FIXTURE_ID,
        "source_s1gd_result_digest": bindings.result_digest,
        "gate_digest": gate.gate_digest,
        "role_order": observed_role_order,
        "role_batch_counts": tuple(role_batch_counts),
        "refinement_batch_counts": refinement_counts,
        "receipt_digests": tuple(item.receipt_digest for item in receipts),
        "invocation_count": len(invocations),
        "positive_batches_consumed": len(receipts),
        "injected_fake_kernel_calls": len(receipts),
        "accounted_field_steps": sum(item.accounted_field_steps for item in receipts),
        "actual_field_steps_executed": sum(
            item.actual_field_steps_executed for item in receipts
        ),
        "all_batches_consumed_once_in_order": len(receipts)
        == gate.expected_batch_count,
        "source_states_preserved": states_before == states_after,
        "fixed_adapters_preserved": adapters_before == adapters_after,
        "aggregate_return_is_atomic": True,
        "real_kernel_called": False,
        "field_object_constructed": False,
        "observed_vectors_present": any(
            item.observed_vectors_present for item in receipts
        ),
        "persistence_performed": any(item.persistence_performed for item in receipts),
        "claims_permitted": False,
        "decision": (
            "FIXED_ADAPTER_POSITIVE_STRUCTURE_SYNTHETICALLY_VALIDATED_"
            "REAL_PATH_CLOSED"
        ),
        "reason": (
            "six-positive-plans-consumed-in-bound-order-through-injected-"
            "counting-kernel;2800-accounted-steps;zero-real-field-steps;"
            "aggregate-returned-only-after-all-receipts-validated"
        ),
    }
    return E1FormationS1GFFixedAdapterPositiveWrapperFixtureResult(
        **values,
        result_digest=_digest(values),
        receipts=receipts,
    )
