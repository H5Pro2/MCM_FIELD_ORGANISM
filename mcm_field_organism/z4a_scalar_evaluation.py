"""Pure Z4-A4 decision and trajectory-free scalar result schema."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import json
import math
from typing import Iterable


class Z4AScalarEvaluationError(ValueError):
    """Raised when scalar input or a Z4-A4 decision leaves its contract."""


WORLD_ORDER = (
    "z4a.video.street-traffic.v1",
    "z4a.av.nasa-earthrise.v1",
    "z4a.audio.sound-mute-sound.v1",
    "z4a.browser.direct.reference.v2",
)
MODEL_ORDER = ("p0.exact", "f3.candidate", "b3.linear-coupled")
ARM_ORDER = (
    "reference",
    "reproduction",
    "partitioned",
    "reversed",
    "permuted",
    "independent",
)
TECHNICAL_CONTROL_ORDER = (
    "all_world_bindings_match",
    "all_world_packages_complete",
    "task_inventory_complete",
    "all_handoffs_complete",
    "all_models_share_handoffs",
    "all_base_fields_match",
    "all_completion_supports_complete",
    "reference_reproduction_stable",
    "partition_invariant",
    "refinement_converges",
    "state_invariants_hold",
    "observer_passive",
    "persistence_boundary_holds",
)
_DECISIONS = {
    "FIELD_ENCODER_NOT_TECHNICALLY_STABLE",
    "F3_TECHNICAL_TRAJECTORY_ADVANTAGE",
    "FIELD_ENCODER_CAUSAL_BUT_BASELINE_EQUIVALENT",
    "NO_STABLE_CAUSAL_FIELD_SEPARATION",
    "Z4A_DECISION_UNRESOLVED",
}
_FORBIDDEN_KEYS = {
    "samples",
    "raw_samples",
    "raw_audio",
    "raw_video",
    "pixels",
    "frames",
    "receptor_sequences",
    "full_trajectories",
    "decision_trajectories",
    "trajectory_samples",
    "field_vectors",
    "activation_vector",
    "afterimage_vector",
    "mass_vector",
    "baseline_state_vector",
}


def _finite_nonnegative(value: float, role: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise Z4AScalarEvaluationError(f"{role} must be finite and nonnegative")
    return number


def _optional_finite_nonnegative(value: float | None, role: str) -> float | None:
    return None if value is None else _finite_nonnegative(value, role)


def _nonnegative_int(value: int, role: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Z4AScalarEvaluationError(f"{role} must be a nonnegative integer")
    return value


def _is_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


@dataclass(frozen=True, slots=True)
class Z4AComponentMeasurement:
    component_id: str
    reference_path_length: float
    n_to_2n_distance: float | None
    two_n_to_4n_distance: float | None
    numerical_envelope: float
    distance_from_reference: float
    comparison_envelope: float
    within_comparison_envelope: bool
    above_comparison_envelope: bool

    def __post_init__(self) -> None:
        if self.component_id not in {
            "activation",
            "afterimage",
            "mcm_mass",
            "baseline_state",
        }:
            raise Z4AScalarEvaluationError("unknown scalar component")
        for role in (
            "reference_path_length",
            "numerical_envelope",
            "distance_from_reference",
            "comparison_envelope",
        ):
            object.__setattr__(
                self,
                role,
                _finite_nonnegative(getattr(self, role), role),
            )
        for role in ("n_to_2n_distance", "two_n_to_4n_distance"):
            object.__setattr__(
                self,
                role,
                _optional_finite_nonnegative(getattr(self, role), role),
            )
        if not isinstance(self.within_comparison_envelope, bool) or not isinstance(
            self.above_comparison_envelope, bool
        ):
            raise Z4AScalarEvaluationError("comparison flags must be boolean")
        expected_within = self.distance_from_reference <= self.comparison_envelope
        if (
            self.within_comparison_envelope != expected_within
            or self.above_comparison_envelope == expected_within
        ):
            raise Z4AScalarEvaluationError("comparison flags changed")


@dataclass(frozen=True, slots=True)
class Z4ARefinementTaskSummary:
    refinement: int | None
    integration_method: str
    final_snapshot_digest: str
    diagnostic_count: int
    substep_count: int
    runtime_seconds: float
    maximum_step_seconds: float
    maximum_abs_activation: float
    maximum_abs_afterimage: float
    maximum_auxiliary_conservation_error: float | None
    minimum_auxiliary_value: float | None

    def __post_init__(self) -> None:
        if self.refinement not in {None, 1, 2, 4}:
            raise Z4AScalarEvaluationError("unknown refinement summary")
        if self.integration_method not in {"p0.exact", "ssprk33"}:
            raise Z4AScalarEvaluationError("unknown integration method")
        if not _is_digest(self.final_snapshot_digest):
            raise Z4AScalarEvaluationError("final snapshot digest is invalid")
        for role in ("diagnostic_count", "substep_count"):
            object.__setattr__(self, role, _nonnegative_int(getattr(self, role), role))
        for role in (
            "runtime_seconds",
            "maximum_step_seconds",
            "maximum_abs_activation",
            "maximum_abs_afterimage",
        ):
            object.__setattr__(
                self,
                role,
                _finite_nonnegative(getattr(self, role), role),
            )
        for role in (
            "maximum_auxiliary_conservation_error",
            "minimum_auxiliary_value",
        ):
            object.__setattr__(
                self,
                role,
                _optional_finite_nonnegative(getattr(self, role), role),
            )


@dataclass(frozen=True, slots=True)
class Z4AArmScalarResult:
    arm_id: str
    execution_digest: str
    final_snapshot_digest: str
    technical_support_count: int
    decision_support_count: int
    component_measurements: tuple[Z4AComponentMeasurement, ...]
    refinement_task_summaries: tuple[Z4ARefinementTaskSummary, ...]

    def __post_init__(self) -> None:
        if self.arm_id not in ARM_ORDER:
            raise Z4AScalarEvaluationError("unknown scalar arm")
        for role in ("execution_digest", "final_snapshot_digest"):
            value = getattr(self, role)
            if not _is_digest(value):
                raise Z4AScalarEvaluationError(f"{role} is invalid")
        for role in ("technical_support_count", "decision_support_count"):
            object.__setattr__(self, role, _nonnegative_int(getattr(self, role), role))
        measurements = tuple(self.component_measurements)
        summaries = tuple(self.refinement_task_summaries)
        if not measurements or any(
            not isinstance(item, Z4AComponentMeasurement) for item in measurements
        ):
            raise Z4AScalarEvaluationError("arm component measurements are missing")
        if not summaries or any(
            not isinstance(item, Z4ARefinementTaskSummary) for item in summaries
        ):
            raise Z4AScalarEvaluationError("arm refinement summaries are missing")
        object.__setattr__(self, "component_measurements", measurements)
        object.__setattr__(self, "refinement_task_summaries", summaries)


@dataclass(frozen=True, slots=True)
class Z4AModelScalarResult:
    model_id: str
    component_ids: tuple[str, ...]
    dynamic_scalar_state_budget: int
    technically_stable: bool
    stable_causal_separation: bool | None
    fast_component_causal_separation: bool | None
    failed_controls: tuple[str, ...]
    arm_results: tuple[Z4AArmScalarResult, ...]
    runtime_seconds: float
    substep_count: int
    maximum_abs_activation: float
    maximum_abs_afterimage: float
    maximum_auxiliary_conservation_error: float | None
    minimum_auxiliary_value: float | None

    def __post_init__(self) -> None:
        expected_components = {
            "p0.exact": ("activation", "afterimage"),
            "f3.candidate": ("activation", "afterimage", "mcm_mass"),
            "b3.linear-coupled": (
                "activation",
                "afterimage",
                "baseline_state",
            ),
        }
        if self.model_id not in expected_components or tuple(
            self.component_ids
        ) != expected_components[self.model_id]:
            raise Z4AScalarEvaluationError("model component inventory changed")
        _nonnegative_int(self.dynamic_scalar_state_budget, "state budget")
        if not isinstance(self.technically_stable, bool):
            raise Z4AScalarEvaluationError("model stability must be boolean")
        for role in (
            "stable_causal_separation",
            "fast_component_causal_separation",
        ):
            value = getattr(self, role)
            if value is not None and not isinstance(value, bool):
                raise Z4AScalarEvaluationError("model decision flag is invalid")
        if self.technically_stable:
            if self.stable_causal_separation is None:
                raise Z4AScalarEvaluationError("stable model decision is missing")
        elif (
            self.stable_causal_separation is not None
            or self.fast_component_causal_separation is not None
        ):
            raise Z4AScalarEvaluationError("unstable model exposes a finding")
        if self.model_id != "f3.candidate" and self.technically_stable:
            if self.fast_component_causal_separation != self.stable_causal_separation:
                raise Z4AScalarEvaluationError("baseline fast decision changed")
        arms = tuple(self.arm_results)
        if tuple(item.arm_id for item in arms) != ARM_ORDER:
            raise Z4AScalarEvaluationError("model arm result order changed")
        object.__setattr__(self, "arm_results", arms)
        object.__setattr__(self, "runtime_seconds", _finite_nonnegative(self.runtime_seconds, "runtime"))
        object.__setattr__(self, "substep_count", _nonnegative_int(self.substep_count, "substeps"))
        for role in ("maximum_abs_activation", "maximum_abs_afterimage"):
            object.__setattr__(self, role, _finite_nonnegative(getattr(self, role), role))
        for role in (
            "maximum_auxiliary_conservation_error",
            "minimum_auxiliary_value",
        ):
            object.__setattr__(
                self,
                role,
                _optional_finite_nonnegative(getattr(self, role), role),
            )
        if self.model_id == "p0.exact" and (
            self.maximum_auxiliary_conservation_error is not None
            or self.minimum_auxiliary_value is not None
        ):
            raise Z4AScalarEvaluationError("P0 gained auxiliary diagnostics")


@dataclass(frozen=True, slots=True)
class Z4AWorldScalarResult:
    world_id: str
    execution_status: str
    failed_controls: tuple[str, ...]
    source_binding_digests: tuple[tuple[str, str], ...]
    sequence_digests: tuple[tuple[str, str], ...]
    proposal_digests: tuple[tuple[str, str], ...]
    base_layer_digest: str
    dock_map_digest: str
    source_event_count: int
    completion_group_count: int
    technical_support_count: int
    decision_support_count: int
    model_results: tuple[Z4AModelScalarResult, ...]
    task_count_planned: int
    task_count_completed: int
    runtime_seconds: float

    def __post_init__(self) -> None:
        if self.world_id not in WORLD_ORDER:
            raise Z4AScalarEvaluationError("unknown Z4-A4 world")
        if self.execution_status not in {"completed", "technical_abort", "not_started"}:
            raise Z4AScalarEvaluationError("unknown world execution status")
        for role in (
            "source_event_count",
            "completion_group_count",
            "technical_support_count",
            "decision_support_count",
            "task_count_planned",
            "task_count_completed",
        ):
            object.__setattr__(self, role, _nonnegative_int(getattr(self, role), role))
        object.__setattr__(self, "runtime_seconds", _finite_nonnegative(self.runtime_seconds, "runtime"))
        models = tuple(self.model_results)
        if self.execution_status == "completed":
            if tuple(item.model_id for item in models) != MODEL_ORDER:
                raise Z4AScalarEvaluationError("completed world model order changed")
            if self.task_count_planned != 42 or self.task_count_completed != 42:
                raise Z4AScalarEvaluationError("completed world requires 42 tasks")
        elif self.execution_status == "not_started" and (
            models or self.task_count_completed != 0
        ):
            raise Z4AScalarEvaluationError("not-started world contains results")
        object.__setattr__(self, "model_results", models)

    def model(self, model_id: str) -> Z4AModelScalarResult:
        for model in self.model_results:
            if model.model_id == model_id:
                return model
        raise KeyError(model_id)


@dataclass(frozen=True, slots=True)
class Z4AModelDecisionState:
    model_id: str
    technically_stable: bool
    stable_causal_separation: bool | None
    fast_component_causal_separation: bool | None

    def __post_init__(self) -> None:
        if self.model_id not in MODEL_ORDER or not isinstance(
            self.technically_stable, bool
        ):
            raise Z4AScalarEvaluationError("model decision state is invalid")
        if self.technically_stable:
            if not isinstance(self.stable_causal_separation, bool) or not isinstance(
                self.fast_component_causal_separation, bool
            ):
                raise Z4AScalarEvaluationError("stable model decision flags are missing")
        elif (
            self.stable_causal_separation is not None
            or self.fast_component_causal_separation is not None
        ):
            raise Z4AScalarEvaluationError("unstable model exposes decision flags")


@dataclass(frozen=True, slots=True)
class Z4AWorldDecisionState:
    world_id: str
    models: tuple[Z4AModelDecisionState, ...]

    def __post_init__(self) -> None:
        if self.world_id not in WORLD_ORDER or tuple(
            item.model_id for item in self.models
        ) != MODEL_ORDER:
            raise Z4AScalarEvaluationError("world decision state order changed")
        object.__setattr__(self, "models", tuple(self.models))

    def model(self, model_id: str) -> Z4AModelDecisionState:
        return self.models[MODEL_ORDER.index(model_id)]


@dataclass(frozen=True, slots=True)
class Z4ADecisionBasis:
    stable_world_ids_by_model: tuple[tuple[str, tuple[str, ...]], ...]
    f3_advantage_world_ids: tuple[str, ...]
    baseline_covered_f3_world_ids: tuple[str, ...]
    unresolved_reason_id: str | None

    def __post_init__(self) -> None:
        if tuple(name for name, _ in self.stable_world_ids_by_model) != MODEL_ORDER:
            raise Z4AScalarEvaluationError("decision basis model order changed")
        for _, world_ids in self.stable_world_ids_by_model:
            if tuple(world_id for world_id in WORLD_ORDER if world_id in world_ids) != tuple(
                world_ids
            ):
                raise Z4AScalarEvaluationError("decision basis world order changed")
        for world_ids in (
            self.f3_advantage_world_ids,
            self.baseline_covered_f3_world_ids,
        ):
            if tuple(world_id for world_id in WORLD_ORDER if world_id in world_ids) != tuple(
                world_ids
            ):
                raise Z4AScalarEvaluationError("decision subset world order changed")
        if self.unresolved_reason_id not in {
            None,
            "mixed_stable_separation_not_preregistered",
        }:
            raise Z4AScalarEvaluationError("unknown unresolved reason")


@dataclass(frozen=True, slots=True)
class Z4ADecisionResult:
    overall_decision: str
    decision_basis: Z4ADecisionBasis

    def __post_init__(self) -> None:
        if self.overall_decision not in _DECISIONS or not isinstance(
            self.decision_basis, Z4ADecisionBasis
        ):
            raise Z4AScalarEvaluationError("overall decision is invalid")


def evaluate_z4a_decision(
    worlds: Iterable[Z4AWorldDecisionState],
    technical_controls: Iterable[tuple[str, bool]],
) -> Z4ADecisionResult:
    """Apply the complete preregistered decision tree without side effects."""

    worlds_in = tuple(worlds)
    controls = tuple(technical_controls)
    if tuple(world.world_id for world in worlds_in) != WORLD_ORDER:
        raise Z4AScalarEvaluationError("decision requires all four ordered worlds")
    if tuple(name for name, _ in controls) != TECHNICAL_CONTROL_ORDER or any(
        not isinstance(value, bool) for _, value in controls
    ):
        raise Z4AScalarEvaluationError("technical control inventory changed")
    if not all(value for _, value in controls) or any(
        not model.technically_stable
        for world in worlds_in
        for model in world.models
    ):
        empty = tuple((model_id, ()) for model_id in MODEL_ORDER)
        return Z4ADecisionResult(
            "FIELD_ENCODER_NOT_TECHNICALLY_STABLE",
            Z4ADecisionBasis(empty, (), (), None),
        )

    stable = tuple(
        (
            model_id,
            tuple(
                world.world_id
                for world in worlds_in
                if world.model(model_id).stable_causal_separation
            ),
        )
        for model_id in MODEL_ORDER
    )
    stable_by_model = dict(stable)
    f3_advantage = tuple(
        world.world_id
        for world in worlds_in
        if world.model("f3.candidate").stable_causal_separation
        and world.model("f3.candidate").fast_component_causal_separation
        and not world.model("p0.exact").stable_causal_separation
        and not world.model("b3.linear-coupled").stable_causal_separation
    )
    baseline_covered_f3 = tuple(
        world.world_id
        for world in worlds_in
        if world.model("f3.candidate").stable_causal_separation
        and (
            world.model("p0.exact").stable_causal_separation
            or world.model("b3.linear-coupled").stable_causal_separation
        )
    )
    unresolved_reason = None
    if len(f3_advantage) >= 2:
        decision = "F3_TECHNICAL_TRAJECTORY_ADVANTAGE"
    elif (
        len(stable_by_model["p0.exact"]) >= 3
        or len(stable_by_model["b3.linear-coupled"]) >= 3
        or (
            len(stable_by_model["f3.candidate"]) >= 3
            and set(stable_by_model["f3.candidate"]) <= set(baseline_covered_f3)
        )
    ):
        decision = "FIELD_ENCODER_CAUSAL_BUT_BASELINE_EQUIVALENT"
    elif all(len(world_ids) < 3 for _, world_ids in stable):
        decision = "NO_STABLE_CAUSAL_FIELD_SEPARATION"
    else:
        decision = "Z4A_DECISION_UNRESOLVED"
        unresolved_reason = "mixed_stable_separation_not_preregistered"
    return Z4ADecisionResult(
        decision,
        Z4ADecisionBasis(
            stable,
            f3_advantage,
            baseline_covered_f3,
            unresolved_reason,
        ),
    )


@dataclass(frozen=True, slots=True)
class Z4ATaskBudget:
    world_count: int
    tasks_per_world: int
    task_count_planned: int
    task_count_completed: int

    def __post_init__(self) -> None:
        if (
            self.world_count != 4
            or self.tasks_per_world != 42
            or self.task_count_planned != 168
            or _nonnegative_int(self.task_count_completed, "completed tasks") > 168
        ):
            raise Z4AScalarEvaluationError("Z4-A4 task budget changed")


@dataclass(frozen=True, slots=True)
class Z4AScalarEvaluationResult:
    schema_id: str
    run_id: str
    preregistration_id: str
    runner_contract_id: str
    decision_contract_id: str
    execution_status: str
    technical_abort_stage: str | None
    world_order: tuple[str, ...]
    model_order: tuple[str, ...]
    arm_order: tuple[str, ...]
    binding_digests: tuple[tuple[str, str], ...]
    technical_controls: tuple[tuple[str, bool], ...]
    world_results: tuple[Z4AWorldScalarResult, ...]
    task_budget: Z4ATaskBudget
    overall_decision: str
    decision_basis: Z4ADecisionBasis
    raw_payload_retained: bool = False
    raw_receptor_sequences_retained: bool = False
    raw_trajectories_retained: bool = False
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    self_regulation_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if (
            self.schema_id != "mcm.z4a.multiworld-field-encoder.run197.v1"
            or self.run_id != "lauf-197"
            or self.preregistration_id != "mcm.z4a.multiworld-field-encoder.v1"
            or self.runner_contract_id != "z4a.generic-field-trajectory-runner.v1"
            or self.decision_contract_id != "z4a.multiworld-field-encoder-decision.v1"
        ):
            raise Z4AScalarEvaluationError("Z4-A4 result identity changed")
        if tuple(self.world_order) != WORLD_ORDER or tuple(self.model_order) != MODEL_ORDER or tuple(self.arm_order) != ARM_ORDER:
            raise Z4AScalarEvaluationError("Z4-A4 result order changed")
        if tuple(name for name, _ in self.technical_controls) != TECHNICAL_CONTROL_ORDER:
            raise Z4AScalarEvaluationError("result control order changed")
        if any(not isinstance(value, bool) for _, value in self.technical_controls):
            raise Z4AScalarEvaluationError("result controls must be boolean")
        if tuple(item.world_id for item in self.world_results) != WORLD_ORDER:
            raise Z4AScalarEvaluationError("result world order changed")
        if self.execution_status not in {"completed", "technical_abort"}:
            raise Z4AScalarEvaluationError("result execution status changed")
        allowed_stages = {
            None,
            "source_preflight",
            "world_package",
            "runner",
            "completion_support",
            "evaluation",
            "serialization",
        }
        if self.technical_abort_stage not in allowed_stages:
            raise Z4AScalarEvaluationError("technical abort stage changed")
        if self.execution_status == "completed" and (
            self.technical_abort_stage is not None
            or self.task_budget.task_count_completed != 168
        ):
            raise Z4AScalarEvaluationError("completed result is incomplete")
        if self.execution_status == "technical_abort" and (
            self.technical_abort_stage is None
            or self.overall_decision != "FIELD_ENCODER_NOT_TECHNICALLY_STABLE"
        ):
            raise Z4AScalarEvaluationError("technical abort decision changed")
        if self.overall_decision not in _DECISIONS:
            raise Z4AScalarEvaluationError("result decision changed")
        claim_flags = (
            self.raw_payload_retained,
            self.raw_receptor_sequences_retained,
            self.raw_trajectories_retained,
            self.memory_claim_allowed,
            self.organization_claim_allowed,
            self.topology_claim_allowed,
            self.semantics_claim_allowed,
            self.self_regulation_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(value is not False for value in claim_flags):
            raise Z4AScalarEvaluationError("retention or claim boundary changed")


def z4a_scalar_result_json_value(result: Z4AScalarEvaluationResult) -> dict:
    if not isinstance(result, Z4AScalarEvaluationResult):
        raise Z4AScalarEvaluationError("serialization requires one scalar result")
    value = asdict(result)

    def validate(item: object) -> None:
        if isinstance(item, dict):
            forbidden = _FORBIDDEN_KEYS & set(item)
            if forbidden:
                raise Z4AScalarEvaluationError(
                    f"forbidden persistence keys: {sorted(forbidden)}"
                )
            for key, nested in item.items():
                if not isinstance(key, str):
                    raise Z4AScalarEvaluationError("JSON keys must be strings")
                validate(nested)
        elif isinstance(item, (list, tuple)):
            for nested in item:
                validate(nested)
        elif isinstance(item, float) and not math.isfinite(item):
            raise Z4AScalarEvaluationError("JSON numbers must be finite")

    validate(value)
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    )
    encoded.encode("ascii")
    return json.loads(encoded)


def z4a_scalar_result_json_text(result: Z4AScalarEvaluationResult) -> str:
    return json.dumps(
        z4a_scalar_result_json_value(result),
        allow_nan=False,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ) + "\n"


def z4a_scalar_evaluation_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            Z4AComponentMeasurement,
            Z4ARefinementTaskSummary,
            Z4AArmScalarResult,
            Z4AModelScalarResult,
            Z4AWorldScalarResult,
            Z4AModelDecisionState,
            Z4AWorldDecisionState,
            Z4ADecisionBasis,
            Z4ADecisionResult,
            Z4ATaskBudget,
            Z4AScalarEvaluationResult,
        )
        for item in fields(contract)
    )
