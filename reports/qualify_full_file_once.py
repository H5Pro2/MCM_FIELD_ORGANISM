"""Bind full-file connection, all envelope positions, then one neutral call."""
import ast
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

from tools import _s2oe_media_session as m

p,b,s=m.p,m.b,m.s
OUT=b.ROOT/"reports/s2oe"/m.full.QUAL_ID
CAPS={"preregistration.json":8192,"preflight.json":32768,"stdout.txt":8192,
      "stderr.txt":16384,"result.json":8192,"REPORT.md":4096,
      "run-common.json":16384,"settings.json":4096,"budget.json":32768}
BASE_CAPS = dict(CAPS)
CAPS.update({"precondition-stop.json":512,"qualification.claim":4})
BUDGET_VERSION = "s2oe.full-file-qualification-budget.v2"
QUAL_LIMITS = dict(p.SESSION_LIMITS, metadata=262144)
NATIVE_DIRS = ("native-full", "native-failure")
TEMP_RESERVE = 32768


def limit_violations(totals, limits):
    return [key for key, value in totals.items() if value > limits[key]]


def collect_log(pipe, path, limit):
    """Bound storage while counting every received byte; overflow is never a pass."""
    received = stored = 0
    with path.open("xb") as stream:
        while chunk := pipe.read(4096):
            received += len(chunk)
            kept = chunk[:max(0, limit-stored)]
            stream.write(kept)
            stored += len(kept)
    return dict(received=received, stored=stored, complete=received==stored,
                omitted=received-stored, limit=limit)


def actual_balance(directory, *, reserves=None):
    """Native classification from the existing ledger; all other physical files counted.

    Different stored paths count separately, conservatively even leftover hard
    links. An orphan/unknown temporary file is retained and fails closure.
    No receptor, scan or memory verifier is invoked here.
    """
    directory = Path(directory)
    totals = {key:0 for key in QUAL_LIMITS}
    files, sessions, violations, references = {}, {}, [], {}
    for name in NATIVE_DIRS:
        path = directory/name
        if not path.exists():
            continue
        mandatory = [path/x for x in ("common.json","record.json","session.json")]
        if not all(x.is_file() for x in mandatory):
            violations.append(name+":INCOMPLETE_ENVELOPE")
            continue
        common = s.read_json(mandatory[0])
        record, session = s.unpack(s.read_json(mandatory[1]),s.read_json(mandatory[2]),common)
        proof_paths = [x for x in (path/"verification.json",path/"verification.claim") if x.exists()]
        row = p.ledger(record,session,common,proof_bytes=sum(x.stat().st_size for x in proof_paths),report_bytes=0)
        sessions[name] = row
        violations.extend(name+":"+x for x in row["violations"])
        for key,n in row["totals"].items(): totals[key] += n
        for x in mandatory+proof_paths:
            files[x.resolve()] = dict(bytes=x.stat().st_size, kind="native-envelope" if x in mandatory else "verification")
        for kind,relative,n,pin in common["references"]:
            x = (b.ROOT/relative).resolve()
            p.need(s.file_reference(kind,x)==[kind,relative,n,pin],"REFERENCE_CHANGED")
            if x in references:
                p.need(references[x]==(kind,n,pin),"REFERENCE_CONFLICT")
                totals[kind] -= n
                totals["total"] -= n
            else:
                references[x]=(kind,n,pin)
                files[x]=dict(bytes=n,kind=kind)
    for x in sorted(directory.rglob("*")):
        if not x.is_file() or x.resolve() in files: continue
        relative=x.relative_to(directory).as_posix()
        n=x.stat().st_size
        files[x.resolve()]=dict(bytes=n,kind="metadata")
        totals["metadata"] += n
        totals["total"] += n
        if relative not in CAPS and relative not in ("neutral-common.json","inventory.json"):
            violations.append(relative+":UNEXPECTED_OR_TEMPORARY_FILE")
        if relative in CAPS and n>CAPS[relative]: violations.append(relative+":LOCAL_LIMIT")
    # Independent path-byte total, including every leftover temporary path.
    physical=sum(x["bytes"] for x in files.values())
    if totals["total"] != physical: violations.append("PHYSICAL_TOTAL_MISMATCH")
    held={}
    for name,cap in (reserves or {}).items():
        p.need(not (directory/name).exists(),"RESERVE_ALREADY_MATERIALIZED")
        held[name]=cap
        totals["metadata"] += cap
        totals["total"] += cap
    totals["shared"]=sum(totals[k] for k in ("sources","nj","formations","generations"))
    violations.extend("qualification:"+x for x in limit_violations(totals,QUAL_LIMITS))
    return dict(version=BUDGET_VERSION,totals=totals,limits=QUAL_LIMITS,
        session_limits=p.SESSION_LIMITS,sessions=sessions,physical_bytes=physical,
        files={x.relative_to(b.ROOT).as_posix():v for x,v in files.items()},
        reserves=held,violations=violations)


def save(name,value):
    s.prior.save(OUT/name,value)


def bound_common(source, run_id, extra=()):
    directory=b.ROOT/"reports/s2oc"/s.QUAL_ID
    anchor=s.read_json(directory/"caller-common.json")
    base,inv=s.qualified_common(b.decode_manifest(anchor["manifest"]),directory)
    spec=p.build(run_id,source,b.digest(m.inventory(True)),mode=p.FULL_VERSION)
    refs=list(base["references"])
    for name in m.FULL_OWN:
        ref=s.file_reference("sources",b.ROOT/name)
        if not any(x[1]==name for x in refs): refs.append(ref)
    refs += [s.file_reference("metadata",directory/"caller-common.json"),
             s.file_reference("sources",OUT/"inventory.json"),*extra]
    return m.bind_common(spec,base,refs)


def compact(upper):
    return dict(limits=upper["limits"], violations=upper["violations"],
        shared_references=upper["positions"][0]["success"]["contributions"]["references"],
        positions=[dict(completed=row["completed"], **{name:dict(totals=row[name]["totals"],
            contributions={k:v for k,v in row[name]["contributions"].items() if k!="references"},
            violations=row[name]["violations"]) for name in ("success","failure")}) for row in upper["positions"]])


def prepare():
    p.need(not OUT.exists(),"QUALIFICATION_ID_USED")
    OUT.mkdir()
    sources=m.inventory(True);save("inventory.json",sources)
    neutral=bound_common(p.Source(str(b.ROOT/"sources/s2oe-worker-neutral/full-file-unused.bin"),"0"*64,32),
                         "full-file-neutral-fixture")
    save("neutral-common.json",neutral)
    upper=m.full.envelope(neutral)
    # Two native fixtures: full success and one-step failure. All native bodies
    # are maximum-sized, not measured from an agreeable memory trajectory.
    a=upper["positions"][20]["success"]["totals"]
    z=upper["positions"][1]["failure"]["totals"]
    refmeta=sum(n for k,_,n,_ in neutral["references"] if k=="metadata")
    extra=sum(CAPS.values())+TEMP_RESERVE
    totals=dict(metadata=a["metadata"]+z["metadata"]-refmeta+extra+len(b.canonical(neutral)),
        sources=a["sources"],verification=262144,nj=a["nj"]+z["nj"],
        formations=a["formations"]+z["formations"],generations=a["generations"]+z["generations"])
    totals["shared"]=totals["sources"]+totals["nj"]+totals["formations"]+totals["generations"]
    totals["total"]=a["total"]+z["total"]-refmeta-a["sources"]-262144+extra+len(b.canonical(neutral))
    violations=upper["violations"]+["qualification:"+k for k in limit_violations(totals,QUAL_LIMITS)]
    tests=sorted(n.name for n in ast.walk(ast.parse((b.ROOT/"tests/test_s2oe_full_file.py").read_text()))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    report=compact(upper)
    if len(b.canonical(report))>CAPS["preflight.json"]: violations.append("preflight-file")
    save("preflight.json",report)
    registration=dict(run_id=m.full.QUAL_ID,sources_digest=b.digest(sources),tests=tests,
        budget_version=BUDGET_VERSION,base_reserves=BASE_CAPS,base_reserve_total=sum(BASE_CAPS.values()),
        caps=CAPS,temporary_reserve=TEMP_RESERVE,qualification_totals=totals,
        limits=QUAL_LIMITS,session_limits=p.SESSION_LIMITS,violations=violations,
        single_test_call=True,real_media_reads=0,expected_native_formations=21,expected_native_scans=0,
        atomic_temporary_boundary="Existing write-once pending file then hard-link publication, no second copied payload. Orphan files remain counted and fail closure.",
        log_boundary="Bounded stdout/stderr; every received byte counted. Overflow means incomplete diagnosis and NOT_QUALIFIED, never silently passed.",
        worker_test_boundary="Neutral protocol/iterator fixtures; no new OS codec qualification.",gates=False)
    registration["coverage"]={
        "selection_time_profile":"test_01_selection_and_clocks, test_02_frame_selection, test_03_mode_mixing",
        "decoder_limits_eof_drain":"test_04_decoder_limits, test_05_packet_limit, test_06_early_eof, test_07_drain_without_conversion",
        "protocol_cancellation":"test_08_worker_drain_protocol, test_09_stop_during_drain, test_13_player_stop_phase",
        "all_prefixes_native_closures":"test_10_all_envelopes, test_11_native_full_session, test_12_failure_after_formation",
        "qualification_session_separation":"test_14_qualification_scope_and_boundaries",
        "logs_temporary_files":"test_15_bounded_logs_and_temporary_accounting",
        "physical_ledger_references":"test_16_combined_closure_and_reference_integrity"}
    save("preregistration.json",registration)
    print(json.dumps(registration,indent=2))
    if violations:
        save("precondition-stop.json",dict(status="PRECONDITION_BLOCKED",test_calls=0,
                                          totals=totals,violations=violations))
        return 2
    return 0


def qualify():
    reg=s.read_json(OUT/"preregistration.json")
    p.need(not reg["violations"] and reg["sources_digest"]==b.digest(m.inventory(True)),"PREFLIGHT_INVALID")
    with (OUT/"qualification.claim").open("xb") as stream: stream.write(b"once")
    log_rows={}
    proc=subprocess.Popen([sys.executable,"-m","unittest","tests.test_s2oe_full_file","-v"],
        cwd=b.ROOT,env=dict(os.environ,FULL_FILE_QUAL_OUT=str(OUT),PYTHONDONTWRITEBYTECODE="1"),
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    def capture(name, pipe):
        try:
            log_rows[name]=collect_log(pipe,OUT/name,CAPS[name])
        except OSError as exc:
            log_rows[name]=dict(complete=False,error_class=type(exc).__name__)
        finally:
            pipe.close()
    threads=[threading.Thread(target=capture,args=(name,pipe))
        for name,pipe in (("stdout.txt",proc.stdout),("stderr.txt",proc.stderr))]
    for thread in threads: thread.start()
    proc.wait()
    for thread in threads: thread.join()
    text="".join((OUT/name).read_text(errors="replace") for name in ("stdout.txt","stderr.txt") if (OUT/name).exists())
    unchanged=reg["sources_digest"]==b.digest(m.inventory(True))
    passed=proc.returncode==0 and f"Ran {len(reg['tests'])} tests" in text and unchanged and all(x["complete"] for x in log_rows.values())
    held={name:CAPS[name] for name in ("result.json","budget.json","REPORT.md")}
    try:
        balance=actual_balance(OUT,reserves=held)
    except Exception as exc:
        # Failed parsing is a technical failure, never an excuse to omit bytes.
        balance=dict(violations=["LEDGER_FAILED:"+type(exc).__name__],
            error_code=getattr(exc,"code",None),
            files={str(x.relative_to(OUT)):x.stat().st_size for x in OUT.rglob("*") if x.is_file()},
            diagnosis_complete=False)
    violations=list(balance["violations"])
    if not all(x["complete"] for x in log_rows.values()): violations.append("INCOMPLETE_LOG_DIAGNOSIS")
    balance["stage"]="PRE_PUBLICATION_WITH_FINITE_CLOSURE_RESERVES"
    if len(b.canonical(balance))>CAPS["budget.json"]:
        violations.append("budget.json:LOCAL_LIMIT")
    save("budget.json",balance)
    files={str(x.relative_to(OUT)):dict(bytes=x.stat().st_size,sha256=s.sha(x.read_bytes()))
           for x in OUT.rglob("*") if x.is_file()}
    result=b.sealed(dict(status="QUALIFIED" if passed and not violations else "NOT_QUALIFIED",
        sources=m.inventory(True),test_calls=1,expected_tests=len(reg["tests"]),exit_code=proc.returncode,
        sources_unchanged=unchanged,files=files,logs=log_rows,
        budget_version=BUDGET_VERSION,closure_reserves=held,violations=violations,gates=False),"result_digest")
    if len(b.canonical(result))>CAPS["result.json"]:
        result=b.sealed({**{k:v for k,v in result.items() if k!="result_digest"},
            "status":"NOT_QUALIFIED","violations":violations+["result.json:LOCAL_LIMIT"]},"result_digest")
    save("result.json",result)
    # The saved result and closure replace reservations; no recursive self-ledger.
    try:
        closure=actual_balance(OUT,reserves={"REPORT.md":CAPS["REPORT.md"]})
    except Exception:
        closure=balance
    print(json.dumps(dict(status=result["status"],totals=closure.get("totals"),
        violations=closure["violations"])))
    return 0 if result["status"]=="QUALIFIED" and not closure["violations"] else 1


def bind_run():
    """Administrative preparation only. Source metadata comes from the closed binding."""
    from tools import _s2oe_local_player as player
    q=s.read_json(OUT/"result.json")
    b.check_root(q,"result_digest")
    p.need(q["status"]=="QUALIFIED" and q["sources"]==m.inventory(True),"QUALIFICATION_INVALID")
    run_id="media-full-file-20260912-01"
    directory=b.ROOT/"reports/s2oe/full-file-run-binding-20260912-01"
    target=b.ROOT/"reports/s2oe"/run_id
    p.need(not directory.exists() and not target.exists()
        and not target.with_suffix(".authorization-used").exists(),"OUTPUT_CONFLICT")
    old=s.read_json(b.ROOT/"reports/s2oe/media-memory-video-20260912-01/common.json")
    source=p.decode(old["manifest"]).source
    # The active admission consumes current inventory and qualification result.
    # Logs, preregistration and closure are retained and counted as its evidence;
    # native qualification records remain explicitly archived, not re-executed.
    names=("result.json","preregistration.json","budget.json","stdout.txt","stderr.txt","qualification.claim","REPORT.md")
    refs=[s.file_reference("metadata",OUT/name) for name in names]
    common=bound_common(source,run_id,refs)
    m.check_common(p.decode(common["manifest"]),common,s.inventory())
    extra=CAPS["run-common.json"]+CAPS["settings.json"]+32768
    upper=m.full.envelope(common,metadata_reserve=extra)
    plan=compact(upper)
    plan.update(run_id=run_id,status="BOUND_AWAITING_AUTHORIZATION" if not upper["violations"] else "PRECONDITION_BLOCKED",
        active_qualification_archive_boundary="Native neutral records are audit archive. Runtime admission consumes result and current sources, not a replay or numerical re-verification of that archive.")
    p.need(len(b.canonical(plan))<=32768 and len(b.canonical(common))<=CAPS["run-common.json"],"RUN_BINDING_LIMIT")
    directory.mkdir()
    s.prior.save(directory/"budget.json",plan)
    if upper["violations"]:
        print(json.dumps(plan));return 2
    s.prior.save(directory/"common.json",common)
    settings=dict(version=player.VERSION,status="BOUND_AWAITING_AUTHORIZATION",
        common=dict(path=(directory/"common.json").relative_to(b.ROOT).as_posix(),sha256=s.sha(b.canonical(common))),
        budget=dict(path=(directory/"budget.json").relative_to(b.ROOT).as_posix(),sha256=s.sha(b.canonical(plan))),
        output=target.relative_to(b.ROOT).as_posix())
    p.need(len(b.canonical(settings))<=CAPS["settings.json"],"SETTINGS_LIMIT")
    s.prior.save(directory/"settings.json",settings)
    print(json.dumps(dict(run_id=run_id,common_sha256=s.sha(b.canonical(common)),
        settings_sha256=s.sha(b.canonical(settings)),budget_sha256=s.sha(b.canonical(plan)),
        status=plan["status"],authorization_created=False,gates=False)))
    return 0


if __name__=="__main__":
    p.need(len(sys.argv)==2 and sys.argv[1] in ("prepare","qualify","bind"),"COMMAND_INVALID")
    raise SystemExit({"prepare":prepare,"qualify":qualify,"bind":bind_run}[sys.argv[1]]())
