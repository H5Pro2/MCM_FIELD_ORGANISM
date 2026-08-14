"""S1-EC114 static contract for an external owner-origin attestation."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_ec110_owner_scope_token_factory import (
    S1_EC110_EXTERNAL_RELEASE_SCHEMA,
)
from .e1_common_probe_ec113_synthetic_bridge_validation_receipt import (
    E1CommonProbeEC113SyntheticBridgeValidationReceipt,
    S1_EC113_RECEIPT_ID,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    S1_EC67_EC59_HANDOFF_DIGEST,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC114ExternalOriginAttestationContractError(ValueError):
    """Raised when the static contract opens or weakens external origin."""


S1_EC114_CONTRACT_ID = (
    "e1.common-probe-external-origin-attestation-contract.s1ec114.v1"
)
S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA = (
    "external_event_digest",
    "authenticated_owner_principal_digest",
    "thread_or_session_binding_digest",
    "exact_owner_message_digest",
    "message_sequence_number",
    "fresh_single_use_nonce_digest",
    "source_ec113_receipt_digest",
    "source_gate_digest",
    "source_handoff_digest",
    "observed_after_explicit_owner_message",
    "verified_outside_research_module",
)
S1_EC114_RELEASE_FIELD_MAPPING = (
    ("release_id", "external_event_digest"),
    ("exact_owner_authorization_digest", "exact_owner_message_digest"),
    ("thread_or_session_binding_digest", "thread_or_session_binding_digest"),
    ("source_gate_digest", "source_gate_digest"),
    ("source_handoff_digest", "source_handoff_digest"),
    ("maximum_field_steps", "fixed:3208"),
    ("persistence_permitted", "fixed:false"),
    ("retry_permitted", "fixed:false"),
    ("issued_after_explicit_owner_message", "observed_after_explicit_owner_message"),
    ("release_attestation_digest", "digest:external-attestation-payload"),
)
S1_EC114_REJECTION_RULES = (
    "ec113-structure-receipt-alone-is-insufficient",
    "research-module-cannot-attest-owner-origin",
    "assistant-generated-text-cannot-attest-owner-origin",
    "unauthenticated-principal-fails-closed",
    "message-session-or-gate-mismatch-fails-closed",
    "missing-or-reused-nonce-fails-closed",
    "out-of-order-or-replayed-event-fails-closed",
    "prior-owner-release-never-carries-forward",
)
S1_EC114_CHECK_NAMES = (
    "ec110-release-schema-exact",
    "all-release-fields-mapped-once",
    "ec113-source-receipt-required",
    "owner-principal-and-message-bound",
    "session-gate-and-handoff-bound",
    "freshness-and-order-bound",
    "nonpersistent-no-retry-fixed",
    "research-and-assistant-origin-rejected",
    "current-external-origin-evidence-absent",
    "audit-does-not-call-classifier-validator-factory-coordinator-writer-or-decider",
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
class E1CommonProbeEC114ExternalOriginAttestationContract:
    contract_id: str
    source_receipt_id: str
    required_external_evidence_schema: tuple[str, ...]
    external_release_schema: tuple[str, ...]
    release_field_mapping: tuple[tuple[str, str], ...]
    rejection_rules: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    source_handoff_digest: str
    maximum_field_steps: int
    external_origin_evidence_present: bool
    authenticated_owner_principal_present: bool
    fresh_single_use_nonce_present: bool
    external_attestation_implemented: bool
    external_release_issued: bool
    owner_scope_token_creation_permitted: bool
    execution_permitted: bool
    persistence_permitted: bool
    retry_permitted: bool
    real_result_ingress_permitted: bool
    research_decision_permitted: bool
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
            self.contract_id != S1_EC114_CONTRACT_ID
            or self.source_receipt_id != S1_EC113_RECEIPT_ID
            or self.required_external_evidence_schema
            != S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA
            or self.external_release_schema != S1_EC110_EXTERNAL_RELEASE_SCHEMA
            or self.release_field_mapping != S1_EC114_RELEASE_FIELD_MAPPING
            or self.rejection_rules != S1_EC114_REJECTION_RULES
            or tuple(name for name, _ in self.checks) != S1_EC114_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.source_handoff_digest != S1_EC67_EC59_HANDOFF_DIGEST
            or self.maximum_field_steps != 3208
            or any(
                value is not False
                for value in (
                    self.external_origin_evidence_present,
                    self.authenticated_owner_principal_present,
                    self.fresh_single_use_nonce_present,
                    self.external_attestation_implemented,
                    self.external_release_issued,
                    self.owner_scope_token_creation_permitted,
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.retry_permitted,
                    self.real_result_ingress_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "EXTERNAL_ORIGIN_CONTRACT_BOUND_ATTESTATION_NOT_IMPLEMENTED"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1CommonProbeEC114ExternalOriginAttestationContractError(
                "S1-EC114 contract changed or inferred external owner origin"
            )


def audit_e1_common_probe_ec114_external_origin_attestation_contract(
) -> E1CommonProbeEC114ExternalOriginAttestationContract:
    """Audit schemas and closed state without reading or attesting a message."""

    source = inspect.getsource(
        audit_e1_common_probe_ec114_external_origin_attestation_contract
    )
    called = _called_names(source)
    forbidden_calls = {
        "classify_e1_common_probe_ec112_owner_message",
        "validate_e1_common_probe_ec113_synthetic_bridge_candidate",
        "create_e1_common_probe_ec110_owner_scope_token",
        "run_e1_common_probe_n2_r2_real_mode_coordinator",
        "run_e1_common_probe_real_formation_receipt_adapter",
        "run_e1_common_probe_real_probe_receipt_adapter",
        "decide_common_probe_evidence",
        "write_text",
        "write_bytes",
        "open",
    }
    mapping_targets = tuple(name for name, _ in S1_EC114_RELEASE_FIELD_MAPPING)
    ec113_fields = E1CommonProbeEC113SyntheticBridgeValidationReceipt.__dataclass_fields__
    checks = (
        (S1_EC114_CHECK_NAMES[0], len(S1_EC110_EXTERNAL_RELEASE_SCHEMA) == 10),
        (
            S1_EC114_CHECK_NAMES[1],
            mapping_targets == S1_EC110_EXTERNAL_RELEASE_SCHEMA
            and len(set(mapping_targets)) == len(mapping_targets),
        ),
        (
            S1_EC114_CHECK_NAMES[2],
            "source_ec113_receipt_digest"
            in S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA
            and "receipt_digest" in ec113_fields,
        ),
        (
            S1_EC114_CHECK_NAMES[3],
            {"authenticated_owner_principal_digest", "exact_owner_message_digest"}
            .issubset(S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA),
        ),
        (
            S1_EC114_CHECK_NAMES[4],
            {
                "thread_or_session_binding_digest",
                "source_gate_digest",
                "source_handoff_digest",
            }.issubset(S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA),
        ),
        (
            S1_EC114_CHECK_NAMES[5],
            {"message_sequence_number", "fresh_single_use_nonce_digest"}
            .issubset(S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA),
        ),
        (
            S1_EC114_CHECK_NAMES[6],
            ("persistence_permitted", "fixed:false")
            in S1_EC114_RELEASE_FIELD_MAPPING
            and ("retry_permitted", "fixed:false")
            in S1_EC114_RELEASE_FIELD_MAPPING,
        ),
        (
            S1_EC114_CHECK_NAMES[7],
            {
                "research-module-cannot-attest-owner-origin",
                "assistant-generated-text-cannot-attest-owner-origin",
            }.issubset(S1_EC114_REJECTION_RULES),
        ),
        (S1_EC114_CHECK_NAMES[8], True),
        (S1_EC114_CHECK_NAMES[9], called.isdisjoint(forbidden_calls)),
    )
    values = {
        "contract_id": S1_EC114_CONTRACT_ID,
        "source_receipt_id": S1_EC113_RECEIPT_ID,
        "required_external_evidence_schema": (
            S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA
        ),
        "external_release_schema": S1_EC110_EXTERNAL_RELEASE_SCHEMA,
        "release_field_mapping": S1_EC114_RELEASE_FIELD_MAPPING,
        "rejection_rules": S1_EC114_REJECTION_RULES,
        "checks": checks,
        "source_handoff_digest": S1_EC67_EC59_HANDOFF_DIGEST,
        "maximum_field_steps": 3208,
        "external_origin_evidence_present": False,
        "authenticated_owner_principal_present": False,
        "fresh_single_use_nonce_present": False,
        "external_attestation_implemented": False,
        "external_release_issued": False,
        "owner_scope_token_creation_permitted": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "real_result_ingress_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "EXTERNAL_ORIGIN_CONTRACT_BOUND_ATTESTATION_NOT_IMPLEMENTED",
        "reason": (
            "EC113 proves candidate structure only; no authenticated external "
            "owner event, fresh nonce, or out-of-module attestor is present, so "
            "no release attestation, owner token, or execution may follow"
        ),
    }
    return E1CommonProbeEC114ExternalOriginAttestationContract(
        **values, contract_digest=_digest(values)
    )
