from __future__ import annotations

import copy
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_one_shot_worker import (
    _prepare_worker_inputs,
)
from mcm_field_organism.e1_confirmation_released_worker_audit import (
    E1ConfirmationReleasedWorkerAuditError,
    S1_EB25_CANONICAL_WORKER_ORDER,
    S1_EB25_RELEASE_DIGESTS,
    audit_e1_confirmation_released_worker_contract,
    current_s1_eb25_release_digests,
)


TARGETS = (
    Path("reports/e1_refined_confirmation_s1eb_once_v1.json"),
    Path("reports/e1_refined_confirmation_s1eb_once_v1.attempt.json"),
    Path("reports/e1_refined_confirmation_s1eb_once_v1.lock"),
)


def _audit():
    inputs = _prepare_worker_inputs()
    return audit_e1_confirmation_released_worker_contract(*inputs)


class E1ConfirmationReleasedWorkerAuditTests(unittest.TestCase):
    def test_audit_binds_release_evidence_and_status(self) -> None:
        result = _audit()

        self.assertEqual(S1_EB25_RELEASE_DIGESTS, result.release_implementation_digests)
        self.assertTrue(result.static_contract_check_complete)
        self.assertTrue(result.owner_one_shot_authorized)
        self.assertTrue(result.resource_enforcement_bound)
        self.assertEqual(
            "RELEASE_CHAIN_BOUND_CANONICAL_WORKER_NOT_IMPLEMENTED",
            result.audit_status,
        )

    def test_audit_binds_exact_canonical_worker_order(self) -> None:
        result = _audit()

        self.assertEqual(S1_EB25_CANONICAL_WORKER_ORDER, result.canonical_worker_order)
        self.assertLess(
            result.canonical_worker_order.index(
                "require_fresh_e1_confirmation_preflight"
            ),
            result.canonical_worker_order.index("create_exclusive_lock_marker"),
        )
        self.assertLess(
            result.canonical_worker_order.index("create_exclusive_attempt_marker"),
            result.canonical_worker_order.index(
                "produce_e1_confirmation_canonical_formation"
            ),
        )

    def test_audit_keeps_worker_execution_and_claims_closed(self) -> None:
        result = _audit()

        self.assertTrue(result.canonical_worker_contract_bound)
        self.assertFalse(result.canonical_worker_implemented)
        for role in (
            "canonical_execution_permitted",
            "canonical_persistence_permitted",
            "retry_permitted",
            "claims_permitted",
        ):
            self.assertFalse(getattr(result, role))

    def test_changed_resource_guard_fails_closed(self) -> None:
        binding, chain, release, authorization, guard = _prepare_worker_inputs()
        changed = copy.deepcopy(guard)
        object.__setattr__(changed, "binding_digest", "0" * 64)

        with self.assertRaises(E1ConfirmationReleasedWorkerAuditError):
            audit_e1_confirmation_released_worker_contract(
                binding, chain, release, authorization, changed
            )

    def test_audit_is_repeatable_and_targets_stay_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = _audit()
        second = _audit()

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_audit_has_no_runtime_or_writer_path(self) -> None:
        source = inspect.getsource(
            audit_e1_confirmation_released_worker_contract
        )
        for forbidden in (
            "produce_e1_confirmation_canonical_formation",
            "run_e1_confirmation_canonical_seven_arm_probe",
            "compose_e1_confirmation_canonical_result",
            "execute_e1_confirmation_canonical_once",
            "run_guarded_synthetic_process",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)

    def test_digest_inventory_and_roles_remain_private(self) -> None:
        self.assertEqual(S1_EB25_RELEASE_DIGESTS, current_s1_eb25_release_digests())
        for role in (
            "E1ConfirmationReleasedWorkerAudit",
            "audit_e1_confirmation_released_worker_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
