from __future__ import annotations

from dataclasses import replace
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_cue_amplitude_curve_contract import build_e1_cue_amplitude_curve_contract
from mcm_field_organism.e1_cue_amplitude_curve_execution import (
    E1CueAmplitudeCurveExecutionError,
    E1CueAmplitudeObservation,
    compose_e1_cue_amplitude_curve_result,
    evaluate_e1_cue_amplitude_curve_result,
    run_e1_cue_amplitude_observation,
)
from mcm_field_organism.e1_e4_one_shot_execution import build_canonical_e1_e4_inputs
from mcm_field_organism.e1_partial_cue_runners import build_e1_partial_cue_runner_inputs


def synthetic_observations(*, nonlinear: bool = False):
    contract = build_e1_cue_amplitude_curve_contract()
    result = {}
    full = contract.s1ct_full_interaction_linf
    for model in contract.model_arms:
        for history in contract.history_arms:
            for side in contract.cue_sides:
                for amplitude in contract.amplitudes:
                    matching = (history == "left-g4" and side == "left") or (history == "right-g4" and side == "right")
                    value = full * amplitude
                    if nonlinear and amplitude == 0.25:
                        value *= 1.5
                    effect = value if model == "e1" and matching else 0.0
                    s = (effect, 0.0, 0.0) if side == "left" else (0.0, 0.0, effect)
                    h = (0.0, 0.0, 0.0)
                    item = E1CueAmplitudeObservation(model, history, side, amplitude, s, h, s, h, True, True)
                    result[(model, history, side, amplitude)] = item
    return result


class E1CueAmplitudeCurveExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.field, cls.state, cls.substrate, cls.afterimage = build_canonical_e1_e4_inputs()
        cls.contract = build_e1_cue_amplitude_curve_contract()
        cls.inputs = build_e1_partial_cue_runner_inputs(cls.field, cls.state, cls.substrate, cls.afterimage)

    def observe(self, model: str, history: str, side: str, amplitude: float):
        return run_e1_cue_amplitude_observation(
            self.contract, self.field, self.inputs, model, history, side,
            amplitude, self.substrate, self.afterimage,
        )

    def test_isolated_smallest_e1_arm_is_measurable_and_refined(self) -> None:
        result = self.observe("e1", "left-g4", "left", 0.125)
        primary = result.delta_s + result.delta_h
        control = result.control_delta_s + result.control_delta_h
        scale = max(abs(value) for value in primary)
        residual = max(abs(a - b) for a, b in zip(primary, control, strict=True))
        self.assertGreater(scale, 1e-12)
        self.assertLessEqual(residual / scale, self.contract.relative_refinement_limit)

    def test_isolated_p0_zero_and_b1_history_independent(self) -> None:
        p0 = self.observe("p0", "neutral", "right", 0.5)
        self.assertEqual((0.0,) * 3, p0.delta_s)
        left = self.observe("b1-static-h8", "left-g4", "left", 0.5)
        right = self.observe("b1-static-h8", "right-g4", "left", 0.5)
        self.assertEqual(left.delta_s, right.delta_s)
        self.assertEqual(left.delta_h, right.delta_h)

    def test_synthetic_linear_curve_is_explained(self) -> None:
        result = compose_e1_cue_amplitude_curve_result(self.contract, synthetic_observations())
        self.assertEqual(72, len(result.observations))
        self.assertEqual(0.0, result.metrics.maximum_relative_linear_residual)
        self.assertEqual(
            "AMPLITUDE_CURVE_EXPLAINED_BY_LINEAR_SCALING",
            evaluate_e1_cue_amplitude_curve_result(self.contract, result),
        )
        self.assertFalse(hasattr(result, "decision"))

    def test_synthetic_nonlinear_curve_has_residual(self) -> None:
        result = compose_e1_cue_amplitude_curve_result(
            self.contract, synthetic_observations(nonlinear=True)
        )
        self.assertGreater(result.metrics.maximum_relative_linear_residual, 0.05)
        self.assertEqual(
            "NONLINEAR_HISTORY_INTERACTION_RESIDUAL",
            evaluate_e1_cue_amplitude_curve_result(self.contract, result),
        )

    def test_invalid_control_precedes_curve_decision(self) -> None:
        values = synthetic_observations()
        key = next(iter(values))
        values[key] = replace(values[key], invariants_hold=False)
        result = compose_e1_cue_amplitude_curve_result(self.contract, values)
        self.assertEqual("INVALID_S1_CU_RUN", evaluate_e1_cue_amplitude_curve_result(self.contract, result))

    def test_incomplete_matrix_and_unknown_amplitude_are_rejected(self) -> None:
        values = synthetic_observations()
        values.pop(next(iter(values)))
        with self.assertRaisesRegex(E1CueAmplitudeCurveExecutionError, "incomplete"):
            compose_e1_cue_amplitude_curve_result(self.contract, values)
        with self.assertRaises(E1CueAmplitudeCurveExecutionError):
            self.observe("e1", "left-g4", "left", 0.3)

    def test_roles_remain_private(self) -> None:
        for role in (
            "E1CueAmplitudeObservation",
            "E1CueAmplitudeCurveResult",
            "run_e1_cue_amplitude_observation",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
