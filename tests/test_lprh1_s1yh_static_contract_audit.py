from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    ROOT
    / "docs/S1YH_LPRH1_STATISCHER_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json"
)
EXPECTED_AUDIT_DIGEST = "5ccde1140bfdf29594bd8596101c3cab11a3349a2a430af3169980b29f944081"


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


class LPRH1S1YHStaticContractAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "85c783b34b812df5d3957552b6fa00c4502b5c0421558795d17956f60d4d826e",
            audit["parent_s1yg_canonical_contract_digest"],
        )
        paths = {
            "s1yg_contract": "docs/S1YG_LPRH1_STATISCHER_FUNKTIONS_PROVENIENZ_KAUSALITAETS_UND_FALSIFIKATIONSVERTRAG_V1.json",
            "s1yg_document": "docs/S1YG_LPRH1_STATISCHER_FUNKTIONS_PROVENIENZ_KAUSALITAETS_UND_FALSIFIKATIONSVERTRAG.md",
            "s1yg_tests": "tests/test_lprh1_s1yg_static_handoff_contract.py",
            "receptor_time_model": "mcm_field_organism/receptor_time_model.py",
            "field_step_time": "mcm_field_organism/field_step_time.py",
            "receptor_contract": "mcm_field_organism/receptor_contract.py",
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

    def test_five_dimensions_pass_and_materialization_fails(self) -> None:
        dimensions = load_audit()["audit_dimensions"]
        self.assertEqual(5, sum(value is True for value in dimensions.values()))
        self.assertFalse(dimensions["unambiguous_materialization_complete"])

    def test_noncircularity_direction_is_complete(self) -> None:
        result = load_audit()["noncircularity_result"]
        self.assertTrue(result["finding_precedes_extraction"])
        self.assertTrue(result["bank_state_precedes_context"])
        self.assertTrue(result["context_does_not_change_recognition"])
        self.assertTrue(result["future_field_output_does_not_define_handoff_content"])
        self.assertEqual("PASS_NONCIRCULAR_READ_ONLY_HANDOFF_DIRECTION", result["decision"])

    def test_eighteen_passed_roles_are_bound(self) -> None:
        audit = load_audit()
        self.assertEqual(18, audit["passed_role_count"])
        self.assertEqual(18, len(audit["passed_roles"]))

    def test_exactly_seven_materialization_blockers_are_bound(self) -> None:
        blockers = load_audit()["materialization_blockers"]
        self.assertEqual(7, len(blockers))
        self.assertEqual(
            {f"M{index}_" for index in range(1, 8)},
            {item["blocker_id"][:3] for item in blockers},
        )
        self.assertEqual(7, load_audit()["failed_role_count"])

    def test_timed_probe_blocker_uses_existing_atomic_type(self) -> None:
        source = (ROOT / "mcm_field_organism/receptor_time_model.py").read_text(encoding="utf-8")
        self.assertIn("class OrganismTimedReceptorFrame", source)
        self.assertIn("frame: ReceptorContactFrame", source)
        self.assertIn("field_time: CommonFieldTime", source)
        blocker = load_audit()["materialization_blockers"][0]
        self.assertIn("ONE_EXACT_ORGANISM_TIMED_RECEPTOR_FRAME", blocker["required_correction"])

    def test_digest_schema_mapping_and_identity_gaps_are_explicit(self) -> None:
        corrections = " ".join(
            item["required_correction"] for item in load_audit()["materialization_blockers"]
        )
        for role in (
            "CANONICAL_PAYLOADS",
            "EXACT_TYPES",
            "CARRIER_ORDER",
            "HANDOFF_AND_RECEIPT_ID_DERIVATION",
        ):
            self.assertIn(role, corrections)

    def test_envelope_and_budget_gaps_are_explicit(self) -> None:
        blockers = {item["blocker_id"]: item["required_correction"] for item in load_audit()["materialization_blockers"]}
        self.assertIn("ZERO_OR_ONE_CONTEXT_SET", blockers["M6_DUAL_ENVELOPE_CARDINALITY_UNBOUND"])
        self.assertIn("EXACTLY_ONE_EXTRACTION_ATTEMPT", blockers["M7_ERROR_AND_CALL_BUDGET_UNBOUND"])
        self.assertIn("ZERO_FIELD_CALLS", blockers["M7_ERROR_AND_CALL_BUDGET_UNBOUND"])

    def test_implementation_and_field_permissions_are_false(self) -> None:
        audit = load_audit()
        self.assertFalse(audit["implementation_permission"])
        self.assertFalse(audit["field_permission"])
        self.assertEqual(
            "BLOCKED_SEVEN_STATIC_BINDINGS_REQUIRED_BEFORE_IMPLEMENTATION",
            audit["materialization_decision"],
        )

    def test_public_surfaces_remain_without_lprh1(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yh", source)
            self.assertNotIn("lprh", source)

    def test_decision_is_blocked_narrow_and_nonexecuting(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "BLOCKED_LPRH1_STATIC_MATERIALIZATION_CORRECTION_REQUIRED_NO_IMPLEMENTATION_OR_EXECUTION",
            audit["decision"],
        )
        self.assertIn("NO_IMPLEMENTABLE_HANDOFF", audit["claim_boundary"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
