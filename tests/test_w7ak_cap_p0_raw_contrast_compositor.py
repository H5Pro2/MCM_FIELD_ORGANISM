from __future__ import annotations

from dataclasses import replace
import math
import unittest

from mcm_field_organism.w7aa_p0_seven_path_consumer import (
    consume_w7aa_p0_seven_path_plan,
)
from mcm_field_organism.w7ac_observer_seven_path_consumer import (
    consume_w7ac_observer_seven_path_result,
)
from mcm_field_organism.w7ae_cap_seven_path_consumer import (
    consume_w7ae_cap_seven_path_plan,
)
from mcm_field_organism.w7ag_passive_cap_measurement_handoff import (
    compose_w7ag_passive_cap_measurement_handoff,
)
from mcm_field_organism.w7ai_p0_zero_start_measurement_reference import (
    compose_w7ai_p0_zero_start_measurement_references,
)
from mcm_field_organism.w7ak_cap_p0_raw_contrast_compositor import (
    W7AKRawContrastError,
    compose_w7ak_cap_p0_raw_contrasts,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7w_symmetric_source_family import (
    build_w7w_source_authorization,
    build_w7w_symmetric_source_family,
)
from mcm_field_organism.w7y_seven_path_source_plan import (
    build_w7y_seven_path_source_plan,
)


class W7AKCAPP0RawContrastCompositorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()
        cls.family = build_w7w_symmetric_source_family(cls.adapter)
        cls.authorization = build_w7w_source_authorization(
            cls.adapter,
            cls.family,
        )
        cls.plan = build_w7y_seven_path_source_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
        )
        cls.p0_result = consume_w7aa_p0_seven_path_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
        )
        cls.observer_result = consume_w7ac_observer_seven_path_result(
            cls.adapter,
            cls.authorization,
            cls.plan,
            cls.p0_result,
        )
        cls.cap_result = consume_w7ae_cap_seven_path_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.p0_result,
            cls.observer_result,
        )
        cls.cap_handoff = compose_w7ag_passive_cap_measurement_handoff(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.cap_result,
        )
        cls.p0_references = compose_w7ai_p0_zero_start_measurement_references(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.p0_result,
            cls.observer_result,
            cls.cap_result,
            cls.cap_handoff,
        )
        cls.input_digests = (
            cls.cap_handoff.measurement_handoff_digest,
            cls.p0_references.p0_zero_start_measurement_reference_digest,
        )
        cls.result = compose_w7ak_cap_p0_raw_contrasts(
            cls.cap_handoff,
            cls.p0_references,
        )

    def test_global_composition_and_digest_are_bound(self) -> None:
        self.assertEqual(
            "w7ak.cap-p0-raw-contrast-compositor.v1",
            self.result.compositor_id,
        )
        self.assertEqual(
            "ca047546d37a0ebd5728ee6adcf27d083c2a7fce3aad82f882284f08629f1fc3",
            self.result.raw_contrast_composition_digest,
        )
        self.assertFalse(self.result.evaluated)

    def test_all_35_roles_and_3185_samples_are_present(self) -> None:
        expected = tuple(
            (path_id, checkpoint)
            for path_id in ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
            for checkpoint in range(5)
        )
        self.assertEqual(
            expected,
            tuple((item.path_id, item.checkpoint) for item in self.result.pairs),
        )
        self.assertEqual(
            3185,
            sum(len(item.residual_samples) for item in self.result.pairs),
        )

    def test_pair_bindings_and_ticks_match_both_inputs(self) -> None:
        for pair in self.result.pairs:
            self.assertEqual(
                pair.cap_measurement.plan_checkpoint_digest,
                pair.plan_checkpoint_digest,
            )
            self.assertEqual(
                pair.p0_reference.plan_checkpoint_digest,
                pair.plan_checkpoint_digest,
            )
            self.assertEqual(
                pair.cap_measurement.field_measurement.probe_observation_ticks,
                pair.observation_ticks,
            )
            self.assertEqual(
                pair.p0_reference.field_measurement.probe_observation_ticks,
                pair.observation_ticks,
            )

    def test_residual_samples_are_exact_cap_minus_p0(self) -> None:
        for pair in self.result.pairs:
            for residual, cap, p0 in zip(
                pair.residual_samples,
                pair.cap_measurement.samples,
                pair.p0_reference.samples,
                strict=True,
            ):
                self.assertEqual(cap.tick, residual.tick)
                self.assertEqual(
                    tuple(a - b for a, b in zip(cap.s_values, p0.s_values, strict=True)),
                    residual.s_residuals,
                )
                self.assertEqual(
                    tuple(a - b for a, b in zip(cap.h_values, p0.h_values, strict=True)),
                    residual.h_residuals,
                )

    def test_primary_raw_distances_match_residuals(self) -> None:
        for pair in self.result.pairs:
            s_values = tuple(
                value
                for sample in pair.residual_samples
                for value in sample.s_residuals
            )
            h_values = tuple(
                value
                for sample in pair.residual_samples
                for value in sample.h_residuals
            )
            self.assertEqual(max(abs(item) for item in s_values), pair.cap_p0_S_linf)
            self.assertEqual(max(abs(item) for item in h_values), pair.cap_p0_H_linf)
            self.assertEqual(
                math.sqrt(
                    math.fsum(item * item for item in s_values)
                    + math.fsum(item * item for item in h_values)
                ),
                pair.cap_p0_SH_trajectory_l2,
            )

    def test_secondary_gaps_use_only_existing_w7p_scalars(self) -> None:
        for pair in self.result.pairs:
            cap = pair.cap_measurement.field_measurement
            p0 = pair.p0_reference.field_measurement
            self.assertEqual(
                abs(cap.probe_S_linf - p0.probe_S_linf),
                pair.abs_probe_S_linf_gap,
            )
            self.assertEqual(
                abs(cap.probe_H_linf - p0.probe_H_linf),
                pair.abs_probe_H_linf_gap,
            )
            self.assertEqual(
                abs(cap.probe_SH_trajectory_l2 - p0.probe_SH_trajectory_l2),
                pair.abs_probe_SH_trajectory_l2_gap,
            )

    def test_pairs_remain_unevaluated_and_role_clean(self) -> None:
        for pair in self.result.pairs:
            self.assertTrue(pair.same_zero_fast_start)
            self.assertFalse(pair.p0_has_substrate)
            self.assertFalse(pair.evaluated)
            self.assertIsNone(pair.p0_reference.initial_state.p0_field.substrate)

    def test_all_countercontrols_are_bound(self) -> None:
        self.assertTrue(self.result.identity_countercontrol_digest)
        self.assertTrue(self.result.symmetry_countercontrol_digest)
        self.assertTrue(self.result.order_countercontrol_digest)
        self.assertEqual(
            35,
            len({item.raw_contrast_pair_digest for item in self.result.pairs}),
        )

    def test_inputs_remain_unchanged(self) -> None:
        self.assertEqual(
            self.input_digests,
            (
                self.cap_handoff.measurement_handoff_digest,
                self.p0_references.p0_zero_start_measurement_reference_digest,
            ),
        )
        self.assertEqual(self.input_digests[0], self.result.cap_handoff_digest)
        self.assertEqual(self.input_digests[1], self.result.p0_reference_digest)

    def test_tampering_and_public_export_are_rejected(self) -> None:
        with self.assertRaises(W7AKRawContrastError):
            replace(
                self.result,
                raw_contrast_composition_digest="0" * 64,
            )
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "compose_w7ak_cap_p0_raw_contrasts"))


if __name__ == "__main__":
    unittest.main()
