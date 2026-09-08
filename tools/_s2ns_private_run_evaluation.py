"""Roles and original-source variation are evaluated only after total verification."""
from dataclasses import asdict
import json
from pathlib import Path

from tools import _s2ns_private_run_verification as verify
from tools import _s2ns_private_evaluation as evaluation

s, run, src, io = verify.s, verify.run, verify.src, verify.io


def evaluate_record(record,proof,*,plan,evaluation_plan):
    src.check(record,"record_digest")
    src.check(plan,"execution_digest")
    src.check(proof,"verification_digest")
    src.check(evaluation_plan,"evaluation_digest")
    s.require(proof["status"] == record["status"] == "RECORDING_COMPLETE" and proof["evaluation_allowed"] is True
        and proof["record_digest"] == record["record_digest"] and evaluation_plan["execution_digest"] == plan["execution_digest"],"EVALUATION_REQUIRES_VERIFICATION")
    expected = evaluation_plan["cases"]
    events = [e for e in record["events"] if e["formation"] is None]
    s.require(len(events) == len(expected) == len(proof["cases"]),"EVALUATION_COMPLETENESS_INVALID")
    outcomes = []
    config = s.profile.build_config()
    specs = {e["event_id"]:e for e in plan["events"]}
    for event,case,p in zip(events,expected,proof["cases"],strict=True):
        s.require(event["event_id"] == case["event_id"] == p["event_id"],"EVALUATION_EVENT_INVALID")
        endpoint = event["source"]
        projection = src.projection_decode(endpoint["projection"])
        views = s.bind_views(projection=projection,config=config,
            source_id=specs[event["event_id"]]["auditory"]["source_id"],
            source_digest=endpoint["audio_source_digest"],pcm_digest=endpoint["pcm_digest"])
        originals = [r for r in p["original_formations"] if r["source_id"] == case["target"]]
        expectation = evaluation.Expectation(event["event_id"],case["target"],
            None if case["prediction"] == "ABSTAIN" else case["prediction"],case["subtype"],
            tuple(tuple(x) for x in p["slot_sources"]),None if not originals else tuple(tuple(x["values"]) for x in originals),
            tuple(x["source_binding_digest"] for x in originals))
        outcomes.append(evaluation.evaluate_case(verify.decode_result(event["results"][0]),p["pair_verification"],
            inventory=verify.decode_inventory(event["inventory"]),lower=views[0],upper=views[1],expectation=expectation))
    groups = []
    # No gain/loss netting. Empty variation references remain a separate null group.
    for arm in s.VIEWS:
        keys = {(o["subtype"],c["competition"],c["receptor_variation"]) for o in outcomes for c in o["comparisons"] if c["single"] == arm}
        for subtype,competition,variation in sorted(keys,key=repr):
            rows = [c for o in outcomes for c in o["comparisons"] if c["single"] == arm and
                (o["subtype"],c["competition"],c["receptor_variation"]) == (subtype,competition,variation)]
            sums = {}
            for label in ("relationship_retention","public_retention"):
                total = {k:sum(c[label][k] for c in rows) for k in ("N","D","R","L","gains")}
                s.require(total["D"] == total["R"]+total["L"],"RETENTION_IDENTITY_INVALID")
                total["status"] = "ERHALTUNG_NICHT_GEPRUEFT" if total["D"] == 0 else "ASSESSED"
                sums[label] = total
            groups.append(dict(single=arm,subtype=subtype,competition=competition,receptor_variation=variation,
                **sums,public_losses=sum(c["public_loss"] for c in rows),new_false_admissions=sum(c["new_false_admission"] for c in rows),
                prevented_false_admissions=sum(c["prevented_false_admission"] for c in rows)))
    return io.sealed(dict(status="FUNCTION_EVALUATED",record_digest=record["record_digest"],
        verification_digest=proof["verification_digest"],evaluation_plan_digest=evaluation_plan["evaluation_digest"],
        cases=outcomes,groups=groups,no_netting=True),"evaluation_digest")


def evaluate_file_once(path,*,plan,evaluation_plan):
    path = Path(path).resolve(strict=True)
    output = path.with_name("evaluation.json")
    s.require(not output.exists(),"EVALUATION_ALREADY_EXISTS")
    with output.with_suffix(".claim").open("xb"):
        pass
    record = json.loads(path.read_bytes())
    wrapper = json.loads(path.with_name("verification.json").read_bytes())
    src.check(wrapper,"report_digest")
    s.require(wrapper["file_sha256"] == io.filehash(path) and wrapper["file_unchanged"] is True,"VERIFICATION_FILE_INVALID")
    proof = {k:v for k,v in wrapper.items() if k not in ("report_digest","file_sha256","file_unchanged")}
    result = evaluate_record(record,proof,plan=plan,evaluation_plan=evaluation_plan)
    io.atomic_write(output,result,run.LIMITS["record_bytes"])
    return output
