"""Private UHD admission qualification and static final binding; no media calls."""
import io
import json
from pathlib import Path
import unittest
from tools import _s2oe_media_session as m
from tools._s2oc_shared_verification import synthetic_forms

b,s,p=m.b,m.s,m.p
OUT=b.ROOT/"reports/s2oe"/m.QUAL_ID
FINAL=b.ROOT/"reports/s2oe/media-player-run-binding-20260912-01"
RUN="media-memory-video-20260911-02"
OLD=b.ROOT/"reports/s2oe/media-player-run-binding-20260911-02"


def save(path,value):s.prior.save(path,value)


def form(refs):
    anchor_path=b.ROOT/"reports/s2oc"/s.QUAL_ID
    anchor=s.read_json(anchor_path/"caller-common.json")
    base,_=s.qualified_common(b.decode_manifest(anchor["manifest"]),anchor_path)
    old=s.read_json(OLD/"common.json")
    source=p.Source(**{k:tuple(v) if type(v) is list else v for k,v in old["manifest"]["source"].items()})
    manifest=p.build(RUN,source,b.digest(m.inventory()))
    return m.bind_common(manifest,base,refs)


def references():
    old=s.read_json(OLD/"common.json")
    refs={r[1]:s.file_reference(r[0],b.ROOT/r[1]) for r in old["references"]}
    for name in m.OWN:refs[name]=s.file_reference("sources",b.ROOT/name)
    for name in m.uhd.ANCHORS:
        path=b.ROOT/m.uhd.CHECK/name
        refs[path.relative_to(b.ROOT).as_posix()]=s.file_reference("metadata",path)
    refs[(OUT/"inventory.json").relative_to(b.ROOT).as_posix()]=s.file_reference("sources",OUT/"inventory.json")
    return list(refs.values())


def balance(common,extra=()):
    rows=[]
    reserves=(("metadata","@evaluation",3000),("metadata","@dispatch",768),
        ("metadata","@final-balance",1536),("metadata","@common-reference",512),
        ("metadata","@original-common",len(b.canonical(common))),("metadata","@player-close",1024),
        ("metadata","@authorization-used",512),("metadata","@settings",1024),
        ("metadata","@authorization-files",1024),("metadata","@start-guide",3072)) + extra
    for n in range(25):
        for label,pair in zip(("success","failure"),synthetic_forms(common,n),strict=True):
            ledger=p.ledger(*pair,common,attachments=reserves)
            rows.append(dict(completed=n,alternative=label,totals=ledger["totals"],violations=ledger["violations"]))
    return dict(version="s2oe.uhd-run-budget.v1",run_id=RUN,limits=p.SESSION_LIMITS,positions=rows,
        maxima={k:max(r["totals"][k] for r in rows) for k in p.SESSION_LIMITS},
        violations=sorted({v for row in rows for v in row["violations"]}),reserves=list(reserves),gates=False)


def prepare():
    OUT.mkdir(exist_ok=False)
    save(OUT/"inventory.json",m.inventory())
    common=form(references())
    save(OUT/"prepared-common.json",common)
    # Entire qualification body, test output, attestations and report are counted prospectively.
    reserve=49152
    # Qualification files are a separate finite scope. Only runtime-required
    # result/log/claim enter the session; the complete qualification remains
    # charged in the shared overall balance, without double-counting references.
    value=balance(common,(("metadata","@runtime-qualification-result-log",8192),))
    value["qualification_reserve"]=reserve
    sources=sum(r[2] for r in common["references"] if r[0]=="sources")
    metadata=sum(r[2] for r in common["references"] if r[0]=="metadata")+reserve
    value["qualification_totals"]=dict(sources=sources,metadata=metadata,shared=sources,total=sources+metadata)
    value["joint_total_upper"]=value["maxima"]["total"]+reserve
    value["violations"] += ["QUAL_"+k.upper()+"_LIMIT" for k,v in value["qualification_totals"].items()
        if v>p.SESSION_LIMITS[k]]
    if value["joint_total_upper"]>p.SESSION_LIMITS["total"]:value["violations"].append("JOINT_TOTAL_LIMIT")
    value["qualification_files_in_scope"]=["prepared-common.json","inventory.json","preflight.json",
        "qualification.claim","qualification.log","result.json","BEFUND.md"]
    save(OUT/"preflight.json",value)
    if value["violations"]:raise RuntimeError("PREQUALIFICATION_BUDGET_STOP: "+str(value["maxima"]))


def qualify():
    assert m.inventory()==s.read_json(OUT/"inventory.json")
    assert not s.read_json(OUT/"preflight.json")["violations"]
    with (OUT/"qualification.claim").open("xb") as f:f.write(b"once\n")
    suite=unittest.defaultTestLoader.discover(str(b.ROOT/"tests"),pattern="test_s2oe_uhd_admission.py")
    log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    with (OUT/"qualification.log").open("x",encoding="utf-8") as f:f.write(log.getvalue())
    value=b.sealed(dict(status="QUALIFIED" if result.wasSuccessful() and result.testsRun==6 else "NOT_QUALIFIED",
        run_id=m.QUAL_ID,sources=m.inventory(),tests=result.testsRun,errors=len(result.errors),failures=len(result.failures),
        log_sha256=s.sha((OUT/"qualification.log").read_bytes()),decoder_calls=0,runtime_calls=0,gates=False),"result_digest")
    save(OUT/"result.json",value)
    assert result.wasSuccessful() and result.testsRun==6


def finish():
    assert s.read_json(OUT/"result.json")["status"]=="QUALIFIED"
    target=b.ROOT/"reports/s2oe"/RUN
    assert not target.exists() and not target.with_suffix(".authorization-used").exists()
    FINAL.mkdir(exist_ok=False)
    refs=references()+[s.file_reference("metadata",OUT/"result.json"),
        s.file_reference("metadata",OUT/"qualification.log"),s.file_reference("metadata",OUT/"qualification.claim")]
    common=form(refs)
    m.check_common(p.decode(common["manifest"]),common,s.inventory())
    budget=balance(common)
    save(FINAL/"common.json",common)
    save(FINAL/"budget.json",budget)
    if budget["violations"]:raise RuntimeError("FINAL_BUDGET_STOP")
    settings=dict(version="s2oe.local-player.v1",status="BOUND_AWAITING_AUTHORIZATION",
        common=dict(path=(FINAL/"common.json").relative_to(b.ROOT).as_posix(),sha256=s.sha((FINAL/"common.json").read_bytes())),
        budget=dict(path=(FINAL/"budget.json").relative_to(b.ROOT).as_posix(),sha256=s.sha((FINAL/"budget.json").read_bytes())),
        output=target.relative_to(b.ROOT).as_posix())
    save(FINAL/"settings.json",settings)
    from tools._s2oe_local_player import load_binding
    load_binding(FINAL/"settings.json",s.sha((FINAL/"settings.json").read_bytes()))
    save(FINAL/"authorization-template.json",dict(version="s2oe.local-player.v1",authorized=False,single_use=True,
        run_id=RUN,settings_sha256=s.sha((FINAL/"settings.json").read_bytes()),
        common_sha256=settings["common"]["sha256"],qualification_sha256=s.sha((OUT/"result.json").read_bytes())))


if __name__=="__main__":
    import sys
    {"prepare":prepare,"qualify":qualify,"finish":finish}[sys.argv[1]]()
