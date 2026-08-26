from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "S1ZH_LPRH1F_STATISCHER_BINDUNGSKORREKTUR_ABNAHME_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
CONTRACT = ROOT / "docs" / "S1ZI_LPRH1F_STATISCHER_RECEIPT_HELPER_UND_FIXTURE_PAYLOAD_KORREKTURVERTRAG_V1.json"
EXPECTED_CONTRACT_DIGEST = "604b8a4482634236756cbe40ea01bbb9be4db14bd0c0a53cc98e95c5319a5f6a"
BOUND_PATHS = {
    "s1zh_audit": "docs/S1ZH_LPRH1F_STATISCHER_BINDUNGSKORREKTUR_ABNAHME_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json",
    "s1zh_document": "docs/S1ZH_LPRH1F_STATISCHER_BINDUNGSKORREKTUR_ABNAHME_UND_IMPLEMENTIERUNGSPREFLIGHT.md",
    "s1zh_tests": "tests/test_lprh1f_s1zh_static_binding_correction_acceptance_and_implementation_preflight.py",
    "s1zg_contract": "docs/S1ZG_LPRH1F_STATISCHER_PRIVATER_ANWENDUNGSPREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json",
    "private_handoff_module": "mcm_field_organism/_lprh1_s1yn_private_local_handoff.py",
    "ppb1_reference_module": "mcm_field_organism/_ppb1_reference.py",
    "read_only_probe_module": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
    "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
    "private_consumer_module": "mcm_field_organism/_lprh1f_s1za_private_context_consumer.py",
    "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
    "package_root": "mcm_field_organism/__init__.py",
    "current_api": "mcm_field_organism/current_api.py",
    "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
}


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class LPRH1FS1ZIStaticReceiptHelperFixtureCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_contract_digest_and_parent_are_bound(self) -> None:
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, canonical_digest(self.contract))
        self.assertEqual(
            canonical_digest(self.audit),
            self.contract["parent_s1zh_canonical_preflight_audit_digest"],
        )
        self.assertEqual(set(BOUND_PATHS), set(self.contract["bound_file_digests"]))
        for role, relative in BOUND_PATHS.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(self.contract["bound_file_digests"][role], actual)

    def test_receipt_is_exactly_nested_and_old_id_is_superseded(self) -> None:
        schema = self.contract["derived_drive_set_schema"]
        self.assertIn(
            "derivation_receipt_LPRH1FDriveDerivationReceipt",
            schema,
        )
        self.assertNotIn("derivation_receipt_id_str", schema)
        self.assertEqual(8, len(self.contract["derivation_receipt_schema"]))
        rules = self.contract["receipt_object_link_invariants"]
        self.assertIn("NO_SEPARATE_UNLINKED_RECEIPT_ID_FIELD_ALLOWED", rules)

    def test_helper_has_finite_errors_and_four_immutable_inputs(self) -> None:
        errors = self.contract["derivation_helper_error_contract"]
        self.assertEqual(8, len(errors["precedence"]))
        self.assertEqual("D01_", errors["precedence"][0][:4])
        self.assertEqual("D08_", errors["precedence"][-1][:4])
        immutable = self.contract["derivation_input_immutability"]
        self.assertTrue(immutable["source_layer_before_equals_after"])
        self.assertTrue(immutable["target_step_before_equals_after"])
        self.assertTrue(immutable["receptor_contact_mapping_before_equals_after"])
        self.assertTrue(immutable["transient_input_mapping_before_equals_after"])

    def test_source_registry_and_all_eight_arm_sources_are_finite(self) -> None:
        registry = self.contract["finite_fixture_source_registry"]
        self.assertEqual(11, len(registry))
        handoff = self.contract["finite_handoff_sources_by_arm"]
        external = self.contract["non_handoff_sources_by_arm"]
        self.assertEqual(4, len(handoff))
        self.assertEqual(4, len(external))
        self.assertEqual(8, len(set(handoff) | set(external)))
        for source in handoff.values():
            self.assertIn(source["config_payload_id"], registry)
            self.assertIn(source["state_payload_id"], registry)
            self.assertIn(source["probe_payload_id"], registry)

    def test_every_arm_has_one_complete_next_layer_payload(self) -> None:
        sources = set(self.contract["finite_handoff_sources_by_arm"]) | set(
            self.contract["non_handoff_sources_by_arm"]
        )
        payloads = self.contract["complete_expected_next_layer_payloads_by_arm"]
        self.assertEqual(sources, set(payloads))
        for payload in payloads.values():
            self.assertEqual(
                {"layer_id", "sample_offsets", "receptor_dock_ids", "neurons"},
                set(payload),
            )
            neuron = payload["neurons"][0]
            self.assertEqual(
                {"tick", "receptor_contact", "local_samples"},
                set(neuron["perception"]),
            )
            self.assertEqual(1, neuron["perception"]["tick"])

    def test_generic_pair_relations_are_exact_in_complete_payloads(self) -> None:
        payloads = self.contract["complete_expected_next_layer_payloads_by_arm"]
        self.assertEqual(payloads["candidate.low"], payloads["generic.low"])
        self.assertEqual(payloads["candidate.high"], payloads["generic.high"])
        self.assertEqual(payloads["no-context.low"], payloads["digest-only.low"])
        self.assertEqual(payloads["no-context.high"], payloads["digest-only.high"])

    def test_three_audit_blockers_close_without_implementation(self) -> None:
        blockers = {
            item["blocker_id"] for item in self.audit["implementation_preflight_blockers"]
        }
        self.assertEqual(blockers, set(self.contract["blocker_closure"]))
        self.assertTrue(all(
            value.startswith("CLOSED_BY_")
            for value in self.contract["blocker_closure"].values()
        ))
        gate = self.contract["implementation_gate"]
        next_gate = "requires_s1zj_static_correction_acceptance_and_final_implementation_preflight"
        self.assertTrue(gate[next_gate])
        self.assertTrue(all(
            value is False for key, value in gate.items() if key != next_gate
        ))
        self.assertTrue(all(
            value == 0 for value in self.contract["execution_counters"].values()
        ))


if __name__ == "__main__":
    unittest.main()
