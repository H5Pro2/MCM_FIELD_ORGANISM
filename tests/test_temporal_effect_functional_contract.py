from __future__ import annotations

import unittest

from mcm_field_organism import (
    ContactRateRepresentation,
    TimedContactSegment,
    duration_weighted_contact,
    normalize_supported_contact_path,
    run_temporal_effect_functional_contract,
    temporal_effect_functional_contract_public_roles,
)


class TemporalEffectFunctionalContractTests(unittest.TestCase):
    def test_dense_and_sparse_constant_support_normalize_identically(self) -> None:
        evidence = run_temporal_effect_functional_contract().representation_refinement
        self.assertEqual((10, 2), (
            evidence.dense_segment_count,
            evidence.sparse_segment_count,
        ))
        self.assertTrue(evidence.same_supported_path)
        self.assertEqual(evidence.dense_supported_path, evidence.sparse_supported_path)
        self.assertEqual(
            (TimedContactSegment(0, 10, 0.5),),
            evidence.dense_supported_path,
        )

    def test_equal_adjacent_supports_merge_but_real_changes_remain(self) -> None:
        representation = ContactRateRepresentation(
            "merge.control",
            (
                TimedContactSegment(0, 1, 0.2),
                TimedContactSegment(1, 2, 0.2),
                TimedContactSegment(2, 3, 0.8),
            ),
        )
        self.assertEqual(
            (
                TimedContactSegment(0, 2, 0.2),
                TimedContactSegment(2, 3, 0.8),
            ),
            normalize_supported_contact_path(representation),
        )

    def test_ordered_paths_survive_endpoint_and_mean_baseline_collision(self) -> None:
        evidence = run_temporal_effect_functional_contract().ordered_path
        self.assertTrue(evidence.endpoints_equal)
        self.assertTrue(evidence.duration_weighted_contacts_equal)
        self.assertTrue(evidence.ordered_paths_distinct)
        self.assertNotEqual(evidence.first_supported_path, evidence.second_supported_path)

    def test_duration_weighted_contact_is_observer_only_and_order_blind(self) -> None:
        first = ContactRateRepresentation(
            "weighted.first",
            (
                TimedContactSegment(0, 1, 0.2),
                TimedContactSegment(1, 2, 0.8),
            ),
        )
        second = ContactRateRepresentation(
            "weighted.second",
            (
                TimedContactSegment(0, 1, 0.8),
                TimedContactSegment(1, 2, 0.2),
            ),
        )
        self.assertEqual(
            duration_weighted_contact(first),
            duration_weighted_contact(second),
        )

    def test_contract_selects_no_field_effect_or_runtime(self) -> None:
        result = run_temporal_effect_functional_contract()
        self.assertTrue(result.require_equal_consequence_for_same_supported_path)
        self.assertTrue(result.require_candidate_access_to_ordered_path)
        self.assertFalse(result.field_effect_equation_selected)
        self.assertFalse(result.runtime_candidate_released)

    def test_public_roles_add_no_field_mechanism(self) -> None:
        forbidden = {
            "activation_update",
            "afterimage_update",
            "integration_rule",
            "decay_rate",
            "selected_architecture",
            "memory",
            "topology",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                temporal_effect_functional_contract_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
