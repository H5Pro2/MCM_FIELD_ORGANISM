"""One independent read-only comparison check, no decoder/project imports."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/s2oe/decoder-isolation-20260911-01"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    with (OUT/"verification.claim").open("xb") as stream:
        stream.write(b"once read-only\n")
    b=json.loads((OUT/"binding.json").read_text())
    for path,ref in b["code"].items():
        assert sha(ROOT/path)==ref["sha256"] and (ROOT/path).stat().st_size==ref["bytes"]
    common=ROOT/"reports/s2oe/media-player-run-binding-20260911-02/common.json"
    assert sha(common)==b["common_sha256"]
    assert json.loads(common.read_text())["manifest"]["source"]==b["source"]
    q=json.loads((OUT/"qualification.json").read_text())
    assert q["status"]=="QUALIFIED" and q["tests"]==6
    assert q["log_sha256"]==sha(OUT/"qualification.log")
    records=[]
    for arm in b["arms"]:
        path=OUT/(arm["name"]+".json")
        r=json.loads(path.read_text())
        assert r["arm"]==arm and r["binding_sha256"]==sha(OUT/"binding.json")
        assert r["selection"]=={"repeat":1,"window":0} and r["decoder_calls"]==1
        assert not r["gates_opened"] and r["system_calls"]==0
        res=r["resources"]
        assert res["worker_closed"] and res["job_confirmed_before_media"]
        assert res["process_commit_limit"]==arm["process"] and res["job_commit_limit"]==arm["job"]
        assert res["diagnostic_arm"]==arm["name"] and res["active_process_limit"]==1
        assert not res["native_log_overflow"] and len(res["native_logs"])<=32
        assert r["host_before"]["available_commit_bytes"]>=b["host_required"]["available_commit_bytes"]
        assert r["host_before"]["physical_available_bytes"]>=b["host_required"]["physical_available_bytes"]
        if r["status"]=="DECODER_WINDOW_COMPLETE":
            assert r["counters"]["selected_windows"]==1
            assert r["pts"]*20<=30000<r["next_pts"]*20
            assert r["output_bytes"]==[19200,6220800]
        else:
            assert r["status"]=="NOT_EVALUABLE" and r["failure"]["code"]
        records.append(r)
    assert records[0]["resources"]["decoder_versions"]==records[1]["resources"]["decoder_versions"]
    sizes={str(p.relative_to(ROOT)):p.stat().st_size for p in OUT.iterdir() if p.is_file()}
    total=sum(sizes.values())+sum(x["bytes"] for x in b["code"].values())+common.stat().st_size
    assert total+24576<=b["total_reserved"]
    result=dict(status="EVIDENCE_VALID",read_only=True,record_sha256={a["name"]:sha(OUT/(a["name"]+".json")) for a in b["arms"]},
        comparison=dict(low=records[0]["status"],high=records[1]["status"]),
        files=sizes,actual_before_verification_bytes=total,bound_total_bytes=b["total_reserved"],
        boundary="Recorded bindings and control flow only; no media regeneration, native allocation reconstruction or numerical AV verification.")
    raw=(json.dumps(result,indent=2,sort_keys=True)+"\n").encode()
    assert len(raw)<=16384
    with (OUT/"verification.json").open("xb") as stream:
        stream.write(raw)


if __name__=="__main__":
    main()
