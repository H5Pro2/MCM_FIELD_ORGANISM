from __future__ import annotations

import unittest

from mcm_field_organism.geometry_amplitude_superposition_probe import (
    AMPLITUDE_SCALE_PAIRS,
    GEOMETRY_CASES,
    run_geometry_amplitude_superposition_probe,
)


class GeometryAmplitudeSuperpositionProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_geometry_amplitude_superposition_probe()

    def test_preregistered_grid_is_complete(self) -> None:
        self.assertEqual(
            len(self.result.cases),
            len(GEOMETRY_CASES) * len(AMPLITUDE_SCALE_PAIRS),
        )

    def test_each_isolated_contact_remains_measurable(self) -> None:
        self.assertTrue(self.result.all_sources_nonzero)

    def test_every_case_matches_the_preregistered_null_model(self) -> None:
        self.assertTrue(self.result.all_cases_additive)
        self.assertLessEqual(self.result.maximum_activation_error, 1e-12)
        self.assertLessEqual(self.result.maximum_afterimage_error, 1e-12)

    def test_probe_preserves_sources_and_runtime_boundary(self) -> None:
        self.assertTrue(self.result.source_states_preserved)
        self.assertFalse(self.result.observer_writeback_performed)
        self.assertFalse(self.result.runtime_changed)


if __name__ == "__main__":
    unittest.main()
