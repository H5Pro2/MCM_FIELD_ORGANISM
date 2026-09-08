"""Administrative, read-only NR coverage admission; never an execution gate."""
import json
from tools import _s2nr_private_run as run

ROOT=run.ROOT
SCHEMA="s2nr.combined-qualification.v1"
BUNDLE="reports/s2nr/combined-qualification-v1/qualification.json"
QUAL_ID="s2nr-qualification-connection-20260908-01"
ENTRY="tools/_s2nr_private_run.py"
TEST="tests/test_s2nr_private_run.py"
ADDED=("tools/_s2nr_private_qualification_binding.py","tests/test_s2nr_private_qualification_binding.py",
    "reports/s2nr/qualify_connection_once.py","reports/s2nr/VERBUNDQUALIFIKATION_BINDUNG.md")
# Exact immutable evidence roots; the failed overall result is not reclassified.
PARTS=(
    ("TYPE_MASK","reports/s2nr/s2nr-runtime-binding-qualification-20260908-01",
     "f053795a4b4b98d8bd6e258338f97448462336deb9ff50e2704fdc8af757fe6f",
     "2fbac9ca4c4a1a794bcc774ef47a2924163f8311e18f01a4d8bae615a9a2513b",
     "S2NR_RUNTIME_BINDING_QUALIFIED",16,16,0),
    ("RUN_GROUPS_01_11","reports/s2nr/s2nr-main-binding-qualification-20260908-01",
     "31c63daa509d7e3f516ef769b5537a06d0da189c3135adddfa3d9d042efb0d41",
     "5497d82ced7440682801fa2d41474ef083ea76f2b6342fa2f725d44b9614a852",
     "NOT_QUALIFIED",12,11,1),
    ("FOCUSED_CONTROLS","reports/s2nr/s2nr-main-binding-focused-qualification-20260908-01",
     "586ec3e1240249858c5fa5f5291da688f32fb19f1e302dfa24018706df562699",
     "aa50dab768a841ff282854532cd5089a76cfa231e7888ac7619f17807c896502",
     "S2NR_FOCUSED_BINDING_QUALIFIED",3,3,0))
SCOPES=("closed types, masks, complements, isolation, read-only and lifecycle",
    "neutral materialization, continued history, provenance, counters and complete recording bounds",
    "failure progress with correct plan, evaluation verification binding, wrong-plan rejection")


def require(ok,code):
    run.require(ok,code)


def read_json(path,limit=65536):
    path=ROOT/path
    require(path.is_file() and path.stat().st_size<=limit,"QUALIFICATION_FILE_INVALID")
    return json.loads(path.read_bytes())


def evidence_parts():
    references,records=[],[]
    for i,(role,folder,sha,h,status,total,covered,exit_code) in enumerate(PARTS):
        path=folder+"/result.json"
        require(run.source.filehash(ROOT/path)==sha,"QUALIFICATION_PART_FILE_CHANGED")
        r=read_json(path,run.ng.MAX_BYTES)
        run.check(r,"result_digest")
        require(r["result_digest"]==h and r["status"]==status and r["exit_code"]==exit_code
            and r["expected_tests"]==total and r["unittest_calls"]==1
            and r["hashes_before"]==r["hashes_after"],"QUALIFICATION_PART_INVALID")
        transcript_path=folder+"/stderr.txt"
        require(run.source.filehash(ROOT/transcript_path)==r["stderr_sha256"],"QUALIFICATION_LOG_CHANGED")
        transcript=(ROOT/transcript_path).read_text(encoding="utf-8")
        pre=read_json(folder+"/preregistration.json",run.ng.MAX_BYTES)
        names=pre["test_ids"] if i==0 else pre["tests"]
        require(len(names)==total and len(set(names))==total,"QUALIFICATION_INVENTORY_INVALID")
        selected=names[:covered]
        require(all(any(line.startswith(name+" ") and line.endswith(" ... ok") for line in transcript.splitlines())
            for name in selected),"QUALIFICATION_SCOPE_NOT_PASSED")
        if i==1:
            require(names[-1]=="test_12_failure_progress_and_verification_required_for_evaluation"
                and "FAILED (failures=1)" in transcript,"HISTORICAL_FAILURE_CHANGED")
        else:
            require(r["passed_tests"]==total and transcript.rstrip().endswith("OK"),"QUALIFICATION_PART_NOT_PASSED")
        references.append(dict(role=role,path=path,file_sha256=sha,result_digest=h,status=status,
            executed_tests=total,covered_tests=covered,selected_tests=selected,scope=SCOPES[i],
            stderr_sha256=r["stderr_sha256"],preregistration_sha256=run.source.filehash(ROOT/folder/"preregistration.json")))
        records.append(r)
    return references,records


def make_bundle():
    references,(types,main,focused)=evidence_parts()
    base=dict(main["hashes_after"])
    changed_from_types=sorted(p for p,h in types["hashes_after"].items() if p in base and base[p]!=h)
    require(changed_from_types==["tools/_s2nr_private_runtime_binding.py","tools/_s2nr_private_runtime_verification.py"],"HISTORICAL_VERSION_TRANSITION_INVALID")
    changes=[p for p,h in base.items() if focused["hashes_after"][p]!=h]
    require(changes==[TEST],"FOCUSED_PRODUCT_CHANGED")
    test_change=dict(path=TEST,before=base[TEST],after=focused["hashes_after"][TEST],scope="test only; independent controls")
    base[TEST]=focused["hashes_after"][TEST]
    current=run.watched()
    require(set(current)==set(base)|set(ADDED) and all(current[p]==h for p,h in base.items() if p!=ENTRY),"QUALIFICATION_SOURCE_MISMATCH")
    require(current[ENTRY]!=base[ENTRY],"ADMINISTRATIVE_CONNECTION_NOT_BOUND")
    return run.sealed(dict(schema=SCHEMA,status="QUALIFICATION_COVERAGE_COMBINED",parts=references,
        previous_failure_preserved=True,no_new_full_test_run=True,
        test_change=test_change,qualified_source_table_digest=run.digest(base),current_sources=current,
        earlier_connection_changes=[dict(path=p,before=types["hashes_after"][p],after=main["hashes_after"][p],
            scope="covered by subsequent run-binding evidence, not the earlier 16-test run") for p in changed_from_types],
        administrative_connection=dict(path=ENTRY,before=base[ENTRY],after=current[ENTRY],
            added_sources={p:current[p] for p in ADDED},historically_tested=False,
            scope="qualification admission and source inventory only",qualification_id=QUAL_ID),
        execution_digest=run.EXECUTION_DIGEST,main_run_authorized=False),"qualification_digest")


def validate_bundle(bundle):
    """Same coverage checker used by the main entry; no status fallback."""
    try:
        require(type(bundle) is dict and bundle.get("qualification_digest")==run.digest(
            {k:v for k,v in bundle.items() if k!="qualification_digest"}),"QUALIFICATION_DIGEST_INVALID")
        require(len(run.canonical(bundle))<=65536,"QUALIFICATION_SIZE_EXCEEDED")
        require(len(bundle.get("parts",()))==3 and [p["role"] for p in bundle["parts"]]==[p[0] for p in PARTS],"QUALIFICATION_PART_MISSING")
        for p,(_,folder,sha,h,*_) in zip(bundle["parts"],PARTS,strict=True):
            require(p["result_digest"]==h and p["file_sha256"]==sha and p["path"]==folder+"/result.json","QUALIFICATION_PART_DIGEST_INVALID")
        require(bundle["current_sources"]==run.watched(),"QUALIFICATION_SOURCE_MISMATCH")
        expected=make_bundle()
        require(bundle==expected,"QUALIFICATION_COVERAGE_INVALID")
        return bundle["qualification_digest"]
    except run.S2NRRunError:
        raise
    except (KeyError,TypeError,ValueError,OSError) as exc:
        raise run.S2NRRunError("QUALIFICATION_BINDING_INVALID") from exc


def watched():
    values=run.watched()
    paths=[BUNDLE]
    for _,folder,*_ in PARTS:
        paths.extend(folder+"/"+p for p in ("result.json","preregistration.json","stderr.txt"))
    values.update({p:run.source.filehash(ROOT/p) for p in paths})
    return dict(sorted(values.items()))


def require_combined_qualification():
    bundle=read_json(BUNDLE)
    h=validate_bundle(bundle)
    # The administrative change has its own neutral result, never a historical claim.
    q=read_json("reports/s2nr/"+QUAL_ID+"/result.json",run.ng.MAX_BYTES)
    run.check(q,"result_digest")
    require(q["status"]=="S2NR_QUALIFICATION_CONNECTION_QUALIFIED" and q["run_id"]==QUAL_ID
        and q["passed_tests"]==q["expected_tests"]==4 and q["exit_code"]==0 and q["unittest_calls"]==1
        and q["qualification_digest"]==h and q["hashes_before"]==q["hashes_after"]==watched(),"ADMINISTRATIVE_QUALIFICATION_REQUIRED")
    return h
