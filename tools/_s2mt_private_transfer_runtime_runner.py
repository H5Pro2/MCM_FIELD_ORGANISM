"""One presealed transfer stream through the unchanged S2-MR runtime."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
from threading import Lock

import numpy as np

from mcm_field_organism._ppb1_reference import normalized_mean_l1_distance
from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import CommonFieldTime, from_auditory_receptor_state, from_visual_receptor_state
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2kq_private_partial_cue_retrieval_336 as visual_scan
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as auditory_scan
from tools import _s2lm_private_role_free_stream_processor as stream
from tools import _s2lo_private_role_free_stream_runner as field_source
from tools import _s2mr_private_minimal_mcm_runtime as runtime
from tools import _s2ms_private_minimal_runtime_reproduction as s2ms
from tools import _s2mx_private_scaled_transfer_sources as raw_source
from tools import _s2jw_profiled_memory_coordinator as memory
from tools._s2jw_default_live_av_pairing import bind_s2jv_default_live_pair, build_s2jv_pairing_plan


S2MT_SCHEMA = "s2mt.private.presealed-transfer-runtime.v1"
S2MT_RESULT_SCHEMA = "s2mt.private.presealed-transfer-result.v1"
S2MT_FAILURE_SCHEMA = "s2mt.private.failure-receipt.v1"
AUTHORIZED_RUN_ID = "s2mt-presealed-transfer-runtime-20260905-02"
FIELD_CLOCK_ID = "s2mt-transfer-field-clock"
SOURCE_CONTRACT_ID = "s2mt-presealed-scaled-transfer-source-v2"
EVENT_COUNT = 28
FORMATION_COUNT = 20
FIELD_CONTACT_COUNT = 8_064
MAX_RESULT_BYTES = 524_288
MAIN_EXECUTION_ENABLED = False
_MAIN_USED = False
_MAIN_LOCK = Lock()
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")
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
    "tools/_s2mx_private_scaled_transfer_sources.py",
    "tools/_s2mt_private_transfer_runtime_runner.py",
    "tools/_s2mt_private_transfer_runtime_verifier.py",
    "mcm_field_organism/finite_video_path.py",
    "mcm_field_organism/log_spectral_receptor.py",
)


class S2MTError(RuntimeError):
    """The presealed transfer stream or its bounded execution is invalid."""


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return encoded + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MTError(message)


def _source_hashes(workspace_root: Path) -> dict[str, str]:
    result = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        _require(path.is_file(), f"bound source is absent: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


@dataclass(frozen=True, slots=True)
class S2MTEventSpecV1:
    event_code: str
    event_id: str
    ordinal: int
    event_type: str
    recipe_id: str
    spec_digest: str
    schema: str = S2MT_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "spec_digest"
        }


def _spec(ordinal: int, event_type: str, recipe_id: str) -> S2MTEventSpecV1:
    temporary = S2MTEventSpecV1(
        f"e{ordinal:02d}",
        f"s2mt-event-e{ordinal:02d}",
        ordinal,
        event_type,
        recipe_id,
        "",
    )
    return S2MTEventSpecV1(
        temporary.event_code,
        temporary.event_id,
        temporary.ordinal,
        temporary.event_type,
        temporary.recipe_id,
        _digest(temporary.payload_without_digest()),
    )


EVENT_SPECS = tuple(
    _spec(index, "COMPLETE_AV_PERCEPTION", recipe_id)
    for index, recipe_id in enumerate(raw_source.FORMATION_SEQUENCE, start=1)
) + tuple(
    _spec(index, f"PARTIAL_{modality}_CUE", recipe_id)
    for index, (recipe_id, modality) in enumerate(raw_source.CUE_SEQUENCE, start=21)
)


@dataclass(frozen=True, slots=True)
class S2MTAttemptBindingsV1:
    source_binding_digest: str
    plan_binding_digest: str
    config_binding_digest: str
    runtime_binding_digest: str


@dataclass(frozen=True, slots=True)
class S2MTFailureReceiptV1:
    phase: str
    event_ordinal: int | None
    completed_event_count: int
    last_runtime_snapshot_digest: str | None
    error_code: str
    source_binding_digest: str
    plan_binding_digest: str
    config_binding_digest: str
    runtime_binding_digest: str
    failure_receipt_digest: str
    schema: str = S2MT_FAILURE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "failure_receipt_digest"
        }


class _S2MTObservedFailure(Exception):
    def __init__(self, receipt: S2MTFailureReceiptV1) -> None:
        super().__init__(receipt.error_code)
        self.receipt = receipt


def _attempt_bindings(source_hashes: dict[str, str]) -> S2MTAttemptBindingsV1:
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
            "audio_input_scale": raw_source.AUDIO_INPUT_SCALE,
            "audio_input_scale_f32_hex": raw_source.AUDIO_INPUT_SCALE_F32_HEX,
            "compatibility_evidence_record_digest": raw_source.S2MW_EVIDENCE_RECORD_DIGEST,
            "event_spec_digests": [item.spec_digest for item in EVENT_SPECS],
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
    return S2MTAttemptBindingsV1(
        source_binding_digest,
        plan_binding_digest,
        config_binding_digest,
        runtime_binding_digest,
    )


def _failure_receipt(
    *,
    phase: str,
    event_ordinal: int | None,
    completed_event_count: int,
    last_runtime_snapshot_digest: str | None,
    bindings: S2MTAttemptBindingsV1,
) -> S2MTFailureReceiptV1:
    _require(phase in FAILURE_CODES, "failure phase differs")
    temporary = S2MTFailureReceiptV1(
        phase,
        event_ordinal,
        completed_event_count,
        last_runtime_snapshot_digest,
        FAILURE_CODES[phase],
        bindings.source_binding_digest,
        bindings.plan_binding_digest,
        bindings.config_binding_digest,
        bindings.runtime_binding_digest,
        "",
    )
    return S2MTFailureReceiptV1(
        temporary.phase,
        temporary.event_ordinal,
        temporary.completed_event_count,
        temporary.last_runtime_snapshot_digest,
        temporary.error_code,
        temporary.source_binding_digest,
        temporary.plan_binding_digest,
        temporary.config_binding_digest,
        temporary.runtime_binding_digest,
        _digest(temporary.payload_without_digest()),
    )


@dataclass(frozen=True, slots=True)
class S2MTMaterializedEventV1:
    spec: S2MTEventSpecV1
    source_digest: str
    perception_digest: str
    source_receipt_digest: str
    field_input: field_source.S2LOFieldInputV1
    operation_payload: object


def _field_input(
    perception_digest: str,
    ordinal: int,
    frames: tuple[OrganismTimedReceptorFrame, ...],
) -> field_source.S2LOFieldInputV1:
    start = (ordinal - 1) * 100_000_000
    end = ordinal * 100_000_000
    _require(
        frames
        and all(item.field_time.clock_id == FIELD_CLOCK_ID for item in frames)
        and all(item.field_time.window_end_tick == end for item in frames),
        "field time binding differs",
    )
    return field_source.S2LOFieldInputV1(perception_digest, start, end, frames)


def _materialize_events(
    plan: raw_source.PresealedAVCorpusPlanV2,
    config: memory.S2JVCoordinatorConfigV1,
) -> tuple[S2MTMaterializedEventV1, ...]:
    _require(plan.event_count == EVENT_COUNT, "presealed event count differs")
    visual = LocalChannelGridReceptor(VisualGridConfig())
    hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
    band_plan = auditory_scan.build_auditory_band_plan_48()
    result = []
    for spec in EVENT_SPECS:
        end = spec.ordinal * 100_000_000
        if spec.event_type in {"COMPLETE_AV_PERCEPTION", "PARTIAL_AUDITORY_CUE"}:
            window = raw_source.verified_audio_window(plan, spec.recipe_id)
            auditory_state = None
            for hop in range(10):
                auditory_state = hearing.push(window[hop * 480 : (hop + 1) * 480])
            _require(auditory_state is not None, "auditory endpoint is absent")
            auditory_frame = OrganismTimedReceptorFrame(
                from_auditory_receptor_state(auditory_state),
                CommonFieldTime(FIELD_CLOCK_ID, end - 10_000_000, end),
            )
            auditory_payload_digest = hashlib.sha256(np.asarray(window, dtype="<f4").tobytes()).hexdigest()
            del window
        if spec.event_type in {"COMPLETE_AV_PERCEPTION", "PARTIAL_VISUAL_CUE"}:
            partial = spec.event_type == "PARTIAL_VISUAL_CUE"
            image = raw_source.verified_visual_frame(plan, spec.recipe_id, partial=partial)
            visual_state = visual.analyze(image, frame_index=(spec.ordinal - 1) * 3 + 2)
            visual_frame = OrganismTimedReceptorFrame(
                from_visual_receptor_state(visual_state),
                CommonFieldTime(
                    FIELD_CLOCK_ID,
                    (((spec.ordinal - 1) * 3 + 2) * 1_000_000_000) // 30,
                    end,
                ),
            )
            visual_payload_digest = hashlib.sha256(image.tobytes(order="C")).hexdigest()
            del image

        if spec.event_type == "COMPLETE_AV_PERCEPTION":
            pairing_plan = build_s2jv_pairing_plan(
                pair_id=f"s2mt-pair-{spec.ordinal:03d}",
                source_contract_id=SOURCE_CONTRACT_ID,
                profile=config.profile,
                auditory=auditory_frame,
                visual=visual_frame,
                auditory_payload_digest=auditory_payload_digest,
                visual_payload_digest=visual_payload_digest,
            )
            operation = bind_s2jv_default_live_pair(
                pairing_plan=pairing_plan,
                profile=config.profile,
                auditory=auditory_frame,
                visual=visual_frame,
            )
            perception_digest = operation.pairing_digest
            frames = (auditory_frame, visual_frame)
            source_payload = {
                "schema": S2MT_SCHEMA,
                "plan_digest": plan.plan_digest,
                "event_spec_digest": spec.spec_digest,
                "source_id": f"s2mt-source-{spec.ordinal:03d}",
                "auditory_payload_digest": auditory_payload_digest,
                "visual_payload_digest": visual_payload_digest,
                "auditory_values_digest": pairing_plan.auditory_values_digest,
                "visual_values_digest": pairing_plan.visual_values_digest,
                "pairing_digest": operation.pairing_digest,
            }
        elif spec.event_type == "PARTIAL_AUDITORY_CUE":
            values = tuple(auditory_state.energy)
            cue = auditory_scan.build_masked_auditory_cue_48(
                pcm_payload_digest=auditory_payload_digest,
                receptor_state_digest=auditory_state.digest(),
                receptor_values_digest=visual_scan.digest(list(values)),
                config_digest=config.config_digest,
                auditory_source_clock_id=auditory_frame.frame.clock_id,
                auditory_window_start_tick=auditory_frame.frame.window_start_tick,
                auditory_window_end_tick=auditory_frame.frame.window_end_tick,
                observed_values=tuple(values[index] for index in auditory_scan.OBSERVED_BANDS),
                band_plan=band_plan,
            )
            operation = stream.AuditoryCueOperationV1(cue, band_plan)
            perception_digest = cue.cue_digest
            frames = (auditory_frame,)
            source_payload = {
                "schema": S2MT_SCHEMA,
                "plan_digest": plan.plan_digest,
                "event_spec_digest": spec.spec_digest,
                "source_id": f"s2mt-source-{spec.ordinal:03d}",
                "auditory_payload_digest": auditory_payload_digest,
                "receptor_state_digest": auditory_state.digest(),
                "cue_digest": cue.cue_digest,
            }
        else:
            values = tuple(visual_state.channel_values)
            source_base = {
                "schema": S2MT_SCHEMA,
                "plan_digest": plan.plan_digest,
                "event_spec_digest": spec.spec_digest,
                "source_id": f"s2mt-source-{spec.ordinal:03d}",
                "visual_payload_digest": visual_payload_digest,
                "receptor_state_digest": visual_state.digest(),
                "receptor_values_digest": visual_scan.digest(list(values)),
            }
            source_digest = _digest(source_base)
            cue = visual_scan.build_masked_memory_cue_336(
                source_digest=source_digest,
                config_digest=config.config_digest,
                field_clock_id=FIELD_CLOCK_ID,
                window_start_tick=visual_frame.field_time.window_start_tick,
                window_end_tick=visual_frame.field_time.window_end_tick,
                visual_source_clock_id=visual_frame.frame.clock_id,
                visual_window_start_tick=visual_frame.frame.window_start_tick,
                visual_window_end_tick=visual_frame.frame.window_end_tick,
                values=tuple(
                    values[index] if index in visual_scan.VISIBLE_POSITIONS else None
                    for index in range(288)
                ),
            )
            operation = cue
            perception_digest = cue.cue_digest
            frames = (visual_frame,)
            source_payload = {**source_base, "cue_digest": cue.cue_digest}
        if spec.event_type != "PARTIAL_VISUAL_CUE":
            source_digest = _digest(source_payload)
        result.append(
            S2MTMaterializedEventV1(
                spec,
                source_digest,
                perception_digest,
                _digest({**source_payload, "source_digest": source_digest}),
                _field_input(perception_digest, spec.ordinal, frames),
                operation,
            )
        )
    return tuple(result)


def _formation_values(value: S2MTMaterializedEventV1) -> tuple[tuple[float, ...], tuple[float, ...]]:
    pair = value.operation_payload
    return tuple(pair.auditory.timed_frame.frame.values), tuple(pair.visual.timed_frame.frame.values)


def _cue_values(value: S2MTMaterializedEventV1) -> tuple[float, ...]:
    operation = value.operation_payload
    cue = operation.cue if type(operation) is stream.AuditoryCueOperationV1 else operation
    return tuple(float(item) for item in cue.values if item is not None)


def _geometry(materialized: tuple[S2MTMaterializedEventV1, ...], config: memory.S2JVCoordinatorConfigV1) -> dict[str, object]:
    first_by_recipe = {}
    for item in materialized[:FORMATION_COUNT]:
        first_by_recipe.setdefault(item.spec.recipe_id, _formation_values(item))
    pairwise = []
    recipes = tuple(first_by_recipe)
    for left_index, left in enumerate(recipes):
        for right in recipes[left_index + 1 :]:
            left_audio, left_visual = first_by_recipe[left]
            right_audio, right_visual = first_by_recipe[right]
            audio_distance = normalized_mean_l1_distance(left_audio, right_audio)
            visual_distance = normalized_mean_l1_distance(left_visual, right_visual)
            pairwise.append(
                {
                    "left": left,
                    "right": right,
                    "auditory_distance": audio_distance,
                    "visual_distance": visual_distance,
                    "fast_separated": (
                        audio_distance > config.tspm_config.auditory_match_threshold
                        or visual_distance > config.tspm_config.visual_match_threshold
                    ),
                }
            )
    cue_matches = []
    for cue_event in materialized[FORMATION_COUNT:]:
        modality = "AUDITORY" if cue_event.spec.event_type == "PARTIAL_AUDITORY_CUE" else "VISUAL"
        matches = []
        distances = {}
        for recipe_id in ("n00", "n01", "n02"):
            candidate = first_by_recipe[recipe_id][0 if modality == "AUDITORY" else 1]
            if modality == "AUDITORY":
                observed_candidate = tuple(candidate[index] for index in auditory_scan.OBSERVED_BANDS)
                distance = normalized_mean_l1_distance(_cue_values(cue_event), observed_candidate)
                matched = distance <= config.tspm_config.profile.auditory_config.match_threshold
            else:
                observed_candidate = tuple(candidate[index] for index in visual_scan.VISIBLE_POSITIONS)
                cue_values = _cue_values(cue_event)
                distance = normalized_mean_l1_distance(cue_values, observed_candidate)
                matched = cue_values == observed_candidate
            distances[recipe_id] = distance
            if matched:
                matches.append(recipe_id)
        cue_matches.append(
            {
                "event_code": cue_event.spec.event_code,
                "recipe_id": cue_event.spec.recipe_id,
                "modality": modality,
                "matching_training_recipes": matches,
                "distances": distances,
            }
        )
    repetition_equal = all(
        _formation_values(item) == first_by_recipe[item.spec.recipe_id]
        for item in materialized[:FORMATION_COUNT]
    )
    first_three_pairs = [
        item for item in pairwise if item["left"] in {"n00", "n01", "n02"} and item["right"] in {"n00", "n01", "n02"}
    ]
    expected_cue_matches = [
        [item.spec.recipe_id] if item.spec.recipe_id in {"n00", "n01", "n02"} else []
        for item in materialized[FORMATION_COUNT:]
    ]
    valid = (
        repetition_equal
        and all(item["fast_separated"] for item in pairwise)
        and all(item["auditory_distance"] > config.tspm_config.profile.auditory_config.match_threshold for item in first_three_pairs)
        and all(item["visual_distance"] > config.tspm_config.profile.visual_config.match_threshold for item in first_three_pairs)
        and [item["matching_training_recipes"] for item in cue_matches] == expected_cue_matches
    )
    payload = {
        "status": "S2MT_GEOMETRY_MATERIALIZED" if valid else "S2MT_GEOMETRY_NOT_MATERIALIZABLE",
        "repetition_values_equal": repetition_equal,
        "pairwise": pairwise,
        "cue_matches": cue_matches,
    }
    return {**payload, "geometry_digest": _digest(payload)}


def _build_event(value: S2MTMaterializedEventV1) -> stream.PerceptionStreamEvent336V1:
    return stream.build_perception_stream_event(
        event_id=value.spec.event_id,
        ordinal=value.spec.ordinal,
        event_type=value.spec.event_type,
        source_digest=value.source_digest,
        perception_digest=value.perception_digest,
        field_projection_digest=value.perception_digest,
        operation_projection_digest=value.perception_digest,
        field_payload=value.field_input,
        operation_payload=value.operation_payload,
    )


def _processor(config: memory.S2JVCoordinatorConfigV1):
    observed = s2ms._ObservedMemoryAdapter(stream.build_s2jw_memory_adapter(config))
    return stream.RoleFreePerceptionStreamProcessor(
        field_adapter=field_source.build_s2lo_field_adapter(),
        memory_adapter=observed,
        visual_scan=stream.build_s2kq_visual_scan_adapter(config, baseline=False),
        visual_baseline=stream.build_s2kq_visual_scan_adapter(config, baseline=True),
        auditory_scan=stream.build_s2kz_auditory_scan_adapter(config, baseline=False),
        auditory_baseline=stream.build_s2kz_auditory_scan_adapter(config, baseline=True),
    ), observed


def _runtime_config(source_hashes: dict[str, str], plan_digest: str) -> runtime.MinimalMCMRuntimeConfig336V1:
    return runtime.build_minimal_runtime_config(
        runtime_id="s2mt-transfer-runtime",
        max_event_count=EVENT_COUNT,
        source_binding_digest=_digest({"plan_digest": plan_digest, "event_spec_digests": [item.spec_digest for item in EVENT_SPECS]}),
        component_binding_digest=_digest(source_hashes),
    )


def _event_record(value, event, step, snapshot, observation):
    return {
        "event_code": value.spec.event_code,
        "event_id": value.spec.event_id,
        "ordinal": value.spec.ordinal,
        "event_type": value.spec.event_type,
        "recipe_id": value.spec.recipe_id,
        "event_spec_digest": value.spec.spec_digest,
        "source_digest": value.source_digest,
        "source_receipt_digest": value.source_receipt_digest,
        "perception_digest": value.perception_digest,
        "event_digest": event.event_digest,
        "runtime_step": s2ms._step_record(step),
        "post_snapshot": s2ms._snapshot_record(snapshot),
        "memory_observation": observation,
    }


def _evaluate(events: list[dict[str, object]], final_open, closed) -> dict[str, object]:
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
    cue_events = events[FORMATION_COUNT:]
    decisions = []
    for event, (role, modality) in zip(cue_events, (
        ("A", "AUDITORY"), ("A", "VISUAL"), ("B", "AUDITORY"), ("B", "VISUAL"),
        ("C", "AUDITORY"), ("C", "VISUAL"), ("UNKNOWN", "AUDITORY"), ("UNKNOWN", "VISUAL"),
    ), strict=True):
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
    memory_read_only = all(
        event["post_snapshot"]["memory_state_digest"] == events[FORMATION_COUNT - 1]["post_snapshot"]["memory_state_digest"]
        for event in cue_events
    )
    expected_presence = [True, True, True, True, False, False, False, False]
    confirmed = (
        all(absent.values())
        and auditory_supports == [2, 3, 3]
        and visual_supports == [2, 3, 3]
        and [item["hypothesis_present"] for item in decisions] == expected_presence
        and all(
            item["area"] == ("B_STABLE_AUDITORY" if item["modality"] == "AUDITORY" else "B_STABLE")
            for item in decisions[:4]
        )
        and all(item["context_status"].startswith("ABSTAIN_") for item in decisions[4:])
        and memory_read_only
        and final_open.processed_event_count == EVENT_COUNT
        and final_open.field_attempt_count == EVENT_COUNT
        and final_open.memory_formation_attempt_count == FORMATION_COUNT
        and final_open.scan_attempt_count == 16
        and final_open.status == "OPEN"
        and closed.status == "CLOSED"
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


def _main_record(
    workspace_root: Path,
    run_id: str,
    source_hashes: dict[str, str],
    bindings: S2MTAttemptBindingsV1,
) -> dict[str, object]:
    completed_event_count = 0
    event_ordinal: int | None = None
    last_runtime_snapshot_digest: str | None = None

    def fail(phase: str) -> _S2MTObservedFailure:
        return _S2MTObservedFailure(
            _failure_receipt(
                phase=phase,
                event_ordinal=event_ordinal,
                completed_event_count=completed_event_count,
                last_runtime_snapshot_digest=last_runtime_snapshot_digest,
                bindings=bindings,
            )
        )

    try:
        plan = raw_source.build_presealed_plan()
        config = field_source._build_config()
    except Exception:
        raise fail("SOURCE_PLAN") from None

    try:
        materialized = _materialize_events(plan, config)
        geometry = _geometry(materialized, config)
        _require(geometry["status"] == "S2MT_GEOMETRY_MATERIALIZED", "presealed receptor geometry differs")
    except Exception:
        raise fail("MATERIALIZATION") from None

    try:
        first = materialized[0]
        initial_field = field_source.initial_s2lo_field_state(first.field_input)
        initial_memory = memory.initial_s2jv_composite_state(config)
        initial_stream = stream.initial_perception_stream_state(
            stream_id="s2mt-transfer-stream",
            field_state=initial_field,
            field_state_digest=initial_field.state_digest,
            memory_state=initial_memory,
            memory_state_digest=initial_memory.state_digest,
        )
        processor, observed = _processor(config)
        runtime_config = _runtime_config(source_hashes, plan.plan_digest)
        subject = runtime.MinimalMCMRuntime336(config=runtime_config, processor=processor, initial_state=initial_stream)
        initial_snapshot = subject.snapshot()
        last_runtime_snapshot_digest = initial_snapshot.snapshot_digest
    except Exception:
        raise fail("RUNTIME_INIT") from None

    events = []
    for value in materialized:
        event_ordinal = value.spec.ordinal
        try:
            event = _build_event(value)
            step = subject.process_once(event)
            snapshot = subject.snapshot()
            event_record = _event_record(value, event, step, snapshot, observed.observations.get(event.ordinal))
        except Exception:
            raise fail("EVENT_PROCESSING") from None
        events.append(event_record)
        completed_event_count += 1
        last_runtime_snapshot_digest = snapshot.snapshot_digest
    event_ordinal = None

    try:
        final_open = subject.snapshot()
        last_runtime_snapshot_digest = final_open.snapshot_digest
        closed = subject.close()
        last_runtime_snapshot_digest = closed.snapshot_digest
    except Exception:
        raise fail("RUNTIME_CLOSE") from None

    try:
        evaluation = _evaluate(events, final_open, closed)
        plan_payload = {
            **plan.payload_without_digest(),
            "recipes": [{**item.payload_without_digest(), "recipe_digest": item.recipe_digest} for item in plan.recipes],
            "plan_digest": plan.plan_digest,
        }
        payload = {
            "schema": S2MT_RESULT_SCHEMA,
            "run_id": run_id,
            "technical_status": "RECORDING_COMPLETE",
            "source_hashes": source_hashes,
            "presealed_source_plan": plan_payload,
            "geometry": geometry,
            "plan": {
                "event_count": EVENT_COUNT,
                "formation_count": FORMATION_COUNT,
                "cue_count": 8,
                "field_contact_count": FIELD_CONTACT_COUNT,
                "event_spec_digests": [item.spec_digest for item in EVENT_SPECS],
                "hypothesis_application_count": 0,
                "completion_count": 0,
            },
            "execution": {
                "runtime_config": {**runtime_config.payload_without_digest(), "config_digest": runtime_config.config_digest},
                "initial_snapshot": s2ms._snapshot_record(initial_snapshot),
                "events": events,
                "final_open_snapshot": s2ms._snapshot_record(final_open),
                "closed_snapshot": s2ms._snapshot_record(closed),
            },
            "evaluation": evaluation,
        }
        return {**payload, "record_digest": _digest(payload)}
    except Exception:
        raise fail("EVALUATION") from None


def _not_evaluable_record(
    run_id: str,
    source_hashes: dict[str, str],
    receipt: S2MTFailureReceiptV1,
) -> dict[str, object]:
    payload = {
        "schema": S2MT_RESULT_SCHEMA,
        "run_id": run_id,
        "technical_status": "NOT_EVALUABLE",
        "source_hashes": source_hashes,
        "execution": None,
        "evaluation": None,
        "failure_code": receipt.error_code,
        "failure_receipt": {
            **receipt.payload_without_digest(),
            "failure_receipt_digest": receipt.failure_receipt_digest,
        },
    }
    return {**payload, "record_digest": _digest(payload)}


def _write_once(output_root: Path, run_id: str, record: dict[str, object]) -> Path:
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
        source_hashes = _source_hashes(workspace_root)
        bindings = _attempt_bindings(source_hashes)
        try:
            record = _main_record(workspace_root, run_id, source_hashes, bindings)
        except _S2MTObservedFailure as failure:
            record = _not_evaluable_record(run_id, source_hashes, failure.receipt)
        return _write_once(output_root, run_id, record)
    finally:
        MAIN_EXECUTION_ENABLED = False
        _MAIN_LOCK.release()


assert len(EVENT_SPECS) == EVENT_COUNT
assert sum(item.event_type == "COMPLETE_AV_PERCEPTION" for item in EVENT_SPECS) == FORMATION_COUNT

__all__: tuple[str, ...] = ()
