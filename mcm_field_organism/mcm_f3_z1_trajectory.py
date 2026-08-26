"""Passive trajectory capture and path metrics for the Z1 audit."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

import numpy as np


class MCMF3Z1TrajectoryError(ValueError):
    """Raised when a Z1 trajectory or metric is outside its fixed contract."""


_ROLES = ("activation", "afterimage", "mass")
_GRID_SIZE = 101


def _vector(values, role: str) -> tuple[float, ...]:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise MCMF3Z1TrajectoryError(f"{role} must be one finite nonempty vector")
    return tuple(float(value) for value in array)


@dataclass(frozen=True, slots=True)
class MCMF3Z1TrajectorySample:
    tick: int
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    mass: tuple[float, ...]

    def __post_init__(self) -> None:
        if isinstance(self.tick, bool) or not isinstance(self.tick, int) or self.tick < 0:
            raise MCMF3Z1TrajectoryError("trajectory tick must be nonnegative")
        for role in _ROLES:
            object.__setattr__(self, role, _vector(getattr(self, role), role))
        sizes = {len(getattr(self, role)) for role in _ROLES}
        if len(sizes) != 1:
            raise MCMF3Z1TrajectoryError("S, H and M vectors must share one geometry")


@dataclass(frozen=True, slots=True)
class MCMF3Z1Trajectory:
    samples: tuple[MCMF3Z1TrajectorySample, ...]

    def __post_init__(self) -> None:
        samples = tuple(self.samples)
        if len(samples) < 2:
            raise MCMF3Z1TrajectoryError("trajectory requires at least two samples")
        if any(
            later.tick <= earlier.tick
            for earlier, later in zip(samples, samples[1:])
        ):
            raise MCMF3Z1TrajectoryError("trajectory ticks must increase strictly")
        sizes = {len(item.activation) for item in samples}
        if len(sizes) != 1:
            raise MCMF3Z1TrajectoryError("trajectory geometry changed")
        object.__setattr__(self, "samples", samples)


class MCMF3Z1TrajectoryObserver:
    """Append-only passive observer compatible with the F3 runtime callback."""

    def __init__(self, initial_tick: int, activation, afterimage, mass) -> None:
        self._samples = [
            MCMF3Z1TrajectorySample(
                initial_tick,
                activation,
                afterimage,
                mass,
            )
        ]

    def __call__(self, tick: int, activation, afterimage, mass) -> None:
        sample = MCMF3Z1TrajectorySample(tick, activation, afterimage, mass)
        if sample.tick <= self._samples[-1].tick:
            raise MCMF3Z1TrajectoryError("observer received a non-increasing tick")
        self._samples.append(sample)

    def trajectory(self) -> MCMF3Z1Trajectory:
        return MCMF3Z1Trajectory(tuple(self._samples))


@dataclass(frozen=True, slots=True)
class MCMF3Z1PathDistances:
    activation: float
    afterimage: float
    mass: float

    def __post_init__(self) -> None:
        for role in _ROLES:
            value = float(getattr(self, role))
            if not math.isfinite(value) or value < 0.0:
                raise MCMF3Z1TrajectoryError("path distances must be finite and nonnegative")
            object.__setattr__(self, role, value)


def _component(trajectory: MCMF3Z1Trajectory, role: str) -> np.ndarray:
    if not isinstance(trajectory, MCMF3Z1Trajectory):
        raise MCMF3Z1TrajectoryError("path metric requires one Z1 trajectory")
    if role not in _ROLES:
        raise MCMF3Z1TrajectoryError("unknown trajectory component")
    return np.asarray(
        [getattr(item, role) for item in trajectory.samples],
        dtype=np.float64,
    )


def normalized_component_path(
    trajectory: MCMF3Z1Trajectory,
    role: str,
    *,
    grid_size: int = _GRID_SIZE,
) -> np.ndarray:
    """Interpolate one vector trajectory over normalized cumulative path length."""

    if isinstance(grid_size, bool) or not isinstance(grid_size, int) or grid_size < 2:
        raise MCMF3Z1TrajectoryError("path grid requires at least two points")
    values = _component(trajectory, role)
    increments = np.linalg.norm(np.diff(values, axis=0), axis=1)
    cumulative = np.concatenate((np.asarray([0.0]), np.cumsum(increments)))
    total = float(cumulative[-1])
    if not math.isfinite(total) or total <= 0.0:
        raise MCMF3Z1TrajectoryError(f"{role} path has zero measurable length")
    coordinates = cumulative / total

    unique_coordinates = []
    unique_values = []
    for coordinate, vector in zip(coordinates, values, strict=True):
        if unique_coordinates and coordinate == unique_coordinates[-1]:
            unique_values[-1] = vector
        else:
            unique_coordinates.append(float(coordinate))
            unique_values.append(vector)
    support = np.asarray(unique_coordinates, dtype=np.float64)
    support_values = np.asarray(unique_values, dtype=np.float64)
    grid = np.linspace(0.0, 1.0, grid_size, dtype=np.float64)
    return np.stack(
        [np.interp(grid, support, support_values[:, index]) for index in range(values.shape[1])],
        axis=1,
    )


def component_path_distance(
    reference: MCMF3Z1Trajectory,
    compared: MCMF3Z1Trajectory,
    role: str,
    *,
    grid_size: int = _GRID_SIZE,
) -> float:
    """Return preregistered scale-relative L-infinity path distance."""

    reference_path = normalized_component_path(reference, role, grid_size=grid_size)
    compared_path = normalized_component_path(compared, role, grid_size=grid_size)
    if reference_path.shape != compared_path.shape:
        raise MCMF3Z1TrajectoryError("compared trajectory geometry differs")
    scale = float(np.max(np.abs(reference_path - reference_path[0])))
    if scale <= 0.0 or not math.isfinite(scale):
        raise MCMF3Z1TrajectoryError(f"{role} reference excursion is not measurable")
    return float(np.max(np.abs(compared_path - reference_path))) / scale


def trajectory_path_distances(
    reference: MCMF3Z1Trajectory,
    compared: MCMF3Z1Trajectory,
) -> MCMF3Z1PathDistances:
    return MCMF3Z1PathDistances(
        *(component_path_distance(reference, compared, role) for role in _ROLES)
    )


def numerical_envelope(
    two_n: MCMF3Z1Trajectory,
    four_n: MCMF3Z1Trajectory,
) -> MCMF3Z1PathDistances:
    distances = trajectory_path_distances(four_n, two_n)
    return MCMF3Z1PathDistances(
        *(max(1e-12, 4.0 * getattr(distances, role)) for role in _ROLES)
    )


def mcm_f3_z1_trajectory_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (MCMF3Z1TrajectorySample, MCMF3Z1Trajectory, MCMF3Z1PathDistances)
        for item in fields(cls)
    )
