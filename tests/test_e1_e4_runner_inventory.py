from __future__ import annotations

import inspect
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e4_execution import (
    E1_E4_EXECUTION_MODEL_IDS,
    preflight_e1_e4_runners,
)
from mcm_field_organism.e1_e4_runner_inventory import (
    E1E4RunnerInventoryError,
    build_e1_e4_runner_inventory,
)
from mcm_field_organism.e1_local_edge_plasticity import (
    E1EdgeBinding,
    E1LocalEdgePlasticityState,
    build_neutral_e1_state,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_coupled_fast_field import contract
from tests.test_neutral_fast_afterimage import shared_field


class E1E4RunnerInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.field = shared_field()
        self.state = build_neutral_e1_state(self.field.layer, contract())
        self.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage = NeutralFastAfterimageConfig(0.5)

    def build(self):
        return build_e1_e4_runner_inventory(
            self.field, self.state, self.substrate, self.afterimage
        )

    def test_inventory_is_complete_ordered_and_preflight_valid(self) -> None:
        inventory, anchors, digest = self.build()
        self.assertEqual(E1_E4_EXECUTION_MODEL_IDS, tuple(inventory))
        self.assertEqual(9, len(preflight_e1_e4_runners(inventory)))
        self.assertTrue(callable(anchors))
        self.assertEqual(64, len(digest))

    def test_build_does_not_execute_any_model_runner(self) -> None:
        module = "mcm_field_organism.e1_e4_runner_inventory"
        with (
            patch(f"{module}.run_e1_e4_e1_b0_b1_models") as e1,
            patch(f"{module}.run_e1_e4_s2_b2_model") as s2,
            patch(f"{module}.build_e1_e4_oracle_g_run") as oracle,
        ):
            inventory, anchors, digest = self.build()
        e1.assert_not_called()
        s2.assert_not_called()
        oracle.assert_not_called()
        self.assertEqual(E1_E4_EXECUTION_MODEL_IDS, tuple(inventory))
        self.assertTrue(callable(anchors))
        self.assertEqual(64, len(digest))

    def test_inventory_is_read_only(self) -> None:
        inventory, _, _ = self.build()
        with self.assertRaises(TypeError):
            inventory["e1"] = inventory["b0"]

    def test_inventory_digest_is_deterministic(self) -> None:
        first = self.build()[2]
        second = self.build()[2]
        self.assertEqual(first, second)
        self.assertEqual(
            "e76d4154ed6e9d68a68b770c2df26012e63ca1abc02149b7c29b8b2a0c1c25c1",
            first,
        )

    def test_builder_does_not_reference_composition_or_evaluation(self) -> None:
        source = inspect.getsource(build_e1_e4_runner_inventory)
        self.assertNotIn("compose_e1_e4_run_result", source)
        self.assertNotIn("evaluate_e1_e4_run", source)

    def test_changed_config_and_non_neutral_e1_are_rejected(self) -> None:
        with self.assertRaises(E1E4RunnerInventoryError):
            build_e1_e4_runner_inventory(
                self.field,
                self.state,
                NeutralLocalFieldSubstrateConfig(2.0),
                self.afterimage,
            )
        first, second = self.state.edge_bindings
        non_neutral = E1LocalEdgePlasticityState(
            self.state.contract,
            (
                E1EdgeBinding(
                    first.first_neuron_id, first.second_neuron_id, 0.1
                ),
                second,
            ),
            self.state.edge_inventory_digest,
        )
        with self.assertRaises(E1E4RunnerInventoryError):
            build_e1_e4_runner_inventory(
                self.field,
                non_neutral,
                self.substrate,
                self.afterimage,
            )

    def test_inputs_remain_fresh_and_unchanged(self) -> None:
        layer_digest = self.field.layer.digest()
        bindings = self.state.edge_bindings
        self.build()
        self.assertEqual(layer_digest, self.field.layer.digest())
        self.assertEqual(bindings, self.state.edge_bindings)
        self.assertEqual(0, self.field.layer.tick)
        self.assertIsNone(self.field.last_distribution)

    def test_inventory_roles_remain_private(self) -> None:
        for role in (
            "build_e1_e4_runner_inventory",
            "E1E4RunnerInventoryError",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
