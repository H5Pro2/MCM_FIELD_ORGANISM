from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_positive_step_receipt_contract import (
    E1CommonProbeN2R2PositiveStepReceiptContractError,
    build_e1_common_probe_n2_r2_positive_step_receipt_fixture,
)
from tests.test_e1_common_probe_n2_r2_object_handoff import (
    E1CommonProbeN2R2ObjectHandoffTests,
)


class E1CommonProbeN2R2PositiveStepReceiptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = E1CommonProbeN2R2ObjectHandoffTests
        source.setUpClass()
        cls.handoff = source(methodName="test_carries_all_real_objects_without_field_steps")._prepare()

    def test_positive_accounting_is_exact_without_real_execution(self) -> None:
        result = build_e1_common_probe_n2_r2_positive_step_receipt_fixture(self.handoff)
        self.assertEqual((4, 8), (result.formation_count, result.probe_count))
        self.assertEqual((1608, 1600, 3208), (
            result.accounted_formation_steps,
            result.accounted_probe_steps,
            result.accounted_total_steps,
        ))
        self.assertEqual(0, result.actual_field_steps_executed)
        self.assertFalse(result.real_wrapper_execution_permitted)

    def test_role_and_backreaction_routes_are_preserved(self) -> None:
        result = build_e1_common_probe_n2_r2_positive_step_receipt_fixture(self.handoff)
        self.assertTrue(result.all_role_routes_exact)
        self.assertTrue(result.all_positive_step_bounds_exact)
        self.assertEqual((None, None), (
            result.probes[0].selected_state_role,
            result.probes[1].selected_state_role,
        ))
        self.assertFalse(result.probes[4].backreaction_enabled)
        self.assertFalse(result.probes[5].backreaction_enabled)

    def test_wrong_positive_step_count_fails_closed(self) -> None:
        result = build_e1_common_probe_n2_r2_positive_step_receipt_fixture(self.handoff)
        with self.assertRaises(E1CommonProbeN2R2PositiveStepReceiptContractError):
            replace(result.formations[0], accounted_field_steps=401)
        with self.assertRaises(E1CommonProbeN2R2PositiveStepReceiptContractError):
            replace(result.probes[0], accounted_field_steps=199)

    def test_fixture_has_no_wrapper_kernel_or_write_path(self) -> None:
        source = inspect.getsource(build_e1_common_probe_n2_r2_positive_step_receipt_fixture)
        for forbidden in (
            "run_e1_common_probe_real_formation_wrapper(",
            "build_e1_common_probe_fresh_field(",
            "run_e1_common_probe_real_probe_wrapper(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
