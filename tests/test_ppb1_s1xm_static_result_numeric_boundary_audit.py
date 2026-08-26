from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1XM_PPB1_STATISCHER_ERGEBNIS_RECEIPT_UND_NUMERISCHER_GRENZWERTAUDIT_V1.json"
EXPECTED_AUDIT_DIGEST = (
    "9030b8879db79fc4095bcde496439873c263e2f8fcbaaf404d4be5cceb38ca6a"
)


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class PPB1S1XMStaticResultNumericBoundaryAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        self.assertEqual(
            EXPECTED_AUDIT_DIGEST,
            canonical_digest(load_json(AUDIT_PATH.relative_to(ROOT).as_posix())),
        )

    def test_parent_result_and_all_bound_files_are_exact(self) -> None:
        audit = load_json(AUDIT_PATH.relative_to(ROOT).as_posix())
        parent = load_json(
            "docs/S1XL_PPB1_EINMALIGER_PRIVATER_REGISTRIERTER_60_ZELLEN_LAUF_V1.json"
        )
        self.assertEqual(audit["parent_s1xl_result_digest"], canonical_digest(parent))
        paths = {
            "s1xl_result_file": "docs/S1XL_PPB1_EINMALIGER_PRIVATER_REGISTRIERTER_60_ZELLEN_LAUF_V1.json",
            "s1xl_document": "docs/S1XL_PPB1_EINMALIGER_PRIVATER_REGISTRIERTER_60_ZELLEN_LAUF.md",
            "s1xl_tests": "tests/test_ppb1_s1xl_registered_run_result_record.py",
            "s1xc_fixture_registry": "mcm_field_organism/_ppb1_s1xc_fixture_registry.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "s1xi_full_runner": "mcm_field_organism/_ppb1_s1xi_private_full_runner.py",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                audit["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_formal_s1xl_receipt_decision_is_preserved(self) -> None:
        audit = load_json(AUDIT_PATH.relative_to(ROOT).as_posix())
        source = load_json(
            "docs/S1XL_PPB1_EINMALIGER_PRIVATER_REGISTRIERTER_60_ZELLEN_LAUF_V1.json"
        )["matrix_receipt"]
        finding = audit["formal_receipt_finding"]
        for role in (
            "matrix_receipt_digest",
            "method_valid",
            "candidate_pass_cell_count",
            "technical_function_decision",
            "baseline_explanation_decision",
            "final_decision",
        ):
            self.assertEqual(source[role], finding[role])
        self.assertFalse(finding["receipt_decision_may_be_rewritten"])

    def test_fixture_literals_bind_positive_auditory_boundary(self) -> None:
        source_path = ROOT / "mcm_field_organism/_ppb1_s1xc_fixture_registry.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assignments = {
            target.id: node.value
            for node in tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
            and target.id in {"_PROBE_VALUES", "_EXPECTED_MASK"}
        }
        probes = ast.literal_eval(assignments["_PROBE_VALUES"])
        mask = ast.literal_eval(assignments["_EXPECTED_MASK"])
        self.assertEqual(0.2, probes["auditory"][2])
        self.assertTrue(mask[2])
        self.assertIn("PPB1ModalityParameters(8, 0.2, 0.1, 3, 512)", source)

    def test_observed_boundary_delta_is_positive_and_candidate_neutral(self) -> None:
        audit = load_json(AUDIT_PATH.relative_to(ROOT).as_posix())
        boundary = audit["numeric_boundary_audit"]
        self.assertEqual(0.2, boundary["threshold_literal"])
        self.assertEqual(0.2, boundary["probe_value_literal"])
        self.assertGreater(boundary["observed_distance"], boundary["threshold_literal"])
        self.assertAlmostEqual(
            boundary["observed_distance"] - boundary["threshold_literal"],
            boundary["observed_minus_threshold"],
        )
        self.assertFalse(
            boundary["prebound_expectation_is_numerically_consistent_with_implemented_metric"]
        )
        self.assertFalse(
            audit["causal_interpretation"]["candidate_specific_counterprediction_tested_by_mismatch"]
        )

    def test_candidate_and_baselines_share_metric_and_threshold_operator(self) -> None:
        candidate = (
            ROOT / "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py"
        ).read_text(encoding="utf-8")
        baseline = (
            ROOT / "mcm_field_organism/_ppb1_s1xc_fixture_registry.py"
        ).read_text(encoding="utf-8")
        for source in (candidate, baseline):
            self.assertIn("normalized_mean_l1_distance(", source)
            self.assertIn("recognized = distance <= config.match_threshold", source)

    def test_complete_baseline_reducibility_is_preserved(self) -> None:
        audit = load_json(AUDIT_PATH.relative_to(ROOT).as_posix())
        result = load_json(
            "docs/S1XL_PPB1_EINMALIGER_PRIVATER_REGISTRIERTER_60_ZELLEN_LAUF_V1.json"
        )["matrix_receipt"]["baseline_explanation_by_system"]
        reducibility = audit["baseline_reducibility"]
        for system, explained in result.items():
            self.assertEqual(explained, reducibility[system])
        self.assertTrue(
            reducibility["one_complete_simpler_baseline_explains_all_observed_candidate_outputs"]
        )
        self.assertFalse(reducibility["mcm_specific_difference_observed"])

    def test_disposition_closes_research_comparison_without_removing_engineering(self) -> None:
        disposition = load_json(AUDIT_PATH.relative_to(ROOT).as_posix())[
            "research_disposition"
        ]
        self.assertFalse(disposition["s1xl_rerun_allowed"])
        self.assertFalse(disposition["s1xl_receipt_repair_allowed"])
        self.assertTrue(disposition["ppb1_engineering_component_remains_available"])
        self.assertFalse(
            disposition["ppb1_established_as_mcm_specific_memory_mechanism"]
        )
        self.assertTrue(disposition["registered_comparison_branch_closed"])

    def test_decision_is_narrow_and_all_execution_counters_are_zero(self) -> None:
        audit = load_json(AUDIT_PATH.relative_to(ROOT).as_posix())
        self.assertEqual(16, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual(
            "PASS_BOUNDARY_EXPECTATION_INCONSISTENT_FORMAL_FAIL_PRESERVED_CANDIDATE_CAUSE_NOT_ESTABLISHED_BASELINE_REDUCIBLE",
            audit["decision"],
        )
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
