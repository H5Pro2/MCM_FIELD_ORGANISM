"""Private S1-EC16 static contract for a future fully published formation run."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .e1_confirmation_full_formation_handoff import (
    S1_EC14_CONTRACT_DIGEST,
    S1_EC14_EDGE_BINDING_COUNT,
    S1_EC14_STATE_COUNT,
)
from .e1_confirmation_full_formation_handoff_publisher import (
    S1_EC15_FAILURE_POLICY,
    S1_EC15_POLICY_DIGEST,
)
from .e1_confirmation_full_formation_resource_preflight import (
    E1FullFormationResourcePreflight,
    S1_EC12_EXPECTED_REFINEMENTS,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullPublishedRunContractError(ValueError):
    """Raised when the S1-EC16 aggregate lifecycle is not fully bound."""


S1_EC16_EXECUTION_ID = "e1.full-formation-published-run.s1ec16.v1"
S1_EC16_REPORT = "e1_full_formation_published_s1ec16_once_v1.json"
S1_EC16_ATTEMPT = "e1_full_formation_published_s1ec16_once_v1.attempt.json"
S1_EC16_LOCK = "e1_full_formation_published_s1ec16_once_v1.lock"
S1_EC16_TRANSITIONS = (
    "verify-prepared-input-digests",
    "verify-s1ec12-before-lock",
    "bind-live-inputs-handoff-and-publisher",
    "create-exclusive-lock",
    "create-exclusive-attempt",
    "verify-s1ec12-inside-attempt",
    "execute-full-r2-r4-r8-five-arm-formation",
    "build-complete-s1ec14-payload-while-states-are-live",
    "write-fsync-reread-temporary-report",
    "exclusive-publish-and-reread-final-report",
    "typed-reload-all-fifteen-states",
    "remove-attempt-after-all-verifications",
    "release-lock",
)
S1_EC16_REQUIRED_GATES = (
    "descriptor-and-input-manifest-bound",
    "s1ec12-resource-gate-passed",
    "preflight-digest-stable-across-attempt",
    "fifteen-formation-arms-only",
    "all-five-arm-controls-pass",
    "prepared-inputs-preserved",
    "fifteen-complete-states-present",
    "two-thousand-one-hundred-seventy-five-bindings-present",
    "s1ec14-payload-digest-verified",
    "s1ec15-final-reread-verified",
    "typed-state-reload-verified",
    "attempt-retained-on-any-post-attempt-failure",
    "no-canonical-path",
    "no-probe",
    "no-claims",
)
S1_EC16_POLICY_DIGEST = _digest(
    {
        "execution_id": S1_EC16_EXECUTION_ID,
        "report_name": S1_EC16_REPORT,
        "attempt_name": S1_EC16_ATTEMPT,
        "lock_name": S1_EC16_LOCK,
        "failure_policy": S1_EC15_FAILURE_POLICY,
        "transitions": S1_EC16_TRANSITIONS,
        "required_gates": S1_EC16_REQUIRED_GATES,
        "refinements": S1_EC12_EXPECTED_REFINEMENTS,
        "handoff_contract_digest": S1_EC14_CONTRACT_DIGEST,
        "publisher_policy_digest": S1_EC15_POLICY_DIGEST,
        "state_count": S1_EC14_STATE_COUNT,
        "edge_binding_count": S1_EC14_EDGE_BINDING_COUNT,
        "execution_authorized": False,
        "canonical_execution_permitted": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }
)


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1FullFormationPublishedRunContract:
    execution_id: str
    policy_digest: str
    research_descriptor_digest: str
    input_manifest_digest: str
    resource_preflight_digest: str
    handoff_contract_digest: str
    publisher_policy_digest: str
    report_path: str
    attempt_path: str
    lock_path: str
    failure_policy: str
    transitions: tuple[str, ...]
    required_gates: tuple[str, ...]
    refinement_step_counts: tuple[tuple[str, int, int, int], ...]
    state_count: int
    edge_binding_count: int
    execution_authorized: bool
    canonical_execution_permitted: bool
    probe_execution_permitted: bool
    claims_permitted: bool

    def __post_init__(self) -> None:
        paths = tuple(
            Path(value)
            for value in (self.report_path, self.attempt_path, self.lock_path)
        )
        if (
            self.execution_id != S1_EC16_EXECUTION_ID
            or self.policy_digest != S1_EC16_POLICY_DIGEST
            or any(
                not _valid_digest(value)
                for value in (
                    self.research_descriptor_digest,
                    self.input_manifest_digest,
                    self.resource_preflight_digest,
                    self.handoff_contract_digest,
                    self.publisher_policy_digest,
                )
            )
            or self.handoff_contract_digest != S1_EC14_CONTRACT_DIGEST
            or self.publisher_policy_digest != S1_EC15_POLICY_DIGEST
            or len(set(paths)) != 3
            or len({path.parent for path in paths}) != 1
            or tuple(path.name for path in paths)
            != (S1_EC16_REPORT, S1_EC16_ATTEMPT, S1_EC16_LOCK)
            or any(path.exists() for path in paths)
            or self.failure_policy != S1_EC15_FAILURE_POLICY
            or self.transitions != S1_EC16_TRANSITIONS
            or self.required_gates != S1_EC16_REQUIRED_GATES
            or self.refinement_step_counts != S1_EC12_EXPECTED_REFINEMENTS
            or self.state_count != S1_EC14_STATE_COUNT
            or self.edge_binding_count != S1_EC14_EDGE_BINDING_COUNT
            or self.execution_authorized is not False
            or self.canonical_execution_permitted is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullPublishedRunContractError(
                "S1-EC16 aggregate run contract changed or paths are used"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_full_formation_published_run_contract(
    preflight: E1FullFormationResourcePreflight,
    directory: Path,
) -> E1FullFormationPublishedRunContract:
    """Bind a fresh aggregate identity without creating markers or executing."""

    if not isinstance(preflight, E1FullFormationResourcePreflight):
        raise E1ConfirmationFullPublishedRunContractError(
            "S1-EC16 requires one accepted S1-EC12 preflight"
        )
    preflight.__post_init__()
    if preflight.resource_gate_passed is not True:
        raise E1ConfirmationFullPublishedRunContractError(
            "S1-EC16 requires the passed S1-EC12 resource gate"
        )
    root = Path(directory).resolve()
    if not root.is_dir() or root == Path("reports").resolve():
        raise E1ConfirmationFullPublishedRunContractError(
            "S1-EC16 requires an existing temporary directory outside reports"
        )
    return E1FullFormationPublishedRunContract(
        execution_id=S1_EC16_EXECUTION_ID,
        policy_digest=S1_EC16_POLICY_DIGEST,
        research_descriptor_digest=preflight.research_descriptor_digest,
        input_manifest_digest=preflight.input_manifest_digest,
        resource_preflight_digest=preflight.result_digest,
        handoff_contract_digest=S1_EC14_CONTRACT_DIGEST,
        publisher_policy_digest=S1_EC15_POLICY_DIGEST,
        report_path=str(root / S1_EC16_REPORT),
        attempt_path=str(root / S1_EC16_ATTEMPT),
        lock_path=str(root / S1_EC16_LOCK),
        failure_policy=S1_EC15_FAILURE_POLICY,
        transitions=S1_EC16_TRANSITIONS,
        required_gates=S1_EC16_REQUIRED_GATES,
        refinement_step_counts=preflight.refinement_step_counts,
        state_count=S1_EC14_STATE_COUNT,
        edge_binding_count=S1_EC14_EDGE_BINDING_COUNT,
        execution_authorized=False,
        canonical_execution_permitted=False,
        probe_execution_permitted=False,
        claims_permitted=False,
    )


@dataclass(frozen=True, slots=True)
class E1FullFormationPublishedRunStaticAudit:
    contract_digest: str
    policy_digest: str
    resource_preflight_digest: str
    checks: tuple[tuple[str, bool], ...]
    transition_count: int
    required_gate_count: int
    ready_for_synthetic_composition: bool
    execution_authorized: bool
    field_execution_performed: bool
    markers_created: bool
    report_created: bool
    probe_execution_permitted: bool
    claims_permitted: bool
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            any(
                not _valid_digest(value)
                for value in (
                    self.contract_digest,
                    self.policy_digest,
                    self.resource_preflight_digest,
                    self.audit_digest,
                )
            )
            or self.policy_digest != S1_EC16_POLICY_DIGEST
            or tuple(name for name, _ in self.checks) != S1_EC16_REQUIRED_GATES
            or any(value is not True for _, value in self.checks)
            or self.transition_count != len(S1_EC16_TRANSITIONS)
            or self.required_gate_count != len(S1_EC16_REQUIRED_GATES)
            or self.ready_for_synthetic_composition is not True
            or self.execution_authorized is not False
            or self.field_execution_performed is not False
            or self.markers_created is not False
            or self.report_created is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullPublishedRunContractError(
                "S1-EC16 static audit changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1ConfirmationFullPublishedRunContractError(
                "S1-EC16 static audit digest changed"
            )


def audit_full_formation_published_run_contract(
    contract: E1FullFormationPublishedRunContract,
    preflight: E1FullFormationResourcePreflight,
) -> E1FullFormationPublishedRunStaticAudit:
    """Audit every aggregate binding without creating a runtime object."""

    if not isinstance(contract, E1FullFormationPublishedRunContract):
        raise E1ConfirmationFullPublishedRunContractError(
            "S1-EC16 audit requires one aggregate contract"
        )
    if not isinstance(preflight, E1FullFormationResourcePreflight):
        raise E1ConfirmationFullPublishedRunContractError(
            "S1-EC16 audit requires one resource preflight"
        )
    contract.__post_init__()
    preflight.__post_init__()
    bindings_hold = (
        contract.research_descriptor_digest == preflight.research_descriptor_digest
        and contract.input_manifest_digest == preflight.input_manifest_digest
        and preflight.resource_gate_passed
        and contract.resource_preflight_digest == preflight.result_digest
        and contract.state_count == S1_EC14_STATE_COUNT
        and contract.edge_binding_count == S1_EC14_EDGE_BINDING_COUNT
        and contract.handoff_contract_digest == S1_EC14_CONTRACT_DIGEST
        and contract.publisher_policy_digest == S1_EC15_POLICY_DIGEST
        and contract.failure_policy == S1_EC15_FAILURE_POLICY
        and not contract.canonical_execution_permitted
        and not contract.probe_execution_permitted
        and not contract.claims_permitted
    )
    checks = tuple(
        (gate, gate in contract.required_gates)
        for gate in S1_EC16_REQUIRED_GATES
    )
    if not bindings_hold or any(value is not True for _, value in checks):
        raise E1ConfirmationFullPublishedRunContractError(
            "S1-EC16 static aggregate gate failed"
        )
    payload = {
        "contract_digest": contract.digest(),
        "policy_digest": contract.policy_digest,
        "resource_preflight_digest": preflight.result_digest,
        "checks": checks,
        "transition_count": len(contract.transitions),
        "required_gate_count": len(contract.required_gates),
        "ready_for_synthetic_composition": True,
        "execution_authorized": False,
        "field_execution_performed": False,
        "markers_created": False,
        "report_created": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }
    return E1FullFormationPublishedRunStaticAudit(
        **payload,
        audit_digest=_digest(payload),
    )
