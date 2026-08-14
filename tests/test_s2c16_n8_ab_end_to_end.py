from __future__ import annotations

from dataclasses import replace
import math
import unittest

from mcm_field_organism.s2_reference_runner import (
    S2ReferenceRunnerError,
    compose_s2c16_n8_ab_reference,
)


class S2C16N8ABEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.b0 = compose_s2c16_n8_ab_reference("b0")
        cls.b2_first = compose_s2c16_n8_ab_reference("b2")
        cls.b2_second = compose_s2c16_n8_ab_reference("b2")

    def test_b0_reference_path_remains_exactly_zero(self) -> None:
        self.assertEqual(0.0, self.b0.a_pair.d_pair)
        self.assertEqual(0.0, self.b0.b_pair.d_pair)
        self.assertEqual(0.0, self.b0.distance.d_world_pair)

    def test_active_b2_composition_is_finite_and_exactly_reproducible(self) -> None:
        self.assertTrue(math.isfinite(self.b2_first.a_pair.d_pair))
        self.assertTrue(math.isfinite(self.b2_first.b_pair.d_pair))
        self.assertTrue(math.isfinite(self.b2_first.distance.d_world_pair))
        self.assertEqual(self.b2_first, self.b2_second)
        self.assertEqual(self.b2_first.digest(), self.b2_second.digest())

    def test_canonical_plans_are_bound_by_four_distinct_digests(self) -> None:
        digests = (*self.b2_first.a_plan_digests, *self.b2_first.b_plan_digests)

        self.assertEqual(4, len(set(digests)))
        self.assertTrue(all(len(value) == 64 for value in digests))

    def test_container_and_distance_provenance_is_closed(self) -> None:
        self.assertEqual(
            self.b2_first.a_pair.d_pair,
            self.b2_first.container.a_d_pair,
        )
        self.assertEqual(
            self.b2_first.b_pair.d_pair,
            self.b2_first.container.b_d_pair,
        )
        self.assertEqual(
            self.b2_first.container.digest(),
            self.b2_first.distance.container_digest,
        )
        self.assertEqual(
            abs(self.b2_first.a_pair.d_pair - self.b2_first.b_pair.d_pair),
            self.b2_first.distance.d_world_pair,
        )

    def test_composition_has_no_decision_or_specificity_role(self) -> None:
        for name in ("decision", "threshold", "world_specificity"):
            self.assertFalse(hasattr(self.b2_first, name))
        with self.assertRaisesRegex(S2ReferenceRunnerError, "only B0 or B2"):
            compose_s2c16_n8_ab_reference("b1")
        with self.assertRaisesRegex(S2ReferenceRunnerError, "provenance"):
            replace(
                self.b2_first,
                distance=replace(
                    self.b2_first.distance,
                    container_digest="0" * 64,
                ),
            )


if __name__ == "__main__":
    unittest.main()
