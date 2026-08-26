from __future__ import annotations

from dataclasses import fields
import hashlib
import json
import unittest

from mcm_field_organism import current_api


class ActiveFieldStateContractTests(unittest.TestCase):
    def test_contract_is_json_safe_and_derived_from_runtime_contracts(self) -> None:
        contract = current_api.active_field_state_contract()
        decoded = json.loads(json.dumps(contract, sort_keys=True))

        self.assertEqual(contract, decoded)
        self.assertEqual("mcm.active_av_field_state.v1", contract["contract_id"])
        self.assertEqual(["auditory", "visual"], contract["modalities"])
        self.assertEqual(
            list(current_api.CURRENT_CONTROLLED_FIELD_EXPORTS),
            contract["active_export_names"],
        )
        self.assertEqual(
            [item.name for item in fields(current_api.ReceptorTimeSequence)],
            contract["receptor_sequence_fields"],
        )
        self.assertEqual(
            [item.name for item in fields(current_api.OrganismTimedReceptorFrame)],
            contract["timed_receptor_frame_fields"],
        )
        self.assertEqual(
            [item.name for item in fields(current_api.ReceptorProposalHandoff)],
            contract["handoff_fields"],
        )
        self.assertEqual(
            [item.name for item in fields(current_api.NeutralAsynchronousFieldRun)],
            contract["field_run_fields"],
        )

    def test_snapshot_and_reference_manifests_remain_separate(self) -> None:
        contract = current_api.active_field_state_contract()

        self.assertEqual(
            {
                "schema_version": 1,
                "root_keys": [
                    "schema_version",
                    "layer",
                    "docks",
                    "last_distribution",
                ],
                "reference_state_fields": ["substrate", "development"],
            },
            contract["snapshot"],
        )
        self.assertEqual(
            {
                "passive_comparison": list(
                    current_api.PASSIVE_COMPARISON_EXPORTS
                ),
                "ci": list(current_api.CI_REFERENCE_EXPORTS),
                "f3": list(current_api.F3_REFERENCE_EXPORTS),
                "s1b": list(current_api.S1B_REFERENCE_EXPORTS),
            },
            contract["reference_manifests"],
        )
        self.assertFalse(contract["memory_claim"])
        self.assertIn(
            "active_field_state_contract",
            contract["active_export_names"],
        )

    def test_digest_is_canonical_deterministic_and_state_free(self) -> None:
        first_contract = current_api.active_field_state_contract()
        encoded = json.dumps(
            first_contract,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        expected = hashlib.sha256(encoded).hexdigest()

        self.assertEqual(expected, current_api.active_field_state_contract_digest())
        self.assertEqual(
            current_api.active_field_state_contract_digest(),
            current_api.active_field_state_contract_digest(),
        )
        self.assertEqual(64, len(expected))
        int(expected, 16)

        first_contract["memory_claim"] = True
        self.assertFalse(current_api.active_field_state_contract()["memory_claim"])


if __name__ == "__main__":
    unittest.main()
