"""Independent bounded recording validation; never advance memory or retrieve."""

from dataclasses import asdict
import json
from pathlib import Path

from mcm_field_organism import _ppb1_reference as ppb
from mcm_field_organism import _tspm1_private as tspm
from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from tools import _s2ne_private_run as run
from tools import _s2ne_private_auditory_transfer as arms
from tools import _s2ne_private_direct_and_verification as independent
from tools import _s2jw_profiled_memory_coordinator as memory
from tools import _s2jw_profiled_memory_ledger as ledgers

require, digest = run.require, run.digest
kz = arms.kz


def _tuples(payload, *names):
    result = dict(payload)
    for name in names:
        result[name] = tuple(result[name])
    return result


def decode_state(p, config):
    """Explicit restoration of the existing types, not a memory operation."""
    b4 = dict(p["b4_state"])
    b4["entries"] = tuple(comparison._FIFOEntry(**_tuples(e, "values")) for e in b4["entries"])
    nested = dict(p["tspm_state"])
    fast = dict(nested["fast_state"])
    fast["slots"] = tuple(tspm.TSPM1FastSlot(**_tuples(s, "auditory_values", "visual_values")) for s in fast["slots"])
    nested["fast_state"] = tspm.TSPM1FastState(**fast)
    for bank in ("auditory_ppb1_state", "visual_ppb1_state"):
        data = dict(nested[bank])
        data["slots"] = tuple(ppb.PPB1PrototypeSlot(**_tuples(s, "prototype_values")) for s in data["slots"])
        nested[bank] = ppb.PPB1BankState(**data)
    result = memory.S2JVCompositeStateV1(**{**p, "b4_state": comparison._B4State(**b4),
                                           "tspm_state": tspm.TSPM1CompositeState(**nested)})
    require(run.canonical(asdict(result)) == run.canonical(p), "STATE_FORM_INVALID")
    return memory._validate_state(config, result)


def decode_arm(p):
    value = dict(p["evidence"])
    scans = []
    for scan in value["bank_scans"]:
        item = _tuples(scan, "matched_slot_digests")
        item["records"] = tuple(kz.AuditorySlotScanRecordV1(**r) for r in scan["records"])
        scans.append(kz.AuditoryBankScanFindingV1(**item))
    value["bank_scans"] = tuple(scans)
    for name in ("a_recent", "b_stable_auditory"):
        value[name] = kz.AuditoryAreaFindingV1(**_tuples(value[name], "parent_scan_digests", "provenance_slot_digests", "masked_values"))
    if value["hypothesis"] is not None:
        value["hypothesis"] = kz.AuditoryPartialCueHypothesis48V1(**_tuples(
            value["hypothesis"], "provenance_slot_digests", "masked_bands", "proposed_values"))
    value["resource_ledger"] = kz.AuditoryPartialCueResourceLedgerV1(**value["resource_ledger"])
    value["source_digests"] = tuple(value["source_digests"])
    result = arms.AuditoryTransferArmV1(**{**p, "sources": tuple(tuple(v) for v in p["sources"]),
                                          "evidence": kz.AuditoryPartialCueRetrievalResultV1(**value)})
    require(run.canonical(asdict(result)) == run.canonical(p), "ARM_FORM_INVALID")
    return result


def _check_digest(obj, key):
    require(type(obj) is dict and obj[key] == digest({k: v for k, v in obj.items() if k != key}), "DIGEST_INVALID")


def _source(spec, receipt, config, catalog):
    _check_digest(receipt, "source_digest")
    source = catalog["audio"][spec.audio_source]
    p = config.profile.profile.auditory_config
    frame = ReceptorContactFrame("auditory", p.geometry_id, spec.event_id, spec.history_id + "-audio-sample",
                                 spec.ordinal * 9600, spec.ordinal * 9600 + 4800, p.carrier_ids, tuple(source["values"]))
    visual = None if receipt["visual"] is None else ReceptorContactFrame(**_tuples(receipt["visual"], "carrier_ids", "values"))
    expected, bound = run.materialized_from_frames(spec, config, catalog, frame, visual)
    require(run.canonical(receipt) == run.canonical(expected), "SOURCE_EVENT_INVALID")
    return bound


def _ppb_relations(config, pre, post, source):
    transitions = []
    for modality in ("auditory", "visual"):
        a = getattr(pre.tspm_state, modality + "_ppb1_state")
        b = getattr(post.tspm_state, modality + "_ppb1_state")
        if b.accepted_step_count == a.accepted_step_count:
            require(a == b, "PPB_NO_UPDATE_INVALID")
            transitions.append(dict(modality=modality, event="NO_UPDATE", slot_id=None,
                                    pre_digest=a.digest(), post_digest=b.digest()))
            continue
        require(b.accepted_step_count == a.accepted_step_count + 1, "PPB_STEP_INVALID")
        selected = [(left, right) for left, right in zip(a.slots, b.slots, strict=True) if left != right]
        require(len(selected) == 1, "PPB_SLOT_TRANSITION_INVALID")
        left, right = selected[0]
        bc = getattr(config.profile.profile, modality + "_config")
        values = getattr(source, modality + "_values")
        require(right.occupied and right.last_selected_step == b.accepted_step_count
                and b.source_clock_id == getattr(source.source, modality).timed_frame.frame.clock_id
                and b.last_source_window_end_tick == getattr(source.source, modality).timed_frame.frame.window_end_tick,
                "PPB_SOURCE_INVALID")
        if not left.occupied or right.support_count == 1:
            event = "CREATED" if not left.occupied else "REPLACED"
            require(right.prototype_values == values and right.support_count == 1, "PPB_CREATED_INVALID")
        else:
            event = "MATCHED"
            expected = tuple((1.0 - bc.update_rate) * p + bc.update_rate * x
                             for p, x in zip(left.prototype_values, values, strict=True))
            require(right.prototype_values == expected
                    and right.support_count == min(bc.stable_after, left.support_count + 1), "PPB_MATCHED_INVALID")
        transitions.append(dict(modality=modality, event=event, slot_id=right.slot_id, support=right.support_count,
            pre_digest=a.digest(), post_digest=b.digest(), full_digest=digest(list(right.prototype_values)),
            masked_digest=digest(list(right.prototype_values[24:] if modality == "auditory" else right.prototype_values[32:]))))
    require((transitions[0]["event"] == "NO_UPDATE") == (transitions[1]["event"] == "NO_UPDATE"), "ATOMIC_PPB_INVALID")
    return transitions


def _formation(event, pre, post, source, config, run_id):
    data = event["formation"]
    receipt = memory.S2JVFormationReceiptV1(**data["receipt"])
    ledger = ledgers.S2JVResourceLedgerV1(**data["ledger"])
    owner = memory.S2JVFormationOwnerSnapshotV1(**data["owner_poststate"])
    prior = memory.S2JVFormationOwnerSnapshotV1(**event["owner_before"])
    result = memory.S2JVFormationResultV1(post, receipt, ledger, owner, data["result_digest"], data["schema"])
    for obj, key in ((receipt, "receipt_digest"), (owner, "owner_state_digest"), (prior, "owner_state_digest")):
        require(getattr(obj, key) == digest(obj.payload_without_digest()), "FORMATION_RECEIPT_INVALID")
    require(data["schema"] == memory.S2JW_COORDINATOR_SCHEMA
            and set(data) == {"receipt", "ledger", "owner_poststate", "result_digest", "schema"}
            and result.result_digest == digest(result.payload_without_digest()), "FORMATION_RESULT_INVALID")
    require(prior.status == "AUTHORIZED" and prior.attempt_count == prior.use_count == 0
            and prior.committed_result_digest is None and prior.failure_code is None
            and owner.status == "CONSUMED" and owner.attempt_count == owner.use_count == 1
            and owner.failure_code is None and owner.committed_result_digest == result.result_digest, "OWNER_LIFECYCLE_INVALID")
    for o in (prior, owner):
        require(o.schema == memory.S2JW_COORDINATOR_SCHEMA and o.owner_id == event["spec"]["event_id"] + "-owner"
                and o.authorization_id == run_id and o.consumption_id == event["spec"]["event_id"] + "-consume"
                and o.authorized_config_digest == config.config_digest and o.authorized_prestate_digest == pre.state_digest
                and o.authorized_input_digest == source.input_digest, "OWNER_BINDING_INVALID")
    require(receipt.schema == memory.S2JW_COORDINATOR_SCHEMA and receipt.config_digest == config.config_digest
            and receipt.owner_prestate_digest == prior.owner_state_digest and receipt.input_digest == source.input_digest
            and receipt.composite_prestate_digest == pre.state_digest and receipt.composite_poststate_digest == post.state_digest
            and receipt.b4_poststate_digest == memory._b4_digest(post.b4_state)
            and receipt.tspm_poststate_digest == post.tspm_state.composite_state_digest
            and receipt.ledger_digest == ledger.ledger_digest, "FORMATION_BINDING_INVALID")
    require(post.generation == pre.generation + 1 and post.parent_state_digest == pre.state_digest
            and post.last_input_digest == source.input_digest
            and post.tspm_state.parent_composite_state_digest == pre.tspm_state.composite_state_digest
            and post.tspm_state.last_exposure_digest == source.tspm_exposure.exposure_digest, "STATE_CHAIN_INVALID")
    relation = digest(dict(schema=memory.S2JW_COORDINATOR_SCHEMA, prestate_digest=pre.state_digest,
                          input_digest=source.input_digest, b4_poststate_digest=receipt.b4_poststate_digest,
                          tspm_poststate_digest=receipt.tspm_poststate_digest, composite_poststate_digest=post.state_digest))
    expected_ledger = ledgers.derive_s2jv_resource_ledger(profile=config.profile, limits=config.ledger_limits,
        operation_id=owner.consumption_id, operation_role="FORMATION", result_digest=relation)
    require(ledger == expected_ledger, "FORMATION_LEDGER_INVALID")
    position = pre.generation % 9
    require(receipt.b4_event == ("B4_APPENDED" if pre.generation < 9 else "B4_EVICTED_AND_APPENDED"), "B4_EVENT_INVALID")
    for i, (left, right) in enumerate(zip(pre.b4_state.entries, post.b4_state.entries, strict=True)):
        if i == position:
            require(right.slot_id == receipt.b4_slot_id and right.occupied and right.values == source.av_values
                    and right.formation_index == post.generation, "B4_SOURCE_INVALID")
        else:
            require(left == right, "B4_UNRELATED_SLOT_CHANGED")
    fast = post.tspm_state.fast_state
    require((fast.auditory_source_clock_id, fast.auditory_last_end_tick,
             fast.visual_source_clock_id, fast.visual_last_end_tick) == (
                source.source.auditory.timed_frame.frame.clock_id, source.source.auditory.timed_frame.frame.window_end_tick,
                source.source.visual.timed_frame.frame.clock_id, source.source.visual.timed_frame.frame.window_end_tick), "FAST_SOURCE_INVALID")
    selected = [(left, right) for left, right in zip(pre.tspm_state.fast_state.slots, fast.slots, strict=True)
                if right.occupied and right.last_selected_step == post.generation]
    require(len(selected) == 1, "FAST_SELECTED_SLOT_INVALID")
    left, right = selected[0]
    fc = config.tspm_config.fast_config
    if right.support_count == 1:
        require(right.auditory_values == source.auditory_values and right.visual_values == source.visual_values
                and right.consolidation_count == 0 and right.last_consolidation_exposure_digest is None, "FAST_CREATED_INVALID")
    else:
        require(left.occupied and right.support_count == min(fc.consolidate_after, left.support_count + 1), "FAST_SUPPORT_INVALID")
        for modality in ("auditory", "visual"):
            before = getattr(left, modality + "_values")
            incoming = getattr(source, modality + "_values")
            expected = tuple((1.0 - fc.update_factor) * p + fc.update_factor * x for p, x in zip(before, incoming, strict=True))
            require(getattr(right, modality + "_values") == expected, "FAST_UPDATE_INVALID")
        require(right.consolidation_count == left.consolidation_count + 1
                and right.last_consolidation_exposure_digest == source.tspm_exposure.exposure_digest, "FAST_CONSOLIDATION_INVALID")
    for old, new in zip(pre.tspm_state.fast_state.slots, fast.slots, strict=True):
        if new.slot_id != right.slot_id:
            require(old == new or (old.occupied and post.generation - old.last_selected_step >= fc.expire_after_exposures
                                   and not new.occupied), "FAST_UNRELATED_SLOT_CHANGED")
    transitions = _ppb_relations(config, pre, post, source)
    require((transitions[0]["event"] != "NO_UPDATE") == (right.support_count >= fc.consolidate_after),
            "CONSOLIDATION_PPB_BINDING_INVALID")
    return transitions


def verify_record(record, *, plan, catalog, config):
    """One pass over recorded events and all arms; predictions are not inputs."""
    _check_digest(record, "record_digest")
    run.check_plan(plan)
    require(record["schema"] == run.SCHEMA and record["plan"] == [asdict(e) for e in plan]
            and record["plan_digest"] == digest(record["plan"])
            and len(run.canonical(record)) <= run.MAX_BYTES, "RECORDING_FORM_INVALID")
    require(record["mode"] in ("MAIN", "NEUTRAL"), "CONFIG_BINDING_INVALID")
    if record["mode"] == "MAIN":
        require(plan == run.EVENTS and catalog == run.load_catalog(), "MAIN_BINDING_INVALID")
    else:
        require(len(plan) <= 5, "NEUTRAL_LIMIT_EXCEEDED")
    require(record["run_id"] == Path(record["output_directory"]).name, "RUN_PATH_INVALID")
    if record["status"] == "NOT_EVALUABLE":
        f = record["failure"]
        require(set(f) == {"phase", "event_index", "completed_events", "event_id", "last_state_digest", "error_class", "code"}
                and type(f["code"]) is str and run.re.fullmatch(r"[A-Z][A-Z0-9_]{0,95}", f["code"]) is not None
                and type(f["error_class"]) is str and run.re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,95}", f["error_class"]) is not None
                and (f["last_state_digest"] is None or kz._valid_digest(f["last_state_digest"])), "FAILURE_FORM_INVALID")
        require(record["code_after"] == {p: run.filehash(run.ROOT / p) if (run.ROOT / p).is_file() else None
                                         for p in record["code_before"]}
                and (not record["code_before"] or set(record["code_before"]) == set(run.source_hashes())),
                "FAILURE_SOURCE_BINDING_INVALID")
        require(record["catalog_digest"] == digest(catalog)
                or (record["catalog_digest"] is None and f["phase"] == "BINDINGS"), "FAILURE_CATALOG_INVALID")
        require(record["config_digest"] == config.config_digest
                or (record["config_digest"] is None and f["phase"] == "BINDINGS"), "CONFIG_BINDING_INVALID")
        require(record["events"] == [] and record["states"] == {} and record["initial_states"] == {}
                and f["phase"] in run.PHASES and type(f["completed_events"]) is int
                and 0 <= f["completed_events"] <= len(plan), "FAILURE_PROGRESS_INVALID")
        n = f["completed_events"]
        require(record["counts"]["events"] == n
                and record["counts"]["formations"] == sum(e.kind == "FORMATION" for e in plan[:n])
                and record["counts"]["cues"] == sum(e.kind == "CUE" for e in plan[:n]), "FAILURE_COUNTS_INVALID")
        require(record["counts"]["arms"] == 4 * record["counts"]["cues"]
                and record["counts"]["slot_visits"] == 20 * record["counts"]["arms"]
                and record["counts"]["formations"] <= record["attempts"]["formations"] <= record["counts"]["formations"] + 1
                and record["counts"]["arms"] <= record["attempts"]["arms"] <= record["counts"]["arms"] + 4,
                "FAILURE_ATTEMPTS_INVALID")
        require((f["event_index"] is None and n == 0 and f["event_id"] is None)
                or (type(f["event_index"]) is int and 0 <= f["event_index"] < len(plan)
                    and f["event_id"] == plan[f["event_index"]].event_id
                    and (f["event_index"] == n or n == len(plan))), "FAILURE_EVENT_INVALID")
        return run.sealed(dict(status="NOT_EVALUABLE", record_digest=record["record_digest"],
                               plan_digest=record["plan_digest"], completed_events=n, read_only=True), "verification_digest")
    require(record["status"] == "RECORDING_COMPLETE" and record["failure"] is None, "TERMINAL_INVALID")
    require(record["config_digest"] == config.config_digest, "CONFIG_BINDING_INVALID")
    require(record["code_before"] == record["code_after"] == run.source_hashes()
            and record["catalog_digest"] == digest(catalog), "SOURCE_BINDING_INVALID")
    states = {key: decode_state(value, config) for key, value in record["states"].items()}
    require(all(key == state.state_digest for key, state in states.items()), "STATE_POOL_INVALID")
    histories = tuple(dict.fromkeys(e.history_id for e in plan))
    require(set(record["initial_states"]) == set(histories), "INITIAL_HISTORY_INVALID")
    current, used = {}, set()
    for history in histories:
        key = record["initial_states"][history]
        s = states[key]
        require(s.generation == 0 and s.parent_state_digest is None and s.last_input_digest is None
                and not any(e.occupied for e in s.b4_state.entries)
                and not any(e.occupied for e in s.tspm_state.fast_state.slots), "INITIAL_STATE_INVALID")
        current[history] = key
        used.add(key)
    require(len(record["events"]) == len(plan), "EVENT_COUNT_INVALID")
    totals = dict(events=0, formations=0, cues=0, arms=0, slot_visits=0, band_differences=0,
                  equality_comparisons=0, retrieval_comparisons=0, logical_operations=0, formation_l1_limit=0)
    transitions, equality = [], []
    for spec, event in zip(plan, record["events"], strict=True):
        _check_digest(event, "event_digest")
        require(event["spec"] == asdict(spec) and event["kind"] == spec.kind
                and event["prestate"] == current[spec.history_id], "EVENT_ORDER_OR_CONTINUITY_INVALID")
        pre, post = states[event["prestate"]], states[event["poststate"]]
        used.update((pre.state_digest, post.state_digest))
        source = _source(spec, event["source"], config, catalog)
        totals["events"] += 1
        if spec.kind == "FORMATION":
            require(event["arms"] == [] and event["cue"] is None, "FORMATION_FORM_INVALID")
            transitions.append(dict(event_id=spec.event_id, transitions=_formation(event, pre, post, source, config, record["run_id"])))
            totals["formations"] += 1
            totals["formation_l1_limit"] += event["formation"]["ledger"]["functional_l1_term_limit"]
        else:
            require(post == pre and event["formation"] is None and event["owner_before"] is None
                    and run.canonical(event["cue"]) == run.canonical(asdict(source)), "READ_ONLY_CUE_INVALID")
            require(len(event["arms"]) == 4, "ARM_COUNT_INVALID")
            decoded = tuple(decode_arm(a) for a in event["arms"])
            require(tuple((a.rule, a.implementation) for a in decoded) == run.ARM_ORDER, "ARM_ORDER_INVALID")
            for arm in decoded:
                independent.verify_arm(arm=arm, config=config, state=pre, cue=source,
                                       band_plan=kz.build_auditory_band_plan_48())
                l = arm.evidence.resource_ledger
                totals["arms"] += 1
                for out, field in (("slot_visits", "total_slot_scan_count"), ("band_differences", "observed_comparison_count"),
                                   ("equality_comparisons", "internal_equality_comparison_count"),
                                   ("retrieval_comparisons", "total_value_comparison_count"), ("logical_operations", "logical_operation_count")):
                    totals[out] += getattr(l, field)
            equality.append(dict(event_id=spec.event_id, reference=independent.compare_technical(decoded[0], decoded[1]),
                                 alternative=independent.compare_technical(decoded[2], decoded[3])))
            totals["cues"] += 1
        current[spec.history_id] = post.state_digest
    require(used == set(states) and totals == record["counts"], "TOTAL_COUNTS_INVALID")
    require(totals["retrieval_comparisons"] <= 27456 and totals["band_differences"] <= 24960
            and totals["equality_comparisons"] <= 2496 and totals["formation_l1_limit"] <= 71040, "RESOURCE_LIMIT_INVALID")
    require(record["attempts"]["formations"] == totals["formations"] and record["attempts"]["arms"] == totals["arms"], "ATTEMPT_COUNT_INVALID")
    if record["mode"] == "MAIN":
        require((totals["formations"], totals["cues"], totals["arms"], totals["slot_visits"], totals["logical_operations"])
                == (20, 13, 52, 1040, 728) and (record["attempts"]["audio"], record["attempts"]["visual"]) == (33, 20), "MAIN_COUNTS_INVALID")
    return run.sealed(dict(status="RECORDING_COMPLETE", record_digest=record["record_digest"], plan_digest=record["plan_digest"],
                           read_only=True, counts=totals, final_states=current, ppb_transitions=transitions,
                           baseline_equality=equality), "verification_digest")


def verify_file_once(recording_path, *, plan, catalog_factory, config, mode):
    """One independent read-only pass; the exclusive pending file prevents retry."""
    path = Path(recording_path).resolve(strict=True)
    require(path.name == "recording.json", "VERIFICATION_PATH_INVALID")
    target = path.with_name("verification.json")
    require(not target.exists(), "VERIFICATION_ALREADY_EXISTS")
    pending = target.with_name(target.name + ".pending")
    with pending.open("xb") as handle:
        before = run.filehash(path)
        try:
            require(path.stat().st_size <= run.MAX_BYTES, "RECORDING_SIZE_EXCEEDED")
            data = path.read_bytes()
            record = json.loads(data)
            require(run.canonical(record) == data and record["mode"] == mode
                    and record["output_directory"] == str(path.parent), "RECORDING_PATH_INVALID")
            result = verify_record(record, plan=plan, catalog=catalog_factory(), config=config)
            require(run.filehash(path) == before, "READ_ONLY_FILE_CHANGED")
        except Exception as error:
            result = dict(status="NOT_EVALUABLE", phase="VERIFICATION", error_class=type(error).__name__,
                          code=error.code if isinstance(error, run.RunError) else "INVALID_RECORDING")
        result = run.sealed({**result, "record_file_sha256": before, "file_unchanged": run.filehash(path) == before}, "report_digest")
        handle.write(run.canonical(result))
        handle.flush()
        run.os.fsync(handle.fileno())
    run.os.link(pending, target)
    pending.unlink()
    return target


def verify_main_once(recording_path):
    path = Path(recording_path).resolve(strict=True)
    require(path.parent.parent == (run.ROOT / "reports/s2ne").resolve(), "VERIFICATION_PATH_INVALID")
    return verify_file_once(path, plan=run.EVENTS, catalog_factory=run.load_catalog, config=run.make_config(), mode="MAIN")


__all__ = ()
