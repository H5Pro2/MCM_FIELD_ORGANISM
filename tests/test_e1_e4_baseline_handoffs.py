from __future__ import annotations

import unittest

import numpy as np

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e4_baseline_handoffs import (
    E1_E4_CHECKPOINT_IDS,
    E1_E4_PROFILE_COMPONENT_COUNT,
    E1E4BaselineHandoffError,
    E1E4CheckpointEffect,
    E1E4ObservableProfile,
    advance_e1_e4_s2_b2,
    advance_frozen_e1_e4_s2_b2_probe,
    build_e1_e4_const_v_handoff,
    build_e1_e4_s2_b2_handoff,
    build_zero_e1_e4_s2_state,
    compare_e1_e4_profiles,
    compute_e1_e4_const_v_coupling,
)
from mcm_field_organism.s2_reference_baselines import advance_s2_reference_model
from mcm_field_organism.w7n_capacity_function_baselines import (
    compute_w7n_coupling_baseline,
)
from tests.test_neutral_fast_afterimage import shared_field


def profile(model_id: str, offset: float = 0.0) -> E1E4ObservableProfile:
    return E1E4ObservableProfile(
        model_id,
        tuple(
            E1E4CheckpointEffect(
                checkpoint_id,
                (index + offset, index + 0.1 + offset, index + 0.2 + offset),
                (index + 0.3 + offset, index + 0.4 + offset, index + 0.5 + offset),
            )
            for index, checkpoint_id in enumerate(E1_E4_CHECKPOINT_IDS)
        ),
    )


class E1E4BaselineHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.field = shared_field()
        cls.s2 = build_e1_e4_s2_b2_handoff(cls.field.layer)
        cls.const_v = build_e1_e4_const_v_handoff(cls.field.layer)

    def test_profile_has_fixed_order_and_72_signed_components(self) -> None:
        item = profile("e1")
        self.assertEqual(E1_E4_PROFILE_COMPONENT_COUNT, len(item.components))
        self.assertEqual((0.0, 0.1, 0.2, 0.3, 0.4, 0.5), item.components[:6])
        self.assertEqual(64, len(item.digest()))

    def test_profile_rejects_missing_or_reordered_checkpoints(self) -> None:
        item = profile("e1")
        with self.assertRaises(E1E4BaselineHandoffError):
            E1E4ObservableProfile("e1", tuple(reversed(item.checkpoints)))

    def test_profile_distance_preserves_release_and_competition_segments(self) -> None:
        distance = compare_e1_e4_profiles(profile("e1"), profile("b2", 0.25))
        self.assertAlmostEqual(0.25, distance.profile_linf_residual)
        self.assertAlmostEqual(18.0, distance.profile_l1_residual)
        self.assertAlmostEqual(0.25, distance.release_segment_linf_residual)
        self.assertAlmostEqual(0.25, distance.competition_segment_linf_residual)

    def test_s2_handoff_binds_default_contract_and_zero_state(self) -> None:
        state = build_zero_e1_e4_s2_state(self.s2)
        self.assertEqual((0.0,) * 3, state.activation)
        self.assertEqual((0.0,) * 3, state.development)
        self.assertEqual(0.25, self.s2.config.coupling_rate_per_second)
        self.assertEqual(8.0, self.s2.config.capacity_ratio)

    def test_s2_active_and_ablated_paths_are_existing_b2_and_b1(self) -> None:
        state = build_zero_e1_e4_s2_state(self.s2)
        generator = np.asarray([[-1.0, 1.0, 0.0], [1.0, -2.0, 1.0], [0.0, 1.0, -1.0]])
        boundary = np.asarray([1.0, 0.0, 0.0])
        active = advance_e1_e4_s2_b2(
            self.s2, state, generator, boundary, 1.0, backreaction_enabled=True
        )
        ablated = advance_e1_e4_s2_b2(
            self.s2, state, generator, boundary, 1.0, backreaction_enabled=False
        )
        expected_active = advance_s2_reference_model(
            "b2", state, generator, boundary, 1.0, self.s2.config
        )
        expected_ablated = advance_s2_reference_model(
            "b1", state, generator, boundary, 1.0, self.s2.config
        )
        self.assertEqual(expected_active, active)
        self.assertEqual(expected_ablated, ablated)

    def test_frozen_s2_probe_retains_l_and_ablation_changes_only_reader(self) -> None:
        state = build_zero_e1_e4_s2_state(self.s2)
        state = advance_e1_e4_s2_b2(
            self.s2,
            state,
            np.zeros((3, 3)),
            np.asarray([0.8, 0.0, -0.4]),
            1.0,
            backreaction_enabled=False,
        ).state
        active = advance_frozen_e1_e4_s2_b2_probe(
            self.s2,
            state,
            np.zeros((3, 3)),
            np.zeros(3),
            1.0,
            backreaction_enabled=True,
        )
        ablated = advance_frozen_e1_e4_s2_b2_probe(
            self.s2,
            state,
            np.zeros((3, 3)),
            np.zeros(3),
            1.0,
            backreaction_enabled=False,
        )
        self.assertEqual(state.development, active.state.development)
        self.assertEqual(state.development, ablated.state.development)
        self.assertNotEqual(active.state.activation, ablated.state.activation)

    def test_const_v_handoff_uses_exact_w7n_spec_on_three_nodes(self) -> None:
        self.assertEqual(
            {"eta": 1.0, "kappa": 0.5, "lambda_sm": 0.5},
            dict(self.const_v.baseline_spec.parameter_bindings),
        )
        self.assertEqual(
            (1.0 / 3.0,) * 3,
            tuple(item.mass for item in self.const_v.initial_substrate.masses),
        )

    def test_const_v_handoff_delegates_to_unchanged_kernel(self) -> None:
        expected = compute_w7n_coupling_baseline(
            self.const_v.baseline_spec,
            self.field.layer,
            self.const_v.initial_substrate,
        )
        actual = compute_e1_e4_const_v_coupling(
            self.const_v,
            self.field.layer,
            self.const_v.initial_substrate,
        )
        self.assertEqual(expected, actual)

    def test_handoffs_reject_wrong_geometry(self) -> None:
        other = shared_field(4)
        with self.assertRaises(E1E4BaselineHandoffError):
            build_e1_e4_s2_b2_handoff(other.layer)
        with self.assertRaises(E1E4BaselineHandoffError):
            compute_e1_e4_const_v_coupling(
                self.const_v, other.layer, self.const_v.initial_substrate
            )

    def test_handoff_roles_are_private(self) -> None:
        for role in (
            "E1E4ObservableProfile",
            "build_e1_e4_s2_b2_handoff",
            "build_e1_e4_const_v_handoff",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
