"""Post-verification ordinal diagnostics; no source-vector arithmetic."""
from tools import _s2nt_private_comparison as c


def strict_order(left,right):
    return "LT" if left < right else "EQ" if left == right else "GT"


def evaluate(record,verification,plan):
    c.check_root(record,"comparison_digest")
    c.check_root(verification,"verification_digest")
    c.require(verification["status"] == "S2NT_COMPARISON_VERIFIED" and verification["evaluation_allowed"] is True
        and verification["comparison_digest"] == record["comparison_digest"],"VERIFICATION_REQUIRED")
    c.require(plan == c.b.evaluation_plan(record["inputs"]["plan"]),"EVALUATION_PLAN_INVALID")
    rows = {p["pair_id"]:p for p in record["primary"]}
    attribution,subtypes = {},{}
    for family in plan["families"]:
        reference = family["reference"]
        attribution[reference],subtypes[reference] = reference,"REFERENCE"
        for role in ("exact","level","frequency","addition","replacement"):
            sid = family[role]
            attribution[sid] = reference if role in ("exact","level","frequency") else None
            subtypes[sid] = role.upper()
    for sid in plan["independent_controls"]:
        attribution[sid],subtypes[sid] = None,"INDEPENDENT_CONTROL"
    findings = []
    for predicate in plan["order_checks"]:
        left,right = rows[predicate["left"]],rows[predicate["right"]]
        order = strict_order(left["mean"],right["mean"])
        findings.append(dict(**predicate,left_distance=left["mean"],right_distance=right["mean"],
            left_subtype=subtypes[left["source_id"]],right_subtype=subtypes[right["source_id"]],order=order,separated=order=="LT"))
    variants,exact = [],[]
    for family in plan["families"]:
        r = family["reference"]
        for role in ("exact","level","frequency"):
            q = family[role]
            pair = rows[f"d{q[-2:]}-{r[-2:]}"]
            item = dict(source_id=q,reference_id=r,subtype=role.upper(),raw_changed=not pair["raw_equal"],
                half_changed=not pair["half_equal"],nominal_variant_without_half_change=role != "exact" and pair["half_equal"])
            (exact if role == "exact" else variants).append(item)
    collisions = [dict(pair_id=p["pair_id"],source_id=p["source_id"],reference_id=p["reference_id"],
        source_subtype=subtypes[p["source_id"]],raw_equal=p["raw_equal"],half_equal=p["half_equal"],
        half_only_collision=p["half_equal"] and not p["raw_equal"],
        different_prescribed_whole_assignment=attribution[p["source_id"]] != attribution[p["reference_id"]])
        for p in record["primary"] if p["raw_equal"] or p["half_equal"]]
    groups = []
    for kind in ("PRIMARY","ATTRIBUTION","CONTROL"):
        items = [f for f in findings if f["group"] == kind]
        groups.append(dict(group=kind,N=len(items),strictly_separated=sum(f["order"]=="LT" for f in items),
            ties=sum(f["order"]=="EQ" for f in items),inverted=sum(f["order"]=="GT" for f in items)))
    subgroups = []
    for kind in ("ADDITION","REPLACEMENT","INDEPENDENT_CONTROL","REFERENCE"):
        items = [f for f in findings if f["right_subtype"] == kind]
        subgroups.append(dict(right_subtype=kind,N=len(items),strictly_separated=sum(f["order"]=="LT" for f in items),
            ties=sum(f["order"]=="EQ" for f in items),inverted=sum(f["order"]=="GT" for f in items)))
    order_pass = all(f["separated"] for f in findings)
    coverage = all(v["half_changed"] for v in variants)
    return c.sealed(dict(status="FUNCTION_EVALUATED",comparison_digest=record["comparison_digest"],
        verification_digest=verification["verification_digest"],evaluation_digest=plan["evaluation_digest"],
        order_findings=findings,groups=groups,subgroups=subgroups,variants=variants,exact_controls=exact,
        pair_collisions=collisions,complete_strict_order=order_pass,actual_variant_coverage=coverage,
        bounded_separation_confirmed=order_pass and coverage,order_checks=24,additional_band_differences=0,
        threshold_derived=False,component_recognition=None,semantic_identity=None,operational_admission=None,
        missing_l1_order_is_not_universal_information_loss=True),"assessment_digest")
