from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_r2_ec86_owner_authorization import (
    E1CommonProbeR2EC86OwnerAuthorizationError,
    bind_e1_common_probe_r2_ec86_owner_authorization,
)
from tests.test_e1_common_probe_r2_ec85_measurement_preflight import (
    E1CommonProbeR2EC85MeasurementPreflightTests,
)
from mcm_field_organism.e1_common_probe_r2_ec85_measurement_preflight import (
    audit_e1_common_probe_r2_ec85_measurement_preflight,
)


class E1CommonProbeR2EC86OwnerAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1CommonProbeR2EC85MeasurementPreflightTests.setUpClass()
        source = E1CommonProbeR2EC85MeasurementPreflightTests
        cls.preflight = audit_e1_common_probe_r2_ec85_measurement_preflight(
            source.root, source.technical, source.contract
        )

    def test_explicit_owner_decision_binds_exactly_one_run(self) -> None:
        receipt = bind_e1_common_probe_r2_ec86_owner_authorization(
            self.preflight, explicit_owner_authorized=True
        )
        self.assertEqual(1, receipt.authorized_execution_count)
        self.assertEqual(3208, receipt.maximum_total_field_steps)
        self.assertEqual(6, receipt.expected_scalar_contrast_count)
        self.assertTrue(receipt.atomic_ec84_return_required)
        self.assertFalse(receipt.execution_started)
        self.assertFalse(receipt.automatic_retry_permitted)

    def test_missing_explicit_decision_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeR2EC86OwnerAuthorizationError, "explicit owner"
        ):
            bind_e1_common_probe_r2_ec86_owner_authorization(
                self.preflight, explicit_owner_authorized=False
            )

    def test_binding_calls_no_execution_handoff_or_writer(self) -> None:
        source = inspect.getsource(bind_e1_common_probe_r2_ec86_owner_authorization)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "build_e1_common_probe_r2_ec84_atomic_return(",
            "reduce_e1_common_probe_r2_ec82_completed_result(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
