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
from mcm_field_organism.e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
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


class E1RepetitionFormationFixtureConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(
            descriptor, SOURCE_DIRECTORY
        )
        cls.bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        values = _typed_values_from_bundle(cls.bundle)
        cls.field = values.initial_field
        cls.state = values.initial_state
        gap = audit_e1_memory_function_gaps(REPORT)
        contract = build_e1_repetition_formation_contract(gap, cls.bundle)
        plans = build_e1_repetition_formation_plans(contract, cls.bundle)
        cls.pair = plans.pairs[1]

    def test_small_real_fixture_passes_all_lifecycle_controls(self) -> None:
        result = run_repetition_formation_fixture_consumer(
            self.pair, self.field, self.state
        )

        self.assertEqual(4, result.fixture_support_count_per_active_arm)
        self.assertEqual(8, result.fixture_step_count_per_arm)
        self.assertTrue(result.initial_inputs_preserved)
        self.assertTrue(result.source_plans_preserved)
        self.assertTrue(result.formation_ablation_neutral)
        self.assertTrue(result.snapshot_restore_roundtrip_exact)
        self.assertFalse(result.result_decision_permitted)

    def test_fixture_is_deterministic_and_preserves_inputs(self) -> None:
        field_digest = _initial_field_digest(self.field)
        state_digest = _initial_state_digest(self.state)
        plan_digest = self.pair.pair_digest

        first = run_repetition_formation_fixture_consumer(
            self.pair, self.field, self.state
        )
        second = run_repetition_formation_fixture_consumer(
            self.pair, self.field, self.state
        )

        self.assertEqual(first.result_digest, second.result_digest)
        self.assertEqual(field_digest, _initial_field_digest(self.field))
        self.assertEqual(state_digest, _initial_state_digest(self.state))
        self.assertEqual(plan_digest, self.pair.pair_digest)

    def test_kernel_failure_yields_no_partial_result_or_input_change(self) -> None:
        field_digest = _initial_field_digest(self.field)
        state_digest = _initial_state_digest(self.state)
        calls = []

        def failing_kernel(*args):
            calls.append(args[0])
            raise RuntimeError("synthetic stop")

        with self.assertRaisesRegex(RuntimeError, "synthetic stop"):
            run_repetition_formation_fixture_consumer(
                self.pair,
                self.field,
                self.state,
                kernel=failing_kernel,
            )

        self.assertEqual(["ab"], calls)
        self.assertEqual(field_digest, _initial_field_digest(self.field))
        self.assertEqual(state_digest, _initial_state_digest(self.state))

    def test_consumer_contains_no_builder_persistence_or_probe(self) -> None:
        source = inspect.getsource(run_repetition_formation_fixture_consumer)
        for forbidden in (
            "build_e1_repetition_formation_plans",
            "build_e1_confirmation_research_corridor",
            "advance_frozen_e1",
            "write_text",
            "write_bytes",
            "_atomic_publish",
            "report_path",
        ):
            self.assertNotIn(forbidden, source)

    def test_protected_report_remains_unchanged(self) -> None:
        before = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        run_repetition_formation_fixture_consumer(
            self.pair, self.field, self.state
        )
        after = hashlib.sha256(REPORT.read_bytes()).hexdigest()

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
