from __future__ import annotations

from dataclasses import fields, replace
import hashlib
import inspect
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wb_private_production_h0_types as s1wb
import mcm_field_organism._ppb1_s1wl_private_authorization_validator_adapter as s1wl
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


RESOURCE_GATE_DIGEST = hashlib.sha256(b"s1wl-resource-gate").hexdigest()
EXECUTION_ID = "ppb1.s1wl.injected.case-001"
EXPECTED_RECEIPT_DIGEST = (
    "ac2ac30f22d1772cd612d85b85f528b21e5cbfd4b3834e0b1098d2f46780da7c"
)


class PPB1S1WLPrivateAuthorizationValidatorAdapterTests(unittest.TestCase):
    def exact_text(self, execution_id=EXECUTION_ID, gate=RESOURCE_GATE_DIGEST):
        return s1wb.S1WB_AUTHORIZATION_TEMPLATE.format(
            execution_id=execution_id,
            contract_digest=s1wb.S1WB_CONTRACT_DIGEST,
            resource_gate_digest=gate,
        )

    def receipt(self, **changes):
        values = {
            "rendered_authorization_text": self.exact_text(),
            "execution_id": EXECUTION_ID,
            "resource_gate_digest": RESOURCE_GATE_DIGEST,
        }
        values.update(changes)
        return s1wl.validate_s1wl_injected_authorization_text(**values)

    def test_exact_injected_text_and_digest_roles_match(self) -> None:
        receipt = self.receipt()
        self.assertTrue(receipt.execution_id_format_valid)
        self.assertTrue(receipt.exact_text_match)
        self.assertTrue(receipt.digest_roles_match)
        self.assertTrue(receipt.injected_text_and_digests_match)
        self.assertFalse(receipt.ready_for_production_authorization)

    def test_receipt_is_canonical_and_deterministic(self) -> None:
        first = self.receipt()
        second = self.receipt()
        self.assertEqual(first, second)
        self.assertEqual(EXPECTED_RECEIPT_DIGEST, first.receipt_digest)

    def test_generic_okay_command_is_rejected(self) -> None:
        receipt = self.receipt(rendered_authorization_text="ok weiter")
        self.assertFalse(receipt.exact_text_match)
        self.assertFalse(receipt.injected_text_and_digests_match)

    def test_single_text_change_is_rejected(self) -> None:
        receipt = self.receipt(
            rendered_authorization_text=self.exact_text() + " "
        )
        self.assertFalse(receipt.exact_text_match)

    def test_execution_id_mismatch_is_rejected(self) -> None:
        receipt = self.receipt(execution_id="ppb1.s1wl.injected.case-002")
        self.assertFalse(receipt.exact_text_match)

    def test_invalid_execution_id_format_is_rejected(self) -> None:
        receipt = self.receipt(execution_id="not-an-execution-id")
        self.assertFalse(receipt.execution_id_format_valid)
        self.assertFalse(receipt.injected_text_and_digests_match)

    def test_each_bound_digest_role_fails_independently(self) -> None:
        drift = hashlib.sha256(b"drift").hexdigest()
        for role in (
            "contract_digest",
            "calibration_digest",
            "parent_plan_digest",
            "corrected_plan_digest",
        ):
            with self.subTest(role=role):
                receipt = self.receipt(**{role: drift})
                self.assertFalse(receipt.digest_roles_match)
                self.assertFalse(receipt.injected_text_and_digests_match)

    def test_malformed_digest_role_fails_closed(self) -> None:
        with self.assertRaises(s1wl.S1WLAuthorizationValidatorError):
            self.receipt(resource_gate_digest="not-a-digest")

    def test_h0d_adapter_reflects_only_injected_validation(self) -> None:
        accepted = s1wl.build_s1wl_injected_h0d_adapter(self.receipt())
        rejected = s1wl.build_s1wl_injected_h0d_adapter(
            self.receipt(rendered_authorization_text="ok weiter")
        )
        self.assertTrue(accepted.validate("H0D").passed)
        self.assertFalse(rejected.validate("H0D").passed)
        self.assertFalse(accepted.production_authorization_enabled)

    def test_all_effect_and_freshness_counts_remain_zero(self) -> None:
        receipt = self.receipt()
        self.assertEqual(
            (0,) * 8,
            (
                receipt.execution_id_freshness_check_count,
                receipt.authorization_instantiation_count,
                receipt.filesystem_read_count,
                receipt.filesystem_write_count,
                receipt.producer_resolution_count,
                receipt.producer_call_count,
                receipt.matrix_path_count,
                receipt.production_artifact_count,
            ),
        )
        self.assertFalse(receipt.production_authorization_instantiated)

    def test_receipt_tampering_and_production_entry_fail_closed(self) -> None:
        with self.assertRaises(s1wl.S1WLAuthorizationValidatorError):
            replace(self.receipt(), exact_text_match=False)
        with self.assertRaises(s1wl.S1WLAuthorizationValidatorError) as raised:
            s1wl.execute_s1wl_production_once()
        self.assertEqual(
            s1wl.S1WL_PRODUCTION_AUTHORIZATION_BLOCKED,
            raised.exception.code,
        )

    def test_module_is_runtime_free_private_and_snapshot_neutral(self) -> None:
        source = inspect.getsource(s1wl)
        for forbidden in (
            "import os",
            "from pathlib",
            "from tempfile",
            "S1WAProductionAuthorization",
            "open(",
            "write_text(",
            "write_bytes(",
            "_execute_s1vq_corrected_matrix",
            "SharedMCMField",
            "ReceptorContactFrame",
        ):
            self.assertNotIn(forbidden, source)
        names = {
            "S1WLInjectedAuthorizationValidationReceipt",
            "validate_s1wl_injected_authorization_text",
            "build_s1wl_injected_h0d_adapter",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
