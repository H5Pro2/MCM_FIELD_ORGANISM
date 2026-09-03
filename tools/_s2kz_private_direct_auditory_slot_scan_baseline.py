"""Independent direct auditory slot-scan baseline for private S2-KZ."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as types


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


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise types.S2KZError("S2KZ_BASELINE_INVALID", message)


def _auditory(values: object, role: str) -> tuple[float, ...]:
    _check(type(values) is tuple and len(values) == 48, f"{role} dimension differs")
    _check(all(type(item) in (int, float) for item in values), f"{role} type differs")
    result = tuple(float(item) for item in values)
    _check(
        all(math.isfinite(item) and 0.0 <= item <= 1.0 for item in result),
        f"{role} value differs",
    )
    return result


def _validate_inputs(config: object, state: object, cue: object, band_plan: object):
    try:
        config = coordinator._validate_config(config)
        state = coordinator._validate_state(config, state)
    except Exception as exc:
        raise types.S2KZError("S2KZ_BASELINE_INVALID", "state validation failed") from exc
    _check(type(band_plan) is types.AuditoryBandPlan48V1, "band plan type differs")
    _check(
        band_plan.schema == types.S2KZ_SCHEMA
        and band_plan.observed_bands == types.OBSERVED_BANDS
        and band_plan.masked_bands == types.MASKED_BANDS
        and band_plan.observed_count == band_plan.masked_count == 24
        and band_plan.plan_digest == _digest(band_plan.payload_without_digest()),
        "band plan relation differs",
    )
    _check(type(cue) is types.MaskedAuditoryCue48V1, "cue type differs")
    _check(
        cue.schema == types.S2KZ_SCHEMA
        and all(
            type(item) is str and _DIGEST.fullmatch(item) is not None
            for item in (
                cue.pcm_payload_digest,
                cue.receptor_state_digest,
                cue.receptor_values_digest,
                cue.observed_values_digest,
                cue.config_digest,
                cue.cue_digest,
            )
        )
        and cue.config_digest == config.config_digest
        and type(cue.auditory_source_clock_id) is str
        and _IDENTIFIER.fullmatch(cue.auditory_source_clock_id) is not None
        and type(cue.auditory_window_start_tick) is int
        and type(cue.auditory_window_end_tick) is int
        and 0 <= cue.auditory_window_start_tick < cue.auditory_window_end_tick
        and type(cue.values) is tuple
        and len(cue.values) == 48
        and cue.band_plan_digest == band_plan.plan_digest
        and all(type(cue.values[index]) in (int, float) for index in types.OBSERVED_BANDS)
        and all(
            math.isfinite(float(cue.values[index]))
            and 0.0 <= float(cue.values[index]) <= 1.0
            for index in types.OBSERVED_BANDS
        )
        and all(cue.values[index] is None for index in types.MASKED_BANDS)
        and cue.observed_values_digest
        == _digest([float(cue.values[index]) for index in types.OBSERVED_BANDS])
        and cue.cue_digest == _digest(cue.payload_without_digest()),
        "cue relation differs",
    )
    fast = state.tspm_state.fast_state
    if state.generation:
        _check(
            fast.auditory_source_clock_id == cue.auditory_source_clock_id
            and fast.auditory_last_end_tick is not None
            and cue.auditory_window_start_tick >= fast.auditory_last_end_tick
            and cue.auditory_window_end_tick > fast.auditory_last_end_tick,
            "native auditory cue time differs",
        )
    return config, state, cue, band_plan


def _record(role, slot_id, slot_digest, values, support, threshold, cue):
    eligible = values is not None
    if eligible:
        terms = tuple(
            abs(values[index] - float(cue.values[index]))
            for index in types.OBSERVED_BANDS
        )
        distance = sum(terms) / 24
        matched = distance <= threshold
        comparisons = len(terms)
        terms_digest = _digest(list(terms))
        value_digest = _digest(list(values))
    else:
        distance = None
        matched = False
        comparisons = 0
        terms_digest = None
        value_digest = None
    payload = {
        "bank_role": role,
        "slot_id": slot_id,
        "slot_digest": slot_digest,
        "eligible": eligible,
        "stable_support": support,
        "match_threshold": threshold,
        "observed_distance": distance,
        "observed_match": matched,
        "observed_comparison_count": comparisons,
        "distance_terms_digest": terms_digest,
        "candidate_values_digest": value_digest,
    }
    record = types.AuditorySlotScanRecordV1(
        role,
        slot_id,
        slot_digest,
        eligible,
        support,
        threshold,
        distance,
        matched,
        comparisons,
        terms_digest,
        value_digest,
        _digest(payload),
    )
    candidate = _RawCandidate(slot_digest, values, value_digest) if matched else None
    return record, candidate


def _close(role, capacity, records, matches):
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
    comparisons = sum(item.observed_comparison_count for item in records)
    payload = {
        "bank_role": role,
        "capacity": capacity,
        "record_digests": [item.record_digest for item in records],
        "eligible_count": eligible,
        "match_count": len(ordered),
        "matched_slot_digests": [item.slot_digest for item in ordered],
        "status": status,
        "comparison_count": comparisons,
    }
    return (
        types.AuditoryBankScanFindingV1(
            role,
            capacity,
            tuple(records),
            eligible,
            len(ordered),
            tuple(item.slot_digest for item in ordered),
            status,
            comparisons,
            _digest(payload),
        ),
        ordered,
    )


def _scan_b4(config, state, cue):
    records, matches = [], []
    threshold = config.tspm_config.fast_config.auditory_match_threshold
    for entry in state.b4_state.entries:
        values = _auditory(entry.values[:48], "B4") if entry.occupied else None
        record, candidate = _record(
            "B4_RECENT",
            entry.slot_id,
            _digest(comparison._canonical(entry)),
            values,
            None,
            threshold,
            cue,
        )
        records.append(record)
        if candidate is not None:
            matches.append(candidate)
    return _close("B4_RECENT", 9, records, matches)


def _scan_fast(config, state, cue):
    records, matches = [], []
    threshold = config.tspm_config.fast_config.auditory_match_threshold
    for slot in state.tspm_state.fast_state.slots:
        values = _auditory(slot.auditory_values, "Fast") if slot.occupied else None
        record, candidate = _record(
            "TSPM_FAST",
            slot.slot_id,
            slot.digest(),
            values,
            slot.support_count if slot.occupied else None,
            threshold,
            cue,
        )
        records.append(record)
        if candidate is not None:
            matches.append(candidate)
    return _close("TSPM_FAST", 3, records, matches)


def _scan_slow(config, state, cue):
    records, matches = [], []
    threshold = config.profile.profile.auditory_config.match_threshold
    for slot in state.tspm_state.auditory_ppb1_state.slots:
        stable = slot.occupied and slot.support_count is not None and slot.support_count >= 3
        values = _auditory(slot.prototype_values, "Slow") if stable else None
        record, candidate = _record(
            "B_STABLE_AUDITORY",
            slot.slot_id,
            _digest(slot.canonical_payload()),
            values,
            slot.support_count if stable else None,
            threshold,
            cue,
        )
        records.append(record)
        if candidate is not None:
            matches.append(candidate)
    return _close("B_STABLE_AUDITORY", 8, records, matches)


def _area(area, status, parents, selected):
    value_digest = selected[0].values_digest if selected else None
    masked = tuple(selected[0].values[index] for index in types.MASKED_BANDS) if selected else ()
    payload = {
        "area": area,
        "status": status,
        "parent_scan_digests": list(parents),
        "provenance_slot_digests": [item.slot_digest for item in selected],
        "candidate_values_digest": value_digest,
        "masked_values": list(masked),
        "public_candidate_count": 1 if selected else 0,
    }
    return types.AuditoryAreaFindingV1(
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
        matches[0]
        for scan, matches in ((b4_scan, b4_matches), (fast_scan, fast_matches))
        if scan.match_count == 1
    )
    if len(candidates) == 2:
        same = candidates[0].values_digest == candidates[1].values_digest and candidates[0].values == candidates[1].values
        return (
            _area("A_RECENT", "A_RECENT_APPLICABLE" if same else "A_RECENT_INTERNAL_CONFLICT", parents, candidates if same else ()),
            48,
        )
    if len(candidates) == 1:
        return _area("A_RECENT", "A_RECENT_APPLICABLE", parents, candidates), 0
    if b4_scan.eligible_count == fast_scan.eligible_count == 0:
        return _area("A_RECENT", "A_RECENT_ABSENT_VALID", parents, ()), 0
    return _area("A_RECENT", "A_RECENT_NOT_APPLICABLE", parents, ()), 0


def _resolve_stable(scan, matches):
    if scan.match_count > 1:
        status, selected = "B_STABLE_AUDITORY_INTERNAL_AMBIGUITY", ()
    elif scan.match_count == 1:
        status, selected = "B_STABLE_AUDITORY_APPLICABLE", matches
    elif scan.eligible_count == 0:
        status, selected = "B_STABLE_AUDITORY_ABSENT_VALID", ()
    else:
        status, selected = "B_STABLE_AUDITORY_NOT_APPLICABLE", ()
    return _area("B_STABLE_AUDITORY", status, (scan.scan_digest,), selected)


def _choose(a, b):
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


def _make_hypothesis(area, a, b, cue, plan, state_digest):
    source = a if area == "A_RECENT" else b
    _check(source.public_candidate_count == 1, "hypothesis source is not unique")
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
    return types.AuditoryPartialCueHypothesis48V1(
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
        _digest(payload),
    )


def _ledger(scans, equality, hypothesis_count, output_size):
    compared = sum(scan.comparison_count for scan in scans)
    payload = {
        "b4_slot_scan_count": 9,
        "fast_slot_scan_count": 3,
        "auditory_slow_slot_scan_count": 8,
        "total_slot_scan_count": 20,
        "observed_comparison_count": compared,
        "internal_equality_comparison_count": equality,
        "total_value_comparison_count": compared + equality,
        "hypothesis_value_count": hypothesis_count,
        "logical_operation_count": 14,
        "memory_receptor_consumer_context_or_field_call_count": 0,
        "serialized_output_bytes": output_size,
    }
    return types.AuditoryPartialCueResourceLedgerV1(*payload.values(), _digest(payload))


def _assemble(config, state, cue, plan, scans, a, b, equality, decision, admitted):
    hypothesis = _make_hypothesis(admitted, a, b, cue, plan, state.state_digest) if admitted else None
    size = 0
    for _ in range(8):
        ledger = _ledger(scans, equality, len(hypothesis.proposed_values) if hypothesis else 0, size)
        payload = {
            "schema": types.S2KZ_SCHEMA,
            "function_role": "DIRECT_AUDITORY_SLOT_SCAN_BASELINE",
            "source_digests": [types.S2KX_CONTRACT_SHA256, types.S2KY_RESULT_SHA256],
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
        result = types.AuditoryPartialCueRetrievalResultV1(
            "DIRECT_AUDITORY_SLOT_SCAN_BASELINE",
            (types.S2KX_CONTRACT_SHA256, types.S2KY_RESULT_SHA256),
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
            _digest(payload),
        )
        next_size = len(_bytes(result.canonical_payload()))
        if next_size == size:
            _check(next_size < 32_768, "output exceeds bound")
            _check(ledger.total_value_comparison_count <= 528, "comparison bound exceeded")
            return result
        size = next_size
    _check(False, "output size did not stabilize")


def form_direct_auditory_slot_scan_baseline_336(*, config, state, cue, band_plan):
    """Recompute the complete auditory scan without primary decision helpers."""

    config, state, cue, plan = _validate_inputs(config, state, cue, band_plan)
    before = state.state_digest
    b4_scan, b4_matches = _scan_b4(config, state, cue)
    fast_scan, fast_matches = _scan_fast(config, state, cue)
    slow_scan, slow_matches = _scan_slow(config, state, cue)
    scans = (b4_scan, fast_scan, slow_scan)
    a, equality = _resolve_recent(b4_scan, b4_matches, fast_scan, fast_matches)
    b = _resolve_stable(slow_scan, slow_matches)
    decision, admitted = _choose(a, b)
    result = _assemble(config, state, cue, plan, scans, a, b, equality, decision, admitted)
    _check(state.state_digest == before, "baseline changed memory state")
    return result


__all__: tuple[str, ...] = ()
