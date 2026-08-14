from __future__ import annotations

import copy
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_owner_authorization import (
    E1ConfirmationOwnerAuthorizationError,
    bind_e1_confirmation_owner_authorization,
)
from mcm_field_organism.e1_confirmation_release_contract import (
    prepare_e1_confirmation_release_contract,
)
from tests.test_e1_confirmation_release_contract import _inputs


REPORTS = Path("reports")
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


class E1ConfirmationOwnerAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        binding, chain, audit = _inputs()
        cls.contract = prepare_e1_confirmation_release_contract(
            binding, chain, audit
        )

    def test_receipt_binds_review_and_one_owner_authorization(self) -> None:
        receipt = bind_e1_confirmation_owner_authorization(self.contract)

        self.assertEqual("FREIGABE", receipt.independent_reviewer_decision)
        self.assertEqual(
            "AUTHORIZED_ONE_SHOT", receipt.project_owner_authorization
        )
        self.assertEqual(1, receipt.authorized_run_count)

    def test_receipt_preserves_resource_and_failure_envelope(self) -> None:
        receipt = bind_e1_confirmation_owner_authorization(self.contract)

        self.assertEqual(23_800, receipt.total_field_steps)
        self.assertEqual(1_800, receipt.max_wall_seconds)
        self.assertEqual(4 * 1024**3, receipt.max_peak_rss_bytes)
        self.assertTrue(receipt.no_retry_after_started_failure)

    def test_authorization_does_not_open_execution(self) -> None:
        receipt = bind_e1_confirmation_owner_authorization(self.contract)

        for role in (
            "resource_enforcement_bound",
            "same_session_preflight_complete",
            "execution_permitted",
            "persistence_permitted",
            "s1_ea6_rerun_permitted",
            "posthoc_tuning_permitted",
            "memory_or_ai_claim_permitted",
        ):
            self.assertFalse(getattr(receipt, role))

    def test_changed_release_draft_fails_closed(self) -> None:
        changed = copy.deepcopy(self.contract)
        object.__setattr__(changed, "execution_permitted", True)

        with self.assertRaises(E1ConfirmationOwnerAuthorizationError):
            bind_e1_confirmation_owner_authorization(changed)

    def test_receipt_is_repeatable_and_targets_stay_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = bind_e1_confirmation_owner_authorization(self.contract)
        second = bind_e1_confirmation_owner_authorization(self.contract)

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_receipt_has_no_runtime_or_writer_path(self) -> None:
        source = inspect.getsource(bind_e1_confirmation_owner_authorization)
        for forbidden in (
            "run_e1_asynchronous_field",
            "execute_e1_confirmation_canonical_once",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)

    def test_receipt_roles_remain_private(self) -> None:
        for role in (
            "E1ConfirmationOwnerAuthorization",
            "bind_e1_confirmation_owner_authorization",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
