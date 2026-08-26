from __future__ import annotations

import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._acm1h_s1uk_matrix import (
    HISTORIES,
    S1UK_OUTCOMES,
    s1uk_path_plan,
)


class S1UKMatrixContractTests(unittest.TestCase):
    def test_bound_plan_has_exactly_the_registered_33_paths(self) -> None:
        plan = s1uk_path_plan()
        self.assertEqual(33, len(plan))
        self.assertEqual(18, sum(row["family"] == "ACM1H" for row in plan))
        self.assertEqual(12, sum(row["family"] == "CGR1" for row in plan))
        self.assertEqual(1, sum(row["family"] == "ACM_OFF" for row in plan))
        self.assertEqual(2, sum(row["family"] == "E1" for row in plan))
        self.assertEqual(33, len({row["path_id"] for row in plan}))
        self.assertEqual(
            {"g0.25_b0.25", "g0.25_b0.5", "g0.5_b0.25", "g0.5_b0.5", "g1_b0.25", "g1_b0.5"},
            {row["config"] for row in plan if row["family"] == "ACM1H"},
        )

    def test_histories_are_the_bound_sign_matched_fixtures(self) -> None:
        self.assertEqual((0.5, 0.5, 0.0), tuple((a - b) for a, b in zip(HISTORIES["G"][0], HISTORIES["G"][0][1:])))
        for left, right in zip(HISTORIES["G"], HISTORIES["O"], strict=True):
            self.assertEqual(
                tuple((a - b) ** 2 for a, b in zip(left, left[1:])),
                tuple((a - b) ** 2 for a, b in zip(right, right[1:])),
            )

    def test_outcomes_and_runtime_stay_private(self) -> None:
        self.assertEqual(3, len(S1UK_OUTCOMES))
        for name in ("execute_s1uk_matrix_once", "s1uk_path_plan"):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertFalse(hasattr(current_api, name))

    def test_plan_construction_is_separate_from_matrix_execution(self) -> None:
        self.assertNotIn("execute", s1uk_path_plan.__name__)


if __name__ == "__main__":
    unittest.main()
