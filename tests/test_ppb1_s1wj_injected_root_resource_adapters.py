from __future__ import annotations

from dataclasses import fields
import hashlib
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory, gettempdir
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wb_private_production_h0_types as s1wb
import mcm_field_organism._ppb1_s1wh_private_injected_coordinator_shell as s1wh
import mcm_field_organism._ppb1_s1wj_injected_root_resource_adapters as s1wj
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]


class PPB1S1WJInjectedRootResourceAdaptersTests(unittest.TestCase):
    def mirror(self, parent: str) -> Path:
        root = Path(parent) / s1wj.S1WJ_MIRROR_ROOT_NAME
        root.mkdir()
        return root

    def root_receipt(
        self,
        root: Path,
        artifact_volume="SYNTHETIC-VOLUME-C",
        temporary_volume="SYNTHETIC-VOLUME-C",
    ):
        return s1wj.resolve_s1wj_injected_root_mirror(
            root,
            artifact_volume,
            temporary_volume,
        )

    def resource_receipt(self, root_receipt, **changes):
        values = {
            "available_physical_memory_bytes": 3 * 1024**3,
            "artifact_volume_free_bytes": 2 * 1024**3,
            "atomic_replace_probe_passed": True,
            "artifact_paths_free": True,
        }
        values.update(changes)
        return s1wj.observe_s1wj_injected_resources(root_receipt, **values)

    def test_root_mirror_receipt_is_canonical_and_write_free(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.mirror(parent)
            receipt = self.root_receipt(root)
            self.assertEqual((), tuple(root.iterdir()))
        self.assertEqual(
            s1wj.S1WJ_PRODUCTION_RELATIVE_ROOT,
            receipt.declared_production_relative_root,
        )
        self.assertTrue(receipt.same_volume)
        self.assertTrue(receipt.mirror_only)
        self.assertFalse(receipt.production_root_accessed)
        self.assertEqual(0, receipt.filesystem_write_count)
        self.assertEqual(0, receipt.production_artifact_count)
        self.assertEqual(receipt.receipt_digest, receipt.canonical_payload()["receipt_digest"])

    def test_real_production_root_is_rejected_before_existence_requirement(self) -> None:
        production = ROOT / "data" / "generated" / "ppb1" / "one_shot"
        with self.assertRaises(s1wj.S1WJAdapterError) as raised:
            self.root_receipt(production)
        self.assertEqual(s1wj.S1WJ_PRODUCTION_ROOT_BLOCKED, raised.exception.code)

    def test_wrong_name_and_workspace_mirror_are_rejected(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            wrong = Path(parent) / "wrong-name"
            wrong.mkdir()
            with self.assertRaises(s1wj.S1WJAdapterError) as raised:
                self.root_receipt(wrong)
        self.assertEqual(s1wj.S1WJ_INVALID_MIRROR_ROOT, raised.exception.code)

        with TemporaryDirectory(dir=ROOT) as parent:
            local = self.mirror(parent)
            with self.assertRaises(s1wj.S1WJAdapterError) as local_error:
                self.root_receipt(local)
        self.assertEqual(
            s1wj.S1WJ_INVALID_MIRROR_ROOT,
            local_error.exception.code,
        )

    def test_invalid_volume_identity_is_rejected(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.mirror(parent)
            with self.assertRaises(s1wj.S1WJAdapterError) as raised:
                self.root_receipt(root, artifact_volume="invalid volume")
        self.assertEqual(s1wj.S1WJ_INVALID_MIRROR_ROOT, raised.exception.code)

    def test_volume_mismatch_remains_explicit_and_fails_h0b(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.mirror(parent)
            receipt = self.root_receipt(
                root,
                artifact_volume="SYNTHETIC-VOLUME-C",
                temporary_volume="SYNTHETIC-VOLUME-D",
            )
        adapter = s1wj.build_s1wj_h0b_adapter(receipt)
        self.assertFalse(receipt.same_volume)
        self.assertFalse(adapter.passed)
        self.assertEqual("H0B", adapter.expected_stage)

    def test_positive_resource_receipt_passes_existing_gate(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.mirror(parent)
            receipt = self.resource_receipt(self.root_receipt(root))
            self.assertEqual((), tuple(root.iterdir()))
        self.assertTrue(receipt.gate.all_resource_gates_passed)
        self.assertEqual(4, receipt.injected_value_count)
        self.assertEqual(receipt.observation.observation_digest, receipt.gate.observation_digest)
        self.assertEqual(
            (0, 0, 0, 0),
            (
                receipt.operating_system_probe_count,
                receipt.filesystem_write_count,
                receipt.production_root_access_count,
                receipt.production_artifact_count,
            ),
        )

    def test_memory_and_disk_fail_independently(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root_receipt = self.root_receipt(self.mirror(parent))
            low_memory = self.resource_receipt(
                root_receipt,
                available_physical_memory_bytes=2 * 1024**3 - 1,
            )
            low_disk = self.resource_receipt(
                root_receipt,
                artifact_volume_free_bytes=1024**3 - 1,
            )
        self.assertFalse(low_memory.gate.memory_gate_passed)
        self.assertTrue(low_memory.gate.disk_gate_passed)
        self.assertTrue(low_disk.gate.memory_gate_passed)
        self.assertFalse(low_disk.gate.disk_gate_passed)

    def test_atomic_and_path_injections_fail_independently(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root_receipt = self.root_receipt(self.mirror(parent))
            atomic = self.resource_receipt(
                root_receipt,
                atomic_replace_probe_passed=False,
            )
            paths = self.resource_receipt(
                root_receipt,
                artifact_paths_free=False,
            )
        self.assertFalse(atomic.gate.atomic_replace_gate_passed)
        self.assertTrue(atomic.gate.artifact_paths_gate_passed)
        self.assertTrue(paths.gate.atomic_replace_gate_passed)
        self.assertFalse(paths.gate.artifact_paths_gate_passed)

    def test_platform_and_source_drift_remain_separate(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root_receipt = self.root_receipt(self.mirror(parent))
            platform = s1wb.S1WB_PLATFORM_BINDING[:-1] + (
                ("pointer_width_bits", "32"),
            )
            source = s1wb.S1WB_CALIBRATED_SOURCE_DIGESTS[:-1] + (
                ("s1vz_resource_calibrator", hashlib.sha256(b"drift").hexdigest()),
            )
            platform_result = self.resource_receipt(
                root_receipt,
                platform_binding=platform,
            )
            source_result = self.resource_receipt(
                root_receipt,
                source_digests=source,
            )
        self.assertFalse(platform_result.gate.platform_gate_passed)
        self.assertTrue(platform_result.gate.source_gate_passed)
        self.assertTrue(source_result.gate.platform_gate_passed)
        self.assertFalse(source_result.gate.source_gate_passed)

    def test_h0b_h0c_adapters_bridge_into_s1wh_and_still_stop_at_h2(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root_receipt = self.root_receipt(self.mirror(parent))
            resource_receipt = self.resource_receipt(root_receipt)
        root_role = s1wh.S1WGProductionArtifactRootResolver(
            "s1wh.injected.root",
            s1wj.build_s1wj_h0b_adapter(root_receipt),
        )
        resource_role = s1wh.S1WGProductionResourceObserverAdapter(
            "s1wh.injected.resource",
            s1wj.build_s1wj_h0c_adapter(resource_receipt),
        )
        authorization = s1wh.S1WGExactProductionAuthorizationActivator(
            "s1wh.injected.authorization",
            s1wh.S1WHInjectedStageAdapter(
                "s1wh.injected.authorization", "H0D"
            ),
        )
        lock = s1wh.S1WGProductionLockTerminalAdapter(
            "s1wh.injected.lock",
            s1wh.S1WHInjectedStageAdapter("s1wh.injected.lock", "H0E"),
            s1wh.S1WHInjectedStageAdapter("s1wh.injected.lock", "H1"),
        )
        producer = s1wh.S1WGPrivateS1VQProducerResolver(
            "s1wh.injected.producer"
        )
        result = s1wh.S1WGPrivateProductionCoordinator(
            resource_role,
            authorization,
            lock,
            producer,
            root_role,
        ).run_injected_h0_h1()
        self.assertEqual("H2_BLOCKED", result.next_stage)
        self.assertEqual(0, result.producer_resolution_count)

    def test_production_entry_and_os_resource_apis_remain_blocked(self) -> None:
        with self.assertRaises(s1wj.S1WJAdapterError) as raised:
            s1wj.execute_s1wj_production_once()
        self.assertEqual(
            s1wj.S1WJ_PRODUCTION_EXECUTION_BLOCKED,
            raised.exception.code,
        )
        source = inspect.getsource(s1wj)
        for forbidden in (
            "import os",
            "import ctypes",
            "import shutil",
            "import platform",
            "disk_usage(",
            "_available_physical_memory(",
            "open(",
            "write_text(",
            "write_bytes(",
            "_execute_s1vq_corrected_matrix",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1wj_remains_private_and_snapshot_neutral(self) -> None:
        names = {
            "S1WJRootMirrorReceipt",
            "S1WJInjectedResourceReceipt",
            "resolve_s1wj_injected_root_mirror",
            "observe_s1wj_injected_resources",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
