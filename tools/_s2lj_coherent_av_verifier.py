"""Independent read-only verifier for the bounded private S2-LJ result."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


S2LJ_RESULT_SCHEMA = "s2lj.coherent-av-end-to-end-result.v1"
S2LJ_TRANSITION_SCHEMA = "s2lj.ppb-transition-proof.v1"
S2LJ_COMPLETION_SCHEMA = "s2lj.masked-context-completion.v1"
UPDATE_RATE = 0.05
EVENT_CHAIN = ("CREATED", "MATCHED", "MATCHED")
SUPPORT_CHAIN = (1, 2, 3)
MAX_RESULT_BYTES = 524_288
MAIN_FORMATION_COUNT = 13
MAIN_FIELD_GROUP_COUNT = 15

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
    "tools/_s2lj_coherent_av_fixtures.py",
    "tools/_s2lj_coherent_av_runner.py",
    "tools/_s2lj_coherent_av_verifier.py",
)


class S2LJVerificationError(ValueError):
    """The stored result cannot be verified without executing project functions."""


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
        raise S2LJVerificationError(message)


def _numeric_vector(value: object, dimension: int, role: str) -> tuple[float, ...]:
    _require(type(value) is list and len(value) == dimension, f"{role} dimension differs")
    _require(
        all(type(item) in (int, float) and math.isfinite(float(item)) for item in value),
        f"{role} contains a non-numeric value",
    )
    result = tuple(float(item) for item in value)
    _require(all(abs(item) <= 1.0 for item in result), f"{role} leaves receptor domain")
    return result


def _matched(previous: tuple[float, ...], current: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(
        (1.0 - UPDATE_RATE) * old + UPDATE_RATE * new
        for old, new in zip(previous, current, strict=True)
    )


def _verify_transition(value: object, modality: str) -> None:
    _require(type(value) is dict, "transition proof is not one object")
    dimension = 48 if modality == "AUDITORY" else 288
    _require(value.get("schema") == S2LJ_TRANSITION_SCHEMA, "transition schema differs")
    _require(value.get("modality") == modality, "transition modality differs")
    _require(value.get("dimension") == dimension, "transition dimension differs")
    _require(value.get("event_chain") == list(EVENT_CHAIN), "transition events differ")
    _require(value.get("support_chain") == list(SUPPORT_CHAIN), "transition supports differ")
    inputs_raw = value.get("input_values")
    recorded_raw = value.get("recorded_prototype_values")
    _require(type(inputs_raw) is list and len(inputs_raw) == 3, "PPB input chain differs")
    _require(type(recorded_raw) is list and len(recorded_raw) == 3, "PPB prototype chain differs")
    inputs = tuple(
        _numeric_vector(item, dimension, f"{modality} PPB input") for item in inputs_raw
    )
    recorded = tuple(
        _numeric_vector(item, dimension, f"{modality} PPB prototype")
        for item in recorded_raw
    )
    derived = (inputs[0],)
    derived += (_matched(derived[-1], inputs[1]),)
    derived += (_matched(derived[-1], inputs[2]),)
    _require(recorded == derived, "PPB prototype is not the exact transition result")
    _require(
        value.get("input_digests") == [_digest(list(item)) for item in inputs],
        "PPB input digests differ",
    )
    _require(
        value.get("prototype_digests") == [_digest(list(item)) for item in recorded],
        "PPB prototype digests differ",
    )
    masked = recorded[-1][24:] if modality == "AUDITORY" else recorded[-1][32:]
    _require(value.get("final_masked_digest") == _digest(list(masked)), "masked digest differs")
    _require(
        value.get("integrity_status") == "PPB_TRANSITION_INTEGRITY_VALID",
        "transition integrity status differs",
    )
    payload = dict(value)
    proof_digest = payload.pop("proof_digest", None)
    _require(proof_digest == _digest(payload), "transition proof digest differs")


def _verify_field(value: object, *, groups: int, events: int) -> None:
    _require(type(value) is dict, "field result is not one object")
    _require(value.get("group_count") == groups, "field group count differs")
    _require(value.get("event_count") == events, "field event count differs")
    points = value.get("point_digests")
    _require(type(points) is list and len(points) == groups, "field trajectory differs")
    _require(len(set(points)) == len(points), "field trajectory digests repeat")
    _require(value.get("initial_fields_distinct") is True, "field arms are not distinct")
    _require(value.get("initial_fields_zero") is True, "field arms do not start at zero")
    _require(value.get("final_components_equal") is True, "field components differ")
    _require(value.get("final_digests_equal") is True, "field digests differ")
    _require(
        value.get("observed_final_digest") == value.get("direct_final_digest"),
        "field final binding differs",
    )
    _require(value.get("nontrivial") is True, "field trajectory is trivial")


def _verify_completion(value: object, final_state: str, field_digest: str) -> None:
    _require(type(value) is dict, "completion is not one object")
    _require(value.get("schema") == S2LJ_COMPLETION_SCHEMA, "completion schema differs")
    modality = value.get("modality")
    dimension = 48 if modality == "AUDITORY" else 288 if modality == "VISUAL" else 0
    _require(dimension > 0, "completion modality differs")
    inputs = value.get("input_values")
    outputs = value.get("output_values")
    _require(type(inputs) is list and len(inputs) == dimension, "completion input differs")
    _require(type(outputs) is list and len(outputs) == dimension, "completion output differs")
    _require(value.get("visible_unchanged") is True, "visible values changed")
    _require(value.get("prestate_digest") == final_state, "completion prestate differs")
    _require(value.get("poststate_digest") == final_state, "completion poststate differs")
    _require(value.get("field_digest") == field_digest, "completion field binding differs")
    payload = dict(value)
    result_digest = payload.pop("result_digest", None)
    _require(result_digest == _digest(payload), "completion digest differs")


def _reject_raw_payloads(value: object) -> None:
    forbidden = {"raw_bytes", "rgb_bytes", "pcm_values", "image", "frame_bytes", "audio_window"}
    if type(value) is dict:
        _require(not forbidden.intersection(value), "stored result contains raw payload")
        for item in value.values():
            _reject_raw_payloads(item)
    elif type(value) is list:
        for item in value:
            _reject_raw_payloads(item)


def _verify_sources(source_hashes: object, workspace_root: Path) -> None:
    _require(type(source_hashes) is dict, "source hashes are absent")
    _require(set(source_hashes) == set(SOURCE_PATHS), "source set differs")
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        _require(path.is_file(), f"bound source is missing: {relative}")
        _require(
            source_hashes[relative] == hashlib.sha256(path.read_bytes()).hexdigest(),
            f"bound source changed: {relative}",
        )


def _verify_record(record: object, workspace_root: Path, expected_mode: str) -> None:
    _require(type(record) is dict, "result root differs")
    _require(record.get("schema") == S2LJ_RESULT_SCHEMA, "result schema differs")
    _require(record.get("mode") == expected_mode, "result mode differs")
    payload = dict(record)
    record_digest = payload.pop("record_digest", None)
    _require(record_digest == _digest(payload), "record digest differs")
    _verify_sources(record.get("source_hashes"), workspace_root)
    _reject_raw_payloads(record)
    if expected_mode == "QUALIFICATION":
        _require(record.get("technical_status") == "RECORDING_COMPLETE", "qualification is incomplete")
        plan = record.get("plan")
        _require(type(plan) is dict, "qualification plan differs")
        _require(plan.get("main_execution_enabled") is False, "main gate was open")
        _require(plan.get("main_authorized_run_id") is None, "main run was authorized")
        _require(plan.get("formation_count") == 1, "qualification formation count differs")
        _require(plan.get("field_group_count") == 1, "qualification field count differs")
        _require(plan.get("main_story_executed") is False, "main story was executed")
        _require(plan.get("raw_payload_retained") is False, "raw payload retention differs")
        _require(len(record.get("formations", [])) == 1, "qualification formations differ")
        transitions = record.get("transitions")
        _require(type(transitions) is list and len(transitions) == 2, "transition proof count differs")
        _verify_transition(transitions[0], "AUDITORY")
        _verify_transition(transitions[1], "VISUAL")
        _verify_field(record.get("field"), groups=1, events=2)
        _require(record.get("cue_sources") == [], "qualification contains a cue")
        _require(record.get("scan_results") == {}, "qualification contains a scan")
        _require(record.get("completions") == [], "qualification contains completion output")
        _require(record.get("evaluation") is None, "qualification contains an evaluation")
        return

    _require(expected_mode == "MAIN", "unsupported verification mode")
    plan = record.get("plan")
    _require(type(plan) is dict and plan.get("formation_count") == MAIN_FORMATION_COUNT, "main plan differs")
    status = record.get("technical_status")
    if status == "NOT_EVALUABLE":
        _require(record.get("execution") is None, "failed run contains execution evidence")
        return
    _require(status == "RECORDING_COMPLETE", "main technical status differs")
    execution = record.get("execution")
    _require(type(execution) is dict, "main execution evidence is absent")
    _require(len(execution.get("formations", [])) == MAIN_FORMATION_COUNT, "main formations differ")
    transitions = execution.get("transitions")
    _require(type(transitions) is list and len(transitions) == 2, "main transition count differs")
    _verify_transition(transitions[0], "AUDITORY")
    _verify_transition(transitions[1], "VISUAL")
    _verify_field(execution.get("field"), groups=MAIN_FIELD_GROUP_COUNT, events=28)
    completions = execution.get("completions")
    _require(type(completions) is list and len(completions) == 6, "completion count differs")
    final_state = execution.get("final_memory_digest")
    field_digest = execution["field"].get("observed_final_digest")
    _require(type(final_state) is str and len(final_state) == 64, "final memory digest differs")
    for completion in completions:
        _verify_completion(completion, final_state, field_digest)
    evaluation = execution.get("evaluation")
    _require(type(evaluation) is dict, "evaluation is absent")
    evaluation_payload = dict(evaluation)
    evaluation_digest = evaluation_payload.pop("evaluation_digest", None)
    _require(evaluation_digest == _digest(evaluation_payload), "evaluation digest differs")


def verify_result_file(
    result_path: Path,
    workspace_root: Path,
    *,
    expected_mode: str,
) -> dict[str, object]:
    if (
        not isinstance(result_path, Path)
        or not result_path.is_absolute()
        or not isinstance(workspace_root, Path)
        or not workspace_root.is_absolute()
    ):
        raise S2LJVerificationError("verification paths must be absolute Path instances")
    try:
        data = result_path.read_bytes()
        _require(len(data) <= MAX_RESULT_BYTES, "result exceeds the bounded envelope")
        _require(data.endswith(b"\n"), "result lacks its canonical line ending")
        record = json.loads(data.decode("ascii"))
        _require(data == _canonical_bytes(record, newline=True), "result serialization is not canonical")
        _verify_record(record, workspace_root, expected_mode)
    except S2LJVerificationError:
        raise
    except Exception as exc:
        raise S2LJVerificationError("result cannot be parsed or verified") from exc
    payload = {
        "verification_status": "RECORDING_COMPLETE",
        "mode": expected_mode,
        "record_digest": record["record_digest"],
        "read_only": True,
    }
    return {**payload, "verification_digest": _digest(payload)}


__all__: tuple[str, ...] = ()
