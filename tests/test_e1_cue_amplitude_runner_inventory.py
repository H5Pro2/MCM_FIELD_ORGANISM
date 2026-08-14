from __future__ import annotations

import inspect
from types import MappingProxyType
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_cue_amplitude_curve_contract import build_e1_cue_amplitude_curve_contract
from mcm_field_organism.e1_cue_amplitude_runner_inventory import (
    E1CueAmplitudeRunnerInventoryError,
    build_e1_cue_amplitude_runner_inventory,
)
from mcm_field_organism.e1_e4_one_shot_execution import build_canonical_e1_e4_inputs
from mcm_field_organism.e1_partial_cue_runners import build_e1_partial_cue_runner_inputs
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)


class E1CueAmplitudeRunnerInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.field, cls.state, cls.substrate, cls.afterimage = build_canonical_e1_e4_inputs()
        cls.contract = build_e1_cue_amplitude_curve_contract()
        cls.inputs = build_e1_partial_cue_runner_inputs(cls.field, cls.state, cls.substrate, cls.afterimage)

    def build(self):
        return build_e1_cue_amplitude_runner_inventory(
            self.contract, self.field, self.inputs, self.substrate, self.afterimage
        )

    def expected_keys(self):
        return tuple(
            (model, history, side, amplitude)
            for model in self.contract.model_arms
            for history in self.contract.history_arms
            for side in self.contract.cue_sides
            for amplitude in self.contract.amplitudes
        )

    def test_inventory_is_complete_ordered_and_read_only(self) -> None:
        inventory, digest = self.build()
        self.assertIsInstance(inventory, MappingProxyType)
        self.assertEqual(self.expected_keys(), tuple(inventory))
        self.assertEqual(72, len(inventory))
        self.assertEqual(64, len(digest))
        with self.assertRaises(TypeError):
            inventory[("e1", "neutral", "left", 0.125)] = lambda: None

    def test_build_does_not_execute_any_amplitude_runner(self) -> None:
        module = "mcm_field_organism.e1_cue_amplitude_runner_inventory"
        with patch(f"{module}.run_e1_cue_amplitude_observation") as runner:
            inventory, _ = self.build()
        runner.assert_not_called()
        self.assertEqual(72, len(inventory))

    def test_one_lazy_role_preserves_identity(self) -> None:
        inventory, _ = self.build()
        result = inventory[("e1", "left-g4", "left", 0.125)]()
        self.assertEqual(("e1", "left-g4", "left", 0.125), (
            result.model_id, result.history_id, result.cue_side, result.amplitude
        ))

    def test_inventory_digest_is_deterministic(self) -> None:
        self.assertEqual(self.build()[1], self.build()[1])
        self.assertEqual(
            "d3a40cbf9e76bffb6ccab1a1a2a3facedef8ad8af7f0f2198bc876e7ef276cd9",
            self.build()[1],
        )

    def test_changed_time_contract_is_rejected(self) -> None:
        with self.assertRaises(E1CueAmplitudeRunnerInventoryError):
            build_e1_cue_amplitude_runner_inventory(
                self.contract, self.field, self.inputs,
                NeutralLocalFieldSubstrateConfig(2.0), self.afterimage,
            )
        with self.assertRaises(E1CueAmplitudeRunnerInventoryError):
            build_e1_cue_amplitude_runner_inventory(
                self.contract, self.field, self.inputs, self.substrate,
                NeutralFastAfterimageConfig(1.0),
            )

    def test_builder_has_no_composition_or_evaluation_reference(self) -> None:
        source = inspect.getsource(build_e1_cue_amplitude_runner_inventory)
        self.assertNotIn("compose_e1_cue_amplitude_curve_result", source)
        self.assertNotIn("evaluate_e1_cue_amplitude_curve_result", source)

    def test_inventory_roles_remain_private(self) -> None:
        for role in (
            "E1CueAmplitudeRunnerInventoryError",
            "build_e1_cue_amplitude_runner_inventory",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
