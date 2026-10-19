"""One bounded S2TW two-arm materialization run."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools import _s2ts_temporal_trace_run as source
from tools import _s2tu_retained_trace as tu
from tools import _s2tw_exact_confirmation as confirmation
from tools import _s2tw_source_schedule as schedule


RUN_ID = "s2tw-exact-confirmation-real-20260919-01"
MAIN_GATE = False
USED = False
RECORD_LIMIT = 262_144


def canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def run_once(out: Path) -> dict[str, object]:
    global MAIN_GATE, USED
    if not MAIN_GATE or USED or out.exists():
        raise ValueError("RUN_NOT_AUTHORIZED")
    USED = True; phase = "BINDING"; progress = {"ordinal": 0, "source_id": None}
    counts = dict(audio=0, nj=0, endpoints=0, formations=0, hints=0, segment_closes=0, owner_closes=0)
    try:
        bound = schedule.binding(); sources, plan = source.source_rows(); profile = bound["profile"]
        import numpy as np
        from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        from tools import _s2nj_private_auditory_output_projection as nj
        receptor = LogSpectralReceptor(LogSpectralConfig(**plan["profiles"]["raw"]["config"]))
        baseline = tu.RetainedTraceStore(profile, "s2tw-baseline")
        candidate = confirmation.ExactConfirmationStore(profile, "s2tw-confirm")
        endpoints, transitions, decisions = [], [], []
        for event in bound["events"]:
            progress = {"ordinal": event["ordinal"], "source_id": event["source_id"]}
            if event["kind"] == "SEGMENT_CLOSE":
                phase = "SEGMENT_CLOSE"; base = baseline.close_segment(event["segment"]); confirm = candidate.close_segment(event["segment"])
                transitions.append(dict(ordinal=event["ordinal"], baseline=base, confirmation=confirm,
                                        baseline_inventory=list(baseline.generations), confirmation_inventory=list(candidate.inventory)))
                counts["segment_closes"] += 1; continue
            phase = "PCM"; item = sources[event["source_id"]]
            payload = source.nu.pcm_window(source.nu.WindowSpec(int(item["stream_id"][1:]), int(item["window_ordinal"])))
            if hashlib.sha256(payload).hexdigest() != item["pcm_sha256"]: raise ValueError("PCM_HASH_INVALID")
            phase = "RECEPTOR"; raw = receptor.analyze(np.frombuffer(payload, dtype="<f4")); counts["audio"] += 1
            state = AuditoryReceptorState("auditory", nj.RAW_GEOMETRY, int(item["nj_snapshot_index"]), int(item["window_start_sample"]), int(item["window_end_sample"]), receptor.channel_ids, raw, AuditoryReceptorContact.ACTIVE_ENERGY if any(raw) else AuditoryReceptorContact.ACTIVE_ZERO)
            phase = "NJ"; half = nj.project_auditory_half_v1(state, config=receptor.config, source_profile_digest=nj.RAW_PROFILE_DIGEST); counts["nj"] += 1; counts["endpoints"] += 1
            values = [value.hex() for value in half.values]
            endpoints.append(dict(ordinal=event["ordinal"], source_id=event["source_id"], pcm_sha256=item["pcm_sha256"], payload_hash_checked=True, values=values, value_digest=digest(values)))
            base_frame = tu.Frame(tuple(half.values), profile, "s2tw-baseline", event["segment"], event["ordinal"])
            confirm_frame = tu.Frame(tuple(half.values), profile, "s2tw-confirm", event["segment"], event["ordinal"])
            base_result = baseline.form(base_frame) if event["kind"] == "FORMATION" else baseline.hint(base_frame)
            confirm_result = candidate.form(confirm_frame) if event["kind"] == "FORMATION" else candidate.hint(confirm_frame)
            if event["kind"] == "FORMATION": counts["formations"] += 1
            else:
                counts["hints"] += 1
                if base_result is not None: decisions.append(dict(ordinal=event["ordinal"], baseline=base_result, confirmation=confirm_result))
        phase = "OWNER_CLOSE"; before = dict(baseline=list(baseline.generations), confirmation=list(candidate.inventory))
        baseline.close_owner(); candidate.close_owner(); counts["owner_closes"] = 2
        record = dict(status="RECORDING_COMPLETE", run_id=RUN_ID, binding=bound, binding_digest=digest(bound), counts=counts,
                      endpoints=endpoints, transitions=transitions, decisions=decisions, inventories_before_owner_close=before, owner_closed=True)
    except Exception as exc:
        record = dict(status="NOT_EVALUABLE", run_id=RUN_ID, counts=counts, failure=dict(phase=phase, code=type(exc).__name__ + ":" + str(exc), progress=progress))
    finally:
        MAIN_GATE = False
    payload = canonical(record)
    if len(payload) > RECORD_LIMIT: raise ValueError("RECORD_SIZE_LIMIT")
    out.mkdir(); (out / "record.json").write_bytes(payload)
    return record
