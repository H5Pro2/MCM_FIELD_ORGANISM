from __future__ import annotations

from dataclasses import replace
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e4_one_shot_execution import build_canonical_e1_e4_inputs
from mcm_field_organism.e1_partial_cue_contract import build_e1_partial_cue_contract
from mcm_field_organism.e1_partial_cue_execution import (
    E1PartialCueExecutionError,
    E1PartialCueObservation,
    build_e1_partial_cue_world_arms,
    compose_e1_partial_cue_result,
    evaluate_e1_partial_cue_result,
)


def observations(*, e1_scale: float = 1.0, b1_scale: float = 0.0):
    contract = build_e1_partial_cue_contract()
    result = {}
    for model in contract.model_arms:
        for history in contract.history_arms:
            for cue in ("left-full", "right-full", "left-partial", "right-partial"):
                side = cue.split("-", 1)[0]
                level = cue.split("-", 1)[1]
                matching = (history == "left-g4" and side == "left") or (
                    history == "right-g4" and side == "right"
                )
                if model == "e1":
                    amplitude = e1_scale * (2.0 if level == "full" else 1.0) * (1.0 if matching else 0.0)
                elif model == "b1-static-h8":
                    amplitude = b1_scale * (2.0 if level == "full" else 1.0)
                else:
                    amplitude = 0.0
                s = (amplitude, 0.0, 0.0) if side == "left" else (0.0, 0.0, amplitude)
                h = tuple(0.5 * value for value in s)
                item = E1PartialCueObservation(
                    model, history, cue, s, h, s, h, True, True
                )
                result[(model, history, cue)] = item
    return result


class E1PartialCueExecutionTests(unittest.TestCase):
    def test_world_arms_build_mirrored_g4_states_without_cue(self) -> None:
        field, state, substrate, afterimage = build_canonical_e1_e4_inputs()
        original = state.edge_bindings
        arms = build_e1_partial_cue_world_arms(field, state, substrate, afterimage)

        left = tuple(item.binding for item in arms.left_g4_state.edge_bindings)
        right = tuple(item.binding for item in arms.right_g4_state.edge_bindings)
        self.assertNotEqual(left, tuple(item.binding for item in arms.neutral_state.edge_bindings))
        self.assertTrue(
            all(abs(a - b) <= 1e-12 for a, b in zip(left, reversed(right), strict=True))
        )
        self.assertLessEqual(arms.maximum_mirror_binding_error, 1e-12)
        self.assertEqual(original, state.edge_bindings)
        self.assertEqual(0, field.layer.tick)

    def test_complete_synthetic_matrix_builds_metrics_without_decision_field(self) -> None:
        contract = build_e1_partial_cue_contract()
        result = compose_e1_partial_cue_result(contract, observations())
        self.assertEqual(36, len(result.observations))
        self.assertGreater(result.metrics.partial_history_cue_interaction_linf, 0.0)
        self.assertGreater(result.metrics.partial_full_direction_dot, 0.0)
        self.assertFalse(hasattr(result, "decision"))
        self.assertFalse(hasattr(result, "memory"))

    def test_synthetic_history_specific_effect_uses_external_decision(self) -> None:
        contract = build_e1_partial_cue_contract()
        result = compose_e1_partial_cue_result(contract, observations())
        self.assertEqual(
            "HISTORY_SPECIFIC_PARTIAL_CUE_EFFECT",
            evaluate_e1_partial_cue_result(contract, result),
        )

    def test_zero_effect_and_invalid_control_take_precedence(self) -> None:
        contract = build_e1_partial_cue_contract()
        zero = compose_e1_partial_cue_result(contract, observations(e1_scale=0.0))
        self.assertEqual(
            "NO_MEASURABLE_PARTIAL_CUE_EFFECT",
            evaluate_e1_partial_cue_result(contract, zero),
        )
        changed = observations()
        key = ("e1", "left-g4", "left-partial")
        changed[key] = replace(changed[key], invariants_hold=False)
        invalid = compose_e1_partial_cue_result(contract, changed)
        self.assertEqual("INVALID_S1_CO_RUN", evaluate_e1_partial_cue_result(contract, invalid))

    def test_incomplete_or_mismatched_matrix_is_rejected(self) -> None:
        contract = build_e1_partial_cue_contract()
        changed = observations()
        changed.pop(("p0", "neutral", "right-partial"))
        with self.assertRaisesRegex(E1PartialCueExecutionError, "incomplete"):
            compose_e1_partial_cue_result(contract, changed)

    def test_nonfinite_observation_is_rejected(self) -> None:
        with self.assertRaises(E1PartialCueExecutionError):
            E1PartialCueObservation(
                "e1", "left-g4", "left-partial", (float("nan"), 0.0, 0.0),
                (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), True, True
            )

    def test_execution_roles_remain_private(self) -> None:
        for role in (
            "E1PartialCueObservation",
            "E1PartialCueRunResult",
            "compose_e1_partial_cue_result",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
