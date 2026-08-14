from __future__ import annotations

import ast
import inspect
import textwrap
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_real_call_adapters import (
    audit_e1_common_probe_n2_r2_real_call_adapters,
    build_e1_common_probe_real_fresh_field_adapter,
    run_e1_common_probe_real_formation_receipt_adapter,
    run_e1_common_probe_real_probe_receipt_adapter,
)


class E1CommonProbeN2R2RealCallAdapterTests(unittest.TestCase):
    def test_all_three_adapter_signatures_are_narrow(self) -> None:
        self.assertEqual(
            ("resolved", "initial_field", "initial_state"),
            tuple(inspect.signature(run_e1_common_probe_real_formation_receipt_adapter).parameters),
        )
        self.assertEqual(
            ("binding", "initial_field"),
            tuple(inspect.signature(build_e1_common_probe_real_fresh_field_adapter).parameters),
        )
        self.assertEqual(
            ("resolved", "fresh", "formation"),
            tuple(inspect.signature(run_e1_common_probe_real_probe_receipt_adapter).parameters),
        )

    def test_static_audit_confirms_order_without_releasing_execution(self) -> None:
        result = audit_e1_common_probe_n2_r2_real_call_adapters()
        self.assertTrue(result.wrapper_then_converter_order_exact)
        self.assertTrue(result.coordinator_binding_implementation_permitted)
        self.assertFalse(result.adapter_execution_permitted)
        self.assertEqual("REAL_CALL_ADAPTERS_IMPLEMENTED_STATICALLY_NOT_RELEASED", result.decision)

    def test_audit_does_not_invoke_adapters(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_n2_r2_real_call_adapters)
        tree = ast.parse(textwrap.dedent(source))
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue({
            "run_e1_common_probe_real_formation_receipt_adapter",
            "build_e1_common_probe_real_fresh_field_adapter",
            "run_e1_common_probe_real_probe_receipt_adapter",
        }.isdisjoint(called))


if __name__ == "__main__":
    unittest.main()
