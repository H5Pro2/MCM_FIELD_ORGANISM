from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2jh_private_controlled_context_admission as admission_contract
from tools import _s2jk_private_direct_end_to_end_baseline as direct_baseline
from tools import _s2jk_private_end_to_end_context_use as context_use
from tests.test_s2hr_role_addressed_consumer_qualification import _bundle


QUALIFICATION_ID = "s2jk-end-to-end-context-use-qualification-20260901-01"
VISIBLE = tuple(0.4 for _ in probe_contract.VISIBLE_POSITIONS)
MASKED_A = tuple(0.25 for _ in probe_contract.MASKED_POSITIONS)
MASKED_B = tuple(0.75 for _ in probe_contract.MASKED_POSITIONS)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _visual(masked_values: tuple[float, ...]) -> tuple[float, ...]:
    values: list[float] = []
    visible_index = 0
    masked_index = 0
    for position in range(18):
        if position in probe_contract.VISIBLE_POSITIONS:
            values.append(VISIBLE[visible_index])
            visible_index += 1
        else:
            values.append(masked_values[masked_index])
            masked_index += 1
    return tuple(values)


VISUAL_A = _visual(MASKED_A)
VISUAL_B = _visual(MASKED_B)


def _probe(tag: str) -> probe_contract.MaskedVisualProbe:
    values: list[float | None] = []
    visible_index = 0
    for position in range(18):
        if position in probe_contract.VISIBLE_POSITIONS:
            values.append(VISIBLE[visible_index])
            visible_index += 1
        else:
            values.append(None)
    return probe_contract.MaskedVisualProbe.build(tuple(values), _digest({"probe-source": tag}))


def _role_source(bundle, area: str):
    if area == "A_RECENT":
        area_finding = bundle.area_findings[0]
        role_finding = area_finding.recent_content
    else:
        area_finding = bundle.area_findings[1]
        role_finding = area_finding.stable_content
    candidate = role_finding.candidate
    if candidate is None:
        return area_finding, role_finding, None
    if area == "A_RECENT":
        component = candidate.components[0]
    else:
        component = next(item for item in candidate.components if item.component_role == "VISUAL")
    return area_finding, role_finding, component


def _finding(
    signal_input: signal_contract.TwoAreaConflictSignalInput,
    bundle,
    area: str,
    status: str,
) -> signal_contract.AreaApplicabilityFinding:
    area_finding, role_finding, component = _role_source(bundle, area)
    if status == "ABSENT_VALID":
        candidate_digest = None
        component_digest = None
        component_source_digest = None
        visible_mismatches = ()
        masked_values = ()
    else:
        assert role_finding.candidate is not None and component is not None
        candidate_digest = role_finding.candidate.candidate_digest
        component_digest = component.component_digest
        component_source_digest = component.source_digest
        visible_mismatches = (0,) if status == "VISIBLE_CONFLICT" else ()
        visual_values = component.values[8:] if component.component_role == "AV_JOINT" else component.values
        masked_values = (
            tuple(visual_values[position] for position in probe_contract.MASKED_POSITIONS)
            if status == "APPLICABLE"
            else ()
        )
    return signal_contract.AreaApplicabilityFinding.build(
        area=area,
        status=status,
        signal_input=signal_input,
        area_finding_digest=area_finding.finding_digest,
        role_finding_digest=role_finding.finding_digest,
        candidate_digest=candidate_digest,
        component_digest=component_digest,
        component_source_digest=component_source_digest,
        visible_mismatch_positions=visible_mismatches,
        masked_values=masked_values,
    )


def _fixture(status: str, tag: str):
    if status == "CONSISTENT":
        a_visual, b_visual = VISUAL_A, VISUAL_A
        a_status, b_status = "APPLICABLE", "APPLICABLE"
    elif status == "CONFLICT":
        a_visual, b_visual = VISUAL_A, VISUAL_B
        a_status, b_status = "APPLICABLE", "APPLICABLE"
    elif status == "SINGLE_SOURCE_A":
        a_visual, b_visual = VISUAL_A, None
        a_status, b_status = "APPLICABLE", "ABSENT_VALID"
    elif status == "SINGLE_SOURCE_B":
        a_visual, b_visual = None, VISUAL_B
        a_status, b_status = "ABSENT_VALID", "APPLICABLE"
    elif status == "NO_CONTEXT":
        a_visual, b_visual = None, None
        a_status, b_status = "ABSENT_VALID", "ABSENT_VALID"
    elif status == "NO_APPLICABLE_CONTEXT":
        a_visual, b_visual = VISUAL_A, VISUAL_B
        a_status, b_status = "VISIBLE_CONFLICT", "VISIBLE_CONFLICT"
    else:
        raise AssertionError("unknown neutral status fixture")

    probe = _probe(tag)
    bundle = _bundle(a_visual, b_visual, source_tag=tag)
    signal_input = signal_contract.TwoAreaConflictSignalInput.build(
        f"neutral-signal-{tag}",
        "SIGNAL",
        probe,
        bundle,
    )
    a_finding = _finding(signal_input, bundle, "A_RECENT", a_status)
    b_finding = _finding(signal_input, bundle, "B_STABLE", b_status)
    applicable = tuple(item for item in (a_finding, b_finding) if item.status == "APPLICABLE")
    present_count = sum(item.status != "ABSENT_VALID" for item in (a_finding, b_finding))
    if len(applicable) == 2:
        differing = tuple(
            position
            for position, left, right in zip(
                probe_contract.MASKED_POSITIONS,
                a_finding.masked_values,
                b_finding.masked_values,
                strict=True,
            )
            if left != right
        )
        comparison_status = "DIFFERENT" if differing else "EQUAL"
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
    if status.startswith("SINGLE_SOURCE"):
        signal_status = "SINGLE_SOURCE"
    else:
        signal_status = status
    ledger = signal_contract.TwoAreaConflictSignalLedger.build(present_count, len(applicable))
    signal_result = signal_contract.build_result(
        signal_input,
        a_finding,
        b_finding,
        comparison,
        ledger,
        signal_status,
    )
    signal_owner = signal_contract.TwoAreaConflictSignalOwner(
        signal_contract.TwoAreaConflictOwnerPrestate.build(f"neutral-signal-owner-{tag}", signal_input)
    )
    signal_commit = signal_contract.publish_success(
        signal_owner,
        signal_input,
        a_finding,
        b_finding,
        comparison,
        ledger,
        signal_result,
    )
    admission_input = admission_contract.ControlledContextAdmissionInput.build(
        f"neutral-admission-{tag}",
        "ADMISSION",
        signal_input,
        signal_commit,
    )
    admission_owner = admission_contract.ContextAdmissionOwner(
        admission_contract.ContextAdmissionOwnerState.ready(f"neutral-admission-owner-{tag}", admission_input)
    )
    admission_commit = admission_contract.form_controlled_context_admission(
        admission_input,
        signal_input,
        signal_commit,
        a_finding,
        b_finding,
        comparison,
        admission_owner,
    )
    return probe, bundle, signal_commit, admission_commit, a_finding, b_finding


def _run(fixture):
    main = context_use.use_admitted_context(*fixture)
    direct = direct_baseline.compose_direct_admission_and_fill(*fixture)
    return main, direct


class TestS2JKPrivateEndToEndContextUse(unittest.TestCase):
    def test_01_all_five_statuses_match_independent_baseline(self) -> None:
        cases = (
            "CONSISTENT",
            "CONFLICT",
            "SINGLE_SOURCE_A",
            "NO_CONTEXT",
            "NO_APPLICABLE_CONTEXT",
        )
        for ordinal, status in enumerate(cases, start=1):
            with self.subTest(status=status):
                main, direct = _run(_fixture(status, f"status-{ordinal}"))
                self.assertEqual(main.source_signal_status, direct.source_signal_status)
                self.assertEqual(main.completion_status, direct.completion_status)
                self.assertEqual(main.output_values, direct.output_values)
                self.assertEqual(main.completed_positions, direct.completed_positions)

    def test_02_single_source_a_b_mirror(self) -> None:
        a_main, a_direct = _run(_fixture("SINGLE_SOURCE_A", "single-a"))
        b_main, b_direct = _run(_fixture("SINGLE_SOURCE_B", "single-b"))
        self.assertEqual(a_main.admitted_role, "A_RECENT")
        self.assertEqual(b_main.admitted_role, "B_STABLE")
        self.assertEqual(a_main.output_values, a_direct.output_values)
        self.assertEqual(b_main.output_values, b_direct.output_values)
        self.assertEqual(tuple(a_main.output_values[pos] for pos in probe_contract.MASKED_POSITIONS), MASKED_A)
        self.assertEqual(tuple(b_main.output_values[pos] for pos in probe_contract.MASKED_POSITIONS), MASKED_B)

    def test_03_consistent_has_no_order_preference(self) -> None:
        main, direct = _run(_fixture("CONSISTENT", "consistent"))
        self.assertIsNone(main.admitted_role)
        self.assertIsNotNone(main.equivalent_role_set_digest)
        self.assertEqual(main.output_values, direct.output_values)
        self.assertEqual(tuple(main.output_values[pos] for pos in probe_contract.MASKED_POSITIONS), MASKED_A)
        self.assertNotIn("selected", main.payload_without_digest())
        self.assertIsNone(main.selected_area)

    def test_04_withheld_statuses_never_call_fill_helper(self) -> None:
        for ordinal, status in enumerate(("CONFLICT", "NO_CONTEXT", "NO_APPLICABLE_CONTEXT"), start=1):
            with self.subTest(status=status):
                fixture = _fixture(status, f"withheld-{ordinal}")
                with patch.object(context_use, "_apply_admitted_supplement", side_effect=AssertionError("must not run")) as helper:
                    result = context_use.use_admitted_context(*fixture)
                helper.assert_not_called()
                self.assertEqual(result.output_values, fixture[0].values)
                self.assertEqual(result.resource_ledger.context_apply_count, 0)

    def test_05_visible_values_are_preserved_and_only_masks_are_filled(self) -> None:
        probe, *rest = _fixture("SINGLE_SOURCE_A", "positions")
        result = context_use.use_admitted_context(probe, *rest)
        self.assertEqual(result.completed_positions, probe_contract.MASKED_POSITIONS)
        for position in probe_contract.VISIBLE_POSITIONS:
            self.assertEqual(result.output_values[position], probe.values[position])
        for position in probe_contract.MASKED_POSITIONS:
            self.assertIsNone(probe.values[position])
            self.assertIsInstance(result.output_values[position], float)

    def test_06_current_only_projection_is_always_the_unchanged_probe(self) -> None:
        for ordinal, status in enumerate(("CONSISTENT", "CONFLICT", "SINGLE_SOURCE_B", "NO_CONTEXT", "NO_APPLICABLE_CONTEXT"), start=1):
            with self.subTest(status=status):
                fixture = _fixture(status, f"current-{ordinal}")
                result = context_use.use_admitted_context(*fixture)
                self.assertEqual(result.current_only_values, fixture[0].values)

    def test_07_manipulated_admission_evidence_fails_closed(self) -> None:
        fixture = _fixture("SINGLE_SOURCE_A", "mutated-admission")
        admission_result = fixture[3].result
        object.__setattr__(admission_result, "result_digest", "0" * 64)
        with self.assertRaises(context_use.S2JKContextUseError) as caught:
            context_use.use_admitted_context(*fixture)
        self.assertEqual(caught.exception.code, "S2JK-E002")

    def test_08_swapped_or_foreign_findings_fail_closed(self) -> None:
        fixture = _fixture("CONFLICT", "swap")
        probe, bundle, signal_commit, admission_commit, a_finding, b_finding = fixture
        with self.assertRaises(context_use.S2JKContextUseError):
            context_use.use_admitted_context(probe, bundle, signal_commit, admission_commit, b_finding, a_finding)

        foreign = _fixture("CONFLICT", "foreign")
        with self.assertRaises(context_use.S2JKContextUseError):
            context_use.use_admitted_context(probe, foreign[1], signal_commit, admission_commit, a_finding, b_finding)

    def test_09_signal_admission_and_state_relations_are_mandatory(self) -> None:
        fixture = _fixture("CONSISTENT", "state-binding")
        signal_result = fixture[2].result
        object.__setattr__(signal_result, "poststate_digest", _digest({"foreign": "state"}))
        with self.assertRaises(context_use.S2JKContextUseError) as caught:
            context_use.use_admitted_context(*fixture)
        self.assertEqual(caught.exception.code, "S2JK-E002")

    def test_10_baseline_does_not_invoke_end_to_end_adapter(self) -> None:
        fixture = _fixture("SINGLE_SOURCE_B", "baseline-independent")
        with patch.object(context_use, "use_admitted_context", side_effect=AssertionError("adapter must not run")) as adapter:
            result = direct_baseline.compose_direct_admission_and_fill(*fixture)
        adapter.assert_not_called()
        self.assertEqual(result.function_role, "DIRECT_COMPOSITION_BASELINE")
        source = Path(direct_baseline.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        calls = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        self.assertNotIn("use_admitted_context", calls)
        self.assertNotIn("_single_source_values", calls)
        self.assertNotIn("_consistent_values", calls)
        self.assertNotIn("_build_result", calls)

    def test_11_inputs_and_state_are_fully_immutable(self) -> None:
        fixture = _fixture("CONSISTENT", "immutable")
        before = tuple(
            item
            for item in (
                fixture[0].probe_digest,
                fixture[1].bundle_digest,
                fixture[1].prestate_digest,
                fixture[1].poststate_digest,
                fixture[2].result.result_digest,
                fixture[3].result.result_digest,
                fixture[4].finding_digest,
                fixture[5].finding_digest,
            )
        )
        result = context_use.use_admitted_context(*fixture)
        after = (
            fixture[0].probe_digest,
            fixture[1].bundle_digest,
            fixture[1].prestate_digest,
            fixture[1].poststate_digest,
            fixture[2].result.result_digest,
            fixture[3].result.result_digest,
            fixture[4].finding_digest,
            fixture[5].finding_digest,
        )
        self.assertEqual(before, after)
        self.assertEqual(result.prestate_digest, result.poststate_digest)
        with self.assertRaises(FrozenInstanceError):
            result.completion_status = "CONTEXT_WITHHELD"  # type: ignore[misc]

    def test_12_bounds_and_forbidden_dependencies(self) -> None:
        result, direct = _run(_fixture("CONSISTENT", "bounds"))
        for item in (result, direct):
            self.assertLessEqual(len(context_use._canonical_bytes(item.payload())), context_use.MAX_ARTIFACT_BYTES)
            self.assertEqual(item.resource_ledger.status_recomputation_count, 0)
            self.assertEqual(item.resource_ledger.applicability_recomputation_count, 0)
            self.assertEqual(item.resource_ledger.memory_receptor_or_field_call_count, 0)
        forbidden = ("runner", "recorder", "registry", "receptor", "tspm", "ppb", "field")
        for module in (context_use, direct_baseline):
            source = Path(module.__file__).read_text(encoding="utf-8").lower()
            imports = (
                node
                for node in ast.walk(ast.parse(source))
                if isinstance(node, (ast.Import, ast.ImportFrom))
            )
            imported = " ".join(ast.unparse(node).lower() for node in imports)
            self.assertFalse(any(token in imported for token in forbidden))


if __name__ == "__main__":
    unittest.main()
