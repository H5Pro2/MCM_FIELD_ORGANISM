from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_worker import (
    E1ConfirmationCanonicalWorkerError,
    E1ConfirmationSyntheticKernelSet,
    S1_EB26_SYNTHETIC_ATTEMPT,
    S1_EB26_SYNTHETIC_LOCK,
    S1_EB26_SYNTHETIC_REPORT,
    S1_EB26_SYNTHETIC_STAGE_ORDER,
    _execute_e1_confirmation_worker_synthetically,
    execute_e1_confirmation_canonical_worker_once,
)
from mcm_field_organism.e1_confirmation_one_shot_worker import (
    _prepare_worker_inputs,
)
from mcm_field_organism.e1_confirmation_released_worker_audit import (
    audit_e1_confirmation_released_worker_contract,
)


TARGETS = (
    Path("reports/e1_refined_confirmation_s1eb_once_v1.json"),
    Path("reports/e1_refined_confirmation_s1eb_once_v1.attempt.json"),
    Path("reports/e1_refined_confirmation_s1eb_once_v1.lock"),
)


def _kernel_set(calls: list[str], fail_at: str | None = None):
    def kernel(role: str):
        def run(previous: str) -> str:
            calls.append(role)
            if role == fail_at:
                raise RuntimeError("synthetic failure")
            return hashlib.sha256(f"{role}:{previous}".encode("ascii")).hexdigest()

        return run

    return E1ConfirmationSyntheticKernelSet(
        **{role: kernel(role) for role in S1_EB26_SYNTHETIC_STAGE_ORDER}
    )


class E1ConfirmationCanonicalWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = _prepare_worker_inputs()
        cls.audit = audit_e1_confirmation_released_worker_contract(*cls.inputs)

    def _run(self, directory: Path, kernels):
        return _execute_e1_confirmation_worker_synthetically(
            *self.inputs, self.audit, kernels, directory
        )

    def test_synthetic_kernels_follow_the_bound_order(self) -> None:
        calls = []
        with TemporaryDirectory() as directory:
            receipt = self._run(Path(directory), _kernel_set(calls))

        self.assertEqual(S1_EB26_SYNTHETIC_STAGE_ORDER, tuple(calls))
        self.assertEqual(
            S1_EB26_SYNTHETIC_STAGE_ORDER,
            tuple(role for role, _ in receipt.stage_digests),
        )
        self.assertFalse(receipt.canonical_execution_permitted)

    def test_success_publishes_then_removes_attempt_and_lock(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            receipt = self._run(root, _kernel_set([]))
            report = root / S1_EB26_SYNTHETIC_REPORT
            payload = json.loads(report.read_text(encoding="ascii"))

            self.assertTrue(report.is_file())
            self.assertEqual(receipt.report_sha256, hashlib.sha256(report.read_bytes()).hexdigest())
            self.assertTrue(payload["synthetic_only"])
            self.assertFalse((root / S1_EB26_SYNTHETIC_ATTEMPT).exists())
            self.assertFalse((root / S1_EB26_SYNTHETIC_LOCK).exists())

    def test_failure_retains_attempt_and_forbids_retry(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
                self._run(root, _kernel_set([], fail_at="probe_r2_r4_r8"))

            self.assertTrue((root / S1_EB26_SYNTHETIC_ATTEMPT).is_file())
            self.assertFalse((root / S1_EB26_SYNTHETIC_REPORT).exists())
            self.assertFalse((root / S1_EB26_SYNTHETIC_LOCK).exists())
            with self.assertRaisesRegex(
                E1ConfirmationCanonicalWorkerError, "already used"
            ):
                self._run(root, _kernel_set([]))

    def test_preflight_precedes_first_marker_in_worker_source(self) -> None:
        source = inspect.getsource(_execute_e1_confirmation_worker_synthetically)

        prepared = source.index("prepare_e1_confirmation_same_session_preflight(")
        required = source.index("require_fresh_e1_confirmation_preflight(")
        marker = source.index("_exclusive_marker(")
        self.assertLess(prepared, required)
        self.assertLess(required, marker)

    def test_changed_audit_fails_before_any_marker(self) -> None:
        changed = copy.deepcopy(self.audit)
        object.__setattr__(changed, "audit_digest", "0" * 64)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(E1ConfirmationCanonicalWorkerError):
                _execute_e1_confirmation_worker_synthetically(
                    *self.inputs, changed, _kernel_set([]), root
                )
            self.assertEqual((), tuple(root.iterdir()))

    def test_registered_directory_and_canonical_entry_remain_locked(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationCanonicalWorkerError, "outside reports"
        ):
            self._run(Path("reports"), _kernel_set([]))
        with self.assertRaisesRegex(
            E1ConfirmationCanonicalWorkerError, "remains locked"
        ):
            execute_e1_confirmation_canonical_worker_once(
                *self.inputs, self.audit
            )

    def test_synthetic_worker_never_touches_canonical_targets(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        with TemporaryDirectory() as directory:
            self._run(Path(directory), _kernel_set([]))

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_canonical_runtime_calls_and_worker_roles_stay_closed(self) -> None:
        source = inspect.getsource(execute_e1_confirmation_canonical_worker_once)
        for forbidden in (
            "produce_e1_confirmation_canonical_formation",
            "run_e1_confirmation_canonical_seven_arm_probe",
            "compose_e1_confirmation_canonical_result",
            "_atomic_publish",
            "_exclusive_marker",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1ConfirmationSyntheticKernelSet",
            "execute_e1_confirmation_canonical_worker_once",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
