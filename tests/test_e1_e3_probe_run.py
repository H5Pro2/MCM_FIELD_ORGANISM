from __future__ import annotations

from dataclasses import asdict
import json
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e3_probe_run import (
    E1_E3_PROBE_ABSOLUTE_TOLERANCE,
    evaluate_e1_e3_probe_run,
    run_e1_e3_probe_once,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_coupled_fast_field import contract
from tests.test_neutral_fast_afterimage import shared_field


class E1E3ProbeRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        field = shared_field()
        state = build_neutral_e1_state(field.layer, contract())
        cls.result = run_e1_e3_probe_once(
            field,
            state,
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
        )
        cls.decision = evaluate_e1_e3_probe_run(cls.result)

    @classmethod
    def tearDownClass(cls) -> None:
        print("E1_E3_PROBE_METRICS=" + json.dumps(asdict(cls.result.metrics), sort_keys=True))
        print(
            "E1_E3_STATE_METRICS="
            + json.dumps(asdict(cls.result.state_arms.metrics), sort_keys=True)
        )
        print("E1_E3_DECISION=" + cls.decision)

    def test_pre_probe_and_ablation_controls_are_exact(self) -> None:
        m = self.result.metrics
        self.assertEqual(0.0, m.pre_probe_s_linf)
        self.assertEqual(0.0, m.pre_probe_h_linf)
        self.assertEqual(0.0, m.ablation_p0_s_linf)
        self.assertEqual(0.0, m.ablation_p0_h_linf)

    def test_fixed_gain_controls_are_exact(self) -> None:
        self.assertEqual(0.0, self.result.metrics.fixed_gain_s_linf)
        self.assertEqual(0.0, self.result.metrics.fixed_gain_h_linf)

    def test_refinement_is_within_registered_tolerance(self) -> None:
        self.assertLessEqual(
            self.result.metrics.refinement_s_linf,
            E1_E3_PROBE_ABSOLUTE_TOLERANCE,
        )
        self.assertLessEqual(
            self.result.metrics.refinement_h_linf,
            E1_E3_PROBE_ABSOLUTE_TOLERANCE,
        )

    def test_release_changes_the_identical_probe_from_hold(self) -> None:
        m = self.result.metrics
        self.assertTrue(
            m.release_hold_s_linf > 1e-12 or m.release_hold_h_linf > 1e-12
        )

    def test_compete_changes_the_identical_probe_from_release(self) -> None:
        m = self.result.metrics
        self.assertTrue(
            m.compete_release_s_linf > 1e-12
            or m.compete_release_h_linf > 1e-12
        )

    def test_state_arm_controls_remain_valid(self) -> None:
        m = self.result.state_arms.metrics
        self.assertLessEqual(m.release_analytic_linf, 1e-12)
        self.assertLessEqual(m.resource_budget_linf, 1e-12)
        self.assertGreater(m.compete_total_binding_rebound, 1e-12)

    def test_decision_is_the_registered_combined_technical_result(self) -> None:
        self.assertEqual("E3_RELEASE_AND_RESOURCE_REUSE", self.decision)

    def test_result_has_no_memory_or_success_role(self) -> None:
        roles = set(self.result.__dataclass_fields__) | set(
            self.result.metrics.__dataclass_fields__
        )
        self.assertTrue(
            {"memory", "forgetting", "learning", "meaning", "success"}.isdisjoint(roles)
        )

    def test_probe_roles_are_not_publicly_exported(self) -> None:
        for role in (
            "E1E3ProbeRunResult",
            "run_e1_e3_probe_once",
            "evaluate_e1_e3_probe_run",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
