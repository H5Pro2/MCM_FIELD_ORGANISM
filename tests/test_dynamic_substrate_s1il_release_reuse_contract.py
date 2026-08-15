from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1il_release_reuse_contract import (
    DTS1S1ILReleaseReuseContractError,
    S1_IL_DECISION,
    build_dts1_s1il_release_reuse_contract,
)


class DTS1S1ILReleaseReuseContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1il_release_reuse_contract()

    def test_binds_s1hh_and_s1ik_without_claiming_results(self) -> None:
        contract = self._contract()
        self.assertEqual(64, len(contract.source_s1hh_contract_digest))
        self.assertEqual(64, len(contract.source_s1ik_audit_receipt_digest))
        self.assertFalse(contract.release_proven)
        self.assertFalse(contract.reuse_proven)
        self.assertFalse(contract.e1_nonreducibility_proven)

    def test_binds_one_shared_endpoint_and_post_A_load_state(self) -> None:
        rules = " ".join(self._contract().geometry_rules)
        self.assertIn("open-three-node-line", rules)
        self.assertIn("share-exactly-one-middle-endpoint", rules)
        self.assertIn("post-A-load-anatomy-with-positive-refractory", rules)
        self.assertIn("no-new-edge-resource-transport", rules)

    def test_isolates_only_recovery_channel_during_zero_contact(self) -> None:
        rules = " ".join(self._contract().sequence_rules)
        self.assertIn("zero-edge-participation", rules)
        self.assertIn("only-the-refractory-to-free-recovery-channel", rules)
        self.assertIn("must-not-change-conductive-turnover", rules)
        self.assertIn("value-identical-positive-B-probe", rules)

    def test_requires_direct_release_and_reuse_ledgers_separately(self) -> None:
        records = " ".join(self._contract().required_records)
        directions = " ".join(self._contract().direction_rules)
        self.assertIn("recovery-channel-transfer", records)
        self.assertIn("additional-B-engagement-kept-as-separate", records)
        self.assertIn("strictly-higher-after-recovery-on", directions)
        self.assertIn("neither-a-field-output", directions)

    def test_binds_all_seven_controls(self) -> None:
        self.assertEqual(
            {
                "N01_VALUE_IDENTICAL_SEQUENCE_REPLAY",
                "N02_RECOVERY_ZERO_EQUALS_RECOVERY_OFF",
                "N03_ZERO_REFRACTORY_SOURCE",
                "N04_ZERO_B_PROBE_PARTICIPATION",
                "N05_A0_DISABLED_FIELD_READOUT",
                "N06_FROZEN_PRERELEASE_ADAPTER",
                "N07_MATCHED_OR_ABLATED_H",
            },
            {case_id for case_id, _ in self._contract().control_cases},
        )

    def test_binds_all_baselines_and_keeps_e1_limit(self) -> None:
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
        self.assertIn("release-and-reuse-alone-are-not-distinctive", baselines["dynamic-two-state-e1"])

    def test_is_fail_closed_and_forbids_field_only_inference(self) -> None:
        contract = self._contract()
        stopp = " ".join(contract.stopp_conditions)
        self.assertTrue(contract.atomic_decision_required)
        self.assertIn("one-failure-makes-the-whole-release-reuse-audit-STOPP", " ".join(contract.acceptance_rules))
        self.assertIn("release-is-inferred-only-from-field-amplitude", stopp)
        self.assertIn("result-dependent-fixture-threshold-direction-rate", stopp)

    def test_selects_no_fixture_equation_runtime_or_execution(self) -> None:
        contract = self._contract()
        for value in (
            contract.fixture_values_selected,
            contract.equation_added_or_changed,
            contract.harness_implemented,
            contract.release_reuse_executed,
            contract.baseline_models_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.technical_field_steps_executed)
        self.assertEqual(0, contract.research_field_steps_executed)
        self.assertEqual(S1_IL_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        first = self._contract()
        self.assertEqual(first.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1ILReleaseReuseContractError):
            replace(first, release_reuse_executed=True)
        with self.assertRaises(DTS1S1ILReleaseReuseContractError):
            replace(first, fixture_values_selected=True)
        source = inspect.getsource(build_dts1_s1il_release_reuse_contract)
        for forbidden in ("advance_", "execute_", "run_", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
