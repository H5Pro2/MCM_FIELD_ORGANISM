from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ii_interference_contract import (
    DTS1S1IIInterferenceContractError,
    S1_II_DECISION,
    build_dts1_s1ii_interference_contract,
)


class DTS1S1IIInterferenceContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1ii_interference_contract()

    def test_binds_sources_candidate_and_only_interference_function(self) -> None:
        contract = self._contract()
        self.assertEqual(64, len(contract.source_s1hh_contract_digest))
        self.assertEqual(64, len(contract.source_s1ih_audit_receipt_digest))
        self.assertEqual(
            "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER",
            contract.candidate_id,
        )
        self.assertIn("INTERFERENCE", contract.function_id)
        self.assertFalse(contract.release_or_reuse_proven)

    def test_binds_one_shared_endpoint_and_no_hidden_pool(self) -> None:
        rules = " ".join(self._contract().geometry_rules)
        self.assertIn("open-three-node-line", rules)
        self.assertIn("share-exactly-one-middle-endpoint", rules)
        self.assertIn("one-finite-capacity-ledger-shared", rules)
        self.assertIn("no-new-edge-resource-transport-global-allocator", rules)

    def test_binds_aba_against_time_and_A_matched_gap(self) -> None:
        contract = self._contract()
        self.assertEqual(
            ("ABA_SHARED_ENDPOINT_COMPETITOR", "A_GAP_A_MATCHED_PASSIVE_INTERVAL"),
            contract.arm_ids,
        )
        rules = " ".join(contract.sequence_rules)
        self.assertIn("same-positive-A-contact", rules)
        self.assertIn("same-positive-duration-rates-and-event-boundaries", rules)
        self.assertIn("positive-participation-only-to-B", rules)
        self.assertIn("zero-participation-to-both-edges", rules)
        self.assertIn("same-positive-A-probe", rules)

    def test_requires_direct_shared_free_final_A_and_field_directions(self) -> None:
        contract = self._contract()
        records = " ".join(contract.required_records)
        directions = " ".join(contract.direction_rules)
        self.assertIn("shared-endpoint-free-resource", records)
        self.assertIn("final-A-accepted-engagement", records)
        self.assertIn("strictly-lower-in-ABA-than-A-gap-A", directions)
        self.assertIn("postsequence-common-field-readout-direction", directions)
        self.assertIn("none-may-substitute", directions)

    def test_binds_all_six_controls(self) -> None:
        self.assertEqual(
            {
                "N01_VALUE_IDENTICAL_ABA_REPLAY",
                "N02_B_ZERO_EQUALS_MATCHED_GAP",
                "N03_A0_DISABLED_FIELD_READOUT",
                "N04_FROZEN_PRESEQUENCE_ADAPTER",
                "N05_MATCHED_OR_ABLATED_H",
                "N06_ZERO_A_PROBE_PARTICIPATION",
            },
            {case_id for case_id, _ in self._contract().control_cases},
        )

    def test_binds_all_baselines_without_overclaiming_e1_separation(self) -> None:
        baselines = dict(self._contract().baseline_counterpredictions)
        self.assertEqual(
            {
                "fixed-adapter-and-frozen-e1",
                "leaky-trace-and-integrator",
                "dynamic-two-state-e1",
                "f3-and-const-v",
                "fast-afterimage",
            },
            set(baselines),
        )
        self.assertIn("competition-alone-is-not-distinctive", baselines["dynamic-two-state-e1"])

    def test_is_fail_closed_and_blocks_result_dependent_changes(self) -> None:
        contract = self._contract()
        stopp = " ".join(contract.stopp_conditions)
        self.assertTrue(contract.atomic_decision_required)
        self.assertIn("one-failure-makes-the-whole-interference-audit-STOPP", " ".join(contract.acceptance_rules))
        self.assertIn("result-dependent-fixture-threshold-direction-rate", stopp)
        self.assertIn("partial-commit", stopp)

    def test_selects_no_fixture_equation_runtime_or_execution(self) -> None:
        contract = self._contract()
        for value in (
            contract.fixture_values_selected,
            contract.equation_added_or_changed,
            contract.interference_harness_implemented,
            contract.interference_executed,
            contract.baseline_models_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
            contract.interference_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.technical_field_steps_executed)
        self.assertEqual(0, contract.research_field_steps_executed)
        self.assertEqual(S1_II_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        first = self._contract()
        self.assertEqual(first.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IIInterferenceContractError):
            replace(first, interference_executed=True)
        with self.assertRaises(DTS1S1IIInterferenceContractError):
            replace(first, fixture_values_selected=True)
        source = inspect.getsource(build_dts1_s1ii_interference_contract)
        for forbidden in ("advance_", "execute_", "run_", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
