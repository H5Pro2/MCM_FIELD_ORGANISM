from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from mcm_field_organism.dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)
from mcm_field_organism.dynamic_substrate_s1jq_adapter_refinement_readiness_precheck import (
    build_dts1_s1jq_adapter_refinement_readiness_precheck,
)
from mcm_field_organism.dynamic_substrate_s1jr_corrected_role_refinement_contract import (
    DTS1S1JRCorrectedRoleRefinementContractError,
    S1_JR_DECISION,
    build_dts1_s1jr_corrected_role_refinement_contract,
)


class DTS1S1JRCorrectedRoleRefinementContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jr_corrected_role_refinement_contract()

    def test_binds_exact_s1jq_s1ja_and_s1jk_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1jq_adapter_refinement_readiness_precheck().audit_digest, contract.source_s1jq_digest)
        self.assertEqual(build_dts1_s1ja_finite_configuration_matrix_contract().contract_digest, contract.source_s1ja_digest)
        self.assertEqual(build_dts1_s1jk_corrected_monotonic_interval_contract().contract_digest, contract.source_s1jk_digest)

    def test_preserves_labels_and_primary(self) -> None:
        self.assertEqual((2, 4, 8), self._contract().control_labels)
        self.assertEqual(4, self._contract().primary_label)

    def test_classifies_two_exact_and_four_native_roles(self) -> None:
        contract = self._contract()
        self.assertEqual((2, 4, 6), (contract.exact_control_role_count, contract.native_refinement_role_count, contract.baseline_role_count))
        self.assertEqual(("B1", "B2"), tuple(row[0] for row in contract.role_refinement_records if not row[3]))

    def test_b1_b2_use_one_exact_full_interval_call(self) -> None:
        rows = self._contract().role_refinement_records[:2]
        self.assertTrue(all(row[1] == "EXACT_FULL_INTERVAL_BIT_IDENTITY_CONTROL" for row in rows))
        self.assertIn("closed-spectral", rows[0][4])
        self.assertIn("matrix-exponential", rows[1][4])
        self.assertTrue(all("bit-identical" in row[5] for row in rows))

    def test_exact_labels_are_independent_and_never_enter_kernel(self) -> None:
        rules = " ".join(self._contract().exact_control_rules)
        self.assertIn("same-complete-materialized-field-and-private-context", rules)
        self.assertIn("does-not-enter-the-kernel-input", rules)
        self.assertIn("no-output-field-or-private-state-is-carried", rules)
        self.assertIn("must-be-bit-identical", rules)

    def test_b3_through_b6_forward_native_refinement(self) -> None:
        rows = self._contract().role_refinement_records[2:]
        self.assertTrue(all(row[1] == "NATIVE_INTERNAL_REFINEMENT" and row[3] for row in rows))
        rules = " ".join(self._contract().native_refinement_rules)
        self.assertIn("existing-F3-runtime-refinement-argument", rules)
        self.assertIn("without-intermediate-SharedMCMField-time-commits", rules)

    def test_all_roles_preserve_one_common_physical_window(self) -> None:
        rules = " ".join(self._contract().common_time_rules)
        self.assertIn("bit-identical-S1-JO-clock", rules)
        self.assertIn("no-role-creates-fractional-ticks", rules)
        self.assertIn("alternative-repeats-from-one-prestate", rules)

    def test_supersedes_only_conflicting_refinement_language(self) -> None:
        rules = " ".join(self._contract().supersession)
        self.assertIn("for-B1-and-B2-only", rules)
        self.assertIn("preserve-all-S1-JP-information", rules)
        self.assertIn("carry-provenance-bit-for-bit", rules)

    def test_fail_closed_on_exact_nonidentity_or_native_drift(self) -> None:
        rules = " ".join(self._contract().fail_closed_rules)
        self.assertIn("non-bit-identical-output", rules)
        self.assertIn("result-dependent-native-refinement", rules)
        self.assertIn("blocks-the-complete-role-block-case", rules)

    def test_binds_fourteen_technical_classes(self) -> None:
        contract = self._contract()
        self.assertEqual(14, contract.technical_test_count)
        self.assertEqual(tuple(f"T{index:02d}" for index in range(1, 15)), tuple(row[0] for row in contract.technical_test_matrix))

    def test_authorizes_implementation_but_executes_nothing(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.corrected_role_refinement_contract_bound)
        self.assertTrue(contract.adapter_implementation_ready)
        self.assertTrue(contract.private_adapter_implementation_authorized_next_stage)
        self.assertFalse(contract.adapters_implemented)
        self.assertFalse(contract.baseline_models_executed)
        self.assertFalse(contract.runtime_integration_present)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_JR_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JRCorrectedRoleRefinementContractError):
            replace(contract, adapter_implementation_ready=False)
        source = inspect.getsource(build_dts1_s1jr_corrected_role_refinement_contract)
        for forbidden in ("advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
