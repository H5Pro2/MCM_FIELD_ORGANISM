from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    EvidenceLevel,
    FORBIDDEN_REGULATION_ROLES,
    REQUIRED_REGULATION_BASELINES,
    REQUIRED_REGULATION_CAUSES,
    REQUIRED_REGULATION_EFFECTS,
    REQUIRED_REGULATION_PROPERTIES,
    RuntimePermission,
    SensorySelfRegulationContractError,
    reference_sensory_self_regulation_contract,
    sensory_self_regulation_contract_public_roles,
)


class SensorySelfRegulationContractTests(unittest.TestCase):
    def test_reference_contract_is_closed_reproducible_and_immutable(self) -> None:
        first = reference_sensory_self_regulation_contract()
        second = reference_sensory_self_regulation_contract()
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(RuntimePermission.CONTRACT_ONLY, first.permission)
        self.assertEqual(EvidenceLevel.E0, first.evidence)
        self.assertFalse(first.writes_back)
        with self.assertRaises(FrozenInstanceError):
            first.writes_back = True  # type: ignore[misc]

    def test_contract_requires_local_history_resource_and_recovery(self) -> None:
        contract = reference_sensory_self_regulation_contract()
        self.assertTrue(
            REQUIRED_REGULATION_CAUSES.issubset(contract.accepted_causes)
        )
        self.assertTrue(
            REQUIRED_REGULATION_EFFECTS.issubset(contract.observable_effects)
        )
        self.assertIn("reduced_world_contact", contract.accepted_causes)
        self.assertIn(
            "recovery_toward_prior_range",
            contract.observable_effects,
        )

    def test_contract_requires_organic_properties_and_simple_baselines(self) -> None:
        contract = reference_sensory_self_regulation_contract()
        self.assertTrue(
            REQUIRED_REGULATION_PROPERTIES.issubset(
                contract.required_properties
            )
        )
        self.assertTrue(
            REQUIRED_REGULATION_BASELINES.issubset(contract.required_baselines)
        )
        for role in (
            "device_independence",
            "reversible_adaptation",
            "recovery_without_replay",
            "baseline_separation",
        ):
            self.assertIn(role, contract.required_properties)

    def test_contract_cannot_be_weakened(self) -> None:
        contract = reference_sensory_self_regulation_contract()
        invalid = (
            {
                "accepted_causes": tuple(
                    value
                    for value in contract.accepted_causes
                    if value != "local_available_resource"
                )
            },
            {
                "observable_effects": tuple(
                    value
                    for value in contract.observable_effects
                    if value != "changed_later_local_receptor_intake"
                )
            },
            {
                "required_properties": tuple(
                    value
                    for value in contract.required_properties
                    if value != "device_independence"
                )
            },
            {
                "required_baselines": tuple(
                    value
                    for value in contract.required_baselines
                    if value != "automatic_gain_control"
                )
            },
            {
                "forbidden_roles": tuple(
                    value
                    for value in contract.forbidden_roles
                    if value != "target_loudness"
                )
            },
        )
        for changes in invalid:
            with self.subTest(changes=changes), self.assertRaises(
                SensorySelfRegulationContractError
            ):
                replace(contract, **changes)

    def test_device_and_controller_roles_cannot_become_causes_or_effects(
        self,
    ) -> None:
        contract = reference_sensory_self_regulation_contract()
        for role in (
            "device_volume",
            "automatic_gain_control",
            "global_controller",
            "semantic_label",
        ):
            with self.subTest(role=role), self.assertRaises(
                SensorySelfRegulationContractError
            ):
                replace(
                    contract,
                    accepted_causes=contract.accepted_causes + (role,),
                )
            with self.subTest(role=role), self.assertRaises(
                SensorySelfRegulationContractError
            ):
                replace(
                    contract,
                    observable_effects=contract.observable_effects + (role,),
                )

    def test_contract_contains_no_gain_value_or_update_equation(self) -> None:
        roles = set(sensory_self_regulation_contract_public_roles())
        forbidden_fields = {
            "gain",
            "volume",
            "sensitivity",
            "learning_rate",
            "adaptation_rate",
            "decay",
            "threshold",
            "target",
            "setpoint",
            "value",
        }
        self.assertTrue(forbidden_fields.isdisjoint(roles))
        self.assertTrue(
            {
                "device_volume",
                "target_loudness",
                "global_controller",
                "fixed_adaptation_rate",
            }.issubset(FORBIDDEN_REGULATION_ROLES)
        )

    def test_runtime_permission_and_evidence_cannot_be_elevated(self) -> None:
        contract = reference_sensory_self_regulation_contract()
        with self.assertRaises(SensorySelfRegulationContractError):
            replace(contract, permission=RuntimePermission.PASSIVE_AVAILABLE)
        with self.assertRaises(SensorySelfRegulationContractError):
            replace(contract, evidence=EvidenceLevel.E1)
        with self.assertRaises(SensorySelfRegulationContractError):
            replace(contract, writes_back=True)


if __name__ == "__main__":
    unittest.main()
