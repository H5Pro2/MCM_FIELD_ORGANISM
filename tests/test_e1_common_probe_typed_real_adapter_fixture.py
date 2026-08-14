from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_real_binding_contract import build_e1_common_probe_real_binding_contract
from mcm_field_organism.e1_common_probe_typed_real_adapter_fixture import E1CommonProbeTypedRealAdapterFixtureError, run_e1_common_probe_typed_real_adapter_fixture


class E1CommonProbeTypedRealAdapterFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = build_e1_common_probe_real_binding_contract()

    def test_complete_typed_zero_step_adapter(self) -> None:
        result = run_e1_common_probe_typed_real_adapter_fixture(self.contract)
        self.assertEqual((6, 24, 48, 48), (result.plan_receipt_count, result.formation_receipt_count, result.fresh_field_receipt_count, result.probe_receipt_count))
        self.assertTrue(result.all_plan_routes_exact)
        self.assertTrue(result.all_state_routes_exact)
        self.assertTrue(result.all_probe_routes_exact)
        self.assertEqual(0, result.field_steps_executed)

    def test_only_adapter_implementation_is_confirmed(self) -> None:
        result = run_e1_common_probe_typed_real_adapter_fixture(self.contract)
        self.assertTrue(result.typed_real_adapter_implemented)
        self.assertFalse(result.real_kernel_execution_permitted)
        self.assertFalse(result.research_decision_permitted)
        self.assertFalse(result.memory_claim_permitted)

    def test_untyped_plan_kernel_fails_closed(self) -> None:
        with self.assertRaises(E1CommonProbeTypedRealAdapterFixtureError):
            run_e1_common_probe_typed_real_adapter_fixture(self.contract, plan_kernel=lambda contact, refinement, probe: None)

    def test_adapter_contains_no_direct_real_kernel_or_write_path(self) -> None:
        source = inspect.getsource(run_e1_common_probe_typed_real_adapter_fixture)
        for forbidden in ("run_prepared_real_formation_arm_in_memory", "advance_frozen_e1_fast_shared_field_transient", "advance_neutral_fast_shared_field_transient", "open(", "write_text", "write_bytes"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
