"""Private S2-NE arms. Only A applicability differs; no main-run entry point."""

from dataclasses import dataclass
import hashlib
from pathlib import Path

from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as kz

MAIN_GATE = False
REFERENCE = "HISTORICAL_SUM_L1_24"
ALTERNATIVE = "ALL_BANDS_24"
RULES = (REFERENCE, ALTERNATIVE)
MAX_OUTPUT_BYTES = 32768
MAX_RECORDING_BYTES = 4194304
MAIN_BUDGET = (20, 13, 52, 1040, 24960, 2496, 27456)
SCHEMA = "s2ne.private-auditory-transfer.v1"
ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = (
    "docs/S2NE_PRIVATER_AUDITIVER_MEMORY_TRANSFER_VERTRAG.md",
    "tools/_s2ne_private_auditory_transfer.py",
    "tools/_s2ne_private_direct_and_verification.py",
    "tools/_s2ne_private_source_binding.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_direct_auditory_slot_scan_baseline.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
)


def check(condition, code="S2NE_BINDING_INVALID"):
    if not condition:
        raise kz.S2KZError(code, code)


def source_bindings():
    return tuple((name, hashlib.sha256((ROOT / name).read_bytes()).hexdigest())
                 for name in SOURCE_PATHS)


@dataclass(frozen=True, slots=True)
class AuditoryTransferArmV1:
    rule: str
    implementation: str
    sources: tuple[tuple[str, str], ...]
    evidence: kz.AuditoryPartialCueRetrievalResultV1
    arm_digest: str
    schema: str = SCHEMA

    def payload_without_digest(self):
        return dict(schema=self.schema, rule=self.rule, implementation=self.implementation,
                    sources=[list(pair) for pair in self.sources],
                    evidence_digest=self.evidence.result_digest)

    def canonical_payload(self):
        return {**self.payload_without_digest(), "arm_digest": self.arm_digest,
                "evidence": self.evidence.canonical_payload()}


def wrap(rule, implementation, evidence):
    check(rule in RULES and implementation in ("PRIMARY", "DIRECT_BASELINE"))
    kz._validate_result(evidence)
    value = AuditoryTransferArmV1(rule, implementation, source_bindings(), evidence, "")
    from dataclasses import replace
    value = replace(value, arm_digest=kz.digest(value.payload_without_digest()))
    check(len(kz.canonical_bytes(value.canonical_payload())) < MAX_OUTPUT_BYTES,
          "S2NE_RESOURCE_EXCEEDED")
    return value


def _a_scan(config, state, cue, bank):
    entries = state.b4_state.entries if bank == 0 else state.tspm_state.fast_state.slots
    role, capacity = kz.BANK_ROLES[bank], kz.BANK_CAPACITIES[bank]
    threshold = config.tspm_config.fast_config.auditory_match_threshold
    records, matches = [], []
    for slot in entries:
        values = None
        if slot.occupied:
            raw = slot.values[:48] if bank == 0 else slot.auditory_values
            values = kz._auditory_values(raw, role)
        slot_digest = kz.digest(comparison._canonical(slot)) if bank == 0 else slot.digest()
        support = slot.support_count if bank == 1 and slot.occupied else None
        terms = tuple(abs(values[i] - float(cue.values[i])) for i in kz.OBSERVED_BANDS) if values is not None else ()
        statistic = max(terms) if terms else None
        matched = statistic is not None and statistic <= threshold
        values_digest = kz.digest(list(values)) if values is not None else None
        payload = dict(bank_role=role, slot_id=slot.slot_id, slot_digest=slot_digest,
                       eligible=values is not None, stable_support=support,
                       match_threshold=threshold, observed_distance=statistic,
                       observed_match=matched, observed_comparison_count=len(terms),
                       distance_terms_digest=kz.digest(list(terms)) if terms else None,
                       candidate_values_digest=values_digest)
        records.append(kz.AuditorySlotScanRecordV1(**payload, record_digest=kz.digest(payload)))
        if matched:
            matches.append(kz._Candidate(slot_digest, values, values_digest))
    return kz._finish_bank(role, capacity, records, matches)


def retrieve(*, rule, config, state, cue, band_plan):
    check(rule in RULES)
    if rule == REFERENCE:
        result = kz.form_auditory_partial_cue_retrieval_336(
            config=config, state=state, cue=cue, band_plan=band_plan)
    else:
        config, state, cue, plan = kz._state_and_cue(config, state, cue, band_plan)
        b4, b4_matches = _a_scan(config, state, cue, 0)
        fast, fast_matches = _a_scan(config, state, cue, 1)
        slow, slow_matches = kz._scan_slow(config, state, cue)
        a, equality = kz._resolve_a(b4, b4_matches, fast, fast_matches)
        b = kz._resolve_b(slow, slow_matches)
        decision, admitted = kz._decide(a, b)
        result = kz._assemble(function_role="AUDITORY_PARTIAL_CUE_RETRIEVAL",
                              config=config, state=state, cue=cue, plan=plan,
                              scans=(b4, fast, slow), a=a, b=b, equality_count=equality,
                              decision=decision, admitted=admitted)
    kz._state_and_cue(config, state, cue, band_plan)
    check(state.state_digest == result.prestate_digest == result.poststate_digest)
    return wrap(rule, "PRIMARY", result)


__all__ = ()
