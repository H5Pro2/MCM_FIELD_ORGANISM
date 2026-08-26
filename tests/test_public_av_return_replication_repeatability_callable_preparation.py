from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_callable_preparation import (
    PublicAVReturnReplicationRepeatabilityCallablePreparationError,
    create_public_av_return_replication_repeatability_executor_callables,
    prepare_public_av_return_replication_repeatability_executor_callables,
    public_av_return_replication_repeatability_callable_preparation_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_gate_instantiation import (
    PublicAVReturnReplicationRepeatabilityGateInstantiationTests,
)


class PublicAVReturnReplicationRepeatabilityCallablePreparationTests(
    PublicAVReturnReplicationRepeatabilityGateInstantiationTests
):
    def setUp(self) -> None:
        super().setUp()
        from mcm_field_organism.public_av_return_replication_repeatability_gate_instantiation import (
            reserve_public_av_return_replication_repeatability_gate_instances,
        )

        self.gate_contract = reserve_public_av_return_replication_repeatability_gate_instances(
            self.acceptance
        )

    def test_prepares_three_unique_callable_identities(self) -> None:
        contract = prepare_public_av_return_replication_repeatability_executor_callables(
            self.gate_contract
        )
        self.assertEqual(
            (1, 2, 3),
            tuple(item.repeat_index for item in contract.slot_callable_preparations),
        )
        self.assertTrue(contract.all_future_callable_ids_unique)
        self.assertTrue(contract.all_three_gate_reservations_bound)

    def test_carries_reserved_gate_and_executor_identities(self) -> None:
        contract = prepare_public_av_return_replication_repeatability_executor_callables(
            self.gate_contract
        )
        for reserved, prepared in zip(
            self.gate_contract.slot_gate_instantiations,
            contract.slot_callable_preparations,
            strict=True,
        ):
            self.assertEqual(reserved.reserved_one_shot_gate_id, prepared.reserved_gate_id)
            self.assertEqual(reserved.reserved_executor_id, prepared.reserved_executor_id)
            self.assertTrue(prepared.callable_identity_reserved)

    def test_rejects_nonfresh_gate_reservation(self) -> None:
        with self.assertRaises(Exception):
            altered_slot = replace(
                self.gate_contract.slot_gate_instantiations[0],
                executor_callable_created=True,
            )
            altered = replace(
                self.gate_contract,
                slot_gate_instantiations=(
                    altered_slot,
                    *self.gate_contract.slot_gate_instantiations[1:],
                ),
            )
            prepare_public_av_return_replication_repeatability_executor_callables(
                altered
            )

    def test_callable_binding_run_and_claim_surfaces_remain_locked(self) -> None:
        contract = prepare_public_av_return_replication_repeatability_executor_callables(
            self.gate_contract
        )
        for role in (
            "callable_objects_created",
            "callable_factories_created",
            "gate_instances_created",
            "callable_gate_binding_performed",
            "start_release_granted",
            "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(
                PublicAVReturnReplicationRepeatabilityCallablePreparationError
            ):
                replace(contract, **{role: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilityCallablePreparationError
        ):
            create_public_av_return_replication_repeatability_executor_callables(
                contract
            )

    def test_json_has_no_callable_objects_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_callable_preparation_to_jsonable(
            prepare_public_av_return_replication_repeatability_executor_callables(
                self.gate_contract
            )
        )
        self.assertEqual(len(payload["slot_callable_preparations"]), 3)
        self.assertNotIn("callable", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
