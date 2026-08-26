from __future__ import annotations

from dataclasses import fields
import hashlib
import inspect
import json
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wb_private_production_h0_types as s1wb
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_OBSERVATION_DIGEST = (
    "bbad80105e915c3c7cb1758a65f9a1bfbec030c1144720016d2c5506a07aad0e"
)
EXPECTED_GATE_DIGEST = (
    "42f87bba351984502d96228f7a85fcdb10f90db5908cd3265646d3a52157bde2"
)
EXPECTED_CANDIDATE_DIGEST = (
    "55a04e8510a82f2f3d9ea945b432cffb9364603aeb13b29d81314c3fc6ae457f"
)
EXPECTED_H0_DIGEST = (
    "cbb4b70ee56a013af1efc327d49528c10fd089f4d60608338837bcd6716412a6"
)


class PPB1S1WBPrivateProductionH0TypesTests(unittest.TestCase):
    def passing_observation(self):
        return s1wb.build_s1wb_injected_observation(
            3 * 1024**3, 2 * 1024**3
        )

    def test_contract_digest_matches_canonical_json(self) -> None:
        path = (
            ROOT
            / "docs"
            / "S1WA_PPB1_PRODUKTIONSBINDUNGS_RESSOURCEN_UND_"
            "AUTORISIERUNGSVERTRAG_V1.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        encoded = json.dumps(
            payload, sort_keys=True, separators=(",", ":")
        ).encode()
        self.assertEqual(
            s1wb.S1WB_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest()
        )

    def test_passing_injected_observation_and_gate_are_canonical(self) -> None:
        observation = self.passing_observation()
        gate = s1wb.evaluate_s1wb_resource_gate(observation)
        self.assertEqual(EXPECTED_OBSERVATION_DIGEST, observation.observation_digest)
        self.assertEqual(EXPECTED_GATE_DIGEST, gate.resource_gate_digest)
        self.assertTrue(gate.all_resource_gates_passed)
        self.assertTrue(
            all(
                value
                for name, value in gate.payload_without_digest().items()
                if name.endswith("_gate_passed")
            )
        )

    def test_memory_and_disk_thresholds_are_inclusive_and_separate(self) -> None:
        exact = s1wb.evaluate_s1wb_resource_gate(
            s1wb.build_s1wb_injected_observation(2 * 1024**3, 1024**3)
        )
        self.assertTrue(exact.memory_gate_passed)
        self.assertTrue(exact.disk_gate_passed)

        low_memory = s1wb.evaluate_s1wb_resource_gate(
            s1wb.build_s1wb_injected_observation(2 * 1024**3 - 1, 1024**3)
        )
        self.assertFalse(low_memory.memory_gate_passed)
        self.assertTrue(low_memory.disk_gate_passed)

        low_disk = s1wb.evaluate_s1wb_resource_gate(
            s1wb.build_s1wb_injected_observation(2 * 1024**3, 1024**3 - 1)
        )
        self.assertTrue(low_disk.memory_gate_passed)
        self.assertFalse(low_disk.disk_gate_passed)

    def test_platform_and_source_drift_fail_independently(self) -> None:
        platform = s1wb.S1WB_PLATFORM_BINDING[:-1] + (
            ("pointer_width_bits", "32"),
        )
        platform_gate = s1wb.evaluate_s1wb_resource_gate(
            s1wb.build_s1wb_injected_observation(
                3 * 1024**3, 2 * 1024**3, platform_binding=platform
            )
        )
        self.assertFalse(platform_gate.platform_gate_passed)
        self.assertTrue(platform_gate.source_gate_passed)

        sources = s1wb.S1WB_CALIBRATED_SOURCE_DIGESTS[:-1] + (
            ("s1vz_resource_calibrator", hashlib.sha256(b"drift").hexdigest()),
        )
        source_gate = s1wb.evaluate_s1wb_resource_gate(
            s1wb.build_s1wb_injected_observation(
                3 * 1024**3, 2 * 1024**3, source_digests=sources
            )
        )
        self.assertTrue(source_gate.platform_gate_passed)
        self.assertFalse(source_gate.source_gate_passed)

    def test_volume_atomic_replace_and_path_gates_are_separate(self) -> None:
        cases = (
            (
                {"temporary_volume_identity": "SYNTHETIC-VOLUME-D"},
                "same_volume_gate_passed",
            ),
            ({"same_volume": False}, "same_volume_gate_passed"),
            ({"atomic_replace_probe_passed": False}, "atomic_replace_gate_passed"),
            ({"artifact_paths_free": False}, "artifact_paths_gate_passed"),
        )
        for changes, failed_role in cases:
            with self.subTest(role=failed_role):
                observation = s1wb.build_s1wb_injected_observation(
                    3 * 1024**3, 2 * 1024**3, **changes
                )
                gate = s1wb.evaluate_s1wb_resource_gate(observation)
                self.assertFalse(getattr(gate, failed_role))
                self.assertFalse(gate.all_resource_gates_passed)

    def test_authorization_candidate_is_exact_but_not_authorization(self) -> None:
        gate = s1wb.evaluate_s1wb_resource_gate(self.passing_observation())
        candidate = s1wb.build_s1wb_authorization_candidate(
            "s1wb.synthetic.case-001", gate
        )
        self.assertEqual(
            EXPECTED_CANDIDATE_DIGEST,
            candidate.authorization_candidate_digest,
        )
        self.assertIn(gate.resource_gate_digest, candidate.rendered_authorization_text)
        self.assertFalse(
            candidate.payload_without_digest()["authorization_instantiation_enabled"]
        )

    def test_candidate_requires_fully_passed_gate(self) -> None:
        gate = s1wb.evaluate_s1wb_resource_gate(
            s1wb.build_s1wb_injected_observation(0, 0)
        )
        with self.assertRaises(s1wb.S1WBValidationError):
            s1wb.build_s1wb_authorization_candidate(
                "s1wb.synthetic.case-002", gate
            )

    def test_production_authorization_type_is_present_but_locked(self) -> None:
        expected_fields = {
            "execution_id",
            "rendered_authorization_text",
            "contract_digest",
            "calibration_digest",
            "resource_gate_digest",
            "parent_plan_digest",
            "corrected_plan_digest",
            "case_count",
            "maximum_registered_call_count",
            "production_entrypoint_id",
            "retry_permitted",
            "authorization_digest",
        }
        self.assertEqual(
            expected_fields,
            {item.name for item in fields(s1wb.S1WAProductionAuthorization)},
        )
        with self.assertRaises(s1wb.S1WBValidationError) as raised:
            s1wb.S1WAProductionAuthorization()
        self.assertEqual(
            s1wb.S1WB_PRODUCTION_AUTHORIZATION_BLOCKED,
            raised.exception.code,
        )

    def test_h0_candidate_stops_only_at_authorization_activation(self) -> None:
        result = s1wb.validate_s1wb_h0_candidate(
            self.passing_observation(), "s1wb.synthetic.case-001"
        )
        self.assertEqual(EXPECTED_H0_DIGEST, result.digest())
        self.assertEqual(s1wb.S1WB_DECISION, result.decision)
        self.assertFalse(result.ready_for_h1)
        self.assertEqual(
            ("H0D_PRODUCTION_AUTHORIZATION_INSTANTIABLE",),
            tuple(role for role, passed in result.checks if not passed),
        )
        self.assertEqual(0, result.producer_call_count)
        self.assertEqual(0, result.production_artifact_count)

    def test_production_entrypoint_remains_hard_blocked(self) -> None:
        with self.assertRaises(s1wb.S1WBValidationError) as raised:
            s1wb.execute_s1wb_production_once()
        self.assertEqual(
            s1wb.S1WB_PRODUCTION_AUTHORIZATION_BLOCKED,
            raised.exception.code,
        )

    def test_module_has_no_resource_probe_filesystem_or_runner_call(self) -> None:
        source = inspect.getsource(s1wb)
        for forbidden in (
            "import os",
            "import shutil",
            "import platform",
            "from pathlib",
            "_execute_s1vq_corrected_matrix(",
            "execute_s1vq_corrected_matrix(",
            "run_s1vw_synthetic_once(",
            "disk_usage(",
            "GetProcessMemoryInfo",
            "open(",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1wb_remains_private_and_snapshot_neutral(self) -> None:
        names = {
            "S1WAProductionResourceObservation",
            "S1WAProductionResourceGate",
            "S1WAProductionAuthorization",
            "validate_s1wb_h0_candidate",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
