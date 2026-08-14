from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_callable_gate_binding_acceptance import (
    PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError,
    accept_public_av_return_replication_repeatability_callable_gate_bindings,
    bind_public_av_return_replication_repeatability_callables_to_gates,
    public_av_return_replication_repeatability_callable_gate_binding_acceptance_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_callable_preparation import (
    prepare_public_av_return_replication_repeatability_executor_callables,
)
from mcm_field_organism.public_av_return_replication_repeatability_gate_instantiation import (
    reserve_public_av_return_replication_repeatability_gate_instances,
)
from tests.test_public_av_return_replication_repeatability_start_acceptance import (
    PublicAVReturnReplicationRepeatabilityStartAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceTests(
    PublicAVReturnReplicationRepeatabilityStartAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.start_acceptance = self.build_acceptance()
        self.gate_contract = reserve_public_av_return_replication_repeatability_gate_instances(
            self.start_acceptance
        )
        self.callable_preparation = prepare_public_av_return_replication_repeatability_executor_callables(
            self.gate_contract
        )

    def test_accepts_three_unique_callable_gate_pairings(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_callable_gate_bindings(
            self.callable_preparation
        )
        self.assertEqual(
            (1, 2, 3),
            tuple(item.repeat_index for item in acceptance.slot_binding_acceptances),
        )
        self.assertTrue(acceptance.all_callable_gate_pairings_unique)
        self.assertTrue(acceptance.all_callable_ids_unique)
        self.assertTrue(acceptance.all_gate_ids_unique)
        self.assertTrue(acceptance.binding_acceptance_complete)

    def test_carries_callable_executor_and_gate_identities(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_callable_gate_bindings(
            self.callable_preparation
        )
        for prepared, accepted in zip(
            self.callable_preparation.slot_callable_preparations,
            acceptance.slot_binding_acceptances,
            strict=True,
        ):
            self.assertEqual(prepared.future_callable_id, accepted.future_callable_id)
            self.assertEqual(prepared.reserved_executor_id, accepted.reserved_executor_id)
            self.assertEqual(prepared.reserved_gate_id, accepted.reserved_gate_id)
            self.assertTrue(accepted.callable_identity_matches)
            self.assertTrue(accepted.executor_identity_matches)
            self.assertTrue(accepted.gate_identity_matches)

    def test_rejects_nonfresh_callable_preparation(self) -> None:
        with self.assertRaises(Exception):
            altered_slot = replace(
                self.callable_preparation.slot_callable_preparations[0],
                callable_object_created=True,
            )
            altered = replace(
                self.callable_preparation,
                slot_callable_preparations=(
                    altered_slot,
                    *self.callable_preparation.slot_callable_preparations[1:],
                ),
            )
            accept_public_av_return_replication_repeatability_callable_gate_bindings(
                altered
            )

    def test_duplicate_callable_gate_pairing_is_rejected(self) -> None:
        first = self.callable_preparation.slot_callable_preparations[0]
        with self.assertRaisesRegex(
            Exception,
            "identity|repeat_index",
        ):
            replace(
                self.callable_preparation.slot_callable_preparations[1],
                future_callable_id=first.future_callable_id,
                reserved_gate_id=first.reserved_gate_id,
            )

    def test_binding_start_and_claim_surfaces_remain_locked(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_callable_gate_bindings(
            self.callable_preparation
        )
        for role in (
            "callable_objects_created",
            "gate_instances_created",
            "callable_gate_binding_performed",
            "executor_binding_performed",
            "start_release_granted",
            "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(
                PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError
            ):
                replace(acceptance, **{role: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError
        ):
            bind_public_av_return_replication_repeatability_callables_to_gates(
                acceptance
            )

    def test_json_has_no_objects_results_or_claim_scores(self) -> None:
        payload = public_av_return_replication_repeatability_callable_gate_binding_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_callable_gate_bindings(
                self.callable_preparation
            )
        )
        self.assertEqual(len(payload["slot_binding_acceptances"]), 3)
        self.assertNotIn("object", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)
        self.assertNotIn("organization_score", payload)


if __name__ == "__main__":
    unittest.main()
