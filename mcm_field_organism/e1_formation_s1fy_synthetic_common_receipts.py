"""S1-FY atomic synthetic common receipts for all thirty probe slots."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
import math

from .e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIPreparedInputs,
)
from .e1_formation_s1fw_synthetic_live_state_handoff import (
    E1FormationS1FWSyntheticLiveStateHandoffResult,
    E1FormationS1FWSyntheticSlotHandoff,
)
from .e1_formation_s1fx_common_probe_receipt_contract import (
    E1FormationS1FXCommonProbeReceiptContract,
    S1_FX_RECEIPT_SCHEMA,
)
from .e1_refined_formation_runner import _digest, _state_payload


class E1FormationS1FYSyntheticCommonReceiptError(ValueError):
    """Raised when a synthetic receipt is incomplete or opens execution."""


S1_FY_COORDINATOR_ID = "e1.synthetic-common-probe-receipts.s1fy.v1"
S1_FY_EXECUTION_KIND = "synthetic-zero-step"
S1_FY_KERNEL_BY_BRANCH = {
    "neutral-p0": "synthetic-neutral-p0-counting-adapter",
    "frozen-e1": "synthetic-frozen-e1-counting-adapter",
    "fixed-adapter": "synthetic-fixed-adapter-counting-adapter",
}


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _branch(handoff: E1FormationS1FWSyntheticSlotHandoff) -> str:
    if handoff.binding.source_state_role is None:
        return "neutral-p0"
    if handoff.binding.fixed_adapter_derivation_required:
        return "fixed-adapter"
    return "frozen-e1"


@dataclass(frozen=True, slots=True)
class E1FormationS1FYCommonProbeReceipt:
    refinement_id: str
    role_id: str
    probe_mode: str
    binding_digest: str
    probe_source_digest: str
    initial_field_digest: str
    terminal_field_digest: str
    ordered_neuron_ids: tuple[str, ...]
    activation_vector: tuple[float, ...]
    afterimage_vector: tuple[float, ...]
    field_step_count: int
    source_support_count: int
    source_state_digest: str | None
    state_digest_before: str | None
    state_digest_after: str | None
    source_state_preserved: bool
    fixed_adapter_digest: str | None
    kernel_name: str
    field_execution_kind: str
    persistence_performed: bool
    claims_permitted: bool
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        branch = (
            "neutral-p0"
            if self.source_state_digest is None
            else "fixed-adapter"
            if self.fixed_adapter_digest is not None
            else "frozen-e1"
        )
        vectors = (tuple(self.activation_vector), tuple(self.afterimage_vector))
        if (
            tuple(self.__dataclass_fields__) != S1_FX_RECEIPT_SCHEMA
            or not all(
                _valid_digest(value)
                for value in (
                    self.binding_digest,
                    self.probe_source_digest,
                    self.initial_field_digest,
                    self.terminal_field_digest,
                    self.receipt_digest,
                )
            )
            or not self.ordered_neuron_ids
            or len(set(self.ordered_neuron_ids)) != len(self.ordered_neuron_ids)
            or any(len(vector) != len(self.ordered_neuron_ids) for vector in vectors)
            or any(not math.isfinite(value) for vector in vectors for value in vector)
            or self.initial_field_digest != self.terminal_field_digest
            or self.field_step_count != 0
            or self.source_support_count != 0
            or self.source_state_preserved is not True
            or self.kernel_name != S1_FY_KERNEL_BY_BRANCH[branch]
            or self.field_execution_kind != S1_FY_EXECUTION_KIND
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.receipt_digest != _digest(payload)
        ):
            raise E1FormationS1FYSyntheticCommonReceiptError(
                "S1-FY common receipt changed or contains field execution"
            )
        if branch == "neutral-p0" and any(
            value is not None
            for value in (
                self.state_digest_before,
                self.state_digest_after,
                self.fixed_adapter_digest,
            )
        ):
            raise E1FormationS1FYSyntheticCommonReceiptError(
                "S1-FY P0 receipt contains causal state evidence"
            )
        if branch == "frozen-e1" and (
            self.state_digest_before != self.source_state_digest
            or self.state_digest_after != self.source_state_digest
            or self.fixed_adapter_digest is not None
        ):
            raise E1FormationS1FYSyntheticCommonReceiptError(
                "S1-FY frozen receipt changed its state evidence"
            )
        if branch == "fixed-adapter" and (
            not _valid_digest(self.source_state_digest)
            or self.state_digest_before is not None
            or self.state_digest_after is not None
            or not _valid_digest(self.fixed_adapter_digest)
        ):
            raise E1FormationS1FYSyntheticCommonReceiptError(
                "S1-FY fixed receipt merged live-state and adapter evidence"
            )


SyntheticReceiptAdapter = Callable[
    [
        E1FormationS1FWSyntheticSlotHandoff,
        str,
        str,
        tuple[str, ...],
        tuple[float, ...],
        tuple[float, ...],
    ],
    E1FormationS1FYCommonProbeReceipt,
]


def _build_receipt(
    handoff: E1FormationS1FWSyntheticSlotHandoff,
    expected_branch: str,
    probe_source_digest: str,
    field_digest: str,
    neuron_ids: tuple[str, ...],
    activation: tuple[float, ...],
    afterimage: tuple[float, ...],
) -> E1FormationS1FYCommonProbeReceipt:
    branch = _branch(handoff)
    if branch != expected_branch:
        raise E1FormationS1FYSyntheticCommonReceiptError(
            "S1-FY counting adapter received the wrong causal branch"
        )
    state_digest = handoff.state_digest
    values = {
        "refinement_id": handoff.binding.refinement_id,
        "role_id": handoff.binding.role_id,
        "probe_mode": handoff.binding.probe_mode,
        "binding_digest": handoff.binding.binding_digest,
        "probe_source_digest": probe_source_digest,
        "initial_field_digest": field_digest,
        "terminal_field_digest": field_digest,
        "ordered_neuron_ids": neuron_ids,
        "activation_vector": activation,
        "afterimage_vector": afterimage,
        "field_step_count": 0,
        "source_support_count": 0,
        "source_state_digest": state_digest,
        "state_digest_before": state_digest if branch == "frozen-e1" else None,
        "state_digest_after": state_digest if branch == "frozen-e1" else None,
        "source_state_preserved": True,
        "fixed_adapter_digest": handoff.fixed_adapter_digest,
        "kernel_name": S1_FY_KERNEL_BY_BRANCH[branch],
        "field_execution_kind": S1_FY_EXECUTION_KIND,
        "persistence_performed": False,
        "claims_permitted": False,
    }
    return E1FormationS1FYCommonProbeReceipt(
        **values,
        receipt_digest=_digest(values),
    )


def build_s1fy_neutral_p0_receipt(*args: object) -> E1FormationS1FYCommonProbeReceipt:
    return _build_receipt(args[0], "neutral-p0", *args[1:])  # type: ignore[arg-type]


def build_s1fy_frozen_e1_receipt(*args: object) -> E1FormationS1FYCommonProbeReceipt:
    return _build_receipt(args[0], "frozen-e1", *args[1:])  # type: ignore[arg-type]


def build_s1fy_fixed_adapter_receipt(*args: object) -> E1FormationS1FYCommonProbeReceipt:
    return _build_receipt(args[0], "fixed-adapter", *args[1:])  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class E1FormationS1FYSyntheticCommonReceiptResult:
    coordinator_id: str
    source_s1fx_contract_digest: str
    source_s1fw_result_digest: str
    source_input_manifest_digest: str
    receipts: tuple[E1FormationS1FYCommonProbeReceipt, ...] = field(repr=False)
    receipt_digests: tuple[str, ...]
    branch_invocation_counts: tuple[tuple[str, int], ...]
    receipt_count: int
    distinct_receipt_count: int
    atomic_result_complete: bool
    source_states_preserved: bool
    common_neuron_order_preserved: bool
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
        receipts = tuple(self.receipts)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"receipts", "result_digest"}
        }
        if (
            self.coordinator_id != S1_FY_COORDINATOR_ID
            or any(
                not _valid_digest(value)
                for value in (
                    self.source_s1fx_contract_digest,
                    self.source_s1fw_result_digest,
                    self.source_input_manifest_digest,
                )
            )
            or len(receipts) != 30
            or self.receipt_digests != tuple(item.receipt_digest for item in receipts)
            or self.branch_invocation_counts
            != (("neutral-p0", 6), ("frozen-e1", 18), ("fixed-adapter", 6))
            or (self.receipt_count, self.distinct_receipt_count) != (30, 30)
            or any(
                value is not True
                for value in (
                    self.atomic_result_complete,
                    self.source_states_preserved,
                    self.common_neuron_order_preserved,
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
            != "SYNTHETIC_COMMON_RECEIPTS_COMPLETE_REAL_PROBE_CLOSED"
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1FYSyntheticCommonReceiptError(
                "S1-FY aggregate is incomplete or opened execution"
            )
        object.__setattr__(self, "receipts", receipts)


def coordinate_e1_formation_s1fy_synthetically(
    contract: E1FormationS1FXCommonProbeReceiptContract,
    handoff: E1FormationS1FWSyntheticLiveStateHandoffResult,
    inputs: E1FormationS1FIPreparedInputs,
    *,
    adapters: dict[str, SyntheticReceiptAdapter] | None = None,
) -> E1FormationS1FYSyntheticCommonReceiptResult:
    """Build all common receipts atomically without advancing a field."""

    if not isinstance(contract, E1FormationS1FXCommonProbeReceiptContract):
        raise E1FormationS1FYSyntheticCommonReceiptError(
            "S1-FY requires the typed S1-FX contract"
        )
    if not isinstance(handoff, E1FormationS1FWSyntheticLiveStateHandoffResult):
        raise E1FormationS1FYSyntheticCommonReceiptError(
            "S1-FY requires the typed S1-FW handoff"
        )
    if not isinstance(inputs, E1FormationS1FIPreparedInputs):
        raise E1FormationS1FYSyntheticCommonReceiptError(
            "S1-FY requires the typed S1-FI inputs"
        )
    contract.__post_init__()
    handoff.__post_init__()
    inputs.__post_init__()
    if (
        contract.source_s1fw_result_digest != handoff.result_digest
        or contract.synthetic_counting_implementation_permitted is not True
        or contract.execution_permitted is not False
        or handoff.field_steps_executed != 0
    ):
        raise E1FormationS1FYSyntheticCommonReceiptError(
            "S1-FY source chain changed or opened execution"
        )
    selected = adapters or {
        "neutral-p0": build_s1fy_neutral_p0_receipt,
        "frozen-e1": build_s1fy_frozen_e1_receipt,
        "fixed-adapter": build_s1fy_fixed_adapter_receipt,
    }
    if set(selected) != set(S1_FY_KERNEL_BY_BRANCH) or not all(
        callable(item) for item in selected.values()
    ):
        raise E1FormationS1FYSyntheticCommonReceiptError(
            "S1-FY requires exactly three counting adapters"
        )
    field_digest = dict(inputs.input_manifest)["initial_field"]
    neurons = tuple(inputs.initial_field.layer.neurons)
    neuron_ids = tuple(item.neuron_id for item in neurons)
    activation = tuple(item.activation for item in neurons)
    afterimage = tuple(item.afterimage for item in neurons)
    probe_source_digest = _digest(
        ("s1fy-synthetic-common-probe", inputs.input_manifest_digest)
    )
    source_before = tuple(
        _digest(_state_payload(item.state)) for item in handoff.live_sources
    )
    counts: Counter[str] = Counter()
    pending: list[E1FormationS1FYCommonProbeReceipt] = []
    for slot in handoff.slot_handoffs:
        branch = _branch(slot)
        receipt = selected[branch](
            slot,
            probe_source_digest,
            field_digest,
            neuron_ids,
            activation,
            afterimage,
        )
        if not isinstance(receipt, E1FormationS1FYCommonProbeReceipt):
            raise E1FormationS1FYSyntheticCommonReceiptError(
                "S1-FY adapter returned no typed receipt"
            )
        receipt.__post_init__()
        if (
            receipt.binding_digest != slot.binding.binding_digest
            or receipt.refinement_id != slot.binding.refinement_id
            or receipt.role_id != slot.binding.role_id
            or receipt.kernel_name != S1_FY_KERNEL_BY_BRANCH[branch]
        ):
            raise E1FormationS1FYSyntheticCommonReceiptError(
                "S1-FY receipt does not match its slot"
            )
        pending.append(receipt)
        counts[branch] += 1
    source_after = tuple(
        _digest(_state_payload(item.state)) for item in handoff.live_sources
    )
    receipts = tuple(pending)
    branch_counts = tuple(
        (branch, counts[branch])
        for branch in ("neutral-p0", "frozen-e1", "fixed-adapter")
    )
    values = {
        "coordinator_id": S1_FY_COORDINATOR_ID,
        "source_s1fx_contract_digest": contract.contract_digest,
        "source_s1fw_result_digest": handoff.result_digest,
        "source_input_manifest_digest": inputs.input_manifest_digest,
        "receipts": receipts,
        "receipt_digests": tuple(item.receipt_digest for item in receipts),
        "branch_invocation_counts": branch_counts,
        "receipt_count": len(receipts),
        "distinct_receipt_count": len({item.receipt_digest for item in receipts}),
        "atomic_result_complete": len(receipts) == 30,
        "source_states_preserved": source_before == source_after,
        "common_neuron_order_preserved": len(
            {item.ordered_neuron_ids for item in receipts}
        )
        == 1,
        "field_steps_executed": sum(item.field_step_count for item in receipts),
        "real_probe_adapter_called": False,
        "persistence_performed": False,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "claims_permitted": False,
        "decision": "SYNTHETIC_COMMON_RECEIPTS_COMPLETE_REAL_PROBE_CLOSED",
        "reason": (
            "thirty-causally-separated-common-receipts-built-atomically;"
            "three-counting-adapters-used;zero-field-steps"
        ),
    }
    payload = {
        name: value for name, value in values.items() if name != "receipts"
    }
    return E1FormationS1FYSyntheticCommonReceiptResult(
        **values,
        result_digest=_digest(payload),
    )
