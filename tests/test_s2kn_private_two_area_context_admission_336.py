from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path
import unittest

from tools import _s2kj_two_area_perceptual_context_336 as context_contract
from tools import _s2kj_validated_perceptual_finding_336 as finding_contract
from tools import _s2kn_private_direct_two_area_admission_baseline as baseline
from tools import _s2kn_private_two_area_context_admission_336 as admission


def _digest(label: str) -> str:
    return finding_contract._digest({"neutral": label})


def _visual(kind: str) -> tuple[float, ...]:
    if kind == "x":
        return (0.0,) * 32 + (0.25,) * 256
    if kind == "y":
        return (0.0,) * 32 + (0.75,) * 256
    if kind == "conflict":
        return (1.0,) * 32 + (0.5,) * 256
    raise AssertionError(kind)


def _candidate(
    role: str,
    kind: str,
    suffix: str,
    state_digest: str,
    probe_digest: str,
    source_digest: str,
) -> finding_contract.Candidate336:
    visual = _visual(kind)
    slot_digest = _digest(f"slot-{role}-{suffix}")
    if role in ("B4_RECENT", "TSPM_FAST"):
        auditory = (0.125,) * 48
        payload = {
            "role": role,
            "slot_id": f"neutral-{role.lower().replace('_', '-')}-{suffix}",
            "slot_digest": slot_digest,
            "auditory_values": list(auditory),
            "visual_values": list(visual),
            "auditory_values_digest": finding_contract._digest(list(auditory)),
            "visual_values_digest": finding_contract._digest(list(visual)),
            "av_values_digest": finding_contract._digest(list(auditory + visual)),
            "formation_index": 1 if role == "B4_RECENT" else None,
            "support": 1 if role == "TSPM_FAST" else None,
            "last_selected_step": 1 if role == "TSPM_FAST" else None,
            "auditory_distance": 0.0,
            "visual_distance": 0.0,
            "mechanical_match": True,
            "observed_state_digest": state_digest,
            "probe_digest": probe_digest,
            "source_digest": source_digest,
        }
        return finding_contract.AVContextCandidate336V1(
            role,
            payload["slot_id"],
            slot_digest,
            auditory,
            visual,
            payload["auditory_values_digest"],
            payload["visual_values_digest"],
            payload["av_values_digest"],
            payload["formation_index"],
            payload["support"],
            payload["last_selected_step"],
            0.0,
            0.0,
            True,
            state_digest,
            probe_digest,
            source_digest,
            finding_contract._digest(payload),
        )
    payload = {
        "role": role,
        "modality": "VISUAL",
        "dimension": 288,
        "slot_id": f"neutral-b-stable-visual-{suffix}",
        "slot_digest": slot_digest,
        "values": list(visual),
        "values_digest": finding_contract._digest(list(visual)),
        "support": 3,
        "stable": True,
        "native_distance": 0.0,
        "mechanical_match": True,
        "observed_state_digest": state_digest,
        "probe_digest": probe_digest,
        "source_digest": source_digest,
    }
    return finding_contract.StableModalityCandidate336V1(
        role,
        "VISUAL",
        288,
        payload["slot_id"],
        slot_digest,
        visual,
        payload["values_digest"],
        3,
        True,
        0.0,
        True,
        state_digest,
        probe_digest,
        source_digest,
        finding_contract._digest(payload),
    )


def _role_finding(
    role: str,
    kind: str,
    suffix: str,
    state_digest: str,
    probe_digest: str,
    source_digest: str,
    source_finding_digest: str,
) -> finding_contract.RoleFinding336V1:
    candidate = (
        None
        if kind == "absent"
        else _candidate(role, kind, suffix, state_digest, probe_digest, source_digest)
    )
    payload = {
        "role": role,
        "status": "ABSENT_VALID" if candidate is None else "AVAILABLE",
        "absence_reason": "NO_FUNCTIONAL_MATCH" if candidate is None else None,
        "candidate_digest": candidate.candidate_digest if candidate else None,
        "observed_state_digest": state_digest,
        "probe_digest": probe_digest,
        "source_finding_digest": source_finding_digest,
    }
    return finding_contract.RoleFinding336V1(
        role,
        payload["status"],
        payload["absence_reason"],
        candidate,
        state_digest,
        probe_digest,
        source_finding_digest,
        finding_contract._digest(payload),
    )


def _context(
    b4_kind: str,
    fast_kind: str,
    b_kind: str,
    suffix: str,
) -> context_contract.TwoAreaPerceptualContext336:
    config_digest = _digest("config")
    state_digest = _digest(f"state-{suffix}")
    retrieval_probe_digest = _digest(f"retrieval-probe-{suffix}")
    source_digest = _digest(f"retrieval-source-{suffix}")
    source_finding_digest = _digest(f"source-finding-{suffix}")
    roles = (
        _role_finding(
            "B4_RECENT",
            b4_kind,
            suffix,
            state_digest,
            retrieval_probe_digest,
            source_digest,
            source_finding_digest,
        ),
        _role_finding(
            "TSPM_FAST",
            fast_kind,
            suffix,
            state_digest,
            retrieval_probe_digest,
            source_digest,
            source_finding_digest,
        ),
        _role_finding(
            "B_STABLE_AUDITORY",
            "absent",
            suffix,
            state_digest,
            retrieval_probe_digest,
            source_digest,
            source_finding_digest,
        ),
        _role_finding(
            "B_STABLE_VISUAL",
            b_kind,
            suffix,
            state_digest,
            retrieval_probe_digest,
            source_digest,
            source_finding_digest,
        ),
    )
    candidate_count = sum(item.candidate is not None for item in roles)
    referenced_values = sum(
        336 if type(item.candidate) is finding_contract.AVContextCandidate336V1 else 288
        for item in roles
        if item.candidate is not None
    )
    payload = {
        "schema": finding_contract.S2KJ_BINDING_SCHEMA,
        "config_digest": config_digest,
        "composite_state_digest": state_digest,
        "probe_digest": retrieval_probe_digest,
        "source_digest": source_digest,
        "auditory_source_digest": _digest(f"auditory-source-{suffix}"),
        "visual_source_digest": _digest(f"visual-source-{suffix}"),
        "source_time_geometry_digest": _digest(f"time-geometry-{suffix}"),
        "source_finding_digest": source_finding_digest,
        "role_finding_digests": [item.finding_digest for item in roles],
        "prestate_digest": state_digest,
        "poststate_digest": state_digest,
        "source_ledger_digest": _digest(f"source-ledger-{suffix}"),
        "candidate_count": candidate_count,
        "referenced_value_count": referenced_values,
    }
    source = finding_contract.ValidatedPerceptualFinding336V1(
        config_digest,
        state_digest,
        retrieval_probe_digest,
        source_digest,
        payload["auditory_source_digest"],
        payload["visual_source_digest"],
        payload["source_time_geometry_digest"],
        source_finding_digest,
        roles,
        state_digest,
        state_digest,
        payload["source_ledger_digest"],
        candidate_count,
        referenced_values,
        finding_contract._digest(payload),
    )
    return context_contract.project_two_area_perceptual_context_336(source)


def _probe(context: context_contract.TwoAreaPerceptualContext336, suffix: str):
    return admission.build_masked_admission_probe_336(
        source_digest=_digest(f"masked-source-{suffix}"),
        config_digest=context.config_digest,
        values=(0.0,) * 32 + (None,) * 256,
    )


def _call(b4_kind: str, fast_kind: str, b_kind: str, suffix: str):
    source = _context(b4_kind, fast_kind, b_kind, suffix)
    probe = _probe(source, suffix)
    return admission.form_two_area_context_admission_336(source, probe), source, probe


def _semantic(result: admission.ControlledContextAdmission336V1) -> tuple[object, ...]:
    hypothesis = result.hypothesis
    return (
        result.decision,
        result.a_recent.status,
        result.b_stable.status,
        result.public_candidate_count,
        None if hypothesis is None else hypothesis.area,
        None if hypothesis is None else hypothesis.proposed_values,
        None if hypothesis is None else len(hypothesis.provenance_finding_digests),
    )


class S2KNPrivateTwoAreaContextAdmission336Tests(unittest.TestCase):
    def test_01_both_internal_a_roles_absent_make_no_a_candidate(self) -> None:
        result, _, _ = _call("absent", "absent", "conflict", "a-absent")
        self.assertEqual("A_RECENT_ABSENT_VALID", result.a_recent.status)
        self.assertEqual(0, result.a_recent.public_candidate_count)
        self.assertEqual("ABSTAIN_NO_APPLICABLE_CONTEXT", result.decision)

    def test_02_only_b4_applicable_makes_one_public_a_candidate(self) -> None:
        result, _, _ = _call("x", "absent", "absent", "b4-only")
        self.assertEqual("ADMIT_SINGLE_CONTEXT", result.decision)
        self.assertEqual("A_RECENT", result.hypothesis.area)
        self.assertEqual(1, len(result.hypothesis.provenance_finding_digests))

    def test_03_only_fast_applicable_makes_one_public_a_candidate(self) -> None:
        result, _, _ = _call("absent", "x", "absent", "fast-only")
        self.assertEqual("ADMIT_SINGLE_CONTEXT", result.decision)
        self.assertEqual("A_RECENT", result.hypothesis.area)
        self.assertEqual(1, len(result.hypothesis.provenance_candidate_digests))

    def test_04_equal_b4_and_fast_collapse_with_two_provenance_records(self) -> None:
        result, _, _ = _call("x", "x", "absent", "a-equal")
        self.assertEqual("A_RECENT_APPLICABLE", result.a_recent.status)
        self.assertEqual(1, result.public_candidate_count)
        self.assertEqual("A_RECENT", result.hypothesis.area)
        self.assertEqual(2, len(result.hypothesis.provenance_candidate_digests))

    def test_05_different_applicable_b4_and_fast_force_internal_abstention(self) -> None:
        result, _, _ = _call("x", "y", "x", "a-conflict")
        self.assertEqual("A_RECENT_INTERNAL_CONFLICT", result.a_recent.status)
        self.assertEqual("ABSTAIN_A_RECENT_INTERNAL_CONFLICT", result.decision)
        self.assertIsNone(result.hypothesis)
        self.assertEqual(1, result.public_candidate_count)

    def test_06_only_b_stable_visual_admits_public_b(self) -> None:
        result, _, _ = _call("absent", "absent", "x", "b-only")
        self.assertEqual("B_STABLE_APPLICABLE", result.b_stable.status)
        self.assertEqual("ADMIT_SINGLE_CONTEXT", result.decision)
        self.assertEqual("B_STABLE", result.hypothesis.area)

    def test_07_simultaneous_a_and_b_are_ambiguous_even_when_equal(self) -> None:
        result, _, _ = _call("x", "absent", "x", "ab-ambiguous")
        self.assertEqual(2, result.public_candidate_count)
        self.assertEqual("ABSTAIN_AMBIGUOUS_CONTEXT", result.decision)
        self.assertIsNone(result.hypothesis)

    def test_08_present_but_visibly_conflicting_roles_are_not_applicable(self) -> None:
        result, _, _ = _call("conflict", "absent", "conflict", "visible-conflict")
        self.assertEqual("A_RECENT_NOT_APPLICABLE", result.a_recent.status)
        self.assertEqual("B_STABLE_NOT_APPLICABLE", result.b_stable.status)
        self.assertEqual("ABSTAIN_NO_APPLICABLE_CONTEXT", result.decision)

    def test_09_complete_valid_absence_is_no_context(self) -> None:
        result, _, _ = _call("absent", "absent", "absent", "all-absent")
        self.assertEqual("ABSTAIN_NO_CONTEXT", result.decision)
        self.assertEqual(0, result.public_candidate_count)
        self.assertIsNone(result.hypothesis)

    def test_10_damaged_nested_candidate_fails_closed_without_output(self) -> None:
        source = _context("x", "absent", "absent", "damaged")
        probe = _probe(source, "damaged")
        object.__setattr__(source.a_recent.b4_recent.candidate, "visual_values", (0.0,) * 287)
        with self.assertRaises(admission.S2KNAdmissionError):
            admission.form_two_area_context_admission_336(source, probe)

    def test_11_b4_fast_swap_preserves_semantics_and_baseline_matches(self) -> None:
        left_context = _context("x", "absent", "absent", "swap-left")
        right_context = _context("absent", "x", "absent", "swap-right")
        left_probe = _probe(left_context, "swap-left")
        right_probe = _probe(right_context, "swap-right")
        left = admission.form_two_area_context_admission_336(left_context, left_probe)
        right = admission.form_two_area_context_admission_336(right_context, right_probe)
        self.assertEqual(_semantic(left), _semantic(right))

        cases = (
            ("absent", "absent", "conflict"),
            ("x", "absent", "absent"),
            ("absent", "x", "absent"),
            ("x", "x", "absent"),
            ("x", "y", "x"),
            ("absent", "absent", "x"),
            ("x", "absent", "x"),
            ("conflict", "absent", "conflict"),
            ("absent", "absent", "absent"),
        )
        for ordinal, kinds in enumerate(cases, start=1):
            context = _context(*kinds, f"baseline-{ordinal:02d}")
            probe = _probe(context, f"baseline-{ordinal:02d}")
            primary = admission.form_two_area_context_admission_336(context, probe)
            direct = baseline.form_direct_two_area_admission_baseline_336(context, probe)
            with self.subTest(ordinal=ordinal):
                self.assertEqual(_semantic(primary), _semantic(direct))

    def test_12_outputs_are_frozen_bounded_read_only_and_private(self) -> None:
        result, context, probe = _call("x", "x", "absent", "bounds")
        before = (context.bundle_digest, context.composite_state_digest, probe.probe_digest)
        self.assertEqual(before, (context.bundle_digest, context.composite_state_digest, probe.probe_digest))
        self.assertEqual(result.prestate_digest, result.poststate_digest)
        self.assertLessEqual(
            result.resource_ledger.serialized_output_bytes,
            admission.MAX_OUTPUT_BYTES,
        )
        self.assertEqual(
            result.resource_ledger.serialized_output_bytes,
            len(admission.canonical_bytes(result.canonical_payload())),
        )
        self.assertEqual(0, result.resource_ledger.memory_receptor_consumer_or_field_call_count)
        self.assertIsNone(result.replacement_perception)
        self.assertIsNone(result.ranking)
        with self.assertRaises(FrozenInstanceError):
            result.decision = "ABSTAIN_NO_CONTEXT"

        root = Path(__file__).resolve().parents[1]
        primary_path = root / "tools" / "_s2kn_private_two_area_context_admission_336.py"
        baseline_path = root / "tools" / "_s2kn_private_direct_two_area_admission_baseline.py"
        forbidden_imports = ("runner", "recorder", "receptor", "field")
        for path in (primary_path, baseline_path):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
                elif isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
            self.assertFalse(
                any(token in module for token in forbidden_imports for module in imports),
                imports,
            )
        baseline_source = baseline_path.read_text(encoding="utf-8")
        self.assertNotIn("form_two_area_context_admission_336(", baseline_source)
        self.assertNotIn("project_a_recent_336(", baseline_source)
        self.assertEqual((), admission.__all__)
        self.assertEqual((), baseline.__all__)


if __name__ == "__main__":
    unittest.main()
