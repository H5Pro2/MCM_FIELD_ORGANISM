from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    CONTINUOUS_WORLD_CONTROL_IDS,
    CONTINUOUS_WORLD_EXPERIENCE_LEVELS,
    CONTINUOUS_WORLD_ORDER_VARIANTS,
    FORBIDDEN_CONTINUOUS_WORLD_RUNTIME_ROLES,
    HOLDOUT_INGRESS_SIGNS,
    SWITCH_CONTACT_COUNTS,
    ContinuousTwoRelationWorldError,
    continuous_two_relation_world_public_roles,
    receptor_contract_public_roles,
    run_continuous_two_relation_world_probe,
)


class ContinuousTwoRelationWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_continuous_two_relation_world_probe()

    def test_full_preregistered_world_matrix_is_present(self) -> None:
        self.assertEqual(768, len(self.result.observations))
        self.assertEqual(
            "77ad7eeefd173f3d51c679009ad598c9d03ff4f756cbf883943aaecbbce03945",
            self.result.digest(),
        )
        self.assertTrue(self.result.controls_complete)
        self.assertTrue(self.result.experience_levels_complete)
        self.assertTrue(self.result.switch_positions_complete)
        self.assertTrue(self.result.orders_complete)
        self.assertTrue(self.result.holdout_sides_complete)
        self.assertEqual(
            set(CONTINUOUS_WORLD_CONTROL_IDS),
            {item.control_id for item in self.result.observations},
        )
        self.assertEqual(
            set(CONTINUOUS_WORLD_EXPERIENCE_LEVELS),
            {
                item.experience_count
                for item in self.result.observations
                if item.control_id == "k3"
            },
        )
        self.assertEqual(
            set(SWITCH_CONTACT_COUNTS),
            {item.switch_contact_count for item in self.result.observations},
        )
        self.assertEqual(
            set(CONTINUOUS_WORLD_ORDER_VARIANTS),
            {item.order_variant for item in self.result.observations},
        )
        self.assertEqual(
            set(HOLDOUT_INGRESS_SIGNS),
            {item.holdout_ingress for item in self.result.observations},
        )

    def test_world_relations_and_permuted_control_are_separated(self) -> None:
        self.assertTrue(self.result.r0_relation_exact)
        self.assertTrue(self.result.r1_relation_exact)
        self.assertTrue(self.result.k4_pairing_destroyed)

    def test_zero_experience_controls_are_exact(self) -> None:
        self.assertTrue(self.result.k2_has_no_new_experience)
        self.assertTrue(self.result.k6_has_no_return_experience)
        self.assertTrue(
            all(
                item.experience_count == 0
                for item in self.result.observations
                if item.control_id == "k2"
            )
        )
        self.assertTrue(
            all(
                item.return_experience_count == 0
                for item in self.result.observations
                if item.control_id == "k6"
            )
        )

    def test_every_branch_uses_one_continuous_field_life(self) -> None:
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
        self.assertTrue(
            FORBIDDEN_CONTINUOUS_WORLD_RUNTIME_ROLES.isdisjoint(receptor_roles)
        )

    def test_observer_is_passive_and_observations_are_immutable(self) -> None:
        observed = []
        repeated = run_continuous_two_relation_world_probe(observer=observed.append)
        self.assertEqual(self.result, repeated)
        self.assertEqual(self.result.digest(), repeated.digest())
        self.assertTrue(repeated.observer_is_neutral)
        self.assertEqual(len(repeated.observations), len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].control_id = "changed"  # type: ignore[misc]

    def test_result_cannot_release_runtime_behavior(self) -> None:
        for role in ("writes_back", "adds_memory_role", "changes_field_transition"):
            with self.assertRaises(ContinuousTwoRelationWorldError):
                replace(self.result, **{role: True})

    def test_public_roles_contain_no_raw_world_or_semantic_payload(self) -> None:
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
            "hidden_position",
        }
        self.assertTrue(forbidden.isdisjoint(continuous_two_relation_world_public_roles()))

    def test_invalid_control_order_is_rejected(self) -> None:
        with self.assertRaises(ContinuousTwoRelationWorldError):
            run_continuous_two_relation_world_probe(controls=("k0",))


if __name__ == "__main__":
    unittest.main()
