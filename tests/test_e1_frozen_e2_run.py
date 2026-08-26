from __future__ import annotations

from dataclasses import asdict
import json
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_frozen_e2_run import (
    E1_FROZEN_E2_ABSOLUTE_TOLERANCE,
    evaluate_e1_frozen_e2_run,
    run_e1_frozen_e2_once,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_coupled_fast_field import contract
from tests.test_neutral_fast_afterimage import shared_field


class E1FrozenE2RunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        field = shared_field()
        state = build_neutral_e1_state(field.layer, contract())
        cls.result = run_e1_frozen_e2_once(
            field,
            state,
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
        )
        cls.decision = evaluate_e1_frozen_e2_run(cls.result)

    @classmethod
    def tearDownClass(cls) -> None:
        print("E1_FROZEN_E2_METRICS=" + json.dumps(asdict(cls.result.metrics), sort_keys=True))
        print("E1_FROZEN_E2_DECISION=" + cls.decision)

    def test_pre_probe_and_ablation_are_exact(self) -> None:
        m = self.result.metrics
        self.assertEqual(0.0, m.pre_s_linf)
        self.assertEqual(0.0, m.pre_h_linf)
        self.assertEqual(0.0, m.ablated_s_linf)
        self.assertEqual(0.0, m.ablated_h_linf)
        self.assertEqual(0.0, m.p0_a0_s_linf)
        self.assertEqual(0.0, m.p0_a0_h_linf)

    def test_history_state_is_distinct_and_mirrored(self) -> None:
        m = self.result.metrics
        self.assertGreater(m.state_linf, E1_FROZEN_E2_ABSOLUTE_TOLERANCE)
        self.assertLessEqual(
            m.total_binding_difference, E1_FROZEN_E2_ABSOLUTE_TOLERANCE
        )
        self.assertLessEqual(
            m.mirror_binding_error, E1_FROZEN_E2_ABSOLUTE_TOLERANCE
        )

    def test_active_history_fields_differ_above_refinement(self) -> None:
        m = self.result.metrics
        self.assertTrue(
            m.active_s_linf > max(m.refinement_s_linf, 1e-12)
            or m.active_h_linf > max(m.refinement_h_linf, 1e-12)
        )

    def test_fixed_gain_controls_are_exact(self) -> None:
        m = self.result.metrics
        self.assertEqual(0.0, m.fixed_gain_s_linf)
        self.assertEqual(0.0, m.fixed_gain_h_linf)

    def test_refinement_residual_is_within_registered_tolerance(self) -> None:
        m = self.result.metrics
        self.assertLessEqual(m.refinement_s_linf, 1e-12)
        self.assertLessEqual(m.refinement_h_linf, 1e-12)

    def test_bounded_decision_is_technical_effect(self) -> None:
        self.assertEqual("E2_TECHNICAL_CAUSAL_EFFECT", self.decision)

    def test_result_contains_no_memory_or_success_role(self) -> None:
        roles = set(self.result.__dataclass_fields__) | set(
            self.result.metrics.__dataclass_fields__
        )
        self.assertTrue(
            {"memory", "learning", "meaning", "success", "organism"}.isdisjoint(roles)
        )

    def test_run_roles_are_not_exported_through_public_apis(self) -> None:
        for role in (
            "E1FrozenE2RunResult",
            "run_e1_frozen_e2_once",
            "evaluate_e1_frozen_e2_run",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
