"""Administrative binding only; never opens a player, decoder or session."""
from tools import _s2oe_media_session as m

b,s,p=m.b,m.s,m.p
OLD=b.ROOT/"reports/s2oe/media-player-qualification-20260911-03"
OUT=b.ROOT/"reports/s2oe"/m.QUAL_ID
EXTRA=("reports/prepare_media_admission.py","reports/verify_media_admission.py")


def prepare():
    if OUT.exists():
        raise RuntimeError("ADMIN_BINDING_ALREADY_EXISTS")
    historic=s.read_json(OLD/"result.json")
    balance=s.read_json(OLD/"final-balance.json")
    current=m.inventory()
    tree=[[f.relative_to(OLD).as_posix(),f.stat().st_size,s.sha(f.read_bytes())]
        for f in sorted(OLD.rglob("*")) if f.is_file()]
    delta=sum(v[1] for v in current.values())-sum(v[1] for v in historic["sources"].values())
    totals=dict(balance["totals"])
    totals["metadata"]-=balance["remaining_reserve"]
    totals["total"]-=balance["remaining_reserve"]
    reserve=98304-balance["screenshot_bytes"]+4608
    for k in ("sources","shared","total"):
        totals[k]+=delta
    totals["metadata"]+=reserve
    totals["total"]+=reserve
    limits=dict(p.SESSION_LIMITS,metadata=147456)
    value=b.sealed(dict(version="s2oe.player-admission.v1",kind="ADMINISTRATIVE_ONLY",
        origin=OLD.relative_to(b.ROOT).as_posix(),tree_sha256=b.digest(tree),file_count=len(tree),
        current_sources_digest=b.digest(current),added_sources=list(EXTRA),
        session_module_transition=dict(old_qualification=historic["run_id"],new_qualification=m.QUAL_ID),
        limits=limits,session_limits=p.SESSION_LIMITS,
        reserves=dict(screenshots=98304,administrative_files_and_report=4608),
        budget=dict(totals=totals,remaining_reserve=reserve,
            violations=[k for k,v in totals.items() if v>limits[k]]),
        new_functional_test_calls=0),"binding_digest")
    OUT.mkdir()
    s.prior.save(OUT/"binding.json",value)
    print(value["budget"])
    if value["budget"]["violations"]:
        raise RuntimeError("ADMIN_BUDGET_EXCEEDED")


if __name__=="__main__":
    prepare()
