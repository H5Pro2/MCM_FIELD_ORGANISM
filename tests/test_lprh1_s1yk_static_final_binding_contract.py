from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1YK_LPRH1_STATISCHER_FINALER_IMPLEMENTIERUNGSBINDUNGSKORREKTURVERTRAG_V1.json"
EXPECTED_CONTRACT_DIGEST = "3b914f2b9d90470223225b070ae1b8673d9665791b697d125871bc30a84d04aa"


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class LPRH1S1YKStaticFinalBindingContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load_contract(), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load_contract()
        self.assertEqual("bffc570218ba0189f3cd0982871a6878cbc76df17dc6688c5b0c9498cd3445a8", contract["parent_s1yj_canonical_audit_digest"])
        paths = {
            "s1yj_audit": "docs/S1YJ_LPRH1_STATISCHER_KORREKTURABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHTAUDIT_V1.json",
            "s1yj_document": "docs/S1YJ_LPRH1_STATISCHER_KORREKTURABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHTAUDIT.md",
            "s1yj_tests": "tests/test_lprh1_s1yj_static_implementation_preflight_audit.py",
            "s1yi_contract": "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json",
            "receptor_time_model": "mcm_field_organism/receptor_time_model.py",
            "field_step_time": "mcm_field_organism/field_step_time.py",
            "receptor_contract": "mcm_field_organism/receptor_contract.py",
            "transient_neuron_input": "mcm_field_organism/transient_neuron_input.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(contract["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_four_output_payloads_and_own_digest_exclusions_are_bound(self) -> None:
        payloads = load_contract()["canonical_output_payloads"]
        self.assertEqual(4, len([key for key in payloads if key.endswith("_payload_keys")]))
        self.assertEqual({"context_digest", "receipt_digest", "envelope_digest"}, set(payloads["own_digest_fields_excluded"]))

    def test_receipt_namespaces_are_distinct(self) -> None:
        namespaces = load_contract()["receipt_identity_namespaces"]
        no_context = namespaces["no_context_receipt_id_payload"]["keys_in_role_order"]
        handoff = namespaces["handoff_receipt_id_payload"]["keys_in_role_order"]
        self.assertIn("receipt_kind_literal_NO_CONTEXT_SOURCE", no_context)
        self.assertIn("receipt_kind_literal_HANDOFF_RESULT", handoff)
        self.assertTrue(namespaces["ids_must_differ_for_negative_result"])

    def test_eight_source_digests_have_exact_order(self) -> None:
        self.assertEqual(
            ["bank_config_digest", "bank_state_digest", "finding_digest", "probe_input_digest", "timed_probe_digest", "target_step_digest", "shared_dock_digest", "receptor_input_digest"],
            load_contract()["source_object_digest_order"],
        )

    def test_six_type_invariant_families_are_nonempty(self) -> None:
        invariants = load_contract()["type_invariants"]
        self.assertEqual(6, len(invariants))
        self.assertTrue(all(items for items in invariants.values()))
        self.assertIn("NO_PARTIAL_OR_ALTERNATIVE_OUTPUT_MEMBER_EXISTS", invariants["LPRH1HandoffResult"])

    def test_eight_error_codes_map_in_exact_precedence(self) -> None:
        dispatch = load_contract()["error_dispatch_in_precedence_order"]
        self.assertEqual(list(range(1, 9)), [item["stage"] for item in dispatch])
        self.assertEqual(8, len({item["code"] for item in dispatch}))
        self.assertEqual("LPRH1_INVALID_INPUT", dispatch[0]["code"])
        self.assertEqual("LPRH1_FIELD_EXECUTION_BLOCKED", dispatch[-1]["code"])

    def test_thirteen_commit_stages_end_in_one_atomic_return(self) -> None:
        order = load_contract()["atomic_commit_order"]
        self.assertEqual(13, len(order))
        self.assertIn("REJECT_DUPLICATE", order[5])
        self.assertIn("ONLY_OBSERVABLE_COMMIT", order[-1])

    def test_failure_has_no_output_ledger_update_or_retry(self) -> None:
        failure = load_contract()["failure_atomicity"]
        self.assertEqual(0, failure["observable_intermediate_output_count"])
        self.assertFalse(failure["ledger_update_before_final_return"])
        self.assertFalse(failure["error_result_members_returned"])
        self.assertEqual(0, failure["retry_count"])

    def test_all_six_s1yj_blockers_are_closed(self) -> None:
        closure = load_contract()["blocker_closure"]
        self.assertEqual({f"P{index}_" for index in range(1, 7)}, {key[:3] for key in closure})
        self.assertTrue(all(value.startswith("CLOSED_BY_") for value in closure.values()))

    def test_public_surfaces_remain_without_lprh1(self) -> None:
        for relative in ("mcm_field_organism/__init__.py", "mcm_field_organism/current_api.py", "mcm_field_organism/root_lazy_exports.py"):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yk", source)
            self.assertNotIn("lprh", source)

    def test_decision_is_complete_narrow_and_nonexecuting(self) -> None:
        contract = load_contract()
        self.assertEqual(25, contract["passed_role_count"])
        self.assertEqual(0, contract["failed_role_count"])
        self.assertEqual("PASS_LPRH1_SIX_FINAL_IMPLEMENTATION_BINDINGS_CLOSED_NO_IMPLEMENTATION_OR_EXECUTION", contract["decision"])
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
