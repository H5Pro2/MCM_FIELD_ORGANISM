from __future__ import annotations

import unittest

from mcm_field_organism.receptor_state_role_audit import (
    receptor_state_role_audit_public_roles,
    run_receptor_state_role_audit,
)


class ReceptorStateRoleAuditTests(unittest.TestCase):
    def test_audio_is_a_finite_rolling_source_process(self) -> None:
        result = run_receptor_state_role_audit()
        self.assertEqual(0.1, result.auditory_window_seconds)
        self.assertEqual(0.01, result.auditory_hop_seconds)
        self.assertGreater(result.auditory_one_hop_history_difference, 0.0)
        self.assertTrue(result.auditory_history_cleared_after_window)

    def test_visual_receptor_does_not_retain_prior_frame_contact(self) -> None:
        result = run_receptor_state_role_audit()
        self.assertEqual(0.0, result.visual_probe_history_difference)
        self.assertTrue(
            result.visual_probe_digest_equal_after_contrasting_history
        )

    def test_distributor_retains_anatomy_but_not_prior_contact(self) -> None:
        result = run_receptor_state_role_audit()
        self.assertTrue(
            result.distributor_probe_digest_equal_after_prior_distribution
        )
        self.assertEqual(1, result.distributor_attached_dock_count_after_probe)

    def test_audit_is_exactly_reproducible(self) -> None:
        self.assertEqual(
            run_receptor_state_role_audit(),
            run_receptor_state_role_audit(),
        )

    def test_public_roles_add_no_persistence_or_field_decision(self) -> None:
        forbidden = {
            "selected_input_role",
            "valid_until",
            "held_contact",
            "field_activation",
            "memory",
            "topology",
            "meaning",
        }
        self.assertTrue(forbidden.isdisjoint(receptor_state_role_audit_public_roles()))


if __name__ == "__main__":
    unittest.main()
