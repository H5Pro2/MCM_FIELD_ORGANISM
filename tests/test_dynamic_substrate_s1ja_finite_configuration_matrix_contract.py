from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_dts1_common_boundary import (
    build_dts1_s1iz_implementation_receipt,
)
from mcm_field_organism.dynamic_substrate_s1it_private_adapter_contract import (
    build_dts1_s1it_private_adapter_contract,
)
from mcm_field_organism.dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    DTS1S1JAFiniteConfigurationMatrixContractError,
    S1_JA_DECISION,
    build_dts1_s1ja_finite_configuration_matrix_contract,
)


class DTS1S1JAFiniteConfigurationMatrixContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1ja_finite_configuration_matrix_contract()

    def test_binds_exact_s1iz_and_s1it_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1iz_implementation_receipt().receipt_digest, contract.source_s1iz_digest)
        self.assertEqual(build_dts1_s1it_private_adapter_contract().contract_digest, contract.source_s1it_digest)

    def test_binds_seven_unique_configuration_records_and_digests(self) -> None:
        records = self._contract().configuration_records
        self.assertEqual(7, self._contract().configuration_count)
        self.assertEqual(7, len({row[0] for row in records}))
        self.assertEqual(7, len({row[3] for row in records}))
        self.assertTrue(all(len(row[3]) == 64 for row in records))

    def test_binds_existing_dts1_and_b2_values(self) -> None:
        records = {row[0]: dict(row[2]) for row in self._contract().configuration_records}
        self.assertEqual((0.4, 0.3, 0.2), tuple(records["DTS1"][key] for key in ("binding_rate", "turnover_rate", "recovery_rate")))
        self.assertEqual((8.0, 0.25, 16), tuple(records["B2_S2_LINEAR_INTEGRATOR"][key] for key in ("capacity_ratio", "coupling_rate_per_second", "rk4_substeps")))

    def test_binds_equal_budget_f3_and_frozen_const_v(self) -> None:
        records = {row[0]: dict(row[2]) for row in self._contract().configuration_records}
        for role in ("B3_F3_LOCAL_LEAKY", "B4_F3_LINEAR_COUPLED", "B5_F3_FULL"):
            self.assertEqual((1.0, 0.5, 1.0), tuple(records[role][key] for key in ("lambda_sm_per_second", "kappa", "eta")))
        self.assertEqual((0.5, 0.5, 1.0), tuple(records["B6_CONST_V"][key] for key in ("lambda_sm_per_second", "kappa", "eta")))

    def test_b1_uses_only_common_predivergence_conductive_values(self) -> None:
        record = next(row for row in self._contract().configuration_records if row[0] == "B1_FIXED_PRERELEASE_ADAPTER")
        payload = dict(record[2])
        self.assertEqual((0.4,), payload["P_IE_fixed_conductive"])
        self.assertEqual((0.2, 0.2), payload["P_IN_fixed_conductive"])
        self.assertEqual("excluded", payload["free_refractory_and_postdivergence_coordinates"])

    def test_all_seven_roles_bind_same_refinement_levels(self) -> None:
        records = self._contract().refinement_records
        self.assertEqual(7, len(records))
        self.assertTrue(all(row[1:3] == ((2, 4, 8), 4) for row in records))
        rules = " ".join(self._contract().refinement_rules)
        self.assertIn("never-at-internal-substeps", rules)
        self.assertIn("without-fitting-thresholding", rules)

    def test_binds_canonical_complete_24_case_matrix(self) -> None:
        contract = self._contract()
        self.assertEqual(24, contract.baseline_case_count)
        self.assertEqual(24, len(set((row[0], row[1]) for row in contract.case_matrix)))
        self.assertTrue(all(row[4] == "BOUND_NOT_IMPLEMENTED_NOT_EXECUTED" for row in contract.case_matrix))
        self.assertEqual(28, contract.profile_component_count)

    def test_each_role_has_four_blocks_with_8_8_6_6_components(self) -> None:
        for role in self._contract().baseline_roles:
            rows = tuple(row for row in self._contract().case_matrix if row[0] == role)
            self.assertEqual((8, 8, 6, 6), tuple(row[3] for row in rows))
            self.assertEqual((2, 2, 3, 3), tuple(row[2] for row in rows))

    def test_selects_no_implementation_execution_or_comparison_threshold(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.parameter_values_selected)
        self.assertTrue(contract.configuration_digests_bound)
        self.assertTrue(contract.refinements_selected)
        self.assertTrue(contract.finite_case_matrix_bound)
        for value in (
            contract.adapters_implemented,
            contract.baseline_models_executed,
            contract.numerical_admissibility_proven,
            contract.comparison_threshold_selected,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_JA_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JAFiniteConfigurationMatrixContractError):
            replace(contract, baseline_case_count=23)
        with self.assertRaises(DTS1S1JAFiniteConfigurationMatrixContractError):
            replace(contract, adapters_implemented=True)
        source = inspect.getsource(build_dts1_s1ja_finite_configuration_matrix_contract)
        for forbidden in ("advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
