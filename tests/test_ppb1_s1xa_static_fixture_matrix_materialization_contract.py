from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "S1XA_PPB1_STATISCHER_FIXTURE_UND_60_ZELLEN_MATRIXMATERIALISIERUNGSVERTRAG_V1.json"
)
EXPECTED_CONTRACT_DIGEST = (
    "2c3e36d4e3acaa05a5158a5e209b445f925e8d9b7926794a7b82e0c91dbc093c"
)


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class PPB1S1XAStaticFixtureMatrixMaterializationContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        payload = load_contract()
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(
            EXPECTED_CONTRACT_DIGEST,
            hashlib.sha256(encoded).hexdigest(),
        )

    def test_parent_and_source_digests_are_exact(self) -> None:
        contract = load_contract()
        self.assertEqual(
            "22b6972bd5f3b9c25f3aef28293aae4e4b4b7288de4b6736e5d876b33d4f9059",
            contract["parent_s1wz_audit_digest"],
        )
        sources = contract["bound_source_digests"]
        for role, relative in (
            ("ppb1_reference", "mcm_field_organism/_ppb1_reference.py"),
            ("ppb1_receptor_profiles", "mcm_field_organism/_ppb1_receptor_profiles.py"),
            ("s1wu_read_only_probe", "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py"),
        ):
            self.assertEqual(
                sources[role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_controlled_profile_and_carrier_derivation_are_bound(self) -> None:
        profile = load_contract()["profile_binding"]
        self.assertEqual("controlled", profile["profile_id"])
        self.assertEqual(12, profile["auditory_carrier_count"])
        self.assertEqual(72, profile["visual_carrier_count"])
        self.assertTrue(profile["ordered_carrier_ids_must_be_derived_from_existing_profile_binder"])
        self.assertFalse(profile["independent_hardcoded_carrier_inventory_allowed"])

    def test_two_finite_configs_are_inside_existing_corridors(self) -> None:
        configs = {item["modality_id"]: item for item in load_contract()["modality_configs"]}
        auditory = configs["auditory"]
        visual = configs["visual"]
        self.assertTrue(8 <= auditory["capacity"] <= 32)
        self.assertTrue(0.02 <= auditory["match_threshold"] <= 0.25)
        self.assertTrue(3 <= auditory["stable_after"] <= 16)
        self.assertTrue(4 <= visual["capacity"] <= 16)
        self.assertTrue(0.01 <= visual["match_threshold"] <= 0.20)
        self.assertTrue(3 <= visual["stable_after"] <= 12)

    def test_formation_and_frozen_candidate_prestate_are_exact(self) -> None:
        contract = load_contract()
        formation = contract["formation_fixture"]
        self.assertEqual(3, formation["formation_contact_count_per_modality"])
        self.assertEqual([[0, 1], [1, 2], [2, 3]], formation["ordered_contact_windows"])
        self.assertFalse(formation["raw_media_or_semantic_payload_allowed"])
        frozen = contract["stabilized_candidate_prestate_expectation"]
        self.assertEqual((3, 1, 1, 3), (
            frozen["accepted_step_count"],
            frozen["occupied_slot_count"],
            frozen["stabilized_slot_count"],
            frozen["support_count"],
        ))
        self.assertTrue(frozen["one_frozen_prestate_per_modality_shared_by_all_five_candidate_probe_cells"])

    def test_probe_values_distances_masks_and_independence_are_bound(self) -> None:
        probes = load_contract()["probe_fixtures"]
        for modality in ("auditory", "visual"):
            fixture = probes[modality]
            self.assertEqual(fixture["component_values"], fixture["expected_distances"])
            threshold = 0.2 if modality == "auditory" else 0.1
            self.assertEqual(
                fixture["expected_recognition_mask"],
                [distance <= threshold for distance in fixture["expected_distances"]],
            )
        self.assertEqual([4, 5], probes["contact_window"])
        self.assertTrue(probes["one_independent_frozen_prestate_per_probe_cell"])

    def test_six_systems_have_prebound_information_and_storage_roles(self) -> None:
        systems = {item["system_id"]: item for item in load_contract()["systems"]}
        self.assertEqual(6, len(systems))
        self.assertEqual(0, systems["no-memory"]["stored_scalar_multiplier_by_modality_dimension"])
        self.assertEqual(3, systems["replay"]["stored_scalar_multiplier_by_modality_dimension"])
        self.assertTrue(systems["replay"]["raw_history_access_used"])
        for system_id in ("ppb1", "static-prototype", "moving-state", "last-vector-distance"):
            self.assertEqual(1, systems[system_id]["stored_scalar_multiplier_by_modality_dimension"])
            self.assertFalse(systems[system_id]["raw_history_access_used"])

    def test_matrix_registry_has_exact_sixty_unique_digest_bound_cells(self) -> None:
        registry = load_contract()["matrix_registry"]
        cells = []
        for modality in registry["ordered_modality_ids"]:
            for system in registry["ordered_system_ids"]:
                for probe in registry["ordered_probe_classes"]:
                    cells.append({
                        "cell_id": f"s1xa.{modality}.{system}.{probe}",
                        "modality_id": modality,
                        "system_id": system,
                        "probe_class": probe,
                    })
        encoded = json.dumps(
            cells,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(60, len(cells))
        self.assertEqual(60, len({cell["cell_id"] for cell in cells}))
        self.assertEqual(registry["first_cell_id"], cells[0]["cell_id"])
        self.assertEqual(registry["last_cell_id"], cells[-1]["cell_id"])
        self.assertEqual(registry["registry_digest"], hashlib.sha256(encoded).hexdigest())

    def test_materialization_roles_and_all_ten_gates_are_complete(self) -> None:
        contract = load_contract()
        self.assertEqual(16, len(contract["cell_materialization_roles"]))
        self.assertEqual(10, len(contract["materialization_gates_before_any_execution"]))
        self.assertIn(
            "NO_RESULT_DERIVED_VALUE_EXISTS",
            contract["materialization_gates_before_any_execution"],
        )

    def test_expected_result_is_prebound_as_baseline_explained(self) -> None:
        expected = load_contract()["prebound_expected_decision_if_execution_matches_contract"]
        self.assertEqual("TECHNICAL_MEMORY_FUNCTION_PASS", expected["candidate_function_decision"])
        self.assertEqual(
            "TECHNICAL_MEMORY_FUNCTION_PASS_BASELINE_EXPLAINED",
            expected["baseline_explanation_decision"],
        )
        self.assertEqual(4, len(expected["expected_explaining_baselines"]))
        self.assertFalse(expected["no_memory_expected_to_explain"])
        self.assertFalse(expected["mcm_specific_memory_claim_allowed"])

    def test_fail_closed_rules_and_prohibitions_keep_execution_at_zero(self) -> None:
        contract = load_contract()
        self.assertEqual(8, len(contract["fail_closed_rules"]))
        self.assertEqual(9, len(contract["current_prohibitions"]))
        self.assertEqual(0, contract["planned_execution_count"])


if __name__ == "__main__":
    unittest.main()
