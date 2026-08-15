from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hh_function_falsification_contract import (
    DynamicSubstrateS1HHContractError,
    S1_HH_DECISION,
    build_dynamic_substrate_s1hh_contract,
)


class DynamicSubstrateS1HHFunctionFalsificationContractTests(unittest.TestCase):
    def _contract(self):
        return build_dynamic_substrate_s1hh_contract()

    def test_binds_exactly_one_three_state_resource_candidate(self) -> None:
        contract = self._contract()
        self.assertEqual(1, contract.candidate_count)
        self.assertEqual(3, len(contract.resource_roles))
        self.assertIn("free:", contract.resource_roles[0])
        self.assertIn("conductive-bound:", contract.resource_roles[1])
        self.assertIn("refractory:", contract.resource_roles[2])
        self.assertTrue(contract.frozen_e1_branch_remains_stopped)

    def test_binds_distinct_predictions_for_every_required_baseline(self) -> None:
        contract = self._contract()
        baselines = {name for name, _ in contract.baseline_predictions}
        self.assertEqual(
            {
                "fixed-adapter-and-frozen-e1",
                "leaky-trace-and-integrator",
                "dynamic-two-state-e1",
                "f3-and-const-v",
                "fast-afterimage",
            },
            baselines,
        )
        self.assertTrue(all(prediction for _, prediction in contract.baseline_predictions))

    def test_binds_attenuation_interference_release_and_rejection(self) -> None:
        contract = self._contract()
        measurements = " ".join(contract.required_measurements)
        self.assertIn("attenuation", measurements)
        self.assertIn("A-B-A", measurements)
        self.assertIn("recovery", measurements)
        self.assertGreaterEqual(len(contract.falsification_conditions), 10)
        self.assertFalse(contract.claims_permitted)
        self.assertIn("memory", contract.blocked_claims)

    def test_selects_no_equation_runtime_parameters_or_execution(self) -> None:
        contract = self._contract()
        self.assertFalse(contract.equation_selected)
        self.assertFalse(contract.parameters_selected)
        self.assertFalse(contract.runtime_implemented)
        self.assertFalse(contract.execution_permitted)
        self.assertEqual(0, contract.field_steps_executed)
        self.assertEqual(S1_HH_DECISION, contract.decision)

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = self._contract()
        second = self._contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(DynamicSubstrateS1HHContractError):
            replace(first, candidate_count=2)
        with self.assertRaises(DynamicSubstrateS1HHContractError):
            replace(first, equation_selected=True)

    def test_builder_has_no_runtime_runner_or_writer_calls(self) -> None:
        source = inspect.getsource(build_dynamic_substrate_s1hh_contract)
        for forbidden in (
            "advance_",
            "run_",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
