"""S1-GI typed fixed-adapter output and pure common-receipt converter."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .e1_formation_s1fx_common_probe_receipt_contract import S1_FX_RECEIPT_SCHEMA
from .e1_formation_s1fw_synthetic_live_state_handoff import _adapter_digest
from .e1_formation_s1gh_fresh_field_bridge import E1FormationS1GHFreshFieldBinding
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest, _state_payload


class E1FormationS1GIFixedAdapterOutputConverterError(ValueError):
    """Raised when fixed-adapter output provenance or causality is changed."""


S1_GI_OUTPUT_ID = "e1.fixed-adapter-typed-output.s1gi.v1"
S1_GI_EXECUTION_KINDS = (
    "synthetic-typed-real-output",
    "real-in-memory-fixed-adapter-probe",
)
S1_GI_KERNEL_NAME = "advance_fixed_e1_adapter_fast_shared_field_transient"


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GIFixedAdapterRealOutput:
    output_id: str
    binding_digest: str
    terminal_field_digest: str
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    field_step_count: int
    source_support_count: int
    source_state_digest_before: str
    source_state_digest_after: str
    fixed_adapter_digest_before: str
    fixed_adapter_digest_after: str
    source_state_preserved: bool
    fixed_adapter_preserved: bool
    field_execution_kind: str
    actual_field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    output_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "output_digest"
        }
        vectors = (tuple(self.activation), tuple(self.afterimage))
        synthetic = self.field_execution_kind == "synthetic-typed-real-output"
        if (
            self.output_id != S1_GI_OUTPUT_ID
            or not all(
                _valid_digest(value)
                for value in (
                    self.binding_digest,
                    self.terminal_field_digest,
                    self.source_state_digest_before,
                    self.source_state_digest_after,
                    self.fixed_adapter_digest_before,
                    self.fixed_adapter_digest_after,
                )
            )
            or not vectors[0]
            or len(vectors[0]) != len(vectors[1])
            or any(not math.isfinite(value) for vector in vectors for value in vector)
            or self.field_step_count < 1
            or self.source_support_count < 1
            or self.source_state_digest_before != self.source_state_digest_after
            or self.fixed_adapter_digest_before != self.fixed_adapter_digest_after
            or self.source_state_preserved is not True
            or self.fixed_adapter_preserved is not True
            or self.field_execution_kind not in S1_GI_EXECUTION_KINDS
            or self.actual_field_steps_executed
            != (0 if synthetic else self.field_step_count)
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.output_digest != _digest(payload)
        ):
            raise E1FormationS1GIFixedAdapterOutputConverterError(
                "S1-GI typed output changed or lost fixed-adapter provenance"
            )
        object.__setattr__(self, "activation", vectors[0])
        object.__setattr__(self, "afterimage", vectors[1])


def build_e1_formation_s1gi_synthetic_typed_output(
    fresh: E1FormationS1GHFreshFieldBinding,
    activation: tuple[float, ...],
    afterimage: tuple[float, ...],
) -> E1FormationS1GIFixedAdapterRealOutput:
    """Construct one typed output shape without invoking a field kernel."""

    if not isinstance(fresh, E1FormationS1GHFreshFieldBinding):
        raise E1FormationS1GIFixedAdapterOutputConverterError(
            "S1-GI requires one typed S1-GH fresh binding"
        )
    fresh.__post_init__()
    activation_in = tuple(activation)
    afterimage_in = tuple(afterimage)
    invocation = fresh.invocation
    state_digest = _digest(_state_payload(invocation.source_state))
    adapter_digest = _adapter_digest(invocation.fixed_adapter)
    plan = invocation.context.probe_plan
    terminal_digest = _digest(
        (
            "s1gi-synthetic-terminal",
            fresh.binding_digest,
            activation_in,
            afterimage_in,
        )
    )
    values = {
        "output_id": S1_GI_OUTPUT_ID,
        "binding_digest": fresh.binding_digest,
        "terminal_field_digest": terminal_digest,
        "activation": activation_in,
        "afterimage": afterimage_in,
        "field_step_count": len(plan.proposal_steps),
        "source_support_count": plan.handoff.source_event_count,
        "source_state_digest_before": state_digest,
        "source_state_digest_after": state_digest,
        "fixed_adapter_digest_before": adapter_digest,
        "fixed_adapter_digest_after": adapter_digest,
        "source_state_preserved": True,
        "fixed_adapter_preserved": True,
        "field_execution_kind": "synthetic-typed-real-output",
        "actual_field_steps_executed": 0,
        "persistence_performed": False,
        "claims_permitted": False,
    }
    return E1FormationS1GIFixedAdapterRealOutput(
        **values,
        output_digest=_digest(values),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GIFixedAdapterCommonProbeReceipt:
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
        vectors = (
            tuple(self.activation_vector),
            tuple(self.afterimage_vector),
        )
        if (
            tuple(self.__dataclass_fields__) != S1_FX_RECEIPT_SCHEMA
            or not self.role_id.startswith("fixed-adapter-")
            or self.probe_mode != "fixed-adapter"
            or not all(
                _valid_digest(value)
                for value in (
                    self.binding_digest,
                    self.probe_source_digest,
                    self.initial_field_digest,
                    self.terminal_field_digest,
                    self.source_state_digest,
                    self.fixed_adapter_digest,
                    self.receipt_digest,
                )
            )
            or any(
                value is not None
                for value in (self.state_digest_before, self.state_digest_after)
            )
            or not self.ordered_neuron_ids
            or len(set(self.ordered_neuron_ids)) != len(self.ordered_neuron_ids)
            or any(len(vector) != len(self.ordered_neuron_ids) for vector in vectors)
            or any(not math.isfinite(value) for vector in vectors for value in vector)
            or self.field_step_count < 1
            or self.source_support_count < 1
            or self.source_state_preserved is not True
            or self.kernel_name != S1_GI_KERNEL_NAME
            or self.field_execution_kind not in S1_GI_EXECUTION_KINDS
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.receipt_digest != _digest(payload)
        ):
            raise E1FormationS1GIFixedAdapterOutputConverterError(
                "S1-GI common receipt changed or merged causal state roles"
            )
        object.__setattr__(self, "activation_vector", vectors[0])
        object.__setattr__(self, "afterimage_vector", vectors[1])


def convert_e1_formation_s1gi_fixed_adapter_output(
    fresh: E1FormationS1GHFreshFieldBinding,
    output: E1FormationS1GIFixedAdapterRealOutput,
) -> E1FormationS1GIFixedAdapterCommonProbeReceipt:
    """Convert one typed output without invoking or repeating its probe."""

    if not isinstance(fresh, E1FormationS1GHFreshFieldBinding) or not isinstance(
        output, E1FormationS1GIFixedAdapterRealOutput
    ):
        raise E1FormationS1GIFixedAdapterOutputConverterError(
            "S1-GI requires typed fresh binding and fixed-adapter output"
        )
    fresh.__post_init__()
    output.__post_init__()
    invocation = fresh.invocation
    plan = invocation.context.probe_plan
    current_state_digest = _digest(_state_payload(invocation.source_state))
    current_adapter_digest = _adapter_digest(invocation.fixed_adapter)
    if (
        output.binding_digest != fresh.binding_digest
        or fresh.initial_field_digest != _initial_field_digest(fresh.fresh_field)
        or output.field_step_count != len(plan.proposal_steps)
        or output.source_support_count != plan.handoff.source_event_count
        or output.source_state_digest_before != current_state_digest
        or output.source_state_digest_after != current_state_digest
        or output.fixed_adapter_digest_before != current_adapter_digest
        or output.fixed_adapter_digest_after != current_adapter_digest
        or output.source_state_preserved is not True
        or output.fixed_adapter_preserved is not True
        or len(output.activation) != len(fresh.ordered_neuron_ids)
        or len(output.afterimage) != len(fresh.ordered_neuron_ids)
        or output.persistence_performed is not False
        or output.claims_permitted is not False
    ):
        raise E1FormationS1GIFixedAdapterOutputConverterError(
            "S1-GI fresh binding and output do not describe one probe"
        )
    values = {
        "refinement_id": fresh.refinement_id,
        "role_id": fresh.role_id,
        "probe_mode": "fixed-adapter",
        "binding_digest": fresh.binding_digest,
        "probe_source_digest": invocation.context.probe_source_digest,
        "initial_field_digest": fresh.initial_field_digest,
        "terminal_field_digest": output.terminal_field_digest,
        "ordered_neuron_ids": fresh.ordered_neuron_ids,
        "activation_vector": output.activation,
        "afterimage_vector": output.afterimage,
        "field_step_count": output.field_step_count,
        "source_support_count": output.source_support_count,
        "source_state_digest": current_state_digest,
        "state_digest_before": None,
        "state_digest_after": None,
        "source_state_preserved": output.source_state_preserved,
        "fixed_adapter_digest": current_adapter_digest,
        "kernel_name": S1_GI_KERNEL_NAME,
        "field_execution_kind": output.field_execution_kind,
        "persistence_performed": output.persistence_performed,
        "claims_permitted": False,
    }
    return E1FormationS1GIFixedAdapterCommonProbeReceipt(
        **values,
        receipt_digest=_digest(values),
    )
