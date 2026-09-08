"""Independent traversal, intersection and decision table; separately charged verification."""
from dataclasses import asdict, replace
from tools import _s2ns_private_two_view as s


def _scan(config, state, inventory, view):
    s.validate_view(config, state, view)
    rows = []
    for bank, slots in enumerate((state.b4_state.entries, state.tspm_state.fast_state.slots,
                                  state.tspm_state.auditory_ppb1_state.slots)):
        for slot in slots:
            values = None
            if slot.occupied:
                if bank == 0:
                    values = slot.values[:48]
                elif bank == 1:
                    values = slot.auditory_values
                elif slot.support_count >= config.profile.profile.auditory_config.stable_after:
                    values = slot.prototype_values
            terms = []
            if values is not None:
                for position in range(24):
                    terms.append(abs(view.values[position]-values[view.indices[position]]))
            statistic = None
            if terms:
                statistic = sum(terms)/24 if bank == 2 else max(terms)
            threshold = (0.1, 0.1, 0.01)[bank]
            generation = inventory.slots[len(rows)].generation
            rows.append(s.Row(len(rows), None if generation is None else generation.generation_digest,
                values is not None, tuple(terms), statistic, threshold,
                statistic is not None and statistic <= threshold))
    return s.seal_scan(implementation="DIRECT_BASELINE", view=view.name, view_digest=view.view_digest,
        endpoint_digest=s.digest(asdict(view.endpoint)), inventory_digest=inventory.inventory_digest,
        prestate_digest=state.state_digest, poststate_digest=state.state_digest,
        rows=tuple(rows), comparisons=sum(map(lambda x: len(x.terms), rows)))


def _decision(arm, masks, eligible, state):
    groups = [[i for i in range(lo, hi) if masks[i]] for lo, hi in ((0, 9), (9, 12), (12, 20))]
    n0, n1, n2 = map(len, groups)
    a, b, eq = [], groups[2] if n2 == 1 else [], 0
    if n0 > 1 or n1 > 1:
        ast = "INTERNAL_AMBIGUITY"
    elif n0 == n1 == 1:
        first = state.b4_state.entries[groups[0][0]].values[:48]
        second = state.tspm_state.fast_state.slots[groups[1][0]-9].auditory_values
        equal = [first[i] == second[i] for i in range(48)]
        eq = 48
        if all(equal) and s.digest(list(first)) == s.digest(list(second)):
            a, ast = groups[0]+groups[1], "APPLICABLE"
        else:
            ast = "INTERNAL_CONFLICT"
    elif n0+n1 == 1:
        a, ast = groups[0]+groups[1], "APPLICABLE"
    else:
        ast = "ABSENT_VALID" if not any(eligible[:12]) else "NOT_APPLICABLE"
    bst = "INTERNAL_AMBIGUITY" if n2 > 1 else "APPLICABLE" if n2 else (
        "NOT_APPLICABLE" if any(eligible[12:]) else "ABSENT_VALID")
    area, provenance = None, []
    if "INTERNAL_AMBIGUITY" in (ast, bst):
        decision = "ABSTAIN_INTERNAL_AMBIGUITY"
    elif ast == "INTERNAL_CONFLICT":
        decision = "ABSTAIN_INTERNAL_CONFLICT"
    elif a and b:
        decision = "ABSTAIN_AMBIGUOUS_CONTEXT"
    elif a or b:
        decision = "ADMIT_SINGLE_CONTEXT"
        area, provenance = ("A_RECENT", a) if a else ("B_STABLE_AUDITORY", b)
    else:
        decision = "ABSTAIN_NO_CONTEXT" if ast == bst == "ABSENT_VALID" else "ABSTAIN_NO_APPLICABLE_CONTEXT"
    return s.Admission(arm, "A_RECENT_"+ast, "B_STABLE_AUDITORY_"+bst, decision, area,
                       tuple(provenance), tuple(i for i in range(20) if masks[i]), eq)


def direct(*, config, state, inventory, lower, upper):
    s.validate_inventory(config, state, inventory)
    before = s.digest(asdict(state))
    scans, decisions = [], []
    for name, view in zip(s.VIEWS, (lower, upper), strict=True):
        if view is None:
            continue
        s.require(type(view) is s.View and view.name == name, "VIEW_BINDING_INVALID")
        scanned = _scan(config, state, inventory, view)
        scans.append(scanned)
        decisions.append(_decision(name, [r.matched for r in scanned.rows], [r.eligible for r in scanned.rows], state))
    if len(scans) != 2:
        decisions.append(s.Admission("CONFIRMED", "NOT_EVALUATED", "NOT_EVALUATED",
            "ABSTAIN_INSUFFICIENT_EVIDENCE", None, (), (), 0))
    else:
        s.require(lower.endpoint == upper.endpoint, "ENDPOINT_MISMATCH")
        lower_hits = {(r.index, r.generation_digest) for r in scans[0].rows if r.matched}
        upper_hits = {(r.index, r.generation_digest) for r in scans[1].rows if r.matched}
        shared = lower_hits.intersection(upper_hits)
        decisions.append(_decision("CONFIRMED", [(r.index, r.generation_digest) in shared for r in scans[0].rows],
            [r.eligible for r in scans[0].rows], state))
    s.require(before == s.digest(asdict(state)), "STATE_MUTATED")
    s.validate_shared(inventory, lower, upper)
    return s.finish("DIRECT_BASELINE", inventory, scans, decisions)


def semantics(result):
    payload = result.payload()
    payload.pop("implementation")
    for scan in payload["scans"]:
        scan.pop("implementation")
        scan.pop("scan_digest")
    return payload


def verify_pair(primary, baseline, **inputs):
    """One independent rescan, no formation/receptor replay; no expected outcomes."""
    expected = direct(**inputs)
    for role, result in (("PRIMARY", primary), ("DIRECT_BASELINE", baseline)):
        s.require(type(result) is s.Result and result.schema == s.SCHEMA
            and result.implementation == role and result.result_digest == s.digest(result.payload()), "RESULT_DIGEST_INVALID")
        for scan in result.scans:
            view = inputs["lower"] if scan.view == s.VIEWS[0] else inputs["upper"]
            s.require(view is not None and scan.implementation == role, "SCAN_BINDING_INVALID")
            s.validate_scan(scan, inputs["inventory"], view)
        s.require(s.canonical(semantics(result)) == s.canonical(semantics(expected)), "RESULT_BINDING_INVALID")
        s.require(len(s.canonical(asdict(result))) <= s.MAX_RESULT_BYTES, "RESULT_SIZE_EXCEEDED")
    proof = dict(status="TECHNICALLY_VALID", primary_digest=primary.result_digest,
        baseline_digest=baseline.result_digest, inventory_digest=inputs["inventory"].inventory_digest,
        verification_scans=len(expected.scans), verification_slot_inspections=20*len(expected.scans),
        verification_band_differences=expected.band_differences,
        verification_equality_comparisons=expected.equality_comparisons,
        inventory_validation_passes=1, native_slots_validated=20,
        scan_row_validations=20*(len(primary.scans)+len(baseline.scans)),
        view_validations=len(expected.scans), no_receptor_or_memory_replay=True,
        limitation="Generation/source links checked against supplied inventory; full formation-chain proof is an upstream boundary.")
    proof["verification_digest"] = s.digest(proof)
    return proof
