from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

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
from mcm_field_organism.e1_repetition_pilot_real_adapter_fixture import (
    E1RepetitionPilotRealAdapterFixtureError,
    run_e1_repetition_pilot_real_adapter_fixture,
)
from mcm_field_organism.e1_repetition_pilot_release_contract import S1_EC29_ARMS
from tests.test_e1_confirmation_typed_prepared_inputs import UPSTREAM


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = ROOT / "synthetic_runs" / "s1ec19_full_published_once_v1"
REPORT = ROOT / "synthetic_runs" / "s1ec23_full_published_probe_once_v1" / "e1_full_published_probe_s1ec23_once_v1.json"


class E1RepetitionPilotRealAdapterFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(descriptor, SOURCE_DIRECTORY)
        bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(run, UPSTREAM)
        cls.values = _typed_values_from_bundle(bundle)
        formation = build_e1_repetition_formation_contract(
            audit_e1_memory_function_gaps(REPORT), bundle
        )
        cls.plans = build_e1_repetition_formation_plans(formation, bundle)

    def test_all_six_roles_use_real_kernels_on_small_fixture(self) -> None:
        result = run_e1_repetition_pilot_real_adapter_fixture(
            self.plans.pairs[1], self.values.initial_field, self.values.initial_state
        )
        self.assertEqual(S1_EC29_ARMS, result.role_order)
        self.assertEqual(48, result.total_field_steps_executed)
        self.assertTrue(result.six_role_adapter_implemented)
        self.assertFalse(result.full_pilot_executed)

    def test_p0_and_e1_roles_are_separated(self) -> None:
        result = run_e1_repetition_pilot_real_adapter_fixture(
            self.plans.pairs[1], self.values.initial_field, self.values.initial_state
        )
        kinds = {item.role_id: item.kernel_kind for item in result.receipts}
        self.assertEqual("p0", kinds["p0_repeated"])
        self.assertEqual("e1", kinds["repeated_formation_ablated"])
        self.assertEqual("e1", kinds["repeated_active"])

    def test_inputs_and_source_pair_are_preserved(self) -> None:
        result = run_e1_repetition_pilot_real_adapter_fixture(
            self.plans.pairs[1], self.values.initial_field, self.values.initial_state
        )
        self.assertTrue(result.initial_inputs_preserved)
        self.assertTrue(result.source_pair_preserved)
        self.assertTrue(all(item.copied_inputs_used for item in result.receipts))

    def test_n1_pair_is_rejected_by_fixture_boundary(self) -> None:
        with self.assertRaises(E1RepetitionPilotRealAdapterFixtureError):
            run_e1_repetition_pilot_real_adapter_fixture(
                self.plans.pairs[0], self.values.initial_field, self.values.initial_state
            )

    def test_protected_report_remains_unchanged(self) -> None:
        before = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        run_e1_repetition_pilot_real_adapter_fixture(
            self.plans.pairs[1], self.values.initial_field, self.values.initial_state
        )
        self.assertEqual(before, hashlib.sha256(REPORT.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
