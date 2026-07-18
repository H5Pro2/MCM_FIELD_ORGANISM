from __future__ import annotations

import unittest

from mcm_field_organism import (
    finite_linear_projection_bank,
    finite_linear_temporal_projection_audit_public_roles,
    run_finite_linear_temporal_projection_audit,
)


class FiniteLinearTemporalProjectionAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = run_finite_linear_temporal_projection_audit()

    def test_projection_bank_has_fewer_rows_than_history_dimensions(self) -> None:
        self.assertEqual(8, self.result.history_dimension)
        self.assertEqual(6, self.result.projection_count)
        self.assertLess(
            self.result.projection_count,
            self.result.history_dimension,
        )

    def test_exact_rank_nullity_leaves_a_nonzero_collision_space(self) -> None:
        self.assertEqual(6, self.result.matrix_rank)
        self.assertEqual(2, self.result.exact_nullity)
        self.assertTrue(self.result.null_vector_nonzero)
        self.assertTrue(self.result.null_vector_annihilated)

    def test_two_valid_distinct_histories_have_equal_endpoints(self) -> None:
        self.assertTrue(self.result.histories_distinct)
        self.assertTrue(self.result.contacts_within_normalized_domain)
        self.assertTrue(self.result.endpoints_equal)

    def test_all_six_projection_values_collide_exactly(self) -> None:
        self.assertTrue(self.result.projections_equal_exactly)
        self.assertEqual(
            self.result.first_projection_values,
            self.result.second_projection_values,
        )

    def test_result_does_not_generalize_beyond_finite_linear_banks(self) -> None:
        self.assertFalse(
            self.result.fixed_linear_bank_injective_on_full_history_space
        )
        self.assertFalse(self.result.all_fixed_finite_representations_falsified)

    def test_public_bank_exposes_only_exact_observer_coefficients(self) -> None:
        bank = finite_linear_projection_bank()
        self.assertEqual(8, bank.history_dimension)
        self.assertEqual(6, len(bank.projection_ids))
        self.assertEqual(6, len(bank.coefficient_rows))
        self.assertTrue(all(len(row) == 8 for row in bank.coefficient_rows))

    def test_no_field_effect_or_runtime_is_released(self) -> None:
        self.assertFalse(self.result.field_effect_performed)
        self.assertFalse(self.result.runtime_candidate_released)

    def test_public_roles_add_no_field_state_or_selection(self) -> None:
        forbidden = {
            "activation",
            "afterimage",
            "selected_representation",
            "storage_policy",
            "memory",
            "topology",
            "weight",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                finite_linear_temporal_projection_audit_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
