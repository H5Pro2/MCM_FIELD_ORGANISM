"""Finite two-arm process caller. No gate is opened merely by importing this file."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import os
import subprocess
import sys
import traceback
from threading import Lock, Thread

from tools import _memory_checkpoint as c
from tools import _checkpoint_transfer_budget as budget

VERSION="checkpoint.transfer-entry.v3"
ROLES=("reference","save","restore")
LOG_CAP=8192


def bounded_process(command,directory,role,*,timeout=180):
    """Stop the producer on overflow; never claim an overflow log is complete."""
    directory=Path(directory)
    state=dict(stored_bytes=0,overflow=False,reader_errors=[])
    lock=Lock()
    with (directory/(role+".stdout")).open("xb") as out, (directory/(role+".stderr")).open("xb") as err:
        process=subprocess.Popen(command,cwd=c.b.ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            env=dict(os.environ,OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1"))
        def capture(source,target):
            try:
                while True:
                    chunk=source.read(1024)
                    if not chunk:break
                    with lock:
                        room=LOG_CAP-state["stored_bytes"]
                        part=chunk[:room]
                        target.write(part);target.flush()
                        state["stored_bytes"]+=len(part)
                        if len(chunk)>room:
                            state["overflow"]=True
                            process.kill()
                            break
            except Exception as exc:
                with lock:state["reader_errors"].append(type(exc).__name__)
                process.kill()
            finally:source.close()
        threads=[Thread(target=capture,args=pair) for pair in ((process.stdout,out),(process.stderr,err))]
        for thread in threads:thread.start()
        timed_out=False
        try:process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out=True;process.kill();process.wait()
        finally:
            for thread in threads:thread.join()
        details=dict(state,pid=process.pid,exit_code=process.returncode,timed_out=timed_out,
            limit=LOG_CAP,wait_completed=True)
        need(not timed_out,"TRANSFER_TIMEOUT",details)
        need(not state["reader_errors"],"TRANSFER_LOG_WRITE_FAILED",details)
        need(not state["overflow"],"TRANSFER_LOG_LIMIT",details)
        return process.returncode


def need(ok,code,details=None):c.require(ok,code,details)
def load(path):return json.loads(Path(path).read_bytes())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_binding(path):
    value=load(path)
    need(value["version"]==VERSION and value["ready"] is True,"TRANSFER_NOT_READY")
    need(value.get("binding_digest")==c.b.digest({k:v for k,v in value.items() if k!="binding_digest"}),"TRANSFER_BINDING_DIGEST")
    manifest=c.b.decode_manifest(value["manifest"])
    need(value["cut"]==4 and len(manifest.events)==7,"TRANSFER_CUT")
    need([e.kind for e in manifest.events]==[c.b.AV]*4+[c.b.A,c.b.V,c.b.AV],"TRANSFER_SEQUENCE")
    need(value["output"]=="reports/"+manifest.run_id,"TRANSFER_OUTPUT_BINDING")
    need(type(value["metadata_by_phase"]) is dict,"TRANSFER_BUDGET_BINDING")
    need(value["budget"]==budget.envelope(value["source_charge"],value["metadata_by_phase"]) and not value["budget"]["violations"],"TRANSFER_BUDGET_BINDING")
    need(set(value["charged_sources"])==set(value["required_sources"]),"TRANSFER_SOURCE_INVENTORY")
    need("tools/_checkpoint_transfer_entry.py" in value["charged_sources"],"TRANSFER_SOURCE_INVENTORY")
    for relative,expected in value["inventory"]["files"].items():
        file=c.b.ROOT/relative
        need(file.stat().st_size==expected["bytes"] and sha(file)==expected["sha256"],"TRANSFER_SOURCE_CHANGED")
    for ref in value["qualification_references"]:
        file=c.b.ROOT/ref["path"]
        need(file.stat().st_size==ref["bytes"] and sha(file)==ref["sha256"],"TRANSFER_QUALIFICATION_CHANGED")
    results={ref["role"]:load(c.b.ROOT/ref["path"]) for ref in value["qualification_references"] if ref["role"].endswith("result")}
    need(set(results)=={"base-result","focus-result","entry-result","authorization-result"},"TRANSFER_QUALIFICATION_COVERAGE")
    need(results["base-result"]["status"]=="NOT_QUALIFIED" and results["base-result"]["hashes_unchanged"] is True,
         "TRANSFER_BASE_COVERAGE")
    need(all(results[key]["status"]=="QUALIFIED" and results[key]["test_calls"]==1
             for key in ("focus-result","entry-result","authorization-result")),"TRANSFER_QUALIFICATION_COVERAGE")
    return value,manifest


def claim(path,content):
    try:
        with Path(path).open("xb") as f:f.write(content)
    except OSError as exc:raise c.CheckpointError("TRANSFER_ALREADY_USED") from exc


def expected_authorization(binding_path,value,manifest):
    return dict(version="checkpoint.transfer-authorization.v2",approved=True,uses=1,
        run_id=manifest.run_id,binding_sha256=sha(binding_path),
        manifest_digest=manifest.manifest_digest,profile_digest=manifest.profile_digest,
        code_digest=c.b.digest(value["inventory"]),
        roles=dict(reference=dict(first=1,last=7,uses=1),save=dict(first=1,last=4,uses=1),
                   restore=dict(first=5,last=7,uses=1)))


def validate_authorization(binding_path,value,manifest,path):
    expected_path=(c.b.ROOT/value["authorization_path"]).resolve()
    need(Path(path).resolve()==expected_path,"TRANSFER_AUTHORIZATION_PATH")
    try:
        with expected_path.open("rb") as stream:raw=stream.read(16385)
        need(len(raw)<=16384,"TRANSFER_AUTHORIZATION_SIZE")
        permit=json.loads(raw)
    except (OSError,ValueError,TypeError) as exc:
        raise c.CheckpointError("TRANSFER_AUTHORIZATION_INVALID") from exc
    need(permit==expected_authorization(binding_path,value,manifest),"TRANSFER_AUTHORIZATION_INVALID")
    need(raw==c.b.canonical(permit),"TRANSFER_AUTHORIZATION_NORMALFORM")
    return hashlib.sha256(raw).hexdigest()


def authorize_worker(binding_path,value,manifest,directory,role):
    need(role in ROLES,"TRANSFER_ROLE")
    need(Path(directory).resolve()==(c.b.ROOT/value["output"]).resolve(),"TRANSFER_AUTHORIZATION_OUTPUT")
    path=c.b.ROOT/value["authorization_path"]
    authorization_digest=validate_authorization(binding_path,value,manifest,path)
    try:
        with Path(str(path)+".used").open("rb") as stream:consumed=stream.read(65)
    except OSError as exc:raise c.CheckpointError("TRANSFER_AUTHORIZATION_NOT_CONSUMED") from exc
    need(consumed==authorization_digest.encode("ascii"),"TRANSFER_AUTHORIZATION_CONSUMPTION")
    section=expected_authorization(binding_path,value,manifest)["roles"][role]
    claim(Path(directory)/(role+".claim"),c.b.canonical(dict(authorization=authorization_digest,role=role,section=section)))
    return section


def full_ledger(directory,*,extra=()):
    result=c.artifact_ledger(directory,extra=extra)
    prereg=load(Path(directory)/"preregistration.json")
    for ref in prereg.get("external_evidence",[]):
        path=c.b.ROOT/ref["path"]
        raw=path.read_bytes()
        need(len(raw)==ref["bytes"] and hashlib.sha256(raw).hexdigest()==ref["sha256"],"TRANSFER_EXTERNAL_CHANGED")
        try:value=json.loads(raw)
        except ValueError:value=None
        classes=c.budgets.classify(len(raw),value)
        result["files"].append(dict(path=ref["path"],bytes=len(raw),classes=classes,reference=True))
        for key,n in classes.items():result["totals"][key]+=n
        result["totals"]["shared"]+=sum(classes[k] for k in ("sources","nj","formations","generations"))
        result["totals"]["total"]+=len(raw)
    result["violations"]=[k for k,v in budget.LIMITS.items() if result["totals"][k]>v]
    result["limits"]=dict(budget.LIMITS)
    return result


def publish(path,value):
    path=Path(path)
    raw=c.b.canonical(c.references(value,c.load_common(path.parent)))
    ledger=full_ledger(path.parent,extra=((path.name,raw,value),(path.name+".pending",raw,value)))
    need(not ledger["violations"],"TRANSFER_BUDGET",ledger)
    pending=path.with_name(path.name+".pending")
    need(not path.exists() and not pending.exists(),"CHECKPOINT_EXISTS")
    try:
        with pending.open("xb") as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.link(pending,path)
        pending.unlink()
    except OSError as exc:
        raise c.CheckpointError("TRANSFER_WRITE_FAILED",dict(path=path.name,
            pending_exists=pending.exists(),target_exists=path.exists())) from exc


def suspend_transfer(session,path):
    """Same native checkpoint, private publication budget; no historical default change."""
    need(session._lock.acquire(blocking=False),"CHECKPOINT_BUSY")
    try:
        need(not session._terminal,"CHECKPOINT_TERMINAL")
        value=c.export(session._runtime,session._manifest,session._code,session.accounting())
        c.validate(value,session._manifest,session._code)
        session._runtime.close();session._terminal=True
        publish(path,value)
        return value["checkpoint_digest"]
    except Exception as exc:
        if session.failure is None:session.fail(exc,"CHECKPOINT_PUBLISH")
        raise
    finally:session._lock.release()


def error_details(exc,phase,**progress):
    return dict(code=getattr(exc,"code",type(exc).__name__),phase=phase,
                details=getattr(exc,"details",None),progress=progress)


def point(session):
    runtime=session._runtime
    return c.copy_json(dict(snapshot=asdict(runtime.subject.snapshot()),
        field_component_digest=runtime.fb.state.field.snapshot().digest(),
        memory_digest=runtime.mb.state.state_digest,births=runtime.births,chain=runtime.chain,
        accounting=session.accounting()))


def worker(binding_path,directory,role):
    session=None
    try:
        value,manifest=check_binding(binding_path);directory=Path(directory)
        need(role in ROLES,"TRANSFER_ROLE")
        dispatch=load(directory/"dispatch.json")
        need(dispatch["binding_sha256"]==sha(binding_path) and dispatch["run_id"]==manifest.run_id,"TRANSFER_DISPATCH")
        authorize_worker(binding_path,value,manifest,directory,role)
        c.MAIN_GATE=True
        session=c.NeutralCheckpointSessionV1(manifest,manifest.code_digest,mode="CALLER_PAYLOADS",
            checkpoint=directory/"checkpoint.json" if role=="restore" else None)
        start=value["cut"] if role=="restore" else 0
        end=value["cut"] if role=="save" else len(manifest.events)
        cut=point(session) if role=="restore" else None
        accounts=[]
        for event in manifest.events[start:end]:
            session.next(event)
            accounts.append(session.accounting())
            if event.ordinal==value["cut"]:cut=point(session)
            # Before another payload, account for a complete failure prefix.
            prefix=dict(prefix=c.prefix_record(session._runtime))
            raw=c.b.canonical(c.references(prefix,c.load_common(directory)))
            ledger=full_ledger(directory,extra=(("prospective-prefix",raw,prefix),))
            need(not ledger["violations"],"TRANSFER_BUDGET",ledger)
        if role=="save":
            projected=c.export(session._runtime,manifest,manifest.code_digest,session.accounting())
            raw=c.b.canonical(c.references(projected,c.load_common(directory)))
            ledger=full_ledger(directory,extra=(("checkpoint.json",raw,projected),("checkpoint.json.pending",raw,projected)))
            need(not ledger["violations"],"TRANSFER_BUDGET",ledger)
            checkpoint_digest=suspend_transfer(session,directory/"checkpoint.json")
            result=dict(status="SUSPENDED_PREFIX",checkpoint_digest=checkpoint_digest)
        else:
            result=dict(status="RECORDING_COMPLETE",record=session.close())
        result.update(role=role,pid=os.getpid(),cut=cut,accounts=accounts,closed=session._runtime.closed)
        c.MAIN_GATE=False
        result["gate"]=False
        publish(directory/(role+".json"),result)
        return 0
    except Exception as exc:
        if session is not None and not session._terminal:session.fail(exc,"TRANSFER_WORKER")
        traceback.print_exc()
        failure=dict(status="NOT_EVALUABLE",role=role,pid=os.getpid(),
            failure=error_details(exc,"TRANSFER_WORKER",session_initialized=session is not None),
            closed=session is None,gate=False)
        if session is not None:
            # Preserve the completed prefix; it is not a full-session success claim.
            names=(role+".json",role+".json.pending")
            if role=="save":names+=("checkpoint.json","checkpoint.json.pending")
            existing=next((Path(directory)/name for name in names
                if (Path(directory)/name).exists()),None)
            failure.update(
                failure=session.failure or error_details(exc,"TRANSFER_WORKER"),
                prefix=c.prefix_record(session._runtime) if existing is None else None,
                available_evidence=None if existing is None else existing.name,
                accounting=session.accounting(),
                closed=session._runtime.closed,gate=False)
        try:publish(Path(directory)/(role+"-failure.json"),failure)
        except Exception:traceback.print_exc()
        return 1
    finally:
        c.MAIN_GATE=False


def launch_stages(binding,directory,spawn):
    stages=[]
    for role in ROLES:
        try:
            if role=="restore":
                need(stages[-1]["exit_code"]==0 and (Path(directory)/"checkpoint.json").is_file(),"TRANSFER_CHECKPOINT_MISSING")
            code=spawn(role)
        except Exception as exc:
            raise c.CheckpointError(getattr(exc,"code","TRANSFER_SPAWN_FAILED"),
                error_details(exc,"PROCESS_DISPATCH",completed_stages=stages,active_role=role)) from exc
        stages.append(dict(role=role,exit_code=code,wait_completed=True))
        need(code==0,"TRANSFER_CHILD_FAILED",dict(completed_stages=stages,active_role=role))
    return stages


def verify_total(directory,manifest,cut):
    """One overall read-only invocation; no field or memory advancement."""
    directory=Path(directory)
    claim(directory/"verification.claim",b"once")
    reference=c.read_checkpoint(directory/"reference.json")
    saved=c.read_checkpoint(directory/"save.json")
    restored=c.read_checkpoint(directory/"restore.json")
    checkpoint=c.read_checkpoint(directory/"checkpoint.json")
    stages=load(directory/"processes.json")
    need([s["role"] for s in stages]==list(ROLES) and all(s["exit_code"]==0 and s["wait_completed"] for s in stages),"TRANSFER_PROCESS_CHAIN")
    need(saved["pid"]!=restored["pid"] and saved["pid"]==checkpoint["process_id"],"TRANSFER_PROCESS_IDENTITY")
    need(saved["status"]=="SUSPENDED_PREFIX" and
         saved["checkpoint_digest"]==checkpoint["checkpoint_digest"],"TRANSFER_CHECKPOINT_BINDING")
    need(all(x["closed"] and x["gate"] is False for x in (reference,saved,restored)),"TRANSFER_LIFECYCLE")
    config=c.r.nn.profile.build_config()
    proofs=[]
    for arm in (reference,restored):
        need(arm["status"]=="RECORDING_COMPLETE" and len(arm["record"]["rows"])==len(manifest.events),"TRANSFER_COMPLETENESS")
        proofs.append(c.verify.verify_core(arm["record"],config,manifest))
        validate_manifest_record(arm["record"],manifest)
    c.validate(checkpoint,manifest,manifest.code_digest)
    need(checkpoint["stream"]["processed_event_count"]==cut,"TRANSFER_CUT")
    accounts=saved["accounts"]+restored["accounts"]
    for xs in (reference["accounts"],accounts):
        need(len(xs)==len(manifest.events),"TRANSFER_ACCOUNTING")
        for n,account in enumerate(xs,1):c.validate_accounting(account,manifest,n)
    need(saved["cut"]==restored["cut"],"TRANSFER_RESTORE_BOUNDARY")
    comparisons=[dict(ordinal=i+1,record_equal=c.b.canonical(a)==c.b.canonical(b),
        accounting_equal=reference["accounts"][i]==accounts[i]) for i,(a,b) in
        enumerate(zip(reference["record"]["rows"],restored["record"]["rows"],strict=True))]
    result=c.b.sealed(dict(status="RECORDING_COMPLETE",evaluation_allowed=True,
        proofs=proofs,rows=comparisons,cut_equal=reference["cut"]==saved["cut"],
        records_equal=reference["record"]==restored["record"],
        boundary="Native per-arm receipts validated; field components compared by full-snapshot digests, not replayed.",
        main_gate=False),"verification_digest")
    c.checked_size(result,131072,"TRANSFER_VERIFICATION")
    publish(directory/"verification.json",result)
    return result


def validate_manifest_record(record,manifest):
    from tools import _s2ng_private_comparison_verification as decoder
    config=c.r.nn.profile.build_config()
    need(len(record["inputs"])==len(manifest.events),"TRANSFER_MANIFEST_LENGTH")
    for spec,raw,receipt in zip(manifest.events,record["inputs"],record["source_receipts"],strict=True):
        event=decoder.decode_input(raw,config)
        need(event.event_id==spec.event_id and event.ordinal==spec.ordinal and event.event_type==spec.kind,
             "TRANSFER_MANIFEST_EVENT")
        if spec.pcm is not None:
            need(receipt["nj"]["pcm_digest"]==spec.pcm.sha256,"TRANSFER_MANIFEST_AUDIO")
        if spec.rgb is not None:
            need(receipt["rgb_digest"]==spec.rgb.sha256,"TRANSFER_MANIFEST_VISUAL")


def comparison_rows(left,right):
    need(len(left["rows"])==len(right["rows"]),"TRANSFER_COMPARISON_LENGTH")
    result=[]
    for n,(a,b) in enumerate(zip(left["rows"],right["rows"],strict=True),1):
        result.append(dict(ordinal=n,
            perception_equal=left["inputs"][n-1]==right["inputs"][n-1],
            memory_equal=a["memory"]==b["memory"],field_equal=a["field"]==b["field"],
            generations_equal=a["generations"]==b["generations"],
            snapshot_equal=a["post"]==b["post"],step_equal=a["step"]==b["step"],
            source_equal=left["source_receipts"][n-1]==right["source_receipts"][n-1]))
    return result


def evaluate(directory,proof,manifest):
    need(proof["status"]=="RECORDING_COMPLETE" and proof["evaluation_allowed"],"TRANSFER_EVALUATION_BLOCKED")
    directory=Path(directory)
    need(c.read_checkpoint(directory/"verification.json")==proof,"TRANSFER_PROOF_BINDING")
    a=c.read_checkpoint(directory/"reference.json")["record"]
    b=c.read_checkpoint(directory/"restore.json")["record"]
    decisions=[]
    for spec,left,right in zip(manifest.events,a["rows"],b["rows"],strict=True):
        if spec.kind==c.b.AV:continue
        decisions.append(dict(event_id=spec.event_id,reference=left["step"]["context_status"],
            restored=right["step"]["context_status"],equal=left["step"]["context_status"]==right["step"]["context_status"]))
    success=proof["cut_equal"] and proof["records_equal"] and all(x["accounting_equal"] for x in proof["rows"])
    result=dict(status="CONFIRMED" if success else "FALSIFIED",decisions=decisions,
        rows=proof["rows"],components=comparison_rows(a,b),cut_equal=proof["cut_equal"],verification_digest=proof["verification_digest"],
        scope="Same finite continuation after orderly process restart; reused sources, no general crash recovery.")
    c.checked_size(result,8192,"TRANSFER_EVALUATION")
    publish(directory/"evaluation.json",result)
    return result


def run(binding_path,authorization):
    value,manifest=check_binding(binding_path)
    authorization=Path(authorization)
    authorization_digest=validate_authorization(binding_path,value,manifest,authorization)
    directory=c.b.ROOT/value["output"]
    need(not directory.exists(),"TRANSFER_OUTPUT_EXISTS")
    claim(Path(str(authorization)+".used"),authorization_digest.encode("ascii"))
    directory.mkdir()
    def spawn(role):
        return bounded_process([sys.executable,"-m","tools._checkpoint_transfer_entry","worker",
            str(binding_path),str(directory),role],directory,role)
    try:
        common=c.common_values(manifest)
        claim(directory/"common.json",c.b.canonical(dict(values=common,sha256=c.b.digest(common))))
        external=list(value["qualification_references"])
        for path in (Path(binding_path),authorization,Path(str(authorization)+".used")):
            external.append(dict(path=path.resolve().relative_to(c.b.ROOT).as_posix(),
                bytes=path.stat().st_size,sha256=sha(path)))
        prereg=dict(inventory=value["inventory"],charged_sources=value["charged_sources"],external_evidence=external)
        claim(directory/"preregistration.json",c.b.canonical(prereg))
        claim(directory/"dispatch.json",c.b.canonical(dict(run_id=manifest.run_id,binding_sha256=sha(binding_path))))
        ledger=full_ledger(directory)
        need(not ledger["violations"],"TRANSFER_INITIAL_BUDGET",ledger)
        stages=launch_stages(value,directory,spawn)
        publish(directory/"processes.json",stages)
        proof=verify_total(directory,manifest,value["cut"])
        evaluate(directory,proof,manifest)
        ledger=full_ledger(directory)
        # The final file describes its own physical contribution without nesting itself.
        length=0
        for _ in range(16):
            result=dict(ledger,closure=dict(final_balance_bytes=length,gate=False))
            result["totals"]=dict(ledger["totals"])
            result["totals"]["metadata"]+=length
            result["totals"]["total"]+=length
            raw=c.b.canonical(result)
            if len(raw)==length:break
            length=len(raw)
        need(len(raw)==length,"TRANSFER_LEDGER_FIXED_POINT")
        publish(directory/"final-balance.json",result)
    except Exception as exc:
        try:
            failure=dict(status="NOT_EVALUABLE",failure=error_details(exc,"PROCESS_OR_CLOSURE"),gate=False,
                artifact_saved=False)
            if (directory/"preregistration.json").exists():publish(directory/"failure.json",failure)
            else:claim(directory/"setup-failure.json",c.b.canonical(failure))
        except Exception:
            # A publication failure is secondary; retain the original exception.
            traceback.print_exc()
        raise
    finally:c.MAIN_GATE=False


if __name__=="__main__":
    if sys.argv[1]=="worker":sys.exit(worker(*sys.argv[2:]))
    elif sys.argv[1]=="run":run(*sys.argv[2:])
    else:raise SystemExit("Unknown command; no gate opened")
