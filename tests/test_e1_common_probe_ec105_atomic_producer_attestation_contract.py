from __future__ import annotations

import ast
from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec105_atomic_producer_attestation_contract import (
    E1CommonProbeEC105AtomicProducerAttestationContractError,
    S1_EC105_INGRESS_ATTESTATION_SCHEMA,
    S1_EC105_PRODUCER_RECEIPT_SCHEMA,
    audit_e1_common_probe_ec105_atomic_producer_attestation_contract,
)


class E1CommonProbeEC105AtomicProducerAttestationContractTests(unittest.TestCase):
    def test_contract_binds_two_producers_and_closed_ingress(self) -> None:
        contract = audit_e1_common_probe_ec105_atomic_producer_attestation_contract()
        self.assertEqual(2, contract.total_source_result_count)
        self.assertEqual(24, contract.total_source_probe_count)
        self.assertEqual(22456, contract.total_accounted_field_steps)
        self.assertTrue(contract.posthoc_self_attestation_forbidden)
        self.assertFalse(contract.real_result_ingress_permitted)

    def test_receipt_and_ingress_schemas_bind_required_lineage(self) -> None:
        self.assertIn("one_shot_authorization_digest", S1_EC105_PRODUCER_RECEIPT_SCHEMA)
        self.assertIn("source_probe_receipt_digests", S1_EC105_PRODUCER_RECEIPT_SCHEMA)
        self.assertIn("r2_producer_receipt_digest", S1_EC105_INGRESS_ATTESTATION_SCHEMA)
        self.assertIn("r4_r8_producer_receipt_digest", S1_EC105_INGRESS_ATTESTATION_SCHEMA)
        self.assertIn("same_objects_forwarded_to_ec102", S1_EC105_INGRESS_ATTESTATION_SCHEMA)

    def test_trust_scope_is_contractual_not_cryptographic(self) -> None:
        contract = audit_e1_common_probe_ec105_atomic_producer_attestation_contract()
        self.assertTrue(contract.digest_chain_detects_accidental_lineage_change)
        self.assertFalse(contract.cryptographic_or_external_execution_proof_provided)
        self.assertEqual("in-process-contractual-not-cryptographic", contract.trust_scope)

    def test_contract_is_deterministic_and_fail_closed(self) -> None:
        first = audit_e1_common_probe_ec105_atomic_producer_attestation_contract()
        second = audit_e1_common_probe_ec105_atomic_producer_attestation_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1CommonProbeEC105AtomicProducerAttestationContractError):
            replace(first, producer_integration_implemented=True)

    def test_audit_does_not_call_production_write_or_decide(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec105_atomic_producer_attestation_contract
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
            "run_e1_common_probe_ec96_authorized_r4_r8_once",
            "extract_e1_common_probe_ec102_coordinator_results",
            "run_e1_common_probe_real_formation_wrapper",
            "run_e1_common_probe_real_probe_wrapper",
            "decide_common_probe_evidence",
            "write_text",
            "write_bytes",
            "open",
        ):
            self.assertNotIn(forbidden, called)


if __name__ == "__main__":
    unittest.main()
