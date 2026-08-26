from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ho_step_implementation_contract import (
    DTS1S1HOStepImplementationContractError,
    S1_HO_DECISION,
    build_dts1_s1ho_step_implementation_contract,
)


class DTS1S1HOStepImplementationContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1ho_step_implementation_contract()

    def test_binds_one_private_pure_step_surface(self) -> None:
        contract = self._contract()
        self.assertEqual(
            "mcm_field_organism.dynamic_substrate_dts1_step",
            contract.target_module,
        )
        self.assertIn("compute_dts1_closed_prestate_step", contract.entry_point)
        self.assertTrue(contract.pure_function_required)
        self.assertTrue(contract.use_existing_s1hi_types)

    def test_inputs_exclude_field_state_and_implicit_time(self) -> None:
        contract = self._contract()
        self.assertEqual(
            {"anatomy", "edge_participations", "elapsed_time", "rates"},
            {name for name, _ in contract.input_types},
        )
        forbidden = " ".join(contract.forbidden_surfaces)
        self.assertIn("implicit-clock-default-step-or-call-counter", forbidden)
        self.assertIn("field-state-layer-adapter-or-backreaction-input", forbidden)

    def test_output_is_new_anatomy_transfer_ledger_and_passive_diagnostics(self) -> None:
        contract = self._contract()
        self.assertEqual(
            {
                "next_anatomy",
                "edge_transfers",
                "input_anatomy_digest",
                "output_anatomy_digest",
                "maximum_local_ledger_residual",
                "global_ledger_residual",
            },
            {name for name, _ in contract.output_types},
        )
        self.assertTrue(contract.immutable_inputs_required)
        self.assertTrue(contract.canonical_output_required)
        self.assertTrue(contract.diagnostics_are_passive)

    def test_algorithm_preserves_closed_prestate_and_atomic_commit_order(self) -> None:
        phases = self._contract().algorithm_phases
        self.assertLess(
            phases.index("derive-free-resource-from-one-closed-anatomy-prestate"),
            phases.index("compute-all-edge-engagement-offers-from-the-closed-prestate"),
        )
        self.assertLess(
            phases.index("compute-all-local-admission-factors-before-any-transfer"),
            phases.index("atomically-build-one-new-complete-anatomy"),
        )
        self.assertIn(
            "compute-interval-fractions-with-negative-expm1",
            phases,
        )

    def test_matrix_is_complete_contiguous_and_covers_hard_boundaries(self) -> None:
        contract = self._contract()
        self.assertEqual(17, len(contract.test_matrix))
        self.assertEqual(
            tuple(f"T{index:02d}" for index in range(1, 18)),
            tuple(test_id for test_id, _ in contract.test_matrix),
        )
        cases = " ".join(case for _, case in contract.test_matrix)
        for required in (
            "zero-interval",
            "shared-node-competition",
            "edge-declaration-order",
            "not-reused-same-step",
            "fail-closed",
            "step-refinement",
            "no-field-runtime-io-or-public-api",
        ):
            self.assertIn(required, cases)

    def test_authorizes_only_next_pure_implementation(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.implementation_authorized_next_stage)
        for value in (
            contract.parameter_values_selected,
            contract.step_implementation_present,
            contract.field_backreaction_selected,
            contract.runtime_integration_present,
            contract.functional_effect_proven,
            contract.execution_permitted,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.field_steps_executed)
        self.assertEqual(S1_HO_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1HOStepImplementationContractError):
            replace(contract, step_implementation_present=True)
        with self.assertRaises(DTS1S1HOStepImplementationContractError):
            replace(contract, field_backreaction_selected=True)
        source = inspect.getsource(build_dts1_s1ho_step_implementation_contract)
        for forbidden in ("advance_", "solve_ivp", "field_runner", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
