from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_permutation_contract import (
    PublicAVReturnPermutationContractError,
    public_av_return_permutation_contract,
    public_av_return_permutation_contract_json_value,
    public_av_return_permutation_contract_public_roles,
)


class PublicAVReturnPermutationContractTests(unittest.TestCase):
    def test_mapping_is_deterministic_rank_reversal_per_modality(self) -> None:
        contract = public_av_return_permutation_contract()
        by_modality = {item.modality_id: item for item in contract.modality_mappings}
        self.assertEqual(tuple(reversed(range(41))), by_modality["auditory"].source_rank_to_time_slot_rank)
        self.assertEqual(tuple(reversed(range(15))), by_modality["visual"].source_rank_to_time_slot_rank)
        self.assertEqual("auditory.reverse_rank.v1", by_modality["auditory"].mapping_id)
        self.assertEqual("visual.reverse_rank.v1", by_modality["visual"].mapping_id)

    def test_event_time_contract_is_fixed_and_shifted_to_stage_two(self) -> None:
        contract = public_av_return_permutation_contract()
        event_time = contract.event_time_contract
        self.assertEqual("public.media.pts_ns", event_time.clock_id)
        self.assertEqual((600_000_000, 1_100_000_000), event_time.stage_two_interval_ticks)
        self.assertEqual(600_000_000, event_time.stage_two_tick_offset)
        self.assertEqual("preserve_original_sorted_time_slots_per_modality", event_time.time_slot_rule)
        self.assertEqual("no_new_overlap_no_time_jitter_no_resampling", event_time.overlap_policy)

    def test_permuted_sequence_digests_are_fixed_sha256(self) -> None:
        contract = public_av_return_permutation_contract()
        self.assertEqual(64, len(contract.auditory_permuted_sequence_digest))
        self.assertEqual(64, len(contract.visual_permuted_sequence_digest))
        self.assertEqual(64, len(contract.contract_digest))
        self.assertNotEqual(
            contract.source_stage_sequence_digest[0],
            contract.auditory_permuted_sequence_digest,
        )
        self.assertNotEqual(
            contract.source_stage_sequence_digest[1],
            contract.visual_permuted_sequence_digest,
        )

    def test_contract_does_not_release_runner_run_or_claims(self) -> None:
        contract = public_av_return_permutation_contract()
        self.assertTrue(contract.fully_specified)
        self.assertFalse(contract.runner_implementation_allowed)
        self.assertFalse(contract.replication_run_allowed)
        self.assertFalse(contract.artificial_media_events_introduced)
        self.assertFalse(contract.field_parameters_changed)
        with self.assertRaisesRegex(PublicAVReturnPermutationContractError, "cannot release"):
            replace(contract, runner_implementation_allowed=True)
        with self.assertRaisesRegex(PublicAVReturnPermutationContractError, "cannot release"):
            replace(contract, memory_claim_allowed=True)

    def test_json_and_roles_exclude_payloads_and_claim_scores(self) -> None:
        contract = public_av_return_permutation_contract()
        encoded = public_av_return_permutation_contract_json_value(contract)
        self.assertEqual("control.stage_two_order_permuted", encoded["arm_id"])
        forbidden = {
            "raw_samples",
            "pixels",
            "label",
            "reward",
            "memory_score",
            "organization_score",
        }
        self.assertTrue(forbidden.isdisjoint(public_av_return_permutation_contract_public_roles()))


if __name__ == "__main__":
    unittest.main()
