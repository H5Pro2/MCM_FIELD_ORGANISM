"""Evaluation roles never enter the two-view scanner or admission table."""
from dataclasses import asdict, dataclass
from tools import _s2ns_private_two_view as s


@dataclass(frozen=True, slots=True)
class Expectation:
    case_id: str
    target_source: str | None
    expected_area: str | None
    subtype: str
    slot_sources: tuple[tuple[str, ...], ...]
    original_formations: tuple[tuple[float, ...], ...] | None
    formation_binding_digests: tuple[str, ...]


def retention(pairs):
    d = sum(a for a, b in pairs)
    r = sum(a and b for a, b in pairs)
    lost = sum(a and not b for a, b in pairs)
    return dict(N=len(pairs), D=d, R=r, L=lost,
        status="ERHALTUNG_NICHT_GEPRUEFT" if d == 0 else "ASSESSED",
        gains=sum(not a and b for a, b in pairs))


def evaluate_case(result, verification, *, inventory, lower, upper, expectation):
    s.require(verification.get("status") == "TECHNICALLY_VALID"
        and verification.get("verification_digest") == s.digest({k: v for k, v in verification.items() if k != "verification_digest"})
        and verification.get("primary_digest") == result.result_digest
        and result.result_digest == s.digest(result.payload()) and result.inventory_digest == inventory.inventory_digest
        and verification.get("inventory_digest") == inventory.inventory_digest, "EVALUATION_REQUIRES_VERIFICATION")
    e = expectation
    s.require(type(e) is Expectation and s.identifier(e.case_id) and s.identifier(e.subtype)
        and (e.target_source is None or s.identifier(e.target_source))
        and e.expected_area in (None, "A_RECENT", "B_STABLE_AUDITORY")
        and type(e.slot_sources) is tuple and len(e.slot_sources) == 20
        and all(type(row) is tuple and all(s.identifier(x) for x in row) for row in e.slot_sources), "EXPECTATION_INVALID")
    s.require(type(e.formation_binding_digests) is tuple and s.hashes(*e.formation_binding_digests), "REFERENCE_BINDING_INVALID")
    if e.original_formations is not None:
        s.require(type(e.original_formations) is tuple
            and len(e.original_formations) == len(e.formation_binding_digests)
            and all(type(row) is tuple and len(row) == 48
                    and all(type(v) is float and 0 <= v <= 1 for v in row) for row in e.original_formations),
            "REFERENCE_BINDING_INVALID")
    target_slots = {i for i, sources in enumerate(e.slot_sources)
                    if e.target_source is not None and sources == (e.target_source,)}
    target_slots = {i for i in target_slots if inventory.slots[i].generation is not None}
    competition = any(sources and i not in target_slots for i, sources in enumerate(e.slot_sources))
    decisions = {a.arm: a for a in result.admissions}
    def good(a):
        return a.area is not None and a.area == e.expected_area and bool(a.provenance) and all(i in target_slots for i in a.provenance)
    joined = decisions["CONFIRMED"]
    comparisons = []
    for name, view in zip(s.VIEWS, (lower, upper), strict=True):
        if name not in decisions:
            continue
        single = decisions[name]
        scan = next(x for x in result.scans if x.view == name)
        s.require(type(view) is s.View and view.view_digest == scan.view_digest, "EVALUATION_VIEW_INVALID")
        reference = None
        if e.original_formations:
            projections = {tuple(row[i] for i in view.indices) for row in e.original_formations}
            reference = next(iter(projections)) if len(projections) == 1 else None
        variation = None if reference is None else view.values != reference
        target_eligible = [i for i in sorted(target_slots) if scan.rows[i].eligible]
        relation_pairs = [(i in single.matched_slots, i in joined.matched_slots) for i in target_eligible]
        correct_single, correct_joined = good(single), good(joined)
        false_single = single.area is not None and not correct_single
        false_joined = joined.area is not None and not correct_joined
        comparisons.append(dict(single=name, competition=competition, receptor_variation=variation,
            cue_candidate_deviation=None if not target_eligible else any(any(t != 0.0 for t in scan.rows[i].terms) for i in target_eligible),
            relationship_retention=retention(relation_pairs),
            relationship_by_area={area: retention([pair for i, pair in zip(target_eligible, relation_pairs, strict=True)
                if ("A_RECENT" if i < 12 else "B_STABLE_AUDITORY") == area]) for area in ("A_RECENT", "B_STABLE_AUDITORY")},
            public_retention=retention([(correct_single, correct_joined and (not correct_single or single.area == joined.area))]
                                      if e.target_source is not None else []),
            public_by_area={area: retention([(correct_single and single.area == area,
                                              correct_joined and joined.area == area)]
                if e.target_source is not None and e.expected_area == area else [])
                for area in ("A_RECENT", "B_STABLE_AUDITORY")},
            lost_target_slots=[i for i, pair in zip(target_eligible, relation_pairs, strict=True) if pair == (True, False)],
            public_loss=correct_single and not correct_joined, public_gain=not correct_single and correct_joined,
            new_false_admission=not false_single and false_joined,
            prevented_false_admission=false_single and not false_joined,
            false_admissions=(false_single, false_joined),
            false_relationships=tuple([i for i in a.matched_slots if i not in target_slots] for a in (single, joined)),
            decisions=(single.decision, joined.decision),
            ambiguity=tuple("AMBIGU" in a.decision or "CONFLICT" in a.decision for a in (single, joined))))
    result = dict(case_id=e.case_id, subtype=e.subtype, comparison_denominator=len(comparisons),
        record_digest=result.result_digest, evaluation_binding_digest=s.digest(asdict(e)),
        comparisons=comparisons, missing_reference_is_null=True, no_netting=True)
    result["evaluation_digest"] = s.digest(result)
    s.require(len(s.canonical(result)) <= 65536, "EVALUATION_SIZE_EXCEEDED")
    return result
