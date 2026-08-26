from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from tests import (
    test_e1_formation_s1gk_fixed_adapter_real_wrapper_contract as contract_fixture,
)

from mcm_field_organism.e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract,
)
from mcm_field_organism.e1_formation_s1gs_real_single_batch_transition import (
    advance_e1_formation_s1gs_real_single_batch_transition,
)
from mcm_field_organism.e1_formation_s1gt_six_arm_release_scope_contract import (
    bind_e1_formation_s1gt_six_arm_release_scope_contract,
)
from mcm_field_organism.e1_formation_s1gv_real_mode_binding_contract import (
    bind_e1_formation_s1gv_real_mode_binding_contract,
)
from mcm_field_organism.e1_formation_s1gw_real_mode_gate import (
    E1FormationS1GWRealModeGateError,
    build_e1_formation_s1gw_real_mode_gate,
    s1gw_real_mode_transition_for_later_injection,
)


class E1FormationS1GWRealModeGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = contract_fixture.E1FormationS1GKFixedAdapterRealWrapperContractTests
        source.setUpClass()
        source_contract = prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
            source.bridge,
            source.integration,
        )
        scope = bind_e1_formation_s1gt_six_arm_release_scope_contract(
            source_contract
        )
        cls.contract = bind_e1_formation_s1gv_real_mode_binding_contract(scope)

    def test_gate_binds_s1gs_transition_without_execution(self) -> None:
        gate = build_e1_formation_s1gw_real_mode_gate(self.contract)
        self.assertTrue(gate.s1gv_contract_required)
        self.assertTrue(gate.s1gs_transition_selected)
        self.assertEqual(2800, gate.planned_real_transition_count)
        self.assertEqual(2800, gate.planned_field_step_count)
        self.assertEqual(660, gate.planned_source_support_count)
        self.assertFalse(gate.real_mode_execution_permitted)
        self.assertFalse(gate.field_execution_performed)
        self.assertFalse(gate.claims_permitted)
        self.assertEqual(
            "S1GU_REAL_MODE_GATE_BOUND_EXECUTION_STILL_CLOSED",
            gate.decision,
        )

    def test_transition_selection_requires_typed_closed_gate(self) -> None:
        gate = build_e1_formation_s1gw_real_mode_gate(self.contract)
        transition = s1gw_real_mode_transition_for_later_injection(gate)
        self.assertIs(transition, advance_e1_formation_s1gs_real_single_batch_transition)
        with self.assertRaises(E1FormationS1GWRealModeGateError):
            s1gw_real_mode_transition_for_later_injection(object())

    def test_gate_is_tamper_evident(self) -> None:
        gate = build_e1_formation_s1gw_real_mode_gate(self.contract)
        with self.assertRaises(E1FormationS1GWRealModeGateError):
            replace(gate, real_mode_execution_permitted=True)
        with self.assertRaises(E1FormationS1GWRealModeGateError):
            replace(gate, accepted_transition_name="other")

    def test_gate_builder_and_selector_do_not_call_real_transition_or_writer(self) -> None:
        combined_source = "\n".join(
            (
                inspect.getsource(build_e1_formation_s1gw_real_mode_gate),
                inspect.getsource(s1gw_real_mode_transition_for_later_injection),
            )
        )
        for forbidden in (
            "advance_e1_formation_s1gs_real_single_batch_transition(",
            "run_e1_formation_s1gu_six_arm_counting_adapter(",
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, combined_source)


if __name__ == "__main__":
    unittest.main()
