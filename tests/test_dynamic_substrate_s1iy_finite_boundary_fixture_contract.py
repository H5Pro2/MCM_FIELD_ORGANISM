from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ix_corrected_event_boundary_contract import (
    build_dts1_s1ix_corrected_event_boundary_contract,
)
from mcm_field_organism.dynamic_substrate_s1iy_finite_boundary_fixture_contract import (
    DTS1S1IYFiniteBoundaryFixtureContractError,
    S1_IY_DECISION,
    build_dts1_s1iy_finite_boundary_fixture_contract,
)


class DTS1S1IYFiniteBoundaryFixtureContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1iy_finite_boundary_fixture_contract()

    def test_binds_exact_s1ix_contract(self) -> None:
        self.assertEqual(
            build_dts1_s1ix_corrected_event_boundary_contract().contract_digest,
            self._contract().source_s1ix_digest,
        )

    def test_binds_exact_four_dyadic_boundary_fixtures(self) -> None:
        fixtures = {row[0]: row[1:] for row in self._contract().boundary_fixtures}
        self.assertEqual(4, self._contract().boundary_role_count)
        self.assertEqual(((-0.5, 0.5, 0.5), (0.0, 0.0, 0.0), (0.25, 0.0)), fixtures["A_BOUNDARY"])
        self.assertEqual(((-0.5, -0.5, 0.5), (0.0, 0.0, 0.0), (0.0, 0.25)), fixtures["B_BOUNDARY"])
        self.assertEqual(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0)), fixtures["GAP_BOUNDARY"])
        self.assertEqual(((-0.5, 0.0, 0.5), (-0.125, 0.0, 0.125), (0.0625, 0.0625)), fixtures["PROBE_BOUNDARY"])

    def test_participations_follow_s1hk_observable_exactly(self) -> None:
        for _, s_values, _, expected in self._contract().boundary_fixtures:
            actual = (
                ((s_values[0] - s_values[1]) / 2.0) ** 2,
                ((s_values[1] - s_values[2]) / 2.0) ** 2,
            )
            self.assertEqual(expected, actual)

    def test_binds_equal_positive_durations_and_zero_contacts(self) -> None:
        self.assertEqual({0.5}, {row[1] for row in self._contract().durations})
        contacts = dict(self._contract().contacts)
        self.assertEqual((0.0, 0.0, 0.0), contacts["all_active_and_readout_intervals"])
        self.assertEqual(0.0, contacts["boundary_operator_duration"])

    def test_probe_does_not_reuse_quarantined_old_vector(self) -> None:
        probe = {row[0]: row[1:] for row in self._contract().boundary_fixtures}["PROBE_BOUNDARY"]
        self.assertNotEqual((-1.0, 0.0, 1.0), probe[0])
        self.assertNotEqual((-0.2, 0.0, 0.2), probe[1])

    def test_tolerances_are_structural_not_outcome_thresholds(self) -> None:
        tolerances = dict(self._contract().tolerances)
        self.assertEqual("bit-exact", tolerances["canonical_vector_digest_and_cross_model_boundary_identity"])
        self.assertEqual("not-bound-in-S1-IY", tolerances["outcome_acceptance_or_baseline_fit_tolerance"])

    def test_binds_exact_finite_double_audit_budget(self) -> None:
        budget = dict(self._contract().call_budget)
        self.assertEqual(112, budget["single_full_fixture_boundary_applications"])
        self.assertEqual(112, budget["single_full_fixture_interval_invocations"])
        self.assertEqual(224, budget["double_audit_max_boundary_applications"])
        self.assertEqual(224, budget["double_audit_max_interval_invocations"])
        self.assertEqual(0, budget["research_field_steps"])

    def test_selects_no_adapter_configuration_implementation_or_execution(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.boundary_values_selected)
        self.assertTrue(contract.durations_selected)
        self.assertTrue(contract.tolerances_selected)
        self.assertTrue(contract.call_budget_bound)
        for value in (
            contract.adapter_configuration_selected,
            contract.configuration_digests_bound,
            contract.boundary_operator_implemented,
            contract.fixtures_implemented,
            contract.baseline_models_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_IY_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IYFiniteBoundaryFixtureContractError):
            replace(contract, call_budget_bound=False)
        with self.assertRaises(DTS1S1IYFiniteBoundaryFixtureContractError):
            replace(contract, boundary_operator_implemented=True)
        source = inspect.getsource(build_dts1_s1iy_finite_boundary_fixture_contract)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
