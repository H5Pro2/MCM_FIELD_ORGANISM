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
    E1RepetitionPilotReleaseContractError,
    S1_EC29_FIELD_ARM_STEPS,
    build_e1_repetition_pilot_release_contract,
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


class E1RepetitionPilotReleaseContractTests(unittest.TestCase):
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
        cls.plans = build_e1_repetition_formation_plans(formation, bundle)
        cls.fixture = run_repetition_formation_fixture_consumer(
            cls.plans.pairs[1], values.initial_field, values.initial_state
        )

    def test_contract_binds_six_ordered_batches_and_exact_load(self) -> None:
        result = build_e1_repetition_pilot_release_contract(
            self.plans, self.fixture
        )

        self.assertEqual(6, len(result.batches))
        self.assertEqual((1, 1, 1, 2, 2, 2), tuple(
            item.contact_count for item in result.batches
        ))
        self.assertEqual(S1_EC29_FIELD_ARM_STEPS, result.field_arm_step_count)
        self.assertEqual(
            result.field_arm_step_count,
            sum(item.field_arm_step_count for item in result.batches),
        )

    def test_p0_ablation_and_active_roles_are_separate(self) -> None:
        result = build_e1_repetition_pilot_release_contract(
            self.plans, self.fixture
        )

        self.assertEqual(
            (
                "p0_repeated",
                "p0_continuous",
                "repeated_formation_ablated",
                "continuous_formation_ablated",
                "repeated_active",
                "continuous_active",
            ),
            result.arms,
        )

    def test_execution_decision_persistence_and_claims_remain_locked(self) -> None:
        result = build_e1_repetition_pilot_release_contract(
            self.plans, self.fixture
        )

        self.assertTrue(result.runner_implementation_permitted)
        self.assertFalse(result.pilot_execution_permitted)
        self.assertFalse(result.persistence_permitted)
        self.assertFalse(result.result_decision_permitted)
        self.assertFalse(result.imprinting_claim_permitted)

    def test_batch_order_change_is_rejected(self) -> None:
        result = build_e1_repetition_pilot_release_contract(
            self.plans, self.fixture
        )
        with self.assertRaises(E1RepetitionPilotReleaseContractError):
            replace(result.batches[0], batch_index=1)

    def test_builder_contains_no_runner_writer_or_resource_measurement(self) -> None:
        source = inspect.getsource(build_e1_repetition_pilot_release_contract)
        for forbidden in (
            "run_repetition_formation_fixture_consumer",
            "run_prepared_real_formation_arm_in_memory",
            "psutil",
            "disk_usage",
            "write_text",
            "write_bytes",
            "_atomic_publish",
        ):
            self.assertNotIn(forbidden, source)

    def test_protected_report_remains_unchanged(self) -> None:
        before = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        build_e1_repetition_pilot_release_contract(self.plans, self.fixture)
        after = hashlib.sha256(REPORT.read_bytes()).hexdigest()

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
