from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_ec78_owner_authorization import (
    E1CommonProbeN2R2EC78OwnerAuthorizationError,
    bind_e1_common_probe_n2_r2_ec78_owner_authorization,
)


class E1CommonProbeN2R2EC78OwnerAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from tests.test_e1_common_probe_n2_r2_ec77_final_release_gate import (
            E1CommonProbeN2R2EC77FinalReleaseGateTests,
        )
        from mcm_field_organism.e1_common_probe_n2_r2_ec77_final_release_gate import (
            prepare_e1_common_probe_n2_r2_ec77_final_release_gate,
        )

        E1CommonProbeN2R2EC77FinalReleaseGateTests.setUpClass()
        source = E1CommonProbeN2R2EC77FinalReleaseGateTests
        cls.gate = prepare_e1_common_probe_n2_r2_ec77_final_release_gate(
            source.project_root,
            source.route,
            source.preflight,
            source.contract,
        )

    def test_explicit_decision_binds_exactly_one_closed_authorization(self) -> None:
        receipt = bind_e1_common_probe_n2_r2_ec78_owner_authorization(
            self.gate, explicit_owner_authorized=True
        )

        self.assertEqual(1, receipt.authorized_execution_count)
        self.assertEqual(3208, receipt.maximum_total_field_steps)
        self.assertFalse(receipt.execution_started)
        self.assertFalse(receipt.automatic_retry_permitted)

    def test_missing_explicit_decision_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeN2R2EC78OwnerAuthorizationError,
            "explicit owner authorization",
        ):
            bind_e1_common_probe_n2_r2_ec78_owner_authorization(
                self.gate, explicit_owner_authorized=False
            )

    def test_binding_calls_no_real_path_or_writer(self) -> None:
        source = inspect.getsource(
            bind_e1_common_probe_n2_r2_ec78_owner_authorization
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
