"""Read-only composition verification. No field, formation or retrieval entry calls."""

from dataclasses import asdict
from tools import _s2ng_private_runtime_comparison as run
from tools import _s2ne_private_run_verification as old
from mcm_field_organism.receptor_contract import ReceptorContactFrame

require, digest, canonical = run.require, run.digest, run.canonical


def tuples(p, *keys):
    return {**p, **{key: tuple(p[key]) for key in keys}}


def check(p, key):
    require(type(p) is dict and key in p and p[key] == digest({k: v for k, v in p.items() if k != key}),
            "DIGEST_INVALID")


def decode_input(p, config):
    f = dict(p["field"])
    frames = []
    for item in f["timed_frames"]:
        raw = item["frame"]
        profile = getattr(config.profile.profile, raw["modality_id"] + "_config")
        frame = ReceptorContactFrame(**tuples({**raw, "carrier_ids": profile.carrier_ids}, "values"))
        frames.append(run.field.OrganismTimedReceptorFrame(frame, run.field.CommonFieldTime(**item["field_time"])))
    f["timed_frames"] = tuple(frames)
    field = run.field.S2LOFieldInputV1(**f)
    e, op = p["event"], p["operation"]
    if e["event_type"] == "COMPLETE_AV_PERCEPTION":
        by_modality = {t.frame.modality_id: t for t in frames}
        operation = run.pairing.bind_s2jv_default_live_pair(
            pairing_plan=run.pairing.S2JVPairingPlanV1(**op), profile=config.profile,
            auditory=by_modality["auditory"], visual=by_modality["visual"])
    elif e["event_type"] == "PARTIAL_AUDITORY_CUE":
        plan = run.audio.kz.build_auditory_band_plan_48()
        require(canonical(op["band_plan"]) == canonical(asdict(plan)), "BAND_PLAN_INVALID")
        cue = run.audio.kz.MaskedAuditoryCue48V1(**tuples(op["cue"], "values"))
        operation = run.stream.AuditoryCueOperationV1(cue, plan)
    else:
        operation = run.visual.MaskedMemoryCue336V1(**tuples(op, "values", "visible_positions", "masked_positions"))
    event = run.stream.PerceptionStreamEvent336V1(**e, field_payload=field, operation_payload=operation)
    require(canonical(run.pack_input(event, config)) == canonical(p), "INPUT_FORM_INVALID")
    return event


def decode_visual(p):
    q = dict(p)
    q["contract_digests"] = tuple(q["contract_digests"])
    q["bank_scans"] = tuple(run.visual.BankScanFinding336V1(**{
        **tuples(s, "matched_slot_digests"), "records": tuple(run.visual.SlotScanRecord336V1(**r) for r in s["records"])
    }) for s in q["bank_scans"])
    for area in ("a_recent", "b_stable"):
        q[area] = run.visual.AreaScanFinding336V1(**tuples(q[area], "parent_scan_digests", "provenance_slot_digests", "masked_values"))
    if q["hypothesis"] is not None:
        q["hypothesis"] = run.visual.PartialCueContextHypothesis336V1(**tuples(
            q["hypothesis"], "provenance_slot_digests", "masked_positions", "proposed_values"))
    q["resource_ledger"] = run.visual.PartialCueResourceLedger336V1(**q["resource_ledger"])
    result = run.visual.PartialCueRetrievalResult336V1(**q)
    run.visual._validate_result(result)
    return result


def visual_semantics(result):
    return tuple(canonical(asdict(getattr(result, k))) if k != "decision" else result.decision
                 for k in ("a_recent", "b_stable", "decision")) + (
                     canonical([asdict(s) for s in result.bank_scans]), canonical(None if result.hypothesis is None else asdict(result.hypothesis)))


def verify_visual(result, config, state, cue):
    d = run.visual_direct
    d._validate_inputs(config, state, cue)
    s0, m0 = d._scan_b4(state, cue)
    s1, m1 = d._scan_fast(state, cue)
    s2, m2 = d._scan_slow(state, cue)
    a, equality = d._resolve_recent(s0, m0, s1, m1)
    b = d._resolve_stable(s2, m2)
    decision, admitted = d._choose(a, b)
    expected = d._assemble(config, state, cue, (s0, s1, s2), a, b, equality, decision, admitted)
    require(visual_semantics(result) == visual_semantics(expected)
            and result.state_digest == result.prestate_digest == result.poststate_digest == state.state_digest
            and result.config_digest == config.config_digest and result.cue_digest == cue.cue_digest,
            "VISUAL_SCAN_INVALID")


def snapshot(p, rc, field, memory_digest, n, formations, last):
    check(p, "snapshot_digest")
    expected = dict(schema=run.stream.S2LM_SCHEMA, stream_id=rc["runtime_id"], status="OPEN",
        next_ordinal=n+1, processed_event_count=n, field_attempt_count=n,
        memory_formation_attempt_count=formations, scan_attempt_count=2*(n-formations),
        field_state_digest=field["state_digest"], memory_state_digest=memory_digest, last_event_digest=last)
    require(p["stream_state_digest"] == digest(expected) and p["runtime_id"] == rc["runtime_id"]
            and p["config_digest"] == rc["config_digest"] and p["max_event_count"] == rc["max_event_count"]
            and p["schema"] == run.runtime.S2MR_SCHEMA and p["status"] in ("OPEN", "CLOSED"), "SNAPSHOT_BINDING_INVALID")
    for k in ("next_ordinal", "processed_event_count", "field_attempt_count", "memory_formation_attempt_count",
              "scan_attempt_count", "field_state_digest", "memory_state_digest"):
        require(p[k] == expected[k], "SNAPSHOT_PROGRESS_INVALID")


def verify_record(record, *, config):
    """Validate all stored evidence; no expected functional outcome is an input."""
    try:
        return _verify_record(record, config)
    except run.S2NGError:
        raise
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as error:
        raise run.S2NGError("RECORD_FORM_INVALID") from error


def _verify_record(r, config):
    before = digest(r)
    require(len(canonical(r)) <= run.MAX_BYTES, "RECORD_SIZE_EXCEEDED")
    check(r, "record_digest")
    require(r["schema"] == run.SCHEMA and r["config_digest"] == config.config_digest
            and r["sources"] == [list(p) for p in run.sources()]
            and r["status"] in ("RECORDING_COMPLETE", "NOT_EVALUABLE"), "RECORD_BINDING_INVALID")
    events = tuple(decode_input(p, config) for p in r["inputs"])
    require(r["input_digest"] == digest(r["inputs"]) and [e.ordinal for e in events] == list(range(1, len(events)+1))
            and r["limits"] == run.budget(tuple(e.event_type for e in events)), "INPUT_ORDER_INVALID")
    require(all(t.field_time.clock_id == r["field_clock_id"] for e in events for t in e.field_payload.timed_frames), "CLOCK_INVALID")
    require(r["mode"] in ("MAIN", "NEUTRAL") and (r["mode"] != "NEUTRAL" or (len(events) <= 6 and r["limits"]["formations_total"] <= 4)), "MODE_INVALID")
    try:
        states = {k: old.decode_state(v, config) for k, v in r["states"].items()}
    except run.memory.S2JWCoordinatorError as error:
        raise run.S2NGError("STATE_BINDING_INVALID") from error
    require(len(states) <= 21 and all(k == s.state_digest and len(canonical(r["states"][k])) <= run.MAX_STATE_BYTES
                                    for k, s in states.items()), "STATE_POOL_INVALID")
    require(len(r["bindings"]) == len(r["runtime_configs"]) == len(r["initial"]) == len(r["final"]) == 2, "ARM_COUNT_INVALID")
    previous, used, scanned = [], set(), set()
    require(len(r["pairs"]) <= len(events) and (r["status"] != "RECORDING_COMPLETE" or len(r["pairs"]) == len(events)), "EVENT_COUNT_INVALID")
    scanmap = {(s["arm"], s["ordinal"], s["role"]): s["value"] for s in r["scans"]}
    require(len(scanmap) == len(r["scans"]) <= 32 and all(len(canonical(v)) < run.MAX_SCAN_BYTES for v in scanmap.values()), "SCAN_POOL_INVALID")
    for i, rule in enumerate(run.audio.RULES):
        binding = run.build_binding(config, rule)
        require(canonical(r["bindings"][i]) == canonical(asdict(binding)), "RULE_BINDING_INVALID")
        rc = run.runtime.build_minimal_runtime_config(runtime_id=f'{r["comparison_id"]}-arm-{i}', max_event_count=len(events),
            source_binding_digest=r["input_digest"], component_binding_digest=binding.binding_digest)
        require(r["runtime_configs"][i] == asdict(rc), "RUNTIME_CONFIG_INVALID")
        initial = r["initial"][i]
        s = states[initial["memory"]]
        require(s.generation == 0 and s.parent_state_digest is None and s.last_input_digest is None
                and not any(e.occupied for e in s.b4_state.entries)
                and not any(e.occupied for e in s.tspm_state.fast_state.slots)
                and initial["field"]["phase"] == "PRE_CONTACT" and initial["field"]["step_count"] == 0, "INITIAL_STATE_INVALID")
        snapshot(initial["snapshot"], asdict(rc), initial["field"], s.state_digest, 0, 0, None)
        previous.append(initial)
        used.add(s.state_digest)
    require(previous[0]["field"] == previous[1]["field"] and previous[0]["memory"] == previous[1]["memory"], "INITIAL_SIBLINGS_DIFFER")
    formations, errors, contacts, comparisons = 0, [], 0, 0
    for n, pair in enumerate(r["pairs"], 1):
        check(pair, "pair_digest")
        event = events[n-1]
        full = event.event_type == "COMPLETE_AV_PERCEPTION"
        formations += int(full)
        require(pair["event_digest"] == event.event_digest and len(pair["arms"]) == 2
                and len(canonical(pair)) <= run.MAX_PAIR_BYTES, "PAIR_BINDING_INVALID")
        for i, arm in enumerate(pair["arms"]):
            prior = previous[i]
            require(arm["pre"] == prior["snapshot"], "SNAPSHOT_CHAIN_INVALID")
            step, post, f = arm["step"], arm["post"], arm["field"]
            sp = {k: v for k, v in step.items() if k not in ("step_digest", "hypothesis")}
            sp["hypothesis_digest"] = None if step["hypothesis"] is None else step["hypothesis"]["hypothesis_digest"]
            require(step["step_digest"] == digest(sp) and step["event_digest"] == event.event_digest
                    and step["prestate_digest"] == arm["pre"]["snapshot_digest"] and step["poststate_digest"] == post["snapshot_digest"], "STEP_BINDING_INVALID")
            error = tuple(step["error_codes"])
            require(all(c in ("FIELD_BRANCH_FAILED", "MEMORY_BRANCH_FAILED", "PRIMARY_SCAN_FAILED", "BASELINE_SCAN_FAILED",
                "SCAN_RESULT_INCOMPLETE", "SCAN_BASELINE_DECISION_MISMATCH", "SCAN_BASELINE_HYPOTHESIS_MISMATCH",
                "SCAN_HYPOTHESIS_INVALID", "SCAN_DECISION_INVALID") for c in error), "ERROR_CODE_INVALID")
            errors.extend(error)
            if step["perception_status"] == "FIELD_CONTACT_RECORDED":
                require("FIELD_BRANCH_FAILED" not in error and f["phase"] == "COMPLETED"
                    and f["step_count"] == prior["field"]["step_count"]+1 and f["last_end_tick"] == event.field_payload.end_tick
                    and f["state_digest"] != prior["field"]["state_digest"], "FIELD_PROGRESS_INVALID")
                payload = dict(schema=run.field.S2LO_SCHEMA, phase=f["phase"], field_component_digest=f["field_component_digest"],
                               last_end_tick=f["last_end_tick"], step_count=f["step_count"])
                require(f["state_digest"] == digest(payload), "FIELD_DIGEST_INVALID")
                count = sum(len(t.frame.values) for t in event.field_payload.timed_frames)
                receipt = dict(schema=run.field.S2LO_SCHEMA, branch="FIELD", input_digest=event.field_projection_digest,
                    prestate_digest=prior["field"]["state_digest"], poststate_digest=f["state_digest"],
                    source_event_count=len(event.field_payload.timed_frames), contact_count=count)
                require(step["field_receipt_digest"] == digest(receipt), "FIELD_RECEIPT_INVALID")
                contacts += count
            else:
                require(step["perception_status"] == "FIELD_CONTACT_FAILED" and "FIELD_BRANCH_FAILED" in error
                        and f == prior["field"] and step["field_receipt_digest"] is None, "FIELD_FAILURE_INVALID")
            prestate, state = states[prior["memory"]], states[arm["memory"]]
            used.add(state.state_digest)
            if full:
                require(step["context_status"] == "NOT_REQUESTED" and step["hypothesis"] is None
                        and step["scan_receipt_digest"] is None and step["baseline_receipt_digest"] is None, "FORMATION_SCAN_INVALID")
                if step["memory_status"] == "FORMATION_COMMITTED":
                    source = run.memory.bind_s2jv_coordinator_input(config=config, source=event.operation_payload)
                    require(state.generation == prestate.generation+1 and state.parent_state_digest == prestate.state_digest
                            and state.last_input_digest == source.input_digest and run.audio.kz._valid_digest(step["memory_receipt_digest"]), "FORMATION_CHAIN_INVALID")
                    for j, (left, right) in enumerate(zip(prestate.b4_state.entries, state.b4_state.entries, strict=True)):
                        require((right.occupied and right.values == source.av_values and right.formation_index == state.generation)
                                if j == prestate.generation % 9 else left == right, "FORMATION_INPUT_INVALID")
                    old._ppb_relations(config, prestate, state, source)
                else:
                    require(step["memory_status"] == "FORMATION_FAILED" and "MEMORY_BRANCH_FAILED" in error
                            and state == prestate and step["memory_receipt_digest"] is None, "MEMORY_FAILURE_INVALID")
            else:
                require(state == prestate and step["memory_status"] == "READ_ONLY_UNCHANGED"
                        and step["memory_receipt_digest"] is None, "CUE_MUTATED_MEMORY")
                results = []
                for role, receipt_key, failure in (("PRIMARY", "scan_receipt_digest", "PRIMARY_SCAN_FAILED"),
                    ("DIRECT_BASELINE", "baseline_receipt_digest", "BASELINE_SCAN_FAILED")):
                    key = (i, n, role)
                    if failure in error:
                        require(key not in scanmap and step[receipt_key] is None, "FAILED_SCAN_INVALID")
                        continue
                    require(key in scanmap, "SCAN_MISSING")
                    scanned.add(key)
                    p = scanmap[key]
                    if event.event_type == "PARTIAL_AUDITORY_CUE":
                        value = old.decode_arm(p)
                        require(value.rule == run.audio.RULES[i] and value.implementation == ("DIRECT_BASELINE" if role == "DIRECT_BASELINE" else "PRIMARY"), "SCAN_RULE_INVALID")
                        run.direct.verify_arm(arm=value, config=config, state=state, cue=event.operation_payload.cue, band_plan=event.operation_payload.band_plan)
                        require(step[receipt_key] == value.arm_digest, "SCAN_RECEIPT_INVALID")
                        result = value.evidence
                    else:
                        result = decode_visual(p)
                        verify_visual(result, config, state, event.operation_payload)
                        require(step[receipt_key] == result.result_digest, "SCAN_RECEIPT_INVALID")
                    results.append(result)
                    comparisons += result.resource_ledger.total_value_comparison_count
                if len(results) == 2:
                    require(results[0].decision == results[1].decision
                            and canonical(None if results[0].hypothesis is None else asdict(results[0].hypothesis))
                            == canonical(None if results[1].hypothesis is None else asdict(results[1].hypothesis)), "BASELINE_DIFFERS")
                    h = None if results[0].hypothesis is None else asdict(results[0].hypothesis)
                    require(canonical(step["hypothesis"]) == canonical(h) and step["context_status"] == (
                        "CONTEXT_CANDIDATE_AVAILABLE" if h is not None else results[0].decision), "CONTEXT_BINDING_INVALID")
                else:
                    require(step["context_status"] == "SCAN_FAILED" and step["hypothesis"] is None, "SCAN_FAILURE_INVALID")
            snapshot(post, r["runtime_configs"][i], f, state.state_digest, n, formations, event.event_digest)
            require(post["status"] == "OPEN", "STREAM_CLOSED_EARLY")
            previous[i] = dict(snapshot=post, field=f, memory=state.state_digest)
        require(pair["arms"][0]["field"] == pair["arms"][1]["field"]
                and pair["arms"][0]["memory"] == pair["arms"][1]["memory"], "SIBLING_STATES_DIFFER")
        if errors:
            require(n == len(r["pairs"]) and r["status"] == "NOT_EVALUABLE", "ERROR_CONTINUED")
    require(scanned == set(scanmap) and used == set(states) and comparisons <= r["limits"]["value_comparisons"], "EVIDENCE_COMPLETENESS_INVALID")
    require(bool(errors) == (r["status"] == "NOT_EVALUABLE"), "TERMINAL_STATUS_INVALID")
    for i, end in enumerate(r["final"]):
        check(end, "snapshot_digest")
        require(end == run.sealed({**{k: v for k, v in previous[i]["snapshot"].items() if k != "snapshot_digest"},
                                  "status": "CLOSED"}, "snapshot_digest"), "CLOSE_INVALID")
    require(digest(r) == before, "VERIFICATION_MUTATED_RECORD")
    return run.sealed(dict(status=r["status"], record_digest=r["record_digest"], read_only=True,
        baseline_equal=True, sibling_states_equal=True, completed_events=len(r["pairs"]), scan_receipts=len(scanned),
        field_contacts=contacts, value_comparisons=comparisons), "verification_digest")


__all__ = ()
