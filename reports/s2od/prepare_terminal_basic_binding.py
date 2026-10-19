"""Administrative preparation only: no payload reads, session, scans or tests."""
from dataclasses import asdict
from pathlib import Path
from tools import _s2od_private_terminal_client as c

s,b=c.s,c.b
RUN="caller-terminal-basic-20260911-01"


def main():
    out=b.ROOT/"reports/s2od/terminal-basic-preparation"
    target=b.ROOT/"reports/s2od"/RUN
    if out.exists() or target.exists(): raise RuntimeError("OUTPUT_EXISTS")
    inv=s.inventory()
    original=s.read_json(b.ROOT/"reports/s2ob/caller-input-binding/manifest.json")
    old=b.decode_manifest(original)
    manifest=b.build_manifest(RUN,old.events,b.digest(inv["ob"]))
    assert asdict(manifest)["events"]==asdict(old)["events"]
    out.mkdir()
    s.prior.save(out/"manifest.json",asdict(manifest))
    historical="reports/s2ob/caller-input-binding/evaluation-plan.json"
    expected=s.read_json(b.ROOT/historical)
    evaluation=b.sealed(dict(version="s2od.terminal-evaluation-binding.v1",run_id=RUN,
        manifest_digest=manifest.manifest_digest,historical_manifest_digest=old.manifest_digest,
        historical_evaluation_digest=expected["evaluation_digest"],
        decisions=expected["decisions"],formations=expected["formations"],
        commands=["open"]+[x for _ in range(7) for x in ("next","status")]+["close"],
        display_fields=["perception_status","memory_status","context_status","hypothesis","error_codes"],
        comparison="Compare hashes of returned display against render_step of stored steps; no scan or verifier rerun",
        execution_authorized=False),"evaluation_digest")
    s.prior.save(out/"evaluation-binding.json",evaluation)
    common,_=s.qualified_common(manifest,b.ROOT/"reports/s2oc"/s.QUAL_ID)
    refs=list(common["references"])
    for p in c.OWN:
        refs.append(s.file_reference("sources",b.ROOT/p))
    q=b.ROOT/"reports/s2od"/c.QUAL_ID
    for name in ("preregistration.json","stdout.txt","stderr.txt","result.json"):
        refs.append(s.file_reference("metadata",q/name))
    for p in ("reports/s2ob/caller-input-binding/manifest.json",historical,
              "reports/s2ob/caller-input-binding/binding.json",
              "reports/s2ob/caller-input-binding/provisioning.json",
              "reports/s2od/BEDIENVERSUCH_VORBEREITUNG.md"):
        refs.append(s.file_reference("metadata",b.ROOT/p))
    for name in ("manifest.json","evaluation-binding.json"):
        refs.append(s.file_reference("metadata",out/name))
    refs.append(s.file_reference("sources",Path(__file__)))
    common=s.build_common(manifest,inv,refs,common["qualification"])
    s.validate_common(common,inv,qualified=True)
    c.validate_client(common,inv)
    s.prior.save(out/"common.json",common)
    extras=c.entry.ATTACHMENTS+(("sources","@pending-fixed-starter",4096),
        ("metadata","@budget-file",8192))
    positions=[]
    violations=[]
    for n in range(8):
        success,failure=c.verification.synthetic_forms(common,n)
        row=dict(completed=n)
        for arm,pair in (("success",success),("failure",failure)):
            measured=s.ledger(*pair,common,attachments=extras)
            row[arm]=measured["totals"]
            violations.extend(dict(completed=n,arm=arm,code=x) for x in measured["violations"])
        positions.append(row)
    maxima={arm:{k:max(row[arm][k] for row in positions) for k in b.LIMITS} for arm in ("success","failure")}
    budget=b.sealed(dict(version="s2od.terminal-preparation.v1",run_id=RUN,
        main_authorized=False,start_logic_bound=False,output=str(target.relative_to(b.ROOT)),
        common_sha256=s.sha(b.canonical(common)),source_digest=b.digest(inv),
        client_sources=c.sources(),manifest_digest=manifest.manifest_digest,
        evaluation_digest=evaluation["evaluation_digest"],positions=positions,maxima=maxima,
        limits=b.LIMITS,attachments=extras,violations=violations,
        read_plan=common["read_plan"],actual_read_bytes=0,
        missing="Fixed authorized starter and display assessment implementation/hash/coverage; 4096-byte source allowance is not a qualification",
        files={name:[(out/name).stat().st_size,s.sha((out/name).read_bytes())]
               for name in ("common.json","manifest.json","evaluation-binding.json")}),"budget_digest")
    if len(b.canonical(budget))>8192: raise RuntimeError("BUDGET_FILE_LIMIT")
    s.prior.save(out/"budget.json",budget)
    print(b.canonical(dict(status="PREPARED_PENDING_START_BINDING",maxima=maxima,violations=violations,
        common_sha256=budget["common_sha256"],budget_digest=budget["budget_digest"],read_plan=budget["read_plan"],
        bytes={p.name:p.stat().st_size for p in out.iterdir()},gates=c.entry.MAIN_GATE)).decode())


if __name__=="__main__":main()
