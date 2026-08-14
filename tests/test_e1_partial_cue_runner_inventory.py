from __future__ import annotations

import inspect
from types import MappingProxyType
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e4_one_shot_execution import build_canonical_e1_e4_inputs
from mcm_field_organism.e1_partial_cue_contract import build_e1_partial_cue_contract
from mcm_field_organism.e1_partial_cue_execution import S1_CP_CUE_IDS
from mcm_field_organism.e1_partial_cue_runner_inventory import (
    E1PartialCueRunnerInventoryError,
    build_e1_partial_cue_runner_inventory,
)
from mcm_field_organism.e1_partial_cue_runners import (
    build_e1_partial_cue_runner_inputs,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)


class E1PartialCueRunnerInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.field, cls.state, cls.substrate, cls.afterimage = build_canonical_e1_e4_inputs()
        cls.contract = build_e1_partial_cue_contract()
        cls.inputs = build_e1_partial_cue_runner_inputs(
            cls.field, cls.state, cls.substrate, cls.afterimage
        )

    def build(self):
        return build_e1_partial_cue_runner_inventory(
            self.contract, self.field, self.inputs, self.substrate, self.afterimage
        )

    def expected_keys(self):
        return tuple(
            (model, history, cue)
            for model in self.contract.model_arms
            for history in self.contract.history_arms
            for cue in S1_CP_CUE_IDS
        )

    def test_inventory_is_complete_ordered_and_read_only(self) -> None:
        inventory, digest = self.build()
        self.assertIsInstance(inventory, MappingProxyType)
        self.assertEqual(self.expected_keys(), tuple(inventory))
        self.assertEqual(36, len(inventory))
        self.assertEqual(64, len(digest))
        with self.assertRaises(TypeError):
            inventory[("e1", "neutral", "left-partial")] = lambda: None

    def test_build_does_not_execute_any_cue_runner(self) -> None:
        module = "mcm_field_organism.e1_partial_cue_runner_inventory"
        with patch(f"{module}.run_e1_partial_cue_observation") as runner:
            inventory, _ = self.build()
        runner.assert_not_called()
        self.assertEqual(36, len(inventory))

    def test_one_selected_lazy_role_preserves_its_identity(self) -> None:
        inventory, _ = self.build()
        result = inventory[("e1", "left-g4", "left-partial")]()
        self.assertEqual("e1", result.model_id)
        self.assertEqual("left-g4", result.history_id)
        self.assertEqual("left-partial", result.cue_id)

    def test_inventory_digest_is_deterministic(self) -> None:
        self.assertEqual(self.build()[1], self.build()[1])
        self.assertEqual(
            "e91148ff48e289a7fcf6b3dbe8f8832a25907f496e24bc73fdce5950f0d34925",
            self.build()[1],
        )

    def test_changed_time_contract_is_rejected(self) -> None:
        with self.assertRaises(E1PartialCueRunnerInventoryError):
            build_e1_partial_cue_runner_inventory(
                self.contract,
                self.field,
                self.inputs,
                NeutralLocalFieldSubstrateConfig(2.0),
                self.afterimage,
            )
        with self.assertRaises(E1PartialCueRunnerInventoryError):
            build_e1_partial_cue_runner_inventory(
                self.contract,
                self.field,
                self.inputs,
                self.substrate,
                NeutralFastAfterimageConfig(1.0),
            )

    def test_builder_does_not_reference_composition_or_evaluation(self) -> None:
        source = inspect.getsource(build_e1_partial_cue_runner_inventory)
        self.assertNotIn("compose_e1_partial_cue_result", source)
        self.assertNotIn("evaluate_e1_partial_cue_result", source)

    def test_inventory_roles_remain_private(self) -> None:
        for role in (
            "E1PartialCueRunnerInventoryError",
            "build_e1_partial_cue_runner_inventory",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
