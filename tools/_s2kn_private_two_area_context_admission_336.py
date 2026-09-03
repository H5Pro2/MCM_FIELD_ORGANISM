"""Private read-only two-area context admission for the 336-value profile."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from tools import _s2kj_two_area_perceptual_context_336 as context_contract
from tools import _s2kj_validated_perceptual_finding_336 as finding_contract


S2KN_SCHEMA = "s2kn.two-area-context-admission-336.v1"
S2KM_CONTRACT_DIGEST = (
    "48b63665e9ded7e9d8c0846c90081d7156487f2486ee54e3b035554d728e1d1e"
)
FUNCTION_ROLES = ("ADMISSION", "DIRECT_TWO_AREA_BASELINE")
INTERNAL_ROLES = ("B4_RECENT", "TSPM_FAST", "B_STABLE_VISUAL")
INTERNAL_STATUSES = ("ABSENT_VALID", "APPLICABLE", "VISIBLE_CONFLICT")
A_STATUSES = (
    "A_RECENT_ABSENT_VALID",
    "A_RECENT_APPLICABLE",
    "A_RECENT_INTERNAL_CONFLICT",
    "A_RECENT_NOT_APPLICABLE",
)
B_STATUSES = (
    "B_STABLE_ABSENT_VALID",
    "B_STABLE_APPLICABLE",
    "B_STABLE_NOT_APPLICABLE",
)
DECISIONS = (
    "ADMIT_SINGLE_CONTEXT",
    "ABSTAIN_A_RECENT_INTERNAL_CONFLICT",
    "ABSTAIN_NO_CONTEXT",
    "ABSTAIN_NO_APPLICABLE_CONTEXT",
    "ABSTAIN_AMBIGUOUS_CONTEXT",
)
PUBLIC_AREAS = ("A_RECENT", "B_STABLE")
VISIBLE_POSITIONS = tuple(range(32))
MASKED_POSITIONS = tuple(range(32, 288))
MASK_PLAN_DIGEST = hashlib.sha256(
    json.dumps(
        {
            "schema": S2KN_SCHEMA,
            "visible_positions": list(VISIBLE_POSITIONS),
            "masked_positions": list(MASKED_POSITIONS),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
).hexdigest()
MAX_OUTPUT_BYTES = 32_768
MAX_LOGICAL_OPERATIONS = 10
MAX_INTERNAL_VISUAL_CHECKS = 3
MAX_PUBLIC_CANDIDATES = 2
MAX_REFERENCED_CONTEXT_VALUES = 1_008
MAX_VISIBLE_COMPARISONS = 96
MAX_INTERNAL_EQUALITY_COMPARISONS = 288
MAX_TOTAL_VALUE_COMPARISONS = 384
MAX_HYPOTHESIS_VALUES = 256

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2KNAdmissionError(ValueError):
    """The admission cannot produce one complete valid result."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2KNAdmissionError(code, message)


def canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")


def digest(payload: object) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _numeric_values(values: object, length: int, label: str) -> tuple[float, ...]:
    _require(
        type(values) is tuple and len(values) == length,
        "S2KN_DIMENSION_INVALID",
        f"{label} dimension differs",
    )
    _require(
        all(type(value) in (int, float) for value in values),
        "S2KN_DIMENSION_INVALID",
        f"{label} contains a nonnumeric value",
    )
    normalized = tuple(float(value) for value in values)
    _require(
        all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in normalized),
        "S2KN_DIMENSION_INVALID",
        f"{label} differs from the receptor domain",
    )
    return normalized


@dataclass(frozen=True, slots=True)
class MaskedAdmissionProbe336V1:
    source_digest: str
    config_digest: str
    values: tuple[float | None, ...]
    visible_positions: tuple[int, ...]
    masked_positions: tuple[int, ...]
    mask_plan_digest: str
    probe_digest: str
    schema: str = S2KN_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "source_digest": self.source_digest,
            "config_digest": self.config_digest,
            "values": list(self.values),
            "visible_positions": list(self.visible_positions),
            "masked_positions": list(self.masked_positions),
            "mask_plan_digest": self.mask_plan_digest,
        }


@dataclass(frozen=True, slots=True)
class InternalVisualApplicability336V1:
    role: str
    status: str
    role_finding_digest: str
    candidate_digest: str | None
    values_digest: str | None
    visible_mismatch_positions: tuple[int, ...]
    masked_values: tuple[float, ...]
    applicability_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "role": self.role,
            "status": self.status,
            "role_finding_digest": self.role_finding_digest,
            "candidate_digest": self.candidate_digest,
            "values_digest": self.values_digest,
            "visible_mismatch_positions": list(self.visible_mismatch_positions),
            "masked_values": list(self.masked_values),
        }


@dataclass(frozen=True, slots=True)
class ARecentApplicability336V1:
    area: str
    status: str
    b4_applicability_digest: str
    fast_applicability_digest: str
    provenance_finding_digests: tuple[str, ...]
    provenance_candidate_digests: tuple[str, ...]
    values_digest: str | None
    masked_values: tuple[float, ...]
    public_candidate_count: int
    area_finding_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "area": self.area,
            "status": self.status,
            "b4_applicability_digest": self.b4_applicability_digest,
            "fast_applicability_digest": self.fast_applicability_digest,
            "provenance_finding_digests": list(self.provenance_finding_digests),
            "provenance_candidate_digests": list(self.provenance_candidate_digests),
            "values_digest": self.values_digest,
            "masked_values": list(self.masked_values),
            "public_candidate_count": self.public_candidate_count,
        }


@dataclass(frozen=True, slots=True)
class BStableApplicability336V1:
    area: str
    status: str
    auditory_finding_digest: str
    visual_applicability_digest: str
    provenance_finding_digest: str | None
    provenance_candidate_digest: str | None
    values_digest: str | None
    masked_values: tuple[float, ...]
    public_candidate_count: int
    area_finding_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "area": self.area,
            "status": self.status,
            "auditory_finding_digest": self.auditory_finding_digest,
            "visual_applicability_digest": self.visual_applicability_digest,
            "provenance_finding_digest": self.provenance_finding_digest,
            "provenance_candidate_digest": self.provenance_candidate_digest,
            "values_digest": self.values_digest,
            "masked_values": list(self.masked_values),
            "public_candidate_count": self.public_candidate_count,
        }


@dataclass(frozen=True, slots=True)
class ContextHypothesis336V1:
    area: str
    provenance_finding_digests: tuple[str, ...]
    provenance_candidate_digests: tuple[str, ...]
    candidate_values_digest: str
    masked_positions: tuple[int, ...]
    proposed_values: tuple[float, ...]
    mask_plan_digest: str
    probe_digest: str
    context_bundle_digest: str
    observed_value_count: int
    field_contact_count: int
    hypothesis_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "area": self.area,
            "provenance_finding_digests": list(self.provenance_finding_digests),
            "provenance_candidate_digests": list(self.provenance_candidate_digests),
            "candidate_values_digest": self.candidate_values_digest,
            "masked_positions": list(self.masked_positions),
            "proposed_values": list(self.proposed_values),
            "mask_plan_digest": self.mask_plan_digest,
            "probe_digest": self.probe_digest,
            "context_bundle_digest": self.context_bundle_digest,
            "observed_value_count": self.observed_value_count,
            "field_contact_count": self.field_contact_count,
        }


@dataclass(frozen=True, slots=True)
class AdmissionResourceLedger336V1:
    validated_probe_count: int
    validated_context_count: int
    internal_visual_check_count: int
    public_area_finding_count: int
    public_candidate_count: int
    referenced_context_value_count: int
    visible_comparison_count: int
    internal_equality_comparison_count: int
    total_value_comparison_count: int
    hypothesis_value_count: int
    logical_operation_count: int
    memory_receptor_consumer_or_field_call_count: int
    serialized_output_bytes: int
    ledger_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "ledger_digest"
        }


@dataclass(frozen=True, slots=True)
class ControlledContextAdmission336V1:
    function_role: str
    contract_digest: str
    context_bundle_digest: str
    context_source_digest: str
    masked_probe_digest: str
    masked_probe_source_digest: str
    mask_plan_digest: str
    config_digest: str
    composite_state_digest: str
    a_recent: ARecentApplicability336V1
    b_stable: BStableApplicability336V1
    public_candidate_count: int
    decision: str
    hypothesis: ContextHypothesis336V1 | None
    resource_ledger: AdmissionResourceLedger336V1
    prestate_digest: str
    poststate_digest: str
    replacement_perception: None
    ranking: None
    result_digest: str
    schema: str = S2KN_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "function_role": self.function_role,
            "contract_digest": self.contract_digest,
            "context_bundle_digest": self.context_bundle_digest,
            "context_source_digest": self.context_source_digest,
            "masked_probe_digest": self.masked_probe_digest,
            "masked_probe_source_digest": self.masked_probe_source_digest,
            "mask_plan_digest": self.mask_plan_digest,
            "config_digest": self.config_digest,
            "composite_state_digest": self.composite_state_digest,
            "a_recent_digest": self.a_recent.area_finding_digest,
            "b_stable_digest": self.b_stable.area_finding_digest,
            "public_candidate_count": self.public_candidate_count,
            "decision": self.decision,
            "hypothesis_digest": self.hypothesis.hypothesis_digest if self.hypothesis else None,
            "resource_ledger_digest": self.resource_ledger.ledger_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "replacement_perception": self.replacement_perception,
            "ranking": self.ranking,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "a_recent": {
                **self.a_recent.payload_without_digest(),
                "area_finding_digest": self.a_recent.area_finding_digest,
            },
            "b_stable": {
                **self.b_stable.payload_without_digest(),
                "area_finding_digest": self.b_stable.area_finding_digest,
            },
            "hypothesis": None
            if self.hypothesis is None
            else {
                **self.hypothesis.payload_without_digest(),
                "hypothesis_digest": self.hypothesis.hypothesis_digest,
            },
            "resource_ledger": {
                **self.resource_ledger.payload_without_digest(),
                "ledger_digest": self.resource_ledger.ledger_digest,
            },
            "result_digest": self.result_digest,
        }


def build_masked_admission_probe_336(
    *,
    source_digest: str,
    config_digest: str,
    values: tuple[float | None, ...],
) -> MaskedAdmissionProbe336V1:
    payload = {
        "schema": S2KN_SCHEMA,
        "source_digest": source_digest,
        "config_digest": config_digest,
        "values": list(values),
        "visible_positions": list(VISIBLE_POSITIONS),
        "masked_positions": list(MASKED_POSITIONS),
        "mask_plan_digest": MASK_PLAN_DIGEST,
    }
    return _validate_probe(
        MaskedAdmissionProbe336V1(
            source_digest,
            config_digest,
            values,
            VISIBLE_POSITIONS,
            MASKED_POSITIONS,
            MASK_PLAN_DIGEST,
            digest(payload),
        )
    )


def _validate_probe(value: object) -> MaskedAdmissionProbe336V1:
    _require(
        type(value) is MaskedAdmissionProbe336V1,
        "S2KN_TYPE_INVALID",
        "exact masked probe required",
    )
    assert isinstance(value, MaskedAdmissionProbe336V1)
    _require(
        value.schema == S2KN_SCHEMA
        and _valid_digest(value.source_digest)
        and _valid_digest(value.config_digest)
        and value.visible_positions == VISIBLE_POSITIONS
        and value.masked_positions == MASKED_POSITIONS
        and value.mask_plan_digest == MASK_PLAN_DIGEST
        and type(value.values) is tuple
        and len(value.values) == 288
        and all(
            type(value.values[index]) in (int, float)
            and math.isfinite(float(value.values[index]))
            and 0.0 <= float(value.values[index]) <= 1.0
            for index in VISIBLE_POSITIONS
        )
        and all(value.values[index] is None for index in MASKED_POSITIONS),
        "S2KN_PROBE_INVALID",
        "masked probe relation differs",
    )
    _require(
        value.probe_digest == digest(value.payload_without_digest()),
        "S2KN_DIGEST_INVALID",
        "masked probe digest differs",
    )
    return value


def _validate_context(
    value: object,
) -> context_contract.TwoAreaPerceptualContext336:
    try:
        result = context_contract._validate_context(value)
        roles = (
            result.a_recent.b4_recent,
            result.a_recent.tspm_fast,
            result.b_stable.auditory,
            result.b_stable.visual,
        )
        for finding, role in zip(roles, finding_contract.ROLE_ORDER, strict=True):
            finding_contract._validate_role_finding(finding, role)
            _require(
                finding.observed_state_digest == result.composite_state_digest
                and finding.probe_digest == result.probe_digest,
                "S2KN_CONTEXT_INVALID",
                "role finding is foreign to the context",
            )
            if finding.candidate is not None:
                _require(
                    finding.candidate.observed_state_digest == result.composite_state_digest
                    and finding.candidate.probe_digest == result.probe_digest
                    and finding.candidate.source_digest == result.source_digest,
                    "S2KN_CONTEXT_INVALID",
                    "candidate is foreign to the context",
                )
    except S2KNAdmissionError:
        raise
    except Exception as exc:
        raise S2KNAdmissionError("S2KN_CONTEXT_INVALID", "context validation failed") from exc
    return result


def _candidate_visual_values(
    finding: finding_contract.RoleFinding336V1,
) -> tuple[tuple[float, ...], str]:
    candidate = finding.candidate
    _require(candidate is not None, "S2KN_EVIDENCE_INVALID", "candidate is missing")
    if type(candidate) is finding_contract.AVContextCandidate336V1:
        return _numeric_values(candidate.visual_values, 288, finding.role), candidate.visual_values_digest
    _require(
        type(candidate) is finding_contract.StableModalityCandidate336V1
        and finding.role == "B_STABLE_VISUAL",
        "S2KN_EVIDENCE_INVALID",
        "visual candidate type differs",
    )
    return _numeric_values(candidate.values, 288, finding.role), candidate.values_digest


def _assess_visual_candidate(
    finding: finding_contract.RoleFinding336V1,
    probe: MaskedAdmissionProbe336V1,
) -> InternalVisualApplicability336V1:
    _require(finding.role in INTERNAL_ROLES, "S2KN_EVIDENCE_INVALID", "visual role differs")
    if finding.status == "ABSENT_VALID":
        payload = {
            "role": finding.role,
            "status": "ABSENT_VALID",
            "role_finding_digest": finding.finding_digest,
            "candidate_digest": None,
            "values_digest": None,
            "visible_mismatch_positions": [],
            "masked_values": [],
        }
        return InternalVisualApplicability336V1(
            finding.role,
            "ABSENT_VALID",
            finding.finding_digest,
            None,
            None,
            (),
            (),
            digest(payload),
        )
    values, values_digest = _candidate_visual_values(finding)
    mismatches = tuple(
        index
        for index in VISIBLE_POSITIONS
        if values[index] != float(probe.values[index])
    )
    status = "VISIBLE_CONFLICT" if mismatches else "APPLICABLE"
    masked = () if mismatches else tuple(values[index] for index in MASKED_POSITIONS)
    payload = {
        "role": finding.role,
        "status": status,
        "role_finding_digest": finding.finding_digest,
        "candidate_digest": finding.candidate.candidate_digest,
        "values_digest": values_digest,
        "visible_mismatch_positions": list(mismatches),
        "masked_values": list(masked),
    }
    return InternalVisualApplicability336V1(
        finding.role,
        status,
        finding.finding_digest,
        finding.candidate.candidate_digest,
        values_digest,
        mismatches,
        masked,
        digest(payload),
    )


def _validate_internal(value: InternalVisualApplicability336V1) -> None:
    _require(
        type(value) is InternalVisualApplicability336V1
        and value.role in INTERNAL_ROLES
        and value.status in INTERNAL_STATUSES
        and _valid_digest(value.role_finding_digest)
        and value.applicability_digest == digest(value.payload_without_digest()),
        "S2KN_EVIDENCE_INVALID",
        "internal applicability differs",
    )
    if value.status == "ABSENT_VALID":
        _require(
            value.candidate_digest is None
            and value.values_digest is None
            and value.visible_mismatch_positions == ()
            and value.masked_values == (),
            "S2KN_EVIDENCE_INVALID",
            "absence anatomy differs",
        )
    elif value.status == "APPLICABLE":
        _require(
            _valid_digest(value.candidate_digest)
            and _valid_digest(value.values_digest)
            and value.visible_mismatch_positions == ()
            and len(value.masked_values) == MAX_HYPOTHESIS_VALUES,
            "S2KN_EVIDENCE_INVALID",
            "applicable anatomy differs",
        )
    else:
        _require(
            _valid_digest(value.candidate_digest)
            and _valid_digest(value.values_digest)
            and 0 < len(value.visible_mismatch_positions) <= len(VISIBLE_POSITIONS)
            and value.masked_values == (),
            "S2KN_EVIDENCE_INVALID",
            "visible conflict anatomy differs",
        )


def project_a_recent_336(
    b4: InternalVisualApplicability336V1,
    fast: InternalVisualApplicability336V1,
) -> ARecentApplicability336V1:
    """Collapse two validated internal A roles into one public A finding."""

    _validate_internal(b4)
    _validate_internal(fast)
    _require(
        b4.role == "B4_RECENT" and fast.role == "TSPM_FAST",
        "S2KN_EVIDENCE_INVALID",
        "A role order differs",
    )
    applicable = tuple(item for item in (b4, fast) if item.status == "APPLICABLE")
    if len(applicable) == 2:
        equal = (
            b4.values_digest == fast.values_digest
            and b4.masked_values == fast.masked_values
        )
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
    values_digest = selected[0].values_digest if selected else None
    masked = selected[0].masked_values if selected else ()
    finding_digests = tuple(item.role_finding_digest for item in selected)
    candidate_digests = tuple(item.candidate_digest for item in selected)
    payload = {
        "area": "A_RECENT",
        "status": status,
        "b4_applicability_digest": b4.applicability_digest,
        "fast_applicability_digest": fast.applicability_digest,
        "provenance_finding_digests": list(finding_digests),
        "provenance_candidate_digests": list(candidate_digests),
        "values_digest": values_digest,
        "masked_values": list(masked),
        "public_candidate_count": 1 if selected else 0,
    }
    return ARecentApplicability336V1(
        "A_RECENT",
        status,
        b4.applicability_digest,
        fast.applicability_digest,
        finding_digests,
        candidate_digests,
        values_digest,
        masked,
        1 if selected else 0,
        digest(payload),
    )


def _project_b_stable(
    auditory: finding_contract.RoleFinding336V1,
    visual: InternalVisualApplicability336V1,
) -> BStableApplicability336V1:
    _validate_internal(visual)
    _require(visual.role == "B_STABLE_VISUAL", "S2KN_EVIDENCE_INVALID", "B role differs")
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
    return BStableApplicability336V1(
        "B_STABLE",
        status,
        auditory.finding_digest,
        visual.applicability_digest,
        visual.role_finding_digest if applicable else None,
        visual.candidate_digest if applicable else None,
        visual.values_digest if applicable else None,
        visual.masked_values if applicable else (),
        1 if applicable else 0,
        digest(payload),
    )


def _hypothesis(
    area: str,
    a_recent: ARecentApplicability336V1,
    b_stable: BStableApplicability336V1,
    probe: MaskedAdmissionProbe336V1,
    context_bundle_digest: str,
) -> ContextHypothesis336V1:
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
    _require(
        area in PUBLIC_AREAS
        and all(_valid_digest(item) for item in findings)
        and all(_valid_digest(item) for item in candidates)
        and _valid_digest(values_digest)
        and len(values) == MAX_HYPOTHESIS_VALUES,
        "S2KN_EVIDENCE_INVALID",
        "hypothesis source differs",
    )
    payload = {
        "area": area,
        "provenance_finding_digests": list(findings),
        "provenance_candidate_digests": list(candidates),
        "candidate_values_digest": values_digest,
        "masked_positions": list(MASKED_POSITIONS),
        "proposed_values": list(values),
        "mask_plan_digest": probe.mask_plan_digest,
        "probe_digest": probe.probe_digest,
        "context_bundle_digest": context_bundle_digest,
        "observed_value_count": 0,
        "field_contact_count": 0,
    }
    return ContextHypothesis336V1(
        area,
        findings,
        candidates,
        values_digest,
        MASKED_POSITIONS,
        values,
        probe.mask_plan_digest,
        probe.probe_digest,
        context_bundle_digest,
        0,
        0,
        digest(payload),
    )


def _decision(
    a_recent: ARecentApplicability336V1,
    b_stable: BStableApplicability336V1,
) -> tuple[str, str | None]:
    if a_recent.status == "A_RECENT_INTERNAL_CONFLICT":
        return "ABSTAIN_A_RECENT_INTERNAL_CONFLICT", None
    count = a_recent.public_candidate_count + b_stable.public_candidate_count
    if count == 1:
        return (
            "ADMIT_SINGLE_CONTEXT",
            "A_RECENT" if a_recent.public_candidate_count else "B_STABLE",
        )
    if count == 2:
        return "ABSTAIN_AMBIGUOUS_CONTEXT", None
    if (
        a_recent.status == "A_RECENT_ABSENT_VALID"
        and b_stable.status == "B_STABLE_ABSENT_VALID"
    ):
        return "ABSTAIN_NO_CONTEXT", None
    return "ABSTAIN_NO_APPLICABLE_CONTEXT", None


def _build_ledger(
    *,
    public_candidate_count: int,
    referenced_context_value_count: int,
    visible_comparison_count: int,
    internal_equality_comparison_count: int,
    hypothesis_value_count: int,
    serialized_output_bytes: int,
) -> AdmissionResourceLedger336V1:
    values = {
        "validated_probe_count": 1,
        "validated_context_count": 1,
        "internal_visual_check_count": 3,
        "public_area_finding_count": 2,
        "public_candidate_count": public_candidate_count,
        "referenced_context_value_count": referenced_context_value_count,
        "visible_comparison_count": visible_comparison_count,
        "internal_equality_comparison_count": internal_equality_comparison_count,
        "total_value_comparison_count": visible_comparison_count
        + internal_equality_comparison_count,
        "hypothesis_value_count": hypothesis_value_count,
        "logical_operation_count": MAX_LOGICAL_OPERATIONS,
        "memory_receptor_consumer_or_field_call_count": 0,
        "serialized_output_bytes": serialized_output_bytes,
    }
    return AdmissionResourceLedger336V1(*values.values(), digest(values))


def _validate_result(value: ControlledContextAdmission336V1) -> ControlledContextAdmission336V1:
    _require(type(value) is ControlledContextAdmission336V1, "S2KN_TYPE_INVALID", "exact result required")
    ledger = value.resource_ledger
    _require(
        value.schema == S2KN_SCHEMA
        and value.function_role in FUNCTION_ROLES
        and value.contract_digest == S2KM_CONTRACT_DIGEST
        and value.decision in DECISIONS
        and value.a_recent.area == "A_RECENT"
        and value.a_recent.status in A_STATUSES
        and value.b_stable.area == "B_STABLE"
        and value.b_stable.status in B_STATUSES
        and value.public_candidate_count
        == value.a_recent.public_candidate_count + value.b_stable.public_candidate_count
        <= MAX_PUBLIC_CANDIDATES
        and value.prestate_digest == value.composite_state_digest == value.poststate_digest
        and value.replacement_perception is None
        and value.ranking is None
        and value.a_recent.area_finding_digest == digest(value.a_recent.payload_without_digest())
        and value.b_stable.area_finding_digest == digest(value.b_stable.payload_without_digest())
        and ledger.ledger_digest == digest(ledger.payload_without_digest())
        and value.result_digest == digest(value.payload_without_digest()),
        "S2KN_RESULT_INVALID",
        "result binding differs",
    )
    _require(
        ledger.internal_visual_check_count <= MAX_INTERNAL_VISUAL_CHECKS
        and ledger.public_candidate_count <= MAX_PUBLIC_CANDIDATES
        and ledger.referenced_context_value_count <= MAX_REFERENCED_CONTEXT_VALUES
        and ledger.visible_comparison_count <= MAX_VISIBLE_COMPARISONS
        and ledger.internal_equality_comparison_count <= MAX_INTERNAL_EQUALITY_COMPARISONS
        and ledger.total_value_comparison_count <= MAX_TOTAL_VALUE_COMPARISONS
        and ledger.hypothesis_value_count <= MAX_HYPOTHESIS_VALUES
        and ledger.logical_operation_count == MAX_LOGICAL_OPERATIONS
        and ledger.memory_receptor_consumer_or_field_call_count == 0,
        "S2KN_RESOURCE_EXCEEDED",
        "resource ledger exceeds its bound",
    )
    if value.hypothesis is None:
        _require(
            value.decision != "ADMIT_SINGLE_CONTEXT" and ledger.hypothesis_value_count == 0,
            "S2KN_RESULT_INVALID",
            "missing hypothesis relation differs",
        )
    else:
        hypothesis = value.hypothesis
        _require(
            value.decision == "ADMIT_SINGLE_CONTEXT"
            and hypothesis.area in PUBLIC_AREAS
            and hypothesis.hypothesis_digest == digest(hypothesis.payload_without_digest())
            and hypothesis.observed_value_count == 0
            and hypothesis.field_contact_count == 0
            and len(hypothesis.proposed_values) == MAX_HYPOTHESIS_VALUES
            and ledger.hypothesis_value_count == MAX_HYPOTHESIS_VALUES,
            "S2KN_RESULT_INVALID",
            "hypothesis relation differs",
        )
    actual_size = len(canonical_bytes(value.canonical_payload()))
    _require(
        actual_size == ledger.serialized_output_bytes <= MAX_OUTPUT_BYTES,
        "S2KN_RESOURCE_EXCEEDED",
        "canonical output size differs",
    )
    return value


def _assemble_result(
    *,
    function_role: str,
    context: context_contract.TwoAreaPerceptualContext336,
    probe: MaskedAdmissionProbe336V1,
    a_recent: ARecentApplicability336V1,
    b_stable: BStableApplicability336V1,
    internal_findings: tuple[InternalVisualApplicability336V1, ...],
    decision: str,
    admitted_area: str | None,
) -> ControlledContextAdmission336V1:
    hypothesis = (
        _hypothesis(admitted_area, a_recent, b_stable, probe, context.bundle_digest)
        if admitted_area is not None
        else None
    )
    visible_comparisons = 32 * sum(
        item.status != "ABSENT_VALID" for item in internal_findings
    )
    equality_comparisons = (
        288
        if internal_findings[0].status == internal_findings[1].status == "APPLICABLE"
        else 0
    )
    size = 0
    for _ in range(8):
        ledger = _build_ledger(
            public_candidate_count=a_recent.public_candidate_count
            + b_stable.public_candidate_count,
            referenced_context_value_count=context.resource_ledger.referenced_value_count,
            visible_comparison_count=visible_comparisons,
            internal_equality_comparison_count=equality_comparisons,
            hypothesis_value_count=len(hypothesis.proposed_values) if hypothesis else 0,
            serialized_output_bytes=size,
        )
        payload = {
            "schema": S2KN_SCHEMA,
            "function_role": function_role,
            "contract_digest": S2KM_CONTRACT_DIGEST,
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
        result = ControlledContextAdmission336V1(
            function_role,
            S2KM_CONTRACT_DIGEST,
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
            digest(payload),
        )
        next_size = len(canonical_bytes(result.canonical_payload()))
        if next_size == size:
            return _validate_result(result)
        size = next_size
    raise S2KNAdmissionError("S2KN_RESOURCE_EXCEEDED", "output size did not stabilize")


def form_two_area_context_admission_336(
    context: context_contract.TwoAreaPerceptualContext336,
    probe: MaskedAdmissionProbe336V1,
) -> ControlledContextAdmission336V1:
    """Admit at most one public A/B context without changing any input."""

    context = _validate_context(context)
    probe = _validate_probe(probe)
    _require(
        probe.config_digest == context.config_digest
        and probe.probe_digest != context.probe_digest,
        "S2KN_SOURCE_INVALID",
        "masked probe binding differs",
    )
    before = (context.bundle_digest, context.composite_state_digest, probe.probe_digest)
    internal = (
        _assess_visual_candidate(context.a_recent.b4_recent, probe),
        _assess_visual_candidate(context.a_recent.tspm_fast, probe),
        _assess_visual_candidate(context.b_stable.visual, probe),
    )
    a_recent = project_a_recent_336(internal[0], internal[1])
    b_stable = _project_b_stable(context.b_stable.auditory, internal[2])
    decision, admitted_area = _decision(a_recent, b_stable)
    result = _assemble_result(
        function_role="ADMISSION",
        context=context,
        probe=probe,
        a_recent=a_recent,
        b_stable=b_stable,
        internal_findings=internal,
        decision=decision,
        admitted_area=admitted_area,
    )
    _require(
        before == (context.bundle_digest, context.composite_state_digest, probe.probe_digest),
        "S2KN_READ_ONLY_VIOLATION",
        "admission changed an input",
    )
    return result


__all__: tuple[str, ...] = ()
