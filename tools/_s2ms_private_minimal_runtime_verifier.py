"""Independent read-only verifier for the bounded S2-MS reproduction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


S2MS_SCHEMA = "s2ms.private.minimal-runtime-reproduction.v1"
S2MS_RESULT_SCHEMA = "s2ms.private.minimal-runtime-reproduction-result.v1"
S2MR_SCHEMA = "s2mr.private.minimal-mcm-runtime-336.v1"
S2LM_SCHEMA = "s2lm.role-free-perception-stream.v1"
S2LO_SCHEMA = "s2lo.role-free-distributed-stream.v1"
AUTHORIZED_RUN_ID = "s2ms-minimal-runtime-s2ln-20260905-01"
REFERENCE_RESULT = "reports/s2ln/s2ln-role-free-distributed-av-20260904-02/result.json"
REFERENCE_RESULT_SHA256 = "665155b9dd221f5347f82f211195e8258cc7e32f7fa9aeca2f2738bf90a626da"
MAX_RESULT_BYTES = 262_144
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

SOURCE_PATHS = (
    "tools/_s2mr_private_minimal_mcm_runtime.py",
    "tools/_s2lm_private_role_free_stream_processor.py",
    "tools/_s2lo_private_role_free_stream_runner.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2kq_private_partial_cue_retrieval_336.py",
    "tools/_s2kq_private_direct_slot_scan_baseline.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_direct_auditory_slot_scan_baseline.py",
    "tools/_s2ms_private_minimal_runtime_reproduction.py",
    "tools/_s2ms_private_minimal_runtime_verifier.py",
    "mcm_field_organism/finite_video_path.py",
    "mcm_field_organism/log_spectral_receptor.py",
)

_FORMATION_CONTENTS = (
    "c00", "c01", "c00", "c02", "c00", "c03", "c00", "c04",
    "c05", "c06", "c07", "c08", "c09", "c01", "c02", "c03",
)


class S2MSVerificationError(ValueError):
    """The S2-MS result is absent, mutated, or internally inconsistent."""


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return encoded + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MSVerificationError(message)


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _spec(ordinal: int, event_type: str, content_id: str | None) -> dict[str, object]:
    code = f"e{ordinal:02d}"
    payload = {
        "schema": S2LO_SCHEMA,
        "event_code": code,
        "event_id": f"s2ln-event-{code}",
        "ordinal": ordinal,
        "event_type": event_type,
        "content_id": content_id,
    }
    return {**payload, "spec_digest": _digest(payload)}


EVENT_SPECS = tuple(
    _spec(index, "COMPLETE_AV_PERCEPTION", content)
    for index, content in enumerate(_FORMATION_CONTENTS, start=1)
) + (
    _spec(17, "PARTIAL_AUDITORY_CUE", None),
    _spec(18, "PARTIAL_VISUAL_CUE", None),
)


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
                key not in forbidden_values
                and not (type(item) is str and item in forbidden_values),
                "research role leaked",
            )
            _reject_forbidden(item)
    elif type(value) is list:
        for item in value:
            _reject_forbidden(item)


def _verify_snapshot(value: object) -> dict[str, object]:
    _require(type(value) is dict, "runtime snapshot is absent")
    payload = dict(value)
    snapshot_digest = payload.pop("snapshot_digest", None)
    _require(snapshot_digest == _digest(payload), "runtime snapshot digest differs")
    _require(payload.get("schema") == S2MR_SCHEMA, "runtime snapshot schema differs")
    _require(payload.get("status") in {"OPEN", "CLOSED"}, "runtime status differs")
    for key in ("stream_state_digest", "field_state_digest", "memory_state_digest", "config_digest"):
        _require(_valid_digest(payload.get(key)), f"snapshot {key} differs")
    return value


def _verify_memory_observation(value: object, ordinal: int, memory_digest: str) -> None:
    _require(type(value) is dict, "memory observation is absent")
    payload = dict(value)
    observation_digest = payload.pop("observation_digest", None)
    _require(observation_digest == _digest(payload), "memory observation digest differs")
    _require(value.get("state_digest") == memory_digest, "memory observation state differs")
    _require(value.get("generation") == ordinal, "memory generation differs")
    b4 = value.get("b4")
    fast = value.get("fast")
    auditory = value.get("auditory_slow")
    visual = value.get("visual_slow")
    _require(all(type(item) is list for item in (b4, fast, auditory, visual)), "memory bank form differs")
    _require(
        [item.get("formation_index") for item in b4]
        == list(range(max(1, ordinal - 8), ordinal + 1)),
        "B4 formation inventory differs",
    )
    for item in b4:
        _require(_valid_digest(item.get("values_digest")), "B4 value digest differs")
    for item in fast:
        _require(
            _valid_digest(item.get("auditory_values_digest"))
            and _valid_digest(item.get("visual_values_digest")),
            "Fast value digest differs",
        )
    for item in auditory + visual:
        _require(
            type(item.get("support_count")) is int
            and 1 <= item["support_count"] <= 3
            and _valid_digest(item.get("prototype_digest")),
            "Slow evidence differs",
        )


def _verify_hypothesis(value: object, modality: str) -> dict[str, object]:
    _require(type(value) is dict and value.get("modality") == modality, "hypothesis modality differs")
    payload = value.get("payload")
    _require(type(payload) is dict, "hypothesis payload is absent")
    _require(value.get("hypothesis_digest") == _digest(payload), "hypothesis digest differs")
    if modality == "AUDITORY":
        positions = payload.get("masked_bands")
        _require(payload.get("area") == "B_STABLE_AUDITORY", "auditory area differs")
        _require(type(positions) is list and len(positions) == 24, "auditory hypothesis dimension differs")
    else:
        positions = payload.get("masked_positions")
        _require(payload.get("area") == "B_STABLE", "visual area differs")
        _require(type(positions) is list and len(positions) == 256, "visual hypothesis dimension differs")
    proposed = payload.get("proposed_values")
    _require(type(proposed) is list and len(proposed) == len(positions), "hypothesis values differ")
    return value


def _reference_projection(workspace_root: Path) -> dict[str, object]:
    path = workspace_root / REFERENCE_RESULT
    data = path.read_bytes()
    _require(hashlib.sha256(data).hexdigest() == REFERENCE_RESULT_SHA256, "reference result changed")
    record = json.loads(data.decode("ascii"))
    evaluation = record.get("evaluation")
    counters = record.get("execution", {}).get("counters")
    _require(type(evaluation) is dict and type(counters) is dict, "reference result is incomplete")
    return {
        "status": evaluation.get("status"),
        "target_absent_from_a_recent": evaluation.get("target_absent_from_a_recent"),
        "auditory_stable_support": evaluation.get("auditory_stable_support"),
        "visual_stable_support": evaluation.get("visual_stable_support"),
        "auditory_area": evaluation.get("auditory", {}).get("area"),
        "visual_area": evaluation.get("visual", {}).get("area"),
        "event_count": counters.get("event_count"),
        "field_attempt_count": counters.get("field_attempt_count"),
        "memory_formation_attempt_count": counters.get("memory_formation_attempt_count"),
        "scan_attempt_count": counters.get("scan_attempt_count"),
    }


def _verify_record(record: object, workspace_root: Path) -> None:
    _require(type(record) is dict and record.get("schema") == S2MS_RESULT_SCHEMA, "result schema differs")
    _require(record.get("run_id") == AUTHORIZED_RUN_ID, "run id differs")
    _require(
        record.get("technical_status") in {"RECORDING_COMPLETE", "NOT_EVALUABLE"},
        "technical status differs",
    )
    payload = dict(record)
    record_digest = payload.pop("record_digest", None)
    _require(record_digest == _digest(payload), "record digest differs")
    _verify_sources(record.get("source_hashes"), workspace_root)
    _reject_forbidden(record)
    _require(
        record.get("reference_result")
        == {"path": REFERENCE_RESULT, "sha256": REFERENCE_RESULT_SHA256},
        "reference binding differs",
    )
    plan = record.get("plan")
    execution = record.get("execution")
    _require(type(plan) is dict, "plan is absent")
    _require(
        plan.get("event_budget") == 18
        and plan.get("formation_count") == 16
        and plan.get("field_contact_count") == 5_712
        and plan.get("hypothesis_application_count") == 0
        and plan.get("completion_count") == 0
        and plan.get("event_spec_digests") == [item["spec_digest"] for item in EVENT_SPECS],
        "execution plan differs",
    )
    if record.get("technical_status") == "NOT_EVALUABLE":
        _require(
            record.get("execution") is None
            and record.get("evaluation") is None
            and record.get("failure_code") == "S2MS_EXECUTION_FAILED",
            "NOT_EVALUABLE form differs",
        )
        return
    _require("failure_code" not in record, "complete result contains failure code")
    _require(type(execution) is dict, "execution is absent")
    config = execution.get("runtime_config")
    _require(type(config) is dict and config.get("max_event_count") == 18, "runtime config differs")
    config_payload = dict(config)
    config_digest = config_payload.pop("config_digest", None)
    _require(config_digest == _digest(config_payload), "runtime config digest differs")
    expected_source_binding = _digest(
        {
            "schema": S2MS_SCHEMA,
            "event_spec_digests": [item["spec_digest"] for item in EVENT_SPECS],
            "reference_result_sha256": REFERENCE_RESULT_SHA256,
        }
    )
    _require(
        config.get("schema") == S2MR_SCHEMA
        and config.get("runtime_id") == "s2ms-minimal-runtime"
        and config.get("source_binding_digest") == expected_source_binding
        and config.get("component_binding_digest") == _digest(record["source_hashes"]),
        "runtime source or component binding differs",
    )
    initial = _verify_snapshot(execution.get("initial_snapshot"))
    _require(
        initial["status"] == "OPEN"
        and initial["processed_event_count"] == 0
        and initial["next_ordinal"] == 1,
        "initial runtime state differs",
    )
    events = execution.get("events")
    _require(type(events) is list and len(events) == 18, "event count differs")
    prior_snapshot = initial
    for index, (event, spec) in enumerate(zip(events, EVENT_SPECS, strict=True)):
        _require(type(event) is dict, "event record differs")
        for key in ("event_code", "event_id", "ordinal", "event_type", "content_id"):
            _require(event.get(key) == spec[key], f"event {key} differs")
        _require(event.get("event_spec_digest") == spec["spec_digest"], "event spec digest differs")
        for key in ("source_digest", "source_receipt_digest", "perception_digest", "event_digest"):
            _require(_valid_digest(event.get(key)), f"event {key} differs")
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
        _require(event["event_digest"] == _digest(event_payload), "event digest differs")
        step = event.get("runtime_step")
        _require(type(step) is dict and type(step.get("payload")) is dict, "runtime step is absent")
        step_payload = step["payload"]
        _require(step.get("step_digest") == _digest(step_payload), "runtime step digest differs")
        _require(
            step_payload.get("event_digest") == event["event_digest"]
            and step_payload.get("prestate_digest") == prior_snapshot["snapshot_digest"],
            "runtime step chain differs",
        )
        snapshot = _verify_snapshot(event.get("post_snapshot"))
        _require(
            step_payload.get("poststate_digest") == snapshot["snapshot_digest"]
            and snapshot["processed_event_count"] == index + 1
            and snapshot["next_ordinal"] == index + 2
            and snapshot["status"] == "OPEN",
            "runtime poststate differs",
        )
        _require(step_payload.get("perception_status") == "FIELD_CONTACT_RECORDED", "field contact failed")
        _require(step_payload.get("error_codes") == [], "runtime step has errors")
        hypothesis = step.get("hypothesis")
        if index < 16:
            _require(
                step_payload.get("memory_status") == "FORMATION_COMMITTED"
                and step_payload.get("context_status") == "NOT_REQUESTED"
                and hypothesis is None,
                "formation routing differs",
            )
            _verify_memory_observation(event.get("memory_observation"), index + 1, snapshot["memory_state_digest"])
        else:
            _require(
                step_payload.get("memory_status") == "READ_ONLY_UNCHANGED"
                and step_payload.get("context_status") == "CONTEXT_CANDIDATE_AVAILABLE"
                and event.get("memory_observation") is None,
                "cue routing differs",
            )
            verified_hypothesis = _verify_hypothesis(hypothesis, "AUDITORY" if index == 16 else "VISUAL")
            _require(
                step_payload.get("hypothesis_digest") == verified_hypothesis["hypothesis_digest"],
                "step hypothesis binding differs",
            )
        prior_snapshot = snapshot

    final_open = _verify_snapshot(execution.get("final_open_snapshot"))
    closed = _verify_snapshot(execution.get("closed_snapshot"))
    _require(final_open == events[-1]["post_snapshot"], "final open snapshot differs")
    _require(
        final_open["status"] == "OPEN"
        and final_open["processed_event_count"] == 18
        and final_open["field_attempt_count"] == 18
        and final_open["memory_formation_attempt_count"] == 16
        and final_open["scan_attempt_count"] == 4,
        "final runtime counters differ",
    )
    close_payload = dict(closed)
    open_payload = dict(final_open)
    close_payload.pop("snapshot_digest")
    open_payload.pop("snapshot_digest")
    _require(close_payload.pop("status") == "CLOSED" and open_payload.pop("status") == "OPEN", "close state differs")
    _require(close_payload == open_payload, "close changed runtime components")
    _require(
        events[15]["post_snapshot"]["memory_state_digest"]
        == events[16]["post_snapshot"]["memory_state_digest"]
        == events[17]["post_snapshot"]["memory_state_digest"],
        "cue changed memory",
    )

    final_memory = events[15]["memory_observation"]
    first_memory = events[0]["memory_observation"]
    target_av = first_memory["b4"][0]["values_digest"]
    target_audio = first_memory["fast"][0]["auditory_values_digest"]
    target_visual = first_memory["fast"][0]["visual_values_digest"]
    target_absent = all(item["values_digest"] != target_av for item in final_memory["b4"]) and all(
        item["auditory_values_digest"] != target_audio
        or item["visual_values_digest"] != target_visual
        for item in final_memory["fast"]
    )
    auditory_stable = [item for item in final_memory["auditory_slow"] if item["support_count"] >= 3]
    visual_stable = [item for item in final_memory["visual_slow"] if item["support_count"] >= 3]
    auditory_hypothesis = events[16]["runtime_step"]["hypothesis"]
    visual_hypothesis = events[17]["runtime_step"]["hypothesis"]
    functional_projection = {
        "target_absent_from_a_recent": target_absent,
        "b4_formation_indexes": [item["formation_index"] for item in final_memory["b4"]],
        "auditory_stable_support": None if len(auditory_stable) != 1 else auditory_stable[0]["support_count"],
        "visual_stable_support": None if len(visual_stable) != 1 else visual_stable[0]["support_count"],
        "auditory_area": auditory_hypothesis["payload"]["area"],
        "visual_area": visual_hypothesis["payload"]["area"],
        "event_count": final_open["processed_event_count"],
        "field_attempt_count": final_open["field_attempt_count"],
        "memory_formation_attempt_count": final_open["memory_formation_attempt_count"],
        "scan_attempt_count": final_open["scan_attempt_count"],
        "field_contact_count": 5_712,
        "memory_read_only_during_cues": True,
        "runtime_closed": True,
    }
    reference = _reference_projection(workspace_root)
    reference_equal = all(
        functional_projection[key] == reference[key]
        for key in (
            "target_absent_from_a_recent", "auditory_stable_support", "visual_stable_support",
            "auditory_area", "visual_area", "event_count", "field_attempt_count",
            "memory_formation_attempt_count", "scan_attempt_count",
        )
    )
    confirmed = (
        reference["status"] == "S2LN_ROLE_FREE_DISTRIBUTED_AV_EXPERIENCE_CONFIRMED"
        and target_absent
        and functional_projection["b4_formation_indexes"] == list(range(8, 17))
        and functional_projection["auditory_stable_support"] == 3
        and functional_projection["visual_stable_support"] == 3
        and reference_equal
    )
    expected_evaluation_payload = {
        "status": (
            "S2MS_MINIMAL_RUNTIME_S2LN_REPRODUCTION_CONFIRMED"
            if confirmed
            else "S2MS_FUNCTION_FALSIFIED"
        ),
        "functional_projection": functional_projection,
        "s2ln_reference_projection": reference,
        "functional_projection_matches_s2ln": reference_equal,
        "runtime_dependent_digest_equality_required": False,
        "hypothesis_applied": False,
        "completion_performed": False,
    }
    expected_evaluation = {
        **expected_evaluation_payload,
        "evaluation_digest": _digest(expected_evaluation_payload),
    }
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
    except S2MSVerificationError:
        raise
    except Exception as exc:
        raise S2MSVerificationError("result cannot be parsed or verified") from exc
    payload = {
        "verification_status": record["technical_status"],
        "run_id": AUTHORIZED_RUN_ID,
        "record_digest": record["record_digest"],
        "read_only": True,
    }
    return {**payload, "verification_digest": _digest(payload)}


__all__: tuple[str, ...] = ()
