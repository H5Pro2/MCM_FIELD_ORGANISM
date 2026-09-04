"""Independent read-only verifier for bounded private S2-LQ results."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from tools import _s2lo_private_role_free_stream_verifier as lo_verifier


S2LQ_SCHEMA = "s2lq.role-free-multipattern-stream.v1"
S2LQ_RESULT_SCHEMA = "s2lq.role-free-multipattern-result.v1"
QUALIFICATION_ID = "s2lq-neutral-qualification-20260904-01"
AUTHORIZED_RUN_ID = "s2lq-main-not-authorized"
MAX_RESULT_BYTES = 1_048_576
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

SOURCE_PATHS = (
    *lo_verifier.SOURCE_PATHS,
    "tools/_s2lq_private_multipattern_stream_runner.py",
    "tools/_s2lq_private_multipattern_stream_verifier.py",
)

_FORMATION_CONTENTS = (
    "p00", "p01", "p02", "p00", "p01", "p00", "p01", "p00", "p01",
    "p02", "p02", "p03", "p04", "p05", "p06", "p07", "p08", "p09",
    "p10", "p11", "p12",
)
_CUE_CONTENTS = (
    ("PARTIAL_AUDITORY_CUE", "p00"),
    ("PARTIAL_VISUAL_CUE", "p00"),
    ("PARTIAL_AUDITORY_CUE", "p01"),
    ("PARTIAL_VISUAL_CUE", "p01"),
    ("PARTIAL_AUDITORY_CUE", "p02"),
    ("PARTIAL_VISUAL_CUE", "p02"),
    ("PARTIAL_AUDITORY_CUE", "p03"),
    ("PARTIAL_VISUAL_CUE", "p03"),
)


class S2LQVerificationError(ValueError):
    """The S2-LQ result is not independently acceptable."""


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
        raise S2LQVerificationError(message)


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _spec(ordinal: int, event_type: str, content_id: str) -> dict[str, object]:
    code = f"e{ordinal:02d}"
    payload = {
        "schema": S2LQ_SCHEMA,
        "event_code": code,
        "event_id": f"s2lq-event-{code}",
        "ordinal": ordinal,
        "event_type": event_type,
        "content_id": content_id,
    }
    return {**payload, "spec_digest": _digest(payload)}


MAIN_SPECS = tuple(
    _spec(index, "COMPLETE_AV_PERCEPTION", content)
    for index, content in enumerate(_FORMATION_CONTENTS, start=1)
) + tuple(
    _spec(index, event_type, content)
    for index, (event_type, content) in enumerate(_CUE_CONTENTS, start=22)
)
QUALIFICATION_SOURCE_SPECS = tuple(
    _spec(index, "COMPLETE_AV_PERCEPTION", content)
    for index, content in enumerate(("p00", "p01", "p02", "p03"), start=1)
)


def _verify_sources(value: object, workspace_root: Path) -> None:
    _require(type(value) is dict and set(value) == set(SOURCE_PATHS), "source set differs")
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        _require(path.is_file(), f"bound source is absent: {relative}")
        _require(
            value[relative] == hashlib.sha256(path.read_bytes()).hexdigest(),
            f"source changed: {relative}",
        )


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


def _verify_multislot(value: object) -> None:
    _require(type(value) is dict and set(value) == {"auditory", "visual"}, "multislot inventory differs")
    for modality in ("auditory", "visual"):
        bank = value[modality]
        _require(type(bank) is dict, "modality inventory differs")
        _require(
            bank.get("occupied_slot_count") == 3
            and bank.get("stable_slot_count") == 2
            and bank.get("support_by_content") == {"p00": 3, "p01": 3, "p02": 2},
            "support inventory differs",
        )
        chains = bank.get("transition_chains")
        _require(type(chains) is dict and set(chains) == {"p00", "p01", "p02"}, "chain inventory differs")
        for content, supports in (("p00", [1, 2, 3]), ("p01", [1, 2, 3]), ("p02", [1, 2])):
            chain = chains[content]
            _require(
                type(chain) is dict
                and type(chain.get("slot_id")) is str
                and chain.get("support_chain") == supports
                and chain.get("transition_integrity") is True
                and len(chain.get("event_codes", ())) == len(supports)
                and len(chain.get("prototype_digests", ())) == len(supports)
                and all(_valid_digest(item) for item in chain["prototype_digests"]),
                "transition chain differs",
            )
        final_digests = bank.get("final_slot_digests")
        _require(
            type(final_digests) is dict
            and set(final_digests) == {"p00", "p01", "p02"}
            and all(_valid_digest(item) for item in final_digests.values()),
            "final prototype inventory differs",
        )


def _verify_qualification(record: dict[str, object]) -> None:
    plan = record.get("plan")
    _require(type(plan) is dict, "qualification plan differs")
    _require(
        plan.get("qualification_id") == QUALIFICATION_ID
        and plan.get("main_execution_enabled") is False
        and plan.get("authorized_run_id") == AUTHORIZED_RUN_ID
        and plan.get("main_story_executed") is False
        and plan.get("main_event_count") == 29
        and plan.get("main_formation_count") == 21
        and plan.get("main_cue_count") == 8
        and plan.get("raw_payload_retained") is False,
        "qualification plan binding differs",
    )
    bindings = record.get("source_bindings")
    _require(type(bindings) is list and len(bindings) == 4, "source binding count differs")
    for binding, spec in zip(bindings, QUALIFICATION_SOURCE_SPECS, strict=True):
        binding_payload = dict(binding) if type(binding) is dict else {}
        binding_digest = binding_payload.pop("binding_digest", None)
        _require(
            type(binding) is dict
            and binding_digest == _digest(binding_payload)
            and binding.get("event_spec_digest") == spec["spec_digest"]
            and binding.get("auditory_dimension") == 48
            and binding.get("visual_dimension") == 288
            and all(
                _valid_digest(binding.get(key))
                for key in ("source_digest", "source_receipt_digest", "pairing_digest")
            ),
            "qualification source binding differs",
        )
    _require(
        record.get("qualification_counters")
        == {
            "source_binding_count": 4,
            "field_calls": 0,
            "memory_calls": 0,
            "scan_calls": 0,
            "main_events_processed": 0,
        },
        "qualification counters differ",
    )
    _verify_multislot(record.get("multislot_inventory"))
    read_only = record.get("read_only_evidence")
    _require(
        type(read_only) is dict
        and _valid_digest(read_only.get("prestate_digest"))
        and read_only.get("prestate_digest") == read_only.get("poststate_digest"),
        "read-only evidence differs",
    )
    _require(
        record.get("interference_classification")
        == "SENSOR_CONFUSION_WITH_EXISTING_STABLE_CONTENT",
        "interference classification differs",
    )
    _require(record.get("evaluation") is None, "qualification contains an evaluation")


def _slot_map(observation: dict[str, object], bank: str) -> dict[str, dict[str, object]]:
    slots = observation.get(bank)
    _require(type(slots) is list, "Slow inventory differs")
    result = {}
    for slot in slots:
        _require(type(slot) is dict and type(slot.get("slot_id")) is str, "Slow slot differs")
        _require(slot["slot_id"] not in result, "duplicate Slow slot")
        result[slot["slot_id"]] = slot
    return result


def _verify_transition_chains(events: list[dict[str, object]], inventory: dict[str, object]) -> None:
    expected_indexes = {"p00": (3, 5, 7), "p01": (4, 6, 8), "p02": (9, 10)}
    for modality in ("auditory", "visual"):
        bank_name = f"{modality}_slow"
        chains = inventory[modality]["transition_chains"]
        for content, indexes in expected_indexes.items():
            chain = chains[content]
            prior = None
            for support, (event_index, event_code, prototype_digest) in enumerate(
                zip(indexes, chain["event_codes"], chain["prototype_digests"], strict=True),
                start=1,
            ):
                event = events[event_index]
                _require(event["event_code"] == event_code, "transition event differs")
                observation = event["memory_observation"]
                source = observation["formation_values"][modality]
                expected = source if prior is None else [
                    (1.0 - 0.05) * previous + 0.05 * current
                    for previous, current in zip(prior, source, strict=True)
                ]
                slot = _slot_map(observation, bank_name).get(chain["slot_id"])
                _require(
                    type(slot) is dict
                    and slot.get("support_count") == support
                    and slot.get("prototype_values") == expected
                    and slot.get("prototype_digest") == prototype_digest == _digest(expected),
                    "PPB transition evidence differs",
                )
                prior = expected


def _verify_main(record: dict[str, object]) -> None:
    plan = record.get("plan")
    execution = record.get("execution")
    _require(type(plan) is dict and type(execution) is dict, "main plan or execution differs")
    _require(
        plan.get("event_spec_digests") == [item["spec_digest"] for item in MAIN_SPECS]
        and plan.get("event_count") == 29
        and plan.get("formation_count") == 21
        and plan.get("auditory_cue_count") == 4
        and plan.get("visual_cue_count") == 4
        and plan.get("field_contacts") == 8_400
        and plan.get("memory_l1_terms") == 74_592
        and plan.get("scan_comparisons_max") == 10_624
        and plan.get("raw_bytes_max") == 156_000_000
        and plan.get("raw_payload_retained") is False,
        "main plan differs",
    )
    preflight = record.get("source_geometry_preflight")
    _require(type(preflight) is dict, "source preflight differs")
    preflight_payload = dict(preflight)
    preflight_digest = preflight_payload.pop("preflight_digest", None)
    _require(
        preflight_digest == _digest(preflight_payload)
        and preflight.get("source_count") == 29
        and preflight.get("formation_count") == 21
        and preflight.get("cue_count") == 8
        and preflight.get("memory_calls") == 0,
        "source preflight binding differs",
    )
    counters = execution.get("counters")
    _require(
        type(counters) is dict
        and (
            counters.get("event_count"),
            counters.get("field_attempt_count"),
            counters.get("memory_formation_attempt_count"),
            counters.get("scan_attempt_count"),
            counters.get("stream_status"),
        )
        == (29, 29, 21, 16, "OPEN"),
        "main counters differ",
    )
    final_memory = counters.get("final_memory_digest")
    _require(_valid_digest(final_memory), "final memory digest differs")
    lo_verifier._verify_field_observation(execution.get("initial_field_observation"), "PRE_CONTACT", 0)
    try:
        lo_verifier._verify_events(execution.get("events"), MAIN_SPECS, final_memory)
    except lo_verifier.S2LOVerificationError as exc:
        raise S2LQVerificationError("S2-LO stream evidence differs") from exc
    events = execution["events"]
    evaluation = record.get("evaluation")
    _require(type(evaluation) is dict, "main evaluation differs")
    evaluation_payload = dict(evaluation)
    evaluation_digest = evaluation_payload.pop("evaluation_digest", None)
    _require(evaluation_digest == _digest(evaluation_payload), "evaluation digest differs")
    _require(
        evaluation.get("status")
        in {"S2LQ_MULTIPATTERN_STREAM_CONFIRMED", "S2LQ_MULTIPATTERN_STREAM_FALSIFIED"},
        "evaluation status differs",
    )
    inventory = evaluation.get("multislot_inventory")
    _verify_multislot(inventory)
    _verify_transition_chains(events, inventory)
    _require(evaluation.get("b4_formation_indexes") == list(range(13, 22)), "B4 result differs")
    _require(
        evaluation.get("content_absent_from_a_recent")
        == {"p00": True, "p01": True, "p02": True, "p03": True},
        "A_RECENT absence differs",
    )
    scan_results = evaluation.get("scan_results")
    expected = (
        "ADMIT_SINGLE_CONTEXT", "ADMIT_SINGLE_CONTEXT",
        "ADMIT_SINGLE_CONTEXT", "ADMIT_SINGLE_CONTEXT",
        "ABSTAIN_INTERNAL_AMBIGUITY", "ABSTAIN_NO_APPLICABLE_CONTEXT",
        "ADMIT_SINGLE_CONTEXT", "ABSTAIN_NO_APPLICABLE_CONTEXT",
    )
    _require(type(scan_results) is list and len(scan_results) == 8, "scan evaluation differs")
    _require(
        all(
            item.get("event_code") == f"e{index:02d}"
            and item.get("decision") == decision
            and item.get("expected_decision") == decision
            and item.get("baseline_equal") is True
            for index, (item, decision) in enumerate(zip(scan_results, expected, strict=True), start=22)
        ),
        "scan decisions differ",
    )
    _require(
        evaluation.get("interference_classification")
        == "SENSOR_CONFUSION_WITH_EXISTING_STABLE_CONTENT"
        and evaluation.get("memory_read_only_during_cues") is True
        and evaluation.get("primary_baseline_equal") is True,
        "interference or read-only evaluation differs",
    )


def _verify_record(record: object, workspace_root: Path, expected_mode: str) -> None:
    _require(
        type(record) is dict
        and record.get("schema") == S2LQ_RESULT_SCHEMA
        and record.get("mode") == expected_mode
        and record.get("technical_status") == "RECORDING_COMPLETE",
        "result envelope differs",
    )
    payload = dict(record)
    record_digest = payload.pop("record_digest", None)
    _require(record_digest == _digest(payload), "record digest differs")
    _verify_sources(record.get("source_hashes"), workspace_root)
    _reject_raw(record)
    if expected_mode == "QUALIFICATION":
        _verify_qualification(record)
    elif expected_mode == "MAIN":
        _verify_main(record)
    else:
        raise S2LQVerificationError("verification mode differs")


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
    except S2LQVerificationError:
        raise
    except Exception as exc:
        raise S2LQVerificationError("result cannot be parsed or verified") from exc
    payload = {
        "verification_status": "RECORDING_COMPLETE",
        "mode": expected_mode,
        "record_digest": record["record_digest"],
        "read_only": True,
    }
    return {**payload, "verification_digest": _digest(payload)}


__all__: tuple[str, ...] = ()
