"""Private read-only auditory partial-cue retrieval for the 336-value memory."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from tools import _s2jw_profiled_memory_coordinator as coordinator


S2KZ_SCHEMA = "s2kz.private.auditory-partial-cue-retrieval-336.v1"
S2KX_CONTRACT_SHA256 = "a7652d029e938fc09038285f63c1107603ced906638a60369dcb67ae9b33d2c0"
S2KY_RESULT_SHA256 = "87ac9aed39e6f3cd63f4d3cee24873a7e67357ce5cd9e5ed1ccc353d407d1dc3"
FUNCTION_ROLES = ("AUDITORY_PARTIAL_CUE_RETRIEVAL", "DIRECT_AUDITORY_SLOT_SCAN_BASELINE")
BANK_ROLES = ("B4_RECENT", "TSPM_FAST", "B_STABLE_AUDITORY")
BANK_CAPACITIES = (9, 3, 8)
BANK_STATUSES = (
    "BANK_ABSENT_VALID",
    "BANK_NO_OBSERVED_MATCH",
    "BANK_UNIQUE_OBSERVED_MATCH",
    "BANK_MULTIPLE_OBSERVED_MATCHES",
)
A_STATUSES = (
    "A_RECENT_ABSENT_VALID",
    "A_RECENT_APPLICABLE",
    "A_RECENT_INTERNAL_AMBIGUITY",
    "A_RECENT_INTERNAL_CONFLICT",
    "A_RECENT_NOT_APPLICABLE",
)
B_STATUSES = (
    "B_STABLE_AUDITORY_ABSENT_VALID",
    "B_STABLE_AUDITORY_APPLICABLE",
    "B_STABLE_AUDITORY_INTERNAL_AMBIGUITY",
    "B_STABLE_AUDITORY_NOT_APPLICABLE",
)
DECISIONS = (
    "ADMIT_SINGLE_CONTEXT",
    "ABSTAIN_INTERNAL_AMBIGUITY",
    "ABSTAIN_INTERNAL_CONFLICT",
    "ABSTAIN_AMBIGUOUS_CONTEXT",
    "ABSTAIN_NO_CONTEXT",
    "ABSTAIN_NO_APPLICABLE_CONTEXT",
)
PUBLIC_AREAS = ("A_RECENT", "B_STABLE_AUDITORY")
OBSERVED_BANDS = tuple(range(24))
MASKED_BANDS = tuple(range(24, 48))
MAX_SLOT_SCANS = 20
MAX_OBSERVED_COMPARISONS = 480
MAX_INTERNAL_EQUALITY_COMPARISONS = 48
MAX_TOTAL_VALUE_COMPARISONS = 528
MAX_HYPOTHESIS_VALUES = 24
MAX_LOGICAL_OPERATIONS = 14
MAX_OUTPUT_BYTES = 32_768

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9.-]{1,95}$")


class S2KZError(ValueError):
    """One fail-closed S2-KZ contract violation."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2KZError(code, message)


def canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def digest(payload: object) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _valid_identifier(value: object) -> bool:
    return type(value) is str and _IDENTIFIER.fullmatch(value) is not None


def _auditory_values(values: object, role: str) -> tuple[float, ...]:
    _require(
        type(values) is tuple and len(values) == 48,
        "S2KZ_DIMENSION_INVALID",
        f"{role} must contain exactly 48 values",
    )
    _require(
        all(type(item) in (int, float) for item in values),
        "S2KZ_DIMENSION_INVALID",
        f"{role} contains a nonnumeric value",
    )
    result = tuple(float(item) for item in values)
    _require(
        all(math.isfinite(item) and 0.0 <= item <= 1.0 for item in result),
        "S2KZ_DIMENSION_INVALID",
        f"{role} differs from the bound receptor domain",
    )
    return result


@dataclass(frozen=True, slots=True)
class AuditoryBandPlan48V1:
    observed_bands: tuple[int, ...]
    masked_bands: tuple[int, ...]
    observed_count: int
    masked_count: int
    plan_digest: str
    schema: str = S2KZ_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "observed_bands": list(self.observed_bands),
            "masked_bands": list(self.masked_bands),
            "observed_count": self.observed_count,
            "masked_count": self.masked_count,
        }


@dataclass(frozen=True, slots=True)
class MaskedAuditoryCue48V1:
    pcm_payload_digest: str
    receptor_state_digest: str
    receptor_values_digest: str
    observed_values_digest: str
    config_digest: str
    auditory_source_clock_id: str
    auditory_window_start_tick: int
    auditory_window_end_tick: int
    values: tuple[float | None, ...]
    band_plan_digest: str
    cue_digest: str
    schema: str = S2KZ_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "pcm_payload_digest": self.pcm_payload_digest,
            "receptor_state_digest": self.receptor_state_digest,
            "receptor_values_digest": self.receptor_values_digest,
            "observed_values_digest": self.observed_values_digest,
            "config_digest": self.config_digest,
            "auditory_source_clock_id": self.auditory_source_clock_id,
            "auditory_window_start_tick": self.auditory_window_start_tick,
            "auditory_window_end_tick": self.auditory_window_end_tick,
            "values": list(self.values),
            "band_plan_digest": self.band_plan_digest,
        }


@dataclass(frozen=True, slots=True)
class AuditorySlotScanRecordV1:
    bank_role: str
    slot_id: str
    slot_digest: str
    eligible: bool
    stable_support: int | None
    match_threshold: float
    observed_distance: float | None
    observed_match: bool
    observed_comparison_count: int
    distance_terms_digest: str | None
    candidate_values_digest: str | None
    record_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "record_digest"
        }


@dataclass(frozen=True, slots=True)
class AuditoryBankScanFindingV1:
    bank_role: str
    capacity: int
    records: tuple[AuditorySlotScanRecordV1, ...]
    eligible_count: int
    match_count: int
    matched_slot_digests: tuple[str, ...]
    status: str
    comparison_count: int
    scan_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "bank_role": self.bank_role,
            "capacity": self.capacity,
            "record_digests": [item.record_digest for item in self.records],
            "eligible_count": self.eligible_count,
            "match_count": self.match_count,
            "matched_slot_digests": list(self.matched_slot_digests),
            "status": self.status,
            "comparison_count": self.comparison_count,
        }


@dataclass(frozen=True, slots=True)
class AuditoryAreaFindingV1:
    area: str
    status: str
    parent_scan_digests: tuple[str, ...]
    provenance_slot_digests: tuple[str, ...]
    candidate_values_digest: str | None
    masked_values: tuple[float, ...]
    public_candidate_count: int
    finding_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "area": self.area,
            "status": self.status,
            "parent_scan_digests": list(self.parent_scan_digests),
            "provenance_slot_digests": list(self.provenance_slot_digests),
            "candidate_values_digest": self.candidate_values_digest,
            "masked_values": list(self.masked_values),
            "public_candidate_count": self.public_candidate_count,
        }


@dataclass(frozen=True, slots=True)
class AuditoryPartialCueHypothesis48V1:
    area: str
    provenance_slot_digests: tuple[str, ...]
    candidate_values_digest: str
    masked_bands: tuple[int, ...]
    proposed_values: tuple[float, ...]
    cue_digest: str
    band_plan_digest: str
    state_digest: str
    observed_value_count: int
    visual_value_count: int
    field_contact_count: int
    hypothesis_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: list(getattr(self, name))
            if name in {"provenance_slot_digests", "masked_bands", "proposed_values"}
            else getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "hypothesis_digest"
        }


@dataclass(frozen=True, slots=True)
class AuditoryPartialCueResourceLedgerV1:
    b4_slot_scan_count: int
    fast_slot_scan_count: int
    auditory_slow_slot_scan_count: int
    total_slot_scan_count: int
    observed_comparison_count: int
    internal_equality_comparison_count: int
    total_value_comparison_count: int
    hypothesis_value_count: int
    logical_operation_count: int
    memory_receptor_consumer_context_or_field_call_count: int
    serialized_output_bytes: int
    ledger_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "ledger_digest"
        }


@dataclass(frozen=True, slots=True)
class AuditoryPartialCueRetrievalResultV1:
    function_role: str
    source_digests: tuple[str, str]
    config_digest: str
    state_digest: str
    cue_digest: str
    band_plan_digest: str
    bank_scans: tuple[AuditoryBankScanFindingV1, ...]
    a_recent: AuditoryAreaFindingV1
    b_stable_auditory: AuditoryAreaFindingV1
    public_candidate_count: int
    decision: str
    hypothesis: AuditoryPartialCueHypothesis48V1 | None
    resource_ledger: AuditoryPartialCueResourceLedgerV1
    prestate_digest: str
    poststate_digest: str
    replacement_perception: None
    ranking: None
    result_digest: str
    schema: str = S2KZ_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "function_role": self.function_role,
            "source_digests": list(self.source_digests),
            "config_digest": self.config_digest,
            "state_digest": self.state_digest,
            "cue_digest": self.cue_digest,
            "band_plan_digest": self.band_plan_digest,
            "bank_scan_digests": [item.scan_digest for item in self.bank_scans],
            "a_recent_digest": self.a_recent.finding_digest,
            "b_stable_auditory_digest": self.b_stable_auditory.finding_digest,
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
            "bank_scans": [
                {
                    **scan.payload_without_digest(),
                    "records": [
                        {**record.payload_without_digest(), "record_digest": record.record_digest}
                        for record in scan.records
                    ],
                    "scan_digest": scan.scan_digest,
                }
                for scan in self.bank_scans
            ],
            "a_recent": {**self.a_recent.payload_without_digest(), "finding_digest": self.a_recent.finding_digest},
            "b_stable_auditory": {
                **self.b_stable_auditory.payload_without_digest(),
                "finding_digest": self.b_stable_auditory.finding_digest,
            },
            "hypothesis": None
            if self.hypothesis is None
            else {**self.hypothesis.payload_without_digest(), "hypothesis_digest": self.hypothesis.hypothesis_digest},
            "resource_ledger": {
                **self.resource_ledger.payload_without_digest(),
                "ledger_digest": self.resource_ledger.ledger_digest,
            },
            "result_digest": self.result_digest,
        }


@dataclass(frozen=True, slots=True)
class _Candidate:
    slot_digest: str
    values: tuple[float, ...]
    values_digest: str


def build_auditory_band_plan_48() -> AuditoryBandPlan48V1:
    payload = {
        "schema": S2KZ_SCHEMA,
        "observed_bands": list(OBSERVED_BANDS),
        "masked_bands": list(MASKED_BANDS),
        "observed_count": 24,
        "masked_count": 24,
    }
    return _validate_band_plan(
        AuditoryBandPlan48V1(OBSERVED_BANDS, MASKED_BANDS, 24, 24, digest(payload))
    )


def _validate_band_plan(value: object) -> AuditoryBandPlan48V1:
    _require(type(value) is AuditoryBandPlan48V1, "S2KZ_TYPE_INVALID", "exact band plan required")
    assert isinstance(value, AuditoryBandPlan48V1)
    _require(
        value.schema == S2KZ_SCHEMA
        and value.observed_bands == OBSERVED_BANDS
        and value.masked_bands == MASKED_BANDS
        and value.observed_count == value.masked_count == 24
        and set(value.observed_bands).isdisjoint(value.masked_bands)
        and tuple(sorted(value.observed_bands + value.masked_bands)) == tuple(range(48))
        and value.plan_digest == digest(value.payload_without_digest()),
        "S2KZ_BAND_PLAN_INVALID",
        "auditory band plan differs",
    )
    return value


def build_masked_auditory_cue_48(
    *,
    pcm_payload_digest: str,
    receptor_state_digest: str,
    receptor_values_digest: str,
    config_digest: str,
    auditory_source_clock_id: str,
    auditory_window_start_tick: int,
    auditory_window_end_tick: int,
    observed_values: tuple[float, ...],
    band_plan: AuditoryBandPlan48V1,
) -> MaskedAuditoryCue48V1:
    plan = _validate_band_plan(band_plan)
    _require(
        type(observed_values) is tuple and len(observed_values) == 24,
        "S2KZ_DIMENSION_INVALID",
        "cue must expose exactly 24 observed values",
    )
    values = tuple(observed_values) + (None,) * 24
    observed_digest = digest(list(observed_values))
    payload = {
        "schema": S2KZ_SCHEMA,
        "pcm_payload_digest": pcm_payload_digest,
        "receptor_state_digest": receptor_state_digest,
        "receptor_values_digest": receptor_values_digest,
        "observed_values_digest": observed_digest,
        "config_digest": config_digest,
        "auditory_source_clock_id": auditory_source_clock_id,
        "auditory_window_start_tick": auditory_window_start_tick,
        "auditory_window_end_tick": auditory_window_end_tick,
        "values": list(values),
        "band_plan_digest": plan.plan_digest,
    }
    return _validate_cue(
        MaskedAuditoryCue48V1(
            pcm_payload_digest,
            receptor_state_digest,
            receptor_values_digest,
            observed_digest,
            config_digest,
            auditory_source_clock_id,
            auditory_window_start_tick,
            auditory_window_end_tick,
            values,
            plan.plan_digest,
            digest(payload),
        ),
        plan,
    )


def _validate_cue(value: object, plan: AuditoryBandPlan48V1) -> MaskedAuditoryCue48V1:
    _require(type(value) is MaskedAuditoryCue48V1, "S2KZ_TYPE_INVALID", "exact cue required")
    assert isinstance(value, MaskedAuditoryCue48V1)
    _require(
        value.schema == S2KZ_SCHEMA
        and all(
            _valid_digest(item)
            for item in (
                value.pcm_payload_digest,
                value.receptor_state_digest,
                value.receptor_values_digest,
                value.observed_values_digest,
                value.config_digest,
                value.cue_digest,
            )
        )
        and _valid_identifier(value.auditory_source_clock_id)
        and type(value.auditory_window_start_tick) is int
        and type(value.auditory_window_end_tick) is int
        and 0 <= value.auditory_window_start_tick < value.auditory_window_end_tick
        and type(value.values) is tuple
        and len(value.values) == 48
        and value.band_plan_digest == plan.plan_digest
        and all(type(value.values[index]) in (int, float) for index in OBSERVED_BANDS)
        and all(
            math.isfinite(float(value.values[index]))
            and 0.0 <= float(value.values[index]) <= 1.0
            for index in OBSERVED_BANDS
        )
        and all(value.values[index] is None for index in MASKED_BANDS)
        and value.observed_values_digest
        == digest([float(value.values[index]) for index in OBSERVED_BANDS])
        and value.cue_digest == digest(value.payload_without_digest()),
        "S2KZ_SOURCE_INVALID",
        "cue source, values, time, band plan, or digest differs",
    )
    return value


def _state_and_cue(
    config: object,
    state: object,
    cue: object,
    band_plan: object,
) -> tuple[
    coordinator.S2JVCoordinatorConfigV1,
    coordinator.S2JVCompositeStateV1,
    MaskedAuditoryCue48V1,
    AuditoryBandPlan48V1,
]:
    try:
        bound_config = coordinator._validate_config(config)
        bound_state = coordinator._validate_state(bound_config, state)
    except Exception as exc:
        raise S2KZError("S2KZ_STATE_INVALID", "config or memory state is invalid") from exc
    plan = _validate_band_plan(band_plan)
    bound_cue = _validate_cue(cue, plan)
    _require(
        bound_cue.config_digest == bound_config.config_digest,
        "S2KZ_SOURCE_INVALID",
        "cue configuration differs",
    )
    fast = bound_state.tspm_state.fast_state
    if bound_state.generation > 0:
        _require(
            fast.auditory_source_clock_id == bound_cue.auditory_source_clock_id
            and fast.auditory_last_end_tick is not None
            and bound_cue.auditory_window_start_tick >= fast.auditory_last_end_tick
            and bound_cue.auditory_window_end_tick > fast.auditory_last_end_tick,
            "S2KZ_SOURCE_INVALID",
            "auditory cue is stale or belongs to another native audio clock",
        )
    return bound_config, bound_state, bound_cue, plan


def _slot_record(
    *,
    bank_role: str,
    slot_id: str,
    slot_digest: str,
    values: tuple[float, ...] | None,
    support: int | None,
    threshold: float,
    cue: MaskedAuditoryCue48V1,
) -> tuple[AuditorySlotScanRecordV1, _Candidate | None]:
    eligible = values is not None
    if eligible:
        terms = tuple(
            abs(values[index] - float(cue.values[index]))
            for index in OBSERVED_BANDS
        )
        observed_distance = sum(terms) / 24
        comparisons = len(terms)
        terms_digest = digest(list(terms))
        matched = observed_distance <= threshold
        values_digest = digest(list(values))
    else:
        observed_distance = None
        comparisons = 0
        terms_digest = None
        matched = False
        values_digest = None
    payload = {
        "bank_role": bank_role,
        "slot_id": slot_id,
        "slot_digest": slot_digest,
        "eligible": eligible,
        "stable_support": support,
        "match_threshold": threshold,
        "observed_distance": observed_distance,
        "observed_match": matched,
        "observed_comparison_count": comparisons,
        "distance_terms_digest": terms_digest,
        "candidate_values_digest": values_digest,
    }
    record = AuditorySlotScanRecordV1(
        bank_role,
        slot_id,
        slot_digest,
        eligible,
        support,
        threshold,
        observed_distance,
        matched,
        comparisons,
        terms_digest,
        values_digest,
        digest(payload),
    )
    candidate = _Candidate(slot_digest, values, values_digest) if matched else None  # type: ignore[arg-type]
    return record, candidate


def _finish_bank(
    bank_role: str,
    capacity: int,
    records: list[AuditorySlotScanRecordV1],
    matches: list[_Candidate],
) -> tuple[AuditoryBankScanFindingV1, tuple[_Candidate, ...]]:
    eligible = sum(item.eligible for item in records)
    if eligible == 0:
        status = "BANK_ABSENT_VALID"
    elif not matches:
        status = "BANK_NO_OBSERVED_MATCH"
    elif len(matches) == 1:
        status = "BANK_UNIQUE_OBSERVED_MATCH"
    else:
        status = "BANK_MULTIPLE_OBSERVED_MATCHES"
    ordered = tuple(sorted(matches, key=lambda item: item.slot_digest))
    payload = {
        "bank_role": bank_role,
        "capacity": capacity,
        "record_digests": [item.record_digest for item in records],
        "eligible_count": eligible,
        "match_count": len(ordered),
        "matched_slot_digests": [item.slot_digest for item in ordered],
        "status": status,
        "comparison_count": sum(item.observed_comparison_count for item in records),
    }
    return (
        AuditoryBankScanFindingV1(
            bank_role,
            capacity,
            tuple(records),
            eligible,
            len(ordered),
            tuple(item.slot_digest for item in ordered),
            status,
            payload["comparison_count"],  # type: ignore[arg-type]
            digest(payload),
        ),
        ordered,
    )


def _scan_b4(config, state, cue):
    records: list[AuditorySlotScanRecordV1] = []
    matches: list[_Candidate] = []
    threshold = config.tspm_config.fast_config.auditory_match_threshold
    for entry in state.b4_state.entries:
        values = _auditory_values(entry.values[:48], "B4 auditory values") if entry.occupied else None
        record, candidate = _slot_record(
            bank_role="B4_RECENT",
            slot_id=entry.slot_id,
            slot_digest=digest(comparison._canonical(entry)),
            values=values,
            support=None,
            threshold=threshold,
            cue=cue,
        )
        records.append(record)
        if candidate is not None:
            matches.append(candidate)
    return _finish_bank("B4_RECENT", 9, records, matches)


def _scan_fast(config, state, cue):
    records: list[AuditorySlotScanRecordV1] = []
    matches: list[_Candidate] = []
    threshold = config.tspm_config.fast_config.auditory_match_threshold
    for slot in state.tspm_state.fast_state.slots:
        values = _auditory_values(slot.auditory_values, "Fast auditory values") if slot.occupied else None
        record, candidate = _slot_record(
            bank_role="TSPM_FAST",
            slot_id=slot.slot_id,
            slot_digest=slot.digest(),
            values=values,
            support=slot.support_count if slot.occupied else None,
            threshold=threshold,
            cue=cue,
        )
        records.append(record)
        if candidate is not None:
            matches.append(candidate)
    return _finish_bank("TSPM_FAST", 3, records, matches)


def _scan_slow(config, state, cue):
    records: list[AuditorySlotScanRecordV1] = []
    matches: list[_Candidate] = []
    threshold = config.profile.profile.auditory_config.match_threshold
    for slot in state.tspm_state.auditory_ppb1_state.slots:
        stable = slot.occupied and slot.support_count is not None and slot.support_count >= 3
        values = _auditory_values(slot.prototype_values, "Slow auditory values") if stable else None
        record, candidate = _slot_record(
            bank_role="B_STABLE_AUDITORY",
            slot_id=slot.slot_id,
            slot_digest=digest(slot.canonical_payload()),
            values=values,
            support=slot.support_count if stable else None,
            threshold=threshold,
            cue=cue,
        )
        records.append(record)
        if candidate is not None:
            matches.append(candidate)
    return _finish_bank("B_STABLE_AUDITORY", 8, records, matches)


def _area_finding(
    area: str,
    status: str,
    parents: tuple[str, ...],
    selected: tuple[_Candidate, ...],
) -> AuditoryAreaFindingV1:
    value_digest = selected[0].values_digest if selected else None
    masked = tuple(selected[0].values[index] for index in MASKED_BANDS) if selected else ()
    payload = {
        "area": area,
        "status": status,
        "parent_scan_digests": list(parents),
        "provenance_slot_digests": [item.slot_digest for item in selected],
        "candidate_values_digest": value_digest,
        "masked_values": list(masked),
        "public_candidate_count": 1 if selected else 0,
    }
    return AuditoryAreaFindingV1(
        area,
        status,
        parents,
        tuple(item.slot_digest for item in selected),
        value_digest,
        masked,
        1 if selected else 0,
        digest(payload),
    )


def _resolve_a(b4_scan, b4_matches, fast_scan, fast_matches):
    parents = (b4_scan.scan_digest, fast_scan.scan_digest)
    if "BANK_MULTIPLE_OBSERVED_MATCHES" in (b4_scan.status, fast_scan.status):
        return _area_finding("A_RECENT", "A_RECENT_INTERNAL_AMBIGUITY", parents, ()), 0
    unique = tuple(
        matches[0]
        for scan, matches in ((b4_scan, b4_matches), (fast_scan, fast_matches))
        if scan.status == "BANK_UNIQUE_OBSERVED_MATCH"
    )
    if len(unique) == 2:
        same = unique[0].values_digest == unique[1].values_digest and unique[0].values == unique[1].values
        if same:
            return _area_finding("A_RECENT", "A_RECENT_APPLICABLE", parents, unique), 48
        return _area_finding("A_RECENT", "A_RECENT_INTERNAL_CONFLICT", parents, ()), 48
    if len(unique) == 1:
        return _area_finding("A_RECENT", "A_RECENT_APPLICABLE", parents, unique), 0
    if b4_scan.status == fast_scan.status == "BANK_ABSENT_VALID":
        return _area_finding("A_RECENT", "A_RECENT_ABSENT_VALID", parents, ()), 0
    return _area_finding("A_RECENT", "A_RECENT_NOT_APPLICABLE", parents, ()), 0


def _resolve_b(scan, matches):
    mapping = {
        "BANK_ABSENT_VALID": "B_STABLE_AUDITORY_ABSENT_VALID",
        "BANK_NO_OBSERVED_MATCH": "B_STABLE_AUDITORY_NOT_APPLICABLE",
        "BANK_UNIQUE_OBSERVED_MATCH": "B_STABLE_AUDITORY_APPLICABLE",
        "BANK_MULTIPLE_OBSERVED_MATCHES": "B_STABLE_AUDITORY_INTERNAL_AMBIGUITY",
    }
    return _area_finding(
        "B_STABLE_AUDITORY",
        mapping[scan.status],
        (scan.scan_digest,),
        matches if len(matches) == 1 else (),
    )


def _decide(a, b):
    if a.status == "A_RECENT_INTERNAL_AMBIGUITY" or b.status == "B_STABLE_AUDITORY_INTERNAL_AMBIGUITY":
        return "ABSTAIN_INTERNAL_AMBIGUITY", None
    if a.status == "A_RECENT_INTERNAL_CONFLICT":
        return "ABSTAIN_INTERNAL_CONFLICT", None
    count = a.public_candidate_count + b.public_candidate_count
    if count == 1:
        return "ADMIT_SINGLE_CONTEXT", "A_RECENT" if a.public_candidate_count else "B_STABLE_AUDITORY"
    if count == 2:
        return "ABSTAIN_AMBIGUOUS_CONTEXT", None
    if a.status == "A_RECENT_ABSENT_VALID" and b.status == "B_STABLE_AUDITORY_ABSENT_VALID":
        return "ABSTAIN_NO_CONTEXT", None
    return "ABSTAIN_NO_APPLICABLE_CONTEXT", None


def _hypothesis(area, a, b, cue, plan, state_digest):
    source = a if area == "A_RECENT" else b
    _require(
        source.public_candidate_count == 1
        and _valid_digest(source.candidate_values_digest)
        and len(source.masked_values) == 24,
        "S2KZ_EVIDENCE_INVALID",
        "hypothesis source differs",
    )
    payload = {
        "area": area,
        "provenance_slot_digests": list(source.provenance_slot_digests),
        "candidate_values_digest": source.candidate_values_digest,
        "masked_bands": list(plan.masked_bands),
        "proposed_values": list(source.masked_values),
        "cue_digest": cue.cue_digest,
        "band_plan_digest": plan.plan_digest,
        "state_digest": state_digest,
        "observed_value_count": 0,
        "visual_value_count": 0,
        "field_contact_count": 0,
    }
    return AuditoryPartialCueHypothesis48V1(
        area,
        source.provenance_slot_digests,
        source.candidate_values_digest,
        plan.masked_bands,
        source.masked_values,
        cue.cue_digest,
        plan.plan_digest,
        state_digest,
        0,
        0,
        0,
        digest(payload),
    )


def _ledger(scans, equality_count, hypothesis_count, output_size):
    comparisons = sum(scan.comparison_count for scan in scans)
    payload = {
        "b4_slot_scan_count": len(scans[0].records),
        "fast_slot_scan_count": len(scans[1].records),
        "auditory_slow_slot_scan_count": len(scans[2].records),
        "total_slot_scan_count": sum(len(scan.records) for scan in scans),
        "observed_comparison_count": comparisons,
        "internal_equality_comparison_count": equality_count,
        "total_value_comparison_count": comparisons + equality_count,
        "hypothesis_value_count": hypothesis_count,
        "logical_operation_count": MAX_LOGICAL_OPERATIONS,
        "memory_receptor_consumer_context_or_field_call_count": 0,
        "serialized_output_bytes": output_size,
    }
    return AuditoryPartialCueResourceLedgerV1(*payload.values(), digest(payload))


def _assemble(*, function_role, config, state, cue, plan, scans, a, b, equality_count, decision, admitted):
    hypothesis = _hypothesis(admitted, a, b, cue, plan, state.state_digest) if admitted else None
    output_size = 0
    for _ in range(8):
        ledger = _ledger(scans, equality_count, len(hypothesis.proposed_values) if hypothesis else 0, output_size)
        payload = {
            "schema": S2KZ_SCHEMA,
            "function_role": function_role,
            "source_digests": [S2KX_CONTRACT_SHA256, S2KY_RESULT_SHA256],
            "config_digest": config.config_digest,
            "state_digest": state.state_digest,
            "cue_digest": cue.cue_digest,
            "band_plan_digest": plan.plan_digest,
            "bank_scan_digests": [item.scan_digest for item in scans],
            "a_recent_digest": a.finding_digest,
            "b_stable_auditory_digest": b.finding_digest,
            "public_candidate_count": a.public_candidate_count + b.public_candidate_count,
            "decision": decision,
            "hypothesis_digest": hypothesis.hypothesis_digest if hypothesis else None,
            "resource_ledger_digest": ledger.ledger_digest,
            "prestate_digest": state.state_digest,
            "poststate_digest": state.state_digest,
            "replacement_perception": None,
            "ranking": None,
        }
        result = AuditoryPartialCueRetrievalResultV1(
            function_role,
            (S2KX_CONTRACT_SHA256, S2KY_RESULT_SHA256),
            config.config_digest,
            state.state_digest,
            cue.cue_digest,
            plan.plan_digest,
            scans,
            a,
            b,
            payload["public_candidate_count"],
            decision,
            hypothesis,
            ledger,
            state.state_digest,
            state.state_digest,
            None,
            None,
            digest(payload),
        )
        next_size = len(canonical_bytes(result.canonical_payload()))
        if next_size == output_size:
            return _validate_result(result)
        output_size = next_size
    raise S2KZError("S2KZ_RESOURCE_EXCEEDED", "output size did not stabilize")


def _validate_result(value):
    ledger = value.resource_ledger
    _require(
        type(value) is AuditoryPartialCueRetrievalResultV1
        and value.schema == S2KZ_SCHEMA
        and value.function_role in FUNCTION_ROLES
        and value.source_digests == (S2KX_CONTRACT_SHA256, S2KY_RESULT_SHA256)
        and tuple(item.bank_role for item in value.bank_scans) == BANK_ROLES
        and tuple(len(item.records) for item in value.bank_scans) == BANK_CAPACITIES
        and all(item.status in BANK_STATUSES for item in value.bank_scans)
        and value.a_recent.status in A_STATUSES
        and value.b_stable_auditory.status in B_STATUSES
        and value.decision in DECISIONS
        and value.public_candidate_count
        == value.a_recent.public_candidate_count + value.b_stable_auditory.public_candidate_count
        <= 2
        and value.prestate_digest == value.state_digest == value.poststate_digest
        and value.replacement_perception is None
        and value.ranking is None
        and ledger.ledger_digest == digest(ledger.payload_without_digest())
        and value.result_digest == digest(value.payload_without_digest()),
        "S2KZ_RESULT_INVALID",
        "result relation differs",
    )
    _require(
        ledger.b4_slot_scan_count == 9
        and ledger.fast_slot_scan_count == 3
        and ledger.auditory_slow_slot_scan_count == 8
        and ledger.total_slot_scan_count == MAX_SLOT_SCANS
        and ledger.observed_comparison_count <= MAX_OBSERVED_COMPARISONS
        and ledger.internal_equality_comparison_count <= MAX_INTERNAL_EQUALITY_COMPARISONS
        and ledger.total_value_comparison_count <= MAX_TOTAL_VALUE_COMPARISONS
        and ledger.hypothesis_value_count <= MAX_HYPOTHESIS_VALUES
        and ledger.logical_operation_count == MAX_LOGICAL_OPERATIONS
        and ledger.memory_receptor_consumer_context_or_field_call_count == 0
        and ledger.serialized_output_bytes == len(canonical_bytes(value.canonical_payload()))
        and ledger.serialized_output_bytes < MAX_OUTPUT_BYTES,
        "S2KZ_RESOURCE_EXCEEDED",
        "resource or output bound differs",
    )
    for scan in value.bank_scans:
        _require(
            scan.scan_digest == digest(scan.payload_without_digest())
            and scan.match_count == len(scan.matched_slot_digests)
            and scan.comparison_count == sum(item.observed_comparison_count for item in scan.records)
            and all(item.record_digest == digest(item.payload_without_digest()) for item in scan.records),
            "S2KZ_RESULT_INVALID",
            "scan evidence differs",
        )
    if value.hypothesis is None:
        _require(
            value.decision != "ADMIT_SINGLE_CONTEXT" and ledger.hypothesis_value_count == 0,
            "S2KZ_RESULT_INVALID",
            "missing hypothesis relation differs",
        )
    else:
        _require(
            value.decision == "ADMIT_SINGLE_CONTEXT"
            and value.hypothesis.area in PUBLIC_AREAS
            and len(value.hypothesis.proposed_values) == 24
            and value.hypothesis.observed_value_count == 0
            and value.hypothesis.visual_value_count == 0
            and value.hypothesis.field_contact_count == 0
            and value.hypothesis.hypothesis_digest == digest(value.hypothesis.payload_without_digest()),
            "S2KZ_RESULT_INVALID",
            "hypothesis relation differs",
        )
    return value


def form_auditory_partial_cue_retrieval_336(
    *,
    config: coordinator.S2JVCoordinatorConfigV1,
    state: coordinator.S2JVCompositeStateV1,
    cue: MaskedAuditoryCue48V1,
    band_plan: AuditoryBandPlan48V1,
) -> AuditoryPartialCueRetrievalResultV1:
    """Scan every native auditory slot and admit at most one A/B candidate."""

    config, state, cue, plan = _state_and_cue(config, state, cue, band_plan)
    before = state.state_digest
    b4_scan, b4_matches = _scan_b4(config, state, cue)
    fast_scan, fast_matches = _scan_fast(config, state, cue)
    slow_scan, slow_matches = _scan_slow(config, state, cue)
    scans = (b4_scan, fast_scan, slow_scan)
    a, equality_count = _resolve_a(b4_scan, b4_matches, fast_scan, fast_matches)
    b = _resolve_b(slow_scan, slow_matches)
    decision, area = _decide(a, b)
    result = _assemble(
        function_role="AUDITORY_PARTIAL_CUE_RETRIEVAL",
        config=config,
        state=state,
        cue=cue,
        plan=plan,
        scans=scans,
        a=a,
        b=b,
        equality_count=equality_count,
        decision=decision,
        admitted=area,
    )
    _require(
        state.state_digest == before,
        "S2KZ_READ_ONLY_VIOLATION",
        "auditory partial-cue retrieval changed memory state",
    )
    return result


__all__: tuple[str, ...] = ()
