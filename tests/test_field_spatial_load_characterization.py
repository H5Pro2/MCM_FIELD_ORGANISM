from __future__ import annotations

import json
import unittest

from mcm_field_organism.field_spatial_load_characterization import (
    FIELD_SPATIAL_LOAD_DURATIONS_SECONDS,
    FIELD_SPATIAL_LOAD_PATTERN_IDS,
    FIELD_SPATIAL_RECOVERY_DURATIONS_SECONDS,
    field_spatial_load_characterization_json_value,
    field_spatial_load_characterization_public_roles,
    run_field_spatial_load_characterization,
)


class FieldSpatialLoadCharacterizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_field_spatial_load_characterization()

    def test_complete_matrix_keeps_distributed_load_nearest_boundary(self) -> None:
        self.assertEqual(36, self.result.observation_count)
        self.assertEqual(
            FIELD_SPATIAL_LOAD_PATTERN_IDS,
            self.result.pattern_ids,
        )
        self.assertEqual("distributed_av", self.result.minimum_boundary_pattern_id)
        self.assertAlmostEqual(
            0.018315638888727337,
            self.result.minimum_boundary_distance,
            places=15,
        )
        self.assertTrue(
            all(not item.normalized_boundary_reached for item in self.result.observations)
        )

    def test_local_contacts_remain_strongest_at_stimulated_neuron(self) -> None:
        for pattern_id in ("local_auditory", "local_visual"):
            for duration in FIELD_SPATIAL_LOAD_DURATIONS_SECONDS:
                item = next(
                    observation
                    for observation in self.result.observations
                    if observation.pattern_id == pattern_id
                    and observation.load_duration_seconds == duration
                    and observation.recovery_duration_seconds == 0.0
                )
                self.assertGreater(
                    item.load_stimulated_linf,
                    item.load_unstimulated_linf,
                )
                self.assertGreater(item.load_cross_modal_transfer_linf, 0.0)

    def test_modalities_share_local_field_effect_without_input_copy(self) -> None:
        local_auditory = self._load("local_auditory", 4.0)
        local_visual = self._load("local_visual", 4.0)
        auditory_modality = self._load("auditory_modality", 4.0)
        self.assertAlmostEqual(
            local_auditory.load_cross_modal_transfer_linf,
            local_visual.load_cross_modal_transfer_linf,
            places=15,
        )
        self.assertGreater(
            auditory_modality.load_cross_modal_transfer_linf,
            local_auditory.load_cross_modal_transfer_linf,
        )
        self.assertTrue(self.result.any_cross_modal_transfer_observed)

    def test_distributed_load_is_stronger_than_local_and_single_modality_load(self) -> None:
        loads = {
            pattern_id: self._load(pattern_id, 4.0)
            for pattern_id in FIELD_SPATIAL_LOAD_PATTERN_IDS
        }
        distributed = loads["distributed_av"].load_activation_linf
        self.assertGreater(distributed, loads["auditory_modality"].load_activation_linf)
        self.assertGreater(distributed, loads["local_auditory"].load_activation_linf)
        self.assertGreater(distributed, loads["local_visual"].load_activation_linf)

    def test_recovery_is_monotone_for_every_spatial_pattern(self) -> None:
        self.assertTrue(self.result.all_recovery_nonincreasing)
        for pattern_id in FIELD_SPATIAL_LOAD_PATTERN_IDS:
            for duration in FIELD_SPATIAL_LOAD_DURATIONS_SECONDS:
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
                    for recovery in FIELD_SPATIAL_RECOVERY_DURATIONS_SECONDS
                )
                self.assertEqual(
                    expected_events,
                    tuple(item.source_event_count for item in group),
                )

    def test_result_contains_no_regulator_or_raw_field_vectors(self) -> None:
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.adaptive_regulation_applied)
        self.assertTrue(all(not item.writes_back for item in self.result.observations))
        self.assertTrue(
            all(
                not item.adaptive_regulation_applied
                for item in self.result.observations
            )
        )
        roles = set(field_spatial_load_characterization_public_roles())
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
            field_spatial_load_characterization_json_value(self.result)
        ).lower()
        for forbidden in ("raw_audio", "raw_video", "receptor_values", "field_values"):
            self.assertNotIn(forbidden, encoded)

    def _load(self, pattern_id: str, duration: float):
        return next(
            item
            for item in self.result.observations
            if item.pattern_id == pattern_id
            and item.load_duration_seconds == duration
            and item.recovery_duration_seconds == 0.0
        )


if __name__ == "__main__":
    unittest.main()
