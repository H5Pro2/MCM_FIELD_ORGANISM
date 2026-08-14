from __future__ import annotations

import ast
from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec110_owner_scope_token_factory import (
    E1CommonProbeEC110OwnerScopeTokenFactoryError,
    S1_EC110_EXTERNAL_RELEASE_SCHEMA,
    S1_EC110_TOKEN_SCHEMA,
    audit_e1_common_probe_ec110_owner_scope_token_factory,
    create_e1_common_probe_ec110_owner_scope_token,
)


class E1CommonProbeEC110OwnerScopeTokenFactoryTests(unittest.TestCase):
    def test_contract_binds_owner_scope_without_release(self) -> None:
        contract = audit_e1_common_probe_ec110_owner_scope_token_factory()
        self.assertEqual("owner-authorized-real-run", contract.authorization_scope)
        self.assertEqual(3208, contract.maximum_field_steps)
        self.assertFalse(contract.new_explicit_owner_release_present)
        self.assertFalse(contract.owner_scope_token_creation_permitted)
        self.assertFalse(contract.execution_permitted)

    def test_token_and_external_release_schemas_are_complete(self) -> None:
        self.assertIn("external_release_attestation_digest", S1_EC110_TOKEN_SCHEMA)
        self.assertIn("issued_after_explicit_owner_message", S1_EC110_EXTERNAL_RELEASE_SCHEMA)
        self.assertIn("thread_or_session_binding_digest", S1_EC110_EXTERNAL_RELEASE_SCHEMA)

    def test_factory_rejects_missing_and_untyped_release(self) -> None:
        for release in (None, object()):
            with self.assertRaises(E1CommonProbeEC110OwnerScopeTokenFactoryError):
                create_e1_common_probe_ec110_owner_scope_token(
                    release,
                    source_gate_digest="0" * 64,
                    source_handoff_digest="0" * 64,
                )

    def test_contract_is_deterministic_and_fail_closed(self) -> None:
        first = audit_e1_common_probe_ec110_owner_scope_token_factory()
        second = audit_e1_common_probe_ec110_owner_scope_token_factory()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1CommonProbeEC110OwnerScopeTokenFactoryError):
            replace(first, owner_scope_token_creation_permitted=True)

    def test_audit_does_not_call_factory_production_write_or_decide(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec110_owner_scope_token_factory
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
