from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ir_corrected_profile_contract import (
    build_dts1_s1ir_corrected_profile_contract,
)
from mcm_field_organism.dynamic_substrate_s1is_baseline_surface_compatibility import (
    DTS1S1ISBaselineSurfaceCompatibilityError,
    S1_IS_DECISION,
    build_dts1_s1is_baseline_surface_compatibility,
)


class DTS1S1ISBaselineSurfaceCompatibilityTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1is_baseline_surface_compatibility()

    def test_binds_corrected_s1ir_contract(self) -> None:
        self.assertEqual(
            build_dts1_s1ir_corrected_profile_contract().contract_digest,
            self._audit().source_s1ir_digest,
        )

    def test_binds_exact_two_and_three_node_requirements(self) -> None:
        self.assertEqual(
            ((2, 4, 8), (2, 4, 8), (3, 6, 6), (3, 6, 6)),
            tuple(row[1:] for row in self._audit().geometry_requirements),
        )

    def test_classifies_all_six_kernel_surfaces_for_both_geometries(self) -> None:
        audit = self._audit()
        self.assertEqual(6, len(audit.surface_records))
        self.assertEqual((6, 6), (audit.two_node_surface_count, audit.three_node_surface_count))
        self.assertTrue(audit.kernel_surface_compatibility_complete)
        self.assertTrue(all(row[-1].startswith("COMPATIBLE_REQUIRES_PRIVATE_") for row in audit.surface_records))

    def test_b1_requires_an_information_barrier(self) -> None:
        b1 = self._audit().surface_records[0]
        self.assertIn("sanitize-to-common-predivergence-conductive-ledger", b1[4])
        rules = " ".join(self._audit().common_adapter_rules)
        self.assertIn("must-not-pass-the-original-DTS1-anatomy-object", rules)

    def test_b2_preserves_its_owned_l_state(self) -> None:
        b2 = self._audit().surface_records[1]
        self.assertIn("equal-length-S-H-L", b2[2])
        self.assertIn("baseline-owned-L", b2[4])

    def test_f3_family_uses_existing_generic_runtime(self) -> None:
        records = self._audit().surface_records[2:]
        self.assertTrue(all("advance_mcm_f3_shared_field" in row[1] for row in records))
        self.assertTrue(all("complete-SharedMCMField-SH-output" in row[3] for row in records))

    def test_const_v_records_existing_three_node_handoff_limit(self) -> None:
        b6 = self._audit().surface_records[-1]
        self.assertIn("existing-E1-E4-handoff-is-three-node-only", b6[2])
        self.assertIn("private-two-node-geometry-handoff", b6[4])

    def test_does_not_claim_executable_composition_or_run_models(self) -> None:
        audit = self._audit()
        for value in (
            audit.executable_composition_ready,
            audit.geometry_adapters_implemented,
            audit.configuration_digests_bound,
            audit.parameter_values_selected,
            audit.baseline_models_executed,
            audit.runtime_integration_present,
            audit.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))
        self.assertEqual(S1_IS_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1ISBaselineSurfaceCompatibilityError):
            replace(audit, executable_composition_ready=True)
        with self.assertRaises(DTS1S1ISBaselineSurfaceCompatibilityError):
            replace(audit, surface_records=())
        source = inspect.getsource(build_dts1_s1is_baseline_surface_compatibility)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
