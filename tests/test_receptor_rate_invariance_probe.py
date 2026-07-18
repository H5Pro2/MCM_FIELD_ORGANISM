from __future__ import annotations

import unittest

from mcm_field_organism import (
    ContactRateRepresentation,
    ReceptorRateInvarianceProbeError,
    TimedContactSegment,
    receptor_rate_invariance_probe_public_roles,
    run_receptor_rate_invariance_probe,
)


class ReceptorRateInvarianceProbeTests(unittest.TestCase):
    def test_physical_time_baseline_is_invariant_to_exact_rate_splitting(self) -> None:
        result = run_receptor_rate_invariance_probe()
        self.assertTrue(result.physical_time_baseline_is_rate_invariant)
        self.assertTrue(all(
            observation.physical_time_difference <= 1e-14
            for observation in result.observations
        ))

    def test_event_count_baseline_changes_with_representation_density(self) -> None:
        result = run_receptor_rate_invariance_probe()
        self.assertFalse(result.event_count_baseline_is_rate_invariant)
        self.assertTrue(all(
            observation.event_count_difference > 1e-8
            for observation in result.observations
        ))

    def test_elapsed_time_does_not_reconstruct_an_omitted_contact(self) -> None:
        result = run_receptor_rate_invariance_probe()
        self.assertGreater(result.omitted_contact_difference, 0.0)
        self.assertEqual(0.0, result.omitted_contact_sparse_end)

    def test_incomplete_or_noncontiguous_histories_are_rejected(self) -> None:
        with self.assertRaisesRegex(ReceptorRateInvarianceProbeError, "contiguous"):
            ContactRateRepresentation(
                "broken",
                (
                    TimedContactSegment(0, 1, 0.0),
                    TimedContactSegment(2, 3, 0.0),
                ),
            )

    def test_public_roles_do_not_claim_runtime_or_organic_time(self) -> None:
        roles = set(receptor_rate_invariance_probe_public_roles())
        forbidden = {
            "field_tick",
            "organic_time",
            "selected_event",
            "modality_weight",
            "memory",
            "topology",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
