from __future__ import annotations

import json
import unittest

from mcm_field_organism.field_background_contrast_characterization import (
    FIELD_BACKGROUND_CONTRAST_MODALITY_IDS,
    FIELD_BACKGROUND_LEVELS,
    FIELD_BACKGROUND_LOAD_DURATIONS_SECONDS,
    field_background_contrast_characterization_json_value,
    field_background_contrast_characterization_public_roles,
    run_field_background_contrast_characterization,
)


class FieldBackgroundContrastCharacterizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_field_background_contrast_characterization()

    def test_complete_paired_matrix(self) -> None:
        self.assertEqual(72, self.result.observation_count)
        self.assertEqual(
            FIELD_BACKGROUND_CONTRAST_MODALITY_IDS,
            self.result.modality_ids,
        )
        self.assertEqual(FIELD_BACKGROUND_LEVELS, self.result.background_levels)
        for item in self.result.observations:
            self.assertEqual(26, item.field_neuron_count)
            self.assertEqual(
                4 * round(item.load_duration_seconds / 0.1),
                item.paired_source_event_count,
            )

    def test_unmodified_field_retains_contrast_across_backgrounds(self) -> None:
        self.assertTrue(self.result.unmodified_contrast_retained)
        self.assertLessEqual(
            self.result.unmodified_max_background_delta_error,
            1e-12,
        )
        self.assertEqual(
            "UNMODIFIED_FIELD_CONTRAST_RETAINED_ACROSS_BOUND_BACKGROUNDS",
            self.result.characterization_decision,
        )
        unmodified = tuple(
            item
            for item in self.result.observations
            if item.baseline_id == "unmodified"
        )
        self.assertTrue(all(item.contrast_delta_linf > 0.0 for item in unmodified))

    def test_fixed_gain_is_background_invariant_and_half_unmodified(self) -> None:
        self.assertLessEqual(
            self.result.fixed_gain_max_background_delta_error,
            1e-12,
        )
        by_key = {
            (
                item.baseline_id,
                item.contrast_modality_id,
                item.background_level,
                item.load_duration_seconds,
            ): item
            for item in self.result.observations
        }
        for modality in FIELD_BACKGROUND_CONTRAST_MODALITY_IDS:
            for background in FIELD_BACKGROUND_LEVELS:
                for duration in FIELD_BACKGROUND_LOAD_DURATIONS_SECONDS:
                    unmodified = by_key[
                        ("unmodified", modality, background, duration)
                    ]
                    fixed_gain = by_key[
                        ("fixed_gain_0_5", modality, background, duration)
                    ]
                    self.assertAlmostEqual(
                        unmodified.contrast_delta_linf * 0.5,
                        fixed_gain.contrast_delta_linf,
                        places=14,
                    )

    def test_fixed_leaky_baseline_is_background_invariant(self) -> None:
        self.assertLessEqual(
            self.result.fixed_leaky_max_background_delta_error,
            1e-12,
        )
        leaky = tuple(
            item
            for item in self.result.observations
            if item.baseline_id == "fixed_leaky_1_0"
        )
        self.assertTrue(all(item.contrast_delta_linf > 0.0 for item in leaky))
        repeated = tuple(
            item for item in leaky if item.load_duration_seconds > 0.1
        )
        self.assertTrue(all(item.afterimage_delta_linf > 0.0 for item in repeated))

    def test_static_clipping_erases_high_background_contrast(self) -> None:
        self.assertTrue(self.result.static_clipping_high_background_contrast_lost)
        clipped = tuple(
            item
            for item in self.result.observations
            if item.baseline_id == "static_clip_0_5"
            and item.background_level >= 0.5
        )
        self.assertTrue(clipped)
        self.assertTrue(all(item.applied_contrast_delta == 0.0 for item in clipped))
        self.assertTrue(all(item.contrast_delta_linf == 0.0 for item in clipped))

    def test_contrast_path_is_local_and_cross_modal_without_hidden_vectors(self) -> None:
        observations = self.result.observations
        self.assertTrue(
            all(
                item.local_contrast_delta_abs == item.contrast_delta_linf
                for item in observations
            )
        )
        self.assertTrue(
            any(item.cross_modal_delta_linf > 0.0 for item in observations)
        )
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.adaptive_regulation_applied)
        roles = set(field_background_contrast_characterization_public_roles())
        forbidden = {
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
        self.assertTrue(forbidden.isdisjoint(roles))
        encoded = json.dumps(
            field_background_contrast_characterization_json_value(self.result)
        ).lower()
        for role in ("raw_audio", "raw_video", "receptor_values", "field_values"):
            self.assertNotIn(role, encoded)


if __name__ == "__main__":
    unittest.main()
