from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    EvidenceLevel,
    FORBIDDEN_LOCAL_FIELD_EFFECT_ROLES,
    LocalFieldEffectAdmissibilityContractError,
    REQUIRED_LOCAL_FIELD_CONTROLS,
    REQUIRED_LOCAL_FIELD_INPUTS,
    REQUIRED_LOCAL_FIELD_INTERPRETATION_LIMITS,
    REQUIRED_LOCAL_FIELD_INVARIANTS,
    RuntimePermission,
    local_field_effect_admissibility_contract_public_roles,
    reference_local_field_effect_admissibility_contract,
)


class LocalFieldEffectAdmissibilityContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = reference_local_field_effect_admissibility_contract()

    def test_reference_contract_is_closed_reproducible_and_immutable(self) -> None:
        second = reference_local_field_effect_admissibility_contract()
        self.assertEqual(self.contract, second)
        self.assertEqual(self.contract.digest(), second.digest())
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, self.contract.permission)
        self.assertEqual(EvidenceLevel.E0, self.contract.evidence)
        self.assertFalse(self.contract.writes_back)
        with self.assertRaises(FrozenInstanceError):
            self.contract.writes_back = True  # type: ignore[misc]

    def test_only_current_contact_and_prior_local_field_are_allowed(self) -> None:
        self.assertTrue(
            REQUIRED_LOCAL_FIELD_INPUTS.issubset(self.contract.allowed_inputs)
        )
        self.assertEqual(
            REQUIRED_LOCAL_FIELD_INPUTS,
            frozenset(self.contract.allowed_inputs),
        )
        self.assertNotIn(
            "previous_self_state_feedback",
            self.contract.allowed_inputs,
        )

    def test_atomic_local_symmetry_invariants_are_required(self) -> None:
        self.assertTrue(
            REQUIRED_LOCAL_FIELD_INVARIANTS.issubset(
                self.contract.required_invariants
            )
        )
        for role in (
            "atomic_prior_tick_causality",
            "candidate_self_state_independence",
            "sample_order_invariance",
            "spatial_reflection_equivariance",
            "zero_source_quiescence",
        ):
            self.assertIn(role, self.contract.required_invariants)

    def test_controls_ablate_each_input_and_technical_order(self) -> None:
        self.assertTrue(
            REQUIRED_LOCAL_FIELD_CONTROLS.issubset(
                self.contract.required_controls
            )
        )
        for role in (
            "local_sample_ablation",
            "receptor_contact_ablation",
            "sample_iteration_permutation",
            "neuron_iteration_permutation",
            "geometry_reflection",
            "observer_removal",
        ):
            self.assertIn(role, self.contract.required_controls)

    def test_interpretation_stops_before_memory_or_development(self) -> None:
        self.assertTrue(
            REQUIRED_LOCAL_FIELD_INTERPRETATION_LIMITS.issubset(
                self.contract.interpretation_limits
            )
        )
        self.assertIn(
            "single_step_effect_is_not_memory",
            self.contract.interpretation_limits,
        )
        self.assertIn(
            "fixed_transition_is_baseline",
            self.contract.interpretation_limits,
        )

    def test_required_boundaries_cannot_be_removed(self) -> None:
        invalid_changes = (
            ("allowed_inputs", "prior_tick_local_field_samples"),
            ("required_invariants", "no_same_tick_recursion"),
            ("required_controls", "geometry_reflection"),
            ("interpretation_limits", "propagation_is_not_topology"),
            ("forbidden_roles", "history_carrier"),
        )
        for field_name, removed in invalid_changes:
            values = tuple(
                value
                for value in getattr(self.contract, field_name)
                if value != removed
            )
            with self.subTest(field_name=field_name), self.assertRaises(
                LocalFieldEffectAdmissibilityContractError
            ):
                replace(self.contract, **{field_name: values})

    def test_forbidden_roles_cannot_become_inputs_or_controls(self) -> None:
        for role in (
            "afterimage_update",
            "history_carrier",
            "modality_weight",
            "target_response",
        ):
            with self.subTest(role=role), self.assertRaises(
                LocalFieldEffectAdmissibilityContractError
            ):
                replace(
                    self.contract,
                    allowed_inputs=self.contract.allowed_inputs + (role,),
                )
            with self.subTest(role=role), self.assertRaises(
                LocalFieldEffectAdmissibilityContractError
            ):
                replace(
                    self.contract,
                    required_controls=self.contract.required_controls + (role,),
                )

    def test_permission_evidence_and_writeback_cannot_be_elevated(self) -> None:
        with self.assertRaises(LocalFieldEffectAdmissibilityContractError):
            replace(
                self.contract,
                permission=RuntimePermission.PASSIVE_AVAILABLE,
            )
        with self.assertRaises(LocalFieldEffectAdmissibilityContractError):
            replace(self.contract, evidence=EvidenceLevel.E1)
        with self.assertRaises(LocalFieldEffectAdmissibilityContractError):
            replace(self.contract, writes_back=True)

    def test_public_contract_contains_no_transition_parameters(self) -> None:
        forbidden_fields = {
            "coupling",
            "decay_rate",
            "threshold",
            "weight",
            "activation_equation",
            "afterimage_equation",
            "memory",
            "topology",
        }
        self.assertTrue(
            forbidden_fields.isdisjoint(
                local_field_effect_admissibility_contract_public_roles()
            )
        )
        self.assertIn(
            "previous_self_state_feedback",
            FORBIDDEN_LOCAL_FIELD_EFFECT_ROLES,
        )


if __name__ == "__main__":
    unittest.main()
