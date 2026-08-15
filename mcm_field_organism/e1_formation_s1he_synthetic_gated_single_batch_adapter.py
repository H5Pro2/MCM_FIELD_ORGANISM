"""S1-HE synthetic-only integration of the gated single-batch adapter flow."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .e1_formation_s1fw_synthetic_live_state_handoff import _adapter_digest
from .e1_formation_s1gh_fresh_field_bridge import E1FormationS1GHFreshFieldBinding
from .e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
    e1_formation_s1gn_current_field_digest,
)
from .e1_formation_s1gq_carrier_transition_schema import (
    E1FormationS1GQCarrierTransitionEnvelope,
    E1FormationS1GQRealFieldCarrierTransition,
    bind_e1_formation_s1gq_carrier_transition_envelope,
)
from .e1_formation_s1gs_real_single_batch_gate_contract import (
    E1FormationS1GSRealSingleBatchGateContract,
)
from .e1_formation_s1gv_real_adapter_call_receipt_schema import (
    E1FormationS1GVRealAdapterCallReceipt,
    S1_GV_KERNEL_NAME,
)
from .e1_formation_s1gw_external_owner_authorization_schema import (
    E1FormationS1GWExternalOwnerAuthorization,
)
from .e1_formation_s1gx_deterministic_single_batch_target import (
    E1FormationS1GXDeterministicSingleBatchTarget,
)
from .e1_formation_s1ha_pure_real_transition_builder import (
    build_e1_formation_s1ha_pure_real_transition,
)
from .e1_formation_s1hc_real_single_use_token import (
    E1FormationS1HCRealSingleUseToken,
)
from .e1_formation_s1hd_private_atomic_receipt_factory import (
    E1FormationS1HDCompletedAdapterBoundaryEvidence,
    S1_HD_EVIDENCE_ID,
    _seal_e1_formation_s1hd_real_adapter_call_receipt,
)
from .e1_refined_formation_runner import _digest, _state_payload
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff import ReceptorProposalBatch
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import (
    TransientNeuronInputSet,
    project_transient_docks_to_neuron_inputs,
)


class E1FormationS1HESyntheticGatedSingleBatchAdapterError(RuntimeError):
    """Raised when synthetic integration widens or returns a partial result."""


S1_HE_GATE_ID = "e1.synthetic-gated-single-batch-adapter.s1he.v1"
S1_HE_RESULT_ID = "e1.synthetic-gated-single-batch-result.s1he.v1"


@dataclass(frozen=True, slots=True)
class E1FormationS1HESyntheticAdapterGate:
    gate_id: str
    synthetic_only: bool
    precomputed_next_field_required: bool
    production_kernel_permitted: bool
    maximum_kernel_calls: int
    maximum_structural_field_steps: int
    retry_permitted: bool
    persistence_permitted: bool
    claims_permitted: bool
    gate_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "gate_digest"
        }
        if (
            self.gate_id != S1_HE_GATE_ID
            or self.synthetic_only is not True
            or self.precomputed_next_field_required is not True
            or self.production_kernel_permitted is not False
            or self.maximum_kernel_calls != 1
            or self.maximum_structural_field_steps != 1
            or self.retry_permitted is not False
            or self.persistence_permitted is not False
            or self.claims_permitted is not False
            or self.gate_digest != _digest(payload)
        ):
            raise E1FormationS1HESyntheticGatedSingleBatchAdapterError(
                "S1-HE synthetic gate opened production execution"
            )


def build_e1_formation_s1he_synthetic_adapter_gate(
) -> E1FormationS1HESyntheticAdapterGate:
    values = {
        "gate_id": S1_HE_GATE_ID,
        "synthetic_only": True,
        "precomputed_next_field_required": True,
        "production_kernel_permitted": False,
        "maximum_kernel_calls": 1,
        "maximum_structural_field_steps": 1,
        "retry_permitted": False,
        "persistence_permitted": False,
        "claims_permitted": False,
    }
    return E1FormationS1HESyntheticAdapterGate(
        **values,
        gate_digest=_digest(values),
    )


SyntheticBatchKernel = Callable[
    [
        SharedMCMField,
        object,
        ReceptorDistribution,
        TransientNeuronInputSet,
    ],
    SharedMCMField,
]


@dataclass(frozen=True, slots=True)
class E1FormationS1HESyntheticGatedSingleBatchResult:
    result_id: str
    synthetic_gate_digest: str
    authorization_digest: str
    token_digest: str
    receipt_digest: str
    transition_digest: str
    envelope_digest: str
    injected_kernel_calls: int
    structural_field_steps: int
    production_kernel_calls: int
    newly_computed_field_steps: int
    token_consumed_before_kernel: bool
    receipt_sealed_after_kernel: bool
    transition_built_after_receipt: bool
    token_retired_after_complete_result: bool
    atomic_complete_return: bool
    retry_permitted: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    result_digest: str
    receipt: E1FormationS1GVRealAdapterCallReceipt = field(
        repr=False,
        compare=False,
    )
    transition: E1FormationS1GQRealFieldCarrierTransition = field(
        repr=False,
        compare=False,
    )
    envelope: E1FormationS1GQCarrierTransitionEnvelope = field(
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"receipt", "transition", "envelope", "result_digest"}
        }
        if (
            self.result_id != S1_HE_RESULT_ID
            or not all(
                len(value) == 64
                for value in (
                    self.synthetic_gate_digest,
                    self.authorization_digest,
                    self.token_digest,
                    self.receipt_digest,
                    self.transition_digest,
                    self.envelope_digest,
                )
            )
            or self.receipt_digest != self.receipt.receipt_digest
            or self.transition_digest != self.transition.transition_digest
            or self.envelope_digest != self.envelope.envelope_digest
            or self.injected_kernel_calls != 1
            or self.structural_field_steps != 1
            or self.production_kernel_calls != 0
            or self.newly_computed_field_steps != 0
            or any(
                value is not True
                for value in (
                    self.token_consumed_before_kernel,
                    self.receipt_sealed_after_kernel,
                    self.transition_built_after_receipt,
                    self.token_retired_after_complete_result,
                    self.atomic_complete_return,
                )
            )
            or self.retry_permitted is not False
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.decision
            != "SYNTHETIC_ATOMIC_ADAPTER_FLOW_VALIDATED_PRODUCTION_KERNEL_CLOSED"
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1HESyntheticGatedSingleBatchAdapterError(
                "S1-HE result opened production execution or returned partially"
            )


def run_e1_formation_s1he_gated_single_batch_adapter_synthetically(
    authorization: E1FormationS1GWExternalOwnerAuthorization,
    token: E1FormationS1HCRealSingleUseToken,
    gate: E1FormationS1GSRealSingleBatchGateContract,
    target: E1FormationS1GXDeterministicSingleBatchTarget,
    fresh: E1FormationS1GHFreshFieldBinding,
    batch: ReceptorProposalBatch,
    previous_carrier: E1FormationS1GNLiveFieldCarrier,
    synthetic_gate: E1FormationS1HESyntheticAdapterGate,
    *,
    synthetic_kernel: SyntheticBatchKernel,
) -> E1FormationS1HESyntheticGatedSingleBatchResult:
    """Validate the complete adapter flow with one precomputed-field callback."""

    if not isinstance(token, E1FormationS1HCRealSingleUseToken):
        raise E1FormationS1HESyntheticGatedSingleBatchAdapterError(
            "S1-HE requires one typed real single-use token"
        )
    try:
        if (
            not isinstance(
                authorization,
                E1FormationS1GWExternalOwnerAuthorization,
            )
            or not isinstance(gate, E1FormationS1GSRealSingleBatchGateContract)
            or not isinstance(target, E1FormationS1GXDeterministicSingleBatchTarget)
            or not isinstance(fresh, E1FormationS1GHFreshFieldBinding)
            or not isinstance(batch, ReceptorProposalBatch)
            or not isinstance(previous_carrier, E1FormationS1GNLiveFieldCarrier)
            or not isinstance(synthetic_gate, E1FormationS1HESyntheticAdapterGate)
            or not callable(synthetic_kernel)
        ):
            raise E1FormationS1HESyntheticGatedSingleBatchAdapterError(
                "S1-HE requires complete typed inputs and one injected kernel"
            )
        authorization.__post_init__()
        gate.__post_init__()
        target.__post_init__()
        fresh.__post_init__()
        previous_carrier.__post_init__()
        synthetic_gate.__post_init__()
        if (
            getattr(synthetic_kernel, "__name__", "")
            == "advance_fixed_e1_adapter_fast_shared_field_transient"
            or token.status != "issued"
            or token.authorization_digest != authorization.authorization_digest
            or token.gate_digest != gate.gate_digest
            or token.binding_digest != target.selected_binding_digest
            or token.batch_index != target.selected_batch_index
            or token.carrier_digest != target.selected_carrier_digest
            or previous_carrier.fresh_binding is not fresh
            or fresh is not target.selected_fresh_binding
            or batch is not target.selected_batch
            or previous_carrier is not target.selected_initial_carrier
        ):
            raise E1FormationS1HESyntheticGatedSingleBatchAdapterError(
                "S1-HE production kernel, token state, or exact route is invalid"
            )
        trajectory = map_proposal_batch_to_transient_docks(
            batch,
            previous_carrier.current_field.docks,
        )
        transient_inputs = project_transient_docks_to_neuron_inputs(
            trajectory,
            previous_carrier.current_field.docks,
        )
        step = batch.step_time
        distribution = ReceptorDistribution(
            CommonFieldTime(step.clock_id, step.start_tick, step.end_tick),
            (),
        )
        state_before = _digest(_state_payload(fresh.invocation.source_state))
        adapter_before = _adapter_digest(fresh.invocation.fixed_adapter)
        token.consume()
        next_field = synthetic_kernel(
            previous_carrier.current_field,
            fresh.invocation.fixed_adapter,
            distribution,
            transient_inputs,
        )
        if not isinstance(next_field, SharedMCMField):
            raise E1FormationS1HESyntheticGatedSingleBatchAdapterError(
                "S1-HE injected kernel returned no SharedMCMField"
            )
        state_after = _digest(_state_payload(fresh.invocation.source_state))
        adapter_after = _adapter_digest(fresh.invocation.fixed_adapter)
        evidence_values = {
            "evidence_id": S1_HD_EVIDENCE_ID,
            "authorization_digest": authorization.authorization_digest,
            "consumed_token_digest": token.token_digest,
            "gate_digest": gate.gate_digest,
            "binding_digest": fresh.binding_digest,
            "batch_index": batch.batch_index,
            "batch_step_start_tick": batch.step_time.start_tick,
            "batch_step_end_tick": batch.step_time.end_tick,
            "previous_carrier_digest": previous_carrier.carrier_digest,
            "previous_field_digest": previous_carrier.current_field_digest,
            "next_field_digest": e1_formation_s1gn_current_field_digest(
                next_field
            ),
            "source_state_digest_before": state_before,
            "source_state_digest_after": state_after,
            "fixed_adapter_digest_before": adapter_before,
            "fixed_adapter_digest_after": adapter_after,
            "kernel_name": S1_GV_KERNEL_NAME,
            "token_consumed_before_adapter": True,
            "next_field_object_replaced": (
                next_field is not previous_carrier.current_field
            ),
            "adapter_calls": 1,
            "field_steps_executed": 1,
            "persistence_performed": False,
            "claims_permitted": False,
        }
        evidence = E1FormationS1HDCompletedAdapterBoundaryEvidence(
            **evidence_values,
            evidence_digest=_digest(evidence_values),
        )
        receipt = _seal_e1_formation_s1hd_real_adapter_call_receipt(
            authorization,
            token,
            gate,
            target,
            fresh,
            batch,
            previous_carrier,
            next_field,
            evidence,
        )
        transition = build_e1_formation_s1ha_pure_real_transition(
            fresh,
            batch,
            previous_carrier,
            next_field,
            receipt,
        )
        envelope = bind_e1_formation_s1gq_carrier_transition_envelope(
            transition
        )
        token.retire("real-attempt-success")
        values = {
            "result_id": S1_HE_RESULT_ID,
            "synthetic_gate_digest": synthetic_gate.gate_digest,
            "authorization_digest": authorization.authorization_digest,
            "token_digest": token.token_digest,
            "receipt_digest": receipt.receipt_digest,
            "transition_digest": transition.transition_digest,
            "envelope_digest": envelope.envelope_digest,
            "injected_kernel_calls": 1,
            "structural_field_steps": 1,
            "production_kernel_calls": 0,
            "newly_computed_field_steps": 0,
            "token_consumed_before_kernel": True,
            "receipt_sealed_after_kernel": True,
            "transition_built_after_receipt": True,
            "token_retired_after_complete_result": token.retired,
            "atomic_complete_return": True,
            "retry_permitted": False,
            "persistence_performed": False,
            "claims_permitted": False,
            "decision": (
                "SYNTHETIC_ATOMIC_ADAPTER_FLOW_VALIDATED_"
                "PRODUCTION_KERNEL_CLOSED"
            ),
        }
        payload = dict(values)
        return E1FormationS1HESyntheticGatedSingleBatchResult(
            **values,
            result_digest=_digest(payload),
            receipt=receipt,
            transition=transition,
            envelope=envelope,
        )
    except Exception as exc:
        if not token.retired:
            token.retire("real-attempt-failure")
        if isinstance(exc, E1FormationS1HESyntheticGatedSingleBatchAdapterError):
            raise
        raise E1FormationS1HESyntheticGatedSingleBatchAdapterError(
            "S1-HE synthetic adapter flow failed; no partial result returned"
        ) from exc
