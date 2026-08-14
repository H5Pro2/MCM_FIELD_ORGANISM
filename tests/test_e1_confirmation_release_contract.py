from __future__ import annotations

import copy
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_producer_binding import (
    prepare_e1_confirmation_canonical_producer_binding,
)
from mcm_field_organism.e1_confirmation_chain_contract import (
    prepare_e1_confirmation_chain_contract,
)
from mcm_field_organism.e1_confirmation_release_audit import (
    audit_e1_confirmation_release_readiness,
)
from mcm_field_organism.e1_confirmation_release_contract import (
    E1ConfirmationReleaseContractError,
    S1_EB19_MAX_PEAK_RSS_BYTES,
    S1_EB19_MAX_WALL_SECONDS,
    S1_EB19_RELEASE_REQUIREMENTS,
    S1_EB19_TOTAL_FIELD_STEPS,
    prepare_e1_confirmation_release_contract,
)


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _inputs():
    binding = prepare_e1_confirmation_canonical_producer_binding(
        REPORTS, UPSTREAM
    )
    chain = prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)
    audit = audit_e1_confirmation_release_readiness(binding, chain)
    return binding, chain, audit


class E1ConfirmationReleaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.binding, cls.chain, cls.audit = _inputs()

    def test_contract_binds_fixed_resource_envelope(self) -> None:
        contract = prepare_e1_confirmation_release_contract(
            self.binding, self.chain, self.audit
        )

        self.assertEqual(S1_EB19_TOTAL_FIELD_STEPS, contract.total_field_steps)
        self.assertEqual(S1_EB19_MAX_WALL_SECONDS, contract.max_wall_seconds)
        self.assertEqual(
            S1_EB19_MAX_PEAK_RSS_BYTES, contract.max_peak_rss_bytes
        )

    def test_contract_lists_all_release_requirements_as_pending(self) -> None:
        contract = prepare_e1_confirmation_release_contract(
            self.binding, self.chain, self.audit
        )

        self.assertEqual(
            S1_EB19_RELEASE_REQUIREMENTS, contract.release_requirements
        )
        self.assertEqual("PENDING", contract.independent_reviewer_decision)
        self.assertEqual("PENDING", contract.project_owner_authorization)
        self.assertFalse(contract.same_session_preflight_complete)
        self.assertFalse(contract.resource_enforcement_bound)

    def test_no_retry_rerun_tuning_or_claim_is_opened(self) -> None:
        contract = prepare_e1_confirmation_release_contract(
            self.binding, self.chain, self.audit
        )

        self.assertTrue(contract.no_retry_after_started_failure)
        for role in (
            "s1_ea6_rerun_permitted",
            "posthoc_tuning_permitted",
            "execution_permitted",
            "persistence_permitted",
            "claims_permitted",
        ):
            self.assertFalse(getattr(contract, role))

    def test_changed_upstream_gate_fails_closed(self) -> None:
        changed = copy.deepcopy(self.audit)
        object.__setattr__(changed, "execution_permitted", True)

        with self.assertRaises(E1ConfirmationReleaseContractError):
            prepare_e1_confirmation_release_contract(
                self.binding, self.chain, changed
            )

    def test_contract_is_repeatable_and_targets_remain_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = prepare_e1_confirmation_release_contract(
            self.binding, self.chain, self.audit
        )
        second = prepare_e1_confirmation_release_contract(
            self.binding, self.chain, self.audit
        )

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_contract_has_no_runtime_or_writer_path(self) -> None:
        source = inspect.getsource(prepare_e1_confirmation_release_contract)
        for forbidden in (
            "run_e1_asynchronous_field",
            "execute_e1_confirmation_canonical_once",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)

    def test_contract_roles_remain_private(self) -> None:
        for role in (
            "E1ConfirmationReleaseContract",
            "prepare_e1_confirmation_release_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
