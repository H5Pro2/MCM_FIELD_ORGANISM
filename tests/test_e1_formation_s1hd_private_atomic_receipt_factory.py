from __future__ import annotations

import inspect
import unittest

import tests.test_e1_formation_s1ha_pure_real_transition_builder as builder_fixture
import tests.test_e1_formation_s1hb_external_owner_origin_bridge as bridge_fixture

from mcm_field_organism.e1_formation_s1fw_synthetic_live_state_handoff import (
    _adapter_digest,
)
from mcm_field_organism.e1_formation_s1gn_live_field_carrier import (
    e1_formation_s1gn_current_field_digest,
)
from mcm_field_organism.e1_formation_s1ha_pure_real_transition_builder import (
    build_e1_formation_s1ha_pure_real_transition,
)
from mcm_field_organism.e1_formation_s1hb_external_owner_origin_bridge import (
    bind_e1_formation_s1hb_external_owner_authorization,
)
from mcm_field_organism.e1_formation_s1hc_real_single_use_token import (
    issue_e1_formation_s1hc_real_single_use_token,
)
from mcm_field_organism.e1_formation_s1hd_private_atomic_receipt_factory import (
    E1FormationS1HDCompletedAdapterBoundaryEvidence,
    E1FormationS1HDPrivateAtomicReceiptFactoryError,
    S1_HD_EVIDENCE_ID,
    _seal_e1_formation_s1hd_real_adapter_call_receipt,
)
from mcm_field_organism.e1_formation_s1gv_real_adapter_call_receipt_schema import (
    S1_GV_KERNEL_NAME,
)
from mcm_field_organism.e1_refined_formation_runner import (
    _digest,
    _state_payload,
)


class E1FormationS1HDPrivateAtomicReceiptFactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        builder = builder_fixture.E1FormationS1HAPureRealTransitionBuilderTests
        builder.setUpClass()
        bridge = bridge_fixture.E1FormationS1HBExternalOwnerOriginBridgeTests
        bridge.setUpClass()
        cls.bridge_source = bridge
        cls.fresh = builder.fresh
        cls.batch = builder.batch
        cls.carrier = builder.carrier
        cls.next_field = builder.next_field
        cls.gate = bridge.gate
        cls.target = bridge.target
        cls.message = bridge.message

    def setUp(self) -> None:
        unique = _digest((self.id(),))
        event = self.bridge_source._event(
            fresh_single_use_nonce_digest=unique,
            host_attestation_digest=_digest(("host", unique)),
        )
        self.authorization = bind_e1_formation_s1hb_external_owner_authorization(
            self.message,
            event,
            self.gate,
            self.target,
            origin_verifier=lambda _event: True,
        )
        self.token = issue_e1_formation_s1hc_real_single_use_token(
            self.authorization,
            self.gate,
            self.target,
        )
        self.token.consume()
        self.evidence = self._evidence()

    def tearDown(self) -> None:
        if not self.token.retired:
            self.token.retire("real-attempt-failure")

    def _evidence(self, **changes):
        state_digest = _digest(_state_payload(self.fresh.invocation.source_state))
        adapter_digest = _adapter_digest(self.fresh.invocation.fixed_adapter)
        values = {
            "evidence_id": S1_HD_EVIDENCE_ID,
            "authorization_digest": self.authorization.authorization_digest,
            "consumed_token_digest": self.token.token_digest,
            "gate_digest": self.gate.gate_digest,
            "binding_digest": self.fresh.binding_digest,
            "batch_index": self.batch.batch_index,
            "batch_step_start_tick": self.batch.step_time.start_tick,
            "batch_step_end_tick": self.batch.step_time.end_tick,
            "previous_carrier_digest": self.carrier.carrier_digest,
            "previous_field_digest": self.carrier.current_field_digest,
            "next_field_digest": e1_formation_s1gn_current_field_digest(
                self.next_field
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
        values.update(changes)
        return E1FormationS1HDCompletedAdapterBoundaryEvidence(
            **values,
            evidence_digest=_digest(values),
        )

    def _seal(self, *, evidence=None, token=None, next_field=None):
        return _seal_e1_formation_s1hd_real_adapter_call_receipt(
            self.authorization,
            self.token if token is None else token,
            self.gate,
            self.target,
            self.fresh,
            self.batch,
            self.carrier,
            self.next_field if next_field is None else next_field,
            self.evidence if evidence is None else evidence,
        )

    def test_seals_exact_gv_receipt_from_consumed_token(self) -> None:
        receipt = self._seal()
        self.assertEqual(self.authorization.authorization_digest, receipt.authorization_digest)
        self.assertEqual(self.token.token_digest, receipt.consumed_token_digest)
        self.assertEqual(self.gate.gate_digest, receipt.gate_digest)
        self.assertEqual(1, receipt.adapter_calls)
        self.assertEqual(1, receipt.field_steps_executed)

    def test_unconsumed_token_fails_closed(self) -> None:
        unique = _digest((self.id(), "unconsumed"))
        event = self.bridge_source._event(
            fresh_single_use_nonce_digest=unique,
            host_attestation_digest=_digest(("host", unique)),
        )
        authorization = bind_e1_formation_s1hb_external_owner_authorization(
            self.message,
            event,
            self.gate,
            self.target,
            origin_verifier=lambda _event: True,
        )
        token = issue_e1_formation_s1hc_real_single_use_token(
            authorization,
            self.gate,
            self.target,
        )
        with self.assertRaises(E1FormationS1HDPrivateAtomicReceiptFactoryError):
            _seal_e1_formation_s1hd_real_adapter_call_receipt(
                authorization,
                token,
                self.gate,
                self.target,
                self.fresh,
                self.batch,
                self.carrier,
                self.next_field,
                self.evidence,
            )
        token.retire("real-attempt-failure")

    def test_cross_bound_evidence_fails_closed(self) -> None:
        for evidence in (
            self._evidence(binding_digest="1" * 64),
            self._evidence(consumed_token_digest="2" * 64),
        ):
            with self.assertRaises(E1FormationS1HDPrivateAtomicReceiptFactoryError):
                self._seal(evidence=evidence)

    def test_wrong_next_field_fails_closed(self) -> None:
        with self.assertRaises(E1FormationS1HDPrivateAtomicReceiptFactoryError):
            self._seal(next_field=self.carrier.current_field)

    def test_receipt_is_accepted_by_pure_transition_builder(self) -> None:
        receipt = self._seal()
        transition = build_e1_formation_s1ha_pure_real_transition(
            self.fresh,
            self.batch,
            self.carrier,
            self.next_field,
            receipt,
        )
        self.assertEqual(receipt.next_field_digest, transition.next_field_digest)
        self.assertEqual(1, transition.actual_field_steps_executed)

    def test_receipt_remains_nonpersistent_and_claim_free(self) -> None:
        receipt = self._seal()
        self.assertFalse(receipt.persistence_performed)
        self.assertFalse(receipt.claims_permitted)
        self.assertTrue(receipt.token_consumed_before_adapter)

    def test_sealer_calls_no_token_consume_adapter_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            _seal_e1_formation_s1hd_real_adapter_call_receipt
        )
        for forbidden in (
            ".consume(",
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "build_e1_formation_s1ha_pure_real_transition(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
