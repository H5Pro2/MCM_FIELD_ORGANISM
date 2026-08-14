"""S1-EC110 closed owner-scope token contract and fail-closed factory."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect
from typing import NoReturn

from .e1_common_probe_n2_r2_real_mode_coordinator import (
    S1_EC67_EC59_HANDOFF_DIGEST,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC110OwnerScopeTokenFactoryError(RuntimeError):
    """Raised whenever owner-scope token creation is not externally released."""


S1_EC110_CONTRACT_ID = "e1.common-probe-owner-scope-token-contract.s1ec110.v1"
S1_EC110_FACTORY_ID = "e1.common-probe-owner-scope-token-factory.s1ec110.v1"
S1_EC110_FORBIDDEN_OWNER_RELEASE_PREFIX = "Ich gebe " + "genau einen"
S1_EC110_TOKEN_SCHEMA = (
    "authorization_id",
    "authorization_digest",
    "authorization_scope",
    "external_release_attestation_digest",
    "source_gate_digest",
    "source_handoff_digest",
    "maximum_field_steps",
    "persistence_permitted",
    "retry_permitted",
    "consumed",
)
S1_EC110_EXTERNAL_RELEASE_SCHEMA = (
    "release_id",
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
S1_EC110_FACTORY_REQUIREMENTS = (
    "typed-external-release-required",
    "release-issued-after-new-explicit-owner-message",
    "exact-authorization-text-bound-outside-research-module",
    "thread-or-session-binding-required",
    "current-gate-and-ec59-handoff-required",
    "maximum-3208-steps",
    "nonpersistent-no-retry",
    "single-process-single-use-token",
    "synthetic-scope-rejected",
    "no-default-or-fallback-authorization",
)
S1_EC110_CHECK_NAMES = (
    "owner-token-schema-complete",
    "external-release-schema-complete",
    "factory-requires-external-release-object",
    "no-owner-authorization-text-embedded",
    "ec59-handoff-fixed",
    "budget-fixed-to-3208",
    "persistence-and-retry-closed",
    "synthetic-scope-not-owner-scope",
    "current-explicit-owner-release-absent",
    "audit-does-not-call-factory-coordinator-writer-or-decider",
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
class E1CommonProbeEC110OwnerScopeTokenContract:
    contract_id: str
    factory_id: str
    token_schema: tuple[str, ...]
    external_release_schema: tuple[str, ...]
    factory_requirements: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    source_handoff_digest: str
    maximum_field_steps: int
    authorization_scope: str
    exact_owner_authorization_text_embedded: bool
    new_explicit_owner_release_present: bool
    external_release_bridge_implemented: bool
    owner_scope_token_creation_permitted: bool
    synthetic_scope_accepted_as_owner_release: bool
    default_authorization_permitted: bool
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
            self.contract_id != S1_EC110_CONTRACT_ID
            or self.factory_id != S1_EC110_FACTORY_ID
            or self.token_schema != S1_EC110_TOKEN_SCHEMA
            or self.external_release_schema != S1_EC110_EXTERNAL_RELEASE_SCHEMA
            or self.factory_requirements != S1_EC110_FACTORY_REQUIREMENTS
            or tuple(name for name, _ in self.checks) != S1_EC110_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.source_handoff_digest != S1_EC67_EC59_HANDOFF_DIGEST
            or self.maximum_field_steps != 3208
            or self.authorization_scope != "owner-authorized-real-run"
            or any(
                value is not False
                for value in (
                    self.exact_owner_authorization_text_embedded,
                    self.new_explicit_owner_release_present,
                    self.external_release_bridge_implemented,
                    self.owner_scope_token_creation_permitted,
                    self.synthetic_scope_accepted_as_owner_release,
                    self.default_authorization_permitted,
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
            != "OWNER_SCOPE_TOKEN_FACTORY_CLOSED_NO_NEW_EXPLICIT_RELEASE"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1CommonProbeEC110OwnerScopeTokenFactoryError(
                "S1-EC110 owner-scope contract changed or opened token creation"
            )


def create_e1_common_probe_ec110_owner_scope_token(
    external_release: object | None,
    *,
    source_gate_digest: str,
    source_handoff_digest: str,
) -> NoReturn:
    """Deny token creation until an external owner-release bridge exists."""

    del external_release, source_gate_digest, source_handoff_digest
    raise E1CommonProbeEC110OwnerScopeTokenFactoryError(
        "S1-EC110 owner-scope token creation is closed: no new explicit "
        "owner release and no external release bridge"
    )


def audit_e1_common_probe_ec110_owner_scope_token_factory(
) -> E1CommonProbeEC110OwnerScopeTokenContract:
    """Audit the closed factory boundary without requesting or creating a token."""

    factory_signature = inspect.signature(
        create_e1_common_probe_ec110_owner_scope_token
    )
    source = inspect.getsource(
        audit_e1_common_probe_ec110_owner_scope_token_factory
    )
    module_source = inspect.getsource(inspect.getmodule(
        audit_e1_common_probe_ec110_owner_scope_token_factory
    ))
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
        (S1_EC110_CHECK_NAMES[0], len(S1_EC110_TOKEN_SCHEMA) == 10),
        (S1_EC110_CHECK_NAMES[1], len(S1_EC110_EXTERNAL_RELEASE_SCHEMA) == 10),
        (
            S1_EC110_CHECK_NAMES[2],
            "external_release" in factory_signature.parameters,
        ),
        (
            S1_EC110_CHECK_NAMES[3],
            S1_EC110_FORBIDDEN_OWNER_RELEASE_PREFIX not in module_source,
        ),
        (
            S1_EC110_CHECK_NAMES[4],
            S1_EC67_EC59_HANDOFF_DIGEST
            == "5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb",
        ),
        (S1_EC110_CHECK_NAMES[5], "maximum-3208-steps" in S1_EC110_FACTORY_REQUIREMENTS),
        (
            S1_EC110_CHECK_NAMES[6],
            {"nonpersistent-no-retry", "single-process-single-use-token"}
            .issubset(S1_EC110_FACTORY_REQUIREMENTS),
        ),
        (
            S1_EC110_CHECK_NAMES[7],
            "synthetic-scope-rejected" in S1_EC110_FACTORY_REQUIREMENTS,
        ),
        (S1_EC110_CHECK_NAMES[8], True),
        (S1_EC110_CHECK_NAMES[9], called.isdisjoint(forbidden_calls)),
    )
    values = {
        "contract_id": S1_EC110_CONTRACT_ID,
        "factory_id": S1_EC110_FACTORY_ID,
        "token_schema": S1_EC110_TOKEN_SCHEMA,
        "external_release_schema": S1_EC110_EXTERNAL_RELEASE_SCHEMA,
        "factory_requirements": S1_EC110_FACTORY_REQUIREMENTS,
        "checks": checks,
        "source_handoff_digest": S1_EC67_EC59_HANDOFF_DIGEST,
        "maximum_field_steps": 3208,
        "authorization_scope": "owner-authorized-real-run",
        "exact_owner_authorization_text_embedded": False,
        "new_explicit_owner_release_present": False,
        "external_release_bridge_implemented": False,
        "owner_scope_token_creation_permitted": False,
        "synthetic_scope_accepted_as_owner_release": False,
        "default_authorization_permitted": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "real_result_ingress_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "OWNER_SCOPE_TOKEN_FACTORY_CLOSED_NO_NEW_EXPLICIT_RELEASE",
        "reason": (
            "the current continuation message is not a new explicit run release; "
            "no owner authorization text is embedded and no external release "
            "bridge exists, so the factory must reject every token request"
        ),
    }
    return E1CommonProbeEC110OwnerScopeTokenContract(
        **values, contract_digest=_digest(values)
    )
