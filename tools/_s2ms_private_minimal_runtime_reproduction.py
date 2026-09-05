"""One bounded S2-LN reproduction through the public S2-MR runtime surface."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from threading import Lock

from tools import _s2kq_private_partial_cue_retrieval_336 as visual_scan
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as auditory_scan
from tools import _s2lm_private_role_free_stream_processor as stream
from tools import _s2lo_private_role_free_stream_runner as source_runtime
from tools import _s2mr_private_minimal_mcm_runtime as runtime
from tools import _s2jw_profiled_memory_coordinator as memory


S2MS_SCHEMA = "s2ms.private.minimal-runtime-reproduction.v1"
S2MS_RESULT_SCHEMA = "s2ms.private.minimal-runtime-reproduction-result.v1"
AUTHORIZED_RUN_ID = "s2ms-minimal-runtime-s2ln-20260905-01"
REFERENCE_RESULT = "reports/s2ln/s2ln-role-free-distributed-av-20260904-02/result.json"
REFERENCE_RESULT_SHA256 = "665155b9dd221f5347f82f211195e8258cc7e32f7fa9aeca2f2738bf90a626da"
MAIN_EVENT_COUNT = 18
MAIN_FORMATION_COUNT = 16
MAIN_FIELD_CONTACTS = 5_712
MAX_RESULT_BYTES = 262_144
MAIN_EXECUTION_ENABLED = False
_MAIN_USED = False
_MAIN_LOCK = Lock()
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")

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


class S2MSReproductionError(RuntimeError):
    """The bounded reproduction input, execution, or result is invalid."""


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
        raise S2MSReproductionError(message)


def _source_hashes(workspace_root: Path) -> dict[str, str]:
    result = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        _require(path.is_file(), f"bound source is absent: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _snapshot_record(value: runtime.MinimalMCMRuntimeSnapshot336V1) -> dict[str, object]:
    return {**value.payload_without_digest(), "snapshot_digest": value.snapshot_digest}


def _hypothesis_record(value: runtime.RuntimeHypothesis336V1 | None) -> dict[str, object] | None:
    if value is None:
        return None
    if type(value) is visual_scan.PartialCueContextHypothesis336V1:
        modality = "VISUAL"
    elif type(value) is auditory_scan.AuditoryPartialCueHypothesis48V1:
        modality = "AUDITORY"
    else:
        raise S2MSReproductionError("runtime hypothesis type differs")
    payload = value.payload_without_digest()
    _require(value.hypothesis_digest == _digest(payload), "runtime hypothesis digest differs")
    return {
        "modality": modality,
        "payload": payload,
        "hypothesis_digest": value.hypothesis_digest,
    }


def _step_record(value: runtime.MinimalMCMRuntimeStep336V1) -> dict[str, object]:
    payload = value.payload_without_digest()
    _require(value.step_digest == _digest(payload), "runtime step digest differs")
    return {
        "payload": payload,
        "hypothesis": _hypothesis_record(value.hypothesis),
        "step_digest": value.step_digest,
    }


def _memory_observation(state: object) -> dict[str, object]:
    _require(type(state) is memory.S2JVCompositeStateV1, "memory poststate type differs")
    assert isinstance(state, memory.S2JVCompositeStateV1)

    def slow(slots: tuple[object, ...]) -> list[dict[str, object]]:
        result = []
        for slot in slots:
            if not slot.occupied:
                continue
            values = list(slot.prototype_values)
            result.append(
                {
                    "slot_id": slot.slot_id,
                    "support_count": slot.support_count,
                    "last_selected_step": slot.last_selected_step,
                    "prototype_digest": _digest(values),
                }
            )
        return result

    b4 = sorted(
        (entry for entry in state.b4_state.entries if entry.occupied),
        key=lambda entry: entry.formation_index,
    )
    fast = tuple(slot for slot in state.tspm_state.fast_state.slots if slot.occupied)
    payload = {
        "state_digest": state.state_digest,
        "generation": state.generation,
        "b4": [
            {
                "slot_id": entry.slot_id,
                "formation_index": entry.formation_index,
                "values_digest": _digest(list(entry.values)),
            }
            for entry in b4
        ],
        "fast": [
            {
                "slot_id": slot.slot_id,
                "support_count": slot.support_count,
                "last_selected_step": slot.last_selected_step,
                "auditory_values_digest": _digest(list(slot.auditory_values)),
                "visual_values_digest": _digest(list(slot.visual_values)),
            }
            for slot in fast
        ],
        "auditory_slow": slow(state.tspm_state.auditory_ppb1_state.slots),
        "visual_slow": slow(state.tspm_state.visual_ppb1_state.slots),
    }
    return {**payload, "observation_digest": _digest(payload)}


class _ObservedMemoryAdapter:
    """Project the poststate of the one qualified adapter call without another probe."""

    def __init__(self, base: stream.MemoryAdapter) -> None:
        self._base = base
        self.observations: dict[int, dict[str, object]] = {}

    def __call__(
        self,
        state: object,
        event: stream.PerceptionStreamEvent336V1,
    ) -> stream.StreamBranchResultV1:
        result = self._base(state, event)
        _require(event.ordinal not in self.observations, "memory event was observed twice")
        self.observations[event.ordinal] = _memory_observation(result.poststate)
        return result


def _processor(
    config: memory.S2JVCoordinatorConfigV1,
) -> tuple[stream.RoleFreePerceptionStreamProcessor, _ObservedMemoryAdapter]:
    observed_memory = _ObservedMemoryAdapter(stream.build_s2jw_memory_adapter(config))
    processor = stream.RoleFreePerceptionStreamProcessor(
        field_adapter=source_runtime.build_s2lo_field_adapter(),
        memory_adapter=observed_memory,
        visual_scan=stream.build_s2kq_visual_scan_adapter(config, baseline=False),
        visual_baseline=stream.build_s2kq_visual_scan_adapter(config, baseline=True),
        auditory_scan=stream.build_s2kz_auditory_scan_adapter(config, baseline=False),
        auditory_baseline=stream.build_s2kz_auditory_scan_adapter(config, baseline=True),
    )
    return processor, observed_memory


def _runtime_config(workspace_root: Path) -> runtime.MinimalMCMRuntimeConfig336V1:
    source_binding = _digest(
        {
            "schema": S2MS_SCHEMA,
            "event_spec_digests": [item.spec_digest for item in source_runtime.MAIN_EVENT_SPECS],
            "reference_result_sha256": REFERENCE_RESULT_SHA256,
        }
    )
    component_binding = _digest(_source_hashes(workspace_root))
    return runtime.build_minimal_runtime_config(
        runtime_id="s2ms-minimal-runtime",
        max_event_count=MAIN_EVENT_COUNT,
        source_binding_digest=source_binding,
        component_binding_digest=component_binding,
    )


def _event_record(
    materialized: source_runtime.S2LOMaterializedEventV1,
    event: stream.PerceptionStreamEvent336V1,
    step: runtime.MinimalMCMRuntimeStep336V1,
    snapshot: runtime.MinimalMCMRuntimeSnapshot336V1,
    memory_observation: dict[str, object] | None,
) -> dict[str, object]:
    return {
        "event_code": materialized.spec.event_code,
        "event_id": event.event_id,
        "ordinal": event.ordinal,
        "event_type": event.event_type,
        "content_id": materialized.spec.content_id,
        "event_spec_digest": materialized.spec.spec_digest,
        "source_digest": materialized.source_digest,
        "source_receipt_digest": materialized.source_receipt_digest,
        "perception_digest": materialized.perception_digest,
        "event_digest": event.event_digest,
        "runtime_step": _step_record(step),
        "post_snapshot": _snapshot_record(snapshot),
        "memory_observation": memory_observation,
    }


def _reference_projection(workspace_root: Path) -> dict[str, object]:
    path = workspace_root / REFERENCE_RESULT
    data = path.read_bytes()
    _require(hashlib.sha256(data).hexdigest() == REFERENCE_RESULT_SHA256, "S2-LN reference changed")
    record = json.loads(data.decode("ascii"))
    evaluation = record.get("evaluation")
    counters = record.get("execution", {}).get("counters")
    _require(type(evaluation) is dict and type(counters) is dict, "S2-LN reference is incomplete")
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


def _evaluate(
    *,
    workspace_root: Path,
    events: list[dict[str, object]],
    final_open: runtime.MinimalMCMRuntimeSnapshot336V1,
    closed: runtime.MinimalMCMRuntimeSnapshot336V1,
    source: source_runtime.S2LOSourceStream,
) -> dict[str, object]:
    target_auditory, target_visual = source.evaluation_values()
    target_av_digest = _digest(list(target_auditory + target_visual))
    target_auditory_digest = _digest(list(target_auditory))
    target_visual_digest = _digest(list(target_visual))
    final_memory = events[15]["memory_observation"]
    _require(type(final_memory) is dict, "final formation observation is absent")
    b4_indexes = [item["formation_index"] for item in final_memory["b4"]]
    target_absent = all(
        item["values_digest"] != target_av_digest for item in final_memory["b4"]
    ) and all(
        item["auditory_values_digest"] != target_auditory_digest
        or item["visual_values_digest"] != target_visual_digest
        for item in final_memory["fast"]
    )
    auditory_stable = [
        item for item in final_memory["auditory_slow"] if item["support_count"] >= 3
    ]
    visual_stable = [
        item for item in final_memory["visual_slow"] if item["support_count"] >= 3
    ]
    auditory_hypothesis = events[16]["runtime_step"]["hypothesis"]
    visual_hypothesis = events[17]["runtime_step"]["hypothesis"]
    _require(type(auditory_hypothesis) is dict and type(visual_hypothesis) is dict, "cue hypothesis is absent")
    auditory_area = auditory_hypothesis["payload"]["area"]
    visual_area = visual_hypothesis["payload"]["area"]
    memory_read_only = (
        events[15]["post_snapshot"]["memory_state_digest"]
        == events[16]["post_snapshot"]["memory_state_digest"]
        == events[17]["post_snapshot"]["memory_state_digest"]
    )
    functional_projection = {
        "target_absent_from_a_recent": target_absent,
        "b4_formation_indexes": b4_indexes,
        "auditory_stable_support": None if len(auditory_stable) != 1 else auditory_stable[0]["support_count"],
        "visual_stable_support": None if len(visual_stable) != 1 else visual_stable[0]["support_count"],
        "auditory_area": auditory_area,
        "visual_area": visual_area,
        "event_count": final_open.processed_event_count,
        "field_attempt_count": final_open.field_attempt_count,
        "memory_formation_attempt_count": final_open.memory_formation_attempt_count,
        "scan_attempt_count": final_open.scan_attempt_count,
        "field_contact_count": MAIN_FIELD_CONTACTS,
        "memory_read_only_during_cues": memory_read_only,
        "runtime_closed": closed.status == "CLOSED",
    }
    reference = _reference_projection(workspace_root)
    reference_equal = all(
        functional_projection[key] == reference[key]
        for key in (
            "target_absent_from_a_recent",
            "auditory_stable_support",
            "visual_stable_support",
            "auditory_area",
            "visual_area",
            "event_count",
            "field_attempt_count",
            "memory_formation_attempt_count",
            "scan_attempt_count",
        )
    )
    confirmed = (
        reference["status"] == "S2LN_ROLE_FREE_DISTRIBUTED_AV_EXPERIENCE_CONFIRMED"
        and target_absent
        and b4_indexes == list(range(8, 17))
        and len(auditory_stable) == len(visual_stable) == 1
        and auditory_stable[0]["support_count"] == visual_stable[0]["support_count"] == 3
        and auditory_area == "B_STABLE_AUDITORY"
        and visual_area == "B_STABLE"
        and all(
            event["runtime_step"]["payload"]["context_status"]
            == ("NOT_REQUESTED" if index < 16 else "CONTEXT_CANDIDATE_AVAILABLE")
            for index, event in enumerate(events)
        )
        and all(not event["runtime_step"]["payload"]["error_codes"] for event in events)
        and memory_read_only
        and functional_projection["field_attempt_count"] == MAIN_EVENT_COUNT
        and functional_projection["memory_formation_attempt_count"] == MAIN_FORMATION_COUNT
        and functional_projection["scan_attempt_count"] == 4
        and functional_projection["field_contact_count"] == MAIN_FIELD_CONTACTS
        and final_open.status == "OPEN"
        and closed.status == "CLOSED"
        and reference_equal
    )
    payload = {
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
    return {**payload, "evaluation_digest": _digest(payload)}


def _main_record(workspace_root: Path, run_id: str) -> dict[str, object]:
    config = source_runtime._build_config()
    source = source_runtime.S2LOSourceStream(config.profile, mode="MAIN")
    band_plan = auditory_scan.build_auditory_band_plan_48()
    first = source.materialize_next(config_digest=config.config_digest, band_plan=band_plan)
    initial_stream = source_runtime._initial_stream(config, first)
    processor, observed_memory = _processor(config)
    runtime_config = _runtime_config(workspace_root)
    subject = runtime.MinimalMCMRuntime336(
        config=runtime_config,
        processor=processor,
        initial_state=initial_stream,
    )
    initial_snapshot = subject.snapshot()
    events: list[dict[str, object]] = []
    materialized = first
    for index, spec in enumerate(source_runtime.MAIN_EVENT_SPECS):
        if index:
            materialized = source.materialize_next(
                config_digest=config.config_digest,
                band_plan=band_plan,
            )
        _require(materialized.spec == spec, "materialized event order differs")
        event = source_runtime.build_stream_event(materialized)
        step = subject.process_once(event)
        snapshot = subject.snapshot()
        observation = observed_memory.observations.get(event.ordinal)
        events.append(_event_record(materialized, event, step, snapshot, observation))
    final_open = subject.snapshot()
    closed = subject.close()
    evaluation = _evaluate(
        workspace_root=workspace_root,
        events=events,
        final_open=final_open,
        closed=closed,
        source=source,
    )
    payload = {
        "schema": S2MS_RESULT_SCHEMA,
        "run_id": run_id,
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": _source_hashes(workspace_root),
        "reference_result": {
            "path": REFERENCE_RESULT,
            "sha256": REFERENCE_RESULT_SHA256,
        },
        "plan": {
            "event_budget": MAIN_EVENT_COUNT,
            "event_spec_digests": [item.spec_digest for item in source_runtime.MAIN_EVENT_SPECS],
            "formation_count": MAIN_FORMATION_COUNT,
            "field_contact_count": MAIN_FIELD_CONTACTS,
            "hypothesis_application_count": 0,
            "completion_count": 0,
        },
        "execution": {
            "runtime_config": {
                **runtime_config.payload_without_digest(),
                "config_digest": runtime_config.config_digest,
            },
            "initial_snapshot": _snapshot_record(initial_snapshot),
            "events": events,
            "final_open_snapshot": _snapshot_record(final_open),
            "closed_snapshot": _snapshot_record(closed),
        },
        "evaluation": evaluation,
    }
    return {**payload, "record_digest": _digest(payload)}


def _not_evaluable_record(workspace_root: Path, run_id: str) -> dict[str, object]:
    payload = {
        "schema": S2MS_RESULT_SCHEMA,
        "run_id": run_id,
        "technical_status": "NOT_EVALUABLE",
        "source_hashes": _source_hashes(workspace_root),
        "reference_result": {
            "path": REFERENCE_RESULT,
            "sha256": REFERENCE_RESULT_SHA256,
        },
        "plan": {
            "event_budget": MAIN_EVENT_COUNT,
            "event_spec_digests": [item.spec_digest for item in source_runtime.MAIN_EVENT_SPECS],
            "formation_count": MAIN_FORMATION_COUNT,
            "field_contact_count": MAIN_FIELD_CONTACTS,
            "hypothesis_application_count": 0,
            "completion_count": 0,
        },
        "execution": None,
        "evaluation": None,
        "failure_code": "S2MS_EXECUTION_FAILED",
    }
    return {**payload, "record_digest": _digest(payload)}


def _write_once(output_root: Path, run_id: str, record: dict[str, object]) -> Path:
    _require(output_root.is_absolute(), "output root must be absolute")
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    target = run_dir / "result.json"
    temporary = run_dir / ".result.json.tmp"
    data = _canonical_bytes(record, newline=True)
    _require(len(data) <= MAX_RESULT_BYTES, "result exceeds byte budget")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise
    return target


def run_main_once(*, workspace_root: Path, output_root: Path, run_id: str) -> Path:
    global MAIN_EXECUTION_ENABLED, _MAIN_USED
    _require(MAIN_EXECUTION_ENABLED is True, "main gate is closed")
    _require(run_id == AUTHORIZED_RUN_ID and _RUN_ID.fullmatch(run_id) is not None, "run id differs")
    _require(not _MAIN_USED and _MAIN_LOCK.acquire(blocking=False), "main run is consumed")
    _MAIN_USED = True
    try:
        try:
            record = _main_record(workspace_root, run_id)
        except Exception:
            record = _not_evaluable_record(workspace_root, run_id)
        return _write_once(output_root, run_id, record)
    finally:
        MAIN_EXECUTION_ENABLED = False
        _MAIN_LOCK.release()


__all__: tuple[str, ...] = ()
