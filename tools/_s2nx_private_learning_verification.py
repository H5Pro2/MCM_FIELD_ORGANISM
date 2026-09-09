"""Independent NX predictions, two direct learners and offline chain replay."""
from tools import _s2nx_private_learning_prediction as p
from tools import _s2nw_private_learning_verification as nw

b = p.b


def direct_predict(coefficients, previous, last):
    p.require(type(coefficients) is tuple and len(coefficients) in (1, 2), "COEFFICIENT_FORM_INVALID")
    p.vector(previous)
    p.vector(last)
    learned = []
    for alpha in coefficients:
        p.nw.LearnedInput(p.PROFILE, alpha, previous, last)
        values = []
        for i in range(48):
            delta = last[i]-previous[i]
            product = alpha*delta
            values.append(last[i]+product)
        p.vector(tuple(values), False)
        learned.append(values)
    fixed, linear, persist = [], [], []
    for i in range(48):
        d = last[i]-previous[i]
        product = 0.5*d
        fixed.append(last[i]+product)
        linear.append(last[i]+(last[i]-previous[i]))
        persist.append(last[i])
    for values in (fixed, linear, persist):
        p.vector(tuple(values), False)
    return learned, dict(FIXED_HALF=fixed, LINEAR=linear, PERSIST=persist)


def scores(predictions, target, histories, scorer):
    result = {arm: scorer(tuple(values), target) for arm, values in predictions.items()}
    result["gains"] = {h: {a: result[a]["mae"]-result[h]["mae"] for a in p.BASELINES} for h in histories}
    result["cross_gain"] = result["H2"]["mae"]-result["H1"]["mae"] if len(histories) == 2 else None
    return result


def verify_record(record, plan):
    p.require(len(b.canonical(record)) <= p.MAX_OUTPUT_BYTES, "OUTPUT_SIZE_EXCEEDED")
    p.check_root(record, "record_digest")
    p.check_root(plan, "execution_digest")
    p.require(record["schema"] == "s2nx.crossed-learning.v1" and record["execution_digest"] == plan["execution_digest"]
        and record["evaluation"] is None and record["main_gate_after"] is False, "RECORD_BINDING_INVALID")
    p.require(record["limits"] == p.work_limits() and record["verification_limits"] == p.verification_limits(), "LIMIT_BINDING_INVALID")
    counts = record["work"]
    p.count_form(counts, p.work_limits())
    p.require(counts["completed_windows"] <= counts["nj_returns"] <= counts["nj_attempts"] <= counts["analyze_returns"]
        <= counts["analyze_attempts"] <= counts["payloads_checked"] <= counts["generation_attempts"], "PROGRESS_INVALID")
    if record["status"] == "NOT_EVALUABLE":
        fail = record["failure"]
        p.require(type(fail) is dict and type(fail.get("phase")) is str and type(fail.get("code")) is str
            and fail.get("work") == counts and record["streams"] == [] and record.get("learning") is None, "FAILURE_BINDING_INVALID")
        return b.sealed(dict(status="TECHNICAL_FAILURE_RECORDED", record_digest=record["record_digest"], evaluation_allowed=False, read_only=True), "verification_digest")
    p.require(record["status"] == "RECORDING_COMPLETE" and record["failure"] is None
        and record["profiles"] == plan["profiles"] == b.profile_binding()
        and len(record["streams"]) == 6 and len(plan["sources"]) == 32, "COMPLETE_BINDING_INVALID")
    carriers = record["carriers"]
    p.require(type(carriers) is list and len(carriers) == len(set(carriers)) == 48
        and all(type(c) is str and c.startswith("auditory.log_hz.") for c in carriers), "CARRIERS_INVALID")
    work = dict.fromkeys(p.verification_limits(), 0)
    states = {h: {a: nw.direct_initial() for a in ("primary", "direct")} for h in ("H1", "H2")}
    bindings = {h: b.sealed(dict(history=h, source_digests=[r["source_digest"] for r in plan["sources"][6*j:6*j+6]]), "history_digest")
        for j, h in enumerate(("H1", "H2"))}
    def envelope(h):
        return dict(binding=bindings[h], states={a: state.payload() for a, state in states[h].items()})
    p.require(b.canonical(record["learning"]["initial"]) == b.canonical({h: envelope(h) for h in states}), "INITIAL_BINDING_INVALID")
    freezes, divisions = {}, dict(primary=0, direct=0)
    for s, (offset, length) in enumerate(((0, 6), (6, 6), (12, 5), (17, 5), (22, 5), (27, 5))):
        training = s < 2
        histories = ["H1" if s == 0 else "H2"] if training else ["H1", "H2"]
        if not training:
            p.require(set(freezes) == {"H1", "H2"} and all(states[h]["primary"].phase == "FROZEN" for h in states), "FREEZE_BINDING_MISSING")
        stream = record["streams"][s]
        p.check_root(stream, "stream_digest")
        sources = plan["sources"][offset:offset+length]
        p.require(stream["stream_id"] == sources[0]["stream_id"] and len(stream["windows"]) == length
            and len(stream["sites"]) == length-2, "STREAM_BINDING_INVALID")
        for k, source in enumerate(sources):
            p.check_root(source, "source_digest")
            p.require(source["window_ordinal"] == k and source["stream_id"] == stream["stream_id"], "SOURCE_ORDER_INVALID")
        values = [nw.verify_window(row, src, plan["profiles"], carriers) for row, src in zip(stream["windows"], sources, strict=True)]
        work["windows"] += length
        work["halvings"] += length*48
        for k, site in enumerate(stream["sites"], 1):
            p.check_root(site, "site_digest")
            binding = site["prediction_binding"]
            p.check_root(binding, "binding_digest")
            expected_states = {h: envelope(h) for h in histories}
            p.require(b.canonical(binding["learning_before"]) == b.canonical(expected_states), "LEARNING_CHAIN_INVALID")
            common = dict(stream_id=stream["stream_id"], origin=k, target=k+1, phase="TRAIN" if training else "FROZEN",
                active_histories=histories, available_windows=k+1, completed_analyses_before=offset+k+1,
                prefix_digests=[r["window_digest"] for r in stream["windows"][:k+1]],
                functional_prefix=dict(half_profile_digest=p.PROFILE, previous_values=list(values[k-1]), last_values=list(values[k])),
                learning_before=expected_states)
            p.require(b.canonical({key: value for key, value in binding.items() if key not in ("primary", "direct", "binding_digest")})
                == b.canonical(common), "PREFIX_BINDING_INVALID")
            p.require(site["target_window_digest"] == stream["windows"][k+1]["window_digest"]
                and site["completed_analyses_after"] == offset+k+2, "TARGET_BINDING_INVALID")
            for arm in ("primary", "direct"):
                learned, controls = direct_predict(tuple(states[h][arm].alpha for h in histories), values[k-1], values[k])
                expected = {**dict(zip(histories, learned, strict=True)), **controls}
                p.require(b.canonical(binding[arm]) == b.canonical(expected), "PREDICTION_INVALID")
                scored = scores(expected, values[k+1], histories, nw.direct_score)
                p.require(b.canonical(site[arm]) == b.canonical(scored), "SCORE_INVALID")
                h = len(histories)
                for key, num in dict(prediction_subtractions=(h+2)*48, prediction_multiplications=(h+1)*48,
                        prediction_additions=(h+2)*48, persist_copies=48, error_terms=(h+3)*48,
                        mae_sums=h+3, gains=3 if training else 7).items():
                    work[key] += num
            observation = b.digest(dict(binding_digest=binding["binding_digest"], target_window_digest=site["target_window_digest"],
                completed_analyses_after=site["completed_analyses_after"], primary_score_digest=b.digest(site["primary"]),
                direct_score_digest=b.digest(site["direct"])))
            if training:
                h = histories[0]
                updated, markers = {}, {}
                for arm in ("primary", "direct"):
                    new, mark = nw.direct_update(states[h][arm], values[k-1], values[k], values[k+1], observation)
                    states[h][arm], updated[arm], markers[arm] = new, new.payload(), mark
                    for key in ("update_differences", "update_products", "update_additions"):
                        work[key] += 96
                    work["updates"] += 1
                    work["update_divisions"] += int(mark["division_performed"])
                    divisions[arm] += int(mark["division_performed"])
                expected_update = dict(history=h, observation_digest=observation, states=updated, markers=markers)
                p.require(b.canonical(site["learning_update"]) == b.canonical(expected_update), "LEARNING_UPDATE_INVALID")
            else:
                p.require(site["learning_update"] is None, "TEST_UPDATE_FORBIDDEN")
            p.require(b.canonical(binding["primary"]) == b.canonical(binding["direct"])
                and b.canonical(site["primary"]) == b.canonical(site["direct"]), "BASELINE_DIFFERS")
            work["sites"] += 1
        if training:
            h = histories[0]
            states[h] = {a: nw.direct_transition(state, "FROZEN") for a, state in states[h].items()}
            freezes[h] = envelope(h)
    p.require(b.canonical(record["learning"]["frozen"]) == b.canonical(freezes), "FREEZE_BINDING_INVALID")
    for h in states:
        states[h] = {a: nw.direct_transition(state, "CLOSED") for a, state in states[h].items()}
    p.require(b.canonical(record["learning"]["closed"]) == b.canonical({h: envelope(h) for h in states}), "CLOSE_BINDING_INVALID")
    p.count_form(work, p.verification_limits(), True)
    p.count_form(counts, p.work_limits(), True)
    p.require(all(counts[a+"_update_divisions"] == n for a, n in divisions.items()), "COMPLETE_COUNTERS_INVALID")
    return b.sealed(dict(status="S2NX_LEARNING_VERIFIED", record_digest=record["record_digest"], execution_digest=plan["execution_digest"],
        work=work, baseline_equal=True, evaluation_allowed=True, read_only=True, payload_regenerations=0, receptor_calls=0, nj_calls=0,
        raw_reconstructed_from_half=False, chronology_independently_proven=False), "verification_digest")
