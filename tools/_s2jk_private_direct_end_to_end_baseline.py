"""Independent direct-table and direct-fill baseline for S2-JI."""

from __future__ import annotations

from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2jh_private_controlled_context_admission as admission_contract
from tools import _s2jk_private_end_to_end_context_use as context_use


_DIRECT_TABLE = {
    "SINGLE_SOURCE": "ADMITTED_SINGLE_SOURCE_COMPLETED",
    "CONSISTENT": "ADMITTED_EQUIVALENT_CONTEXT_COMPLETED",
    "CONFLICT": "CONTEXT_WITHHELD",
    "NO_CONTEXT": "CONTEXT_WITHHELD",
    "NO_APPLICABLE_CONTEXT": "CONTEXT_WITHHELD",
}


def _direct_single_source_values(
    result: admission_contract.ControlledPerceptualContextAdmission,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
) -> tuple[float, ...]:
    finding = a_finding if result.admitted_role == "A_RECENT" else b_finding
    context_use._require(
        finding.area == result.admitted_role
        and finding.status == "APPLICABLE"
        and finding.masked_values_digest == result.common_supplement_digest,
        "S2JK-E004",
        "direct single-source finding differs",
    )
    binding = admission_contract.digest(
        {
            "schema": admission_contract.S2JH_SCHEMA,
            "binding_kind": "UNIQUE_APPLICABLE_CONTEXT",
            "area": finding.area,
            "finding_digest": finding.finding_digest,
            "candidate_digest": finding.candidate_digest,
            "masked_values_digest": finding.masked_values_digest,
        }
    )
    context_use._require(result.admitted_context_binding_digest == binding, "S2JK-E002", "direct single-source binding differs")
    return finding.masked_values


def _direct_consistent_values(
    result: admission_contract.ControlledPerceptualContextAdmission,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
) -> tuple[float, ...]:
    context_use._require(
        a_finding.status == b_finding.status == "APPLICABLE"
        and a_finding.masked_values == b_finding.masked_values
        and a_finding.masked_values_digest == b_finding.masked_values_digest == result.common_supplement_digest,
        "S2JK-E004",
        "direct equivalent supplement differs",
    )
    role_set_digest = admission_contract.digest(
        {
            "schema": admission_contract.S2JH_SCHEMA,
            "binding_kind": "UNORDERED_EQUIVALENT_ROLE_SET",
            "role_finding_pairs": sorted(
                (
                    (a_finding.area, a_finding.finding_digest),
                    (b_finding.area, b_finding.finding_digest),
                )
            ),
        }
    )
    binding = admission_contract.digest(
        {
            "schema": admission_contract.S2JH_SCHEMA,
            "binding_kind": "UNORDERED_EQUIVALENT_CONTEXTS",
            "equivalent_role_set_digest": role_set_digest,
            "common_masked_values_digest": result.common_supplement_digest,
        }
    )
    context_use._require(
        result.equivalent_role_set_digest == role_set_digest
        and result.admitted_context_binding_digest == binding,
        "S2JK-E002",
        "direct equivalent binding differs",
    )
    return tuple(a_finding.masked_values)


def _direct_fill(
    probe: probe_contract.MaskedVisualProbe,
    masked_values: tuple[float, ...],
) -> tuple[float | None, ...]:
    context_use._require(type(masked_values) is tuple and len(masked_values) == 9, "S2JK-E004", "direct supplement dimension differs")
    output = list(probe.values)
    for position, value in zip(probe_contract.MASKED_POSITIONS, masked_values, strict=True):
        context_use._require(type(value) is float and 0.0 <= value <= 1.0, "S2JK-E004", "direct supplement value differs")
        output[position] = value
    return tuple(output)


def compose_direct_admission_and_fill(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    admission_commit: admission_contract.ControlledContextAdmissionCommit,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
) -> context_use.EndToEndContextUseResult:
    """Apply a literal status table and an independent direct mask fill."""

    before = (
        probe.probe_digest,
        bundle.bundle_digest,
        bundle.prestate_digest,
        bundle.poststate_digest,
        signal_commit.result.result_digest,
        admission_commit.result.result_digest,
        a_finding.finding_digest,
        b_finding.finding_digest,
    )
    result = context_use._validate_evidence(
        probe,
        bundle,
        signal_commit,
        admission_commit,
        a_finding,
        b_finding,
    )
    context_use._require(result.source_signal_status in _DIRECT_TABLE, "S2JK-E003", "direct table status differs")
    completion_status = _DIRECT_TABLE[result.source_signal_status]
    if result.source_signal_status == "SINGLE_SOURCE":
        masked_values = _direct_single_source_values(result, a_finding, b_finding)
        output_values = _direct_fill(probe, masked_values)
        source_count = 1
    elif result.source_signal_status == "CONSISTENT":
        masked_values = _direct_consistent_values(result, a_finding, b_finding)
        output_values = _direct_fill(probe, masked_values)
        source_count = 2
    else:
        context_use._require(result.decision == "PROCEED_WITHOUT_CONTEXT", "S2JK-E003", "direct withheld decision differs")
        output_values = probe.values
        source_count = 0
    after = (
        probe.probe_digest,
        bundle.bundle_digest,
        bundle.prestate_digest,
        bundle.poststate_digest,
        signal_commit.result.result_digest,
        admission_commit.result.result_digest,
        a_finding.finding_digest,
        b_finding.finding_digest,
    )
    context_use._require(before == after, "S2JK-E005", "direct input evidence changed")
    completed = completion_status != "CONTEXT_WITHHELD"
    ledger = context_use.EndToEndContextUseLedger.build(source_count, completed)
    payload = {
        "schema": context_use.S2JK_SCHEMA,
        "function_role": "DIRECT_COMPOSITION_BASELINE",
        "source_signal_status": result.source_signal_status,
        "admission_decision": result.decision,
        "completion_status": completion_status,
        "admitted_role": result.admitted_role,
        "equivalent_role_set_digest": result.equivalent_role_set_digest,
        "common_supplement_digest": result.common_supplement_digest,
        "probe_digest": probe.probe_digest,
        "bundle_digest": bundle.bundle_digest,
        "signal_result_digest": signal_commit.result.result_digest,
        "admission_result_digest": result.result_digest,
        "current_only_values": list(probe.values),
        "output_values": list(output_values),
        "completed_positions": list(probe_contract.MASKED_POSITIONS if completed else ()),
        "prestate_digest": bundle.prestate_digest,
        "poststate_digest": bundle.poststate_digest,
        "resource_ledger_digest": ledger.ledger_digest,
        "selected_area": None,
        "ranking": None,
        "merged_context_digest": None,
    }
    return context_use.EndToEndContextUseResult(
        "DIRECT_COMPOSITION_BASELINE",
        result.source_signal_status,
        result.decision,
        completion_status,
        result.admitted_role,
        result.equivalent_role_set_digest,
        result.common_supplement_digest,
        probe.probe_digest,
        bundle.bundle_digest,
        signal_commit.result.result_digest,
        result.result_digest,
        probe.values,
        output_values,
        probe_contract.MASKED_POSITIONS if completed else (),
        bundle.prestate_digest,
        bundle.poststate_digest,
        ledger,
        None,
        None,
        None,
        context_use._digest(payload),
    )


__all__: tuple[str, ...] = ()
