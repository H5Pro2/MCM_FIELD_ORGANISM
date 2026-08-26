from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jd_corrected_pih_exposure_contract import (
    build_dts1_s1jd_corrected_pih_exposure_contract,
)
from mcm_field_organism.dynamic_substrate_s1je_finite_pih_boundary_fixture_contract import (
    DTS1S1JEFinitePIHBoundaryFixtureContractError,
    S1_JE_DECISION,
    build_dts1_s1je_finite_pih_boundary_fixture_contract,
)


class DTS1S1JEFinitePIHBoundaryFixtureContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1je_finite_pih_boundary_fixture_contract()

    def test_binds_exact_s1jd_contract(self) -> None:
        self.assertEqual(
            build_dts1_s1jd_corrected_pih_exposure_contract().contract_digest,
            self._contract().source_s1jd_digest,
        )

    def test_binds_exact_two_node_boundary_fixture(self) -> None:
        fixture = dict(self._contract().boundary_fixture)
        self.assertEqual("A_BOUNDARY_2N", fixture["role"])
        self.assertEqual((-0.5, 0.5), fixture["S"])
        self.assertEqual((0.0, 0.0), fixture["H"])
        self.assertEqual((0.25,), fixture["expected_S1_HK_participation"])

    def test_participation_follows_s1hk_exactly(self) -> None:
        fixture = dict(self._contract().boundary_fixture)
        s_values = fixture["S"]
        actual = (((s_values[0] - s_values[1]) / 2.0) ** 2,)
        self.assertEqual(fixture["expected_S1_HK_participation"], actual)

    def test_does_not_reuse_quarantined_old_pih_field_vectors(self) -> None:
        fixture = dict(self._contract().boundary_fixture)
        self.assertNotEqual((-1.0, 1.0), fixture["S"])
        self.assertNotEqual((-0.2, 0.2), fixture["H"])

    def test_binds_positive_duration_zero_contact_and_zero_boundary_time(self) -> None:
        interval = dict(self._contract().interval_fixture)
        self.assertEqual(0.5, interval["duration"])
        self.assertEqual((0.0, 0.0), interval["receptor_contact"])
        self.assertEqual(0.0, interval["boundary_operator_duration"])

    def test_tolerances_are_structural_not_outcome_thresholds(self) -> None:
        tolerances = dict(self._contract().tolerances)
        self.assertEqual("bit-exact", tolerances["canonical_fixture_digest_and_cross_model_boundary_identity"])
        self.assertEqual("not-bound-in-S1-JE", tolerances["outcome_acceptance_or_baseline_fit_tolerance"])

    def test_binds_exact_refined_double_audit_budget(self) -> None:
        budget = dict(self._contract().call_budget)
        self.assertEqual((7, 3, 3), tuple(budget[key] for key in ("models", "active_intervals_per_model_per_refinement", "refinement_levels")))
        self.assertEqual((63, 63), tuple(budget[key] for key in ("single_complete_audit_boundary_applications", "single_complete_audit_interval_invocations")))
        self.assertEqual((126, 126), tuple(budget[key] for key in ("double_audit_max_boundary_applications", "double_audit_max_interval_invocations")))

    def test_selects_no_implementation_or_execution(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.boundary_values_selected)
        self.assertTrue(contract.duration_selected)
        self.assertTrue(contract.tolerances_selected)
        self.assertTrue(contract.call_budget_bound)
        for value in (
            contract.two_node_boundary_implemented,
            contract.common_interval_envelope_bound,
            contract.adapters_implemented,
            contract.baseline_models_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_JE_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JEFinitePIHBoundaryFixtureContractError):
            replace(contract, duration_selected=False)
        with self.assertRaises(DTS1S1JEFinitePIHBoundaryFixtureContractError):
            replace(contract, two_node_boundary_implemented=True)
        source = inspect.getsource(build_dts1_s1je_finite_pih_boundary_fixture_contract)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
