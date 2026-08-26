from __future__ import annotations

import json
import unittest

from mcm_field_organism.field_event_density_resource_characterization import (
    FIELD_EVENT_DENSITY_IDS,
    FIELD_EVENT_DENSITY_REPETITIONS,
    field_event_density_resource_characterization_json_value,
    field_event_density_resource_characterization_public_roles,
    run_field_event_density_resource_characterization,
)


class FieldEventDensityResourceCharacterizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_field_event_density_resource_characterization()

    def test_fixed_density_inventory_is_complete(self) -> None:
        self.assertEqual(6, self.result.observation_count)
        self.assertEqual(FIELD_EVENT_DENSITY_IDS, self.result.density_ids)
        self.assertEqual(
            FIELD_EVENT_DENSITY_REPETITIONS,
            self.result.repetitions_per_density,
        )
        self.assertEqual(
            (20, 200, 2000),
            tuple(
                item.source_event_count
                for item in self.result.observations
                if item.input_amplitude == 0.0
            ),
        )
        self.assertEqual(
            (10, 100, 1000),
            tuple(
                item.completion_group_count
                for item in self.result.observations
                if item.input_amplitude == 0.0
            ),
        )
        self.assertTrue(
            all(item.proposal_batch_count == 1 for item in self.result.observations)
        )

    def test_projected_work_inventory_grows_independently_of_field_value(self) -> None:
        self.assertEqual(
            (260, 2600, 26000),
            tuple(
                item.projected_local_contact_count
                for item in self.result.observations
                if item.input_amplitude == 0.0
            ),
        )
        self.assertEqual(100.0, self.result.source_event_growth_factor)
        self.assertEqual(100.0, self.result.projected_contact_growth_factor)

    def test_zero_contact_endpoint_is_exact_and_density_invariant(self) -> None:
        zero = tuple(
            item for item in self.result.observations if item.input_amplitude == 0.0
        )
        self.assertTrue(self.result.zero_contact_endpoints_equal)
        self.assertEqual(
            1,
            len({item.endpoint_digest for item in zero}),
        )
        for item in zero:
            self.assertTrue(item.repeated_endpoints_equal)
            self.assertEqual(0.0, item.final_activation_l1)
            self.assertEqual(0.0, item.final_activation_linf)
            self.assertEqual(0.0, item.final_afterimage_linf)
        self.assertEqual(
            "FIELD_ENDPOINT_INVARIANT_ACROSS_BOUND_EVENT_DENSITIES",
            self.result.characterization_decision,
        )

    def test_active_contact_endpoint_is_density_invariant(self) -> None:
        active = tuple(
            item for item in self.result.observations if item.input_amplitude == 0.1
        )
        self.assertTrue(self.result.active_contact_density_invariant)
        self.assertLessEqual(
            self.result.active_contact_max_density_delta_linf,
            1e-12,
        )
        self.assertTrue(all(item.final_activation_linf > 0.0 for item in active))
        self.assertEqual(0.0, active[0].reference_activation_delta_linf)

    def test_runtime_measurements_are_descriptive_and_ordered(self) -> None:
        for item in self.result.observations:
            self.assertLessEqual(
                item.runtime_seconds_min,
                item.runtime_seconds_median,
            )
            self.assertLessEqual(
                item.runtime_seconds_median,
                item.runtime_seconds_max,
            )
            self.assertLessEqual(
                item.process_seconds_min,
                item.process_seconds_median,
            )
            self.assertLessEqual(
                item.process_seconds_median,
                item.process_seconds_max,
            )
        self.assertFalse(self.result.resource_limit_observed)

    def test_resource_probe_has_no_adaptive_or_hidden_field_roles(self) -> None:
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.adaptive_regulation_applied)
        roles = set(field_event_density_resource_characterization_public_roles())
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
            field_event_density_resource_characterization_json_value(self.result)
        ).lower()
        for role in ("raw_audio", "raw_video", "receptor_values", "field_values"):
            self.assertNotIn(role, encoded)


if __name__ == "__main__":
    unittest.main()
