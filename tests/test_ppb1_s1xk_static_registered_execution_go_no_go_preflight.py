from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1XK_PPB1_STATISCHER_REGISTRIERTER_AUSFUEHRUNGS_GO_NO_GO_UND_AUTORISIERUNGSPREFLIGHT_V1.json"
S1XI_SOURCE = ROOT / "mcm_field_organism/_ppb1_s1xi_private_full_runner.py"
EXPECTED_AUDIT_DIGEST = (
    "bb1a605d6dd1a98da7f414ec2f5b6ee8b282f9ce719fd9dd4c318af4824fef95"
)


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class PPB1S1XKStaticRegisteredExecutionPreflightTests(unittest.TestCase):
    def test_preflight_is_canonical_and_digest_bound(self) -> None:
        self.assertEqual(EXPECTED_AUDIT_DIGEST, canonical_digest(load_audit()))

    def test_parent_and_contract_digests_are_canonical(self) -> None:
        audit = load_audit()
        for role, relative in (
            ("parent_s1xj_audit_digest", "docs/S1XJ_PPB1_STATISCHER_VOLLFORM_RUNNER_SPERREN_RECEIPT_UND_AGGREGATOR_ABSCHLUSSAUDIT_V1.json"),
            ("bound_s1xe_contract_digest", "docs/S1XE_PPB1_STATISCHER_PRIVATER_MATRIXRUNNER_RECEIPT_UND_ENTSCHEIDUNGSVERTRAG_V1.json"),
        ):
            value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual(audit[role], canonical_digest(value))

    def test_all_bound_file_digests_are_exact(self) -> None:
        paths = {
            "s1xj_audit_file": "docs/S1XJ_PPB1_STATISCHER_VOLLFORM_RUNNER_SPERREN_RECEIPT_UND_AGGREGATOR_ABSCHLUSSAUDIT_V1.json",
            "s1xj_document": "docs/S1XJ_PPB1_STATISCHER_VOLLFORM_RUNNER_SPERREN_RECEIPT_UND_AGGREGATOR_ABSCHLUSSAUDIT.md",
            "s1xj_tests": "tests/test_ppb1_s1xj_static_full_runner_lock_receipt_aggregator_audit.py",
            "s1xi_source": "mcm_field_organism/_ppb1_s1xi_private_full_runner.py",
            "s1xc_fixture_registry": "mcm_field_organism/_ppb1_s1xc_fixture_registry.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "s1xf_miniature_runner": "mcm_field_organism/_ppb1_s1xf_private_miniature_runner.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                load_audit()["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_nine_technical_gates_pass_and_authorization_gate_is_open(self) -> None:
        audit = load_audit()
        technical = audit["go_no_go_gates"][:-1]
        authorization = audit["go_no_go_gates"][-1]
        self.assertEqual(9, len(technical))
        self.assertTrue(all(item["passed"] for item in technical))
        self.assertEqual(
            "S1XK_EXPLICIT_OWNER_EXECUTION_AUTHORIZATION_PRESENT",
            authorization["gate_id"],
        )
        self.assertFalse(authorization["passed"])
        self.assertFalse(audit["technical_gate_summary"]["additional_runner_implementation_required"])
        self.assertFalse(audit["technical_gate_summary"]["source_file_unlock_edit_allowed"])

    def test_runner_source_remains_private_false_locked_and_registered(self) -> None:
        source = S1XI_SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assignment = next(
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "S1XI_REGISTERED_EXECUTION_ENABLED"
                for target in node.targets
            )
        )
        self.assertIs(assignment.value.value, False)
        entry = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "run_s1xi_registered_matrix"
        )
        entry_source = ast.get_source_segment(source, entry)
        self.assertIn("S1XI_REGISTERED_EXECUTION_LOCKED", entry_source)
        self.assertIn("_execute_plan_set(registered=True)", entry_source)
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            self.assertNotIn("s1xi", (ROOT / relative).read_text(encoding="utf-8").lower())

    def test_execution_budget_is_exact_finite_and_retry_free(self) -> None:
        budget = load_audit()["registered_execution_budget"]
        self.assertEqual(
            {
                "process_count": 1,
                "registered_runner_call_count": 1,
                "materializer_call_count": 1,
                "initial_state_call_count": 2,
                "formation_advance_call_count": 6,
                "candidate_probe_call_count": 10,
                "baseline_probe_call_count": 50,
                "registered_matrix_cell_count": 60,
                "substitute_matrix_cell_count": 0,
                "retry_count": 0,
            },
            budget,
        )

    def test_registered_identity_and_full_order_are_bound(self) -> None:
        identity = load_audit()["registered_execution_identity"]
        self.assertEqual(2, len(identity["ordered_modality_ids"]))
        self.assertEqual(6, len(identity["ordered_system_ids"]))
        self.assertEqual(5, len(identity["ordered_probe_classes"]))
        self.assertEqual(
            "s1xa.auditory.ppb1.exact-positive", identity["first_cell_id"]
        )
        self.assertEqual(
            "s1xa.visual.last-vector-distance.distinct-negative",
            identity["last_cell_id"],
        )

    def test_authorization_text_and_process_local_protocol_are_exact(self) -> None:
        audit = load_audit()
        text = audit["required_owner_authorization_text"]
        self.assertEqual(
            audit["required_owner_authorization_text_sha256"],
            hashlib.sha256(text.encode("utf-8")).hexdigest(),
        )
        protocol = audit["one_process_authorization_protocol"]
        self.assertTrue(protocol["unlock_is_process_local_only"])
        self.assertTrue(protocol["source_file_must_remain_unchanged"])
        self.assertTrue(protocol["set_registered_execution_enabled_false_in_finally"])
        self.assertFalse(protocol["second_call_or_retry_allowed"])
        self.assertFalse(protocol["substitute_entry_call_allowed"])

    def test_outcomes_and_interpretation_boundary_are_narrow(self) -> None:
        audit = load_audit()
        self.assertEqual(4, len(audit["allowed_registered_outcomes"]))
        boundary = audit["interpretation_boundary"]
        self.assertTrue(boundary["method_invalid_has_no_function_decision"])
        self.assertFalse(boundary["technical_function_pass_is_capability_claim"])
        self.assertFalse(boundary["baseline_explained_is_mcm_specific_result"])
        self.assertFalse(boundary["unexplained_engineering_difference_is_memory_claim"])

    def test_decision_is_ready_but_execution_remains_closed_and_zero(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "TECHNICALLY_GO_AWAITING_EXPLICIT_OWNER_AUTHORIZATION",
            audit["decision"],
        )
        self.assertFalse(audit["owner_authorization_present"])
        self.assertFalse(audit["execution_permitted"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
