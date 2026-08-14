from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism.mcm_f3_z1_trajectory import (
    MCMF3Z1TrajectoryError,
    MCMF3Z1TrajectoryObserver,
    component_path_distance,
    normalized_component_path,
    numerical_envelope,
    trajectory_path_distances,
)


def trajectory(ticks, scale: float = 1.0):
    observer = MCMF3Z1TrajectoryObserver(
        ticks[0],
        (0.0, 0.0),
        (0.0, 0.0),
        (1.0, 0.0),
    )
    for index, tick in enumerate(ticks[1:], start=1):
        observer(
            tick,
            (scale * index, scale * 0.5 * index),
            (scale * 0.25 * index, scale * index),
            (1.0 - scale * 0.1 * index, scale * 0.1 * index),
        )
    return observer.trajectory()


class MCMF3Z1TrajectoryTests(unittest.TestCase):
    def test_observer_copies_runtime_arrays(self) -> None:
        activation = np.asarray([0.0, 0.0])
        observer = MCMF3Z1TrajectoryObserver(0, activation, (0.0, 0.0), (1.0, 0.0))
        activation[:] = 9.0
        observer(1, (1.0, 0.5), (0.25, 1.0), (0.9, 0.1))
        self.assertEqual((0.0, 0.0), observer.trajectory().samples[0].activation)

    def test_identical_geometry_with_different_ticks_has_zero_distance(self) -> None:
        reference = trajectory((0, 1, 2, 3))
        stretched = trajectory((0, 2, 4, 6))
        distances = trajectory_path_distances(reference, stretched)
        self.assertEqual(0.0, distances.activation)
        self.assertEqual(0.0, distances.afterimage)
        self.assertEqual(0.0, distances.mass)

    def test_path_metric_detects_changed_geometry(self) -> None:
        reference = trajectory((0, 1, 2, 3))
        changed = trajectory((0, 1, 2, 3), scale=0.5)
        self.assertGreater(component_path_distance(reference, changed, "activation"), 0.0)

    def test_normalized_path_ignores_stationary_duplicate_points(self) -> None:
        observer = MCMF3Z1TrajectoryObserver(0, (0.0,), (0.0,), (1.0,))
        observer(1, (0.0,), (0.0,), (1.0,))
        observer(2, (1.0,), (1.0,), (0.5,))
        path = normalized_component_path(observer.trajectory(), "activation")
        self.assertEqual((101, 1), path.shape)
        self.assertEqual(0.0, path[0, 0])
        self.assertEqual(1.0, path[-1, 0])

    def test_numerical_envelope_has_fixed_floor(self) -> None:
        same = trajectory((0, 1, 2, 3))
        envelope = numerical_envelope(same, same)
        self.assertEqual(1e-12, envelope.activation)
        self.assertEqual(1e-12, envelope.afterimage)
        self.assertEqual(1e-12, envelope.mass)

    def test_zero_length_component_is_rejected(self) -> None:
        observer = MCMF3Z1TrajectoryObserver(0, (0.0,), (0.0,), (1.0,))
        observer(1, (0.0,), (0.0,), (1.0,))
        with self.assertRaises(MCMF3Z1TrajectoryError):
            normalized_component_path(observer.trajectory(), "activation")

    def test_non_increasing_observer_tick_is_rejected(self) -> None:
        observer = MCMF3Z1TrajectoryObserver(0, (0.0,), (0.0,), (1.0,))
        with self.assertRaises(MCMF3Z1TrajectoryError):
            observer(0, (1.0,), (1.0,), (0.0,))


if __name__ == "__main__":
    unittest.main()
