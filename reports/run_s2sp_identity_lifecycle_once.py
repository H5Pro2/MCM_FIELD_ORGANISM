"""One private S2-SP lifecycle comparison without shift-hint selection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools import _s2jw_default_live_profile as profile_module
from tools import _s2sp_private_memory_compare as core


RUN_ID = "s2sp-identity-lifecycle-20260919-01"
MAX_BYTES = 262_144
ARMS = {
    "HISTORICAL": core.coordinator.tspm1.PPB_UPDATE_HISTORICAL,
    "IDENTITY_PRESERVING_V1": core.coordinator.tspm1.PPB_UPDATE_IDENTITY_PRESERVING,
}
SEQUENCE = (
    ("e01", "FORMATION", core.TARGET, "base"),
    ("e02", "FORMATION", core.TARGET, "base"),
    ("e03", "FORMATION", core.TARGET, "base"),
    ("e04", "FORMATION", core.TARGET, "base"),
    ("e05", "CUE", core.TARGET, None),
    ("e06", "FORMATION", core.COMPETITOR_1, "tone-0430"),
    ("e07", "FORMATION", core.COMPETITOR_1_VARIANT, "tone-0430"),
    ("e08", "FORMATION", core.COMPETITOR_2, "tone-1710"),
    ("e09", "FORMATION", core.COMPETITOR_2, "tone-1710"),
    ("e10", "FORMATION", core.COMPETITOR_3, "tone-4300"),
    ("e11", "FORMATION", core.COMPETITOR_3, "tone-4300"),
    ("e12", "FORMATION", core.COMPETITOR_4, "tone-9000"),
    ("e13", "CUE", core.TARGET, None),
    ("e14", "FORMATION", core.COMPETITOR_4, "tone-9000"),
    ("e15", "CUE", core.TARGET, None),
    ("e16", "CUE", core.COMPETITOR_1_VARIANT, None),
)


def canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def bank(scan: dict[str, object], bank_id: str) -> dict[str, object]:
    return next(item for item in scan["banks"] if item["bank"] == bank_id)


def _variation_evidence(prestate, result, input_values: tuple[float, ...]) -> dict[str, object] | None:
    before_step = prestate.tspm_state.visual_ppb1_state.accepted_step_count
    after_state = result.poststate.tspm_state.visual_ppb1_state
    if after_state.accepted_step_count != before_step + 1:
        return None
    selected = next(slot for slot in after_state.slots if slot.occupied and slot.last_selected_step == after_state.accepted_step_count)
    previous = next((slot for slot in prestate.tspm_state.visual_ppb1_state.slots if slot.slot_id == selected.slot_id), None)
    if previous is None or not previous.occupied:
        return None
    changed = [
        index for index, (old, current) in enumerate(zip(previous.prototype_values, input_values, strict=True))
        if old != current
    ]
    payload = {
        "slot_id": selected.slot_id,
        "changed_indices": changed,
        "changed_formula_values": [
            (1.0 - 0.05) * previous.prototype_values[index] + 0.05 * input_values[index]
            for index in changed
        ],
        "stored_values": [selected.prototype_values[index] for index in changed],
    }
    return {**payload, "variation_evidence_digest": digest(payload)}


def verify(record: dict[str, object]) -> dict[str, object]:
    expected_counts = {
        "events_per_arm": 16,
        "formations_per_arm": 12,
        "cues_per_arm": 4,
        "shared_audio_analyses": 12,
        "shared_visual_analyses": 16,
        "field_contacts": 0,
    }
    if record["counts"] != expected_counts or set(record["arms"]) != set(ARMS):
        raise ValueError("lifecycle envelope differs")
    for arm_id, mode in ARMS.items():
        arm = record["arms"][arm_id]
        if arm["ppb_update_mode"] != mode or len(arm["events"]) != 16:
            raise ValueError("arm binding differs")
        for event in arm["events"]:
            if event["kind"] == "CUE":
                scan = event["scan"]
                if scan["comparison_digest"] != digest({"state_digest": scan["state_digest"], "banks": scan["banks"]}):
                    raise ValueError("read-only scan differs")
            else:
                evidence = dict(event["transition_evidence"])
                evidence_digest = evidence.pop("transition_evidence_digest")
                if evidence_digest != digest(evidence):
                    raise ValueError("transition evidence differs")
                variation = event.get("variation_evidence")
                if variation is not None:
                    payload = dict(variation)
                    variation_digest = payload.pop("variation_evidence_digest")
                    if variation_digest != digest(payload) or payload["stored_values"] != payload["changed_formula_values"]:
                        raise ValueError("variation formula differs")
    if record["arms"]["HISTORICAL"]["input_digests"] != record["arms"]["IDENTITY_PRESERVING_V1"]["input_digests"]:
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
    inputs = {arm_id: [] for arm_id in ARMS}
    formation_ordinal = 0
    for ordinal, (event_id, kind, cells, audio_mode) in enumerate(SEQUENCE):
        if kind == "FORMATION":
            pair, visual_values = sources.formation(event_id=event_id, ordinal=formation_ordinal, cells=cells, audio_mode=audio_mode)
            for arm_id, mode in ARMS.items():
                result = core.form(config=config, state=states[arm_id], pair=pair, event_id=event_id, run_id=f"{RUN_ID}.{arm_id.lower()}", ppb_update_mode=mode)
                variation = _variation_evidence(states[arm_id], result, visual_values) if event_id == "e07" else None
                evidence = core.transition_evidence(prestate=states[arm_id], result=result)
                states[arm_id] = result.poststate
                inputs[arm_id].append(pair.pairing_digest)
                events[arm_id].append({
                    "event_id": event_id, "kind": kind, "pairing_digest": pair.pairing_digest,
                    "visual_values_digest": digest(list(visual_values)), "state_digest": result.poststate.state_digest,
                    "transition_evidence": evidence, "variation_evidence": variation,
                })
            formation_ordinal += 1
        else:
            cue = sources.cue(ordinal=ordinal, cells=cells)
            for arm_id in ARMS:
                scan = core.compare_state(state=states[arm_id], cue_values=cue)
                inputs[arm_id].append(digest(list(cue)))
                events[arm_id].append({"event_id": event_id, "kind": kind, "cue_digest": digest(list(cue)), "state_digest": states[arm_id].state_digest, "scan": scan})
    arms = {arm_id: {"ppb_update_mode": mode, "input_digests": inputs[arm_id], "events": events[arm_id]} for arm_id, mode in ARMS.items()}
    record = {
        "schema": "s2sp.identity-lifecycle.v1", "run_id": RUN_ID,
        "status": "RECORDING_COMPLETE", "config_digest": config.config_digest,
        "arms": arms,
        "counts": {"events_per_arm": 16, "formations_per_arm": 12, "cues_per_arm": 4, "shared_audio_analyses": sources.audio_analyses, "shared_visual_analyses": sources.visual_analyses, "field_contacts": 0},
    }
    record["record_digest"] = digest(record)
    verification = verify(record)
    evaluation = {
        "run_id": RUN_ID,
        "cues": {
            arm_id: {
                event["event_id"]: {
                    bank_id: {"candidate_ids": bank(event["scan"], bank_id)["candidate_ids"], "exact_candidate_ids": bank(event["scan"], bank_id)["exact_baseline_candidate_ids"]}
                    for bank_id in ("B4", "FAST", "VISUAL_SLOW")
                }
                for event in arms[arm_id]["events"] if event["kind"] == "CUE"
            }
            for arm_id in ARMS
        },
    }
    payloads = {"record.json": canonical(record), "verification.json": canonical(verification), "evaluation.json": canonical(evaluation)}
    if sum(len(value) for value in payloads.values()) > MAX_BYTES:
        raise RuntimeError("lifecycle budget exceeded")
    output.mkdir(parents=True)
    for name, value in payloads.items():
        (output / name).write_bytes(value)
    return output


if __name__ == "__main__":
    print(run_once())
