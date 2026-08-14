from __future__ import annotations

import ast
import inspect
import textwrap
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_real_wrapper_binding_audit import (
    audit_e1_common_probe_n2_r2_real_wrapper_binding,
)


class E1CommonProbeN2R2RealWrapperBindingAuditTests(unittest.TestCase):
    def test_finds_positive_step_receipt_gap(self) -> None:
        result = audit_e1_common_probe_n2_r2_real_wrapper_binding()
        self.assertTrue(result.fresh_field_directly_compatible)
        self.assertFalse(result.formation_positive_step_receipt_supported)
        self.assertFalse(result.probe_positive_step_receipt_supported)
        self.assertFalse(result.coordinator_positive_step_result_supported)
        self.assertFalse(result.real_wrapper_binding_ready)
        self.assertTrue(result.positive_step_receipt_implementation_permitted)
        self.assertEqual("KORREKTUR_POSITIVE_STEP_RECEIPTS_MISSING", result.decision)

    def test_audit_does_not_invoke_coordinator_or_wrappers(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_n2_r2_real_wrapper_binding)
        tree = ast.parse(textwrap.dedent(source))
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue({
            "run_e1_common_probe_n2_r2_execution_coordinator_fixture",
            "run_e1_common_probe_real_formation_wrapper",
            "build_e1_common_probe_fresh_field",
            "run_e1_common_probe_real_probe_wrapper",
            "open",
        }.isdisjoint(called_names))
        self.assertNotIn("write_text", source)
        self.assertNotIn("write_bytes", source)

    def test_all_static_checks_are_explicitly_satisfied(self) -> None:
        result = audit_e1_common_probe_n2_r2_real_wrapper_binding()
        self.assertTrue(all(passed for _, passed in result.checks))
        self.assertFalse(result.wrapper_execution_permitted)
        self.assertFalse(result.memory_claim_permitted)


if __name__ == "__main__":
    unittest.main()
