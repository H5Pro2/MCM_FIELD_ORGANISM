"""One independent read-only administrative audit; no functional replay."""
import ast
import hashlib
import re
from pathlib import Path
from tools import _s2oe_media_session as m

b,s,p=m.b,m.s,m.p


def need(ok,code):
    if not ok:
        raise ValueError(code)


def main():
    out=b.ROOT/"reports/s2oe"/m.QUAL_ID
    with (out/"verification.claim").open("xb") as stream:
        stream.write(b"ONCE")
    binding=s.read_json(out/"binding.json")
    b.check_root(binding,"binding_digest")
    need(binding["version"]=="s2oe.player-admission.v1" and binding["kind"]=="ADMINISTRATIVE_ONLY","ADMIN_VERSION")
    old=b.ROOT/binding["origin"]
    need(old==b.ROOT/"reports/s2oe/media-player-qualification-20260911-03","ORIGIN_INVALID")
    tree=[[f.relative_to(old).as_posix(),f.stat().st_size,s.sha(f.read_bytes())]
        for f in sorted(old.rglob("*")) if f.is_file()]
    need(len(tree)==binding["file_count"] and b.digest(tree)==binding["tree_sha256"],"EVIDENCE_CHANGED")
    result=s.read_json(old/"result.json");b.check_root(result,"result_digest")
    pre=s.read_json(old/"preregistration.json")
    need(result["status"]=="NOT_QUALIFIED" and result["exit_code"]==0 and result["hashes_unchanged"]
        and result["test_calls"]==1 and result["expected_tests"]==10
        and set(result["budget_violations"])=={"metadata","screenshots"},"HISTORICAL_RESULT_INVALID")
    for name,digest in result["files"].items():
        need(s.sha((old/name).read_bytes())==digest,"QUALIFICATION_FILE_CHANGED")
    names=sorted(n.name for n in ast.walk(ast.parse((b.ROOT/"tests/test_s2oe_player.py").read_text()))
        if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    log=(old/"stderr.txt").read_text()
    passed=sorted(re.findall(r"^(test_\w+) \([^\n]+\) \.\.\. ok$",log,re.M))
    need(names==pre["tests"]==passed and len(names)==10 and log.rstrip().endswith("OK"),"COVERAGE_INCOMPLETE")
    current=m.inventory()
    need(b.digest(current)==binding["current_sources_digest"],"CURRENT_SOURCE_CHANGED")
    added=["reports/prepare_media_admission.py","reports/verify_media_admission.py"]
    need(binding["added_sources"]==added and set(current)==set(result["sources"])|set(added),"SOURCE_SET_CHANGED")
    for name,expected in result["sources"].items():
        raw=(b.ROOT/name).read_bytes()
        if name=="tools/_s2oe_media_session.py":
            transition=binding["session_module_transition"]
            need(transition==dict(old_qualification=result["run_id"],new_qualification=m.QUAL_ID),"TRANSITION_INVALID")
            before=f'QUAL_ID = "{m.QUAL_ID}"'.encode()
            after=f'QUAL_ID = "{result["run_id"]}"'.encode()
            suffix=b',\n       "reports/prepare_media_admission.py", "reports/verify_media_admission.py")'
            need(raw.count(before)==1 and raw.count(suffix)==1,"ADMIN_DELTA_INVALID")
            raw=raw.replace(before,after).replace(suffix,b')')
        need([s.sha(raw),len(raw)]==expected,"FUNCTIONAL_SOURCE_CHANGED")
    for item in pre["environment"]["browser"]["files"]:
        path=Path(item["path"])
        with path.open("rb") as stream:
            digest=hashlib.file_digest(stream,"sha256").hexdigest()
        need(path.stat().st_size==item["size"] and digest==item["sha256"],"BROWSER_CHANGED")
    common=s.read_json(old/"native-player/common.json")
    physical=sum(row[1] for row in tree)
    sources=0
    for kind,name,size,digest in common["references"]:
        path=b.ROOT/name
        raw=path.read_bytes()
        if name!="tools/_s2oe_media_session.py":
            need(len(raw)==size and s.sha(raw)==digest,"TRANSITIVE_REFERENCE_CHANGED")
        if not path.is_relative_to(old):
            physical+=len(raw)
        if kind=="sources":
            sources+=len(raw)
    for name in added:
        physical+=(b.ROOT/name).stat().st_size
        sources+=(b.ROOT/name).stat().st_size
    record,session=s.unpack(s.read_json(old/"native-player/record.json"),s.read_json(old/"native-player/session.json"),common)
    native=p.ledger(record,session,common)["contributions"]
    native_bytes=sum(native["native"].values())+native["prefix_steps"]
    proof_bytes=sum(row[1] for row in tree if row[0].endswith(("verification.json","verification.claim")))
    images=sum(row[1] for row in tree if row[0] in ("desktop.jpg","mobile.jpg"))
    need(images==68891 and binding["reserves"]==dict(screenshots=98304,administrative_files_and_report=4608),"RESERVE_INVALID")
    reserve=98304-images+4608
    parts={k:native["native"].get(k,0) for k in ("nj","formations","generations")}
    totals=dict(metadata=physical-native_bytes-proof_bytes-sources+reserve,sources=sources,
        verification=proof_bytes,**parts,shared=sources+sum(parts.values()),total=physical+reserve)
    limits=dict(p.SESSION_LIMITS,metadata=147456)
    need(binding["limits"]==limits and binding["session_limits"]==p.SESSION_LIMITS
        and p.SESSION_LIMITS["metadata"]==98304,"SCOPE_INVALID")
    need(totals==binding["budget"]["totals"] and all(v<=limits[k] for k,v in totals.items()),"BUDGET_INVALID")
    need(not p.MAIN_GATE and binding["new_functional_test_calls"]==0,"EXECUTION_NOT_ALLOWED")
    admitted=b.sealed(dict(run_id=m.QUAL_ID,status="QUALIFIED",kind="ADMINISTRATIVE_ADMISSION",
        sources=current,binding_sha256=s.sha((out/"binding.json").read_bytes()),
        historical_result_digest=result["result_digest"],read_only=True,
        functional_test_calls=0,historical_passed_groups=10,verification_calls=1,
        totals=totals,gates=False),"result_digest")
    need(sum(f.stat().st_size for f in out.iterdir() if f.is_file())+len(b.canonical(admitted))+512<=4608,"ADMIN_ENVELOPE_INVALID")
    s.prior.save(out/"result.json",admitted)
    print(dict(status=admitted["status"],kind=admitted["kind"],totals=totals))


if __name__=="__main__":
    main()
