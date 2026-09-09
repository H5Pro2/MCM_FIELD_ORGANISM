"""Five ordinal findings, only after a bound successful technical proof."""
from tools import _s2nu_private_comparison as c


def strict_order(left,right):
    return "LT" if left < right else "EQ" if left == right else "GT"


def evaluate(record,verification,plan):
    c.check_root(record,"comparison_digest")
    c.check_root(verification,"verification_digest")
    c.require(record["status"] == "RECORDING_COMPLETE" and verification["status"] == "S2NU_COMPARISON_VERIFIED"
        and verification["evaluation_allowed"] is True and verification["comparison_digest"] == record["comparison_digest"],
        "VERIFICATION_REQUIRED")
    c.require(plan == c.b.evaluation_plan(record["inputs"]["plan"]),"EVALUATION_PLAN_INVALID")
    totals = {r["stream_id"]:r["measurement"]["ordered"]["T"] for r in record["primary"]}
    findings = []
    for predicate in plan["criteria"]:
        left,right = totals[predicate["left"]],totals[predicate["right"]]
        order = strict_order(left,right)
        findings.append(dict(**predicate,left_T=left,right_T=right,order=order,strictly_ordered=order=="LT"))
    controls = record["controls"]["primary"]
    success = controls["endpoints_equal"] and controls["multiset_equal"] and findings[0]["strictly_ordered"]
    return c.sealed(dict(status="FUNCTION_EVALUATED",comparison_digest=record["comparison_digest"],
        verification_digest=verification["verification_digest"],evaluation_digest=plan["evaluation_digest"],
        findings=findings,endpoints_equal=controls["endpoints_equal"],multiset_equal=controls["multiset_equal"],
        primary_confirmed=success,primary_status="CONFIRMED" if success else "NOT_CONFIRMED",
        descriptive_passes=sum(f["strictly_ordered"] for f in findings[1:]),descriptive_denominator=4,
        order_checks=5,additional_band_differences=0,source_continuity_proven=False,
        category_recognition_proven=False,learning_binding_proven=False),"assessment_digest")
