"""Bound NQ composition, one atomic result. Main is closed by default."""
from dataclasses import asdict
from pathlib import Path

from tools import _s2nq_private_mask_scan as s
from tools import _s2nq_private_direct as baseline
from tools import _s2nq_private_sources as sources

io, memory = sources.io, s.memory
ROOT, MAX_BYTES = io.ROOT, 4194304
MAIN_GATE = False
SCHEMA = "s2nq.memory-transfer-recording.v1"
ORDER = tuple((view, role) for view in s.VIEWS for role in ("PRIMARY", "DIRECT_BASELINE"))
LIMITS = dict(events=36, formations=16, cues=20, arms=80, slot_inspections=1600,
              band_differences=38400, equality_comparisons=3840, logical_operations=1120,
              formation_l1_limit=71040, recording_bytes=MAX_BYTES)
# Additional read-only work, never charged to retrieval execution.
VERIFY_LIMITS = dict(arm_checks=80, slot_inspections=1600, band_differences=38400,
    equality_comparisons=3840, formation_checks=16, fast_rank_terms=16128,
    ppb_selection_terms=24576, update_components=10752, state_decodes=20, source_bindings=36,
    state_validation_passes=116, state_value_validation_limit=645888,
    source_projection_validation_passes=108, input_value_checks=6336, max_input_bytes=MAX_BYTES)
PHASES = ("BINDINGS", "INITIAL_STATE", "SOURCE", "FORMATION", "RETRIEVAL", "FINAL_BINDINGS", "PUBLICATION")


def code_hashes():
    paths = set(s.ne.SOURCE_PATHS) | {
        "docs/S2NQ_STATISCHER_MEMORY_TRANSFERPLAN_AUDITIVE_ABDECKUNG.md",
        "tools/_s2nq_private_mask_scan.py", "tools/_s2nq_private_direct.py",
        "tools/_s2nq_private_sources.py", "tools/_s2nq_private_run.py",
        "tools/_s2nq_private_verification.py", "tools/_s2nq_private_evaluation.py",
        "tools/_s2nl_private_half_profile_binding.py", "tools/_s2nl_private_rank_verification.py",
        "tools/_s2nj_private_auditory_output_projection.py", "tools/_s2np_private_source_binding.py",
        "tools/_s2np_private_receptor_materialization.py", "tools/_s2ne_private_run.py",
        "tools/_s2ne_private_run_verification.py", "tools/_s2jx_default_live_memory_fixtures.py",
        "mcm_field_organism/log_spectral_receptor.py", "mcm_field_organism/finite_video_path.py",
        "mcm_field_organism/receptor_contract.py", "mcm_field_organism/receptor_time_model.py",
    }
    return {p:io.filehash(ROOT/p) for p in sorted(paths)}


def counts(events):
    fs = [e for e in events if e["kind"] == "FORMATION"]
    arms = [a for e in events for a in e["arms"]]
    return dict(events=len(events), formations=len(fs), cues=len(events)-len(fs), arms=len(arms),
        slot_inspections=sum(len(a["rows"]) for a in arms), band_differences=sum(a["comparisons"] for a in arms),
        equality_comparisons=sum(a["equality_comparisons"] for a in arms), logical_operations=len(arms)*14,
        formation_l1_limit=sum(e["formation"]["ledger"]["functional_l1_term_limit"] for e in fs))


def execute_once(*, run_id, output_root, events, provider_factory, mode="NEUTRAL"):
    s.require(type(run_id) is str and s.re.fullmatch(r"s2nq-[a-z0-9-]{5,80}",run_id) is not None, "RUN_ID_INVALID")
    s.require(mode in ("MAIN", "NEUTRAL"), "MODE_INVALID")
    sources.validate_plan(events, neutral=mode=="NEUTRAL")
    if mode == "MAIN":
        s.require(MAIN_GATE and provider_factory is sources.Sources and events == sources.EVENTS, "MAIN_GATE_CLOSED")
        s.require(Path(output_root).resolve() == (ROOT/"reports/s2nq").resolve(), "MAIN_PATH_INVALID")
    else:
        s.require(provider_factory is not sources.Sources, "NEUTRAL_SOURCE_INVALID")
    target = Path(output_root).resolve(strict=True)/run_id
    target.mkdir(exist_ok=False)
    config, hashes = None, {}
    base = dict(schema=SCHEMA, run_id=run_id, mode=mode, output_directory=str(target),
        config_digest=None, plan=[asdict(e) for e in events],
        plan_digest=s.digest([asdict(e) for e in events]), limits=LIMITS, verification_limits=VERIFY_LIMITS,
        code_before=hashes, catalog_digest=None)
    pool, initial, current, recorded = {}, {}, {}, []
    provider = None
    phase, index, last = "BINDINGS", None, None
    attempted = dict(formations=0, arms=0)
    try:
        config = s.profile.build_config()
        base["config_digest"] = config.config_digest
        hashes = code_hashes()
        base["code_before"] = hashes
        provider = provider_factory(config)
        base["catalog_digest"] = s.digest(provider.catalog)
        for index, spec in enumerate(events):
            phase = "INITIAL_STATE"
            if spec.history not in current:
                current[spec.history] = memory.initial_s2jv_composite_state(config)
                initial[spec.history] = current[spec.history].state_digest
                pool[current[spec.history].state_digest] = asdict(current[spec.history])
            pre = current[spec.history]
            last, before = pre.state_digest, s.digest(asdict(pre))
            phase = "SOURCE"
            receipt, bound = provider.materialize(spec)
            e = dict(spec=asdict(spec), kind=spec.kind, source=receipt, prestate=pre.state_digest,
                     poststate=pre.state_digest, formation=None, owner_before=None, cues=[], arms=[])
            if spec.kind == "FORMATION":
                phase = "FORMATION"
                owner = memory.S2JVFormationOwner(spec.event_id+"-owner",run_id,spec.event_id+"-consume",
                    config.config_digest,pre.state_digest,bound.input_digest)
                e["owner_before"] = asdict(owner.snapshot())
                attempted["formations"] += 1
                result = memory.advance_s2jv_atomic(config=config,prestate=pre,source=bound,owner=owner)
                e["formation"] = asdict(result)
                del e["formation"]["poststate"]
                current[spec.history] = result.poststate
                e["poststate"] = result.poststate.state_digest
                pool[result.poststate.state_digest] = asdict(result.poststate)
            else:
                phase = "RETRIEVAL"
                e["cues"] = [asdict(c) for c in bound]
                for cue in bound:
                    for fn in (s.retrieve, baseline.direct):
                        attempted["arms"] += 1
                        e["arms"].append(asdict(fn(config=config,state=pre,cue=cue)))
            s.require(before == s.digest(asdict(pre)), "PRESTATE_MUTATED")
            recorded.append(io.sealed(e,"event_digest"))
            last = e["poststate"]
        phase = "FINAL_BINDINGS"
        s.require(code_hashes() == hashes, "CODE_CHANGED")
        metrics = counts(recorded)
        s.require(all(v <= LIMITS[k] for k,v in metrics.items()), "EXECUTION_BUDGET_EXCEEDED")
        if mode == "MAIN":
            s.require((metrics["events"],metrics["formations"],metrics["cues"],metrics["arms"])
                      == (36,16,20,80), "MAIN_COUNTS_INVALID")
            s.require((provider.audio_analyses,provider.nj_projections,provider.visual_analyses)==(36,36,16), "MATERIALIZATION_COUNTS_INVALID")
        phase = "PUBLICATION"
        record = io.sealed({**base,"code_after":code_hashes(),"status":"RECORDING_COMPLETE",
            "events":recorded,"states":pool,"initial_states":initial,"counts":metrics,"attempts":attempted,
            "source_counts":dict(audio=provider.audio_analyses,nj=provider.nj_projections,visual=provider.visual_analyses),
            "failure":None},"record_digest")
        s.require(len(s.canonical(record)) <= MAX_BYTES, "RECORDING_SIZE_EXCEEDED")
    except Exception as exc:
        # Terminal technical evidence, never an invitation to retry.
        failure = dict(phase=phase,event_index=index,event_id=None if index is None else events[index].event_id,
            completed_events=len(recorded),last_state_digest=last,error_class=type(exc).__name__,
            code=exc.code if isinstance(exc,s.S2NQError) else "TECHNICAL_EXECUTION_ERROR")
        after = {p:io.filehash(ROOT/p) if (ROOT/p).is_file() else None for p in hashes}
        record = io.sealed({**base,"code_after":after,"status":"NOT_EVALUABLE",
            "events":[],"states":{},"initial_states":{},"counts":counts(recorded),"attempts":attempted,
            "source_counts":dict(audio=getattr(provider,"audio_analyses",0),nj=getattr(provider,"nj_projections",0),
                                 visual=getattr(provider,"visual_analyses",0)),"failure":failure},"record_digest")
    io.atomic_write(target/"recording.json",record,MAX_BYTES)
    return target/"recording.json"


def run_main_once(*, run_id, output_root=ROOT/"reports/s2nq"):
    global MAIN_GATE
    try:
        s.require(MAIN_GATE is True,"MAIN_GATE_CLOSED")
        return execute_once(run_id=run_id,output_root=output_root,events=sources.EVENTS,
                            provider_factory=sources.Sources,mode="MAIN")
    finally:
        MAIN_GATE = False
