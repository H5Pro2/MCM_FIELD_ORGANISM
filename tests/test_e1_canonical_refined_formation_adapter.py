from __future__ import annotations

import inspect
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_canonical_refined_formation_adapter import (
    E1CanonicalRefinedFormationAdapterError,
    produce_e1_canonical_refined_formation,
)
from mcm_field_organism.e1_refined_chain_canonical_producer import (
    prepare_e1_refined_chain_canonical_producer,
)
from mcm_field_organism.e1_completion_aligned_refinement import (
    build_e1_completion_aligned_refinement_plans,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from tests.test_e1_a0_av_history_producer import contract, field, source
from tests.e1_refined_chain_test_paths import make_unused_refined_chain_paths


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_frozen_state_transfer_s1dn_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json",
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.attempt.json",
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.lock",
)


class E1CanonicalRefinedFormationAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        global REPORTS, UPSTREAM, TARGETS
        cls._temporary, REPORTS, UPSTREAM = make_unused_refined_chain_paths()
        TARGETS = tuple(REPORTS / path.name for path in TARGETS)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_adapter_is_bound_but_not_called_by_preflight(self) -> None:
        with patch(
            "mcm_field_organism.e1_canonical_refined_formation_adapter."
            "produce_e1_canonical_refined_formation",
            side_effect=AssertionError("canonical formation called"),
        ):
            binding = prepare_e1_refined_chain_canonical_producer(
                REPORTS, UPSTREAM
            )

        self.assertTrue(binding.canonical_producer_bound)
        self.assertFalse(binding.execution_permitted)

    def test_adapter_source_contains_all_five_arms_and_three_refinements(self) -> None:
        source = inspect.getsource(produce_e1_canonical_refined_formation)

        for role in (
            '"ab"',
            '"ba"',
            '"ab_identity"',
            '"ab_formation_ablated"',
            '"ba_formation_ablated"',
            "_run_active_arm",
            "_run_ablated_arm",
            "ab_plans.plans",
            "ba_plans.plans",
        ):
            self.assertIn(role, source)

    def test_invalid_binding_fails_before_canonical_inputs(self) -> None:
        with patch(
            "mcm_field_organism.e1_canonical_refined_formation_adapter."
            "_canonical_inputs",
            side_effect=AssertionError("inputs built"),
        ):
            with self.assertRaises(E1CanonicalRefinedFormationAdapterError):
                produce_e1_canonical_refined_formation(None)

    def test_five_arm_core_runs_only_with_substituted_synthetic_inputs(self) -> None:
        binding = prepare_e1_refined_chain_canonical_producer(REPORTS, UPSTREAM)
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
        with patch(
            "mcm_field_organism.e1_canonical_refined_formation_adapter."
            "_canonical_inputs",
            return_value=(permutation, ab, ba, initial, state),
        ):
            result = produce_e1_canonical_refined_formation(binding)

        self.assertEqual("canonical-s1du", result.source_provenance)
        self.assertEqual(("r1", "r2", "r4"), tuple(
            item.refinement_id for item in result.refinements
        ))
        for refinement in result.refinements:
            self.assertEqual(refinement.b_ab, refinement.b_ab_identity)
            self.assertTrue(all(
                edge.binding == 0.0
                for edge in refinement.b_ab_formation_ablated.edge_bindings
            ))

    def test_static_adapter_check_keeps_one_shot_paths_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        inspect.getsource(produce_e1_canonical_refined_formation)
        after = tuple(path.exists() for path in TARGETS)

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, after)

    def test_adapter_roles_remain_private(self) -> None:
        for role in (
            "E1CanonicalRefinedFormationProduction",
            "produce_e1_canonical_refined_formation",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
