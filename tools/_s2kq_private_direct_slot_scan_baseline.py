"""Independent direct slot-scan baseline for the private S2-KQ contract."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2kq_private_partial_cue_retrieval_336 as types


_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9.-]{1,95}$")


@dataclass(frozen=True, slots=True)
class _RawCandidate:
    slot_digest: str
    values: tuple[float, ...]
    values_digest: str


def _bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _digest(payload: object) -> str:
    return hashlib.sha256(_bytes(payload)).hexdigest()


def _fail(message: str) -> None:
    raise types.S2KQError("S2KQ_BASELINE_INVALID", message)


def _check(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


def _visual(values: object, role: str) -> tuple[float, ...]:
    _check(type(values) is tuple and len(values) == 288, f"{role} dimension differs")
    _check(all(type(item) in (int, float) for item in values), f"{role} type differs")
    result = tuple(float(item) for item in values)
    _check(
        all(math.isfinite(item) and 0.0 <= item <= 1.0 for item in result),
        f"{role} value differs",
    )
    return result


def _validate_inputs(config: object, state: object, cue: object):
    try:
        config = coordinator._validate_config(config)
        state = coordinator._validate_state(config, state)
    except Exception as exc:
        raise types.S2KQError("S2KQ_BASELINE_INVALID", "state validation failed") from exc
    _check(type(cue) is types.MaskedMemoryCue336V1, "cue type differs")
    _check(
        cue.schema == types.S2KQ_SCHEMA
        and type(cue.source_digest) is str
        and _DIGEST.fullmatch(cue.source_digest) is not None
        and type(cue.config_digest) is str
        and _DIGEST.fullmatch(cue.config_digest) is not None
        and cue.config_digest == config.config_digest
        and type(cue.field_clock_id) is str
        and _IDENTIFIER.fullmatch(cue.field_clock_id) is not None
        and type(cue.window_start_tick) is int
        and type(cue.window_end_tick) is int
        and 0 <= cue.window_start_tick < cue.window_end_tick
        and type(cue.visual_source_clock_id) is str
        and _IDENTIFIER.fullmatch(cue.visual_source_clock_id) is not None
        and type(cue.visual_window_start_tick) is int
        and type(cue.visual_window_end_tick) is int
        and 0 <= cue.visual_window_start_tick < cue.visual_window_end_tick
        and cue.visible_positions == types.VISIBLE_POSITIONS
        and cue.masked_positions == types.MASKED_POSITIONS
        and cue.mask_plan_digest == types.MASK_PLAN_DIGEST
        and type(cue.values) is tuple
        and len(cue.values) == 288
        and all(type(cue.values[index]) in (int, float) for index in types.VISIBLE_POSITIONS)
        and all(
            math.isfinite(float(cue.values[index]))
            and 0.0 <= float(cue.values[index]) <= 1.0
            for index in types.VISIBLE_POSITIONS
        )
        and all(cue.values[index] is None for index in types.MASKED_POSITIONS)
        and cue.cue_digest == _digest(cue.payload_without_digest()),
        "cue relation differs",
    )
    fast = state.tspm_state.fast_state
    if state.generation:
        _check(
            fast.visual_source_clock_id == cue.visual_source_clock_id
            and fast.visual_last_end_tick is not None
            and cue.visual_window_start_tick >= fast.visual_last_end_tick
            and cue.visual_window_end_tick > fast.visual_last_end_tick,
            "native visual cue time differs",
        )
    return config, state, cue


def _record(
    role: str,
    slot_id: str,
    slot_digest: str,
    values: tuple[float, ...] | None,
    support: int | None,
    cue: types.MaskedMemoryCue336V1,
) -> tuple[types.SlotScanRecord336V1, _RawCandidate | None]:
    eligible = values is not None
    compared = 32 if eligible else 0
    matched = eligible and all(
        values[index] == float(cue.values[index]) for index in types.VISIBLE_POSITIONS
    )
    value_digest = _digest(list(values)) if eligible else None
    relation_digest = _digest(
        {
            "schema": types.S2KQ_SCHEMA,
            "bank_role": role,
            "slot_digest": slot_digest,
            "cue_digest": cue.cue_digest,
            "mask_plan_digest": cue.mask_plan_digest,
            "observed_match": matched,
            "observed_comparison_count": compared,
        }
    )
    payload = {
        "bank_role": role,
        "slot_id": slot_id,
        "slot_digest": slot_digest,
        "eligible": eligible,
        "stable_support": support,
        "observed_match": matched,
        "observed_comparison_count": compared,
        "observed_relation_digest": relation_digest,
        "candidate_values_digest": value_digest,
    }
    result = types.SlotScanRecord336V1(
        role,
        slot_id,
        slot_digest,
        eligible,
        support,
        matched,
        compared,
        relation_digest,
        value_digest,
        _digest(payload),
    )
    candidate = _RawCandidate(slot_digest, values, value_digest) if matched else None  # type: ignore[arg-type]
    return result, candidate


def _close_bank(
    role: str,
    capacity: int,
    records: list[types.SlotScanRecord336V1],
    matches: list[_RawCandidate],
):
    eligible_count = sum(item.eligible for item in records)
    if eligible_count == 0:
        status = "BANK_ABSENT_VALID"
    elif len(matches) == 0:
        status = "BANK_NO_OBSERVED_MATCH"
    elif len(matches) == 1:
        status = "BANK_UNIQUE_OBSERVED_MATCH"
    else:
        status = "BANK_MULTIPLE_OBSERVED_MATCHES"
    ordered = tuple(sorted(matches, key=lambda item: item.slot_digest))
    comparisons = sum(item.observed_comparison_count for item in records)
    payload = {
        "bank_role": role,
        "capacity": capacity,
        "record_digests": [item.record_digest for item in records],
        "eligible_count": eligible_count,
        "match_count": len(ordered),
        "matched_slot_digests": [item.slot_digest for item in ordered],
        "status": status,
        "comparison_count": comparisons,
    }
    return (
        types.BankScanFinding336V1(
            role,
            capacity,
            tuple(records),
            eligible_count,
            len(ordered),
            tuple(item.slot_digest for item in ordered),
            status,
            comparisons,
            _digest(payload),
        ),
        ordered,
    )


def _scan_b4(state, cue):
    records = []
    matches = []
    for entry in state.b4_state.entries:
        visual = _visual(entry.values[48:], "B4") if entry.occupied else None
        record, candidate = _record(
            "B4_RECENT",
            entry.slot_id,
            _digest(comparison._canonical(entry)),
            visual,
            None,
            cue,
        )
        records.append(record)
        if candidate is not None:
            matches.append(candidate)
    return _close_bank("B4_RECENT", 9, records, matches)


def _scan_fast(state, cue):
    records = []
    matches = []
    for slot in state.tspm_state.fast_state.slots:
        visual = _visual(slot.visual_values, "Fast") if slot.occupied else None
        record, candidate = _record(
            "TSPM_FAST",
            slot.slot_id,
            slot.digest(),
            visual,
            slot.support_count if slot.occupied else None,
            cue,
        )
        records.append(record)
        if candidate is not None:
            matches.append(candidate)
    return _close_bank("TSPM_FAST", 3, records, matches)


def _scan_slow(state, cue):
    records = []
    matches = []
    for slot in state.tspm_state.visual_ppb1_state.slots:
        stable = slot.occupied and slot.support_count is not None and slot.support_count >= 3
        visual = _visual(slot.prototype_values, "Slow") if stable else None
        record, candidate = _record(
            "B_STABLE_VISUAL",
            slot.slot_id,
            _digest(slot.canonical_payload()),
            visual,
            slot.support_count if stable else None,
            cue,
        )
        records.append(record)
        if candidate is not None:
            matches.append(candidate)
    return _close_bank("B_STABLE_VISUAL", 4, records, matches)


def _area(area: str, status: str, parents: tuple[str, ...], selected: tuple[_RawCandidate, ...]):
    value_digest = selected[0].values_digest if selected else None
    masked = tuple(selected[0].values[index] for index in types.MASKED_POSITIONS) if selected else ()
    payload = {
        "area": area,
        "status": status,
        "parent_scan_digests": list(parents),
        "provenance_slot_digests": [item.slot_digest for item in selected],
        "candidate_values_digest": value_digest,
        "masked_values": list(masked),
        "public_candidate_count": 1 if selected else 0,
    }
    return types.AreaScanFinding336V1(
        area,
        status,
        parents,
        tuple(item.slot_digest for item in selected),
        value_digest,
        masked,
        1 if selected else 0,
        _digest(payload),
    )


def _resolve_recent(b4_scan, b4_matches, fast_scan, fast_matches):
    parents = (b4_scan.scan_digest, fast_scan.scan_digest)
    if b4_scan.match_count > 1 or fast_scan.match_count > 1:
        return _area("A_RECENT", "A_RECENT_INTERNAL_AMBIGUITY", parents, ()), 0
    candidates = tuple(
        values[0]
        for scan, values in ((b4_scan, b4_matches), (fast_scan, fast_matches))
        if scan.match_count == 1
    )
    if len(candidates) == 2:
        same = candidates[0].values_digest == candidates[1].values_digest and candidates[0].values == candidates[1].values
        return (
            _area("A_RECENT", "A_RECENT_APPLICABLE" if same else "A_RECENT_INTERNAL_CONFLICT", parents, candidates if same else ()),
            288,
        )
    if len(candidates) == 1:
        return _area("A_RECENT", "A_RECENT_APPLICABLE", parents, candidates), 0
    if b4_scan.eligible_count == fast_scan.eligible_count == 0:
        return _area("A_RECENT", "A_RECENT_ABSENT_VALID", parents, ()), 0
    return _area("A_RECENT", "A_RECENT_NOT_APPLICABLE", parents, ()), 0


def _resolve_stable(scan, matches):
    if scan.match_count > 1:
        status = "B_STABLE_INTERNAL_AMBIGUITY"
        selected = ()
    elif scan.match_count == 1:
        status = "B_STABLE_APPLICABLE"
        selected = matches
    elif scan.eligible_count == 0:
        status = "B_STABLE_ABSENT_VALID"
        selected = ()
    else:
        status = "B_STABLE_NOT_APPLICABLE"
        selected = ()
    return _area("B_STABLE", status, (scan.scan_digest,), selected)


def _choose(a, b):
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


def _make_hypothesis(area, a, b, cue, state_digest):
    source = a if area == "A_RECENT" else b
    _check(source.public_candidate_count == 1, "hypothesis source is not unique")
    payload = {
        "area": area,
        "provenance_slot_digests": list(source.provenance_slot_digests),
        "candidate_values_digest": source.candidate_values_digest,
        "masked_positions": list(types.MASKED_POSITIONS),
        "proposed_values": list(source.masked_values),
        "cue_digest": cue.cue_digest,
        "mask_plan_digest": cue.mask_plan_digest,
        "state_digest": state_digest,
        "observed_value_count": 0,
        "field_contact_count": 0,
    }
    return types.PartialCueContextHypothesis336V1(
        area,
        source.provenance_slot_digests,
        source.candidate_values_digest,
        types.MASKED_POSITIONS,
        source.masked_values,
        cue.cue_digest,
        cue.mask_plan_digest,
        state_digest,
        0,
        0,
        _digest(payload),
    )


def _make_ledger(scans, equality_count, hypothesis_count, output_size):
    compared = sum(scan.comparison_count for scan in scans)
    payload = {
        "b4_slot_scan_count": 9,
        "fast_slot_scan_count": 3,
        "visual_slow_slot_scan_count": 4,
        "total_slot_scan_count": 16,
        "observed_comparison_count": compared,
        "internal_equality_comparison_count": equality_count,
        "total_value_comparison_count": compared + equality_count,
        "hypothesis_value_count": hypothesis_count,
        "logical_operation_count": 12,
        "memory_receptor_consumer_or_field_call_count": 0,
        "serialized_output_bytes": output_size,
    }
    return types.PartialCueResourceLedger336V1(*payload.values(), _digest(payload))


def _assemble(config, state, cue, scans, a, b, equality_count, decision, admitted):
    hypothesis = _make_hypothesis(admitted, a, b, cue, state.state_digest) if admitted else None
    size = 0
    for _ in range(8):
        ledger = _make_ledger(scans, equality_count, len(hypothesis.proposed_values) if hypothesis else 0, size)
        payload = {
            "schema": types.S2KQ_SCHEMA,
            "function_role": "DIRECT_SLOT_SCAN_BASELINE",
            "contract_digests": [types.S2KQ_CONTRACT_DIGEST, types.S2KR_CONTRACT_DIGEST],
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
        result = types.PartialCueRetrievalResult336V1(
            "DIRECT_SLOT_SCAN_BASELINE",
            (types.S2KQ_CONTRACT_DIGEST, types.S2KR_CONTRACT_DIGEST),
            config.config_digest,
            state.state_digest,
            cue.cue_digest,
            cue.mask_plan_digest,
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
            _digest(payload),
        )
        next_size = len(_bytes(result.canonical_payload()))
        if next_size == size:
            _check(next_size < types.MAX_OUTPUT_BYTES, "output exceeds bound")
            _check(ledger.total_value_comparison_count <= 800, "comparison bound exceeded")
            return result
        size = next_size
    _fail("output size did not stabilize")


def form_direct_partial_cue_slot_scan_baseline_336(
    *,
    config: coordinator.S2JVCoordinatorConfigV1,
    state: coordinator.S2JVCompositeStateV1,
    cue: types.MaskedMemoryCue336V1,
) -> types.PartialCueRetrievalResult336V1:
    """Recompute the complete scan and table without primary decision helpers."""

    config, state, cue = _validate_inputs(config, state, cue)
    before = state.state_digest
    b4_scan, b4_matches = _scan_b4(state, cue)
    fast_scan, fast_matches = _scan_fast(state, cue)
    slow_scan, slow_matches = _scan_slow(state, cue)
    scans = (b4_scan, fast_scan, slow_scan)
    a, equality = _resolve_recent(b4_scan, b4_matches, fast_scan, fast_matches)
    b = _resolve_stable(slow_scan, slow_matches)
    decision, admitted = _choose(a, b)
    result = _assemble(config, state, cue, scans, a, b, equality, decision, admitted)
    _check(state.state_digest == before, "baseline changed memory state")
    return result


__all__: tuple[str, ...] = ()
