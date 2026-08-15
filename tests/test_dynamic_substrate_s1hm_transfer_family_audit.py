from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hm_transfer_family_audit import (
    DTS1S1HMTransferFamilyAuditError,
    S1_HM_DECISION,
    audit_dts1_s1hm_transfer_family,
)


class DTS1S1HMTransferFamilyAuditTests(unittest.TestCase):
    def _audit(self):
        return audit_dts1_s1hm_transfer_family()

    def test_audits_exactly_one_three_compartment_family(self) -> None:
        audit = self._audit()
        self.assertEqual(1, audit.audited_family_count)
        self.assertEqual(
            "LOCAL_BOUNDED_THREE_COMPARTMENT_TURNOVER",
            audit.family_id,
        )
        self.assertEqual(
            {
                "J_bind": "k_bind*p_e*2*min(f_i,f_j)",
                "J_turn": "k_turn*b_e",
                "J_rec": "k_rec*u_e",
            },
            dict(audit.flux_family),
        )

    def test_family_preserves_cycle_and_has_direct_partition_counterprediction(self) -> None:
        audit = self._audit()
        self.assertEqual("J_bind-J_turn", dict(audit.state_balance)["d_b_e/dt"])
        self.assertEqual("J_turn-J_rec", dict(audit.state_balance)["d_u_e/dt"])
        self.assertTrue(audit.direct_partition_counterprediction_exists)
        self.assertTrue(all(value for _, value in audit.checks))

    def test_zulassen_is_engineering_only_and_keeps_baseline_stop_lines(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.explicit_engineering_assumption)
        self.assertTrue(audit.known_three_compartment_material_family)
        self.assertFalse(audit.mcm_intrinsic_nature_claim)
        self.assertIn(
            "registered-leaky-or-integrator-baseline-reproduces-all-required-profiles",
            audit.stop_conditions_remaining,
        )
        self.assertEqual(S1_HM_DECISION, audit.decision)

    def test_selects_no_values_integrator_backreaction_runtime_or_effect(self) -> None:
        audit = self._audit()
        for value in (
            audit.parameter_values_selected,
            audit.discrete_integrator_selected,
            audit.conflict_resolution_selected,
            audit.field_backreaction_selected,
            audit.runtime_implemented,
            audit.functional_effect_proven,
            audit.execution_permitted,
            audit.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, audit.field_steps_executed)

    def test_audit_is_deterministic_tamper_evident_and_static(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1HMTransferFamilyAuditError):
            replace(audit, field_backreaction_selected=True)
        with self.assertRaises(DTS1S1HMTransferFamilyAuditError):
            replace(audit, audited_family_count=2)
        source = inspect.getsource(audit_dts1_s1hm_transfer_family)
        for forbidden in ("advance_", "solve_ivp", "field_runner", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
