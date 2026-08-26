from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs" / (
    "S1XB_PPB1_STATISCHER_MATERIALISIERUNGS_REGISTRY_UND_"
    "NICHTAUSFUEHRUNGSAUDIT_V1.json"
)
EXPECTED_AUDIT_DIGEST = (
    "e6aa23306023106dc56b1cfa85970547c76d249d0c8d428149506c6d341ff903"
)


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


class PPB1S1XBStaticMaterializationRegistryNonexecutionAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_contract_and_all_bound_files_are_exact(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "2c3e36d4e3acaa05a5158a5e209b445f925e8d9b7926794a7b82e0c91dbc093c",
            audit["parent_s1xa_contract_digest"],
        )
        paths = {
            "s1xa_contract_file": "docs/S1XA_PPB1_STATISCHER_FIXTURE_UND_60_ZELLEN_MATRIXMATERIALISIERUNGSVERTRAG_V1.json",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "ppb1_receptor_profiles": "mcm_field_organism/_ppb1_receptor_profiles.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "s1vn_baseline_inventory": "mcm_field_organism/_ppb1_s1vn_matrix.py",
        }
        for role, relative_path in paths.items():
            self.assertEqual(
                audit["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest(),
            )

    def test_all_eighteen_static_roles_pass(self) -> None:
        audit = load_audit()
        self.assertEqual(18, len(audit["checked_roles"]))
        self.assertEqual(18, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])

    def test_registry_remains_exact_and_digest_bound(self) -> None:
        registry = load_audit()["registry_audit"]
        self.assertEqual(60, registry["cell_count"])
        self.assertEqual(60, registry["unique_cell_count"])
        self.assertEqual(
            "77d9437ce497bf298029c0b017cbb91df7f92a06d678c500d09319158b52668d",
            registry["registry_digest"],
        )

    def test_existing_baselines_are_not_misclassified_as_read_only(self) -> None:
        inventory = load_audit()["existing_baseline_inventory"]
        self.assertEqual(
            {"B01", "B03", "B04", "B07"},
            set(inventory["reusable_semantic_roles"]),
        )
        self.assertFalse(inventory["existing_step_is_read_only"])
        self.assertFalse(inventory["direct_reuse_for_s1xa_probe_allowed"])
        self.assertFalse(inventory["last_vector_read_only_role_exists"])

        source = (ROOT / inventory["source"]).read_text(encoding="utf-8")
        tree = ast.parse(source)
        advance = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == inventory["existing_step_function"]
        )
        string_constants = {
            node.value
            for node in ast.walk(advance)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        self.assertTrue({"B01", "B03", "B04", "B07"} <= string_constants)
        self.assertNotIn("last-vector-distance", string_constants)
        self.assertTrue(
            any(
                isinstance(node, ast.BinOp)
                and isinstance(node.op, ast.Add)
                and isinstance(node.left, ast.Attribute)
                and node.left.attr == "accepted_step_count"
                for node in ast.walk(advance)
            )
        )

    def test_exactly_three_bounded_implementation_gaps_remain(self) -> None:
        gaps = load_audit()["bounded_implementation_gaps"]
        self.assertEqual(3, len(gaps))
        self.assertTrue(all(not gap["blocks_contract_validity"] for gap in gaps))

    def test_decision_and_claim_boundary_are_narrow(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "PASS_STATIC_MATERIALIZATION_CONTRACT_READY_FOR_PRIVATE_IMPLEMENTATION_WITH_BOUND_GAPS",
            audit["decision"],
        )
        self.assertEqual(
            "NO_TECHNICAL_FUNCTION_RESULT_OR_MCM_MEMORY_CLAIM",
            audit["claim_boundary"],
        )

    def test_every_execution_counter_is_zero(self) -> None:
        counters = load_audit()["execution_counters"]
        self.assertEqual(8, len(counters))
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_next_step_remains_private_and_synthetic(self) -> None:
        self.assertEqual(
            "S1XC_PRIVATE_PURE_FIXTURE_REGISTRY_AND_READ_ONLY_BASELINE_IMPLEMENTATION_SYNTHETIC_TESTS_ONLY",
            load_audit()["next_step"],
        )


if __name__ == "__main__":
    unittest.main()
