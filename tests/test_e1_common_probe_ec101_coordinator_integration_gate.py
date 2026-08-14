from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec101_coordinator_integration_gate import (
    E1CommonProbeEC101CoordinatorIntegrationGateError,
    S1_EC101_CHECK_NAMES,
    audit_e1_common_probe_ec101_coordinator_integration_gate,
)


class E1CommonProbeEC101CoordinatorIntegrationGateTests(unittest.TestCase):
    def test_all_static_compatibility_checks_pass(self) -> None:
        result = audit_e1_common_probe_ec101_coordinator_integration_gate()
        self.assertEqual(S1_EC101_CHECK_NAMES, tuple(name for name, _ in result.checks))
        self.assertTrue(all(value for _, value in result.checks))
        self.assertEqual((("r2", 8), ("r4", 8), ("r8", 8)), result.required_probe_counts)
        self.assertEqual(24, result.total_source_probe_count)

    def test_gate_is_deterministic_and_closed(self) -> None:
        first = audit_e1_common_probe_ec101_coordinator_integration_gate()
        second = audit_e1_common_probe_ec101_coordinator_integration_gate()
        self.assertEqual(first.gate_digest, second.gate_digest)
        self.assertFalse(first.coordinator_execution_permitted)
        self.assertFalse(first.ec46_decision_permitted)
        self.assertTrue(first.new_owner_authorization_required_for_future_execution)

    def test_changed_gate_fails_closed(self) -> None:
        result = audit_e1_common_probe_ec101_coordinator_integration_gate()
        with self.assertRaises(E1CommonProbeEC101CoordinatorIntegrationGateError):
            replace(result, coordinator_execution_permitted=True)
        with self.assertRaises(E1CommonProbeEC101CoordinatorIntegrationGateError):
            replace(result, total_source_probe_count=23)

    def test_audit_source_has_no_execution_decision_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec101_coordinator_integration_gate
        )
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_ec96_authorized_r4_r8_once(",
            "run_e1_common_probe_real_probe_wrapper(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
