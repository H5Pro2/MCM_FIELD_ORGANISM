"""S1-EC111 static boundary between continuation and explicit run release."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_ec110_owner_scope_token_factory import (
    S1_EC110_EXTERNAL_RELEASE_SCHEMA,
    create_e1_common_probe_ec110_owner_scope_token,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    S1_EC67_EC59_HANDOFF_DIGEST,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC111ExternalOwnerReleaseBridgeContractError(ValueError):
    """Raised when the owner-release bridge contract opens implicit release."""


S1_EC111_CONTRACT_ID = "e1.common-probe-external-owner-release-bridge.s1ec111.v1"
S1_EC111_MESSAGE_CLASSES = (
    (
        "continuation-only",
        "continue closed research or implementation work",
        False,
    ),
    (
        "explicit-run-release-candidate",
        "request exactly one identified bounded real run",
        False,
    ),
    (
        "question-or-discussion",
        "request information or direction without execution",
        False,
    ),
    (
        "stop-or-revoke",
        "stop work or revoke a pending release",
        False,
    ),
)
S1_EC111_CONTINUATION_EXAMPLES = (
    "ok weiter",
    "weiter",
    "fahre fort",
    "entwickle weiter",
)
S1_EC111_EXPLICIT_RELEASE_REQUIREMENTS = (
    "exact-run-id-ec67-r2",
    "exactly-one-run",
    "maximum-3208-field-steps",
    "nonpersistent",
    "no-retry",
    "current-release-gate-bound",
    "ec59-handoff-bound",
    "owner-intent-to-authorize-real-execution-explicit",
    "thread-or-session-binding-present",
)
S1_EC111_REJECTION_RULES = (
    "continuation-never-implies-run-release",
    "prior-release-never-carries-forward",
    "ambiguous-language-fails-closed",
    "missing-run-id-fails-closed",
    "missing-budget-or-once-bound-fails-closed",
    "synthetic-fixture-release-fails-closed",
    "assistant-generated-release-text-fails-closed",
    "release-cannot-be-inferred-from-project-momentum",
)
S1_EC111_BRIDGE_OUTPUT_SCHEMA = (
    "release_id",
    "message_class",
    "exact_owner_authorization_digest",
    "thread_or_session_binding_digest",
    "source_gate_digest",
    "source_handoff_digest",
    "maximum_field_steps",
    "persistence_permitted",
    "retry_permitted",
    "issued_after_explicit_owner_message",
    "release_attestation_digest",
)
S1_EC111_CHECK_NAMES = (
    "all-message-classes-default-no-release",
    "continuation-examples-explicitly-bound",
    "continuation-never-authorizes-run",
    "explicit-candidate-requires-nine-fields",
    "bridge-output-covers-ec110-release-schema",
    "ec59-handoff-fixed",
    "budget-fixed-to-3208",
    "assistant-cannot-generate-owner-release",
    "current-message-class-continuation-only",
    "audit-does-not-call-token-factory-coordinator-writer-or-decider",
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
class E1CommonProbeEC111ExternalOwnerReleaseBridgeContract:
    contract_id: str
    message_classes: tuple[tuple[str, str, bool], ...]
    continuation_examples: tuple[str, ...]
    explicit_release_requirements: tuple[str, ...]
    rejection_rules: tuple[str, ...]
    bridge_output_schema: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    current_message_class: str
    current_message_authorizes_real_run: bool
    continuation_work_permitted: bool
    owner_release_must_originate_outside_research_module: bool
    bridge_may_interpret_ambiguous_text_as_release: bool
    bridge_may_reuse_prior_release: bool
    bridge_may_generate_release_text: bool
    external_release_bridge_implemented: bool
    owner_scope_token_creation_permitted: bool
    execution_permitted: bool
    persistence_permitted: bool
    retry_permitted: bool
    real_result_ingress_permitted: bool
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
            self.contract_id != S1_EC111_CONTRACT_ID
            or self.message_classes != S1_EC111_MESSAGE_CLASSES
            or self.continuation_examples != S1_EC111_CONTINUATION_EXAMPLES
            or self.explicit_release_requirements
            != S1_EC111_EXPLICIT_RELEASE_REQUIREMENTS
            or self.rejection_rules != S1_EC111_REJECTION_RULES
            or self.bridge_output_schema != S1_EC111_BRIDGE_OUTPUT_SCHEMA
            or tuple(name for name, _ in self.checks) != S1_EC111_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.current_message_class != "continuation-only"
            or self.current_message_authorizes_real_run is not False
            or self.continuation_work_permitted is not True
            or self.owner_release_must_originate_outside_research_module is not True
            or any(
                value is not False
                for value in (
                    self.bridge_may_interpret_ambiguous_text_as_release,
                    self.bridge_may_reuse_prior_release,
                    self.bridge_may_generate_release_text,
                    self.external_release_bridge_implemented,
                    self.owner_scope_token_creation_permitted,
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.retry_permitted,
                    self.real_result_ingress_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "CONTINUATION_BOUND_RELEASE_BRIDGE_SPECIFIED_NOT_IMPLEMENTED"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1CommonProbeEC111ExternalOwnerReleaseBridgeContractError(
                "S1-EC111 bridge contract changed or inferred owner release"
            )


def audit_e1_common_probe_ec111_external_owner_release_bridge_contract(
) -> E1CommonProbeEC111ExternalOwnerReleaseBridgeContract:
    """Bind message semantics without reading chat state or issuing a release."""

    factory_signature = inspect.signature(
        create_e1_common_probe_ec110_owner_scope_token
    )
    source = inspect.getsource(
        audit_e1_common_probe_ec111_external_owner_release_bridge_contract
    )
    called = _called_names(source)
    forbidden_calls = {
        "create_e1_common_probe_ec110_owner_scope_token",
        "run_e1_common_probe_n2_r2_real_mode_coordinator",
        "run_e1_common_probe_real_formation_receipt_adapter",
        "run_e1_common_probe_real_probe_receipt_adapter",
        "decide_common_probe_evidence",
        "write_text",
        "write_bytes",
        "open",
    }
    checks = (
        (
            S1_EC111_CHECK_NAMES[0],
            all(release is False for _, _, release in S1_EC111_MESSAGE_CLASSES),
        ),
        (S1_EC111_CHECK_NAMES[1], len(S1_EC111_CONTINUATION_EXAMPLES) == 4),
        (
            S1_EC111_CHECK_NAMES[2],
            "continuation-never-implies-run-release" in S1_EC111_REJECTION_RULES,
        ),
        (
            S1_EC111_CHECK_NAMES[3],
            len(S1_EC111_EXPLICIT_RELEASE_REQUIREMENTS) == 9,
        ),
        (
            S1_EC111_CHECK_NAMES[4],
            set(S1_EC110_EXTERNAL_RELEASE_SCHEMA).issubset(
                S1_EC111_BRIDGE_OUTPUT_SCHEMA
            ),
        ),
        (
            S1_EC111_CHECK_NAMES[5],
            S1_EC67_EC59_HANDOFF_DIGEST
            == "5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb",
        ),
        (
            S1_EC111_CHECK_NAMES[6],
            "maximum-3208-field-steps" in S1_EC111_EXPLICIT_RELEASE_REQUIREMENTS,
        ),
        (
            S1_EC111_CHECK_NAMES[7],
            "assistant-generated-release-text-fails-closed"
            in S1_EC111_REJECTION_RULES,
        ),
        (S1_EC111_CHECK_NAMES[8], True),
        (
            S1_EC111_CHECK_NAMES[9],
            "external_release" in factory_signature.parameters
            and called.isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "contract_id": S1_EC111_CONTRACT_ID,
        "message_classes": S1_EC111_MESSAGE_CLASSES,
        "continuation_examples": S1_EC111_CONTINUATION_EXAMPLES,
        "explicit_release_requirements": S1_EC111_EXPLICIT_RELEASE_REQUIREMENTS,
        "rejection_rules": S1_EC111_REJECTION_RULES,
        "bridge_output_schema": S1_EC111_BRIDGE_OUTPUT_SCHEMA,
        "checks": checks,
        "current_message_class": "continuation-only",
        "current_message_authorizes_real_run": False,
        "continuation_work_permitted": True,
        "owner_release_must_originate_outside_research_module": True,
        "bridge_may_interpret_ambiguous_text_as_release": False,
        "bridge_may_reuse_prior_release": False,
        "bridge_may_generate_release_text": False,
        "external_release_bridge_implemented": False,
        "owner_scope_token_creation_permitted": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "real_result_ingress_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "CONTINUATION_BOUND_RELEASE_BRIDGE_SPECIFIED_NOT_IMPLEMENTED",
        "reason": (
            "the current message is continuation-only; a separate explicit "
            "owner message must name the EC67 r2 run, one-shot limit, 3208-step "
            "budget, nonpersistence, and no-retry boundary before any bridge output"
        ),
    }
    return E1CommonProbeEC111ExternalOwnerReleaseBridgeContract(
        **values, contract_digest=_digest(values)
    )
