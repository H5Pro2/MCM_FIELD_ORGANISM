"""Prepare then invoke exactly one bounded neutral qualification."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/s2oe/immediate-visual-qualification-20260912-04"
PARENT="reports/s2oe/media-memory-video-20260912-01/record.json"
OWN=("tools/_s2oe_immediate_visual_input.py","tools/_s2oe_immediate_visual_control.py",
     "tests/test_s2oe_immediate_visual_input.py","reports/qualify_immediate_visual_once.py")
META=dict(preregistration=8192,log=65536,result=8192,balance=4096,run_binding=8192,report=4096)


def raw(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def publish(name,value):
    with (OUT/name).open("xb") as f:
        f.write(value if isinstance(value,bytes) else raw(value))


def inventory():
    pending=set(OWN); found={}
    while pending:
        path=pending.pop()
        if path in found: continue
        data=(ROOT/path).read_bytes();found[path]=[sha(data),len(data)]
        if not path.endswith(".py"): continue
        tree=ast.parse(data.decode("utf-8-sig"))
        package=path[:-3].replace("/",".").split(".")[:-1]
        names=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import): names.extend(a.name for a in node.names)
            if isinstance(node,ast.ImportFrom):
                prefix=".".join(package[:len(package)-node.level+1]) if node.level else ""
                base=".".join(x for x in (prefix,node.module) if x)
                names.extend([base,*[base+"."+a.name for a in node.names]])
            if isinstance(node,ast.Constant) and isinstance(node.value,str):
                value=node.value
                if (len(value)<240 and "\n" not in value and value.startswith(("tools/","reports/","tests/","docs/","mcm_field_organism/"))
                    and value.endswith((".py",".md")) and (ROOT/value).is_file()): pending.add(value)
        for name in names:
            if name.split(".")[0] not in ("tools","mcm_field_organism","reports","tests"): continue
            parts=name.split(".")
            for i in range(1,len(parts)+1):
                stem="/".join(parts[:i])
                for candidate in (stem+".py",stem+"/__init__.py"):
                    if (ROOT/candidate).is_file(): pending.add(candidate)
    return found


def prepare():
    OUT.mkdir(exist_ok=False)
    inv=inventory(); invraw=raw(inv)
    parent=(ROOT/PARENT).read_bytes()
    obj=json.loads(parent);ex=obj["record"]["execution"];event=ex["inputs"][2]["event"]
    binding=dict(version="s2oe.immediate-historical-input.v1",path=PARENT,byte_count=len(parent),
        sha256=sha(parent),event_digest=event["event_digest"],config_digest=ex["config_digest"],neutral=False)
    tree=ast.parse((ROOT/OWN[2]).read_text(encoding="utf-8"))
    tests=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    parts=dict(historical_input=len(parent),metadata=sum(META.values()),sources=len(invraw),
               verification=262144,supplement=4096,data=393216)
    totals=dict(total=sum(parts.values()),shared=parts["sources"]+parts["supplement"],
                metadata=parts["metadata"],sources=parts["sources"],verification=parts["verification"])
    limits=dict(total=4194304,shared=262144,metadata=131072,sources=174080,verification=262144)
    violations=[k for k in totals if totals[k]>limits[k]]
    if len(parent)>2097152: violations.append("historical_input")
    pr=dict(version="s2oe.immediate-qualification.v2",tests=tests,inventory_sha256=sha(invraw),
        budget_binding=dict(version="s2oe.immediate-qualification-metadata.v2",
            scope="qualification-directory-only",log_reserve=65536,metadata_limit=131072,
            real_session_metadata_limit=65536,historical_defaults_changed=False),
        parent_binding=binding,parts=parts,totals=totals,limits=limits,metadata_reserves=META,
        violations=violations,python=sys.version,executable=sys.executable,
        prepare_parent_read_bytes=len(parent),test_parent_read_bytes=0,
        neutral_limits=dict(administrative_fixtures=22,native_fixtures=1,synthetic_nj=1,formations=1,scans=4,
                            scan_value_comparisons=3200,real_receptor_calls=0))
    publish("inventory.json",invraw);publish("preregistration.json",pr)
    print(json.dumps(dict(totals=totals,violations=violations,tests=len(tests))))
    if violations or len(raw(pr))>META["preregistration"]:
        raise SystemExit("PRESTART_STOP")


def test_child():
    # Even accidental fixture reuse may not read real records or media.
    def audit(event,args):
        if event == "open" and isinstance(args[0],(str,bytes)):
            path=Path(args[0]).resolve()
            if path == (ROOT/PARENT).resolve() or path.suffix.lower() in (".mp4",".pcm",".rgb"):
                raise RuntimeError("REAL_INPUT_FORBIDDEN")
    sys.addaudithook(audit)
    sys.path.insert(0,str(ROOT))
    suite=unittest.defaultTestLoader.loadTestsFromName("tests.test_s2oe_immediate_visual_input")
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    bodies=sys.modules["tests.test_s2oe_immediate_visual_input"].InputTests.body_calls
    publish("test-result.json",dict(tests=result.testsRun,test_bodies_reached=bodies,
        errors=len(result.errors),failures=len(result.failures),
        success=result.wasSuccessful()))
    return 0 if result.wasSuccessful() else 1


def qualify():
    pr=json.loads((OUT/"preregistration.json").read_bytes())
    if pr["violations"] or sha(raw(inventory())) != pr["inventory_sha256"]:
        raise SystemExit("BINDING_CHANGED")
    publish("qualification.claim",b"once\n")
    with (OUT/"qualification.log").open("xb") as log:
        result=subprocess.run([sys.executable,str(Path(__file__).resolve()),"child"],cwd=ROOT,
                              stdout=log,stderr=subprocess.STDOUT,timeout=180)
    current=sha(raw(inventory()))
    files={f.name:dict(bytes=f.stat().st_size,sha256=sha(f.read_bytes())) for f in OUT.iterdir() if f.is_file()}
    test=json.loads((OUT/"test-result.json").read_bytes()) if (OUT/"test-result.json").exists() else {}
    good=(result.returncode==0 and test.get("tests")==len(pr["tests"]) and test.get("success")
          and current==pr["inventory_sha256"] and files["qualification.log"]["bytes"]<=META["log"])
    publish("result.json",dict(status="QUALIFIED" if good else "NOT_QUALIFIED",returncode=result.returncode,
        test=test,files=files,inventory_before=pr["inventory_sha256"],inventory_after=current,
        unittest_calls=1,real_run=False,gates=False))
    print(json.dumps(dict(status="QUALIFIED" if good else "NOT_QUALIFIED",test=test,files=files)))


if __name__ == "__main__":
    if sys.argv[1] == "prepare": prepare()
    elif sys.argv[1] == "qualify": qualify()
    elif sys.argv[1] == "child": raise SystemExit(test_child())
    else: raise SystemExit("UNKNOWN_MODE")
