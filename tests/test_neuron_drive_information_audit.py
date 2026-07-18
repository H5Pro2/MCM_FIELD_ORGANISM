from __future__ import annotations

import unittest

from mcm_field_organism.neuron_drive_information_audit import (
    EndpointContactHistory,
    NeuronDriveInformationAuditError,
    neuron_drive_information_audit_public_roles,
    run_neuron_drive_information_audit,
)


class NeuronDriveInformationAuditTests(unittest.TestCase):
    def test_current_contact_is_separable_from_prior_state_and_time(self) -> None:
        comparison = run_neuron_drive_information_audit().current_contact_axis
        self.assertEqual(
            ("current_receptor_contact", "receptor_endpoint_change"),
            comparison.differing_roles,
        )

    def test_prior_receptor_contact_is_preserved_separately(self) -> None:
        comparison = run_neuron_drive_information_audit().prior_contact_axis
        self.assertEqual(
            ("prior_receptor_contact", "receptor_endpoint_change"),
            comparison.differing_roles,
        )
        self.assertEqual(
            comparison.first.previous_activation,
            comparison.second.previous_activation,
        )

    def test_elapsed_time_is_an_independent_drive_axis(self) -> None:
        comparison = run_neuron_drive_information_audit().elapsed_time_axis
        self.assertEqual(("elapsed_seconds",), comparison.differing_roles)

    def test_change_is_undefined_without_current_contact(self) -> None:
        observation = run_neuron_drive_information_audit().missing_current_contact
        self.assertIsNone(observation.current_receptor_contact)
        self.assertIsNone(observation.receptor_endpoint_change)

    def test_equal_endpoints_and_time_do_not_reveal_interruption(self) -> None:
        result = run_neuron_drive_information_audit()
        self.assertTrue(result.endpoint_history_information_equal)
        self.assertNotEqual(
            result.continuous_history.sampled_contact_sum,
            result.interrupted_history.sampled_contact_sum,
        )

    def test_invalid_endpoint_histories_are_rejected(self) -> None:
        with self.assertRaisesRegex(NeuronDriveInformationAuditError, "at least two"):
            EndpointContactHistory("short", (1.0,), 1.0)
        with self.assertRaisesRegex(NeuronDriveInformationAuditError, "positive"):
            EndpointContactHistory("time", (1.0, 1.0), 0.0)

    def test_public_roles_add_no_transition_or_contact_persistence(self) -> None:
        forbidden = {
            "transition_equation",
            "held_contact",
            "valid_until",
            "selected_input_role",
            "field_activation",
            "memory",
            "topology",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(neuron_drive_information_audit_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
