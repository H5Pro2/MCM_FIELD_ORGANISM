from __future__ import annotations

import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e4_one_shot_execution import build_canonical_e1_e4_inputs
from mcm_field_organism.e1_partial_cue_contract import build_e1_partial_cue_contract
from mcm_field_organism.e1_partial_cue_runners import (
    E1PartialCueRunnerError,
    build_e1_partial_cue_runner_inputs,
    run_e1_partial_cue_observation,
)


class E1PartialCueRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.field, cls.state, cls.substrate, cls.afterimage = build_canonical_e1_e4_inputs()
        cls.contract = build_e1_partial_cue_contract()
        cls.inputs = build_e1_partial_cue_runner_inputs(
            cls.field, cls.state, cls.substrate, cls.afterimage
        )

    def observe(self, model: str, history: str, cue: str):
        return run_e1_partial_cue_observation(
            self.contract,
            self.field,
            self.inputs,
            model,
            history,
            cue,
            self.substrate,
            self.afterimage,
        )

    def test_p0_is_exact_zero_for_partial_and_full_cues(self) -> None:
        for cue in ("left-partial", "right-full"):
            result = self.observe("p0", "neutral", cue)
            self.assertEqual((0.0, 0.0, 0.0), result.delta_s)
            self.assertEqual((0.0, 0.0, 0.0), result.delta_h)
            self.assertEqual(result.delta_s, result.control_delta_s)
            self.assertEqual(result.delta_h, result.control_delta_h)

    def test_e1_partial_cue_is_measurable_and_state_stays_frozen(self) -> None:
        bindings = self.inputs.world_arms.left_g4_state.edge_bindings
        result = self.observe("e1", "left-g4", "left-partial")
        self.assertGreater(max(abs(value) for value in result.delta_s + result.delta_h), 1e-12)
        self.assertEqual(bindings, self.inputs.world_arms.left_g4_state.edge_bindings)
        self.assertTrue(result.schedule_matches)
        self.assertTrue(result.invariants_hold)

    def test_static_b1_is_history_independent_for_identical_cue(self) -> None:
        left = self.observe("b1-static-h8", "left-g4", "left-partial")
        right = self.observe("b1-static-h8", "right-g4", "left-partial")
        neutral = self.observe("b1-static-h8", "neutral", "left-partial")
        self.assertEqual(left.delta_s, right.delta_s)
        self.assertEqual(left.delta_h, right.delta_h)
        self.assertEqual(left.delta_s, neutral.delta_s)
        self.assertEqual(left.delta_h, neutral.delta_h)

    def test_n2_n4_refinement_is_below_registered_limit(self) -> None:
        result = self.observe("e1", "right-g4", "right-full")
        primary = result.delta_s + result.delta_h
        control = result.control_delta_s + result.control_delta_h
        scale = max(abs(value) for value in primary)
        residual = max(abs(a - b) for a, b in zip(primary, control, strict=True))
        self.assertLessEqual(residual / scale, self.contract.relative_refinement_limit)

    def test_mirrored_e1_arms_produce_mirrored_observations(self) -> None:
        left = self.observe("e1", "left-g4", "left-partial")
        right = self.observe("e1", "right-g4", "right-partial")
        for first, second in ((left.delta_s, right.delta_s), (left.delta_h, right.delta_h)):
            self.assertTrue(
                all(abs(a - b) <= 1e-12 for a, b in zip(first, reversed(second), strict=True))
            )

    def test_inputs_and_initial_field_remain_unchanged(self) -> None:
        layer_digest = self.field.layer.digest()
        arms = self.inputs.world_arms
        self.observe("e1", "neutral", "right-partial")
        self.assertEqual(layer_digest, self.field.layer.digest())
        self.assertEqual(0, self.field.layer.tick)
        self.assertIsNone(self.field.last_distribution)
        self.assertIs(arms, self.inputs.world_arms)

    def test_unknown_arm_is_rejected(self) -> None:
        with self.assertRaises(E1PartialCueRunnerError):
            self.observe("unknown", "neutral", "left-partial")

    def test_runner_roles_remain_private(self) -> None:
        for role in (
            "E1PartialCueRunnerInputs",
            "build_e1_partial_cue_runner_inputs",
            "run_e1_partial_cue_observation",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
