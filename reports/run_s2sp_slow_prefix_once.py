"""One diagnostic S2-SP prefix through e06, with no replay or public retrieval."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools import _s2jw_default_live_profile as profile_module
from tools import _s2sp_private_memory_compare as core


RUN_ID = "s2sp-slow-prefix-diagnostic-20260919-01"
MAX_BYTES = 262_144


def canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def verify(record: dict[str, object]) -> dict[str, object]:
    transitions = [event for event in record["events"] if event["kind"] == "FORMATION"]
    if len(transitions) != 4 or record["counts"] != {"events": 6, "formations": 4, "cues": 2, "audio_analyses": 4, "visual_analyses": 6, "field_contacts": 0}:
        raise ValueError("diagnostic count differs")
    for expected, event in enumerate(transitions):
        evidence = event["transition_evidence"]
        if evidence["formation_generation_before"] != expected or evidence["formation_generation_after"] != expected + 1:
            raise ValueError("generation differs")
        if evidence["visual_ppb_action"] != ("ADVANCED" if evidence["consolidation_eligible"] else "NOT_ADVANCED"):
            raise ValueError("ppb action differs")
        if evidence["consolidation_status"] != ("COMMITTED" if evidence["consolidation_eligible"] else "NOT_ELIGIBLE"):
            raise ValueError("consolidation differs")
        if evidence["fast_generation"] is not None or evidence["fast_generation_status"] != "NOT_AVAILABLE_IN_NATIVE_SLOT":
            raise ValueError("unavailable generation differs")
        payload = dict(evidence)
        receipt = payload.pop("transition_evidence_digest")
        if receipt != digest(payload):
            raise ValueError("evidence digest differs")
    before = hashlib.sha256(canonical(record)).hexdigest()
    return {"status": "VERIFIED", "run_id": RUN_ID, "record_digest": record["record_digest"], "record_sha256": before}


def run_once() -> Path:
    root = Path(__file__).resolve().parents[1]
    output = root / "reports" / RUN_ID
    if output.exists():
        raise RuntimeError("output exists")
    profile = profile_module.build_s2jw_default_live_profile()
    config = core.build_config()
    sources = core.Sources(profile)
    state = core.coordinator.initial_s2jv_composite_state(config)
    events = []
    for event_id, kind, cells in (("e01", "FORMATION", core.TARGET), ("e02", "CUE", core.TARGET), ("e03", "FORMATION", core.TARGET), ("e04", "FORMATION", core.TARGET), ("e05", "FORMATION", core.TARGET), ("e06", "CUE", core.TARGET)):
        ordinal = len(events)
        if kind == "FORMATION":
            formation_ordinal = sum(item["kind"] == "FORMATION" for item in events)
            pair, values = sources.formation(event_id=event_id, ordinal=formation_ordinal, cells=cells)
            result = core.form(config=config, state=state, pair=pair, event_id=event_id, run_id=RUN_ID)
            evidence = core.transition_evidence(prestate=state, result=result)
            state = result.poststate
            events.append({"event_id": event_id, "kind": kind, "pairing_digest": pair.pairing_digest, "visual_values_digest": digest(list(values)), "state_digest": state.state_digest, "transition_evidence": evidence})
        else:
            cue = sources.cue(ordinal=ordinal, cells=cells)
            scan = core.compare_state(state=state, cue_values=cue)
            events.append({"event_id": event_id, "kind": kind, "state_digest": state.state_digest, "cue_digest": digest(list(cue)), "scan": scan})
    record = {"schema": "s2sp.slow-prefix-diagnostic.v1", "run_id": RUN_ID, "status": "RECORDING_COMPLETE", "config_digest": config.config_digest, "events": events, "counts": {"events": 6, "formations": 4, "cues": 2, "audio_analyses": sources.audio_analyses, "visual_analyses": sources.visual_analyses, "field_contacts": 0}}
    record["record_digest"] = digest(record)
    verification = verify(record)
    data = {"record.json": canonical(record), "verification.json": canonical(verification)}
    if sum(len(value) for value in data.values()) > MAX_BYTES:
        raise RuntimeError("diagnostic budget exceeded")
    output.mkdir(parents=True)
    for name, value in data.items():
        (output / name).write_bytes(value)
    return output


if __name__ == "__main__":
    print(run_once())
