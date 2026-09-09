"""Separate evaluation, no prediction, source, receptor or error recomputation."""
from tools import _s2nv_private_prediction as p

b = p.b


def outcome(gain):
    return "WIN" if gain>0 else "LOSS" if gain<0 else "TIE"


def evaluate(record, proof, evaluation):
    for obj,key in ((record,"record_digest"),(proof,"verification_digest"),(evaluation,"evaluation_digest")):
        p.check_root(obj,key)
    p.require(record["status"]=="RECORDING_COMPLETE" and proof["status"]=="S2NV_PREDICTION_VERIFIED"
        and proof["record_digest"]==record["record_digest"] and proof["evaluation_allowed"] is True
        and evaluation["execution_digest"]==record["execution_digest"],"EVALUATION_NOT_AUTHORIZED")
    p.require(b.canonical(evaluation)==b.canonical(b.evaluation_plan(dict(execution_digest=record["execution_digest"]))),"EVALUATION_BINDING_INVALID")
    rows,sites = [],{}
    for stream in record["streams"]:
        individual = []
        for site in stream["sites"]:
            binding = site["prediction_binding"]
            score = site["primary"]
            row = dict(target=binding["target"],phase=evaluation["reporting"]["target_phases"][str(binding["target"])],
                linear_mae=score["LINEAR_TWO_STATE"]["mae"],persist_mae=score["PERSIST_LAST"]["mae"],
                gain=score["gain"],outcome=outcome(score["gain"]))
            individual.append(row)
            sites[f"p{len(sites)+1:02d}"] = row
        rows.append(dict(stream_id=stream["stream_id"],category=evaluation["categories"][stream["stream_id"]],N=3,
            counts={label:sum(x["outcome"]==label for x in individual) for label in ("WIN","TIE","LOSS")},sites=individual))
    checks = []
    for spec in evaluation["criteria"]:
        row = sites[spec["site_id"]]
        passed = row["linear_mae"]<row["persist_mae"] if spec["operator"]=="LT" else row["linear_mae"]>row["persist_mae"]
        checks.append(dict(**spec,passed=passed))
    return b.sealed(dict(status="FUNCTIONALLY_EVALUATED",record_digest=record["record_digest"],verification_digest=proof["verification_digest"],
        evaluation_digest=evaluation["evaluation_digest"],primary="CONFIRMED" if all(x["passed"] for x in checks[:3]) else "FALSIFIED",
        streams=rows,criteria=checks,pooled_mean=None,losses_compensated=False,learning_claim=False,
        work=dict(outcome_classifications=12,strict_conditions=6)) ,"evaluation_result_digest")
