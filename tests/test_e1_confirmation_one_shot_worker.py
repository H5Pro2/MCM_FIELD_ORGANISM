from __future__ import annotations

import copy
import inspect
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_one_shot_worker import (
    E1ConfirmationOneShotWorkerError,
    S1_EB24_MARKER_NAME,
    _prepare_worker_inputs,
    _run_synthetic_worker_in_child,
    run_guarded_synthetic_e1_confirmation_worker,
)


REPORTS = Path("reports")
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


class E1ConfirmationOneShotWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        *_, cls.guard = _prepare_worker_inputs()

    def test_guarded_worker_consumes_preflight_before_synthetic_marker(self):
        with TemporaryDirectory() as directory:
            receipt = run_guarded_synthetic_e1_confirmation_worker(
                self.guard, Path(directory)
            )

            self.assertEqual(
                "SYNTHETIC_ORCHESTRATION_COMPLETE", receipt.worker_status
            )
            self.assertNotEqual(os.getpid(), receipt.process_id)
            self.assertLessEqual(
                receipt.preflight_age_at_marker_ns, 5_000_000_000
            )
            self.assertEqual(1, receipt.work_invocation_count)
            self.assertFalse(receipt.canonical_execution_permitted)
            self.assertFalse(receipt.claims_permitted)

    def test_marker_binds_child_preflight_and_exactly_once(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            receipt = run_guarded_synthetic_e1_confirmation_worker(
                self.guard, root
            )
            marker = json.loads(
                (root / S1_EB24_MARKER_NAME).read_text(encoding="ascii")
            )

            self.assertEqual(receipt.preflight_digest, marker["preflight_digest"])
            self.assertEqual(receipt.process_id, marker["process_id"])
            with self.assertRaises(E1ConfirmationOneShotWorkerError):
                run_guarded_synthetic_e1_confirmation_worker(self.guard, root)

    def test_child_order_is_preflight_require_then_marker(self) -> None:
        source = inspect.getsource(_run_synthetic_worker_in_child)

        prepared = source.index("prepare_e1_confirmation_same_session_preflight(")
        required = source.index("require_fresh_e1_confirmation_preflight(")
        marker = source.index("_exclusive_synthetic_marker(")
        self.assertLess(prepared, required)
        self.assertLess(required, marker)

    def test_changed_resource_guard_fails_before_process_start(self) -> None:
        changed = copy.deepcopy(self.guard)
        object.__setattr__(changed, "binding_digest", "0" * 64)

        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                E1ConfirmationOneShotWorkerError, "unchanged closed"
            ):
                run_guarded_synthetic_e1_confirmation_worker(
                    changed, Path(directory)
                )
            self.assertEqual((), tuple(Path(directory).iterdir()))

    def test_registered_directory_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationOneShotWorkerError, "outside reports"
        ):
            run_guarded_synthetic_e1_confirmation_worker(
                self.guard, REPORTS
            )

    def test_canonical_targets_stay_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        with TemporaryDirectory() as directory:
            run_guarded_synthetic_e1_confirmation_worker(
                self.guard, Path(directory)
            )

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_worker_has_no_canonical_runtime_or_public_api(self) -> None:
        source = inspect.getsource(run_guarded_synthetic_e1_confirmation_worker)
        for forbidden in (
            "produce_e1_confirmation_canonical_formation",
            "run_e1_asynchronous_field",
            "execute_e1_confirmation_canonical_once",
            "_atomic_publish",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1ConfirmationOneShotWorkerReceipt",
            "run_guarded_synthetic_e1_confirmation_worker",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
