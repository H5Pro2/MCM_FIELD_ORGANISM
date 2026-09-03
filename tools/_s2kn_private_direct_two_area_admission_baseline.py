"""Independent direct-table baseline for private S2-KN admission."""

from __future__ import annotations

import hashlib
import json

from tools import _s2kj_two_area_perceptual_context_336 as context_contract
from tools import _s2kj_validated_perceptual_finding_336 as finding_contract
from tools import _s2kn_private_two_area_context_admission_336 as admission_types


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise admission_types.S2KNAdmissionError("S2KN_BASELINE_INVALID", message)


def _validate_sources(
    context: object,
    probe: object,
) -> tuple[
    context_contract.TwoAreaPerceptualContext336,
    admission_types.MaskedAdmissionProbe336V1,
]:
    try:
        context = context_contract._validate_context(context)
        _check(
            type(probe) is admission_types.MaskedAdmissionProbe336V1
            and probe.schema == admission_types.S2KN_SCHEMA
            and probe.visible_positions == admission_types.VISIBLE_POSITIONS
            and probe.masked_positions == admission_types.MASKED_POSITIONS
            and probe.mask_plan_digest == admission_types.MASK_PLAN_DIGEST
            and len(probe.values) == 288
            and all(
                type(probe.values[index]) in (int, float)
                for index in admission_types.VISIBLE_POSITIONS
            )
            and all(probe.values[index] is None for index in admission_types.MASKED_POSITIONS)
            and probe.probe_digest == _digest(probe.payload_without_digest())
            and probe.config_digest == context.config_digest
            and probe.probe_digest != context.probe_digest,
            "probe relation differs",
        )
        roles = (
            context.a_recent.b4_recent,
            context.a_recent.tspm_fast,
            context.b_stable.auditory,
            context.b_stable.visual,
        )
        for finding, role in zip(roles, finding_contract.ROLE_ORDER, strict=True):
            finding_contract._validate_role_finding(finding, role)
            _check(
                finding.observed_state_digest == context.composite_state_digest
                and finding.probe_digest == context.probe_digest,
                "finding is foreign",
            )
            if finding.candidate is not None:
                _check(
                    finding.candidate.observed_state_digest == context.composite_state_digest
                    and finding.candidate.probe_digest == context.probe_digest
                    and finding.candidate.source_digest == context.source_digest,
                    "candidate is foreign",
                )
    except admission_types.S2KNAdmissionError:
        raise
    except Exception as exc:
        raise admission_types.S2KNAdmissionError(
            "S2KN_BASELINE_INVALID", "source validation failed"
        ) from exc
    return context, probe


def _visual_values(finding: finding_contract.RoleFinding336V1) -> tuple[tuple[float, ...], str]:
    candidate = finding.candidate
    _check(candidate is not None, "candidate is missing")
    if type(candidate) is finding_contract.AVContextCandidate336V1:
        return candidate.visual_values, candidate.visual_values_digest
    _check(
        type(candidate) is finding_contract.StableModalityCandidate336V1,
        "candidate type differs",
    )
    return candidate.values, candidate.values_digest


def _assess(
    finding: finding_contract.RoleFinding336V1,
    probe: admission_types.MaskedAdmissionProbe336V1,
) -> admission_types.InternalVisualApplicability336V1:
    if finding.status == "ABSENT_VALID":
        values = {
            "role": finding.role,
            "status": "ABSENT_VALID",
            "role_finding_digest": finding.finding_digest,
            "candidate_digest": None,
            "values_digest": None,
            "visible_mismatch_positions": [],
            "masked_values": [],
        }
        return admission_types.InternalVisualApplicability336V1(
            finding.role,
            "ABSENT_VALID",
            finding.finding_digest,
            None,
            None,
            (),
            (),
            _digest(values),
        )
    candidate_values, values_digest = _visual_values(finding)
    mismatches = tuple(
        index
        for index in admission_types.VISIBLE_POSITIONS
        if candidate_values[index] != float(probe.values[index])
    )
    status = "VISIBLE_CONFLICT" if mismatches else "APPLICABLE"
    masked = (
        ()
        if mismatches
        else tuple(candidate_values[index] for index in admission_types.MASKED_POSITIONS)
    )
    values = {
        "role": finding.role,
        "status": status,
        "role_finding_digest": finding.finding_digest,
        "candidate_digest": finding.candidate.candidate_digest,
        "values_digest": values_digest,
        "visible_mismatch_positions": list(mismatches),
        "masked_values": list(masked),
    }
    return admission_types.InternalVisualApplicability336V1(
        finding.role,
        status,
        finding.finding_digest,
        finding.candidate.candidate_digest,
        values_digest,
        mismatches,
        masked,
        _digest(values),
    )


def _area_a(
    b4: admission_types.InternalVisualApplicability336V1,
    fast: admission_types.InternalVisualApplicability336V1,
) -> admission_types.ARecentApplicability336V1:
    applicable = tuple(item for item in (b4, fast) if item.status == "APPLICABLE")
    if len(applicable) == 2:
        equal = b4.values_digest == fast.values_digest and b4.masked_values == fast.masked_values
        status = "A_RECENT_APPLICABLE" if equal else "A_RECENT_INTERNAL_CONFLICT"
        selected = applicable if equal else ()
    elif len(applicable) == 1:
        status = "A_RECENT_APPLICABLE"
        selected = applicable
    elif b4.status == fast.status == "ABSENT_VALID":
        status = "A_RECENT_ABSENT_VALID"
        selected = ()
    else:
        status = "A_RECENT_NOT_APPLICABLE"
        selected = ()
    payload = {
        "area": "A_RECENT",
        "status": status,
        "b4_applicability_digest": b4.applicability_digest,
        "fast_applicability_digest": fast.applicability_digest,
        "provenance_finding_digests": [item.role_finding_digest for item in selected],
        "provenance_candidate_digests": [item.candidate_digest for item in selected],
        "values_digest": selected[0].values_digest if selected else None,
        "masked_values": list(selected[0].masked_values if selected else ()),
        "public_candidate_count": 1 if selected else 0,
    }
    return admission_types.ARecentApplicability336V1(
        "A_RECENT",
        status,
        b4.applicability_digest,
        fast.applicability_digest,
        tuple(payload["provenance_finding_digests"]),
        tuple(payload["provenance_candidate_digests"]),
        payload["values_digest"],
        selected[0].masked_values if selected else (),
        payload["public_candidate_count"],
        _digest(payload),
    )


def _area_b(
    auditory: finding_contract.RoleFinding336V1,
    visual: admission_types.InternalVisualApplicability336V1,
) -> admission_types.BStableApplicability336V1:
    status = {
        "ABSENT_VALID": "B_STABLE_ABSENT_VALID",
        "APPLICABLE": "B_STABLE_APPLICABLE",
        "VISIBLE_CONFLICT": "B_STABLE_NOT_APPLICABLE",
    }[visual.status]
    applicable = visual.status == "APPLICABLE"
    payload = {
        "area": "B_STABLE",
        "status": status,
        "auditory_finding_digest": auditory.finding_digest,
        "visual_applicability_digest": visual.applicability_digest,
        "provenance_finding_digest": visual.role_finding_digest if applicable else None,
        "provenance_candidate_digest": visual.candidate_digest if applicable else None,
        "values_digest": visual.values_digest if applicable else None,
        "masked_values": list(visual.masked_values if applicable else ()),
        "public_candidate_count": 1 if applicable else 0,
    }
    return admission_types.BStableApplicability336V1(
        "B_STABLE",
        status,
        auditory.finding_digest,
        visual.applicability_digest,
        payload["provenance_finding_digest"],
        payload["provenance_candidate_digest"],
        payload["values_digest"],
        visual.masked_values if applicable else (),
        payload["public_candidate_count"],
        _digest(payload),
    )


def _make_hypothesis(
    area: str,
    a_recent: admission_types.ARecentApplicability336V1,
    b_stable: admission_types.BStableApplicability336V1,
    probe: admission_types.MaskedAdmissionProbe336V1,
    context_bundle_digest: str,
) -> admission_types.ContextHypothesis336V1:
    if area == "A_RECENT":
        findings = a_recent.provenance_finding_digests
        candidates = a_recent.provenance_candidate_digests
        values_digest = a_recent.values_digest
        values = a_recent.masked_values
    else:
        findings = (b_stable.provenance_finding_digest,)
        candidates = (b_stable.provenance_candidate_digest,)
        values_digest = b_stable.values_digest
        values = b_stable.masked_values
    _check(
        area in admission_types.PUBLIC_AREAS
        and all(admission_types._valid_digest(item) for item in findings)
        and all(admission_types._valid_digest(item) for item in candidates)
        and admission_types._valid_digest(values_digest)
        and len(values) == admission_types.MAX_HYPOTHESIS_VALUES,
        "hypothesis source differs",
    )
    payload = {
        "area": area,
        "provenance_finding_digests": list(findings),
        "provenance_candidate_digests": list(candidates),
        "candidate_values_digest": values_digest,
        "masked_positions": list(admission_types.MASKED_POSITIONS),
        "proposed_values": list(values),
        "mask_plan_digest": probe.mask_plan_digest,
        "probe_digest": probe.probe_digest,
        "context_bundle_digest": context_bundle_digest,
        "observed_value_count": 0,
        "field_contact_count": 0,
    }
    return admission_types.ContextHypothesis336V1(
        area,
        findings,
        candidates,
        values_digest,
        admission_types.MASKED_POSITIONS,
        values,
        probe.mask_plan_digest,
        probe.probe_digest,
        context_bundle_digest,
        0,
        0,
        _digest(payload),
    )


def _make_ledger(
    public_candidate_count: int,
    referenced_value_count: int,
    visible_comparison_count: int,
    equality_comparison_count: int,
    hypothesis_value_count: int,
    output_size: int,
) -> admission_types.AdmissionResourceLedger336V1:
    payload = {
        "validated_probe_count": 1,
        "validated_context_count": 1,
        "internal_visual_check_count": 3,
        "public_area_finding_count": 2,
        "public_candidate_count": public_candidate_count,
        "referenced_context_value_count": referenced_value_count,
        "visible_comparison_count": visible_comparison_count,
        "internal_equality_comparison_count": equality_comparison_count,
        "total_value_comparison_count": visible_comparison_count + equality_comparison_count,
        "hypothesis_value_count": hypothesis_value_count,
        "logical_operation_count": admission_types.MAX_LOGICAL_OPERATIONS,
        "memory_receptor_consumer_or_field_call_count": 0,
        "serialized_output_bytes": output_size,
    }
    return admission_types.AdmissionResourceLedger336V1(*payload.values(), _digest(payload))


def _assemble(
    context: context_contract.TwoAreaPerceptualContext336,
    probe: admission_types.MaskedAdmissionProbe336V1,
    a_recent: admission_types.ARecentApplicability336V1,
    b_stable: admission_types.BStableApplicability336V1,
    internal: tuple[admission_types.InternalVisualApplicability336V1, ...],
    decision: str,
    admitted_area: str | None,
) -> admission_types.ControlledContextAdmission336V1:
    hypothesis = (
        _make_hypothesis(admitted_area, a_recent, b_stable, probe, context.bundle_digest)
        if admitted_area is not None
        else None
    )
    visible_comparisons = 32 * sum(item.status != "ABSENT_VALID" for item in internal)
    equality_comparisons = (
        288 if internal[0].status == internal[1].status == "APPLICABLE" else 0
    )
    output_size = 0
    for _ in range(8):
        ledger = _make_ledger(
            a_recent.public_candidate_count + b_stable.public_candidate_count,
            context.resource_ledger.referenced_value_count,
            visible_comparisons,
            equality_comparisons,
            len(hypothesis.proposed_values) if hypothesis else 0,
            output_size,
        )
        payload = {
            "schema": admission_types.S2KN_SCHEMA,
            "function_role": "DIRECT_TWO_AREA_BASELINE",
            "contract_digest": admission_types.S2KM_CONTRACT_DIGEST,
            "context_bundle_digest": context.bundle_digest,
            "context_source_digest": context.source_digest,
            "masked_probe_digest": probe.probe_digest,
            "masked_probe_source_digest": probe.source_digest,
            "mask_plan_digest": probe.mask_plan_digest,
            "config_digest": context.config_digest,
            "composite_state_digest": context.composite_state_digest,
            "a_recent_digest": a_recent.area_finding_digest,
            "b_stable_digest": b_stable.area_finding_digest,
            "public_candidate_count": a_recent.public_candidate_count
            + b_stable.public_candidate_count,
            "decision": decision,
            "hypothesis_digest": hypothesis.hypothesis_digest if hypothesis else None,
            "resource_ledger_digest": ledger.ledger_digest,
            "prestate_digest": context.composite_state_digest,
            "poststate_digest": context.composite_state_digest,
            "replacement_perception": None,
            "ranking": None,
        }
        result = admission_types.ControlledContextAdmission336V1(
            "DIRECT_TWO_AREA_BASELINE",
            admission_types.S2KM_CONTRACT_DIGEST,
            context.bundle_digest,
            context.source_digest,
            probe.probe_digest,
            probe.source_digest,
            probe.mask_plan_digest,
            context.config_digest,
            context.composite_state_digest,
            a_recent,
            b_stable,
            payload["public_candidate_count"],
            decision,
            hypothesis,
            ledger,
            context.composite_state_digest,
            context.composite_state_digest,
            None,
            None,
            _digest(payload),
        )
        next_size = len(admission_types.canonical_bytes(result.canonical_payload()))
        if next_size == output_size:
            _check(next_size <= admission_types.MAX_OUTPUT_BYTES, "output is too large")
            return result
        output_size = next_size
    raise admission_types.S2KNAdmissionError(
        "S2KN_BASELINE_INVALID", "output size did not stabilize"
    )


def form_direct_two_area_admission_baseline_336(
    context: context_contract.TwoAreaPerceptualContext336,
    probe: admission_types.MaskedAdmissionProbe336V1,
) -> admission_types.ControlledContextAdmission336V1:
    """Recompute the S2-KM table without calling the admission implementation."""

    context, probe = _validate_sources(context, probe)
    before = (context.bundle_digest, context.composite_state_digest, probe.probe_digest)
    internal = (
        _assess(context.a_recent.b4_recent, probe),
        _assess(context.a_recent.tspm_fast, probe),
        _assess(context.b_stable.visual, probe),
    )
    a_recent = _area_a(internal[0], internal[1])
    b_stable = _area_b(context.b_stable.auditory, internal[2])
    if a_recent.status == "A_RECENT_INTERNAL_CONFLICT":
        decision, area = "ABSTAIN_A_RECENT_INTERNAL_CONFLICT", None
    else:
        count = a_recent.public_candidate_count + b_stable.public_candidate_count
        if count == 1:
            decision = "ADMIT_SINGLE_CONTEXT"
            area = "A_RECENT" if a_recent.public_candidate_count else "B_STABLE"
        elif count == 2:
            decision, area = "ABSTAIN_AMBIGUOUS_CONTEXT", None
        elif (
            a_recent.status == "A_RECENT_ABSENT_VALID"
            and b_stable.status == "B_STABLE_ABSENT_VALID"
        ):
            decision, area = "ABSTAIN_NO_CONTEXT", None
        else:
            decision, area = "ABSTAIN_NO_APPLICABLE_CONTEXT", None
    result = _assemble(context, probe, a_recent, b_stable, internal, decision, area)
    _check(
        before == (context.bundle_digest, context.composite_state_digest, probe.probe_digest),
        "baseline changed an input",
    )
    return result


__all__: tuple[str, ...] = ()
