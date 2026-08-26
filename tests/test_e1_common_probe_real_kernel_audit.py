from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_real_kernel_audit import (
    E1CommonProbeRealKernelAuditError,
    audit_e1_common_probe_real_kernels,
)


class E1CommonProbeRealKernelAuditTests(unittest.TestCase):
    def test_existing_kernels_are_sufficient_but_adapter_is_not(self) -> None:
        result = audit_e1_common_probe_real_kernels()
        self.assertTrue(result.existing_kernels_sufficient)
        self.assertFalse(result.existing_eight_role_adapter_complete)
        self.assertTrue(result.narrow_adapter_implementation_permitted)
        self.assertFalse(result.field_execution_permitted)

    def test_exact_missing_slots_are_reported(self) -> None:
        result = audit_e1_common_probe_real_kernels()
        self.assertEqual(
            (
                "p0-reset-ab",
                "p0-reset-ba",
                "e1-formation-ablated-ab",
                "e1-formation-ablated-ba",
            ),
            result.required_new_adapter_slots,
        )

    def test_claim_or_execution_release_fails_closed(self) -> None:
        result = audit_e1_common_probe_real_kernels()
        for update in (
            {"field_execution_permitted": True},
            {"memory_claim_permitted": True},
            {"existing_eight_role_adapter_complete": True},
        ):
            with self.subTest(update=update):
                with self.assertRaises(E1CommonProbeRealKernelAuditError):
                    replace(result, **update)

    def test_audit_does_not_invoke_field_kernels_or_write(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_real_kernels)
        for forbidden in (
            "run_prepared_real_formation_arm_in_memory(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_neutral_fast_shared_field_transient(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
