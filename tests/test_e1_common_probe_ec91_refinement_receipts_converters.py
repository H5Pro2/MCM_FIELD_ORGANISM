from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec91_refinement_receipts_converters import (
    E1CommonProbeEC91RefinementReceiptConverterError,
    convert_e1_common_probe_ec91_formation_output,
    run_e1_common_probe_ec91_synthetic_fixture,
    _synthetic_formation_output,
)
from tests.test_e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffsTests,
)


class E1CommonProbeEC91RefinementReceiptsConvertersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1CommonProbeEC89R4R8ObjectHandoffsTests.setUpClass()
        cls.handoffs = E1CommonProbeEC89R4R8ObjectHandoffsTests()._prepare()

    def test_full_synthetic_r4_r8_conversion_is_exact(self) -> None:
        result = run_e1_common_probe_ec91_synthetic_fixture(self.handoffs)
        self.assertEqual(("r4", "r8"), result.refinement_ids)
        self.assertEqual(
            (("r4", 3216, 3200, 6416), ("r8", 6432, 6400, 12832)),
            result.accounted_budgets,
        )
        self.assertTrue(all(len(items) == 4 for items in result.formations))
        self.assertTrue(all(len(items) == 8 for items in result.probes))
        self.assertTrue(result.all_routes_exact)
        self.assertEqual(0, result.actual_field_steps_executed)

    def test_fixture_is_deterministic(self) -> None:
        first = run_e1_common_probe_ec91_synthetic_fixture(self.handoffs)
        second = run_e1_common_probe_ec91_synthetic_fixture(self.handoffs)
        self.assertEqual(first.result_digest, second.result_digest)

    def test_wrong_refinement_output_fails_closed(self) -> None:
        r4_handoff, r8_handoff = self.handoffs.handoffs
        r4_slot = r4_handoff.formation_slots[0]
        r8_slot = next(
            item
            for item in r8_handoff.formation_slots
            if item.binding.state_role == r4_slot.binding.state_role
        )
        output = _synthetic_formation_output(r8_handoff, r8_slot)
        with self.assertRaises(E1CommonProbeEC91RefinementReceiptConverterError):
            convert_e1_common_probe_ec91_formation_output(
                r4_handoff, r4_slot, output
            )

    def test_fixture_calls_no_wrapper_kernel_or_writer(self) -> None:
        source = inspect.getsource(run_e1_common_probe_ec91_synthetic_fixture)
        for forbidden in (
            "run_e1_common_probe_real_formation_wrapper(",
            "run_e1_common_probe_real_probe_wrapper(",
            "run_prepared_real_formation_arm_in_memory(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_neutral_fast_shared_field_transient(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
