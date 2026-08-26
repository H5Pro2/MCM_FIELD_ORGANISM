from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hn_discrete_integration_contract import (
    DTS1S1HNDiscreteIntegrationContractError,
    S1_HN_DECISION,
    build_dts1_s1hn_discrete_integration_contract,
)


class DTS1S1HNDiscreteIntegrationContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1hn_discrete_integration_contract()

    def test_binds_one_closed_prestate_exponential_map(self) -> None:
        contract = self._contract()
        self.assertEqual(
            "CLOSED_PRESTATE_EXPONENTIAL_TRANSFER_MAP",
            contract.map_id,
        )
        self.assertEqual(
            {
                "alpha_bind": "1-exp(-k_bind*Delta_t)",
                "alpha_turn": "1-exp(-k_turn*Delta_t)",
                "alpha_rec": "1-exp(-k_rec*Delta_t)",
            },
            dict(contract.interval_fractions),
        )
        self.assertTrue(contract.one_closed_prestate)

    def test_joint_admission_is_simultaneous_and_order_independent(self) -> None:
        contract = self._contract()
        offers = dict(contract.closed_prestate_offers)
        self.assertEqual("0.5*sum(d_e for incident edges)", offers["D_i"])
        self.assertEqual("1 if D_i=0 else min(1,f_i/D_i)", offers["a_i"])
        self.assertEqual("d_e*min(a_i,a_j)", offers["x_e"])
        self.assertTrue(contract.simultaneous_local_admission_selected)
        self.assertTrue(contract.edge_order_independent)

    def test_atomic_commit_preserves_directed_cycle_and_half_share_ledger(self) -> None:
        commit = dict(self._contract().atomic_commit)
        self.assertEqual("b_e+x_e-y_e", commit["b_e_next"])
        self.assertEqual("u_e+y_e-z_e", commit["u_e_next"])
        self.assertEqual(
            "f_i-0.5*sum(x_e for incident edges)"
            "+0.5*sum(z_e for incident edges)",
            commit["f_i_next"],
        )

    def test_proof_obligations_bind_positivity_conservation_and_no_reuse(self) -> None:
        contract = self._contract()
        obligations = dict(contract.proof_obligations)
        self.assertTrue(contract.positivity_preserved_by_construction)
        self.assertTrue(contract.conservation_preserved_by_construction)
        self.assertTrue(obligations["zero-interval-is-the-identity-map"])
        self.assertTrue(
            obligations["newly-produced-resource-is-not-reused-in-the-same-step"]
        )
        self.assertTrue(
            obligations["small-interval-map-is-first-order-consistent-with-s1hm-family"]
        )

    def test_contract_forbids_repair_and_keeps_execution_closed(self) -> None:
        contract = self._contract()
        for value in (
            contract.post_hoc_clipping_permitted,
            contract.post_hoc_normalization_permitted,
            contract.parameter_values_selected,
            contract.executable_step_implemented,
            contract.field_backreaction_selected,
            contract.runtime_implemented,
            contract.functional_effect_proven,
            contract.execution_permitted,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.field_steps_executed)
        self.assertEqual(S1_HN_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1HNDiscreteIntegrationContractError):
            replace(contract, executable_step_implemented=True)
        with self.assertRaises(DTS1S1HNDiscreteIntegrationContractError):
            replace(contract, post_hoc_clipping_permitted=True)
        source = inspect.getsource(build_dts1_s1hn_discrete_integration_contract)
        for forbidden in ("advance_", "solve_ivp", "field_runner", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
