from __future__ import annotations

import unittest

from mcm_field_organism.w7bo_const_v_convergence_evaluator import (
    W7BOConstVConvergenceEvaluatorError,
    evaluate_w7bo_const_v_convergence,
)


class W7BOConstVConvergenceEvaluatorTests(unittest.TestCase):
    def test_incomplete_inventory_is_rejected(self) -> None:
        with self.assertRaises(W7BOConstVConvergenceEvaluatorError):
            evaluate_w7bo_const_v_convergence((), object(), object())

    def test_evaluator_is_not_publicly_exported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(mcm_field_organism, "evaluate_w7bo_const_v_convergence"))
        self.assertFalse(hasattr(current_api, "evaluate_w7bo_const_v_convergence"))


if __name__ == "__main__":
    unittest.main()
