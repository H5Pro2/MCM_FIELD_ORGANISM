from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wc_production_roles_preflight as s1wc
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


EXPECTED_PREFLIGHT_DIGEST = (
    "76bc75d6b50ae5904135df4dfef4b6d83b0fc0be400596ce85b7db8cf15d1b5f"
)
EXPECTED_SOURCE_DIGESTS = (
    (
        "s1vq_runner",
        "c9485bf36e6bec241ac3e0c565e7b5d5ec7fc4041596557f2e3db26ecb757c48",
    ),
    (
        "s1vt_pipeline",
        "0aeba24aac5732f11500ec02f51aded07097c0e58c54b05a9f6978ff6980b891",
    ),
    (
        "s1vw_synthetic_orchestrator",
        "37ea1c2a76b1a987dc72a3999162cd730484a75a5a3cdf60f04d6562320322f0",
    ),
    (
        "s1vz_resource_calibrator",
        "8ef0268fe3e1c5d9eac1e85092f21854ed7a09992e79dbf9e8efd1066d5c42f5",
    ),
    (
        "s1wb_private_h0_types",
        "ca46267182a38ad2324122a051885cd4360d80173deb671027b3f028ba271bef",
    ),
)


class PPB1S1WCProductionRolesPreflightTests(unittest.TestCase):
    def test_bound_plan_budget_and_resource_minima_are_preserved(self) -> None:
        result = s1wc.run_s1wc_static_preflight()
        self.assertEqual(528, result.case_count)
        self.assertEqual(75808, result.maximum_registered_call_count)
        self.assertEqual(2 * 1024**3, result.minimum_free_memory_bytes)
        self.assertEqual(1024**3, result.minimum_free_disk_bytes)
        self.assertEqual(s1wc.S1WC_CONTRACT_DIGEST, result.contract_digest)
        self.assertEqual(s1wc.S1WC_CALIBRATION_DIGEST, result.calibration_digest)

    def test_existing_contract_calibration_and_types_pass(self) -> None:
        checks = dict(s1wc.run_s1wc_static_preflight().checks)
        for role in (
            "S1WA_CONTRACT_DIGEST_VALID",
            "S1VZ_CALIBRATION_DIGEST_VALID",
            "CALIBRATED_SOURCE_DIGESTS_PRESERVED",
            "RESOURCE_OBSERVATION_FIELDS_COMPLETE",
            "RESOURCE_GATE_FIELDS_COMPLETE",
            "AUTHORIZATION_FIELDS_COMPLETE",
            "CALIBRATED_RESOURCE_MINIMA_PRESERVED",
        ):
            self.assertTrue(checks[role])

    def test_exact_six_remaining_production_blockers_are_bound(self) -> None:
        result = s1wc.run_s1wc_static_preflight()
        self.assertEqual(s1wc.S1WC_DECISION, result.decision)
        self.assertEqual(s1wc.S1WC_BLOCKERS, result.blockers)
        self.assertFalse(result.ready_for_production_implementation)
        self.assertEqual(0, result.resource_probe_count)
        self.assertEqual(0, result.producer_call_count)
        self.assertEqual(0, result.production_artifact_count)

    def test_only_six_bound_production_checks_fail(self) -> None:
        failed = tuple(
            role
            for role, passed in s1wc.run_s1wc_static_preflight().checks
            if not passed
        )
        self.assertEqual(
            (
                "REAL_RESOURCE_OBSERVER_PRESENT",
                "PRODUCTION_AUTHORIZATION_UNLOCKED",
                "LOCK_AND_TERMINAL_TYPES_PRESENT",
                "PRIVATE_REAL_PRODUCER_BOUND",
                "PRODUCTION_ARTIFACT_PATH_WIRED",
                "PRODUCTION_ENTRYPOINT_OPEN",
            ),
            failed,
        )

    def test_preflight_and_source_digests_are_canonical(self) -> None:
        first = s1wc.run_s1wc_static_preflight()
        second = s1wc.run_s1wc_static_preflight()
        self.assertEqual(first, second)
        self.assertEqual(EXPECTED_SOURCE_DIGESTS, first.source_digests)
        self.assertEqual(EXPECTED_PREFLIGHT_DIGEST, first.digest())

    def test_minimum_drift_fails_closed(self) -> None:
        with patch.object(s1wc.s1wb, "S1WB_MINIMUM_FREE_MEMORY_BYTES", 1):
            with self.assertRaises(s1wc.S1WCPreflightError) as raised:
                s1wc.run_s1wc_static_preflight()
        self.assertEqual(s1wc.S1WC_PREFLIGHT_DRIFT, raised.exception.code)

    def test_preflight_function_calls_no_runtime_role(self) -> None:
        source = Path(s1wc.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "run_s1wc_static_preflight"
        )
        calls = set()
        for node in ast.walk(function):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
        for forbidden in (
            "build_s1wb_injected_observation",
            "evaluate_s1wb_resource_gate",
            "build_s1wb_authorization_candidate",
            "validate_s1wb_h0_candidate",
            "execute_s1wb_production_once",
            "_execute_s1vq_corrected_matrix",
            "run_s1vw_synthetic_once",
            "run_s1vz_three_process_calibration",
        ):
            self.assertNotIn(forbidden, calls)

    def test_preflight_source_has_no_resource_or_filesystem_probe(self) -> None:
        source = Path(s1wc.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "import os",
            "import shutil",
            "import platform",
            "import ctypes",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1wc_remains_private_and_snapshot_neutral(self) -> None:
        names = {"S1WCPreflightResult", "run_s1wc_static_preflight"}
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
