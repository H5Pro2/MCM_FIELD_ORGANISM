from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism.receptor_process_contract import (
    FORBIDDEN_RECEPTOR_PROCESS_ROLES,
    REQUIRED_RECEPTOR_PROCESS_CAUSES,
    REQUIRED_RECEPTOR_PROCESS_OBSERVATIONS,
    REQUIRED_RECEPTOR_PROCESS_PROPERTIES,
    ReceptorProcessContractError,
    receptor_process_contract_public_roles,
    reference_receptor_process_contract,
)
from mcm_field_organism import EvidenceLevel, RuntimePermission


class ReceptorProcessContractTests(unittest.TestCase):
    def test_reference_contract_is_closed_reproducible_and_immutable(self) -> None:
        first = reference_receptor_process_contract()
        second = reference_receptor_process_contract()
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, first.permission)
        self.assertEqual(EvidenceLevel.E0, first.evidence)
        self.assertFalse(first.writes_back)
        with self.assertRaises(FrozenInstanceError):
            first.writes_back = True  # type: ignore[misc]

    def test_contract_allows_stateful_and_stateless_local_processes(self) -> None:
        contract = reference_receptor_process_contract()
        self.assertTrue(
            REQUIRED_RECEPTOR_PROCESS_PROPERTIES.issubset(
                contract.required_properties
            )
        )
        self.assertIn("finite_process_state", contract.required_properties)
        self.assertIn(
            "explicit_statelessness_allowed", contract.required_properties
        )
        self.assertIn("process_specific_dynamics", contract.required_properties)

    def test_contract_requires_causal_source_progress_and_history_loss(self) -> None:
        contract = reference_receptor_process_contract()
        self.assertTrue(
            REQUIRED_RECEPTOR_PROCESS_CAUSES.issubset(contract.accepted_causes)
        )
        self.assertTrue(
            REQUIRED_RECEPTOR_PROCESS_OBSERVATIONS.issubset(
                contract.required_observations
            )
        )
        self.assertIn(
            "finite_history_loss_for_stateful_process",
            contract.required_observations,
        )

    def test_required_boundaries_cannot_be_removed(self) -> None:
        contract = reference_receptor_process_contract()
        invalid = (
            {
                "accepted_causes": tuple(
                    value
                    for value in contract.accepted_causes
                    if value != "new_local_source_contact"
                )
            },
            {
                "required_observations": tuple(
                    value
                    for value in contract.required_observations
                    if value != "absence_without_contact_inference"
                )
            },
            {
                "required_properties": tuple(
                    value
                    for value in contract.required_properties
                    if value != "no_implicit_hold"
                )
            },
            {
                "forbidden_roles": tuple(
                    value
                    for value in contract.forbidden_roles
                    if value != "sample_and_hold"
                )
            },
        )
        for change in invalid:
            with self.subTest(change=change), self.assertRaises(
                ReceptorProcessContractError
            ):
                replace(contract, **change)

    def test_forbidden_dynamics_cannot_become_causes_or_observations(self) -> None:
        contract = reference_receptor_process_contract()
        for role in (
            "sample_and_hold",
            "forced_shared_dynamics",
            "modality_weight",
            "field_feedback",
        ):
            with self.subTest(role=role), self.assertRaises(
                ReceptorProcessContractError
            ):
                replace(contract, accepted_causes=contract.accepted_causes + (role,))
            with self.subTest(role=role), self.assertRaises(
                ReceptorProcessContractError
            ):
                replace(
                    contract,
                    required_observations=contract.required_observations + (role,),
                )

    def test_public_contract_contains_no_transition_parameters(self) -> None:
        forbidden_fields = {
            "window_size",
            "hop_size",
            "decay_rate",
            "valid_until",
            "held_value",
            "modality_weight",
            "field_activation",
            "memory",
            "meaning",
        }
        self.assertTrue(
            forbidden_fields.isdisjoint(receptor_process_contract_public_roles())
        )
        self.assertTrue(
            {
                "shared_window_size",
                "shared_decay_rate",
                "last_value_buffer",
                "invented_contact_duration",
            }.issubset(FORBIDDEN_RECEPTOR_PROCESS_ROLES)
        )

    def test_runtime_permission_evidence_and_writeback_cannot_be_elevated(self) -> None:
        contract = reference_receptor_process_contract()
        with self.assertRaises(ReceptorProcessContractError):
            replace(contract, permission=RuntimePermission.PASSIVE_AVAILABLE)
        with self.assertRaises(ReceptorProcessContractError):
            replace(contract, evidence=EvidenceLevel.E1)
        with self.assertRaises(ReceptorProcessContractError):
            replace(contract, writes_back=True)


if __name__ == "__main__":
    unittest.main()
