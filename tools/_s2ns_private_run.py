"""Finite NS transaction/source chain and a single exclusive atomic recording."""
from dataclasses import asdict
import json
from pathlib import Path
import re

from tools import _s2ns_private_run_sources as src
from tools import _s2ns_private_direct as direct

s, b, io = src.s, src.b, src.io
ROOT = b.ROOT
SCHEMA = "s2ns.formation-chain-recording.v2"
MAIN_GATE = False
QUAL_ID = "s2ns-run-binding-qualification-20260908-01"
OWN = ("tools/_s2ns_private_run_sources.py","tools/_s2ns_private_run.py",
    "tools/_s2ns_private_run_verification.py","tools/_s2ns_private_run_evaluation.py",
    "tests/test_s2ns_private_run_binding.py","reports/s2ns/qualify_run_binding_once.py",
    "reports/s2ns/S2NS_LAUFANBINDUNG_QUALIFIKATIONSBINDUNG.md")
LIMITS = dict(events=31,formations=16,cues=15,scans=60,slot_rows=1200,
    band_differences=28800,decisions=90,equality_comparisons=4320,formation_l1_terms=71040,
    audio=31,nj=31,visual=16,states=17,record_bytes=4194304)
VERIFY_LIMITS = dict(formation_checks=16,fast_rank_terms=16128,ppb_selection_terms=24576,
    update_components=10752,state_decodes=17,source_bindings=31,halving_terms=1488,
    scans=60,slot_rows=1200,band_differences=28800,equality_comparisons=4320,
    state_validation_passes=48)
# Disjoint serialized sections, including full metadata and JSON delimiters.
SECTION_BYTES = dict(state=98304,source_formation=16384,source_cue=8192,
    formation=8192,inventory=24576,result=49152,event_shell=1024,outer=65536)
MAX_ENVELOPE_BYTES = 17*98304 + 16*16384 + 15*8192 + 16*8192 + 15*24576 + 30*49152 + 31*1024 + 65536
PHASES = ("BINDINGS","INITIAL_STATE","SOURCE","FORMATION","RETRIEVAL","PUBLICATION")


def code_hashes():
    from tools import _s2nq_private_run as historical
    extra = ("tools/_s2ns_private_two_view.py","tools/_s2ns_private_direct.py",
        "tools/_s2ns_private_evaluation.py","tools/_s2nq_private_verification.py")
    return {**historical.code_hashes(),**b.watched(),**{p:io.filehash(ROOT/p) for p in OWN+extra}}


def validate_plan(plan, mode):
    src.check(plan,"execution_digest")
    events = plan["events"]
    s.require(type(events) is list and 0 < len(events) <= 31,"PLAN_COUNT_INVALID")
    seen, histories = set(), []
    for n,e in enumerate(events,1):
        s.require(e["ordinal"] == n and type(e["ordinal"]) is int and e["event_id"] not in seen
            and s.identifier(e["history_id"]) and e["event_type"] in (b.AV,b.A),"EVENT_ORDER_INVALID")
        seen.add(e["event_id"])
        first = not histories or histories[-1] != e["history_id"]
        s.require(e["starts_fresh_history"] is first and (not first or e["history_id"] not in histories),"HISTORY_ORDER_INVALID")
        if first:
            histories.append(e["history_id"])
        src.bind_time(e,plan["execution_digest"])
        s.require((e["visual"] is None) == (e["event_type"] == b.A),"EVENT_FORM_INVALID")
        for part in (e["auditory"],e["visual"]):
            if part is not None:
                src.row(plan,part["source_id"])
    s.require(sum(e["event_type"] == b.AV for e in events) <= 16 and sum(e["event_type"] == b.A for e in events) <= 15,"PLAN_COUNT_INVALID")
    if mode == "MAIN":
        s.require(plan["execution_digest"] == src.EXECUTION_DIGEST and events == b.events(),"MAIN_PLAN_INVALID")
    else:
        s.require(mode == "NEUTRAL" and all(not x["source_id"].startswith("ns-") for x in plan["sources"]),"NEUTRAL_SOURCE_INVALID")


def next_inventory(config, history, pre, post, prior, event, bound, formation):
    """Only runner-owned actual transactions create births; verifier derives them afresh."""
    chain = s.digest(dict(previous=prior.verified_chain_digest,event_digest=s.digest(event),
        prestate=pre.state_digest,poststate=post.state_digest,input_digest=bound.input_digest,
        result_digest=formation["result_digest"]))
    slots = []
    for i,((bank,a),(_,z)) in enumerate(zip(s.slot_items(pre),s.slot_items(post),strict=True)):
        g = prior.slots[i].generation
        if not z.occupied:
            g = None
        elif a != z and (bank == 0 or z.support_count == 1):
            transition = "REPLACED" if a.occupied else "CREATED"
            g = s.Generation(history,s.BANKS[bank],z.slot_id,event["event_id"],event["ordinal"],transition,
                pre.state_digest,bound.input_digest,s.slot_hash(bank,z),s.digest(dict(
                    transaction=formation["result_digest"],bank=s.BANKS[bank],slot_id=z.slot_id,event=transition)))
        s.require(not z.occupied or g is not None,"GENERATION_CHAIN_MISSING")
        values = s.slot_values(bank,z)
        slots.append(s.SlotBinding(s.BANKS[bank],z.slot_id,s.slot_hash(bank,z),
            None if values is None else s.digest(list(values)),g))
    return s.Inventory(history,config.config_digest,s.profile.half.PROFILE_DIGEST,post.state_digest,chain,tuple(slots))


def initial_inventory(config,history,state):
    s.require(state.generation == 0 and not any(x.occupied for _,x in s.slot_items(state)),"INITIAL_STATE_INVALID")
    return s.Inventory(history,config.config_digest,s.profile.half.PROFILE_DIGEST,state.state_digest,
        s.digest(dict(history=history,initial_state=state.state_digest,config=config.config_digest)),
        tuple(s.SlotBinding(s.BANKS[k],x.slot_id,s.slot_hash(k,x),None,None) for k,x in s.slot_items(state)))


def counts(events):
    forms = [e for e in events if e["formation"] is not None]
    results = [r for e in events for r in e["results"]]
    scans = [scan for r in results for scan in r["scans"]]
    return dict(events=len(events),formations=len(forms),cues=len(events)-len(forms),scans=len(scans),
        slot_rows=sum(len(x["rows"]) for x in scans),band_differences=sum(x["band_differences"] for x in results),
        decisions=sum(len(x["admissions"]) for x in results),equality_comparisons=sum(x["equality_comparisons"] for x in results),
        formation_l1_terms=sum(x["formation"]["ledger"]["functional_l1_term_limit"] for x in forms))


def size_check(record):
    """Every actual section is capped; the sum covers the full envelope, not a stub."""
    size = lambda x: len(s.canonical(x))
    s.require(MAX_ENVELOPE_BYTES <= LIMITS["record_bytes"] and len(record["states"]) <= 17,"ENVELOPE_BUDGET_INVALID")
    for state in record["states"].values():
        s.require(size(state) <= SECTION_BYTES["state"],"STATE_SIZE_EXCEEDED")
    for e in record["events"]:
        source_cap = SECTION_BYTES["source_formation" if e["formation"] is not None else "source_cue"]
        s.require(size(e["source"]) <= source_cap,"SOURCE_SIZE_EXCEEDED")
        s.require(size(dict(formation=e["formation"],owner_before=e["owner_before"])) <= SECTION_BYTES["formation"],"FORMATION_SIZE_EXCEEDED")
        s.require(size(e["inventory"]) <= SECTION_BYTES["inventory"],"INVENTORY_SIZE_EXCEEDED")
        for result in e["results"]:
            s.require(size(result) <= SECTION_BYTES["result"],"RESULT_SIZE_EXCEEDED")
        shell = {k:v for k,v in e.items() if k not in ("source","formation","owner_before","inventory","results")}
        s.require(size(shell)+256 <= SECTION_BYTES["event_shell"],"EVENT_SIZE_EXCEEDED")
    outer = {k:v for k,v in record.items() if k not in ("events","states")}
    s.require(size(outer)+4096 <= SECTION_BYTES["outer"] and size(record) <= LIMITS["record_bytes"],"RECORD_SIZE_EXCEEDED")
    return size(record)


def qualification_binding():
    folder = ROOT/"reports/s2ns"/QUAL_ID
    q = json.loads((folder/"result.json").read_bytes())
    src.check(q,"result_digest")
    s.require(q["status"] == "S2NS_RUN_BINDING_QUALIFIED" and q["test_calls"] == 1 and q["exit_code"] == 0
        and q["hashes_before"] == q["hashes_after"] == code_hashes()
        and q["logic_qualification_digest"] == logic_qualification(),"QUALIFICATION_REQUIRED")
    return q["result_digest"]


def logic_qualification():
    path = ROOT/"reports/s2ns/s2ns-two-view-qualification-20260908-01/result.json"
    s.require(io.filehash(path) == "4d180e4e2d0cc2054c1f2217fa4c5ea1f476237ee12a144acefb82392bf48fe4","LOGIC_QUALIFICATION_INVALID")
    q = json.loads(path.read_bytes())
    src.check(q,"result_digest")
    s.require(q["status"] == "S2NS_TWO_VIEW_LOGIC_QUALIFIED" and q["passed_tests"] == 24
        and q["hashes_before"] == q["hashes_after"]
        and all(io.filehash(ROOT/p) == h for p,h in q["hashes_before"].items()),"LOGIC_QUALIFICATION_INVALID")
    return q["result_digest"]


def execute_once(*,run_id,output_root,plan,provider_factory,mode="NEUTRAL",qualification=None):
    s.require(type(run_id) is str and re.fullmatch(r"s2ns-[a-z0-9-]{5,80}",run_id),"RUN_ID_INVALID")
    if mode == "MAIN":
        s.require(MAIN_GATE is True and provider_factory is src.Sources,"MAIN_GATE_CLOSED")
        s.require(Path(output_root).resolve() == (ROOT/"reports/s2ns").resolve(),"MAIN_PATH_INVALID")
    else:
        s.require(mode == "NEUTRAL" and provider_factory is not src.Sources,"NEUTRAL_SOURCE_INVALID")
        validate_plan(plan,mode)
    target = Path(output_root).resolve(strict=True)/run_id
    target.mkdir(exist_ok=False)
    config = s.profile.build_config()
    hashes = code_hashes()
    base = dict(schema=SCHEMA,source_schema=src.SCHEMA,run_id=run_id,mode=mode,
        output_directory=str(target),plan_digest=src.EXECUTION_DIGEST if plan is None else plan["execution_digest"],config_digest=config.config_digest,
        qualification_digest=qualification,code_before=hashes,limits=LIMITS,verification_limits=VERIFY_LIMITS)
    recorded,pool,current,inventories,initial = [],{},{},{},{}
    provider,index,last = None,None,None
    phase = "BINDINGS"
    attempts = dict(formations=0,results=0)
    try:
        if mode == "MAIN":
            qualification = qualification_binding()
            base["qualification_digest"] = qualification
            plan = src.load_plan()
        validate_plan(plan,mode)
        provider = provider_factory(config,plan)
        for index,spec in enumerate(plan["events"]):
            phase = "INITIAL_STATE"
            history = spec["history_id"]
            if history not in current:
                state = s.memory.initial_s2jv_composite_state(config)
                current[history] = state
                pool[state.state_digest] = asdict(state)
                initial[history] = state.state_digest
                inventories[history] = initial_inventory(config,history,state)
            pre = current[history]
            last,before = pre.state_digest,s.digest(asdict(pre))
            phase = "SOURCE"
            source,bound = provider.materialize(spec)
            e = dict(spec_digest=s.digest(spec),event_id=spec["event_id"],history_id=history,
                source=source,prestate=pre.state_digest,poststate=pre.state_digest,
                formation=None,owner_before=None,inventory=None,view_digests=[],results=[])
            if spec["event_type"] == b.AV:
                phase = "FORMATION"
                owner = s.memory.S2JVFormationOwner(spec["event_id"]+"-owner",run_id,spec["event_id"]+"-consume",
                    config.config_digest,pre.state_digest,bound.input_digest)
                e["owner_before"] = asdict(owner.snapshot())
                attempts["formations"] += 1
                result = s.memory.advance_s2jv_atomic(config=config,prestate=pre,source=bound,owner=owner)
                form = asdict(result)
                del form["poststate"]
                e["formation"] = form
                post = result.poststate
                inventories[history] = next_inventory(config,history,pre,post,inventories[history],spec,bound,form)
                current[history] = post
                e["poststate"] = post.state_digest
                pool[post.state_digest] = asdict(post)
            else:
                phase = "RETRIEVAL"
                inventory = inventories[history]
                e["inventory"] = asdict(inventory)
                e["view_digests"] = [v.view_digest for v in bound]
                for fn in (s.retrieve,direct.direct):
                    attempts["results"] += 1
                    result = fn(config=config,state=pre,inventory=inventory,lower=bound[0],upper=bound[1])
                    e["results"].append(asdict(result))
            s.require(before == s.digest(asdict(pre)),"STATE_MUTATED")
            recorded.append(io.sealed(e,"event_digest"))
            last = e["poststate"]
        phase = "PUBLICATION"
        c = counts(recorded)
        s.require(all(v <= LIMITS[k] for k,v in c.items()),"EXECUTION_BUDGET_EXCEEDED")
        source_counts = dict(audio=provider.audio_analyses,nj=provider.nj_projections,visual=provider.visual_analyses)
        s.require(source_counts["nj"] == len(recorded) and 0 <= source_counts["audio"] <= len(recorded)
            and 0 <= source_counts["visual"] <= c["formations"],"SOURCE_COUNTS_INVALID")
        if mode == "MAIN":
            s.require(source_counts == dict(audio=31,nj=31,visual=16),"SOURCE_COUNTS_INVALID")
        s.require(code_hashes() == hashes,"CODE_CHANGED")
        record = io.sealed({**base,"code_after":hashes,"status":"RECORDING_COMPLETE","events":recorded,
            "states":pool,"initial_states":initial,"counts":c,"attempts":attempts,"source_counts":source_counts,"failure":None},"record_digest")
        size_check(record)
    except Exception as exc:
        failure = dict(phase=phase,source_phase=getattr(provider,"phase",None),event_index=index,
            event_id=None if index is None else plan["events"][index]["event_id"],completed_events=len(recorded),
            last_state_digest=last,error_class=type(exc).__name__,code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"))
        record = io.sealed({**base,"code_after":code_hashes(),"status":"NOT_EVALUABLE","events":[],"states":{},
            "initial_states":{},"counts":counts(recorded),"attempts":attempts,
            "source_counts":dict(audio=getattr(provider,"audio_analyses",0),nj=getattr(provider,"nj_projections",0),
                visual=getattr(provider,"visual_analyses",0)),"failure":failure},"record_digest")
    io.atomic_write(target/"recording.json",record,LIMITS["record_bytes"])
    return target/"recording.json"


def run_main_once(*,run_id,output_root=ROOT/"reports/s2ns"):
    global MAIN_GATE
    try:
        s.require(MAIN_GATE is True,"MAIN_GATE_CLOSED")
        return execute_once(run_id=run_id,output_root=output_root,plan=None,
            provider_factory=src.Sources,mode="MAIN")
    finally:
        MAIN_GATE = False
