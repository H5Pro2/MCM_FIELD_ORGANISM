from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_ec75_synthetic_route import (
    run_e1_common_probe_n2_r2_ec75_synthetic_route,
)


class E1CommonProbeN2R2EC75SyntheticRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from tests.test_e1_common_probe_n2_r2_object_handoff import (
            E1CommonProbeN2R2ObjectHandoffTests,
        )

        E1CommonProbeN2R2ObjectHandoffTests.setUpClass()
        cls.handoff = E1CommonProbeN2R2ObjectHandoffTests()._prepare()

    def test_full_route_passes_all_six_gates_and_all_routes(self) -> None:
        result = run_e1_common_probe_n2_r2_ec75_synthetic_route(self.handoff)

        self.assertEqual((4, 8, 8), (
            result.formation_count,
            result.fresh_field_count,
            result.probe_count,
        ))
        self.assertTrue(result.all_six_diagnostic_gates_passed_for_all_formations)
        self.assertTrue(result.all_state_routes_exact)
        self.assertTrue(result.all_backreaction_routes_exact)
        self.assertTrue(result.all_fresh_fields_identical_and_object_separate)

    def test_accounting_is_complete_but_actual_field_steps_stay_zero(self) -> None:
        result = run_e1_common_probe_n2_r2_ec75_synthetic_route(self.handoff)

        self.assertEqual((1608, 1600, 3208), (
            result.accounted_formation_steps,
            result.accounted_probe_steps,
            result.accounted_total_steps,
        ))
        self.assertEqual(0, result.actual_field_steps_executed)
        self.assertFalse(result.real_wrapper_execution_permitted)
        self.assertFalse(result.real_adapter_execution_permitted)
        self.assertFalse(result.real_coordinator_execution_permitted)

    def test_route_is_deterministic(self) -> None:
        first = run_e1_common_probe_n2_r2_ec75_synthetic_route(self.handoff)
        second = run_e1_common_probe_n2_r2_ec75_synthetic_route(self.handoff)

        self.assertEqual(first.result_digest, second.result_digest)
        self.assertEqual(
            first.formation_diagnostic_digests,
            second.formation_diagnostic_digests,
        )

    def test_route_source_has_no_real_execution_or_write_call(self) -> None:
        source = inspect.getsource(run_e1_common_probe_n2_r2_ec75_synthetic_route)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_real_formation_receipt_adapter(",
            "run_e1_common_probe_real_probe_receipt_adapter(",
            "run_e1_common_probe_real_formation_wrapper(",
            "run_e1_common_probe_real_probe_wrapper(",
            "run_prepared_real_formation_arm_in_memory(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
