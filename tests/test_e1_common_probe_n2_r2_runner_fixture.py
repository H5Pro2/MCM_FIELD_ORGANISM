from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_runner_fixture import E1CommonProbeN2R2RunnerFixtureError, run_e1_common_probe_n2_r2_runner_fixture
from mcm_field_organism.e1_common_probe_real_binding_contract import build_e1_common_probe_real_binding_contract
from mcm_field_organism.e1_common_probe_small_real_result_audit import audit_e1_common_probe_small_real_result


class E1CommonProbeN2R2RunnerFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = build_e1_common_probe_real_binding_contract()
        self.audit = audit_e1_common_probe_small_real_result()

    def test_exact_bounded_matrix_and_step_plan(self) -> None:
        result = run_e1_common_probe_n2_r2_runner_fixture(self.contract, self.audit)
        self.assertEqual((2, "r2"), (result.contact_count, result.refinement_id))
        self.assertEqual((4, 8), (result.formation_state_count, result.probe_slot_count))
        self.assertEqual((1608, 1600, 3208), (result.planned_formation_steps, result.planned_probe_steps, result.planned_total_steps))
        self.assertEqual(0, result.executed_field_steps)

    def test_routes_are_complete_without_decision(self) -> None:
        result = run_e1_common_probe_n2_r2_runner_fixture(self.contract, self.audit)
        self.assertTrue(result.all_state_routes_exact)
        self.assertTrue(result.all_probe_routes_exact)
        self.assertTrue(result.all_fresh_fields_identical_and_separate)
        self.assertFalse(result.real_execution_permitted)
        self.assertFalse(result.ec46_decision_permitted)

    def test_untyped_plan_fails_closed(self) -> None:
        with self.assertRaises(E1CommonProbeN2R2RunnerFixtureError):
            run_e1_common_probe_n2_r2_runner_fixture(self.contract, self.audit, plan_kernel=lambda contact, refinement, probe: None)

    def test_runner_has_no_direct_real_kernel_or_write_path(self) -> None:
        source = inspect.getsource(run_e1_common_probe_n2_r2_runner_fixture)
        for forbidden in ("run_prepared_real_formation_arm_in_memory", "run_e1_common_probe_real_probe_wrapper", "open(", "write_text", "write_bytes"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
