"""Private read-only partial-cue retrieval from the 336-value memory state."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from tools import _s2jw_profiled_memory_coordinator as coordinator


S2KQ_SCHEMA = "s2kq.private.partial-cue-retrieval-336.v1"
S2KQ_CONTRACT_DIGEST = "cb04bfea559bfdd84d16fc855ffb0059360eba0232326615517fbc525aa1f5b8"
S2KR_CONTRACT_DIGEST = "8fde5ed37cb119d05eb7ede13967a6649ec00c600470d64c9960eaa4e3bb15da"
FUNCTION_ROLES = ("PARTIAL_CUE_RETRIEVAL", "DIRECT_SLOT_SCAN_BASELINE")
BANK_ROLES = ("B4_RECENT", "TSPM_FAST", "B_STABLE_VISUAL")
BANK_CAPACITIES = (9, 3, 4)
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
    "B_STABLE_ABSENT_VALID",
    "B_STABLE_APPLICABLE",
    "B_STABLE_INTERNAL_AMBIGUITY",
    "B_STABLE_NOT_APPLICABLE",
)
DECISIONS = (
    "ADMIT_SINGLE_CONTEXT",
    "ABSTAIN_INTERNAL_AMBIGUITY",
    "ABSTAIN_INTERNAL_CONFLICT",
    "ABSTAIN_AMBIGUOUS_CONTEXT",
    "ABSTAIN_NO_CONTEXT",
    "ABSTAIN_NO_APPLICABLE_CONTEXT",
)
PUBLIC_AREAS = ("A_RECENT", "B_STABLE")
VISIBLE_POSITIONS = tuple(range(32))
MASKED_POSITIONS = tuple(range(32, 288))
MASK_PLAN_DIGEST = hashlib.sha256(
    json.dumps(
        {
            "schema": S2KQ_SCHEMA,
            "visible_positions": list(VISIBLE_POSITIONS),
            "masked_positions": list(MASKED_POSITIONS),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
).hexdigest()
MAX_SLOT_SCANS = 16
MAX_VISIBLE_COMPARISONS = 512
MAX_INTERNAL_EQUALITY_COMPARISONS = 288
MAX_TOTAL_VALUE_COMPARISONS = 800
MAX_HYPOTHESIS_VALUES = 256
MAX_LOGICAL_OPERATIONS = 12
MAX_OUTPUT_BYTES = 32_768

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9.-]{1,95}$")


class S2KQError(ValueError):
    """One fail-closed S2-KQ contract violation."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2KQError(code, message)


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


def _visual_values(values: object, role: str) -> tuple[float, ...]:
    _require(
        type(values) is tuple and len(values) == 288,
        "S2KQ_DIMENSION_INVALID",
        f"{role} must contain exactly 288 values",
    )
    _require(
        all(type(item) in (int, float) for item in values),
        "S2KQ_DIMENSION_INVALID",
        f"{role} contains a nonnumeric value",
    )
    result = tuple(float(item) for item in values)
    _require(
        all(math.isfinite(item) and 0.0 <= item <= 1.0 for item in result),
        "S2KQ_DIMENSION_INVALID",
        f"{role} differs from the receptor domain",
    )
    return result


@dataclass(frozen=True, slots=True)
class MaskedMemoryCue336V1:
    source_digest: str
    config_digest: str
    field_clock_id: str
    window_start_tick: int
    window_end_tick: int
    values: tuple[float | None, ...]
    visible_positions: tuple[int, ...]
    masked_positions: tuple[int, ...]
    mask_plan_digest: str
    cue_digest: str
    schema: str = S2KQ_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "source_digest": self.source_digest,
            "config_digest": self.config_digest,
            "field_clock_id": self.field_clock_id,
            "window_start_tick": self.window_start_tick,
            "window_end_tick": self.window_end_tick,
            "values": list(self.values),
            "visible_positions": list(self.visible_positions),
            "masked_positions": list(self.masked_positions),
            "mask_plan_digest": self.mask_plan_digest,
        }


@dataclass(frozen=True, slots=True)
class SlotScanRecord336V1:
    bank_role: str
    slot_id: str
    slot_digest: str
    eligible: bool
    stable_support: int | None
    observed_match: bool
    observed_comparison_count: int
    observed_relation_digest: str
    candidate_values_digest: str | None
    record_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "bank_role": self.bank_role,
            "slot_id": self.slot_id,
            "slot_digest": self.slot_digest,
            "eligible": self.eligible,
            "stable_support": self.stable_support,
            "observed_match": self.observed_match,
            "observed_comparison_count": self.observed_comparison_count,
            "observed_relation_digest": self.observed_relation_digest,
            "candidate_values_digest": self.candidate_values_digest,
        }


@dataclass(frozen=True, slots=True)
class BankScanFinding336V1:
    bank_role: str
    capacity: int
    records: tuple[SlotScanRecord336V1, ...]
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
class AreaScanFinding336V1:
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
class PartialCueContextHypothesis336V1:
    area: str
    provenance_slot_digests: tuple[str, ...]
    candidate_values_digest: str
    masked_positions: tuple[int, ...]
    proposed_values: tuple[float, ...]
    cue_digest: str
    mask_plan_digest: str
    state_digest: str
    observed_value_count: int
    field_contact_count: int
    hypothesis_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "area": self.area,
            "provenance_slot_digests": list(self.provenance_slot_digests),
            "candidate_values_digest": self.candidate_values_digest,
            "masked_positions": list(self.masked_positions),
            "proposed_values": list(self.proposed_values),
            "cue_digest": self.cue_digest,
            "mask_plan_digest": self.mask_plan_digest,
            "state_digest": self.state_digest,
            "observed_value_count": self.observed_value_count,
            "field_contact_count": self.field_contact_count,
        }


@dataclass(frozen=True, slots=True)
class PartialCueResourceLedger336V1:
    b4_slot_scan_count: int
    fast_slot_scan_count: int
    visual_slow_slot_scan_count: int
    total_slot_scan_count: int
    observed_comparison_count: int
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
class PartialCueRetrievalResult336V1:
    function_role: str
    contract_digests: tuple[str, str]
    config_digest: str
    state_digest: str
    cue_digest: str
    mask_plan_digest: str
    bank_scans: tuple[BankScanFinding336V1, ...]
    a_recent: AreaScanFinding336V1
    b_stable: AreaScanFinding336V1
    public_candidate_count: int
    decision: str
    hypothesis: PartialCueContextHypothesis336V1 | None
    resource_ledger: PartialCueResourceLedger336V1
    prestate_digest: str
    poststate_digest: str
    replacement_perception: None
    ranking: None
    result_digest: str
    schema: str = S2KQ_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "function_role": self.function_role,
            "contract_digests": list(self.contract_digests),
            "config_digest": self.config_digest,
            "state_digest": self.state_digest,
            "cue_digest": self.cue_digest,
            "mask_plan_digest": self.mask_plan_digest,
            "bank_scan_digests": [item.scan_digest for item in self.bank_scans],
            "a_recent_digest": self.a_recent.finding_digest,
            "b_stable_digest": self.b_stable.finding_digest,
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
            "b_stable": {**self.b_stable.payload_without_digest(), "finding_digest": self.b_stable.finding_digest},
            "hypothesis": None
            if self.hypothesis is None
            else {**self.hypothesis.payload_without_digest(), "hypothesis_digest": self.hypothesis.hypothesis_digest},
            "resource_ledger": {**self.resource_ledger.payload_without_digest(), "ledger_digest": self.resource_ledger.ledger_digest},
            "result_digest": self.result_digest,
        }


@dataclass(frozen=True, slots=True)
class _Candidate:
    slot_digest: str
    values: tuple[float, ...]
    values_digest: str


def build_masked_memory_cue_336(
    *,
    source_digest: str,
    config_digest: str,
    field_clock_id: str,
    window_start_tick: int,
    window_end_tick: int,
    values: tuple[float | None, ...],
) -> MaskedMemoryCue336V1:
    payload = {
        "schema": S2KQ_SCHEMA,
        "source_digest": source_digest,
        "config_digest": config_digest,
        "field_clock_id": field_clock_id,
        "window_start_tick": window_start_tick,
        "window_end_tick": window_end_tick,
        "values": list(values),
        "visible_positions": list(VISIBLE_POSITIONS),
        "masked_positions": list(MASKED_POSITIONS),
        "mask_plan_digest": MASK_PLAN_DIGEST,
    }
    return _validate_cue(
        MaskedMemoryCue336V1(
            source_digest,
            config_digest,
            field_clock_id,
            window_start_tick,
            window_end_tick,
            values,
            VISIBLE_POSITIONS,
            MASKED_POSITIONS,
            MASK_PLAN_DIGEST,
            digest(payload),
        )
    )


def _validate_cue(value: object) -> MaskedMemoryCue336V1:
    _require(type(value) is MaskedMemoryCue336V1, "S2KQ_TYPE_INVALID", "exact cue required")
    assert isinstance(value, MaskedMemoryCue336V1)
    _require(
        value.schema == S2KQ_SCHEMA
        and _valid_digest(value.source_digest)
        and _valid_digest(value.config_digest)
        and _valid_identifier(value.field_clock_id)
        and type(value.window_start_tick) is int
        and type(value.window_end_tick) is int
        and 0 <= value.window_start_tick < value.window_end_tick
        and type(value.values) is tuple
        and len(value.values) == 288
        and value.visible_positions == VISIBLE_POSITIONS
        and value.masked_positions == MASKED_POSITIONS
        and value.mask_plan_digest == MASK_PLAN_DIGEST
        and all(type(value.values[index]) in (int, float) for index in VISIBLE_POSITIONS)
        and all(
            math.isfinite(float(value.values[index]))
            and 0.0 <= float(value.values[index]) <= 1.0
            for index in VISIBLE_POSITIONS
        )
        and all(value.values[index] is None for index in MASKED_POSITIONS)
        and value.cue_digest == digest(value.payload_without_digest()),
        "S2KQ_SOURCE_INVALID",
        "cue, mask, time, or digest binding differs",
    )
    return value


def _state_and_cue(
    config: object,
    state: object,
    cue: object,
) -> tuple[coordinator.S2JVCoordinatorConfigV1, coordinator.S2JVCompositeStateV1, MaskedMemoryCue336V1]:
    try:
        bound_config = coordinator._validate_config(config)
        bound_state = coordinator._validate_state(bound_config, state)
    except Exception as exc:
        raise S2KQError("S2KQ_STATE_INVALID", "config or memory state is invalid") from exc
    bound_cue = _validate_cue(cue)
    _require(
        bound_cue.config_digest == bound_config.config_digest,
        "S2KQ_SOURCE_INVALID",
        "cue configuration differs",
    )
    fast = bound_state.tspm_state.fast_state
    if bound_state.generation > 0:
        _require(
            fast.auditory_source_clock_id == fast.visual_source_clock_id == bound_cue.field_clock_id
            and fast.auditory_last_end_tick is not None
            and fast.visual_last_end_tick is not None
            and bound_cue.window_end_tick > fast.auditory_last_end_tick
            and bound_cue.window_end_tick > fast.visual_last_end_tick,
            "S2KQ_SOURCE_INVALID",
            "cue is stale or belongs to another clock",
        )
    return bound_config, bound_state, bound_cue


def _slot_record(
    *,
    bank_role: str,
    slot_id: str,
    slot_digest: str,
    values: tuple[float, ...] | None,
    support: int | None,
    cue: MaskedMemoryCue336V1,
) -> tuple[SlotScanRecord336V1, _Candidate | None]:
    eligible = values is not None
    comparisons = len(VISIBLE_POSITIONS) if eligible else 0
    match = eligible and all(
        values[index] == float(cue.values[index]) for index in VISIBLE_POSITIONS
    )
    values_digest = digest(list(values)) if eligible else None
    relation = digest(
        {
            "schema": S2KQ_SCHEMA,
            "bank_role": bank_role,
            "slot_digest": slot_digest,
            "cue_digest": cue.cue_digest,
            "mask_plan_digest": cue.mask_plan_digest,
            "observed_match": match,
            "observed_comparison_count": comparisons,
        }
    )
    payload = {
        "bank_role": bank_role,
        "slot_id": slot_id,
        "slot_digest": slot_digest,
        "eligible": eligible,
        "stable_support": support,
        "observed_match": match,
        "observed_comparison_count": comparisons,
        "observed_relation_digest": relation,
        "candidate_values_digest": values_digest,
    }
    record = SlotScanRecord336V1(
        bank_role,
        slot_id,
        slot_digest,
        eligible,
        support,
        match,
        comparisons,
        relation,
        values_digest,
        digest(payload),
    )
    candidate = _Candidate(slot_digest, values, values_digest) if match else None  # type: ignore[arg-type]
    return record, candidate


def _finish_bank(
    bank_role: str,
    capacity: int,
    records: list[SlotScanRecord336V1],
    matches: list[_Candidate],
) -> tuple[BankScanFinding336V1, tuple[_Candidate, ...]]:
    eligible = sum(item.eligible for item in records)
    if eligible == 0:
        status = "BANK_ABSENT_VALID"
    elif not matches:
        status = "BANK_NO_OBSERVED_MATCH"
    elif len(matches) == 1:
        status = "BANK_UNIQUE_OBSERVED_MATCH"
    else:
        status = "BANK_MULTIPLE_OBSERVED_MATCHES"
    ordered_matches = tuple(sorted(matches, key=lambda item: item.slot_digest))
    payload = {
        "bank_role": bank_role,
        "capacity": capacity,
        "record_digests": [item.record_digest for item in records],
        "eligible_count": eligible,
        "match_count": len(matches),
        "matched_slot_digests": [item.slot_digest for item in ordered_matches],
        "status": status,
        "comparison_count": sum(item.observed_comparison_count for item in records),
    }
    return (
        BankScanFinding336V1(
            bank_role,
            capacity,
            tuple(records),
            eligible,
            len(matches),
            tuple(item.slot_digest for item in ordered_matches),
            status,
            payload["comparison_count"],  # type: ignore[arg-type]
            digest(payload),
        ),
        ordered_matches,
    )


def _scan_b4(state: coordinator.S2JVCompositeStateV1, cue: MaskedMemoryCue336V1):
    records: list[SlotScanRecord336V1] = []
    matches: list[_Candidate] = []
    for entry in state.b4_state.entries:
        values = _visual_values(entry.values[48:], "B4 visual values") if entry.occupied else None
        record, match = _slot_record(
            bank_role="B4_RECENT",
            slot_id=entry.slot_id,
            slot_digest=digest(comparison._canonical(entry)),
            values=values,
            support=None,
            cue=cue,
        )
        records.append(record)
        if match is not None:
            matches.append(match)
    return _finish_bank("B4_RECENT", 9, records, matches)


def _scan_fast(state: coordinator.S2JVCompositeStateV1, cue: MaskedMemoryCue336V1):
    records: list[SlotScanRecord336V1] = []
    matches: list[_Candidate] = []
    for slot in state.tspm_state.fast_state.slots:
        values = _visual_values(slot.visual_values, "Fast visual values") if slot.occupied else None
        record, match = _slot_record(
            bank_role="TSPM_FAST",
            slot_id=slot.slot_id,
            slot_digest=slot.digest(),
            values=values,
            support=slot.support_count if slot.occupied else None,
            cue=cue,
        )
        records.append(record)
        if match is not None:
            matches.append(match)
    return _finish_bank("TSPM_FAST", 3, records, matches)


def _scan_slow(state: coordinator.S2JVCompositeStateV1, cue: MaskedMemoryCue336V1):
    records: list[SlotScanRecord336V1] = []
    matches: list[_Candidate] = []
    for slot in state.tspm_state.visual_ppb1_state.slots:
        stable = slot.occupied and slot.support_count is not None and slot.support_count >= 3
        values = _visual_values(slot.prototype_values, "Slow visual values") if stable else None
        record, match = _slot_record(
            bank_role="B_STABLE_VISUAL",
            slot_id=slot.slot_id,
            slot_digest=digest(slot.canonical_payload()),
            values=values,
            support=slot.support_count if stable else None,
            cue=cue,
        )
        records.append(record)
        if match is not None:
            matches.append(match)
    return _finish_bank("B_STABLE_VISUAL", 4, records, matches)


def _area_finding(
    area: str,
    status: str,
    parents: tuple[str, ...],
    selected: tuple[_Candidate, ...],
) -> AreaScanFinding336V1:
    values_digest = selected[0].values_digest if selected else None
    masked = tuple(selected[0].values[index] for index in MASKED_POSITIONS) if selected else ()
    payload = {
        "area": area,
        "status": status,
        "parent_scan_digests": list(parents),
        "provenance_slot_digests": [item.slot_digest for item in selected],
        "candidate_values_digest": values_digest,
        "masked_values": list(masked),
        "public_candidate_count": 1 if selected else 0,
    }
    return AreaScanFinding336V1(
        area,
        status,
        parents,
        tuple(item.slot_digest for item in selected),
        values_digest,
        masked,
        1 if selected else 0,
        digest(payload),
    )


def _resolve_a(
    b4_scan: BankScanFinding336V1,
    b4_matches: tuple[_Candidate, ...],
    fast_scan: BankScanFinding336V1,
    fast_matches: tuple[_Candidate, ...],
) -> tuple[AreaScanFinding336V1, int]:
    parents = (b4_scan.scan_digest, fast_scan.scan_digest)
    if "BANK_MULTIPLE_OBSERVED_MATCHES" in (b4_scan.status, fast_scan.status):
        return _area_finding("A_RECENT", "A_RECENT_INTERNAL_AMBIGUITY", parents, ()), 0
    unique = tuple(
        values[0]
        for scan, values in ((b4_scan, b4_matches), (fast_scan, fast_matches))
        if scan.status == "BANK_UNIQUE_OBSERVED_MATCH"
    )
    if len(unique) == 2:
        if unique[0].values_digest == unique[1].values_digest and unique[0].values == unique[1].values:
            return _area_finding("A_RECENT", "A_RECENT_APPLICABLE", parents, unique), 288
        return _area_finding("A_RECENT", "A_RECENT_INTERNAL_CONFLICT", parents, ()), 288
    if len(unique) == 1:
        return _area_finding("A_RECENT", "A_RECENT_APPLICABLE", parents, unique), 0
    if b4_scan.status == fast_scan.status == "BANK_ABSENT_VALID":
        return _area_finding("A_RECENT", "A_RECENT_ABSENT_VALID", parents, ()), 0
    return _area_finding("A_RECENT", "A_RECENT_NOT_APPLICABLE", parents, ()), 0


def _resolve_b(
    scan: BankScanFinding336V1,
    matches: tuple[_Candidate, ...],
) -> AreaScanFinding336V1:
    mapping = {
        "BANK_ABSENT_VALID": "B_STABLE_ABSENT_VALID",
        "BANK_NO_OBSERVED_MATCH": "B_STABLE_NOT_APPLICABLE",
        "BANK_UNIQUE_OBSERVED_MATCH": "B_STABLE_APPLICABLE",
        "BANK_MULTIPLE_OBSERVED_MATCHES": "B_STABLE_INTERNAL_AMBIGUITY",
    }
    selected = matches if len(matches) == 1 else ()
    return _area_finding("B_STABLE", mapping[scan.status], (scan.scan_digest,), selected)


def _decide(a: AreaScanFinding336V1, b: AreaScanFinding336V1) -> tuple[str, str | None]:
    if a.status == "A_RECENT_INTERNAL_AMBIGUITY" or b.status == "B_STABLE_INTERNAL_AMBIGUITY":
        return "ABSTAIN_INTERNAL_AMBIGUITY", None
    if a.status == "A_RECENT_INTERNAL_CONFLICT":
        return "ABSTAIN_INTERNAL_CONFLICT", None
    count = a.public_candidate_count + b.public_candidate_count
    if count == 1:
        return "ADMIT_SINGLE_CONTEXT", "A_RECENT" if a.public_candidate_count else "B_STABLE"
    if count == 2:
        return "ABSTAIN_AMBIGUOUS_CONTEXT", None
    if a.status == "A_RECENT_ABSENT_VALID" and b.status == "B_STABLE_ABSENT_VALID":
        return "ABSTAIN_NO_CONTEXT", None
    return "ABSTAIN_NO_APPLICABLE_CONTEXT", None


def _hypothesis(
    area: str,
    a: AreaScanFinding336V1,
    b: AreaScanFinding336V1,
    cue: MaskedMemoryCue336V1,
    state_digest: str,
) -> PartialCueContextHypothesis336V1:
    finding = a if area == "A_RECENT" else b
    _require(
        finding.public_candidate_count == 1
        and _valid_digest(finding.candidate_values_digest)
        and len(finding.masked_values) == MAX_HYPOTHESIS_VALUES,
        "S2KQ_EVIDENCE_INVALID",
        "hypothesis source differs",
    )
    payload = {
        "area": area,
        "provenance_slot_digests": list(finding.provenance_slot_digests),
        "candidate_values_digest": finding.candidate_values_digest,
        "masked_positions": list(MASKED_POSITIONS),
        "proposed_values": list(finding.masked_values),
        "cue_digest": cue.cue_digest,
        "mask_plan_digest": cue.mask_plan_digest,
        "state_digest": state_digest,
        "observed_value_count": 0,
        "field_contact_count": 0,
    }
    return PartialCueContextHypothesis336V1(
        area,
        finding.provenance_slot_digests,
        finding.candidate_values_digest,  # type: ignore[arg-type]
        MASKED_POSITIONS,
        finding.masked_values,
        cue.cue_digest,
        cue.mask_plan_digest,
        state_digest,
        0,
        0,
        digest(payload),
    )


def _ledger(
    scans: tuple[BankScanFinding336V1, ...],
    equality_count: int,
    hypothesis_count: int,
    output_size: int,
) -> PartialCueResourceLedger336V1:
    comparisons = sum(scan.comparison_count for scan in scans)
    payload = {
        "b4_slot_scan_count": len(scans[0].records),
        "fast_slot_scan_count": len(scans[1].records),
        "visual_slow_slot_scan_count": len(scans[2].records),
        "total_slot_scan_count": sum(len(scan.records) for scan in scans),
        "observed_comparison_count": comparisons,
        "internal_equality_comparison_count": equality_count,
        "total_value_comparison_count": comparisons + equality_count,
        "hypothesis_value_count": hypothesis_count,
        "logical_operation_count": MAX_LOGICAL_OPERATIONS,
        "memory_receptor_consumer_or_field_call_count": 0,
        "serialized_output_bytes": output_size,
    }
    return PartialCueResourceLedger336V1(*payload.values(), digest(payload))


def _assemble(
    *,
    function_role: str,
    config: coordinator.S2JVCoordinatorConfigV1,
    state: coordinator.S2JVCompositeStateV1,
    cue: MaskedMemoryCue336V1,
    scans: tuple[BankScanFinding336V1, ...],
    a: AreaScanFinding336V1,
    b: AreaScanFinding336V1,
    equality_count: int,
    decision: str,
    admitted_area: str | None,
) -> PartialCueRetrievalResult336V1:
    hypothesis = _hypothesis(admitted_area, a, b, cue, state.state_digest) if admitted_area else None
    output_size = 0
    for _ in range(8):
        ledger = _ledger(scans, equality_count, len(hypothesis.proposed_values) if hypothesis else 0, output_size)
        payload = {
            "schema": S2KQ_SCHEMA,
            "function_role": function_role,
            "contract_digests": [S2KQ_CONTRACT_DIGEST, S2KR_CONTRACT_DIGEST],
            "config_digest": config.config_digest,
            "state_digest": state.state_digest,
            "cue_digest": cue.cue_digest,
            "mask_plan_digest": cue.mask_plan_digest,
            "bank_scan_digests": [item.scan_digest for item in scans],
            "a_recent_digest": a.finding_digest,
            "b_stable_digest": b.finding_digest,
            "public_candidate_count": a.public_candidate_count + b.public_candidate_count,
            "decision": decision,
            "hypothesis_digest": hypothesis.hypothesis_digest if hypothesis else None,
            "resource_ledger_digest": ledger.ledger_digest,
            "prestate_digest": state.state_digest,
            "poststate_digest": state.state_digest,
            "replacement_perception": None,
            "ranking": None,
        }
        result = PartialCueRetrievalResult336V1(
            function_role,
            (S2KQ_CONTRACT_DIGEST, S2KR_CONTRACT_DIGEST),
            config.config_digest,
            state.state_digest,
            cue.cue_digest,
            cue.mask_plan_digest,
            scans,
            a,
            b,
            payload["public_candidate_count"],  # type: ignore[arg-type]
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
    raise S2KQError("S2KQ_RESOURCE_EXCEEDED", "output size did not stabilize")


def _validate_result(value: PartialCueRetrievalResult336V1) -> PartialCueRetrievalResult336V1:
    ledger = value.resource_ledger
    _require(
        type(value) is PartialCueRetrievalResult336V1
        and value.schema == S2KQ_SCHEMA
        and value.function_role in FUNCTION_ROLES
        and value.contract_digests == (S2KQ_CONTRACT_DIGEST, S2KR_CONTRACT_DIGEST)
        and tuple(item.bank_role for item in value.bank_scans) == BANK_ROLES
        and tuple(len(item.records) for item in value.bank_scans) == BANK_CAPACITIES
        and all(item.status in BANK_STATUSES for item in value.bank_scans)
        and value.a_recent.status in A_STATUSES
        and value.b_stable.status in B_STATUSES
        and value.decision in DECISIONS
        and value.public_candidate_count
        == value.a_recent.public_candidate_count + value.b_stable.public_candidate_count
        <= 2
        and value.prestate_digest == value.state_digest == value.poststate_digest
        and value.replacement_perception is None
        and value.ranking is None
        and ledger.ledger_digest == digest(ledger.payload_without_digest())
        and value.result_digest == digest(value.payload_without_digest()),
        "S2KQ_RESULT_INVALID",
        "result relation differs",
    )
    _require(
        ledger.b4_slot_scan_count == 9
        and ledger.fast_slot_scan_count == 3
        and ledger.visual_slow_slot_scan_count == 4
        and ledger.total_slot_scan_count == MAX_SLOT_SCANS
        and ledger.observed_comparison_count <= MAX_VISIBLE_COMPARISONS
        and ledger.internal_equality_comparison_count <= MAX_INTERNAL_EQUALITY_COMPARISONS
        and ledger.total_value_comparison_count <= MAX_TOTAL_VALUE_COMPARISONS
        and ledger.hypothesis_value_count <= MAX_HYPOTHESIS_VALUES
        and ledger.logical_operation_count == MAX_LOGICAL_OPERATIONS
        and ledger.memory_receptor_consumer_or_field_call_count == 0
        and ledger.serialized_output_bytes == len(canonical_bytes(value.canonical_payload()))
        and ledger.serialized_output_bytes < MAX_OUTPUT_BYTES,
        "S2KQ_RESOURCE_EXCEEDED",
        "resource or output bound differs",
    )
    if value.hypothesis is None:
        _require(
            value.decision != "ADMIT_SINGLE_CONTEXT" and ledger.hypothesis_value_count == 0,
            "S2KQ_RESULT_INVALID",
            "missing hypothesis relation differs",
        )
    else:
        _require(
            value.decision == "ADMIT_SINGLE_CONTEXT"
            and value.hypothesis.area in PUBLIC_AREAS
            and len(value.hypothesis.proposed_values) == MAX_HYPOTHESIS_VALUES
            and value.hypothesis.observed_value_count == 0
            and value.hypothesis.field_contact_count == 0
            and value.hypothesis.hypothesis_digest == digest(value.hypothesis.payload_without_digest()),
            "S2KQ_RESULT_INVALID",
            "hypothesis relation differs",
        )
    return value


def form_partial_cue_retrieval_336(
    *,
    config: coordinator.S2JVCoordinatorConfigV1,
    state: coordinator.S2JVCompositeStateV1,
    cue: MaskedMemoryCue336V1,
) -> PartialCueRetrievalResult336V1:
    """Scan every native slot and admit at most one public A/B candidate."""

    config, state, cue = _state_and_cue(config, state, cue)
    before = state.state_digest
    b4_scan, b4_matches = _scan_b4(state, cue)
    fast_scan, fast_matches = _scan_fast(state, cue)
    slow_scan, slow_matches = _scan_slow(state, cue)
    scans = (b4_scan, fast_scan, slow_scan)
    a, equality_count = _resolve_a(b4_scan, b4_matches, fast_scan, fast_matches)
    b = _resolve_b(slow_scan, slow_matches)
    decision, area = _decide(a, b)
    result = _assemble(
        function_role="PARTIAL_CUE_RETRIEVAL",
        config=config,
        state=state,
        cue=cue,
        scans=scans,
        a=a,
        b=b,
        equality_count=equality_count,
        decision=decision,
        admitted_area=area,
    )
    _require(
        state.state_digest == before,
        "S2KQ_READ_ONLY_VIOLATION",
        "partial-cue retrieval changed memory state",
    )
    return result


__all__: tuple[str, ...] = ()
