from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1fp_common_probe_contract import (
    E1FormationS1FPCommonProbeContractError,
    S1_FP_DECISIONS,
    S1_FP_PROBE_ROLES,
    audit_e1_formation_s1fp_common_probe_contract,
)


class E1FormationS1FPCommonProbeContractTests(unittest.TestCase):
    def test_fresh_end_to_end_inventory_is_bound_but_closed(self) -> None:
        result = audit_e1_formation_s1fp_common_probe_contract()
        self.assertEqual(15, result.formation_state_count)
        self.assertEqual(30, result.probe_slot_count)
        self.assertEqual(("r2", "r4", "r8"), result.refinements)
        self.assertFalse(result.owner_authorization_present)
        self.assertFalse(result.field_execution_permitted)

    def test_probe_roles_bind_all_causal_controls(self) -> None:
        result = audit_e1_formation_s1fp_common_probe_contract()
        self.assertEqual(S1_FP_PROBE_ROLES, result.probe_roles)
        self.assertIn("p0-reset-ab", result.probe_roles)
        self.assertIn("e1-probe-feedback-ablated-ba", result.probe_roles)
        self.assertIn("e1-formation-ablated-ab", result.probe_roles)
        self.assertIn("fixed-adapter-ba", result.probe_roles)

    def test_existing_numeric_bounds_are_not_changed(self) -> None:
        result = audit_e1_formation_s1fp_common_probe_contract()
        self.assertEqual(1e-12, result.absolute_control_tolerance)
        self.assertEqual(8.0, result.strict_signal_margin)
        self.assertEqual(0.01, result.relative_refinement_limit)
        self.assertEqual(S1_FP_DECISIONS, result.decisions)

    def test_previous_run_state_and_authorization_cannot_be_reused(self) -> None:
        result = audit_e1_formation_s1fp_common_probe_contract()
        self.assertTrue(result.fresh_formation_in_same_process_required)
        self.assertFalse(result.previous_state_or_authorization_reuse_permitted)
        self.assertTrue(result.formed_state_frozen_during_probe_required)

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = audit_e1_formation_s1fp_common_probe_contract()
        second = audit_e1_formation_s1fp_common_probe_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1FormationS1FPCommonProbeContractError):
            replace(first, field_execution_permitted=True)

    def test_builder_runs_no_formation_probe_or_writer(self) -> None:
        source = inspect.getsource(audit_e1_formation_s1fp_common_probe_contract)
        for forbidden in (
            "run_e1_formation_s1fl_once(",
            "run_small_five_arm_formation_in_memory(",
            "advance_neutral_fast_shared_field_transient(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
