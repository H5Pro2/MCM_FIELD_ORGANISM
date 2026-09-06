"""Independent NF whole-record verification, using unchanged NE receipt checks."""

from dataclasses import asdict
import json
from pathlib import Path

from tools import _s2ne_private_run_verification as old
from tools import _s2nf_private_run as run

ne, require, digest = run.ne, run.require, run.digest


def verify_record(record, *, plan, config):
    old._check_digest(record, "record_digest")
    require(set(record) == {"schema", "run_id", "mode", "output_directory", "plan", "plan_digest", "config_digest",
        "code_before", "code_after", "catalog", "catalog_digest", "status", "events", "states", "initial_states",
        "counts", "failure", "attempts", "record_digest"}, "RECORDING_KEYS_INVALID")
    ne.check_plan(plan)
    require(record["schema"] == run.SCHEMA and record["plan"] == [asdict(e) for e in plan]
            and record["plan_digest"] == digest(record["plan"]) and len(ne.canonical(record)) <= run.MAX_BYTES,
            "RECORDING_FORM_INVALID")
    mode = record["mode"]
    require(mode in ("MAIN", "NEUTRAL") and record["run_id"] == Path(record["output_directory"]).name, "RUN_BINDING_INVALID")
    if mode == "MAIN":
        require(plan == run.sources.events_from_plan(run.sources.load_plan()), "MAIN_PLAN_INVALID")
    else:
        require(len(plan) <= 6 and sum(e.kind == "FORMATION" for e in plan) <= 2
                and all(e.audio_source.startswith("neutral") for e in plan), "NEUTRAL_BOUNDARY_INVALID")
    run.check_limits(record["counts"])
    require(all(type(n) is int and n >= 0 for n in (*record["counts"].values(), *record["attempts"].values())), "COUNTER_FORM_INVALID")
    if record["status"] == "NOT_EVALUABLE":
        f = record["failure"]
        require(set(f) == {"phase", "event_index", "event_id", "completed_events", "last_state_digest", "error_class", "code"}
                and f["phase"] in run.PHASES and ne.re.fullmatch(r"[A-Z][A-Z0-9_]{0,95}", f["code"])
                and ne.re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,95}", f["error_class"]), "FAILURE_FORM_INVALID")
        n, i = f["completed_events"], f["event_index"]
        require(type(n) is int and 0 <= n <= len(plan)
                and ((i is None and n == 0 and f["event_id"] is None) or
                     (type(i) is int and 0 <= i < len(plan) and f["event_id"] == plan[i].event_id
                      and (i == n or n == len(plan)))), "FAILURE_PROGRESS_INVALID")
        require(record["events"] == [] and record["states"] == record["initial_states"] == {}
                and record["catalog"] is record["catalog_digest"] is None, "PARTIAL_RESULT_FORBIDDEN")
        require(f["last_state_digest"] is None or ne.arms.kz._valid_digest(f["last_state_digest"]), "FAILURE_STATE_INVALID")
        require(record["config_digest"] == config.config_digest or
                (record["config_digest"] is None and f["phase"] == "BINDINGS"), "CONFIG_INVALID")
        c, a = record["counts"], record["attempts"]
        require(c["events"] == n and c["formations"] == sum(e.kind == "FORMATION" for e in plan[:n])
                and c["cues"] == n - c["formations"] and c["arms"] == 4 * c["cues"]
                and c["slot_visits"] == 20 * c["arms"]
                and c["formations"] <= a["formations"] <= c["formations"] + 1
                and c["arms"] <= a["arms"] <= c["arms"] + 4, "FAILURE_COUNTER_INVALID")
        require(record["code_after"] == {p: ne.filehash(run.sources.ROOT / p) if (run.sources.ROOT / p).is_file()
                else None for p in record["code_before"]}, "FAILURE_SOURCE_INVALID")
        require((record["code_before"] == {} and f["phase"] == "BINDINGS" and n == 0)
                or set(record["code_before"]) == set(run.sources.source_hashes()), "FAILURE_SOURCE_SET_INVALID")
        return run.sealed(dict(status="NOT_EVALUABLE", record_digest=record["record_digest"],
            plan_digest=record["plan_digest"], completed_events=n, read_only=True), "verification_digest")
    require(record["status"] == "RECORDING_COMPLETE" and record["failure"] is None
            and record["config_digest"] == config.config_digest, "TERMINAL_OR_CONFIG_INVALID")
    require(record["code_before"] == record["code_after"] == run.sources.source_hashes(), "CODE_BINDING_INVALID")
    catalog = record["catalog"]
    require(digest(catalog) == record["catalog_digest"], "CATALOG_DIGEST_INVALID")
    run.sources.validate_catalog(catalog, main=mode == "MAIN")
    require(set(catalog["audio"]) == {e.audio_source for e in plan}, "CATALOG_EVENT_SET_INVALID")
    states = {key: old.decode_state(value, config) for key, value in record["states"].items()}
    require(all(key == state.state_digest for key, state in states.items()), "STATE_POOL_INVALID")
    histories = tuple(dict.fromkeys(e.history_id for e in plan))
    require(set(record["initial_states"]) == set(histories), "INITIAL_HISTORY_INVALID")
    current, used = dict(record["initial_states"]), set(record["initial_states"].values())
    for key in current.values():
        s = states[key]
        require(s.generation == 0 and s.parent_state_digest is None and s.last_input_digest is None
                and not any(e.occupied for e in s.b4_state.entries)
                and not any(e.occupied for e in s.tspm_state.fast_state.slots)
                and all(bank.accepted_step_count == 0 and not any(e.occupied for e in bank.slots)
                        for bank in (s.tspm_state.auditory_ppb1_state, s.tspm_state.visual_ppb1_state)), "INITIAL_STATE_INVALID")
    require(len(record["events"]) == len(plan), "EVENT_COUNT_INVALID")
    transitions, equality = [], []
    for spec, event in zip(plan, record["events"], strict=True):
        old._check_digest(event, "event_digest")
        require(event["spec"] == asdict(spec) and event["kind"] == spec.kind
                and event["prestate"] == current[spec.history_id], "EVENT_CONTINUITY_INVALID")
        pre, post = states[event["prestate"]], states[event["poststate"]]
        used.update((pre.state_digest, post.state_digest))
        bound = old._source(spec, event["source"], config, catalog)
        if spec.kind == "FORMATION":
            require(event["cue"] is None and event["arms"] == [], "FORMATION_FORM_INVALID")
            transitions.append(dict(event_id=spec.event_id,
                transitions=old._formation(event, pre, post, bound, config, record["run_id"])))
        else:
            require(pre == post and event["formation"] is None and event["owner_before"] is None
                    and ne.canonical(event["cue"]) == ne.canonical(asdict(bound)), "READ_ONLY_CUE_INVALID")
            decoded = tuple(old.decode_arm(a) for a in event["arms"])
            require(tuple((a.rule, a.implementation) for a in decoded) == ne.ARM_ORDER, "ARM_ORDER_INVALID")
            for arm in decoded:
                ne.direct.verify_arm(arm=arm, config=config, state=pre, cue=bound,
                                     band_plan=ne.arms.kz.build_auditory_band_plan_48())
            equality.append(dict(event_id=spec.event_id,
                reference=ne.direct.compare_technical(decoded[0], decoded[1]),
                alternative=ne.direct.compare_technical(decoded[2], decoded[3])))
        current[spec.history_id] = post.state_digest
    totals = ne.counts(record["events"])
    require(totals == record["counts"] and used == set(states), "TOTALS_OR_STATE_POOL_INVALID")
    require(record["attempts"]["formations"] == totals["formations"] and record["attempts"]["arms"] == totals["arms"], "ATTEMPT_COUNT_INVALID")
    if mode == "MAIN":
        require(tuple(totals[k] for k in ("events", "formations", "cues", "arms", "slot_visits", "logical_operations"))
                == (13, 3, 10, 40, 800, 560)
                and (record["attempts"]["audio"], record["attempts"]["visual"]) == (13, 3), "MAIN_COUNTS_INVALID")
    return run.sealed(dict(status="RECORDING_COMPLETE", record_digest=record["record_digest"],
        plan_digest=record["plan_digest"], counts=totals, read_only=True,
        final_states=current, ppb_transitions=transitions, baseline_equality=equality), "verification_digest")


def verify_file_once(path, *, plan, config):
    path = Path(path).resolve(strict=True)
    require(path.name == "recording.json", "RECORDING_PATH_INVALID")
    target = path.with_name("verification.json")
    require(not target.exists(), "VERIFICATION_ALREADY_EXISTS")
    pending = target.with_name(target.name + ".pending")
    with pending.open("xb") as handle:
        before = ne.filehash(path)
        try:
            require(path.stat().st_size <= run.MAX_BYTES, "RECORDING_SIZE_EXCEEDED")
            data = path.read_bytes()
            record = json.loads(data)
            require(ne.canonical(record) == data and record["output_directory"] == str(path.parent), "RECORDING_PATH_INVALID")
            result = verify_record(record, plan=plan, config=config)
            require(ne.filehash(path) == before, "FILE_MUTATED")
        except Exception as error:
            result = dict(status="NOT_EVALUABLE", phase="VERIFICATION", error_class=type(error).__name__,
                          code=error.code if isinstance(error, ne.RunError) else "INVALID_RECORDING")
        result = run.sealed({**result, "record_file_sha256": before, "file_unchanged": ne.filehash(path) == before}, "report_digest")
        handle.write(ne.canonical(result))
        handle.flush()
        ne.os.fsync(handle.fileno())
    ne.os.link(pending, target)
    pending.unlink()
    return target


def verify_main_once(path):
    require(Path(path).resolve().parent.parent == (run.sources.ROOT / "reports/s2nf").resolve(), "MAIN_OUTPUT_ROOT_INVALID")
    return verify_file_once(path, plan=run.sources.events_from_plan(run.sources.load_plan()), config=ne.make_config())
