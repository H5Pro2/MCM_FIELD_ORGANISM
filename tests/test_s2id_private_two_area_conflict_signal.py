"""Neutral one-shot qualification tests for the private S2-IC signal."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2ic_private_direct_two_area_conflict_baseline as baseline
from tools import _s2ic_private_two_area_conflict_contract as contract
from tools import _s2ic_private_two_area_conflict_signal as signal


VISIBLE_VALUE = 0.25
OTHER_VISIBLE_VALUE = 0.75
MASKED_X = 0.375
MASKED_Y = 0.625


def _digest(label: str) -> str:
    return contract.digest({"neutral": label})


def _visual(kind: str) -> tuple[float, ...]:
    values = []
    for index in range(18):
        if index in probe_contract.VISIBLE_POSITIONS:
            values.append(OTHER_VISIBLE_VALUE if kind == "conflict" else VISIBLE_VALUE)
        else:
            values.append(MASKED_Y if kind == "y" else MASKED_X)
    return tuple(values)


def _probe() -> probe_contract.MaskedVisualProbe:
    values = tuple(
        VISIBLE_VALUE if index in probe_contract.VISIBLE_POSITIONS else None
        for index in range(18)
    )
    return probe_contract.MaskedVisualProbe.build(values, _digest("probe-source"))


def _component(
    area: str,
    visual_kind: str,
) -> context.PerceptualContextComponent:
    visual = _visual(visual_kind)
    if area == "A_RECENT":
        values = (0.125,) * 8 + visual
        role = "AV_JOINT"
        native = (0.01, 0.01)
        functional = (0.01, 0.01)
        support = None
        stable = None
        selected = None
        formation = 1
    else:
        values = visual
        role = "VISUAL"
        native = (0.01,)
        functional = (0.01,)
        support = 3
        stable = True
        selected = 4
        formation = None
    payload = {
        "schema": context.S2GB_SCHEMA,
        "component_role": role,
        "values": list(values),
        "source_id": f"neutral.{area.lower()}.{visual_kind}",
        "source_digest": _digest(f"{area}-{visual_kind}-source"),
        "values_digest": context._digest(list(values)),
        "native_distances": list(native),
        "functional_distances": list(functional),
        "support_count": support,
        "stable": stable,
        "last_selected_step": selected,
        "formation_index": formation,
    }
    return context.PerceptualContextComponent(
        role,
        values,
        payload["source_id"],
        payload["source_digest"],
        payload["values_digest"],
        native,
        functional,
        support,
        stable,
        selected,
        formation,
        context._digest(payload),
    )


def _role_finding(area: str, kind: str) -> context.PerceptualContextRoleFinding:
    role = "B4_RECENT" if area == "A_RECENT" else "TSPM_SLOW"
    if kind == "absent":
        absence_reason = "NO_OCCUPIED_SOURCE" if area == "A_RECENT" else "NO_STABLE_SLOW_MATCH"
        payload = {
            "schema": context.S2GB_SCHEMA,
            "role": role,
            "status": "ABSENT_VALID",
            "candidate_digest": None,
            "absence_reason": absence_reason,
        }
        return context.PerceptualContextRoleFinding(
            role,
            "ABSENT_VALID",
            None,
            absence_reason,
            context._digest(payload),
        )

    component = _component(area, kind)
    relation = (
        "JOINT_SOURCE_VALUES"
        if area == "A_RECENT"
        else "CROSS_MODAL_RELATION_NOT_REPRESENTED"
    )
    candidate_payload = {
        "schema": context.S2GB_SCHEMA,
        "role": role,
        "component_digests": [component.component_digest],
        "cross_modal_relation": relation,
    }
    candidate = context.PerceptualContextCandidate(
        role,
        (component,),
        relation,
        context._digest(candidate_payload),
    )
    status = "AVAILABLE_COMPLETE" if area == "A_RECENT" else "AVAILABLE_PARTIAL"
    finding_payload = {
        "schema": context.S2GB_SCHEMA,
        "role": role,
        "status": status,
        "candidate_digest": candidate.candidate_digest,
        "absence_reason": None,
    }
    return context.PerceptualContextRoleFinding(
        role,
        status,
        candidate,
        None,
        context._digest(finding_payload),
    )


def _absent_fast() -> context.PerceptualContextRoleFinding:
    payload = {
        "schema": context.S2GB_SCHEMA,
        "role": "TSPM_FAST",
        "status": "ABSENT_VALID",
        "candidate_digest": None,
        "absence_reason": "NO_OCCUPIED_SOURCE",
    }
    return context.PerceptualContextRoleFinding(
        "TSPM_FAST",
        "ABSENT_VALID",
        None,
        "NO_OCCUPIED_SOURCE",
        context._digest(payload),
    )


def _sequence() -> context.B4ShortSequenceFinding:
    payload = {
        "schema": context.S2GB_SCHEMA,
        "status": "NOT_REQUESTED",
        "reference_digests": [],
        "observed_b4_state_digest": _digest("b4-state"),
        "source_evidence_digest": _digest("sequence-absence"),
    }
    return context.B4ShortSequenceFinding(
        "NOT_REQUESTED",
        (),
        payload["observed_b4_state_digest"],
        payload["source_evidence_digest"],
        context._digest(payload),
    )


def _bundle(
    a_kind: str,
    b_kind: str,
    probe: probe_contract.MaskedVisualProbe,
) -> two_area.TwoAreaContextBundle:
    a_role = _role_finding("A_RECENT", a_kind)
    b_role = _role_finding("B_STABLE", b_kind)
    fast = _absent_fast()
    sequence = _sequence()
    a_payload = {
        "schema": two_area.S2GI_SCHEMA,
        "area": "A_RECENT",
        "recent_content_finding_digest": a_role.finding_digest,
        "fast_internal_finding_digest": fast.finding_digest,
        "short_sequence_finding_digest": sequence.finding_digest,
    }
    area_a = two_area.AreaARecentFinding(
        "A_RECENT",
        a_role,
        fast,
        sequence,
        two_area._digest(a_payload),
    )
    b_payload = {
        "schema": two_area.S2GI_SCHEMA,
        "area": "B_STABLE",
        "stable_content_finding_digest": b_role.finding_digest,
    }
    area_b = two_area.AreaBStableFinding(
        "B_STABLE",
        b_role,
        two_area._digest(b_payload),
    )
    candidates = tuple(
        finding.candidate for finding in (a_role, b_role) if finding.candidate is not None
    )
    components = tuple(item for candidate in candidates for item in candidate.components)
    ledger_payload = {
        "schema": two_area.S2GI_SCHEMA,
        "validated_bundle_count": 1,
        "validated_role_count": 3,
        "candidate_reference_count": len(candidates),
        "component_reference_count": len(components),
        "value_reference_count": sum(len(item.values) for item in components),
        "sequence_reference_count": 0,
        "area_projection_count": 2,
        "digest_operation_count": 4,
        "source_ledger_digest": _digest("source-ledger"),
    }
    ledger = two_area.TwoAreaContextResourceLedger(
        1,
        3,
        len(candidates),
        len(components),
        sum(len(item.values) for item in components),
        0,
        2,
        4,
        ledger_payload["source_ledger_digest"],
        two_area._digest(ledger_payload),
    )
    state = _digest("composite-state")
    output_payload = {
        "schema": two_area.S2GI_SCHEMA,
        "contract_digest": two_area.S2GH_CONTRACT_DIGEST,
        "source_bundle_digest": _digest("source-bundle"),
        "binding_digest": _digest("binding"),
        "config_digest": _digest("config"),
        "composite_state_digest": state,
        "probe_digest": probe.probe_digest,
        "source_digest": _digest("bundle-source"),
        "area_finding_digests": [area_a.finding_digest, area_b.finding_digest],
        "resource_ledger_digest": ledger.ledger_digest,
        "prestate_digest": state,
        "poststate_digest": state,
        "automatic_selection": None,
    }
    return two_area.TwoAreaContextBundle(
        two_area.S2GH_CONTRACT_DIGEST,
        output_payload["source_bundle_digest"],
        output_payload["binding_digest"],
        output_payload["config_digest"],
        state,
        probe.probe_digest,
        output_payload["source_digest"],
        (area_a, area_b),
        ledger,
        state,
        state,
        None,
        two_area._digest(output_payload),
    )


def _call(
    function_role: str,
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    suffix: str,
) -> tuple[contract.TwoAreaConflictSignalCommit, contract.TwoAreaConflictSignalOwner]:
    signal_input = contract.TwoAreaConflictSignalInput.build(
        f"neutral-{function_role.lower().replace('_', '-')}-{suffix}",
        function_role,
        probe,
        bundle,
    )
    owner = contract.TwoAreaConflictSignalOwner(
        contract.TwoAreaConflictOwnerPrestate.build(
            f"neutral-owner-{function_role.lower().replace('_', '-')}-{suffix}",
            signal_input,
        )
    )
    if function_role == "SIGNAL":
        return signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner), owner
    return baseline.form_direct_two_area_conflict_baseline(probe, bundle, signal_input, owner), owner


def _failure_fixture() -> tuple[
    probe_contract.MaskedVisualProbe,
    two_area.TwoAreaContextBundle,
    contract.TwoAreaConflictSignalInput,
    contract.TwoAreaConflictSignalOwner,
]:
    probe = _probe()
    bundle = _bundle("x", "x", probe)
    signal_input = contract.TwoAreaConflictSignalInput.build(
        "neutral-error-invocation",
        "SIGNAL",
        probe,
        bundle,
    )
    owner = contract.TwoAreaConflictSignalOwner(
        contract.TwoAreaConflictOwnerPrestate.build("neutral-error-owner", signal_input)
    )
    return probe, bundle, signal_input, owner


class S2IDPrivateTwoAreaConflictSignalTests(unittest.TestCase):
    def test_01_all_ten_paths_and_role_swaps_match_the_direct_baseline(self) -> None:
        cases = (
            ("x", "x", "CONSISTENT"),
            ("x", "y", "CONFLICT"),
            ("x", "absent", "SINGLE_SOURCE"),
            ("absent", "x", "SINGLE_SOURCE"),
            ("absent", "absent", "NO_CONTEXT"),
            ("x", "conflict", "SINGLE_SOURCE"),
            ("conflict", "x", "SINGLE_SOURCE"),
            ("conflict", "conflict", "NO_APPLICABLE_CONTEXT"),
            ("conflict", "absent", "NO_APPLICABLE_CONTEXT"),
            ("absent", "conflict", "NO_APPLICABLE_CONTEXT"),
        )
        seen = set()
        for ordinal, (a_kind, b_kind, expected) in enumerate(cases, start=1):
            for mirror, pair in enumerate(((a_kind, b_kind), (b_kind, a_kind))):
                probe = _probe()
                bundle = _bundle(pair[0], pair[1], probe)
                before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
                signal_commit, _ = _call("SIGNAL", probe, bundle, f"p{ordinal:02d}m{mirror}")
                baseline_commit, _ = _call("DIRECT_BASELINE", probe, bundle, f"p{ordinal:02d}m{mirror}")
                self.assertEqual(expected, signal_commit.result.status)
                self.assertEqual(signal_commit.result.status, baseline_commit.result.status)
                self.assertEqual(
                    signal_commit.result.differing_masked_positions,
                    baseline_commit.result.differing_masked_positions,
                )
                self.assertEqual(before, (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest))
                seen.add(signal_commit.result.status)
        self.assertEqual(set(contract.RESULT_STATUSES), seen)

    def test_02_status_boundaries_are_exclusive(self) -> None:
        probe = _probe()
        no_context, _ = _call("SIGNAL", probe, _bundle("absent", "absent", probe), "exclusive-none")
        none_applicable, _ = _call("SIGNAL", probe, _bundle("conflict", "absent", probe), "exclusive-conflict")
        self.assertEqual("NO_CONTEXT", no_context.result.status)
        self.assertEqual((), no_context.result.present_areas)
        self.assertEqual("NO_APPLICABLE_CONTEXT", none_applicable.result.status)
        self.assertEqual(("A_RECENT",), none_applicable.result.present_areas)
        self.assertEqual((), none_applicable.result.applicable_areas)

    def test_03_atomic_owner_read_only_and_no_selection(self) -> None:
        probe = _probe()
        bundle = _bundle("x", "y", probe)
        commit, owner = _call("SIGNAL", probe, bundle, "atomic-success")
        self.assertEqual("CONSUMED", owner.state)
        self.assertIs(owner.poststate, commit.owner_poststate)
        self.assertIsNone(commit.result.selected_area)
        self.assertIsNone(commit.result.recommended_area)
        self.assertIsNone(commit.result.automatic_selection)
        self.assertEqual(commit.result.prestate_digest, commit.result.poststate_digest)
        with self.assertRaises(FrozenInstanceError):
            commit.result.status = "CONSISTENT"

    def test_04_e001_type_or_schema_fails_without_regular_result(self) -> None:
        probe, bundle, signal_input, owner = _failure_fixture()
        object.__setattr__(signal_input, "schema", "invalid")
        with self.assertRaises(contract.S2ICSignalFailure) as caught:
            signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner)
        self.assertEqual("S2HZ-E001", caught.exception.code)
        self.assertEqual("FAILED", owner.state)
        self.assertFalse(hasattr(caught.exception, "result"))

    def test_05_e002_source_or_digest_mutation_fails_closed(self) -> None:
        probe, bundle, signal_input, owner = _failure_fixture()
        object.__setattr__(bundle, "source_digest", _digest("foreign-source"))
        with self.assertRaises(contract.S2ICSignalFailure) as caught:
            signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner)
        self.assertEqual("S2HZ-E002", caught.exception.code)

    def test_06_e003_owner_binding_mutation_fails_closed(self) -> None:
        probe, bundle, signal_input, owner = _failure_fixture()
        foreign_input = contract.TwoAreaConflictSignalInput.build(
            "neutral-foreign-invocation", "SIGNAL", probe, bundle
        )
        object.__setattr__(owner, "_prestate", contract.TwoAreaConflictOwnerPrestate.build("neutral-error-owner", foreign_input))
        with self.assertRaises(contract.S2ICSignalFailure) as caught:
            signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner)
        self.assertEqual("S2HZ-E003", caught.exception.code)

    def test_07_e004_probe_mask_mutation_fails_closed(self) -> None:
        probe, bundle, signal_input, owner = _failure_fixture()
        object.__setattr__(probe, "visible_positions", probe_contract.VISIBLE_POSITIONS[:-1])
        with self.assertRaises(contract.S2ICSignalFailure) as caught:
            signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner)
        self.assertEqual("S2HZ-E004", caught.exception.code)

    def test_08_e005_area_evidence_mutation_fails_closed(self) -> None:
        probe, bundle, signal_input, owner = _failure_fixture()
        object.__setattr__(bundle.area_findings[1], "stable_content", _absent_fast())
        with self.assertRaises(contract.S2ICSignalFailure) as caught:
            signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner)
        self.assertEqual("S2HZ-E005", caught.exception.code)

    def test_09_e006_read_only_state_mutation_fails_closed(self) -> None:
        probe, bundle, signal_input, owner = _failure_fixture()
        object.__setattr__(bundle, "poststate_digest", _digest("changed-state"))
        with self.assertRaises(contract.S2ICSignalFailure) as caught:
            signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner)
        self.assertEqual("S2HZ-E006", caught.exception.code)

    def test_10_e007_resource_mutation_fails_closed(self) -> None:
        probe, bundle, signal_input, owner = _failure_fixture()
        object.__setattr__(bundle.resource_ledger, "candidate_reference_count", 4)
        with self.assertRaises(contract.S2ICSignalFailure) as caught:
            signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner)
        self.assertEqual("S2HZ-E007", caught.exception.code)

    def test_11_e008_owner_reuse_is_terminal_and_has_no_second_output(self) -> None:
        probe, bundle, signal_input, owner = _failure_fixture()
        first = signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner)
        self.assertEqual("CONSUMED", first.owner_poststate.state)
        with self.assertRaises(contract.S2ICContractError) as caught:
            signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner)
        self.assertEqual("S2HZ-E008", caught.exception.code)
        self.assertIs(owner.poststate, first.owner_poststate)

    def test_12_ledger_formulas_cover_every_reachable_count_pair(self) -> None:
        for present, applicable in ((0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2)):
            ledger = contract.TwoAreaConflictSignalLedger.build(present, applicable)
            self.assertEqual(9 * present, ledger.visible_compare_count)
            self.assertEqual(9 * applicable, ledger.masked_value_reference_count)
            self.assertEqual(9 if applicable == 2 else 0, ledger.cross_area_compare_count)
            self.assertLessEqual(
                contract.artifact_size({**ledger.payload_without_digest(), "ledger_digest": ledger.ledger_digest}),
                contract.ARTIFACT_LIMITS["ledger"],
            )

    def test_13_worst_case_owner_and_success_artifacts_respect_limits(self) -> None:
        probe = _probe()
        bundle = _bundle("x", "y", probe)
        signal_input = contract.TwoAreaConflictSignalInput.build(
            "a" + "b" * 95,
            "SIGNAL",
            probe,
            bundle,
        )
        owner = contract.TwoAreaConflictSignalOwner(
            contract.TwoAreaConflictOwnerPrestate.build("a" + "c" * 95, signal_input)
        )
        commit = signal.form_two_area_conflict_signal(probe, bundle, signal_input, owner)
        payloads = (
            ("input", {**signal_input.payload_without_digest(), "input_digest": signal_input.input_digest}),
            ("owner", {**owner.prestate.payload_without_digest(), "owner_prestate_digest": owner.prestate.owner_prestate_digest}),
            ("owner", {**commit.owner_poststate.payload_without_digest(), "owner_poststate_digest": commit.owner_poststate.owner_poststate_digest}),
            ("result", {**commit.result.payload_without_digest(), "result_digest": commit.result.result_digest}),
            ("receipt", {**commit.receipt.payload_without_digest(), "receipt_digest": commit.receipt.receipt_digest}),
        )
        for role, payload in payloads:
            self.assertLessEqual(contract.artifact_size(payload), contract.ARTIFACT_LIMITS[role])

    def test_14_identifier_overflow_is_rejected_before_an_owner_exists(self) -> None:
        probe = _probe()
        bundle = _bundle("x", "x", probe)
        with self.assertRaises(contract.S2ICContractError) as caught:
            contract.TwoAreaConflictSignalInput.build("a" + "b" * 96, "SIGNAL", probe, bundle)
        self.assertEqual("S2HZ-E001", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
