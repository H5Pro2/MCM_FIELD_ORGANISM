from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1iw_exposure_ordering_precheck import (
    build_dts1_s1iw_exposure_ordering_precheck,
)
from mcm_field_organism.dynamic_substrate_s1ix_corrected_event_boundary_contract import (
    DTS1S1IXCorrectedEventBoundaryContractError,
    S1_IX_DECISION,
    build_dts1_s1ix_corrected_event_boundary_contract,
)


class DTS1S1IXCorrectedEventBoundaryContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1ix_corrected_event_boundary_contract()

    def test_binds_exact_s1iw_precheck(self) -> None:
        self.assertEqual(
            build_dts1_s1iw_exposure_ordering_precheck().audit_digest,
            self._contract().source_s1iw_digest,
        )

    def test_binds_four_boundary_roles_with_exact_participation_structure(self) -> None:
        roles = dict(self._contract().boundary_roles)
        self.assertEqual(4, self._contract().boundary_role_count)
        self.assertIn("positive-S1-HK-participation-on-A", roles["A_BOUNDARY"])
        self.assertIn("positive-on-B", roles["B_BOUNDARY"])
        self.assertIn("exact-zero-S1-HK-participation-on-A-and-B", roles["GAP_BOUNDARY"])

    def test_boundary_replaces_only_sh_without_time_or_model_step(self) -> None:
        rules = " ".join(self._contract().boundary_operator_rules)
        self.assertIn("replace-only-the-exposed-three-node-S-H", rules)
        self.assertIn("preserve-DTS1-anatomy-B1-fixed-adapter-B2-L", rules)
        self.assertIn("consume-zero-time-call-no-model-equation", rules)

    def test_participation_is_derived_after_clamp(self) -> None:
        rules = " ".join(self._contract().active_interval_rules)
        self.assertIn("from-the-clamped-S-prestate-before-each-resource-active-interval", rules)
        self.assertIn("all-node-zero-receptor-contact", rules)

    def test_pik_and_pin_have_aligned_boundary_active_pairs(self) -> None:
        pik = self._contract().p_ik_schedule
        pin = self._contract().p_in_schedule
        self.assertEqual(("A_BOUNDARY", "B_BOUNDARY", "A_BOUNDARY"), tuple(row[2] for row in pik[:3]))
        self.assertEqual(("A_BOUNDARY", "GAP_BOUNDARY", "A_BOUNDARY"), tuple(row[2] for row in pik[3:6]))
        self.assertEqual(("A_BOUNDARY", "GAP_BOUNDARY", "B_BOUNDARY"), tuple(pin[index][2] for index in (0, 2, 4)))

    def test_pin_keeps_only_recovery_as_internal_arm_difference(self) -> None:
        rules = " ".join(self._contract().intervention_rules)
        self.assertIn("only-the-internal-DTS1-recovery-channel-differs", rules)
        self.assertIn("B1-through-B6-remain-parameter-and-configuration-identical", rules)

    def test_supersedes_only_old_carry_rule_and_preserves_profile_quarantine(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.old_within_history_sh_carry_rule_superseded)
        self.assertTrue(contract.temporal_alignment_contract_valid)
        preserved = " ".join(contract.preserved_s1iv_rules)
        self.assertIn("old-P_IK-and-P_IN-field-vector-quarantine", preserved)

    def test_selects_no_values_implementation_or_execution(self) -> None:
        contract = self._contract()
        for value in (
            contract.boundary_values_selected,
            contract.durations_selected,
            contract.configuration_values_selected,
            contract.configuration_digests_bound,
            contract.boundary_operator_implemented,
            contract.fixtures_implemented,
            contract.baseline_models_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_IX_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IXCorrectedEventBoundaryContractError):
            replace(contract, temporal_alignment_contract_valid=False)
        with self.assertRaises(DTS1S1IXCorrectedEventBoundaryContractError):
            replace(contract, boundary_values_selected=True)
        source = inspect.getsource(build_dts1_s1ix_corrected_event_boundary_contract)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
