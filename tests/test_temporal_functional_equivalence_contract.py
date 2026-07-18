from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    EvidenceLevel,
    FORBIDDEN_FUNCTIONAL_EQUIVALENCE_ROLES,
    REQUIRED_CONTROLS,
    REQUIRED_DISTINCTION_RULES,
    REQUIRED_EQUIVALENCE_RULES,
    REQUIRED_EQUIVALENCE_SCOPE,
    RuntimePermission,
    TemporalFunctionalEquivalenceContractError,
    reference_temporal_functional_equivalence_contract,
    temporal_functional_equivalence_contract_public_roles,
)


class TemporalFunctionalEquivalenceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = reference_temporal_functional_equivalence_contract()

    def test_reference_contract_is_closed_reproducible_and_immutable(self) -> None:
        second = reference_temporal_functional_equivalence_contract()
        self.assertEqual(self.contract, second)
        self.assertEqual(self.contract.digest(), second.digest())
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, self.contract.permission)
        self.assertEqual(EvidenceLevel.E0, self.contract.evidence)
        self.assertFalse(self.contract.writes_back)
        with self.assertRaises(FrozenInstanceError):
            self.contract.writes_back = True  # type: ignore[misc]

    def test_equivalence_is_relative_and_does_not_require_history_identity(self) -> None:
        self.assertTrue(
            REQUIRED_EQUIVALENCE_SCOPE.issubset(
                self.contract.equivalence_scope
            )
        )
        self.assertTrue(
            REQUIRED_EQUIVALENCE_RULES.issubset(
                self.contract.equivalence_rules
            )
        )
        self.assertIn(
            "history_identity_not_required",
            self.contract.equivalence_rules,
        )
        self.assertIn(
            "registered_probe_family_only",
            self.contract.equivalence_scope,
        )

    def test_distinction_requires_causal_swap_and_neutralization(self) -> None:
        self.assertTrue(
            REQUIRED_DISTINCTION_RULES.issubset(
                self.contract.distinction_rules
            )
        )
        self.assertIn(
            "difference_follows_carrier_swap",
            self.contract.distinction_rules,
        )
        self.assertIn(
            "difference_vanishes_on_carrier_neutralization",
            self.contract.distinction_rules,
        )

    def test_controls_match_present_and_remove_observer(self) -> None:
        self.assertTrue(
            REQUIRED_CONTROLS.issubset(self.contract.required_controls)
        )
        self.assertIn(
            "matched_fast_neuron_state",
            self.contract.required_controls,
        )
        self.assertIn("observer_removal", self.contract.required_controls)

    def test_required_boundaries_cannot_be_removed(self) -> None:
        invalid_changes = (
            ("equivalence_scope", "matched_external_present"),
            ("equivalence_rules", "equivalence_is_probe_relative"),
            ("distinction_rules", "difference_follows_carrier_swap"),
            ("required_controls", "candidate_carrier_isolation"),
            ("forbidden_roles", "history_template"),
        )
        for field_name, removed in invalid_changes:
            values = tuple(
                value
                for value in getattr(self.contract, field_name)
                if value != removed
            )
            with self.subTest(field_name=field_name), self.assertRaises(
                TemporalFunctionalEquivalenceContractError
            ):
                replace(self.contract, **{field_name: values})

    def test_forbidden_roles_cannot_be_required(self) -> None:
        for role in (
            "history_template",
            "target_response",
            "branch_specific_reader",
            "runtime_field_writeback",
        ):
            with self.subTest(role=role), self.assertRaises(
                TemporalFunctionalEquivalenceContractError
            ):
                replace(
                    self.contract,
                    required_controls=self.contract.required_controls + (role,),
                )

    def test_permission_evidence_and_writeback_cannot_be_elevated(self) -> None:
        with self.assertRaises(TemporalFunctionalEquivalenceContractError):
            replace(
                self.contract,
                permission=RuntimePermission.PASSIVE_AVAILABLE,
            )
        with self.assertRaises(TemporalFunctionalEquivalenceContractError):
            replace(self.contract, evidence=EvidenceLevel.E1)
        with self.assertRaises(TemporalFunctionalEquivalenceContractError):
            replace(self.contract, writes_back=True)

    def test_public_contract_contains_no_effect_parameters(self) -> None:
        forbidden_fields = {
            "history_window",
            "decay_rate",
            "effect_weight",
            "activation",
            "afterimage",
            "memory",
            "topology",
            "meaning",
        }
        self.assertTrue(
            forbidden_fields.isdisjoint(
                temporal_functional_equivalence_contract_public_roles()
            )
        )
        self.assertIn(
            "selected_representation",
            FORBIDDEN_FUNCTIONAL_EQUIVALENCE_ROLES,
        )


if __name__ == "__main__":
    unittest.main()
