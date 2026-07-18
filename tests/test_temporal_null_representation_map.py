from __future__ import annotations

import unittest

from mcm_field_organism import (
    run_temporal_null_representation_map,
    temporal_null_representation_map_public_roles,
)


class TemporalNullRepresentationMapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = run_temporal_null_representation_map()
        self.by_id = {
            item.representation_id: item for item in self.result.evaluations
        }

    def test_event_count_fails_both_contract_axes(self) -> None:
        item = self.by_id["event_count"]
        self.assertFalse(item.representation_invariant)
        self.assertFalse(item.ordered_paths_accessible)
        self.assertFalse(item.satisfies_both_contract_axes)

    def test_endpoint_is_invariant_but_loses_order(self) -> None:
        item = self.by_id["endpoint"]
        self.assertTrue(item.representation_invariant)
        self.assertFalse(item.ordered_paths_accessible)
        self.assertFalse(item.satisfies_both_contract_axes)

    def test_duration_weighted_mean_is_invariant_but_loses_order(self) -> None:
        item = self.by_id["duration_weighted_mean"]
        self.assertTrue(item.representation_invariant)
        self.assertFalse(item.ordered_paths_accessible)
        self.assertFalse(item.satisfies_both_contract_axes)

    def test_full_supported_path_carries_both_axes_but_is_variable_width(self) -> None:
        item = self.by_id["full_supported_path"]
        self.assertTrue(item.representation_invariant)
        self.assertTrue(item.ordered_paths_accessible)
        self.assertTrue(item.satisfies_both_contract_axes)
        self.assertFalse(item.fixed_width_in_controls)
        self.assertEqual((1, 1, 3, 3), (
            item.dense_payload_item_count,
            item.sparse_payload_item_count,
            item.first_order_payload_item_count,
            item.second_order_payload_item_count,
        ))

    def test_map_claims_neither_minimality_nor_runtime_release(self) -> None:
        self.assertEqual(
            ("endpoint", "duration_weighted_mean", "full_supported_path"),
            self.result.representation_invariant_ids,
        )
        self.assertEqual(("full_supported_path",), self.result.order_accessible_ids)
        self.assertEqual(("full_supported_path",), self.result.satisfies_both_ids)
        self.assertFalse(self.result.minimal_representation_proven)
        self.assertFalse(self.result.runtime_candidate_released)

    def test_public_roles_add_no_field_effect_or_storage(self) -> None:
        forbidden = {
            "field_activation",
            "afterimage_update",
            "selected_representation",
            "storage_policy",
            "memory",
            "topology",
            "weight",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                temporal_null_representation_map_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
