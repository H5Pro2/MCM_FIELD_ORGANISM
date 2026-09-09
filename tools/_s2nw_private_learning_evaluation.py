"""Post-verification NW evaluation: no learning, prediction or source execution."""
from tools import _s2nw_private_learning_prediction as p

b = p.b


def outcome(gain):
    return "WIN" if gain > 0 else "LOSS" if gain < 0 else "TIE"


def evaluate(record, proof, evaluation):
    for obj,key in ((record,"record_digest"),(proof,"verification_digest"),(evaluation,"evaluation_digest")):
        p.check_root(obj,key)
    p.require(record["status"] == "RECORDING_COMPLETE" and proof["status"] == "S2NW_LEARNING_VERIFIED"
        and proof["record_digest"] == record["record_digest"] and proof["evaluation_allowed"] is True
        and evaluation["execution_digest"] == record["execution_digest"],"EVALUATION_NOT_AUTHORIZED")
    p.require(b.canonical(evaluation) == b.canonical(b.evaluation_plan(dict(execution_digest=record["execution_digest"]))),"EVALUATION_BINDING_INVALID")
    streams,lookup = [],{}
    for s,stream in enumerate(record["streams"]):
        sites = []
        for k,site in enumerate(stream["sites"],1):
            binding,score = site["prediction_binding"],site["primary"]
            site_id = f"t{k:02d}" if s == 0 else f"p{(s-1)*3+k:02d}"
            row = dict(site_id=site_id,target=binding["target"],phase="TRAIN" if s == 0 else
                evaluation["reporting"]["target_phases"][str(binding["target"])],
                alpha=binding["learning_before"]["primary"]["alpha"],
                mae={arm:score[arm]["mae"] for arm in p.ARMS},gains=score["gains"],
                outcomes={arm:outcome(score["gains"][arm]) for arm in p.BASELINES})
            sites.append(row)
            lookup[site_id] = row
        streams.append(dict(stream_id=stream["stream_id"],category=evaluation["categories"][stream["stream_id"]],
            phase="TRAIN" if s == 0 else "FROZEN",N_per_baseline=len(sites),sites=sites,
            counts={arm:{label:sum(x["outcomes"][arm] == label for x in sites) for label in ("WIN","TIE","LOSS")}
                for arm in p.BASELINES}))
    checks = []
    for spec in evaluation["criteria"]:
        scores = lookup[spec["site_id"]]["mae"]
        left,right = scores[spec["left"].removeprefix("MAE_")],scores[spec["right"].removeprefix("MAE_")]
        checks.append(dict(**spec,passed=left < right if spec["operator"] == "LT" else left > right))
    state = record["learning"]["frozen"]["primary"]
    noninitial = any(state[key] != record["learning"]["initial"]["primary"][key] for key in ("Sxx","Sxy","alpha"))
    informative = state["n"] == 4 and state["Sxx"] > 0 and noninitial
    return b.sealed(dict(status="FUNCTIONALLY_EVALUATED",record_digest=record["record_digest"],
        verification_digest=proof["verification_digest"],evaluation_digest=evaluation["evaluation_digest"],
        primary="CONFIRMED" if informative and all(x["passed"] for x in checks[:6]) else "FALSIFIED",
        informative_learning_state=informative,frozen_alpha=state["alpha"],streams=streams,criteria=checks,
        pooled_mean=None,losses_compensated=False,training_replaces_transfer=False,
        source_identity_claim=False,general_sequence_learning_claim=False,
        work=dict(outcome_classifications=32,training_outcome_classifications=8,strict_conditions=9)),"evaluation_result_digest")
