"""Bound one-shot S2-SP PPB lifecycle V2 runner.

The runner consumes only OA-presealed A--E recipes.  It stores no raw payload,
does not replay a historical runner, and treats unmet lifecycle conditions as
functional results rather than technical failures.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import from_visual_receptor_state
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2nl_private_half_profile_binding as half_profile
from tools import _s2oa_private_source_binding as source
from tools import _s2ob_private_caller_binding as oa
from tools import _s2sp_oa_materialization_adapter as adapter
from tools import _s2sp_private_memory_compare as core


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "s2sp.ppb-lifecycle-v2.v1"
MAIN_GATE = False
_USED = False
ARMS = {"HISTORICAL": coordinator.tspm1.PPB_UPDATE_HISTORICAL,
        "IDENTITY_PRESERVING_V1": coordinator.tspm1.PPB_UPDATE_IDENTITY_PRESERVING}
ROLES = (0, 0, 0, 0, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5)
CUE_ORDINALS = (14, 20)
MAX_BYTES = 262_144


class S2SPV2Error(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _require(ok: bool, code: str) -> None:
    if not ok:
        raise S2SPV2Error(code)


def _canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _source_plan() -> tuple[dict[str, object], dict[tuple[int, bool], dict[str, object]], dict[str, object]]:
    directory = ROOT / "reports/s2oa/s2oa-source-preseal-20260909-01"
    execution = json.loads((directory / "execution-plan.json").read_bytes())
    seal = json.loads((directory / "seal.json").read_bytes())
    _require(execution["execution_digest"] == source.digest({k: v for k, v in execution.items() if k != "execution_digest"}),
             "OA_EXECUTION_DIGEST_INVALID")
    _require(seal["execution_digest"] == execution["execution_digest"] and seal["status"] == "S2OA_SOURCES_PRESEALED",
             "OA_SOURCE_SEAL_INVALID")
    _require(execution["source_hashes"] == source.watched() and execution["profiles"] == source.profiles(),
             "OA_SOURCE_BINDING_CHANGED")
    audio = next(item for item in execution["sources"] if item["kind"] == "PCM")
    visual = {(item["recipe"]["ordinal"], item["recipe"]["visible_positions"] is not None): item
              for item in execution["sources"] if item["kind"] == "RGB"}
    _require(set((role, False) for role in ROLES) <= set(visual) and (0, True) in visual,
             "OA_ROLE_SOURCE_MISSING")
    return audio, visual, execution


def _visible_values(item: oa.Input) -> tuple[float, ...]:
    operation = item.event.operation_payload
    _require(type(operation) is oa.r.ng.visual.MaskedMemoryCue336V1, "CUE_TYPE_INVALID")
    _require(operation.visible_positions == tuple(range(32)), "CUE_SIGHT_INVALID")
    return tuple(0.0 if value is None else value for value in operation.values)


def _direct_baseline(state: object, cue: tuple[float, ...]) -> dict[str, tuple[str, ...]]:
    _require(type(state) is coordinator.S2JVCompositeStateV1 and len(cue) == 288, "BASELINE_FORM_INVALID")
    return {bank: tuple(candidate_id for candidate_id, values in rows if all(values[i] == cue[i] for i in range(32)))
            for bank, rows in core._candidate_rows(state).items()}


def _materialize_sequence() -> tuple[list[tuple[str, object]], dict[str, int], dict[str, object]]:
    audio_spec, visuals, execution = _source_plan()
    pcm, rgb, identity = source.generators()
    _require(identity == execution["generators"], "OA_GENERATOR_BINDING_INVALID")
    config = half_profile.build_config()
    hearing = oa.r.half.spectral.LogSpectralReceptor(oa.r.nn.LogSpectralConfig())
    video = LocalChannelGridReceptor(VisualGridConfig())
    output: list[tuple[str, object]] = []
    counts = {"payloads": 0, "audio": 0, "visual": 0, "nj": 0, "materialized_events": 0}
    role_index = 0
    for ordinal in range(1, 21):
        cue = ordinal in CUE_ORDINALS
        role = 0 if cue else ROLES[role_index]
        if not cue:
            role_index += 1
        visual_spec = visuals[(role, cue)]
        image = rgb(visual_spec["recipe"]["ordinal"])
        try:
            if cue:
                source.occlude(image, list(range(32)))
            raw = image.tobytes(order="C")
            _require(len(raw) == visual_spec["byte_count"] and hashlib.sha256(raw).hexdigest() == visual_spec["payload_sha256"],
                     "OA_VISUAL_PAYLOAD_INVALID")
            state = video.analyze(image, frame_index=6 * (ordinal - 1) + 2)
            counts["payloads"] += 1; counts["visual"] += 1
            visual = oa.r.nn.OrganismTimedReceptorFrame(from_visual_receptor_state(state),
                oa.r.nn.CommonFieldTime(oa.CLOCK, (6 * (ordinal - 1) + 2) * 1_000_000_000 // 30,
                                         200_000_000 * (ordinal - 1) + 100_000_000))
        finally:
            del image
        event_id = f"s2sp-v2-e{ordinal:02d}"
        if cue:
            item = oa.bind_input(config=config, ordinal=ordinal, event_id=event_id, kind=oa.V,
                                 visual=visual, rgb_digest=visual_spec["payload_sha256"])
            output.append(("CUE", item))
            counts["materialized_events"] += 1
            continue
        payload = pcm(audio_spec["recipe"])
        try:
            _require(hashlib.sha256(payload).hexdigest() == audio_spec["payload_sha256"], "OA_AUDIO_PAYLOAD_INVALID")
            samples = np.frombuffer(payload, dtype="<f4")
            try:
                values = hearing.analyze(samples)
            finally:
                del samples
            counts["payloads"] += 1; counts["audio"] += 1
            activity = oa.r.half.AuditoryReceptorContact.ACTIVE_ENERGY if any(values) else oa.r.half.AuditoryReceptorContact.ACTIVE_ZERO
            start = 9600 * (ordinal - 1)
            raw_audio = oa.r.half.AuditoryReceptorState("auditory", oa.r.half.RAW_GEOMETRY, start // 480,
                start, start + 4800, hearing.channel_ids, values, activity)
        finally:
            del payload
        item = oa.bind_input(config=config, ordinal=ordinal, event_id=event_id, kind=oa.AV, raw_audio=raw_audio,
                             visual=visual, pcm_digest=audio_spec["payload_sha256"], rgb_digest=visual_spec["payload_sha256"])
        value = adapter.bind_materialized_input(item, event_id=event_id, ordinal=ordinal,
                                                pcm_digest=audio_spec["payload_sha256"], rgb_digest=visual_spec["payload_sha256"])
        adapter.validate_half_profile_pair(value)
        output.append(("FORMATION", value))
        counts["nj"] += 1; counts["materialized_events"] += 1
    _require(counts == {"payloads": 38, "audio": 18, "visual": 20, "nj": 18, "materialized_events": 20},
             "V2_MATERIALIZATION_COUNTS_INVALID")
    return output, counts, {"execution_digest": execution["execution_digest"], "generator_identity": identity}


def verify(record: dict[str, object]) -> dict[str, object]:
    _require(record["status"] == "RECORDING_COMPLETE" and record["counts"]["events_per_arm"] == 20,
             "V2_RECORD_INVALID")
    inputs = None
    for arm, body in record["arms"].items():
        _require(body["mode"] == ARMS[arm] and len(body["events"]) == 20, "V2_ARM_INVALID")
        items = tuple(row["input_digest"] for row in body["events"])
        if inputs is None:
            inputs = items
        else:
            _require(inputs == items, "V2_INPUTS_DIFFER")
        for row in body["events"]:
            if row["kind"] == "FORMATION":
                transition = dict(row["transition"])
                _require(transition.pop("transition_evidence_digest") == core.digest(transition), "V2_TRANSITION_INVALID")
            else:
                _require(row["prestate_digest"] == row["poststate_digest"] and row["baseline"] == row["observed"],
                         "V2_CUE_INVALID")
    return {"status": "VERIFIED", "record_digest": record["record_digest"], "read_only": True}


def evaluate(record: dict[str, object]) -> dict[str, object]:
    result = {}
    for arm, body in record["arms"].items():
        forms = [row for row in body["events"] if row["kind"] == "FORMATION"]
        target = next((row["transition"]["visual_ppb_readout"] for row in forms[:4]
                       if row["transition"]["visual_ppb_readout"] is not None), None)
        cue14 = next(row for row in body["events"] if row["ordinal"] == 14)
        cue20 = next(row for row in body["events"] if row["ordinal"] == 20)
        absent = all(not cue14["baseline"][bank] for bank in ("B4", "FAST"))
        replaced = target is not None and any(row["transition"]["visual_ppb_readout"] is not None
            and row["transition"]["visual_ppb_readout"]["slot_id"] == target["slot_id"]
            and row["transition"]["visual_ppb_readout"]["event"] == "REPLACED" for row in forms[4:])
        result[arm] = {"cue14": "READY" if absent and target is not None else "PRÜFBEDINGUNG_NICHT_ERREICHT",
                       "cue20": "READY" if replaced else "PRÜFBEDINGUNG_NICHT_ERREICHT",
                       "cue14_observed": cue14["observed"], "cue20_observed": cue20["observed"]}
    return result


def record_materialized_once(
    items: list[tuple[str, object]], counts: dict[str, int], source_binding: dict[str, object], run_id: str,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    """Advance two fresh arms from already materialized inputs exactly once."""
    _require(len(items) == 20 and counts["materialized_events"] == 20, "V2_MATERIALIZED_ENVELOPE_INVALID")
    config = half_profile.build_config()
    states = {arm: coordinator.initial_s2jv_composite_state(config) for arm in ARMS}
    rows = {arm: [] for arm in ARMS}
    for ordinal, (kind, item) in enumerate(items, 1):
        if kind == "FORMATION":
            _require(type(item) is adapter.S2SPOAMaterializedPairV1 and item.ordinal == ordinal, "V2_PAIR_INVALID")
            for arm, mode in ARMS.items():
                pre = states[arm]
                result = core.form(config=config, state=pre, pair=item.pair, event_id=item.event_id,
                                   run_id=f"{run_id}-{arm.lower()}", ppb_update_mode=mode)
                transition = core.transition_evidence(prestate=pre, result=result)
                rows[arm].append({"ordinal": ordinal, "kind": kind, "input_digest": item.evidence_digest,
                    "prestate_digest": pre.state_digest, "poststate_digest": result.poststate.state_digest,
                    "transition": transition})
                states[arm] = result.poststate
        else:
            _require(type(item) is oa.Input and item.event.ordinal == ordinal, "V2_CUE_INPUT_INVALID")
            cue = _visible_values(item)
            for arm in ARMS:
                state = states[arm]; scan = core.compare_state(state=state, cue_values=cue)
                observed = {row["bank"]: tuple(row["exact_baseline_candidate_ids"]) for row in scan["banks"]}
                rows[arm].append({"ordinal": ordinal, "kind": kind, "input_digest": _digest(list(cue)),
                    "prestate_digest": state.state_digest, "poststate_digest": state.state_digest,
                    "baseline": _direct_baseline(state, cue), "observed": observed})
    record = {"schema": SCHEMA, "run_id": run_id, "status": "RECORDING_COMPLETE", "source_binding": source_binding,
              "counts": {**counts, "events_per_arm": 20, "formations_per_arm": 18, "cues_per_arm": 2},
              "arms": {arm: {"mode": mode, "events": rows[arm]} for arm, mode in ARMS.items()}}
    record["record_digest"] = _digest(record)
    proof = verify(record)
    evaluation = evaluate(record)
    _require(sum(len(_canonical(value)) for value in (record, proof, evaluation)) <= MAX_BYTES,
             "V2_RESULT_BUDGET_EXCEEDED")
    return record, proof, evaluation


def run_once(run_id: str) -> Path:
    global MAIN_GATE, _USED
    _require(MAIN_GATE and not _USED and run_id == "s2sp-ppb-lifecycle-v2-20260919-01", "V2_GATE_OR_ID_INVALID")
    output = ROOT / "reports" / run_id
    _require(not output.exists(), "V2_OUTPUT_EXISTS")
    _USED = True
    output.mkdir()
    try:
        items, counts, source_binding = _materialize_sequence()
        record, proof, evaluation = record_materialized_once(items, counts, source_binding, run_id)
        payloads = {"record.json": _canonical(record), "verification.json": _canonical(proof), "evaluation.json": _canonical(evaluation)}
        for name, value in payloads.items():
            (output / name).write_bytes(value)
        return output
    finally:
        MAIN_GATE = False
