from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wo_static_receipt_composition_preflight as s1wo
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


EXPECTED_PREFLIGHT_DIGEST = (
    "ab96a2bf9965fd6f31550a45817e77db6fd1d90a02dcb481ae4fdc078d4c9374"
)


class PPB1S1WOStaticReceiptCompositionPreflightTests(unittest.TestCase):
    def test_contract_and_s1wn_source_are_bound(self) -> None:
        result = s1wo.run_s1wo_static_preflight()
        self.assertEqual(s1wo.S1WO_CONTRACT_DIGEST, result.contract_digest)
        self.assertEqual(s1wo.S1WO_S1WN_SOURCE_DIGEST, result.s1wn_source_digest)

    def test_exact_eight_private_structure_checks_pass(self) -> None:
        passed = tuple(
            role
            for role, value in s1wo.run_s1wo_static_preflight().checks
            if value
        )
        self.assertEqual(
            (
                "S1WG_CONTRACT_DIGEST_VALID",
                "S1WN_SOURCE_DIGEST_BOUND",
                "THREE_PRIVATE_INPUT_TYPES_COMPLETE",
                "TWO_DIGEST_EQUALITIES_COMPLETE",
                "THREE_POSITIVE_INPUT_GATES_COMPLETE",
                "H0B_TO_H1_COMPOSITION_ROLES_COMPLETE",
                "SYNTHETIC_H0E_H1_AND_ZERO_EFFECTS_BOUND",
                "RECEIPT_PRODUCERS_RUNTIME_ABSENT_ENTRY_BLOCKED",
            ),
            passed,
        )

    def test_exact_six_production_blockers_remain(self) -> None:
        result = s1wo.run_s1wo_static_preflight()
        self.assertEqual(s1wo.S1WO_DECISION, result.decision)
        self.assertEqual(s1wo.S1WO_BLOCKERS, result.blockers)
        self.assertFalse(result.ready_for_production_execution)

    def test_only_six_production_checks_fail(self) -> None:
        failed = tuple(
            role
            for role, passed in s1wo.run_s1wo_static_preflight().checks
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
        first = s1wo.run_s1wo_static_preflight()
        second = s1wo.run_s1wo_static_preflight()
        self.assertEqual(first, second)
        self.assertEqual(EXPECTED_PREFLIGHT_DIGEST, first.digest())

    def test_s1wn_source_drift_fails_closed(self) -> None:
        with patch.object(s1wo, "S1WO_S1WN_SOURCE_DIGEST", "0" * 64):
            with self.assertRaises(s1wo.S1WOPreflightError) as raised:
                s1wo.run_s1wo_static_preflight()
        self.assertEqual(s1wo.S1WO_PREFLIGHT_DRIFT, raised.exception.code)

    def test_only_source_and_contract_reads_have_nonzero_counts(self) -> None:
        result = s1wo.run_s1wo_static_preflight()
        self.assertEqual(
            (1, 1),
            (result.source_read_count, result.contract_read_count),
        )
        self.assertEqual(
            (0,) * 15,
            (
                result.composition_call_count,
                result.coordinator_call_count,
                result.adapter_call_count,
                result.root_receipt_producer_call_count,
                result.resource_receipt_producer_call_count,
                result.authorization_validator_call_count,
                result.operating_system_probe_count,
                result.filesystem_write_count,
                result.execution_id_freshness_check_count,
                result.authorization_instantiation_count,
                result.lock_write_count,
                result.producer_resolution_count,
                result.producer_call_count,
                result.matrix_path_count,
                result.production_artifact_count,
            ),
        )

    def test_preflight_function_never_calls_s1wn_or_dependencies(self) -> None:
        tree = ast.parse(Path(s1wo.__file__).read_text(encoding="utf-8"))
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "run_s1wo_static_preflight"
        )
        calls = set()
        for node in ast.walk(function):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
        self.assertTrue(
            {
                "compose_s1wn_in_memory_h0_h1",
                "run_injected_h0_h1",
                "resolve_s1wj_injected_root_mirror",
                "observe_s1wj_injected_resources",
                "validate_s1wl_injected_authorization_text",
                "execute_s1wn_production_once",
            }.isdisjoint(calls)
        )

    def test_preflight_source_has_no_runtime_dependencies(self) -> None:
        tree = ast.parse(Path(s1wo.__file__).read_text(encoding="utf-8"))
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

    def test_s1wo_remains_private_and_snapshot_neutral(self) -> None:
        names = {"S1WOPreflightResult", "run_s1wo_static_preflight"}
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
