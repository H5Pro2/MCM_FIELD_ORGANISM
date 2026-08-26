from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jc_pih_exposure_assumption_precheck import (
    build_dts1_s1jc_pih_exposure_assumption_precheck,
)
from mcm_field_organism.dynamic_substrate_s1jd_corrected_pih_exposure_contract import (
    DTS1S1JDCorrectedPIHExposureContractError,
    S1_JD_DECISION,
    build_dts1_s1jd_corrected_pih_exposure_contract,
)


class DTS1S1JDCorrectedPIHExposureContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jd_corrected_pih_exposure_contract()

    def test_binds_exact_s1jc_precheck(self) -> None:
        self.assertEqual(
            build_dts1_s1jc_pih_exposure_assumption_precheck().audit_digest,
            self._contract().source_s1jc_digest,
        )

    def test_binds_one_positive_two_node_a_boundary_role(self) -> None:
        role, rule = self._contract().boundary_role
        self.assertEqual("A_BOUNDARY_2N", role)
        self.assertIn("two-node-S-H-prestate", rule)
        self.assertIn("strictly-positive-S1-HK-participation", rule)

    def test_binds_three_identical_boundary_active_checkpoint_rows(self) -> None:
        schedule = self._contract().schedule
        self.assertEqual((3, 3), (self._contract().interval_count, self._contract().checkpoint_count))
        self.assertEqual((1, 2, 3), tuple(row[0] for row in schedule))
        self.assertEqual({"A_BOUNDARY_2N"}, {row[1] for row in schedule})
        self.assertEqual({"A_ACTIVE_2N"}, {row[2] for row in schedule})

    def test_boundary_replaces_only_sh_and_hidden_state_carries(self) -> None:
        boundary = " ".join(self._contract().boundary_rules)
        models = " ".join(self._contract().model_rules)
        self.assertIn("replace-only-S-H", boundary)
        self.assertIn("preserving-DTS1-anatomy-B1-fixed-adapter-B2-L", boundary)
        self.assertIn("DTS1-carries-only-its-complete-resource-anatomy", models)
        self.assertIn("B3-through-B6-carry-only", models)

    def test_dts1_derives_participation_after_boundary_and_no_private_reset(self) -> None:
        rules = " ".join(self._contract().active_interval_rules)
        self.assertIn("after-the-common-boundary", rules)
        self.assertIn("identical-all-node-zero-receptor-contact", rules)
        self.assertIn("no-additional-S-H-boundary-at-private-internal-refinement-substeps", rules)

    def test_binds_exact_eight_component_signed_profile(self) -> None:
        self.assertEqual(8, self._contract().profile_component_count)
        rules = " ".join(self._contract().profile_rules)
        self.assertIn("checkpoint-two-minus-one", rules)
        self.assertIn("checkpoint-three-minus-one", rules)
        self.assertIn("two-S-values-then-two-H-values", rules)

    def test_supersedes_old_field_path_but_retains_direct_ledgers(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.old_resource_only_field_path_superseded)
        self.assertTrue(contract.old_p_ih_field_vectors_quarantined)
        self.assertTrue(contract.direct_p_ih_ledgers_retained)

    def test_selects_no_values_implementation_or_execution(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.corrected_common_exposure_valid)
        for value in (
            contract.boundary_values_selected,
            contract.duration_selected,
            contract.tolerances_selected,
            contract.call_budget_bound,
            contract.two_node_boundary_implemented,
            contract.common_interval_envelope_bound,
            contract.adapters_implemented,
            contract.baseline_models_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_JD_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JDCorrectedPIHExposureContractError):
            replace(contract, corrected_common_exposure_valid=False)
        with self.assertRaises(DTS1S1JDCorrectedPIHExposureContractError):
            replace(contract, boundary_values_selected=True)
        source = inspect.getsource(build_dts1_s1jd_corrected_pih_exposure_contract)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
