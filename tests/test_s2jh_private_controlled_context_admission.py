from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path
import unittest

from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2jh_private_controlled_context_admission as admission
from tools import _s2jh_private_direct_admission_baseline as baseline


MASKED_X = (0.25,) * 9
MASKED_Y = (0.75,) * 9


def _digest(label: str) -> str:
    return signal_contract.digest({"neutral": label})


def _signal_input(suffix: str) -> signal_contract.TwoAreaConflictSignalInput:
    state = _digest(f"state-{suffix}")
    payload = {
        "schema": signal_contract.S2IC_SCHEMA,
        "invocation_id": f"neutral-signal-{suffix}",
        "function_role": "SIGNAL",
        "probe_digest": _digest(f"probe-{suffix}"),
        "probe_source_digest": _digest(f"probe-source-{suffix}"),
        "mask_digest": _digest(f"mask-{suffix}"),
        "bundle_digest": _digest(f"bundle-{suffix}"),
        "bundle_source_digest": _digest(f"bundle-source-{suffix}"),
        "config_digest": _digest(f"config-{suffix}"),
        "composite_state_digest": state,
        "bundle_prestate_digest": state,
        "bundle_poststate_digest": state,
        "a_area_finding_digest": _digest(f"area-a-{suffix}"),
        "b_area_finding_digest": _digest(f"area-b-{suffix}"),
    }
    return signal_contract.TwoAreaConflictSignalInput(
        payload["invocation_id"],
        "SIGNAL",
        payload["probe_digest"],
        payload["probe_source_digest"],
        payload["mask_digest"],
        payload["bundle_digest"],
        payload["bundle_source_digest"],
        payload["config_digest"],
        state,
        state,
        state,
        payload["a_area_finding_digest"],
        payload["b_area_finding_digest"],
        signal_contract.digest(payload),
    )


def _finding(
    signal_input: signal_contract.TwoAreaConflictSignalInput,
    area: str,
    kind: str,
    suffix: str,
) -> signal_contract.AreaApplicabilityFinding:
    area_digest = (
        signal_input.a_area_finding_digest
        if area == "A_RECENT"
        else signal_input.b_area_finding_digest
    )
    if kind == "absent":
        return signal_contract.AreaApplicabilityFinding.build(
            area=area,
            status="ABSENT_VALID",
            signal_input=signal_input,
            area_finding_digest=area_digest,
            role_finding_digest=_digest(f"role-{area}-{suffix}"),
            candidate_digest=None,
            component_digest=None,
            component_source_digest=None,
            visible_mismatch_positions=(),
            masked_values=(),
        )

    status = "VISIBLE_CONFLICT" if kind == "visible-conflict" else "APPLICABLE"
    masked_values = MASKED_Y if kind == "y" else MASKED_X
    return signal_contract.AreaApplicabilityFinding.build(
        area=area,
        status=status,
        signal_input=signal_input,
        area_finding_digest=area_digest,
        role_finding_digest=_digest(f"role-{area}-{kind}-{suffix}"),
        candidate_digest=_digest(f"candidate-{area}-{kind}-{suffix}"),
        component_digest=_digest(f"component-{area}-{kind}-{suffix}"),
        component_source_digest=_digest(f"component-source-{area}-{kind}-{suffix}"),
        visible_mismatch_positions=(0,) if status == "VISIBLE_CONFLICT" else (),
        masked_values=masked_values if status == "APPLICABLE" else (),
    )


def _signal_evidence(
    a_kind: str,
    b_kind: str,
    suffix: str,
) -> tuple[
    signal_contract.TwoAreaConflictSignalInput,
    signal_contract.TwoAreaConflictSignalCommit,
    signal_contract.AreaApplicabilityFinding,
    signal_contract.AreaApplicabilityFinding,
    signal_contract.MaskedSupplementComparison,
]:
    signal_input = _signal_input(suffix)
    a_finding = _finding(signal_input, "A_RECENT", a_kind, suffix)
    b_finding = _finding(signal_input, "B_STABLE", b_kind, suffix)
    applicable = tuple(
        finding for finding in (a_finding, b_finding) if finding.status == "APPLICABLE"
    )
    present_count = sum(
        finding.status != "ABSENT_VALID" for finding in (a_finding, b_finding)
    )
    if len(applicable) == 2:
        differing = (
            ()
            if a_finding.masked_values_digest == b_finding.masked_values_digest
            else signal_contract.probe_contract.MASKED_POSITIONS
        )
        comparison_status = "EQUAL" if not differing else "DIFFERENT"
    else:
        differing = ()
        comparison_status = "NOT_PERFORMED"
    comparison = signal_contract.MaskedSupplementComparison.build(
        signal_input,
        a_finding,
        b_finding,
        comparison_status,
        differing,
    )
    if present_count == 0:
        status = "NO_CONTEXT"
    elif len(applicable) == 0:
        status = "NO_APPLICABLE_CONTEXT"
    elif len(applicable) == 1:
        status = "SINGLE_SOURCE"
    else:
        status = "CONSISTENT" if comparison_status == "EQUAL" else "CONFLICT"
    ledger = signal_contract.TwoAreaConflictSignalLedger.build(
        present_count,
        len(applicable),
    )
    result = signal_contract.build_result(
        signal_input,
        a_finding,
        b_finding,
        comparison,
        ledger,
        status,
    )
    signal_owner = signal_contract.TwoAreaConflictSignalOwner(
        signal_contract.TwoAreaConflictOwnerPrestate.build(
            f"neutral-signal-owner-{suffix}",
            signal_input,
        )
    )
    commit = signal_contract.publish_success(
        signal_owner,
        signal_input,
        a_finding,
        b_finding,
        comparison,
        ledger,
        result,
    )
    return signal_input, commit, a_finding, b_finding, comparison


def _call(
    a_kind: str,
    b_kind: str,
    suffix: str,
    function_role: str,
) -> tuple[
    admission.ControlledContextAdmissionCommit,
    admission.ContextAdmissionOwner,
    tuple[object, ...],
]:
    evidence = _signal_evidence(a_kind, b_kind, suffix)
    return _call_with_evidence(evidence, suffix, function_role)


def _call_with_evidence(
    evidence: tuple[
        signal_contract.TwoAreaConflictSignalInput,
        signal_contract.TwoAreaConflictSignalCommit,
        signal_contract.AreaApplicabilityFinding,
        signal_contract.AreaApplicabilityFinding,
        signal_contract.MaskedSupplementComparison,
    ],
    suffix: str,
    function_role: str,
) -> tuple[
    admission.ControlledContextAdmissionCommit,
    admission.ContextAdmissionOwner,
    tuple[object, ...],
]:
    signal_input, signal_commit, a_finding, b_finding, comparison = evidence
    admission_input = admission.ControlledContextAdmissionInput.build(
        f"neutral-{function_role.lower().replace('_', '-')}-{suffix}",
        function_role,
        signal_input,
        signal_commit,
    )
    owner = admission.ContextAdmissionOwner(
        admission.ContextAdmissionOwnerState.ready(
            f"neutral-owner-{function_role.lower().replace('_', '-')}-{suffix}",
            admission_input,
        )
    )
    function = (
        admission.form_controlled_context_admission
        if function_role == "ADMISSION"
        else baseline.form_direct_context_admission_baseline
    )
    commit = function(
        admission_input,
        signal_input,
        signal_commit,
        a_finding,
        b_finding,
        comparison,
        owner,
    )
    return commit, owner, (admission_input, *evidence)


def _failure_fixture(suffix: str = "failure") -> tuple[object, ...]:
    evidence = _signal_evidence("x", "x", suffix)
    signal_input, signal_commit, a_finding, b_finding, comparison = evidence
    admission_input = admission.ControlledContextAdmissionInput.build(
        f"neutral-admission-{suffix}",
        "ADMISSION",
        signal_input,
        signal_commit,
    )
    owner = admission.ContextAdmissionOwner(
        admission.ContextAdmissionOwnerState.ready(
            f"neutral-owner-admission-{suffix}",
            admission_input,
        )
    )
    return admission_input, signal_input, signal_commit, a_finding, b_finding, comparison, owner


def _invoke_fixture(fixture: tuple[object, ...]) -> admission.ControlledContextAdmissionCommit:
    return admission.form_controlled_context_admission(*fixture)


class S2JHPrivateControlledContextAdmissionTests(unittest.TestCase):
    def test_01_all_five_statuses_match_independent_table_baseline(self) -> None:
        cases = (
            ("x", "x", "CONSISTENT", "ALLOW_CONTEXT"),
            ("x", "y", "CONFLICT", "PROCEED_WITHOUT_CONTEXT"),
            ("x", "absent", "SINGLE_SOURCE", "ALLOW_CONTEXT"),
            ("absent", "absent", "NO_CONTEXT", "PROCEED_WITHOUT_CONTEXT"),
            ("visible-conflict", "absent", "NO_APPLICABLE_CONTEXT", "PROCEED_WITHOUT_CONTEXT"),
        )
        seen = set()
        for ordinal, (a_kind, b_kind, status, decision) in enumerate(cases, start=1):
            evidence = _signal_evidence(a_kind, b_kind, f"shared-{ordinal:02d}")
            primary, _, _ = _call_with_evidence(
                evidence,
                f"case-{ordinal:02d}",
                "ADMISSION",
            )
            direct, _, _ = _call_with_evidence(
                evidence,
                f"base-{ordinal:02d}",
                "DIRECT_TABLE_BASELINE",
            )
            self.assertEqual(status, primary.result.source_signal_status)
            self.assertEqual(decision, primary.result.decision)
            self.assertEqual(primary.result.decision, direct.result.decision)
            self.assertEqual(primary.result.reason, direct.result.reason)
            self.assertEqual(primary.result.admitted_role, direct.result.admitted_role)
            self.assertEqual(
                primary.result.equivalent_role_set_digest,
                direct.result.equivalent_role_set_digest,
            )
            self.assertEqual(
                primary.result.common_supplement_digest,
                direct.result.common_supplement_digest,
            )
            self.assertEqual(
                primary.result.admitted_context_binding_digest,
                direct.result.admitted_context_binding_digest,
            )
            seen.add(status)
        self.assertEqual(set(signal_contract.RESULT_STATUSES), seen)

    def test_02_single_source_mirrors_without_preference(self) -> None:
        a_only, _, _ = _call("x", "absent", "single-a", "ADMISSION")
        b_only, _, _ = _call("absent", "x", "single-b", "ADMISSION")
        self.assertEqual("A_RECENT", a_only.result.admitted_role)
        self.assertEqual("B_STABLE", b_only.result.admitted_role)
        self.assertEqual(a_only.result.decision, b_only.result.decision)
        self.assertEqual(a_only.result.reason, b_only.result.reason)
        self.assertIsNone(a_only.result.equivalent_role_set_digest)
        self.assertIsNone(b_only.result.equivalent_role_set_digest)

    def test_03_consistent_exposes_only_unordered_equivalence_and_common_binding(self) -> None:
        commit, _, _ = _call("x", "x", "consistent", "ADMISSION")
        result = commit.result
        self.assertEqual("ALLOW_CONTEXT", result.decision)
        self.assertEqual("EQUIVALENT_CONTEXTS", result.reason)
        self.assertIsNone(result.admitted_role)
        self.assertTrue(admission.valid_digest(result.equivalent_role_set_digest))
        self.assertTrue(admission.valid_digest(result.common_supplement_digest))
        self.assertTrue(admission.valid_digest(result.admitted_context_binding_digest))
        self.assertIsNone(result.selected_area)
        self.assertIsNone(result.ranking)
        self.assertIsNone(result.merged_context_digest)
        self.assertNotIn("equivalent_roles", result.payload_without_digest())

    def test_04_all_withheld_statuses_publish_no_context_reference(self) -> None:
        cases = (
            ("x", "y", "CONFLICT_WITHHELD"),
            ("absent", "absent", "CONTEXT_ABSENT"),
            ("visible-conflict", "absent", "CONTEXT_INAPPLICABLE"),
        )
        for ordinal, (a_kind, b_kind, reason) in enumerate(cases, start=1):
            commit, _, _ = _call(a_kind, b_kind, f"withheld-{ordinal}", "ADMISSION")
            result = commit.result
            self.assertEqual("PROCEED_WITHOUT_CONTEXT", result.decision)
            self.assertEqual(reason, result.reason)
            self.assertIsNone(result.admitted_role)
            self.assertIsNone(result.equivalent_role_set_digest)
            self.assertIsNone(result.common_supplement_digest)
            self.assertIsNone(result.admitted_context_binding_digest)

    def test_05_success_is_frozen_read_only_and_consumes_owner_once(self) -> None:
        commit, owner, artifacts = _call("x", "x", "immutable", "ADMISSION")
        before = tuple(
            getattr(item, name)
            for item, name in (
                (artifacts[0], "input_digest"),
                (artifacts[1], "input_digest"),
                (artifacts[2].result, "result_digest"),
                (artifacts[3], "finding_digest"),
                (artifacts[4], "finding_digest"),
                (artifacts[5], "comparison_digest"),
            )
        )
        self.assertEqual("CONSUMED", owner.state)
        self.assertIs(owner.poststate, commit.owner_poststate)
        self.assertEqual(commit.result.prestate_digest, commit.result.poststate_digest)
        after = tuple(
            getattr(item, name)
            for item, name in (
                (artifacts[0], "input_digest"),
                (artifacts[1], "input_digest"),
                (artifacts[2].result, "result_digest"),
                (artifacts[3], "finding_digest"),
                (artifacts[4], "finding_digest"),
                (artifacts[5], "comparison_digest"),
            )
        )
        self.assertEqual(before, after)
        with self.assertRaises(FrozenInstanceError):
            commit.result.decision = "PROCEED_WITHOUT_CONTEXT"

    def test_06_owner_reuse_is_rejected_without_second_output(self) -> None:
        fixture = _failure_fixture("owner-reuse")
        first = _invoke_fixture(fixture)
        owner = fixture[-1]
        self.assertEqual("CONSUMED", owner.state)
        with self.assertRaises(admission.S2JHAdmissionError) as caught:
            _invoke_fixture(fixture)
        self.assertEqual("S2JH-E006", caught.exception.code)
        self.assertIs(owner.poststate, first.owner_poststate)

    def test_07_mutated_input_or_signal_digest_fails_closed(self) -> None:
        fixture = _failure_fixture("digest-mutation")
        object.__setattr__(fixture[0], "signal_result_digest", _digest("foreign-result"))
        with self.assertRaises(admission.S2JHAdmissionFailure) as caught:
            _invoke_fixture(fixture)
        self.assertIn(caught.exception.code, ("S2JH-E002", "S2JH-E004"))
        self.assertEqual("FAILED", fixture[-1].state)

    def test_08_swapped_area_evidence_fails_closed(self) -> None:
        fixture = list(_failure_fixture("swapped-areas"))
        fixture[3], fixture[4] = fixture[4], fixture[3]
        with self.assertRaises(admission.S2JHAdmissionFailure) as caught:
            _invoke_fixture(tuple(fixture))
        self.assertEqual("S2JH-E004", caught.exception.code)
        self.assertEqual("FAILED", fixture[-1].state)

    def test_09_manipulated_comparison_or_receipt_fails_closed(self) -> None:
        for suffix, target_index, field in (
            ("comparison", 5, "comparison_digest"),
            ("receipt", 2, "receipt"),
        ):
            fixture = list(_failure_fixture(f"mutated-{suffix}"))
            if target_index == 5:
                object.__setattr__(fixture[target_index], field, _digest(f"foreign-{suffix}"))
            else:
                object.__setattr__(
                    fixture[target_index].receipt,
                    "result_digest",
                    _digest("foreign-receipt-result"),
                )
            with self.subTest(suffix=suffix):
                with self.assertRaises(admission.S2JHAdmissionFailure):
                    _invoke_fixture(tuple(fixture))
                self.assertEqual("FAILED", fixture[-1].state)

    def test_10_state_digest_break_fails_closed(self) -> None:
        fixture = list(_failure_fixture("state-break"))
        object.__setattr__(fixture[2].result, "poststate_digest", _digest("changed-state"))
        with self.assertRaises(admission.S2JHAdmissionFailure) as caught:
            _invoke_fixture(tuple(fixture))
        self.assertIn(caught.exception.code, ("S2JH-E004", "S2JH-E005"))
        self.assertEqual("FAILED", fixture[-1].state)

    def test_11_byte_and_operation_limits_are_materialized(self) -> None:
        signal_input, signal_commit, a_finding, b_finding, comparison = _signal_evidence(
            "x", "x", "worst-case"
        )
        admission_input = admission.ControlledContextAdmissionInput.build(
            "a" + "b" * 95,
            "ADMISSION",
            signal_input,
            signal_commit,
        )
        owner = admission.ContextAdmissionOwner(
            admission.ContextAdmissionOwnerState.ready("a" + "c" * 95, admission_input)
        )
        commit = admission.form_controlled_context_admission(
            admission_input,
            signal_input,
            signal_commit,
            a_finding,
            b_finding,
            comparison,
            owner,
        )
        ledger = admission.ContextAdmissionLedger.build(2)
        artifacts = (
            ("input", {**admission_input.payload_without_digest(), "input_digest": admission_input.input_digest}),
            ("owner", {**owner.prestate.payload_without_digest(), "owner_state_digest": owner.prestate.owner_state_digest}),
            ("ledger", {**ledger.payload_without_digest(), "ledger_digest": ledger.ledger_digest}),
            ("result", {**commit.result.payload_without_digest(), "result_digest": commit.result.result_digest}),
            ("owner", {**commit.owner_poststate.payload_without_digest(), "owner_state_digest": commit.owner_poststate.owner_state_digest}),
            ("receipt", {**commit.receipt.payload_without_digest(), "receipt_digest": commit.receipt.receipt_digest}),
        )
        actual_total = 0
        for role, payload in artifacts:
            size = admission.artifact_size(payload)
            actual_total += size
            self.assertLessEqual(size, admission.ARTIFACT_LIMITS[role])
        self.assertLessEqual(actual_total, admission.MAX_SUCCESS_ARTIFACT_BYTES)
        self.assertEqual(admission.MAX_LOGICAL_OPERATIONS, ledger.logical_operation_count)
        self.assertEqual(0, ledger.memory_receptor_or_field_call_count)

    def test_12_private_import_boundary_and_baseline_independence(self) -> None:
        root = Path(__file__).resolve().parents[1]
        primary_path = root / "tools" / "_s2jh_private_controlled_context_admission.py"
        baseline_path = root / "tools" / "_s2jh_private_direct_admission_baseline.py"
        forbidden = ("mcm_field_organism", "receptor", "runner", "snapshot", "field")
        for path in (primary_path, baseline_path):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            modules = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    modules.append(node.module)
                elif isinstance(node, ast.Import):
                    modules.extend(alias.name for alias in node.names)
            self.assertFalse(
                any(token in module for token in forbidden for module in modules),
                modules,
            )
        baseline_source = baseline_path.read_text(encoding="utf-8")
        self.assertNotIn("form_controlled_context_admission(", baseline_source)
        self.assertEqual((), admission.__all__)
        self.assertEqual((), baseline.__all__)


if __name__ == "__main__":
    unittest.main()
