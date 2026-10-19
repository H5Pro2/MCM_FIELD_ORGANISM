"""One bounded S2TU materialization run; no field or A/B integration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools import _s2ts_temporal_trace_run as src
from tools import _s2tu_retained_trace as tu
from tools import _s2tu_source_schedule as sch


RUN_ID = "s2tu-retention-real-20260919-01"
MAIN_GATE = False
USED = False
RECORD_LIMIT = 262_144


def canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _write(out: Path, record: dict[str, object]) -> None:
    payload = canonical(record)
    if len(payload) > RECORD_LIMIT:
        raise ValueError("RECORD_SIZE_LIMIT")
    out.mkdir()
    (out / "record.json").write_bytes(payload)


def run_once(out: Path) -> dict[str, object]:
    """Materialize exactly the bound endpoints after the caller opens MAIN_GATE."""
    global MAIN_GATE, USED
    if not MAIN_GATE or USED or out.exists():
        raise ValueError("RUN_NOT_AUTHORIZED")
    USED = True
    phase = "BINDING"
    progress: dict[str, object] = {"ordinal": 0, "source_id": None}
    counts = dict(audio=0, nj=0, endpoints=0, formations=0, hints=0, segment_closes=0, owner_closes=0)
    rows: list[dict[str, object]] = []
    try:
        bound = sch.binding()
        sources, plan = src.source_rows()
        profile = bound["profile"]
        import numpy as np
        from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        from tools import _s2nj_private_auditory_output_projection as nj

        receptor = LogSpectralReceptor(LogSpectralConfig(**plan["profiles"]["raw"]["config"]))
        store = tu.RetainedTraceStore(profile, "s2tu-owner-01")
        decisions: list[dict[str, object]] = []
        transitions: list[dict[str, object]] = []
        for event in bound["events"]:
            progress = {"ordinal": event["ordinal"], "source_id": event["source_id"]}
            if event["kind"] == "SEGMENT_CLOSE":
                phase = "SEGMENT_CLOSE"
                transitions.append(store.close_segment(event["segment"]))
                counts["segment_closes"] += 1
                continue
            phase = "PCM"
            source = sources[event["source_id"]]
            payload = src.nu.pcm_window(src.nu.WindowSpec(int(source["stream_id"][1:]), int(source["window_ordinal"])))
            if hashlib.sha256(payload).hexdigest() != source["pcm_sha256"]:
                raise ValueError("PCM_HASH_INVALID")
            phase = "RECEPTOR"
            raw = receptor.analyze(np.frombuffer(payload, dtype="<f4"))
            counts["audio"] += 1
            state = AuditoryReceptorState(
                "auditory", nj.RAW_GEOMETRY, int(source["nj_snapshot_index"]), int(source["window_start_sample"]),
                int(source["window_end_sample"]), receptor.channel_ids, raw,
                AuditoryReceptorContact.ACTIVE_ENERGY if any(raw) else AuditoryReceptorContact.ACTIVE_ZERO,
            )
            phase = "NJ"
            half = nj.project_auditory_half_v1(state, config=receptor.config, source_profile_digest=nj.RAW_PROFILE_DIGEST)
            counts["nj"] += 1
            counts["endpoints"] += 1
            values = [value.hex() for value in half.values]
            frame = tu.Frame(tuple(half.values), profile, event["owner"], event["segment"], event["ordinal"])
            rows.append(dict(
                ordinal=event["ordinal"], source_id=event["source_id"], pcm_sha256=source["pcm_sha256"],
                payload_hash_checked=True, frame=dict(owner=event["owner"], segment=event["segment"],
                ordinal=event["ordinal"], native_end=source["window_end_sample"], runtime_time=event["ordinal"]),
                values=values, value_digest=digest(values),
            ))
            result = store.form(frame) if event["kind"] == "FORMATION" else store.hint(frame)
            if event["kind"] == "FORMATION":
                counts["formations"] += 1
            else:
                counts["hints"] += 1
                if result is not None:
                    decisions.append(dict(ordinal=event["ordinal"], result=result))
        phase = "OWNER_CLOSE"
        retained_before_owner_close = list(store.generations)
        store.close_owner()
        counts["owner_closes"] += 1
        record: dict[str, object] = dict(
            status="RECORDING_COMPLETE", run_id=RUN_ID, binding=bound, binding_digest=digest(bound), counts=counts,
            endpoints=rows, transitions=transitions, decisions=decisions,
            retained_generations_before_owner_close=retained_before_owner_close, owner_closed=True,
        )
    except Exception as exc:
        record = dict(status="NOT_EVALUABLE", run_id=RUN_ID, counts=counts,
                      failure=dict(phase=phase, code=type(exc).__name__ + ":" + str(exc), progress=progress))
    finally:
        MAIN_GATE = False
    _write(out, record)
    return record
