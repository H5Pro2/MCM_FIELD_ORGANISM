from __future__ import annotations

import copy
import math
import unittest

import numpy as np

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e3_state_arms import (
    E1_E3_RELEASE_TIMES_SECONDS,
    E1E3StateArmsError,
    build_e1_e3_state_arms,
    evaluate_e1_e3_state_arms,
    produce_e1_uniform_release_checkpoints,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.e1_mirrored_history import produce_e1_mirrored_histories
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_coupled_fast_field import contract
from tests.test_neutral_fast_afterimage import shared_field, with_fast_state


class E1E3StateArmsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.field = shared_field()
        cls.initial_state = build_neutral_e1_state(cls.field.layer, contract())
        cls.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        cls.afterimage = NeutralFastAfterimageConfig(0.5)
        cls.history = produce_e1_mirrored_histories(
            cls.field,
            cls.initial_state,
            cls.substrate,
            cls.afterimage,
        )
        cls.result = build_e1_e3_state_arms(
            cls.field,
            cls.history.left_e1_state,
            cls.substrate,
            cls.afterimage,
        )

    def test_release_times_and_analytic_curve_are_exact(self) -> None:
        checkpoints = self.result.release_checkpoints
        self.assertEqual(
            E1_E3_RELEASE_TIMES_SECONDS,
            tuple(item.elapsed_seconds for item in checkpoints),
        )
        self.assertLessEqual(self.result.metrics.release_analytic_linf, 1e-12)
        initial = np.asarray(
            [item.binding for item in checkpoints[0].state.edge_bindings]
        )
        for item in checkpoints:
            expected = initial * math.exp(-0.25 * item.elapsed_seconds)
            np.testing.assert_allclose(
                [edge.binding for edge in item.state.edge_bindings],
                expected,
                rtol=0.0,
                atol=1e-12,
            )

    def test_release_is_monotone_without_new_binding(self) -> None:
        totals = [
            sum(edge.binding for edge in item.state.edge_bindings)
            for item in self.result.release_checkpoints
        ]
        self.assertTrue(all(second < first for first, second in zip(totals, totals[1:])))
        self.assertGreater(self.result.metrics.release_total_binding_drop, 0.0)

    def test_resource_budget_is_preserved(self) -> None:
        self.assertLessEqual(self.result.metrics.resource_budget_linf, 1e-12)

    def test_competing_history_rebinds_resource(self) -> None:
        m = self.result.metrics
        self.assertGreater(m.compete_release_binding_linf, 1e-12)
        self.assertGreater(m.compete_total_binding_rebound, 1e-12)

    def test_neutral_baseline_is_separate_from_reused_state(self) -> None:
        self.assertGreater(self.result.metrics.compete_neutral_binding_linf, 1e-12)
        self.assertIsNot(self.result.compete_state, self.result.neutral_state)
        self.assertIsNot(self.result.compete_field, self.result.neutral_field)

    def test_state_arm_readiness_is_not_a_final_e3_decision(self) -> None:
        self.assertEqual(
            "E3_STATE_ARMS_READY_FOR_PROBE",
            evaluate_e1_e3_state_arms(self.result),
        )
        roles = set(self.result.__dataclass_fields__) | set(
            self.result.metrics.__dataclass_fields__
        )
        self.assertTrue({"memory", "forgetting", "success", "meaning"}.isdisjoint(roles))

    def test_inputs_remain_unchanged_and_arms_are_separate(self) -> None:
        field_digest = self.field.layer.digest()
        state = copy.deepcopy(self.history.left_e1_state)
        build_e1_e3_state_arms(
            self.field, state, self.substrate, self.afterimage
        )
        self.assertEqual(field_digest, self.field.layer.digest())
        self.assertEqual(state, self.history.left_e1_state)
        self.assertIsNot(self.result.hold_state, self.history.left_e1_state)

    def test_nonuniform_release_field_is_rejected(self) -> None:
        nonuniform = with_fast_state(self.field, (0.0, 0.1, 0.0), (0.0,) * 3)
        with self.assertRaises(E1E3StateArmsError):
            produce_e1_uniform_release_checkpoints(
                nonuniform, self.history.left_e1_state
            )

    def test_advanced_field_is_rejected_as_fresh_competing_input(self) -> None:
        with self.assertRaises(E1E3StateArmsError):
            build_e1_e3_state_arms(
                self.history.left_field,
                self.history.left_e1_state,
                self.substrate,
                self.afterimage,
            )

    def test_state_arm_roles_are_not_publicly_exported(self) -> None:
        for role in (
            "E1E3StateArmsResult",
            "build_e1_e3_state_arms",
            "evaluate_e1_e3_state_arms",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
