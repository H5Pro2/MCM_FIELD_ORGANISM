from __future__ import annotations

import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e3_state_arms import (
    build_e1_e3_state_arms,
    produce_e1_competing_checkpoints,
    produce_e1_uniform_release_checkpoints,
)
from mcm_field_organism.e1_e4_baseline_handoffs import E1_E4_CHECKPOINT_IDS
from mcm_field_organism.e1_e4_e1_runners import run_e1_e4_e1_b0_b1_models
from mcm_field_organism.e1_e4_execution import (
    E1_E4_ABSOLUTE_TOLERANCE,
    E1_E4_CONTINUITY_ANCHORS,
    E1_E4_REFINEMENT_LIMIT,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.e1_mirrored_history import produce_e1_mirrored_histories
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_coupled_fast_field import contract
from tests.test_neutral_fast_afterimage import shared_field


class E1E4E1RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.initial = shared_field()
        cls.initial_state = build_neutral_e1_state(cls.initial.layer, contract())
        cls.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        cls.afterimage = NeutralFastAfterimageConfig(0.5)
        cls.runs, cls.anchors = run_e1_e4_e1_b0_b1_models(
            cls.initial,
            cls.initial_state,
            cls.substrate,
            cls.afterimage,
        )
        cls.by_id = {item.model_id: item for item in cls.runs}

    def test_e1_b0_b1_profiles_are_complete_and_ordered(self) -> None:
        self.assertEqual(("e1", "b0", "b1"), tuple(item.model_id for item in self.runs))
        for item in self.runs:
            with self.subTest(model_id=item.model_id):
                self.assertEqual(72, len(item.profile.components))
                self.assertEqual(
                    E1_E4_CHECKPOINT_IDS,
                    tuple(point.checkpoint_id for point in item.profile.checkpoints),
                )

    def test_e1_is_measurable_and_checkpoint_variable(self) -> None:
        profile = self.by_id["e1"].profile
        self.assertGreater(max(abs(value) for value in profile.components), 1e-12)
        self.assertGreater(
            len(
                {
                    item.activation_effect + item.afterimage_effect
                    for item in profile.checkpoints
                }
            ),
            1,
        )

    def test_b0_is_exact_zero(self) -> None:
        self.assertTrue(all(value == 0.0 for value in self.by_id["b0"].profile.components))

    def test_b1_is_one_static_h8_gain_at_every_checkpoint(self) -> None:
        checkpoints = self.by_id["b1"].profile.checkpoints
        first = checkpoints[0].activation_effect + checkpoints[0].afterimage_effect
        self.assertTrue(
            all(item.activation_effect + item.afterimage_effect == first for item in checkpoints)
        )
        self.assertGreater(max(abs(value) for value in first), 1e-12)

    def test_all_controls_and_refinement_limits_hold(self) -> None:
        for item in self.runs:
            with self.subTest(model_id=item.model_id):
                self.assertTrue(item.controls_hold)
                self.assertTrue(item.technically_compatible)
                self.assertLessEqual(item.relative_refinement_linf, E1_E4_REFINEMENT_LIMIT)

    def test_actual_continuity_anchors_match_stored_s1cd_values(self) -> None:
        self.assertEqual(
            tuple(name for name, _ in E1_E4_CONTINUITY_ANCHORS),
            tuple(name for name, _ in self.anchors),
        )
        for (name, actual), (_, expected) in zip(
            self.anchors, E1_E4_CONTINUITY_ANCHORS, strict=True
        ):
            with self.subTest(name=name):
                self.assertLessEqual(abs(actual - expected), E1_E4_ABSOLUTE_TOLERANCE)

    def test_competing_checkpoint_extension_preserves_existing_c8(self) -> None:
        history = produce_e1_mirrored_histories(
            self.initial,
            self.initial_state,
            self.substrate,
            self.afterimage,
        )
        release = produce_e1_uniform_release_checkpoints(
            self.initial, history.left_e1_state
        )
        checkpoints = produce_e1_competing_checkpoints(
            self.initial,
            release[2].state,
            self.substrate,
            self.afterimage,
        )
        existing = build_e1_e3_state_arms(
            self.initial,
            history.left_e1_state,
            self.substrate,
            self.afterimage,
        )
        self.assertEqual(8, len(checkpoints))
        self.assertEqual(existing.compete_field, checkpoints[-1][0])
        self.assertEqual(existing.compete_state, checkpoints[-1][1])

    def test_inputs_remain_fresh_and_unchanged(self) -> None:
        self.assertEqual(0, self.initial.layer.tick)
        self.assertIsNone(self.initial.last_distribution)
        self.assertEqual(
            (0.0, 0.0),
            tuple(item.binding for item in self.initial_state.edge_bindings),
        )

    def test_new_runner_roles_remain_private(self) -> None:
        for role in (
            "run_e1_e4_e1_b0_b1_models",
            "E1E4E1RunnerError",
            "produce_e1_competing_checkpoints",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
