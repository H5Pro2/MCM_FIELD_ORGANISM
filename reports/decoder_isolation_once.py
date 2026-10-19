"""Two prebound sequential decoder calls, exclusively diagnostic."""
import ctypes as ct
from dataclasses import make_dataclass
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
OUT = ROOT/"reports/s2oe/decoder-isolation-20260911-01"
COMMON = ROOT/"reports/s2oe/media-player-run-binding-20260911-02/common.json"
COMMON_SHA = "7d306c851a74eeccb00c6aca3b5397372c6d8e450f217cb12a457f08bae5e6d3"
FILES = ("tools/_s2oe_decoder_worker.py","tools/_s2oe_media_decoder.py",
    "tools/_s2oe_isolation_log.py","tests/s2oe_isolation_worker.py","tests/test_s2oe_isolation.py",
    "reports/decoder_isolation_once.py","reports/verify_decoder_isolation.py")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name,value):
    raw = (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n").encode()
    with (OUT/name).open("xb") as stream:
        stream.write(raw)


def inventory():
    return {p:dict(bytes=(ROOT/p).stat().st_size,sha256=sha(ROOT/p)) for p in FILES}


def host():
    class Performance(ct.Structure):
        _fields_ = [("cb",ct.c_ulong)] + [(n,ct.c_size_t) for n in
            ("CommitTotal","CommitLimit","CommitPeak","PhysicalTotal","PhysicalAvailable",
             "SystemCache","KernelTotal","KernelPaged","KernelNonpaged","PageSize")] + [
            (n,ct.c_ulong) for n in ("HandleCount","ProcessCount","ThreadCount")]
    value=Performance()
    value.cb=ct.sizeof(value)
    api=ct.WinDLL("psapi",use_last_error=True)
    api.GetPerformanceInfo.argtypes=[ct.POINTER(Performance),ct.c_ulong]
    api.GetPerformanceInfo.restype=ct.c_int
    if not api.GetPerformanceInfo(ct.byref(value),value.cb):
        raise OSError(ct.get_last_error())
    return dict(available_commit_bytes=(value.CommitLimit-value.CommitTotal)*value.PageSize,
        physical_available_bytes=value.PhysicalAvailable*value.PageSize,
        commit_limit_bytes=value.CommitLimit*value.PageSize)


def suitable(h):
    return h["available_commit_bytes"]>=3*1073741824 and h["physical_available_bytes"]>=2*1073741824


def checked():
    b=json.loads((OUT/"binding.json").read_text())
    assert b["code"]==inventory() and sha(COMMON)==COMMON_SHA
    return b


def prepare():
    OUT.mkdir(exist_ok=False)
    assert sha(COMMON)==COMMON_SHA
    h=host()
    code=inventory()
    ledger=dict(code_bytes=sum(v["bytes"] for v in code.values()),common_bytes=COMMON.stat().st_size,
        binding_reserve=8192,qualification_reserve=16384,arm_reserves=131072,
        verification_reserve=16384,report_reserve=8192)
    save("binding.json",dict(version="s2oe.decoder-isolation.v1",code=code,common_sha256=COMMON_SHA,
        source=json.loads(COMMON.read_text())["manifest"]["source"],host_before=h,
        host_required=dict(available_commit_bytes=3*1073741824,physical_available_bytes=2*1073741824),
        arms=[dict(name="COMMIT_512",process=536870912,job=536870912),
            dict(name="COMMIT_1024",process=1073741824,job=1073741824)],
        selection=dict(repeat=1,window=0),native_log_limit=dict(messages=32,bytes=32768),
        log_level="ERROR",deduplicate_logs=False,ledger=ledger,total_reserved=sum(ledger.values()),
        qualification_id="decoder-isolation-neutral-20260911-01",
        test_inventory=["default_and_forbidden_stage","two_native_job_bindings",
            "original_native_exception_and_message","abrupt_exit_preserves_native_log",
            "native_log_bound_is_explicit","job_message_kinds_remain_distinct"],
        limits_interpretation="Overlapping process/job bounds; workers sequential, not additive."))
    assert sum(ledger.values())<393216 and suitable(h),"PRESTART_BUDGET_STOP"


def qualify():
    checked()
    with (OUT/"qualification.claim").open("xb") as stream:
        stream.write(b"once\n")
    suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"),pattern="test_s2oe_isolation.py")
    log=io.StringIO()
    r=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    with (OUT/"qualification.log").open("x",encoding="utf-8") as stream:
        stream.write(log.getvalue())
    save("qualification.json",dict(status="QUALIFIED" if r.wasSuccessful() and r.testsRun==6
        else "NOT_QUALIFIED",tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),
        log_sha256=sha(OUT/"qualification.log")))
    assert r.wasSuccessful() and r.testsRun==6
    assert sum((OUT/n).stat().st_size for n in
        ("qualification.claim","qualification.log","qualification.json"))<=16384


def run():
    b=checked()
    assert json.loads((OUT/"qualification.json").read_text())["status"]=="QUALIFIED"
    with (OUT/"comparison.claim").open("xb") as stream:
        stream.write(b"two fixed arms, one call each\n")
    from tools import _s2oe_decoder_worker as w
    source=dict(b["source"])
    for k in ("video_time_base","audio_time_base","frame_rate","video_size"):
        source[k]=tuple(source[k])
    src=make_dataclass("Source",[(k,object) for k in source],frozen=True)(**source)
    for arm in b["arms"]:
        worker=None
        r=dict(arm=arm,binding_sha256=sha(OUT/"binding.json"),status="NOT_EVALUABLE",
            host_before=host(),decoder_calls=0,selection=b["selection"],gates_opened=False,
            system_calls=0)
        try:
            if not suitable(r["host_before"]):
                raise w.WorkerError("HOST_BUDGET_STOP")
            worker=w.WorkerDecoder(src,diagnostic_arm=arm["name"])
            r["decoder_calls"]=1
            pcm,rgb,pts,next_pts=worker.select(1,0)
            r.update(status="DECODER_WINDOW_COMPLETE",pts=pts,next_pts=next_pts,
                output_bytes=[pcm.nbytes,rgb.nbytes],
                output_sha256=[hashlib.sha256(memoryview(pcm)).hexdigest(),
                    hashlib.sha256(memoryview(rgb)).hexdigest()])
            del pcm,rgb
        except BaseException as exc:
            r["failure"]=dict(code=getattr(exc,"code",None),exception_type=type(exc).__name__)
        finally:
            if worker:
                try:
                    worker.close()
                except BaseException as exc:
                    r["close_error"]=type(exc).__name__
                r.update(resources=worker.resources,counters=worker.counters,
                    phase=worker.last_confirmed_phase)
            save(arm["name"]+".json",r)
        assert (OUT/(arm["name"]+".json")).stat().st_size<=65536
        if r.get("failure",{}).get("code")=="HOST_BUDGET_STOP" or "close_error" in r:
            break


if __name__=="__main__":
    {"prepare":prepare,"qualify":qualify,"run":run}[sys.argv[1]]()
