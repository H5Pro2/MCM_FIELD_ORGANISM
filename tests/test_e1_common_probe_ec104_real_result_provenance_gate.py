from __future__ import annotations

import ast
from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec103_synthetic_coordinator_e2e_fixture import (
    build_e1_common_probe_ec103_synthetic_r2_result,
    build_e1_common_probe_ec103_synthetic_r4_r8_result,
)
from mcm_field_organism.e1_common_probe_ec104_real_result_provenance_gate import (
    E1CommonProbeEC104RealResultProvenanceGateError,
    S1_EC104_REQUIRED_ATTESTATION_FIELDS,
    audit_e1_common_probe_ec104_real_result_provenance_gate,
)


class E1CommonProbeEC104RealResultProvenanceGateTests(unittest.TestCase):
    def test_current_ingress_remains_closed_without_attestation(self) -> None:
        gate = audit_e1_common_probe_ec104_real_result_provenance_gate()
        self.assertTrue(all(value for _, value in gate.checks))
        self.assertFalse(gate.actual_execution_provenance_established)
        self.assertFalse(gate.current_results_admissible_as_real_execution)
        self.assertFalse(gate.ec102_ingress_permitted)
        self.assertEqual(
            "REAL_RESULT_PROVENANCE_NOT_ESTABLISHED_INGRESS_CLOSED",
            gate.decision,
        )

    def test_ec103_outer_shapes_do_not_open_real_ingress(self) -> None:
        r2 = build_e1_common_probe_ec103_synthetic_r2_result()
        r4_r8 = build_e1_common_probe_ec103_synthetic_r4_r8_result()
        r2.__post_init__()
        r4_r8.__post_init__()
        gate = audit_e1_common_probe_ec104_real_result_provenance_gate()
        self.assertEqual(3208, r2.actual_field_steps_executed)
        self.assertTrue(r4_r8.authorization_consumed)
        self.assertFalse(gate.current_results_admissible_as_real_execution)

    def test_required_attestation_is_atomic_and_complete(self) -> None:
        self.assertEqual(
            (
                "producer_id",
                "one_shot_authorization_digest",
                "source_result_digests",
                "source_probe_receipt_digests",
                "accounted_field_steps",
                "producer_sequence",
                "attestation_digest",
            ),
            S1_EC104_REQUIRED_ATTESTATION_FIELDS,
        )

    def test_gate_is_deterministic_and_fail_closed(self) -> None:
        first = audit_e1_common_probe_ec104_real_result_provenance_gate()
        second = audit_e1_common_probe_ec104_real_result_provenance_gate()
        self.assertEqual(first.gate_digest, second.gate_digest)
        with self.assertRaises(E1CommonProbeEC104RealResultProvenanceGateError):
            replace(first, ec102_ingress_permitted=True)

    def test_audit_does_not_execute_extract_write_or_decide(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec104_real_result_provenance_gate
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
            "extract_e1_common_probe_ec102_coordinator_results",
            "run_e1_common_probe_n2_r2_real_mode_coordinator",
            "run_e1_common_probe_ec96_authorized_r4_r8_once",
            "run_e1_common_probe_real_formation_wrapper",
            "run_e1_common_probe_real_probe_wrapper",
            "decide_common_probe_evidence",
            "write_text",
            "write_bytes",
            "open",
        ):
            self.assertNotIn(forbidden, called)


if __name__ == "__main__":
    unittest.main()
