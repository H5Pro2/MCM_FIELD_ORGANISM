from __future__ import annotations

import unittest

from mcm_field_organism import (
    run_temporal_input_architecture_audit,
    temporal_input_architecture_audit_public_roles,
)


class TemporalInputArchitectureAuditTests(unittest.TestCase):
    def test_temporal_carrier_preserves_both_rate_representations(self) -> None:
        evidence = run_temporal_input_architecture_audit().temporal_proposal_carrier
        self.assertEqual((10, 2), (
            evidence.dense_event_count,
            evidence.sparse_event_count,
        ))
        self.assertTrue(evidence.same_horizon)
        self.assertTrue(evidence.same_constant_contact_values)
        self.assertTrue(evidence.same_contact_endpoint)
        self.assertTrue(evidence.both_sequences_losslessly_carried)

    def test_temporal_payload_remains_rate_exposed(self) -> None:
        result = run_temporal_input_architecture_audit()
        self.assertFalse(
            result.temporal_proposal_carrier.payload_cardinality_equal
        )
        self.assertFalse(result.temporal_carrier_rate_neutral_without_rule)

    def test_current_field_rejects_batch_without_mutation(self) -> None:
        evidence = run_temporal_input_architecture_audit().temporal_proposal_carrier
        self.assertFalse(evidence.current_field_accepts_temporal_batch)
        self.assertTrue(evidence.field_state_unchanged_after_rejection)

    def test_serial_existing_path_advances_at_receptor_event_count(self) -> None:
        evidence = run_temporal_input_architecture_audit().asynchronous_local_effect
        self.assertEqual(10, evidence.dense_complete_field_advance_count)
        self.assertEqual(2, evidence.sparse_complete_field_advance_count)
        self.assertTrue(evidence.final_contact_activation_equal)
        self.assertFalse(evidence.complete_advance_count_equal)
        self.assertTrue(evidence.distributor_anatomy_unchanged)

    def test_no_separate_asynchronous_local_effect_api_exists(self) -> None:
        result = run_temporal_input_architecture_audit()
        self.assertFalse(
            result.asynchronous_local_effect.separate_local_effect_entrypoint_available
        )
        self.assertFalse(result.asynchronous_effect_rate_neutral_without_rule)
        self.assertFalse(result.runtime_candidate_released)

    def test_public_roles_add_no_temporal_reduction_or_new_state(self) -> None:
        forbidden = {
            "integrated_contact",
            "selected_frame",
            "temporal_weight",
            "decay_rate",
            "local_event_state",
            "transition_equation",
            "memory",
            "topology",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                temporal_input_architecture_audit_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
