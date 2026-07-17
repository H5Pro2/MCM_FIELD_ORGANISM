from __future__ import annotations

from dataclasses import asdict
import unittest

import numpy as np

from mcm_field_organism import (
    CONTINUOUS_FORWARD,
    CONTINUOUS_REVERSE,
    INTERRUPTED_CONTACTS,
    PERMUTED_CONTACTS,
    SEQUENCE_IDS,
    STATIONARY_CONTACTS,
    LocalTransitionEvidenceProbeError,
    local_transition_evidence_probe_public_roles,
    run_local_transition_evidence_probe,
)


class LocalTransitionEvidenceProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_local_transition_evidence_probe()
        cls.by_id = {item.sequence_id: item for item in cls.result.sequences}

    def test_preregistered_sequences_are_exact(self) -> None:
        self.assertEqual((1, 2, 3, 4, 5), CONTINUOUS_FORWARD)
        self.assertEqual((5, 4, 3, 2, 1), CONTINUOUS_REVERSE)
        self.assertEqual((1, 4, 2, 5, 3), PERMUTED_CONTACTS)
        self.assertEqual(
            (1, None, 2, None, 3, None, 4, None, 5),
            INTERRUPTED_CONTACTS,
        )
        self.assertEqual((3, 3, 3, 3, 3), STATIONARY_CONTACTS)

    def test_all_sequence_families_are_present(self) -> None:
        self.assertEqual(5, len(self.result.sequences))
        self.assertEqual(
            tuple(sorted(SEQUENCE_IDS)),
            tuple(item.sequence_id for item in self.result.sequences),
        )

    def test_primary_energy_and_position_frequency_are_equal(self) -> None:
        self.assertTrue(self.result.primary_energy_equal)
        self.assertTrue(self.result.primary_position_frequency_equal)
        primary = tuple(
            self.by_id[item]
            for item in (
                "continuous_forward",
                "continuous_reverse",
                "permuted",
            )
        )
        self.assertEqual({5.0}, {item.total_energy for item in primary})
        self.assertEqual(1, len({item.position_frequency for item in primary}))
        self.assertTrue(all(item.frame_energies == (1.0,) * 5 for item in primary))

    def test_forward_and_reverse_events_are_exact_mirrors(self) -> None:
        forward = self.by_id["continuous_forward"]
        reverse = self.by_id["continuous_reverse"]
        self.assertEqual(4.0, forward.local_transition_total)
        self.assertEqual(4, forward.source_negative_column_events)
        self.assertEqual(0, forward.source_positive_column_events)
        self.assertEqual(4.0, reverse.local_transition_total)
        self.assertEqual(0, reverse.source_negative_column_events)
        self.assertEqual(4, reverse.source_positive_column_events)
        self.assertTrue(self.result.time_reversal_is_symmetric)

    def test_permutation_and_interruption_remove_local_events(self) -> None:
        permuted = self.by_id["permuted"]
        interrupted = self.by_id["interrupted"]
        self.assertEqual(0.0, permuted.local_transition_total)
        self.assertEqual(0, len(permuted.events))
        self.assertEqual(9, interrupted.frame_count)
        self.assertEqual(5.0, interrupted.total_energy)
        self.assertEqual(0.0, interrupted.local_transition_total)
        self.assertTrue(self.result.interruption_removes_events)

    def test_stationary_contact_is_only_self_overlap(self) -> None:
        stationary = self.by_id["stationary"]
        self.assertEqual(4.0, stationary.self_overlap_total)
        self.assertEqual(0.0, stationary.local_transition_total)
        self.assertTrue(self.result.stationary_separates_self_from_neighbor)
        self.assertTrue(self.result.primary_self_overlap_zero)

    def test_events_use_only_the_previous_completed_tick(self) -> None:
        for sequence_id in ("continuous_forward", "continuous_reverse"):
            for event in self.by_id[sequence_id].events:
                self.assertEqual(event.target_tick - 1, event.source_tick)
                self.assertEqual(1.0, event.current_contact)
                self.assertEqual(1.0, event.prior_local_activation)
                self.assertIn(
                    event.relative_source_position,
                    ((0, -1, 0), (0, 1, 0)),
                )

    def test_runtime_evidence_is_exactly_the_fixed_neighbor_baseline(self) -> None:
        self.assertTrue(self.result.all_runtime_events_match_fixed_neighbor_baseline)
        for sequence in self.result.sequences:
            self.assertTrue(sequence.runtime_matches_fixed_neighbor_baseline)
            self.assertEqual(
                sequence.local_transition_total,
                sequence.baseline_transition_total,
            )

    def test_spatial_channel_and_order_controls_close(self) -> None:
        self.assertTrue(self.result.expected_event_counts_exact)
        self.assertTrue(self.result.spatial_reflection_is_equivariant)
        self.assertTrue(self.result.channel_permutation_is_equivariant)
        self.assertTrue(self.result.offset_order_is_neutral)
        self.assertTrue(self.result.observation_order_is_neutral)

    def test_observer_sequence_order_and_repetition_are_neutral(self) -> None:
        observed = []
        with_observer = run_local_transition_evidence_probe(
            observer=lambda item: observed.append(item.sequence_id)
        )
        reversed_result = run_local_transition_evidence_probe(
            sequence_order=reversed(SEQUENCE_IDS)
        )
        self.assertEqual(list(SEQUENCE_IDS), observed)
        self.assertEqual(self.result.digest(), with_observer.digest())
        self.assertEqual(self.result.digest(), reversed_result.digest())
        self.assertTrue(with_observer.observer_is_neutral)
        self.assertTrue(reversed_result.sequence_order_is_neutral)
        self.assertTrue(self.result.repeated_run_is_neutral)

    def test_canonical_digest_is_stable(self) -> None:
        self.assertEqual(
            "dd0658ac075b5f0de5ea3edabec453c77f4ca03fc87b0ed193da3f1fbb9d711e",
            self.result.digest(),
        )

    def test_invalid_sequence_orders_are_rejected(self) -> None:
        invalid = (
            (),
            SEQUENCE_IDS[:-1],
            SEQUENCE_IDS + ("continuous_forward",),
            (
                "continuous_forward",
                "continuous_forward",
                "interrupted",
                "permuted",
                "stationary",
            ),
            (
                "continuous_forward",
                "continuous_reverse",
                "interrupted",
                "permuted",
                "unknown",
            ),
        )
        for order in invalid:
            with self.subTest(order=order):
                with self.assertRaises(LocalTransitionEvidenceProbeError):
                    run_local_transition_evidence_probe(sequence_order=order)

    def test_result_retains_no_frames_and_releases_no_mechanic(self) -> None:
        self.assertFalse(self.result.retains_raw_frames)
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.releases_disposition)
        self.assertTrue(
            all(item.afterimage_is_zero for item in self.result.sequences)
        )
        self.assertTrue(
            all(item.input_frames_unchanged for item in self.result.sequences)
        )
        self.assertFalse(
            any(
                isinstance(value, np.ndarray)
                for sequence in self.result.sequences
                for value in asdict(sequence).values()
            )
        )

    def test_public_roles_exclude_inferred_world_meaning(self) -> None:
        roles = set(local_transition_evidence_probe_public_roles())
        forbidden = {
            "frame",
            "image",
            "pixels",
            "object",
            "form",
            "view",
            "motion",
            "direction",
            "velocity",
            "pattern_id",
            "meaning",
            "memory",
            "disposition",
            "weight",
            "learning_rate",
            "reward",
            "winner",
            "action",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
