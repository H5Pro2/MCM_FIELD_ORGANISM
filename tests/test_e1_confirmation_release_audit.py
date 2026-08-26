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
    E1ConfirmationReleaseAuditError,
    S1_EB17_IMPLEMENTATION_DIGESTS,
    S1_EB17_REQUIRED_RELEASE_ACTIONS,
    audit_e1_confirmation_release_readiness,
    current_s1_eb17_implementation_digests,
)


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _inputs():
    return (
        prepare_e1_confirmation_canonical_producer_binding(REPORTS, UPSTREAM),
        prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM),
    )


class E1ConfirmationReleaseAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.binding, cls.chain = _inputs()

    def test_audit_binds_all_s1eb9_through_s1eb16_roles(self) -> None:
        audit = audit_e1_confirmation_release_readiness(
            self.binding, self.chain
        )

        self.assertEqual(
            S1_EB17_IMPLEMENTATION_DIGESTS,
            audit.implementation_digests,
        )
        self.assertEqual(8, len(audit.bound_chain_roles))
        self.assertTrue(audit.technical_chain_complete)

    def test_audit_identifies_remaining_release_actions(self) -> None:
        audit = audit_e1_confirmation_release_readiness(
            self.binding, self.chain
        )

        self.assertEqual(
            S1_EB17_REQUIRED_RELEASE_ACTIONS,
            audit.required_release_actions,
        )
        self.assertEqual(
            "TECHNICALLY_BOUND_AWAITING_EXPLICIT_RESEARCH_RELEASE",
            audit.audit_status,
        )
        self.assertFalse(audit.research_release_complete)

    def test_all_execution_and_claim_gates_remain_closed(self) -> None:
        audit = audit_e1_confirmation_release_readiness(
            self.binding, self.chain
        )

        for role in (
            "execution_permitted",
            "persistence_permitted",
            "retry_permitted",
            "claims_permitted",
        ):
            self.assertFalse(getattr(audit, role))

    def test_changed_binding_gate_fails_closed(self) -> None:
        changed = copy.deepcopy(self.binding)
        object.__setattr__(changed, "execution_permitted", True)

        with self.assertRaises(E1ConfirmationReleaseAuditError):
            audit_e1_confirmation_release_readiness(changed, self.chain)

    def test_audit_is_repeatable_and_targets_stay_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = audit_e1_confirmation_release_readiness(
            self.binding, self.chain
        )
        second = audit_e1_confirmation_release_readiness(
            self.binding, self.chain
        )

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_audit_has_no_runtime_result_or_writer_path(self) -> None:
        source = inspect.getsource(audit_e1_confirmation_release_readiness)
        for forbidden in (
            "run_e1_asynchronous_field",
            "produce_e1_confirmation_canonical_formation",
            "run_e1_confirmation_canonical_seven_arm_probe",
            "compose_e1_confirmation_canonical_result",
            "execute_e1_confirmation_canonical_once",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_audit_digest_inventory_and_roles_remain_private(self) -> None:
        self.assertEqual(
            S1_EB17_IMPLEMENTATION_DIGESTS,
            current_s1_eb17_implementation_digests(),
        )
        for role in (
            "E1ConfirmationReleaseAudit",
            "audit_e1_confirmation_release_readiness",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
