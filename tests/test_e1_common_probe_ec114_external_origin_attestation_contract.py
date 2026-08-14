from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec110_owner_scope_token_factory import (
    S1_EC110_EXTERNAL_RELEASE_SCHEMA,
)
from mcm_field_organism.e1_common_probe_ec114_external_origin_attestation_contract import (
    E1CommonProbeEC114ExternalOriginAttestationContractError,
    S1_EC114_RELEASE_FIELD_MAPPING,
    S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA,
    audit_e1_common_probe_ec114_external_origin_attestation_contract,
)


class E1CommonProbeEC114ExternalOriginAttestationContractTests(unittest.TestCase):
    def test_contract_maps_exact_ec110_release_schema(self) -> None:
        contract = audit_e1_common_probe_ec114_external_origin_attestation_contract()
        self.assertEqual(S1_EC110_EXTERNAL_RELEASE_SCHEMA, contract.external_release_schema)
        self.assertEqual(
            S1_EC110_EXTERNAL_RELEASE_SCHEMA,
            tuple(name for name, _ in S1_EC114_RELEASE_FIELD_MAPPING),
        )
        self.assertEqual(11, len(S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA))

    def test_external_origin_evidence_is_explicit_and_absent(self) -> None:
        contract = audit_e1_common_probe_ec114_external_origin_attestation_contract()
        self.assertIn(
            "authenticated_owner_principal_digest",
            contract.required_external_evidence_schema,
        )
        self.assertIn(
            "fresh_single_use_nonce_digest",
            contract.required_external_evidence_schema,
        )
        self.assertFalse(contract.external_origin_evidence_present)
        self.assertFalse(contract.external_attestation_implemented)

    def test_token_execution_and_real_ingress_remain_closed(self) -> None:
        contract = audit_e1_common_probe_ec114_external_origin_attestation_contract()
        self.assertFalse(contract.external_release_issued)
        self.assertFalse(contract.owner_scope_token_creation_permitted)
        self.assertFalse(contract.execution_permitted)
        self.assertFalse(contract.real_result_ingress_permitted)

    def test_contract_is_deterministic(self) -> None:
        first = audit_e1_common_probe_ec114_external_origin_attestation_contract()
        second = audit_e1_common_probe_ec114_external_origin_attestation_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)

    def test_opening_any_closed_flag_fails(self) -> None:
        contract = audit_e1_common_probe_ec114_external_origin_attestation_contract()
        for field_name in (
            "external_origin_evidence_present",
            "external_attestation_implemented",
            "external_release_issued",
            "owner_scope_token_creation_permitted",
            "execution_permitted",
        ):
            with self.subTest(field_name=field_name):
                with self.assertRaises(
                    E1CommonProbeEC114ExternalOriginAttestationContractError
                ):
                    replace(contract, **{field_name: True})

    def test_audit_does_not_call_sensitive_paths(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec114_external_origin_attestation_contract
        )
        for forbidden in (
            "classify_e1_common_probe_ec112_owner_message(",
            "validate_e1_common_probe_ec113_synthetic_bridge_candidate(",
            "create_e1_common_probe_ec110_owner_scope_token(",
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "decide_common_probe_evidence(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
