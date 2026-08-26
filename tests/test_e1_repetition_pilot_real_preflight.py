from __future__ import annotations

from dataclasses import replace
import hashlib
import inspect
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
from mcm_field_organism.e1_repetition_formation_fixture_consumer import run_repetition_formation_fixture_consumer
from mcm_field_organism.e1_repetition_formation_planner import build_e1_repetition_formation_plans
from mcm_field_organism.e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
    audit_e1_repetition_pilot_real_preflight,
)
from mcm_field_organism.e1_repetition_pilot_release_contract import build_e1_repetition_pilot_release_contract
from mcm_field_organism.e1_repetition_pilot_runner_fixture import run_repetition_pilot_runner_fixture
from tests.test_e1_confirmation_typed_prepared_inputs import UPSTREAM


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = ROOT / "synthetic_runs" / "s1ec19_full_published_once_v1"
REPORT = ROOT / "synthetic_runs" / "s1ec23_full_published_probe_once_v1" / "e1_full_published_probe_s1ec23_once_v1.json"


class E1RepetitionPilotRealPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(descriptor, SOURCE_DIRECTORY)
        bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(run, UPSTREAM)
        values = _typed_values_from_bundle(bundle)
        formation = build_e1_repetition_formation_contract(audit_e1_memory_function_gaps(REPORT), bundle)
        cls.plans = build_e1_repetition_formation_plans(formation, bundle)
        fixture = run_repetition_formation_fixture_consumer(cls.plans.pairs[1], values.initial_field, values.initial_state)
        cls.contract = build_e1_repetition_pilot_release_contract(cls.plans, fixture)
        cls.runner_fixture = run_repetition_pilot_runner_fixture(cls.contract)

    def _resources(self) -> E1PilotRealResourceSnapshot:
        return E1PilotRealResourceSnapshot(8 * 1024**3, 200 * 1024**3)

    def test_ready_but_adapter_and_owner_keep_execution_locked(self) -> None:
        result = audit_e1_repetition_pilot_real_preflight(
            self.contract, self.plans, self.runner_fixture, self._resources()
        )
        self.assertEqual("VORBEREITET_NICHT_FREIGEGEBEN", result.decision)
        self.assertTrue(result.adapter_implementation_permitted)
        self.assertFalse(result.real_role_adapter_implemented)
        self.assertFalse(result.owner_execution_authorized)
        self.assertFalse(result.pilot_execution_permitted)

    def test_insufficient_memory_requires_correction(self) -> None:
        resources = replace(self._resources(), free_memory_bytes=4 * 1024**3 - 1)
        result = audit_e1_repetition_pilot_real_preflight(
            self.contract, self.plans, self.runner_fixture, resources
        )
        self.assertEqual("KORREKTUR", result.decision)
        self.assertFalse(result.adapter_implementation_permitted)

    def test_kernel_inventory_separates_p0_from_e1(self) -> None:
        result = audit_e1_repetition_pilot_real_preflight(
            self.contract, self.plans, self.runner_fixture, self._resources()
        )
        bindings = {role: (kernel, mode) for role, kernel, mode in result.kernel_bindings}
        self.assertIn("neutral_asynchronous", bindings["p0_repeated"][0])
        self.assertIn("prepared_real_formation", bindings["repeated_active"][0])
        self.assertNotEqual(bindings["p0_repeated"], bindings["repeated_formation_ablated"])

    def test_preflight_contains_no_field_adapter_writer_or_authorization_input(self) -> None:
        source = inspect.getsource(audit_e1_repetition_pilot_real_preflight)
        for forbidden in (
            "run_neutral_asynchronous_field(",
            "run_prepared_real_formation_arm_in_memory(",
            "owner_authorized",
            "write_text",
            "write_bytes",
            "_atomic_publish",
        ):
            self.assertNotIn(forbidden, source)

    def test_protected_report_remains_unchanged(self) -> None:
        before = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        audit_e1_repetition_pilot_real_preflight(
            self.contract, self.plans, self.runner_fixture, self._resources()
        )
        self.assertEqual(before, hashlib.sha256(REPORT.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
