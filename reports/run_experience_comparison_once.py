"""File-bound preparation/one neutral qualification. Real execution not authorized."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"reports/experience-comparison-qualification-20260919-01"
OWN = ("tools/_experience_comparison.py","tools/_experience_verification.py",
       "tests/test_experience_comparison.py","reports/run_experience_comparison_once.py",
       "tools/_experience_entry.py")
LIMITS = dict(total=25165824,metadata=3145728,sources=524288,shared=786432,verification=262144)


def raw(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path,value):
    with path.open("xb") as f:
        f.write(raw(value))


def inventory():
    pending,found=set(OWN),{}
    while pending:
        name=pending.pop()
        if name in found:
            continue
        data=(ROOT/name).read_bytes()
        found[name]=dict(sha256=sha(data),bytes=len(data))
        if not name.endswith(".py"):
            continue
        tree=ast.parse(data.decode("utf-8-sig"))
        package=name[:-3].replace("/",".").split(".")[:-1]
        for node in ast.walk(tree):
            names=[]
            if isinstance(node,ast.Import):
                names=[x.name for x in node.names]
            elif isinstance(node,ast.ImportFrom):
                prefix=".".join(package[:len(package)-node.level+1]) if node.level else ""
                base=".".join(x for x in (prefix,node.module) if x)
                names=[base]+[base+"."+x.name for x in node.names if x.name!="*"]
            for module in names:
                if module.split(".")[0] not in ("tools","reports","tests","mcm_field_organism"):
                    continue
                parts=module.split(".")
                for n in range(1,len(parts)+1):
                    stem="/".join(parts[:n])
                    for candidate in (stem+".py",stem+"/__init__.py"):
                        if (ROOT/candidate).is_file() and candidate not in found:
                            pending.add(candidate)
    return dict(sorted(found.items()))


def reservations(inv):
    # One joint prospective peak: retained qualification + real result + one
    # temporary publication copy. Historical software is hash-bound in the
    # existing inventory convention, not copied into the evidence directory.
    parts=[dict(path="active-code-inventory",kind="sources",bytes=len(raw(inv))),
           *[dict(path=name,kind="sources",bytes=inv[name]["bytes"]) for name in OWN],
           dict(path="all-metadata-including-full-logs",kind="metadata",bytes=1048576),
           dict(path="joint-verification",kind="verification",bytes=262144)]
    for prefix in ("qualification", "real", "temporary"):
        parts.extend([dict(path=prefix+"-native",kind="native",bytes=6291456),
            dict(path=prefix+"-nj",kind="nj",bytes=32*1024),
            dict(path=prefix+"-formations",kind="formations",bytes=30*1536),
            dict(path=prefix+"-generations",kind="generations",bytes=30*1536)])
    totals=dict.fromkeys(LIMITS,0)
    for x in parts:
        totals["total"]+=x["bytes"]
        if x["kind"] in totals:
            totals[x["kind"]]+=x["bytes"]
        if x["kind"] in ("sources","nj","formations","generations"):
            totals["shared"]+=x["bytes"]
    return dict(profile="EXPERIENCE_COMPARISON_24M_V1",contributions=parts,totals=totals,limits=LIMITS,
                violations=[k for k in LIMITS if totals[k]>LIMITS[k]],
                alternatives="success or failure within each envelope; no duplicated success+failure reservation",
                limits_boundary="Evidence only; no memory, decoder, RAM or per-item increase")


def prepare():
    if OUT.exists():
        raise RuntimeError("QUALIFICATION_DIRECTORY_USED")
    inv=inventory()
    tree=ast.parse((ROOT/OWN[2]).read_text(encoding="utf-8"))
    tests=[node.name for node in ast.walk(tree) if isinstance(node,ast.FunctionDef) and node.name.startswith("test_")]
    balance=reservations(inv)
    OUT.mkdir()
    save(OUT/"inventory.json",inv)
    save(OUT/"preflight.json",balance)
    save(OUT/"preregistration.json",dict(version="experience-qualification.v1",tests=tests,
        test_calls=1,real_payloads=False,inventory_sha256=sha(raw(inv)),preflight_sha256=sha(raw(balance)),
        native_case="24+14 events, independent native null states; synthetic receptor values, no media decoding",
        work=dict(formations=30,contacts=11424,scans=16,verification_separate=True),
        additional_neutral_work="one formation in failure case; two null-state lifecycle instances",
        full_logs_reserve=262144,all_metadata_reserve=1048576))
    print(json.dumps(balance,indent=2))
    if balance["violations"]:
        raise RuntimeError("PREFLIGHT_LIMIT_NO_TEST_STARTED")


def qualify(expected):
    pr_bytes=(OUT/"preregistration.json").read_bytes()
    if sha(pr_bytes)!=expected:
        raise RuntimeError("PREREGISTRATION_CHANGED")
    pr=json.loads(pr_bytes)
    inv=inventory()
    if inv!=json.loads((OUT/"inventory.json").read_bytes()) or reservations(inv)["violations"]:
        raise RuntimeError("CURRENT_BINDING_INVALID")
    save(OUT/"qualification.claim",dict(preregistration_sha256=expected))
    env=dict(os.environ,EXPERIENCE_QUAL_OUT=str(OUT),PYTHONPATH=str(ROOT))
    # One test process; all logs retained even if the reserved envelope fails.
    with (OUT/"stdout.txt").open("xb") as stdout,(OUT/"stderr.txt").open("xb") as stderr:
        result=subprocess.run([sys.executable,str(Path(__file__).resolve()),"test-body"],cwd=ROOT,env=env,stdout=stdout,stderr=stderr)
    metrics=json.loads((OUT/"metrics.json").read_bytes()) if (OUT/"metrics.json").exists() else None
    unchanged=inv==inventory()
    files={x.name:dict(bytes=x.stat().st_size,sha256=sha(x.read_bytes())) for x in OUT.iterdir() if x.is_file()}
    actual=sum(x["bytes"] for x in files.values())
    logs=sum(files[n]["bytes"] for n in ("stdout.txt","stderr.txt"))
    metadata=sum(x["bytes"] for name,x in files.items() if name not in ("inventory.json","native-record.json","native-verification.json"))
    native=files.get("native-record.json",{}).get("bytes",0)
    proof=files.get("native-verification.json",{}).get("bytes",0)
    actual_fit=metadata+65536<=1048576 and native<=6291456 and proof<=131072
    good=result.returncode==0 and metrics is not None and metrics["tests_run"]==len(pr["tests"]) and unchanged and logs<=pr["full_logs_reserve"] and actual_fit
    save(OUT/"result.json",dict(status="QUALIFIED" if good else "NOT_QUALIFIED",test_calls=1,
        metrics=metrics,exit_code=result.returncode,hashes_unchanged=unchanged,files=files,
        physical_qualification_bytes=actual,full_log_bytes=logs,main_gate=False,
        actual_envelope=dict(metadata=metadata,record=native,verification=proof,closure_reserve=65536,within_reserves=actual_fit),
        boundary="Synthetic endpoints, not real media or a receptor/decoder requalification."))
    print(json.dumps(json.loads((OUT/"result.json").read_bytes()),indent=2))


def test_body():
    sys.path.insert(0,str(ROOT))
    import unittest
    import importlib.util
    spec=importlib.util.spec_from_file_location("experience_tests",ROOT/OWN[2])
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite=unittest.defaultTestLoader.loadTestsFromModule(module)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    save(OUT/"metrics.json",dict(tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                                skipped=len(result.skipped)))
    raise SystemExit(0 if result.wasSuccessful() else 1)


def final_binding():
    sys.path.insert(0,str(ROOT))
    from tools import _experience_comparison as c
    q=json.loads((OUT/"result.json").read_bytes())
    inv=inventory()
    if q["status"]!="QUALIFIED" or inv!=json.loads((OUT/"inventory.json").read_bytes()):
        raise RuntimeError("QUALIFICATION_NOT_VALID")
    target=ROOT/"reports/experience-comparison-real-20260919-01"
    if target.exists():
        raise RuntimeError("REAL_OUTPUT_EXISTS")
    source=c.p.Source("C:/Users/TV/Downloads/17138816-uhd_3840_2160_30fps.mp4",
        "df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa",83498438)
    manifest=c.p.build("experience-comparison-real-20260919-01",source,c.b.digest(inv))
    binding=c.b.sealed(dict(version=c.VERSION,profile=c.PROFILE,authorized=False,output=str(target.resolve()),
        manifest=c.asdict(manifest),code_digest=c.b.digest(inv),qualification_digest=c.b.digest(q),
        qualification_directory=OUT.relative_to(ROOT).as_posix(),reservations=reservations(inv)["contributions"],
        decoder_binding=dict(decoder_resource_profile=c.media.uhd.resources(),
            decoder_profile=json.loads(c.media.uhd.profile.bind(source,manifest.run_id))),
        time_boundary="Fresh local ordinal 1 uses global time position 11, field interval [0,2100000000]; contacts unchanged; no artificial memory aging.",
        provenance="Target-only update history at fixed window 2 or 8; mixed origin reported, not a correct-target claim."),"binding_digest")
    folder=ROOT/"reports/experience-comparison-real-20260919-01-binding"
    folder.mkdir()
    save(folder/"binding.json",binding)
    save(folder/"budget.json",reservations(inv))
    print(sha(raw(binding)))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("prepare","qualify","test-body","bind"))
    parser.add_argument("--preregistration-sha256")
    args=parser.parse_args()
    if args.action=="prepare":prepare()
    elif args.action=="qualify":qualify(args.preregistration_sha256)
    elif args.action=="test-body":test_body()
    else:final_binding()
