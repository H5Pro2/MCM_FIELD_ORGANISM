"""Prepare an explicitly blocked next-run binding; never opens media or runtime."""
from dataclasses import make_dataclass
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools import _s2oe_uhd_profile as p

RUN="media-memory-video-20260911-02"
OUT=ROOT/"reports/s2oe/media-player-run-binding-20260911-03"
CHECK=ROOT/"reports/s2oe/decoder-uhd-sequence-20260911-01"


def main():
    target=ROOT/"reports/s2oe"/RUN
    assert not target.exists() and not target.with_suffix(".authorization-used").exists()
    OUT.mkdir(exist_ok=False)
    old=json.loads((ROOT/"reports/s2oe/media-player-run-binding-20260911-02/common.json").read_text())
    check=json.loads((CHECK/"binding.json").read_text())
    proof=json.loads((CHECK/"verification.json").read_text())
    assert proof["status"]=="EVIDENCE_VALID" and proof["decoder_status"]=="DECODER_SEQUENCE_COMPLETE"
    d=dict(old["manifest"]["source"])
    for k in ("video_time_base","audio_time_base","frame_rate","video_size"):
        d[k]=tuple(d[k])
    source=make_dataclass("Source",[(k,object) for k in d],frozen=True)(**d)
    rows={ref[1]:dict(kind=ref[0],bytes=(ROOT/ref[1]).stat().st_size,
        sha256=p.sha((ROOT/ref[1]).read_bytes())) for ref in old["references"]}
    old_source_bytes=sum(v["bytes"] for v in rows.values() if v["kind"]=="sources")
    for name in (*check["code"],"reports/prepare_uhd_run_binding.py"):
        rows[name]=dict(kind="sources",bytes=(ROOT/name).stat().st_size,sha256=p.sha((ROOT/name).read_bytes()))
    for name in ("binding.json","qualification.claim","qualification.json","qualification.log",
            "record.json","decoder.claim","verification.claim","verification.json"):
        path=CHECK/name
        rows[str(path.relative_to(ROOT)).replace("\\","/")]=dict(kind="metadata",bytes=path.stat().st_size,
            sha256=p.sha(path.read_bytes()))
    sources=sum(v["bytes"] for v in rows.values() if v["kind"]=="sources")
    binding=dict(status="BLOCKED_NOT_START_READY",run_id=RUN,output=str(target),
        output_absent=True,authorization_created=False,profile=json.loads(p.bind(source,RUN)),
        events=old["manifest"]["events"],current_references=rows,
        decoder_check_record_sha256=proof["record_sha256"],
        lower_bound=dict(previous_reference_sources_current_bytes=old_source_bytes,
            sources_including_current_new_dependencies=sources,source_limit=262144,
            source_excess=sources-262144),
        limitations=["Session still constructs default 512 MiB worker.",
            "Historical worker/player source approvals do not cover changed source hashes.",
            "Source lower bound exceeds unchanged limit; complete final session ledger not approved.",
            "Resource evidence and independent session verifier need explicit private profile binding."],
        system_limits_unchanged=True)
    with (OUT/"proposed-binding.json").open("x",encoding="utf-8") as stream:
        json.dump(binding,stream,indent=2,sort_keys=True)


if __name__=="__main__":main()
