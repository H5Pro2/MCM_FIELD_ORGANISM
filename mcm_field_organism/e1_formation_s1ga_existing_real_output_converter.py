"""S1-GA pure converter for existing P0 and frozen-E1 real-output shapes."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .e1_common_probe_real_wrappers import (
    E1CommonProbeFreshField,
    E1CommonProbeRealProbeOutput,
    E1CommonProbeResolvedSlot,
)
from .e1_formation_s1fx_common_probe_receipt_contract import S1_FX_RECEIPT_SCHEMA
from .e1_frozen_state_transfer_contract import _probe_digest
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest


class E1FormationS1GAExistingRealOutputConverterError(ValueError):
    """Raised when a converted receipt loses its bound output provenance."""


S1_GA_CONVERTER_ID = "e1.existing-real-output-common-receipt-converter.s1ga.v1"
S1_GA_EXECUTION_KINDS = (
    "synthetic-typed-real-output",
    "real-in-memory-common-probe",
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _probe_mode(role_id: str) -> str:
    if role_id.startswith("p0-reset-"):
        return "neutral-p0"
    if role_id.startswith("e1-active-"):
        return "frozen-e1-feedback-enabled"
    if role_id.startswith("e1-probe-feedback-ablated-"):
        return "frozen-e1-feedback-disabled"
    if role_id.startswith("e1-formation-ablated-"):
        return "frozen-formation-ablated-feedback-enabled"
    raise E1FormationS1GAExistingRealOutputConverterError(
        "S1-GA received a role outside P0/Frozen-E1"
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GAConvertedCommonProbeReceipt:
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
        is_p0 = self.probe_mode == "neutral-p0"
        vectors = (tuple(self.activation_vector), tuple(self.afterimage_vector))
        if (
            tuple(self.__dataclass_fields__) != S1_FX_RECEIPT_SCHEMA
            or self.probe_mode != _probe_mode(self.role_id)
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
            or self.field_step_count < 1
            or self.source_support_count < 1
            or self.source_state_preserved is not True
            or self.fixed_adapter_digest is not None
            or self.kernel_name
            != (
                "advance_neutral_fast_shared_field_transient"
                if is_p0
                else "advance_frozen_e1_fast_shared_field_transient"
            )
            or self.field_execution_kind not in S1_GA_EXECUTION_KINDS
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.receipt_digest != _digest(payload)
        ):
            raise E1FormationS1GAExistingRealOutputConverterError(
                "S1-GA converted receipt changed or lost provenance"
            )
        state_values = (
            self.source_state_digest,
            self.state_digest_before,
            self.state_digest_after,
        )
        if is_p0 and any(value is not None for value in state_values):
            raise E1FormationS1GAExistingRealOutputConverterError(
                "S1-GA P0 receipt contains state evidence"
            )
        if not is_p0 and (
            not all(_valid_digest(value) for value in state_values)
            or len(set(state_values)) != 1
        ):
            raise E1FormationS1GAExistingRealOutputConverterError(
                "S1-GA frozen receipt lost its unchanged source state"
            )


def convert_e1_formation_s1ga_existing_real_output(
    resolved: E1CommonProbeResolvedSlot,
    fresh: E1CommonProbeFreshField,
    output: E1CommonProbeRealProbeOutput,
    *,
    field_execution_kind: str,
) -> E1FormationS1GAConvertedCommonProbeReceipt:
    """Convert one bound typed output without invoking or repeating its probe."""

    if not isinstance(resolved, E1CommonProbeResolvedSlot):
        raise E1FormationS1GAExistingRealOutputConverterError(
            "S1-GA requires one typed resolved slot"
        )
    if not isinstance(fresh, E1CommonProbeFreshField):
        raise E1FormationS1GAExistingRealOutputConverterError(
            "S1-GA requires one typed fresh field"
        )
    if not isinstance(output, E1CommonProbeRealProbeOutput):
        raise E1FormationS1GAExistingRealOutputConverterError(
            "S1-GA requires one typed real-output shape"
        )
    resolved.__post_init__()
    output.__post_init__()
    binding = resolved.binding
    is_p0 = binding.state_role is None
    source_state_digest = output.frozen_state_digest_before
    neuron_ids = tuple(item.neuron_id for item in fresh.field.layer.neurons)
    if (
        field_execution_kind not in S1_GA_EXECUTION_KINDS
        or fresh.binding_digest != binding.binding_digest
        or output.binding_digest != binding.binding_digest
        or fresh.initial_field_digest != _initial_field_digest(fresh.field)
        or binding.probe_source_digest != _probe_digest(resolved.probe_sequences)
        or output.field_step_count != len(resolved.probe_plan.proposal_steps)
        or output.source_support_count
        != resolved.probe_plan.handoff.source_event_count
        or len(output.activation) != len(neuron_ids)
        or len(output.afterimage) != len(neuron_ids)
        or (source_state_digest is None) is not is_p0
        or output.frozen_state_digest_after != source_state_digest
        or output.frozen_state_preserved is not True
        or output.persistence_performed is not False
        or output.research_decision_permitted is not False
        or output.memory_claim_permitted is not False
    ):
        raise E1FormationS1GAExistingRealOutputConverterError(
            "S1-GA contexts and output do not describe one bound probe"
        )
    values = {
        "refinement_id": binding.refinement_id,
        "role_id": binding.role_id,
        "probe_mode": _probe_mode(binding.role_id),
        "binding_digest": binding.binding_digest,
        "probe_source_digest": binding.probe_source_digest,
        "initial_field_digest": fresh.initial_field_digest,
        "terminal_field_digest": output.terminal_field_digest,
        "ordered_neuron_ids": neuron_ids,
        "activation_vector": output.activation,
        "afterimage_vector": output.afterimage,
        "field_step_count": output.field_step_count,
        "source_support_count": output.source_support_count,
        "source_state_digest": source_state_digest,
        "state_digest_before": output.frozen_state_digest_before,
        "state_digest_after": output.frozen_state_digest_after,
        "source_state_preserved": output.frozen_state_preserved,
        "fixed_adapter_digest": None,
        "kernel_name": binding.probe_kernel,
        "field_execution_kind": field_execution_kind,
        "persistence_performed": output.persistence_performed,
        "claims_permitted": False,
    }
    return E1FormationS1GAConvertedCommonProbeReceipt(
        **values,
        receipt_digest=_digest(values),
    )
