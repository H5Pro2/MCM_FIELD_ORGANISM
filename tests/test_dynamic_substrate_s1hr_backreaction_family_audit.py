from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hr_backreaction_family_audit import (
    DTS1S1HRBackreactionFamilyAuditError,
    S1_HR_DECISION,
    audit_dts1_s1hr_backreaction_family,
)


class DTS1S1HRBackreactionFamilyAuditTests(unittest.TestCase):
    def _audit(self):
        return audit_dts1_s1hr_backreaction_family()

    def test_audits_exactly_one_parameterless_conductance_family(self) -> None:
        audit = self._audit()
        self.assertEqual(1, audit.audited_family_count)
        self.assertEqual(
            "SYMMETRIC_BOUNDED_CONDUCTANCE_AUGMENTATION",
            audit.family_id,
        )
        self.assertEqual(
            {
                "c_e": "b_e/(2*min(q_i,q_j))",
                "r_0": "1/response_time",
                "r_e_active": "r_0*(1+c_e)",
                "r_e_ablated": "r_0",
                "edge_flux_i_from_j": "r_e*(S_j-S_i)",
            },
            dict(audit.family_form),
        )
        self.assertTrue(audit.parameterless_reader)

    def test_s1hi_ledger_bounds_occupancy_and_edge_rate(self) -> None:
        audit = self._audit()
        self.assertIn(
            "s1hi-ledger-implies-zero-not-greater-than-c_e-not-greater-than-one",
            audit.bounds,
        )
        self.assertIn(
            "active-rate-between-r_0-and-two-times-r_0",
            audit.bounds,
        )

    def test_generator_remains_symmetric_conservative_and_diffusive(self) -> None:
        properties = self._audit().generator_properties
        for required in (
            "symmetric-internal-edge-generator",
            "zero-row-sum-and-no-additive-field-source",
            "negative-semidefinite-diffusion-form",
            "constant-field-nullspace-preserved",
            "receptor-boundary-and-fast-afterimage-unchanged",
        ):
            self.assertIn(required, properties)

    def test_instantaneous_adapter_equivalence_is_not_hidden(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.known_adapter_family)
        self.assertTrue(audit.instantaneous_fixed_adapter_equivalence)
        self.assertTrue(audit.trajectory_counterprediction_requires_dynamic_state)
        self.assertIn(
            "fixed-pre-probe-rate-ledger-reproduces-the-complete-candidate-trajectory",
            audit.stop_conditions,
        )

    def test_ablation_and_required_baselines_remain_explicit(self) -> None:
        audit = self._audit()
        self.assertEqual(6, len(audit.ablation_arms))
        for arm in ("P0", "A0", "A1", "F0", "U0", "E1"):
            self.assertTrue(any(item.startswith(arm + "-") for item in audit.ablation_arms))
        self.assertIn("dynamic-two-state-e1", dict(audit.counterpredictions))

    def test_zulassen_selects_no_implementation_values_runtime_or_effect(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.backreaction_family_selected)
        self.assertTrue(audit.frozen_e1_branch_remains_stopped)
        for value in (
            audit.backreaction_implementation_present,
            audit.coupled_integrator_selected,
            audit.material_rate_values_selected,
            audit.runtime_integration_present,
            audit.research_execution_permitted,
            audit.functional_effect_proven,
            audit.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, audit.field_steps_executed)
        self.assertEqual(S1_HR_DECISION, audit.decision)

    def test_audit_is_deterministic_tamper_evident_and_static(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1HRBackreactionFamilyAuditError):
            replace(audit, audited_family_count=2)
        with self.assertRaises(DTS1S1HRBackreactionFamilyAuditError):
            replace(audit, instantaneous_fixed_adapter_equivalence=False)
        source = inspect.getsource(audit_dts1_s1hr_backreaction_family)
        for forbidden in ("numpy", "field_runner", "compute_dts1_closed_prestate_step", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
