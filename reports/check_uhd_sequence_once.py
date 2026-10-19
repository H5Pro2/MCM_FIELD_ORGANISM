"""File-bound complete decoder sequence; no receptors, runtime or memory."""
from dataclasses import make_dataclass
import io
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from reports.decoder_isolation_once import host,suitable,sha
from tools import _s2oe_uhd_profile as p

RUN="decoder-uhd-sequence-20260911-01"
OUT=ROOT/"reports/s2oe"/RUN
COMMON=ROOT/"reports/s2oe/media-player-run-binding-20260911-02/common.json"
COMMON_SHA="7d306c851a74eeccb00c6aca3b5397372c6d8e450f217cb12a457f08bae5e6d3"
FILES=(*p.OWN,"reports/decoder_isolation_once.py","reports/check_uhd_sequence_once.py",
    "reports/verify_uhd_sequence.py","tests/test_s2oe_uhd_profile.py")


def save(name,value):
    with (OUT/name).open("xb") as stream:
        stream.write((json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n").encode())


def source(data):
    d=dict(data)
    for k in ("video_time_base","audio_time_base","frame_rate","video_size"):
        d[k]=tuple(d[k])
    return make_dataclass("Source",[(k,object) for k in d],frozen=True)(**d)


def inventory():
    return {f:dict(bytes=(ROOT/f).stat().st_size,sha256=sha(ROOT/f)) for f in FILES}


def checked():
    b=json.loads((OUT/"binding.json").read_text())
    assert b["code"]==inventory() and sha(COMMON)==COMMON_SHA
    return b


def prepare():
    OUT.mkdir(exist_ok=False)
    assert sha(COMMON)==COMMON_SHA
    old=json.loads(COMMON.read_text())
    h=host()
    code=inventory()
    ledger=dict(code_bytes=sum(x["bytes"] for x in code.values()),
        common_bytes=COMMON.stat().st_size,binding_reserve=16384,qualification_reserve=16384,
        record_reserve=131072,verification_reserve=16384,report_reserve=8192)
    profile=p.bind(source(old["manifest"]["source"]),RUN)
    save("binding.json",dict(version=p.VERSION,run_id=RUN,code=code,
        common_sha256=COMMON_SHA,profile=json.loads(profile),events=old["manifest"]["events"],
        qualification_id="uhd-profile-neutral-20260911-01",test_groups=6,host_before=h,
        tests=["immutable_profile_and_default","false_process_and_job_limits_independently",
            "other_configuration_rejected","source_and_run_separation","code_and_integrity",
            "factory_and_active_limit_failure"],ledger=ledger,total_reserved=sum(ledger.values()),
        expected=dict(events=24,selected_windows=20,passes=2,select_calls=24,release_calls=20),
        no_system_processing=True))
    assert (OUT/"binding.json").stat().st_size<=16384
    assert suitable(h) and sum(ledger.values())<393216,"PRESTART_BUDGET_STOP"


def qualify():
    checked()
    with (OUT/"qualification.claim").open("xb") as stream:stream.write(b"once\n")
    suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"),pattern="test_s2oe_uhd_profile.py")
    log=io.StringIO()
    r=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    with (OUT/"qualification.log").open("x",encoding="utf-8") as stream:stream.write(log.getvalue())
    save("qualification.json",dict(status="QUALIFIED" if r.wasSuccessful() and r.testsRun==6
        else "NOT_QUALIFIED",tests=r.testsRun,errors=len(r.errors),failures=len(r.failures),
        log_sha256=sha(OUT/"qualification.log")))
    assert r.wasSuccessful() and r.testsRun==6
    assert sum((OUT/n).stat().st_size for n in ("qualification.claim","qualification.log","qualification.json"))<=16384


def endpoint(decoder,event):
    import numpy as np
    from fractions import Fraction
    pcm,rgb,pts,next_pts=decoder.select(event["pass_number"],event["window_number"])
    try:
        p.worker.require(pcm.dtype==np.dtype("<f4") and pcm.shape==(4800,)
            and np.isfinite(pcm).all() and np.max(np.abs(pcm))<=1,"PCM_INVALID")
        p.worker.require(rgb.dtype==np.uint8 and rgb.shape==(1080,1920,3),"RGB_INVALID")
        p.worker.require(not pcm.flags.writeable and not rgb.flags.writeable,"OUTPUT_MUTABLE")
        center=Fraction(event["window_number"],2)+Fraction(1,20)
        p.worker.require(Fraction(pts,30000)<=center<Fraction(next_pts,30000),"FRAME_SELECTION_INVALID")
        return dict(event=event,pts=pts,next_pts=next_pts,video_time_base=[1,30000],
            audio_start_sample=event["window_number"]*24000,audio_samples=4800,
            pcm_sha256=p.sha(memoryview(pcm)),rgb_sha256=p.sha(memoryview(rgb)),
            output_bytes=[pcm.nbytes,rgb.nbytes],formats=[str(pcm.dtype),str(rgb.dtype)],
            shapes=[list(pcm.shape),list(rgb.shape)],
            counters=dict(decoder.counters),job=decoder.job.snapshot())
    finally:
        del pcm,rgb


def run():
    b=checked()
    assert json.loads((OUT/"qualification.json").read_text())["status"]=="QUALIFIED"
    with (OUT/"decoder.claim").open("xb") as stream:stream.write(b"one complete bound sequence\n")
    decoder=None
    r=dict(status="NOT_EVALUABLE",run_id=RUN,binding_sha256=sha(OUT/"binding.json"),
        qualification_sha256=sha(OUT/"qualification.json"),events=[],select_calls=0,release_calls=0,
        host_before=host(),gates_opened=False,system_calls=0)
    try:
        p.worker.require(suitable(r["host_before"]),"HOST_BUDGET_STOP")
        decoder=p.open_decoder(source(b["profile"]["source"]),p.canonical(b["profile"]),RUN)
        for event in b["events"]:
            r["current_event"]=event
            r["select_calls"]+=1
            r["events"].append(endpoint(decoder,event))
            if event["kind"]=="COMPLETE_AV_PERCEPTION":
                decoder.release()
                r["release_calls"]+=1
            p.worker.require(len(p.canonical(r))<=110000,"DECODER_RECORD_PROGRESS_LIMIT")
        p.worker.require(decoder.counters["selected_windows"]==20 and decoder.counters["passes"]==2
            and r["release_calls"]==20,"SEQUENCE_INCOMPLETE")
        r["status"]="DECODER_SEQUENCE_COMPLETE"
    except BaseException as exc:
        r["failure"]=dict(code=getattr(exc,"code",None),exception_type=type(exc).__name__)
    finally:
        if decoder:
            try:decoder.close()
            except BaseException as exc:r["close_error"]=type(exc).__name__
            r.update(resources=decoder.resources,counters=decoder.counters,phase=decoder.last_confirmed_phase)
        save("record.json",r)
    assert (OUT/"record.json").stat().st_size<=131072


if __name__=="__main__":
    {"prepare":prepare,"qualify":qualify,"run":run}[sys.argv[1]]()
