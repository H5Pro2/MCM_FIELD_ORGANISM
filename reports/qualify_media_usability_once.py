"""One neutral usability qualification and a separately blocked real binding."""
import io
import unittest
from tools import _s2oe_local_player as ui
from reports import qualify_uhd_admission_once as previous

m,p,b,s=ui.m,ui.p,ui.b,ui.s
OUT=b.ROOT/"reports/s2oe"/m.QUAL_ID
FINAL=b.ROOT/"reports/s2oe/media-player-run-binding-20260912-03"
RUN="media-memory-video-20260912-01"


def save(path,value):s.prior.save(path,value)


def common(refs):
    old=s.read_json(b.ROOT/"reports/s2oe/media-player-run-binding-20260912-01/common.json")
    src=p.Source(**{k:tuple(v) if isinstance(v,list) else v for k,v in old["manifest"]["source"].items()})
    basepath=b.ROOT/"reports/s2oc"/s.QUAL_ID
    base,_=s.qualified_common(b.decode_manifest(s.read_json(basepath/"caller-common.json")["manifest"]),basepath)
    return m.bind_common(p.build(RUN,src,b.digest(m.inventory())),base,refs)


def refs():
    rows=previous.references()
    for name in ("result.json","qualification.log"):
        rows.append(s.file_reference("metadata",b.ROOT/"reports/s2oe/media-uhd-admission-20260912-01"/name))
    return rows


def budget(value,extra=()):
    # Include the physical budget file itself in every progress/closure alternative.
    result=previous.balance(value,(("metadata","@budget-file-and-binding-check",16384),)+extra)
    result["run_id"]=RUN
    return result


def prepare():
    OUT.mkdir(exist_ok=False)
    save(OUT/"inventory.json",m.inventory())
    c=common(refs())
    save(OUT/"prepared-common.json",c)
    value=budget(c,(("metadata","@new-runtime-result-log",12288),))
    value["qualification_reserve"]=65536
    sources=sum(r[2] for r in c["references"] if r[0]=="sources")
    metadata=sum(r[2] for r in c["references"] if r[0]=="metadata")+65536
    value["qualification_totals"]=dict(sources=sources,shared=sources,metadata=metadata,total=sources+metadata)
    value["joint_total_upper"]=value["maxima"]["total"]+65536
    value["violations"] += ["QUAL_"+k.upper()+"_LIMIT" for k,v in value["qualification_totals"].items() if v>p.SESSION_LIMITS[k]]
    if value["joint_total_upper"]>4194304:value["violations"].append("JOINT_TOTAL_LIMIT")
    value["test_inventory"]=["user_stop","server_shutdown","source_end","technical_error",
        "unknown_is_not_user_stop","complete","dom_projection","invalid_stop_cause"]
    save(OUT/"preflight.json",value)
    assert not value["violations"],str(value["maxima"])


def qualify():
    assert m.inventory()==s.read_json(OUT/"inventory.json")
    assert not s.read_json(OUT/"preflight.json")["violations"]
    with (OUT/"qualification.claim").open("xb") as f:f.write(b"once\n")
    suite=unittest.defaultTestLoader.discover(str(b.ROOT/"tests"),pattern="test_s2oe_usability.py")
    log=io.StringIO()
    r=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    with (OUT/"qualification.log").open("x",encoding="utf-8") as f:f.write(log.getvalue())
    result=b.sealed(dict(status="QUALIFIED" if r.wasSuccessful() and r.testsRun==8 else "NOT_QUALIFIED",
        run_id=m.QUAL_ID,tests=r.testsRun,errors=len(r.errors),failures=len(r.failures),sources=m.inventory(),
        log_sha256=s.sha((OUT/"qualification.log").read_bytes()),gates=False,real_media_calls=0),"result_digest")
    save(OUT/"result.json",result)
    assert r.wasSuccessful() and r.testsRun==8
    assert sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())+8192<=65536


def finish():
    assert s.read_json(OUT/"result.json")["status"]=="QUALIFIED"
    output=b.ROOT/"reports/s2oe"/RUN
    assert not output.exists() and not output.with_suffix(".authorization-used").exists()
    FINAL.mkdir(exist_ok=False)
    c=common(refs()+[s.file_reference("metadata",OUT/n) for n in ("result.json","qualification.log","qualification.claim")])
    m.check_common(p.decode(c["manifest"]),c,s.inventory())
    value=budget(c)
    value["joint_total_upper"]=value["maxima"]["total"]+65536
    save(FINAL/"common.json",c)
    save(FINAL/"budget.json",value)
    assert not value["violations"] and value["joint_total_upper"]<=4194304
    settings=dict(version=ui.VERSION,status="BOUND_AWAITING_AUTHORIZATION",output=output.relative_to(b.ROOT).as_posix(),
        common=dict(path=(FINAL/"common.json").relative_to(b.ROOT).as_posix(),sha256=s.sha((FINAL/"common.json").read_bytes())),
        budget=dict(path=(FINAL/"budget.json").relative_to(b.ROOT).as_posix(),sha256=s.sha((FINAL/"budget.json").read_bytes())))
    save(FINAL/"settings.json",settings)
    ui.load_binding(FINAL/"settings.json",s.sha((FINAL/"settings.json").read_bytes()))
    save(FINAL/"authorization-template.json",dict(version=ui.VERSION,authorized=False,single_use=True,run_id=RUN,
        settings_sha256=s.sha((FINAL/"settings.json").read_bytes()),common_sha256=settings["common"]["sha256"],
        qualification_sha256=s.sha((OUT/"result.json").read_bytes())))


if __name__=="__main__":
    import sys
    {"prepare":prepare,"qualify":qualify,"finish":finish}[sys.argv[1]]()
