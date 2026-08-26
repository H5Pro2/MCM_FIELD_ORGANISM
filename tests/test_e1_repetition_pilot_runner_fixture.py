from __future__ import annotations

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
from mcm_field_organism.e1_memory_function_gap_audit import (
    audit_e1_memory_function_gaps,
)
from mcm_field_organism.e1_repetition_formation_contract import (
    build_e1_repetition_formation_contract,
)
from mcm_field_organism.e1_repetition_formation_fixture_consumer import (
    run_repetition_formation_fixture_consumer,
)
from mcm_field_organism.e1_repetition_formation_planner import (
    build_e1_repetition_formation_plans,
)
from mcm_field_organism.e1_repetition_pilot_release_contract import (
    build_e1_repetition_pilot_release_contract,
)
from mcm_field_organism.e1_repetition_pilot_runner_fixture import (
    build_synthetic_pilot_arm_receipt,
    run_repetition_pilot_runner_fixture,
)
from tests.test_e1_confirmation_typed_prepared_inputs import UPSTREAM


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = ROOT / "synthetic_runs" / "s1ec19_full_published_once_v1"
REPORT = (
    ROOT
    / "synthetic_runs"
    / "s1ec23_full_published_probe_once_v1"
    / "e1_full_published_probe_s1ec23_once_v1.json"
)


class E1RepetitionPilotRunnerFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(
            descriptor, SOURCE_DIRECTORY
        )
        bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        values = _typed_values_from_bundle(bundle)
        gap = audit_e1_memory_function_gaps(REPORT)
        formation = build_e1_repetition_formation_contract(gap, bundle)
        plans = build_e1_repetition_formation_plans(formation, bundle)
        fixture = run_repetition_formation_fixture_consumer(
            plans.pairs[1], values.initial_field, values.initial_state
        )
        cls.contract = build_e1_repetition_pilot_release_contract(
            plans, fixture
        )

    def test_all_roles_run_in_preregistered_order_without_field_steps(self) -> None:
        result = run_repetition_pilot_runner_fixture(self.contract)

        self.assertEqual(36, result.arm_call_count)
        self.assertEqual(tuple(range(6)), result.batch_completion_order)
        self.assertEqual(0, result.executed_field_step_count)
        self.assertEqual(12, result.p0_receipt_count)
        self.assertEqual(12, result.formation_ablation_receipt_count)
        self.assertEqual(12, result.active_e1_receipt_count)
        self.assertFalse(result.result_decision_permitted)

    def test_fail_fast_stops_at_first_kernel_error_without_result(self) -> None:
        calls = []

        def failing_kernel(batch, arm_id):
            calls.append((batch.batch_index, arm_id))
            if len(calls) == 4:
                raise RuntimeError("fixture stop")
            return build_synthetic_pilot_arm_receipt(batch, arm_id)

        with self.assertRaisesRegex(RuntimeError, "fixture stop"):
            run_repetition_pilot_runner_fixture(self.contract, failing_kernel)

        self.assertEqual(4, len(calls))
        self.assertEqual((0, "continuous_formation_ablated"), calls[-1])

    def test_mismatched_receipt_is_rejected_immediately(self) -> None:
        def wrong_kernel(batch, arm_id):
            return build_synthetic_pilot_arm_receipt(
                batch, "p0_continuous" if arm_id == "p0_repeated" else arm_id
            )

        with self.assertRaisesRegex(ValueError, "current batch role"):
            run_repetition_pilot_runner_fixture(self.contract, wrong_kernel)

    def test_runner_contains_no_field_writer_or_decision_path(self) -> None:
        source = inspect.getsource(run_repetition_pilot_runner_fixture)
        for forbidden in (
            "run_prepared_real_formation_arm_in_memory",
            "advance_",
            "write_text",
            "write_bytes",
            "_atomic_publish",
            "technical_decision",
        ):
            self.assertNotIn(forbidden, source)

    def test_protected_report_remains_unchanged(self) -> None:
        before = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        run_repetition_pilot_runner_fixture(self.contract)
        after = hashlib.sha256(REPORT.read_bytes()).hexdigest()

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
