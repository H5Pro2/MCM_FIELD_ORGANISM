from __future__ import annotations

import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_av_history_permutation import (
    build_e1_av_history_permutation,
)
from mcm_field_organism.e1_confirmation_formation_runner import (
    E1ConfirmationFormationRunnerError,
    run_synthetic_e1_confirmation_formation,
)
from mcm_field_organism.e1_confirmation_refinement_planner import (
    build_e1_confirmation_refinement_plans,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.e1_refined_confirmation_contract import (
    build_e1_refined_confirmation_contract,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_a0_av_history_producer import contract, field, source


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _inputs():
    corridor = build_e1_refined_confirmation_contract(REPORTS, UPSTREAM)
    permutation = source()
    ab = build_e1_confirmation_refinement_plans(
        corridor,
        permutation.history_ab,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    ba = build_e1_confirmation_refinement_plans(
        corridor,
        permutation.history_ba,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    initial = field()
    state = build_neutral_e1_state(initial.layer, contract())
    return corridor, permutation, ab, ba, initial, state


def _run():
    corridor, permutation, ab, ba, initial, state = _inputs()
    return run_synthetic_e1_confirmation_formation(
        corridor,
        permutation,
        ab,
        ba,
        initial,
        state,
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


class E1ConfirmationFormationRunnerTests(unittest.TestCase):
    def test_runner_consumes_r2_r4_r8_synthetic_plans(self) -> None:
        result = _run()

        self.assertEqual(
            (("r2", 2), ("r4", 4), ("r8", 8)),
            tuple(
                (item.refinement_id, item.factor)
                for item in result.refinements
            ),
        )
        self.assertEqual("synthetic-s1eb3", result.source_provenance)

    def test_identity_and_formation_ablations_are_exact(self) -> None:
        result = _run()

        for refinement in result.refinements:
            self.assertEqual(refinement.b_ab, refinement.b_ab_identity)
            self.assertIsNot(refinement.b_ab, refinement.b_ab_identity)
            for state in (
                refinement.b_ab_formation_ablated,
                refinement.b_ba_formation_ablated,
            ):
                self.assertTrue(
                    all(item.binding == 0.0 for item in state.edge_bindings)
                )

    def test_support_resource_and_backreaction_controls_hold(self) -> None:
        result = _run()

        for refinement in result.refinements:
            self.assertEqual(5, len(refinement.arm_audits))
            for audit in refinement.arm_audits:
                self.assertEqual(4, audit.source_support_count)
                self.assertEqual(4, audit.assigned_event_count)
                self.assertLessEqual(audit.resource_budget_error, 1e-12)
                self.assertFalse(audit.history_backreaction_enabled)

    def test_output_has_no_field_probe_metrics_or_decision(self) -> None:
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
            self.assertTrue(
                forbidden.isdisjoint(refinement.__dataclass_fields__)
            )

    def test_runner_is_repeatable_and_preserves_initial_inputs(self) -> None:
        corridor, permutation, ab, ba, initial, state = _inputs()
        layer_digest = initial.layer.digest()
        first = run_synthetic_e1_confirmation_formation(
            corridor,
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
        self.assertTrue(
            all(item.binding == 0.0 for item in state.edge_bindings)
        )

    def test_canonical_source_is_rejected_before_execution(self) -> None:
        corridor, _, ab, ba, initial, state = _inputs()

        with self.assertRaisesRegex(
            E1ConfirmationFormationRunnerError,
            "rejects canonical",
        ):
            run_synthetic_e1_confirmation_formation(
                corridor,
                build_e1_av_history_permutation(),
                ab,
                ba,
                initial,
                state,
                NeutralLocalFieldSubstrateConfig(1.0),
                NeutralFastAfterimageConfig(0.5),
            )

    def test_plan_source_mismatch_is_rejected(self) -> None:
        corridor, permutation, ab, ba, initial, state = _inputs()
        with self.assertRaisesRegex(
            E1ConfirmationFormationRunnerError,
            "plans do not match",
        ):
            run_synthetic_e1_confirmation_formation(
                corridor,
                permutation,
                ba,
                ab,
                initial,
                state,
                NeutralLocalFieldSubstrateConfig(1.0),
                NeutralFastAfterimageConfig(0.5),
            )

    def test_runner_keeps_canonical_paths_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        _run()

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_runner_has_no_probe_or_release_path_and_remains_private(self) -> None:
        source_text = inspect.getsource(
            run_synthetic_e1_confirmation_formation
        )
        for forbidden in (
            "_fixed_probe_sequences",
            "run_e1_frozen_probe",
            "execute_e1_refined_chain_one_shot",
            "e1_refined_confirmation_s1eb_once_v1",
        ):
            self.assertNotIn(forbidden, source_text)
        for role in (
            "E1ConfirmationFormationProduction",
            "run_synthetic_e1_confirmation_formation",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
