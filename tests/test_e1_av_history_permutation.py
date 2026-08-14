from __future__ import annotations

import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_av_history_permutation import (
    E1AVHistoryPermutationError,
    build_e1_av_history_permutation,
    permute_reduced_av_history_blocks,
)
from mcm_field_organism.receptor_contract import CommonFieldTime
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


class E1AVHistoryPermutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build_e1_av_history_permutation()

    def test_warmup_yields_equal_a_and_b_frame_counts(self) -> None:
        audits = {item.modality_id: item for item in self.result.modality_audits}
        self.assertEqual((100, 100), (
            audits["auditory"].first_block_count,
            audits["auditory"].second_block_count,
        ))
        self.assertEqual((10, 10), (
            audits["visual"].first_block_count,
            audits["visual"].second_block_count,
        ))

    def test_every_required_inventory_is_exactly_preserved(self) -> None:
        for audit in self.result.modality_audits:
            with self.subTest(modality=audit.modality_id):
                self.assertEqual(
                    audit.payload_inventory_digest,
                    audit.permuted_payload_inventory_digest,
                )
                self.assertEqual(
                    audit.source_support_inventory_digest,
                    audit.permuted_source_support_inventory_digest,
                )
                self.assertEqual(
                    audit.organism_slot_inventory_digest,
                    audit.permuted_organism_slot_inventory_digest,
                )
                self.assertEqual(
                    audit.total_absolute_mass,
                    audit.permuted_total_absolute_mass,
                )
                self.assertEqual(
                    audit.quadratic_energy,
                    audit.permuted_quadratic_energy,
                )

    def test_ba_reuses_source_frames_and_only_changes_their_slots(self) -> None:
        for source, permuted in zip(
            self.result.history_ab,
            self.result.history_ba,
            strict=True,
        ):
            with self.subTest(modality=source.modality_id):
                self.assertEqual(
                    {id(item.frame) for item in source.frames},
                    {id(item.frame) for item in permuted.frames},
                )
                self.assertEqual(
                    tuple(item.field_time for item in source.frames),
                    tuple(item.field_time for item in permuted.frames),
                )
                half = len(source.frames) // 2
                self.assertEqual(
                    tuple(item.frame.snapshot_id for item in source.frames[half:]),
                    tuple(item.frame.snapshot_id for item in permuted.frames[:half]),
                )
                self.assertEqual(
                    tuple(item.frame.snapshot_id for item in source.frames[:half]),
                    tuple(item.frame.snapshot_id for item in permuted.frames[half:]),
                )

    def test_ordered_digests_differ_but_build_is_repeatable(self) -> None:
        repeated = build_e1_av_history_permutation()
        self.assertNotEqual(
            self.result.history_ab_digest,
            self.result.history_ba_digest,
        )
        self.assertEqual(
            self.result.history_ab_digest,
            repeated.history_ab_digest,
        )
        self.assertEqual(
            self.result.history_ba_digest,
            repeated.history_ba_digest,
        )
        self.assertEqual(
            self.result.permutation_digest,
            repeated.permutation_digest,
        )

    def test_unequal_blocks_are_rejected(self) -> None:
        source = self.result.history_ab
        auditory = source[0]
        shortened = ReceptorTimeSequence(
            auditory.modality_id,
            auditory.geometry_id,
            auditory.clock_id,
            auditory.frames[:-1],
        )
        with self.assertRaisesRegex(E1AVHistoryPermutationError, "equal"):
            permute_reduced_av_history_blocks((shortened, source[1]))

    def test_wrong_clock_and_split_are_rejected(self) -> None:
        source = self.result.history_ab
        auditory = source[0]
        wrong_clock = ReceptorTimeSequence(
            auditory.modality_id,
            auditory.geometry_id,
            "organism.wrong",
            tuple(
                OrganismTimedReceptorFrame(
                    item.frame,
                    CommonFieldTime(
                        "organism.wrong",
                        item.field_time.window_start_tick,
                        item.field_time.window_end_tick,
                    ),
                )
                for item in auditory.frames
            ),
        )
        with self.assertRaisesRegex(E1AVHistoryPermutationError, "S1-DE clock"):
            permute_reduced_av_history_blocks((wrong_clock, source[1]))
        with self.assertRaisesRegex(E1AVHistoryPermutationError, "positive"):
            permute_reduced_av_history_blocks(source, split_tick=0)

    def test_source_builder_has_no_field_or_e1_output(self) -> None:
        forbidden = {
            "field",
            "e1_state",
            "adapter",
            "memory",
            "meaning",
            "reward",
        }
        self.assertTrue(forbidden.isdisjoint(self.result.__dataclass_fields__))
        for role in (
            "E1AVHistoryPermutation",
            "build_e1_av_history_permutation",
            "permute_reduced_av_history_blocks",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
