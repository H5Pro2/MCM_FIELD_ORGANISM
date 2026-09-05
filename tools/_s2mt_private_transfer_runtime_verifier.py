"""Independent read-only verifier for the presealed S2-MT transfer stream."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from tools import _s2mt_private_presealed_transfer_sources as raw_source


S2MT_SCHEMA = "s2mt.private.presealed-transfer-runtime.v1"
S2MT_RESULT_SCHEMA = "s2mt.private.presealed-transfer-result.v1"
S2MT_FAILURE_SCHEMA = "s2mt.private.failure-receipt.v1"
S2MR_SCHEMA = "s2mr.private.minimal-mcm-runtime-336.v1"
S2LM_SCHEMA = "s2lm.role-free-perception-stream.v1"
AUTHORIZED_RUN_ID = "s2mt-presealed-transfer-runtime-20260905-02"
EVENT_COUNT = 28
FORMATION_COUNT = 20
FIELD_CONTACT_COUNT = 8_064
MAX_RESULT_BYTES = 524_288
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
FAILURE_CODES = {
    "SOURCE_PLAN": "S2MT_SOURCE_PLAN_FAILED",
    "MATERIALIZATION": "S2MT_MATERIALIZATION_FAILED",
    "RUNTIME_INIT": "S2MT_RUNTIME_INIT_FAILED",
    "EVENT_PROCESSING": "S2MT_EVENT_PROCESSING_FAILED",
    "RUNTIME_CLOSE": "S2MT_RUNTIME_CLOSE_FAILED",
    "EVALUATION": "S2MT_EVALUATION_FAILED",
}

SOURCE_PATHS = (
    "tools/_s2mr_private_minimal_mcm_runtime.py",
    "tools/_s2lm_private_role_free_stream_processor.py",
    "tools/_s2lo_private_role_free_stream_runner.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2kq_private_partial_cue_retrieval_336.py",
    "tools/_s2kq_private_direct_slot_scan_baseline.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_direct_auditory_slot_scan_baseline.py",
    "tools/_s2mt_private_presealed_transfer_sources.py",
    "tools/_s2mt_private_transfer_runtime_runner.py",
    "tools/_s2mt_private_transfer_runtime_verifier.py",
    "mcm_field_organism/finite_video_path.py",
    "mcm_field_organism/log_spectral_receptor.py",
)


class S2MTVerificationError(ValueError):
    """The transfer result is absent, changed, or internally inconsistent."""


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return encoded + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MTVerificationError(message)


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _spec(ordinal: int, event_type: str, recipe_id: str) -> dict[str, object]:
    payload = {
        "schema": S2MT_SCHEMA,
        "event_code": f"e{ordinal:02d}",
        "event_id": f"s2mt-event-e{ordinal:02d}",
        "ordinal": ordinal,
        "event_type": event_type,
        "recipe_id": recipe_id,
    }
    return {**payload, "spec_digest": _digest(payload)}


EVENT_SPECS = tuple(
    _spec(index, "COMPLETE_AV_PERCEPTION", recipe_id)
    for index, recipe_id in enumerate(raw_source.FORMATION_SEQUENCE, start=1)
) + tuple(
    _spec(index, f"PARTIAL_{modality}_CUE", recipe_id)
    for index, (recipe_id, modality) in enumerate(raw_source.CUE_SEQUENCE, start=21)
)


def _expected_attempt_bindings(source_hashes: dict[str, str]) -> dict[str, str]:
    _require(set(source_hashes) == set(SOURCE_PATHS), "source binding set differs")
    source_binding_digest = _digest(source_hashes)
    plan_binding_digest = _digest(
        {
            "schema": raw_source.S2MT_SOURCE_SCHEMA,
            "recipe_ids": list(raw_source.RECIPE_IDS),
            "formation_sequence": list(raw_source.FORMATION_SEQUENCE),
            "cue_sequence": [list(item) for item in raw_source.CUE_SEQUENCE],
            "frequencies_hz": list(raw_source.FREQUENCIES_HZ),
            "visual_seeds": list(raw_source.VISUAL_SEEDS),
            "event_spec_digests": [item["spec_digest"] for item in EVENT_SPECS],
        }
    )
    config_binding_digest = _digest(
        {
            "profile_id": "default-live.v1",
            "field_adapter_source": source_hashes["tools/_s2lo_private_role_free_stream_runner.py"],
            "memory_coordinator_source": source_hashes["tools/_s2jw_profiled_memory_coordinator.py"],
        }
    )
    runtime_binding_digest = _digest(
        {
            "runtime_id": "s2mt-transfer-runtime",
            "max_event_count": EVENT_COUNT,
            "runtime_source": source_hashes["tools/_s2mr_private_minimal_mcm_runtime.py"],
            "stream_source": source_hashes["tools/_s2lm_private_role_free_stream_processor.py"],
            "source_binding_digest": source_binding_digest,
            "plan_binding_digest": plan_binding_digest,
            "config_binding_digest": config_binding_digest,
        }
    )
    return {
        "source_binding_digest": source_binding_digest,
        "plan_binding_digest": plan_binding_digest,
        "config_binding_digest": config_binding_digest,
        "runtime_binding_digest": runtime_binding_digest,
    }


def _verify_failure_receipt(value: object, source_hashes: dict[str, str]) -> None:
    expected_keys = {
        "schema",
        "phase",
        "event_ordinal",
        "completed_event_count",
        "last_runtime_snapshot_digest",
        "error_code",
        "source_binding_digest",
        "plan_binding_digest",
        "config_binding_digest",
        "runtime_binding_digest",
        "failure_receipt_digest",
    }
    _require(type(value) is dict and set(value) == expected_keys, "failure receipt form differs")
    payload = dict(value)
    receipt_digest = payload.pop("failure_receipt_digest")
    _require(receipt_digest == _digest(payload), "failure receipt digest differs")
    _require(payload.get("schema") == S2MT_FAILURE_SCHEMA, "failure receipt schema differs")
    phase = payload.get("phase")
    _require(phase in FAILURE_CODES and payload.get("error_code") == FAILURE_CODES[phase], "failure phase or code differs")
    expected_bindings = _expected_attempt_bindings(source_hashes)
    _require(all(payload.get(key) == digest for key, digest in expected_bindings.items()), "failure attempt binding differs")
    ordinal = payload.get("event_ordinal")
    completed = payload.get("completed_event_count")
    last_snapshot = payload.get("last_runtime_snapshot_digest")
    _require(type(completed) is int and 0 <= completed <= EVENT_COUNT, "failure progress differs")
    if phase in {"SOURCE_PLAN", "MATERIALIZATION", "RUNTIME_INIT"}:
        _require(ordinal is None and completed == 0 and last_snapshot is None, "pre-runtime failure progress differs")
    elif phase == "EVENT_PROCESSING":
        _require(type(ordinal) is int and 1 <= ordinal <= EVENT_COUNT, "event failure ordinal differs")
        _require(completed == ordinal - 1 and _valid_digest(last_snapshot), "event failure progress differs")
    else:
        _require(ordinal is None and completed == EVENT_COUNT and _valid_digest(last_snapshot), "terminal failure progress differs")


def _verify_sources(value: object, workspace_root: Path) -> None:
    _require(type(value) is dict and set(value) == set(SOURCE_PATHS), "source set differs")
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        _require(path.is_file(), f"source is absent: {relative}")
        _require(value[relative] == hashlib.sha256(path.read_bytes()).hexdigest(), f"source changed: {relative}")


def _reject_forbidden(value: object) -> None:
    forbidden_keys = {
        "raw_bytes", "rgb_bytes", "frame_bytes", "image", "audio_window",
        "pcm_values", "pcm_samples", "raw_payload", "replacement_perception",
    }
    forbidden_values = {"TARGET", "DISTRACTOR", "HOLDOUT", "FAMILY"}
    if type(value) is dict:
        _require(not forbidden_keys.intersection(value), "raw or replacement payload appears")
        for key, item in value.items():
            _require(
                key not in forbidden_values and not (type(item) is str and item in forbidden_values),
                "research role leaked",
            )
            _reject_forbidden(item)
    elif type(value) is list:
        for item in value:
            _reject_forbidden(item)


def _expected_source_plan() -> dict[str, object]:
    plan = raw_source.build_presealed_plan()
    return {
        **plan.payload_without_digest(),
        "recipes": [
            {**item.payload_without_digest(), "recipe_digest": item.recipe_digest}
            for item in plan.recipes
        ],
        "plan_digest": plan.plan_digest,
    }


def _verify_geometry(value: object) -> None:
    _require(type(value) is dict, "geometry evidence is absent")
    payload = dict(value)
    geometry_digest = payload.pop("geometry_digest", None)
    _require(geometry_digest == _digest(payload), "geometry digest differs")
    _require(value.get("status") == "S2MT_GEOMETRY_MATERIALIZED", "geometry did not pass")
    _require(value.get("repetition_values_equal") is True, "repetition geometry differs")
    pairwise = value.get("pairwise")
    cues = value.get("cue_matches")
    _require(type(pairwise) is list and len(pairwise) == 66, "pairwise geometry count differs")
    _require(all(item.get("fast_separated") is True for item in pairwise), "one formation pair is not Fast-separated")
    _require(type(cues) is list and len(cues) == 8, "cue geometry count differs")
    expected = [["n00"], ["n00"], ["n01"], ["n01"], ["n02"], ["n02"], [], []]
    _require([item.get("matching_training_recipes") for item in cues] == expected, "cue geometry differs")


def _verify_snapshot(value: object) -> dict[str, object]:
    _require(type(value) is dict, "runtime snapshot is absent")
    payload = dict(value)
    snapshot_digest = payload.pop("snapshot_digest", None)
    _require(snapshot_digest == _digest(payload), "runtime snapshot digest differs")
    _require(payload.get("schema") == S2MR_SCHEMA and payload.get("status") in {"OPEN", "CLOSED"}, "runtime snapshot form differs")
    for key in ("stream_state_digest", "field_state_digest", "memory_state_digest", "config_digest"):
        _require(_valid_digest(payload.get(key)), f"snapshot {key} differs")
    return value


def _verify_memory_observation(value: object, generation: int, state_digest: str) -> None:
    _require(type(value) is dict, "memory observation is absent")
    payload = dict(value)
    observation_digest = payload.pop("observation_digest", None)
    _require(observation_digest == _digest(payload), "memory observation digest differs")
    _require(value.get("state_digest") == state_digest and value.get("generation") == generation, "memory observation state differs")
    b4 = value.get("b4")
    fast = value.get("fast")
    auditory = value.get("auditory_slow")
    visual = value.get("visual_slow")
    _require(all(type(item) is list for item in (b4, fast, auditory, visual)), "memory bank form differs")
    _require(
        [item.get("formation_index") for item in b4]
        == list(range(max(1, generation - 8), generation + 1)),
        "B4 inventory differs",
    )
    for item in b4:
        _require(_valid_digest(item.get("values_digest")), "B4 digest differs")
    for item in fast:
        _require(_valid_digest(item.get("auditory_values_digest")) and _valid_digest(item.get("visual_values_digest")), "Fast digest differs")
    for item in auditory + visual:
        _require(type(item.get("support_count")) is int and 1 <= item["support_count"] <= 3, "Slow support differs")
        _require(_valid_digest(item.get("prototype_digest")), "Slow prototype digest differs")


def _verify_hypothesis(value: object, modality: str, expected_present: bool) -> None:
    if not expected_present:
        _require(value is None, "unexpected hypothesis was published")
        return
    _require(type(value) is dict and value.get("modality") == modality, "hypothesis modality differs")
    payload = value.get("payload")
    _require(type(payload) is dict and value.get("hypothesis_digest") == _digest(payload), "hypothesis digest differs")
    positions = payload.get("masked_bands") if modality == "AUDITORY" else payload.get("masked_positions")
    proposed = payload.get("proposed_values")
    expected_count = 24 if modality == "AUDITORY" else 256
    expected_area = "B_STABLE_AUDITORY" if modality == "AUDITORY" else "B_STABLE"
    _require(payload.get("area") == expected_area, "hypothesis area differs")
    _require(type(positions) is list and type(proposed) is list and len(positions) == len(proposed) == expected_count, "hypothesis dimension differs")


def _expected_evaluation(events: list[dict[str, object]], final_open: dict[str, object], closed: dict[str, object]) -> dict[str, object]:
    final_memory = events[FORMATION_COUNT - 1]["memory_observation"]
    target_digests = {}
    for recipe in ("n00", "n01", "n02"):
        event = next(item for item in events[:FORMATION_COUNT] if item["recipe_id"] == recipe)
        observation = event["memory_observation"]
        ordinal = event["ordinal"]
        b4 = next(item for item in observation["b4"] if item["formation_index"] == ordinal)
        fast = next(item for item in observation["fast"] if item["last_selected_step"] == ordinal)
        target_digests[recipe] = {
            "av": b4["values_digest"],
            "auditory": fast["auditory_values_digest"],
            "visual": fast["visual_values_digest"],
        }
    absent = {
        recipe: all(item["values_digest"] != digests["av"] for item in final_memory["b4"])
        and all(
            item["auditory_values_digest"] != digests["auditory"]
            or item["visual_values_digest"] != digests["visual"]
            for item in final_memory["fast"]
        )
        for recipe, digests in target_digests.items()
    }
    auditory_supports = sorted(item["support_count"] for item in final_memory["auditory_slow"])
    visual_supports = sorted(item["support_count"] for item in final_memory["visual_slow"])
    decisions = []
    roles = (
        ("A", "AUDITORY"), ("A", "VISUAL"), ("B", "AUDITORY"), ("B", "VISUAL"),
        ("C", "AUDITORY"), ("C", "VISUAL"), ("UNKNOWN", "AUDITORY"), ("UNKNOWN", "VISUAL"),
    )
    for event, (role, modality) in zip(events[FORMATION_COUNT:], roles, strict=True):
        step = event["runtime_step"]
        hypothesis = step["hypothesis"]
        decisions.append(
            {
                "evaluation_role": role,
                "modality": modality,
                "context_status": step["payload"]["context_status"],
                "area": None if hypothesis is None else hypothesis["payload"]["area"],
                "hypothesis_present": hypothesis is not None,
            }
        )
    final_memory_digest = events[FORMATION_COUNT - 1]["post_snapshot"]["memory_state_digest"]
    memory_read_only = all(event["post_snapshot"]["memory_state_digest"] == final_memory_digest for event in events[FORMATION_COUNT:])
    expected_presence = [True, True, True, True, False, False, False, False]
    confirmed = (
        all(absent.values())
        and auditory_supports == [2, 3, 3]
        and visual_supports == [2, 3, 3]
        and [item["hypothesis_present"] for item in decisions] == expected_presence
        and all(item["area"] == ("B_STABLE_AUDITORY" if item["modality"] == "AUDITORY" else "B_STABLE") for item in decisions[:4])
        and all(item["context_status"].startswith("ABSTAIN_") for item in decisions[4:])
        and memory_read_only
        and final_open["processed_event_count"] == EVENT_COUNT
        and final_open["field_attempt_count"] == EVENT_COUNT
        and final_open["memory_formation_attempt_count"] == FORMATION_COUNT
        and final_open["scan_attempt_count"] == 16
        and final_open["status"] == "OPEN"
        and closed["status"] == "CLOSED"
    )
    payload = {
        "status": "S2MT_TRANSFER_STREAM_CONFIRMED" if confirmed else "S2MT_FUNCTION_FALSIFIED",
        "a_recent_absence": absent,
        "auditory_slow_supports": auditory_supports,
        "visual_slow_supports": visual_supports,
        "cue_decisions": decisions,
        "memory_read_only_during_cues": memory_read_only,
        "field_contact_count": FIELD_CONTACT_COUNT,
        "hypothesis_application_count": 0,
        "completion_count": 0,
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def _verify_record(record: object, workspace_root: Path) -> None:
    _require(type(record) is dict and record.get("schema") == S2MT_RESULT_SCHEMA, "result schema differs")
    _require(record.get("run_id") == AUTHORIZED_RUN_ID, "run id differs")
    _require(record.get("technical_status") in {"RECORDING_COMPLETE", "NOT_EVALUABLE"}, "technical status differs")
    payload = dict(record)
    record_digest = payload.pop("record_digest", None)
    _require(record_digest == _digest(payload), "record digest differs")
    _verify_sources(record.get("source_hashes"), workspace_root)
    _reject_forbidden(record)
    if record.get("technical_status") == "NOT_EVALUABLE":
        receipt = record.get("failure_receipt")
        _require(record.get("execution") is None and record.get("evaluation") is None, "NOT_EVALUABLE leaked partial output")
        _verify_failure_receipt(receipt, record["source_hashes"])
        _require(record.get("failure_code") == receipt["error_code"], "failure code binding differs")
        return
    _require("failure_code" not in record, "complete result contains failure code")
    expected_source_plan = _expected_source_plan()
    _require(record.get("presealed_source_plan") == expected_source_plan, "presealed source plan differs")
    _verify_geometry(record.get("geometry"))
    plan = record.get("plan")
    execution = record.get("execution")
    _require(type(plan) is dict and type(execution) is dict, "plan or execution is absent")
    _require(
        plan.get("event_count") == EVENT_COUNT
        and plan.get("formation_count") == FORMATION_COUNT
        and plan.get("cue_count") == 8
        and plan.get("field_contact_count") == FIELD_CONTACT_COUNT
        and plan.get("hypothesis_application_count") == 0
        and plan.get("completion_count") == 0
        and plan.get("event_spec_digests") == [item["spec_digest"] for item in EVENT_SPECS],
        "execution plan differs",
    )
    config = execution.get("runtime_config")
    _require(type(config) is dict and config.get("schema") == S2MR_SCHEMA and config.get("runtime_id") == "s2mt-transfer-runtime" and config.get("max_event_count") == EVENT_COUNT, "runtime config differs")
    config_payload = dict(config)
    config_digest = config_payload.pop("config_digest", None)
    _require(config_digest == _digest(config_payload), "runtime config digest differs")
    _require(
        config.get("source_binding_digest") == _digest({"plan_digest": expected_source_plan["plan_digest"], "event_spec_digests": [item["spec_digest"] for item in EVENT_SPECS]})
        and config.get("component_binding_digest") == _digest(record["source_hashes"]),
        "runtime binding differs",
    )
    initial = _verify_snapshot(execution.get("initial_snapshot"))
    _require(initial["status"] == "OPEN" and initial["processed_event_count"] == 0 and initial["next_ordinal"] == 1, "initial runtime state differs")
    events = execution.get("events")
    _require(type(events) is list and len(events) == EVENT_COUNT, "event count differs")
    prior = initial
    for index, (event, spec) in enumerate(zip(events, EVENT_SPECS, strict=True)):
        _require(type(event) is dict, "event record differs")
        for key in ("event_code", "event_id", "ordinal", "event_type", "recipe_id"):
            _require(event.get(key) == spec[key], f"event {key} differs")
        _require(event.get("event_spec_digest") == spec["spec_digest"], "event spec digest differs")
        _require(_valid_digest(event.get("source_digest")) and _valid_digest(event.get("source_receipt_digest")) and _valid_digest(event.get("perception_digest")), "event source binding differs")
        event_payload = {
            "schema": S2LM_SCHEMA,
            "event_id": event["event_id"],
            "ordinal": event["ordinal"],
            "event_type": event["event_type"],
            "source_digest": event["source_digest"],
            "perception_digest": event["perception_digest"],
            "field_projection_digest": event["perception_digest"],
            "operation_projection_digest": event["perception_digest"],
        }
        _require(event.get("event_digest") == _digest(event_payload), "event digest differs")
        step = event.get("runtime_step")
        _require(type(step) is dict and type(step.get("payload")) is dict, "runtime step is absent")
        step_payload = step["payload"]
        _require(step.get("step_digest") == _digest(step_payload), "runtime step digest differs")
        _require(step_payload.get("event_digest") == event["event_digest"], "runtime event binding differs")
        hypothesis = step.get("hypothesis")
        _require(
            step_payload.get("hypothesis_digest") == (None if hypothesis is None else hypothesis.get("hypothesis_digest")),
            "runtime hypothesis binding differs",
        )
        snapshot = _verify_snapshot(event.get("post_snapshot"))
        _require(step_payload.get("prestate_digest") == prior["snapshot_digest"] and step_payload.get("poststate_digest") == snapshot["snapshot_digest"], "runtime chain differs")
        _require(snapshot["processed_event_count"] == index + 1 and snapshot["next_ordinal"] == index + 2 and snapshot["status"] == "OPEN", "runtime counters differ")
        _require(step_payload.get("perception_status") == "FIELD_CONTACT_RECORDED" and step_payload.get("error_codes") == [], "runtime event failed")
        if index < FORMATION_COUNT:
            _require(step_payload.get("memory_status") == "FORMATION_COMMITTED" and step_payload.get("context_status") == "NOT_REQUESTED" and step.get("hypothesis") is None, "formation routing differs")
            _verify_memory_observation(event.get("memory_observation"), index + 1, snapshot["memory_state_digest"])
        else:
            expected_present = index < 24
            _require(step_payload.get("memory_status") == "READ_ONLY_UNCHANGED" and event.get("memory_observation") is None, "cue changed memory")
            _verify_hypothesis(step.get("hypothesis"), "AUDITORY" if index % 2 == 0 else "VISUAL", expected_present)
            if expected_present:
                _require(step_payload.get("context_status") == "CONTEXT_CANDIDATE_AVAILABLE", "known cue was not admitted")
            else:
                _require(str(step_payload.get("context_status", "")).startswith("ABSTAIN_"), "unknown or unstable cue did not abstain")
        prior = snapshot
    final_open = _verify_snapshot(execution.get("final_open_snapshot"))
    closed = _verify_snapshot(execution.get("closed_snapshot"))
    _require(final_open == events[-1]["post_snapshot"], "final open snapshot differs")
    _require(final_open["processed_event_count"] == EVENT_COUNT and final_open["field_attempt_count"] == EVENT_COUNT and final_open["memory_formation_attempt_count"] == FORMATION_COUNT and final_open["scan_attempt_count"] == 16, "final counters differ")
    open_payload = dict(final_open)
    close_payload = dict(closed)
    open_payload.pop("snapshot_digest")
    close_payload.pop("snapshot_digest")
    _require(open_payload.pop("status") == "OPEN" and close_payload.pop("status") == "CLOSED" and open_payload == close_payload, "runtime close differs")
    expected_evaluation = _expected_evaluation(events, final_open, closed)
    _require(record.get("evaluation") == expected_evaluation, "evaluation differs")


def verify_result_file(result_path: Path, workspace_root: Path) -> dict[str, object]:
    _require(result_path.is_absolute() and workspace_root.is_absolute(), "absolute paths required")
    try:
        data = result_path.read_bytes()
        _require(len(data) <= MAX_RESULT_BYTES, "result exceeds byte budget")
        _require(data.endswith(b"\n"), "canonical line ending is absent")
        record = json.loads(data.decode("ascii"))
        _require(data == _canonical_bytes(record, newline=True), "result serialization differs")
        _verify_record(record, workspace_root)
    except S2MTVerificationError:
        raise
    except Exception as exc:
        raise S2MTVerificationError("result cannot be parsed or verified") from exc
    payload = {
        "verification_status": record["technical_status"],
        "run_id": AUTHORIZED_RUN_ID,
        "record_digest": record["record_digest"],
        "read_only": True,
    }
    return {**payload, "verification_digest": _digest(payload)}


__all__: tuple[str, ...] = ()
