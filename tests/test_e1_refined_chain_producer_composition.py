from __future__ import annotations

from dataclasses import replace
import hashlib
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_completion_aligned_refinement import (
    build_e1_completion_aligned_refinement_plans,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.e1_refined_chain_producer_composition import (
    E1RefinedChainProducerCompositionError,
    E1RefinedProbeCompositionResult,
    compose_synthetic_e1_refined_chain_result,
)
from mcm_field_organism.e1_refined_formation_runner import (
    run_synthetic_e1_refined_formation,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_a0_av_history_producer import contract, field, source


def _formation():
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
    return run_synthetic_e1_refined_formation(
        permutation, ab, ba, initial,
        build_neutral_e1_state(initial.layer, contract()),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


def _digest(role: str) -> str:
    return hashlib.sha256(role.encode("ascii")).hexdigest()


def _probe(formed):
    scale = 1.0 + (0.01 / formed.factor)
    from mcm_field_organism.e1_refined_chain_producer_composition import _state_digest
    return E1RefinedProbeCompositionResult(
        refinement_id=formed.refinement_id,
        factor=formed.factor,
        field_digests=tuple(
            (role, _digest(f"{formed.refinement_id}.{role}"))
            for role in (
                "p0", "ab_active", "ba_active", "ab_probe_ablated",
                "ba_probe_ablated", "ab_fixed", "ba_fixed",
            )
        ),
        ab_active_s=(scale, 0.25),
        ba_active_s=(0.25, scale),
        ab_active_h=(scale / 2.0, 0.125),
        ba_active_h=(0.125, scale / 2.0),
        post_probe_ab_state_digest=_state_digest(formed.b_ab),
        post_probe_ba_state_digest=_state_digest(formed.b_ba),
        probe_ablation_residual=0.0,
        fixed_adapter_residual=0.0,
        initial_fields_identical_and_separate=True,
        supports_assigned_once=True,
    )


class E1RefinedChainProducerCompositionTests(unittest.TestCase):
    def test_composition_consumes_three_formations_and_three_probes(self) -> None:
        calls = []
        def runner(formed):
            calls.append(formed.refinement_id)
            return _probe(formed)

        result = compose_synthetic_e1_refined_chain_result(_formation(), runner)

        self.assertEqual(["r1", "r2", "r4"], calls)
        self.assertEqual(("r1", "r2", "r4"), tuple(
            item.refinement_id for item in result.refinements
        ))
        self.assertEqual(13, len(result.metrics))
        self.assertEqual(11, len(result.controls))

    def test_composition_derives_exact_controls_and_digests(self) -> None:
        result = compose_synthetic_e1_refined_chain_result(_formation(), _probe)

        controls = dict(result.controls)
        self.assertTrue(all(controls.values()))
        self.assertEqual(0.0, dict(result.metrics)["identity_residual"])
        self.assertEqual(0.0, dict(result.metrics)["formation_ablation_residual"])
        for refinement in result.refinements:
            self.assertEqual(5, len(refinement.formation_state_digests))
            self.assertEqual(7, len(refinement.probe_field_digests))

    def test_changed_post_probe_state_fails_the_frozen_control(self) -> None:
        def changed(formed):
            return replace(_probe(formed), post_probe_ab_state_digest="0" * 64)

        result = compose_synthetic_e1_refined_chain_result(_formation(), changed)

        self.assertFalse(dict(result.controls)["all_formed_states_remain_frozen_during_probe"])
        self.assertEqual("TECHNICALLY_INVALID", result.technical_decision)

    def test_invalid_probe_inventory_and_noncallable_fail_closed(self) -> None:
        formation = _formation()
        with self.assertRaises(E1RefinedChainProducerCompositionError):
            compose_synthetic_e1_refined_chain_result(formation, None)
        with self.assertRaises(E1RefinedChainProducerCompositionError):
            replace(_probe(formation.refinements[0]), field_digests=())

    def test_composition_is_repeatable_and_private(self) -> None:
        first = compose_synthetic_e1_refined_chain_result(_formation(), _probe)
        second = compose_synthetic_e1_refined_chain_result(_formation(), _probe)

        self.assertEqual(first, second)
        for role in (
            "E1RefinedProbeCompositionResult",
            "compose_synthetic_e1_refined_chain_result",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
