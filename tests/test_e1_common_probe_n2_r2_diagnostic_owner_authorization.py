from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_diagnostic_owner_authorization import (
    E1CommonProbeN2R2DiagnosticOwnerAuthorizationError,
    bind_e1_common_probe_n2_r2_diagnostic_owner_authorization,
)


class E1CommonProbeN2R2DiagnosticOwnerAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from tests.test_e1_common_probe_n2_r2_diagnostic_one_shot_contract import (
            E1CommonProbeN2R2DiagnosticOneShotContractTests,
        )
        from mcm_field_organism.e1_common_probe_n2_r2_diagnostic_one_shot_contract import (
            prepare_e1_common_probe_n2_r2_diagnostic_one_shot_contract,
        )

        E1CommonProbeN2R2DiagnosticOneShotContractTests.setUpClass()
        cls.contract = prepare_e1_common_probe_n2_r2_diagnostic_one_shot_contract(
            E1CommonProbeN2R2DiagnosticOneShotContractTests.preflight
        )

    def test_explicit_decision_binds_exactly_one_closed_authorization(self) -> None:
        receipt = bind_e1_common_probe_n2_r2_diagnostic_owner_authorization(
            self.contract, explicit_owner_authorized=True
        )
        self.assertEqual(1, receipt.authorized_execution_count)
        self.assertEqual(3208, receipt.maximum_total_field_steps)
        self.assertTrue(receipt.nonpersistent_only)
        self.assertFalse(receipt.execution_started)
        self.assertFalse(receipt.automatic_retry_permitted)

    def test_missing_explicit_decision_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeN2R2DiagnosticOwnerAuthorizationError,
            "explicit owner authorization",
        ):
            bind_e1_common_probe_n2_r2_diagnostic_owner_authorization(
                self.contract, explicit_owner_authorized=False
            )

    def test_binding_does_not_execute_or_persist(self) -> None:
        source = inspect.getsource(
            bind_e1_common_probe_n2_r2_diagnostic_owner_authorization
        )
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_real_formation_receipt_adapter(",
            "run_e1_common_probe_real_probe_receipt_adapter(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
