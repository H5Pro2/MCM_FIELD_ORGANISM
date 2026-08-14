"""Authorized one-shot S1-EC34 in-memory n1/n2 technical pilot."""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
import math
import time

from .e1_confirmation_prepared_real_formation_kernel import (
    run_prepared_real_formation_arm_in_memory,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest
from .e1_repetition_formation_planner import E1RepetitionFormationPlanSet
from .e1_repetition_pilot_post_adapter_preflight import (
    E1RepetitionPilotPostAdapterPreflight,
    S1_EC33_EC29_CONTRACT_DIGEST,
)
from .e1_repetition_pilot_release_contract import (
    E1RepetitionPilotReleaseContract,
    S1_EC29_ARMS,
    S1_EC29_FIELD_ARM_STEPS,
)
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1RepetitionPilotOnceRunnerError(ValueError):
    """Raised when S1-EC34 cannot remain one-shot, bounded, and in-memory."""


S1_EC34_RUN_ID = "e1.repetition-pilot-once.s1ec34.v1"
S1_EC34_AUTHORIZATION_SCOPE = (
    "one-nonpersistent-n1-n2-pilot-exactly-25368-field-arm-steps"
)
S1_EC34_EC33_PREFLIGHT_DIGEST = (
    "77922b78e2347d88b685023e2c86ee728a4ff9ba91ed0c35f495b9101866d3b8"
)


@dataclass(slots=True)
class E1PilotOnceAuthorization:
    scope: str
    approved_field_arm_steps: int
    consumed: bool = False

    def consume(self) -> None:
        if (
            self.scope != S1_EC34_AUTHORIZATION_SCOPE
            or self.approved_field_arm_steps != S1_EC29_FIELD_ARM_STEPS
            or self.consumed
        ):
            raise E1RepetitionPilotOnceRunnerError(
                "S1-EC34 requires one fresh exact owner authorization"
            )
        self.consumed = True


@dataclass(frozen=True, slots=True)
class E1PilotOnceArmMeasurement:
    batch_index: int
    contact_count: int
    refinement_id: str
    role_id: str
    field_step_count: int
    source_support_count: int
    output_digest: str
    maximum_binding: float | None
    total_binding: float | None
    input_objects_preserved: bool

    def __post_init__(self) -> None:
        if (
            self.batch_index not in range(6)
            or self.contact_count not in (1, 2)
            or self.refinement_id not in ("r2", "r4", "r8")
            or self.role_id not in S1_EC29_ARMS
            or self.field_step_count < 1
            or self.source_support_count != self.contact_count * 110
            or len(self.output_digest) != 64
            or self.input_objects_preserved is not True
        ):
            raise E1RepetitionPilotOnceRunnerError(
                "S1-EC34 arm measurement changed"
            )
        is_p0 = self.role_id.startswith("p0_")
        if is_p0 is not (self.maximum_binding is None):
            raise E1RepetitionPilotOnceRunnerError(
                "S1-EC34 P0 and E1 measurements are mixed"
            )
        if not is_p0 and (
            self.maximum_binding is None
            or self.total_binding is None
            or not math.isfinite(self.maximum_binding)
            or not math.isfinite(self.total_binding)
            or self.maximum_binding < 0.0
            or self.total_binding < 0.0
        ):
            raise E1RepetitionPilotOnceRunnerError(
                "S1-EC34 E1 binding measurement is invalid"
            )


@dataclass(frozen=True, slots=True)
class E1PilotOnceBatchContrast:
    batch_index: int
    contact_count: int
    refinement_id: str
    active_state_linf: float
    active_state_l1: float
    repeated_ablation_maximum_binding: float
    continuous_ablation_maximum_binding: float
    p0_output_digests_equal: bool


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotOnceRawResult:
    run_id: str
    contract_digest: str
    plan_set_digest: str
    preflight_digest: str
    measurements: tuple[E1PilotOnceArmMeasurement, ...]
    contrasts: tuple[E1PilotOnceBatchContrast, ...]
    batch_completion_order: tuple[int, ...]
    executed_field_arm_step_count: int
    elapsed_seconds: float
    authorization_consumed: bool
    all_inputs_preserved: bool
    all_supports_assigned_once: bool
    all_ablations_neutral: bool
    full_pilot_completed: bool
    persistence_performed: bool
    technical_interpretation_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.run_id != S1_EC34_RUN_ID
            or self.contract_digest != S1_EC33_EC29_CONTRACT_DIGEST
            or len(self.plan_set_digest) != 64
            or self.preflight_digest != S1_EC34_EC33_PREFLIGHT_DIGEST
            or len(self.measurements) != 36
            or len(self.contrasts) != 6
            or self.batch_completion_order != tuple(range(6))
            or self.executed_field_arm_step_count != S1_EC29_FIELD_ARM_STEPS
            or not math.isfinite(self.elapsed_seconds)
            or self.elapsed_seconds < 0.0
            or any(
                value is not True
                for value in (
                    self.authorization_consumed,
                    self.all_inputs_preserved,
                    self.all_supports_assigned_once,
                    self.all_ablations_neutral,
                    self.full_pilot_completed,
                    self.technical_interpretation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.persistence_performed,
                    self.research_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotOnceRunnerError(
                "S1-EC34 raw result crossed its technical scope"
            )
        payload = {
            "run_id": self.run_id,
            "contract_digest": self.contract_digest,
            "plan_set_digest": self.plan_set_digest,
            "preflight_digest": self.preflight_digest,
            "measurement_digests": tuple(
                _digest(asdict(item)) for item in self.measurements
            ),
            "contrast_digests": tuple(
                _digest(asdict(item)) for item in self.contrasts
            ),
            "batch_completion_order": self.batch_completion_order,
            "executed_field_arm_step_count": self.executed_field_arm_step_count,
            "elapsed_seconds": self.elapsed_seconds,
            "authorization_consumed": self.authorization_consumed,
            "all_inputs_preserved": self.all_inputs_preserved,
            "all_supports_assigned_once": self.all_supports_assigned_once,
            "all_ablations_neutral": self.all_ablations_neutral,
            "full_pilot_completed": self.full_pilot_completed,
            "persistence_performed": self.persistence_performed,
            "technical_interpretation_permitted": self.technical_interpretation_permitted,
            "research_decision_permitted": self.research_decision_permitted,
            "memory_claim_permitted": self.memory_claim_permitted,
        }
        if self.result_digest != _digest(payload):
            raise E1RepetitionPilotOnceRunnerError(
                "S1-EC34 raw result digest changed"
            )


def _bindings(state: E1LocalEdgePlasticityState) -> tuple[float, ...]:
    return tuple(item.binding for item in state.edge_bindings)


def run_e1_repetition_pilot_once_in_memory(
    authorization: E1PilotOnceAuthorization,
    preflight: E1RepetitionPilotPostAdapterPreflight,
    contract: E1RepetitionPilotReleaseContract,
    plans: E1RepetitionFormationPlanSet,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
) -> E1RepetitionPilotOnceRawResult:
    """Consume authorization and run the exact EC29 matrix without writes."""

    if not isinstance(authorization, E1PilotOnceAuthorization):
        raise E1RepetitionPilotOnceRunnerError("S1-EC34 authorization is missing")
    for value, expected, role in (
        (preflight, E1RepetitionPilotPostAdapterPreflight, "EC33 preflight"),
        (contract, E1RepetitionPilotReleaseContract, "EC29 contract"),
        (plans, E1RepetitionFormationPlanSet, "EC27 plans"),
        (initial_field, SharedMCMField, "initial field"),
        (initial_state, E1LocalEdgePlasticityState, "initial state"),
    ):
        if not isinstance(value, expected):
            raise E1RepetitionPilotOnceRunnerError(f"S1-EC34 requires {role}")
    preflight.__post_init__()
    contract.__post_init__()
    plans.__post_init__()
    if (
        preflight.preflight_digest != S1_EC34_EC33_PREFLIGHT_DIGEST
        or preflight.technical_release_ready is not True
        or preflight.pilot_execution_permitted is not False
        or contract.contract_digest != S1_EC33_EC29_CONTRACT_DIGEST
        or plans.plan_set_digest != contract.source_plan_set_digest
        or contract.field_arm_step_count != S1_EC29_FIELD_ARM_STEPS
    ):
        raise E1RepetitionPilotOnceRunnerError("S1-EC34 upstream binding changed")
    authorization.consume()
    start = time.monotonic()
    field_digest = _initial_field_digest(initial_field)
    state_digest = _initial_state_digest(initial_state)
    measurements = []
    contrasts = []
    completed = []
    for batch in contract.batches:
        if time.monotonic() - start > contract.maximum_runtime_seconds:
            raise E1RepetitionPilotOnceRunnerError(
                "S1-EC34 exceeded its runtime cap before the next batch"
            )
        pair = plans.pairs[batch.contact_count - 1]
        schedules = {
            "repeated": pair.repeated_sequences,
            "continuous": pair.continuous_sequences,
        }
        repeated_plan = next(
            item for item in pair.repeated_plans.plans
            if item.refinement_id == batch.refinement_id
        )
        continuous_plan = next(
            item for item in pair.continuous_plans.plans
            if item.refinement_id == batch.refinement_id
        )
        proposal_steps = {
            "repeated": repeated_plan.proposal_steps,
            "continuous": continuous_plan.proposal_steps,
        }
        states = {}
        p0_digests = {}
        for role_id in batch.arm_order:
            schedule_kind = "repeated" if "repeated" in role_id else "continuous"
            sequences = schedules[schedule_kind]
            steps = proposal_steps[schedule_kind]
            if role_id.startswith("p0_"):
                field_copy = copy.deepcopy(initial_field)
                run = run_neutral_asynchronous_field(
                    field_copy,
                    sequences,
                    steps,
                    NeutralLocalFieldSubstrateConfig(1.0),
                    afterimage_config=NeutralFastAfterimageConfig(0.5),
                )
                output_digest = run.field.snapshot().digest()
                p0_digests[schedule_kind] = output_digest
                maximum = None
                total = None
                support_count = run.source_support_count
                preserved = field_copy is not initial_field
            else:
                enabled = role_id.endswith("_active")
                internal_arm_id = (
                    "ab" if schedule_kind == "repeated" else "ba"
                )
                if not enabled:
                    internal_arm_id += "_formation_ablated"
                run = run_prepared_real_formation_arm_in_memory(
                    internal_arm_id,
                    batch.refinement_id,
                    sequences,
                    steps,
                    initial_field,
                    initial_state,
                    enabled,
                )
                state = run.output_state
                states[role_id] = state
                binding_values = _bindings(state)
                maximum = max(binding_values)
                total = math.fsum(binding_values)
                output_digest = run.result_digest
                support_count = run.audit.source_support_count
                preserved = run.input_objects_preserved
            measurements.append(E1PilotOnceArmMeasurement(
                batch.batch_index,
                batch.contact_count,
                batch.refinement_id,
                role_id,
                len(steps),
                support_count,
                output_digest,
                maximum,
                total,
                preserved,
            ))
        repeated_values = _bindings(states["repeated_active"])
        continuous_values = _bindings(states["continuous_active"])
        differences = tuple(
            abs(left - right)
            for left, right in zip(repeated_values, continuous_values, strict=True)
        )
        contrasts.append(E1PilotOnceBatchContrast(
            batch.batch_index,
            batch.contact_count,
            batch.refinement_id,
            max(differences),
            math.fsum(differences),
            max(_bindings(states["repeated_formation_ablated"])),
            max(_bindings(states["continuous_formation_ablated"])),
            p0_digests["repeated"] == p0_digests["continuous"],
        ))
        completed.append(batch.batch_index)
    elapsed = time.monotonic() - start
    preserved = (
        _initial_field_digest(initial_field) == field_digest
        and _initial_state_digest(initial_state) == state_digest
        and all(item.input_objects_preserved for item in measurements)
    )
    executed_steps = sum(item.field_step_count for item in measurements)
    values = {
        "run_id": S1_EC34_RUN_ID,
        "contract_digest": contract.contract_digest,
        "plan_set_digest": plans.plan_set_digest,
        "preflight_digest": preflight.preflight_digest,
        "batch_completion_order": tuple(completed),
        "executed_field_arm_step_count": executed_steps,
        "elapsed_seconds": elapsed,
        "authorization_consumed": authorization.consumed,
        "all_inputs_preserved": preserved,
        "all_supports_assigned_once": all(
            item.source_support_count == item.contact_count * 110
            for item in measurements
        ),
        "all_ablations_neutral": all(
            item.maximum_binding == 0.0
            for item in measurements
            if "formation_ablated" in item.role_id
        ),
        "full_pilot_completed": executed_steps == S1_EC29_FIELD_ARM_STEPS,
        "persistence_performed": False,
        "technical_interpretation_permitted": True,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    payload = dict(values)
    payload["measurement_digests"] = tuple(
        _digest(asdict(item)) for item in measurements
    )
    payload["contrast_digests"] = tuple(
        _digest(asdict(item)) for item in contrasts
    )
    return E1RepetitionPilotOnceRawResult(
        **values,
        measurements=tuple(measurements),
        contrasts=tuple(contrasts),
        result_digest=_digest(payload),
    )
