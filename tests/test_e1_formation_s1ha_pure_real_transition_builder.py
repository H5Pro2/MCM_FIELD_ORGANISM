from __future__ import annotations

import inspect
import unittest

import tests.test_e1_formation_s1gx_deterministic_single_batch_target as target_fixture

from mcm_field_organism.e1_formation_s1fw_synthetic_live_state_handoff import (
    _adapter_digest,
)
from mcm_field_organism.e1_formation_s1gn_live_field_carrier import (
    e1_formation_s1gn_current_field_digest,
)
from mcm_field_organism.e1_formation_s1gq_carrier_transition_schema import (
    bind_e1_formation_s1gq_carrier_transition_envelope,
)
from mcm_field_organism.e1_formation_s1gv_real_adapter_call_receipt_schema import (
    E1FormationS1GVRealAdapterCallReceipt,
    S1_GV_KERNEL_NAME,
    S1_GV_RECEIPT_ID,
)
from mcm_field_organism.e1_formation_s1ha_pure_real_transition_builder import (
    E1FormationS1HAPureRealTransitionBuilderError,
    build_e1_formation_s1ha_pure_real_transition,
)
from mcm_field_organism.e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
)
from mcm_field_organism.e1_refined_formation_runner import (
    _digest,
    _state_payload,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from mcm_field_organism.receptor_contract import CommonFieldTime
from mcm_field_organism.receptor_distributor import ReceptorDistribution
from mcm_field_organism.transient_dock_trajectory import (
    map_proposal_batch_to_transient_docks,
)
from mcm_field_organism.transient_neuron_input import (
    project_transient_docks_to_neuron_inputs,
)


class E1FormationS1HAPureRealTransitionBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = target_fixture.E1FormationS1GXDeterministicSingleBatchTargetTests
        source.setUpClass()
        target = source()._select()
        cls.fresh = target.selected_fresh_binding
        cls.batch = target.selected_batch
        cls.carrier = target.selected_initial_carrier
        cls.gate = source.gate
        trajectory = map_proposal_batch_to_transient_docks(
            cls.batch,
            cls.carrier.current_field.docks,
        )
        transient_inputs = project_transient_docks_to_neuron_inputs(
            trajectory,
            cls.carrier.current_field.docks,
        )
        step = cls.batch.step_time
        distribution = ReceptorDistribution(
            CommonFieldTime(step.clock_id, step.start_tick, step.end_tick),
            (),
        )
        cls.next_field = advance_fixed_e1_adapter_fast_shared_field_transient(
            cls.carrier.current_field,
            cls.fresh.invocation.fixed_adapter,
            distribution,
            transient_inputs,
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
        )
        cls.receipt = cls._synthetic_receipt()

    @classmethod
    def _synthetic_receipt(cls):
        state_digest = _digest(_state_payload(cls.fresh.invocation.source_state))
        adapter_digest = _adapter_digest(cls.fresh.invocation.fixed_adapter)
        values = {
            "receipt_id": S1_GV_RECEIPT_ID,
            "gate_digest": cls.gate.gate_digest,
            "authorization_digest": _digest(("s1ha-synthetic-auth",)),
            "consumed_token_digest": _digest(("s1ha-synthetic-token",)),
            "binding_digest": cls.fresh.binding_digest,
            "batch_index": cls.batch.batch_index,
            "batch_step_start_tick": cls.batch.step_time.start_tick,
            "batch_step_end_tick": cls.batch.step_time.end_tick,
            "previous_carrier_digest": cls.carrier.carrier_digest,
            "previous_field_digest": cls.carrier.current_field_digest,
            "next_field_digest": e1_formation_s1gn_current_field_digest(
                cls.next_field
            ),
            "source_state_digest_before": state_digest,
            "source_state_digest_after": state_digest,
            "fixed_adapter_digest_before": adapter_digest,
            "fixed_adapter_digest_after": adapter_digest,
            "kernel_name": S1_GV_KERNEL_NAME,
            "token_consumed_before_adapter": True,
            "next_field_object_replaced": True,
            "adapter_calls": 1,
            "field_steps_executed": 1,
            "persistence_performed": False,
            "claims_permitted": False,
        }
        return E1FormationS1GVRealAdapterCallReceipt(
            **values,
            receipt_digest=_digest(values),
        )

    def _receipt(self, **changes):
        values = {
            name: getattr(self.receipt, name)
            for name in self.receipt.__dataclass_fields__
            if name != "receipt_digest"
        }
        values.update(changes)
        return E1FormationS1GVRealAdapterCallReceipt(
            **values,
            receipt_digest=_digest(values),
        )

    def _build(self, **changes):
        receipt = self._receipt(**changes) if changes else self.receipt
        return build_e1_formation_s1ha_pure_real_transition(
            self.fresh,
            self.batch,
            self.carrier,
            self.next_field,
            receipt,
        )

    def test_builds_one_real_transition_and_shared_envelope(self) -> None:
        transition = self._build()
        envelope = bind_e1_formation_s1gq_carrier_transition_envelope(
            transition
        )
        self.assertEqual("real-field-advance", envelope.transition_kind)
        self.assertEqual(1, transition.actual_field_steps_executed)
        self.assertTrue(transition.field_object_replaced)
        self.assertIs(transition.previous_carrier, self.carrier)
        self.assertIs(transition.next_carrier.current_field, self.next_field)

    def test_next_carrier_accounting_is_exact(self) -> None:
        transition = self._build()
        next_carrier = transition.next_carrier
        self.assertEqual(1, next_carrier.completed_batch_count)
        self.assertEqual(self.batch.event_count, next_carrier.accounted_source_support_count)
        self.assertEqual(1, next_carrier.actual_field_steps_executed)
        self.assertEqual(
            e1_formation_s1gn_current_field_digest(self.next_field),
            next_carrier.current_field_digest,
        )

    def test_builder_is_deterministic_for_same_completed_evidence(self) -> None:
        first = self._build()
        second = self._build()
        self.assertEqual(first.transition_digest, second.transition_digest)
        self.assertEqual(first.next_carrier.carrier_digest, second.next_carrier.carrier_digest)

    def test_cross_bound_receipt_fails_closed(self) -> None:
        with self.assertRaises(E1FormationS1HAPureRealTransitionBuilderError):
            self._build(binding_digest="1" * 64)
        with self.assertRaises(E1FormationS1HAPureRealTransitionBuilderError):
            self._build(gate_digest="2" * 64)

    def test_wrong_field_or_attestation_fails_closed(self) -> None:
        with self.assertRaises(E1FormationS1HAPureRealTransitionBuilderError):
            build_e1_formation_s1ha_pure_real_transition(
                self.fresh,
                self.batch,
                self.carrier,
                self.carrier.current_field,
                self.receipt,
            )
        with self.assertRaises(E1FormationS1HAPureRealTransitionBuilderError):
            self._build(
                source_state_digest_before="3" * 64,
                source_state_digest_after="3" * 64,
            )

    def test_result_does_not_persist_or_claim(self) -> None:
        transition = self._build()
        self.assertFalse(transition.persistence_performed)
        self.assertFalse(transition.claims_permitted)
        self.assertEqual(1, transition.accounted_field_steps)

    def test_builder_calls_no_adapter_kernel_token_authorization_or_writer(self) -> None:
        source = inspect.getsource(build_e1_formation_s1ha_pure_real_transition)
        for forbidden in (
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "E1FormationS1GWExternalOwnerAuthorization(",
            "issue_e1_formation_s1gt_synthetic_single_use_token(",
            "E1FormationS1GVRealAdapterCallReceipt(",
            ".consume(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
