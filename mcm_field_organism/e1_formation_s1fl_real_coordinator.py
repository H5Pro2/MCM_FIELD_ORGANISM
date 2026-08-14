"""S1-FL real coordinator implementation with a counting-only test entry."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .e1_confirmation_small_five_arm_formation import (
    E1SmallFiveArmFormationResult,
    run_small_five_arm_formation_in_memory,
)
from .e1_formation_s1fd_state_convergence_evaluator import (
    E1FormationS1FDStateConvergenceResult,
    evaluate_e1_formation_s1fd_state_convergence,
)
from .e1_formation_s1ff_in_memory_capture_adapter import (
    E1FormationS1FFCaptureResult,
    capture_e1_formation_s1ff_in_memory,
)
from .e1_formation_s1fh_fresh_capture_one_shot_contract import (
    E1FormationS1FHFreshCaptureOneShotContract,
)
from .e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIFreshCapturePreflight,
    E1FormationS1FIPreparedInputs,
    E1FormationS1FIResourceSnapshot,
    preflight_e1_formation_s1fi_fresh_capture,
    read_e1_formation_s1fi_resource_snapshot,
)
from .e1_formation_s1fk_real_coordinator_contract import (
    E1FormationS1FKOwnerAuthorizationToken,
    E1FormationS1FKRealCoordinatorContract,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FLRealCoordinatorError(RuntimeError):
    """Raised when S1-FL cannot return one complete atomic result."""


S1_FL_COORDINATOR_ID = "e1.formation-capture-real-coordinator.s1fl.v1"
S1_FL_EXECUTION_MODES = ("counting-test", "real")


ResourceReader = Callable[[], E1FormationS1FIResourceSnapshot]
FiveArmRunner = Callable[..., E1SmallFiveArmFormationResult]


@dataclass(frozen=True, slots=True)
class E1FormationS1FLCoordinatorResult:
    coordinator_id: str
    execution_mode: str
    source_s1fk_contract_digest: str
    source_s1fh_contract_digest: str
    source_preflight_digest: str
    immediate_preflight_digest: str
    authorization_digest: str
    refinement_result_digests: tuple[tuple[str, str], ...]
    capture: E1FormationS1FFCaptureResult = field(repr=False)
    evaluation: E1FormationS1FDStateConvergenceResult = field(repr=False)
    formation_runner_call_count: int
    formation_result_count: int
    captured_state_count: int
    planned_field_steps: int
    field_steps_executed: int
    authorization_consumed: bool
    immediate_preflight_passed: bool
    atomic_result_complete: bool
    probe_execution_performed: bool
    persistence_performed: bool
    automatic_retry_performed: bool
    posthoc_parameter_change_performed: bool
    memory_claim_allowed: bool
    decision: str
    reason: str
    result_digest: str

    def __post_init__(self) -> None:
        expected_steps = 0 if self.execution_mode == "counting-test" else 14_000
        expected_decision = (
            "COUNTING_ADAPTER_COORDINATION_CONFIRMED_REAL_EXECUTION_CLOSED"
            if self.execution_mode == "counting-test"
            else "REAL_FORMATION_CAPTURE_COMPLETED_DIAGNOSTIC_ONLY"
        )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"capture", "evaluation", "result_digest"}
        }
        payload["capture_digest"] = self.capture.capture_digest
        payload["evaluation_digest"] = self.evaluation.result_digest
        if (
            self.coordinator_id != S1_FL_COORDINATOR_ID
            or self.execution_mode not in S1_FL_EXECUTION_MODES
            or any(
                not isinstance(value, str)
                or len(value) != 64
                or any(char not in "0123456789abcdef" for char in value)
                for value in (
                    self.source_s1fk_contract_digest,
                    self.source_s1fh_contract_digest,
                    self.source_preflight_digest,
                    self.immediate_preflight_digest,
                    self.authorization_digest,
                )
            )
            or tuple(role for role, _ in self.refinement_result_digests)
            != ("r2", "r4", "r8")
            or any(
                len(value) != 64
                for _, value in self.refinement_result_digests
            )
            or not isinstance(self.capture, E1FormationS1FFCaptureResult)
            or not isinstance(self.evaluation, E1FormationS1FDStateConvergenceResult)
            or self.formation_runner_call_count != 3
            or self.formation_result_count != 15
            or self.captured_state_count != 15
            or self.planned_field_steps != 14_000
            or self.field_steps_executed != expected_steps
            or self.authorization_consumed is not True
            or self.immediate_preflight_passed is not True
            or self.atomic_result_complete is not True
            or any(
                value is not False
                for value in (
                    self.probe_execution_performed,
                    self.persistence_performed,
                    self.automatic_retry_performed,
                    self.posthoc_parameter_change_performed,
                    self.memory_claim_allowed,
                )
            )
            or self.decision != expected_decision
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1FLRealCoordinatorError(
                "S1-FL coordinator result changed or is incomplete"
            )


def _coordinate_e1_formation_s1fl(
    contract: E1FormationS1FKRealCoordinatorContract,
    one_shot: E1FormationS1FHFreshCaptureOneShotContract,
    source_preflight: E1FormationS1FIFreshCapturePreflight,
    inputs: E1FormationS1FIPreparedInputs,
    authorization_text: str,
    resource_reader: ResourceReader,
    formation_runner: FiveArmRunner,
    *,
    execution_mode: str,
) -> E1FormationS1FLCoordinatorResult:
    if execution_mode not in S1_FL_EXECUTION_MODES:
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL execution mode is invalid"
        )
    if not isinstance(contract, E1FormationS1FKRealCoordinatorContract):
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL requires the typed S1-FK contract"
        )
    if not isinstance(one_shot, E1FormationS1FHFreshCaptureOneShotContract):
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL requires the typed S1-FH contract"
        )
    if not isinstance(source_preflight, E1FormationS1FIFreshCapturePreflight):
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL requires the typed source preflight"
        )
    if not isinstance(inputs, E1FormationS1FIPreparedInputs):
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL requires typed formation-only inputs"
        )
    if not callable(resource_reader) or not callable(formation_runner):
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL requires callable resource and formation adapters"
        )
    contract.__post_init__()
    one_shot.__post_init__()
    source_preflight.__post_init__()
    inputs.__post_init__()
    if (
        contract.source_s1fh_contract_digest != one_shot.contract_digest
        or source_preflight.source_s1fh_contract_digest != one_shot.contract_digest
        or source_preflight.input_manifest_digest != inputs.input_manifest_digest
        or source_preflight.technical_preflight_passed is not True
        or source_preflight.execution_permitted is not False
        or contract.execution_permitted is not False
    ):
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL source contract or preflight binding changed"
        )
    if execution_mode == "real" and (
        resource_reader is not read_e1_formation_s1fi_resource_snapshot
        or formation_runner is not run_small_five_arm_formation_in_memory
    ):
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL real mode requires the exact bound production adapters"
        )

    resources = resource_reader()
    if not isinstance(resources, E1FormationS1FIResourceSnapshot):
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL resource adapter returned no typed snapshot"
        )
    immediate = preflight_e1_formation_s1fi_fresh_capture(
        one_shot, inputs, resources
    )
    if immediate.technical_preflight_passed is not True:
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL immediate preflight failed before the first arm"
        )
    token = E1FormationS1FKOwnerAuthorizationToken(
        authorization_text,
        contract.contract_digest,
        immediate,
    )
    token.consume()

    refinements = []
    for ab_plan, ba_plan in zip(
        inputs.history_ab_plans.plans,
        inputs.history_ba_plans.plans,
        strict=True,
    ):
        result = formation_runner(
            ab_plan.refinement_id,
            inputs.av_permutation.history_ab,
            inputs.av_permutation.history_ba,
            ab_plan.proposal_steps,
            ba_plan.proposal_steps,
            inputs.initial_field,
            inputs.initial_state,
        )
        if not isinstance(result, E1SmallFiveArmFormationResult):
            raise E1FormationS1FLRealCoordinatorError(
                "S1-FL formation adapter returned no typed five-arm result"
            )
        result.__post_init__()
        if result.refinement_id != ab_plan.refinement_id:
            raise E1FormationS1FLRealCoordinatorError(
                "S1-FL formation adapter changed refinement order"
            )
        refinements.append(result)
    formed = tuple(refinements)
    if tuple(item.refinement_id for item in formed) != ("r2", "r4", "r8"):
        raise E1FormationS1FLRealCoordinatorError(
            "S1-FL did not receive all three formation refinements"
        )
    arm_results = tuple(arm for item in formed for arm in item.arms)
    capture = capture_e1_formation_s1ff_in_memory(arm_results)
    evaluation = evaluate_e1_formation_s1fd_state_convergence(
        capture.state_vectors
    )
    values = {
        "coordinator_id": S1_FL_COORDINATOR_ID,
        "execution_mode": execution_mode,
        "source_s1fk_contract_digest": contract.contract_digest,
        "source_s1fh_contract_digest": one_shot.contract_digest,
        "source_preflight_digest": source_preflight.preflight_digest,
        "immediate_preflight_digest": immediate.preflight_digest,
        "authorization_digest": token.authorization_digest,
        "refinement_result_digests": tuple(
            (item.refinement_id, item.result_digest) for item in formed
        ),
        "capture": capture,
        "evaluation": evaluation,
        "formation_runner_call_count": 3,
        "formation_result_count": len(arm_results),
        "captured_state_count": len(capture.state_vectors),
        "planned_field_steps": 14_000,
        "field_steps_executed": 0 if execution_mode == "counting-test" else 14_000,
        "authorization_consumed": token.consumed,
        "immediate_preflight_passed": immediate.technical_preflight_passed,
        "atomic_result_complete": True,
        "probe_execution_performed": False,
        "persistence_performed": False,
        "automatic_retry_performed": False,
        "posthoc_parameter_change_performed": False,
        "memory_claim_allowed": False,
        "decision": (
            "COUNTING_ADAPTER_COORDINATION_CONFIRMED_REAL_EXECUTION_CLOSED"
            if execution_mode == "counting-test"
            else "REAL_FORMATION_CAPTURE_COMPLETED_DIAGNOSTIC_ONLY"
        ),
        "reason": (
            "three-counting-adapter-calls-captured-and-evaluated-with-zero-field-steps"
            if execution_mode == "counting-test"
            else "one-authorized-real-formation-capture-completed-without-probe-or-persistence"
        ),
    }
    digest_payload = {
        name: value
        for name, value in values.items()
        if name not in {"capture", "evaluation"}
    }
    digest_payload["capture_digest"] = capture.capture_digest
    digest_payload["evaluation_digest"] = evaluation.result_digest
    return E1FormationS1FLCoordinatorResult(
        **values,
        result_digest=_digest(digest_payload),
    )


def coordinate_e1_formation_s1fl_with_counting_adapters(
    contract: E1FormationS1FKRealCoordinatorContract,
    one_shot: E1FormationS1FHFreshCaptureOneShotContract,
    source_preflight: E1FormationS1FIFreshCapturePreflight,
    inputs: E1FormationS1FIPreparedInputs,
    authorization_text: str,
    resource_reader: ResourceReader,
    formation_runner: FiveArmRunner,
) -> E1FormationS1FLCoordinatorResult:
    """Exercise coordination with explicit zero-field-step test adapters."""

    return _coordinate_e1_formation_s1fl(
        contract,
        one_shot,
        source_preflight,
        inputs,
        authorization_text,
        resource_reader,
        formation_runner,
        execution_mode="counting-test",
    )


def run_e1_formation_s1fl_once(
    contract: E1FormationS1FKRealCoordinatorContract,
    one_shot: E1FormationS1FHFreshCaptureOneShotContract,
    source_preflight: E1FormationS1FIFreshCapturePreflight,
    inputs: E1FormationS1FIPreparedInputs,
    authorization_text: str,
) -> E1FormationS1FLCoordinatorResult:
    """Run the bound real path only with exact production adapters."""

    return _coordinate_e1_formation_s1fl(
        contract,
        one_shot,
        source_preflight,
        inputs,
        authorization_text,
        read_e1_formation_s1fi_resource_snapshot,
        run_small_five_arm_formation_in_memory,
        execution_mode="real",
    )
