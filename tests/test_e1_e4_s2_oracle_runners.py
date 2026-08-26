from __future__ import annotations

from dataclasses import replace
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e4_baseline_handoffs import E1_E4_CHECKPOINT_IDS
from mcm_field_organism.e1_e4_e1_runners import run_e1_e4_e1_b0_b1_models
from mcm_field_organism.e1_e4_execution import E1_E4_REFINEMENT_LIMIT
from mcm_field_organism.e1_e4_s2_oracle_runners import (
    E1E4S2OracleRunnerError,
    build_e1_e4_oracle_g_run,
    run_e1_e4_s2_b2_model,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_coupled_fast_field import contract
from tests.test_neutral_fast_afterimage import shared_field


class E1E4S2OracleRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.initial = shared_field()
        cls.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        cls.afterimage = NeutralFastAfterimageConfig(0.5)
        cls.s2 = run_e1_e4_s2_b2_model(
            cls.initial, cls.substrate, cls.afterimage
        )
        e1_runs, _ = run_e1_e4_e1_b0_b1_models(
            cls.initial,
            build_neutral_e1_state(cls.initial.layer, contract()),
            cls.substrate,
            cls.afterimage,
        )
        cls.e1 = e1_runs[0]
        cls.oracle = build_e1_e4_oracle_g_run(cls.e1)

    def test_s2_profile_is_complete_measurable_and_checkpoint_variable(self) -> None:
        self.assertEqual("b2", self.s2.model_id)
        self.assertEqual(72, len(self.s2.profile.components))
        self.assertEqual(
            E1_E4_CHECKPOINT_IDS,
            tuple(item.checkpoint_id for item in self.s2.profile.checkpoints),
        )
        self.assertGreater(max(abs(value) for value in self.s2.profile.components), 1e-12)
        self.assertGreater(
            len(
                {
                    item.activation_effect + item.afterimage_effect
                    for item in self.s2.profile.checkpoints
                }
            ),
            1,
        )

    def test_s2_controls_invariants_and_refinement_hold(self) -> None:
        self.assertTrue(self.s2.controls_hold)
        self.assertTrue(self.s2.technically_compatible)
        self.assertLessEqual(self.s2.relative_refinement_linf, E1_E4_REFINEMENT_LIMIT)
        self.assertGreaterEqual(self.s2.minimum_internal_resource, -1.0)

    def test_oracle_profile_is_exactly_e1_with_distinct_identity(self) -> None:
        self.assertEqual("oracle-g", self.oracle.model_id)
        self.assertEqual(self.e1.profile.components, self.oracle.profile.components)
        self.assertNotEqual(self.e1.parameter_digest, self.oracle.parameter_digest)
        self.assertTrue(self.oracle.controls_hold)

    def test_oracle_rejects_invalid_or_non_e1_source(self) -> None:
        with self.assertRaises(E1E4S2OracleRunnerError):
            build_e1_e4_oracle_g_run(replace(self.e1, fixed_reader_controls_hold=False))
        with self.assertRaises(E1E4S2OracleRunnerError):
            build_e1_e4_oracle_g_run(replace(self.e1, model_id="b1", profile=replace(self.e1.profile, model_id="b1")))

    def test_changed_s2_field_contract_is_rejected(self) -> None:
        with self.assertRaises(E1E4S2OracleRunnerError):
            run_e1_e4_s2_b2_model(
                self.initial,
                NeutralLocalFieldSubstrateConfig(2.0),
                self.afterimage,
            )

    def test_inputs_remain_fresh_and_roles_private(self) -> None:
        self.assertEqual(0, self.initial.layer.tick)
        self.assertIsNone(self.initial.last_distribution)
        for role in (
            "run_e1_e4_s2_b2_model",
            "build_e1_e4_oracle_g_run",
            "E1E4S2OracleRunnerError",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
