from __future__ import annotations

import unittest

from mcm_field_organism import (
    asynchronous_dock_adjacency_audit_public_roles,
    audit_asynchronous_dock_adjacency,
    run_asynchronous_dock_adjacency_audit,
)
from mcm_field_organism.asynchronous_dock_adjacency_audit import _sequence


class AsynchronousDockAdjacencyAuditTests(unittest.TestCase):
    def test_alternating_modalities_interrupt_every_same_dock_pair(self) -> None:
        result = run_asynchronous_dock_adjacency_audit().alternating
        for modality_id in ("auditory", "visual"):
            measure = result.measure(modality_id)
            self.assertEqual(2, measure.within_dock_pair_count)
            self.assertEqual(0, measure.globally_adjacent_pair_count)
            self.assertEqual(2, measure.interrupted_pair_count)
            self.assertEqual((1, 1), measure.intervening_group_counts)

    def test_rate_skew_matches_the_controlled_310_to_16_event_counts(self) -> None:
        result = run_asynchronous_dock_adjacency_audit().rate_skewed
        auditory = result.measure("auditory")
        visual = result.measure("visual")
        self.assertEqual((310, 16), (auditory.event_count, visual.event_count))
        self.assertEqual((309, 15), (
            auditory.within_dock_pair_count,
            visual.within_dock_pair_count,
        ))
        self.assertEqual(293, auditory.globally_adjacent_pair_count)
        self.assertEqual(0, visual.globally_adjacent_pair_count)
        self.assertEqual(16, auditory.interrupted_pair_count)
        self.assertEqual(15, visual.interrupted_pair_count)

    def test_rate_skew_produces_modality_asymmetric_endpoint_availability(self) -> None:
        result = run_asynchronous_dock_adjacency_audit()
        self.assertTrue(result.rate_skewed_information_is_asymmetric)
        self.assertAlmostEqual(
            293 / 309,
            result.rate_skewed.measure(
                "auditory"
            ).globally_adjacent_pair_fraction,
        )
        self.assertEqual(
            0.0,
            result.rate_skewed.measure("visual").globally_adjacent_pair_fraction,
        )

    def test_synchronized_groups_preserve_both_same_dock_adjacencies(self) -> None:
        result = run_asynchronous_dock_adjacency_audit().synchronized
        self.assertEqual(3, result.completion_group_count)
        for modality_id in ("auditory", "visual"):
            measure = result.measure(modality_id)
            self.assertEqual(2, measure.globally_adjacent_pair_count)
            self.assertEqual(0, measure.interrupted_pair_count)

    def test_sequence_declaration_order_does_not_change_the_audit(self) -> None:
        auditory = _sequence("auditory", (1, 3, 5))
        visual = _sequence("visual", (2, 4, 6))
        self.assertEqual(
            audit_asynchronous_dock_adjacency((auditory, visual)),
            audit_asynchronous_dock_adjacency((visual, auditory)),
        )

    def test_single_event_has_no_invented_pair_fraction(self) -> None:
        result = audit_asynchronous_dock_adjacency(
            (_sequence("auditory", (1,)),)
        ).measure("auditory")
        self.assertEqual(0, result.within_dock_pair_count)
        self.assertIsNone(result.globally_adjacent_pair_fraction)

    def test_public_roles_add_no_field_tick_hold_or_memory(self) -> None:
        forbidden = {
            "field_tick",
            "held_contact",
            "selected_event",
            "activation",
            "afterimage",
            "memory",
            "topology",
            "weight",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                asynchronous_dock_adjacency_audit_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
