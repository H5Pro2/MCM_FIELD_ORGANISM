from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_acceptance_contract import (
    build_e1_common_probe_acceptance_contract,
)
from mcm_field_organism.e1_common_probe_synthetic_runner_fixture import (
    E1CommonProbeSyntheticRunnerFixtureError,
    run_e1_common_probe_synthetic_runner_fixture,
)


class E1CommonProbeSyntheticRunnerFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = build_e1_common_probe_acceptance_contract()

    def test_all_roles_and_refinements_are_integrated(self) -> None:
        result = run_e1_common_probe_synthetic_runner_fixture(self.contract)
        self.assertEqual(24, result.sample_count)
        self.assertTrue(result.all_roles_present_per_refinement)
        self.assertTrue(result.common_neuron_order_preserved)
        self.assertEqual(0, result.field_steps_executed)

    def test_registered_decider_receives_converged_synthetic_fixture(self) -> None:
        result = run_e1_common_probe_synthetic_runner_fixture(self.contract)
        self.assertEqual(
            "NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE",
            result.synthetic_decision,
        )
        self.assertLess(result.fine_s, result.coarse_s)
        self.assertLess(result.fine_h, result.coarse_h)
        self.assertEqual(0.0, result.maximum_p0_reset_s)
        self.assertEqual(0.0, result.maximum_feedback_ablation_s)
        self.assertEqual(0.0, result.maximum_formation_ablation_s)
        self.assertFalse(result.research_decision_permitted)

    def test_untyped_kernel_fails_closed(self) -> None:
        with self.assertRaises(E1CommonProbeSyntheticRunnerFixtureError):
            run_e1_common_probe_synthetic_runner_fixture(
                self.contract,
                sample_kernel=lambda role, refinement: None,
            )

    def test_runner_contains_no_field_or_write_path(self) -> None:
        source = inspect.getsource(run_e1_common_probe_synthetic_runner_fixture)
        for forbidden in (
            "run_neutral_asynchronous_field",
            "run_prepared_real_formation_arm_in_memory",
            "open(",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
