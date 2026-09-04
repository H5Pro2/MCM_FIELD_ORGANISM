"""Independent read-only verifier for one bounded S2-LS stream result."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re


SCHEMA = "s2ls.presealed-corpus-stream.v1"
RESULT_SCHEMA = "s2ls.presealed-corpus-stream-result.v1"
QUALIFICATION_ID = "s2ls-neutral-stream-qualification-20260904-02"
MAX_RESULT_BYTES = 2_097_152
FAST_AUDITORY_MATCH_THRESHOLD = 0.2
FAST_VISUAL_MATCH_THRESHOLD = 0.2
EXPECTED_PLAN_DIGEST = "1ad42964295cce44b87f6c3d02479983878ca7c403eee21440783fe3326e661a"
EXPECTED_PLAN_FILE_SHA256 = "d1453b4abefdccb6425e4faf5b2d434cfda842f608d75bed585f5b12dd7338ae"
EXPECTED_EVIDENCE_DIGEST = "0840c261f91f824cd913fb1bc5ccdd9ba21b75d6680e61948561a986e2443f9b"
EXPECTED_EVIDENCE_FILE_SHA256 = "e09583f995f75ff4d9454af969133b51d9b4852a404af24befa61fadb8757e8a"
PLAN_RELATIVE_PATH = "reports/s2ls/s2ls-presealed-av-corpus-plan-20260904-01/presealed-corpus-plan.json"
EVIDENCE_RELATIVE_PATH = "reports/s2ls/s2ls-corpus-receptor-materialization-20260904-01/receptor-materialization.json"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

SOURCE_PATHS = (
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2kq_private_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2lm_private_role_free_stream_processor.py",
    "tools/_s2lo_private_role_free_stream_runner.py",
    "tools/_s2ls_private_presealed_av_corpus_plan.py",
    "tools/_s2ls_private_corpus_receptor_materialization.py",
    "tools/_s2ls_private_corpus_stream_runner.py",
    "tools/_s2ls_private_corpus_stream_verifier.py",
)


class S2LSVerificationError(ValueError):
    """The result cannot be accepted without executing project functions."""


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LSVerificationError(message)


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _verify_frozen(workspace_root: Path, binding: object) -> tuple[dict[str, object], dict[str, object]]:
    expected = {
        "plan_digest": EXPECTED_PLAN_DIGEST,
        "plan_file_sha256": EXPECTED_PLAN_FILE_SHA256,
        "evidence_digest": EXPECTED_EVIDENCE_DIGEST,
        "evidence_file_sha256": EXPECTED_EVIDENCE_FILE_SHA256,
    }
    _require(binding == expected, "frozen binding differs")
    plan_data = (workspace_root / PLAN_RELATIVE_PATH).read_bytes()
    evidence_data = (workspace_root / EVIDENCE_RELATIVE_PATH).read_bytes()
    _require(hashlib.sha256(plan_data).hexdigest() == EXPECTED_PLAN_FILE_SHA256, "plan file changed")
    _require(hashlib.sha256(evidence_data).hexdigest() == EXPECTED_EVIDENCE_FILE_SHA256, "evidence file changed")
    plan = json.loads(plan_data.decode("ascii"))
    evidence = json.loads(evidence_data.decode("ascii"))
    _require(plan_data == _canonical_bytes(plan, newline=True), "plan serialization differs")
    _require(evidence_data == _canonical_bytes(evidence, newline=True), "evidence serialization differs")
    plan_payload = dict(plan)
    evidence_payload = dict(evidence)
    _require(plan_payload.pop("plan_digest") == _digest(plan_payload) == EXPECTED_PLAN_DIGEST, "plan digest differs")
    _require(evidence_payload.pop("evidence_digest") == _digest(evidence_payload) == EXPECTED_EVIDENCE_DIGEST, "evidence digest differs")
    return plan, evidence


def _verify_sources(workspace_root: Path, value: object) -> None:
    _require(type(value) is dict and set(value) == set(SOURCE_PATHS), "source set differs")
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        _require(path.is_file(), f"bound source missing: {relative}")
        _require(value[relative] == hashlib.sha256(path.read_bytes()).hexdigest(), f"bound source changed: {relative}")


def _reject_raw(value: object) -> None:
    forbidden = {"raw_bytes", "rgb_bytes", "pcm_samples", "raw_payload", "image_bytes", "audio_bytes"}
    if type(value) is dict:
        _require(not forbidden.intersection(value), "raw source appears in result")
        for item in value.values():
            _reject_raw(item)
    elif type(value) is list:
        for item in value:
            _reject_raw(item)


def _verify_slot(value: object, *, fast: bool) -> None:
    _require(type(value) is dict, "slot projection differs")
    required = {"slot_id", "occupied", "support_count", "last_selected_step", "slot_digest"}
    _require(required.issubset(value) and _valid_digest(value.get("slot_digest")), "slot binding differs")
    if fast:
        _require(_valid_digest(value.get("auditory_values_digest")) and _valid_digest(value.get("visual_values_digest")), "Fast values binding differs")
    else:
        _require(_valid_digest(value.get("prototype_digest")), "PPB values binding differs")


def _verify_transition(value: object, prior_memory_digest: str | None, post_memory_digest: str) -> None:
    _require(type(value) is dict, "formation transition is absent")
    payload = dict(value)
    transition_digest = payload.pop("formation_transition_digest", None)
    _require(transition_digest == _digest(payload), "formation transition digest differs")
    _require(value.get("poststate_digest") == post_memory_digest, "formation transition poststate differs")
    if prior_memory_digest is not None:
        _require(value.get("prestate_digest") == prior_memory_digest, "formation transition chain differs")
    fast = value.get("fast")
    _require(type(fast) is dict and fast.get("event") in {"CREATED", "MATCHED", "REPLACED"}, "Fast transition event differs")
    fast_payload = dict(fast)
    _require(fast_payload.pop("transition_digest", None) == _digest(fast_payload), "Fast transition digest differs")
    _verify_slot(fast.get("pre_slot"), fast=True)
    _verify_slot(fast.get("post_slot"), fast=True)
    _require(fast["selected_slot_id"] == fast["post_slot"]["slot_id"], "Fast selected slot differs")
    if not fast["pre_slot"]["occupied"]:
        _require(fast["event"] == "CREATED", "Fast creation event differs")
        _require(fast["auditory_source_distance"] is None and fast["visual_source_distance"] is None, "Fast creation distance differs")
    else:
        auditory_distance = fast["auditory_source_distance"]
        visual_distance = fast["visual_source_distance"]
        _require(
            type(auditory_distance) is float
            and math.isfinite(auditory_distance)
            and auditory_distance >= 0.0
            and type(visual_distance) is float
            and math.isfinite(visual_distance)
            and visual_distance >= 0.0,
            "Fast transition distance differs",
        )
        expected_fast_event = (
            "MATCHED"
            if auditory_distance <= FAST_AUDITORY_MATCH_THRESHOLD
            and visual_distance <= FAST_VISUAL_MATCH_THRESHOLD
            else "REPLACED"
        )
        _require(fast["event"] == expected_fast_event, "Fast transition classification differs")
    for role in ("auditory_ppb", "visual_ppb"):
        item = value.get(role)
        _require(type(item) is dict and item.get("event") in {"NO_UPDATE", "CREATED", "MATCHED", "REPLACED"}, "PPB transition event differs")
        item_payload = dict(item)
        _require(item_payload.pop("transition_digest", None) == _digest(item_payload), "PPB transition digest differs")
        if item["event"] == "NO_UPDATE":
            _require(item["slot_id"] is None and item["pre_slot"] is None and item["post_slot"] is None, "empty PPB transition differs")
        else:
            _verify_slot(item.get("pre_slot"), fast=False)
            _verify_slot(item.get("post_slot"), fast=False)
            _require(item["slot_id"] == item["post_slot"]["slot_id"], "PPB selected slot differs")
            if not item["pre_slot"]["occupied"]:
                _require(item["event"] == "CREATED" and item["source_distance"] is None, "PPB creation event differs")
            else:
                distance = item["source_distance"]
                threshold = item["match_threshold"]
                _require(
                    type(distance) is float
                    and math.isfinite(distance)
                    and distance >= 0.0
                    and type(threshold) is float
                    and math.isfinite(threshold)
                    and threshold >= 0.0,
                    "PPB transition distance differs",
                )
                expected_ppb_event = "MATCHED" if distance <= threshold else "REPLACED"
                _require(item["event"] == expected_ppb_event, "PPB transition classification differs")


def _verify_scan(value: object, memory_digest: str) -> None:
    _require(type(value) is dict and value.get("scan_role") in {"PRIMARY", "DIRECT_BASELINE"}, "scan role differs")
    _require(value.get("prestate_digest") == memory_digest == value.get("poststate_digest"), "scan changed memory")
    _require(_valid_digest(value.get("input_digest")) and _valid_digest(value.get("receipt_digest")), "scan digest differs")
    hypothesis = value.get("hypothesis")
    if hypothesis is None:
        _require(value.get("hypothesis_digest") is None, "absent hypothesis has digest")
    else:
        _require(type(hypothesis) is dict and hypothesis.get("hypothesis_digest") == value.get("hypothesis_digest"), "hypothesis binding differs")
        payload = dict(hypothesis)
        _require(payload.pop("hypothesis_digest", None) == _digest(payload), "hypothesis digest differs")


def _verify_events(events: object, expected_count: int, formation_count: int, evidence: dict[str, object]) -> None:
    _require(type(events) is list and len(events) == expected_count, "event count differs")
    frozen = {item["event_id"]: item for item in evidence["event_receptor_bindings"]}
    prior_memory = None
    formations = 0
    for ordinal, event in enumerate(events, start=1):
        _require(type(event) is dict and event.get("ordinal") == ordinal, "event order differs")
        _require(event.get("owner_status") == "CONSUMED" and event.get("error_codes") == [], "event did not complete")
        _require(_valid_digest(event.get("source_digest")) and _valid_digest(event.get("result_digest")), "event digest binding differs")
        frozen_id = event.get("frozen_event_id")
        _require(frozen_id in frozen, "frozen event is absent")
        _require(event.get("event_receptor_binding_digest") == frozen[frozen_id]["event_receptor_binding_digest"], "event receptor binding differs")
        if event.get("event_type") == "COMPLETE_AV_PERCEPTION":
            formations += 1
            _require(type(event.get("memory_observation")) is dict, "formation memory observation is absent")
            _verify_transition(event.get("formation_transition"), prior_memory, event["memory_poststate_digest"])
            prior_memory = event["memory_poststate_digest"]
        else:
            _require(event.get("formation_transition") is None and event.get("memory_observation") is None, "cue contains a formation")
            _verify_scan(event.get("primary_scan"), prior_memory)
            _verify_scan(event.get("baseline_scan"), prior_memory)
    _require(formations == formation_count, "formation count differs")


def _verify_evaluation(value: object) -> None:
    _require(type(value) is dict and value.get("status") == "S2LS_FUNCTION_EVALUATED", "evaluation status differs")
    payload = dict(value)
    _require(payload.pop("evaluation_digest", None) == _digest(payload), "evaluation digest differs")
    _require(value.get("technical_success_depends_on_function") is False, "function gates technical completion")
    _require(value.get("adaptive_win_required") is False and value.get("negative_results_are_evaluable") is True, "evaluation acceptance differs")
    _require(set(value.get("modalities", {})) == {"AUDITORY", "VISUAL"}, "modality evaluation differs")
    cases = value.get("cases")
    _require(type(cases) is list and len(cases) == 8, "comparison case count differs")
    for case in cases:
        case_payload = dict(case)
        _require(case_payload.pop("case_digest", None) == _digest(case_payload), "comparison case digest differs")
        _require(case.get("modality") in {"AUDITORY", "VISUAL"}, "comparison modality differs")
        for arm in ("adaptive", "frozen", "replay"):
            result = case.get(arm)
            result_payload = dict(result)
            _require(result_payload.pop("arm_digest", None) == _digest(result_payload), "comparison arm digest differs")


def _verify_record(record: object, workspace_root: Path, expected_mode: str) -> None:
    _require(type(record) is dict and record.get("schema") == RESULT_SCHEMA, "result schema differs")
    _require(record.get("mode") == expected_mode and record.get("technical_status") == "RECORDING_COMPLETE", "technical status differs")
    payload = dict(record)
    _require(payload.pop("record_digest", None) == _digest(payload), "record digest differs")
    _, evidence = _verify_frozen(workspace_root, record.get("frozen_binding"))
    _verify_sources(workspace_root, record.get("source_hashes"))
    _reject_raw(record)
    _require(record.get("raw_payload_retained") is False, "raw retention differs")
    execution = record.get("execution")
    _require(type(execution) is dict, "execution is absent")
    execution_payload = dict(execution)
    _require(execution_payload.pop("execution_digest", None) == _digest(execution_payload), "execution digest differs")
    counters = execution.get("counters")
    _require(type(counters) is dict and counters.get("stream_status") == "OPEN", "stream state differs")
    if expected_mode == "QUALIFICATION":
        _require(record.get("run_id") == QUALIFICATION_ID, "qualification id differs")
        _require(record.get("plan") == {"event_count": 3, "formation_count": 1, "cue_count": 2, "main_story_executed": False, "main_execution_enabled": False}, "qualification plan differs")
        _require((counters.get("event_count"), counters.get("field_attempt_count"), counters.get("memory_formation_attempt_count"), counters.get("scan_attempt_count")) == (3, 3, 1, 4), "qualification counters differ")
        _verify_events(execution.get("events"), 3, 1, evidence)
        _require(record.get("evaluation") is None, "qualification contains evaluation")
    else:
        _require(expected_mode == "MAIN", "verification mode differs")
        _require(record.get("plan") == {"event_count": 25, "formation_count": 17, "cue_count": 8, "main_execution_enabled": True}, "main plan differs")
        _require((counters.get("event_count"), counters.get("field_attempt_count"), counters.get("memory_formation_attempt_count"), counters.get("scan_attempt_count")) == (25, 25, 17, 16), "main counters differ")
        _verify_events(execution.get("events"), 25, 17, evidence)
        _verify_evaluation(record.get("evaluation"))


def verify_result_file(result_path: Path, workspace_root: Path, *, expected_mode: str) -> dict[str, object]:
    _require(isinstance(result_path, Path) and result_path.is_absolute(), "absolute result Path required")
    _require(isinstance(workspace_root, Path) and workspace_root.is_absolute(), "absolute workspace Path required")
    try:
        data = result_path.read_bytes()
        _require(len(data) <= MAX_RESULT_BYTES and data.endswith(b"\n"), "result envelope differs")
        record = json.loads(data.decode("ascii"))
        _require(data == _canonical_bytes(record, newline=True), "result serialization differs")
        _verify_record(record, workspace_root, expected_mode)
    except S2LSVerificationError:
        raise
    except Exception as exc:
        raise S2LSVerificationError("result cannot be parsed or verified") from exc
    payload = {"verification_status": "RECORDING_COMPLETE", "mode": expected_mode, "record_digest": record["record_digest"], "read_only": True}
    return {**payload, "verification_digest": _digest(payload)}


__all__: tuple[str, ...] = ()
