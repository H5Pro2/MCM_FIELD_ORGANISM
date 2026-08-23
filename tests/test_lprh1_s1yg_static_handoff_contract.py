from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "docs/S1YG_LPRH1_STATISCHER_FUNKTIONS_PROVENIENZ_KAUSALITAETS_UND_FALSIFIKATIONSVERTRAG_V1.json"
)
EXPECTED_CONTRACT_DIGEST = "85c783b34b812df5d3957552b6fa00c4502b5c0421558795d17956f60d4d826e"


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class LPRH1S1YGStaticHandoffContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_contract(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load_contract()
        self.assertEqual(
            "0b6213f031808b3e31b9dbff9e2ca86f5a6cd2c42b3fd43d4f44270cfa0b258b",
            contract["parent_s1yf_canonical_audit_digest"],
        )
        paths = {
            "s1yf_audit": "docs/S1YF_PPB1_STATISCHE_ENGINEERINGKONSOLIDIERUNG_UND_FELDHANDOFF_FRAGENAUSWAHL_V1.json",
            "s1yf_document": "docs/S1YF_PPB1_STATISCHE_ENGINEERINGKONSOLIDIERUNG_UND_FELDHANDOFF_FRAGENAUSWAHL.md",
            "s1yf_tests": "tests/test_ppb1_s1yf_static_field_handoff_question_selection.py",
            "field_step_time": "mcm_field_organism/field_step_time.py",
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
                contract["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_exactly_one_function_and_seven_inputs_are_bound(self) -> None:
        function = load_contract()["single_function"]
        self.assertEqual(1, function["function_count"])
        self.assertEqual("LPRH-1_LOCAL_PROTOTYPE_READ_ONLY_HANDOFF", function["function_id"])
        self.assertEqual(7, len(function["input_roles"]))
        self.assertFalse(function["field_consumption"])

    def test_positive_and_negative_outputs_are_separate(self) -> None:
        function = load_contract()["single_function"]
        self.assertIn("LOCAL_PROTOTYPE_CONTEXT", function["positive_output"])
        self.assertIn("NO_CONTEXT_RECEIPT", function["negative_output"])
        self.assertIn("WITHOUT_CONTEXT_VALUES", function["negative_output"])

    def test_eight_extraction_preconditions_and_exact_copy_are_bound(self) -> None:
        extraction = load_contract()["read_only_extraction_contract"]
        self.assertEqual(8, len(extraction["positive_preconditions"]))
        self.assertIn("WITHOUT_TRANSFORMATION_REORDERING_SCALING_OR_FUSION", extraction["content_rule"])
        self.assertIn("REMAIN_UNCHANGED", extraction["immutability_rule"])

    def test_current_sources_can_bind_slot_finding_and_original_frame(self) -> None:
        reference = (ROOT / "mcm_field_organism/_ppb1_reference.py").read_text(encoding="utf-8")
        probe = (ROOT / "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py").read_text(encoding="utf-8")
        for role in ("prototype_values", "support_count", "slot_id", "carrier_ids", "geometry_id"):
            self.assertIn(role, reference)
        for role in ("recognized", "selected_slot_id", "selected_prototype_digest", "probe_input_digest"):
            self.assertIn(role, probe)

    def test_context_has_nine_roles_and_is_not_receptor_or_persistent(self) -> None:
        anatomy = load_contract()["private_context_anatomy"]
        self.assertEqual(9, len(anatomy["required_roles"]))
        self.assertEqual("RECEPTOR_CONTACT_FRAME", anatomy["must_not_be_type"])
        self.assertFalse(anatomy["persistent_snapshot_member"])
        self.assertFalse(anatomy["public_api_member"])
        self.assertFalse(anatomy["production_member"])

    def test_causal_time_is_same_clock_immediate_and_single_use(self) -> None:
        causal = load_contract()["causal_time_contract"]
        self.assertIn("SHARE_ONE_CLOCK_ID", causal["clock_rule"])
        self.assertIn("START_TICK_EQUALS", causal["adjacency_rule"])
        self.assertIn("EXACTLY_THE_BOUND_TARGET_FIELD_STEP", causal["single_proposal_rule"])
        self.assertFalse(causal["future_or_stale_context_allowed"])

    def test_dual_input_boundary_preserves_receptor_and_blocks_coupling(self) -> None:
        boundary = load_contract()["dual_input_boundary_contract"]
        self.assertEqual("EXISTING_TRANSIENT_NEURON_INPUT_SET_UNCHANGED", boundary["receptor_role"])
        self.assertTrue(boundary["receptor_digest_before_equals_after"])
        self.assertFalse(boundary["context_may_enter_receptor_contact_collection"])
        self.assertFalse(boundary["context_may_enter_field_snapshot"])
        self.assertFalse(boundary["field_coupling_rule_selected"])

    def test_five_future_controls_and_stop_conditions_are_bound(self) -> None:
        contract = load_contract()
        self.assertEqual(5, len(contract["future_falsification_controls"]))
        self.assertEqual(5, len(contract["stop_conditions"]))
        self.assertIn("CURRENT_INPUT_COPY_CONTEXT", contract["future_falsification_controls"])

    def test_all_four_s1yf_blockers_are_contractually_closed(self) -> None:
        self.assertEqual(
            {
                "B1_PROTOTYPE_CONTENT_NOT_EXPOSED",
                "B2_NO_SEPARATE_TRANSIENT_CONTEXT_TYPE",
                "B3_NO_DUAL_INPUT_FIELD_BOUNDARY",
                "B4_FRESHNESS_AND_CAUSAL_TIME_UNBOUND",
            },
            set(load_contract()["blocker_disposition"]),
        )
        self.assertIn(
            "FIELD_CONSUMPTION_REMAINS_BLOCKED",
            load_contract()["blocker_disposition"]["B3_NO_DUAL_INPUT_FIELD_BOUNDARY"],
        )

    def test_public_surfaces_remain_without_lprh1(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yg", source)
            self.assertNotIn("lprh", source)

    def test_decision_is_complete_narrow_and_nonexecuting(self) -> None:
        contract = load_contract()
        self.assertEqual(25, contract["passed_role_count"])
        self.assertEqual(0, contract["failed_role_count"])
        self.assertEqual(
            "PASS_LPRH1_STATIC_HANDOFF_CONTRACT_FOUR_BLOCKERS_CLOSED_FIELD_COUPLING_REMAINS_BLOCKED",
            contract["decision"],
        )
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
