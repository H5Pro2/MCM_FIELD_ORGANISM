from __future__ import annotations

import copy
import inspect
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_execution_coordinator_fixture import (
    E1CommonProbeN2R2ExecutionCoordinatorFixtureError,
    E1CoordinatorFormationReceipt,
    E1CoordinatorProbeReceipt,
    run_e1_common_probe_n2_r2_execution_coordinator_fixture,
)
from mcm_field_organism.e1_common_probe_real_wrappers import E1CommonProbeFreshField
from mcm_field_organism.e1_refined_chain_canonical_producer import _initial_field_digest
from mcm_field_organism.e1_refined_formation_runner import _digest, _state_payload
from tests.test_e1_common_probe_n2_r2_object_handoff import E1CommonProbeN2R2ObjectHandoffTests


class E1CommonProbeN2R2ExecutionCoordinatorFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = E1CommonProbeN2R2ObjectHandoffTests
        source.setUpClass()
        cls.handoff = source(methodName="test_carries_all_real_objects_without_field_steps")._prepare()

    def _kernels(self):
        formation_calls = []
        fresh_calls = []
        probe_calls = []

        def formation(slot, initial_field, initial_state):
            state = copy.deepcopy(initial_state)
            values = {
                "state_role": slot.binding.state_role,
                "output_state_digest": _digest(_state_payload(state)),
                "field_steps_executed": 0,
            }
            result = E1CoordinatorFormationReceipt(
                **values, output_state=state, receipt_digest=_digest(values)
            )
            formation_calls.append((slot, initial_field, initial_state, result))
            return result

        def fresh(binding, initial_field):
            field = copy.deepcopy(initial_field)
            result = E1CommonProbeFreshField(
                binding.binding_digest, _initial_field_digest(initial_field), field
            )
            fresh_calls.append((binding, initial_field, result))
            return result

        def probe(slot, fresh_field, state):
            values = {
                "binding_digest": slot.binding.binding_digest,
                "selected_state_digest": None if state is None else _digest(_state_payload(state)),
                "backreaction_enabled": slot.binding.backreaction_enabled,
                "activation": (0.0, 0.0, 0.0),
                "afterimage": (0.0, 0.0, 0.0),
                "field_steps_executed": 0,
            }
            result = E1CoordinatorProbeReceipt(**values, receipt_digest=_digest(values))
            probe_calls.append((slot, fresh_field, state, result))
            return result

        return formation, fresh, probe, formation_calls, fresh_calls, probe_calls

    def test_exact_four_formation_eight_probe_coordination(self) -> None:
        formation, fresh, probe, formation_calls, fresh_calls, probe_calls = self._kernels()
        result = run_e1_common_probe_n2_r2_execution_coordinator_fixture(
            self.handoff,
            formation_kernel=formation,
            fresh_field_kernel=fresh,
            probe_kernel=probe,
        )
        self.assertEqual((4, 8, 8), (len(formation_calls), len(fresh_calls), len(probe_calls)))
        self.assertEqual(0, result.field_steps_executed)
        self.assertTrue(result.all_state_routes_exact)
        self.assertTrue(result.all_backreaction_routes_exact)
        self.assertFalse(result.real_wrapper_execution_permitted)

    def test_p0_and_e1_state_objects_are_routed_by_identity(self) -> None:
        formation, fresh, probe, formation_calls, _, probe_calls = self._kernels()
        run_e1_common_probe_n2_r2_execution_coordinator_fixture(
            self.handoff,
            formation_kernel=formation,
            fresh_field_kernel=fresh,
            probe_kernel=probe,
        )
        states = {call[0].binding.state_role: call[3].output_state for call in formation_calls}
        for slot, _, state, _ in probe_calls:
            expected = None if slot.binding.state_role is None else states[slot.binding.state_role]
            self.assertIs(state, expected)

    def test_untyped_formation_double_fails_closed(self) -> None:
        _, fresh, probe, _, _, _ = self._kernels()
        with self.assertRaises(E1CommonProbeN2R2ExecutionCoordinatorFixtureError):
            run_e1_common_probe_n2_r2_execution_coordinator_fixture(
                self.handoff,
                formation_kernel=lambda *args: None,
                fresh_field_kernel=fresh,
                probe_kernel=probe,
            )

    def test_coordinator_has_no_direct_real_wrapper_or_write_path(self) -> None:
        source = inspect.getsource(run_e1_common_probe_n2_r2_execution_coordinator_fixture)
        for forbidden in (
            "run_e1_common_probe_real_formation_wrapper(",
            "build_e1_common_probe_fresh_field(",
            "run_e1_common_probe_real_probe_wrapper(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
