from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_contact_axis_audit import (
    E1CommonProbeContactAxisAuditError,
    audit_e1_common_probe_contact_axis,
)


class E1CommonProbeContactAxisAuditTests(unittest.TestCase):
    def test_missing_axis_is_detected_before_real_binding(self) -> None:
        result = audit_e1_common_probe_contact_axis()
        self.assertEqual((1, 2), result.required_contact_counts)
        self.assertEqual(24, result.current_sample_count)
        self.assertEqual(48, result.required_sample_count)
        self.assertFalse(result.existing_adapter_contact_axis_complete)
        self.assertFalse(result.real_kernel_binding_permitted)

    def test_n1_remains_a_required_control(self) -> None:
        result = audit_e1_common_probe_contact_axis()
        self.assertEqual("required-control-not-discardable", result.n1_role)
        self.assertEqual(
            "candidate-branch-not-generalizable-to-n1", result.n2_role
        )

    def test_bypassing_correction_fails_closed(self) -> None:
        result = audit_e1_common_probe_contact_axis()
        for update in (
            {"real_kernel_binding_permitted": True},
            {"field_execution_permitted": True},
            {"existing_adapter_contact_axis_complete": True},
        ):
            with self.subTest(update=update):
                with self.assertRaises(E1CommonProbeContactAxisAuditError):
                    replace(result, **update)

    def test_audit_contains_no_adapter_call_field_or_write_path(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_contact_axis)
        for forbidden in (
            "run_e1_common_probe_eight_role_adapter_fixture(",
            "run_prepared_real_formation_arm_in_memory",
            "advance_frozen_e1_fast_shared_field_transient",
            "advance_neutral_fast_shared_field_transient",
            "open(",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
