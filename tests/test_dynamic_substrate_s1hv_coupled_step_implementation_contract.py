from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hv_coupled_step_implementation_contract import (
    DTS1S1HVCoupledStepImplementationContractError,
    S1_HV_DECISION,
    build_dts1_s1hv_coupled_step_implementation_contract,
)


class DTS1S1HVCoupledStepImplementationContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1hv_coupled_step_implementation_contract()

    def test_binds_one_private_module_entry_point_and_s1hu_order(self) -> None:
        contract = self._contract()
        self.assertEqual(
            "mcm_field_organism.dynamic_substrate_dts1_coupled_step",
            contract.target_module,
        )
        self.assertIn("advance_dts1_coupled_fast_shared_field", contract.entry_point)
        self.assertEqual(
            "CLOSED_PRESTATE_PARALLEL_READ_ATOMIC_COMMIT", contract.order_id
        )

    def test_inputs_are_complete_explicit_and_select_no_values(self) -> None:
        names = {name for name, _ in self._contract().inputs}
        self.assertEqual(
            {
                "field",
                "anatomy",
                "distribution",
                "step_time",
                "substrate_config",
                "afterimage_config",
                "dts1_rates",
                "dissipation_config",
                "backreaction_enabled",
            },
            names,
        )
        self.assertFalse(self._contract().material_rate_values_selected)

    def test_result_is_one_complete_atomic_pair_with_passive_ledgers(self) -> None:
        fields = dict(self._contract().result_fields)
        names = set(fields)
        for required in (
            "field",
            "anatomy",
            "elapsed_time",
            "participations",
            "resource_transfers",
            "applied_adapter",
        ):
            self.assertIn(required, names)
        self.assertIn("empty only for exact zero duration", fields["participations"])
        self.assertIn("empty only for exact zero duration", fields["resource_transfers"])
        self.assertIn("None only for exact zero duration", fields["applied_adapter"])
        self.assertTrue(self._contract().atomic_pair_commit_required)

    def test_phases_bind_prestate_only_proposals_and_zero_duration(self) -> None:
        phases = self._contract().phases
        for required in (
            "return-exact-input-pair-on-zero-duration-without-calling-either-proposal",
            "derive-complete-canonical-p_n-from-S_n-only-with-the-s1hk-observable",
            "derive-active-or-ablated-adapter-and-G_n-from-A_n-only-with-s1ht",
            "compute-complete-A_next-from-A_n-p_n-elapsed-and-rates-with-s1hp",
            "construct-one-new-result-as-the-only-atomic-pair-commit",
        ):
            self.assertIn(required, phases)
        self.assertTrue(self._contract().one_closed_prestate_required)

    def test_p0_a0_and_active_zero_binding_delegate_to_neutral_path(self) -> None:
        identities = self._contract().neutral_identities
        for required in (
            "P0-remains-the-existing-neutral-fast-field-function-outside-this-module",
            "A0-computes-A_next-but-calls-the-existing-neutral-fast-field-function-once",
            "A1-with-zero-prestate-binding-uses-the-same-direct-neutral-field-call-as-A0",
            "A0-field-output-is-value-and-bit-identical-to-P0-for-identical-field-inputs",
        ):
            self.assertIn(required, identities)
        self.assertTrue(self._contract().exact_p0_a0_field_identity_required)
        self.assertTrue(
            self._contract().active_zero_binding_neutral_delegation_required
        )

    def test_reuses_existing_integrator_and_forbids_extra_freedoms(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.existing_neutral_integrator_reuse_required)
        self.assertFalse(contract.new_field_integrator_selected)
        for required in (
            "poststate-reader-resource-first-field-first-or-midpoint-coupling",
            "implicit-iteration-solver-tolerance-or-adaptive-substep-selection",
            "new-field-integrator-or-duplicated-neutral-A0-numerics",
            "mutation-partial-commit-clipping-normalization-or-state-repair",
        ):
            self.assertIn(required, contract.forbidden_surfaces)

    def test_matrix_is_contiguous_and_covers_causal_and_failure_boundaries(self) -> None:
        matrix = self._contract().test_matrix
        self.assertEqual(20, len(matrix))
        self.assertEqual(
            tuple(f"T{index:02d}" for index in range(1, 21)),
            tuple(test_id for test_id, _ in matrix),
        )
        cases = " ".join(case for _, case in matrix)
        for required in (
            "bit-exact-direct-neutral-fast-step-output",
            "new-binding-cannot-affect-the-current-field-proposal",
            "new-field-values-cannot-affect-the-current-resource-proposal",
            "field-failure-yields-no-anatomy-or-pair-output",
            "n-2n-4n-residual-and-reader-latency-are-measurable",
        ):
            self.assertIn(required, cases)

    def test_authorizes_only_private_implementation_next(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.implementation_authorized_next_stage)
        for value in (
            contract.coupled_step_implementation_present,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
            contract.functional_effect_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.field_steps_executed)
        self.assertEqual(S1_HV_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1HVCoupledStepImplementationContractError):
            replace(contract, coupled_step_implementation_present=True)
        with self.assertRaises(DTS1S1HVCoupledStepImplementationContractError):
            replace(contract, research_execution_permitted=True)
        source = inspect.getsource(
            build_dts1_s1hv_coupled_step_implementation_contract
        )
        for forbidden in ("numpy", "advance_neutral", "compute_dts1", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
