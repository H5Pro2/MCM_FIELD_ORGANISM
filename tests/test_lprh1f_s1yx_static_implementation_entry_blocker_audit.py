from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1YX_LPRH1F_STATISCHER_IMPLEMENTIERUNGSEINGANGS_BLOCKERAUDIT_V1.json"
S1YV_PATH = ROOT / "docs/S1YV_LPRH1F_STATISCHER_FINALER_PREFLIGHT_KORREKTURVERTRAG_V1.json"
S1YT_PATH = ROOT / "docs/S1YT_LPRH1F_STATISCHER_PREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json"
EXPECTED_AUDIT_DIGEST = "d446adbfd8bdca365e786c0f21f6852f77d9f9da8c1da0d91cb476390056b96a"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def class_fields(relative: str, class_name: str) -> set[str]:
    tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
    node = next(item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == class_name)
    return {
        target.id
        for item in node.body
        if isinstance(item, ast.AnnAssign) and isinstance((target := item.target), ast.Name)
    }


class LPRH1FS1YXStaticImplementationEntryBlockerAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_bound_sources_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        paths = {
            "s1yv_contract": "docs/S1YV_LPRH1F_STATISCHER_FINALER_PREFLIGHT_KORREKTURVERTRAG_V1.json",
            "s1yt_contract": "docs/S1YT_LPRH1F_STATISCHER_PREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json",
            "mcm_neuron": "mcm_field_organism/mcm_neuron.py",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
        }
        for role, relative in paths.items():
            self.assertEqual(audit["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_required_payload_and_signature_match_parent_contracts(self) -> None:
        audit = load(AUDIT_PATH)
        s1yv = load(S1YV_PATH)
        s1yt = load(S1YT_PATH)
        self.assertEqual(s1yv["authoritative_field_prestate_and_drive_order"]["field_prestate_canonical_payload"], audit["required_field_prestate_payload"])
        prepare = next(item for item in s1yt["future_private_functions"] if item["function_id"] == "prepare_lprh1f_base_drive_set")
        self.assertEqual(prepare["input_roles_in_order"], audit["authorized_prepare_signature"])

    def test_layer_id_is_absent_from_drive_and_neuron_but_present_on_layer(self) -> None:
        self.assertNotIn("layer_id", class_fields("mcm_field_organism/mcm_neuron.py", "MCMNeuron"))
        self.assertNotIn("layer_id", class_fields("mcm_field_organism/mcm_neuron_layer.py", "MCMNeuronDrive"))
        self.assertIn("layer_id", class_fields("mcm_field_organism/mcm_neuron_layer.py", "MCMNeuronLayer"))

    def test_exactly_one_required_role_is_not_derivable(self) -> None:
        audit = load(AUDIT_PATH)
        required = set(audit["required_field_prestate_payload"])
        derivable = set(audit["derivable_from_ordered_drives"])
        self.assertEqual({"layer_id"}, required - derivable)
        self.assertEqual(["layer_id"], audit["not_derivable_from_ordered_drives"])

    def test_blocker_rejects_unsafe_workarounds(self) -> None:
        blocker = load(AUDIT_PATH)["blocker"]
        self.assertEqual("IMPLEMENTATION_BLOCKING", blocker["severity"])
        self.assertEqual(4, len(blocker["unsafe_workarounds"]))
        self.assertIn("CANNOT_SATISFY", blocker["effect"])

    def test_recommended_correction_preserves_layer_provenance(self) -> None:
        options = load(AUDIT_PATH)["correction_options"]
        recommended = [item for item in options if item["recommended"]]
        self.assertEqual(1, len(recommended))
        self.assertEqual("ADD_SOURCE_LAYER_OBJECT", recommended[0]["option_id"])
        self.assertEqual("STRONG", recommended[0]["provenance_strength"])

    def test_implementation_is_suspended_and_module_absent(self) -> None:
        gate = load(AUDIT_PATH)["gate_effect"]
        self.assertTrue(gate["s1yw_private_implementation_authorization_suspended"])
        self.assertFalse(gate["consumer_module_created"])
        self.assertFalse((ROOT / "mcm_field_organism/_lprh1f_s1yx_private_context_consumer.py").exists())
        self.assertTrue(gate["requires_explicit_static_correction_contract"])

    def test_decision_is_one_failure_and_nonexecuting(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual(16, audit["passed_audit_role_count"])
        self.assertEqual(1, audit["failed_audit_role_count"])
        self.assertEqual("FAIL_LPRH1F_IMPLEMENTATION_BLOCKED_LAYER_ID_SOURCE_UNBOUND", audit["decision"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
