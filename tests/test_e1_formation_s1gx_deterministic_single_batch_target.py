from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gh_fresh_field_bridge as bridge_fixture

from mcm_field_organism.e1_formation_s1gh_fresh_field_bridge import (
    bind_e1_formation_s1gh_fresh_fields,
)
from mcm_field_organism.e1_formation_s1gs_real_single_batch_gate_contract import (
    build_e1_formation_s1gs_real_single_batch_gate_contract,
)
from mcm_field_organism.e1_formation_s1gx_deterministic_single_batch_target import (
    E1FormationS1GXDeterministicSingleBatchTargetError,
    select_e1_formation_s1gx_deterministic_single_batch_target,
)


class E1FormationS1GXDeterministicSingleBatchTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = bridge_fixture.E1FormationS1GHFreshFieldBridgeTests
        source.setUpClass()
        cls.bridge = bind_e1_formation_s1gh_fresh_fields(
            source.bindings,
            source.inputs,
        )
        cls.gate = build_e1_formation_s1gs_real_single_batch_gate_contract()

    def _select(self):
        return select_e1_formation_s1gx_deterministic_single_batch_target(
            self.bridge,
            self.gate,
        )

    def test_selects_r2_ab_as_smallest_canonical_role(self) -> None:
        target = self._select()
        self.assertEqual(
            ("r2", "fixed-adapter-ab"),
            (target.selected_refinement_id, target.selected_role_id),
        )
        self.assertTrue(target.smallest_refinement_selected)
        self.assertTrue(target.canonical_first_role_selected)
        self.assertEqual(
            (200, 200, 400, 400, 800, 800),
            tuple(item[2] for item in target.candidate_batch_counts),
        )

    def test_binds_exact_first_batch_and_initial_carrier_objects(self) -> None:
        target = self._select()
        self.assertEqual(0, target.selected_batch_index)
        self.assertTrue(target.exact_first_batch_selected)
        self.assertIs(
            target.selected_initial_carrier.current_field,
            target.selected_fresh_binding.fresh_field,
        )
        self.assertIs(
            target.selected_batch,
            target.selected_fresh_binding.invocation.context.probe_plan
            .handoff.batches[0],
        )
        self.assertTrue(target.fresh_field_object_carried_explicitly)
        self.assertTrue(target.source_field_unchanged)

    def test_target_is_limited_to_one_call_and_step(self) -> None:
        target = self._select()
        self.assertEqual((1, 1), (
            target.maximum_adapter_calls,
            target.maximum_field_steps,
        ))
        self.assertEqual(
            "S1-GY-REAL-SINGLE-CARRIER-BATCH-PILOT",
            target.run_id,
        )

    def test_selection_does_not_request_authorization_or_execute(self) -> None:
        target = self._select()
        self.assertTrue(target.authorization_required)
        self.assertFalse(target.authorization_present)
        self.assertFalse(target.authorization_requested)
        self.assertFalse(target.token_created)
        self.assertFalse(target.transition_created)
        self.assertEqual((0, 0), (
            target.adapter_calls,
            target.field_steps_executed,
        ))
        self.assertFalse(target.persistence_performed)
        self.assertFalse(target.claims_permitted)

    def test_selection_is_deterministic_and_tampering_fails_closed(self) -> None:
        first = self._select()
        second = self._select()
        self.assertEqual(first.target_digest, second.target_digest)
        with self.assertRaises(E1FormationS1GXDeterministicSingleBatchTargetError):
            replace(first, selected_role_id="fixed-adapter-ba")
        with self.assertRaises(E1FormationS1GXDeterministicSingleBatchTargetError):
            replace(first, field_steps_executed=1)

    def test_selector_calls_no_transition_adapter_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            select_e1_formation_s1gx_deterministic_single_batch_target
        )
        for forbidden in (
            "advance_e1_formation_s1gn_live_field_carrier_synthetically(",
            "bind_e1_formation_s1gq_carrier_transition_envelope(",
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
