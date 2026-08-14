from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_callable_gate_binding_acceptance import (
    accept_public_av_return_replication_repeatability_callable_gate_bindings,
)
from mcm_field_organism.public_av_return_replication_repeatability_final_orchestration import (
    PublicAVReturnReplicationRepeatabilityFinalOrchestrationError,
    orchestrate_public_av_return_replication_repeatability_candidates,
    public_av_return_replication_repeatability_final_orchestration_to_jsonable,
    start_public_av_return_replication_repeatability_orchestration,
)
from tests.test_public_av_return_replication_repeatability_callable_gate_binding_acceptance import (
    PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilityFinalOrchestrationTests(
    PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.binding_acceptance = (
            accept_public_av_return_replication_repeatability_callable_gate_bindings(
                self.callable_preparation
            )
        )

    def test_exposes_exactly_three_ordered_start_candidates(self) -> None:
        contract = orchestrate_public_av_return_replication_repeatability_candidates(
            self.binding_acceptance
        )
        self.assertEqual((1, 2, 3), contract.candidate_order)
        self.assertEqual(
            (1, 2, 3),
            tuple(item.repeat_index for item in contract.ordered_start_candidates),
        )
        self.assertTrue(contract.final_orchestration_contract_complete)

    def test_carries_binding_callable_gate_and_executor_identities(self) -> None:
        contract = orchestrate_public_av_return_replication_repeatability_candidates(
            self.binding_acceptance
        )
        for accepted, candidate in zip(
            self.binding_acceptance.slot_binding_acceptances,
            contract.ordered_start_candidates,
            strict=True,
        ):
            self.assertEqual(accepted.binding_acceptance_id, candidate.binding_acceptance_id)
            self.assertEqual(accepted.future_callable_id, candidate.future_callable_id)
            self.assertEqual(accepted.reserved_gate_id, candidate.reserved_gate_id)
            self.assertEqual(accepted.reserved_executor_id, candidate.reserved_executor_id)

    def test_rejects_nonfresh_binding_acceptance(self) -> None:
        with self.assertRaises(Exception):
            altered_slot = replace(
                self.binding_acceptance.slot_binding_acceptances[0],
                callable_object_created=True,
            )
            replace(
                self.binding_acceptance,
                slot_binding_acceptances=(
                    altered_slot,
                    *self.binding_acceptance.slot_binding_acceptances[1:],
                ),
            )

    def test_object_scheduler_start_and_claim_surfaces_remain_locked(self) -> None:
        contract = orchestrate_public_av_return_replication_repeatability_candidates(
            self.binding_acceptance
        )
        for role in (
            "callable_objects_created",
            "gate_instances_created",
            "bindings_performed",
            "scheduler_created",
            "automatic_transition_available",
            "start_release_granted",
            "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(
                PublicAVReturnReplicationRepeatabilityFinalOrchestrationError
            ):
                replace(contract, **{role: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilityFinalOrchestrationError
        ):
            start_public_av_return_replication_repeatability_orchestration(contract)

    def test_json_contains_no_scheduler_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_final_orchestration_to_jsonable(
            orchestrate_public_av_return_replication_repeatability_candidates(
                self.binding_acceptance
            )
        )
        self.assertEqual(len(payload["ordered_start_candidates"]), 3)
        self.assertNotIn("scheduler", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
