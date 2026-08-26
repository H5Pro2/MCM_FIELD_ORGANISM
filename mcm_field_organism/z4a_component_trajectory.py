"""Role-variable passive trajectories and completion support for Z4-A3."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

import numpy as np

from .receptor_proposal_handoff_audit import ReceptorProposalHandoff


class Z4AComponentTrajectoryError(ValueError):
    """Raised when a Z4-A trajectory leaves its fixed technical contract."""


_MODEL_COMPONENTS = {
    "p0.exact": ("activation", "afterimage"),
    "f3.candidate": ("activation", "afterimage", "mcm_mass"),
    "b3.linear-coupled": ("activation", "afterimage", "baseline_state"),
}
_COMPONENT_INVENTORIES = frozenset(_MODEL_COMPONENTS.values())


def _validated_tick(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Z4AComponentTrajectoryError("trajectory tick must be nonnegative")
    return value


def _validated_components(
    components: Iterable[tuple[str, Iterable[float]]],
) -> tuple[tuple[str, tuple[float, ...]], ...]:
    result = []
    for item in tuple(components):
        if not isinstance(item, tuple) or len(item) != 2:
            raise Z4AComponentTrajectoryError(
                "each component must be one (component_id, values) tuple"
            )
        component_id, values = item
        if not isinstance(component_id, str) or not component_id:
            raise Z4AComponentTrajectoryError("component_id must be nonempty")
        array = np.asarray(values, dtype=np.float64)
        if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
            raise Z4AComponentTrajectoryError(
                f"{component_id} must be one finite nonempty vector"
            )
        result.append((component_id, tuple(float(value) for value in array)))
    validated = tuple(result)
    component_ids = tuple(component_id for component_id, _ in validated)
    if component_ids not in _COMPONENT_INVENTORIES:
        raise Z4AComponentTrajectoryError(
            "component inventory or ordering is outside the Z4-A3 contract"
        )
    if len({len(values) for _, values in validated}) != 1:
        raise Z4AComponentTrajectoryError(
            "all trajectory components must share one field geometry"
        )
    return validated


@dataclass(frozen=True, slots=True)
class Z4ATrajectorySample:
    tick: int
    components: tuple[tuple[str, tuple[float, ...]], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "tick", _validated_tick(self.tick))
        object.__setattr__(
            self,
            "components",
            _validated_components(self.components),
        )

    @property
    def component_ids(self) -> tuple[str, ...]:
        return tuple(component_id for component_id, _ in self.components)

    def values_for(self, component_id: str) -> tuple[float, ...]:
        for current_id, values in self.components:
            if current_id == component_id:
                return values
        raise KeyError(component_id)


@dataclass(frozen=True, slots=True)
class Z4AComponentTrajectory:
    model_id: str
    samples: tuple[Z4ATrajectorySample, ...]

    def __post_init__(self) -> None:
        if self.model_id not in _MODEL_COMPONENTS:
            raise Z4AComponentTrajectoryError("unknown Z4-A3 model_id")
        samples = tuple(self.samples)
        if len(samples) < 2 or any(
            not isinstance(sample, Z4ATrajectorySample) for sample in samples
        ):
            raise Z4AComponentTrajectoryError(
                "trajectory requires at least two valid samples"
            )
        if any(
            later.tick <= earlier.tick
            for earlier, later in zip(samples, samples[1:])
        ):
            raise Z4AComponentTrajectoryError(
                "trajectory ticks must increase strictly"
            )
        expected_components = _MODEL_COMPONENTS[self.model_id]
        if any(sample.component_ids != expected_components for sample in samples):
            raise Z4AComponentTrajectoryError(
                "trajectory components do not match model_id"
            )
        dimensions = {
            len(values)
            for sample in samples
            for _, values in sample.components
        }
        if len(dimensions) != 1:
            raise Z4AComponentTrajectoryError("trajectory geometry changed")
        object.__setattr__(self, "samples", samples)

    @property
    def component_ids(self) -> tuple[str, ...]:
        return _MODEL_COMPONENTS[self.model_id]

    @property
    def field_node_count(self) -> int:
        return len(self.samples[0].components[0][1])


class Z4ATrajectoryObserver:
    """Append-only observer that copies runtime arrays without writeback."""

    def __init__(
        self,
        model_id: str,
        initial_tick: int,
        components: Iterable[tuple[str, Iterable[float]]],
    ) -> None:
        if model_id not in _MODEL_COMPONENTS:
            raise Z4AComponentTrajectoryError("unknown Z4-A3 model_id")
        initial = Z4ATrajectorySample(initial_tick, tuple(components))
        if initial.component_ids != _MODEL_COMPONENTS[model_id]:
            raise Z4AComponentTrajectoryError(
                "observer components do not match model_id"
            )
        self._model_id = model_id
        self._samples = [initial]

    def __call__(
        self,
        tick: int,
        components: Iterable[tuple[str, Iterable[float]]],
    ) -> None:
        sample = Z4ATrajectorySample(tick, tuple(components))
        if sample.component_ids != _MODEL_COMPONENTS[self._model_id]:
            raise Z4AComponentTrajectoryError(
                "observer components do not match model_id"
            )
        if sample.tick <= self._samples[-1].tick:
            raise Z4AComponentTrajectoryError(
                "observer received a non-increasing tick"
            )
        if len(sample.components[0][1]) != len(self._samples[0].components[0][1]):
            raise Z4AComponentTrajectoryError("observer geometry changed")
        self._samples.append(sample)

    def trajectory(self) -> Z4AComponentTrajectory:
        return Z4AComponentTrajectory(self._model_id, tuple(self._samples))


def z4a_completion_ticks_from_handoff(
    handoff: ReceptorProposalHandoff,
) -> tuple[int, ...]:
    """Return neutral start plus real completion ticks from one handoff."""

    if not isinstance(handoff, ReceptorProposalHandoff) or not handoff.batches:
        raise Z4AComponentTrajectoryError(
            "completion support requires one nonempty receptor handoff"
        )
    if (
        not handoff.every_in_horizon_event_assigned_once
        or handoff.source_event_count < 1
        or handoff.assigned_event_count != handoff.source_event_count
        or handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
    ):
        raise Z4AComponentTrajectoryError(
            "completion support requires a complete validated handoff"
        )
    first_step = handoff.batches[0].step_time
    previous_end = first_step.start_tick
    completion_ticks = []
    for batch_index, batch in enumerate(handoff.batches):
        step = batch.step_time
        if (
            batch.batch_index != batch_index
            or step.clock_id != handoff.clock_id
            or step.start_tick != previous_end
        ):
            raise Z4AComponentTrajectoryError(
                "handoff proposal batches are not contiguous and ordered"
            )
        group_ticks = tuple(group.completion_tick for group in batch.completion_groups)
        if any(
            tick <= step.start_tick or tick > step.end_tick for tick in group_ticks
        ) or any(
            later <= earlier
            for earlier, later in zip(group_ticks, group_ticks[1:])
        ):
            raise Z4AComponentTrajectoryError(
                "handoff completion groups are outside their proposal span"
            )
        completion_ticks.extend(group_ticks)
        previous_end = step.end_tick
    required_ticks = (first_step.start_tick, *completion_ticks)
    if len(required_ticks) < 2 or any(
        later <= earlier
        for earlier, later in zip(required_ticks, required_ticks[1:])
    ):
        raise Z4AComponentTrajectoryError(
            "completion support must increase strictly"
        )
    return required_ticks


def select_z4a_completion_support(
    trajectory: Z4AComponentTrajectory,
    required_ticks: Iterable[int],
) -> Z4AComponentTrajectory:
    """Select exact completion samples without interpolation or value tests."""

    if not isinstance(trajectory, Z4AComponentTrajectory):
        raise Z4AComponentTrajectoryError(
            "support selection requires one Z4-A trajectory"
        )
    ticks = tuple(_validated_tick(tick) for tick in required_ticks)
    if len(ticks) < 2 or any(
        later <= earlier for earlier, later in zip(ticks, ticks[1:])
    ):
        raise Z4AComponentTrajectoryError(
            "required support ticks must increase strictly"
        )
    by_tick = {sample.tick: sample for sample in trajectory.samples}
    missing = tuple(tick for tick in ticks if tick not in by_tick)
    if missing:
        raise Z4AComponentTrajectoryError(
            f"trajectory lacks required completion ticks: {missing[:3]}"
        )
    return Z4AComponentTrajectory(
        trajectory.model_id,
        tuple(by_tick[tick] for tick in ticks),
    )


@dataclass(frozen=True, slots=True)
class Z4ATrajectorySupport:
    support_id: str
    required_ticks: tuple[int, ...]
    technical_trajectory: Z4AComponentTrajectory
    decision_trajectory: Z4AComponentTrajectory

    def __post_init__(self) -> None:
        if self.support_id != "z4a.completion-support.v1":
            raise Z4AComponentTrajectoryError("Z4-A3 support identity changed")
        if (
            not isinstance(self.technical_trajectory, Z4AComponentTrajectory)
            or not isinstance(self.decision_trajectory, Z4AComponentTrajectory)
        ):
            raise Z4AComponentTrajectoryError(
                "support requires technical and decision trajectories"
            )
        if self.technical_trajectory.model_id != self.decision_trajectory.model_id:
            raise Z4AComponentTrajectoryError("support model identity changed")
        ticks = tuple(_validated_tick(tick) for tick in self.required_ticks)
        object.__setattr__(self, "required_ticks", ticks)
        if len(ticks) < 2:
            raise Z4AComponentTrajectoryError(
                "support requires a neutral start and one completion"
            )
        if self.technical_trajectory.samples[0].tick != ticks[0]:
            raise Z4AComponentTrajectoryError(
                "technical trajectory does not start at the neutral horizon"
            )
        expected = select_z4a_completion_support(
            self.technical_trajectory,
            ticks,
        )
        if expected != self.decision_trajectory:
            raise Z4AComponentTrajectoryError(
                "decision trajectory differs from exact completion support"
            )


def build_z4a_trajectory_support(
    technical_trajectory: Z4AComponentTrajectory,
    handoff: ReceptorProposalHandoff,
) -> Z4ATrajectorySupport:
    required_ticks = z4a_completion_ticks_from_handoff(handoff)
    decision_trajectory = select_z4a_completion_support(
        technical_trajectory,
        required_ticks,
    )
    return Z4ATrajectorySupport(
        "z4a.completion-support.v1",
        required_ticks,
        technical_trajectory,
        decision_trajectory,
    )


def z4a_component_trajectory_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            Z4ATrajectorySample,
            Z4AComponentTrajectory,
            Z4ATrajectorySupport,
        )
        for item in fields(contract)
    )
