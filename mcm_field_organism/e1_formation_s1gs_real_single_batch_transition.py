"""S1-GS private real single-batch transition adapter for fixed adapters."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_formation_s1gh_fresh_field_bridge import E1FormationS1GHFreshFieldBinding
from .e1_formation_s1fw_synthetic_live_state_handoff import _adapter_digest
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
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest, _state_payload
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff import ReceptorProposalBatch
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1FormationS1GSRealSingleBatchTransitionError(ValueError):
    """Raised when the real transition crosses its narrow one-step boundary."""


S1_GS_ADAPTER_ID = "e1.real-single-batch-transition.s1gs.v1"
S1_GS_DECISION = (
    "REAL_SINGLE_BATCH_TRANSITION_VALIDATED_WRAPPER_GATE_REMAINS_CLOSED"
)


@dataclass(frozen=True, slots=True)
class E1FormationS1GSRealSingleBatchTransitionResult:
    adapter_id: str
    fresh_binding_digest: str
    previous_carrier_digest: str
    next_carrier_digest: str
    transition_digest: str
    envelope_digest: str
    batch_index: int
    batch_source_support_count: int
    accounted_field_steps: int
    actual_field_steps_executed: int
    field_object_replaced: bool
    source_state_preserved: bool
    fixed_adapter_preserved: bool
    persistence_performed: bool
    claims_permitted: bool
    wrapper_gate_opened: bool
    decision: str
    result_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if (
            self.adapter_id != S1_GS_ADAPTER_ID
            or any(
                len(value) != 64
                for value in (
                    self.fresh_binding_digest,
                    self.previous_carrier_digest,
                    self.next_carrier_digest,
                    self.transition_digest,
                    self.envelope_digest,
                )
            )
            or self.batch_index < 0
            or self.batch_source_support_count < 0
            or self.accounted_field_steps != 1
            or self.actual_field_steps_executed != 1
            or self.field_object_replaced is not True
            or self.source_state_preserved is not True
            or self.fixed_adapter_preserved is not True
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.wrapper_gate_opened is not False
            or self.decision != S1_GS_DECISION
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GSRealSingleBatchTransitionError(
                "S1-GS real transition changed accounting, persistence, or gate state"
            )


def advance_e1_formation_s1gs_real_single_batch_transition(
    fresh: E1FormationS1GHFreshFieldBinding,
    batch: ReceptorProposalBatch,
    carrier: E1FormationS1GNLiveFieldCarrier,
) -> E1FormationS1GQRealFieldCarrierTransition:
    """Execute exactly one fixed-adapter field step and return a real transition."""

    if (
        not isinstance(fresh, E1FormationS1GHFreshFieldBinding)
        or not isinstance(batch, ReceptorProposalBatch)
        or not isinstance(carrier, E1FormationS1GNLiveFieldCarrier)
    ):
        raise E1FormationS1GSRealSingleBatchTransitionError(
            "S1-GS requires fresh binding, batch, and live carrier"
        )
    fresh.__post_init__()
    carrier.__post_init__()
    batches = fresh.invocation.context.probe_plan.handoff.batches
    if (
        carrier.fresh_binding is not fresh
        or carrier.binding_digest != fresh.binding_digest
        or carrier.completed_batch_count >= len(batches)
        or batches[carrier.completed_batch_count] is not batch
        or batch.batch_index != carrier.completed_batch_count
        or fresh.invocation.fixed_adapter is None
    ):
        raise E1FormationS1GSRealSingleBatchTransitionError(
            "S1-GS carrier and exact fixed-adapter batch do not share one route"
        )

    trajectory = map_proposal_batch_to_transient_docks(
        batch,
        carrier.current_field.docks,
    )
    inputs = project_transient_docks_to_neuron_inputs(
        trajectory,
        carrier.current_field.docks,
    )
    distribution = ReceptorDistribution(
        CommonFieldTime(
            batch.step_time.clock_id,
            batch.step_time.start_tick,
            batch.step_time.end_tick,
        ),
        (),
    )
    next_field = advance_fixed_e1_adapter_fast_shared_field_transient(
        carrier.current_field,
        fresh.invocation.fixed_adapter,
        distribution,
        inputs,
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )
    next_values = {
        "carrier_id": S1_GN_CARRIER_ID,
        "fresh_binding": fresh,
        "current_field": next_field,
        "binding_digest": carrier.binding_digest,
        "initial_field_digest": carrier.initial_field_digest,
        "current_field_digest": e1_formation_s1gn_current_field_digest(next_field),
        "ordered_neuron_ids": carrier.ordered_neuron_ids,
        "completed_batch_count": carrier.completed_batch_count + 1,
        "accounted_source_support_count": (
            carrier.accounted_source_support_count + batch.event_count
        ),
        "actual_field_steps_executed": carrier.actual_field_steps_executed + 1,
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
    values = {
        "transition_id": S1_GQ_REAL_TRANSITION_ID,
        "previous_carrier": carrier,
        "next_carrier": next_carrier,
        "binding_digest": fresh.binding_digest,
        "batch_index": batch.batch_index,
        "batch_step_start_tick": batch.step_time.start_tick,
        "batch_step_end_tick": batch.step_time.end_tick,
        "batch_source_support_count": batch.event_count,
        "previous_field_digest": carrier.current_field_digest,
        "next_field_digest": next_carrier.current_field_digest,
        "previous_field_object_carried_explicitly": True,
        "next_field_object_carried_explicitly": True,
        "synthetic_no_field_advance": False,
        "field_object_replaced": True,
        "accounted_field_steps": 1,
        "actual_field_steps_executed": 1,
        "persistence_performed": False,
        "claims_permitted": False,
    }
    payload = {
        name: value
        for name, value in values.items()
        if name not in {"previous_carrier", "next_carrier"}
    }
    return E1FormationS1GQRealFieldCarrierTransition(
        **values,
        transition_digest=_digest(payload),
    )


def validate_e1_formation_s1gs_real_single_batch_transition(
    fresh: E1FormationS1GHFreshFieldBinding,
    batch: ReceptorProposalBatch,
    carrier: E1FormationS1GNLiveFieldCarrier,
) -> E1FormationS1GSRealSingleBatchTransitionResult:
    """Run one isolated real transition and bind its shared envelope receipt."""

    source_state = fresh.invocation.source_state
    source_state_digest_before = _digest(_state_payload(source_state))
    fixed_adapter_digest_before = _adapter_digest(fresh.invocation.fixed_adapter)
    transition = advance_e1_formation_s1gs_real_single_batch_transition(
        fresh,
        batch,
        carrier,
    )
    envelope = bind_e1_formation_s1gq_carrier_transition_envelope(transition)
    source_state_digest_after = _digest(_state_payload(source_state))
    fixed_adapter_digest_after = _adapter_digest(fresh.invocation.fixed_adapter)
    values = {
        "adapter_id": S1_GS_ADAPTER_ID,
        "fresh_binding_digest": fresh.fresh_binding_digest,
        "previous_carrier_digest": carrier.carrier_digest,
        "next_carrier_digest": transition.next_carrier.carrier_digest,
        "transition_digest": transition.transition_digest,
        "envelope_digest": envelope.envelope_digest,
        "batch_index": batch.batch_index,
        "batch_source_support_count": batch.event_count,
        "accounted_field_steps": envelope.accounted_field_steps,
        "actual_field_steps_executed": envelope.actual_field_steps_executed,
        "field_object_replaced": envelope.field_object_replaced,
        "source_state_preserved": (
            source_state_digest_before == source_state_digest_after
        ),
        "fixed_adapter_preserved": (
            fixed_adapter_digest_before == fixed_adapter_digest_after
        ),
        "persistence_performed": envelope.persistence_performed,
        "claims_permitted": envelope.claims_permitted,
        "wrapper_gate_opened": False,
        "decision": S1_GS_DECISION,
    }
    return E1FormationS1GSRealSingleBatchTransitionResult(
        **values,
        result_digest=_digest(values),
    )
