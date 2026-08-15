"""S1-GZ closed implementation plan for the five missing real-path parts."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1gy_single_batch_total_preflight import (
    E1FormationS1GYSingleBatchTotalPreflight,
    S1_GY_IMPLEMENTATION_BLOCKERS,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GZRealPathImplementationPlanError(ValueError):
    """Raised when the plan widens scope or pretends readiness."""


S1_GZ_PLAN_ID = "e1.real-single-batch-implementation-plan.s1gz.v1"
S1_GZ_IMPLEMENTATION_SEQUENCE = (
    "pure-real-transition-builder",
    "external-owner-authorization-origin-bridge",
    "real-single-use-token-factory",
    "atomic-real-adapter-call-receipt-factory",
    "gated-real-single-batch-adapter",
)
S1_GZ_RUNTIME_SEQUENCE = (
    "accept-externally-originated-owner-authorization",
    "validate-authorization-against-exact-s1gy-target",
    "create-one-process-local-real-single-use-token",
    "revalidate-gate-target-route-and-one-step-budget",
    "consume-token-immediately-before-adapter-call",
    "perform-exactly-one-adapter-call-and-one-field-step",
    "create-authentic-receipt-inside-the-same-adapter-boundary",
    "build-pure-real-transition-from-receipt-and-new-field",
    "validate-shared-real-transition-envelope",
    "return-one-complete-transition-or-no-result",
    "retire-authorization-and-token-after-success-or-failure",
)
S1_GZ_COMPONENT_CONTRACTS = (
    (
        "pure-real-transition-builder",
        "construct-transition-only-from-validated-route-new-field-and-receipt",
        "must-not-call-adapter-create-token-or-authenticate-owner",
    ),
    (
        "external-owner-authorization-origin-bridge",
        "validate-external-origin-and-bind-owner-message-to-exact-target",
        "must-not-invent-authorization-create-token-or-call-adapter",
    ),
    (
        "real-single-use-token-factory",
        "issue-one-process-local-noncopyable-token-after-valid-authorization",
        "must-not-interpret-messages-call-adapter-or-survive-attempt-end",
    ),
    (
        "atomic-real-adapter-call-receipt-factory",
        "seal-one-consumed-token-and-one-authentic-kernel-result-as-receipt",
        "must-not-be-publicly-callable-or-fabricate-kernel-execution",
    ),
    (
        "gated-real-single-batch-adapter",
        "own-token-consumption-kernel-call-receipt-sealing-and-fail-closed-return",
        "must-not-retry-reparametrize-persist-or-return-partial-results",
    ),
)
S1_GZ_ATOMIC_OWNERSHIP_BOUNDARIES = (
    "origin-bridge-alone-validates-external-owner-origin",
    "token-factory-alone-creates-one-token-after-valid-authorization",
    "adapter-boundary-alone-consumes-token-calls-kernel-and-seals-receipt",
    "transition-builder-never-owns-authorization-token-or-kernel-access",
    "any-failure-retires-attempt-and-returns-no-partial-result",
)
S1_GZ_CHECK_NAMES = (
    "source-s1gy-static-preflight-passes-but-is-not-ready",
    "five-source-blockers-remain-explicit",
    "implementation-sequence-covers-five-components-once",
    "pure-builder-is-implemented-before-effectful-integration",
    "origin-validation-precedes-real-token-creation",
    "token-consumption-immediately-precedes-only-adapter-call",
    "receipt-is-sealed-inside-adapter-boundary-after-kernel-result",
    "pure-transition-build-follows-authentic-receipt",
    "failure-path-retires-attempt-and-returns-no-partial-result",
    "plan-calls-no-authorization-token-adapter-kernel-transition-or-writer",
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
class E1FormationS1GZRealPathImplementationPlan:
    plan_id: str
    source_s1gy_preflight_digest: str
    target_digest: str
    implementation_blockers: tuple[str, ...]
    implementation_sequence: tuple[str, ...]
    runtime_sequence: tuple[str, ...]
    component_contracts: tuple[tuple[str, str, str], ...]
    atomic_ownership_boundaries: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    maximum_adapter_calls: int
    maximum_field_steps: int
    implementation_started: bool
    implementation_ready: bool
    authorization_request_ready: bool
    authorization_present: bool
    token_created: bool
    receipt_created: bool
    transition_created: bool
    adapter_calls: int
    field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    plan_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "plan_digest"
        }
        if (
            self.plan_id != S1_GZ_PLAN_ID
            or len(self.source_s1gy_preflight_digest) != 64
            or len(self.target_digest) != 64
            or self.implementation_blockers != S1_GY_IMPLEMENTATION_BLOCKERS
            or self.implementation_sequence != S1_GZ_IMPLEMENTATION_SEQUENCE
            or self.runtime_sequence != S1_GZ_RUNTIME_SEQUENCE
            or self.component_contracts != S1_GZ_COMPONENT_CONTRACTS
            or self.atomic_ownership_boundaries
            != S1_GZ_ATOMIC_OWNERSHIP_BOUNDARIES
            or tuple(name for name, _ in self.checks) != S1_GZ_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.maximum_adapter_calls != 1
            or self.maximum_field_steps != 1
            or any(
                value is not False
                for value in (
                    self.implementation_started,
                    self.implementation_ready,
                    self.authorization_request_ready,
                    self.authorization_present,
                    self.token_created,
                    self.receipt_created,
                    self.transition_created,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.adapter_calls != 0
            or self.field_steps_executed != 0
            or self.decision
            != "FIVE_COMPONENT_IMPLEMENTATION_ORDER_BOUND_EXECUTION_CLOSED"
            or not self.reason
            or self.plan_digest != _digest(payload)
        ):
            raise E1FormationS1GZRealPathImplementationPlanError(
                "S1-GZ plan widened scope, hid a dependency, or opened execution"
            )


def build_e1_formation_s1gz_real_path_implementation_plan(
    preflight: E1FormationS1GYSingleBatchTotalPreflight,
) -> E1FormationS1GZRealPathImplementationPlan:
    """Bind implementation and runtime order without implementing either."""

    if not isinstance(preflight, E1FormationS1GYSingleBatchTotalPreflight):
        raise E1FormationS1GZRealPathImplementationPlanError(
            "S1-GZ requires the exact S1-GY preflight"
        )
    preflight.__post_init__()
    builder_source = inspect.getsource(
        build_e1_formation_s1gz_real_path_implementation_plan
    )
    forbidden_calls = {
        "E1FormationS1GWExternalOwnerAuthorization",
        "issue_e1_formation_s1gt_synthetic_single_use_token",
        "E1FormationS1GVRealAdapterCallReceipt",
        "bind_e1_formation_s1gq_carrier_transition_envelope",
        "map_proposal_batch_to_transient_docks",
        "project_transient_docks_to_neuron_inputs",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "consume",
        "open",
        "write_text",
        "write_bytes",
    }
    runtime = S1_GZ_RUNTIME_SEQUENCE
    checks = (
        (
            S1_GZ_CHECK_NAMES[0],
            preflight.static_contracts_complete is True
            and preflight.implementation_ready is False
            and preflight.authorization_request_ready is False,
        ),
        (
            S1_GZ_CHECK_NAMES[1],
            preflight.implementation_blockers == S1_GY_IMPLEMENTATION_BLOCKERS
            and len(preflight.implementation_blockers) == 5,
        ),
        (
            S1_GZ_CHECK_NAMES[2],
            len(S1_GZ_IMPLEMENTATION_SEQUENCE) == 5
            and len(set(S1_GZ_IMPLEMENTATION_SEQUENCE)) == 5
            and set(S1_GZ_IMPLEMENTATION_SEQUENCE)
            == {
                "pure-real-transition-builder",
                "external-owner-authorization-origin-bridge",
                "real-single-use-token-factory",
                "atomic-real-adapter-call-receipt-factory",
                "gated-real-single-batch-adapter",
            },
        ),
        (
            S1_GZ_CHECK_NAMES[3],
            S1_GZ_IMPLEMENTATION_SEQUENCE[0] == "pure-real-transition-builder",
        ),
        (
            S1_GZ_CHECK_NAMES[4],
            runtime.index("validate-authorization-against-exact-s1gy-target")
            < runtime.index("create-one-process-local-real-single-use-token"),
        ),
        (
            S1_GZ_CHECK_NAMES[5],
            runtime.index("consume-token-immediately-before-adapter-call") + 1
            == runtime.index(
                "perform-exactly-one-adapter-call-and-one-field-step"
            ),
        ),
        (
            S1_GZ_CHECK_NAMES[6],
            runtime.index(
                "perform-exactly-one-adapter-call-and-one-field-step"
            )
            < runtime.index(
                "create-authentic-receipt-inside-the-same-adapter-boundary"
            ),
        ),
        (
            S1_GZ_CHECK_NAMES[7],
            runtime.index(
                "create-authentic-receipt-inside-the-same-adapter-boundary"
            )
            < runtime.index(
                "build-pure-real-transition-from-receipt-and-new-field"
            ),
        ),
        (
            S1_GZ_CHECK_NAMES[8],
            runtime[-1]
            == "retire-authorization-and-token-after-success-or-failure"
            and "return-one-complete-transition-or-no-result" in runtime,
        ),
        (
            S1_GZ_CHECK_NAMES[9],
            _called_names(builder_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "plan_id": S1_GZ_PLAN_ID,
        "source_s1gy_preflight_digest": preflight.preflight_digest,
        "target_digest": preflight.target_digest,
        "implementation_blockers": S1_GY_IMPLEMENTATION_BLOCKERS,
        "implementation_sequence": S1_GZ_IMPLEMENTATION_SEQUENCE,
        "runtime_sequence": runtime,
        "component_contracts": S1_GZ_COMPONENT_CONTRACTS,
        "atomic_ownership_boundaries": S1_GZ_ATOMIC_OWNERSHIP_BOUNDARIES,
        "checks": checks,
        "maximum_adapter_calls": 1,
        "maximum_field_steps": 1,
        "implementation_started": False,
        "implementation_ready": False,
        "authorization_request_ready": False,
        "authorization_present": False,
        "token_created": False,
        "receipt_created": False,
        "transition_created": False,
        "adapter_calls": 0,
        "field_steps_executed": 0,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": "FIVE_COMPONENT_IMPLEMENTATION_ORDER_BOUND_EXECUTION_CLOSED",
        "reason": (
            "the-five-missing-components-now-have-separate-build-and-runtime-"
            "orders-with-authentication-token-and-adapter-ownership-boundaries;"
            "no-component-is-implemented-no-authorization-is-requested-and-no-"
            "real-path-action-occurs"
        ),
    }
    return E1FormationS1GZRealPathImplementationPlan(
        **values,
        plan_digest=_digest(values),
    )
