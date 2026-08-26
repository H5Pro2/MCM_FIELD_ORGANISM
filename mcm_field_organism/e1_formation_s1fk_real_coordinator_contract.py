"""S1-FK closed contract for a future real in-memory coordinator."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_confirmation_prepared_formation_consumer import (
    S1_EC7_FORMATION_ARMS,
    S1_EC7_REFINEMENTS,
)
from .e1_confirmation_small_five_arm_formation import (
    E1SmallFiveArmFormationResult,
    run_small_five_arm_formation_in_memory,
)
from .e1_formation_s1fd_state_convergence_evaluator import (
    evaluate_e1_formation_s1fd_state_convergence,
)
from .e1_formation_s1ff_in_memory_capture_adapter import (
    capture_e1_formation_s1ff_in_memory,
)
from .e1_formation_s1fh_fresh_capture_one_shot_contract import (
    E1FormationS1FHFreshCaptureOneShotContract,
)
from .e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIFreshCapturePreflight,
    read_e1_formation_s1fi_resource_snapshot,
)
from .e1_formation_s1fj_synthetic_coordinator import S1_FJ_COORDINATOR_ID
from .e1_refined_formation_runner import _digest


class E1FormationS1FKRealCoordinatorContractError(ValueError):
    """Raised when S1-FK changes or accepts invalid authorization."""


S1_FK_CONTRACT_ID = "e1.formation-capture-real-coordinator-contract.s1fk.v1"
S1_FK_REQUIRED_AUTHORIZATION_TEXT = (
    "Ich gebe genau einen nicht persistenten S1-FK Formation-Capture-Lauf "
    "mit maximal 14.000 Feldschritten frei. Kein Retry, keine "
    "Nachparametrierung und keine Probe. Die Ausfuehrung darf nur starten, "
    "wenn der S1-FI-Preflight unmittelbar vor dem ersten Formation-Arm "
    "erneut vollstaendig besteht."
)
S1_FK_COORDINATOR_SEQUENCE = (
    "validate-s1fh-contract-and-s1fi-preflight",
    "validate-formation-only-input-manifest",
    "read-immediate-memory-snapshot",
    "rerun-s1fi-preflight-with-immediate-snapshot",
    "validate-and-consume-owner-token-once",
    "run-r2-five-arm-formation",
    "run-r4-five-arm-formation",
    "run-r8-five-arm-formation",
    "flatten-fifteen-arm-results",
    "capture-with-s1ff",
    "evaluate-with-s1fd",
    "return-atomic-in-memory-result",
)
S1_FK_FAILURE_POLICY = (
    "fail-before-first-arm-if-immediate-preflight-or-token-fails;"
    "fail-without-result-on-any-later-error;no-retry"
)
S1_FK_CHECK_NAMES = (
    "s1fh-one-shot-scope-bound",
    "s1fj-dry-integration-bound",
    "five-arm-runner-signature-bound",
    "five-arm-result-schema-bound",
    "runner-delegates-exactly-five-arm-specification",
    "immediate-memory-reader-bound",
    "s1ff-capture-bound-after-fifteen-results",
    "s1fd-evaluation-bound-after-capture",
    "probe-and-persistence-absent-from-sequence",
    "audit-does-not-run-field-capture-evaluator-or-writer",
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


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


class E1FormationS1FKOwnerAuthorizationToken:
    """One-process token bound to one contract and one current preflight."""

    __slots__ = (
        "contract_digest",
        "preflight_digest",
        "authorization_digest",
        "_consumed",
    )

    def __init__(
        self,
        authorization_text: str,
        contract_digest: str,
        preflight: E1FormationS1FIFreshCapturePreflight,
    ) -> None:
        if authorization_text != S1_FK_REQUIRED_AUTHORIZATION_TEXT:
            raise E1FormationS1FKRealCoordinatorContractError(
                "S1-FK requires the exact explicit owner authorization"
            )
        if not isinstance(preflight, E1FormationS1FIFreshCapturePreflight):
            raise E1FormationS1FKRealCoordinatorContractError(
                "S1-FK token requires one typed current preflight"
            )
        preflight.__post_init__()
        if (
            not _valid_digest(contract_digest)
            or preflight.technical_preflight_passed is not True
            or preflight.execution_permitted is not False
            or preflight.owner_authorization_present is not False
        ):
            raise E1FormationS1FKRealCoordinatorContractError(
                "S1-FK token source is not technically ready and closed"
            )
        self.contract_digest = contract_digest
        self.preflight_digest = preflight.preflight_digest
        self.authorization_digest = _digest(authorization_text)
        self._consumed = False

    @property
    def consumed(self) -> bool:
        return self._consumed

    def consume(self) -> None:
        if self._consumed:
            raise E1FormationS1FKRealCoordinatorContractError(
                "S1-FK authorization token was already consumed; retry forbidden"
            )
        self._consumed = True


@dataclass(frozen=True, slots=True)
class E1FormationS1FKRealCoordinatorContract:
    contract_id: str
    source_s1fh_contract_digest: str
    source_s1fj_coordinator_id: str
    refinements: tuple[tuple[str, int], ...]
    formation_arm_ids: tuple[str, ...]
    five_arm_runner: str
    capture_adapter: str
    convergence_evaluator: str
    immediate_resource_reader: str
    maximum_formation_field_steps: int
    maximum_execution_count: int
    maximum_retry_count: int
    required_authorization_text_digest: str
    authorization_token_type: str
    coordinator_sequence: tuple[str, ...]
    failure_policy: str
    checks: tuple[tuple[str, bool], ...]
    immediate_preflight_required: bool
    authorization_consumed_before_first_arm_required: bool
    atomic_result_required: bool
    owner_authorization_present: bool
    coordinator_implementation_permitted: bool
    execution_permitted: bool
    probe_execution_permitted: bool
    persistence_permitted: bool
    automatic_retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    partial_result_return_permitted: bool
    memory_claim_permitted: bool
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
            self.contract_id != S1_FK_CONTRACT_ID
            or not _valid_digest(self.source_s1fh_contract_digest)
            or self.source_s1fj_coordinator_id != S1_FJ_COORDINATOR_ID
            or self.refinements != S1_EC7_REFINEMENTS
            or self.formation_arm_ids != S1_EC7_FORMATION_ARMS
            or self.five_arm_runner
            != "run_small_five_arm_formation_in_memory"
            or self.capture_adapter != "capture_e1_formation_s1ff_in_memory"
            or self.convergence_evaluator
            != "evaluate_e1_formation_s1fd_state_convergence"
            or self.immediate_resource_reader
            != "read_e1_formation_s1fi_resource_snapshot"
            or self.maximum_formation_field_steps != 14_000
            or (self.maximum_execution_count, self.maximum_retry_count) != (1, 0)
            or self.required_authorization_text_digest
            != _digest(S1_FK_REQUIRED_AUTHORIZATION_TEXT)
            or self.authorization_token_type
            != "E1FormationS1FKOwnerAuthorizationToken"
            or self.coordinator_sequence != S1_FK_COORDINATOR_SEQUENCE
            or self.failure_policy != S1_FK_FAILURE_POLICY
            or tuple(name for name, _ in self.checks) != S1_FK_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.immediate_preflight_required,
                    self.authorization_consumed_before_first_arm_required,
                    self.atomic_result_required,
                    self.coordinator_implementation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.probe_execution_permitted,
                    self.persistence_permitted,
                    self.automatic_retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.partial_result_return_permitted,
                    self.memory_claim_permitted,
                )
            )
            or self.decision
            != "REAL_COORDINATOR_CONTRACT_BOUND_AWAITING_IMPLEMENTATION_AND_OWNER_AUTHORIZATION"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1FKRealCoordinatorContractError(
                "S1-FK coordinator contract changed or opened execution"
            )


def audit_e1_formation_s1fk_real_coordinator_contract(
    one_shot: E1FormationS1FHFreshCaptureOneShotContract,
) -> E1FormationS1FKRealCoordinatorContract:
    """Bind callable interfaces without invoking the coordinator sequence."""

    if not isinstance(one_shot, E1FormationS1FHFreshCaptureOneShotContract):
        raise E1FormationS1FKRealCoordinatorContractError(
            "S1-FK requires the typed S1-FH contract"
        )
    one_shot.__post_init__()
    audit_source = inspect.getsource(
        audit_e1_formation_s1fk_real_coordinator_contract
    )
    runner_source = inspect.getsource(run_small_five_arm_formation_in_memory)
    runner_parameters = tuple(
        inspect.signature(run_small_five_arm_formation_in_memory).parameters
    )
    result_fields = tuple(E1SmallFiveArmFormationResult.__dataclass_fields__)
    forbidden_calls = {
        "run_small_five_arm_formation_in_memory",
        "run_prepared_real_formation_arm_in_memory",
        "read_e1_formation_s1fi_resource_snapshot",
        "capture_e1_formation_s1ff_in_memory",
        "evaluate_e1_formation_s1fd_state_convergence",
        "write_text",
        "write_bytes",
        "open",
    }
    checks = (
        (
            S1_FK_CHECK_NAMES[0],
            one_shot.formation_arm_count == 15
            and one_shot.maximum_formation_field_steps == 14_000,
        ),
        (S1_FK_CHECK_NAMES[1], bool(S1_FJ_COORDINATOR_ID)),
        (
            S1_FK_CHECK_NAMES[2],
            runner_parameters
            == (
                "refinement_id",
                "history_ab",
                "history_ba",
                "ab_proposal_steps",
                "ba_proposal_steps",
                "initial_field",
                "initial_state",
            ),
        ),
        (
            S1_FK_CHECK_NAMES[3],
            "arms" in result_fields and "result_digest" in result_fields,
        ),
        (
            S1_FK_CHECK_NAMES[4],
            "specs = (" in runner_source
            and "for arm_id, sequences, steps, formation_enabled in specs"
            in runner_source,
        ),
        (S1_FK_CHECK_NAMES[5], callable(read_e1_formation_s1fi_resource_snapshot)),
        (S1_FK_CHECK_NAMES[6], callable(capture_e1_formation_s1ff_in_memory)),
        (
            S1_FK_CHECK_NAMES[7],
            callable(evaluate_e1_formation_s1fd_state_convergence),
        ),
        (
            S1_FK_CHECK_NAMES[8],
            all(
                "probe" not in step and "persist" not in step
                for step in S1_FK_COORDINATOR_SEQUENCE
            ),
        ),
        (
            S1_FK_CHECK_NAMES[9],
            _called_names(audit_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "contract_id": S1_FK_CONTRACT_ID,
        "source_s1fh_contract_digest": one_shot.contract_digest,
        "source_s1fj_coordinator_id": S1_FJ_COORDINATOR_ID,
        "refinements": S1_EC7_REFINEMENTS,
        "formation_arm_ids": S1_EC7_FORMATION_ARMS,
        "five_arm_runner": "run_small_five_arm_formation_in_memory",
        "capture_adapter": "capture_e1_formation_s1ff_in_memory",
        "convergence_evaluator": (
            "evaluate_e1_formation_s1fd_state_convergence"
        ),
        "immediate_resource_reader": (
            "read_e1_formation_s1fi_resource_snapshot"
        ),
        "maximum_formation_field_steps": 14_000,
        "maximum_execution_count": 1,
        "maximum_retry_count": 0,
        "required_authorization_text_digest": _digest(
            S1_FK_REQUIRED_AUTHORIZATION_TEXT
        ),
        "authorization_token_type": "E1FormationS1FKOwnerAuthorizationToken",
        "coordinator_sequence": S1_FK_COORDINATOR_SEQUENCE,
        "failure_policy": S1_FK_FAILURE_POLICY,
        "checks": checks,
        "immediate_preflight_required": True,
        "authorization_consumed_before_first_arm_required": True,
        "atomic_result_required": True,
        "owner_authorization_present": False,
        "coordinator_implementation_permitted": True,
        "execution_permitted": False,
        "probe_execution_permitted": False,
        "persistence_permitted": False,
        "automatic_retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "partial_result_return_permitted": False,
        "memory_claim_permitted": False,
        "decision": (
            "REAL_COORDINATOR_CONTRACT_BOUND_AWAITING_IMPLEMENTATION_"
            "AND_OWNER_AUTHORIZATION"
        ),
        "reason": (
            "real-five-arm-runner-capture-and-evaluator-interfaces-bound;"
            "coordinator-not-implemented-and-owner-authorization-absent"
        ),
    }
    return E1FormationS1FKRealCoordinatorContract(
        **values,
        contract_digest=_digest(values),
    )
