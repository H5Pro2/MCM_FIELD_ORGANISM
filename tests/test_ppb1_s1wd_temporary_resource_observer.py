from __future__ import annotations

import ast
from dataclasses import fields
import os
from pathlib import Path
from tempfile import TemporaryDirectory, gettempdir
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wb_private_production_h0_types as s1wb
import mcm_field_organism._ppb1_s1wd_temporary_resource_observer as s1wd
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
EXECUTION_ID = "s1wd.synthetic.case-001"


class PPB1S1WDTemporaryResourceObserverTests(unittest.TestCase):
    def temporary_observer_root(self, parent: str) -> Path:
        root = Path(parent) / "s1wd-h0-observer"
        root.mkdir()
        return root

    def test_real_observation_binds_current_resources_and_sources(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            result = s1wd.observe_s1wd_temporary_h0(
                self.temporary_observer_root(parent), EXECUTION_ID
            )

        observation = result.observation
        self.assertGreater(observation.available_physical_memory_bytes, 0)
        self.assertGreater(observation.artifact_volume_free_bytes, 0)
        self.assertEqual(s1wb.S1WB_PLATFORM_BINDING, observation.platform_binding)
        self.assertEqual(
            s1wb.S1WB_CALIBRATED_SOURCE_DIGESTS,
            observation.source_digests,
        )
        self.assertEqual(
            observation.artifact_volume_identity,
            observation.temporary_volume_identity,
        )
        self.assertTrue(observation.same_volume)
        self.assertTrue(observation.atomic_replace_probe_passed)
        self.assertTrue(observation.artifact_paths_free)

    def test_real_observation_is_accepted_by_the_existing_gate(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            result = s1wd.observe_s1wd_temporary_h0(
                self.temporary_observer_root(parent), EXECUTION_ID
            )
        observation = result.observation
        gate = s1wb.evaluate_s1wb_resource_gate(observation)
        self.assertEqual(
            observation.available_physical_memory_bytes
            >= s1wb.S1WB_MINIMUM_FREE_MEMORY_BYTES,
            gate.memory_gate_passed,
        )
        self.assertEqual(
            observation.artifact_volume_free_bytes
            >= s1wb.S1WB_MINIMUM_FREE_DISK_BYTES,
            gate.disk_gate_passed,
        )
        self.assertTrue(gate.platform_gate_passed)
        self.assertTrue(gate.source_gate_passed)
        self.assertTrue(gate.same_volume_gate_passed)
        self.assertTrue(gate.atomic_replace_gate_passed)
        self.assertTrue(gate.artifact_paths_gate_passed)

    def test_atomic_probe_is_single_and_leaves_no_artifact(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.temporary_observer_root(parent)
            result = s1wd.observe_s1wd_temporary_h0(root, EXECUTION_ID)
            remaining = tuple(root.iterdir())
        self.assertEqual(1, result.atomic_probe_count)
        self.assertTrue(result.probe_cleanup_passed)
        self.assertEqual(0, result.production_artifact_count)
        self.assertEqual((), remaining)

    def test_existing_role_path_fails_the_path_gate_without_mutation(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.temporary_observer_root(parent)
            existing = root / f"{EXECUTION_ID}.lock.json"
            existing.write_bytes(b"sentinel")
            result = s1wd.observe_s1wd_temporary_h0(root, EXECUTION_ID)
            self.assertEqual(b"sentinel", existing.read_bytes())
            self.assertEqual((existing,), tuple(root.iterdir()))
        self.assertFalse(result.observation.artifact_paths_free)

    def test_existing_atomic_probe_path_fails_closed_without_overwrite(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.temporary_observer_root(parent)
            existing = root / f".{EXECUTION_ID}.atomic-probe.tmp"
            existing.write_bytes(b"sentinel")
            with self.assertRaises(s1wd.S1WDObservationError) as raised:
                s1wd.observe_s1wd_temporary_h0(root, EXECUTION_ID)
            self.assertEqual(b"sentinel", existing.read_bytes())
        self.assertEqual(
            s1wd.S1WD_ATOMIC_REPLACE_PROBE_FAILED,
            raised.exception.code,
        )

    def test_wrong_temporary_root_name_is_rejected(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = Path(parent) / "wrong-name"
            root.mkdir()
            with self.assertRaises(s1wd.S1WDObservationError) as raised:
                s1wd.observe_s1wd_temporary_h0(root, EXECUTION_ID)
        self.assertEqual(s1wd.S1WD_INVALID_TEMPORARY_ROOT, raised.exception.code)

    def test_workspace_root_is_rejected_even_with_expected_name(self) -> None:
        with TemporaryDirectory(dir=ROOT) as parent:
            root = self.temporary_observer_root(parent)
            with self.assertRaises(s1wd.S1WDObservationError) as raised:
                s1wd.observe_s1wd_temporary_h0(root, EXECUTION_ID)
        self.assertEqual(s1wd.S1WD_INVALID_TEMPORARY_ROOT, raised.exception.code)

    def test_production_root_is_explicitly_rejected(self) -> None:
        production = ROOT / "data" / "generated" / "ppb1" / "one_shot"
        previous = Path.cwd()
        with TemporaryDirectory(dir=gettempdir()) as other_working_directory:
            os.chdir(other_working_directory)
            try:
                with self.assertRaises(s1wd.S1WDObservationError) as raised:
                    s1wd.observe_s1wd_temporary_h0(production, EXECUTION_ID)
            finally:
                os.chdir(previous)
        self.assertEqual(s1wd.S1WD_PRODUCTION_ROOT_BLOCKED, raised.exception.code)

    def test_invalid_execution_id_is_rejected_before_probe(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.temporary_observer_root(parent)
            with self.assertRaises(s1wd.S1WDObservationError) as raised:
                s1wd.observe_s1wd_temporary_h0(root, "production.case-001")
            self.assertEqual((), tuple(root.iterdir()))
        self.assertEqual(s1wd.S1WD_INVALID_EXECUTION_ID, raised.exception.code)

    def test_production_entrypoint_and_runner_calls_remain_blocked(self) -> None:
        with self.assertRaises(s1wd.S1WDObservationError) as raised:
            s1wd.execute_s1wd_production_once()
        self.assertEqual(
            s1wd.S1WD_PRODUCTION_EXECUTION_BLOCKED,
            raised.exception.code,
        )

        tree = ast.parse(Path(s1wd.__file__).read_text(encoding="utf-8"))
        calls = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertTrue(
            {
                "_execute_s1vq_corrected_matrix",
                "execute_s1vq_corrected_matrix",
                "run_s1vw_synthetic_once",
                "run_s1vz_three_process_calibration",
            }.isdisjoint(calls)
        )

    def test_s1wd_remains_private_and_snapshot_neutral(self) -> None:
        names = {
            "S1WDTemporaryObservationResult",
            "observe_s1wd_temporary_h0",
            "execute_s1wd_production_once",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
