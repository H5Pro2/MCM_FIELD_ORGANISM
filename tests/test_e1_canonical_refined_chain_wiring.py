from __future__ import annotations

import inspect
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_canonical_refined_chain_wiring import (
    E1CanonicalRefinedChainWiringError,
    prepare_e1_canonical_refined_chain_wiring,
    produce_e1_canonical_refined_chain_result,
)
from mcm_field_organism.e1_canonical_refined_formation_adapter import (
    produce_e1_canonical_refined_formation,
)
from mcm_field_organism.e1_completion_aligned_refinement import (
    build_e1_completion_aligned_refinement_plans,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.e1_refined_chain_canonical_producer import (
    prepare_e1_refined_chain_canonical_producer,
)
from mcm_field_organism.receptor_time_model import ReceptorTimeSequence
from tests.test_e1_a0_av_history_producer import contract, field, source
from tests.e1_refined_chain_test_paths import make_unused_refined_chain_paths


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_frozen_state_transfer_s1dn_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json",
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.attempt.json",
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.lock",
)


def _synthetic_formation(binding):
    permutation = source()
    ab = build_e1_completion_aligned_refinement_plans(
        permutation.history_ab, horizon_start_tick=0,
        horizon_end_tick=2_000_000, ticks_per_second=1_000_000.0,
    )
    ba = build_e1_completion_aligned_refinement_plans(
        permutation.history_ba, horizon_start_tick=0,
        horizon_end_tick=2_000_000, ticks_per_second=1_000_000.0,
    )
    initial = field()
    state = build_neutral_e1_state(initial.layer, contract())
    with patch(
        "mcm_field_organism.e1_canonical_refined_formation_adapter."
        "_canonical_inputs",
        return_value=(permutation, ab, ba, initial, state),
    ):
        return produce_e1_canonical_refined_formation(binding)


def _synthetic_probe():
    return tuple(
        ReceptorTimeSequence(
            item.modality_id, item.geometry_id, item.clock_id, (item.frames[0],)
        )
        for item in source().history_ab
    )


class E1CanonicalRefinedChainWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        global REPORTS, UPSTREAM, TARGETS
        cls._temporary, REPORTS, UPSTREAM = make_unused_refined_chain_paths()
        TARGETS = tuple(REPORTS / path.name for path in TARGETS)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_preflight_binds_full_chain_without_execution(self) -> None:
        with patch(
            "mcm_field_organism.e1_canonical_refined_chain_wiring."
            "produce_e1_canonical_refined_chain_result",
            side_effect=AssertionError("producer called"),
        ):
            result = prepare_e1_canonical_refined_chain_wiring(REPORTS, UPSTREAM)

        self.assertEqual((110, 100), (
            result.probe_support_count, result.probe_completion_count
        ))
        self.assertEqual((
            ("r1", 100), ("r2", 200), ("r4", 400)
        ), result.probe_step_counts)
        self.assertTrue(result.formation_bound)
        self.assertTrue(result.probe_bound)
        self.assertTrue(result.composition_bound)
        self.assertFalse(result.execution_permitted)

    def test_full_producer_path_runs_only_with_all_inputs_substituted(self) -> None:
        binding = prepare_e1_refined_chain_canonical_producer(REPORTS, UPSTREAM)
        formation = _synthetic_formation(binding)
        probe = _synthetic_probe()
        with patch(
            "mcm_field_organism.e1_canonical_refined_chain_wiring."
            "produce_e1_canonical_refined_formation",
            return_value=formation,
        ), patch(
            "mcm_field_organism.e1_canonical_refined_chain_wiring."
            "_fixed_probe_sequences",
            return_value=probe,
        ), patch(
            "mcm_field_organism.e1_canonical_refined_chain_wiring."
            "build_e1_av_history_permutation",
            return_value=source(),
        ), patch(
            "mcm_field_organism.e1_canonical_refined_chain_wiring."
            "_fresh_canonical_field",
            side_effect=lambda unused: field(),
        ):
            result = produce_e1_canonical_refined_chain_result(binding)

        self.assertEqual(3, len(result.refinements))
        self.assertTrue(all(dict(result.controls).values()))

    def test_invalid_binding_fails_before_formation(self) -> None:
        with patch(
            "mcm_field_organism.e1_canonical_refined_chain_wiring."
            "produce_e1_canonical_refined_formation",
            side_effect=AssertionError("formation called"),
        ):
            with self.assertRaises(E1CanonicalRefinedChainWiringError):
                produce_e1_canonical_refined_chain_result(None)

    def test_producer_wires_all_three_private_stages(self) -> None:
        source_text = inspect.getsource(produce_e1_canonical_refined_chain_result)
        for role in (
            "produce_e1_canonical_refined_formation",
            "run_private_e1_refined_seven_arm_probe",
            "_compose_e1_refined_chain_result",
        ):
            self.assertIn(role, source_text)

    def test_preflight_keeps_registered_paths_free_and_roles_private(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        prepare_e1_canonical_refined_chain_wiring(REPORTS, UPSTREAM)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        self.assertEqual((False, False, False), before)
        for role in (
            "E1CanonicalRefinedChainWiring",
            "prepare_e1_canonical_refined_chain_wiring",
            "produce_e1_canonical_refined_chain_result",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
