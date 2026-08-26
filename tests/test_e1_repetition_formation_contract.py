from __future__ import annotations

from dataclasses import replace
import hashlib
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_memory_function_gap_audit import (
    audit_e1_memory_function_gaps,
)
from mcm_field_organism.e1_repetition_formation_contract import (
    E1RepetitionFormationContractError,
    S1_EC26_CONTACT_COUNTS,
    S1_EC26_HORIZON_TICKS,
    build_e1_repetition_formation_contract,
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


class E1RepetitionFormationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(
            descriptor, SOURCE_DIRECTORY
        )
        cls.bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        cls.gap_audit = audit_e1_memory_function_gaps(REPORT)

    def test_contract_binds_exposure_matched_schedules(self) -> None:
        result = build_e1_repetition_formation_contract(
            self.gap_audit, self.bundle
        )

        self.assertEqual(
            S1_EC26_CONTACT_COUNTS,
            tuple(item.contact_count for item in result.schedules),
        )
        for schedule in result.schedules:
            self.assertEqual(S1_EC26_HORIZON_TICKS, schedule.horizon_end_tick)
            self.assertEqual(
                schedule.contact_count * 1_000_000,
                schedule.total_contact_ticks,
            )
            self.assertEqual(
                schedule.contact_count * 110,
                schedule.expected_event_count,
            )
            self.assertEqual(
                schedule.repeated_start_ticks[-1] + 1_000_000,
                schedule.continuous_end_tick,
            )

    def test_one_contact_pair_is_an_identity_control(self) -> None:
        result = build_e1_repetition_formation_contract(
            self.gap_audit, self.bundle
        )
        one = result.schedules[0]

        self.assertEqual((0,), one.repeated_start_ticks)
        self.assertEqual((0, 1_000_000), (
            one.continuous_start_tick, one.continuous_end_tick
        ))

    def test_schedule_change_is_rejected(self) -> None:
        result = build_e1_repetition_formation_contract(
            self.gap_audit, self.bundle
        )
        with self.assertRaises(E1RepetitionFormationContractError):
            replace(
                result.schedules[-1],
                repeated_start_ticks=(0, 2_000_000),
            )

    def test_contract_build_has_no_field_runner_or_writer(self) -> None:
        source = inspect.getsource(build_e1_repetition_formation_contract)
        for forbidden in (
            "advance_",
            "execute_",
            "run_full",
            "write_text",
            "write_bytes",
            "_atomic_publish",
        ):
            self.assertNotIn(forbidden, source)

    def test_contract_permits_only_planner_implementation(self) -> None:
        result = build_e1_repetition_formation_contract(
            self.gap_audit, self.bundle
        )

        self.assertTrue(result.planner_implementation_permitted)
        self.assertFalse(result.field_execution_permitted)
        self.assertFalse(result.result_decision_permitted)
        self.assertFalse(result.imprinting_claim_permitted)

    def test_protected_report_remains_unchanged(self) -> None:
        before = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        build_e1_repetition_formation_contract(self.gap_audit, self.bundle)
        after = hashlib.sha256(REPORT.read_bytes()).hexdigest()

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
