from __future__ import annotations

import ast
from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec107_r2_attested_return_integration_contract import (
    E1CommonProbeEC107R2AttestedReturnIntegrationContractError,
    S1_EC107_CONSUMPTION_SEQUENCE,
    S1_EC107_FAILURE_SEMANTICS,
    audit_e1_common_probe_ec107_r2_attested_return_integration_contract,
)


class E1CommonProbeEC107R2AttestedReturnIntegrationContractTests(unittest.TestCase):
    def test_contract_binds_token_budget_and_atomic_return(self) -> None:
        contract = audit_e1_common_probe_ec107_r2_attested_return_integration_contract()
        self.assertEqual(3208, contract.exact_field_step_budget)
        self.assertEqual((4, 8), (contract.exact_formation_count, contract.exact_probe_count))
        self.assertTrue(contract.token_single_process_and_single_use)
        self.assertTrue(contract.receipt_built_only_inside_successful_coordinator)
        self.assertFalse(contract.coordinator_integration_implemented)

    def test_consumption_order_is_fail_closed(self) -> None:
        self.assertLess(
            S1_EC107_CONSUMPTION_SEQUENCE.index(
                "consume-token-immediately-before-first-adapter"
            ),
            S1_EC107_CONSUMPTION_SEQUENCE.index(
                "execute-four-formations-and-eight-probes-once"
            ),
        )
        self.assertEqual(
            "return-result-and-receipt-in-one-immutable-envelope",
            S1_EC107_CONSUMPTION_SEQUENCE[-1],
        )

    def test_failure_semantics_forbid_retry_and_partial_success(self) -> None:
        contract = audit_e1_common_probe_ec107_r2_attested_return_integration_contract()
        self.assertEqual(3, len(S1_EC107_FAILURE_SEMANTICS))
        self.assertTrue(contract.partial_success_return_forbidden)
        self.assertFalse(contract.retry_permitted)
        self.assertFalse(contract.execution_permitted)

    def test_contract_is_deterministic_and_fail_closed(self) -> None:
        first = audit_e1_common_probe_ec107_r2_attested_return_integration_contract()
        second = audit_e1_common_probe_ec107_r2_attested_return_integration_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1CommonProbeEC107R2AttestedReturnIntegrationContractError):
            replace(first, token_implemented=True)

    def test_audit_does_not_call_production_write_or_decide(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec107_r2_attested_return_integration_contract
        )
        called = {
            node.func.id
            if isinstance(node.func, ast.Name)
            else node.func.attr
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Call)
            and isinstance(node.func, (ast.Name, ast.Attribute))
        }
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator",
            "run_e1_common_probe_real_formation_receipt_adapter",
            "build_e1_common_probe_real_fresh_field_adapter",
            "run_e1_common_probe_real_probe_receipt_adapter",
            "decide_common_probe_evidence",
            "write_text",
            "write_bytes",
            "open",
        ):
            self.assertNotIn(forbidden, called)


if __name__ == "__main__":
    unittest.main()
