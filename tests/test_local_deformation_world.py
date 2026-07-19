from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    DEFORMATION_GROUP_IDS,
    DEFORMATION_HOLDOUT_POSITIONS,
    DEFORMATION_ORDER_VARIANTS,
    DEFORMATION_STAGE_IDS,
    FORBIDDEN_DEFORMATION_RUNTIME_ROLES,
    LocalDeformationWorldError,
    local_deformation_world_public_roles,
    receptor_contract_public_roles,
    run_local_deformation_world_probe,
)


class LocalDeformationWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_local_deformation_world_probe()

    def test_preregistered_matrix_is_complete(self) -> None:
        self.assertEqual(336, len(self.result.observations))
        self.assertEqual(
            "ecce078b165d20afc4424cbf7829212e67c29daf369f3558f892067be43f4a28",
            self.result.digest(),
        )
        self.assertTrue(self.result.groups_complete)
        self.assertTrue(self.result.stages_complete)
        self.assertTrue(self.result.orders_complete)
        self.assertTrue(self.result.holdouts_complete)
        self.assertEqual(
            set(DEFORMATION_GROUP_IDS),
            {item.group_id for item in self.result.observations},
        )
        self.assertEqual(
            set(DEFORMATION_STAGE_IDS),
            {item.stage_id for item in self.result.observations},
        )
        self.assertEqual(
            set(DEFORMATION_ORDER_VARIANTS),
            {item.order_variant for item in self.result.observations},
        )
        self.assertEqual(
            set(DEFORMATION_HOLDOUT_POSITIONS),
            {item.holdout_ingress for item in self.result.observations},
        )

    def test_forms_and_pairing_control_are_exact(self) -> None:
        self.assertTrue(self.result.forms_non_affine)
        self.assertTrue(self.result.d5_margins_preserved)
        self.assertTrue(self.result.d5_pairing_destroyed)
        self.assertTrue(
            all(
                not item.local_pairing_valid
                for item in self.result.observations
                if item.group_id == "g7"
            )
        )

    def test_every_branch_is_one_continuous_field_life(self) -> None:
        self.assertTrue(self.result.continuous_state_preserved)
        self.assertTrue(
            all(
                item.continuous_state
                and item.first_tick == 0
                and item.last_tick > item.completed_contacts
                for item in self.result.observations
            )
        )

    def test_world_metadata_does_not_enter_runtime_contracts(self) -> None:
        self.assertFalse(self.result.forbidden_metadata_reaches_runtime)
        receptor_roles = set().union(*map(set, receptor_contract_public_roles()))
        self.assertTrue(FORBIDDEN_DEFORMATION_RUNTIME_ROLES.isdisjoint(receptor_roles))

    def test_observer_is_passive_and_observations_are_immutable(self) -> None:
        observed = []
        repeated = run_local_deformation_world_probe(observer=observed.append)
        self.assertEqual(self.result, repeated)
        self.assertEqual(self.result.digest(), repeated.digest())
        self.assertEqual(len(repeated.observations), len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].group_id = "changed"  # type: ignore[misc]

    def test_result_cannot_release_runtime_behavior(self) -> None:
        for role in ("writes_back", "adds_memory_role", "changes_field_transition"):
            with self.assertRaises(LocalDeformationWorldError):
                replace(self.result, **{role: True})

    def test_public_roles_contain_no_raw_or_semantic_payload(self) -> None:
        forbidden = {
            "frame",
            "image",
            "pixels",
            "object",
            "meaning",
            "semantic_label",
            "memory_state",
            "topology",
            "reward",
            "interpolation_weight",
        }
        self.assertTrue(forbidden.isdisjoint(local_deformation_world_public_roles()))

    def test_invalid_group_selection_is_rejected(self) -> None:
        with self.assertRaises(LocalDeformationWorldError):
            run_local_deformation_world_probe(groups=("g0",))


if __name__ == "__main__":
    unittest.main()
