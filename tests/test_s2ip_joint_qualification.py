"""Corrected one-shot S2-IP assembly for the neutral S2-IN qualification."""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest

from tests import test_s2id_private_two_area_conflict_signal as s2id
from tests import test_s2io_joint_qualification as s2io


QUALIFICATION_ID = "s2ip-joint-qualification-20260901-01"

SIGNAL_TEST_METHODS = (
    "test_01_all_ten_paths_and_role_swaps_match_the_direct_baseline",
    "test_02_status_boundaries_are_exclusive",
    "test_03_atomic_owner_read_only_and_no_selection",
    "test_04_e001_type_or_schema_fails_without_regular_result",
    "test_05_e002_source_or_digest_mutation_fails_closed",
    "test_06_e003_owner_binding_mutation_fails_closed",
    "test_07_e004_probe_mask_mutation_fails_closed",
    "test_08_e005_area_evidence_mutation_fails_closed",
    "test_09_e006_read_only_state_mutation_fails_closed",
    "test_10_e007_resource_mutation_fails_closed",
    "test_11_e008_owner_reuse_is_terminal_and_has_no_second_output",
    "test_12_ledger_formulas_cover_every_reachable_count_pair",
    "test_13_worst_case_owner_and_success_artifacts_respect_limits",
    "test_14_identifier_overflow_is_rejected_before_an_owner_exists",
)

JOINT_TEST_METHODS = (
    "test_15_distinct_retrieval_and_signal_probes_bind_without_digest_equality",
    "test_16_swapped_case_plan_and_probe_relations_fail_closed",
    "test_17_owner_is_atomic_and_rejects_a_foreign_pairing",
    "test_18_candidates_remain_bound_to_retrieval_and_status_to_signal_probe",
    "test_19_registry_gate_and_complete_neutral_recording_are_valid",
    "test_20_event_and_receipt_manipulations_are_rejected",
    "test_21_complete_and_not_evaluable_are_exclusive",
    "test_22_all_76_parent_sets_are_canonical_and_independently_reconstructed",
    "test_23_zero_and_single_parent_operations_keep_the_legacy_projection",
    "test_24_duplicate_parent_is_rejected_by_both_materializers",
    "test_25_missing_parent_is_rejected_by_both_materializers",
    "test_26_foreign_parent_is_rejected_by_both_materializers",
    "test_27_later_parent_is_rejected_by_both_materializers",
    "test_28_op_171_maximum_owner_start_is_exactly_814_bytes",
    "test_29_all_envelopes_from_171_through_183_respect_the_bound_table",
    "test_30_each_bootstrap_partial_failure_is_start_rejected",
    "test_31_full_bootstrap_is_atomic_bounded_and_activates_at_operation_three",
    "test_32_start_rejected_lifecycle_mutations_are_invalid",
    "test_33_append_only_reuse_is_rejected_without_changing_complete_run",
    "test_34_lifecycle_bounds_and_registry_remain_exact",
)


class S2IPSignalQualificationTests(s2id.S2IDPrivateTwoAreaConflictSignalTests):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="s2ip-signal-")
        cls._case_root = Path(cls._temporary.name).resolve()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def setUp(self) -> None:
        self.output_directory = self._case_root / self._testMethodName
        self.output_directory.mkdir(parents=False, exist_ok=False)


class S2IPJointQualificationTests(s2io.S2IOJointQualificationTests):
    # The corrected body below replaces the obsolete inherited ie-op-002 test.
    # The differently named S2-IO correction is hidden from active discovery.
    test_21_complete_and_post_bootstrap_not_evaluable_are_exclusive = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="s2ip-joint-")
        cls._case_root = Path(cls._temporary.name).resolve()
        fixture_root = cls._case_root / "shared-neutral-fixture"
        fixture_root.mkdir()
        cls.valid_run = s2io._complete_neutral_recording(
            fixture_root, "s2ip-neutral-complete-01"
        )

    def setUp(self) -> None:
        self.root = self._case_root / self._testMethodName
        self.root.mkdir(parents=False, exist_ok=False)
        if self._testMethodName == "test_33_append_only_reuse_is_rejected_without_changing_complete_run":
            local = self.root / "s2io-neutral-complete-01"
            shutil.copytree(self.valid_run, local)
            self.valid_run = local

    def test_21_complete_and_not_evaluable_are_exclusive(self) -> None:
        s2io.S2IOJointQualificationTests.test_21_complete_and_post_bootstrap_not_evaluable_are_exclusive(
            self
        )


def _active_ids(class_name: str, methods: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"{__name__}.{class_name}.{method}" for method in methods)


ACTIVE_TEST_IDS = (
    *_active_ids("S2IPSignalQualificationTests", SIGNAL_TEST_METHODS),
    *_active_ids("S2IPJointQualificationTests", JOINT_TEST_METHODS),
)

ACTIVE_OUTPUT_ROLES = tuple(f"case-output/{index:02d}-{method}" for index, method in enumerate(
    (*SIGNAL_TEST_METHODS, *JOINT_TEST_METHODS),
    1,
))


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    signal_names = tuple(loader.getTestCaseNames(S2IPSignalQualificationTests))
    joint_names = tuple(loader.getTestCaseNames(S2IPJointQualificationTests))
    discovered_ids = (
        *_active_ids("S2IPSignalQualificationTests", signal_names),
        *_active_ids("S2IPJointQualificationTests", joint_names),
    )
    if signal_names != SIGNAL_TEST_METHODS or joint_names != JOINT_TEST_METHODS:
        raise RuntimeError("S2-IP active test list differs from the static registration")
    if discovered_ids != ACTIVE_TEST_IDS or len(set(discovered_ids)) != len(discovered_ids):
        raise RuntimeError("S2-IP contains a duplicate or displaced test ID")
    if len(ACTIVE_OUTPUT_ROLES) != len(ACTIVE_TEST_IDS) or len(set(ACTIVE_OUTPUT_ROLES)) != len(ACTIVE_OUTPUT_ROLES):
        raise RuntimeError("S2-IP contains a duplicate output role")
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(S2IPSignalQualificationTests))
    suite.addTests(loader.loadTestsFromTestCase(S2IPJointQualificationTests))
    return suite


if __name__ == "__main__":
    unittest.main()
