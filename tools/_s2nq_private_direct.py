"""Independent slot traversal and decision table, no production scan helpers."""
from dataclasses import asdict
from tools import _s2nq_private_mask_scan as s


def direct(*, config, state, cue):
    s.validate_inputs(config, state, cue)
    before = s.digest(asdict(state))
    records, selected, populated = [], [[], [], []], [0, 0, 0]
    for bank in range(3):
        entries = (state.b4_state.entries, state.tspm_state.fast_state.slots,
                   state.tspm_state.auditory_ppb1_state.slots)[bank]
        for slot in entries:
            values, support = None, None
            if bank == 0:
                slot_hash = s.digest(s.ne.comparison._canonical(slot))
                if slot.occupied:
                    values = slot.values[:48]
            elif bank == 1:
                slot_hash = slot.digest()
                if slot.occupied:
                    values, support = slot.auditory_values, slot.support_count
            else:
                slot_hash = s.digest(slot.canonical_payload())
                if slot.occupied:
                    support = slot.support_count
                    if support >= config.profile.profile.auditory_config.stable_after:
                        values = slot.prototype_values
            terms = []
            if values is not None:
                populated[bank] += 1
                for position in range(24):
                    original_index = cue.band_plan.observed[position]
                    terms.append(abs(values[original_index] - cue.values[position]))
            threshold = (0.1, 0.1, 0.01)[bank]
            statistic = None
            if terms:
                statistic = sum(terms)/24 if bank == 2 else max(terms)
            match = statistic is not None and statistic <= threshold
            values_hash = s.digest(list(values)) if values is not None else None
            records.append(s.Row(s.ROLES[bank], slot.slot_id, slot_hash, values is not None, support,
                                 values_hash, tuple(terms), statistic, threshold, match))
            if match:
                selected[bank].append((slot_hash, values, values_hash))
    counts = tuple(len(x) for x in selected)
    equality, a, b = 0, [], selected[2] if counts[2] == 1 else []
    if max(counts[:2]) > 1:
        a_state = "INTERNAL_AMBIGUITY"
    elif counts[:2] == (1, 1):
        equality = 48
        equal_components = [x == y for x, y in zip(selected[0][0][1], selected[1][0][1], strict=True)]
        if all(equal_components) and selected[0][0][2] == selected[1][0][2]:
            a, a_state = selected[0]+selected[1], "APPLICABLE"
        else:
            a_state = "INTERNAL_CONFLICT"
    elif sum(counts[:2]) == 1:
        a, a_state = selected[0]+selected[1], "APPLICABLE"
    else:
        a_state = "ABSENT_VALID" if sum(populated[:2]) == 0 else "NOT_APPLICABLE"
    b_state = ("INTERNAL_AMBIGUITY" if counts[2] > 1 else "APPLICABLE" if counts[2] == 1
               else "ABSENT_VALID" if populated[2] == 0 else "NOT_APPLICABLE")
    if "INTERNAL_AMBIGUITY" in (a_state, b_state):
        decision = "ABSTAIN_INTERNAL_AMBIGUITY"
    elif a_state == "INTERNAL_CONFLICT":
        decision = "ABSTAIN_INTERNAL_CONFLICT"
    else:
        number = int(bool(a)) + int(bool(b))
        decision = {1: "ADMIT_SINGLE_CONTEXT", 2: "ABSTAIN_AMBIGUOUS_CONTEXT"}.get(number)
        if decision is None:
            decision = "ABSTAIN_NO_CONTEXT" if (a_state, b_state) == ("ABSENT_VALID", "ABSENT_VALID") else "ABSTAIN_NO_APPLICABLE_CONTEXT"
    h = None
    if decision == "ADMIT_SINGLE_CONTEXT":
        source = a if a else b
        h = s.Hypothesis("A_RECENT" if a else "B_STABLE_AUDITORY", tuple(x[0] for x in source), source[0][2],
                         cue.band_plan.complement, tuple(source[0][1][i] for i in cue.band_plan.complement))
    s.require(s.digest(asdict(state)) == before, "STATE_MUTATED")
    return s.finish(implementation="DIRECT_BASELINE", view=cue.band_plan.view,
        config_digest=config.config_digest, cue_digest=cue.cue_digest, prestate_digest=state.state_digest,
        poststate_digest=state.state_digest, rows=tuple(records), a_status="A_RECENT_"+a_state,
        b_status="B_STABLE_AUDITORY_"+b_state, decision=decision, hypothesis=h,
        comparisons=sum(len(r.terms) for r in records), equality_comparisons=equality)


def semantics(result):
    return {k: v for k, v in result.payload().items() if k != "implementation"}


def verify(result, *, config, state, cue):
    """Additional verification arithmetic, explicitly outside execution budgets."""
    s.require(type(result) is s.Result and result.result_digest == s.digest(result.payload())
              and result.implementation in ("PRIMARY", "DIRECT_BASELINE"), "RESULT_DIGEST_INVALID")
    expected = direct(config=config, state=state, cue=cue)
    s.require(s.canonical(semantics(result)) == s.canonical(semantics(expected)), "SCAN_BINDING_INVALID")
    s.require(len(s.canonical(asdict(result))) <= s.MAX_ARM_BYTES, "ARM_SIZE_EXCEEDED")
    return dict(slot_inspections=20, band_differences=expected.comparisons,
                equality_comparisons=expected.equality_comparisons)
