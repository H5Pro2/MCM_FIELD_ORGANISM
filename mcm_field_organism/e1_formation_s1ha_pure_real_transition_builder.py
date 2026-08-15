"""S1-HA pure builder for one provenance-bound real field transition."""

from __future__ import annotations

from .e1_formation_s1fw_synthetic_live_state_handoff import _adapter_digest
from .e1_formation_s1gh_fresh_field_bridge import E1FormationS1GHFreshFieldBinding
from .e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
    S1_GN_CARRIER_ID,
    e1_formation_s1gn_current_field_digest,
)
from .e1_formation_s1gq_carrier_transition_schema import (
    E1FormationS1GQRealFieldCarrierTransition,
    S1_GQ_REAL_TRANSITION_ID,
    bind_e1_formation_s1gq_carrier_transition_envelope,
)
from .e1_formation_s1gs_real_single_batch_gate_contract import (
    build_e1_formation_s1gs_real_single_batch_gate_contract,
)
from .e1_formation_s1gv_real_adapter_call_receipt_schema import (
    E1FormationS1GVRealAdapterCallReceipt,
)
from .e1_refined_formation_runner import _digest, _state_payload
from .receptor_proposal_handoff import ReceptorProposalBatch
from .shared_mcm_field import SharedMCMField


class E1FormationS1HAPureRealTransitionBuilderError(ValueError):
    """Raised when route, receipt, field, or carrier provenance is invalid."""


def build_e1_formation_s1ha_pure_real_transition(
    fresh: E1FormationS1GHFreshFieldBinding,
    batch: ReceptorProposalBatch,
    previous_carrier: E1FormationS1GNLiveFieldCarrier,
    next_field: SharedMCMField,
    adapter_call_receipt: E1FormationS1GVRealAdapterCallReceipt,
) -> E1FormationS1GQRealFieldCarrierTransition:
    """Build one transition from completed evidence without field execution."""

    if (
        not isinstance(fresh, E1FormationS1GHFreshFieldBinding)
        or not isinstance(batch, ReceptorProposalBatch)
        or not isinstance(previous_carrier, E1FormationS1GNLiveFieldCarrier)
        or not isinstance(next_field, SharedMCMField)
        or not isinstance(
            adapter_call_receipt,
            E1FormationS1GVRealAdapterCallReceipt,
        )
    ):
        raise E1FormationS1HAPureRealTransitionBuilderError(
            "S1-HA requires typed binding, batch, carrier, field, and receipt"
        )
    fresh.__post_init__()
    previous_carrier.__post_init__()
    adapter_call_receipt.__post_init__()
    gate = build_e1_formation_s1gs_real_single_batch_gate_contract()
    batches = fresh.invocation.context.probe_plan.handoff.batches
    next_field_digest = e1_formation_s1gn_current_field_digest(next_field)
    current_state_digest = _digest(
        _state_payload(fresh.invocation.source_state)
    )
    current_adapter_digest = _adapter_digest(fresh.invocation.fixed_adapter)
    receipt = adapter_call_receipt
    if (
        previous_carrier.fresh_binding is not fresh
        or previous_carrier.binding_digest != fresh.binding_digest
        or previous_carrier.completed_batch_count >= len(batches)
        or batches[previous_carrier.completed_batch_count] is not batch
        or batch.batch_index != previous_carrier.completed_batch_count
        or receipt.gate_digest != gate.gate_digest
        or receipt.binding_digest != fresh.binding_digest
        or receipt.batch_index != batch.batch_index
        or receipt.batch_step_start_tick != batch.step_time.start_tick
        or receipt.batch_step_end_tick != batch.step_time.end_tick
        or receipt.previous_carrier_digest != previous_carrier.carrier_digest
        or receipt.previous_field_digest
        != previous_carrier.current_field_digest
        or receipt.next_field_digest != next_field_digest
        or receipt.source_state_digest_before != current_state_digest
        or receipt.source_state_digest_after != current_state_digest
        or receipt.fixed_adapter_digest_before != current_adapter_digest
        or receipt.fixed_adapter_digest_after != current_adapter_digest
        or next_field is previous_carrier.current_field
        or next_field.layer.tick != previous_carrier.current_field.layer.tick + 1
        or tuple(item.neuron_id for item in next_field.layer.neurons)
        != previous_carrier.ordered_neuron_ids
        or next_field_digest == previous_carrier.current_field_digest
    ):
        raise E1FormationS1HAPureRealTransitionBuilderError(
            "S1-HA route, receipt, attestations, or next field do not match"
        )

    next_values = {
        "carrier_id": S1_GN_CARRIER_ID,
        "fresh_binding": fresh,
        "current_field": next_field,
        "binding_digest": previous_carrier.binding_digest,
        "initial_field_digest": previous_carrier.initial_field_digest,
        "current_field_digest": next_field_digest,
        "ordered_neuron_ids": previous_carrier.ordered_neuron_ids,
        "completed_batch_count": previous_carrier.completed_batch_count + 1,
        "accounted_source_support_count": (
            previous_carrier.accounted_source_support_count + batch.event_count
        ),
        "actual_field_steps_executed": (
            previous_carrier.actual_field_steps_executed + 1
        ),
        "persistence_performed": False,
        "claims_permitted": False,
    }
    next_payload = {
        name: value
        for name, value in next_values.items()
        if name not in {"fresh_binding", "current_field"}
    }
    next_carrier = E1FormationS1GNLiveFieldCarrier(
        **next_values,
        carrier_digest=_digest(next_payload),
    )
    transition_values = {
        "transition_id": S1_GQ_REAL_TRANSITION_ID,
        "previous_carrier": previous_carrier,
        "next_carrier": next_carrier,
        "binding_digest": fresh.binding_digest,
        "batch_index": batch.batch_index,
        "batch_step_start_tick": batch.step_time.start_tick,
        "batch_step_end_tick": batch.step_time.end_tick,
        "batch_source_support_count": batch.event_count,
        "previous_field_digest": previous_carrier.current_field_digest,
        "next_field_digest": next_field_digest,
        "previous_field_object_carried_explicitly": True,
        "next_field_object_carried_explicitly": True,
        "synthetic_no_field_advance": False,
        "field_object_replaced": True,
        "accounted_field_steps": 1,
        "actual_field_steps_executed": 1,
        "persistence_performed": False,
        "claims_permitted": False,
    }
    transition_payload = {
        name: value
        for name, value in transition_values.items()
        if name not in {"previous_carrier", "next_carrier"}
    }
    transition = E1FormationS1GQRealFieldCarrierTransition(
        **transition_values,
        transition_digest=_digest(transition_payload),
    )
    envelope = bind_e1_formation_s1gq_carrier_transition_envelope(transition)
    if (
        envelope.transition_kind != "real-field-advance"
        or envelope.transition_digest != transition.transition_digest
        or envelope.previous_carrier is not previous_carrier
        or envelope.next_carrier is not next_carrier
        or envelope.actual_field_steps_executed != 1
        or envelope.persistence_performed is not False
        or envelope.claims_permitted is not False
    ):
        raise E1FormationS1HAPureRealTransitionBuilderError(
            "S1-HA shared envelope rejected the complete real transition"
        )
    return transition
