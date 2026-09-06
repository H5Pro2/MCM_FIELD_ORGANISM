"""Independent direct A-decision table; consumes hits, never measures distances."""

from tools import _s2nc_private_rule_comparison as types


def decide(case, b4_hits, fast_hits):
    types.validate_case(case)
    for hits, bank in ((b4_hits, case.b4), (fast_hits, case.fast)):
        types.require(type(hits) is tuple and all(type(i) is int for i in hits)
                      and tuple(sorted(set(hits))) == hits
                      and all(0 <= i < len(bank) and bank[i] is not None for i in hits),
                      "BASELINE_HITS_INVALID")
    counts = (len(b4_hits), len(fast_hits))
    if any(n >= 2 for n in counts):
        return types.Decision("A_RECENT_INTERNAL_AMBIGUITY", (), None), 0
    if counts == (0, 0):
        occupied = any(item is not None for bank in (case.b4, case.fast) for item in bank)
        status = "A_RECENT_NOT_APPLICABLE" if occupied else "A_RECENT_ABSENT_VALID"
        return types.Decision(status, (), None), 0
    if counts == (1, 1):
        left = case.b4[b4_hits[0]]
        right = case.fast[fast_hits[0]]
        equality = [left.values[i] == right.values[i] for i in range(48)]
        same_digest = types.digest(left.values) == types.digest(right.values)
        if False in equality or not same_digest:
            return types.Decision("A_RECENT_INTERNAL_CONFLICT", (), None), 48
        return types.Decision("A_RECENT_APPLICABLE", (left.source_id, right.source_id),
                              types.digest(left.values)), 48
    item = case.b4[b4_hits[0]] if counts == (1, 0) else case.fast[fast_hits[0]]
    return types.Decision("A_RECENT_APPLICABLE", (item.source_id,), types.digest(item.values)), 0
