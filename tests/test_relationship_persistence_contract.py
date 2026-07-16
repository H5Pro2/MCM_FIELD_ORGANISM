from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    EvidenceLevel,
    FORBIDDEN_PERSISTENCE_ROLES,
    REQUIRED_CAUSES,
    REQUIRED_EFFECTS,
    REQUIRED_PROPERTIES,
    RelationshipPersistenceContractError,
    RuntimePermission,
    reference_relationship_persistence_contract,
    relationship_persistence_contract_public_roles,
)


class RelationshipPersistenceContractTests(unittest.TestCase):
    def test_reference_contract_is_closed_reproducible_and_immutable(self) -> None:
        first = reference_relationship_persistence_contract()
        second = reference_relationship_persistence_contract()
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, first.permission)
        self.assertEqual(EvidenceLevel.E0, first.evidence)
        self.assertFalse(first.writes_back)
        with self.assertRaises(FrozenInstanceError):
            first.writes_back = True  # type: ignore[misc]

    def test_contract_requires_local_causes_and_later_causal_effects(self) -> None:
        contract = reference_relationship_persistence_contract()
        self.assertTrue(REQUIRED_CAUSES.issubset(contract.accepted_causes))
        self.assertTrue(REQUIRED_EFFECTS.issubset(contract.observable_effects))
        self.assertIn("changed_later_local_field_intake", contract.observable_effects)
        self.assertNotIn("stored_value", contract.observable_effects)

    def test_contract_requires_dissolution_rebinding_and_open_representation(self) -> None:
        contract = reference_relationship_persistence_contract()
        self.assertTrue(REQUIRED_PROPERTIES.issubset(contract.required_properties))
        for role in (
            "reversible_weakening",
            "complete_dissolution",
            "local_rebinding",
            "representation_open",
        ):
            self.assertIn(role, contract.required_properties)

    def test_contract_cannot_be_weakened_by_removing_required_roles(self) -> None:
        contract = reference_relationship_persistence_contract()
        invalid = (
            {"accepted_causes": tuple(value for value in contract.accepted_causes if value != "local_available_resource")},
            {"observable_effects": tuple(value for value in contract.observable_effects if value != "complete_functional_loss")},
            {"required_properties": tuple(value for value in contract.required_properties if value != "complete_dissolution")},
            {"forbidden_roles": tuple(value for value in contract.forbidden_roles if value != "object_template")},
        )
        for changes in invalid:
            with self.subTest(changes=changes), self.assertRaises(RelationshipPersistenceContractError):
                replace(contract, **changes)

    def test_forbidden_payload_cannot_become_a_cause_or_effect(self) -> None:
        contract = reference_relationship_persistence_contract()
        for role in ("raw_image", "object_template", "vector_embedding", "semantic_label"):
            with self.subTest(role=role), self.assertRaises(RelationshipPersistenceContractError):
                replace(contract, accepted_causes=contract.accepted_causes + (role,))
            with self.subTest(role=role), self.assertRaises(RelationshipPersistenceContractError):
                replace(contract, observable_effects=contract.observable_effects + (role,))

    def test_contract_contains_no_update_equation_or_semantic_storage_field(self) -> None:
        roles = set(relationship_persistence_contract_public_roles())
        forbidden_fields = {
            "weight", "learning_rate", "decay", "threshold", "similarity",
            "embedding", "pattern_id", "object_id", "label", "word", "syntax",
            "payload", "value", "memory_slot", "target",
        }
        self.assertTrue(forbidden_fields.isdisjoint(roles))
        self.assertTrue({
            "raw_image", "object_template", "word_token", "syntax_class",
            "permanent_edge", "monotonic_accumulator",
        }.issubset(FORBIDDEN_PERSISTENCE_ROLES))

    def test_runtime_permission_and_evidence_cannot_be_elevated(self) -> None:
        contract = reference_relationship_persistence_contract()
        with self.assertRaises(RelationshipPersistenceContractError):
            replace(contract, permission=RuntimePermission.PASSIVE_AVAILABLE)
        with self.assertRaises(RelationshipPersistenceContractError):
            replace(contract, evidence=EvidenceLevel.E1)
        with self.assertRaises(RelationshipPersistenceContractError):
            replace(contract, writes_back=True)


if __name__ == "__main__":
    unittest.main()
