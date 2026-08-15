"""S1-HD private receipt sealer for one completed adapter-boundary call."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_formation_s1fw_synthetic_live_state_handoff import _adapter_digest
from .e1_formation_s1gh_fresh_field_bridge import E1FormationS1GHFreshFieldBinding
from .e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
    e1_formation_s1gn_current_field_digest,
)
from .e1_formation_s1gs_real_single_batch_gate_contract import (
    E1FormationS1GSRealSingleBatchGateContract,
)
from .e1_formation_s1gv_real_adapter_call_receipt_schema import (
    E1FormationS1GVRealAdapterCallReceipt,
    S1_GV_KERNEL_NAME,
    S1_GV_RECEIPT_ID,
)
from .e1_formation_s1gw_external_owner_authorization_schema import (
    E1FormationS1GWExternalOwnerAuthorization,
)
from .e1_formation_s1gx_deterministic_single_batch_target import (
    E1FormationS1GXDeterministicSingleBatchTarget,
)
from .e1_formation_s1hc_real_single_use_token import (
    E1FormationS1HCRealSingleUseToken,
)
from .e1_refined_formation_runner import _digest, _state_payload
from .receptor_proposal_handoff import ReceptorProposalBatch
from .shared_mcm_field import SharedMCMField


class E1FormationS1HDPrivateAtomicReceiptFactoryError(ValueError):
    """Raised when completed call evidence cannot be sealed exactly once."""


S1_HD_EVIDENCE_ID = "e1.completed-adapter-boundary-evidence.s1hd.v1"


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1HDCompletedAdapterBoundaryEvidence:
    """Adapter-owned evidence shape; this module provides no evidence factory."""

    evidence_id: str
    authorization_digest: str
    consumed_token_digest: str
    gate_digest: str
    binding_digest: str
    batch_index: int
    batch_step_start_tick: int
    batch_step_end_tick: int
    previous_carrier_digest: str
    previous_field_digest: str
    next_field_digest: str
    source_state_digest_before: str
    source_state_digest_after: str
    fixed_adapter_digest_before: str
    fixed_adapter_digest_after: str
    kernel_name: str
    token_consumed_before_adapter: bool
    next_field_object_replaced: bool
    adapter_calls: int
    field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    evidence_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "evidence_digest"
        }
        if (
            self.evidence_id != S1_HD_EVIDENCE_ID
            or not all(
                _valid_digest(value)
                for value in (
                    self.authorization_digest,
                    self.consumed_token_digest,
                    self.gate_digest,
                    self.binding_digest,
                    self.previous_carrier_digest,
                    self.previous_field_digest,
                    self.next_field_digest,
                    self.source_state_digest_before,
                    self.source_state_digest_after,
                    self.fixed_adapter_digest_before,
                    self.fixed_adapter_digest_after,
                )
            )
            or isinstance(self.batch_index, bool)
            or not isinstance(self.batch_index, int)
            or self.batch_index < 0
            or self.batch_step_start_tick < 0
            or self.batch_step_end_tick <= self.batch_step_start_tick
            or self.previous_field_digest == self.next_field_digest
            or self.source_state_digest_before != self.source_state_digest_after
            or self.fixed_adapter_digest_before != self.fixed_adapter_digest_after
            or self.kernel_name != S1_GV_KERNEL_NAME
            or self.token_consumed_before_adapter is not True
            or self.next_field_object_replaced is not True
            or self.adapter_calls != 1
            or self.field_steps_executed != 1
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.evidence_digest != _digest(payload)
        ):
            raise E1FormationS1HDPrivateAtomicReceiptFactoryError(
                "S1-HD completed call evidence lost exact one-step provenance"
            )


def _seal_e1_formation_s1hd_real_adapter_call_receipt(
    authorization: E1FormationS1GWExternalOwnerAuthorization,
    token: E1FormationS1HCRealSingleUseToken,
    gate: E1FormationS1GSRealSingleBatchGateContract,
    target: E1FormationS1GXDeterministicSingleBatchTarget,
    fresh: E1FormationS1GHFreshFieldBinding,
    batch: ReceptorProposalBatch,
    previous_carrier: E1FormationS1GNLiveFieldCarrier,
    next_field: SharedMCMField,
    evidence: E1FormationS1HDCompletedAdapterBoundaryEvidence,
) -> E1FormationS1GVRealAdapterCallReceipt:
    """Seal completed evidence without consuming a token or calling an adapter."""

    if (
        not isinstance(
            authorization,
            E1FormationS1GWExternalOwnerAuthorization,
        )
        or not isinstance(token, E1FormationS1HCRealSingleUseToken)
        or not isinstance(gate, E1FormationS1GSRealSingleBatchGateContract)
        or not isinstance(target, E1FormationS1GXDeterministicSingleBatchTarget)
        or not isinstance(fresh, E1FormationS1GHFreshFieldBinding)
        or not isinstance(batch, ReceptorProposalBatch)
        or not isinstance(previous_carrier, E1FormationS1GNLiveFieldCarrier)
        or not isinstance(next_field, SharedMCMField)
        or not isinstance(evidence, E1FormationS1HDCompletedAdapterBoundaryEvidence)
    ):
        raise E1FormationS1HDPrivateAtomicReceiptFactoryError(
            "S1-HD requires complete typed call-boundary inputs"
        )
    authorization.__post_init__()
    gate.__post_init__()
    target.__post_init__()
    fresh.__post_init__()
    previous_carrier.__post_init__()
    evidence.__post_init__()
    batches = fresh.invocation.context.probe_plan.handoff.batches
    next_field_digest = e1_formation_s1gn_current_field_digest(next_field)
    state_digest = _digest(_state_payload(fresh.invocation.source_state))
    adapter_digest = _adapter_digest(fresh.invocation.fixed_adapter)
    if (
        token.status != "consumed"
        or token.authorization_digest != authorization.authorization_digest
        or token.gate_digest != gate.gate_digest
        or token.run_id != target.run_id
        or token.binding_digest != target.selected_binding_digest
        or token.batch_index != target.selected_batch_index
        or token.carrier_digest != target.selected_carrier_digest
        or authorization.gate_digest != gate.gate_digest
        or authorization.binding_digest != fresh.binding_digest
        or previous_carrier.fresh_binding is not fresh
        or previous_carrier.carrier_digest != target.selected_carrier_digest
        or previous_carrier.completed_batch_count >= len(batches)
        or batches[previous_carrier.completed_batch_count] is not batch
        or batch.batch_index != previous_carrier.completed_batch_count
        or next_field is previous_carrier.current_field
        or next_field_digest == previous_carrier.current_field_digest
        or evidence.authorization_digest != authorization.authorization_digest
        or evidence.consumed_token_digest != token.token_digest
        or evidence.gate_digest != gate.gate_digest
        or evidence.binding_digest != fresh.binding_digest
        or evidence.batch_index != batch.batch_index
        or evidence.batch_step_start_tick != batch.step_time.start_tick
        or evidence.batch_step_end_tick != batch.step_time.end_tick
        or evidence.previous_carrier_digest != previous_carrier.carrier_digest
        or evidence.previous_field_digest != previous_carrier.current_field_digest
        or evidence.next_field_digest != next_field_digest
        or evidence.source_state_digest_before != state_digest
        or evidence.source_state_digest_after != state_digest
        or evidence.fixed_adapter_digest_before != adapter_digest
        or evidence.fixed_adapter_digest_after != adapter_digest
    ):
        raise E1FormationS1HDPrivateAtomicReceiptFactoryError(
            "S1-HD token, route, field, or completed evidence does not match"
        )
    values = {
        "receipt_id": S1_GV_RECEIPT_ID,
        "gate_digest": evidence.gate_digest,
        "authorization_digest": evidence.authorization_digest,
        "consumed_token_digest": evidence.consumed_token_digest,
        "binding_digest": evidence.binding_digest,
        "batch_index": evidence.batch_index,
        "batch_step_start_tick": evidence.batch_step_start_tick,
        "batch_step_end_tick": evidence.batch_step_end_tick,
        "previous_carrier_digest": evidence.previous_carrier_digest,
        "previous_field_digest": evidence.previous_field_digest,
        "next_field_digest": evidence.next_field_digest,
        "source_state_digest_before": evidence.source_state_digest_before,
        "source_state_digest_after": evidence.source_state_digest_after,
        "fixed_adapter_digest_before": evidence.fixed_adapter_digest_before,
        "fixed_adapter_digest_after": evidence.fixed_adapter_digest_after,
        "kernel_name": evidence.kernel_name,
        "token_consumed_before_adapter": evidence.token_consumed_before_adapter,
        "next_field_object_replaced": evidence.next_field_object_replaced,
        "adapter_calls": evidence.adapter_calls,
        "field_steps_executed": evidence.field_steps_executed,
        "persistence_performed": False,
        "claims_permitted": False,
    }
    return E1FormationS1GVRealAdapterCallReceipt(
        **values,
        receipt_digest=_digest(values),
    )
