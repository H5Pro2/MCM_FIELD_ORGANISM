from __future__ import annotations

import json
import unittest

from mcm_field_organism.field_contact_mass_counterbaseline import (
    FIELD_CONTACT_MASS_LOAD_DURATIONS_SECONDS,
    FIELD_CONTACT_MASS_PATTERN_IDS,
    FIELD_CONTACT_MASS_RECOVERY_DURATIONS_SECONDS,
    field_contact_mass_counterbaseline_json_value,
    field_contact_mass_counterbaseline_public_roles,
    run_field_contact_mass_counterbaseline,
)


class FieldContactMassCounterbaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_field_contact_mass_counterbaseline()

    def test_complete_matrix_has_exact_equal_contact_mass(self) -> None:
        self.assertEqual(45, self.result.observation_count)
        self.assertEqual(FIELD_CONTACT_MASS_PATTERN_IDS, self.result.pattern_ids)
        self.assertEqual(1.0, self.result.total_contact_mass)
        for item in self.result.observations:
            self.assertAlmostEqual(1.0, item.total_contact_mass, places=15)
            self.assertEqual(
                1.0 / item.active_contact_count,
                item.per_contact_amplitude,
            )
            self.assertEqual(26, item.field_neuron_count)

    def test_equal_mass_preserves_l1_but_changes_local_peak(self) -> None:
        loads = self._long_loads()
        l1_values = tuple(item.load_activation_l1 for item in loads.values())
        self.assertLess(max(l1_values) - min(l1_values), 3e-15)
        self.assertEqual(
            "local_auditory_mass1",
            self.result.long_load_highest_pattern_id,
        )
        self.assertAlmostEqual(
            0.35727128118469537,
            self.result.long_load_highest_linf,
            places=15,
        )
        self.assertEqual(
            "av_distributed_mass1",
            self.result.long_load_lowest_pattern_id,
        )
        self.assertAlmostEqual(
            0.037757090811971726,
            self.result.long_load_lowest_linf,
            places=15,
        )
        self.assertEqual(
            "EQUAL_CONTACT_MASS_GEOMETRY_DIFFERENCE_OBSERVED",
            self.result.characterization_decision,
        )

    def test_spreading_same_mass_increases_boundary_distance(self) -> None:
        loads = self._long_loads()
        self.assertGreater(
            loads["av_distributed_mass1"].normalized_boundary_distance,
            loads["local_auditory_mass1"].normalized_boundary_distance,
        )
        self.assertGreater(
            loads["auditory_distributed_mass1"].normalized_boundary_distance,
            loads["local_auditory_mass1"].normalized_boundary_distance,
        )
        self.assertGreater(
            loads["visual_distributed_mass1"].normalized_boundary_distance,
            loads["local_visual_mass1"].normalized_boundary_distance,
        )
        self.assertTrue(
            all(not item.normalized_boundary_reached for item in loads.values())
        )

    def test_recovery_is_monotone_for_every_equal_mass_pattern(self) -> None:
        self.assertTrue(self.result.all_recovery_nonincreasing)
        for pattern_id in FIELD_CONTACT_MASS_PATTERN_IDS:
            for duration in FIELD_CONTACT_MASS_LOAD_DURATIONS_SECONDS:
                group = tuple(
                    item
                    for item in self.result.observations
                    if item.pattern_id == pattern_id
                    and item.load_duration_seconds == duration
                )
                values = tuple(item.recovery_activation_linf for item in group)
                self.assertEqual(tuple(sorted(values, reverse=True)), values)
                expected_events = tuple(
                    2 * round((duration + recovery) / 0.1)
                    for recovery in FIELD_CONTACT_MASS_RECOVERY_DURATIONS_SECONDS
                )
                self.assertEqual(
                    expected_events,
                    tuple(item.source_event_count for item in group),
                )

    def test_counterbaseline_contains_no_regulator_or_raw_vectors(self) -> None:
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.adaptive_regulation_applied)
        self.assertTrue(all(not item.writes_back for item in self.result.observations))
        roles = set(field_contact_mass_counterbaseline_public_roles())
        forbidden_roles = {
            "gain_state",
            "sensitivity_state",
            "adaptation_rate",
            "target_activity",
            "controller_output",
            "raw_audio",
            "raw_video",
            "receptor_values",
            "field_values",
            "memory",
        }
        self.assertTrue(forbidden_roles.isdisjoint(roles))
        encoded = json.dumps(
            field_contact_mass_counterbaseline_json_value(self.result)
        ).lower()
        for forbidden in ("raw_audio", "raw_video", "receptor_values", "field_values"):
            self.assertNotIn(forbidden, encoded)

    def _long_loads(self):
        return {
            item.pattern_id: item
            for item in self.result.observations
            if item.load_duration_seconds == 4.0
            and item.recovery_duration_seconds == 0.0
        }


if __name__ == "__main__":
    unittest.main()
