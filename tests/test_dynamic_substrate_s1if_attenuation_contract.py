from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1if_attenuation_contract import (
    DTS1S1IFAttenuationContractError,
    S1_IF_DECISION,
    build_dts1_s1if_attenuation_contract,
)


class DTS1S1IFAttenuationContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1if_attenuation_contract()

    def test_binds_sources_candidate_and_only_attenuation_function(self) -> None:
        contract = self._contract()
        self.assertEqual(64, len(contract.source_s1hh_contract_digest))
        self.assertEqual(64, len(contract.source_s1ie_audit_receipt_digest))
        self.assertEqual(
            "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER",
            contract.candidate_id,
        )
        self.assertIn("ATTENUATION", contract.function_id)
        self.assertFalse(contract.broader_function_proven)

    def test_binds_equal_contacts_continuous_anatomy_and_common_probe(self) -> None:
        contract = self._contract()
        rules = " ".join(contract.sequence_rules)
        self.assertIn("at-least-three-consecutive-A-contacts", rules)
        self.assertIn("same-positive-local-participation", rules)
        self.assertIn("anatomy-carries-continuously", rules)
        self.assertIn("value-identical-registered-S-H-probe-prestate", rules)
        self.assertIn("do-not-commit-resource-poststates", rules)

    def test_requires_direct_ledger_and_field_readout_directions(self) -> None:
        contract = self._contract()
        records = " ".join(contract.required_records)
        directions = " ".join(contract.direction_rules)
        self.assertIn("accepted-target-edge-engagement", records)
        self.assertIn("oriented-target-edge-S-contrast", records)
        self.assertIn("strict-decrease-in-accepted-engagement", directions)
        self.assertIn("strict-directed-attenuation", directions)
        self.assertIn("neither-may-substitute", directions)

    def test_binds_all_required_controls(self) -> None:
        contract = self._contract()
        self.assertEqual(
            {
                "N01_VALUE_IDENTICAL_REPLAY",
                "N02_A0_DISABLED_CANDIDATE",
                "N03_FROZEN_PRESEQUENCE_ADAPTER",
                "N04_MATCHED_OR_ABLATED_H",
                "N05_ZERO_PARTICIPATION",
            },
            {case_id for case_id, _ in contract.control_cases},
        )

    def test_binds_all_baselines_without_overclaiming_e1_separation(self) -> None:
        contract = self._contract()
        baselines = dict(contract.baseline_counterpredictions)
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
        self.assertIn("attenuation-alone-is-not-distinctive", baselines["dynamic-two-state-e1"])

    def test_is_fail_closed_and_blocks_result_dependent_changes(self) -> None:
        contract = self._contract()
        stopp = " ".join(contract.stopp_conditions)
        self.assertTrue(contract.atomic_decision_required)
        self.assertIn("one-failure-makes-the-whole-attenuation-audit-STOPP", " ".join(contract.acceptance_rules))
        self.assertIn("result-dependent-fixture-count", stopp)
        self.assertIn("resource-reset-contact-counter-phase-detector", stopp)

    def test_selects_no_fixture_equation_runtime_or_execution(self) -> None:
        contract = self._contract()
        self.assertFalse(contract.exact_contact_count_selected)
        self.assertFalse(contract.fixture_values_selected)
        self.assertFalse(contract.equation_added_or_changed)
        self.assertFalse(contract.attenuation_harness_implemented)
        self.assertFalse(contract.attenuation_executed)
        self.assertFalse(contract.baseline_models_executed)
        self.assertFalse(contract.runtime_integration_present)
        self.assertFalse(contract.research_execution_permitted)
        self.assertEqual(0, contract.technical_field_steps_executed)
        self.assertEqual(0, contract.research_field_steps_executed)
        self.assertEqual(S1_IF_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        first = self._contract()
        second = self._contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1IFAttenuationContractError):
            replace(first, attenuation_executed=True)
        with self.assertRaises(DTS1S1IFAttenuationContractError):
            replace(first, exact_contact_count_selected=True)
        source = inspect.getsource(build_dts1_s1if_attenuation_contract)
        for forbidden in ("advance_", "execute_", "run_", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
