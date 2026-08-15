"""S1-GU static contract for a pure provenance-bound real transition builder."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
)
from .e1_formation_s1gq_carrier_transition_schema import (
    E1FormationS1GQRealFieldCarrierTransition,
    bind_e1_formation_s1gq_carrier_transition_envelope,
)
from .e1_formation_s1gs_real_single_batch_gate_contract import (
    E1FormationS1GSRealSingleBatchGateContract,
    build_e1_formation_s1gs_real_single_batch_gate_contract,
)
from .e1_refined_formation_runner import _digest
from .shared_mcm_field import SharedMCMField


class E1FormationS1GURealTransitionBuilderContractError(ValueError):
    """Raised when the builder contract loses provenance or opens execution."""


S1_GU_CONTRACT_ID = "e1.real-transition-builder-contract.s1gu.v1"
S1_GU_BUILDER_INTERFACE = (
    ("fresh", "E1FormationS1GHFreshFieldBinding"),
    ("batch", "ReceptorProposalBatch"),
    ("previous_carrier", "E1FormationS1GNLiveFieldCarrier"),
    ("next_field", "SharedMCMField"),
    ("adapter_call_receipt", "E1FormationS1GVRealAdapterCallReceipt"),
    ("return", "E1FormationS1GQRealFieldCarrierTransition"),
)
S1_GU_REQUIRED_ADAPTER_RECEIPT_FIELDS = (
    "gate_digest",
    "authorization_digest",
    "consumed_token_digest",
    "binding_digest",
    "batch_index",
    "batch_step_start_tick",
    "batch_step_end_tick",
    "previous_carrier_digest",
    "previous_field_digest",
    "next_field_digest",
    "source_state_digest_before",
    "source_state_digest_after",
    "fixed_adapter_digest_before",
    "fixed_adapter_digest_after",
    "kernel_name",
    "token_consumed_before_adapter",
    "next_field_object_replaced",
    "adapter_calls",
    "field_steps_executed",
    "persistence_performed",
    "claims_permitted",
    "receipt_digest",
)
S1_GU_VALIDATION_SEQUENCE = (
    "validate-closed-s1gs-gate-contract",
    "validate-exact-fresh-batch-and-previous-carrier-route",
    "validate-typed-adapter-call-receipt-before-building",
    "bind-receipt-to-consumed-token-and-s1gs-gate",
    "bind-receipt-to-previous-carrier-and-field-digest",
    "bind-next-field-object-and-recomputed-digest-to-receipt",
    "require-new-field-object-and-one-layer-tick-advance",
    "require-source-state-and-fixed-adapter-digests-unchanged",
    "construct-next-carrier-with-one-batch-support-and-step-increment",
    "construct-s1gq-real-transition",
    "validate-real-transition-through-shared-envelope",
    "return-only-complete-transition-after-all-checks",
)
S1_GU_ABORT_CONDITIONS = (
    "adapter-call-receipt-missing-untyped-or-digest-invalid",
    "receipt-gate-authorization-or-consumed-token-mismatch",
    "fresh-batch-carrier-route-or-order-mismatch",
    "previous-carrier-or-field-digest-mismatch",
    "next-field-object-is-reused-or-digest-mismatched",
    "next-field-neuron-order-anatomy-or-tick-mismatch",
    "adapter-call-count-or-field-step-count-is-not-one",
    "source-state-or-fixed-adapter-attestation-changed",
    "real-envelope-validation-fails",
    "retry-persistence-reparametrization-partial-return-or-claim-requested",
)
S1_GU_CHECK_NAMES = (
    "s1gs-source-gate-is-closed-at-one-call-and-step",
    "current-carrier-and-next-field-types-are-explicit",
    "s1gq-real-transition-has-required-carrier-and-digest-fields",
    "shared-envelope-accepts-one-transition-parameter",
    "next-field-alone-is-not-accepted-as-kernel-provenance",
    "adapter-call-receipt-binds-token-route-fields-and-attestations",
    "builder-implementation-only-is-open-after-receipt-schema",
    "contract-calls-no-adapter-kernel-token-or-writer",
)


def _called_names(source: str) -> frozenset[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return frozenset(names)


@dataclass(frozen=True, slots=True)
class E1FormationS1GURealTransitionBuilderContract:
    contract_id: str
    source_s1gs_gate_digest: str
    builder_interface: tuple[tuple[str, str], ...]
    required_adapter_receipt_fields: tuple[str, ...]
    validation_sequence: tuple[str, ...]
    abort_conditions: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    next_field_alone_is_sufficient_provenance: bool
    typed_adapter_call_receipt_required: bool
    adapter_call_receipt_schema_implemented: bool
    pure_transition_builder_implementation_permitted: bool
    pure_transition_builder_implemented: bool
    adapter_or_kernel_access_permitted: bool
    authorization_token_creation_permitted: bool
    execution_permitted: bool
    retry_permitted: bool
    persistence_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if (
            self.contract_id != S1_GU_CONTRACT_ID
            or len(self.source_s1gs_gate_digest) != 64
            or self.builder_interface != S1_GU_BUILDER_INTERFACE
            or self.required_adapter_receipt_fields
            != S1_GU_REQUIRED_ADAPTER_RECEIPT_FIELDS
            or self.validation_sequence != S1_GU_VALIDATION_SEQUENCE
            or self.abort_conditions != S1_GU_ABORT_CONDITIONS
            or tuple(name for name, _ in self.checks) != S1_GU_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.typed_adapter_call_receipt_required is not True
            or any(
                value is not False
                for value in (
                    self.next_field_alone_is_sufficient_provenance,
                    self.adapter_call_receipt_schema_implemented,
                    self.pure_transition_builder_implementation_permitted,
                    self.pure_transition_builder_implemented,
                    self.adapter_or_kernel_access_permitted,
                    self.authorization_token_creation_permitted,
                    self.execution_permitted,
                    self.retry_permitted,
                    self.persistence_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "REAL_TRANSITION_BUILDER_BOUND_TYPED_ADAPTER_CALL_RECEIPT_REQUIRED"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1GURealTransitionBuilderContractError(
                "S1-GU contract lost provenance or opened execution"
            )


def audit_e1_formation_s1gu_real_transition_builder_contract(
) -> E1FormationS1GURealTransitionBuilderContract:
    """Bind the pure builder boundary without implementing or calling it."""

    gate = build_e1_formation_s1gs_real_single_batch_gate_contract()
    if not isinstance(gate, E1FormationS1GSRealSingleBatchGateContract):
        raise E1FormationS1GURealTransitionBuilderContractError(
            "S1-GU requires the exact S1-GS gate contract"
        )
    gate.__post_init__()
    carrier_fields = set(E1FormationS1GNLiveFieldCarrier.__dataclass_fields__)
    real_transition_fields = set(
        E1FormationS1GQRealFieldCarrierTransition.__dataclass_fields__
    )
    envelope_parameters = tuple(
        inspect.signature(
            bind_e1_formation_s1gq_carrier_transition_envelope
        ).parameters
    )
    audit_source = inspect.getsource(
        audit_e1_formation_s1gu_real_transition_builder_contract
    )
    forbidden_calls = {
        "map_proposal_batch_to_transient_docks",
        "project_transient_docks_to_neuron_inputs",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "issue_e1_formation_s1gt_synthetic_single_use_token",
        "consume",
        "open",
        "write_text",
        "write_bytes",
    }
    checks = (
        (
            S1_GU_CHECK_NAMES[0],
            gate.maximum_adapter_calls == 1
            and gate.maximum_field_steps == 1
            and gate.execution_permitted is False,
        ),
        (
            S1_GU_CHECK_NAMES[1],
            "current_field" in carrier_fields
            and "current_field_digest" in carrier_fields
            and inspect.isclass(SharedMCMField),
        ),
        (
            S1_GU_CHECK_NAMES[2],
            {
                "previous_carrier",
                "next_carrier",
                "previous_field_digest",
                "next_field_digest",
                "actual_field_steps_executed",
                "transition_digest",
            }.issubset(real_transition_fields),
        ),
        (S1_GU_CHECK_NAMES[3], envelope_parameters == ("transition",)),
        (
            S1_GU_CHECK_NAMES[4],
            ("next_field", "SharedMCMField") in S1_GU_BUILDER_INTERFACE
            and (
                "adapter_call_receipt",
                "E1FormationS1GVRealAdapterCallReceipt",
            )
            in S1_GU_BUILDER_INTERFACE,
        ),
        (
            S1_GU_CHECK_NAMES[5],
            {
                "gate_digest",
                "authorization_digest",
                "consumed_token_digest",
                "previous_carrier_digest",
                "next_field_digest",
                "source_state_digest_before",
                "source_state_digest_after",
                "fixed_adapter_digest_before",
                "fixed_adapter_digest_after",
                "kernel_name",
                "token_consumed_before_adapter",
                "next_field_object_replaced",
                "adapter_calls",
                "field_steps_executed",
            }.issubset(S1_GU_REQUIRED_ADAPTER_RECEIPT_FIELDS),
        ),
        (
            S1_GU_CHECK_NAMES[6],
            "validate-typed-adapter-call-receipt-before-building"
            in S1_GU_VALIDATION_SEQUENCE,
        ),
        (
            S1_GU_CHECK_NAMES[7],
            _called_names(audit_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "contract_id": S1_GU_CONTRACT_ID,
        "source_s1gs_gate_digest": gate.gate_digest,
        "builder_interface": S1_GU_BUILDER_INTERFACE,
        "required_adapter_receipt_fields": (
            S1_GU_REQUIRED_ADAPTER_RECEIPT_FIELDS
        ),
        "validation_sequence": S1_GU_VALIDATION_SEQUENCE,
        "abort_conditions": S1_GU_ABORT_CONDITIONS,
        "checks": checks,
        "next_field_alone_is_sufficient_provenance": False,
        "typed_adapter_call_receipt_required": True,
        "adapter_call_receipt_schema_implemented": False,
        "pure_transition_builder_implementation_permitted": False,
        "pure_transition_builder_implemented": False,
        "adapter_or_kernel_access_permitted": False,
        "authorization_token_creation_permitted": False,
        "execution_permitted": False,
        "retry_permitted": False,
        "persistence_permitted": False,
        "claims_permitted": False,
        "decision": (
            "REAL_TRANSITION_BUILDER_BOUND_TYPED_ADAPTER_CALL_RECEIPT_REQUIRED"
        ),
        "reason": (
            "a-new-shared-field-object-alone-cannot-prove-one-authorized-"
            "kernel-call;the-pure-builder-must-require-a-typed-receipt-binding-"
            "gate-token-route-before-and-after-field-digests-and-unchanged-"
            "source-state-and-fixed-adapter-attestations"
        ),
    }
    return E1FormationS1GURealTransitionBuilderContract(
        **values,
        contract_digest=_digest(values),
    )
