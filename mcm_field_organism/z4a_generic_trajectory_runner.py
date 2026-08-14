"""Generic 42-task P0/F3/B3 technical trajectory runner for Z4-A3."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import time
from typing import Callable, Iterable

import numpy as np

from .field_step_time import MCMFieldStepTime
from .mcm_f3_baseline_coupling import compute_mcm_f3_linear_coupled_baseline
from .mcm_f3_controlled_history_source import mcm_f3_receptor_sequences_digest
from .mcm_f3_coupling import compute_mcm_f3_coupling
from .mcm_f3_history_run import mcm_f3_history_preregistration
from .mcm_f3_runtime import (
    MCMF3AdvanceDiagnostics,
    activate_mcm_f3_field,
    advance_mcm_f3_shared_field_transient,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff_audit import (
    ReceptorProposalHandoff,
    handoff_receptor_completion_groups,
)
from .receptor_time_alignment import ReceptorTimeSequence
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs
from .z4a_component_trajectory import (
    Z4AComponentTrajectory,
    Z4ATrajectoryObserver,
    Z4ATrajectorySupport,
    build_z4a_trajectory_support,
)


class Z4AGenericTrajectoryRunnerError(ValueError):
    """Raised when a Z4-A3 world, task, or technical result drifts."""


_ARM_IDS = (
    "reference",
    "reproduction",
    "partitioned",
    "reversed",
    "permuted",
    "independent",
)
_MODEL_IDS = ("p0.exact", "f3.candidate", "b3.linear-coupled")
_REFINEMENTS = (1, 2, 4)
_MASS_TOLERANCE = 1e-12


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _is_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def z4a_proposal_steps_digest(steps: Iterable[MCMFieldStepTime]) -> str:
    steps_in = tuple(steps)
    if not steps_in or any(not isinstance(item, MCMFieldStepTime) for item in steps_in):
        raise Z4AGenericTrajectoryRunnerError("proposal digest requires field steps")
    return _digest(
        [
            {
                "clock_id": item.clock_id,
                "start_tick": item.start_tick,
                "end_tick": item.end_tick,
                "ticks_per_second": item.ticks_per_second,
            }
            for item in steps_in
        ]
    )


def z4a_execution_digest(sequence_digest: str, proposal_digest: str) -> str:
    if not _is_digest(sequence_digest) or not _is_digest(proposal_digest):
        raise Z4AGenericTrajectoryRunnerError(
            "execution digest requires canonical sequence and proposal digests"
        )
    return _digest(
        {
            "sequence_digest": sequence_digest,
            "proposal_digest": proposal_digest,
        }
    )


@dataclass(frozen=True, slots=True)
class Z4AWorldArmInput:
    arm_id: str
    sequences: tuple[ReceptorTimeSequence, ...]
    sequence_digest: str
    proposal_steps: tuple[MCMFieldStepTime, ...]
    proposal_digest: str
    execution_digest: str

    def __post_init__(self) -> None:
        if self.arm_id not in _ARM_IDS:
            raise Z4AGenericTrajectoryRunnerError("unknown Z4-A3 source arm")
        sequences = tuple(self.sequences)
        steps = tuple(self.proposal_steps)
        if not sequences or any(
            not isinstance(item, ReceptorTimeSequence) for item in sequences
        ):
            raise Z4AGenericTrajectoryRunnerError("arm requires receptor sequences")
        if not steps or any(not isinstance(item, MCMFieldStepTime) for item in steps):
            raise Z4AGenericTrajectoryRunnerError("arm requires proposal steps")
        if any(
            earlier.end_tick != later.start_tick
            for earlier, later in zip(steps, steps[1:])
        ):
            raise Z4AGenericTrajectoryRunnerError("proposal steps must be contiguous")
        clock_id = steps[0].clock_id
        ticks_per_second = steps[0].ticks_per_second
        if any(
            item.clock_id != clock_id or item.ticks_per_second != ticks_per_second
            for item in steps
        ) or any(item.clock_id != clock_id for item in sequences):
            raise Z4AGenericTrajectoryRunnerError("arm clock binding changed")
        expected_sequence = mcm_f3_receptor_sequences_digest(sequences)
        expected_proposal = z4a_proposal_steps_digest(steps)
        expected_execution = z4a_execution_digest(
            expected_sequence,
            expected_proposal,
        )
        if self.sequence_digest != expected_sequence:
            raise Z4AGenericTrajectoryRunnerError("arm sequence digest changed")
        if self.proposal_digest != expected_proposal:
            raise Z4AGenericTrajectoryRunnerError("arm proposal digest changed")
        if self.execution_digest != expected_execution:
            raise Z4AGenericTrajectoryRunnerError("arm execution digest changed")
        object.__setattr__(self, "sequences", sequences)
        object.__setattr__(self, "proposal_steps", steps)

    @property
    def start_tick(self) -> int:
        return self.proposal_steps[0].start_tick

    @property
    def end_tick(self) -> int:
        return self.proposal_steps[-1].end_tick


def build_z4a_world_arm_input(
    arm_id: str,
    sequences: Iterable[ReceptorTimeSequence],
    proposal_steps: Iterable[MCMFieldStepTime],
) -> Z4AWorldArmInput:
    sequences_in = tuple(sequences)
    steps_in = tuple(proposal_steps)
    sequence_digest = mcm_f3_receptor_sequences_digest(sequences_in)
    proposal_digest = z4a_proposal_steps_digest(steps_in)
    return Z4AWorldArmInput(
        arm_id,
        sequences_in,
        sequence_digest,
        steps_in,
        proposal_digest,
        z4a_execution_digest(sequence_digest, proposal_digest),
    )


def _world_digest_payload(
    world_id: str,
    source_binding_digests: tuple[tuple[str, str], ...],
    modality_ids: tuple[str, ...],
    clock_id: str,
    ticks_per_second: float,
    horizon_start_tick: int,
    horizon_end_tick: int,
    dock_anatomies: tuple[tuple[str, ReceptorDockAnatomy], ...],
    field_sample_offsets: tuple[tuple[int, ...], ...],
    arms: tuple[Z4AWorldArmInput, ...],
) -> dict:
    return {
        "world_id": world_id,
        "source_binding_digests": source_binding_digests,
        "modality_ids": modality_ids,
        "clock_id": clock_id,
        "ticks_per_second": ticks_per_second,
        "horizon": (horizon_start_tick, horizon_end_tick),
        "dock_anatomies": [
            {
                "modality_id": modality_id,
                "dock_id": anatomy.dock_id,
                "positions": anatomy.positions,
            }
            for modality_id, anatomy in dock_anatomies
        ],
        "field_sample_offsets": field_sample_offsets,
        "arms": [
            (
                arm.arm_id,
                arm.sequence_digest,
                arm.proposal_digest,
                arm.execution_digest,
            )
            for arm in arms
        ],
    }


def z4a_world_contract_digest(
    world_id: str,
    source_binding_digests: tuple[tuple[str, str], ...],
    modality_ids: tuple[str, ...],
    clock_id: str,
    ticks_per_second: float,
    horizon_start_tick: int,
    horizon_end_tick: int,
    dock_anatomies: tuple[tuple[str, ReceptorDockAnatomy], ...],
    field_sample_offsets: tuple[tuple[int, ...], ...],
    arms: tuple[Z4AWorldArmInput, ...],
) -> str:
    return _digest(
        _world_digest_payload(
            world_id,
            source_binding_digests,
            modality_ids,
            clock_id,
            ticks_per_second,
            horizon_start_tick,
            horizon_end_tick,
            dock_anatomies,
            field_sample_offsets,
            arms,
        )
    )


def _sequence_structure(sequence: ReceptorTimeSequence) -> tuple:
    return (
        sequence.modality_id,
        sequence.geometry_id,
        tuple(
            (
                item.frame.clock_id,
                item.frame.window_start_tick,
                item.frame.window_end_tick,
                item.field_time.window_start_tick,
                item.field_time.window_end_tick,
                item.frame.carrier_ids,
            )
            for item in sequence.frames
        ),
    )


def _value_inventory(sequence: ReceptorTimeSequence) -> tuple[tuple[float, ...], ...]:
    return tuple(sorted(item.frame.values for item in sequence.frames))


@dataclass(frozen=True, slots=True)
class Z4AWorldInput:
    world_id: str
    world_contract_digest: str
    source_binding_digests: tuple[tuple[str, str], ...]
    modality_ids: tuple[str, ...]
    clock_id: str
    ticks_per_second: float
    horizon_start_tick: int
    horizon_end_tick: int
    dock_anatomies: tuple[tuple[str, ReceptorDockAnatomy], ...]
    field_sample_offsets: tuple[tuple[int, ...], ...]
    arms: tuple[Z4AWorldArmInput, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.world_id, str) or not self.world_id:
            raise Z4AGenericTrajectoryRunnerError("world_id must be nonempty")
        source_bindings = tuple(self.source_binding_digests)
        modalities = tuple(self.modality_ids)
        anatomies = tuple(self.dock_anatomies)
        offsets = tuple(tuple(item) for item in self.field_sample_offsets)
        arms = tuple(self.arms)
        if not source_bindings or any(
            not isinstance(name, str) or not name or not _is_digest(digest)
            for name, digest in source_bindings
        ):
            raise Z4AGenericTrajectoryRunnerError("source bindings are invalid")
        if not modalities or len(set(modalities)) != len(modalities):
            raise Z4AGenericTrajectoryRunnerError("world modalities are invalid")
        if tuple(arm.arm_id for arm in arms) != _ARM_IDS:
            raise Z4AGenericTrajectoryRunnerError("world requires six ordered arms")
        if tuple(name for name, _ in anatomies) != modalities or any(
            not isinstance(anatomy, ReceptorDockAnatomy)
            or anatomy.modality_id != name
            for name, anatomy in anatomies
        ):
            raise Z4AGenericTrajectoryRunnerError("dock anatomy binding changed")
        if not offsets:
            raise Z4AGenericTrajectoryRunnerError("field sample offsets are required")
        if (
            isinstance(self.ticks_per_second, bool)
            or not math.isfinite(float(self.ticks_per_second))
            or self.ticks_per_second <= 0.0
            or self.horizon_end_tick <= self.horizon_start_tick
        ):
            raise Z4AGenericTrajectoryRunnerError("world horizon is invalid")
        for arm in arms:
            if (
                tuple(item.modality_id for item in arm.sequences) != modalities
                or arm.proposal_steps[0].clock_id != self.clock_id
                or arm.proposal_steps[0].ticks_per_second != self.ticks_per_second
                or arm.start_tick != self.horizon_start_tick
                or arm.end_tick != self.horizon_end_tick
            ):
                raise Z4AGenericTrajectoryRunnerError("arm world binding changed")
        reference = arms[0]
        reference_structure = tuple(
            _sequence_structure(sequence) for sequence in reference.sequences
        )
        for arm in arms[1:]:
            if tuple(_sequence_structure(sequence) for sequence in arm.sequences) != reference_structure:
                raise Z4AGenericTrajectoryRunnerError(
                    "arm receptor geometry or support inventory changed"
                )
        by_id = {arm.arm_id: arm for arm in arms}
        if by_id["reproduction"].sequence_digest != reference.sequence_digest:
            raise Z4AGenericTrajectoryRunnerError("reproduction digest changed")
        if (
            by_id["partitioned"].sequence_digest != reference.sequence_digest
            or by_id["partitioned"].proposal_digest == reference.proposal_digest
        ):
            raise Z4AGenericTrajectoryRunnerError("partition arm contract changed")
        reference_inventories = tuple(
            _value_inventory(sequence) for sequence in reference.sequences
        )
        for arm_id in ("reversed", "permuted"):
            arm = by_id[arm_id]
            if arm.sequence_digest == reference.sequence_digest or tuple(
                _value_inventory(sequence) for sequence in arm.sequences
            ) != reference_inventories:
                raise Z4AGenericTrajectoryRunnerError(
                    f"{arm_id} value inventory changed"
                )
        if by_id["independent"].sequence_digest == reference.sequence_digest:
            raise Z4AGenericTrajectoryRunnerError("independent control is not distinct")
        expected_world_digest = z4a_world_contract_digest(
            self.world_id,
            source_bindings,
            modalities,
            self.clock_id,
            float(self.ticks_per_second),
            self.horizon_start_tick,
            self.horizon_end_tick,
            anatomies,
            offsets,
            arms,
        )
        if self.world_contract_digest != expected_world_digest:
            raise Z4AGenericTrajectoryRunnerError("world contract digest changed")
        object.__setattr__(self, "source_binding_digests", source_bindings)
        object.__setattr__(self, "modality_ids", modalities)
        object.__setattr__(self, "dock_anatomies", anatomies)
        object.__setattr__(self, "field_sample_offsets", offsets)
        object.__setattr__(self, "arms", arms)

    def arm(self, arm_id: str) -> Z4AWorldArmInput:
        for arm in self.arms:
            if arm.arm_id == arm_id:
                return arm
        raise KeyError(arm_id)


def build_z4a_world_input(
    world_id: str,
    source_binding_digests: tuple[tuple[str, str], ...],
    modality_ids: tuple[str, ...],
    clock_id: str,
    ticks_per_second: float,
    horizon_start_tick: int,
    horizon_end_tick: int,
    dock_anatomies: tuple[tuple[str, ReceptorDockAnatomy], ...],
    field_sample_offsets: tuple[tuple[int, ...], ...],
    arms: tuple[Z4AWorldArmInput, ...],
) -> Z4AWorldInput:
    digest = z4a_world_contract_digest(
        world_id,
        source_binding_digests,
        modality_ids,
        clock_id,
        ticks_per_second,
        horizon_start_tick,
        horizon_end_tick,
        dock_anatomies,
        field_sample_offsets,
        arms,
    )
    return Z4AWorldInput(
        world_id,
        digest,
        source_binding_digests,
        modality_ids,
        clock_id,
        ticks_per_second,
        horizon_start_tick,
        horizon_end_tick,
        dock_anatomies,
        field_sample_offsets,
        arms,
    )


@dataclass(frozen=True, slots=True)
class Z4AExecutionTask:
    model_id: str
    arm_id: str
    refinement: int | None

    def __post_init__(self) -> None:
        if self.model_id not in _MODEL_IDS or self.arm_id not in _ARM_IDS:
            raise Z4AGenericTrajectoryRunnerError("unknown Z4-A3 task")
        if self.model_id == "p0.exact":
            if self.refinement is not None:
                raise Z4AGenericTrajectoryRunnerError("P0 refinement must be exact")
        elif self.refinement not in _REFINEMENTS:
            raise Z4AGenericTrajectoryRunnerError("unknown Z4-A3 refinement")

    @property
    def task_key(self) -> tuple[str, str, int | None]:
        return self.model_id, self.arm_id, self.refinement


def _execution_tasks() -> tuple[Z4AExecutionTask, ...]:
    result = []
    for model_id in _MODEL_IDS:
        for arm_id in _ARM_IDS:
            refinements = (None,) if model_id == "p0.exact" else _REFINEMENTS
            result.extend(
                Z4AExecutionTask(model_id, arm_id, refinement)
                for refinement in refinements
            )
    return tuple(result)


@dataclass(frozen=True, slots=True)
class Z4AExecutionPlan:
    runner_contract_id: str
    world: Z4AWorldInput
    base_field: SharedMCMField
    base_layer_digest: str
    handoffs: tuple[tuple[str, ReceptorProposalHandoff], ...]
    tasks: tuple[Z4AExecutionTask, ...]

    def __post_init__(self) -> None:
        if self.runner_contract_id != "z4a.generic-field-trajectory-runner.v1":
            raise Z4AGenericTrajectoryRunnerError("runner identity changed")
        if not isinstance(self.world, Z4AWorldInput):
            raise Z4AGenericTrajectoryRunnerError("plan requires one world")
        if not isinstance(self.base_field, SharedMCMField) or self.base_field.substrate is not None:
            raise Z4AGenericTrajectoryRunnerError("plan requires a neutral base field")
        if self.base_layer_digest != self.base_field.layer.digest():
            raise Z4AGenericTrajectoryRunnerError("base layer digest changed")
        if tuple(name for name, _ in self.handoffs) != _ARM_IDS or any(
            not isinstance(handoff, ReceptorProposalHandoff)
            for _, handoff in self.handoffs
        ):
            raise Z4AGenericTrajectoryRunnerError("plan handoff inventory changed")
        if self.tasks != _execution_tasks():
            raise Z4AGenericTrajectoryRunnerError("42-task inventory changed")

    def handoff_for(self, arm_id: str) -> ReceptorProposalHandoff:
        for current_id, handoff in self.handoffs:
            if current_id == arm_id:
                return handoff
        raise KeyError(arm_id)


def prepare_z4a_execution(world: Z4AWorldInput) -> Z4AExecutionPlan:
    if not isinstance(world, Z4AWorldInput):
        raise Z4AGenericTrajectoryRunnerError("execution requires one bound world")
    reference_frames = tuple(
        sequence.frames[0].frame for sequence in world.arm("reference").sequences
    )
    try:
        base_field = build_shared_mcm_field(
            reference_frames,
            dict(world.dock_anatomies),
            sample_offsets=world.field_sample_offsets,
        )
        handoffs = tuple(
            (
                arm.arm_id,
                handoff_receptor_completion_groups(
                    arm.sequences,
                    arm.proposal_steps,
                ),
            )
            for arm in world.arms
        )
    except ValueError as exc:
        raise Z4AGenericTrajectoryRunnerError(str(exc)) from exc
    for arm_id, handoff in handoffs:
        arm = world.arm(arm_id)
        event_count = sum(len(sequence.frames) for sequence in arm.sequences)
        if (
            handoff.completed_before_or_at_start_snapshot_ids
            or handoff.completed_after_horizon_snapshot_ids
            or not handoff.every_in_horizon_event_assigned_once
            or handoff.assigned_event_count != event_count
        ):
            raise Z4AGenericTrajectoryRunnerError("world handoff is incomplete")
    return Z4AExecutionPlan(
        "z4a.generic-field-trajectory-runner.v1",
        world,
        base_field,
        base_field.layer.digest(),
        handoffs,
        _execution_tasks(),
    )


@dataclass(frozen=True, slots=True)
class Z4ATaskTrajectory:
    model_id: str
    arm_id: str
    refinement: int | None
    support: Z4ATrajectorySupport
    final_snapshot_digest: str
    observer_neutral: bool
    integration_method: str
    diagnostic_count: int
    substep_count: int
    runtime_seconds: float
    maximum_step_seconds: float
    maximum_mass_error: float | None
    minimum_auxiliary_state: float | None
    initial_auxiliary_total: float | None
    final_auxiliary_total: float | None
    maximum_abs_activation: float
    maximum_abs_afterimage: float
    dynamic_scalar_state_budget: int

    def __post_init__(self) -> None:
        task = Z4AExecutionTask(self.model_id, self.arm_id, self.refinement)
        if not isinstance(self.support, Z4ATrajectorySupport):
            raise Z4AGenericTrajectoryRunnerError("task requires trajectory support")
        if self.support.technical_trajectory.model_id != task.model_id:
            raise Z4AGenericTrajectoryRunnerError("task trajectory model changed")
        if not _is_digest(self.final_snapshot_digest) or not isinstance(
            self.observer_neutral, bool
        ):
            raise Z4AGenericTrajectoryRunnerError("task final control is invalid")
        expected_method = "p0.exact" if self.model_id == "p0.exact" else "ssprk33"
        if self.integration_method != expected_method:
            raise Z4AGenericTrajectoryRunnerError("task integration method changed")
        if (
            isinstance(self.diagnostic_count, bool)
            or not isinstance(self.diagnostic_count, int)
            or self.diagnostic_count < 1
        ):
            raise Z4AGenericTrajectoryRunnerError("task diagnostics are missing")
        if (
            isinstance(self.substep_count, bool)
            or not isinstance(self.substep_count, int)
            or self.substep_count < 0
        ):
            raise Z4AGenericTrajectoryRunnerError("task substep count is invalid")
        for value in (self.runtime_seconds, self.maximum_step_seconds):
            if not math.isfinite(float(value)) or value < 0.0:
                raise Z4AGenericTrajectoryRunnerError("task runtime diagnostic is invalid")
        for value in (self.maximum_abs_activation, self.maximum_abs_afterimage):
            if not math.isfinite(float(value)) or value < 0.0:
                raise Z4AGenericTrajectoryRunnerError("task field bound is invalid")
        expected_budget = (
            2 if self.model_id == "p0.exact" else 3
        ) * self.support.technical_trajectory.field_node_count
        if self.dynamic_scalar_state_budget != expected_budget:
            raise Z4AGenericTrajectoryRunnerError("task state budget changed")
        auxiliary = (
            self.maximum_mass_error,
            self.minimum_auxiliary_state,
            self.initial_auxiliary_total,
            self.final_auxiliary_total,
        )
        if self.model_id == "p0.exact":
            if any(value is not None for value in auxiliary):
                raise Z4AGenericTrajectoryRunnerError("P0 gained an auxiliary state")
        elif any(
            value is None or not math.isfinite(float(value)) for value in auxiliary
        ):
            raise Z4AGenericTrajectoryRunnerError("coupled task diagnostics are invalid")

    @property
    def task_key(self) -> tuple[str, str, int | None]:
        return self.model_id, self.arm_id, self.refinement


def _field_vectors(field: SharedMCMField) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.asarray([item.activation for item in field.layer.neurons], dtype=np.float64),
        np.asarray([item.afterimage for item in field.layer.neurons], dtype=np.float64),
    )


def _run_task_once(
    plan: Z4AExecutionPlan,
    task: Z4AExecutionTask,
    handoff: ReceptorProposalHandoff,
    *,
    observe: bool,
) -> tuple[SharedMCMField, Z4AComponentTrajectory | None, tuple[MCMF3AdvanceDiagnostics, ...]]:
    arm = plan.world.arm(task.arm_id)
    substrate_config = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage_config = NeutralFastAfterimageConfig(0.5)
    if task.model_id == "p0.exact":
        field = plan.base_field
        activation, afterimage = _field_vectors(field)
        observer = (
            Z4ATrajectoryObserver(
                task.model_id,
                arm.start_tick,
                (("activation", activation), ("afterimage", afterimage)),
            )
            if observe
            else None
        )

        def p0_callback(tick, current_activation, current_afterimage):
            if observer is not None:
                observer(
                    tick,
                    (
                        ("activation", current_activation),
                        ("afterimage", current_afterimage),
                    ),
                )

        for batch in handoff.batches:
            dock_trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
            inputs = project_transient_docks_to_neuron_inputs(dock_trajectory, field.docks)
            field = advance_neutral_fast_shared_field_transient(
                field,
                ReceptorDistribution(
                    CommonFieldTime(
                        batch.step_time.clock_id,
                        batch.step_time.start_tick,
                        batch.step_time.end_tick,
                    ),
                    (),
                ),
                inputs,
                substrate_config,
                afterimage_config,
                _state_observer=p0_callback if observe else None,
            )
        return field, None if observer is None else observer.trajectory(), ()

    calculator = (
        compute_mcm_f3_coupling
        if task.model_id == "f3.candidate"
        else compute_mcm_f3_linear_coupled_baseline
    )
    field = activate_mcm_f3_field(
        plan.base_field,
        mcm_f3_history_preregistration().active_arm,
    )
    activation, afterimage = _field_vectors(field)
    auxiliary = np.asarray(
        [item.mass for item in field.substrate.masses],
        dtype=np.float64,
    )
    auxiliary_id = (
        "mcm_mass" if task.model_id == "f3.candidate" else "baseline_state"
    )
    observer = (
        Z4ATrajectoryObserver(
            task.model_id,
            arm.start_tick,
            (
                ("activation", activation),
                ("afterimage", afterimage),
                (auxiliary_id, auxiliary),
            ),
        )
        if observe
        else None
    )

    def coupled_callback(tick, current_activation, current_afterimage, current_auxiliary):
        if observer is not None:
            observer(
                tick,
                (
                    ("activation", current_activation),
                    ("afterimage", current_afterimage),
                    (auxiliary_id, current_auxiliary),
                ),
            )

    diagnostics = []
    for batch in handoff.batches:
        dock_trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
        inputs = project_transient_docks_to_neuron_inputs(dock_trajectory, field.docks)
        result = advance_mcm_f3_shared_field_transient(
            field,
            ReceptorDistribution(
                CommonFieldTime(
                    batch.step_time.clock_id,
                    batch.step_time.start_tick,
                    batch.step_time.end_tick,
                ),
                (),
            ),
            inputs,
            substrate_config,
            afterimage_config,
            refinement=task.refinement,
            _coupling_calculator=calculator,
            _state_observer=coupled_callback if observe else None,
        )
        field = result.field
        diagnostics.append(result.diagnostics)
    return field, None if observer is None else observer.trajectory(), tuple(diagnostics)


def _execute_task(
    plan: Z4AExecutionPlan,
    task: Z4AExecutionTask,
    handoff: ReceptorProposalHandoff,
) -> Z4ATaskTrajectory:
    started = time.perf_counter()
    observed_field, trajectory, diagnostics = _run_task_once(
        plan,
        task,
        handoff,
        observe=True,
    )
    unobserved_field, _, _ = _run_task_once(
        plan,
        task,
        handoff,
        observe=False,
    )
    if trajectory is None:
        raise Z4AGenericTrajectoryRunnerError("observed task lost its trajectory")
    support = build_z4a_trajectory_support(trajectory, handoff)
    activation, afterimage = _field_vectors(observed_field)
    if task.model_id == "p0.exact":
        auxiliary_values = (None, None, None, None)
        diagnostic_count = len(handoff.batches)
        integration_method = "p0.exact"
        substep_count = 0
        maximum_step_seconds = 0.0
    else:
        if observed_field.substrate is None:
            raise Z4AGenericTrajectoryRunnerError("coupled task lost auxiliary state")
        final_auxiliary = tuple(item.mass for item in observed_field.substrate.masses)
        initial_total = observed_field.substrate.arm.initial_total_mass
        auxiliary_values = (
            max(item.maximum_mass_error for item in diagnostics),
            min(item.minimum_mass for item in diagnostics),
            initial_total,
            math.fsum(final_auxiliary),
        )
        diagnostic_count = len(diagnostics)
        integration_method = "ssprk33"
        substep_count = sum(item.substep_count for item in diagnostics)
        maximum_step_seconds = max(item.maximum_step_seconds for item in diagnostics)
    runtime_seconds = time.perf_counter() - started
    return Z4ATaskTrajectory(
        task.model_id,
        task.arm_id,
        task.refinement,
        support,
        observed_field.snapshot().digest(),
        observed_field.snapshot().digest() == unobserved_field.snapshot().digest(),
        integration_method,
        diagnostic_count,
        substep_count,
        runtime_seconds,
        maximum_step_seconds,
        *auxiliary_values,
        float(np.max(np.abs(activation))),
        float(np.max(np.abs(afterimage))),
        (2 if task.model_id == "p0.exact" else 3) * len(activation),
    )


def _final_vector(result: Z4ATaskTrajectory) -> np.ndarray:
    sample = result.support.decision_trajectory.samples[-1]
    return np.concatenate(
        [np.asarray(values, dtype=np.float64) for _, values in sample.components]
    )


def _refinement_converges(results: tuple[Z4ATaskTrajectory, ...]) -> bool:
    indexed = {result.task_key: result for result in results}
    for model_id in ("f3.candidate", "b3.linear-coupled"):
        for arm_id in _ARM_IDS:
            n = _final_vector(indexed[(model_id, arm_id, 1)])
            two_n = _final_vector(indexed[(model_id, arm_id, 2)])
            four_n = _final_vector(indexed[(model_id, arm_id, 4)])
            if float(np.linalg.norm(two_n - four_n)) > float(
                np.linalg.norm(n - two_n)
            ) + 1e-15:
                return False
    return True


def _trajectory_state_invariants(result: Z4ATaskTrajectory) -> bool:
    for sample in result.support.technical_trajectory.samples:
        components = dict(sample.components)
        for component_id in ("activation", "afterimage"):
            values = components[component_id]
            if any(value < -1.0 - 1e-12 or value > 1.0 + 1e-12 for value in values):
                return False
        auxiliary_id = (
            "mcm_mass"
            if result.model_id == "f3.candidate"
            else "baseline_state"
            if result.model_id == "b3.linear-coupled"
            else None
        )
        if auxiliary_id is not None:
            auxiliary = components[auxiliary_id]
            if any(value < 0.0 for value in auxiliary):
                return False
            if result.initial_auxiliary_total is None or abs(
                math.fsum(auxiliary) - result.initial_auxiliary_total
            ) > _MASS_TOLERANCE:
                return False
    return True


@dataclass(frozen=True, slots=True)
class Z4ATechnicalPacket:
    technical_packet_id: str
    runner_contract_id: str
    world_id: str
    world_contract_digest: str
    source_binding_digests: tuple[tuple[str, str], ...]
    sequence_digests: tuple[tuple[str, str], ...]
    proposal_digests: tuple[tuple[str, str], ...]
    execution_digests: tuple[tuple[str, str], ...]
    base_layer_digest: str
    dock_map_digest: str
    source_event_count: int
    completion_group_count: int
    task_inventory: tuple[Z4AExecutionTask, ...]
    trajectories: tuple[Z4ATaskTrajectory, ...]
    controls: tuple[tuple[str, bool], ...]
    research_decision: None = None
    run_id: None = None

    def __post_init__(self) -> None:
        if self.technical_packet_id != "z4a.technical-packet.v1":
            raise Z4AGenericTrajectoryRunnerError("technical packet identity changed")
        if self.runner_contract_id != "z4a.generic-field-trajectory-runner.v1":
            raise Z4AGenericTrajectoryRunnerError("packet runner identity changed")
        if not isinstance(self.world_id, str) or not self.world_id:
            raise Z4AGenericTrajectoryRunnerError("packet world identity changed")
        if not _is_digest(self.world_contract_digest) or not _is_digest(
            self.base_layer_digest
        ) or not _is_digest(self.dock_map_digest):
            raise Z4AGenericTrajectoryRunnerError("packet binding digest changed")
        for role in (
            "source_binding_digests",
            "sequence_digests",
            "proposal_digests",
            "execution_digests",
        ):
            pairs = tuple(getattr(self, role))
            if not pairs or any(
                not isinstance(name, str) or not name or not _is_digest(digest)
                for name, digest in pairs
            ):
                raise Z4AGenericTrajectoryRunnerError(f"packet {role} changed")
            object.__setattr__(self, role, pairs)
        if tuple(name for name, _ in self.sequence_digests) != _ARM_IDS or tuple(
            name for name, _ in self.proposal_digests
        ) != _ARM_IDS or tuple(name for name, _ in self.execution_digests) != _ARM_IDS:
            raise Z4AGenericTrajectoryRunnerError("packet arm digest order changed")
        for role in ("source_event_count", "completion_group_count"):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise Z4AGenericTrajectoryRunnerError(f"packet {role} changed")
        if self.task_inventory != _execution_tasks():
            raise Z4AGenericTrajectoryRunnerError("packet task inventory changed")
        trajectories = tuple(self.trajectories)
        if len(trajectories) != 42 or tuple(
            item.task_key for item in trajectories
        ) != tuple(task.task_key for task in self.task_inventory):
            raise Z4AGenericTrajectoryRunnerError("packet requires 42 ordered results")
        if tuple(name for name, _ in self.controls) != (
            "handoffs_complete",
            "shared_handoff_per_arm",
            "observer_neutral",
            "state_invariants_hold",
            "decision_support_equal",
            "refinement_converges",
        ):
            raise Z4AGenericTrajectoryRunnerError("packet control inventory changed")
        if self.research_decision is not None or self.run_id is not None:
            raise Z4AGenericTrajectoryRunnerError(
                "technical packet cannot contain a research decision or run id"
            )
        object.__setattr__(self, "trajectories", trajectories)


_TaskExecutor = Callable[
    [Z4AExecutionPlan, Z4AExecutionTask, ReceptorProposalHandoff],
    Z4ATaskTrajectory,
]


def _execute_z4a_technical_packet(
    plan: Z4AExecutionPlan,
    executor: _TaskExecutor,
) -> Z4ATechnicalPacket:
    if not isinstance(plan, Z4AExecutionPlan) or not callable(executor):
        raise Z4AGenericTrajectoryRunnerError("technical execution is invalid")
    handoff_ids_by_arm = {
        arm_id: id(handoff) for arm_id, handoff in plan.handoffs
    }
    passed_handoff_ids: dict[str, set[int]] = {arm_id: set() for arm_id in _ARM_IDS}
    results = []
    for task in plan.tasks:
        handoff = plan.handoff_for(task.arm_id)
        passed_handoff_ids[task.arm_id].add(id(handoff))
        results.append(executor(plan, task, handoff))
    trajectories = tuple(results)
    state_invariants = all(
        _trajectory_state_invariants(result)
        and result.maximum_abs_activation <= 1.0 + 1e-12
        and result.maximum_abs_afterimage <= 1.0 + 1e-12
        and (
            result.model_id == "p0.exact"
            or (
                result.maximum_mass_error is not None
                and result.maximum_mass_error <= _MASS_TOLERANCE
                and result.minimum_auxiliary_state is not None
                and result.minimum_auxiliary_state >= 0.0
                and result.initial_auxiliary_total is not None
                and result.final_auxiliary_total is not None
                and abs(
                    result.initial_auxiliary_total - result.final_auxiliary_total
                )
                <= _MASS_TOLERANCE
            )
        )
        for result in trajectories
    )
    controls = (
        ("handoffs_complete", True),
        (
            "shared_handoff_per_arm",
            all(
                passed_handoff_ids[arm_id] == {handoff_ids_by_arm[arm_id]}
                for arm_id in _ARM_IDS
            ),
        ),
        ("observer_neutral", all(result.observer_neutral for result in trajectories)),
        ("state_invariants_hold", state_invariants),
        (
            "decision_support_equal",
            len(
                {
                    result.support.required_ticks
                    for result in trajectories
                }
            )
            == 1,
        ),
        ("refinement_converges", _refinement_converges(trajectories)),
    )
    dock_map_digest = _digest(
        [
            {
                "dock_id": dock.dock_id,
                "modality_id": dock.dock_map.modality_id,
                "geometry_id": dock.dock_map.receptor_geometry_id,
                "pairs": dock.dock_map.pairs,
            }
            for dock in plan.base_field.docks
        ]
    )
    reference_arm = plan.world.arm("reference")
    reference_handoff = plan.handoff_for("reference")
    return Z4ATechnicalPacket(
        "z4a.technical-packet.v1",
        plan.runner_contract_id,
        plan.world.world_id,
        plan.world.world_contract_digest,
        plan.world.source_binding_digests,
        tuple((arm.arm_id, arm.sequence_digest) for arm in plan.world.arms),
        tuple((arm.arm_id, arm.proposal_digest) for arm in plan.world.arms),
        tuple((arm.arm_id, arm.execution_digest) for arm in plan.world.arms),
        plan.base_layer_digest,
        dock_map_digest,
        sum(len(sequence.frames) for sequence in reference_arm.sequences),
        sum(len(batch.completion_groups) for batch in reference_handoff.batches),
        plan.tasks,
        trajectories,
        controls,
    )


def execute_z4a_technical_packet(world: Z4AWorldInput) -> Z4ATechnicalPacket:
    """Execute exactly 42 technical tasks without a research decision."""

    return _execute_z4a_technical_packet(
        prepare_z4a_execution(world),
        _execute_task,
    )


def z4a_generic_trajectory_runner_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            Z4AWorldArmInput,
            Z4AWorldInput,
            Z4AExecutionTask,
            Z4AExecutionPlan,
            Z4ATaskTrajectory,
            Z4ATechnicalPacket,
        )
        for item in fields(contract)
    )
