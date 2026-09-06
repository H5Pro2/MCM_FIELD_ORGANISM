"""Small closed S2-NF execution binding; no predictions in the run path."""

from dataclasses import asdict
from pathlib import Path
import re

from tools import _s2ne_private_run as ne
from tools import _s2nf_private_run_sources as sources

MAIN_GATE = False
SCHEMA = "s2nf.complete-transfer-recording.v1"
require, digest, sealed = ne.require, ne.digest, ne.sealed
MAX_BYTES = ne.MAX_BYTES
PHASES = ne.PHASES
LIMITS = dict(band_differences=19200, equality_comparisons=1920, retrieval_comparisons=21120,
              formation_l1_limit=10656, logical_operations=560, slot_visits=800)


def check_limits(counts):
    require(all(counts[k] <= limit for k, limit in LIMITS.items()), "NF_RESOURCE_LIMIT_EXCEEDED")


def execute_once(*, run_id, output_root, plan, provider_factory, mode="NEUTRAL", size_limit=MAX_BYTES):
    ne.check_plan(plan)
    require(type(run_id) is str and re.fullmatch(r"[a-z][a-z0-9-]{7,89}", run_id), "RUN_ID_INVALID")
    require(mode in ("MAIN", "NEUTRAL"), "MODE_INVALID")
    require(type(size_limit) is int and 0 < size_limit <= MAX_BYTES, "SIZE_LIMIT_INVALID")
    if mode == "MAIN":
        require(MAIN_GATE is True and provider_factory is sources.Sources and size_limit == MAX_BYTES, "MAIN_GATE_CLOSED")
        require(plan == sources.events_from_plan(sources.load_plan())
                and Path(output_root).resolve() == (sources.ROOT / "reports/s2nf").resolve(), "MAIN_PLAN_INVALID")
    else:
        require(len(plan) <= 6 and sum(e.kind == "FORMATION" for e in plan) <= 2
                and all(e.audio_source.startswith("neutral") for e in plan), "NEUTRAL_BOUNDARY_INVALID")
    target = Path(output_root).resolve(strict=True) / run_id
    target.mkdir(exist_ok=False)
    base = dict(schema=SCHEMA, run_id=run_id, mode=mode, output_directory=str(target),
        plan=[asdict(e) for e in plan], plan_digest=digest([asdict(e) for e in plan]),
        config_digest=None, code_before={}, code_after={}, catalog=None, catalog_digest=None)
    events, states, initial, current = [], {}, {}, {}
    phase, index, last, provider = "BINDINGS", None, None, None
    formations = arm_calls = 0
    try:
        base["code_before"] = sources.source_hashes()
        config = ne.make_config()
        base["config_digest"] = config.config_digest
        provider = provider_factory(config)
        for index, spec in enumerate(plan):
            phase = "INITIAL_STATE"
            if spec.history_id not in current:
                current[spec.history_id] = ne.memory.initial_s2jv_composite_state(config)
                initial[spec.history_id] = current[spec.history_id].state_digest
                states[current[spec.history_id].state_digest] = asdict(current[spec.history_id])
            pre = current[spec.history_id]
            last, before = pre.state_digest, digest(asdict(pre))
            phase = "SOURCE"
            receipt, bound = provider.materialize(spec)
            event = dict(spec=asdict(spec), kind=spec.kind, source=receipt, prestate=last, poststate=last,
                formation=None, owner_before=None, cue=None, arms=[])
            if spec.kind == "FORMATION":
                phase = "FORMATION"
                owner = ne.memory.S2JVFormationOwner(spec.event_id + "-owner", run_id,
                    spec.event_id + "-consume", config.config_digest, last, bound.input_digest)
                event["owner_before"] = asdict(owner.snapshot())
                formations += 1
                result = ne.memory.advance_s2jv_atomic(config=config, prestate=pre, source=bound, owner=owner)
                event["formation"] = asdict(result)
                del event["formation"]["poststate"]
                current[spec.history_id] = result.poststate
                event["poststate"] = result.poststate.state_digest
                states[result.poststate.state_digest] = asdict(result.poststate)
            else:
                phase = "RETRIEVAL"
                event["cue"] = asdict(bound)
                for rule, implementation in ne.ARM_ORDER:
                    function = ne.arms.retrieve if implementation == "PRIMARY" else ne.direct.direct_retrieve
                    arm_calls += 1
                    result = function(rule=rule, config=config, state=pre, cue=bound,
                                      band_plan=ne.arms.kz.build_auditory_band_plan_48())
                    event["arms"].append(asdict(result))
            require(before == digest(asdict(pre)), "PRESTATE_MUTATED")
            events.append(sealed(event, "event_digest"))
            last = event["poststate"]
        phase = "FINAL_BINDINGS"
        sources.validate_catalog(provider.catalog, main=mode == "MAIN")
        base["catalog"], base["catalog_digest"] = provider.catalog, digest(provider.catalog)
        base["code_after"] = sources.source_hashes()
        require(base["code_before"] == base["code_after"], "CODE_CHANGED")
        counts = ne.counts(events)
        check_limits(counts)
        if mode == "MAIN":
            require(tuple(counts[k] for k in ("events", "formations", "cues", "arms", "slot_visits")) == (13, 3, 10, 40, 800)
                    and (provider.audio_analyses, provider.visual_analyses) == (13, 3), "MAIN_COUNTS_INVALID")
        phase = "PUBLICATION"
        record = sealed({**base, "status": "RECORDING_COMPLETE", "events": events, "states": states,
            "initial_states": initial, "counts": counts, "failure": None,
            "attempts": dict(formations=formations, arms=arm_calls, audio=provider.audio_analyses,
                             visual=provider.visual_analyses)}, "record_digest")
        require(len(ne.canonical(record)) <= size_limit, "RECORDING_SIZE_EXCEEDED")
    except Exception as error:
        base["code_after"] = {p: ne.filehash(sources.ROOT / p) if (sources.ROOT / p).is_file() else None for p in base["code_before"]}
        record = sealed({**base, "catalog": None, "catalog_digest": None, "status": "NOT_EVALUABLE",
            "events": [], "states": {}, "initial_states": {}, "counts": ne.counts(events),
            "attempts": dict(formations=formations, arms=arm_calls, audio=getattr(provider, "audio_analyses", 0),
                             visual=getattr(provider, "visual_analyses", 0)),
            "failure": dict(phase=phase, event_index=index, event_id=None if index is None else plan[index].event_id,
                completed_events=len(events), last_state_digest=last, error_class=type(error).__name__,
                code=error.code if isinstance(error, ne.RunError) else "EXECUTION_ERROR")}, "record_digest")
    ne.atomic_write(target / "recording.json", record)
    return target / "recording.json"


def run_main_once(*, run_id, output_root=sources.ROOT / "reports/s2nf"):
    global MAIN_GATE
    try:
        require(MAIN_GATE is True, "MAIN_GATE_CLOSED")
        return execute_once(run_id=run_id, output_root=output_root, plan=sources.events_from_plan(sources.load_plan()),
                            provider_factory=sources.Sources, mode="MAIN")
    finally:
        MAIN_GATE = False
