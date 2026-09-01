from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2ig_private_append_only_recorder as recording
from tools import _s2ig_private_fixture_registry as fixtures
from tools import _s2ig_private_result_verifier as verifier
from tools import _s2ig_private_runner as runner
from tools import _s2jk_private_direct_end_to_end_baseline as context_baseline
from tools import _s2jk_private_end_to_end_context_use as context_use
from tests.test_s2jk_private_end_to_end_context_use import _fixture


QUALIFICATION_ID = "s2jl-s2ig-end-to-end-integration-qualification-20260901-02"
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


def _comparison(
    signal_input: signal_contract.TwoAreaConflictSignalInput,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
) -> signal_contract.MaskedSupplementComparison:
    if a_finding.status == b_finding.status == "APPLICABLE":
        differing = tuple(
            position
            for position, left, right in zip(
                signal_contract.probe_contract.MASKED_POSITIONS,
                a_finding.masked_values,
                b_finding.masked_values,
                strict=True,
            )
            if left != right
        )
        status = "DIFFERENT" if differing else "EQUAL"
    else:
        differing = ()
        status = "NOT_PERFORMED"
    return signal_contract.MaskedSupplementComparison.build(
        signal_input,
        a_finding,
        b_finding,
        status,
        differing,
    )


def _integrated(status: str, tag: str, case_id: str = "c01"):
    probe, bundle, signal_commit, _old_admission, a_finding, b_finding = _fixture(status, tag)
    signal_input = signal_contract.TwoAreaConflictSignalInput.build(
        f"neutral-signal-{tag}",
        "SIGNAL",
        probe,
        bundle,
    )
    comparison = _comparison(signal_input, a_finding, b_finding)
    evidence = runner._SignalEvidenceCommit(
        signal_commit,
        a_finding,
        b_finding,
        comparison,
    )
    admission = runner._admit_signal_evidence(
        runner._case_runtime_identifiers(case_id),
        signal_input,
        evidence,
    )
    current = runner._current_only_projection(probe, bundle)
    plus = context_use.use_admitted_context(
        probe,
        bundle,
        signal_commit,
        admission,
        a_finding,
        b_finding,
    )
    direct = context_baseline.compose_direct_admission_and_fill(
        probe,
        bundle,
        signal_commit,
        admission,
        a_finding,
        b_finding,
    )
    return probe, bundle, signal_commit, admission, current, plus, direct, a_finding, b_finding


def _envelope_size(result: dict[str, object]) -> int:
    envelope = {
        "schema": recording.RECORDER_SCHEMA,
        "operation_id": "ie-op-999",
        "owner_id": "a" * 96,
        "reservation_digest": "0" * 64,
        "start_event_digest": "1" * 64,
        "artifact": {"result": result},
    }
    return len(recording.canonical_bytes(envelope))


class TestS2JLS2IGEndToEndIntegration(unittest.TestCase):
    def test_01_registry_adds_exactly_forty_context_operations(self) -> None:
        fixtures.validate_literal_fixtures()
        self.assertEqual(fixtures.SUCCESS_OPERATION_COUNT, 223)
        self.assertEqual(fixtures.SUCCESS_EVENT_COUNT, 446)
        rows = fixtures.OPERATION_ROWS[170:210]
        self.assertEqual(len(rows), 40)
        expected = (
            "CONTEXT_ADMISSION_INVOKE",
            "CURRENT_PERCEPTION_ONLY_PROJECT",
            "ADMITTED_CONTEXT_USE_INVOKE",
            "DIRECT_CONTEXT_USE_BASELINE_INVOKE",
            "CONTEXT_USE_CASE_EVIDENCE_SEAL",
        )
        for offset in range(0, 40, 5):
            self.assertEqual(tuple(row.operation_class for row in rows[offset : offset + 5]), expected)

    def test_02_exact_operation_parent_and_receipt_roles(self) -> None:
        for case_index in range(8):
            base = 171 + 5 * case_index
            rows = fixtures.OPERATION_ROWS[base - 1 : base + 4]
            self.assertEqual(rows[0].receipt_type, "S2IGContextAdmissionReceipt")
            self.assertEqual(rows[1].receipt_type, "S2IGCurrentOnlyReceipt")
            self.assertEqual(rows[2].parent_operations, (rows[0].operation_id, rows[1].operation_id))
            self.assertEqual(rows[3].parent_operations, (rows[0].operation_id, rows[1].operation_id))
            self.assertEqual(len(rows[4].parent_operations), 5)
        self.assertEqual(fixtures.OPERATION_ROWS[210].operation_class, "EXECUTION_EVIDENCE_SEAL")

    def test_03_exact_success_failure_and_parent_budgets(self) -> None:
        self.assertEqual(fixtures.MAX_SUCCESS_PATH_BYTES, 1_283_226)
        self.assertEqual(fixtures.MAX_FAILURE_PATH_BYTES, 1_290_394)
        self.assertEqual(fixtures.COMPACT_PARENT_OPERATION_COUNT, 116)
        self.assertEqual(fixtures.COMPACT_PARENT_REFERENCE_COUNT, 294)
        self.assertEqual(fixtures.TOTAL_INTERNAL_PARENT_REFERENCE_COUNT, 400)
        added_artifacts = 8 * (3_072 + 1_536 + 3_584 + 3_584 + 3_584)
        added_events = 80 * fixtures.MAX_EVENT_BYTES
        self.assertEqual(added_artifacts, 122_880)
        self.assertEqual(added_events, 122_880)
        execution_row = fixtures.OPERATION_ROWS[210]
        parents = tuple(
            (parent, fixtures.canonical_digest({"neutral-parent": parent}))
            for parent in execution_row.parent_operations
        )
        parent_set = fixtures.materialize_parent_set(
            execution_row,
            fixtures.REGISTRY,
            "0" * 64,
            parents,
        )
        self.assertEqual(parent_set.parent_count, 8)
        self.assertLessEqual(
            len(fixtures.canonical_bytes(parent_set.payload_without_digest())),
            fixtures.MAX_PARENT_SET_PREIMAGE_BYTES,
        )

    def test_04_independent_registry_and_evaluation_roots_match(self) -> None:
        expected_rows = verifier._expected_rows()
        self.assertEqual(len(expected_rows), 223)
        for actual, independent in zip(fixtures.OPERATION_ROWS, expected_rows, strict=True):
            self.assertEqual(actual.operation_id, independent["operation_id"])
            self.assertEqual(actual.operation_class, independent["operation_class"])
            self.assertEqual(actual.parent_operations, independent["parents"])
            self.assertEqual(actual.receipt_type, independent["receipt_type"])
            self.assertEqual(actual.output_max_bytes, independent["limit"])
        root = verifier.expected_evaluation_root(WORKSPACE_ROOT)
        bindings = tuple(
            runner.EvaluationCaseBinding.build(case_id, status, completion, target)
            for case_id, status, completion, target, _digest in root["case_bindings"]
        )
        plan = runner.bind_evaluation_plan(
            root["plan_id"],
            bindings,
            root["evaluation_source_digests"],
        )
        self.assertEqual(plan.seal_digest, root["seal_digest"])

    def test_05_all_five_statuses_cross_admission_current_plus_and_baseline(self) -> None:
        cases = (
            "CONSISTENT",
            "CONFLICT",
            "SINGLE_SOURCE_A",
            "NO_CONTEXT",
            "NO_APPLICABLE_CONTEXT",
        )
        for ordinal, status in enumerate(cases, start=1):
            with self.subTest(status=status):
                probe, bundle, _signal, admission, current, plus, direct, _a, _b = _integrated(
                    status,
                    f"integrated-{ordinal}",
                )
                self.assertEqual(current["output_values"], probe.values)
                self.assertEqual(plus.output_values, direct.output_values)
                self.assertEqual(plus.source_signal_status, admission.result.source_signal_status)
                self.assertEqual(plus.prestate_digest, plus.poststate_digest)
                self.assertEqual(plus.prestate_digest, bundle.composite_state_digest)

    def test_06_single_source_mirror_and_consistent_have_no_preference(self) -> None:
        a = _integrated("SINGLE_SOURCE_A", "mirror-a", "c04")[5]
        b = _integrated("SINGLE_SOURCE_B", "mirror-b", "c05")[5]
        consistent = _integrated("CONSISTENT", "mirror-consistent")[5]
        self.assertEqual(a.admitted_role, "A_RECENT")
        self.assertEqual(b.admitted_role, "B_STABLE")
        self.assertIsNone(consistent.admitted_role)
        self.assertIsNotNone(consistent.equivalent_role_set_digest)
        self.assertIsNone(consistent.selected_area)

    def test_07_withheld_cases_do_not_enter_the_fill_helper(self) -> None:
        for ordinal, status in enumerate(("CONFLICT", "NO_CONTEXT", "NO_APPLICABLE_CONTEXT"), start=1):
            fixture = _integrated(status, f"withheld-setup-{ordinal}")
            probe, bundle, signal, admission, _current, _plus, _direct, a_finding, b_finding = fixture
            with patch.object(context_use, "_apply_admitted_supplement", side_effect=AssertionError("fill forbidden")) as helper, patch.object(
                context_baseline,
                "_direct_fill",
                side_effect=AssertionError("direct fill forbidden"),
            ) as direct_helper:
                result = context_use.use_admitted_context(
                    probe,
                    bundle,
                    signal,
                    admission,
                    a_finding,
                    b_finding,
                )
                direct_result = context_baseline.compose_direct_admission_and_fill(
                    probe,
                    bundle,
                    signal,
                    admission,
                    a_finding,
                    b_finding,
                )
            helper.assert_not_called()
            direct_helper.assert_not_called()
            self.assertEqual(result.output_values, probe.values)
            self.assertEqual(direct_result.output_values, probe.values)

    def test_08_compact_receipts_fit_all_bound_envelopes(self) -> None:
        _probe, _bundle, _signal, admission, current, plus, direct, _a, _b = _integrated(
            "CONSISTENT",
            "receipt-size",
        )
        receipts = (
            (runner._context_admission_receipt(admission), 3_072),
            (runner._current_only_receipt(current), 1_536),
            (runner._context_use_receipt(plus, "END_TO_END_ADAPTER"), 3_584),
            (
                runner._context_use_receipt(direct, "DIRECT_COMPOSITION_BASELINE"),
                3_584,
            ),
        )
        for receipt, limit in receipts:
            self.assertLessEqual(_envelope_size(receipt), limit)
            self.assertLessEqual(_envelope_size(receipt), fixtures.MAX_INDIVIDUAL_ARTIFACT_BYTES)

    def test_09_current_only_is_pure_and_read_only(self) -> None:
        probe, bundle, *_rest = _fixture("SINGLE_SOURCE_A", "current-only")
        before = (probe.probe_digest, bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        result = runner._current_only_projection(probe, bundle)
        after = (probe.probe_digest, bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        self.assertEqual(before, after)
        self.assertEqual(result["input_values"], result["output_values"])
        self.assertEqual(result["completed_positions"], ())
        self.assertEqual(result["memory_receptor_or_field_call_count"], 0)

    def test_10_manipulated_admission_stops_before_context_output(self) -> None:
        fixture = _integrated("SINGLE_SOURCE_A", "admission-mutation")
        admission = fixture[3]
        object.__setattr__(admission.result, "result_digest", "0" * 64)
        with self.assertRaises(context_use.S2JKContextUseError):
            context_use.use_admitted_context(
                fixture[0],
                fixture[1],
                fixture[2],
                admission,
                fixture[7],
                fixture[8],
            )

    def test_11_verifier_checks_withheld_context_receipts_and_successors(self) -> None:
        probe, bundle, signal, admission, current, plus, direct, _a, _b = _integrated(
            "CONFLICT",
            "verifier-withheld",
        )
        admission_receipt = runner._context_admission_receipt(admission)
        current_receipt = runner._current_only_receipt(current)
        plus_receipt = runner._context_use_receipt(plus, "END_TO_END_ADAPTER")
        direct_receipt = runner._context_use_receipt(direct, "DIRECT_COMPOSITION_BASELINE")
        operation_ids = ("ie-op-171", "ie-op-172", "ie-op-173", "ie-op-174", "ie-op-175")
        artifact_digests = {
            operation_id: hashlib.sha256(operation_id.encode("ascii")).hexdigest()
            for operation_id in operation_ids
        }
        legacy_digest = hashlib.sha256(b"legacy-case").hexdigest()
        context_evidence = {
            "probe_digest": probe.probe_digest,
            "bundle_digest": bundle.bundle_digest,
            "admission_result_digest": admission.result.result_digest,
            "completion_status": plus.completion_status,
            "probe_values": probe.values,
            "current_only_values": current["output_values"],
            "plus_values": plus.output_values,
            "direct_baseline_values": direct.output_values,
            "plus_equals_direct_baseline": True,
            "all_read_only": True,
            "status_recomputation_count": 0,
            "applicability_recomputation_count": 0,
            "admission_artifact_digest": artifact_digests[operation_ids[0]],
            "current_only_artifact_digest": artifact_digests[operation_ids[1]],
            "plus_artifact_digest": artifact_digests[operation_ids[2]],
            "direct_baseline_artifact_digest": artifact_digests[operation_ids[3]],
            "legacy_case_evidence_artifact_digest": legacy_digest,
        }
        evidence = {"signal_status": signal.result.status}
        errors: list[str] = []
        verifier._validate_s2jk_context_use_case(
            case_id="c02",
            expected_target=None,
            evidence=evidence,
            context_evidence=context_evidence,
            admission=admission_receipt,
            current=current_receipt,
            plus=plus_receipt,
            direct=direct_receipt,
            artifact_digests=artifact_digests,
            operation_ids=operation_ids,
            errors=errors,
        )
        self.assertEqual(errors, [])
        altered = dict(plus_receipt)
        altered["bundle_digest"] = "0" * 64
        verifier._validate_s2jk_context_use_case(
            case_id="c02",
            expected_target=None,
            evidence=evidence,
            context_evidence=context_evidence,
            admission=admission_receipt,
            current=current_receipt,
            plus=altered,
            direct=direct_receipt,
            artifact_digests=artifact_digests,
            operation_ids=operation_ids,
            errors=errors,
        )
        self.assertTrue(errors)

    def test_12_gate_sources_and_architecture_boundaries_remain_closed(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        source_names = tuple(name for name, _path in runner._source_paths(WORKSPACE_ROOT))
        self.assertIn("_s2jh_private_controlled_context_admission", source_names)
        self.assertIn("_s2jk_private_end_to_end_context_use", source_names)
        self.assertIn("_s2jk_private_direct_end_to_end_baseline", source_names)
        self.assertEqual(len(source_names), len(set(source_names)))
        runner_source = Path(runner.__file__).read_text(encoding="utf-8")
        tree = ast.parse(runner_source)
        created_modules = tuple(
            path.name
            for path in (WORKSPACE_ROOT / "tools").glob("_s2jl*")
        )
        self.assertEqual(created_modules, ())
        self.assertFalse(
            any(
                isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "MAIN_EXECUTION_ENABLED" for target in node.targets)
                and isinstance(node.value, ast.Constant)
                and node.value.value is True
                for node in ast.walk(tree)
            )
        )


if __name__ == "__main__":
    unittest.main()
