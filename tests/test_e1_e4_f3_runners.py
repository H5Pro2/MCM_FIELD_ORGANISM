from __future__ import annotations

import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e4_baseline_handoffs import E1_E4_CHECKPOINT_IDS
from mcm_field_organism.e1_e4_f3_runners import (
    E1_E4_F3_MODEL_IDS,
    E1E4F3RunnerError,
    build_e1_e4_f3_runner,
    run_e1_e4_f3_model,
)
from mcm_field_organism.e1_e4_execution import E1_E4_REFINEMENT_LIMIT
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_neutral_fast_afterimage import shared_field


class E1E4F3RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.initial = shared_field()
        cls.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        cls.afterimage = NeutralFastAfterimageConfig(0.5)
        cls.results = {
            model_id: run_e1_e4_f3_model(
                model_id,
                cls.initial,
                cls.substrate,
                cls.afterimage,
            )
            for model_id in E1_E4_F3_MODEL_IDS
        }

    def test_all_four_registered_models_produce_complete_profiles(self) -> None:
        self.assertEqual(E1_E4_F3_MODEL_IDS, tuple(self.results))
        for model_id, result in self.results.items():
            with self.subTest(model_id=model_id):
                self.assertEqual(model_id, result.model_id)
                self.assertEqual(72, len(result.profile.components))
                self.assertEqual(
                    E1_E4_CHECKPOINT_IDS,
                    tuple(item.checkpoint_id for item in result.profile.checkpoints),
                )

    def test_ablation_frozen_reader_and_invariants_hold(self) -> None:
        for model_id, result in self.results.items():
            with self.subTest(model_id=model_id):
                self.assertTrue(result.observation_schedule_matches)
                self.assertTrue(result.ablation_controls_hold)
                self.assertTrue(result.fixed_reader_controls_hold)
                self.assertTrue(result.invariants_hold)
                self.assertTrue(result.technically_compatible)
                self.assertGreaterEqual(result.minimum_internal_resource, 0.0)

    def test_refinement_is_within_registered_limit(self) -> None:
        for model_id, result in self.results.items():
            with self.subTest(model_id=model_id):
                self.assertLessEqual(
                    result.relative_refinement_linf, E1_E4_REFINEMENT_LIMIT
                )

    def test_profiles_are_measurable_and_not_checkpoint_constant(self) -> None:
        for model_id, result in self.results.items():
            with self.subTest(model_id=model_id):
                self.assertGreater(
                    max(abs(value) for value in result.profile.components), 1e-12
                )
                checkpoint_vectors = {
                    item.activation_effect + item.afterimage_effect
                    for item in result.profile.checkpoints
                }
                self.assertGreater(len(checkpoint_vectors), 1)

    def test_model_parameter_bindings_are_distinct_and_deterministic(self) -> None:
        digests = tuple(item.parameter_digest for item in self.results.values())
        self.assertEqual(4, len(set(digests)))
        self.assertTrue(all(len(item) == 64 for item in digests))

    def test_runner_factory_binds_without_immediate_execution(self) -> None:
        runner = build_e1_e4_f3_runner(
            "b3", self.initial, self.substrate, self.afterimage
        )
        self.assertTrue(callable(runner))

    def test_unknown_model_and_changed_field_contract_are_rejected(self) -> None:
        with self.assertRaises(E1E4F3RunnerError):
            run_e1_e4_f3_model(
                "b2", self.initial, self.substrate, self.afterimage
            )
        with self.assertRaises(E1E4F3RunnerError):
            run_e1_e4_f3_model(
                "b3",
                self.initial,
                NeutralLocalFieldSubstrateConfig(2.0),
                self.afterimage,
            )

    def test_initial_field_is_not_mutated(self) -> None:
        self.assertEqual(0, self.initial.layer.tick)
        self.assertIsNone(self.initial.last_distribution)
        self.assertIsNone(self.initial.substrate)

    def test_runner_roles_remain_private(self) -> None:
        for role in (
            "run_e1_e4_f3_model",
            "build_e1_e4_f3_runner",
            "E1E4F3RunnerError",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
