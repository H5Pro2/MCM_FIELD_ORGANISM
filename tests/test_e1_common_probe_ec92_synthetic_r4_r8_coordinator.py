from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec91_refinement_receipts_converters import (
    run_e1_common_probe_ec91_synthetic_fixture,
)
from mcm_field_organism.e1_common_probe_ec92_synthetic_r4_r8_coordinator import (
    S1_EC92_EXPECTED_SCALARS,
    run_e1_common_probe_ec92_synthetic_coordinator,
)
from tests.test_e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffsTests,
)


class E1CommonProbeEC92SyntheticR4R8CoordinatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1CommonProbeEC89R4R8ObjectHandoffsTests.setUpClass()
        cls.handoffs = E1CommonProbeEC89R4R8ObjectHandoffsTests()._prepare()
        cls.fixture = run_e1_common_probe_ec91_synthetic_fixture(cls.handoffs)

    def test_complete_atomic_r4_r8_result(self) -> None:
        result = run_e1_common_probe_ec92_synthetic_coordinator(
            self.handoffs, self.fixture
        )
        self.assertEqual((("r4", 8), ("r8", 8)), result.fresh_field_counts)
        self.assertEqual((("r4", 6416), ("r8", 12832)), result.accounted_budgets)
        self.assertEqual(
            S1_EC92_EXPECTED_SCALARS,
            tuple(
                (item.refinement_id, item.contrast_scalars)
                for item in result.scalar_receipts
            ),
        )
        self.assertTrue(result.atomic_scalar_return)
        self.assertEqual(0, result.actual_field_steps_executed)

    def test_all_sixteen_fields_are_digest_identical_and_object_separate(self) -> None:
        result = run_e1_common_probe_ec92_synthetic_coordinator(
            self.handoffs, self.fixture
        )
        fields = [item.field for group in result.fresh_fields for item in group]
        self.assertEqual(16, len({id(item) for item in fields}))
        self.assertTrue(result.all_fresh_fields_identical_and_object_separate)

    def test_result_is_deterministic(self) -> None:
        first = run_e1_common_probe_ec92_synthetic_coordinator(
            self.handoffs, self.fixture
        )
        second = run_e1_common_probe_ec92_synthetic_coordinator(
            self.handoffs, self.fixture
        )
        self.assertEqual(first.result_digest, second.result_digest)

    def test_no_field_kernel_wrapper_or_writer_is_called(self) -> None:
        source = inspect.getsource(run_e1_common_probe_ec92_synthetic_coordinator)
        for forbidden in (
            "run_e1_common_probe_real_formation_wrapper(",
            "run_e1_common_probe_real_probe_wrapper(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_neutral_fast_shared_field_transient(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
