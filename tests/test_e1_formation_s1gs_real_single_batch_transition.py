from __future__ import annotations

import inspect
import unittest

import tests.test_e1_formation_s1gn_live_field_carrier as carrier_fixture

from mcm_field_organism.e1_formation_s1gn_live_field_carrier import (
    build_e1_formation_s1gn_initial_live_field_carrier,
)
from mcm_field_organism.e1_formation_s1go_private_carrier_wrapper import (
    E1FormationS1GOPrivateCarrierWrapperError,
    run_e1_formation_s1go_private_carrier_wrapper,
)
from mcm_field_organism.e1_formation_s1gq_carrier_transition_schema import (
    bind_e1_formation_s1gq_carrier_transition_envelope,
)
from mcm_field_organism.e1_formation_s1gs_real_single_batch_transition import (
    E1FormationS1GSRealSingleBatchTransitionError,
    advance_e1_formation_s1gs_real_single_batch_transition,
    validate_e1_formation_s1gs_real_single_batch_transition,
)
from mcm_field_organism.e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract,
)
from mcm_field_organism.e1_formation_s1gl_private_fixed_adapter_wrapper import (
    build_e1_formation_s1gl_synthetic_only_gate,
)

from tests import (
    test_e1_formation_s1gk_fixed_adapter_real_wrapper_contract as contract_fixture,
)


class E1FormationS1GSRealSingleBatchTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = carrier_fixture.E1FormationS1GNLiveFieldCarrierTests
        source.setUpClass()
        cls.bridge = source.bridge
        contract_source = (
            contract_fixture.E1FormationS1GKFixedAdapterRealWrapperContractTests
        )
        contract_source.setUpClass()
        cls.contract = prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
            contract_source.bridge,
            contract_source.integration,
        )

    def _first_real_transition(self):
        fresh = self.bridge.fresh_bindings[0]
        carrier = build_e1_formation_s1gn_initial_live_field_carrier(fresh)
        batch = fresh.invocation.context.probe_plan.handoff.batches[0]
        transition = advance_e1_formation_s1gs_real_single_batch_transition(
            fresh,
            batch,
            carrier,
        )
        return fresh, batch, carrier, transition

    def test_real_single_batch_transition_returns_real_envelope(self) -> None:
        _, batch, carrier, transition = self._first_real_transition()
        envelope = bind_e1_formation_s1gq_carrier_transition_envelope(transition)
        self.assertEqual("real-field-advance", envelope.transition_kind)
        self.assertIs(envelope.previous_carrier, carrier)
        self.assertIsNot(transition.next_carrier.current_field, carrier.current_field)
        self.assertEqual(batch.batch_index, envelope.batch_index)
        self.assertEqual(1, envelope.accounted_field_steps)
        self.assertEqual(1, envelope.actual_field_steps_executed)
        self.assertTrue(envelope.field_object_replaced)
        self.assertFalse(envelope.persistence_performed)
        self.assertFalse(envelope.claims_permitted)

    def test_validation_receipt_preserves_source_state_and_adapter(self) -> None:
        fresh = self.bridge.fresh_bindings[0]
        carrier = build_e1_formation_s1gn_initial_live_field_carrier(fresh)
        batch = fresh.invocation.context.probe_plan.handoff.batches[0]
        result = validate_e1_formation_s1gs_real_single_batch_transition(
            fresh,
            batch,
            carrier,
        )
        self.assertEqual(1, result.actual_field_steps_executed)
        self.assertTrue(result.source_state_preserved)
        self.assertTrue(result.fixed_adapter_preserved)
        self.assertFalse(result.wrapper_gate_opened)
        self.assertEqual(
            "REAL_SINGLE_BATCH_TRANSITION_VALIDATED_WRAPPER_GATE_REMAINS_CLOSED",
            result.decision,
        )

    def test_wrapper_still_rejects_real_transition_envelope(self) -> None:
        with self.assertRaises(E1FormationS1GOPrivateCarrierWrapperError):
            run_e1_formation_s1go_private_carrier_wrapper(
                self.contract,
                self.bridge,
                build_e1_formation_s1gl_synthetic_only_gate(),
                carrier_transition=advance_e1_formation_s1gs_real_single_batch_transition,
            )

    def test_out_of_order_batch_fails_closed(self) -> None:
        fresh = self.bridge.fresh_bindings[0]
        carrier = build_e1_formation_s1gn_initial_live_field_carrier(fresh)
        wrong_batch = fresh.invocation.context.probe_plan.handoff.batches[1]
        with self.assertRaises(E1FormationS1GSRealSingleBatchTransitionError):
            advance_e1_formation_s1gs_real_single_batch_transition(
                fresh,
                wrong_batch,
                carrier,
            )

    def test_adapter_has_no_writer_persistence_or_wrapper_gate_change(self) -> None:
        source = inspect.getsource(
            advance_e1_formation_s1gs_real_single_batch_transition
        )
        self.assertIn("advance_fixed_e1_adapter_fast_shared_field_transient(", source)
        for forbidden in (
            "open(",
            "write_text(",
            "write_bytes(",
            "persistence_performed\": True",
            "claims_permitted\": True",
            "run_e1_formation_s1go_private_carrier_wrapper(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
