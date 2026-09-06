"""Post-verification NF retention, losses and removal controls; no execution."""

import json
from pathlib import Path

from tools import _s2nf_private_run as run
from tools import _s2nf_private_run_verification as verification

ne, require, digest = run.ne, run.require, run.digest


def retention(rows):
    d = sum(r["reference_correct"] and r["competition_present"] for r in rows)
    kept = sum(r["reference_correct"] and r["competition_present"] and r["alternative_correct"] for r in rows)
    return dict(N=len(rows), D=d, R=kept, L=d - kept,
        status="ERHALTUNG_NICHT_GEPRUEFT" if d == 0 else "FALSIFIED" if d != kept else "CONFIRMED")


def summarize(rows):
    known = [r for r in rows if r["target_expected"]]
    controls = [r for r in rows if not r["target_expected"]]
    groups = {"all_competition_cases": retention(known),
              "EXACT": retention([r for r in known if r["subtype"] == "EXACT"]),
              "VARIANTS": retention([r for r in known if r["subtype"] != "EXACT"])}
    for name in ("UNIFORM_GAIN", "FREQUENCY", "SPECTRAL_REWEIGHT", "LOCAL_PARTIAL_ADDITION"):
        groups[name] = retention([r for r in known if r["subtype"] == name])
    for axis in ("pcm_varied", "receptor_48_varied", "observed_24_varied"):
        for flag in (False, True):
            groups[f"{axis}:{flag}"] = retention([r for r in known if r[axis] is flag])
    metrics = {}
    for name, subset in (("all", rows), ("target_present", known), ("target_removed", controls)):
        metrics[name] = dict(N=len(subset))
        for arm in ("reference", "alternative"):
            metrics[name][arm] = dict(false_admissions=sum(r[arm + "_false_admission"] for r in subset),
                correct=sum(r[arm + "_correct"] for r in subset),
                abstentions=sum(r[arm + "_abstains"] for r in subset),
                ambiguities=sum("AMBIGU" in r[arm + "_decision"] for r in subset))
    losses = [r["case_id"] for r in known if r["competition_present"] and r["reference_correct"] and not r["alternative_correct"]]
    return dict(retention=groups, outcomes=metrics, losses=losses,
        new_correct_hits=[r["case_id"] for r in known if not r["reference_correct"] and r["alternative_correct"]],
        prevented_false_admissions=[r["case_id"] for r in rows if r["reference_false_admission"] and not r["alternative_false_admission"]],
        status="FALSIFIED" if losses or metrics["all"]["alternative"]["false_admissions"] else groups["all_competition_cases"]["status"])


def presence(state, av):
    return dict(b4=[s.slot_id for s in state.b4_state.entries if s.occupied and s.values == av],
                fast=[s.slot_id for s in state.tspm_state.fast_state.slots if s.occupied and s.auditory_values + s.visual_values == av])


def evaluate_record(record, proof, *, relations, config):
    require(record["status"] == proof["status"] == "RECORDING_COMPLETE"
            and proof["record_digest"] == record["record_digest"]
            and proof["plan_digest"] == record["plan_digest"], "VERIFICATION_REQUIRED")
    verification.old._check_digest(record, "record_digest")
    verification.old._check_digest(proof, "verification_digest")
    cues = [e for e in record["events"] if e["kind"] == "CUE"]
    require(len(cues) == len(relations) == len(proof["baseline_equality"]), "CASE_COUNT_INVALID")
    catalog, rows, inventory = record["catalog"], [], {}
    # Formations, never probe target values, define the candidates to be scored.
    formed = {}
    for e in record["events"]:
        if e["kind"] == "FORMATION":
            formed[e["spec"]["audio_source"]] = tuple(catalog["audio"][e["spec"]["audio_source"]]["values"]) + tuple(e["source"]["visual"]["values"])
    for history, key in proof["final_states"].items():
        s = verification.old.decode_state(record["states"][key], config)
        inputs = [formed[e["spec"]["audio_source"]] for e in record["events"]
                  if e["kind"] == "FORMATION" and e["spec"]["history_id"] == history]
        inventory[history] = dict(
            b4_matches_formations=[x.values for x in s.b4_state.entries if x.occupied] == inputs,
            fast_matches_formations=[x.auditory_values + x.visual_values for x in s.tspm_state.fast_state.slots if x.occupied] == inputs,
            fast_support_one=all(x.support_count == 1 for x in s.tspm_state.fast_state.slots if x.occupied),
            slow_empty=not any(x.occupied for bank in (s.tspm_state.auditory_ppb1_state, s.tspm_state.visual_ppb1_state) for x in bank.slots))
    for relation, event, baseline in zip(relations, cues, proof["baseline_equality"], strict=True):
        require(relation["event_id"] == event["spec"]["event_id"] == baseline["event_id"], "CASE_EVENT_INVALID")
        target, competitor = formed[relation["related_source_id"]], formed[relation["competitor_source_id"]]
        state = verification.old.decode_state(record["states"][event["prestate"]], config)
        tp, cp = presence(state, target), presence(state, competitor)
        competition = bool(tp["b4"] and tp["fast"] and cp["b4"] and cp["fast"] and target != competitor)
        values = catalog["audio"][event["spec"]["audio_source"]]
        row = dict(case_id=relation["case_id"], event_id=relation["event_id"], subtype=relation["subtype"],
            target_expected=relation["target_present"], competition_present=competition,
            target_presence=tp, competitor_presence=cp, prestate_digest=state.state_digest,
            pcm_varied=values["payload_digest"] != catalog["audio"][relation["related_source_id"]]["payload_digest"],
            receptor_48_varied=values["values_digest"] != digest(list(target[:48])),
            observed_24_varied=digest(values["values"][:24]) != digest(list(target[:24])),
            baseline_equal=baseline["reference"] and baseline["alternative"])
        for name, index in (("reference", 0), ("alternative", 2)):
            evidence = event["arms"][index]["evidence"]
            hyp = evidence["hypothesis"]
            admitted = hyp is not None
            correct = (hyp is not None and hyp["area"] == "A_RECENT" and hyp["candidate_values_digest"] == digest(list(target[:48]))
                       and tuple(hyp["proposed_values"]) == target[24:48]) if relation["target_present"] else not admitted
            row.update({name + "_correct": correct, name + "_false_admission": admitted and not correct,
                name + "_abstains": not admitted, name + "_decision": evidence["decision"],
                name + "_arm_digest": event["arms"][index]["arm_digest"]})
        rows.append(row)
    result = summarize(rows)
    if not all(all(checks.values()) for checks in inventory.values()) or not all(r["baseline_equal"] for r in rows):
        result["status"] = "FALSIFIED"
    return run.sealed({**result, "rows": rows, "inventory_checks": inventory, "run_id": record["run_id"],
        "record_digest": record["record_digest"], "verification_digest": proof["verification_digest"]}, "evaluation_digest")


def evaluate_main_once(path):
    path = Path(path).resolve(strict=True)
    require(path.name == "recording.json" and path.parent.parent == (run.sources.ROOT / "reports/s2nf").resolve(), "EVALUATION_PATH_INVALID")
    target = path.with_name("evaluation.json")
    reservation = path.with_name("evaluation-reservation.json")
    require(not target.exists(), "EVALUATION_ALREADY_EXISTS")
    with reservation.open("x", encoding="ascii") as handle:
        handle.write('{"evaluation_calls":1}')
    record = json.loads(path.read_bytes())
    proof = json.loads(path.with_name("verification.json").read_bytes())
    verification.old._check_digest(proof, "report_digest")
    require(proof["file_unchanged"] is True and proof["record_file_sha256"] == ne.filehash(path)
            and record["mode"] == "MAIN", "VERIFIED_FILE_CHANGED")
    run.sources.load_plan()
    evaluation = json.loads((run.sources.ROOT / run.sources.PRESEAL / "evaluation-plan.json").read_bytes())
    inner = {k: v for k, v in proof.items() if k not in ("record_file_sha256", "file_unchanged", "report_digest")}
    result = evaluate_record(record, inner, relations=evaluation["cases"], config=ne.make_config())
    ne.atomic_write(target, result)
    return target
