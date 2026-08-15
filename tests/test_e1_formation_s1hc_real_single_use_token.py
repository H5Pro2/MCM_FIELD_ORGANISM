from __future__ import annotations

import copy
import pickle
import unittest

import tests.test_e1_formation_s1hb_external_owner_origin_bridge as bridge_fixture

from mcm_field_organism.e1_formation_s1gw_external_owner_authorization_schema import (
    E1FormationS1GWExternalOwnerAuthorization,
)
from mcm_field_organism.e1_formation_s1hb_external_owner_origin_bridge import (
    bind_e1_formation_s1hb_external_owner_authorization,
)
from mcm_field_organism.e1_formation_s1hc_real_single_use_token import (
    E1FormationS1HCRealSingleUseTokenError,
    issue_e1_formation_s1hc_real_single_use_token,
)
from mcm_field_organism.e1_refined_formation_runner import _digest


class E1FormationS1HCRealSingleUseTokenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = bridge_fixture.E1FormationS1HBExternalOwnerOriginBridgeTests
        source.setUpClass()
        cls.source = source
        cls.gate = source.gate
        cls.target = source.target
        cls.message = source.message

    def setUp(self) -> None:
        unique = _digest((self.id(),))
        event = self.source._event(
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

    def _issue(self, authorization=None):
        return issue_e1_formation_s1hc_real_single_use_token(
            self.authorization if authorization is None else authorization,
            self.gate,
            self.target,
        )

    def test_issues_exact_process_local_token(self) -> None:
        token = self._issue()
        self.assertEqual(self.authorization.authorization_digest, token.authorization_digest)
        self.assertEqual(self.gate.gate_digest, token.gate_digest)
        self.assertEqual(self.target.selected_binding_digest, token.binding_digest)
        self.assertEqual((1, 1), (
            token.maximum_adapter_calls,
            token.maximum_field_steps,
        ))
        self.assertEqual("issued", token.status)

    def test_same_authorization_cannot_issue_twice(self) -> None:
        token = self._issue()
        with self.assertRaises(E1FormationS1HCRealSingleUseTokenError):
            self._issue()
        token.retire("real-attempt-failure")

    def test_success_requires_one_consumption_then_retirement(self) -> None:
        token = self._issue()
        with self.assertRaises(E1FormationS1HCRealSingleUseTokenError):
            token.retire("real-attempt-success")
        token.consume()
        self.assertTrue(token.consumed)
        with self.assertRaises(E1FormationS1HCRealSingleUseTokenError):
            token.consume()
        token.retire("real-attempt-success")
        self.assertTrue(token.retired)
        self.assertEqual("real-attempt-success", token.outcome)

    def test_failure_retires_before_or_after_consumption(self) -> None:
        before = self._issue()
        before.retire("real-attempt-failure")
        self.assertTrue(before.retired)

        event = self.source._event(
            fresh_single_use_nonce_digest=_digest((self.id(), "after")),
            host_attestation_digest=_digest((self.id(), "host-after")),
        )
        authorization = bind_e1_formation_s1hb_external_owner_authorization(
            self.message,
            event,
            self.gate,
            self.target,
            origin_verifier=lambda _event: True,
        )
        after = self._issue(authorization)
        after.consume()
        after.retire("real-attempt-failure")
        self.assertTrue(after.retired)

    def test_cross_bound_authorization_fails_closed(self) -> None:
        values = {
            name: getattr(self.authorization, name)
            for name in self.authorization.__dataclass_fields__
            if name != "authorization_digest"
        }
        values["binding_digest"] = "1" * 64
        wrong = E1FormationS1GWExternalOwnerAuthorization(
            **values,
            authorization_digest=_digest(values),
        )
        with self.assertRaises(E1FormationS1HCRealSingleUseTokenError):
            self._issue(wrong)

    def test_token_cannot_be_copied_serialized_or_reassigned(self) -> None:
        token = self._issue()
        for operation in (
            lambda: copy.copy(token),
            lambda: copy.deepcopy(token),
            lambda: pickle.dumps(token),
        ):
            with self.assertRaises(E1FormationS1HCRealSingleUseTokenError):
                operation()
        with self.assertRaises(E1FormationS1HCRealSingleUseTokenError):
            token.binding_digest = "2" * 64
        token.retire("real-attempt-failure")

    def test_factory_has_no_adapter_kernel_transition_or_writer_access(self) -> None:
        import inspect

        source = inspect.getsource(issue_e1_formation_s1hc_real_single_use_token)
        for forbidden in (
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "build_e1_formation_s1ha_pure_real_transition(",
            "bind_e1_formation_s1gq_carrier_transition_envelope(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
