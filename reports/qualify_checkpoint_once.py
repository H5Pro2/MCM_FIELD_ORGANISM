"""One prebound neutral invocation; no real seven-event execution."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from reports.prepare_checkpoint_budget import field_upper, record_upper

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"reports/memory-checkpoint-qualification-20260912-02"
OWN = ("tools/_memory_checkpoint.py", "tests/test_memory_checkpoint.py",
       "reports/prepare_checkpoint_budget.py", "reports/qualify_checkpoint_once.py",
       "tools/_memory_checkpoint_ledger.py")


def metadata_envelope(inv):
    """Only administrative configuration/templates; no fixture endpoints or runtime."""
    from dataclasses import fields
    os.environ["CHECKPOINT_QUAL_DIR"]=str(OUT)
    os.environ["CHECKPOINT_CODE_DIGEST"]=sha(raw(inv))
    from tests import test_memory_checkpoint as test
    c=test.c; b=c.b
    manifest=test.fixture_manifest()
    common=c.common_values(manifest)
    snapshot={f.name:"f"*64 for f in fields(c.r.ng.runtime.MinimalMCMRuntimeSnapshot336V1)}
    wrapper={k:"f"*64 for k in ("phase","field_component_digest","last_end_tick","step_count","state_digest")}
    def header(events,forms,scans,audio):
        native=dict(schema=b.SCHEMA,status="RECORDING_COMPLETE",run_id=manifest.run_id,
            config_digest="f"*64,runtime_config=common["runtime_config"],binding=common["binding"],
            initial=dict(snapshot=snapshot,field=wrapper,memory="f"*64),final=snapshot,
            inputs=[None]*events,source_receipts=[None]*audio+[
                dict(nj=None,rgb_digest="f"*64,source_digest="f"*64)]*(events-audio),
            rows=[None]*events,states={f"{i:064x}":None for i in range(forms+1)},
            scans=[None]*scans,failure=None,main_gate=False,record_digest="f"*64)
        # Null placeholders remain charged, making this larger than punctuation alone.
        return len(raw(c.references(native,common)))
    common_bytes=len(raw(dict(values=common,sha256=b.digest(common))))
    components=dict(common=common_bytes,arm_headers=2*header(4,2,4,3),
        prefix_header=header(1,1,0,1),temporary_prefix_header=header(1,1,0,1),
        checkpoint_and_temporary_outer=2*4096,worker_result_wrappers=4096,
        preregistration_without_inventory=4096,full_log_files=12288,
        result_report_and_ledger=12288,negative_fixture_and_claims=1024)
    return dict(parts=components,total=sum(components.values()),limit=65536,
        method="Concrete native header keys with 64-character scalar placeholders, exact shared configuration, full array/key punctuation; explicit remaining file caps.")


def raw(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def inventory():
    pending=set(OWN); found={}
    while pending:
        name=pending.pop()
        if name in found:
            continue
        data=(ROOT/name).read_bytes()
        found[name]=dict(bytes=len(data),sha256=sha(data))
        if not name.endswith(".py"):
            continue
        package=name[:-3].split("/")[:-1]
        for node in ast.walk(ast.parse(data.decode("utf-8-sig"))):
            modules=[]
            if isinstance(node,ast.Import):
                modules=[x.name for x in node.names]
            elif isinstance(node,ast.ImportFrom):
                prefix=".".join(package[:len(package)-node.level+1]) if node.level else ""
                base=".".join(x for x in (prefix,node.module) if x)
                modules=[base]+[base+"."+x.name for x in node.names if x.name!="*"]
            for module in modules:
                if module.split(".")[0] not in ("mcm_field_organism","tools","reports","tests"):
                    continue
                parts=module.split(".")
                for i in range(1,len(parts)+1):
                    stem="/".join(parts[:i])
                    for candidate in (stem+".py",stem+"/__init__.py"):
                        if (ROOT/candidate).is_file() and candidate not in found:
                            pending.add(candidate)
    return dict(files=dict(sorted(found.items())),python=sys.version,
                interpreter_sha256=sha(Path(sys.executable).read_bytes()))


def prepare():
    if OUT.exists():
        raise SystemExit("Qualification directory already exists; no overwrite or retry")
    inv=inventory()
    tree=ast.parse((ROOT/OWN[1]).read_text(encoding="utf-8"))
    tests=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    field=field_upper()
    arm=record_upper(4,2,4,3)["total"]
    prefix=record_upper(1,1,0,1)["total"]
    checkpoint=prefix+field["bytes"]+32768
    # Both completed arms plus both checkpoint names: conservative over reachable phases.
    parts=dict(arms=2*arm,checkpoint=checkpoint,temporary_checkpoint=checkpoint,
        verification=262144,source_attachment=len(raw(inv))+sum((ROOT/p).stat().st_size for p in OWN),
        metadata_and_full_logs=65536,closure=4096)
    total=sum(parts.values())
    metadata=metadata_envelope(inv)
    metadata_parts=metadata["parts"];metadata_total=metadata["total"]
    violations=[]
    if metadata_total>65536:violations.append("METADATA")
    if field["bytes"]>524288:violations.append("FIELD_CHECKPOINT")
    if parts["source_attachment"]>174080:violations.append("SOURCES")
    if parts["source_attachment"]+2*(3*1024+2*1536+2*1536)+1024+1536+1536>262144:
        violations.append("SHARED")
    if total>4194304:violations.append("TOTAL")
    value=dict(status="READY" if not violations else "PRECONDITION_STOP",test_calls=0,
        qualification_id=OUT.name,tests=tests,inventory=inv,code_digest=sha(raw(inv)),
        field_upper=field,parts=parts,total=total,total_limit=4194304,violations=violations,
        metadata_parts=metadata_parts,metadata_total=metadata_total,metadata_limit=65536,
        charged_sources=list(OWN),
        native_scope="Four neutral endpoint events; save after event one. Not the seven-event task.",
        identities="Same logical IDs/digests; separate exited processes. No consumed event owner restored.",
        excluded="Real payloads, seven-event task, live source, historical tests.")
    OUT.mkdir()
    (OUT/"preregistration.json").write_bytes(raw(value))
    print(json.dumps({k:v for k,v in value.items() if k!="inventory"},indent=2))


def qualify():
    value=json.loads((OUT/"preregistration.json").read_bytes())
    if value["status"]!="READY" or value["inventory"]!=inventory():
        raise SystemExit("Precondition not met; no test invocation")
    with (OUT/"invocation.claim").open("xb") as handle:
        handle.write(b"once")
    env=dict(os.environ,CHECKPOINT_QUAL_DIR=str(OUT),CHECKPOINT_CODE_DIGEST=value["code_digest"],
             OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1")
    with (OUT/"qualification.stdout").open("xb") as stdout, (OUT/"qualification.stderr").open("xb") as stderr:
        process=subprocess.run([sys.executable,"-m","unittest","tests.test_memory_checkpoint","-v"],
            cwd=ROOT,env=env,stdout=stdout,stderr=stderr,check=False)
    files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in OUT.iterdir() if p.is_file()}
    unchanged=inventory()==value["inventory"]
    from tools import _memory_checkpoint as c
    balance=c.artifact_ledger(OUT)
    result=dict(qualification_id=OUT.name,test_calls=1,exit_code=process.returncode,
        status="QUALIFIED" if process.returncode==0 and unchanged and not balance["violations"] else "NOT_QUALIFIED",
        hashes_unchanged=unchanged,files=files,
        gates=False,balance=balance["totals"],budget_violations=balance["violations"],
        note="No real seven-event admission. Complete logs retained even on failure.")
    (OUT/"result.json").write_bytes(raw(result))
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    {"prepare":prepare,"qualify":qualify}[sys.argv[1]]()
