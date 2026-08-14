from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_descriptor_refinement_planner import (
    build_e1_confirmation_descriptor_refinement_plans,
)
from mcm_field_organism.e1_confirmation_prepared_formation_consumer import (
    _typed_values_from_bundle,
)
from mcm_field_organism.e1_confirmation_published_probe_fixture_consumer import (
    S1_EC21_CONSUMER_ID,
    _run_refinement_fixture,
    run_published_probe_fixture_consumer,
)
from mcm_field_organism.e1_confirmation_published_probe_handoff_audit import (
    audit_published_probe_handoff,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_confirmation_small_refinement_matrix import (
    run_small_real_refinement_matrix,
)
from mcm_field_organism.receptor_time_model import ReceptorTimeSequence
from tests.test_e1_confirmation_full_formation_handoff import (
    S1_EC13_REPORT,
    S1_EC13_REPORT_SHA256,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "synthetic_runs" / "s1ec19_full_published_once_v1"
REPORT = DIRECTORY / "e1_full_formation_published_s1ec19_once_v1.json"


class E1ConfirmationPublishedProbeFixtureConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protected_paths = (*CANONICAL_TARGETS, S1_EC13_REPORT, REPORT)
        cls.protected_before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in cls.protected_paths
        )
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(
            descriptor, DIRECTORY
        )
        cls.bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        cls.audit = audit_published_probe_handoff(REPORT, cls.bundle)
        values = _typed_values_from_bundle(cls.bundle)
        cls.fixture_probe = tuple(
            ReceptorTimeSequence(
                item.modality_id,
                item.geometry_id,
                item.clock_id,
                (item.frames[0],),
            )
            for item in values.probe_sequences
        )
        cls.fixture_probe_plans = build_e1_confirmation_descriptor_refinement_plans(
            values.corridor,
            cls.fixture_probe,
            horizon_start_tick=0,
            horizon_end_tick=1_000_000,
            ticks_per_second=1_000_000.0,
        )
        cls.fixture = run_small_real_refinement_matrix(
            values.av_permutation.history_ab,
            values.av_permutation.history_ba,
            values.initial_field,
            values.initial_state,
        )
        cls.result = run_published_probe_fixture_consumer(
            cls.audit,
            cls.bundle,
            cls.fixture,
            cls.fixture_probe,
            cls.fixture_probe_plans,
        )
        cls.protected_after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in cls.protected_paths
        )

    def test_all_three_refinements_cross_all_seven_arms(self) -> None:
        self.assertEqual(S1_EC21_CONSUMER_ID, self.result.consumer_id)
        self.assertEqual(
            ("r2", "r4", "r8"),
            tuple(item.refinement_id for item in self.result.refinements),
        )
        self.assertTrue(self.result.all_registered_controls_passed)
        for item in self.result.refinements:
            self.assertEqual(7, len(item.field_digests))
            self.assertEqual(0.0, item.probe_ablation_residual)
            self.assertEqual(0.0, item.fixed_adapter_residual)
            self.assertEqual(0.0, item.frozen_state_change)

    def test_fixture_is_explicit_and_no_decision_is_opened(self) -> None:
        self.assertTrue(self.result.fixture_payload_only)
        self.assertFalse(self.result.persistent_states_consumed)
        self.assertFalse(self.result.registered_probe_consumed)
        self.assertFalse(self.result.probe_execution_permitted)
        self.assertFalse(self.result.result_decision_permitted)
        self.assertFalse(self.result.claims_permitted)

    def test_consumer_is_repeatable(self) -> None:
        values = _typed_values_from_bundle(self.bundle)
        first = _run_refinement_fixture(
            self.fixture.refinements[0],
            self.fixture_probe_plans.plans[0],
            values.initial_field,
        )
        second = _run_refinement_fixture(
            self.fixture.refinements[0],
            self.fixture_probe_plans.plans[0],
            values.initial_field,
        )

        self.assertEqual(first, second)

    def test_consumer_has_no_report_loader_writer_or_decision_path(self) -> None:
        source = inspect.getsource(run_published_probe_fixture_consumer)

        for forbidden in (
            "read_text",
            "read_bytes",
            "load_full_formation_handoff_payload",
            "_atomic_publish",
            "_exclusive_marker",
            "technical_decision",
            "memory_claim",
        ):
            self.assertNotIn(forbidden, source)

    def test_persistent_and_terminal_artifacts_remain_unchanged(self) -> None:
        self.assertEqual(self.protected_before, self.protected_after)
        self.assertEqual(
            S1_EC13_REPORT_SHA256,
            hashlib.sha256(S1_EC13_REPORT.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
