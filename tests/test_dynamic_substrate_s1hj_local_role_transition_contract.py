from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hj_local_role_transition_contract import (
    DTS1LocalRoleTransition,
    DTS1S1HJRoleTransitionContractError,
    S1_HJ_DECISION,
    build_dts1_s1hj_local_role_transition_contract,
)


class DTS1S1HJLocalRoleTransitionContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1hj_local_role_transition_contract()

    def test_binds_exactly_one_directed_three_role_cycle(self) -> None:
        contract = self._contract()
        self.assertEqual(
            (
                ("free", "conductive-bound"),
                ("conductive-bound", "refractory"),
                ("refractory", "free"),
            ),
            contract.role_cycle,
        )
        self.assertEqual(3, len(contract.transitions))
        self.assertTrue(all(item.same_edge_only for item in contract.transitions))
        self.assertTrue(all(item.content_free for item in contract.transitions))

    def test_binds_local_causes_and_forbids_shortcuts(self) -> None:
        contract = self._contract()
        self.assertIn(
            "current-symmetric-edge-local-fast-field-participation-for-engagement-only",
            contract.allowed_causal_inputs,
        )
        self.assertIn(("free", "refractory"), contract.forbidden_transitions)
        self.assertIn(("conductive-bound", "free"), contract.forbidden_transitions)
        self.assertIn(("refractory", "conductive-bound"), contract.forbidden_transitions)
        self.assertIn("afterimage-h", contract.forbidden_causal_inputs)
        self.assertIn(
            "repetition-history-phase-or-age-counter",
            contract.forbidden_causal_inputs,
        )

    def test_bookkeeping_preserves_s1hi_identity_without_amount_rule(self) -> None:
        contract = self._contract()
        ledger_effects = {item.transition_id: item.ledger_effect for item in contract.transitions}
        self.assertIn("half leaves", ledger_effects["local-engagement"])
        self.assertIn("identical edge", ledger_effects["local-turnover"])
        self.assertIn("half returns", ledger_effects["local-recovery"])
        self.assertTrue(contract.eligibility_is_not_transition_amount)
        self.assertTrue(contract.ledger_effect_is_not_dynamics_equation)

    def test_binds_concurrent_competition_fail_closed(self) -> None:
        contract = self._contract()
        self.assertEqual(4, len(contract.concurrency_rules))
        self.assertIn(
            "call-order-must-not-select-a-winning-edge",
            contract.concurrency_rules,
        )
        self.assertIn(
            "unresolved-overdraw-must-fail-closed-without-partial-state",
            contract.concurrency_rules,
        )

    def test_selects_no_observable_amount_rate_dynamics_or_effect(self) -> None:
        contract = self._contract()
        for value in (
            contract.exact_field_observable_selected,
            contract.transfer_amount_selected,
            contract.rate_selected,
            contract.time_law_selected,
            contract.integrator_selected,
            contract.field_backreaction_selected,
            contract.runtime_implemented,
            contract.functional_effect_proven,
            contract.execution_permitted,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.field_steps_executed)
        self.assertEqual(S1_HJ_DECISION, contract.decision)

    def test_transition_and_contract_are_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1HJRoleTransitionContractError):
            replace(contract, rate_selected=True)
        with self.assertRaises(DTS1S1HJRoleTransitionContractError):
            DTS1LocalRoleTransition(
                transition_id="shortcut",
                source_role="free",
                target_role="refractory",
                causal_eligibility="none",
                ledger_effect="none",
                same_edge_only=True,
                content_free=True,
            )
        source = inspect.getsource(build_dts1_s1hj_local_role_transition_contract)
        for forbidden in ("advance_", "field_runner", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
