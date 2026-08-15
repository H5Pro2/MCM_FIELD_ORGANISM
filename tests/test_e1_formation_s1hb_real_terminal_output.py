from __future__ import annotations

import copy
import inspect
import unittest

from tests import test_e1_formation_s1gu_six_arm_counting_adapter as gu_fixture

from mcm_field_organism.e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
    S1_GN_CARRIER_ID,
    build_e1_formation_s1gn_initial_live_field_carrier,
    e1_formation_s1gn_current_field_digest,
)
from mcm_field_organism.e1_formation_s1gu_six_arm_counting_adapter import (
    E1FormationS1GUSixArmCountingAdapterError,
    S1_GU_REAL_DECISION,
    _s1gu_execution_mode,
)
from mcm_field_organism.e1_formation_s1hb_real_terminal_output import (
    E1FormationS1HBRealTerminalOutputError,
    S1_HB_EXECUTION_KIND,
    build_e1_formation_s1hb_real_terminal_output,
)
from mcm_field_organism.e1_refined_formation_runner import _digest


class E1FormationS1HBRealTerminalOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = gu_fixture.E1FormationS1GUSixArmCountingAdapterTests
        source.setUpClass()
        cls.fresh = source.bridge.fresh_bindings[0]

    def _terminal_carrier(self) -> E1FormationS1GNLiveFieldCarrier:
        fresh = self.fresh
        field = copy.deepcopy(fresh.fresh_field)
        plan = fresh.invocation.context.probe_plan
        values = {
            "carrier_id": S1_GN_CARRIER_ID,
            "fresh_binding": fresh,
            "current_field": field,
            "binding_digest": fresh.binding_digest,
            "initial_field_digest": fresh.initial_field_digest,
            "current_field_digest": e1_formation_s1gn_current_field_digest(field),
            "ordered_neuron_ids": fresh.ordered_neuron_ids,
            "completed_batch_count": len(plan.handoff.batches),
            "accounted_source_support_count": plan.handoff.source_event_count,
            "actual_field_steps_executed": len(plan.handoff.batches),
            "persistence_performed": False,
            "claims_permitted": False,
        }
        payload = {
            name: value
            for name, value in values.items()
            if name not in {"fresh_binding", "current_field"}
        }
        return E1FormationS1GNLiveFieldCarrier(
            **values,
            carrier_digest=_digest(payload),
        )

    def test_builds_real_typed_output_from_complete_terminal_carrier(self) -> None:
        carrier = self._terminal_carrier()
        output = build_e1_formation_s1hb_real_terminal_output(self.fresh, carrier)
        self.assertEqual(S1_HB_EXECUTION_KIND, output.field_execution_kind)
        self.assertEqual(carrier.completed_batch_count, output.field_step_count)
        self.assertEqual(
            carrier.actual_field_steps_executed,
            output.actual_field_steps_executed,
        )
        self.assertEqual(carrier.current_field_digest, output.terminal_field_digest)
        self.assertTrue(output.source_state_preserved)
        self.assertTrue(output.fixed_adapter_preserved)

    def test_rejects_incomplete_or_synthetic_terminal_carrier(self) -> None:
        with self.assertRaises(E1FormationS1HBRealTerminalOutputError):
            build_e1_formation_s1hb_real_terminal_output(
                self.fresh,
                build_e1_formation_s1gn_initial_live_field_carrier(self.fresh),
            )

    def test_s1gu_real_mode_is_exact_and_rejects_partial_execution(self) -> None:
        real_mode, decision, reason = _s1gu_execution_mode(
            (("real-field-advance", 2800),),
            2800,
        )
        self.assertTrue(real_mode)
        self.assertEqual(S1_GU_REAL_DECISION, decision)
        self.assertTrue(reason)
        with self.assertRaises(E1FormationS1GUSixArmCountingAdapterError):
            _s1gu_execution_mode((("real-field-advance", 2799),), 2799)

    def test_builder_calls_no_transition_kernel_writer_or_persistence(self) -> None:
        source = inspect.getsource(build_e1_formation_s1hb_real_terminal_output)
        for forbidden in (
            "advance_e1_formation_s1gs_real_single_batch_transition(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
