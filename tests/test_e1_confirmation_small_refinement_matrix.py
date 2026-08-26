from __future__ import annotations

import hashlib
import inspect
import math
from pathlib import Path
import unittest

from mcm_field_organism.e1_confirmation_small_refinement_matrix import (
    run_small_real_refinement_matrix,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from tests.test_e1_a0_av_history_producer import contract, field, source
from tests.test_e1_confirmation_typed_prepared_inputs import CANONICAL_TARGETS


class E1ConfirmationSmallRefinementMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = source()
        cls.field = field()
        cls.state = build_neutral_e1_state(cls.field.layer, contract())
        cls.result = run_small_real_refinement_matrix(
            cls.source.history_ab,
            cls.source.history_ba,
            cls.field,
            cls.state,
        )

    def test_matrix_uses_real_r2_r4_r8_step_counts_and_controls(self) -> None:
        self.assertEqual(
            (("r2", 4), ("r4", 8), ("r8", 16)),
            self.result.step_counts,
        )
        self.assertTrue(self.result.all_five_arm_controls_passed)
        self.assertTrue(self.result.prepared_inputs_preserved)
        self.assertFalse(self.result.canonical_execution_permitted)

    def test_matrix_records_finite_predeclared_residuals(self) -> None:
        values = (
            *(value for _, value in self.result.history_state_distances),
            self.result.r2_r4_state_residual,
            self.result.r4_r8_state_residual,
        )

        self.assertTrue(all(math.isfinite(value) and value >= 0.0 for value in values))
        self.assertEqual(
            self.result.r4_r8_state_residual
            <= self.result.r2_r4_state_residual,
            self.result.convergence_nonincreasing,
        )

    def test_matrix_is_repeatable_and_preserves_original_inputs(self) -> None:
        field_digest = _initial_field_digest(self.field)
        state_digest = _initial_state_digest(self.state)

        repeated = run_small_real_refinement_matrix(
            self.source.history_ab,
            self.source.history_ba,
            self.field,
            self.state,
        )

        self.assertEqual(self.result.result_digest, repeated.result_digest)
        self.assertEqual(field_digest, _initial_field_digest(self.field))
        self.assertEqual(state_digest, _initial_state_digest(self.state))

    def test_matrix_has_no_persistence_or_canonical_path(self) -> None:
        source_text = inspect.getsource(run_small_real_refinement_matrix)

        for forbidden in (
            "write_text",
            "write_bytes",
            "report_path",
            "attempt_path",
            "lock_path",
            "execute_prepared_bundle_synthetically",
        ):
            self.assertNotIn(forbidden, source_text)

    def test_terminal_s1eb31_artifacts_remain_unchanged(self) -> None:
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        run_small_real_refinement_matrix(
            self.source.history_ab,
            self.source.history_ba,
            self.field,
            self.state,
        )
        after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
