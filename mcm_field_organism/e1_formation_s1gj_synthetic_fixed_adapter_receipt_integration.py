"""S1-GJ atomic integration of six synthetic fixed-adapter receipts."""

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
    convert_e1_formation_s1gi_fixed_adapter_output,
)
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest, _state_payload


class E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError(ValueError):
    """Raised when S1-GJ loses one role, receipt, or atomic boundary."""


S1_GJ_INTEGRATION_ID = "e1.synthetic-fixed-adapter-receipt-integration.s1gj.v1"
S1_GJ_TOTAL_SUPPORT_COUNT = 660
OutputFactory = Callable[
    [E1FormationS1GHFreshFieldBinding],
    E1FormationS1GIFixedAdapterRealOutput,
]


@dataclass(frozen=True, slots=True)
class E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationResult:
    integration_id: str
    source_s1gh_result_digest: str
    role_order: tuple[tuple[str, str], ...]
    output_digests: tuple[str, ...]
    receipt_digests: tuple[str, ...]
    refinement_receipt_counts: tuple[tuple[str, int], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    output_count: int
    receipt_count: int
    planned_field_steps: int
    actual_field_steps_executed: int
    total_source_support_count: int
    all_fresh_bindings_consumed_once_in_order: bool
    all_output_bindings_exact: bool
    all_receipt_bindings_exact: bool
    all_raw_vectors_lossless: bool
    all_causal_evidence_separate: bool
    fresh_fields_preserved: bool
    source_states_preserved: bool
    fixed_adapters_preserved: bool
    atomic_return_complete: bool
    field_kernel_called: bool
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
            self.integration_id != S1_GJ_INTEGRATION_ID
            or len(self.source_s1gh_result_digest) != 64
            or self.role_order != S1_GF_ROLE_ORDER
            or len(outputs) != 6
            or len(receipts) != 6
            or self.output_digests != tuple(item.output_digest for item in outputs)
            or self.receipt_digests
            != tuple(item.receipt_digest for item in receipts)
            or self.refinement_receipt_counts
            != (("r2", 2), ("r4", 2), ("r8", 2))
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or (self.output_count, self.receipt_count) != (6, 6)
            or self.planned_field_steps != S1_GF_TOTAL_BATCH_COUNT
            or self.actual_field_steps_executed != 0
            or self.total_source_support_count != S1_GJ_TOTAL_SUPPORT_COUNT
            or any(
                value is not True
                for value in (
                    self.all_fresh_bindings_consumed_once_in_order,
                    self.all_output_bindings_exact,
                    self.all_receipt_bindings_exact,
                    self.all_raw_vectors_lossless,
                    self.all_causal_evidence_separate,
                    self.fresh_fields_preserved,
                    self.source_states_preserved,
                    self.fixed_adapters_preserved,
                    self.atomic_return_complete,
                )
            )
            or any(
                value is not False
                for value in (
                    self.field_kernel_called,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "SIX_SYNTHETIC_FIXED_ADAPTER_RECEIPTS_ATOMICALLY_INTEGRATED_REAL_KERNEL_CLOSED"
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError(
                "S1-GJ aggregate changed, lost one role, or opened execution"
            )
        object.__setattr__(self, "outputs", outputs)
        object.__setattr__(self, "receipts", receipts)


def integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts(
    bridge: E1FormationS1GHFreshFieldBridgeResult,
    *,
    output_factory: OutputFactory,
) -> E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationResult:
    """Return six receipts only after every synthetic output validates."""

    if not isinstance(bridge, E1FormationS1GHFreshFieldBridgeResult) or not callable(
        output_factory
    ):
        raise E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError(
            "S1-GJ requires typed S1-GH bridge and injected output factory"
        )
    bridge.__post_init__()
    fresh_bindings = tuple(bridge.fresh_bindings)
    role_order = tuple(
        (item.refinement_id, item.role_id) for item in fresh_bindings
    )
    if (
        role_order != S1_GF_ROLE_ORDER
        or len(fresh_bindings) != 6
        or bridge.field_steps_executed != 0
        or bridge.field_kernel_called is not False
    ):
        raise E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError(
            "S1-GJ fresh-field source changed or opened execution"
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
    pending_outputs = []
    pending_receipts = []
    try:
        for fresh in fresh_bindings:
            output = output_factory(fresh)
            if not isinstance(output, E1FormationS1GIFixedAdapterRealOutput):
                raise E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError(
                    "S1-GJ output factory returned no typed S1-GI output"
                )
            output.__post_init__()
            if (
                output.binding_digest != fresh.binding_digest
                or output.field_execution_kind != "synthetic-typed-real-output"
                or output.actual_field_steps_executed != 0
            ):
                raise E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError(
                    "S1-GJ synthetic output route or execution kind changed"
                )
            receipt = convert_e1_formation_s1gi_fixed_adapter_output(fresh, output)
            if (
                receipt.binding_digest != fresh.binding_digest
                or (receipt.refinement_id, receipt.role_id)
                != (fresh.refinement_id, fresh.role_id)
            ):
                raise E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError(
                    "S1-GJ receipt route changed"
                )
            pending_outputs.append(output)
            pending_receipts.append(receipt)
    except E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError:
        raise
    except Exception as exc:
        raise E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError(
            "S1-GJ output integration aborted; no aggregate returned"
        ) from exc

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
    refinement_receipt_counts = tuple(
        (
            refinement,
            sum(item.refinement_id == refinement for item in receipts),
        )
        for refinement in ("r2", "r4", "r8")
    )
    refinement_step_counts = tuple(
        (
            refinement,
            sum(
                item.field_step_count
                for item in receipts
                if item.refinement_id == refinement
            ),
        )
        for refinement in ("r2", "r4", "r8")
    )
    values = {
        "integration_id": S1_GJ_INTEGRATION_ID,
        "source_s1gh_result_digest": bridge.result_digest,
        "role_order": role_order,
        "output_digests": tuple(item.output_digest for item in outputs),
        "receipt_digests": tuple(item.receipt_digest for item in receipts),
        "refinement_receipt_counts": refinement_receipt_counts,
        "refinement_step_counts": refinement_step_counts,
        "output_count": len(outputs),
        "receipt_count": len(receipts),
        "planned_field_steps": sum(item.field_step_count for item in receipts),
        "actual_field_steps_executed": sum(
            item.actual_field_steps_executed for item in outputs
        ),
        "total_source_support_count": sum(
            item.source_support_count for item in receipts
        ),
        "all_fresh_bindings_consumed_once_in_order": tuple(
            item.binding_digest for item in fresh_bindings
        )
        == tuple(item.binding_digest for item in receipts),
        "all_output_bindings_exact": all(
            output.binding_digest == fresh.binding_digest
            for fresh, output in zip(fresh_bindings, outputs, strict=True)
        ),
        "all_receipt_bindings_exact": all(
            receipt.binding_digest == fresh.binding_digest
            for fresh, receipt in zip(fresh_bindings, receipts, strict=True)
        ),
        "all_raw_vectors_lossless": all(
            output.activation == receipt.activation_vector
            and output.afterimage == receipt.afterimage_vector
            and fresh.ordered_neuron_ids == receipt.ordered_neuron_ids
            for fresh, output, receipt in zip(
                fresh_bindings, outputs, receipts, strict=True
            )
        ),
        "all_causal_evidence_separate": all(
            receipt.source_state_digest is not None
            and receipt.fixed_adapter_digest is not None
            and receipt.state_digest_before is None
            and receipt.state_digest_after is None
            for receipt in receipts
        ),
        "fresh_fields_preserved": fields_before == fields_after,
        "source_states_preserved": states_before == states_after,
        "fixed_adapters_preserved": adapters_before == adapters_after,
        "atomic_return_complete": len(outputs) == len(receipts) == 6,
        "field_kernel_called": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "SIX_SYNTHETIC_FIXED_ADAPTER_RECEIPTS_ATOMICALLY_INTEGRATED_"
            "REAL_KERNEL_CLOSED"
        ),
        "reason": (
            "six-s1gh-bindings-produced-six-typed-s1gi-outputs-and-six-common-"
            "receipts-in-order;2800-planned-steps;660-supports;zero-real-"
            "field-steps;aggregate-returned-only-after-full-validation"
        ),
    }
    payload = {
        name: value
        for name, value in values.items()
        if name not in {"outputs", "receipts"}
    }
    return E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationResult(
        **values,
        result_digest=_digest(payload),
        outputs=outputs,
        receipts=receipts,
    )
