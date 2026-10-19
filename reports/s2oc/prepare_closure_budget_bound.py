"""Static serialization bound only: no project imports, payloads or test call."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports/s2oc/closure-budget-preparation-20260910-01.json"


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def read(path):
    raw = (ROOT/path).read_bytes()
    return json.loads(raw), dict(path=path, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def atom(size):
    return "x"*(size-2)


def main():
    if OUT.exists():
        raise RuntimeError("PREPARATION_OUTPUT_EXISTS")
    m, mp = read("reports/s2oc/memory-cycle-input-binding/manifest.json")
    historic, hp = read("reports/s2oc/caller-session-basic-20260910-01/record.json")
    session, sp = read("reports/s2oc/caller-session-basic-20260910-01/session.json")
    final, fp = read("reports/s2oc/caller-memory-cycle-20260910-01/final-balance.json")
    # Only invariant non-native envelope fields are retained. No transaction,
    # receptor values or memory state is replayed, compared or reconstructed.
    base = {k: deepcopy(v) for k, v in historic["execution"].items()
            if k not in ("states", "inputs", "rows", "scans", "source_receipts")}
    base["run_id"] = m["run_id"]
    base["runtime_config"]["runtime_id"] = m["run_id"]
    base["runtime_config"]["max_event_count"] = 21
    for snap in (base["initial"]["snapshot"], base["final"]):
        snap["runtime_id"] = m["run_id"]
        for k, v in snap.items():
            if type(v) is int:
                snap[k] = 28
    totals = []
    external = final["reference_bytes"]["metadata"]
    sources = final["reference_bytes"]["sources"]
    for n in range(22):
        selected = m["events"][:n]
        forms = sum(e["kind"] == "COMPLETE_AV_PERCEPTION" for e in selected)
        cues = n-forms
        core = deepcopy(base)
        core["states"] = {f"{i:064x}": atom(98304) for i in range(forms+1)}
        core["inputs"] = [atom(16384) for _ in selected]
        core["scans"] = [atom(32767) for _ in range(2*cues)]
        core["rows"] = [dict(step=atom(16375), formation=atom(1536), generations=atom(1536))
                        if e["kind"] == "COMPLETE_AV_PERCEPTION" else
                        dict(step=atom(16375), formation=None, generations=None) for e in selected]
        core["source_receipts"] = [dict(nj=atom(1000)) if e["kind"] == "COMPLETE_AV_PERCEPTION"
            else dict(nj=None, rgb_digest="0"*64, source_digest="0"*64) for e in selected]
        native = sum(len(wire(x)) for x in core["states"].values())
        native += sum(len(wire(x)) for x in core["inputs"]+core["scans"])
        for row in core["rows"]:
            native += len(wire({k:v for k,v in row.items() if k not in ("formation", "generations")}))
            native += sum(len(wire(row[k])) for k in ("formation", "generations") if row[k] is not None)
        native += sum(len(wire(x)) for x in core["source_receipts"] if x["nj"] is not None)
        record = deepcopy(historic)
        record.update(manifest=m, run_id=m["run_id"], execution=core)
        binding = deepcopy(session)
        binding.update(run_id=m["run_id"], returned_results=[dict(ordinal=i, sha256="0"*64, byte_count=16384)
                       for i in range(1,n+1)], failed_prefix_steps=[])
        meta = len(wire(record))+len(wire(binding))-native+external+512
        # The existing external dispatch/balance/evaluation caps stay counted.
        meta += 768+1536+3000
        failure = deepcopy(record)
        failure["execution"] = None
        failure["status"] = "NOT_EVALUABLE"
        failure["failure"] = dict(phase="SERIALIZATION", ordinal=21, source_id="x"*80,
            completed_events=n, code="COMBINED_RUNTIME_METADATA_LIMIT", error_class="BudgetError",
            last_snapshot_digest="0"*64, final=core["final"], balance=atom(4096))
        fb = deepcopy(binding)
        fb["status"] = "NOT_EVALUABLE"
        fb["failed_prefix_steps"] = [atom(16384) for _ in selected]
        fm = len(wire(failure))+len(wire(fb))-n*16384+external+512+768+1536+3000
        totals.append(dict(completed=n, formations=forms, success_metadata=meta,
                           failure_metadata=fm, metadata_limit=65536,
                           violations=[k for k,v in (("success",meta),("failure",fm)) if v>65536]))
    result = dict(kind="STATIC_SERIALIZATION_PREPARATION_NOT_QUALIFICATION", test_calls=0,
        inputs=[mp,hp,sp,fp], metadata_references=external, source_references=sources,
        boundary="Invariant historical envelope structure, synthetic native maximum bodies; no replay. "
                 "Renewed code/qualification references and new entry fields are not yet included. "
                 "This is not a complete active upper bound or a historical trigger measurement.",
        positions=totals)
    with OUT.open("xb") as f:
        f.write(wire(result))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
