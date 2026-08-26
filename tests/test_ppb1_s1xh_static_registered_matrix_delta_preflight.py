from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_PATH = ROOT / "docs" / (
    "S1XH_PPB1_STATISCHER_REGISTERED_MATRIX_IMPLEMENTIERUNGSDELTA_"
    "UND_AUSFUEHRUNGSPREFLIGHT_V1.json"
)
EXPECTED_PREFLIGHT_DIGEST = (
    "11971a2c994806c2abd51540d5bd931c5fd70290c771e43fa248c157c009ea13"
)


def load_preflight():
    return json.loads(PREFLIGHT_PATH.read_text(encoding="utf-8"))


def canonical_json_digest(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class PPB1S1XHStaticRegisteredMatrixDeltaPreflightTests(unittest.TestCase):
    def test_preflight_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_preflight(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(
            EXPECTED_PREFLIGHT_DIGEST, hashlib.sha256(encoded).hexdigest()
        )

    def test_parent_and_s1xe_contract_digests_are_canonical(self) -> None:
        preflight = load_preflight()
        self.assertEqual(
            canonical_json_digest(
                ROOT / "docs/S1XG_PPB1_STATISCHER_MINIATURRUNNER_ABSCHLUSSAUDIT_V1.json"
            ),
            preflight["parent_s1xg_audit_digest"],
        )
        self.assertEqual(
            canonical_json_digest(
                ROOT
                / "docs/S1XE_PPB1_STATISCHER_PRIVATER_MATRIXRUNNER_RECEIPT_"
                "UND_ENTSCHEIDUNGSVERTRAG_V1.json"
            ),
            preflight["bound_s1xe_contract_digest"],
        )

    def test_all_bound_files_match_exact_hashes(self) -> None:
        paths = {
            "s1xe_contract_file": (
                "docs/S1XE_PPB1_STATISCHER_PRIVATER_MATRIXRUNNER_RECEIPT_"
                "UND_ENTSCHEIDUNGSVERTRAG_V1.json"
            ),
            "s1xg_audit_file": "docs/S1XG_PPB1_STATISCHER_MINIATURRUNNER_ABSCHLUSSAUDIT_V1.json",
            "s1xf_miniature_runner": "mcm_field_organism/_ppb1_s1xf_private_miniature_runner.py",
            "s1xc_fixture_registry": "mcm_field_organism/_ppb1_s1xc_fixture_registry.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                load_preflight()["bound_file_digests"][role],
            )

    def test_eight_roles_are_reusable_without_field_change(self) -> None:
        self.assertEqual(8, len(load_preflight()["reusable_roles"]))

    def test_three_existing_miniature_roles_are_not_full_matrix_roles(self) -> None:
        roles = load_preflight()["non_reusable_as_full_matrix_roles"]
        self.assertEqual(3, len(roles))
        self.assertEqual(
            {"S1XF_RUN_S1XF_MINIATURE_CONTRACT", "S1XF_CELL_RECEIPT", "S1XF_MATRIX_RECEIPT"},
            {item["existing_role"] for item in roles},
        )

    def test_exactly_three_implementation_gaps_and_one_authorization_gate_remain(self) -> None:
        preflight = load_preflight()
        self.assertEqual(3, len(preflight["implementation_gaps"]))
        self.assertFalse(preflight["authorization_gate"]["currently_present"])
        self.assertFalse(
            preflight["authorization_gate"][
                "implementation_authorization_is_execution_authorization"
            ]
        )

    def test_current_source_has_no_full_runner_plan_consumption_or_aggregator(self) -> None:
        source = (
            ROOT / "mcm_field_organism/_ppb1_s1xf_private_miniature_runner.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        attributes = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        names = {
            node.name for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        self.assertNotIn("cell_plans", attributes)
        self.assertFalse(any("registered" in name and "runner" in name for name in names))
        self.assertNotIn("technical_function_decision", source)
        self.assertNotIn("baseline_explanation_decision", source)

    def test_full_call_budget_registry_and_receipt_roles_are_exact(self) -> None:
        preflight = load_preflight()
        budget = preflight["required_full_runner_call_budget"]
        self.assertEqual((1, 2, 6, 10, 50, 60, 0), tuple(budget.values()))
        order = preflight["required_registered_order"]
        self.assertEqual(10, order["candidate_cell_count"])
        self.assertEqual(50, order["baseline_cell_count"])
        self.assertEqual(19, len(preflight["required_new_cell_receipt_roles"]))
        self.assertEqual(15, len(preflight["required_new_matrix_receipt_roles"]))

    def test_aggregation_is_same_baseline_all_ten_and_prebound_not_observed(self) -> None:
        aggregation = load_preflight()["aggregation_binding"]
        self.assertTrue(aggregation["candidate_pass_requires_all_ten_cells_and_both_formations"])
        self.assertTrue(
            aggregation[
                "one_baseline_must_match_all_ten_candidate_behavioral_outputs"
            ]
        )
        self.assertFalse(aggregation["mixing_baselines_across_cells_allowed"])
        self.assertFalse(aggregation["expected_value_is_observed_result"])

    def test_preflight_is_not_ready_and_all_execution_counters_are_zero(self) -> None:
        preflight = load_preflight()
        self.assertEqual(
            "NOT_READY_THREE_IMPLEMENTATION_GAPS_AND_EXECUTION_AUTHORIZATION_MISSING",
            preflight["decision"],
        )
        self.assertTrue(all(value == 0 for value in preflight["execution_counters"].values()))

    def test_next_step_is_private_implementation_not_registered_execution(self) -> None:
        next_step = load_preflight()["next_step"]
        self.assertIn("PRIVATE_FULL_RUNNER_AND_RECEIPT_IMPLEMENTATION", next_step)
        self.assertIn("NO_REGISTERED_MATRIX_EXECUTION", next_step)


if __name__ == "__main__":
    unittest.main()
