from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from types import SimpleNamespace
import unittest

from mcm_field_organism.w7ak_cap_p0_raw_contrast_compositor import (
    W7AKResidualSample,
)
from mcm_field_organism.w7an_r124_resolution_container import (
    W7ANR124ResolutionContainer,
)
from mcm_field_organism.w7ao_resolution_comparison_contract import (
    build_w7ao_resolution_comparison_contract,
)
from mcm_field_organism.w7ap_raw_resolution_distance_compositor import (
    compose_w7ap_raw_resolution_distances,
)
from mcm_field_organism.w7aq_numerical_evaluation_contract import (
    build_w7aq_numerical_evaluation_contract,
)
from mcm_field_organism.w7ar_numerical_resolution_evaluator import (
    W7ARNumericalResolutionEvaluationError,
    evaluate_w7ar_numerical_resolution,
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _sample(tick: int, value: float) -> W7AKResidualSample:
    s_values = (value, value + 1.0)
    h_values = (value + 2.0, value + 3.0)
    payload = {
        "tick": tick,
        "s_residuals": s_values,
        "h_residuals": h_values,
    }
    return W7AKResidualSample(tick, s_values, h_values, _digest(payload))


def _composition(offsets=(0.0, 1.0, 1.25)):
    container = object.__new__(W7ANR124ResolutionContainer)
    roles = tuple(
        (path_id, checkpoint)
        for path_id in ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
        for checkpoint in range(5)
    )
    resolutions = []
    for resolution_id, offset in zip(("r1", "r2", "r4"), offsets, strict=True):
        pairs = tuple(
            SimpleNamespace(
                path_id=path_id,
                checkpoint=checkpoint,
                plan_checkpoint_digest=f"plan-{path_id}-{checkpoint}",
                observation_ticks=(10, 20),
                residual_samples=(
                    _sample(10, offset + checkpoint),
                    _sample(20, offset + checkpoint + 0.5),
                ),
            )
            for path_id, checkpoint in roles
        )
        resolutions.append(
            SimpleNamespace(
                resolution_id=resolution_id,
                evaluated=False,
                pair_container=SimpleNamespace(pairs=pairs, evaluated=False),
            )
        )
    object.__setattr__(container, "resolutions", tuple(resolutions))
    object.__setattr__(container, "convergence_compared", False)
    object.__setattr__(container, "effect_floor_ready", False)
    object.__setattr__(
        container,
        "resolution_container_digest",
        "4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5",
    )
    return compose_w7ap_raw_resolution_distances(
        container,
        build_w7ao_resolution_comparison_contract(),
    )


class W7ARNumericalResolutionEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_w7aq_numerical_evaluation_contract()
        cls.composition = _composition()
        cls.result = evaluate_w7ar_numerical_resolution(
            cls.composition,
            cls.contract,
        )

    def test_all_70_component_checks_are_bound_in_role_order(self):
        self.assertEqual(70, len(self.result.component_checks))
        self.assertEqual(
            ("ab", 0, "S_linf"),
            (
                self.result.component_checks[0].path_id,
                self.result.component_checks[0].checkpoint,
                self.result.component_checks[0].metric,
            ),
        )

    def test_converged_input_builds_preregistered_floors(self):
        self.assertTrue(self.result.all_components_converged)
        self.assertEqual(0.25, self.result.epsilon_num)
        self.assertEqual(2.5, self.result.effect_floor)
        self.assertEqual(
            "RESOLUTION_COMPARISON_CONVERGED",
            self.result.outcome,
        )

    def test_nonconvergence_exposes_no_floor(self):
        result = evaluate_w7ar_numerical_resolution(
            _composition((0.0, 1.0, 3.0)),
            self.contract,
        )
        self.assertFalse(result.all_components_converged)
        self.assertIsNone(result.epsilon_num)
        self.assertIsNone(result.effect_floor)
        self.assertEqual("NUMERICALLY_UNRESOLVED", result.outcome)

    def test_exact_double_zero_is_the_only_equality_exception(self):
        result = evaluate_w7ar_numerical_resolution(
            _composition((0.0, 0.0, 0.0)),
            self.contract,
        )
        self.assertTrue(result.all_components_converged)
        self.assertEqual(0.0, result.epsilon_num)
        self.assertTrue(
            all(item.exact_zero_exception for item in result.component_checks)
        )

    def test_evaluation_is_deterministic_and_does_not_mutate_input(self):
        input_digest = self.composition.raw_resolution_distance_composition_digest
        repeat = evaluate_w7ar_numerical_resolution(
            self.composition,
            self.contract,
        )
        self.assertEqual(
            self.result.evaluation_result_digest,
            repeat.evaluation_result_digest,
        )
        self.assertEqual(
            input_digest,
            self.composition.raw_resolution_distance_composition_digest,
        )

    def test_all_functional_claims_remain_locked(self):
        self.assertFalse(self.result.field_function_decision_allowed)
        self.assertFalse(self.result.memory_claim_allowed)

    def test_tampered_result_is_rejected(self):
        with self.assertRaises(W7ARNumericalResolutionEvaluationError):
            replace(self.result, effect_floor=1.0)

    def test_evaluator_is_not_publicly_exported(self):
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "evaluate_w7ar_numerical_resolution")
        )


if __name__ == "__main__":
    unittest.main()
