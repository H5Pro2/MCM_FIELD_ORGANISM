"""Versioned one-shot caller. No built-in corpus, generation, retry or evaluation."""
import argparse
import json
from pathlib import Path

from tools import _s2oc_bound_session as entry
from tools import _s2oc_shared_verification as verification

shared, b = entry.shared, entry.b


def _run_bound(common_path, trusted_sha256, inventory_path, output, *, neutral=False):
    """Caller must separately open entry.MAIN_GATE; the CLI never opens it."""
    output = Path(output)
    common = shared.read_json(common_path)
    shared.need(shared.sha(b.canonical(common)) == trusted_sha256, "CALLER_PIN_INVALID")
    inv = shared.read_json(inventory_path)
    try:
        failure = None
        try:
            raw = entry.run_once(common, inv, output, neutral=neutral, common_path=common_path)
        except Exception as exc:
            failure = dict(code=getattr(exc,"code",type(exc).__name__),error_class=type(exc).__name__)
            if not (output/"record.json").exists():
                if not output.exists():
                    output.mkdir()
                error = dict(status="NOT_EVALUABLE",phase="BINDINGS",completed_events=0,
                    failure=failure,balance=getattr(exc,"balance",None),gates=False)
                shared.prior.save(output/"prestart-error.json",error)
                raise
            raw = b.canonical(shared.unpack(shared.read_json(output/"record.json"),
                shared.read_json(output/"session.json"),common)[0])
        proof, measured = verification.verify_once(output, inv, qualified=not neutral)
        dispatch = dict(version=shared.VERSION,status=json.loads(raw)["status"],gates=False,
            common_sha256=trusted_sha256,verification_digest=proof["verification_digest"],evaluation_calls=0,
            failure=failure)
        shared.need(len(b.canonical(dispatch))<=768,"DISPATCH_LIMIT")
        shared.prior.save(output/"dispatch.json",dispatch)
        # References, report, future assessment and this ledger remain charged.
        record,session=shared.unpack(shared.read_json(output/"record.json"),shared.read_json(output/"session.json"),common)
        estimate=0
        for _ in range(12):
            pointer=(output/"common-reference.json").stat().st_size if (output/"common-reference.json").exists() else 0
            actual=shared.ledger(record,session,common,attachments=(("metadata","dispatch.json",len(b.canonical(dispatch))),
                ("metadata","final-balance.json",estimate),("metadata","common-reference.json",pointer)),
                proof_bytes=len(b.canonical(proof))+4,report_bytes=0)
            summary = dict(reserved_totals=measured["totals"],actual_totals=actual["totals"],
                contributions={k:v for k,v in actual["contributions"].items() if k!="references"},
                references_sha256=b.digest(common["references"]),common_sha256=trusted_sha256,
                violations=actual["violations"],not_written=["evaluation.json","BEFUND.md"])
            size=len(b.canonical(summary))
            if size==estimate:break
            estimate=size
        else:raise entry.budget.BudgetError("BALANCE_SIZE_UNSTABLE")
        shared.need(size<=1536 and not actual["violations"],"FINAL_BALANCE_LIMIT")
        shared.prior.save(output/"final-balance.json",summary)
        return dispatch
    finally:
        entry.MAIN_GATE = False


def run(common_path, trusted_sha256, inventory_path, output, *, neutral=False):
    try:
        return _run_bound(common_path,trusted_sha256,inventory_path,output,neutral=neutral)
    finally:
        entry.MAIN_GATE=False


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--common",required=True)
    p.add_argument("--sha256",required=True)
    p.add_argument("--inventory",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    # No command line switch grants a real run.
    run(args.common,args.sha256,args.inventory,args.output)


if __name__=="__main__":
    main()
