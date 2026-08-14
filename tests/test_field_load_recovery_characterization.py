from __future__ import annotations

import json
import unittest

from mcm_field_organism.field_load_recovery_characterization import (
    FIELD_LOAD_AMPLITUDES,
    FIELD_LOAD_BASELINE_IDS,
    FIELD_LOAD_DURATIONS_SECONDS,
    FIELD_RECOVERY_DURATIONS_SECONDS,
    field_load_recovery_characterization_json_value,
    field_load_recovery_characterization_public_roles,
    run_field_load_recovery_characterization,
)
from mcm_field_organism.sensory_self_regulation_contract import (
    reference_sensory_self_regulation_contract,
)


class FieldLoadRecoveryCharacterizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_field_load_recovery_characterization()

    def test_complete_matrix_stays_below_normalized_boundary(self) -> None:
        self.assertEqual(144, self.result.observation_count)
        self.assertEqual(
            "NORMALIZED_BOUNDARY_NOT_REACHED_IN_BOUND_MATRIX",
            self.result.characterization_decision,
        )
        self.assertFalse(self.result.unmodified_boundary_reached)
        self.assertAlmostEqual(
            0.018315638888732444,
            self.result.unmodified_min_boundary_distance,
            places=15,
        )
        self.assertTrue(
            all(item.field_neuron_count == 26 for item in self.result.observations)
        )

    def test_unmodified_load_increases_with_strength_and_duration(self) -> None:
        observations = {
            (item.input_amplitude, item.load_duration_seconds): item
            for item in self.result.observations
            if item.baseline_id == "unmodified"
            and item.recovery_duration_seconds == 0.0
        }
        for duration in FIELD_LOAD_DURATIONS_SECONDS:
            values = tuple(
                observations[(amplitude, duration)].load_activation_linf
                for amplitude in FIELD_LOAD_AMPLITUDES
            )
            self.assertEqual(tuple(sorted(values)), values)
            self.assertEqual(len(values), len(set(values)))
        for amplitude in FIELD_LOAD_AMPLITUDES:
            values = tuple(
                observations[(amplitude, duration)].load_activation_linf
                for duration in FIELD_LOAD_DURATIONS_SECONDS
            )
            self.assertEqual(tuple(sorted(values)), values)
            self.assertEqual(len(values), len(set(values)))

    def test_zero_contact_recovery_is_monotone_without_regulation(self) -> None:
        self.assertTrue(self.result.unmodified_recovery_nonincreasing)
        for amplitude in FIELD_LOAD_AMPLITUDES:
            for duration in FIELD_LOAD_DURATIONS_SECONDS:
                group = tuple(
                    item
                    for item in self.result.observations
                    if item.baseline_id == "unmodified"
                    and item.input_amplitude == amplitude
                    and item.load_duration_seconds == duration
                )
                by_recovery = {
                    item.recovery_duration_seconds: item for item in group
                }
                self.assertEqual(
                    by_recovery[0.0].load_activation_linf,
                    by_recovery[0.0].recovery_activation_linf,
                )
                self.assertLess(
                    by_recovery[4.0].recovery_activation_linf,
                    by_recovery[0.0].recovery_activation_linf,
                )

    def test_fixed_baselines_are_separate_runtime_paths(self) -> None:
        self.assertEqual(FIELD_LOAD_BASELINE_IDS, self.result.baseline_ids)
        selected = {
            item.baseline_id: item
            for item in self.result.observations
            if item.input_amplitude == 1.0
            and item.load_duration_seconds == 4.0
            and item.recovery_duration_seconds == 0.0
        }
        self.assertEqual(0.5, selected["fixed_gain_0_5"].applied_amplitude)
        self.assertEqual(0.5, selected["static_clip_0_5"].applied_amplitude)
        self.assertEqual(1.0, selected["fixed_leaky_1_0"].applied_amplitude)
        self.assertEqual(1.0, selected["unmodified"].applied_amplitude)
        self.assertLess(
            selected["fixed_leaky_1_0"].load_activation_linf,
            selected["unmodified"].load_activation_linf,
        )
        self.assertEqual(0.0, selected["fixed_leaky_1_0"].load_afterimage_linf)
        self.assertEqual(0.0, selected["unmodified"].load_afterimage_linf)

    def test_characterization_does_not_release_regulation(self) -> None:
        contract = reference_sensory_self_regulation_contract()
        self.assertFalse(contract.writes_back)
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.adaptive_regulation_applied)
        self.assertTrue(
            all(not item.writes_back for item in self.result.observations)
        )
        self.assertTrue(
            all(
                not item.adaptive_regulation_applied
                for item in self.result.observations
            )
        )

    def test_public_result_is_scalar_and_contains_no_controller_state(self) -> None:
        roles = set(field_load_recovery_characterization_public_roles())
        forbidden_roles = {
            "gain_state",
            "sensitivity_state",
            "adaptation_rate",
            "target_activity",
            "setpoint",
            "controller_output",
            "raw_audio",
            "raw_video",
            "receptor_values",
            "field_values",
            "memory",
        }
        self.assertTrue(forbidden_roles.isdisjoint(roles))
        encoded = json.dumps(
            field_load_recovery_characterization_json_value(self.result)
        ).lower()
        for forbidden in ("raw_audio", "raw_video", "receptor_values", "field_values"):
            self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
