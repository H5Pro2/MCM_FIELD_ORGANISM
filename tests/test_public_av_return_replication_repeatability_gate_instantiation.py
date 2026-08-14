from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.public_av_return_permutation_contract import (
    public_av_return_permutation_contract,
)
from mcm_field_organism.public_av_return_replication_repeatability_executor_binding import (
    bind_public_av_return_replication_repeatability_slot_executors,
)
from mcm_field_organism.public_av_return_replication_repeatability_gate_instantiation import (
    PublicAVReturnReplicationRepeatabilityGateInstantiationError,
    instantiate_public_av_return_replication_repeatability_gates,
    public_av_return_replication_repeatability_gate_instantiation_to_jsonable,
    reserve_public_av_return_replication_repeatability_gate_instances,
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
    build_public_av_return_replication_repeatability_start_acceptance,
)
from mcm_field_organism.public_av_return_replication_runner import (
    wire_public_av_return_replication_runner,
)
from mcm_field_organism.public_media_source_contract import (
    PublicMediaSourceAudit,
    nasa_earthrise_av_source_contract,
)


class PublicAVReturnReplicationRepeatabilityGateInstantiationTests(unittest.TestCase):
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
        self.acceptance = build_public_av_return_replication_repeatability_start_acceptance(
            preflight=preflight,
            slot_start_contract=slot_start,
            executor_binding_contract=executor_binding,
        )

    def test_reserves_three_fresh_gate_and_executor_identities(self) -> None:
        contract = reserve_public_av_return_replication_repeatability_gate_instances(
            self.acceptance
        )
        self.assertEqual(
            (1, 2, 3),
            tuple(item.repeat_index for item in contract.slot_gate_instantiations),
        )
        self.assertTrue(contract.all_reserved_gate_ids_unique)
        self.assertTrue(contract.all_reserved_executor_ids_unique)
        self.assertTrue(contract.fresh_gate_per_slot_required)
        self.assertFalse(contract.gate_instances_created)
        self.assertFalse(contract.executor_callables_created)

    def test_carries_start_acceptance_gate_and_executor_identities(self) -> None:
        contract = reserve_public_av_return_replication_repeatability_gate_instances(
            self.acceptance
        )
        for accepted, reserved in zip(
            self.acceptance.slot_acceptances,
            contract.slot_gate_instantiations,
            strict=True,
        ):
            self.assertEqual(accepted.acceptance_id, reserved.slot_acceptance_id)
            self.assertEqual(
                accepted.future_one_shot_entrypoint_id,
                reserved.reserved_one_shot_gate_id,
            )
            self.assertEqual(accepted.future_executor_id, reserved.reserved_executor_id)
            self.assertTrue(reserved.start_acceptance_bound)
            self.assertTrue(reserved.one_shot_gate_identity_reserved)

    def test_acceptance_with_created_gate_is_rejected(self) -> None:
        with self.assertRaisesRegex(Exception, "non-executable|fresh|uninstantiated"):
            altered_slot = replace(
                self.acceptance.slot_acceptances[0],
                gate_instance_created=True,
            )
            altered = replace(
                self.acceptance,
                slot_acceptances=(altered_slot, *self.acceptance.slot_acceptances[1:]),
            )
            reserve_public_av_return_replication_repeatability_gate_instances(altered)

    def test_instantiation_start_and_claim_surfaces_remain_locked(self) -> None:
        contract = reserve_public_av_return_replication_repeatability_gate_instances(
            self.acceptance
        )
        for role in (
            "gate_instances_created",
            "executor_callables_created",
            "executor_binding_performed",
            "start_release_granted",
            "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaisesRegex(
                PublicAVReturnReplicationRepeatabilityGateInstantiationError,
                "cannot create",
            ):
                replace(contract, **{role: True})
        with self.assertRaisesRegex(
            PublicAVReturnReplicationRepeatabilityGateInstantiationError,
            "not released",
        ):
            instantiate_public_av_return_replication_repeatability_gates(contract)

    def test_json_contract_contains_no_execution_results_or_claim_scores(self) -> None:
        payload = public_av_return_replication_repeatability_gate_instantiation_to_jsonable(
            reserve_public_av_return_replication_repeatability_gate_instances(
                self.acceptance
            )
        )
        self.assertEqual(len(payload["slot_gate_instantiations"]), 3)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)
        self.assertNotIn("organization_score", payload)


if __name__ == "__main__":
    unittest.main()
