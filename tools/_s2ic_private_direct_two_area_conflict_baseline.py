"""Independent direct-comparison baseline for the private S2-IC signal."""

from __future__ import annotations

from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2ic_private_two_area_conflict_contract as contract
from tools import _s2jd_private_aggregate_context_binding as aggregate_binding


def _direct_area_projection(
    area_name: str,
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_input: contract.TwoAreaConflictSignalInput,
) -> contract.AreaApplicabilityFinding:
    operation = "O2" if area_name == "A_RECENT" else "O3"
    if area_name == "A_RECENT":
        area_finding = bundle.area_findings[0]
        role_finding = area_finding.recent_content
        contract.require(area_finding.area == area_name and role_finding.role == "B4_RECENT", "S2HZ-E005", operation)
        if role_finding.status == "ABSENT_VALID":
            contract.require(role_finding.candidate is None and role_finding.absence_reason is not None, "S2HZ-E005", operation)
            return contract.AreaApplicabilityFinding.build(
                area=area_name,
                status="ABSENT_VALID",
                signal_input=signal_input,
                area_finding_digest=area_finding.finding_digest,
                role_finding_digest=role_finding.finding_digest,
                candidate_digest=None,
                component_digest=None,
                component_source_digest=None,
                visible_mismatch_positions=(),
                masked_values=(),
            )
        contract.require(role_finding.status == "AVAILABLE_COMPLETE", "S2HZ-E005", operation)
        candidate = role_finding.candidate
        contract.require(candidate is not None and candidate.role == "B4_RECENT" and len(candidate.components) == 1, "S2HZ-E005", operation)
        component = candidate.components[0]
        contract.require(component.component_role == "AV_JOINT" and len(component.values) == 26, "S2HZ-E005", operation)
        visual_values = tuple(component.values[8:])
    else:
        contract.require(area_name == "B_STABLE", "S2HZ-E005", operation)
        area_finding = bundle.area_findings[1]
        role_finding = area_finding.stable_content
        contract.require(area_finding.area == area_name and role_finding.role == "TSPM_SLOW", "S2HZ-E005", operation)
        if role_finding.status == "ABSENT_VALID":
            contract.require(role_finding.candidate is None and role_finding.absence_reason is not None, "S2HZ-E005", operation)
            return contract.AreaApplicabilityFinding.build(
                area=area_name,
                status="ABSENT_VALID",
                signal_input=signal_input,
                area_finding_digest=area_finding.finding_digest,
                role_finding_digest=role_finding.finding_digest,
                candidate_digest=None,
                component_digest=None,
                component_source_digest=None,
                visible_mismatch_positions=(),
                masked_values=(),
            )
        contract.require(role_finding.status in ("AVAILABLE_COMPLETE", "AVAILABLE_PARTIAL"), "S2HZ-E005", operation)
        candidate = role_finding.candidate
        contract.require(candidate is not None and candidate.role == "TSPM_SLOW", "S2HZ-E005", operation)
        visual_components = tuple(item for item in candidate.components if item.component_role == "VISUAL")
        contract.require(len(visual_components) == 1, "S2HZ-E005", operation)
        component = visual_components[0]
        contract.require(component.stable is True and len(component.values) == 18, "S2HZ-E005", operation)
        visual_values = tuple(component.values)

    contract.require(
        type(visual_values) is tuple
        and len(visual_values) == 18
        and all(type(value) is float and 0.0 <= value <= 1.0 for value in visual_values),
        "S2HZ-E005",
        operation,
    )
    mismatches = tuple(
        position
        for position in probe_contract.VISIBLE_POSITIONS
        if probe.values[position] != visual_values[position]
    )
    applicable = not mismatches
    return contract.AreaApplicabilityFinding.build(
        area=area_name,
        status="APPLICABLE" if applicable else "VISIBLE_CONFLICT",
        signal_input=signal_input,
        area_finding_digest=area_finding.finding_digest,
        role_finding_digest=role_finding.finding_digest,
        candidate_digest=candidate.candidate_digest,
        component_digest=component.component_digest,
        component_source_digest=component.source_digest,
        visible_mismatch_positions=mismatches,
        masked_values=(
            tuple(visual_values[position] for position in probe_contract.MASKED_POSITIONS)
            if applicable
            else ()
        ),
    )


def _direct_decision(
    signal_input: contract.TwoAreaConflictSignalInput,
    left: contract.AreaApplicabilityFinding,
    right: contract.AreaApplicabilityFinding,
) -> tuple[contract.MaskedSupplementComparison, str]:
    applicable = tuple(item for item in (left, right) if item.status == "APPLICABLE")
    present_count = sum(item.status != "ABSENT_VALID" for item in (left, right))
    if len(applicable) != 2:
        comparison = contract.MaskedSupplementComparison.build(signal_input, left, right, "NOT_PERFORMED", ())
    else:
        different = tuple(
            position
            for position, left_value, right_value in zip(
                probe_contract.MASKED_POSITIONS,
                left.masked_values,
                right.masked_values,
                strict=True,
            )
            if left_value != right_value
        )
        comparison = contract.MaskedSupplementComparison.build(
            signal_input,
            left,
            right,
            "DIFFERENT" if different else "EQUAL",
            different,
        )

    if present_count == 0:
        status = "NO_CONTEXT"
    elif len(applicable) == 0:
        status = "NO_APPLICABLE_CONTEXT"
    elif len(applicable) == 1:
        status = "SINGLE_SOURCE"
    else:
        status = "CONSISTENT" if comparison.comparison_status == "EQUAL" else "CONFLICT"
    return comparison, status


def form_direct_two_area_conflict_baseline(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_input: contract.TwoAreaConflictSignalInput,
    owner: contract.TwoAreaConflictSignalOwner,
) -> contract.TwoAreaConflictSignalCommit:
    """Classify A/B directly without calling the S2-IC signal implementation."""

    if type(owner) is not contract.TwoAreaConflictSignalOwner or owner.state != "READY":
        contract.fail("S2HZ-E008", "O1")
    try:
        before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        contract.validate_sources(signal_input, owner, probe, bundle, "DIRECT_BASELINE")
        a_finding = _direct_area_projection("A_RECENT", probe, bundle, signal_input)
        b_finding = _direct_area_projection("B_STABLE", probe, bundle, signal_input)
        comparison, status = _direct_decision(signal_input, a_finding, b_finding)
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


def _direct_area_aggregate_projection(
    area_name: str,
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_input: contract.TwoAreaConflictSignalInput,
    binding: aggregate_binding.AggregateVisibilityBindingV1,
) -> contract.AreaApplicabilityFinding:
    operation = "O2" if area_name == "A_RECENT" else "O3"
    area_finding = bundle.area_findings[0] if area_name == "A_RECENT" else bundle.area_findings[1]
    role_finding = area_finding.recent_content if area_name == "A_RECENT" else area_finding.stable_content
    evidence = binding.a_evidence if area_name == "A_RECENT" else binding.b_evidence
    if role_finding.status == "ABSENT_VALID":
        contract.require(evidence.status == aggregate_binding.ABSENT_VALID, "S2HZ-E005", operation)
        return contract.AreaApplicabilityFinding.build(
            area=area_name,
            status="ABSENT_VALID",
            signal_input=signal_input,
            area_finding_digest=area_finding.finding_digest,
            role_finding_digest=role_finding.finding_digest,
            candidate_digest=None,
            component_digest=None,
            component_source_digest=None,
            visible_mismatch_positions=(),
            masked_values=(),
        )
    candidate = role_finding.candidate
    contract.require(candidate is not None, "S2HZ-E005", operation)
    components = (
        candidate.components
        if area_name == "A_RECENT"
        else tuple(item for item in candidate.components if item.component_role == "VISUAL")
    )
    contract.require(len(components) == 1, "S2HZ-E005", operation)
    component = components[0]
    visual = tuple(component.values[8:]) if area_name == "A_RECENT" else tuple(component.values)
    mismatches = []
    for position in probe_contract.VISIBLE_POSITIONS:
        relation = aggregate_binding.aggregate_digests_equivalent(
            binding.probe_ordered_aggregate_code_digests[position],
            evidence.ordered_aggregate_code_digests[position],
        )
        if relation == aggregate_binding.aggregate.DIFFERENT_RECEPTOR_AGGREGATE:
            mismatches.append(position)
    mismatch_tuple = tuple(mismatches)
    applicable = not mismatch_tuple
    return contract.AreaApplicabilityFinding.build(
        area=area_name,
        status="APPLICABLE" if applicable else "VISIBLE_CONFLICT",
        signal_input=signal_input,
        area_finding_digest=area_finding.finding_digest,
        role_finding_digest=role_finding.finding_digest,
        candidate_digest=candidate.candidate_digest,
        component_digest=component.component_digest,
        component_source_digest=component.source_digest,
        visible_mismatch_positions=mismatch_tuple,
        masked_values=(
            tuple(visual[position] for position in probe_contract.MASKED_POSITIONS)
            if applicable
            else ()
        ),
    )


def _direct_decision_with_aggregate_evidence(
    signal_input: contract.TwoAreaConflictSignalInput,
    left: contract.AreaApplicabilityFinding,
    right: contract.AreaApplicabilityFinding,
    binding: aggregate_binding.AggregateVisibilityBindingV1,
) -> tuple[contract.MaskedSupplementComparison, str]:
    applicable = tuple(item for item in (left, right) if item.status == "APPLICABLE")
    present_count = sum(item.status != "ABSENT_VALID" for item in (left, right))
    if len(applicable) != 2:
        comparison = contract.MaskedSupplementComparison.build(
            signal_input, left, right, "NOT_PERFORMED", ()
        )
    else:
        different = []
        for position in probe_contract.MASKED_POSITIONS:
            relation = aggregate_binding.aggregate_digests_equivalent(
                binding.a_evidence.ordered_aggregate_code_digests[position],
                binding.b_evidence.ordered_aggregate_code_digests[position],
            )
            if relation == aggregate_binding.aggregate.DIFFERENT_RECEPTOR_AGGREGATE:
                different.append(position)
        comparison = contract.MaskedSupplementComparison.build(
            signal_input,
            left,
            right,
            "DIFFERENT" if different else "EQUAL",
            tuple(different),
        )
    if present_count == 0:
        status = "NO_CONTEXT"
    elif len(applicable) == 0:
        status = "NO_APPLICABLE_CONTEXT"
    elif len(applicable) == 1:
        status = "SINGLE_SOURCE"
    else:
        status = "CONSISTENT" if comparison.comparison_status == "EQUAL" else "CONFLICT"
    return comparison, status


def form_direct_two_area_conflict_baseline_with_aggregate_evidence(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_input: contract.TwoAreaConflictSignalInput,
    owner: contract.TwoAreaConflictSignalOwner,
    binding: aggregate_binding.AggregateVisibilityBindingV1,
) -> contract.TwoAreaConflictSignalCommit:
    """Apply the same aggregate rule through an independent direct path."""

    if type(owner) is not contract.TwoAreaConflictSignalOwner or owner.state != "READY":
        contract.fail("S2HZ-E008", "O1")
    try:
        before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        contract.validate_sources(signal_input, owner, probe, bundle, "DIRECT_BASELINE")
        aggregate_binding.validate_aggregate_visibility_binding(
            binding, probe, bundle, signal_input
        )
        left = _direct_area_aggregate_projection(
            "A_RECENT", probe, bundle, signal_input, binding
        )
        right = _direct_area_aggregate_projection(
            "B_STABLE", probe, bundle, signal_input, binding
        )
        comparison, status = _direct_decision_with_aggregate_evidence(
            signal_input, left, right, binding
        )
        present_count = sum(item.status != "ABSENT_VALID" for item in (left, right))
        applicable_count = sum(item.status == "APPLICABLE" for item in (left, right))
        ledger = contract.TwoAreaConflictSignalLedger.build(present_count, applicable_count)
        contract.require(
            before == (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest),
            "S2HZ-E006",
            "O5",
        )
        result = contract.build_result(signal_input, left, right, comparison, ledger, status)
        return contract.publish_success(owner, signal_input, left, right, comparison, ledger, result)
    except contract.S2ICSignalFailure:
        raise
    except (contract.S2ICContractError, aggregate_binding.S2JDBindingError) as error:
        mapped = error if isinstance(error, contract.S2ICContractError) else contract.S2ICContractError("S2HZ-E005", "O1")
        contract.publish_failure(owner, signal_input, mapped)
    except Exception as error:
        contract.publish_failure(owner, signal_input, contract.S2ICContractError("S2HZ-E001", "O1"))
        raise AssertionError("unreachable") from error
