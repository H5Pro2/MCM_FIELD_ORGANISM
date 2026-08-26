from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_object_handoff import (
    E1CommonProbeN2R2ObjectHandoffError,
    prepare_e1_common_probe_n2_r2_object_handoff,
)
from mcm_field_organism.e1_common_probe_real_binding_contract import (
    build_e1_common_probe_real_binding_contract,
)
from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_prepared_formation_consumer import (
    _typed_values_from_bundle,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_memory_function_gap_audit import audit_e1_memory_function_gaps
from mcm_field_organism.e1_repetition_formation_contract import build_e1_repetition_formation_contract
from mcm_field_organism.e1_repetition_formation_planner import build_e1_repetition_formation_plans
from tests.test_e1_confirmation_typed_prepared_inputs import UPSTREAM, _typed_inputs


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = ROOT / "synthetic_runs" / "s1ec19_full_published_once_v1"
REPORT = ROOT / "synthetic_runs" / "s1ec23_full_published_probe_once_v1" / "e1_full_published_probe_s1ec23_once_v1.json"


class E1CommonProbeN2R2ObjectHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(descriptor, SOURCE_DIRECTORY)
        bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(run, UPSTREAM)
        descriptor_values = _typed_values_from_bundle(bundle)
        formation = build_e1_repetition_formation_contract(
            audit_e1_memory_function_gaps(REPORT), bundle
        )
        cls.formation_plans = build_e1_repetition_formation_plans(formation, bundle)
        cls.inputs = _typed_inputs()
        cls.contract = build_e1_common_probe_real_binding_contract()
        cls.descriptor_initial_field = descriptor_values.initial_field

    def _prepare(self, **kwargs):
        return prepare_e1_common_probe_n2_r2_object_handoff(
            self.contract,
            self.formation_plans,
            self.inputs.probe_sequences,
            self.inputs.probe_plans,
            self.inputs.initial_field,
            self.inputs.initial_state,
            **kwargs,
        )

    def test_carries_all_real_objects_without_field_steps(self) -> None:
        result = self._prepare()
        self.assertEqual((2, "r2"), (result.contact_count, result.refinement_id))
        self.assertEqual((8, 4), (len(result.resolved_slots), len(result.formation_slots)))
        self.assertIs(result.contract, self.contract)
        self.assertIs(result.formation_plans, self.formation_plans)
        self.assertIs(result.initial_field, self.inputs.initial_field)
        self.assertIs(result.initial_state, self.inputs.initial_state)
        self.assertEqual(0, result.field_steps_executed)
        self.assertFalse(result.execution_permitted)

    def test_each_slot_is_resolved_with_the_same_input_objects(self) -> None:
        calls = []

        def resolver(contract, binding, formation_plans, sequences, probe_plans):
            calls.append((contract, binding, formation_plans, sequences, probe_plans))
            from mcm_field_organism.e1_common_probe_real_wrappers import resolve_e1_common_probe_real_slot
            return resolve_e1_common_probe_real_slot(
                contract, binding, formation_plans, sequences, probe_plans
            )

        result = self._prepare(resolver=resolver)
        self.assertEqual(8, len(calls))
        self.assertTrue(all(call[0] is self.contract for call in calls))
        self.assertTrue(all(call[2] is self.formation_plans for call in calls))
        self.assertTrue(all(call[4] is self.inputs.probe_plans for call in calls))
        self.assertTrue(result.all_slot_objects_resolved)
        self.assertTrue(result.all_formation_routes_unique)

    def test_untyped_resolver_result_fails_closed(self) -> None:
        with self.assertRaises(E1CommonProbeN2R2ObjectHandoffError):
            self._prepare(resolver=lambda *args: None)

    def test_adapter_has_no_execution_or_write_path(self) -> None:
        source = inspect.getsource(prepare_e1_common_probe_n2_r2_object_handoff)
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
