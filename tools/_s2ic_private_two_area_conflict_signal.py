"""Private pure S2-IC read-only conflict signal for A_RECENT and B_STABLE."""

from __future__ import annotations

from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2ic_private_two_area_conflict_contract as contract
from tools import _s2jd_private_aggregate_context_binding as aggregate_binding


def _absence(
    area: str,
    signal_input: contract.TwoAreaConflictSignalInput,
    area_digest: str,
    role_finding: context.PerceptualContextRoleFinding,
) -> contract.AreaApplicabilityFinding:
    contract.require(
        role_finding.status == "ABSENT_VALID"
        and role_finding.candidate is None
        and role_finding.absence_reason is not None,
        "S2HZ-E005",
        "O2" if area == "A_RECENT" else "O3",
    )
    return contract.AreaApplicabilityFinding.build(
        area=area,
        status="ABSENT_VALID",
        signal_input=signal_input,
        area_finding_digest=area_digest,
        role_finding_digest=role_finding.finding_digest,
        candidate_digest=None,
        component_digest=None,
        component_source_digest=None,
        visible_mismatch_positions=(),
        masked_values=(),
    )


def _finding_from_visual(
    *,
    area: str,
    signal_input: contract.TwoAreaConflictSignalInput,
    probe: probe_contract.MaskedVisualProbe,
    area_digest: str,
    role_finding: context.PerceptualContextRoleFinding,
    candidate: context.PerceptualContextCandidate,
    component: context.PerceptualContextComponent,
    visual: tuple[float, ...],
) -> contract.AreaApplicabilityFinding:
    operation = "O2" if area == "A_RECENT" else "O3"
    contract.require(
        type(visual) is tuple
        and len(visual) == 18
        and all(type(value) is float and 0.0 <= value <= 1.0 for value in visual),
        "S2HZ-E005",
        operation,
    )
    mismatches = tuple(
        index
        for index in probe_contract.VISIBLE_POSITIONS
        if probe.values[index] != visual[index]
    )
    status = "APPLICABLE" if not mismatches else "VISIBLE_CONFLICT"
    masked_values = (
        tuple(visual[index] for index in probe_contract.MASKED_POSITIONS)
        if status == "APPLICABLE"
        else ()
    )
    return contract.AreaApplicabilityFinding.build(
        area=area,
        status=status,
        signal_input=signal_input,
        area_finding_digest=area_digest,
        role_finding_digest=role_finding.finding_digest,
        candidate_digest=candidate.candidate_digest,
        component_digest=component.component_digest,
        component_source_digest=component.source_digest,
        visible_mismatch_positions=mismatches,
        masked_values=masked_values,
    )


def _assess_a(
    signal_input: contract.TwoAreaConflictSignalInput,
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
) -> contract.AreaApplicabilityFinding:
    area = bundle.area_findings[0]
    finding = area.recent_content
    contract.require(area.area == "A_RECENT" and finding.role == "B4_RECENT", "S2HZ-E005", "O2")
    if finding.status == "ABSENT_VALID":
        return _absence("A_RECENT", signal_input, area.finding_digest, finding)
    contract.require(finding.status == "AVAILABLE_COMPLETE", "S2HZ-E005", "O2")
    candidate = finding.candidate
    contract.require(
        candidate is not None
        and candidate.role == "B4_RECENT"
        and len(candidate.components) == 1,
        "S2HZ-E005",
        "O2",
    )
    component = candidate.components[0]
    contract.require(component.component_role == "AV_JOINT" and len(component.values) == 26, "S2HZ-E005", "O2")
    visual = tuple(component.values[8:])
    return _finding_from_visual(
        area="A_RECENT",
        signal_input=signal_input,
        probe=probe,
        area_digest=area.finding_digest,
        role_finding=finding,
        candidate=candidate,
        component=component,
        visual=visual,
    )


def _assess_b(
    signal_input: contract.TwoAreaConflictSignalInput,
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
) -> contract.AreaApplicabilityFinding:
    area = bundle.area_findings[1]
    finding = area.stable_content
    contract.require(area.area == "B_STABLE" and finding.role == "TSPM_SLOW", "S2HZ-E005", "O3")
    if finding.status == "ABSENT_VALID":
        return _absence("B_STABLE", signal_input, area.finding_digest, finding)
    contract.require(finding.status in ("AVAILABLE_COMPLETE", "AVAILABLE_PARTIAL"), "S2HZ-E005", "O3")
    candidate = finding.candidate
    contract.require(candidate is not None and candidate.role == "TSPM_SLOW", "S2HZ-E005", "O3")
    visual_components = tuple(
        component for component in candidate.components if component.component_role == "VISUAL"
    )
    contract.require(len(visual_components) == 1, "S2HZ-E005", "O3")
    component = visual_components[0]
    contract.require(component.stable is True and len(component.values) == 18, "S2HZ-E005", "O3")
    return _finding_from_visual(
        area="B_STABLE",
        signal_input=signal_input,
        probe=probe,
        area_digest=area.finding_digest,
        role_finding=finding,
        candidate=candidate,
        component=component,
        visual=tuple(component.values),
    )


def _compare(
    signal_input: contract.TwoAreaConflictSignalInput,
    a_finding: contract.AreaApplicabilityFinding,
    b_finding: contract.AreaApplicabilityFinding,
) -> contract.MaskedSupplementComparison:
    if a_finding.status != "APPLICABLE" or b_finding.status != "APPLICABLE":
        return contract.MaskedSupplementComparison.build(
            signal_input,
            a_finding,
            b_finding,
            "NOT_PERFORMED",
            (),
        )
    differing = tuple(
        position
        for position, a_value, b_value in zip(
            probe_contract.MASKED_POSITIONS,
            a_finding.masked_values,
            b_finding.masked_values,
            strict=True,
        )
        if a_value != b_value
    )
    return contract.MaskedSupplementComparison.build(
        signal_input,
        a_finding,
        b_finding,
        "DIFFERENT" if differing else "EQUAL",
        differing,
    )


def _status(
    a_finding: contract.AreaApplicabilityFinding,
    b_finding: contract.AreaApplicabilityFinding,
    comparison: contract.MaskedSupplementComparison,
) -> str:
    findings = (a_finding, b_finding)
    present_count = sum(item.status != "ABSENT_VALID" for item in findings)
    applicable_count = sum(item.status == "APPLICABLE" for item in findings)
    if present_count == 0:
        return "NO_CONTEXT"
    if applicable_count == 0:
        return "NO_APPLICABLE_CONTEXT"
    if applicable_count == 1:
        return "SINGLE_SOURCE"
    contract.require(comparison.comparison_status in ("EQUAL", "DIFFERENT"), "S2HZ-E005", "O4")
    return "CONSISTENT" if comparison.comparison_status == "EQUAL" else "CONFLICT"


def form_two_area_conflict_signal(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_input: contract.TwoAreaConflictSignalInput,
    owner: contract.TwoAreaConflictSignalOwner,
) -> contract.TwoAreaConflictSignalCommit:
    """Form one atomic read-only five-state signal without choosing an area."""

    if type(owner) is not contract.TwoAreaConflictSignalOwner or owner.state != "READY":
        contract.fail("S2HZ-E008", "O1")
    try:
        before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        contract.validate_sources(signal_input, owner, probe, bundle, "SIGNAL")
        a_finding = _assess_a(signal_input, probe, bundle)
        b_finding = _assess_b(signal_input, probe, bundle)
        comparison = _compare(signal_input, a_finding, b_finding)
        status = _status(a_finding, b_finding, comparison)
        present_count = sum(item.status != "ABSENT_VALID" for item in (a_finding, b_finding))
        applicable_count = sum(item.status == "APPLICABLE" for item in (a_finding, b_finding))
        ledger = contract.TwoAreaConflictSignalLedger.build(present_count, applicable_count)
        contract.require(
            before == (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest),
            "S2HZ-E006",
            "O5",
        )
        result = contract.build_result(signal_input, a_finding, b_finding, comparison, ledger, status)
        return contract.publish_success(owner, signal_input, a_finding, b_finding, comparison, ledger, result)
    except contract.S2ICSignalFailure:
        raise
    except contract.S2ICContractError as error:
        contract.publish_failure(owner, signal_input, error)
    except Exception as error:
        contract.publish_failure(owner, signal_input, contract.S2ICContractError("S2HZ-E001", "O1"))
        raise AssertionError("unreachable") from error


def _finding_from_aggregate_evidence(
    *,
    area: str,
    signal_input: contract.TwoAreaConflictSignalInput,
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    binding: aggregate_binding.AggregateVisibilityBindingV1,
) -> contract.AreaApplicabilityFinding:
    operation = "O2" if area == "A_RECENT" else "O3"
    area_finding = bundle.area_findings[0] if area == "A_RECENT" else bundle.area_findings[1]
    role_finding = area_finding.recent_content if area == "A_RECENT" else area_finding.stable_content
    evidence = binding.a_evidence if area == "A_RECENT" else binding.b_evidence
    if role_finding.status == "ABSENT_VALID":
        return _absence(area, signal_input, area_finding.finding_digest, role_finding)
    candidate = role_finding.candidate
    contract.require(candidate is not None, "S2HZ-E005", operation)
    components = (
        candidate.components
        if area == "A_RECENT"
        else tuple(item for item in candidate.components if item.component_role == "VISUAL")
    )
    contract.require(len(components) == 1, "S2HZ-E005", operation)
    component = components[0]
    visual = tuple(component.values[8:]) if area == "A_RECENT" else tuple(component.values)
    mismatches = tuple(
        position
        for position in probe_contract.VISIBLE_POSITIONS
        if aggregate_binding.aggregate_digests_equivalent(
            binding.probe_ordered_aggregate_code_digests[position],
            evidence.ordered_aggregate_code_digests[position],
        )
        != aggregate_binding.aggregate.SAME_RECEPTOR_AGGREGATE
    )
    status = "APPLICABLE" if not mismatches else "VISIBLE_CONFLICT"
    return contract.AreaApplicabilityFinding.build(
        area=area,
        status=status,
        signal_input=signal_input,
        area_finding_digest=area_finding.finding_digest,
        role_finding_digest=role_finding.finding_digest,
        candidate_digest=candidate.candidate_digest,
        component_digest=component.component_digest,
        component_source_digest=component.source_digest,
        visible_mismatch_positions=mismatches,
        masked_values=(
            tuple(visual[index] for index in probe_contract.MASKED_POSITIONS)
            if status == "APPLICABLE"
            else ()
        ),
    )


def _compare_with_aggregate_evidence(
    signal_input: contract.TwoAreaConflictSignalInput,
    a_finding: contract.AreaApplicabilityFinding,
    b_finding: contract.AreaApplicabilityFinding,
    binding: aggregate_binding.AggregateVisibilityBindingV1,
) -> contract.MaskedSupplementComparison:
    if a_finding.status != "APPLICABLE" or b_finding.status != "APPLICABLE":
        return contract.MaskedSupplementComparison.build(
            signal_input, a_finding, b_finding, "NOT_PERFORMED", ()
        )
    differing = tuple(
        position
        for position in probe_contract.MASKED_POSITIONS
        if aggregate_binding.aggregate_digests_equivalent(
            binding.a_evidence.ordered_aggregate_code_digests[position],
            binding.b_evidence.ordered_aggregate_code_digests[position],
        )
        != aggregate_binding.aggregate.SAME_RECEPTOR_AGGREGATE
    )
    return contract.MaskedSupplementComparison.build(
        signal_input,
        a_finding,
        b_finding,
        "DIFFERENT" if differing else "EQUAL",
        differing,
    )


def form_two_area_conflict_signal_with_aggregate_evidence(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_input: contract.TwoAreaConflictSignalInput,
    owner: contract.TwoAreaConflictSignalOwner,
    binding: aggregate_binding.AggregateVisibilityBindingV1,
) -> contract.TwoAreaConflictSignalCommit:
    """Form the signal using only prospective receptor aggregate equality."""

    if type(owner) is not contract.TwoAreaConflictSignalOwner or owner.state != "READY":
        contract.fail("S2HZ-E008", "O1")
    try:
        before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        contract.validate_sources(signal_input, owner, probe, bundle, "SIGNAL")
        aggregate_binding.validate_aggregate_visibility_binding(
            binding, probe, bundle, signal_input
        )
        a_finding = _finding_from_aggregate_evidence(
            area="A_RECENT",
            signal_input=signal_input,
            probe=probe,
            bundle=bundle,
            binding=binding,
        )
        b_finding = _finding_from_aggregate_evidence(
            area="B_STABLE",
            signal_input=signal_input,
            probe=probe,
            bundle=bundle,
            binding=binding,
        )
        comparison = _compare_with_aggregate_evidence(
            signal_input, a_finding, b_finding, binding
        )
        status = _status(a_finding, b_finding, comparison)
        present_count = sum(item.status != "ABSENT_VALID" for item in (a_finding, b_finding))
        applicable_count = sum(item.status == "APPLICABLE" for item in (a_finding, b_finding))
        ledger = contract.TwoAreaConflictSignalLedger.build(present_count, applicable_count)
        contract.require(
            before == (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest),
            "S2HZ-E006",
            "O5",
        )
        result = contract.build_result(signal_input, a_finding, b_finding, comparison, ledger, status)
        return contract.publish_success(owner, signal_input, a_finding, b_finding, comparison, ledger, result)
    except contract.S2ICSignalFailure:
        raise
    except (contract.S2ICContractError, aggregate_binding.S2JDBindingError) as error:
        mapped = error if isinstance(error, contract.S2ICContractError) else contract.S2ICContractError("S2HZ-E005", "O1")
        contract.publish_failure(owner, signal_input, mapped)
    except Exception as error:
        contract.publish_failure(owner, signal_input, contract.S2ICContractError("S2HZ-E001", "O1"))
        raise AssertionError("unreachable") from error
