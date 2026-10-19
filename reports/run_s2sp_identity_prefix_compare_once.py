"""One private S2-SP e01-e06 comparison of two fixed PPB update modes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools import _s2jw_default_live_profile as profile_module
from tools import _s2sp_private_memory_compare as core


RUN_ID = "s2sp-identity-prefix-compare-20260919-01"
MAX_BYTES = 262_144
ARMS = {
    "HISTORICAL": core.coordinator.tspm1.PPB_UPDATE_HISTORICAL,
    "IDENTITY_PRESERVING_V1": core.coordinator.tspm1.PPB_UPDATE_IDENTITY_PRESERVING,
}
SEQUENCE = (
    ("e01", "FORMATION"),
    ("e02", "CUE"),
    ("e03", "FORMATION"),
    ("e04", "FORMATION"),
    ("e05", "FORMATION"),
    ("e06", "CUE"),
)


def canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _slow_bank(scan: dict[str, object]) -> dict[str, object]:
    return next(bank for bank in scan["banks"] if bank["bank"] == "VISUAL_SLOW")


def verify(record: dict[str, object]) -> dict[str, object]:
    if record["counts"] != {
        "events_per_arm": 6,
        "formations_per_arm": 4,
        "cues_per_arm": 2,
        "shared_audio_analyses": 4,
        "shared_visual_analyses": 6,
        "field_contacts": 0,
    }:
        raise ValueError("comparison counts differ")
    arms = record["arms"]
    if set(arms) != set(ARMS):
        raise ValueError("comparison arms differ")
    for arm_id, mode in ARMS.items():
        arm = arms[arm_id]
        if arm["ppb_update_mode"] != mode or len(arm["events"]) != 6:
            raise ValueError("arm binding differs")
        formations = [event for event in arm["events"] if event["kind"] == "FORMATION"]
        for expected, event in enumerate(formations):
            evidence = event["transition_evidence"]
            if evidence["formation_generation_before"] != expected or evidence["formation_generation_after"] != expected + 1:
                raise ValueError("formation generations differ")
            if evidence["visual_ppb_action"] != ("ADVANCED" if evidence["consolidation_eligible"] else "NOT_ADVANCED"):
                raise ValueError("PPB action differs")
            payload = dict(evidence)
            evidence_digest = payload.pop("transition_evidence_digest")
            if evidence_digest != digest(payload):
                raise ValueError("transition evidence digest differs")
        for event in arm["events"]:
            if event["kind"] != "CUE":
                continue
            scan = event["scan"]
            if scan["comparison_digest"] != digest({"state_digest": scan["state_digest"], "banks": scan["banks"]}):
                raise ValueError("read-only comparison differs")
    if arms["HISTORICAL"]["input_digests"] != arms["IDENTITY_PRESERVING_V1"]["input_digests"]:
        raise ValueError("arms do not share inputs")
    return {"status": "VERIFIED", "run_id": RUN_ID, "record_digest": record["record_digest"]}


def run_once() -> Path:
    root = Path(__file__).resolve().parents[1]
    output = root / "reports" / RUN_ID
    if output.exists():
        raise RuntimeError("output exists")
    profile = profile_module.build_s2jw_default_live_profile()
    config = core.build_config()
    sources = core.Sources(profile)
    states = {arm_id: core.coordinator.initial_s2jv_composite_state(config) for arm_id in ARMS}
    events = {arm_id: [] for arm_id in ARMS}
    input_digests = {arm_id: [] for arm_id in ARMS}
    formation_ordinal = 0
    for ordinal, (event_id, kind) in enumerate(SEQUENCE):
        if kind == "FORMATION":
            pair, values = sources.formation(event_id=event_id, ordinal=formation_ordinal, cells=core.TARGET)
            for arm_id, mode in ARMS.items():
                result = core.form(
                    config=config,
                    state=states[arm_id],
                    pair=pair,
                    event_id=event_id,
                    run_id=f"{RUN_ID}.{arm_id.lower()}",
                    ppb_update_mode=mode,
                )
                evidence = core.transition_evidence(prestate=states[arm_id], result=result)
                states[arm_id] = result.poststate
                input_digests[arm_id].append(pair.pairing_digest)
                events[arm_id].append({
                    "event_id": event_id,
                    "kind": kind,
                    "pairing_digest": pair.pairing_digest,
                    "visual_values_digest": digest(list(values)),
                    "state_digest": result.poststate.state_digest,
                    "transition_evidence": evidence,
                })
            formation_ordinal += 1
        else:
            cue = sources.cue(ordinal=ordinal, cells=core.TARGET)
            for arm_id in ARMS:
                scan = core.compare_state(state=states[arm_id], cue_values=cue)
                input_digests[arm_id].append(digest(list(cue)))
                events[arm_id].append({
                    "event_id": event_id,
                    "kind": kind,
                    "cue_digest": digest(list(cue)),
                    "state_digest": states[arm_id].state_digest,
                    "scan": scan,
                })
    arms = {
        arm_id: {
            "ppb_update_mode": mode,
            "input_digests": input_digests[arm_id],
            "events": events[arm_id],
        }
        for arm_id, mode in ARMS.items()
    }
    record = {
        "schema": "s2sp.identity-prefix-compare.v1",
        "run_id": RUN_ID,
        "status": "RECORDING_COMPLETE",
        "config_digest": config.config_digest,
        "arms": arms,
        "counts": {
            "events_per_arm": 6,
            "formations_per_arm": 4,
            "cues_per_arm": 2,
            "shared_audio_analyses": sources.audio_analyses,
            "shared_visual_analyses": sources.visual_analyses,
            "field_contacts": 0,
        },
    }
    record["record_digest"] = digest(record)
    verification = verify(record)
    evaluation = {
        "run_id": RUN_ID,
        "e06": {
            arm_id: {
                "slow_candidate_ids": _slow_bank(arms[arm_id]["events"][-1]["scan"])["candidate_ids"],
                "exact_candidate_ids": _slow_bank(arms[arm_id]["events"][-1]["scan"])["exact_baseline_candidate_ids"],
                "shift_status": _slow_bank(arms[arm_id]["events"][-1]["scan"])["hint_status"],
            }
            for arm_id in ARMS
        },
    }
    payloads = {
        "record.json": canonical(record),
        "verification.json": canonical(verification),
        "evaluation.json": canonical(evaluation),
    }
    if sum(len(payload) for payload in payloads.values()) > MAX_BYTES:
        raise RuntimeError("comparison budget exceeded")
    output.mkdir(parents=True)
    for name, payload in payloads.items():
        (output / name).write_bytes(payload)
    return output


if __name__ == "__main__":
    print(run_once())
