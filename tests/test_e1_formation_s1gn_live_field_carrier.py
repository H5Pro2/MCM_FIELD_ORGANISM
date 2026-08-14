from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gh_fresh_field_bridge as bridge_fixture

from mcm_field_organism.e1_formation_s1gh_fresh_field_bridge import (
    bind_e1_formation_s1gh_fresh_fields,
)
from mcm_field_organism.e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrierError,
    advance_e1_formation_s1gn_live_field_carrier_synthetically,
    build_e1_formation_s1gn_initial_live_field_carrier,
)


class E1FormationS1GNLiveFieldCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = bridge_fixture.E1FormationS1GHFreshFieldBridgeTests
        source.setUpClass()
        cls.bridge = bind_e1_formation_s1gh_fresh_fields(
            source.bindings,
            source.inputs,
        )

    def test_initial_carriers_wrap_exact_six_fresh_fields(self) -> None:
        carriers = tuple(
            build_e1_formation_s1gn_initial_live_field_carrier(item)
            for item in self.bridge.fresh_bindings
        )
        self.assertEqual(6, len(carriers))
        self.assertTrue(
            all(
                carrier.current_field is fresh.fresh_field
                and carrier.current_field_digest == fresh.initial_field_digest
                and carrier.completed_batch_count == 0
                for fresh, carrier in zip(
                    self.bridge.fresh_bindings, carriers, strict=True
                )
            )
        )

    def test_synthetic_transition_carries_field_explicitly_without_advance(self) -> None:
        fresh = self.bridge.fresh_bindings[0]
        carrier = build_e1_formation_s1gn_initial_live_field_carrier(fresh)
        batch = fresh.invocation.context.probe_plan.handoff.batches[0]
        transition = advance_e1_formation_s1gn_live_field_carrier_synthetically(
            fresh,
            batch,
            carrier,
        )
        self.assertIs(transition.next_carrier.current_field, carrier.current_field)
        self.assertEqual(1, transition.next_carrier.completed_batch_count)
        self.assertEqual(
            batch.event_count,
            transition.next_carrier.accounted_source_support_count,
        )
        self.assertEqual(0, transition.next_carrier.actual_field_steps_executed)
        self.assertFalse(transition.field_object_replaced)

    def test_all_six_plans_reach_exact_batch_and_support_totals(self) -> None:
        completed = []
        for fresh in self.bridge.fresh_bindings:
            carrier = build_e1_formation_s1gn_initial_live_field_carrier(fresh)
            for batch in fresh.invocation.context.probe_plan.handoff.batches:
                carrier = advance_e1_formation_s1gn_live_field_carrier_synthetically(
                    fresh,
                    batch,
                    carrier,
                ).next_carrier
            completed.append(carrier)
        self.assertEqual(
            2800,
            sum(item.completed_batch_count for item in completed),
        )
        self.assertEqual(
            660,
            sum(item.accounted_source_support_count for item in completed),
        )
        self.assertEqual(
            0,
            sum(item.actual_field_steps_executed for item in completed),
        )

    def test_cross_binding_out_of_order_and_tampering_fail_closed(self) -> None:
        first, second = self.bridge.fresh_bindings[:2]
        carrier = build_e1_formation_s1gn_initial_live_field_carrier(first)
        first_batch = first.invocation.context.probe_plan.handoff.batches[0]
        second_batch = second.invocation.context.probe_plan.handoff.batches[0]
        with self.assertRaises(E1FormationS1GNLiveFieldCarrierError):
            advance_e1_formation_s1gn_live_field_carrier_synthetically(
                second,
                second_batch,
                carrier,
            )
        with self.assertRaises(E1FormationS1GNLiveFieldCarrierError):
            advance_e1_formation_s1gn_live_field_carrier_synthetically(
                first,
                first.invocation.context.probe_plan.handoff.batches[1],
                carrier,
            )
        with self.assertRaises(E1FormationS1GNLiveFieldCarrierError):
            replace(carrier, actual_field_steps_executed=1)
        self.assertEqual(0, first_batch.batch_index)

    def test_transition_calls_no_real_field_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            advance_e1_formation_s1gn_live_field_carrier_synthetically
        )
        for forbidden in (
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
