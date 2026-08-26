from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FINDING = ROOT / "docs/S1ZM_LPRH1F_PRIVATE_IMPLEMENTIERUNG_UND_SYNTHETISCHER_ANWENDUNGSBEFUND_V1.json"
AUDIT = ROOT / "docs/S1ZN_LPRH1F_STATISCHER_PRIVATER_IMPLEMENTIERUNGS_RECEIPT_GRENZ_UND_ERGEBNISABSCHLUSSAUDIT_V1.json"
MODULE = ROOT / "mcm_field_organism/_lprh1f_s1zm_private_proposal_application.py"
EXPECTED_AUDIT_DIGEST = "7c1fb1f7718249335f5edfe36b035f1dc64ec92d90e8fd2f29db5592e6c0a0ff"
BOUND_PATHS = {
    "s1zm_finding": "docs/S1ZM_LPRH1F_PRIVATE_IMPLEMENTIERUNG_UND_SYNTHETISCHER_ANWENDUNGSBEFUND_V1.json",
    "s1zm_document": "docs/S1ZM_LPRH1F_PRIVATE_IMPLEMENTIERUNG_UND_SYNTHETISCHER_ANWENDUNGSBEFUND.md",
    "s1zm_private_module": "mcm_field_organism/_lprh1f_s1zm_private_proposal_application.py",
    "s1zm_private_tests": "tests/test_lprh1f_s1zm_private_proposal_application.py",
    "s1zl_tests_after_authorized_implementation": "tests/test_lprh1f_s1zl_static_source_prestate_closure_and_final_implementation_preflight.py",
    "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
    "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
    "package_root": "mcm_field_organism/__init__.py",
    "current_api": "mcm_field_organism/current_api.py",
    "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
}


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class LPRH1FS1ZNStaticPrivateImplementationClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.finding = json.loads(FINDING.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.source = MODULE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_audit_digest_parent_and_all_bound_files(self) -> None:
        self.assertEqual(EXPECTED_AUDIT_DIGEST, canonical_digest(self.audit))
        self.assertEqual(
            canonical_digest(self.finding),
            self.audit["parent_s1zm_canonical_implementation_finding_digest"],
        )
        self.assertEqual(set(BOUND_PATHS), set(self.audit["bound_file_digests"]))
        for role, relative in BOUND_PATHS.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(self.audit["bound_file_digests"][role], actual)

    def test_exact_private_types_and_authorized_functions_exist_statically(self) -> None:
        class_names = {
            node.name for node in self.tree.body if isinstance(node, ast.ClassDef)
        }
        function_names = {
            node.name for node in self.tree.body if isinstance(node, ast.FunctionDef)
        }
        self.assertEqual(
            {
                "LPRH1FPrivateApplicationError",
                "LPRH1FDriveDerivationReceipt",
                "LPRH1FDerivedDriveSet",
                "LPRH1FPrivateLayerApplicationReceipt",
                "LPRH1FPrivateAppliedLayerResult",
            },
            class_names,
        )
        self.assertTrue(set(self.audit["static_implementation_finding"]["authorized_functions"]).issubset(function_names))

    def test_error_inventories_receipts_and_layer_sources_are_present(self) -> None:
        assignments = {
            target.id
            for node in self.tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        self.assertEqual(8, len({name for name in assignments if name.startswith("LPRH1F_DERIVATION_")}))
        self.assertEqual(11, len({name for name in assignments if name.startswith("LPRH1F_APPLICATION_")}))
        self.assertIn("derivation_receipt: LPRH1FDriveDerivationReceipt", self.source)
        self.assertIn("source_layer._perception_for", self.source)
        self.assertIn("next_layer = source_layer.advance", self.source)

    def test_public_surfaces_and_core_remain_separate(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1zm", source)
            self.assertNotIn("lprh1fprivateappliedlayerresult", source)
        self.assertTrue(all(self.audit["boundary_finding"].values()))

    def test_bound_result_confirms_exact_generic_reduction(self) -> None:
        result = self.audit["synthetic_result_acceptance"]
        self.assertTrue(result["all_eight_expected_next_layers_matched"])
        self.assertTrue(result["candidate_low_equals_generic_low"])
        self.assertTrue(result["candidate_high_equals_generic_high"])
        self.assertTrue(result["generic_reduction_confirmed"])
        self.assertFalse(result["independent_lprh1f_field_mechanism_supported"])
        self.assertEqual(
            self.finding["actual_next_layer_digests"]["candidate.low"],
            self.finding["actual_next_layer_digests"]["generic.low"],
        )

    def test_research_branch_closes_while_private_reference_is_retained(self) -> None:
        disposition = self.audit["research_disposition"]
        self.assertEqual(
            "TERMINALLY_CLOSED_BY_EXACT_GENERIC_REDUCTION",
            disposition["lprh1f_as_independent_candidate"],
        )
        self.assertEqual(
            "RETAIN_AS_ENGINEERING_REFERENCE_AND_REGRESSION_BASELINE",
            disposition["private_implementation"],
        )
        self.assertFalse(disposition["further_lprh1f_equation_or_candidate_variant_allowed"])
        self.assertFalse(disposition["new_research_claim_supported"])

    def test_static_pass_has_zero_reexecution(self) -> None:
        self.assertEqual(49, self.audit["passed_audit_role_count"])
        self.assertEqual(0, self.audit["failed_audit_role_count"])
        self.assertEqual(
            "PASS_LPRH1F_PRIVATE_IMPLEMENTATION_CLOSED_GENERIC_REDUCTION_CONFIRMED_CANDIDATE_TERMINATED",
            self.audit["decision"],
        )
        self.assertTrue(all(value == 0 for value in self.audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
