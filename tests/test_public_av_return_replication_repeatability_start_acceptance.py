from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_permutation_contract import (
    public_av_return_permutation_contract,
)
from mcm_field_organism.public_av_return_replication_repeatability_executor_binding import (
    bind_public_av_return_replication_repeatability_slot_executors,
)
from mcm_field_organism.public_av_return_replication_repeatability_preflight import (
    audit_public_av_return_replication_repeatability_preflight,
)
from mcm_field_organism.public_av_return_replication_repeatability_runner import (
    wire_public_av_return_replication_repeatability_runner,
)
from mcm_field_organism.public_av_return_replication_repeatability_slot_start import (
    bind_public_av_return_replication_repeatability_slots,
)
from mcm_field_organism.public_av_return_replication_repeatability_start_acceptance import (
    PublicAVReturnReplicationRepeatabilityStartAcceptanceError,
    build_public_av_return_replication_repeatability_start_acceptance,
    public_av_return_replication_repeatability_start_acceptance_to_jsonable,
    start_public_av_return_replication_repeatability_from_acceptance,
)
from mcm_field_organism.public_av_return_replication_runner import (
    wire_public_av_return_replication_runner,
)
from mcm_field_organism.public_media_source_contract import (
    PublicMediaSourceAudit,
    nasa_earthrise_av_source_contract,
)
from pathlib import Path


class PublicAVReturnReplicationRepeatabilityStartAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        source = nasa_earthrise_av_source_contract()
        source_audit = PublicMediaSourceAudit(
            source.source_id,
            True,
            True,
            True,
            True,
            source.expected_size_bytes,
            source.expected_sha1,
        )
        path = Path("synthetic-contract-only.mp4")
        permutation = public_av_return_permutation_contract()
        base_runner = wire_public_av_return_replication_runner(
            permutation_contract=permutation
        )
        repeatability_runner = wire_public_av_return_replication_repeatability_runner(
            base_wiring=base_runner
        )
        preflight = audit_public_av_return_replication_repeatability_preflight(
            path,
            source_audit=source_audit,
            repeatability_wiring=repeatability_runner,
            base_wiring=base_runner,
            permutation_contract=permutation,
        )
        slot_start = bind_public_av_return_replication_repeatability_slots(
            repeatability_runner,
            preflight,
        )
        executor_binding = (
            bind_public_av_return_replication_repeatability_slot_executors(
                slot_start,
                base_runner,
                permutation,
            )
        )
        self.preflight = preflight
        self.slot_start = slot_start
        self.executor_binding = executor_binding

    def build_acceptance(self):
        return build_public_av_return_replication_repeatability_start_acceptance(
            preflight=self.preflight,
            slot_start_contract=self.slot_start,
            executor_binding_contract=self.executor_binding,
        )

    def test_accepts_three_ordered_consistent_slots(self) -> None:
        acceptance = self.build_acceptance()
        self.assertEqual(
            tuple(slot.repeat_index for slot in acceptance.slot_acceptances),
            (1, 2, 3),
        )
        self.assertTrue(acceptance.all_three_slots_consistent)
        self.assertTrue(acceptance.start_acceptance_complete)

    def test_keeps_future_gates_unique_unconsumed_and_uninstantiated(self) -> None:
        acceptance = self.build_acceptance()
        self.assertTrue(acceptance.all_three_one_shot_releases_unconsumed)
        self.assertTrue(acceptance.all_future_gate_ids_unique)
        self.assertTrue(acceptance.all_future_executor_ids_unique)
        self.assertFalse(acceptance.gate_instances_created)
        self.assertTrue(
            all(slot.fresh_one_shot_gate_required for slot in acceptance.slot_acceptances)
        )

    def test_rejects_executor_to_entrypoint_identity_mismatch(self) -> None:
        first = replace(
            self.executor_binding.slot_executor_bindings[0],
            one_shot_entrypoint_id="mismatched.entrypoint.repeat-1.v1",
        )
        bad_binding = replace(
            self.executor_binding,
            slot_executor_bindings=(
                first,
                *self.executor_binding.slot_executor_bindings[1:],
            ),
        )
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilityStartAcceptanceError
        ):
            build_public_av_return_replication_repeatability_start_acceptance(
                preflight=self.preflight,
                slot_start_contract=self.slot_start,
                executor_binding_contract=bad_binding,
            )

    def test_start_and_claim_surfaces_remain_locked(self) -> None:
        acceptance = self.build_acceptance()
        self.assertFalse(acceptance.executor_callables_created)
        self.assertFalse(acceptance.executor_binding_allowed)
        self.assertFalse(acceptance.start_release_granted)
        self.assertFalse(acceptance.repeatability_run_allowed)
        self.assertFalse(acceptance.stability_threshold_defined)
        self.assertFalse(acceptance.memory_claim_allowed)
        self.assertFalse(acceptance.organization_claim_allowed)
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilityStartAcceptanceError
        ):
            start_public_av_return_replication_repeatability_from_acceptance(acceptance)

    def test_json_contract_contains_no_results_or_claim_scores(self) -> None:
        payload = public_av_return_replication_repeatability_start_acceptance_to_jsonable(
            self.build_acceptance()
        )
        self.assertEqual(len(payload["slot_acceptances"]), 3)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)
        self.assertNotIn("organization_score", payload)


if __name__ == "__main__":
    unittest.main()
