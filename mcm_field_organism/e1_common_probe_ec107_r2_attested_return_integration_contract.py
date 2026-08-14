"""S1-EC107 static EC67 authorization and attested-return integration contract."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_ec106_attestation_receipts import (
    E1CommonProbeEC106R2ProducerReceipt,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
    run_e1_common_probe_n2_r2_real_mode_coordinator,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC107R2AttestedReturnIntegrationContractError(ValueError):
    """Raised when EC107 changes or opens the proposed EC67 integration."""


S1_EC107_CONTRACT_ID = "e1.common-probe-r2-attested-return-integration.s1ec107.v1"
S1_EC107_TOKEN_SCHEMA = (
    "authorization_id",
    "authorization_digest",
    "source_gate_digest",
    "source_handoff_digest",
    "maximum_field_steps",
    "persistence_permitted",
    "retry_permitted",
    "consumed",
)
S1_EC107_RETURN_ENVELOPE_SCHEMA = (
    "envelope_id",
    "authorization_digest",
    "source_result_digest",
    "producer_receipt_digest",
    "result_and_receipt_returned_together",
    "field_steps_executed",
    "persistence_performed",
    "retry_permitted",
    "envelope_digest",
    "result",
    "producer_receipt",
)
S1_EC107_CONSUMPTION_SEQUENCE = (
    "validate-handoff-gate-token-and-exact-adapters",
    "verify-token-unconsumed-and-budget-3208",
    "consume-token-immediately-before-first-adapter",
    "execute-four-formations-and-eight-probes-once",
    "build-and-validate-ec67-result",
    "build-r2-producer-receipt-inside-coordinator",
    "return-result-and-receipt-in-one-immutable-envelope",
)
S1_EC107_FAILURE_SEMANTICS = (
    (
        "before-token-consumption",
        "zero-adapter-calls-token-remains-unconsumed-no-receipt",
    ),
    (
        "after-token-consumption-before-envelope",
        "attempt-consumed-no-retry-no-receipt-no-partial-success",
    ),
    (
        "successful-envelope",
        "exactly-3208-steps-token-consumed-result-and-receipt-bound",
    ),
)
S1_EC107_REQUIRED_SIGNATURE_CHANGES = (
    ("remove", "preflight_and_owner_released: bool"),
    ("add", "gate: typed-current-r2-release-gate"),
    ("add", "authorization: E1CommonProbeEC107R2AuthorizationToken"),
    ("return", "E1CommonProbeEC107R2AttestedCoordinatorEnvelope"),
)
S1_EC107_CHECK_NAMES = (
    "current-ec67-uses-boolean-release",
    "current-ec67-has-no-authorization-token",
    "current-ec67-returns-bare-result",
    "current-result-has-exact-r2-budget",
    "ec106-r2-receipt-type-exists",
    "new-token-must-bind-owner-gate-handoff-and-budget",
    "token-consumption-precedes-first-adapter",
    "receipt-construction-follows-result-validation",
    "result-and-receipt-return-atomically",
    "audit-does-not-call-coordinator-adapter-writer-or-decider",
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
class E1CommonProbeEC107R2AttestedReturnIntegrationContract:
    contract_id: str
    token_schema: tuple[str, ...]
    return_envelope_schema: tuple[str, ...]
    consumption_sequence: tuple[str, ...]
    failure_semantics: tuple[tuple[str, str], ...]
    required_signature_changes: tuple[tuple[str, str], ...]
    checks: tuple[tuple[str, bool], ...]
    exact_field_step_budget: int
    exact_formation_count: int
    exact_probe_count: int
    owner_authorization_text_required_before_token_creation: bool
    token_single_process_and_single_use: bool
    token_consumed_immediately_before_first_adapter: bool
    receipt_built_only_inside_successful_coordinator: bool
    bare_result_return_forbidden_after_integration: bool
    partial_success_return_forbidden: bool
    current_coordinator_change_required: bool
    token_implemented: bool
    return_envelope_implemented: bool
    coordinator_integration_implemented: bool
    execution_permitted: bool
    persistence_permitted: bool
    retry_permitted: bool
    ec102_ingress_permitted: bool
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
            self.contract_id != S1_EC107_CONTRACT_ID
            or self.token_schema != S1_EC107_TOKEN_SCHEMA
            or self.return_envelope_schema != S1_EC107_RETURN_ENVELOPE_SCHEMA
            or self.consumption_sequence != S1_EC107_CONSUMPTION_SEQUENCE
            or self.failure_semantics != S1_EC107_FAILURE_SEMANTICS
            or self.required_signature_changes
            != S1_EC107_REQUIRED_SIGNATURE_CHANGES
            or tuple(name for name, _ in self.checks) != S1_EC107_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or (
                self.exact_field_step_budget,
                self.exact_formation_count,
                self.exact_probe_count,
            )
            != (3208, 4, 8)
            or any(
                value is not True
                for value in (
                    self.owner_authorization_text_required_before_token_creation,
                    self.token_single_process_and_single_use,
                    self.token_consumed_immediately_before_first_adapter,
                    self.receipt_built_only_inside_successful_coordinator,
                    self.bare_result_return_forbidden_after_integration,
                    self.partial_success_return_forbidden,
                    self.current_coordinator_change_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.token_implemented,
                    self.return_envelope_implemented,
                    self.coordinator_integration_implemented,
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.retry_permitted,
                    self.ec102_ingress_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "EC67_ATTESTED_RETURN_INTEGRATION_SPECIFIED_NOT_IMPLEMENTED"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1CommonProbeEC107R2AttestedReturnIntegrationContractError(
                "S1-EC107 integration contract changed or opened execution"
            )


def audit_e1_common_probe_ec107_r2_attested_return_integration_contract(
) -> E1CommonProbeEC107R2AttestedReturnIntegrationContract:
    """Specify the EC67 migration without invoking or modifying EC67."""

    signature = inspect.signature(run_e1_common_probe_n2_r2_real_mode_coordinator)
    result_fields = E1CommonProbeN2R2RealModeCoordinatorResult.__dataclass_fields__
    receipt_fields = E1CommonProbeEC106R2ProducerReceipt.__dataclass_fields__
    source = inspect.getsource(
        audit_e1_common_probe_ec107_r2_attested_return_integration_contract
    )
    called = _called_names(source)
    forbidden_calls = {
        "run_e1_common_probe_n2_r2_real_mode_coordinator",
        "run_e1_common_probe_real_formation_receipt_adapter",
        "build_e1_common_probe_real_fresh_field_adapter",
        "run_e1_common_probe_real_probe_receipt_adapter",
        "decide_common_probe_evidence",
        "write_text",
        "write_bytes",
        "open",
    }
    checks = (
        (
            S1_EC107_CHECK_NAMES[0],
            "preflight_and_owner_released" in signature.parameters,
        ),
        (S1_EC107_CHECK_NAMES[1], "authorization" not in signature.parameters),
        (
            S1_EC107_CHECK_NAMES[2],
            str(signature.return_annotation)
            == "E1CommonProbeN2R2RealModeCoordinatorResult",
        ),
        (
            S1_EC107_CHECK_NAMES[3],
            {
                "accounted_total_steps",
                "actual_field_steps_executed",
                "formation_count",
                "probe_count",
            }.issubset(result_fields),
        ),
        (
            S1_EC107_CHECK_NAMES[4],
            {
                "one_shot_authorization_digest",
                "source_result_digest",
                "source_probe_receipt_digests",
                "receipt_digest",
            }.issubset(receipt_fields),
        ),
        (
            S1_EC107_CHECK_NAMES[5],
            set(S1_EC107_TOKEN_SCHEMA)
            >= {
                "authorization_digest",
                "source_gate_digest",
                "source_handoff_digest",
                "maximum_field_steps",
            },
        ),
        (
            S1_EC107_CHECK_NAMES[6],
            S1_EC107_CONSUMPTION_SEQUENCE.index(
                "consume-token-immediately-before-first-adapter"
            )
            < S1_EC107_CONSUMPTION_SEQUENCE.index(
                "execute-four-formations-and-eight-probes-once"
            ),
        ),
        (
            S1_EC107_CHECK_NAMES[7],
            S1_EC107_CONSUMPTION_SEQUENCE.index(
                "build-and-validate-ec67-result"
            )
            < S1_EC107_CONSUMPTION_SEQUENCE.index(
                "build-r2-producer-receipt-inside-coordinator"
            ),
        ),
        (
            S1_EC107_CHECK_NAMES[8],
            S1_EC107_CONSUMPTION_SEQUENCE[-1]
            == "return-result-and-receipt-in-one-immutable-envelope",
        ),
        (S1_EC107_CHECK_NAMES[9], called.isdisjoint(forbidden_calls)),
    )
    values = {
        "contract_id": S1_EC107_CONTRACT_ID,
        "token_schema": S1_EC107_TOKEN_SCHEMA,
        "return_envelope_schema": S1_EC107_RETURN_ENVELOPE_SCHEMA,
        "consumption_sequence": S1_EC107_CONSUMPTION_SEQUENCE,
        "failure_semantics": S1_EC107_FAILURE_SEMANTICS,
        "required_signature_changes": S1_EC107_REQUIRED_SIGNATURE_CHANGES,
        "checks": checks,
        "exact_field_step_budget": 3208,
        "exact_formation_count": 4,
        "exact_probe_count": 8,
        "owner_authorization_text_required_before_token_creation": True,
        "token_single_process_and_single_use": True,
        "token_consumed_immediately_before_first_adapter": True,
        "receipt_built_only_inside_successful_coordinator": True,
        "bare_result_return_forbidden_after_integration": True,
        "partial_success_return_forbidden": True,
        "current_coordinator_change_required": True,
        "token_implemented": False,
        "return_envelope_implemented": False,
        "coordinator_integration_implemented": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "ec102_ingress_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "EC67_ATTESTED_RETURN_INTEGRATION_SPECIFIED_NOT_IMPLEMENTED",
        "reason": (
            "EC67 still accepts a boolean release and returns a bare result; "
            "a consumed one-shot token and atomic result-receipt envelope are "
            "specified but intentionally not implemented"
        ),
    }
    return E1CommonProbeEC107R2AttestedReturnIntegrationContract(
        **values, contract_digest=_digest(values)
    )
