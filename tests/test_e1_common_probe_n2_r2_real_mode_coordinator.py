from __future__ import annotations

import ast
import inspect
import textwrap
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorError,
    audit_e1_common_probe_n2_r2_real_mode_coordinator,
    run_e1_common_probe_n2_r2_real_mode_coordinator,
)


class E1CommonProbeN2R2RealModeCoordinatorTests(unittest.TestCase):
    def test_unreleased_call_fails_before_handoff_or_adapter_use(self) -> None:
        with self.assertRaises(E1CommonProbeN2R2RealModeCoordinatorError):
            run_e1_common_probe_n2_r2_real_mode_coordinator(
                None, preflight_and_owner_released=False
            )

    def test_static_audit_confirms_release_guard_and_keeps_execution_blocked(self) -> None:
        result = audit_e1_common_probe_n2_r2_real_mode_coordinator()
        self.assertTrue(result.real_mode_coordinator_implemented)
        self.assertTrue(result.preflight_required_before_adapter_calls)
        self.assertTrue(result.new_real_preflight_permitted)
        self.assertFalse(result.coordinator_execution_permitted)
        self.assertEqual(
            "REAL_MODE_COORDINATOR_IMPLEMENTED_NOT_PREFLIGHTED_NOT_RELEASED",
            result.decision,
        )

    def test_audit_does_not_invoke_real_coordinator(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_n2_r2_real_mode_coordinator)
        tree = ast.parse(textwrap.dedent(source))
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertNotIn("run_e1_common_probe_n2_r2_real_mode_coordinator", called)

    def test_coordinator_has_no_write_path(self) -> None:
        source = inspect.getsource(run_e1_common_probe_n2_r2_real_mode_coordinator)
        for forbidden in ("write_text", "write_bytes", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
