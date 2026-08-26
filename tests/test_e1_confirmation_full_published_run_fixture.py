from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_full_formation_resource_preflight import (
    preflight_prepared_full_formation_resources,
)
from mcm_field_organism.e1_confirmation_full_published_run_contract import (
    S1_EC16_TRANSITIONS,
    prepare_full_formation_published_run_contract,
)
from mcm_field_organism.e1_confirmation_full_published_run_fixture import (
    E1ConfirmationFullPublishedRunFixtureError,
    S1_EC17_POLICY_DIGEST,
    execute_full_published_run_fixture_once,
    load_full_published_run_fixture_payload,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from tests.test_e1_confirmation_full_formation_handoff import (
    S1_EC13_REPORT,
    S1_EC13_REPORT_SHA256,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


class E1ConfirmationFullPublishedRunFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_directory = TemporaryDirectory()
        cls.target_directory = TemporaryDirectory()
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        source_run = prepare_e1_confirmation_synthetic_run_contract(
            descriptor, Path(cls.source_directory.name)
        )
        cls.bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            source_run, UPSTREAM
        )
        cls.preflight = preflight_prepared_full_formation_resources(cls.bundle)
        cls.contract = prepare_full_formation_published_run_contract(
            cls.preflight, Path(cls.target_directory.name)
        )
        cls.receipt = execute_full_published_run_fixture_once(
            cls.contract, cls.bundle
        )
        cls.report = json.loads(
            Path(cls.receipt.report_path).read_text(encoding="ascii")
        )
        cls.matrix = load_full_published_run_fixture_payload(
            cls.report["payload"]
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.target_directory.cleanup()
        cls.source_directory.cleanup()

    def test_real_small_matrix_crosses_complete_aggregate_lifecycle(self) -> None:
        self.assertEqual(
            "e145102b7dc391bb3f999f0afb37d76583905036cdd7fe5d021f3c2e97cecae3",
            S1_EC17_POLICY_DIGEST,
        )
        self.assertTrue(self.receipt.attempt_present_during_fixture_execution)
        self.assertTrue(self.receipt.final_reread_verified)
        self.assertTrue(self.receipt.typed_reload_verified)
        self.assertFalse(self.receipt.full_formation_executed)
        self.assertEqual(self.matrix.result_digest, self.receipt.matrix_result_digest)
        self.assertFalse(Path(self.contract.attempt_path).exists())
        self.assertFalse(Path(self.contract.lock_path).exists())
        self.assertTrue(Path(self.contract.report_path).is_file())

    def test_report_contains_all_fifteen_full_geometry_states(self) -> None:
        states = tuple(
            arm.output_state
            for refinement in self.matrix.refinements
            for arm in refinement.arms
        )

        self.assertEqual(15, len(states))
        self.assertEqual(2_175, sum(len(item.edge_bindings) for item in states))
        self.assertTrue(self.matrix.all_five_arm_controls_passed)
        self.assertTrue(self.matrix.prepared_inputs_preserved)

    def test_transition_coverage_marks_only_two_fixture_substitutions(self) -> None:
        coverage = dict(self.receipt.transition_coverage)

        self.assertEqual(set(S1_EC16_TRANSITIONS), set(coverage))
        self.assertEqual(
            "substituted-small-real-fixture",
            coverage["execute-full-r2-r4-r8-five-arm-formation"],
        )
        self.assertEqual(
            "observed-fixture-schema-equivalent",
            coverage[
                "build-complete-s1ec14-payload-while-states-are-live"
            ],
        )
        self.assertEqual(11, tuple(coverage.values()).count("observed"))

    def test_successful_identity_rejects_second_execution(self) -> None:
        with self.assertRaises(ValueError):
            execute_full_published_run_fixture_once(
                self.contract,
                self.bundle,
                lambda *_args: self.matrix,
            )

    def test_reload_failure_retains_attempt_and_blocks_retry(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_full_formation_published_run_contract(
                self.preflight, Path(directory)
            )
            with patch(
                "mcm_field_organism.e1_confirmation_full_published_run_fixture."
                "load_full_published_run_fixture_payload",
                side_effect=ValueError("fixture reload failure"),
            ):
                with self.assertRaisesRegex(ValueError, "fixture reload failure"):
                    execute_full_published_run_fixture_once(
                        contract,
                        self.bundle,
                        lambda *_args: self.matrix,
                    )

            self.assertTrue(Path(contract.attempt_path).is_file())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaises(ValueError):
                execute_full_published_run_fixture_once(
                    contract,
                    self.bundle,
                    lambda *_args: self.matrix,
                )

    def test_executor_contains_no_full_formation_or_probe_call(self) -> None:
        source = inspect.getsource(execute_full_published_run_fixture_once)

        for forbidden in (
            "execute_prepared_full_formation_lifecycle",
            "consume_prepared_full_formation",
            "run_seven_arm_probe",
            "run_e1_confirmation_probe",
            "reports/",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1ec13_and_terminal_artifacts_remain_unchanged(self) -> None:
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        load_full_published_run_fixture_payload(self.report["payload"])
        after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )

        self.assertEqual(before, after)
        self.assertEqual(
            S1_EC13_REPORT_SHA256,
            hashlib.sha256(S1_EC13_REPORT.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
