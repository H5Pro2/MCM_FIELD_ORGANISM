from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wf_static_roles_integration_preflight as s1wf
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


EXPECTED_PREFLIGHT_DIGEST = (
    "bdd1f9652ac2cd094d794c4a589a2eeae90ca5357f5ccf34863f1368e99c96af"
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
    (
        "s1wd_temporary_resource_observer",
        "9db1b25065241b19c57fa5ad4bd939d73909eaac7980899e308017ba4fc71bef",
    ),
    (
        "s1we_private_lock_terminal_types",
        "59c0e98e08b6ecdc85ad44629fd55a9d6125e62957e2a386c3a92094639d9ace",
    ),
)


class PPB1S1WFStaticRolesIntegrationPreflightTests(unittest.TestCase):
    def test_contract_plan_budget_and_resource_minima_are_preserved(self) -> None:
        result = s1wf.run_s1wf_static_preflight()
        self.assertEqual(s1wf.S1WF_CONTRACT_DIGEST, result.contract_digest)
        self.assertEqual(s1wf.S1WF_CALIBRATION_DIGEST, result.calibration_digest)
        self.assertEqual(528, result.case_count)
        self.assertEqual(75808, result.maximum_registered_call_count)
        self.assertEqual(2 * 1024**3, result.minimum_free_memory_bytes)
        self.assertEqual(1024**3, result.minimum_free_disk_bytes)

    def test_private_s1wd_and_s1we_roles_are_complete(self) -> None:
        checks = dict(s1wf.run_s1wf_static_preflight().checks)
        for role in (
            "S1WD_SOURCE_DIGEST_BOUND",
            "S1WE_SOURCE_DIGEST_BOUND",
            "PRIVATE_TEMP_RESOURCE_OBSERVER_COMPLETE",
            "PRIVATE_LOCK_TERMINAL_TYPES_COMPLETE",
            "PRIVATE_TEMP_LOCK_TERMINAL_WRITERS_COMPLETE",
        ):
            self.assertTrue(checks[role])

    def test_exact_six_production_integration_blockers_are_bound(self) -> None:
        result = s1wf.run_s1wf_static_preflight()
        self.assertEqual(s1wf.S1WF_DECISION, result.decision)
        self.assertEqual(s1wf.S1WF_BLOCKERS, result.blockers)
        self.assertFalse(result.ready_for_production_execution)

    def test_only_the_six_production_integration_checks_fail(self) -> None:
        failed = tuple(
            role
            for role, passed in s1wf.run_s1wf_static_preflight().checks
            if not passed
        )
        self.assertEqual(
            (
                "PRODUCTION_RESOURCE_OBSERVER_WIRED",
                "PRODUCTION_AUTHORIZATION_UNLOCKED",
                "PRODUCTION_LOCK_TERMINAL_WRITERS_WIRED",
                "PRIVATE_REAL_PRODUCER_BOUND",
                "PRODUCTION_ARTIFACT_PATH_WIRED",
                "PRODUCTION_ENTRYPOINT_OPEN",
            ),
            failed,
        )

    def test_preflight_and_source_digests_are_canonical(self) -> None:
        first = s1wf.run_s1wf_static_preflight()
        second = s1wf.run_s1wf_static_preflight()
        self.assertEqual(first, second)
        self.assertEqual(EXPECTED_SOURCE_DIGESTS, first.source_digests)
        self.assertEqual(EXPECTED_PREFLIGHT_DIGEST, first.digest())

    def test_private_source_drift_fails_closed(self) -> None:
        with patch.object(s1wf, "S1WF_S1WD_SOURCE_DIGEST", "0" * 64):
            with self.assertRaises(s1wf.S1WFPreflightError) as raised:
                s1wf.run_s1wf_static_preflight()
        self.assertEqual(s1wf.S1WF_PREFLIGHT_DRIFT, raised.exception.code)

    def test_static_audit_has_zero_runtime_effects(self) -> None:
        result = s1wf.run_s1wf_static_preflight()
        self.assertEqual(0, result.resource_probe_count)
        self.assertEqual(0, result.filesystem_write_count)
        self.assertEqual(0, result.authorization_instantiation_count)
        self.assertEqual(0, result.producer_call_count)
        self.assertEqual(0, result.production_artifact_count)

    def test_preflight_function_calls_no_runtime_role(self) -> None:
        tree = ast.parse(Path(s1wf.__file__).read_text(encoding="utf-8"))
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "run_s1wf_static_preflight"
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
            "observe_s1wd_temporary_h0",
            "write_s1we_synthetic_lock",
            "publish_s1we_synthetic_terminal",
            "build_s1wb_injected_observation",
            "evaluate_s1wb_resource_gate",
            "S1WAProductionAuthorization",
            "_execute_s1vq_corrected_matrix",
            "run_s1vw_synthetic_once",
            "run_s1vz_three_process_calibration",
        ):
            self.assertNotIn(forbidden, calls)

    def test_preflight_source_has_no_resource_or_filesystem_runtime(self) -> None:
        source = Path(s1wf.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "import os",
            "import shutil",
            "import platform",
            "import ctypes",
            "from tempfile",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1wf_remains_private_and_snapshot_neutral(self) -> None:
        names = {"S1WFPreflightResult", "run_s1wf_static_preflight"}
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
