from __future__ import annotations

import unittest

from mcm_field_organism import (
    BaselineValidationError,
    run_spatial_afterimage_orientation_probe,
)


class SpatialAfterimageOrientationProbeTests(unittest.TestCase):
    def test_endpoint_matches_current_and_center_local_scalar_state(self) -> None:
        result = run_spatial_afterimage_orientation_probe()
        self.assertEqual(
            result.forward_endpoint.activation,
            result.reverse_endpoint.activation,
        )
        self.assertEqual(
            result.forward_endpoint.center_activation,
            result.reverse_endpoint.center_activation,
        )
        self.assertEqual(
            result.forward_endpoint.center_afterimage,
            result.reverse_endpoint.center_afterimage,
        )

    def test_spatial_afterimage_distinguishes_mirrored_trajectory_orientation(self) -> None:
        result = run_spatial_afterimage_orientation_probe()
        self.assertNotEqual(
            result.forward_endpoint.afterimage,
            result.reverse_endpoint.afterimage,
        )
        self.assertLess(result.forward_endpoint.spatial_orientation, 0.0)
        self.assertGreater(result.reverse_endpoint.spatial_orientation, 0.0)
        self.assertAlmostEqual(
            result.forward_endpoint.spatial_orientation,
            -result.reverse_endpoint.spatial_orientation,
        )

    def test_complete_states_are_exact_spatial_mirrors(self) -> None:
        result = run_spatial_afterimage_orientation_probe()
        self.assertEqual(
            result.forward_endpoint.afterimage,
            tuple(reversed(result.reverse_endpoint.afterimage)),
        )
        self.assertEqual(
            result.forward_contacts,
            tuple(tuple(reversed(frame)) for frame in result.reverse_contacts),
        )

    def test_passive_pause_reduces_but_does_not_invent_orientation(self) -> None:
        result = run_spatial_afterimage_orientation_probe(pause_steps=3)
        self.assertLess(
            abs(result.forward_relaxed.spatial_orientation),
            abs(result.forward_endpoint.spatial_orientation),
        )
        self.assertAlmostEqual(
            result.forward_relaxed.spatial_orientation,
            -result.reverse_relaxed.spatial_orientation,
        )

    def test_exact_reset_removes_every_orientation_difference(self) -> None:
        result = run_spatial_afterimage_orientation_probe()
        self.assertEqual((0.0,) * result.width, result.reset.activation)
        self.assertEqual((0.0,) * result.width, result.reset.afterimage)
        self.assertEqual(0.0, result.reset.spatial_orientation)

    def test_result_carries_across_parameter_family_without_sign_change(self) -> None:
        for tau in (0.25, 0.5, 1.0, 2.0, 8.0):
            with self.subTest(tau=tau):
                result = run_spatial_afterimage_orientation_probe(tau=tau)
                self.assertLess(result.forward_endpoint.spatial_orientation, 0.0)
                self.assertGreater(result.reverse_endpoint.spatial_orientation, 0.0)

    def test_amplitude_scales_observation_without_changing_its_role(self) -> None:
        full = run_spatial_afterimage_orientation_probe(amplitude=1.0)
        half = run_spatial_afterimage_orientation_probe(amplitude=0.5)
        self.assertAlmostEqual(
            half.forward_endpoint.spatial_orientation,
            0.5 * full.forward_endpoint.spatial_orientation,
        )

    def test_invalid_probe_domains_are_rejected(self) -> None:
        invalid = (
            {"width": 4},
            {"width": 3},
            {"amplitude": 0.0},
            {"amplitude": 1.1},
            {"pause_steps": -1},
            {"pause_steps": True},
        )
        for parameters in invalid:
            with self.subTest(parameters=parameters):
                with self.assertRaises(BaselineValidationError):
                    run_spatial_afterimage_orientation_probe(**parameters)


if __name__ == "__main__":
    unittest.main()
