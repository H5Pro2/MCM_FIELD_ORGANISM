from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1gs_real_single_batch_gate_contract import (
    E1FormationS1GSRealSingleBatchGateContractError,
    build_e1_formation_s1gs_real_single_batch_gate_contract,
)


class E1FormationS1GSRealSingleBatchGateContractTests(unittest.TestCase):
    def test_gate_scope_is_exactly_one_binding_batch_call_and_step(self) -> None:
        gate = build_e1_formation_s1gs_real_single_batch_gate_contract()
        self.assertEqual(1, gate.maximum_adapter_calls)
        self.assertEqual(1, gate.maximum_field_steps)
        self.assertEqual("real-field-advance", gate.required_transition_kind)
        self.assertEqual(5, len(gate.scope))

    def test_external_authorization_and_single_use_token_are_required(self) -> None:
        gate = build_e1_formation_s1gs_real_single_batch_gate_contract()
        self.assertTrue(gate.external_owner_authorization_required)
        self.assertTrue(gate.process_local_single_use_token_required)
        self.assertFalse(gate.authorization_present)
        self.assertFalse(gate.authorization_token_implemented)
        self.assertFalse(gate.token_creation_permitted)

    def test_authorization_and_consumption_order_is_bound(self) -> None:
        gate = build_e1_formation_s1gs_real_single_batch_gate_contract()
        authorization = gate.gate_sequence.index(
            "validate-external-authorization-before-token-creation"
        )
        creation = gate.gate_sequence.index(
            "create-one-process-local-single-use-token"
        )
        consumption = gate.gate_sequence.index(
            "consume-token-immediately-before-first-adapter-call"
        )
        adapter = gate.gate_sequence.index("permit-exactly-one-adapter-call")
        self.assertLess(authorization, creation)
        self.assertLess(consumption, adapter)

    def test_execution_retry_partial_return_and_claims_remain_closed(self) -> None:
        gate = build_e1_formation_s1gs_real_single_batch_gate_contract()
        self.assertFalse(gate.real_transition_builder_implemented)
        self.assertFalse(gate.real_adapter_implemented)
        self.assertFalse(gate.execution_permitted)
        self.assertFalse(gate.retry_permitted)
        self.assertFalse(gate.reparametrization_permitted)
        self.assertFalse(gate.partial_return_permitted)
        self.assertFalse(gate.persistence_permitted)
        self.assertFalse(gate.claims_permitted)

    def test_gate_is_deterministic_and_tampering_fails_closed(self) -> None:
        first = build_e1_formation_s1gs_real_single_batch_gate_contract()
        second = build_e1_formation_s1gs_real_single_batch_gate_contract()
        self.assertEqual(first, second)
        self.assertTrue(all(value for _, value in first.checks))
        with self.assertRaises(E1FormationS1GSRealSingleBatchGateContractError):
            replace(first, execution_permitted=True)
        with self.assertRaises(E1FormationS1GSRealSingleBatchGateContractError):
            replace(first, maximum_field_steps=2)

    def test_builder_calls_no_adapter_kernel_token_factory_or_writer(self) -> None:
        source = inspect.getsource(
            build_e1_formation_s1gs_real_single_batch_gate_contract
        )
        for forbidden in (
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "create_authorization_token(",
            ".consume(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
