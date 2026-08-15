"""S1-GS closed contract for one future real carrier-batch gate."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1gp_real_carrier_exchange_contract import (
    E1FormationS1GPRealCarrierExchangeContract,
    audit_e1_formation_s1gp_real_carrier_exchange_contract,
)
from .e1_formation_s1gq_carrier_transition_schema import (
    S1_GQ_TRANSITION_KINDS,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GSRealSingleBatchGateContractError(ValueError):
    """Raised when the closed one-batch gate is widened or authorized."""


S1_GS_GATE_ID = "e1.real-single-carrier-batch-gate.s1gs.v1"
S1_GS_SCOPE = (
    "one-exact-fresh-binding",
    "one-exact-next-proposal-batch",
    "one-exact-current-live-field-carrier",
    "one-real-field-advance",
    "one-real-transition-envelope",
)
S1_GS_AUTHORIZATION_REQUIREMENTS = (
    "external-owner-authorization-must-be-explicit-and-new",
    "authorization-must-name-s1gs-successor-run",
    "authorization-must-limit-adapter-calls-to-one",
    "authorization-must-limit-field-steps-to-one",
    "authorization-must-prohibit-retry-and-reparametrization",
    "authorization-must-expire-after-success-or-failure",
)
S1_GS_GATE_SEQUENCE = (
    "validate-static-s1gp-exchange-contract",
    "validate-exact-fresh-batch-carrier-route",
    "validate-external-authorization-before-token-creation",
    "create-one-process-local-single-use-token",
    "revalidate-route-and-one-step-budget",
    "consume-token-immediately-before-first-adapter-call",
    "permit-exactly-one-adapter-call",
    "require-one-real-transition-envelope-or-fail-closed",
    "return-no-partial-result-on-any-failure",
    "retire-token-after-success-or-failure",
)
S1_GS_ABORT_CONDITIONS = (
    "authorization-missing-ambiguous-stale-or-scope-mismatched",
    "token-missing-already-consumed-copied-or-expired",
    "fresh-binding-batch-carrier-or-digest-mismatch",
    "batch-is-not-the-exact-next-bound-batch",
    "requested-adapter-call-count-is-not-one",
    "requested-field-step-budget-is-not-one",
    "adapter-raises-or-returns-no-new-shared-field",
    "real-transition-envelope-is-missing-or-inconsistent",
    "source-state-or-fixed-adapter-attestation-changes",
    "persistence-retry-reparametrization-or-claim-requested",
)
S1_GS_CHECK_NAMES = (
    "source-s1gp-contract-is-closed-and-type-complete",
    "real-envelope-kind-is-exactly-bound",
    "scope-is-one-binding-one-batch-one-step",
    "authorization-precedes-token-and-adapter",
    "single-use-token-consumption-precedes-only-adapter-call",
    "success-and-failure-both-retire-token",
    "all-invalid-paths-return-no-partial-result",
    "contract-calls-no-adapter-kernel-token-factory-or-writer",
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
class E1FormationS1GSRealSingleBatchGateContract:
    gate_id: str
    source_s1gp_contract_digest: str
    scope: tuple[str, ...]
    authorization_requirements: tuple[str, ...]
    gate_sequence: tuple[str, ...]
    abort_conditions: tuple[str, ...]
    required_transition_kind: str
    maximum_adapter_calls: int
    maximum_field_steps: int
    checks: tuple[tuple[str, bool], ...]
    external_owner_authorization_required: bool
    authorization_present: bool
    process_local_single_use_token_required: bool
    authorization_token_implemented: bool
    token_creation_permitted: bool
    real_transition_builder_implemented: bool
    real_adapter_implemented: bool
    execution_permitted: bool
    retry_permitted: bool
    reparametrization_permitted: bool
    partial_return_permitted: bool
    persistence_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    gate_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "gate_digest"
        }
        if (
            self.gate_id != S1_GS_GATE_ID
            or len(self.source_s1gp_contract_digest) != 64
            or self.scope != S1_GS_SCOPE
            or self.authorization_requirements
            != S1_GS_AUTHORIZATION_REQUIREMENTS
            or self.gate_sequence != S1_GS_GATE_SEQUENCE
            or self.abort_conditions != S1_GS_ABORT_CONDITIONS
            or self.required_transition_kind != "real-field-advance"
            or self.maximum_adapter_calls != 1
            or self.maximum_field_steps != 1
            or tuple(name for name, _ in self.checks) != S1_GS_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.external_owner_authorization_required,
                    self.process_local_single_use_token_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.authorization_present,
                    self.authorization_token_implemented,
                    self.token_creation_permitted,
                    self.real_transition_builder_implemented,
                    self.real_adapter_implemented,
                    self.execution_permitted,
                    self.retry_permitted,
                    self.reparametrization_permitted,
                    self.partial_return_permitted,
                    self.persistence_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "REAL_SINGLE_BATCH_GATE_BOUND_AUTHORIZATION_AND_TOKEN_ABSENT"
            or not self.reason
            or self.gate_digest != _digest(payload)
        ):
            raise E1FormationS1GSRealSingleBatchGateContractError(
                "S1-GS gate widened, authorized itself, or opened execution"
            )


def build_e1_formation_s1gs_real_single_batch_gate_contract(
) -> E1FormationS1GSRealSingleBatchGateContract:
    """Build the closed gate contract without creating an authorization token."""

    source_contract = audit_e1_formation_s1gp_real_carrier_exchange_contract()
    if not isinstance(source_contract, E1FormationS1GPRealCarrierExchangeContract):
        raise E1FormationS1GSRealSingleBatchGateContractError(
            "S1-GS requires the exact S1-GP exchange contract"
        )
    source_contract.__post_init__()
    builder_source = inspect.getsource(
        build_e1_formation_s1gs_real_single_batch_gate_contract
    )
    forbidden_calls = {
        "map_proposal_batch_to_transient_docks",
        "project_transient_docks_to_neuron_inputs",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "create_authorization_token",
        "consume",
        "open",
        "write_text",
        "write_bytes",
    }
    checks = (
        (
            S1_GS_CHECK_NAMES[0],
            source_contract.execution_permitted is False
            and source_contract.real_adapter_implementation_permitted is False
            and source_contract.separate_real_transition_type_required is True,
        ),
        (
            S1_GS_CHECK_NAMES[1],
            S1_GQ_TRANSITION_KINDS == (
                "synthetic-no-field-advance",
                "real-field-advance",
            ),
        ),
        (
            S1_GS_CHECK_NAMES[2],
            S1_GS_SCOPE
            == (
                "one-exact-fresh-binding",
                "one-exact-next-proposal-batch",
                "one-exact-current-live-field-carrier",
                "one-real-field-advance",
                "one-real-transition-envelope",
            ),
        ),
        (
            S1_GS_CHECK_NAMES[3],
            S1_GS_GATE_SEQUENCE.index(
                "validate-external-authorization-before-token-creation"
            )
            < S1_GS_GATE_SEQUENCE.index(
                "create-one-process-local-single-use-token"
            ),
        ),
        (
            S1_GS_CHECK_NAMES[4],
            S1_GS_GATE_SEQUENCE.index(
                "consume-token-immediately-before-first-adapter-call"
            )
            < S1_GS_GATE_SEQUENCE.index("permit-exactly-one-adapter-call"),
        ),
        (
            S1_GS_CHECK_NAMES[5],
            "retire-token-after-success-or-failure" in S1_GS_GATE_SEQUENCE,
        ),
        (
            S1_GS_CHECK_NAMES[6],
            "return-no-partial-result-on-any-failure" in S1_GS_GATE_SEQUENCE
            and "persistence-retry-reparametrization-or-claim-requested"
            in S1_GS_ABORT_CONDITIONS,
        ),
        (
            S1_GS_CHECK_NAMES[7],
            _called_names(builder_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "gate_id": S1_GS_GATE_ID,
        "source_s1gp_contract_digest": source_contract.contract_digest,
        "scope": S1_GS_SCOPE,
        "authorization_requirements": S1_GS_AUTHORIZATION_REQUIREMENTS,
        "gate_sequence": S1_GS_GATE_SEQUENCE,
        "abort_conditions": S1_GS_ABORT_CONDITIONS,
        "required_transition_kind": "real-field-advance",
        "maximum_adapter_calls": 1,
        "maximum_field_steps": 1,
        "checks": checks,
        "external_owner_authorization_required": True,
        "authorization_present": False,
        "process_local_single_use_token_required": True,
        "authorization_token_implemented": False,
        "token_creation_permitted": False,
        "real_transition_builder_implemented": False,
        "real_adapter_implemented": False,
        "execution_permitted": False,
        "retry_permitted": False,
        "reparametrization_permitted": False,
        "partial_return_permitted": False,
        "persistence_permitted": False,
        "claims_permitted": False,
        "decision": (
            "REAL_SINGLE_BATCH_GATE_BOUND_AUTHORIZATION_AND_TOKEN_ABSENT"
        ),
        "reason": (
            "one-future-real-carrier-batch-is-statically-limited-to-one-"
            "adapter-call-and-one-field-step;external-owner-authorization-"
            "and-single-use-token-are-required-but-absent;execution-remains-"
            "fail-closed"
        ),
    }
    return E1FormationS1GSRealSingleBatchGateContract(
        **values,
        gate_digest=_digest(values),
    )
