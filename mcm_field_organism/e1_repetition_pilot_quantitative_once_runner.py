"""Authorized one-shot S1-EC44 quantitative in-memory n1/n2 pilot."""

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
from .e1_repetition_pilot_once_runner import (
    E1PilotOnceArmMeasurement,
    E1PilotOnceBatchContrast,
    _bindings,
)
from .e1_repetition_pilot_quantitative_final_preflight import (
    E1RepetitionPilotQuantitativeFinalPreflight,
)
from .e1_repetition_pilot_quantitative_p0_schema import (
    E1PilotQuantitativeP0Pair,
    E1PilotQuantitativeP0RefinementProfile,
    build_quantitative_p0_refinement_profile,
    collect_quantitative_p0_pair,
)
from .e1_repetition_pilot_release_contract import (
    E1RepetitionPilotReleaseContract,
    S1_EC29_FIELD_ARM_STEPS,
)
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1RepetitionPilotQuantitativeOnceRunnerError(ValueError):
    """Raised when EC44 crosses its exact one-shot technical scope."""


S1_EC44_RUN_ID = "e1.repetition-pilot-quantitative-once.s1ec44.v1"
S1_EC44_AUTHORIZATION_SCOPE = (
    "one-corrected-nonpersistent-n1-n2-pilot-exactly-25368-field-arm-steps"
)
S1_EC44_EC43_PREFLIGHT_DIGEST = (
    "d5ec35418a2c282ea3d9cb5597561e53b457c450dd7e89004adf0c6a1d2f4046"
)
S1_EC44_EC29_CONTRACT_DIGEST = (
    "834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8"
)


@dataclass(slots=True)
class E1QuantitativePilotOnceAuthorization:
    scope: str
    approved_field_arm_steps: int
    consumed: bool = False

    def consume(self) -> None:
        if (
            self.scope != S1_EC44_AUTHORIZATION_SCOPE
            or self.approved_field_arm_steps != S1_EC29_FIELD_ARM_STEPS
            or self.consumed
        ):
            raise E1RepetitionPilotQuantitativeOnceRunnerError(
                "S1-EC44 requires one fresh exact owner authorization"
            )
        self.consumed = True


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotQuantitativeOnceRawResult:
    run_id: str
    contract_digest: str
    plan_set_digest: str
    preflight_digest: str
    measurements: tuple[E1PilotOnceArmMeasurement, ...]
    contrasts: tuple[E1PilotOnceBatchContrast, ...]
    p0_pairs: tuple[E1PilotQuantitativeP0Pair, ...]
    p0_profiles: tuple[E1PilotQuantitativeP0RefinementProfile, ...]
    batch_completion_order: tuple[int, ...]
    executed_field_arm_step_count: int
    p0_snapshot_handoff_count: int
    elapsed_seconds: float
    authorization_consumed: bool
    all_inputs_preserved: bool
    all_supports_assigned_once: bool
    all_ablations_neutral: bool
    full_pilot_completed: bool
    persistence_performed: bool
    technical_raw_report_permitted: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    field_time_claim_permitted: bool
    organization_claim_permitted: bool
    ai_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.run_id != S1_EC44_RUN_ID
            or self.contract_digest != S1_EC44_EC29_CONTRACT_DIGEST
            or len(self.plan_set_digest) != 64
            or self.preflight_digest != S1_EC44_EC43_PREFLIGHT_DIGEST
            or len(self.measurements) != 36
            or len(self.contrasts) != 6
            or len(self.p0_pairs) != 6
            or tuple(item.contact_count for item in self.p0_profiles) != (1, 2)
            or self.batch_completion_order != tuple(range(6))
            or self.executed_field_arm_step_count != S1_EC29_FIELD_ARM_STEPS
            or self.p0_snapshot_handoff_count != 12
            or not math.isfinite(self.elapsed_seconds)
            or self.elapsed_seconds < 0.0
            or any(value is not True for value in (
                self.authorization_consumed,
                self.all_inputs_preserved,
                self.all_supports_assigned_once,
                self.all_ablations_neutral,
                self.full_pilot_completed,
                self.technical_raw_report_permitted,
            ))
            or any(value is not False for value in (
                self.persistence_performed,
                self.result_decision_permitted,
                self.memory_claim_permitted,
                self.field_time_claim_permitted,
                self.organization_claim_permitted,
                self.ai_claim_permitted,
            ))
        ):
            raise E1RepetitionPilotQuantitativeOnceRunnerError(
                "S1-EC44 raw result crossed its technical scope"
            )
        payload = _result_payload(self)
        if self.result_digest != _digest(payload):
            raise E1RepetitionPilotQuantitativeOnceRunnerError(
                "S1-EC44 raw result digest changed"
            )


def _result_payload(result: E1RepetitionPilotQuantitativeOnceRawResult) -> dict:
    return {
        "run_id": result.run_id,
        "contract_digest": result.contract_digest,
        "plan_set_digest": result.plan_set_digest,
        "preflight_digest": result.preflight_digest,
        "measurement_digests": tuple(_digest(asdict(x)) for x in result.measurements),
        "contrast_digests": tuple(_digest(asdict(x)) for x in result.contrasts),
        "p0_pair_digests": tuple(x.pair_digest for x in result.p0_pairs),
        "p0_profile_digests": tuple(x.profile_digest for x in result.p0_profiles),
        "batch_completion_order": result.batch_completion_order,
        "executed_field_arm_step_count": result.executed_field_arm_step_count,
        "p0_snapshot_handoff_count": result.p0_snapshot_handoff_count,
        "elapsed_seconds": result.elapsed_seconds,
        "authorization_consumed": result.authorization_consumed,
        "all_inputs_preserved": result.all_inputs_preserved,
        "all_supports_assigned_once": result.all_supports_assigned_once,
        "all_ablations_neutral": result.all_ablations_neutral,
        "full_pilot_completed": result.full_pilot_completed,
        "persistence_performed": result.persistence_performed,
        "technical_raw_report_permitted": result.technical_raw_report_permitted,
        "result_decision_permitted": result.result_decision_permitted,
        "memory_claim_permitted": result.memory_claim_permitted,
        "field_time_claim_permitted": result.field_time_claim_permitted,
        "organization_claim_permitted": result.organization_claim_permitted,
        "ai_claim_permitted": result.ai_claim_permitted,
    }


def _result_payload_from_values(values: dict) -> dict:
    payload = dict(values)
    payload["measurement_digests"] = tuple(
        _digest(asdict(x)) for x in payload.pop("measurements")
    )
    payload["contrast_digests"] = tuple(
        _digest(asdict(x)) for x in payload.pop("contrasts")
    )
    payload["p0_pair_digests"] = tuple(
        x.pair_digest for x in payload.pop("p0_pairs")
    )
    payload["p0_profile_digests"] = tuple(
        x.profile_digest for x in payload.pop("p0_profiles")
    )
    return payload


def run_e1_repetition_pilot_quantitative_once_in_memory(
    authorization: E1QuantitativePilotOnceAuthorization,
    preflight: E1RepetitionPilotQuantitativeFinalPreflight,
    contract: E1RepetitionPilotReleaseContract,
    plans: E1RepetitionFormationPlanSet,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
) -> E1RepetitionPilotQuantitativeOnceRawResult:
    """Consume the EC44 authorization and execute the exact in-memory matrix."""

    for value, expected, role in (
        (authorization, E1QuantitativePilotOnceAuthorization, "authorization"),
        (preflight, E1RepetitionPilotQuantitativeFinalPreflight, "EC43 preflight"),
        (contract, E1RepetitionPilotReleaseContract, "EC29 contract"),
        (plans, E1RepetitionFormationPlanSet, "EC27 plans"),
        (initial_field, SharedMCMField, "initial field"),
        (initial_state, E1LocalEdgePlasticityState, "initial state"),
    ):
        if not isinstance(value, expected):
            raise E1RepetitionPilotQuantitativeOnceRunnerError(
                f"S1-EC44 requires {role}"
            )
    preflight.__post_init__()
    contract.__post_init__()
    plans.__post_init__()
    if (
        preflight.preflight_digest != S1_EC44_EC43_PREFLIGHT_DIGEST
        or preflight.technical_execution_ready is not True
        or preflight.owner_execution_authorized is not False
        or preflight.pilot_execution_permitted is not False
        or contract.contract_digest != S1_EC44_EC29_CONTRACT_DIGEST
        or plans.plan_set_digest != contract.source_plan_set_digest
        or contract.field_arm_step_count != S1_EC29_FIELD_ARM_STEPS
    ):
        raise E1RepetitionPilotQuantitativeOnceRunnerError(
            "S1-EC44 upstream binding changed"
        )
    authorization.consume()
    start = time.monotonic()
    field_digest = _initial_field_digest(initial_field)
    state_digest = _initial_state_digest(initial_state)
    measurements: list[E1PilotOnceArmMeasurement] = []
    contrasts: list[E1PilotOnceBatchContrast] = []
    p0_pairs: list[E1PilotQuantitativeP0Pair] = []
    completed: list[int] = []

    for batch in contract.batches:
        if time.monotonic() - start > contract.maximum_runtime_seconds:
            raise E1RepetitionPilotQuantitativeOnceRunnerError(
                "S1-EC44 exceeded its runtime cap before the next batch"
            )
        pair = plans.pairs[batch.contact_count - 1]
        schedules = {
            "repeated": pair.repeated_sequences,
            "continuous": pair.continuous_sequences,
        }
        repeated_plan = next(x for x in pair.repeated_plans.plans if x.refinement_id == batch.refinement_id)
        continuous_plan = next(x for x in pair.continuous_plans.plans if x.refinement_id == batch.refinement_id)
        proposal_steps = {
            "repeated": repeated_plan.proposal_steps,
            "continuous": continuous_plan.proposal_steps,
        }
        states = {}
        p0_snapshots = {}
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
                snapshot = run.field.snapshot()
                p0_snapshots[schedule_kind] = snapshot
                output_digest = snapshot.digest()
                maximum = total = None
                support_count = run.source_support_count
                preserved = field_copy is not initial_field
            else:
                enabled = role_id.endswith("_active")
                internal_arm_id = "ab" if schedule_kind == "repeated" else "ba"
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
            if role_id == "p0_continuous":
                p0_pairs.append(collect_quantitative_p0_pair(
                    batch.contact_count,
                    batch.refinement_id,
                    p0_snapshots["repeated"],
                    p0_snapshots["continuous"],
                ))
                p0_snapshots.clear()

        repeated_values = _bindings(states["repeated_active"])
        continuous_values = _bindings(states["continuous_active"])
        differences = tuple(abs(a - b) for a, b in zip(repeated_values, continuous_values, strict=True))
        p0_pair = p0_pairs[-1]
        contrasts.append(E1PilotOnceBatchContrast(
            batch.batch_index,
            batch.contact_count,
            batch.refinement_id,
            max(differences),
            math.fsum(differences),
            max(_bindings(states["repeated_formation_ablated"])),
            max(_bindings(states["continuous_formation_ablated"])),
            p0_pair.repeated_snapshot_digest == p0_pair.continuous_snapshot_digest,
        ))
        completed.append(batch.batch_index)

    profiles = tuple(
        build_quantitative_p0_refinement_profile(tuple(
            item for item in p0_pairs if item.contact_count == contact_count
        ))
        for contact_count in (1, 2)
    )
    elapsed = time.monotonic() - start
    preserved = (
        _initial_field_digest(initial_field) == field_digest
        and _initial_state_digest(initial_state) == state_digest
        and all(item.input_objects_preserved for item in measurements)
    )
    executed_steps = sum(item.field_step_count for item in measurements)
    values = {
        "run_id": S1_EC44_RUN_ID,
        "contract_digest": contract.contract_digest,
        "plan_set_digest": plans.plan_set_digest,
        "preflight_digest": preflight.preflight_digest,
        "measurements": tuple(measurements),
        "contrasts": tuple(contrasts),
        "p0_pairs": tuple(p0_pairs),
        "p0_profiles": profiles,
        "batch_completion_order": tuple(completed),
        "executed_field_arm_step_count": executed_steps,
        "p0_snapshot_handoff_count": len(p0_pairs) * 2,
        "elapsed_seconds": elapsed,
        "authorization_consumed": authorization.consumed,
        "all_inputs_preserved": preserved,
        "all_supports_assigned_once": all(x.source_support_count == x.contact_count * 110 for x in measurements),
        "all_ablations_neutral": all(x.maximum_binding == 0.0 for x in measurements if "formation_ablated" in x.role_id),
        "full_pilot_completed": executed_steps == S1_EC29_FIELD_ARM_STEPS,
        "persistence_performed": False,
        "technical_raw_report_permitted": True,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
        "field_time_claim_permitted": False,
        "organization_claim_permitted": False,
        "ai_claim_permitted": False,
    }
    return E1RepetitionPilotQuantitativeOnceRawResult(
        **values,
        result_digest=_digest(_result_payload_from_values(values)),
    )
