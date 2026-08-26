from __future__ import annotations

import copy
from pathlib import Path
import unittest

from mcm_field_organism.e1_common_probe_ec91_refinement_receipts_converters import (
    _synthetic_formation_output,
    _synthetic_probe_output,
    convert_e1_common_probe_ec91_formation_output,
    convert_e1_common_probe_ec91_probe_output,
    run_e1_common_probe_ec91_synthetic_fixture,
)
from mcm_field_organism.e1_common_probe_ec92_synthetic_r4_r8_coordinator import (
    run_e1_common_probe_ec92_synthetic_coordinator,
)
from mcm_field_organism.e1_common_probe_ec93_r4_r8_real_adapter_preflight import (
    build_e1_common_probe_ec93_r4_r8_real_adapter_preflight,
)
from mcm_field_organism.e1_common_probe_ec94_final_resource_identity_gate import (
    audit_e1_common_probe_ec94_final_resource_identity_gate,
)
from mcm_field_organism.e1_common_probe_ec96_authorized_r4_r8_once import (
    E1CommonProbeEC96AuthorizationToken,
    E1CommonProbeEC96AuthorizedOnceError,
    S1_EC96_AUTHORIZATION_TEXT,
    run_e1_common_probe_ec96_authorized_r4_r8_once,
)
from mcm_field_organism.e1_common_probe_n2_r2_positive_step_receipt_contract import (
    S1_EC63_ROLE_STATE_ROUTES,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_preflight import (
    audit_e1_common_probe_protected_artifacts,
)
from mcm_field_organism.e1_common_probe_real_wrappers import E1CommonProbeFreshField
from mcm_field_organism.e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
)
from tests.test_e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffsTests,
)


class E1CommonProbeEC96AuthorizedR4R8OnceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1CommonProbeEC89R4R8ObjectHandoffsTests.setUpClass()
        cls.handoffs = E1CommonProbeEC89R4R8ObjectHandoffsTests()._prepare()
        fixture = run_e1_common_probe_ec91_synthetic_fixture(cls.handoffs)
        coordinator = run_e1_common_probe_ec92_synthetic_coordinator(
            cls.handoffs, fixture
        )
        preflight = build_e1_common_probe_ec93_r4_r8_real_adapter_preflight(
            cls.handoffs, fixture, coordinator
        )
        resources = E1PilotRealResourceSnapshot(6 * 1024**3, 200 * 1024**3)
        protected = audit_e1_common_probe_protected_artifacts(
            Path(__file__).resolve().parents[1]
        )
        cls.gate = audit_e1_common_probe_ec94_final_resource_identity_gate(
            cls.handoffs, coordinator, preflight, resources, protected
        )

    def _token(self):
        return E1CommonProbeEC96AuthorizationToken(
            S1_EC96_AUTHORIZATION_TEXT, self.gate.gate_digest
        )

    def _adapters(self, counts):
        routes = dict(S1_EC63_ROLE_STATE_ROUTES)

        def formation(handoff, slot, initial_field, initial_state):
            counts["formation"] += 1
            return convert_e1_common_probe_ec91_formation_output(
                handoff,
                slot,
                _synthetic_formation_output(handoff, slot),
                execution_mode="real-wrapper",
            )

        def fresh(binding, initial_field):
            counts["fresh"] += 1
            return E1CommonProbeFreshField(
                binding.binding_digest,
                self.handoffs.handoffs[0].initial_field_digest,
                copy.deepcopy(initial_field),
            )

        def probe(handoff, slot, fresh_field, formation_receipt):
            counts["probe"] += 1
            index = handoff.resolved_slots.index(slot)
            role = routes[slot.binding.role_id]
            expected = None if role is None else formation_receipt.output_state_digest
            output = _synthetic_probe_output(handoff, slot, expected, index)
            return convert_e1_common_probe_ec91_probe_output(
                handoff,
                slot,
                output,
                formation_receipt,
                execution_mode="real-wrapper",
            )

        return formation, fresh, probe

    def test_resource_failure_is_zero_adapter_and_does_not_consume(self) -> None:
        counts = {"formation": 0, "fresh": 0, "probe": 0}
        token = self._token()
        formation, fresh, probe = self._adapters(counts)
        with self.assertRaisesRegex(E1CommonProbeEC96AuthorizedOnceError, "zero-step"):
            run_e1_common_probe_ec96_authorized_r4_r8_once(
                self.handoffs,
                self.gate,
                token,
                resource_reader=lambda: E1PilotRealResourceSnapshot(1, 1),
                formation_adapter=formation,
                fresh_field_adapter=fresh,
                probe_adapter=probe,
            )
        self.assertEqual({"formation": 0, "fresh": 0, "probe": 0}, counts)
        self.assertFalse(token.consumed)

    def test_complete_call_is_atomic_and_token_cannot_retry(self) -> None:
        counts = {"formation": 0, "fresh": 0, "probe": 0}
        token = self._token()
        formation, fresh, probe = self._adapters(counts)
        result = run_e1_common_probe_ec96_authorized_r4_r8_once(
            self.handoffs,
            self.gate,
            token,
            resource_reader=lambda: E1PilotRealResourceSnapshot(
                6 * 1024**3, 200 * 1024**3
            ),
            formation_adapter=formation,
            fresh_field_adapter=fresh,
            probe_adapter=probe,
        )
        self.assertEqual({"formation": 8, "fresh": 16, "probe": 16}, counts)
        self.assertEqual(19248, result.total_field_steps)
        self.assertTrue(result.atomic_scalar_return)
        self.assertTrue(token.consumed)
        with self.assertRaises(E1CommonProbeEC96AuthorizedOnceError):
            run_e1_common_probe_ec96_authorized_r4_r8_once(
                self.handoffs,
                self.gate,
                token,
                resource_reader=lambda: E1PilotRealResourceSnapshot(
                    6 * 1024**3, 200 * 1024**3
                ),
                formation_adapter=formation,
                fresh_field_adapter=fresh,
                probe_adapter=probe,
            )


if __name__ == "__main__":
    unittest.main()
