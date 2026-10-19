"""Independent evidence-only verification: no project/decoder imports."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"reports/s2oe/decoder-first-window-diagnostic-20260911-01"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    with (OUT/"verification.claim").open("xb") as stream:
        stream.write(b"once, read-only evidence\n")
    b = json.loads((OUT/"binding.json").read_text())
    r = json.loads((OUT/"diagnostic.json").read_text())
    assert r["binding_sha256"] == sha(OUT/"binding.json")
    for path, ref in b["code"].items():
        assert sha(ROOT/path) == ref["sha256"]
        assert (ROOT/path).stat().st_size == ref["bytes"]
    common = ROOT/"reports/s2oe/media-player-run-binding-20260911-02/common.json"
    assert sha(common) == b["common_sha256"] == r["source_binding_sha256"]
    assert json.loads(common.read_text())["manifest"]["source"] == b["source"]
    q = json.loads((OUT/"qualification.json").read_text())
    assert q["status"] == "QUALIFIED" and q["tests"] == 5
    assert q["log_sha256"] == sha(OUT/"qualification.log")
    assert r["decoder_calls"] <= 1 and r["selection"] == {"repeat": 1, "window": 0}
    assert all(r[k] == 0 for k in ("receptors", "nj", "field", "memory", "runtime"))
    assert r["gates_opened"] is False
    resources = r.get("resources", r.get("failure", {}).get("detail"))
    assert resources["process_commit_limit"] == resources["job_commit_limit"] == 536870912
    if "resources" in r:
        assert resources["worker_closed"] is True
        assert r["counters"]["selected_windows"] <= 1
    if r["status"] == "NOT_EVALUABLE":
        assert r["failure"]["code"]
    else:
        assert r["status"] == "DECODER_WINDOW_COMPLETE"
        assert r["pts"] * 20 <= 30000 < r["next_pts"] * 20
        assert r["output_bytes"] == [19200, 6220800]
    entries = {str(p.relative_to(ROOT)): p.stat().st_size for p in OUT.iterdir() if p.is_file()}
    total = sum(entries.values()) + sum(v["bytes"] for v in b["code"].values()) + common.stat().st_size
    assert total + 8192 + 8192 <= b["total_reserved_bytes"]
    result = dict(status="EVIDENCE_VALID", diagnostic_status=r["status"],
        diagnostic_sha256=sha(OUT/"diagnostic.json"), files=entries,
        actual_before_verification_bytes=total, verification_and_report_reserve=16384,
        bound_total_bytes=b["total_reserved_bytes"], read_only=True,
        limits="Recorded phases, counters, code and limits only; no media or decoder replay; no numerical AV validation.")
    raw = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    assert len(raw) <= 8192
    with (OUT/"verification.json").open("xb") as stream:
        stream.write(raw)


if __name__ == "__main__":
    verify()
