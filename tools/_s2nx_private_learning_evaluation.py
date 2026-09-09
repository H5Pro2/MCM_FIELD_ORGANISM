"""Post-verification NX criteria; no predictor, learner or source calls."""
from tools import _s2nx_private_learning_prediction as p
from tools._s2nw_private_learning_evaluation import outcome

b = p.b


def evaluate(record, proof, evaluation):
    for obj, key in ((record, "record_digest"), (proof, "verification_digest"), (evaluation, "evaluation_digest")):
        p.check_root(obj, key)
    p.require(record["status"] == "RECORDING_COMPLETE" and proof["status"] == "S2NX_LEARNING_VERIFIED"
        and proof["record_digest"] == record["record_digest"] and proof["evaluation_allowed"] is True
        and evaluation["execution_digest"] == record["execution_digest"], "EVALUATION_NOT_AUTHORIZED")
    p.require(b.canonical(evaluation) == b.canonical(b.evaluation_plan(dict(execution_digest=record["execution_digest"]))), "EVALUATION_BINDING_INVALID")
    streams, lookup = [], {}
    for s, stream in enumerate(record["streams"]):
        sites = []
        for k, site in enumerate(stream["sites"], 1):
            binding, score = site["prediction_binding"], site["primary"]
            histories = binding["active_histories"]
            site_id = f"t{s*4+k:02d}" if s < 2 else f"p{(s-2)*3+k:02d}"
            row = dict(site_id=site_id, target=binding["target"], phase="TRAIN" if s < 2 else
                evaluation["reporting"]["target_phases"][str(binding["target"])],
                alphas={h: binding["learning_before"][h]["states"]["primary"]["alpha"] for h in histories},
                mae={arm: score[arm]["mae"] for arm in (*histories, *p.BASELINES)}, gains=score["gains"],
                outcomes={h: {a: outcome(score["gains"][h][a]) for a in p.BASELINES} for h in histories},
                cross_gain=score["cross_gain"], cross_outcome=outcome(score["cross_gain"]) if s >= 2 else None)
            sites.append(row)
            lookup[site_id] = row
        streams.append(dict(stream_id=stream["stream_id"], category=evaluation["categories"][stream["stream_id"]],
            phase="TRAIN" if s < 2 else "FROZEN", N_per_history_baseline=len(sites), sites=sites,
            counts={h: {a: {label: sum(x["outcomes"][h][a] == label for x in sites) for label in ("WIN", "TIE", "LOSS")}
                for a in p.BASELINES} for h in histories}))
    checks = []
    for spec in evaluation["criteria"]:
        mae = lookup[spec["site_id"]]["mae"]
        left, right = mae[spec["left"].removeprefix("MAE_")], mae[spec["right"].removeprefix("MAE_")]
        checks.append(dict(**spec, passed=left < right if spec["operator"] == "LT" else left > right))
    informative, coefficients = {}, {}
    for h in p.HISTORIES:
        state = record["learning"]["frozen"][h]["states"]["primary"]
        initial = record["learning"]["initial"][h]["states"]["primary"]
        informative[h] = state["n"] == 4 and state["Sxx"] > 0 and any(state[key] != initial[key] for key in ("Sxx", "Sxy", "alpha"))
        coefficients[h] = state["alpha"]
    blocks = {prefix: all(x["passed"] for x in checks if x["check_id"].startswith(prefix)) for prefix in ("K", "F", "B", "W")}
    different = coefficients["H1"] != coefficients["H2"]
    result = b.sealed(dict(status="FUNCTIONALLY_EVALUATED", record_digest=record["record_digest"],
        verification_digest=proof["verification_digest"], evaluation_digest=evaluation["evaluation_digest"],
        primary="CONFIRMED" if blocks["K"] and blocks["F"] and all(informative.values()) and different else "FALSIFIED",
        blocks={k: "CONFIRMED" if v else "FALSIFIED" for k, v in blocks.items()},
        informative_learning_states=informative, frozen_alphas=coefficients, actual_alphas_different=different,
        streams=streams, criteria=checks, pooled_mean=None, losses_compensated=False, training_replaces_transfer=False,
        automatic_history_selection_claim=False, source_identity_claim=False, general_sequence_learning_claim=False,
        work=dict(outcome_classifications=108, training_outcome_classifications=24, strict_conditions=28)), "evaluation_result_digest")
    p.require(len(b.canonical(result)) <= 262144, "EVALUATION_SIZE_EXCEEDED")
    return result
