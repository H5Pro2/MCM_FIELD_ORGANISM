from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1ZD_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_MATERIALISIERBARKEITSAUDIT_V1.json"
S1ZC_PATH = ROOT / "docs/S1ZC_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_UND_BASELINEVERTRAG_V1.json"
LAYER_PATH = ROOT / "mcm_field_organism/mcm_neuron_layer.py"
FIXTURE_PATH = ROOT / "tests/test_lprh1f_s1za_private_layer_bound_context_consumer.py"
EXPECTED_AUDIT_DIGEST = "89d8eeaca4284209734a206a350df02c1ce42e20a20a8e8a1c46cea1547e43e6"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1ZDStaticProposalApplicationMaterializabilityAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        parent = load(S1ZC_PATH)
        encoded = json.dumps(parent, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(audit["parent_s1zc_canonical_contract_digest"], hashlib.sha256(encoded).hexdigest())
        paths = {
            "s1zc_contract": "docs/S1ZC_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_UND_BASELINEVERTRAG_V1.json",
            "s1zc_document": "docs/S1ZC_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_UND_BASELINEVERTRAG.md",
            "s1zc_tests": "tests/test_lprh1f_s1zc_static_private_proposal_application_and_baseline_contract.py",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "private_consumer_module": "mcm_field_organism/_lprh1f_s1za_private_context_consumer.py",
            "private_consumer_tests": "tests/test_lprh1f_s1za_private_layer_bound_context_consumer.py",
        }
        for role, relative in paths.items():
            self.assertEqual(audit["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_core_constructs_perception_and_drive_inside_advance_path(self) -> None:
        tree = ast.parse(LAYER_PATH.read_text(encoding="utf-8"))
        layer_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MCMNeuronLayer")
        advance = next(node for node in layer_class.body if isinstance(node, ast.FunctionDef) and node.name == "advance")
        calls = {ast.unparse(node.func) for node in ast.walk(advance) if isinstance(node, ast.Call)}
        self.assertIn("self._perception_for", calls)
        self.assertIn("advance_mcm_neuron", calls)
        standalone = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "advance_mcm_neuron")
        constructors = {ast.unparse(node.func) for node in ast.walk(standalone) if isinstance(node, ast.Call)}
        self.assertIn("MCMNeuronDrive", constructors)

    def test_no_bound_public_preapplication_drive_derivation_path_exists(self) -> None:
        tree = ast.parse(LAYER_PATH.read_text(encoding="utf-8"))
        names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and ("drive" in node.name or "perception" in node.name)
        }
        self.assertEqual({"_perception_for"}, names & {"_perception_for", "drives_for", "prepare_drives", "derive_drives"})
        blocker = load(AUDIT_PATH)["materializability_blockers"][0]
        self.assertEqual("M1_PREAPPLICATION_DRIVE_DERIVATION_PATH_UNBOUND", blocker["blocker_id"])

    def test_current_fixture_has_empty_docks_and_nonempty_transient_drive(self) -> None:
        source = FIXTURE_PATH.read_text(encoding="utf-8")
        self.assertIn("receptor_dock_ids=(),", source)
        self.assertIn("transient_receptor_input=transient", source)
        blocker = load(AUDIT_PATH)["materializability_blockers"][1]
        self.assertEqual("M2_CURRENT_SYNTHETIC_FIXTURE_CANNOT_REGENERATE_BOUND_DRIVE", blocker["blocker_id"])

    def test_two_blockers_are_implementation_blocking(self) -> None:
        blockers = load(AUDIT_PATH)["materializability_blockers"]
        self.assertEqual(2, len(blockers))
        self.assertEqual(2, len({item["blocker_id"] for item in blockers}))
        self.assertTrue(all(item["severity"] == "IMPLEMENTATION_BLOCKING" for item in blockers))
        self.assertTrue(all(item["missing_binding"] and item["effect"] for item in blockers))

    def test_unsafe_workarounds_are_explicitly_rejected(self) -> None:
        workarounds = load(AUDIT_PATH)["unsafe_workarounds"]
        self.assertEqual(5, len(workarounds))
        self.assertTrue(any("SECOND_TIME" in item for item in workarounds))
        self.assertTrue(any("DISABLE_CALLBACK_DRIVE_DIGEST_CHECK" == item for item in workarounds))
        self.assertTrue(any("MCMNeuronLayer" in item for item in workarounds))

    def test_correction_is_private_source_bound_and_core_preserving(self) -> None:
        correction = load(AUDIT_PATH)["bounded_correction_direction"]
        self.assertIn("PRIVATE_PURE", correction["correction_id"])
        self.assertIn("MUST_EQUAL", correction["equivalence_rule"])
        self.assertFalse(correction["core_change_allowed"])
        self.assertFalse(correction["public_api_change_allowed"])
        self.assertFalse(correction["second_capture_advance_allowed"])
        self.assertTrue(correction["requires_static_correction_contract"])

    def test_prior_private_component_and_generic_relation_remain_valid(self) -> None:
        findings = load(AUDIT_PATH)["preserved_findings"]
        self.assertEqual(5, len(findings))
        self.assertTrue(all(findings.values()))

    def test_decision_blocks_every_execution_and_records_two_failures(self) -> None:
        audit = load(AUDIT_PATH)
        gate = audit["gate_effect"]
        self.assertTrue(all(value is False for key, value in gate.items() if key != "requires_s1ze_static_correction_contract"))
        self.assertTrue(gate["requires_s1ze_static_correction_contract"])
        self.assertEqual(21, audit["passed_audit_role_count"])
        self.assertEqual(2, audit["failed_audit_role_count"])
        self.assertEqual("FAIL_LPRH1F_PRIVATE_PROPOSAL_APPLICATION_NOT_MATERIALIZABLE_PREAPPLICATION_DRIVE_PATH_AND_FIXTURE_UNBOUND", audit["decision"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
