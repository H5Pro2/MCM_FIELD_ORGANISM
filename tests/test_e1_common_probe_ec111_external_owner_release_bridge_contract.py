from __future__ import annotations

import ast
from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec111_external_owner_release_bridge_contract import (
    E1CommonProbeEC111ExternalOwnerReleaseBridgeContractError,
    S1_EC111_CONTINUATION_EXAMPLES,
    S1_EC111_EXPLICIT_RELEASE_REQUIREMENTS,
    S1_EC111_REJECTION_RULES,
    audit_e1_common_probe_ec111_external_owner_release_bridge_contract,
)


class E1CommonProbeEC111ExternalOwnerReleaseBridgeContractTests(unittest.TestCase):
    def test_current_message_is_continuation_not_release(self) -> None:
        contract = audit_e1_common_probe_ec111_external_owner_release_bridge_contract()
        self.assertEqual("continuation-only", contract.current_message_class)
        self.assertFalse(contract.current_message_authorizes_real_run)
        self.assertTrue(contract.continuation_work_permitted)
        self.assertFalse(contract.owner_scope_token_creation_permitted)

    def test_continuation_examples_never_authorize_run(self) -> None:
        self.assertIn("ok weiter", S1_EC111_CONTINUATION_EXAMPLES)
        self.assertIn(
            "continuation-never-implies-run-release", S1_EC111_REJECTION_RULES
        )
        self.assertIn(
            "prior-release-never-carries-forward", S1_EC111_REJECTION_RULES
        )

    def test_explicit_release_candidate_requires_complete_boundary(self) -> None:
        self.assertEqual(9, len(S1_EC111_EXPLICIT_RELEASE_REQUIREMENTS))
        for required in (
            "exact-run-id-ec67-r2",
            "exactly-one-run",
            "maximum-3208-field-steps",
            "nonpersistent",
            "no-retry",
        ):
            self.assertIn(required, S1_EC111_EXPLICIT_RELEASE_REQUIREMENTS)

    def test_contract_is_deterministic_and_fail_closed(self) -> None:
        first = audit_e1_common_probe_ec111_external_owner_release_bridge_contract()
        second = audit_e1_common_probe_ec111_external_owner_release_bridge_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1CommonProbeEC111ExternalOwnerReleaseBridgeContractError):
            replace(first, current_message_authorizes_real_run=True)

    def test_audit_does_not_call_factory_production_write_or_decide(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec111_external_owner_release_bridge_contract
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
            "create_e1_common_probe_ec110_owner_scope_token",
            "run_e1_common_probe_n2_r2_real_mode_coordinator",
            "run_e1_common_probe_real_formation_receipt_adapter",
            "run_e1_common_probe_real_probe_receipt_adapter",
            "decide_common_probe_evidence",
            "write_text",
            "write_bytes",
            "open",
        ):
            self.assertNotIn(forbidden, called)


if __name__ == "__main__":
    unittest.main()
