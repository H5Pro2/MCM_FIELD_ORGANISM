from __future__ import annotations

from dataclasses import fields
import hashlib
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory, gettempdir
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1we_private_lock_terminal_types as s1we
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
EXECUTION_ID = "s1we.synthetic.case-001"


def digest(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


class PPB1S1WEPrivateLockTerminalTypesTests(unittest.TestCase):
    def temporary_root(self, parent: str) -> Path:
        root = Path(parent) / s1we.S1WE_TEMPORARY_ROOT_NAME
        root.mkdir()
        return root

    def marker(self, execution_id: str = EXECUTION_ID):
        return s1we.build_s1we_synthetic_lock_marker(
            execution_id,
            digest("synthetic-authorization"),
            digest("synthetic-resource-gate"),
        )

    def success(self, marker=None):
        return s1we.build_s1we_synthetic_success_outcome(
            marker or self.marker(),
            digest("matrix"),
            digest("composition"),
            digest("evaluation"),
        )

    def error(self, marker=None):
        return s1we.build_s1we_synthetic_error_outcome(
            marker or self.marker(),
            "H4",
            "SYNTHETIC_SEAL_FAILED",
            digest("error-detail"),
            42,
        )

    def test_three_bound_production_role_types_are_canonical(self) -> None:
        marker = self.marker()
        success = self.success(marker)
        error = self.error(marker)
        self.assertEqual(marker, self.marker())
        self.assertEqual(success, self.success(marker))
        self.assertEqual(error, self.error(marker))
        self.assertEqual(
            "S1WAProductionLockMarker",
            marker.canonical_payload()["role"],
        )
        self.assertEqual("SUCCESS", success.canonical_payload()["status"])
        self.assertEqual("ERROR", error.canonical_payload()["status"])
        self.assertTrue(marker.authorization_consumed)
        self.assertFalse(marker.retry_permitted)
        self.assertFalse(success.partial_result_exposed)
        self.assertFalse(error.partial_result_exposed)

    def test_lock_is_created_exclusively_and_matches_canonical_bytes(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.temporary_root(parent)
            marker = self.marker()
            path = s1we.write_s1we_synthetic_lock(root, marker)
            payload = json.loads(path.read_text(encoding="utf-8"))
            before = path.read_bytes()
            with self.assertRaises(s1we.S1WEValidationError) as raised:
                s1we.write_s1we_synthetic_lock(root, marker)
            self.assertEqual(before, path.read_bytes())
        self.assertEqual(marker.canonical_payload(), payload)
        self.assertEqual(s1we.S1WE_ARTIFACT_ROLE_OCCUPIED, raised.exception.code)

    def test_any_existing_artifact_role_blocks_lock_without_mutation(self) -> None:
        for suffix in ("lock.json", "success.json", "error.json", "tmp"):
            with self.subTest(suffix=suffix), TemporaryDirectory(
                dir=gettempdir()
            ) as parent:
                root = self.temporary_root(parent)
                occupied = root / f"{EXECUTION_ID}.{suffix}"
                occupied.write_bytes(b"sentinel")
                with self.assertRaises(s1we.S1WEValidationError) as raised:
                    s1we.write_s1we_synthetic_lock(root, self.marker())
                self.assertEqual(b"sentinel", occupied.read_bytes())
                self.assertEqual((occupied,), tuple(root.iterdir()))
                self.assertEqual(
                    s1we.S1WE_ARTIFACT_ROLE_OCCUPIED,
                    raised.exception.code,
                )

    def test_success_is_atomic_and_preserves_durable_lock(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.temporary_root(parent)
            marker = self.marker()
            lock = s1we.write_s1we_synthetic_lock(root, marker)
            lock_before = lock.read_bytes()
            outcome = self.success(marker)
            terminal = s1we.publish_s1we_synthetic_terminal(root, outcome)
            names = {path.name for path in root.iterdir()}
            payload = json.loads(terminal.read_text(encoding="utf-8"))
            self.assertEqual(lock_before, lock.read_bytes())
        self.assertTrue(terminal.name.endswith(".success.json"))
        self.assertEqual(outcome.canonical_payload(), payload)
        self.assertEqual(
            {f"{EXECUTION_ID}.lock.json", f"{EXECUTION_ID}.success.json"},
            names,
        )

    def test_error_is_atomic_and_contains_no_result_roles(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.temporary_root(parent)
            marker = self.marker()
            s1we.write_s1we_synthetic_lock(root, marker)
            outcome = self.error(marker)
            terminal = s1we.publish_s1we_synthetic_terminal(root, outcome)
            payload = json.loads(terminal.read_text(encoding="utf-8"))
            names = {path.name for path in root.iterdir()}
        self.assertTrue(terminal.name.endswith(".error.json"))
        self.assertEqual("H4", payload["error_stage"])
        self.assertEqual("H3", payload["last_completed_stage"])
        self.assertNotIn("matrix_result_digest", payload)
        self.assertNotIn("composition_result_digest", payload)
        self.assertNotIn("evaluation_result_digest", payload)
        self.assertEqual(
            {f"{EXECUTION_ID}.lock.json", f"{EXECUTION_ID}.error.json"},
            names,
        )

    def test_terminal_requires_matching_untampered_lock(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.temporary_root(parent)
            marker = self.marker()
            outcome = self.success(marker)
            with self.assertRaises(s1we.S1WEValidationError) as missing:
                s1we.publish_s1we_synthetic_terminal(root, outcome)
            lock = s1we.write_s1we_synthetic_lock(root, marker)
            payload = json.loads(lock.read_text(encoding="utf-8"))
            payload["retry_permitted"] = True
            lock.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(s1we.S1WEValidationError) as changed:
                s1we.publish_s1we_synthetic_terminal(root, outcome)
        self.assertEqual(s1we.S1WE_LOCK_REQUIRED, missing.exception.code)
        self.assertEqual(s1we.S1WE_LOCK_MISMATCH, changed.exception.code)

    def test_success_and_error_are_mutually_exclusive(self) -> None:
        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = self.temporary_root(parent)
            marker = self.marker()
            s1we.write_s1we_synthetic_lock(root, marker)
            success = s1we.publish_s1we_synthetic_terminal(
                root, self.success(marker)
            )
            success_before = success.read_bytes()
            with self.assertRaises(s1we.S1WEValidationError) as raised:
                s1we.publish_s1we_synthetic_terminal(root, self.error(marker))
            self.assertEqual(success_before, success.read_bytes())
            self.assertFalse((root / f"{EXECUTION_ID}.error.json").exists())
            self.assertFalse((root / f"{EXECUTION_ID}.tmp").exists())
        self.assertEqual(s1we.S1WE_ARTIFACT_ROLE_OCCUPIED, raised.exception.code)

        with TemporaryDirectory(dir=gettempdir()) as parent:
            root = Path(parent)
            source = root / "source.tmp"
            target = root / "target.json"
            source.write_bytes(b"new")
            target.write_bytes(b"existing")
            with self.assertRaises(OSError):
                s1we._atomic_move_without_replace(source, target)
            self.assertEqual(b"new", source.read_bytes())
            self.assertEqual(b"existing", target.read_bytes())

    def test_wrong_workspace_and_production_roots_are_rejected(self) -> None:
        production = ROOT / "data" / "generated" / "ppb1" / "one_shot"
        with self.assertRaises(s1we.S1WEValidationError) as production_error:
            s1we.write_s1we_synthetic_lock(production, self.marker())
        self.assertEqual(
            s1we.S1WE_PRODUCTION_ROOT_BLOCKED,
            production_error.exception.code,
        )

        with TemporaryDirectory(dir=gettempdir()) as parent:
            wrong = Path(parent) / "wrong-name"
            wrong.mkdir()
            with self.assertRaises(s1we.S1WEValidationError) as wrong_error:
                s1we.write_s1we_synthetic_lock(wrong, self.marker())
        self.assertEqual(
            s1we.S1WE_INVALID_TEMPORARY_ROOT,
            wrong_error.exception.code,
        )

        with TemporaryDirectory(dir=ROOT) as parent:
            workspace = self.temporary_root(parent)
            with self.assertRaises(s1we.S1WEValidationError) as local_error:
                s1we.write_s1we_synthetic_lock(workspace, self.marker())
        self.assertEqual(
            s1we.S1WE_INVALID_TEMPORARY_ROOT,
            local_error.exception.code,
        )

    def test_invalid_synthetic_roles_fail_closed(self) -> None:
        with self.assertRaises(s1we.S1WEValidationError):
            s1we.build_s1we_synthetic_lock_marker(
                "production.case-001",
                digest("synthetic-authorization"),
                digest("synthetic-resource-gate"),
            )
        with self.assertRaises(s1we.S1WEValidationError):
            s1we.build_s1we_synthetic_lock_marker(
                EXECUTION_ID,
                "not-a-digest",
                digest("synthetic-resource-gate"),
            )
        with self.assertRaises(s1we.S1WEValidationError):
            s1we.build_s1we_synthetic_error_outcome(
                self.marker(),
                "H1",
                "INVALID_STAGE",
                digest("error-detail"),
                None,
            )

    def test_production_entry_and_runtime_dependencies_remain_blocked(self) -> None:
        with self.assertRaises(s1we.S1WEValidationError) as raised:
            s1we.execute_s1we_production_once()
        self.assertEqual(
            s1we.S1WE_PRODUCTION_EXECUTION_BLOCKED,
            raised.exception.code,
        )
        source = inspect.getsource(s1we)
        for forbidden in (
            "_execute_s1vq_corrected_matrix(",
            "execute_s1vq_corrected_matrix(",
            "run_s1vw_synthetic_once(",
            "S1WAProductionAuthorization(",
            "SharedMCMField",
            "ReceptorContactFrame",
            "datetime",
            "time.time",
        ):
            self.assertNotIn(forbidden, source)

    def test_bound_fields_match_the_static_contract_roles(self) -> None:
        self.assertEqual(
            {
                "execution_id",
                "authorization_digest",
                "resource_gate_digest",
                "source_digests",
                "authorization_consumed",
                "retry_permitted",
                "marker_digest",
            },
            {item.name for item in fields(s1we.S1WAProductionLockMarker)},
        )
        self.assertIn(
            "terminal_digest",
            {item.name for item in fields(s1we.S1WAProductionSuccessOutcome)},
        )
        self.assertIn(
            "terminal_digest",
            {item.name for item in fields(s1we.S1WAProductionErrorOutcome)},
        )

    def test_s1we_remains_private_and_snapshot_neutral(self) -> None:
        names = {
            "S1WAProductionLockMarker",
            "S1WAProductionSuccessOutcome",
            "S1WAProductionErrorOutcome",
            "write_s1we_synthetic_lock",
            "publish_s1we_synthetic_terminal",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
