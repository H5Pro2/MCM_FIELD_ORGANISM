from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "S1ZJ_LPRH1F_STATISCHER_RECEIPT_HELPER_FIXTURE_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
CONTRACT = ROOT / "docs" / "S1ZK_LPRH1F_STATISCHER_QUELLLAYER_VORZUSTANDS_UND_DRIVE_PAYLOAD_VERTRAG_V1.json"
EXPECTED_CONTRACT_DIGEST = "9da7bde86925de356fa51b91b1c8ab08f9b7408730cef438b0bfbb89e1ed26fb"


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


class LPRH1FS1ZKStaticSourceLayerPrestateDrivePayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_contract_digest_parent_and_immediate_source_files(self) -> None:
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, canonical_digest(self.contract))
        self.assertEqual(
            canonical_digest(self.audit),
            self.contract["parent_s1zj_canonical_preflight_audit_digest"],
        )
        for role, path in (
            ("s1zj_audit", AUDIT),
            ("s1zj_document", ROOT / "docs/S1ZJ_LPRH1F_STATISCHER_RECEIPT_HELPER_FIXTURE_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT.md"),
            ("s1zj_tests", ROOT / "tests/test_lprh1f_s1zj_static_receipt_helper_fixture_closure_and_implementation_preflight.py"),
        ):
            self.assertEqual(
                self.contract["bound_file_digests"][role],
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )

    def test_source_neuron_layer_and_field_prestate_digests_are_literal(self) -> None:
        neuron = self.contract["source_neuron_canonical_payload"]
        layer = self.contract["source_layer_canonical_payload"]
        prestate = self.contract["field_prestate_canonical_payload"]
        self.assertEqual(self.contract["source_neuron_digest"], canonical_digest(neuron))
        self.assertEqual(self.contract["source_layer_digest"], canonical_digest(layer))
        self.assertEqual(self.contract["field_prestate_digest"], canonical_digest(prestate))
        self.assertEqual(neuron, layer["neurons"][0])
        self.assertEqual(self.contract["source_neuron_digest"], prestate["ordered_previous_neuron_digests"][0])

    def test_source_perception_is_complete_tick_zero_payload(self) -> None:
        perception = self.contract["source_neuron_canonical_payload"]["perception"]
        self.assertEqual(
            {"tick": 0, "receptor_contact": None, "local_samples": []},
            perception,
        )
        self.assertEqual([0], self.contract["source_neuron_canonical_payload"]["position"])

    def test_all_input_and_bundle_digests_recompute_exactly(self) -> None:
        payloads = self.contract["drive_input_payloads"]
        digests = self.contract["drive_input_digests"]
        transient = payloads["transient_input"]
        transient_mapping = [["neuron.0", transient]]
        self.assertEqual(digests["target_step_digest"], canonical_digest(payloads["target_step"]))
        self.assertEqual(digests["receptor_contact_mapping_digest"], canonical_digest(payloads["receptor_contact_mapping"]))
        self.assertEqual(digests["transient_input_digest"], canonical_digest(transient))
        self.assertEqual(digests["transient_input_mapping_digest"], canonical_digest(transient_mapping))
        self.assertEqual(digests["receptor_input_bundle_digest"], canonical_digest(self.contract["receptor_input_bundle_canonical_payload"]))

    def test_expected_drive_payload_and_digest_are_complete(self) -> None:
        drive = self.contract["expected_single_derived_drive_canonical_payload"]
        self.assertEqual(
            self.contract["expected_single_derived_drive_digest"],
            canonical_digest(drive),
        )
        self.assertEqual(
            self.contract["source_neuron_digest"],
            drive["previous_neuron_digest"],
        )
        self.assertEqual(
            self.contract["expected_derived_perception_canonical_payload"],
            drive["perception_canonical_payload"],
        )

    def test_one_s1zj_blocker_closes_but_implementation_stays_blocked(self) -> None:
        blockers = {
            item["blocker_id"] for item in self.audit["implementation_preflight_blockers"]
        }
        self.assertEqual(blockers, set(self.contract["blocker_closure"]))
        gate = self.contract["implementation_gate"]
        next_gate = "requires_s1zl_static_source_prestate_closure_and_final_implementation_preflight"
        self.assertTrue(gate[next_gate])
        self.assertTrue(all(
            value is False for key, value in gate.items() if key != next_gate
        ))
        self.assertTrue(all(value == 0 for value in self.contract["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
