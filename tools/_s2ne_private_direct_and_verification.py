"""Independent A scan and read-only S2-NE evidence checking, without expectations."""

from tools import _s2kz_private_direct_auditory_slot_scan_baseline as direct
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as kz
from tools import _s2ne_private_auditory_transfer as ne


def _direct_a(config, state, cue, ordinal):
    rows, hits = [], []
    role = ("B4_RECENT", "TSPM_FAST")[ordinal]
    slots = (state.b4_state.entries, state.tspm_state.fast_state.slots)[ordinal]
    for slot in slots:
        sd = direct._digest(direct.comparison._canonical(slot)) if ordinal == 0 else slot.digest()
        values = None if not slot.occupied else direct._auditory(
            slot.values[:48] if ordinal == 0 else slot.auditory_values, role)
        differences = []
        if values is not None:
            for i in range(24):
                differences.append(abs(values[i] - float(cue.values[i])))
        distance = max(differences) if differences else None
        threshold = config.tspm_config.fast_config.auditory_match_threshold
        payload = {
            "bank_role": role, "slot_id": slot.slot_id, "slot_digest": sd,
            "eligible": values is not None,
            "stable_support": slot.support_count if ordinal == 1 and slot.occupied else None,
            "match_threshold": threshold, "observed_distance": distance,
            "observed_match": distance is not None and distance <= threshold,
            "observed_comparison_count": len(differences),
            "distance_terms_digest": direct._digest(differences) if differences else None,
            "candidate_values_digest": direct._digest(list(values)) if values is not None else None,
        }
        rows.append(kz.AuditorySlotScanRecordV1(**payload, record_digest=direct._digest(payload)))
        if payload["observed_match"]:
            hits.append(direct._RawCandidate(sd, values, payload["candidate_values_digest"]))
    return direct._close(role, (9, 3)[ordinal], rows, hits)


def direct_retrieve(*, rule, config, state, cue, band_plan):
    ne.check(rule in ne.RULES)
    if rule == ne.REFERENCE:
        value = direct.form_direct_auditory_slot_scan_baseline_336(
            config=config, state=state, cue=cue, band_plan=band_plan)
    else:
        config, state, cue, plan = direct._validate_inputs(config, state, cue, band_plan)
        b4, bm = _direct_a(config, state, cue, 0)
        fast, fm = _direct_a(config, state, cue, 1)
        slow, sm = direct._scan_slow(config, state, cue)
        a, equality = direct._resolve_recent(b4, bm, fast, fm)
        b = direct._resolve_stable(slow, sm)
        decision, admitted = direct._choose(a, b)
        value = direct._assemble(config, state, cue, plan, (b4, fast, slow),
                                 a, b, equality, decision, admitted)
    direct._validate_inputs(config, state, cue, band_plan)
    ne.check(value.prestate_digest == state.state_digest == value.poststate_digest)
    return ne.wrap(rule, "DIRECT_BASELINE", value)


def verify_arm(*, arm, config, state, cue, band_plan):
    """Reconstruct recorded rows, not an invocation of either retrieval arm."""
    config, state, cue, plan = direct._validate_inputs(config, state, cue, band_plan)
    ne.check(type(arm) is ne.AuditoryTransferArmV1 and arm.schema == ne.SCHEMA)
    ne.check(arm.rule in ne.RULES and arm.implementation in ("PRIMARY", "DIRECT_BASELINE"))
    ne.check(arm.sources == ne.source_bindings()
             and arm.arm_digest == direct._digest(arm.payload_without_digest()))
    result = kz._validate_result(arm.evidence)
    ne.check(result.function_role == ("AUDITORY_PARTIAL_CUE_RETRIEVAL" if arm.implementation == "PRIMARY"
                                     else "DIRECT_AUDITORY_SLOT_SCAN_BASELINE"))
    ne.check(result.state_digest == state.state_digest and result.config_digest == config.config_digest
             and result.cue_digest == cue.cue_digest and result.band_plan_digest == plan.plan_digest)
    ne.check(len(direct._bytes(arm.canonical_payload())) < ne.MAX_OUTPUT_BYTES, "S2NE_RESOURCE_EXCEEDED")
    banks = (state.b4_state.entries, state.tspm_state.fast_state.slots,
             state.tspm_state.auditory_ppb1_state.slots)
    rebuilt, candidates = [], []
    for bank, (slots, scan) in enumerate(zip(banks, result.bank_scans, strict=True)):
        matches = []
        threshold = (config.profile.profile.auditory_config.match_threshold if bank == 2
                     else config.tspm_config.fast_config.auditory_match_threshold)
        for slot, record in zip(slots, scan.records, strict=True):
            eligible = slot.occupied and (bank != 2 or slot.support_count >= 3)
            support = slot.support_count if bank != 0 and eligible else None
            sd = (slot.digest() if bank == 1 else direct._digest(
                slot.canonical_payload() if bank == 2 else direct.comparison._canonical(slot)))
            raw = (slot.values[:48] if bank == 0 else
                   slot.auditory_values if bank == 1 else slot.prototype_values) if eligible else None
            values = direct._auditory(raw, "recorded candidate") if eligible else None
            terms = [abs(values[i] - float(cue.values[i])) for i in range(24)] if eligible else []
            statistic = None
            if eligible:
                statistic = max(terms) if bank < 2 and arm.rule == ne.ALTERNATIVE else sum(terms) / 24
            expected = dict(bank_role=kz.BANK_ROLES[bank], slot_id=slot.slot_id, slot_digest=sd,
                            eligible=eligible, stable_support=support, match_threshold=threshold,
                            observed_distance=statistic, observed_match=eligible and statistic <= threshold,
                            observed_comparison_count=len(terms),
                            distance_terms_digest=direct._digest(terms) if eligible else None,
                            candidate_values_digest=direct._digest(list(values)) if eligible else None)
            ne.check(record.payload_without_digest() == expected)
            if expected["observed_match"]:
                matches.append(direct._RawCandidate(sd, values, expected["candidate_values_digest"]))
        closed, ordered = direct._close(kz.BANK_ROLES[bank], kz.BANK_CAPACITIES[bank], list(scan.records), matches)
        ne.check(closed == scan)
        rebuilt.append(closed)
        candidates.append(ordered)
    a, equality = direct._resolve_recent(rebuilt[0], candidates[0], rebuilt[1], candidates[1])
    b = direct._resolve_stable(rebuilt[2], candidates[2])
    decision, admitted = direct._choose(a, b)
    hypothesis = direct._make_hypothesis(admitted, a, b, cue, plan, state.state_digest) if admitted else None
    ne.check((result.a_recent, result.b_stable_auditory, result.decision, result.hypothesis)
             == (a, b, decision, hypothesis))
    ledger = direct._ledger(rebuilt, equality, 24 if hypothesis else 0,
                            len(direct._bytes(result.canonical_payload())))
    ne.check(result.resource_ledger == ledger)
    return "VERIFIED_READ_ONLY"


def compare_technical(primary, baseline):
    """Compare functional bindings, never role-dependent envelope digests."""
    ne.check(primary.rule == baseline.rule and primary.sources == baseline.sources)
    left, right = primary.evidence, baseline.evidence
    return (left.bank_scans, left.a_recent, left.b_stable_auditory, left.decision, left.hypothesis,
            left.config_digest, left.state_digest, left.cue_digest, left.band_plan_digest) == (
                right.bank_scans, right.a_recent, right.b_stable_auditory, right.decision, right.hypothesis,
                right.config_digest, right.state_digest, right.cue_digest, right.band_plan_digest)


__all__ = ()
