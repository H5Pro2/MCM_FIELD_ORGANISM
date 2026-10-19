"""Bind complete prospective envelopes, then at most one focused test call."""
import ast
from dataclasses import asdict
import os
from pathlib import Path
import subprocess
import sys

from reports.s2od import start_terminal_basic_once as st

c, s, b = st.client, st.s, st.b
OWN = ("reports/s2od/start_terminal_basic_once.py", "tests/test_s2od_native_start.py",
       "reports/s2od/qualify_native_start_once.py", "reports/s2ob/run_caller_once.py",
       "tools/_s2od_budget_session.py")
QUAL_CAP = 6607
PREPARATION_CAP = 16384
QUALIFICATION_VERSION = "s2od.qualification-envelope.v1"
QUALIFICATION_METADATA = 73728
QUALIFICATION_BALANCE_CAP = 4096


def qualification_totals(session_totals, additions):
    """An invalid session is never rescued by the outer qualification allowance."""
    violations = ["SESSION_"+v for v in st.od.violations(session_totals)]
    c.need(all(k == "metadata" and type(n) is int and n >= 0 for k,p,n in additions),
           "QUALIFICATION_ADDITION_INVALID")
    totals = dict(session_totals)
    extra = sum(n for k,p,n in additions)
    totals["metadata"] += extra
    totals["total"] += extra
    limits = dict(st.od.LIMITS, metadata=QUALIFICATION_METADATA)
    violations += ["QUALIFICATION_"+k.upper()+"_LIMIT" for k,n in totals.items() if n > limits[k]]
    return dict(session=dict(session_totals), additions=list(additions), totals=totals, violations=violations)


def assessment_shape():
    """Output grammar bound, not an evaluated historic or predicted result."""
    digest = "f" * 64
    decisions = [dict(event_id="e"*80, expected="s"*64, observed="s"*64,
        expected_area="A_RECENT", area="B_STABLE", read_only=False, confirmed=False) for _ in range(3)]
    observed = dict(b4_occupied=9, fast_occupied=3, fast_support=[2]*3,
                    auditory_ppb_support=[3]*4, visual_ppb_support=[3]*4)
    checks = {k:False for k in ("b4", "fast_count", "fast_support", "auditory_count",
              "visual_count", "auditory_support", "visual_support", "stable")}
    forms = [dict(event_id="e"*80, observed=observed, both_modalities_stable=False,
        checks=checks, confirmed=False, state_digest=digest, generation_chain_digest=digest) for _ in range(4)]
    result = dict(schema="s2ob.caller-task-result.v1", run_id="r"*80,
        record_digest=digest, verification_digest=digest, evaluation_plan_digest=digest,
        decisions=decisions, formations=forms, status="FALSIFIED", evaluation_digest=digest,
        boundary="Finite caller input only; no stable B retrieval after eviction, variants, or general robustness.")
    return dict(functional=result, display_hashes=[digest]*7, display_equal=[False]*7,
                verification_calls_by_starter=0)


def bindings(manifest, inv, refs):
    common, _ = s.qualified_common(manifest, b.ROOT/"reports/s2oc"/s.QUAL_ID)
    allrefs = list(common["references"])
    allrefs.extend(s.file_reference("sources", b.ROOT/p) for p in c.OWN)
    q = b.ROOT/"reports/s2od"/c.QUAL_ID
    allrefs.extend(s.file_reference("metadata", q/name) for name in
                   ("preregistration.json", "stdout.txt", "stderr.txt", "result.json"))
    return s.build_common(manifest, inv, allrefs + refs, common["qualification"])


def positions(common, extra=(), *, qualification=False):
    rows, violations = [], []
    for n in range(len(common["manifest"]["events"])+1):
        row = dict(completed=n)
        for arm, pair in zip(("success","failure"), c.verification.synthetic_forms(common,n)):
            measured = st.od.ledger(*pair, common, attachments=st.ATTACHMENTS if qualification
                                    else st.ATTACHMENTS+extra)
            if qualification:
                measured = qualification_totals(measured["totals"], extra)
                row["session_"+arm] = measured["session"]
            row[arm] = measured["totals"]
            violations.extend(dict(completed=n, arm=arm, total=measured["totals"], code=v)
                              for v in measured["violations"])
        rows.append(row)
    return rows, violations


def main():
    out = b.ROOT/"reports/s2od"/st.QUAL_ID
    if out.exists():
        raise RuntimeError("QUALIFICATION_ID_USED")
    out.mkdir()
    s.prior.save(out/st.od.POLICY_NAME, st.od.policy())
    policy_ref = s.file_reference("metadata", out/st.od.POLICY_NAME)
    inv = s.inventory()
    refs = [s.file_reference("sources", b.ROOT/p) for p in OWN]
    test_tree = ast.parse((b.ROOT/OWN[1]).read_text(encoding="utf-8"))
    names = sorted(n.name for n in ast.walk(test_tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    if len(names) != st.TEST_COUNT:
        raise RuntimeError("TEST_INVENTORY_INVALID")
    original = s.read_json(b.ROOT/"reports/s2ob/caller-input-binding/manifest.json")
    manifest = b.build_manifest(st.RUN_ID, b.decode_manifest(original).events, b.digest(inv["ob"]))
    runrefs = refs + [policy_ref] + [s.file_reference("metadata", b.ROOT/p) for p in
        ("reports/s2ob/caller-input-binding/manifest.json", "reports/s2ob/caller-input-binding/evaluation-plan.json")]
    run = bindings(manifest, inv, runrefs)
    # Future qualification and evaluation binding are counted before they exist.
    prospective = (("metadata","@new-qualification",QUAL_CAP),
                   ("metadata","@evaluation-binding",3072))
    run_rows, violations = positions(run, prospective)
    input_root = b.ROOT/"sources/s2od-neutral"/st.QUAL_ID
    payloads = {}
    for name, raw in (("window.pcm", b"\0"*19200), ("frame.rgb", bytes((36,84,132))*(1920*1080))):
        payloads[name] = dict(path=(input_root/name).relative_to(b.ROOT).as_posix(), sha256=s.sha(raw), byte_count=len(raw))
        del raw
    events = []
    for n, kind in enumerate((b.AV,b.A),1):
        pcm = b.Payload(source_id=f"native-neutral-pcm-{n}", **payloads["window.pcm"])
        rgb = b.Payload(source_id=f"native-neutral-rgb-{n}", **payloads["frame.rgb"]) if kind == b.AV else None
        events.append(b.Event(f"native-neutral-event-{n}", n, kind, **b.expected_times(n,kind), pcm=pcm, rgb=rgb))
    neutral = b.build_manifest("native-neutral-terminal",tuple(events),b.digest(inv["ob"]))
    common = bindings(neutral, inv, refs+[policy_ref])
    # One native output plus all shared test/closure artifacts; no duplicate native records.
    extra = (("metadata","@qualification-files",QUAL_CAP),
             ("metadata","@preparation",PREPARATION_CAP), ("metadata","@metrics",1024),
             ("metadata","@qualification-balance",QUALIFICATION_BALANCE_CAP))
    native_rows, native_violations = positions(common, extra, qualification=True)
    violations += native_violations
    shape_bytes = len(b.canonical(assessment_shape()))
    if shape_bytes > st.CAPS["evaluation"]:
        violations.append(dict(code="ASSESSMENT_SHAPE_LIMIT", actual=shape_bytes, limit=st.CAPS["evaluation"]))
    preparation = dict(status="PRECONDITION_BLOCKED" if violations else "BOUND", test_calls=0, tests=names,
        run_positions=run_rows, native_positions=native_rows, violations=violations,
        local_caps=dict(st.CAPS,starter=refs[0][2]), qualification_cap=QUAL_CAP, preparation_cap=PREPARATION_CAP,
        assessment_shape_bytes=shape_bytes, limits=dict(st.od.LIMITS), budget_policy=policy_ref,
        qualification_version=QUALIFICATION_VERSION, qualification_metadata_limit=QUALIFICATION_METADATA,
        qualification_additions=extra,
        source_contributions=run["references"], source_digest=b.digest(inv),
        boundary="Native inputs are separate input stock (6240000 bytes), not system-generated evidence. No inputs read.")
    if len(b.canonical(preparation)) > PREPARATION_CAP:
        preparation["violations"].append(dict(code="PREPARATION_LIMIT",actual=len(b.canonical(preparation)),limit=PREPARATION_CAP))
    s.prior.save(out/"preparation.json",preparation)
    if preparation["violations"]:
        print(b.canonical(dict(status="PRECONDITION_BLOCKED",test_calls=0,violations=preparation["violations"])).decode())
        return 2
    s.prior.save(out/"native-common.json",common)
    pr = dict(run_id=st.QUAL_ID, tests=names, test_calls=1, retry=False,
        source_refs=refs, base_inventory_digest=b.digest(inv), payloads=payloads,
        budget_policy=policy_ref,
        qualification_version=QUALIFICATION_VERSION, qualification_metadata_limit=QUALIFICATION_METADATA,
        native_common_sha256=s.sha(b.canonical(common)), preparation_sha256=s.sha(b.canonical(preparation)),
        expected=dict(audio=2,nj=2,visual=1,verifications=1,native_complete=True,gates=False),
        qualification_cap=QUAL_CAP, log_policy="Full logs retained, overflow fails qualification; no universal log-size guarantee.")
    s.prior.save(out/"preregistration.json",pr)
    print("PRE_TEST_BOUND",flush=True)
    result = subprocess.run([sys.executable,"-B","-m","unittest","tests.test_s2od_native_start"],
        cwd=b.ROOT, env=dict(os.environ,OD_START_OUT=str(out)),capture_output=True,check=False)
    (out/"stdout.txt").write_bytes(result.stdout)
    (out/"stderr.txt").write_bytes(result.stderr)
    metrics = s.read_json(out/"metrics.json") if (out/"metrics.json").exists() else {}
    unchanged = refs == [s.file_reference("sources",b.ROOT/p) for p in OWN] and inv == s.inventory()
    good = result.returncode == 0 and unchanged and metrics == pr["expected"]
    q = b.sealed(dict(run_id=st.QUAL_ID,status="QUALIFIED" if good else "NOT_QUALIFIED",test_calls=1,
        passed_tests=st.TEST_COUNT if good else None,expected_tests=st.TEST_COUNT,exit_code=result.returncode,
        starter=refs[0],sources=refs,source_digest=b.digest(inv),hashes_unchanged=unchanged,
        native_complete=metrics.get("native_complete",False),gates=st.od.MAIN_GATE,
        evidence={name:s.sha((out/name).read_bytes()) for name in
                  ("preregistration.json","stdout.txt","stderr.txt","metrics.json") if (out/name).exists()}),"result_digest")
    used = sum((out/name).stat().st_size for name in q["evidence"] if name != "metrics.json")+len(b.canonical(q))
    if used > QUAL_CAP:
        q = b.sealed({**{k:v for k,v in q.items() if k!="result_digest"},"status":"NOT_QUALIFIED"},"result_digest")
    s.prior.save(out/"result.json",q)
    final = out/"native/final-balance.json"
    if final.exists():
        session_totals = s.read_json(final)["actual"]
        names = ("preparation.json", "preregistration.json", "stdout.txt", "stderr.txt", "metrics.json", "result.json")
        additions = [("metadata", name, (out/name).stat().st_size) for name in names if (out/name).exists()]
        size = 0
        for _ in range(12):
            balance = qualification_totals(session_totals, additions+[("metadata","qualification-balance.json",size)])
            balance.update(version=QUALIFICATION_VERSION, session_metadata_limit=65536,
                           qualification_metadata_limit=QUALIFICATION_METADATA,
                           common_and_policy="Counted once in native ledger; preparation retained in full.")
            new_size = len(b.canonical(balance))
            if new_size == size:
                break
            size = new_size
        else:
            raise RuntimeError("QUALIFICATION_BALANCE_UNSTABLE")
        s.prior.save(out/"qualification-balance.json",balance)
        if balance["violations"] or size > QUALIFICATION_BALANCE_CAP:
            q = b.sealed({**{k:v for k,v in q.items() if k!="result_digest"},"status":"NOT_QUALIFIED"},"result_digest")
            s.prior.save(out/"result.json",q)
            # Keep the final changed result size visible even on a budget failure.
            delta = (out/"result.json").stat().st_size - dict((p,n) for k,p,n in additions)["result.json"]
            balance["result_growth_after_budget_failure"] = delta
            s.prior.save(out/"qualification-balance.json",balance)
    print(b.canonical(dict(status=q["status"],qualification_bytes=used,metrics=metrics,gates=st.od.MAIN_GATE)).decode())
    return 0 if q["status"]=="QUALIFIED" else 1


if __name__=="__main__":
    raise SystemExit(main())
