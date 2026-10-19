"""Single focused verification qualification, with no real control call."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/s2oe/immediate-closure-qualification-20260912-01"
TEST="tests/test_s2oe_immediate_closure.py"
OWN=(TEST,"tools/_s2oe_immediate_visual_verification.py","reports/run_immediate_visual_once.py",
     "reports/qualify_immediate_verification_once.py")


def raw(x): return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha(x): return hashlib.sha256(x).hexdigest()
def write(name,x):
    with (OUT/name).open("xb") as f: f.write(x if isinstance(x,bytes) else raw(x))


def inventory():
    pending=set(OWN);found={}
    while pending:
        path=pending.pop()
        if path in found: continue
        data=(ROOT/path).read_bytes();found[path]=[sha(data),len(data)]
        if not path.endswith(".py"): continue
        package=path[:-3].replace("/",".").split(".")[:-1]
        names=[]
        for n in ast.walk(ast.parse(data.decode("utf-8-sig"))):
            if isinstance(n,ast.Import): names.extend(a.name for a in n.names)
            if isinstance(n,ast.ImportFrom):
                prefix=".".join(package[:len(package)-n.level+1]) if n.level else ""
                base=".".join(x for x in (prefix,n.module) if x)
                names.extend([base,*[base+"."+a.name for a in n.names]])
            if isinstance(n,ast.Constant) and isinstance(n.value,str):
                s=n.value
                if len(s)<240 and "\n" not in s and s.startswith(("tools/","reports/","tests/","docs/","mcm_field_organism/")) and s.endswith((".py",".md")) and (ROOT/s).is_file(): pending.add(s)
        for name in names:
            if name.split(".")[0] not in ("tools","reports","tests","mcm_field_organism"): continue
            parts=name.split(".")
            for i in range(1,len(parts)+1):
                for candidate in ("/".join(parts[:i])+".py","/".join(parts[:i])+"/__init__.py"):
                    if (ROOT/candidate).is_file(): pending.add(candidate)
    return found


def prepare():
    OUT.mkdir(exist_ok=False)
    inv=inventory();tests=sorted(n.name for n in ast.walk(ast.parse((ROOT/TEST).read_text()))
        if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    parts=dict(historical_input=1359778,metadata=98304,sources=len(raw(inv)),verification=262144,
               supplement=4096,neutral_data=393216)
    limits=dict(metadata=131072,sources=174080,shared=262144,total=4194304)
    totals=dict(metadata=parts["metadata"],sources=parts["sources"],shared=parts["sources"]+4096,total=sum(parts.values()))
    violations=[k for k in limits if totals[k]>limits[k]]
    write("inventory.json",inv)
    write("preregistration.json",dict(tests=tests,inventory_sha256=sha(raw(inv)),parts=parts,limits=limits,totals=totals,
        violations=violations,log_limit=65536,verifier_calls_max=1,formations=2,public_scans=8,
        private_verification_scan_comparisons_max=3200,python=sys.version,real_gate=False))
    print(json.dumps(dict(tests=len(tests),totals=totals,violations=violations)))
    if violations: raise SystemExit("PRESTART_STOP")


def child():
    def audit(event,args):
        if event=="open" and isinstance(args[0],(str,bytes)):
            path=Path(args[0]).resolve()
            if path==(ROOT/"reports/s2oe/media-memory-video-20260912-01/record.json").resolve() or path.suffix.lower() in (".mp4",".pcm",".rgb"):
                raise RuntimeError("REAL_INPUT_FORBIDDEN")
    sys.addaudithook(audit);sys.path.insert(0,str(ROOT));os.environ["IMMEDIATE_QUAL_DIR"]=str(OUT)
    suite=unittest.defaultTestLoader.loadTestsFromName("tests.test_s2oe_immediate_closure")
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    write("test-result.json",dict(tests=result.testsRun,errors=len(result.errors),failures=len(result.failures),success=result.wasSuccessful()))
    return 0 if result.wasSuccessful() else 1


def qualify():
    pr=json.loads((OUT/"preregistration.json").read_bytes())
    if pr["violations"] or sha(raw(inventory()))!=pr["inventory_sha256"]: raise SystemExit("BINDING_CHANGED")
    write("qualification.claim",b"once\n")
    with (OUT/"qualification.log").open("xb") as log:
        result=subprocess.run([sys.executable,__file__,"child"],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    files={f.name:dict(bytes=f.stat().st_size,sha256=sha(f.read_bytes())) for f in OUT.iterdir() if f.is_file()}
    after=sha(raw(inventory()))
    test=json.loads((OUT/"test-result.json").read_bytes())
    good=result.returncode==0 and test["tests"]==4 and files["qualification.log"]["bytes"]<=65536 and after==pr["inventory_sha256"]
    status="QUALIFIED" if good else "NOT_QUALIFIED"
    write("result.json",dict(status=status,test=test,files=files,inventory_before=pr["inventory_sha256"],inventory_after=after,unittest_calls=1,gates=False))
    print(json.dumps(dict(status=status,test=test,files=files)))


if __name__=="__main__":
    if sys.argv[1]=="prepare": prepare()
    elif sys.argv[1]=="qualify": qualify()
    elif sys.argv[1]=="child": raise SystemExit(child())
    else: raise SystemExit("UNKNOWN_MODE")
