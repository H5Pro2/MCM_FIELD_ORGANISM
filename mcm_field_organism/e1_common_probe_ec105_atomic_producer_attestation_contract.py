"""S1-EC105 static contract for atomic EC67/EC96 producer attestations."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_ec96_authorized_r4_r8_once import (
    E1CommonProbeEC96AtomicResult,
    run_e1_common_probe_ec96_authorized_r4_r8_once,
)
from .e1_common_probe_ec102_coordinator_result_extractor import (
    extract_e1_common_probe_ec102_coordinator_results,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
    run_e1_common_probe_n2_r2_real_mode_coordinator,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC105AtomicProducerAttestationContractError(ValueError):
    """Raised when the static EC105 attestation contract is opened or changed."""


S1_EC105_CONTRACT_ID = "e1.common-probe-producer-attestation-contract.s1ec105.v1"
S1_EC105_PRODUCER_RECEIPT_SCHEMA = (
    "receipt_id",
    "producer_id",
    "one_shot_authorization_digest",
    "source_result_digest",
    "source_probe_receipt_digests",
    "accounted_field_steps",
    "producer_sequence_index",
    "emitted_atomically_with_result",
    "contractual_not_cryptographic",
    "receipt_digest",
)
S1_EC105_INGRESS_ATTESTATION_SCHEMA = (
    "attestation_id",
    "r2_producer_receipt_digest",
    "r4_r8_producer_receipt_digest",
    "source_result_digests",
    "source_probe_receipt_digests",
    "accounted_field_steps",
    "producer_sequence",
    "both_receipts_validated",
    "same_objects_forwarded_to_ec102",
    "contractual_not_cryptographic",
    "attestation_digest",
)
S1_EC105_PRODUCER_BINDINGS = (
    (
        "EC67-r2",
        "E1CommonProbeN2R2RealModeCoordinatorResult.result_digest",
        "E1CommonProbeN2R2RealModeCoordinatorResult.probe_receipt_digests",
        8,
        3208,
        "new-explicit-one-shot-authorization-required",
    ),
    (
        "EC96-r4-r8",
        "E1CommonProbeEC96AtomicResult.result_digest",
        "E1CommonProbeEC96AtomicResult.refinements[*].probe_receipt_digests",
        16,
        19248,
        "existing-consumed-EC96-authorization-digest",
    ),
)
S1_EC105_PRODUCER_SEQUENCE = ("EC67-r2", "EC96-r4-r8", "EC102-ingress")
S1_EC105_INTEGRATION_POINTS = (
    (
        "run_e1_common_probe_n2_r2_real_mode_coordinator",
        "return-result-and-r2-producer-receipt-atomically",
        "missing",
    ),
    (
        "run_e1_common_probe_ec96_authorized_r4_r8_once",
        "return-result-and-r4-r8-producer-receipt-atomically",
        "missing",
    ),
    (
        "extract_e1_common_probe_ec102_coordinator_results",
        "require-and-validate-one-combined-ingress-attestation",
        "missing",
    ),
)
S1_EC105_CHECK_NAMES = (
    "ec67-result-exposes-bound-result-and-eight-probe-digests",
    "ec96-result-exposes-bound-result-and-sixteen-probe-digests",
    "ec67-lacks-explicit-one-shot-authorization-object",
    "ec96-receives-explicit-authorization-object",
    "ec67-does-not-return-producer-receipt",
    "ec96-does-not-return-producer-receipt",
    "ec102-does-not-require-ingress-attestation",
    "producer-budgets-sum-to-22456",
    "producer-probe-counts-sum-to-24",
    "audit-does-not-call-production-path",
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
class E1CommonProbeEC105AtomicProducerAttestationContract:
    contract_id: str
    producer_receipt_schema: tuple[str, ...]
    ingress_attestation_schema: tuple[str, ...]
    producer_bindings: tuple[tuple[str, str, str, int, int, str], ...]
    producer_sequence: tuple[str, ...]
    integration_points: tuple[tuple[str, str, str], ...]
    checks: tuple[tuple[str, bool], ...]
    total_source_result_count: int
    total_source_probe_count: int
    total_accounted_field_steps: int
    attestation_must_be_emitted_with_each_result: bool
    posthoc_self_attestation_forbidden: bool
    digest_chain_detects_accidental_lineage_change: bool
    cryptographic_or_external_execution_proof_provided: bool
    trust_scope: str
    producer_integration_implemented: bool
    ec102_integration_implemented: bool
    real_result_ingress_permitted: bool
    execution_permitted: bool
    persistence_permitted: bool
    retry_permitted: bool
    ec46_decision_permitted: bool
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
            self.contract_id != S1_EC105_CONTRACT_ID
            or self.producer_receipt_schema != S1_EC105_PRODUCER_RECEIPT_SCHEMA
            or self.ingress_attestation_schema
            != S1_EC105_INGRESS_ATTESTATION_SCHEMA
            or self.producer_bindings != S1_EC105_PRODUCER_BINDINGS
            or self.producer_sequence != S1_EC105_PRODUCER_SEQUENCE
            or self.integration_points != S1_EC105_INTEGRATION_POINTS
            or tuple(name for name, _ in self.checks) != S1_EC105_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or (
                self.total_source_result_count,
                self.total_source_probe_count,
                self.total_accounted_field_steps,
            )
            != (2, 24, 22456)
            or any(
                value is not True
                for value in (
                    self.attestation_must_be_emitted_with_each_result,
                    self.posthoc_self_attestation_forbidden,
                    self.digest_chain_detects_accidental_lineage_change,
                )
            )
            or self.cryptographic_or_external_execution_proof_provided is not False
            or self.trust_scope != "in-process-contractual-not-cryptographic"
            or any(
                value is not False
                for value in (
                    self.producer_integration_implemented,
                    self.ec102_integration_implemented,
                    self.real_result_ingress_permitted,
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.retry_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "ATTESTATION_CONTRACT_SPECIFIED_INTEGRATION_NOT_IMPLEMENTED"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1CommonProbeEC105AtomicProducerAttestationContractError(
                "S1-EC105 attestation contract changed or opened execution"
            )


def audit_e1_common_probe_ec105_atomic_producer_attestation_contract(
) -> E1CommonProbeEC105AtomicProducerAttestationContract:
    """Bind the future receipt schemas without invoking any producer."""

    r2_fields = E1CommonProbeN2R2RealModeCoordinatorResult.__dataclass_fields__
    r4_r8_fields = E1CommonProbeEC96AtomicResult.__dataclass_fields__
    r2_signature = inspect.signature(
        run_e1_common_probe_n2_r2_real_mode_coordinator
    )
    r4_r8_signature = inspect.signature(
        run_e1_common_probe_ec96_authorized_r4_r8_once
    )
    extractor_signature = inspect.signature(
        extract_e1_common_probe_ec102_coordinator_results
    )
    source = inspect.getsource(
        audit_e1_common_probe_ec105_atomic_producer_attestation_contract
    )
    called = _called_names(source)
    production_calls = {
        "run_e1_common_probe_n2_r2_real_mode_coordinator",
        "run_e1_common_probe_ec96_authorized_r4_r8_once",
        "extract_e1_common_probe_ec102_coordinator_results",
        "run_e1_common_probe_real_formation_wrapper",
        "run_e1_common_probe_real_probe_wrapper",
        "decide_common_probe_evidence",
        "write_text",
        "write_bytes",
        "open",
    }
    checks = (
        (
            S1_EC105_CHECK_NAMES[0],
            "result_digest" in r2_fields and "probe_receipt_digests" in r2_fields,
        ),
        (
            S1_EC105_CHECK_NAMES[1],
            "result_digest" in r4_r8_fields and "refinements" in r4_r8_fields,
        ),
        (
            S1_EC105_CHECK_NAMES[2],
            "authorization" not in r2_signature.parameters,
        ),
        (
            S1_EC105_CHECK_NAMES[3],
            "authorization" in r4_r8_signature.parameters,
        ),
        (
            S1_EC105_CHECK_NAMES[4],
            str(r2_signature.return_annotation)
            == "E1CommonProbeN2R2RealModeCoordinatorResult",
        ),
        (
            S1_EC105_CHECK_NAMES[5],
            str(r4_r8_signature.return_annotation) == "E1CommonProbeEC96AtomicResult",
        ),
        (
            S1_EC105_CHECK_NAMES[6],
            "producer_attestation" not in extractor_signature.parameters,
        ),
        (
            S1_EC105_CHECK_NAMES[7],
            sum(item[4] for item in S1_EC105_PRODUCER_BINDINGS) == 22456,
        ),
        (
            S1_EC105_CHECK_NAMES[8],
            sum(item[3] for item in S1_EC105_PRODUCER_BINDINGS) == 24,
        ),
        (S1_EC105_CHECK_NAMES[9], called.isdisjoint(production_calls)),
    )
    values = {
        "contract_id": S1_EC105_CONTRACT_ID,
        "producer_receipt_schema": S1_EC105_PRODUCER_RECEIPT_SCHEMA,
        "ingress_attestation_schema": S1_EC105_INGRESS_ATTESTATION_SCHEMA,
        "producer_bindings": S1_EC105_PRODUCER_BINDINGS,
        "producer_sequence": S1_EC105_PRODUCER_SEQUENCE,
        "integration_points": S1_EC105_INTEGRATION_POINTS,
        "checks": checks,
        "total_source_result_count": 2,
        "total_source_probe_count": 24,
        "total_accounted_field_steps": 22456,
        "attestation_must_be_emitted_with_each_result": True,
        "posthoc_self_attestation_forbidden": True,
        "digest_chain_detects_accidental_lineage_change": True,
        "cryptographic_or_external_execution_proof_provided": False,
        "trust_scope": "in-process-contractual-not-cryptographic",
        "producer_integration_implemented": False,
        "ec102_integration_implemented": False,
        "real_result_ingress_permitted": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "ATTESTATION_CONTRACT_SPECIFIED_INTEGRATION_NOT_IMPLEMENTED",
        "reason": (
            "EC67 needs an explicit one-shot authorization and both producers "
            "must emit bound receipts with their results before EC102 may form "
            "one contractual ingress attestation"
        ),
    }
    return E1CommonProbeEC105AtomicProducerAttestationContract(
        **values, contract_digest=_digest(values)
    )
