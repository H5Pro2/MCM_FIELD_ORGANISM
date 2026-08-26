from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hs_backreaction_implementation_contract import (
    DTS1S1HSBackreactionImplementationContractError,
    S1_HS_DECISION,
    build_dts1_s1hs_backreaction_implementation_contract,
)


class DTS1S1HSBackreactionImplementationContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1hs_backreaction_implementation_contract()

    def test_binds_one_private_module_and_two_pure_entry_points(self) -> None:
        contract = self._contract()
        self.assertEqual(
            "mcm_field_organism.dynamic_substrate_dts1_backreaction",
            contract.target_module,
        )
        self.assertEqual({"adapter", "generator"}, {name for name, _ in contract.entry_points})
        self.assertTrue(contract.pure_adapter_required)
        self.assertTrue(contract.pure_generator_required)

    def test_adapter_inputs_are_complete_explicit_and_immutable(self) -> None:
        contract = self._contract()
        self.assertEqual(
            {"layer", "anatomy", "substrate_config", "backreaction_enabled"},
            {name for name, _ in contract.adapter_inputs},
        )
        self.assertTrue(contract.existing_geometry_digest_required)
        self.assertTrue(contract.exact_ablation_required)
        self.assertTrue(contract.immutable_inputs_required)

    def test_adapter_phases_bind_geometry_conductive_only_and_rate_range(self) -> None:
        phases = self._contract().adapter_phases
        self.assertIn(
            "require-exact-complete-edge-inventory-and-existing-digest-identity",
            phases,
        )
        self.assertIn(
            "read-only-conductive-bound-resource-from-one-closed-anatomy",
            phases,
        )
        self.assertIn(
            "validate-rate-range-and-return-one-new-immutable-ledger",
            phases,
        )

    def test_generator_phases_bind_symmetric_conservative_matrix(self) -> None:
        phases = self._contract().generator_phases
        for required in (
            "allocate-one-zero-float64-square-matrix",
            "book-each-undirected-rate-symmetrically-once",
            "book-negative-diagonal-edge-rate-at-both-endpoints",
            "validate-finiteness-symmetry-zero-row-sum-and-nonpositive-spectrum",
            "return-new-matrix-without-boundary-source-or-state-advance",
        ):
            self.assertIn(required, phases)

    def test_matrix_is_contiguous_and_covers_all_hard_boundaries(self) -> None:
        contract = self._contract()
        self.assertEqual(16, len(contract.test_matrix))
        self.assertEqual(
            tuple(f"T{index:02d}" for index in range(1, 17)),
            tuple(test_id for test_id, _ in contract.test_matrix),
        )
        cases = " ".join(case for _, case in contract.test_matrix)
        for required in (
            "heterogeneous-capacity",
            "ablation-returns-exact-base-rate",
            "same-b-different-refractory",
            "negative-semidefinite",
            "antisymmetric-and-sum-conserving",
            "no-runtime-boundary-io-snapshot-or-public-api",
        ):
            self.assertIn(required, cases)

    def test_forbids_resource_step_boundary_and_extra_reader_freedom(self) -> None:
        forbidden = self._contract().forbidden_surfaces
        for required in (
            "calling-or-advancing-the-dts1-resource-step",
            "reading-free-or-refractory-resource-in-the-rate-formula",
            "extra-gain-threshold-sign-label-modality-or-history-input",
            "receptor-boundary-afterimage-or-external-source-booking",
            "package-level-or-current-api-export",
        ):
            self.assertIn(required, forbidden)

    def test_authorizes_only_next_private_implementation(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.implementation_authorized_next_stage)
        for value in (
            contract.backreaction_implementation_present,
            contract.coupled_integrator_selected,
            contract.material_rate_values_selected,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
            contract.functional_effect_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.field_steps_executed)
        self.assertEqual(S1_HS_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1HSBackreactionImplementationContractError):
            replace(contract, backreaction_implementation_present=True)
        with self.assertRaises(DTS1S1HSBackreactionImplementationContractError):
            replace(contract, coupled_integrator_selected=True)
        source = inspect.getsource(build_dts1_s1hs_backreaction_implementation_contract)
        for forbidden in ("numpy", "field_runner", "compute_dts1_edge_rates", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
