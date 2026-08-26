from __future__ import annotations

import inspect
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_av_history_permutation import (
    build_e1_av_history_permutation,
)
from mcm_field_organism.e1_completion_aligned_refinement import (
    build_e1_completion_aligned_refinement_plans,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.e1_refined_formation_runner import (
    E1RefinedFormationRunnerError,
    run_synthetic_e1_refined_formation,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_a0_av_history_producer import contract, field, source


def _inputs():
    permutation = source()
    ab = build_e1_completion_aligned_refinement_plans(
        permutation.history_ab,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    ba = build_e1_completion_aligned_refinement_plans(
        permutation.history_ba,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    initial = field()
    state = build_neutral_e1_state(initial.layer, contract())
    return permutation, ab, ba, initial, state


def _run():
    permutation, ab, ba, initial, state = _inputs()
    return run_synthetic_e1_refined_formation(
        permutation,
        ab,
        ba,
        initial,
        state,
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


class E1RefinedFormationRunnerTests(unittest.TestCase):
    def test_runner_consumes_all_three_refinement_plans(self) -> None:
        result = _run()

        self.assertEqual(
            (("r1", 1), ("r2", 2), ("r4", 4)),
            tuple((item.refinement_id, item.factor) for item in result.refinements),
        )
        self.assertEqual("synthetic", result.source_provenance)

    def test_ab_identity_is_exact_and_object_separate(self) -> None:
        result = _run()

        for refinement in result.refinements:
            self.assertEqual(refinement.b_ab, refinement.b_ab_identity)
            self.assertIsNot(refinement.b_ab, refinement.b_ab_identity)

    def test_formation_ablations_remain_neutral(self) -> None:
        result = _run()

        for refinement in result.refinements:
            for state in (
                refinement.b_ab_formation_ablated,
                refinement.b_ba_formation_ablated,
            ):
                self.assertTrue(all(item.binding == 0.0 for item in state.edge_bindings))

    def test_support_resource_and_backreaction_controls_hold(self) -> None:
        result = _run()

        for refinement in result.refinements:
            self.assertEqual(5, len(refinement.arm_audits))
            for audit in refinement.arm_audits:
                self.assertEqual(4, audit.source_support_count)
                self.assertEqual(4, audit.assigned_event_count)
                self.assertLessEqual(audit.resource_budget_error, 1e-12)
                self.assertFalse(audit.history_backreaction_enabled)

    def test_output_contains_states_and_audits_but_no_fields_or_probe(self) -> None:
        result = _run()
        forbidden = {
            "field",
            "ab_field",
            "ba_field",
            "probe",
            "metrics",
            "decision",
            "memory",
        }

        self.assertTrue(forbidden.isdisjoint(result.__dataclass_fields__))
        for refinement in result.refinements:
            self.assertTrue(forbidden.isdisjoint(refinement.__dataclass_fields__))

    def test_runner_is_repeatable_and_keeps_initial_inputs_unchanged(self) -> None:
        permutation, ab, ba, initial, state = _inputs()
        layer_digest = initial.layer.digest()
        first = run_synthetic_e1_refined_formation(
            permutation,
            ab,
            ba,
            initial,
            state,
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
        )
        second = _run()

        self.assertEqual(first.production_digest, second.production_digest)
        self.assertEqual(layer_digest, initial.layer.digest())
        self.assertIsNone(initial.last_distribution)
        self.assertTrue(all(item.binding == 0.0 for item in state.edge_bindings))

    def test_canonical_source_is_rejected_before_execution(self) -> None:
        canonical = build_e1_av_history_permutation()
        permutation, ab, ba, initial, state = _inputs()
        del permutation
        with self.assertRaisesRegex(
            E1RefinedFormationRunnerError,
            "rejects canonical",
        ):
            run_synthetic_e1_refined_formation(
                canonical,
                ab,
                ba,
                initial,
                state,
                NeutralLocalFieldSubstrateConfig(1.0),
                NeutralFastAfterimageConfig(0.5),
            )

    def test_runner_remains_private(self) -> None:
        source_text = inspect.getsource(run_synthetic_e1_refined_formation)
        for forbidden in (
            "run_e1_frozen_probe",
            "execute_e1_frozen_state_transfer_one_shot",
            "produce_e1_frozen_state_transfer",
        ):
            self.assertNotIn(forbidden, source_text)
        for role in (
            "E1RefinedFormationProduction",
            "run_synthetic_e1_refined_formation",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
