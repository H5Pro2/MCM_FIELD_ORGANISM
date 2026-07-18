from __future__ import annotations

import unittest

from mcm_field_organism import (
    field_input_capacity_audit_public_roles,
    run_field_input_capacity_audit,
)


class FieldInputCapacityAuditTests(unittest.TestCase):
    def test_one_frame_per_modality_is_accepted(self) -> None:
        capacity = run_field_input_capacity_audit().capacity
        self.assertTrue(capacity.single_frame_distribution_accepted)
        self.assertTrue(capacity.scalar_contact_accepted)

    def test_same_dock_batch_is_rejected_by_current_distribution(self) -> None:
        capacity = run_field_input_capacity_audit().capacity
        self.assertEqual(2, capacity.same_dock_batch_frame_count)
        self.assertTrue(capacity.same_dock_batch_rejected)
        self.assertIn("duplicate modality frame", capacity.same_dock_batch_error)

    def test_contact_sequence_is_rejected_by_scalar_perception(self) -> None:
        capacity = run_field_input_capacity_audit().capacity
        self.assertTrue(capacity.contact_sequence_rejected)
        self.assertIn("must be numeric", capacity.contact_sequence_error)

    def test_serial_delivery_requires_one_complete_advance_per_frame(self) -> None:
        capacity = run_field_input_capacity_audit().capacity
        self.assertEqual(2, capacity.serial_distribution_count)
        self.assertEqual(2, capacity.required_complete_field_advances_if_serialized)

    def test_endpoint_only_input_collides_for_different_inner_histories(self) -> None:
        collision = run_field_input_capacity_audit().endpoint_collision
        self.assertNotEqual(
            collision.first_contact_history,
            collision.second_contact_history,
        )
        self.assertEqual(
            collision.first_contact_history[-1],
            collision.second_contact_history[-1],
        )
        self.assertTrue(collision.endpoint_only_drives_equal)

    def test_no_existing_direct_representation_accepts_the_batch(self) -> None:
        self.assertFalse(
            run_field_input_capacity_audit().variable_same_dock_batch_directly_representable
        )

    def test_public_roles_add_no_reduction_transition_or_memory(self) -> None:
        forbidden = {
            "selected_frame",
            "mean_contact",
            "integrated_contact",
            "encoded_sequence",
            "transition_equation",
            "field_activation",
            "afterimage_update",
            "memory",
            "topology",
            "weight",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(field_input_capacity_audit_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
