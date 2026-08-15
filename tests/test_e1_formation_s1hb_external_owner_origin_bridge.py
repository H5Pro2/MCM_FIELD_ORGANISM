from __future__ import annotations

import inspect
import unittest

import tests.test_e1_formation_s1gx_deterministic_single_batch_target as target_fixture

from mcm_field_organism.e1_formation_s1gw_external_owner_authorization_schema import (
    S1_GW_PROJECT_ID,
    S1_GW_REQUIRED_OWNER_CLAUSES,
)
from mcm_field_organism.e1_formation_s1hb_external_owner_origin_bridge import (
    E1FormationS1HBExternalOwnerOriginBridgeError,
    E1FormationS1HBExternalOwnerOriginEvent,
    S1_HB_EVENT_ID,
    S1_HB_ORIGIN_KIND,
    bind_e1_formation_s1hb_external_owner_authorization,
)
from mcm_field_organism.e1_refined_formation_runner import _digest


class E1FormationS1HBExternalOwnerOriginBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = target_fixture.E1FormationS1GXDeterministicSingleBatchTargetTests
        source.setUpClass()
        cls.gate = source.gate
        cls.target = source()._select()
        cls.message = (
            "Ich autorisiere ausdruecklich den exakt gebundenen S1-GY-Lauf "
            "einmalig, nicht persistent und ohne Retry oder Claims."
        )
        cls.event = cls._event()

    @classmethod
    def _event(cls, **changes):
        values = {
            "event_id": S1_HB_EVENT_ID,
            "origin_kind": S1_HB_ORIGIN_KIND,
            "host_provider_id": "synthetic-test-host",
            "authenticated_owner_principal_digest": _digest(("owner",)),
            "task_or_session_binding_digest": _digest(("task",)),
            "fresh_single_use_nonce_digest": _digest(("nonce",)),
            "host_attestation_digest": _digest(("host-attestation",)),
            "owner_message_digest": _digest(cls.message.lower()),
            "project_id": S1_GW_PROJECT_ID,
            "run_id": cls.target.run_id,
            "gate_digest": cls.gate.gate_digest,
            "binding_digest": cls.target.selected_binding_digest,
            "batch_index": cls.target.selected_batch_index,
            "carrier_digest": cls.target.selected_carrier_digest,
            "maximum_adapter_calls": 1,
            "maximum_field_steps": 1,
            "required_owner_clauses": S1_GW_REQUIRED_OWNER_CLAUSES,
            "explicit_owner_message": True,
            "single_use": True,
            "non_persistent": True,
            "retry_permitted": False,
            "reparametrization_permitted": False,
            "partial_return_permitted": False,
            "claims_permitted": False,
            "expires_after_success_or_failure": True,
            "host_sequence": 1,
        }
        values.update(changes)
        return E1FormationS1HBExternalOwnerOriginEvent(
            **values,
            event_digest=_digest(values),
        )

    def _bind(self, event=None, *, verifier=lambda _event: True):
        return bind_e1_formation_s1hb_external_owner_authorization(
            self.message,
            self.event if event is None else event,
            self.gate,
            self.target,
            origin_verifier=verifier,
        )

    def test_synthetic_external_verifier_binds_exact_authorization(self) -> None:
        authorization = self._bind()
        self.assertEqual(self.target.run_id, authorization.run_id)
        self.assertEqual(self.gate.gate_digest, authorization.gate_digest)
        self.assertEqual(
            self.target.selected_binding_digest,
            authorization.binding_digest,
        )
        self.assertEqual(
            self.event.event_digest,
            authorization.external_origin_receipt_digest,
        )

    def test_ok_weiter_is_never_authorization(self) -> None:
        with self.assertRaises(E1FormationS1HBExternalOwnerOriginBridgeError):
            bind_e1_formation_s1hb_external_owner_authorization(
                "ok weiter",
                self.event,
                self.gate,
                self.target,
                origin_verifier=lambda _event: True,
            )

    def test_missing_or_negative_external_verifier_fails_closed(self) -> None:
        with self.assertRaises(E1FormationS1HBExternalOwnerOriginBridgeError):
            self._bind(verifier=lambda _event: False)
        with self.assertRaises(E1FormationS1HBExternalOwnerOriginBridgeError):
            self._bind(verifier=lambda _event: 1)
        with self.assertRaises(E1FormationS1HBExternalOwnerOriginBridgeError):
            self._bind(verifier=lambda _event: 1 / 0)

    def test_cross_bound_host_event_fails_closed(self) -> None:
        wrong_binding = self._event(binding_digest="1" * 64)
        wrong_gate = self._event(gate_digest="2" * 64)
        for event in (wrong_binding, wrong_gate):
            with self.assertRaises(E1FormationS1HBExternalOwnerOriginBridgeError):
                self._bind(event)

    def test_message_digest_mismatch_fails_closed(self) -> None:
        event = self._event(owner_message_digest=_digest(("other",)))
        with self.assertRaises(E1FormationS1HBExternalOwnerOriginBridgeError):
            self._bind(event)

    def test_authorization_remains_one_shot_nonpersistent_and_claim_free(self) -> None:
        authorization = self._bind()
        self.assertEqual((1, 1), (
            authorization.maximum_adapter_calls,
            authorization.maximum_field_steps,
        ))
        self.assertTrue(authorization.single_use)
        self.assertTrue(authorization.non_persistent)
        self.assertFalse(authorization.retry_permitted)
        self.assertFalse(authorization.claims_permitted)

    def test_bridge_calls_no_token_adapter_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            bind_e1_formation_s1hb_external_owner_authorization
        )
        for forbidden in (
            "issue_e1_formation_s1gt_synthetic_single_use_token(",
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "build_e1_formation_s1ha_pure_real_transition(",
            ".consume(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
