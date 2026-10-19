"""Independent stored-evidence check, no media or project imports."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/s2oe/decoder-uhd-sequence-20260911-01"


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    with (OUT/"verification.claim").open("xb") as stream:stream.write(b"once read-only\n")
    b=json.loads((OUT/"binding.json").read_text())
    r=json.loads((OUT/"record.json").read_text())
    assert r["binding_sha256"]==sha(OUT/"binding.json")
    assert r["qualification_sha256"]==sha(OUT/"qualification.json")
    q=json.loads((OUT/"qualification.json").read_text())
    assert q["status"]=="QUALIFIED" and q["tests"]==6 and q["log_sha256"]==sha(OUT/"qualification.log")
    for path,ref in b["code"].items():assert sha(ROOT/path)==ref["sha256"]
    common=ROOT/"reports/s2oe/media-player-run-binding-20260911-02/common.json"
    assert sha(common)==b["common_sha256"]
    old=json.loads(common.read_text())
    assert b["events"]==old["manifest"]["events"] and b["profile"]["source"]==old["manifest"]["source"]
    profile=dict(b["profile"])
    digest=profile.pop("profile_digest")
    assert hashlib.sha256(json.dumps(profile,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()==digest
    assert profile["run_id"]==b["run_id"]==r["run_id"]
    assert profile["config"]["process_commit_bytes"]==profile["config"]["job_commit_bytes"]==1073741824
    assert not r["gates_opened"] and r["system_calls"]==0
    for i,row in enumerate(r["events"]):
        e=b["events"][i]
        assert row["event"]==e
        center=Fraction(e["window_number"],2)+Fraction(1,20)
        assert Fraction(row["pts"],30000)<=center<Fraction(row["next_pts"],30000)
        assert row["video_time_base"]==[1,30000]
        assert row["audio_start_sample"]==e["window_number"]*24000 and row["audio_samples"]==4800
        assert row["output_bytes"]==[19200,6220800] and row["shapes"]==[[4800],[1080,1920,3]]
        assert row["formats"]==["float32","uint8"]
        assert all(len(row[k])==64 and all(c in "0123456789abcdef" for c in row[k]) for k in ("pcm_sha256","rgb_sha256"))
        assert row["job"]["process_commit_limit"]==row["job"]["job_commit_limit"]==1073741824
    res=r["resources"]
    assert res["worker_closed"] and res["private_profile_digest"]==digest
    assert res["private_run_id"]==r["run_id"] and not res["native_log_overflow"]
    if r["status"]=="DECODER_SEQUENCE_COMPLETE":
        assert len(r["events"])==24 and r["select_calls"]==24 and r["release_calls"]==20
        assert r["counters"]["selected_windows"]==20 and r["counters"]["passes"]==2
        assert res["read_counters_complete"]
    else:
        assert r["status"]=="NOT_EVALUABLE" and r["failure"]["code"]
    sizes={str(x.relative_to(ROOT)):x.stat().st_size for x in OUT.iterdir() if x.is_file()}
    total=sum(sizes.values())+sum(x["bytes"] for x in b["code"].values())+common.stat().st_size
    assert total+24576<=b["total_reserved"]
    result=dict(status="EVIDENCE_VALID",decoder_status=r["status"],read_only=True,
        record_sha256=sha(OUT/"record.json"),files=sizes,actual_before_verification=total,
        bound_total=b["total_reserved"],
        boundary="Stored prefix, timestamps, shape, digest and resource bindings; no decoder or numerical sample reconstruction.")
    with (OUT/"verification.json").open("x",encoding="utf-8") as stream:
        json.dump(result,stream,sort_keys=True,indent=2)


if __name__=="__main__":main()
