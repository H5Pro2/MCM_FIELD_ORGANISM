from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_a0_av_history_producer import (
    E1A0AVHistoryProducerError,
    _produce_e1_a0_av_histories,
    produce_e1_a0_av_histories,
)
from mcm_field_organism.e1_av_history_permutation import (
    build_e1_av_history_permutation,
    permute_reduced_av_history_blocks,
)
from mcm_field_organism.e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1EdgeBinding,
    E1LocalEdgePlasticityContract,
    E1LocalEdgePlasticityState,
    build_neutral_e1_state,
)
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
)
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from mcm_field_organism.shared_mcm_field import (
    ReceptorDockAnatomy,
    build_shared_mcm_field,
)


CLOCK_ID = "organism.e1.av-history"
RATE = 1_000_000.0


def frame(modality_id: str, block: str, value: float) -> ReceptorContactFrame:
    index = 0 if block == "a" else 1
    return ReceptorContactFrame(
        modality_id=modality_id,
        geometry_id=f"{modality_id}.synthetic.s1dg",
        snapshot_id=f"{modality_id}.{block}",
        clock_id=f"{modality_id}.source.s1dg",
        window_start_tick=index * 100,
        window_end_tick=(index + 1) * 100,
        carrier_ids=(f"{modality_id}.carrier.0",),
        values=(value,),
    )


def sequence(
    modality_id: str,
    first: float,
    second: float,
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality_id,
        f"{modality_id}.synthetic.s1dg",
        CLOCK_ID,
        (
            OrganismTimedReceptorFrame(
                frame(modality_id, "a", first),
                CommonFieldTime(CLOCK_ID, 0, 1_000_000),
            ),
            OrganismTimedReceptorFrame(
                frame(modality_id, "b", second),
                CommonFieldTime(CLOCK_ID, 1_000_000, 2_000_000),
            ),
        ),
    )


def source():
    return permute_reduced_av_history_blocks(
        (
            sequence("auditory", 0.8, -0.25),
            sequence("visual", -0.6, 0.35),
        )
    )


def field():
    history = source().history_ab
    return build_shared_mcm_field(
        (history[0].frames[0].frame, history[1].frames[0].frame),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,),),
            ),
            "visual": ReceptorDockAnatomy(
                "visual",
                "dock.visual",
                ((1,),),
            ),
        },
        sample_offsets=((-1,), (1,)),
    )


def contract() -> E1LocalEdgePlasticityContract:
    return E1LocalEdgePlasticityContract(
        E1_CONTRACT_ID,
        1.0,
        1.5,
        0.25,
        0.5,
    )


def produce():
    initial = field()
    state = build_neutral_e1_state(initial.layer, contract())
    return _produce_e1_a0_av_histories(
        source(),
        initial,
        state,
        (MCMFieldStepTime(CLOCK_ID, 0, 2_000_000, RATE),),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


class E1A0AVHistoryProducerTests(unittest.TestCase):
    def test_synthetic_histories_preserve_each_p0_a0_identity(self) -> None:
        result = produce()

        self.assertEqual(("ab", "ba"), tuple(
            item.history_id for item in result.arm_audits
        ))
        for audit in result.arm_audits:
            with self.subTest(history=audit.history_id):
                self.assertEqual(audit.p0_field_digest, audit.a0_field_digest)
                self.assertEqual(4, audit.source_support_count)
                self.assertEqual(4, audit.assigned_event_count)
                self.assertLessEqual(audit.resource_budget_error, 1e-12)
                self.assertTrue(audit.all_adapters_ablated)

    def test_only_separate_e1_end_states_and_audits_leave_the_core(self) -> None:
        result = produce()

        self.assertIsNot(result.b_ab, result.b_ba)
        forbidden = {
            "field",
            "ab_field",
            "ba_field",
            "snapshot",
            "last_distribution",
            "probe",
            "adapter",
        }
        self.assertTrue(forbidden.isdisjoint(result.__dataclass_fields__))

    def test_initial_field_and_e1_state_remain_unchanged(self) -> None:
        initial = field()
        state = build_neutral_e1_state(initial.layer, contract())
        layer_digest = initial.layer.digest()

        _produce_e1_a0_av_histories(
            source(),
            initial,
            state,
            (MCMFieldStepTime(CLOCK_ID, 0, 2_000_000, RATE),),
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
        )

        self.assertEqual(layer_digest, initial.layer.digest())
        self.assertIsNone(initial.last_distribution)
        self.assertTrue(all(item.binding == 0.0 for item in state.edge_bindings))

    def test_non_neutral_start_and_changed_runtime_contract_fail_closed(self) -> None:
        initial = field()
        neutral = build_neutral_e1_state(initial.layer, contract())
        edge = neutral.edge_bindings[0]
        non_neutral = E1LocalEdgePlasticityState(
            neutral.contract,
            (E1EdgeBinding(edge.first_neuron_id, edge.second_neuron_id, 0.1),),
            neutral.edge_inventory_digest,
        )
        with self.assertRaisesRegex(E1A0AVHistoryProducerError, "neutral"):
            _produce_e1_a0_av_histories(
                source(),
                initial,
                non_neutral,
                (MCMFieldStepTime(CLOCK_ID, 0, 2_000_000, RATE),),
                NeutralLocalFieldSubstrateConfig(1.0),
                NeutralFastAfterimageConfig(0.5),
            )
        with self.assertRaisesRegex(E1A0AVHistoryProducerError, "H time"):
            _produce_e1_a0_av_histories(
                source(),
                initial,
                neutral,
                (MCMFieldStepTime(CLOCK_ID, 0, 2_000_000, RATE),),
                NeutralLocalFieldSubstrateConfig(1.0),
                NeutralFastAfterimageConfig(0.75),
            )

    def test_synthetic_production_is_repeatable(self) -> None:
        first = produce()
        second = produce()

        self.assertEqual(first.production_digest, second.production_digest)
        self.assertEqual(first.b_ab, second.b_ab)
        self.assertEqual(first.b_ba, second.b_ba)

    def test_canonical_entry_preflights_84_nodes_without_history_execution(self) -> None:
        canonical = build_e1_av_history_permutation()
        sentinel = object()
        with patch(
            "mcm_field_organism.e1_a0_av_history_producer._produce_e1_a0_av_histories",
            return_value=sentinel,
        ) as core:
            result = produce_e1_a0_av_histories(canonical)

        self.assertIs(sentinel, result)
        args = core.call_args.args
        self.assertEqual(84, len(args[1].layer.neurons))
        self.assertTrue(all(item.binding == 0.0 for item in args[2].edge_bindings))
        self.assertEqual(
            (MCMFieldStepTime(CLOCK_ID, 0, 2_000_000, RATE),),
            args[3],
        )

    def test_changed_canonical_digest_and_public_exports_are_rejected(self) -> None:
        changed = replace(
            build_e1_av_history_permutation(),
            history_ab_digest="0" * 64,
        )
        with self.assertRaisesRegex(E1A0AVHistoryProducerError, "digest"):
            produce_e1_a0_av_histories(changed)
        for role in (
            "E1A0AVHistoryProduction",
            "produce_e1_a0_av_histories",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
