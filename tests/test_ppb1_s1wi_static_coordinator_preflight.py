from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wi_static_coordinator_preflight as s1wi
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


EXPECTED_PREFLIGHT_DIGEST = (
    "23570a445ec570ec375ccaefd1aa7a7b7f17bdb021778b145de303d1bd93e2ab"
)


class PPB1S1WIStaticCoordinatorPreflightTests(unittest.TestCase):
    def test_parent_contract_preflight_and_source_are_bound(self) -> None:
        result = s1wi.run_s1wi_static_preflight()
        self.assertEqual(s1wi.S1WI_CONTRACT_DIGEST, result.contract_digest)
        self.assertEqual(
            s1wi.S1WI_PARENT_PREFLIGHT_DIGEST,
            result.parent_preflight_digest,
        )
        self.assertEqual(
            s1wi.S1WI_S1WH_SOURCE_DIGEST,
            result.s1wh_source_digest,
        )

    def test_exact_eight_private_structure_checks_pass(self) -> None:
        result = s1wi.run_s1wi_static_preflight()
        passed = tuple(role for role, value in result.checks if value)
        self.assertEqual(
            (
                "S1WG_CONTRACT_DIGEST_VALID",
                "S1WH_SOURCE_DIGEST_BOUND",
                "SIX_PRIVATE_INTEGRATION_ROLE_TYPES_COMPLETE",
                "IMMUTABLE_IN_MEMORY_ADAPTER_COMPLETE",
                "PRODUCER_RESOLVER_STRUCTURALLY_NONCALLABLE",
                "H0A_TO_H1_AND_H2_BLOCK_STATICALLY_BOUND",
                "SEVEN_ZERO_EFFECT_COUNTERS_BOUND",
                "RUNTIME_IMPORTS_ABSENT_AND_ENTRY_BLOCKED",
            ),
            passed,
        )

    def test_exact_six_production_blockers_remain(self) -> None:
        result = s1wi.run_s1wi_static_preflight()
        self.assertEqual(s1wi.S1WI_DECISION, result.decision)
        self.assertEqual(s1wi.S1WI_BLOCKERS, result.blockers)
        self.assertFalse(result.ready_for_production_execution)

    def test_only_six_production_checks_fail(self) -> None:
        failed = tuple(
            role
            for role, passed in s1wi.run_s1wi_static_preflight().checks
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

    def test_preflight_is_canonical_and_deterministic(self) -> None:
        first = s1wi.run_s1wi_static_preflight()
        second = s1wi.run_s1wi_static_preflight()
        self.assertEqual(first, second)
        self.assertEqual(EXPECTED_PREFLIGHT_DIGEST, first.digest())

    def test_s1wh_source_drift_fails_closed(self) -> None:
        with patch.object(s1wi, "S1WI_S1WH_SOURCE_DIGEST", "0" * 64):
            with self.assertRaises(s1wi.S1WIPreflightError) as raised:
                s1wi.run_s1wi_static_preflight()
        self.assertEqual(s1wi.S1WI_PREFLIGHT_DRIFT, raised.exception.code)

    def test_only_one_source_and_contract_read_have_nonzero_counts(self) -> None:
        result = s1wi.run_s1wi_static_preflight()
        self.assertEqual(1, result.source_read_count)
        self.assertEqual(1, result.contract_read_count)
        self.assertEqual(
            (0, 0, 0, 0, 0, 0, 0, 0),
            (
                result.coordinator_call_count,
                result.resource_probe_count,
                result.filesystem_write_count,
                result.authorization_instantiation_count,
                result.producer_resolution_count,
                result.producer_call_count,
                result.matrix_path_count,
                result.production_artifact_count,
            ),
        )

    def test_preflight_function_never_calls_s1wh_runtime(self) -> None:
        tree = ast.parse(Path(s1wi.__file__).read_text(encoding="utf-8"))
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "run_s1wi_static_preflight"
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
            "run_injected_h0_h1",
            "build_s1wh_injected_receipt",
            "execute_s1wh_production_once",
            "S1WHInjectedStageAdapter",
            "S1WGPrivateProductionCoordinator",
        ):
            self.assertNotIn(forbidden, calls)

    def test_preflight_source_has_no_runtime_dependencies(self) -> None:
        tree = ast.parse(Path(s1wi.__file__).read_text(encoding="utf-8"))
        imports = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.update(alias.name for alias in node.names)
        self.assertTrue(
            {
                "os",
                "ctypes",
                "shutil",
                "tempfile",
                "_execute_s1vq_corrected_matrix",
                "SharedMCMField",
                "ReceptorContactFrame",
            }.isdisjoint(imports)
        )

    def test_s1wi_remains_private_and_snapshot_neutral(self) -> None:
        names = {"S1WIPreflightResult", "run_s1wi_static_preflight"}
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
