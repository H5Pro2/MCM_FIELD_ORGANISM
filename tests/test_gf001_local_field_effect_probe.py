from __future__ import annotations

import unittest

from mcm_field_organism import (
    GF001_BASELINE_IDS,
    GF001_BRANCH_IDS,
    GF001LocalFieldEffectProbeError,
    gf001_local_field_effect_probe_public_roles,
    run_gf001_local_field_effect_probe,
)


class GF001LocalFieldEffectProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_gf001_local_field_effect_probe()
        cls.by_key = {
            (item.baseline_id, item.branch_id): item
            for item in cls.result.observations
        }

    def values(self, baseline_id: str, branch_id: str):
        return dict(
            self.by_key[(baseline_id, branch_id)].activation_by_position
        )

    def test_every_preregistered_baseline_and_branch_is_present(self) -> None:
        self.assertTrue(self.result.baseline_ids_exact)
        self.assertTrue(self.result.branch_ids_exact_per_baseline)
        self.assertEqual(
            len(GF001_BASELINE_IDS) * len(GF001_BRANCH_IDS),
            len(self.result.observations),
        )

    def test_control_baselines_are_exact(self) -> None:
        self.assertTrue(self.result.receptor_projection_exact)
        self.assertTrue(self.result.hold_state_exact)

    def test_b2_and_b3_have_only_the_preregistered_local_contrast(self) -> None:
        self.assertTrue(
            self.result.effect_baselines_have_local_causal_contrast
        )
        self.assertTrue(self.result.local_ablation_removes_effect)
        self.assertTrue(self.result.current_contact_ablation_isolated)
        b2 = self.values(
            "b2.symmetric_local_activation_mean",
            "original_inputs",
        )
        b3 = self.values(
            "b3.symmetric_contact_and_local_activation_mean",
            "original_inputs",
        )
        self.assertEqual(0.5, b2[(0, 1)])
        self.assertEqual(0.375, b3[(0, 1)])
        self.assertEqual(
            {0.0},
            set(
                self.values(
                    "b2.symmetric_local_activation_mean",
                    "local_sample_ablation",
                ).values()
            ),
        )

    def test_zero_contact_and_missing_receptor_remain_distinct(self) -> None:
        self.assertTrue(self.result.zero_and_missing_contact_are_distinct)

    def test_order_reflection_and_dock_exchange_controls_close(self) -> None:
        self.assertTrue(self.result.sample_order_is_neutral)
        self.assertTrue(self.result.neuron_order_is_neutral)
        self.assertTrue(self.result.horizontal_reflection_is_equivariant)
        self.assertTrue(self.result.dock_exchange_is_equivariant)

    def test_null_same_dock_and_cross_dock_controls_close(self) -> None:
        self.assertTrue(self.result.zero_source_is_quiet)
        self.assertTrue(self.result.same_dock_effect_is_present)
        self.assertTrue(self.result.cross_dock_effect_is_present)

    def test_observer_rebuild_and_afterimage_controls_close(self) -> None:
        self.assertTrue(self.result.observer_is_neutral)
        self.assertTrue(self.result.independent_rebuild_is_exact)
        self.assertTrue(self.result.all_afterimages_are_zero)

    def test_every_output_is_explained_by_a_fixed_baseline(self) -> None:
        self.assertTrue(self.result.fixed_baselines_explain_all_outputs)
        self.assertFalse(self.result.input_frames_retained)
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.runtime_candidate_released)

    def test_result_digest_is_stable(self) -> None:
        self.assertEqual(
            "c9355116d4fb9eb9695fc468c2a90cec3f9b2fb7f3d59070a5cb69a65183f496",
            self.result.digest(),
        )

    def test_input_order_does_not_change_canonical_result(self) -> None:
        reverse = run_gf001_local_field_effect_probe(
            baseline_order=reversed(GF001_BASELINE_IDS),
            branch_order=reversed(GF001_BRANCH_IDS),
        )
        self.assertEqual(self.result.digest(), reverse.digest())

    def test_invalid_orders_are_rejected(self) -> None:
        with self.assertRaises(GF001LocalFieldEffectProbeError):
            run_gf001_local_field_effect_probe(
                baseline_order=GF001_BASELINE_IDS[:-1]
            )
        with self.assertRaises(GF001LocalFieldEffectProbeError):
            run_gf001_local_field_effect_probe(
                branch_order=GF001_BRANCH_IDS + ("original_inputs",)
            )

    def test_public_roles_exclude_mechanics_and_interpretations(self) -> None:
        forbidden = {
            "weight",
            "threshold",
            "decay_rate",
            "learning_rate",
            "memory",
            "relationship",
            "topology",
            "semantic_label",
            "meaning",
            "reward",
            "winner",
        }
        self.assertTrue(
            forbidden.isdisjoint(gf001_local_field_effect_probe_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
