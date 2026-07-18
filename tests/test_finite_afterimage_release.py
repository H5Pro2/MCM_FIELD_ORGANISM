from __future__ import annotations

import math
import unittest

from mcm_field_organism import (
    FiniteAfterimageReleaseConfig,
    FiniteAfterimageReleaseError,
    finite_afterimage_extinction_time,
    release_afterimage,
)


class FiniteAfterimageReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = FiniteAfterimageReleaseConfig(
            time_scale_seconds=1.0,
            release_exponent=0.5,
        )

    def test_config_requires_explicit_finite_candidate_parameters(self) -> None:
        for time_scale in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(time_scale=time_scale), self.assertRaises(
                FiniteAfterimageReleaseError
            ):
                FiniteAfterimageReleaseConfig(time_scale, 0.5)
        for exponent in (-1.0, 0.0, 1.0, math.inf, math.nan):
            with self.subTest(exponent=exponent), self.assertRaises(
                FiniteAfterimageReleaseError
            ):
                FiniteAfterimageReleaseConfig(1.0, exponent)

    def test_invalid_runtime_values_are_rejected(self) -> None:
        for value in (math.inf, math.nan):
            with self.subTest(value=value), self.assertRaises(
                FiniteAfterimageReleaseError
            ):
                release_afterimage(value, 1.0, self.config)
        for elapsed in (-1.0, math.inf, math.nan):
            with self.subTest(elapsed=elapsed), self.assertRaises(
                FiniteAfterimageReleaseError
            ):
                release_afterimage(1.0, elapsed, self.config)

    def test_release_is_sign_symmetric_and_monotone(self) -> None:
        positive = [
            release_afterimage(1.0, elapsed, self.config)
            for elapsed in (0.0, 0.5, 1.0, 1.5, 2.0)
        ]
        negative = [
            release_afterimage(-1.0, elapsed, self.config)
            for elapsed in (0.0, 0.5, 1.0, 1.5, 2.0)
        ]
        self.assertEqual(positive, sorted(positive, reverse=True))
        self.assertEqual(negative, [-value for value in positive])

    def test_release_reaches_exact_zero_at_analytic_extinction(self) -> None:
        extinction = finite_afterimage_extinction_time(1.0, self.config)
        self.assertEqual(extinction, 2.0)
        self.assertEqual(
            release_afterimage(1.0, extinction, self.config),
            0.0,
        )
        self.assertEqual(
            release_afterimage(1.0, extinction + 10.0, self.config),
            0.0,
        )

    def test_release_obeys_the_time_semigroup(self) -> None:
        direct = release_afterimage(0.81, 1.25, self.config)
        partitioned = release_afterimage(
            release_afterimage(0.81, 0.4, self.config),
            0.85,
            self.config,
        )
        self.assertAlmostEqual(direct, partitioned, places=15)

    def test_zero_elapsed_time_preserves_the_value(self) -> None:
        self.assertEqual(release_afterimage(-0.37, 0.0, self.config), -0.37)
        self.assertEqual(release_afterimage(0.0, 5.0, self.config), 0.0)

    def test_each_local_value_releases_without_order_dependence(self) -> None:
        values = (0.81, -0.25, 0.0, 1.0)
        forward = tuple(
            release_afterimage(value, 0.5, self.config) for value in values
        )
        reversed_result = tuple(
            reversed(
                tuple(
                    release_afterimage(value, 0.5, self.config)
                    for value in reversed(values)
                )
            )
        )
        self.assertEqual(forward, reversed_result)

    def test_extinction_duration_remains_amplitude_dependent(self) -> None:
        self.assertLess(
            finite_afterimage_extinction_time(0.25, self.config),
            finite_afterimage_extinction_time(1.0, self.config),
        )


if __name__ == "__main__":
    unittest.main()
