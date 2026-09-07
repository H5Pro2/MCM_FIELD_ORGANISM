"""Post-verification evaluation only. Roles never enter a comparison function."""

from dataclasses import asdict
from tools import _s2np_private_coverage_comparison as c


def retention(rows, axis):
    eligible = [r for r in rows if r["target_present"]]
    denominator = [r for r in eligible if r["before"][axis]]
    retained = sum(r["after"][axis] for r in denominator)
    lost = len(denominator) - retained
    return dict(N=len(eligible), D=len(denominator), R=retained, L=lost,
        status="ERHALTUNG_NICHT_GEPRUEFT" if not denominator else
               "LOSS_OBSERVED" if lost else "RETAINED_ON_OBSERVED_SUBSET")


def summarize(rows):
    relation, unique = retention(rows, "target_applicable"), retention(rows, "correct_unique")
    changed = [r for r in rows if r["subtype"] != "EXACT" and r["before_variation"] == "NON_BITIDENTICAL"
               and r["after_variation"] == "NON_BITIDENTICAL"]
    changed_retention = retention(changed, "target_applicable")
    new_false = sum(len(r["new_false_applicability"]) for r in rows)
    views = {}
    for side in ("before", "after"):
        views[side] = dict(panel_denominator=len(rows),
            correct_unique=sum(r[side]["correct_unique"] for r in rows),
            false_unique=sum(r[side]["false_unique"] for r in rows),
            ambiguous=sum(r[side]["ambiguous"] for r in rows),
            empty=sum(r[side]["empty"] for r in rows),
            nontarget_relation_denominator=sum(r["nontarget_count"] for r in rows),
            false_applicability=sum(len(r[side]["false_applicable_ids"]) for r in rows))
    improvement = (views["after"]["false_applicability"] < views["before"]["false_applicability"]
                   or views["after"]["correct_unique"] > views["before"]["correct_unique"])
    status = ("LOSSLESS_COVERAGE_CLAIM_FALSIFIED" if relation["L"] or unique["L"] or new_false else
              "ERHALTUNG_NICHT_GEPRUEFT" if changed_retention["D"] == 0 else
              "LIMITED_ADVANTAGE" if improvement else "NO_ADVANTAGE")
    return dict(relationship=relation, correct_unique=unique, changed_relationship=changed_retention,
        sides=views, new_false_applicability=new_false,
        relationship_gains=sum(r["relationship_gain"] for r in rows),
        unique_gains=sum(r["unique_gain"] for r in rows),
        relationship_loss_ids=[r["case_id"] for r in rows if r["relationship_loss"]],
        unique_loss_ids=[r["case_id"] for r in rows if r["unique_loss"]], status=status)


def _outcome(hits, target):
    return dict(hits=list(hits), target_applicable=target is not None and target in hits,
        correct_unique=target is not None and hits == (target,),
        false_unique=len(hits) == 1 and hits != (target,), ambiguous=len(hits) > 1,
        empty=len(hits) == 0, false_applicable_ids=[h for h in hits if h != target])


def _variation(cue, target):
    if target is None:
        return "NO_TARGET"
    return "BITIDENTICAL" if tuple(x.hex() for x in cue.values) == tuple(x.hex() for x in target.values) else "NON_BITIDENTICAL"


def evaluate(catalog, primary, verification, evaluation_plan, execution_digest, payload_hashes):
    """No source subtraction, scans, or receptor calls; consume verified findings."""
    c.fixed_inputs(catalog)
    c.check_hash(execution_digest)
    c.require(evaluation_plan == c.binding.evaluation_plan({"execution_digest": execution_digest}),
              "EVALUATION_PLAN_INVALID")
    c.require(type(primary) is tuple and len(primary) == 120, "EVALUATION_COUNT_INVALID")
    c.require(type(verification) is dict, "VERIFICATION_REQUIRED")
    v = dict(verification)
    recorded = v.pop("verification_digest", None)
    c.require(recorded == c.digest(v) and v.get("status") == "TECHNICALLY_VALID"
              and v.get("catalog_digest") == c.digest([asdict(item) for item in catalog])
              and v.get("primary_digest") == v.get("direct_digest") == c.digest([asdict(r) for r in primary])
              and len(v.get("receipts", ())) == 120, "VERIFICATION_REQUIRED")
    ids = tuple(f"np-a{n:02d}" for n in range(1, 13))
    c.require(type(payload_hashes) is tuple and len(payload_hashes) == 12
              and all(type(p) is tuple and len(p) == 2 for p in payload_hashes)
              and tuple(p[0] for p in payload_hashes) == ids, "PAYLOAD_BINDING_INVALID")
    for _, sha in payload_hashes:
        c.check_hash(sha)
    c.require(payload_hashes == tuple((item.source_id, item.payload_digest) for item in catalog[:12]),
              "PAYLOAD_BINDING_INVALID")
    payloads = dict(payload_hashes)
    inputs = {(v.view_id, v.source_id): v for v in catalog}
    results = {(r.view_id, r.panel_id, r.cue_id): r for r in primary}
    expectations = {r["cue_id"]: r for r in evaluation_plan["relations"]}
    rows, groups = [], []
    for new_view in ("DISTRIBUTED_24", "FULL_48_DIAGNOSTIC"):
        for k, condition in enumerate(c.CONDITIONS):
            subset = []
            for p, refs in c.binding.PANELS:
                for cue_id in c.binding.CUES:
                    spec = expectations[cue_id]
                    target = spec["target_source_id"]
                    present = target is not None and target in refs
                    panel_class = ("INDEPENDENT_CONTROL" if target is None else
                        "EMPTY_TARGET_REMOVAL" if not refs else "TARGET_REMOVED" if not present else
                        "TARGET_WITH_COMPETITOR" if len(refs) > 1 else "TARGET_ONLY")
                    left = _outcome(results["CONTIGUOUS_24", p, cue_id].findings[k].hits, target)
                    right = _outcome(results[new_view, p, cue_id].findings[k].hits, target)
                    row = dict(case_id=f"{p}-{cue_id}", panel_id=p, cue_id=cue_id,
                        comparison_view=new_view, diagnostic_only=new_view == "FULL_48_DIAGNOSTIC",
                        condition=condition, family=target or "NONE", subtype=spec["subtype"],
                        panel_class=panel_class, target_present=present,
                        payload_variation="NO_TARGET" if target is None else
                            "BITIDENTICAL" if payloads[cue_id] == payloads[target] else "NON_BITIDENTICAL",
                        before_variation=_variation(inputs["CONTIGUOUS_24", cue_id],
                            inputs.get(("CONTIGUOUS_24", target))),
                        after_variation=_variation(inputs[new_view, cue_id], inputs.get((new_view, target))),
                        nontarget_count=sum(r != target for r in refs), before=left, after=right,
                        relationship_loss=present and left["target_applicable"] and not right["target_applicable"],
                        relationship_gain=present and not left["target_applicable"] and right["target_applicable"],
                        unique_loss=left["correct_unique"] and not right["correct_unique"],
                        unique_gain=not left["correct_unique"] and right["correct_unique"],
                        new_false_applicability=[r for r in right["false_applicable_ids"] if r not in left["false_applicable_ids"]],
                        prevented_false_applicability=[r for r in left["false_applicable_ids"] if r not in right["false_applicable_ids"]])
                    subset.append(row)
            rows.extend(subset)
            groups.append(dict(comparison_view=new_view, condition=condition, stratum="ALL", summary=summarize(subset)))
            keys = ("family", "subtype", "panel_class", "payload_variation", "before_variation", "after_variation")
            # Joint strata retain the real denominators; no cross-modality or exact/variant pooling.
            strata = sorted({tuple(r[key] for key in keys) for r in subset})
            for stratum in strata:
                selected = [r for r in subset if tuple(r[key] for key in keys) == stratum]
                groups.append(dict(comparison_view=new_view, condition=condition,
                    stratum=dict(zip(keys, stratum, strict=True)), summary=summarize(selected)))
    result = dict(schema="s2np.coverage-evaluation.v1", execution_digest=execution_digest,
        evaluation_plan_digest=evaluation_plan["evaluation_digest"],
        verification_digest=verification["verification_digest"], rows=rows, groups=groups,
        removal_pairs=evaluation_plan["removal_pairs"], no_global_success_seal=True,
        memory_or_knownness_claim=False)
    c.bounded_payload(result)
    return {**result, "evaluation_digest": c.digest(result)}
