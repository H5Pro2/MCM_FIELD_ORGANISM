"""One bounded S2-TS source-to-trace connection; no field or A/B memory."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from typing import Any

from tools import _s2nu_private_source_binding as nu
from tools import _s2ts_temporal_trace as ts

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PLAN = ROOT / "reports/s2nu/s2nu-source-preseal-20260909-01/execution-plan.json"
SOURCE_PLAN_SHA256 = "6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10"
VERSION = "s2ts.source-trace-run.v1"
RUN_ID = "s2ts-temporal-trace-real-20260919-01"
MAIN_GATE = False
USED = False


class S2TSRunError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def need(ok: bool, code: str) -> None:
    if not ok:
        raise S2TSRunError(code)


def canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def source_rows() -> tuple[dict[str, Any], dict[str, Any]]:
    need(hashlib.sha256(SOURCE_PLAN.read_bytes()).hexdigest() == SOURCE_PLAN_SHA256, "SOURCE_PLAN_CHANGED")
    plan = json.loads(SOURCE_PLAN.read_bytes())
    need(plan["execution_digest"] == "1d2787da42fe01e6bb960ad545bcfbf96a3e4abd036ce91033b325c450d7f2c7", "SOURCE_EXECUTION_INVALID")
    return {row["source_id"]: row for row in plan["sources"]}, plan


def schedule() -> tuple[dict[str, object], ...]:
    # a,b,c,d are deliberately repeated source identities, never deduplicated.
    ids = dict(a="nu-s02-w00", b="nu-s02-w01", c="nu-s02-w02", d="nu-s02-w03")
    sequence = (("s1", "FORMATION", "a"), ("s1", "FORMATION", "b"), ("s1", "FORMATION", "c"), ("s1", "FORMATION", "d"),
                ("s1", "HINT", "b"), ("s1", "HINT", "c"), ("s1", "HINT", "c"), ("s1", "HINT", "b"),
                ("s1", "HINT", "a"), ("s1", "HINT", "c"), ("s1", "CLOSE", None),
                ("s2", "HINT", "b"), ("s2", "HINT", "c"), ("s2", "FORMATION", "a"), ("s2", "FORMATION", "b"),
                ("s2", "FORMATION", "a"), ("s2", "FORMATION", "b"), ("s2", "HINT", "a"), ("s2", "HINT", "b"), ("s2", "CLOSE", None))
    return tuple(dict(ordinal=index + 1, session=session, kind=kind, label=label,
                      source_id=None if label is None else ids[label], runtime_time=(index + 1) * 100_000)
                 for index, (session, kind, label) in enumerate(sequence))


def binding() -> dict[str, object]:
    rows, plan = source_rows(); events = schedule()
    uses = [dict(ordinal=e["ordinal"], source=rows[e["source_id"]]) for e in events if e["source_id"]]
    value = dict(version=VERSION, source_plan_sha256=SOURCE_PLAN_SHA256,
                 source_execution_digest=plan["execution_digest"], profile=plan["profiles"]["half_profile_digest"],
                 events=events, source_uses=uses,
                 limits=dict(events=20, formations=8, audio_analyses=18, nj_projections=18,
                             field_contacts=0, scans=0, state_bytes=98304, metadata_bytes=65536, shared_bytes=262144))
    need(len(events) == 20 and sum(e["kind"] == "FORMATION" for e in events) == 8 and len(uses) == 18, "SCHEDULE_INVALID")
    return {**value, "binding_digest": digest(value)}


def _frame(row: dict[str, Any], event: dict[str, object], values: tuple[float, ...], profile: str) -> ts.Frame:
    return ts.Frame(values, profile, str(event["session"]), int(event["ordinal"]),
                    int(row["window_end_sample"]), int(event["runtime_time"]))


def execute_frames(events: tuple[dict[str, object], ...], frames: dict[int, ts.Frame]) -> dict[str, object]:
    """Neutrally exercise the same event handoff with already bound frames."""
    traces: dict[str, ts.TemporalTrace] = {}
    decisions: list[dict[str, object]] = []
    baselines: list[dict[str, object]] = []
    actions: list[dict[str, object]] = []
    for event in events:
        session, kind, ordinal = str(event["session"]), str(event["kind"]), int(event["ordinal"])
        trace = traces.setdefault(session, ts.TemporalTrace(frames[next(k for k in frames if frames[k].session == session)].profile, session))
        if kind == "CLOSE":
            actions.append(dict(ordinal=ordinal, action=trace.close()))
            continue
        active_before = trace._active
        result = trace.form(frames[ordinal]) if kind == "FORMATION" else trace.hint(frames[ordinal])
        actions.append(dict(ordinal=ordinal, action=result))
        if result is not None and kind == "HINT":
            decisions.append(dict(ordinal=ordinal, result=result))
            if active_before is not None:
                hint = (frames[ordinal - 1], frames[ordinal])
                baselines.append(dict(ordinal=ordinal, single=ts.single_membership(active_before, hint),
                                      unordered=ts.unordered_membership(active_before, hint),
                                      trace_digest=digest([frame.value_digest for frame in active_before.frames])))
    return dict(actions=actions, decisions=decisions, baselines=baselines)


def canonical_trace(value: object) -> dict[str, object]:
    """The only internal-to-record boundary for trace evidence."""
    trace = json.loads(canonical(value))
    need(type(trace) is dict and set(trace) == {"actions", "decisions", "baselines"}, "TRACE_RECORD_INVALID")
    for action in trace["actions"]:
        need(type(action) is dict and set(action) == {"ordinal", "action"} and type(action["ordinal"]) is int,
             "TRACE_ACTION_INVALID")
        item = action["action"]
        need(item is None or type(item) is str or type(item) is dict, "TRACE_ACTION_INVALID")
    for decision in trace["decisions"]:
        need(type(decision) is dict and set(decision) == {"ordinal", "result"} and type(decision["result"]) is dict,
             "TRACE_DECISION_INVALID")
        result = decision["result"]
        need(set(result) == {"decision", "generation", "offsets"} and type(result["decision"]) is str
             and (result["generation"] is None or type(result["generation"]) is int)
             and type(result["offsets"]) is list and all(type(offset) is int and 0 <= offset <= 2 for offset in result["offsets"]),
             "TRACE_DECISION_INVALID")
    for baseline in trace["baselines"]:
        need(type(baseline) is dict and set(baseline) == {"ordinal", "single", "unordered", "trace_digest"}, "TRACE_BASELINE_INVALID")
        for key in ("single", "unordered"):
            data = baseline[key]
            need(type(data) is dict and set(data) == {"present", "multiset_digest"} and type(data["present"]) is list
                 and len(data["present"]) == 2 and all(type(flag) is bool for flag in data["present"])
                 and type(data["multiset_digest"]) is str and len(data["multiset_digest"]) == 64, "TRACE_BASELINE_INVALID")
        need(type(baseline["trace_digest"]) is str and len(baseline["trace_digest"]) == 64, "TRACE_BASELINE_INVALID")
    return trace


def run_once(output: Path) -> dict[str, object]:
    global MAIN_GATE, USED
    need(MAIN_GATE and not USED and not output.exists(), "RUN_NOT_AUTHORIZED")
    USED = True
    phase, current, counts, rows, failure = "BINDING", None, dict(audio=0, nj=0, endpoints=0, formations=0, hints=0, closes=0), [], None
    try:
        bound = binding(); source_by_id, plan = source_rows(); profile = str(bound["profile"])
        import numpy as np
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
        from tools import _s2nj_private_auditory_output_projection as nj
        receptor = LogSpectralReceptor(LogSpectralConfig(**plan["profiles"]["raw"]["config"]))
        states: dict[int, ts.Frame] = {}
        for event in bound["events"]:
            kind, ordinal = str(event["kind"]), int(event["ordinal"])
            if kind == "CLOSE":
                counts["closes"] += 1; continue
            current, phase = str(event["source_id"]), "PCM"
            source = source_by_id[current]; payload = nu.pcm_window(nu.WindowSpec(int(source["stream_id"][1:]), int(source["window_ordinal"])))
            need(hashlib.sha256(payload).hexdigest() == source["pcm_sha256"], "PCM_HASH_INVALID")
            phase = "RECEPTOR"; samples = np.frombuffer(payload, dtype="<f4"); raw_values = receptor.analyze(samples); counts["audio"] += 1
            state = AuditoryReceptorState("auditory", nj.RAW_GEOMETRY, int(source["nj_snapshot_index"]), int(source["window_start_sample"]), int(source["window_end_sample"]), receptor.channel_ids, raw_values, AuditoryReceptorContact.ACTIVE_ENERGY if any(raw_values) else AuditoryReceptorContact.ACTIVE_ZERO)
            phase = "NJ"; projected = nj.project_auditory_half_v1(state, config=receptor.config, source_profile_digest=nj.RAW_PROFILE_DIGEST); counts["nj"] += 1
            frame = _frame(source, event, tuple(projected.values), profile); states[ordinal] = frame; counts["endpoints"] += 1
            rows.append(dict(ordinal=ordinal, source_id=current, pcm_sha256=source["pcm_sha256"], payload_hash_checked=True,
                             raw_values_digest=digest([x.hex() for x in raw_values]), half_values_hex=[x.hex() for x in projected.values],
                             frame=dict(native_end=frame.native_end, runtime_time=frame.runtime_time, value_digest=frame.value_digest)))
            if kind == "FORMATION": counts["formations"] += 1
            else: counts["hints"] += 1
        phase = "TRACE"; trace_result = canonical_trace(execute_frames(tuple(bound["events"]), states))
        result = dict(version=VERSION, run_id=RUN_ID, status="RECORDING_COMPLETE", binding=bound, endpoints=rows,
                      trace=trace_result, counts=counts, failure=None, main_gate_after=False)
        need(len(canonical(result)) <= 262144, "RESULT_LIMIT")
    except Exception as exc:
        result = dict(version=VERSION, run_id=RUN_ID, status="NOT_EVALUABLE", counts=counts,
                      failure=dict(phase=phase, source_id=current, code=getattr(exc, "code", type(exc).__name__)), main_gate_after=False)
    finally:
        MAIN_GATE = False
    output.mkdir(); (output / "record.json").write_bytes(canonical(result))
    return result
