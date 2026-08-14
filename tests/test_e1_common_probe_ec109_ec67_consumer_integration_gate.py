from __future__ import annotations

import ast
from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec109_ec67_consumer_integration_gate import (
    E1CommonProbeEC109EC67ConsumerIntegrationGateError,
    S1_EC109_MIGRATION_ORDER,
    audit_e1_common_probe_ec109_ec67_consumer_integration_gate,
)


class E1CommonProbeEC109EC67ConsumerIntegrationGateTests(unittest.TestCase):
    def test_three_runtime_consumers_and_static_groups_are_mapped(self) -> None:
        gate = audit_e1_common_probe_ec109_ec67_consumer_integration_gate()
        self.assertEqual(3, gate.runtime_consumer_count)
        self.assertEqual(3, gate.static_consumer_group_count)
        self.assertEqual(("EC82", "EC84", "EC102"), tuple(item[0] for item in gate.runtime_consumers))
        self.assertTrue(gate.all_current_consumers_expect_bare_result)

    def test_producer_migration_precedes_consumers(self) -> None:
        self.assertLess(
            S1_EC109_MIGRATION_ORDER.index(
                "add-attested-envelope-return-path-inside-ec67"
            ),
            S1_EC109_MIGRATION_ORDER.index("migrate-ec82-to-envelope-input"),
        )
        self.assertLess(
            S1_EC109_MIGRATION_ORDER.index("migrate-ec82-to-envelope-input"),
            S1_EC109_MIGRATION_ORDER.index(
                "migrate-ec102-to-envelope-plus-attestation-input"
            ),
        )

    def test_all_integration_flags_remain_closed(self) -> None:
        gate = audit_e1_common_probe_ec109_ec67_consumer_integration_gate()
        self.assertFalse(gate.envelope_migration_complete)
        self.assertFalse(gate.ec67_attested_return_implemented)
        self.assertFalse(gate.ec82_migrated)
        self.assertFalse(gate.ec84_migrated)
        self.assertFalse(gate.ec102_migrated)
        self.assertFalse(gate.real_result_ingress_permitted)

    def test_gate_is_deterministic_and_fail_closed(self) -> None:
        first = audit_e1_common_probe_ec109_ec67_consumer_integration_gate()
        second = audit_e1_common_probe_ec109_ec67_consumer_integration_gate()
        self.assertEqual(first.gate_digest, second.gate_digest)
        with self.assertRaises(E1CommonProbeEC109EC67ConsumerIntegrationGateError):
            replace(first, ec67_attested_return_implemented=True)

    def test_audit_does_not_call_production_write_or_decide(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec109_ec67_consumer_integration_gate
        )
        called = {
            node.func.id
            if isinstance(node.func, ast.Name)
            else node.func.attr
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Call)
            and isinstance(node.func, (ast.Name, ast.Attribute))
        }
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator",
            "reduce_e1_common_probe_r2_ec82_completed_result",
            "build_e1_common_probe_r2_ec84_atomic_return",
            "extract_e1_common_probe_ec102_coordinator_results",
            "run_e1_common_probe_real_formation_receipt_adapter",
            "run_e1_common_probe_real_probe_receipt_adapter",
            "decide_common_probe_evidence",
            "write_text",
            "write_bytes",
            "open",
        ):
            self.assertNotIn(forbidden, called)


if __name__ == "__main__":
    unittest.main()
