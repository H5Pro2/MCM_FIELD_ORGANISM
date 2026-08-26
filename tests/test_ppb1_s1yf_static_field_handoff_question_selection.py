from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    ROOT
    / "docs/S1YF_PPB1_STATISCHE_ENGINEERINGKONSOLIDIERUNG_UND_FELDHANDOFF_FRAGENAUSWAHL_V1.json"
)
EXPECTED_AUDIT_DIGEST = "0b6213f031808b3e31b9dbff9e2ca86f5a6cd2c42b3fd43d4f44270cfa0b258b"


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


class PPB1S1YFStaticFieldHandoffQuestionSelectionTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "24018d0a83d65edbae36c0f1fe4a7fd0b955a9ab6fe95171b565aaa8d64c2908",
            audit["parent_s1ye_canonical_audit_digest"],
        )
        paths = {
            "s1ye_audit": "docs/S1YE_PPB1_STATISCHER_NICHTDUPLIZIERUNGS_INFORMATIONS_UND_AEQUIVALENZAUDIT_V1.json",
            "s1ye_document": "docs/S1YE_PPB1_STATISCHER_NICHTDUPLIZIERUNGS_INFORMATIONS_UND_AEQUIVALENZAUDIT.md",
            "s1ye_tests": "tests/test_ppb1_s1ye_static_nonduplication_equivalence_audit.py",
            "active_common_field_architecture": "docs/architektur/024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md",
            "receptor_contract": "mcm_field_organism/receptor_contract.py",
            "receptor_proposal_handoff": "mcm_field_organism/receptor_proposal_handoff.py",
            "transient_dock_trajectory": "mcm_field_organism/transient_dock_trajectory.py",
            "transient_neuron_input": "mcm_field_organism/transient_neuron_input.py",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                audit["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_engineering_status_separates_available_and_absent_roles(self) -> None:
        status = load_audit()["consolidated_ppb1_status"]
        self.assertEqual(4, len(status["available_roles"]))
        self.assertEqual(4, len(status["absent_roles"]))
        self.assertIn("FIELD_HANDOFF_OR_FIELD_FEEDBACK", status["absent_roles"])

    def test_active_field_chain_has_five_ordered_stages(self) -> None:
        self.assertEqual(
            [
                "REDUCED_RECEPTOR_CONTACT_FRAME",
                "LOSSLESS_RECEPTOR_PROPOSAL_HANDOFF",
                "TRANSIENT_DOCK_TRAJECTORY",
                "LOCAL_TRANSIENT_NEURON_INPUT",
                "SHARED_MCM_FIELD_STEP",
            ],
            load_audit()["active_field_boundary"]["input_chain"],
        )

    def test_active_sources_bind_lossless_transient_local_receptor_roles(self) -> None:
        proposal = (ROOT / "mcm_field_organism/receptor_proposal_handoff.py").read_text(encoding="utf-8")
        trajectory = (ROOT / "mcm_field_organism/transient_dock_trajectory.py").read_text(encoding="utf-8")
        local = (ROOT / "mcm_field_organism/transient_neuron_input.py").read_text(encoding="utf-8")
        self.assertIn("Lossless handoff of receptor completion groups", proposal)
        self.assertIn("not part of persistent field state", trajectory)
        self.assertIn("Local transient neuron inputs", local)
        self.assertIn("TransientLocalReceptorContact", local)

    def test_memory_finding_must_not_be_relabelled_as_receptor_contact(self) -> None:
        boundary = load_audit()["active_field_boundary"]
        self.assertTrue(boundary["receptor_origin_must_remain_lossless"])
        self.assertTrue(boundary["external_memory_hit_must_not_be_relabeled_as_receptor_contact"])
        self.assertFalse(boundary["field_snapshot_change_authorized"])

    def test_exactly_one_local_handoff_question_is_selected(self) -> None:
        selected = load_audit()["single_selected_question"]
        self.assertEqual(1, selected["selected_question_count"])
        self.assertEqual("LPRH-1_LOCAL_PROTOTYPE_READ_ONLY_HANDOFF", selected["question_id"])
        self.assertIn("SEPARATELY_TYPED_TRANSIENT_LOCAL_CONTEXT", selected["question"])
        self.assertIn("WITHOUT_ALTERING_OR_RELABELING", selected["question"])

    def test_five_provenance_roles_and_future_control_are_bound(self) -> None:
        selected = load_audit()["single_selected_question"]
        self.assertEqual(5, len(selected["mandatory_provenance_roles"]))
        self.assertIn("IDENTICAL_FIELD_PRESTATE", selected["mandatory_future_control"])
        self.assertIn("LPRH1_ON_VERSUS_OFF", selected["mandatory_future_control"])

    def test_current_probe_exposes_digest_but_not_prototype_values(self) -> None:
        source = (ROOT / "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py").read_text(encoding="utf-8")
        finding_start = source.index("class S1WUReadOnlyPerceptualFinding")
        probe_start = source.index("def probe_s1wu_perceptual_state")
        finding = source[finding_start:probe_start]
        self.assertIn("selected_prototype_digest", finding)
        self.assertNotIn("prototype_values:", finding)

    def test_exactly_four_static_blockers_are_explicit(self) -> None:
        blockers = load_audit()["static_blockers"]
        self.assertEqual(
            {
                "B1_PROTOTYPE_CONTENT_NOT_EXPOSED",
                "B2_NO_SEPARATE_TRANSIENT_CONTEXT_TYPE",
                "B3_NO_DUAL_INPUT_FIELD_BOUNDARY",
                "B4_FRESHNESS_AND_CAUSAL_TIME_UNBOUND",
            },
            {item["blocker_id"] for item in blockers},
        )

    def test_six_fail_closed_rules_are_bound(self) -> None:
        rules = load_audit()["fail_closed_rules"]
        self.assertEqual(6, len(rules))
        self.assertIn("NO_RECEPTOR_FRAME_SYNTHESIS_OR_RELABELING", rules)
        self.assertIn("NO_FIELD_EXECUTION_BEFORE_ALL_FOUR_BLOCKERS_ARE_CONTRACTUALLY_CLOSED", rules)

    def test_public_surfaces_remain_without_lprh1(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yf", source)
            self.assertNotIn("lprh", source)

    def test_decision_is_complete_narrow_and_nonexecuting(self) -> None:
        audit = load_audit()
        self.assertEqual(25, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual(
            "PASS_SELECT_LPRH1_AS_SINGLE_CONTROLLED_LOCAL_FIELD_HANDOFF_QUESTION_FOUR_BLOCKERS_OPEN",
            audit["decision"],
        )
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
