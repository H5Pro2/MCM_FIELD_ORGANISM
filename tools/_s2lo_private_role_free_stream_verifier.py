"""Independent read-only verifier for one bounded S2-LO result."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


S2LO_SCHEMA = "s2lo.role-free-distributed-stream.v1"
S2LO_RESULT_SCHEMA = "s2lo.role-free-distributed-result.v1"
S2LM_SCHEMA = "s2lm.role-free-perception-stream.v1"
QUALIFICATION_ID = "s2lo-neutral-qualification-20260904-03"
MAX_RESULT_BYTES = 1_048_576
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

SOURCE_PATHS = (
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/finite_video_path.py",
    "mcm_field_organism/log_spectral_receptor.py",
    "mcm_field_organism/broadband_hearing_path.py",
    "tools/_s2jt_private_timed_field_projection.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2kq_private_partial_cue_retrieval_336.py",
    "tools/_s2kq_private_direct_slot_scan_baseline.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_direct_auditory_slot_scan_baseline.py",
    "tools/_s2lm_private_role_free_stream_processor.py",
    "tools/_s2lo_private_role_free_stream_runner.py",
    "tools/_s2lo_private_role_free_stream_verifier.py",
)

_FORMATION_CONTENTS = (
    "c00", "c01", "c00", "c02", "c00", "c03", "c00", "c04",
    "c05", "c06", "c07", "c08", "c09", "c01", "c02", "c03",
)


class S2LOVerificationError(ValueError):
    """The result cannot be accepted without executing project functions."""


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
        raise S2LOVerificationError(message)


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


MAIN_SPECS = tuple(
    _spec(index, "COMPLETE_AV_PERCEPTION", content)
    for index, content in enumerate(_FORMATION_CONTENTS, start=1)
) + (
    _spec(17, "PARTIAL_AUDITORY_CUE", None),
    _spec(18, "PARTIAL_VISUAL_CUE", None),
)
QUALIFICATION_SPECS = (
    _spec(1, "COMPLETE_AV_PERCEPTION", "c04"),
    _spec(2, "PARTIAL_AUDITORY_CUE", None),
    _spec(3, "PARTIAL_VISUAL_CUE", None),
)


def _verify_sources(value: object, workspace_root: Path) -> None:
    _require(type(value) is dict and set(value) == set(SOURCE_PATHS), "source set differs")
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        _require(path.is_file(), f"bound source is absent: {relative}")
        _require(value[relative] == hashlib.sha256(path.read_bytes()).hexdigest(), f"source changed: {relative}")


def _reject_raw(value: object) -> None:
    forbidden = {
        "raw_bytes", "rgb_bytes", "frame_bytes", "image", "audio_window",
        "pcm_values", "pcm_samples", "raw_payload",
    }
    if type(value) is dict:
        _require(not forbidden.intersection(value), "raw payload appears in result")
        for item in value.values():
            _reject_raw(item)
    elif type(value) is list:
        for item in value:
            _reject_raw(item)


def _verify_scan(value: object, role: str, memory_digest: str) -> None:
    _require(type(value) is dict, "scan result is absent")
    _require(value.get("scan_role") == role, "scan role differs")
    _require(
        value.get("prestate_digest") == memory_digest
        and value.get("poststate_digest") == memory_digest,
        "scan changed memory",
    )
    _require(_valid_digest(value.get("input_digest")), "scan input digest differs")
    _require(_valid_digest(value.get("receipt_digest")), "scan receipt differs")
    hypothesis = value.get("hypothesis")
    if hypothesis is None:
        _require(value.get("hypothesis_digest") is None, "absent hypothesis has a digest")
        return
    _require(type(hypothesis) is dict, "hypothesis form differs")
    _require(hypothesis.get("hypothesis_digest") == value.get("hypothesis_digest"), "hypothesis binding differs")
    hypothesis_payload = dict(hypothesis)
    hypothesis_digest = hypothesis_payload.pop("hypothesis_digest", None)
    _require(hypothesis_digest == _digest(hypothesis_payload), "hypothesis digest is inconsistent")
    positions = hypothesis.get("masked_positions", hypothesis.get("masked_bands"))
    proposed = hypothesis.get("proposed_values")
    _require(type(positions) is list and type(proposed) is list, "hypothesis values differ")
    _require(len(positions) == len(proposed) and len(positions) in {24, 256}, "hypothesis dimension differs")
    _require(hypothesis.get("area") in {"A_RECENT", "B_STABLE", "B_STABLE_AUDITORY"}, "hypothesis area differs")


def _verify_memory_observation(value: object, formation_count: int, state_digest: str) -> None:
    _require(type(value) is dict, "memory observation is absent")
    _require(value.get("state_digest") == state_digest and value.get("generation") == formation_count, "memory observation state differs")
    formation = value.get("formation_values")
    _require(type(formation) is dict, "formation values are absent")
    auditory = formation.get("auditory")
    visual = formation.get("visual")
    _require(type(auditory) is list and len(auditory) == 48, "auditory formation dimension differs")
    _require(type(visual) is list and len(visual) == 288, "visual formation dimension differs")
    _require(formation.get("auditory_digest") == _digest(auditory), "auditory formation digest differs")
    _require(formation.get("visual_digest") == _digest(visual), "visual formation digest differs")
    _require(formation.get("av_digest") == _digest(auditory + visual), "AV formation digest differs")
    b4 = value.get("b4")
    _require(type(b4) is list, "B4 observation differs")
    indexes = [item.get("formation_index") for item in b4 if type(item) is dict]
    expected = list(range(max(1, formation_count - 8), formation_count + 1))
    _require(indexes == expected, "B4 FIFO anatomy differs")
    for bank, dimension in (("auditory_slow", 48), ("visual_slow", 288)):
        slots = value.get(bank)
        _require(type(slots) is list, "Slow observation differs")
        for slot in slots:
            _require(type(slot) is dict, "Slow slot form differs")
            values = slot.get("prototype_values")
            _require(type(values) is list and len(values) == dimension, "Slow prototype dimension differs")
            _require(slot.get("prototype_digest") == _digest(values), "Slow prototype digest differs")
            _require(type(slot.get("support_count")) is int and 1 <= slot["support_count"] <= 3, "Slow support differs")


def _verify_field_observation(value: object, phase: str, step_count: int) -> None:
    _require(type(value) is dict and value.get("phase") == phase, "field phase differs")
    _require(value.get("step_count") == step_count, "field step differs")
    component_digest = value.get("field_component_digest")
    _require(_valid_digest(component_digest), "field component digest differs")
    state_payload = {
        "schema": S2LO_SCHEMA,
        "phase": phase,
        "field_component_digest": component_digest,
        "last_end_tick": value.get("last_end_tick"),
        "step_count": step_count,
    }
    _require(value.get("state_digest") == _digest(state_payload), "field state digest differs")
    pre_contact = value.get("pre_contact_payload")
    if phase == "PRE_CONTACT":
        _require(step_count == 0 and value.get("last_end_tick") == 0, "PRE_CONTACT lifecycle differs")
        _require(type(pre_contact) is dict, "PRE_CONTACT payload is absent")
        _require(
            pre_contact.get("schema") == "s2lo.pre-contact-field.v1"
            and pre_contact.get("phase") == "PRE_CONTACT"
            and _digest(pre_contact) == component_digest,
            "PRE_CONTACT binding differs",
        )
        components = pre_contact.get("null_components")
        _require(type(components) is list and len(components) == 336, "PRE_CONTACT null inventory differs")
        _require(
            all(
                type(item) is dict
                and item.get("activation") == 0.0
                and item.get("afterimage") == 0.0
                and item.get("perception_tick") == 0
                and item.get("receptor_contact") == 0.0
                and item.get("local_sample_count") == 0
                for item in components
            ),
            "PRE_CONTACT contains a non-null component",
        )
    else:
        _require(
            phase == "COMPLETED"
            and step_count > 0
            and type(value.get("last_end_tick")) is int
            and value["last_end_tick"] > 0
            and pre_contact is None,
            "COMPLETED field lifecycle differs",
        )


def _verify_events(events: object, specs: tuple[dict[str, object], ...], final_memory: str) -> None:
    _require(type(events) is list and len(events) == len(specs), "event cardinality differs")
    prior = None
    formation_count = 0
    for value, spec in zip(events, specs, strict=True):
        _require(type(value) is dict, "event form differs")
        for key in ("event_code", "event_id", "ordinal", "event_type", "content_id"):
            _require(value.get(key) == spec[key], f"event {key} differs")
        _require(value.get("event_spec_digest") == spec["spec_digest"], "event spec digest differs")
        for key in (
            "source_digest", "source_receipt_digest", "perception_digest", "event_digest",
            "prestate_digest", "poststate_digest", "field_receipt_digest",
            "field_poststate_digest", "memory_poststate_digest",
            "owner_poststate_digest", "result_digest",
        ):
            _require(_valid_digest(value.get(key)), f"event {key} differs")
        if prior is not None:
            _require(value.get("prestate_digest") == prior, "stream chain differs")
        prior = value["poststate_digest"]
        _require(value.get("owner_status") == "CONSUMED" and value.get("error_codes") == [], "event did not complete")
        event_payload = {
            "schema": S2LM_SCHEMA,
            "event_id": value["event_id"],
            "ordinal": value["ordinal"],
            "event_type": value["event_type"],
            "source_digest": value["source_digest"],
            "perception_digest": value["perception_digest"],
            "field_projection_digest": value["perception_digest"],
            "operation_projection_digest": value["perception_digest"],
        }
        _require(value["event_digest"] == _digest(event_payload), "event digest differs")
        _verify_field_observation(value.get("field_observation"), "COMPLETED", value["ordinal"])
        _require(value["field_observation"]["state_digest"] == value["field_poststate_digest"], "field poststate binding differs")
        if value["event_type"] == "COMPLETE_AV_PERCEPTION":
            formation_count += 1
            _require(_valid_digest(value.get("memory_receipt_digest")), "formation receipt differs")
            _require(value.get("primary_scan") is None and value.get("baseline_scan") is None, "formation contains a scan")
            _verify_memory_observation(value.get("memory_observation"), formation_count, value["memory_poststate_digest"])
        else:
            _require(value.get("memory_receipt_digest") is None, "cue contains a formation")
            _require(value.get("memory_observation") is None, "cue contains a memory observation")
            _verify_scan(value.get("primary_scan"), "PRIMARY", final_memory)
            _verify_scan(value.get("baseline_scan"), "DIRECT_BASELINE", final_memory)
        result_payload = {
            "schema": S2LM_SCHEMA,
            "event_digest": value["event_digest"],
            "prestate_digest": value["prestate_digest"],
            "poststate_digest": value["poststate_digest"],
            "field_receipt_digest": value["field_receipt_digest"],
            "memory_receipt_digest": value.get("memory_receipt_digest"),
            "primary_scan_receipt_digest": None if value.get("primary_scan") is None else value["primary_scan"]["receipt_digest"],
            "baseline_scan_receipt_digest": None if value.get("baseline_scan") is None else value["baseline_scan"]["receipt_digest"],
            "error_codes": value["error_codes"],
            "owner_poststate_digest": value["owner_poststate_digest"],
        }
        _require(value["result_digest"] == _digest(result_payload), "event result digest differs")


def _verify_main_function(execution: dict[str, object], evaluation: dict[str, object]) -> None:
    events = execution["events"]
    _require(type(events) is list and len(events) == 18, "main event evidence differs")
    transition_events = [events[index] for index in (2, 4, 6)]

    def verify_transition(modality: str) -> bool:
        prior = None
        for support, event in enumerate(transition_events, start=1):
            observation = event["memory_observation"]
            source_values = observation["formation_values"][modality]
            slots = observation[f"{modality}_slow"]
            _require(type(source_values) is list and type(slots) is list, "PPB transition form differs")
            if len(slots) != 1 or slots[0].get("support_count") != support:
                return False
            actual = slots[0]["prototype_values"]
            expected = source_values if prior is None else [
                (1.0 - 0.05) * previous + 0.05 * current
                for previous, current in zip(prior, source_values, strict=True)
            ]
            if actual != expected or slots[0].get("prototype_digest") != _digest(actual):
                return False
            prior = actual
        return True

    transition = {
        "auditory": verify_transition("auditory"),
        "visual": verify_transition("visual"),
        "event_codes": [event["event_code"] for event in transition_events],
        "support_chain": [1, 2, 3],
    }
    _require(evaluation.get("ppb_transition_integrity") == transition, "PPB transition evaluation differs")
    final_observation = events[15]["memory_observation"]
    b4_indexes = [item["formation_index"] for item in final_observation["b4"]]
    _require(b4_indexes == list(range(8, 17)), "final B4 anatomy differs")
    _require(evaluation.get("b4_formation_indexes") == b4_indexes, "B4 evaluation differs")

    target = events[0]["memory_observation"]["formation_values"]
    target_absent = all(
        item["values_digest"] != target["av_digest"] for item in final_observation["b4"]
    ) and all(
        item["auditory_values_digest"] != target["auditory_digest"]
        or item["visual_values_digest"] != target["visual_digest"]
        for item in final_observation["fast"]
    )
    _require(evaluation.get("target_absent_from_a_recent") is target_absent, "A_RECENT evaluation differs")
    _require(
        len(final_observation["auditory_slow"]) == 1
        and len(final_observation["visual_slow"]) == 1
        and final_observation["auditory_slow"][0]["support_count"] == 3
        and final_observation["visual_slow"][0]["support_count"] == 3,
        "final stable bank evidence differs",
    )
    _require(evaluation.get("primary_baseline_equal") is True, "scan baseline differs")
    _require(evaluation.get("memory_read_only_during_cues") is True, "cue read-only result differs")


def _verify_record(record: object, workspace_root: Path, expected_mode: str) -> None:
    _require(type(record) is dict and record.get("schema") == S2LO_RESULT_SCHEMA, "result schema differs")
    _require(record.get("mode") == expected_mode, "result mode differs")
    payload = dict(record)
    record_digest = payload.pop("record_digest", None)
    _require(record_digest == _digest(payload), "record digest differs")
    _verify_sources(record.get("source_hashes"), workspace_root)
    _reject_raw(record)
    _require(record.get("technical_status") == "RECORDING_COMPLETE", "recording is incomplete")
    plan = record.get("plan")
    execution = record.get("execution")
    _require(type(plan) is dict and type(execution) is dict, "plan or execution is absent")
    counters = execution.get("counters")
    _require(type(counters) is dict and counters.get("stream_status") == "OPEN", "stream counters differ")
    final_memory = counters.get("final_memory_digest")
    _require(_valid_digest(final_memory), "final memory digest differs")
    _verify_field_observation(execution.get("initial_field_observation"), "PRE_CONTACT", 0)
    if expected_mode == "QUALIFICATION":
        _require(plan.get("qualification_id") == QUALIFICATION_ID, "qualification id differs")
        _require(plan.get("main_execution_enabled") is False, "main gate was open")
        _require(plan.get("main_story_executed") is False, "main story was executed")
        _require(plan.get("raw_payload_retained") is False, "raw payload retention differs")
        _require(plan.get("event_spec_digests") == [item["spec_digest"] for item in QUALIFICATION_SPECS], "qualification plan differs")
        _require(
            (counters.get("event_count"), counters.get("field_attempt_count"), counters.get("memory_formation_attempt_count"), counters.get("scan_attempt_count"))
            == (3, 3, 1, 4),
            "qualification counters differ",
        )
        _verify_events(execution.get("events"), QUALIFICATION_SPECS, final_memory)
        _require(record.get("evaluation") is None, "qualification contains evaluation")
        return
    _require(expected_mode == "MAIN", "unsupported verification mode")
    _require(
        plan.get("event_spec_digests") == [item["spec_digest"] for item in MAIN_SPECS]
        and plan.get("event_count") == 18
        and plan.get("formation_count") == 16
        and plan.get("field_contacts") == 5_712
        and plan.get("memory_l1_terms") == 56_832
        and plan.get("scan_comparisons_max") == 2_656
        and plan.get("raw_bytes_max") == 106_080_000
        and plan.get("raw_payload_retained") is False,
        "main plan differs",
    )
    _require(
        (counters.get("event_count"), counters.get("field_attempt_count"), counters.get("memory_formation_attempt_count"), counters.get("scan_attempt_count"))
        == (18, 18, 16, 4),
        "main counters differ",
    )
    _verify_events(execution.get("events"), MAIN_SPECS, final_memory)
    evaluation = record.get("evaluation")
    _require(type(evaluation) is dict, "main evaluation is absent")
    evaluation_payload = dict(evaluation)
    evaluation_digest = evaluation_payload.pop("evaluation_digest", None)
    _require(evaluation_digest == _digest(evaluation_payload), "evaluation digest differs")
    _require(
        evaluation.get("status") in {
            "S2LN_ROLE_FREE_DISTRIBUTED_AV_EXPERIENCE_CONFIRMED",
            "S2LN_FUNCTION_FALSIFIED",
        },
        "evaluation status differs",
    )
    _verify_main_function(execution, evaluation)


def verify_result_file(
    result_path: Path,
    workspace_root: Path,
    *,
    expected_mode: str,
) -> dict[str, object]:
    _require(
        isinstance(result_path, Path)
        and result_path.is_absolute()
        and isinstance(workspace_root, Path)
        and workspace_root.is_absolute(),
        "verification paths must be absolute Path instances",
    )
    try:
        data = result_path.read_bytes()
        _require(len(data) <= MAX_RESULT_BYTES, "result exceeds bounded size")
        _require(data.endswith(b"\n"), "canonical line ending is absent")
        record = json.loads(data.decode("ascii"))
        _require(data == _canonical_bytes(record, newline=True), "serialization is not canonical")
        _verify_record(record, workspace_root, expected_mode)
    except S2LOVerificationError:
        raise
    except Exception as exc:
        raise S2LOVerificationError("result cannot be parsed or verified") from exc
    payload = {
        "verification_status": "RECORDING_COMPLETE",
        "mode": expected_mode,
        "record_digest": record["record_digest"],
        "read_only": True,
    }
    return {**payload, "verification_digest": _digest(payload)}


__all__: tuple[str, ...] = ()
