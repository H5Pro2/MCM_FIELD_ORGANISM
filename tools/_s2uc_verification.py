"""Independent prefix verifier for complete S2-UC neutral records."""
from __future__ import annotations
from tools import _s2tu_retained_trace as tu
from tools import _s2ub_candidate_verification as candidate

def _materialization(receipt, endpoint, profile):
    if receipt is None:
        return
    required = {"pcm_sha256", "payload_bytes", "raw_state_digest", "projection_digest", "source_values_digest", "projection_binding", "subnormal_band_indices", "underflow_band_indices"}
    if type(receipt) is not dict or set(receipt) != required or receipt["pcm_sha256"] != endpoint["pcm_sha256"] or receipt["payload_bytes"] != endpoint["pcm_byte_count"]:
        raise ValueError("MATERIALIZATION_BINDING_INVALID")
    if any(type(receipt[key]) is not str or len(receipt[key]) != 64 for key in ("raw_state_digest", "projection_digest", "source_values_digest")):
        raise ValueError("MATERIALIZATION_DIGEST_INVALID")
    binding = receipt["projection_binding"]
    if type(binding) is not dict or binding.get("profile_digest") != profile:
        raise ValueError("MATERIALIZATION_PROFILE_INVALID")

def _frame(row, profile):
    return tu.Frame(tuple(float.fromhex(v) for v in row["values_hex"]), profile, "verify", row["segment"], row["ordinal"])

def _frames(left, right):
    return tuple((f.values, f.ordinal, f.segment) for f in left) == tuple((f.values, f.ordinal, f.segment) for f in right)

def _state(snapshot, retained, candidate_state, profile, owner):
    if set(snapshot) != {"profile", "owner", "closed", "forming", "candidate", "retained", "hints"}:
        return False
    if snapshot["profile"] != profile or snapshot["owner"] != owner or snapshot["closed"] is not False:
        return False
    if snapshot["forming"] != () or snapshot["hints"] != ():
        return False
    actual_r, actual_c = snapshot["retained"], snapshot["candidate"]
    if (actual_r is None) != (retained is None) or (actual_c is None) != (candidate_state is None): return False
    if retained is not None and (actual_r[0] != retained[0] or not _frames(actual_r[1], retained[1])): return False
    return candidate_state is None or (actual_c[0] == candidate_state[0] and _frames(actual_c[1], candidate_state[1]))

def _immediate_state(snapshot, retained, profile, owner):
    if set(snapshot) != {"profile", "owner", "closed", "forming", "retained", "hints"}:
        return False
    if snapshot["profile"] != profile or snapshot["owner"] != owner or snapshot["closed"] is not False:
        return False
    actual = snapshot["retained"]
    if (actual is None) != (not retained): return False
    if actual is not None:
        expected = tuple((generation, tuple((frame.values, frame.ordinal, frame.segment) for frame in frames)) for generation, frames in retained)
        observed = tuple((generation, tuple((frame.values, frame.ordinal, frame.segment) for frame in frames)) for generation, frames in actual)
        if observed != expected: return False
    return snapshot["forming"] == () and snapshot["hints"] == ()

def _verify_prefix(story, manifest):
    """Independently replay every completed event available in one story record."""
    expected = [row for row in manifest["events"] if row["story"] == story["story"]]
    events = story.get("events")
    if type(events) is not list or len(events) > len(expected): raise ValueError("PREFIX_EVENT_COUNT_INVALID")
    retained=[]; generation=0; forming=[]; groups=[]; hints={}; transition=0
    hint_rows = story.get("hints", []); hint_receipts={row["ordinal"]:row for row in hint_rows}
    if len(hint_rows) != len(hint_receipts): raise ValueError("DUPLICATE_HINT_RECEIPT_INVALID")
    for bound, observed in zip(expected, events):
        if any(observed.get(k) != bound.get(k) for k in ("ordinal","kind","segment")): raise ValueError("EVENT_BINDING_INVALID")
        if bound["kind"] == "CLOSE":
            group=tuple(forming); forming=[]
            if len(group)!=4: raise ValueError("FORMATION_INVALID")
            same=[x for x in retained if tuple(f.values for f in x[1])==tuple(f.values for f in group)]
            if len(same)==1: immediate={"action":"TRACE_CONFIRMED","generation":same[0][0],"evicted":None}
            elif not same:
                generation+=1; evicted=retained[0][0] if len(retained)==2 else None; retained=(retained+[(generation,group)])[-2:]
                immediate={"action":"TRACE_RETAINED","generation":generation,"evicted":evicted}
            else: raise ValueError("IMMEDIATE_AMBIGUOUS_INVALID")
            groups.append(group); direct=candidate.replay(tuple(groups))
            receipts=story.get("transitions", [])
            if transition >= len(receipts): raise ValueError("TRANSITION_RECEIPT_INVALID")
            receipt=receipts[transition]; transition+=1
            if receipt["immediate"]!=immediate or receipt["candidate"]!=direct["transitions"][-1] or receipt["immediate_inventory"]!=tuple(x[0] for x in retained) or receipt["candidate_inventory"]!=direct["inventory"]: raise ValueError("TRANSITION_RECEIPT_INVALID")
            continue
        endpoint=bound["endpoint"]
        if observed.get("source_id") != endpoint["source_id"] or len(observed.get("values_hex", [])) != 48: raise ValueError("ENDPOINT_BINDING_INVALID")
        _materialization(observed.get("materialization"), endpoint, manifest["profile"])
        frame=_frame(observed, manifest["profile"])
        if bound["kind"] == "FORMATION": forming.append(frame); continue
        hint=hints.setdefault(bound["segment"], []); hint.append(frame)
        if len(hint)==2:
            matches=[(item[0], offset) for item in retained for offset in range(3) if item[1][offset].values==hint[0].values and item[1][offset+1].values==hint[1].values]
            immediate={"decision":"TRACE_MATCH" if len(matches)==1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE" if matches else "ABSTAIN_NO_RETAINED_TRACE","matches":matches}
            direct=candidate.replay(tuple(groups)); candidate_hint=candidate.hint(direct["retained"], tuple(hint)); receipt=hint_receipts.get(bound["ordinal"])
            if receipt is None or receipt["immediate"] != immediate or receipt["candidate"] != candidate_hint: raise ValueError("HINT_RECEIPT_INVALID")
            immediate_owner=f"s2uc-{story['story']}-tw"; candidate_owner=f"s2uc-{story['story']}-candidate"
            if not _immediate_state(receipt["immediate_before"], retained, manifest["profile"], immediate_owner) or not _immediate_state(receipt["immediate_after"], retained, manifest["profile"], immediate_owner): raise ValueError("IMMEDIATE_STATE_INVALID")
            if not _state(receipt["candidate_before"], direct["retained"], direct["candidate"], manifest["profile"], candidate_owner) or not _state(receipt["candidate_after"], direct["retained"], direct["candidate"], manifest["profile"], candidate_owner): raise ValueError("CANDIDATE_STATE_INVALID")
            hints[bound["segment"]]=[]
    if transition != len(story.get("transitions", [])): raise ValueError("TRANSITION_RECEIPT_INVALID")
    return expected, events

def verify_failure(record: dict[str, object], manifest: dict[str, object]) -> dict[str, object]:
    """Verify a terminated prefix without interpreting it as a functional result."""
    if record.get("status") != "NOT_EVALUABLE" or record.get("manifest_digest") != manifest.get("binding_digest"):
        raise ValueError("FAILURE_STATUS_OR_MANIFEST_INVALID")
    stories = record.get("stories")
    failure = record.get("failure")
    if type(stories) is not list or not stories or type(failure) is not dict:
        raise ValueError("FAILURE_SHAPE_INVALID")
    names = [row.get("story") for row in stories]
    expected_names = ["g1", "g2", "g3"][:len(stories)]
    if names != expected_names or stories[-1].get("status") != "NOT_EVALUABLE" or any(row.get("status") != "COMPLETE" for row in stories[:-1]):
        raise ValueError("FAILURE_STORY_SEQUENCE_INVALID")
    if record.get("not_executed") != ["g1", "g2", "g3"][len(stories):] or record.get("terminal") != {"status":"CLOSED_AFTER_FAILURE", "started_stories":names, "not_executed":record["not_executed"]}:
        raise ValueError("FAILURE_TERMINAL_INVALID")
    failed = stories[-1]
    for story in stories:
        expected_story, observed_story = _verify_prefix(story, manifest)
        if story is not failed and len(observed_story) != len(expected_story): raise ValueError("FAILURE_COMPLETED_STORY_INVALID")
    expected = [row for row in manifest["events"] if row["story"] == failed["story"]]
    observed = failed.get("events")
    closure_failure = failure.get("code") == "OWNER_CLOSE_INVALID"
    if type(observed) is not list or (not closure_failure and len(observed) >= len(expected)) or (closure_failure and len(observed) != len(expected)):
        raise ValueError("FAILURE_PREFIX_INVALID")
    for bound, row in zip(expected, observed):
        if any(row.get(key) != bound.get(key) for key in ("ordinal", "kind", "segment")):
            raise ValueError("FAILURE_EVENT_BINDING_INVALID")
    attempted = None if closure_failure else expected[len(observed)]
    progress = failure.get("progress")
    if type(progress) is not dict or progress.get("story") != failed["story"]:
        raise ValueError("FAILURE_PROGRESS_INVALID")
    if closure_failure:
        if progress.get("phase") != "OWNER_CLOSE" or progress.get("completed") != len(expected): raise ValueError("FAILURE_CLOSE_PROGRESS_INVALID")
    elif any(progress.get(key) != attempted.get(key) for key in ("ordinal", "story_ordinal")):
        raise ValueError("FAILURE_PROGRESS_INVALID")
    counts = progress.get("counts")
    if type(counts) is not dict or counts.get("materialization_attempts", 0) < counts.get("materializations", 0):
        raise ValueError("FAILURE_COUNTER_INVALID")
    materialized = sum(row.get("kind") != "CLOSE" for story in stories for row in story.get("events", []))
    if counts.get("materializations") not in (materialized, materialized + 1):
        raise ValueError("FAILURE_MATERIALIZATION_PROGRESS_INVALID")
    if not closure_failure and attempted["kind"] != "CLOSE" and counts.get("materialization_attempts") not in (counts.get("materializations"), counts.get("materializations") + 1):
        raise ValueError("FAILURE_ATTEMPT_PROGRESS_INVALID")
    completed_calls = sum(1 for story in stories for row in story.get("events", []))
    immediate_calls = counts.get("immediate_calls")
    candidate_calls = counts.get("candidate_calls")
    if (type(immediate_calls) is not int or type(candidate_calls) is not int
            or not (completed_calls <= candidate_calls <= immediate_calls <= completed_calls + 1)):
        raise ValueError("FAILURE_ARM_PROGRESS_INVALID")
    closes = failed.get("owner_closes")
    if set(closes or {}) != {"immediate", "candidate"} or record.get("counts", {}).get("owner_closes") != 2 * len(stories):
        raise ValueError("FAILURE_OWNER_CLOSE_INVALID")
    return {"status":"VERIFIED_FAILURE", "story":failed["story"], "failed_ordinal":None if attempted is None else attempted["ordinal"], "phase":"OWNER_CLOSE" if closure_failure else "EVENT"}

def verify(record: dict[str, object], manifest: dict[str, object], *, require_source_completion: bool = False) -> dict[str, object]:
    if record.get("status") != "COMPLETE" or record.get("manifest_digest") != manifest.get("binding_digest"):
        raise ValueError("STATUS_OR_MANIFEST_INVALID")
    if record.get("terminal") != {"status":"CLOSED","started_stories":["g1","g2","g3"],"not_executed":[]}:
        raise ValueError("TERMINAL_INVALID")
    stories = record.get("stories")
    if type(stories) is not list or [r.get("story") for r in stories] != ["g1","g2","g3"] or any(r.get("status") != "COMPLETE" for r in stories):
        raise ValueError("STORY_SEQUENCE_INVALID")
    total = {"materializations":0,"formations":0,"hint_frames":0,"segment_closes":0,"immediate_calls":0,"candidate_calls":0}
    for story in stories:
        expected = [row for row in manifest["events"] if row["story"] == story["story"]]
        events = story.get("events")
        if type(events) is not list or len(events) != len(expected): raise ValueError("EVENT_COUNT_INVALID")
        retained=[]; generation=0; forming=[]; groups=[]; hints={}; transition=0
        hint_rows = story.get("hints", [])
        hint_receipts={r["ordinal"]:r for r in hint_rows}
        if len(hint_rows) != len(hint_receipts): raise ValueError("DUPLICATE_HINT_RECEIPT_INVALID")
        for bound, observed in zip(expected, events):
            if any(observed.get(k) != bound.get(k) for k in ("ordinal","kind","segment")): raise ValueError("EVENT_BINDING_INVALID")
            if bound["kind"] == "CLOSE":
                group=tuple(forming); forming=[]
                if len(group)!=4: raise ValueError("FORMATION_INVALID")
                same=[x for x in retained if tuple(f.values for f in x[1])==tuple(f.values for f in group)]
                if len(same)==1: immediate={"action":"TRACE_CONFIRMED","generation":same[0][0],"evicted":None}
                elif not same:
                    generation+=1; evicted=retained[0][0] if len(retained)==2 else None; retained=(retained+[(generation,group)])[-2:]
                    immediate={"action":"TRACE_RETAINED","generation":generation,"evicted":evicted}
                else: raise ValueError("IMMEDIATE_AMBIGUOUS_INVALID")
                groups.append(group); direct=candidate.replay(tuple(groups)); receipt=story["transitions"][transition]; transition+=1
                if receipt["immediate"]!=immediate or receipt["candidate"]!=direct["transitions"][-1] or receipt["immediate_inventory"]!=tuple(x[0] for x in retained) or receipt["candidate_inventory"]!=direct["inventory"]: raise ValueError("TRANSITION_RECEIPT_INVALID")
                for k in ("segment_closes","immediate_calls","candidate_calls"): total[k]+=1
                continue
            endpoint=bound.get("endpoint")
            if observed.get("source_id")!=endpoint["source_id"] or len(observed.get("values_hex",[]))!=48: raise ValueError("ENDPOINT_BINDING_INVALID")
            _materialization(observed.get("materialization"), endpoint, manifest["profile"])
            frame=_frame(observed,manifest["profile"]); total["materializations"]+=1; total["immediate_calls"]+=1; total["candidate_calls"]+=1
            if bound["kind"]=="FORMATION": forming.append(frame); total["formations"]+=1; continue
            hint=hints.setdefault(bound["segment"],[]); hint.append(frame); total["hint_frames"]+=1
            if len(hint)==2:
                matches=[(x[0],i) for x in retained for i in range(3) if x[1][i].values==hint[0].values and x[1][i+1].values==hint[1].values]
                immediate={"decision":"TRACE_MATCH" if len(matches)==1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE" if matches else "ABSTAIN_NO_RETAINED_TRACE","matches":matches}
                direct=candidate.replay(tuple(groups)); candidate_hint=candidate.hint(direct["retained"],tuple(hint)); receipt=hint_receipts.get(bound["ordinal"])
                if receipt is None or receipt["immediate"]!=immediate or receipt["candidate"]!=candidate_hint: raise ValueError("HINT_RECEIPT_INVALID")
                immediate_owner = f"s2uc-{story['story']}-tw"; candidate_owner = f"s2uc-{story['story']}-candidate"
                if not _immediate_state(receipt["immediate_before"], retained, manifest["profile"], immediate_owner) or not _immediate_state(receipt["immediate_after"], retained, manifest["profile"], immediate_owner): raise ValueError("IMMEDIATE_STATE_INVALID")
                if not _state(receipt["candidate_before"],direct["retained"],direct["candidate"], manifest["profile"], candidate_owner) or not _state(receipt["candidate_after"],direct["retained"],direct["candidate"], manifest["profile"], candidate_owner): raise ValueError("CANDIDATE_STATE_INVALID")
                hints[bound["segment"]]=[]
        if transition!=len(story["transitions"]) or story.get("completed")!=len(expected): raise ValueError("STORY_COMPLETION_INVALID")
        if story.get("owner_closes") != {"immediate":{"closed":True},"candidate":{"closed":True}} or not story["closed"]["immediate"]["closed"] or not story["closed"]["candidate"]["closed"]: raise ValueError("OWNER_CLOSE_INVALID")
    if any(record["counts"].get(k)!=v for k,v in total.items()): raise ValueError("COUNTER_INVALID")
    completion = record.get("source_completion")
    expected = total["materializations"]
    if (require_source_completion and completion is None) or (completion is not None and (type(completion) is not dict or completion.get("attempts") != expected or completion.get("successes") != expected
                                   or completion.get("counters", {}).get("pcm_hashes") != expected
                                   or completion.get("counters", {}).get("audio_analyses") != expected
                                   or completion.get("counters", {}).get("nj_projections") != expected)):
        raise ValueError("SOURCE_COMPLETION_INVALID")
    return {"status":"VERIFIED","stories":["g1","g2","g3"]}
