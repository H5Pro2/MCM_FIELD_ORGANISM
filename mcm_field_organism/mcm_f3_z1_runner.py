"""Bounded F3/B3 trajectory runner for the preregistered Z1 audit."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
from typing import Callable

import numpy as np

from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .mcm_f3_baseline_coupling import compute_mcm_f3_linear_coupled_baseline
from .mcm_f3_coupling import compute_mcm_f3_coupling
from .mcm_f3_history_run import mcm_f3_history_preregistration
from .mcm_f3_runtime import (
    activate_mcm_f3_field,
    advance_mcm_f3_shared_field_transient,
)
from .mcm_f3_z1_source import (
    MCMF3Z1SourceArm,
    MCMF3Z1SourceSet,
    build_mcm_f3_z1_source,
)
from .mcm_f3_z1_trajectory import (
    MCMF3Z1Trajectory,
    MCMF3Z1TrajectoryObserver,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff_audit import handoff_receptor_completion_groups
from .shared_mcm_field import SharedMCMField, build_shared_mcm_field
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class MCMF3Z1RunnerError(ValueError):
    """Raised when the Z1 execution inventory or a technical control drifts."""


_MODEL_IDS = ("f3-candidate", "linear-coupled-field")
_SOURCE_ARM_IDS = (
    "a.reference",
    "a.partitioned",
    "a.stretched",
    "a.compressed",
    "a.reversed",
    "a.permuted",
    "b.independent",
)
_REFINEMENTS = (1, 2, 4)
_VISUAL_COLUMNS = 6
_VISUAL_ROWS = 4
_MASS_TOLERANCE = 1e-12


@dataclass(frozen=True, slots=True)
class MCMF3Z1ExecutionTask:
    model_id: str
    arm_id: str
    refinement: int
    reproduction: bool = False

    def __post_init__(self) -> None:
        if self.model_id not in _MODEL_IDS:
            raise MCMF3Z1RunnerError("unknown Z1 model")
        if self.arm_id not in _SOURCE_ARM_IDS:
            raise MCMF3Z1RunnerError("unknown Z1 source arm")
        if self.refinement not in _REFINEMENTS:
            raise MCMF3Z1RunnerError("unknown Z1 refinement")
        if self.reproduction and self.refinement != 4:
            raise MCMF3Z1RunnerError("only the 4n task may be reproduced")

    @property
    def task_key(self) -> tuple[str, str, int, bool]:
        return self.model_id, self.arm_id, self.refinement, self.reproduction


@dataclass(frozen=True, slots=True)
class MCMF3Z1ExecutionPlan:
    preregistration_id: str
    source: MCMF3Z1SourceSet
    base_field: SharedMCMField
    base_layer_digest: str
    tasks: tuple[MCMF3Z1ExecutionTask, ...]
    handoff_controls: tuple[tuple[str, bool], ...]

    def __post_init__(self) -> None:
        if self.preregistration_id != "mcm.f3.z1.trajectory-covariance.v1":
            raise MCMF3Z1RunnerError("Z1 preregistration identity changed")
        if not isinstance(self.source, MCMF3Z1SourceSet):
            raise MCMF3Z1RunnerError("Z1 plan requires the fixed source set")
        if not isinstance(self.base_field, SharedMCMField):
            raise MCMF3Z1RunnerError("Z1 plan requires one shared base field")
        if self.base_field.substrate is not None:
            raise MCMF3Z1RunnerError("Z1 base field must not contain a substrate")
        expected = _execution_tasks(self.source)
        if self.tasks != expected:
            raise MCMF3Z1RunnerError("Z1 task inventory changed")
        if tuple(name for name, _ in self.handoff_controls) != tuple(
            item.arm_id for item in self.source.arms
        ):
            raise MCMF3Z1RunnerError("Z1 handoff control inventory changed")
        if not all(value for _, value in self.handoff_controls):
            raise MCMF3Z1RunnerError("Z1 source handoff is incomplete")


@dataclass(frozen=True, slots=True)
class MCMF3Z1ArmTrajectory:
    model_id: str
    arm_id: str
    refinement: int
    reproduction: bool
    trajectory: MCMF3Z1Trajectory
    final_snapshot_digest: str
    diagnostic_count: int
    maximum_mass_error: float
    minimum_mass: float
    maximum_abs_activation: float
    maximum_abs_afterimage: float

    def __post_init__(self) -> None:
        MCMF3Z1ExecutionTask(
            self.model_id,
            self.arm_id,
            self.refinement,
            self.reproduction,
        )
        if not isinstance(self.trajectory, MCMF3Z1Trajectory):
            raise MCMF3Z1RunnerError("Z1 arm requires one passive trajectory")
        if not isinstance(self.final_snapshot_digest, str) or not self.final_snapshot_digest:
            raise MCMF3Z1RunnerError("Z1 arm requires one final snapshot digest")
        if (
            isinstance(self.diagnostic_count, bool)
            or not isinstance(self.diagnostic_count, int)
            or self.diagnostic_count < 1
        ):
            raise MCMF3Z1RunnerError("Z1 arm requires integration diagnostics")
        for role in (
            "maximum_mass_error",
            "minimum_mass",
            "maximum_abs_activation",
            "maximum_abs_afterimage",
        ):
            value = float(getattr(self, role))
            if not math.isfinite(value) or value < 0.0:
                raise MCMF3Z1RunnerError("Z1 diagnostics must be finite and nonnegative")
            object.__setattr__(self, role, value)

    @property
    def task_key(self) -> tuple[str, str, int, bool]:
        return self.model_id, self.arm_id, self.refinement, self.reproduction


@dataclass(frozen=True, slots=True)
class MCMF3Z1TechnicalPacket:
    preregistration_id: str
    base_layer_digest: str
    source_execution_digests: tuple[tuple[str, str], ...]
    trajectories: tuple[MCMF3Z1ArmTrajectory, ...]
    controls: tuple[tuple[str, bool], ...]
    research_decision: None = None
    run_id: None = None

    def __post_init__(self) -> None:
        if self.preregistration_id != "mcm.f3.z1.trajectory-covariance.v1":
            raise MCMF3Z1RunnerError("Z1 packet preregistration changed")
        trajectories = tuple(self.trajectories)
        expected_tasks = {
            (model_id, arm_id, refinement, reproduction)
            for model_id in _MODEL_IDS
            for arm_id in _SOURCE_ARM_IDS
            for refinement, reproduction in (
                (1, False),
                (2, False),
                (4, False),
                (4, True),
            )
        }
        if {item.task_key for item in trajectories} != expected_tasks:
            raise MCMF3Z1RunnerError("Z1 packet requires all 56 unique tasks")
        if tuple(name for name, _ in self.source_execution_digests) != _SOURCE_ARM_IDS:
            raise MCMF3Z1RunnerError("Z1 packet source digest inventory changed")
        if tuple(name for name, _ in self.controls) != (
            "source_contracts_hold",
            "handoffs_complete",
            "reproductions_exact",
            "mass_and_value_invariants_hold",
            "refinement_final_error_decreased",
        ):
            raise MCMF3Z1RunnerError("Z1 packet controls changed")
        if self.research_decision is not None or self.run_id is not None:
            raise MCMF3Z1RunnerError("technical Z1 packet cannot contain a run decision")
        object.__setattr__(self, "trajectories", trajectories)


def _execution_tasks(source: MCMF3Z1SourceSet) -> tuple[MCMF3Z1ExecutionTask, ...]:
    return tuple(
        MCMF3Z1ExecutionTask(model_id, arm.arm_id, refinement, reproduction)
        for model_id in _MODEL_IDS
        for arm in source.arms
        for refinement, reproduction in ((1, False), (2, False), (4, False), (4, True))
    )


def _handoff_complete(arm: MCMF3Z1SourceArm) -> bool:
    handoff = handoff_receptor_completion_groups(arm.sequences, arm.proposal_steps)
    return (
        not handoff.completed_before_or_at_start_snapshot_ids
        and not handoff.completed_after_horizon_snapshot_ids
        and handoff.every_in_horizon_event_assigned_once
        and handoff.assigned_event_count == arm.event_count
    )


def prepare_mcm_f3_z1_execution() -> MCMF3Z1ExecutionPlan:
    """Prepare all fixed source handoffs without advancing field dynamics."""

    source = build_mcm_f3_z1_source()
    reference = source.arm("a.reference")
    reference_frames = tuple(item.frames[0].frame for item in reference.sequences)
    base_field = build_shared_mcm_field(
        reference_frames,
        audio_video_dock_anatomies(
            auditory_carrier_count=len(reference_frames[0].carrier_ids),
            visual_grid_columns=_VISUAL_COLUMNS,
            visual_grid_rows=_VISUAL_ROWS,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    return MCMF3Z1ExecutionPlan(
        "mcm.f3.z1.trajectory-covariance.v1",
        source,
        base_field,
        base_field.layer.digest(),
        _execution_tasks(source),
        tuple((arm.arm_id, _handoff_complete(arm)) for arm in source.arms),
    )


def _field_vectors(field: SharedMCMField) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if field.substrate is None:
        raise MCMF3Z1RunnerError("Z1 active field lost its substrate")
    return (
        np.asarray([item.activation for item in field.layer.neurons], dtype=np.float64),
        np.asarray([item.afterimage for item in field.layer.neurons], dtype=np.float64),
        np.asarray([item.mass for item in field.substrate.masses], dtype=np.float64),
    )


def _execute_task(
    plan: MCMF3Z1ExecutionPlan,
    task: MCMF3Z1ExecutionTask,
) -> MCMF3Z1ArmTrajectory:
    arm = plan.source.arm(task.arm_id)
    calculator = (
        compute_mcm_f3_coupling
        if task.model_id == "f3-candidate"
        else compute_mcm_f3_linear_coupled_baseline
    )
    field = activate_mcm_f3_field(
        plan.base_field,
        mcm_f3_history_preregistration().active_arm,
    )
    activation, afterimage, mass = _field_vectors(field)
    observer = MCMF3Z1TrajectoryObserver(
        arm.start_tick,
        activation,
        afterimage,
        mass,
    )
    handoff = handoff_receptor_completion_groups(arm.sequences, arm.proposal_steps)
    diagnostics = []
    for batch in handoff.batches:
        dock_trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
        inputs = project_transient_docks_to_neuron_inputs(dock_trajectory, field.docks)
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        result = advance_mcm_f3_shared_field_transient(
            field,
            distribution,
            inputs,
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
            refinement=task.refinement,
            _coupling_calculator=calculator,
            _state_observer=observer,
        )
        field = result.field
        diagnostics.append(result.diagnostics)
    return MCMF3Z1ArmTrajectory(
        task.model_id,
        task.arm_id,
        task.refinement,
        task.reproduction,
        observer.trajectory(),
        field.snapshot().digest(),
        len(diagnostics),
        max(item.maximum_mass_error for item in diagnostics),
        min(item.minimum_mass for item in diagnostics),
        max(item.maximum_abs_activation for item in diagnostics),
        max(item.maximum_abs_afterimage for item in diagnostics),
    )


def _reproductions_exact(trajectories: tuple[MCMF3Z1ArmTrajectory, ...]) -> bool:
    indexed = {item.task_key: item for item in trajectories}
    return all(
        indexed[(model_id, arm_id, 4, False)].trajectory
        == indexed[(model_id, arm_id, 4, True)].trajectory
        and indexed[(model_id, arm_id, 4, False)].final_snapshot_digest
        == indexed[(model_id, arm_id, 4, True)].final_snapshot_digest
        for model_id in _MODEL_IDS
        for arm_id in tuple(item.arm_id for item in _source_arm_runs(trajectories))
    )


def _source_arm_runs(
    trajectories: tuple[MCMF3Z1ArmTrajectory, ...],
) -> tuple[MCMF3Z1ArmTrajectory, ...]:
    return tuple(
        item
        for item in trajectories
        if item.model_id == _MODEL_IDS[0]
        and item.refinement == 1
        and not item.reproduction
    )


def _final_vector(item: MCMF3Z1ArmTrajectory) -> np.ndarray:
    sample = item.trajectory.samples[-1]
    return np.asarray(sample.activation + sample.afterimage + sample.mass)


def _refinement_error_decreased(
    trajectories: tuple[MCMF3Z1ArmTrajectory, ...],
) -> bool:
    indexed = {item.task_key: item for item in trajectories}
    arm_ids = tuple(item.arm_id for item in _source_arm_runs(trajectories))
    for model_id in _MODEL_IDS:
        for arm_id in arm_ids:
            n = _final_vector(indexed[(model_id, arm_id, 1, False)])
            two_n = _final_vector(indexed[(model_id, arm_id, 2, False)])
            four_n = _final_vector(indexed[(model_id, arm_id, 4, False)])
            if float(np.linalg.norm(two_n - four_n)) > float(np.linalg.norm(n - two_n)):
                return False
    return True


_TaskExecutor = Callable[
    [MCMF3Z1ExecutionPlan, MCMF3Z1ExecutionTask],
    MCMF3Z1ArmTrajectory,
]


def _execute_mcm_f3_z1_packet(
    plan: MCMF3Z1ExecutionPlan,
    executor: _TaskExecutor,
) -> MCMF3Z1TechnicalPacket:
    trajectories = tuple(executor(plan, task) for task in plan.tasks)
    invariants_hold = all(
        item.maximum_mass_error <= _MASS_TOLERANCE
        and item.minimum_mass >= 0.0
        and math.isfinite(item.maximum_abs_activation)
        and math.isfinite(item.maximum_abs_afterimage)
        for item in trajectories
    )
    controls = (
        ("source_contracts_hold", True),
        ("handoffs_complete", all(value for _, value in plan.handoff_controls)),
        ("reproductions_exact", _reproductions_exact(trajectories)),
        ("mass_and_value_invariants_hold", invariants_hold),
        ("refinement_final_error_decreased", _refinement_error_decreased(trajectories)),
    )
    return MCMF3Z1TechnicalPacket(
        plan.preregistration_id,
        plan.base_layer_digest,
        tuple((item.arm_id, item.execution_digest) for item in plan.source.arms),
        trajectories,
        controls,
    )


def execute_mcm_f3_z1_technical_packet() -> MCMF3Z1TechnicalPacket:
    """Advance all fixed tasks but emit no research decision or run artifact."""

    return _execute_mcm_f3_z1_packet(prepare_mcm_f3_z1_execution(), _execute_task)


def mcm_f3_z1_runner_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            MCMF3Z1ExecutionTask,
            MCMF3Z1ExecutionPlan,
            MCMF3Z1ArmTrajectory,
            MCMF3Z1TechnicalPacket,
        )
        for item in fields(cls)
    )
