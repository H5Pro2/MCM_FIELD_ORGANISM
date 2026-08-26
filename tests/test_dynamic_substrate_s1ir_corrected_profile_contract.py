from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ip_joint_baseline_contract import (
    build_dts1_s1ip_joint_baseline_contract,
)
from mcm_field_organism.dynamic_substrate_s1iq_compatibility_precheck import (
    build_dts1_s1iq_compatibility_precheck,
)
from mcm_field_organism.dynamic_substrate_s1ir_corrected_profile_contract import (
    DTS1S1IRCorrectedProfileContractError,
    S1_IR_DECISION,
    build_dts1_s1ir_corrected_profile_contract,
)


class DTS1S1IRCorrectedProfileContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1ir_corrected_profile_contract()

    def test_binds_s1iq_and_supersedes_exact_s1ip(self) -> None:
        corrected = self._contract()
        self.assertEqual(build_dts1_s1iq_compatibility_precheck().audit_digest, corrected.source_s1iq_audit_digest)
        self.assertEqual(build_dts1_s1ip_joint_baseline_contract().contract_digest, corrected.superseded_s1ip_digest)
        self.assertFalse(corrected.s1ip_valid_for_future_baseline_work)

    def test_corrects_only_two_block_counts_and_total(self) -> None:
        original = build_dts1_s1ip_joint_baseline_contract()
        corrected = self._contract()
        self.assertEqual((8, 8, 6, 6), tuple(item[2] for item in corrected.profile_blocks))
        self.assertEqual(28, corrected.profile_component_count)
        self.assertEqual(tuple(item[:2] for item in original.profile_blocks), tuple(item[:2] for item in corrected.profile_blocks))

    def test_preserves_roles_rules_gates_and_decisions(self) -> None:
        original = build_dts1_s1ip_joint_baseline_contract()
        corrected = self._contract()
        for role in (
            "reference_receipts",
            "executable_baseline_roles",
            "structural_baseline_roles",
            "profile_rules",
            "structural_gates",
            "allowed_baseline_inputs",
            "forbidden_baseline_inputs",
            "parameter_rules",
            "decision_order",
            "stopp_conditions",
            "forbidden_interpretations",
        ):
            self.assertEqual(getattr(original, role), getattr(corrected, role))

    def test_changes_only_global_metric_cardinality_labels(self) -> None:
        original = build_dts1_s1ip_joint_baseline_contract().comparison_metrics
        corrected = self._contract().comparison_metrics
        self.assertEqual(original[2:], corrected[2:])
        self.assertEqual(tuple(item.replace("36", "28") for item in original[:2]), corrected[:2])

    def test_reauthorizes_static_compatibility_audit_only(self) -> None:
        corrected = self._contract()
        self.assertTrue(corrected.corrected_profile_contract_valid)
        self.assertTrue(corrected.compatibility_audit_authorized_next_stage)
        self.assertFalse(corrected.baseline_signatures_classified)
        self.assertEqual(S1_IR_DECISION, corrected.decision)

    def test_selects_no_values_implementation_runtime_or_execution(self) -> None:
        corrected = self._contract()
        for value in (
            corrected.parameter_values_selected,
            corrected.comparison_threshold_selected,
            corrected.geometry_adapters_implemented,
            corrected.profile_container_implemented,
            corrected.baseline_models_executed,
            corrected.joint_comparison_executed,
            corrected.runtime_integration_present,
            corrected.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (corrected.technical_field_steps_executed, corrected.research_field_steps_executed))

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        corrected = self._contract()
        self.assertEqual(corrected.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IRCorrectedProfileContractError):
            replace(corrected, profile_component_count=36)
        with self.assertRaises(DTS1S1IRCorrectedProfileContractError):
            replace(corrected, profile_rules=())
        source = inspect.getsource(build_dts1_s1ir_corrected_profile_contract)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
