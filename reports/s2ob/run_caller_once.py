"""One authorized caller run; unchanged OB entry, verifier, and frozen task inputs."""
import hashlib
import json
from pathlib import Path
from tools import _s2ob_private_caller_binding as b
from tools import _s2ob_private_caller_verification as v

ROOT = b.ROOT
INPUT = ROOT / "reports/s2ob/caller-input-binding"
OUT = ROOT / "reports/s2ob/caller-av-basic-20260910-01"


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(65536):
            h.update(block)
    return h.hexdigest()


def save(name, value, limit):
    b.r.ng.ne.atomic_write(OUT/name, value, limit)


def evaluate(record, proof, plan):
    b.require(proof["evaluation_allowed"] and proof["record_digest"] == record["record_digest"], "EVALUATION_NOT_ALLOWED")
    core = record["execution"]
    rows = {e["event_id"]: row for e, row in zip(record["manifest"]["events"], core["rows"], strict=True)}
    decisions = []
    for expected in plan["decisions"]:
        row = rows[expected["event_id"]]
        hypothesis = row["step"]["hypothesis"]
        observed = "ADMIT_SINGLE_CONTEXT" if hypothesis is not None else row["step"]["context_status"]
        area = None if hypothesis is None else hypothesis["area"]
        decisions.append(dict(event_id=expected["event_id"], expected=expected["expected"], observed=observed,
            expected_area=expected["area"], area=area,
            read_only=row["pre"]["memory_state_digest"] == row["memory"],
            confirmed=(observed, area) == (expected["expected"], expected["area"])))
    formations = []
    for expected in plan["formations"]:
        row = rows[expected["event_id"]]
        # The verified wire body retains native scalar metadata; no vector reconstruction or new scan.
        body = core["states"][row["memory"]]["body"]
        ts = body["tspm_state"]
        occupied = lambda xs: [x for x in xs if x["occupied"]]
        fast = occupied(ts["fast_state"]["slots"])
        audio = occupied(ts["auditory_ppb1_state"]["slots"])
        visual = occupied(ts["visual_ppb1_state"]["slots"])
        observed = dict(b4_occupied=len(occupied(body["b4_state"]["entries"])), fast_occupied=len(fast),
            fast_support=[s["support_count"] for s in fast],
            auditory_ppb_support=[s["support_count"] for s in audio],
            visual_ppb_support=[s["support_count"] for s in visual])
        supports = [] if expected["ppb_support"] is None else [expected["ppb_support"]]
        stable = bool(audio and visual) and all(s["support_count"] >= 3 for s in audio+visual)
        checks = dict(b4=observed["b4_occupied"] == expected["b4_occupied"],
            fast_count=len(fast) == expected["fast_occupied"], fast_support=observed["fast_support"] == [expected["fast_support"]],
            auditory_count=len(audio) == expected["ppb_occupied"], visual_count=len(visual) == expected["ppb_occupied"],
            auditory_support=observed["auditory_ppb_support"] == supports,
            visual_support=observed["visual_ppb_support"] == supports, stable=stable == expected["both_modalities_stable"])
        formations.append(dict(event_id=expected["event_id"], observed=observed, both_modalities_stable=stable,
            checks=checks, confirmed=all(checks.values()), state_digest=row["memory"],
            generation_chain_digest=row["chain_digest"]))
    return b.sealed(dict(schema="s2ob.caller-task-result.v1", run_id=record["run_id"],
        record_digest=record["record_digest"], verification_digest=proof["verification_digest"],
        evaluation_plan_digest=plan["evaluation_digest"], decisions=decisions, formations=formations,
        status="CONFIRMED" if all(x["confirmed"] for x in decisions+formations) else "FALSIFIED",
        boundary="Finite caller input only; no stable B retrieval after eviction, variants, or general robustness."), "evaluation_digest")


def ledger(record, proof, dispatch, binding, *, evaluation_bytes=4096):
    core = record.get("execution")
    parts = {} if core is None else b.core_sizes(core)["items"]
    record_bytes = len(b.canonical(record))
    record_meta = record_bytes-sum(sum(xs) for xs in parts.values())
    refs = {p.relative_to(ROOT).as_posix(): p.stat().st_size for p in INPUT.iterdir() if p.is_file()}
    sources = {p.relative_to(ROOT).as_posix(): p.stat().st_size for p in
        (b.QUAL_DIR/"code-inventory.json", ROOT/"reports/s2ob/prepare_caller_input.py", Path(__file__))}
    proof_bytes = 262144 if proof is None else len(b.canonical(proof))+4
    metadata = dict(record=record_meta, input_references=sum(refs.values()), dispatch=len(b.canonical(dispatch)),
        qualification_reserve=4096, report_reserve=512, evaluation=evaluation_bytes, balance_reserve=4096)
    totals = dict(metadata=sum(metadata.values()), sources=sum(sources.values()), verification=proof_bytes,
        **{k: sum(parts.get(k, [])) for k in ("nj", "formations", "generations")})
    totals["shared"] = totals["sources"]+sum(totals[k] for k in ("nj", "formations", "generations"))
    totals["total"] = record_bytes-record_meta+totals["metadata"]+totals["sources"]+proof_bytes
    violations = [k.upper()+"_LIMIT" for k, n in totals.items() if n > b.LIMITS[k]]
    for k, cap in binding["caps"].items():
        actual = totals.get(k, sum(parts.get(k, [])))
        if actual > cap:
            violations.append("CALLER_"+k.upper()+"_LIMIT")
    if record_meta > 24576:
        violations.append("RECORD_METADATA_RESERVE_LIMIT")
    if refs[(INPUT/"provisioning.json").relative_to(ROOT).as_posix()]+refs[(INPUT/"binding.json").relative_to(ROOT).as_posix()]+metadata["dispatch"] > 6144:
        violations.append("BINDING_METADATA_RESERVE_LIMIT")
    return dict(schema="s2ob.caller-actual-budget.v1", record_digest=record.get("record_digest"),
        record_bytes=record_bytes, item_bytes=parts, input_references=refs, source_references=sources,
        metadata_contributions=metadata, qualification_actual=3131, qualification_reserved=4096,
        totals_with_remaining_reserves=totals, violations=violations,
        raw_input_storage_bytes=binding["raw_input_storage_bytes"], raw_input_read_bytes=binding["raw_input_read_bytes"],
        raw_input_boundary=binding["raw_input_boundary"])


def main():
    phase = "BINDINGS"
    record = proof = assessment = None
    dispatch = dict(run_id=OUT.name, main_calls=0, verification_calls=0, evaluation_calls=0,
        caller_script=dict(path=Path(__file__).relative_to(ROOT).as_posix(), sha256=file_hash(Path(__file__)), bytes=Path(__file__).stat().st_size),
        authorized_by="user: one real OB caller run; historical main_execution_authorized=false remains unchanged",
        gate_after=False)
    try:
        b.require(not OUT.exists(), "OUTPUT_EXISTS")
        binding = json.loads((INPUT/"binding.json").read_bytes()); b.check_root(binding, "binding_digest")
        source = json.loads((INPUT/"provisioning.json").read_bytes()); b.check_root(source, "provisioning_digest")
        plan = json.loads((INPUT/"evaluation-plan.json").read_bytes()); b.check_root(plan, "evaluation_digest")
        manifest = b.decode_manifest(json.loads((INPUT/"manifest.json").read_bytes()))
        b.require(manifest.run_id == OUT.name and manifest.manifest_digest == binding["manifest_digest"] == plan["manifest_digest"]
            and plan["evaluation_digest"] == binding["evaluation_digest"], "CALLER_INPUT_BINDING_INVALID")
        b.require(file_hash(ROOT/source["producer"]["path"]) == source["producer"]["sha256"], "PRODUCER_CHANGED")
        inventory = b.code_inventory()
        b.require(b.digest(inventory) == manifest.code_digest == binding["prerequisite"]["code_inventory_digest"], "CODE_BINDING_INVALID")
        b.qualified_references(inventory)
        qualification=json.loads((b.QUAL_DIR/"result.json").read_bytes())
        b.require(qualification["result_digest"] == binding["prerequisite"]["result_digest"], "QUALIFICATION_BINDING_INVALID")
        attachment_bytes=sum(p.stat().st_size for p in (b.QUAL_DIR/"code-inventory.json",
            ROOT/"reports/s2ob/prepare_caller_input.py", Path(__file__)))
        b.require(attachment_bytes <= binding["caps"]["sources"]
            and sum(binding["caps"].values()) == binding["total_upper_bound"] <= b.LIMITS["total"]
            and sum(binding["metadata_reservations"].values()) <= b.LIMITS["metadata"], "PRE_RUN_BUDGET_INVALID")
        for p in binding["input_files"].values():
            path = ROOT/p["path"]
            b.require(path.stat().st_size == p["byte_count"] and file_hash(path) == p["sha256"], "CALLER_PAYLOAD_CHANGED")
        dispatch.update(manifest_digest=manifest.manifest_digest, binding_digest=binding["binding_digest"],
            code_digest=manifest.code_digest, qualification_result_digest=binding["prerequisite"]["result_digest"])
        print(json.dumps(dict(phase="BOUND", run_id=manifest.run_id, manifest_digest=manifest.manifest_digest,
            total_upper_bound=binding["total_upper_bound"], source_attachments=attachment_bytes)), flush=True)
        phase="MAIN"; dispatch["main_calls"]=1; b.MAIN_GATE=True
        record=b.run_once(manifest, OUT)
        phase="VERIFICATION"; dispatch["verification_calls"]=1
        proof=v.verify_once(OUT)
        phase="TOTAL_BUDGET"
        budget=ledger(record, proof, dispatch, binding)
        b.require(not budget["violations"], "CALLER_TOTAL_BUDGET_INVALID")
        if record["status"] == "RECORDING_COMPLETE" and proof["evaluation_allowed"]:
            phase="EVALUATION"; dispatch["evaluation_calls"]=1
            assessment=evaluate(record, proof, plan)
            b.require(len(b.canonical(assessment)) <= 4096, "EVALUATION_SIZE_LIMIT")
            save("evaluation.json", assessment, 4096)
        dispatch.update(status=record["status"], phase="CLOSED", failure=record["failure"] if assessment is None else None)
    except Exception as exc:
        dispatch.update(status="NOT_EVALUABLE", phase=phase,
            failure=dict(code=getattr(exc, "code", "CALLER_DISPATCH_ERROR"), error_class=type(exc).__name__))
    finally:
        b.MAIN_GATE=False
        dispatch["gate_after"]=False
    if not OUT.exists():
        OUT.mkdir()
    save("dispatch.json", dispatch, 6144)
    if record is not None:
        budget=ledger(record, proof, dispatch, binding,
            evaluation_bytes=4096 if assessment is None else len(b.canonical(assessment)))
        save("final-balance.json", budget, 4096)
        print(json.dumps(dict(status=dispatch["status"], calls=[dispatch[k] for k in ("main_calls","verification_calls","evaluation_calls")],
            counts=record["counts"], evaluation=None if assessment is None else assessment["status"],
            budget=budget["totals_with_remaining_reserves"], violations=budget["violations"])))
    else:
        print(json.dumps(dispatch))
    return 0 if dispatch["status"] == "RECORDING_COMPLETE" and proof is not None and proof["evaluation_allowed"] and not budget["violations"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
