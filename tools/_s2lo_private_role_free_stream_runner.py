"""Private fixtures, adapters, and closed runner for the S2-LN stream."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
from threading import Lock

import numpy as np

from mcm_field_organism.audio_video_field_geometry import ORTHOGONAL_FIELD_SAMPLE_OFFSETS
from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from mcm_field_organism.receptor_distributor import ReceptorDistribution
from mcm_field_organism.receptor_proposal_handoff import handoff_receptor_completion_groups
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame, ReceptorTimeSequence
from mcm_field_organism.shared_mcm_field import SharedMCMField, build_shared_mcm_field
from mcm_field_organism.transient_dock_trajectory import map_proposal_batch_to_transient_docks
from mcm_field_organism.transient_neuron_input import project_transient_docks_to_neuron_inputs
from tools import _s2kq_private_partial_cue_retrieval_336 as visual_scan
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as auditory_scan
from tools import _s2lm_private_role_free_stream_processor as stream
from tools import _s2jt_private_timed_field_projection as field_path
from tools import _s2jw_profiled_memory_coordinator as memory
from tools import _s2ld_auditory_partial_cue_fixtures as source_fixtures
from tools import _s2ks_real_partial_cue_fixtures as visual_cues
from tools._s2jw_default_live_av_pairing import (
    S2JVBoundAVPairV1,
    bind_s2jv_default_live_pair,
    build_s2jv_pairing_plan,
)
from tools._s2jw_default_live_profile import S2JWDefaultLiveProfileV1, build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits


S2LO_SCHEMA = "s2lo.role-free-distributed-stream.v1"
S2LO_RESULT_SCHEMA = "s2lo.role-free-distributed-result.v1"
FIELD_CLOCK_ID = "s2ln-role-free-field-clock"
SOURCE_CONTRACT_ID = "s2ln-role-free-source"
AUTHORIZED_RUN_ID = "s2ln-role-free-distributed-av-20260904-01"
QUALIFICATION_ID = "s2lo-neutral-qualification-20260904-02"
MAIN_EXECUTION_ENABLED = False
MAX_RESULT_BYTES = 1_048_576
MAIN_EVENT_COUNT = 18
MAIN_FORMATION_COUNT = 16
MAIN_FIELD_CONTACTS = 5_712
MAIN_MEMORY_L1_TERMS = 56_832
MAIN_SCAN_COMPARISONS = 2_656
MAIN_RAW_BYTES = 106_080_000

_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_MAIN_LOCK = Lock()
_MAIN_USED = False

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


class S2LOError(RuntimeError):
    """One bounded source, branch, result, or execution relation is invalid."""


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
        raise S2LOError(message)


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class S2LOEventSpecV1:
    event_code: str
    event_id: str
    ordinal: int
    event_type: str
    content_id: str | None
    spec_digest: str
    schema: str = S2LO_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "event_code": self.event_code,
            "event_id": self.event_id,
            "ordinal": self.ordinal,
            "event_type": self.event_type,
            "content_id": self.content_id,
        }


def _event_spec(ordinal: int, event_type: str, content_id: str | None) -> S2LOEventSpecV1:
    code = f"e{ordinal:02d}"
    payload = {
        "schema": S2LO_SCHEMA,
        "event_code": code,
        "event_id": f"s2ln-event-{code}",
        "ordinal": ordinal,
        "event_type": event_type,
        "content_id": content_id,
    }
    return S2LOEventSpecV1(
        code,
        payload["event_id"],
        ordinal,
        event_type,
        content_id,
        _digest(payload),
    )


_FORMATION_CONTENTS = (
    "c00", "c01", "c00", "c02", "c00", "c03", "c00", "c04",
    "c05", "c06", "c07", "c08", "c09", "c01", "c02", "c03",
)
MAIN_EVENT_SPECS = tuple(
    _event_spec(index, "COMPLETE_AV_PERCEPTION", content)
    for index, content in enumerate(_FORMATION_CONTENTS, start=1)
) + (
    _event_spec(17, "PARTIAL_AUDITORY_CUE", None),
    _event_spec(18, "PARTIAL_VISUAL_CUE", None),
)

QUALIFICATION_EVENT_SPECS = (
    _event_spec(1, "COMPLETE_AV_PERCEPTION", "c04"),
    _event_spec(2, "PARTIAL_AUDITORY_CUE", None),
    _event_spec(3, "PARTIAL_VISUAL_CUE", None),
)

_CONTENT_RECIPES = {
    "c00": ("P", "P"),
    **{f"c{index:02d}": ("D_FAR", f"E{index}") for index in range(1, 10)},
}


@dataclass(frozen=True, slots=True)
class S2LOFieldInputV1:
    perception_digest: str
    start_tick: int
    end_tick: int
    timed_frames: tuple[OrganismTimedReceptorFrame, ...]


@dataclass(frozen=True, slots=True)
class S2LOMaterializedEventV1:
    spec: S2LOEventSpecV1
    source_digest: str
    perception_digest: str
    source_receipt_digest: str
    field_input: S2LOFieldInputV1
    operation_payload: object


class S2LOSourceStream:
    """Materialize one ordered source at a time without retaining raw payloads."""

    def __init__(self, profile: S2JWDefaultLiveProfileV1, *, mode: str) -> None:
        _require(type(profile) is S2JWDefaultLiveProfileV1, "exact profile required")
        _require(mode in {"MAIN", "QUALIFICATION"}, "source mode differs")
        self._profile = profile
        self._specs = MAIN_EVENT_SPECS if mode == "MAIN" else QUALIFICATION_EVENT_SPECS
        self._mode = mode
        self._next = 0
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self._evaluation_values: tuple[tuple[float, ...], tuple[float, ...]] | None = None

    @property
    def next_ordinal(self) -> int:
        return self._next + 1

    def _audio_state(self, recipe: str):
        window = source_fixtures.auditory_pcm(recipe)
        state = None
        for hop in range(10):
            state = self._hearing.push(window[hop * 480 : (hop + 1) * 480])
        _require(state is not None, "audio receptor endpoint is absent")
        return window, state

    def _field_input(
        self,
        perception_digest: str,
        ordinal: int,
        frames: tuple[OrganismTimedReceptorFrame, ...],
    ) -> S2LOFieldInputV1:
        start = (ordinal - 1) * 100_000_000
        end = ordinal * 100_000_000
        _require(
            frames
            and all(item.field_time.clock_id == FIELD_CLOCK_ID for item in frames)
            and all(item.field_time.window_end_tick == end for item in frames),
            "field frame binding differs",
        )
        return S2LOFieldInputV1(perception_digest, start, end, frames)

    def _formation(self, spec: S2LOEventSpecV1) -> S2LOMaterializedEventV1:
        _require(spec.content_id in _CONTENT_RECIPES, "formation content differs")
        audio_recipe, visual_recipe = _CONTENT_RECIPES[spec.content_id]
        window, auditory_state = self._audio_state(audio_recipe)
        image = source_fixtures.visual_image(visual_recipe)
        visual_state = self._visual.analyze(image, frame_index=(spec.ordinal - 1) * 3 + 2)
        end = spec.ordinal * 100_000_000
        auditory = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(auditory_state),
            CommonFieldTime(FIELD_CLOCK_ID, end - 10_000_000, end),
        )
        visual = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual_state),
            CommonFieldTime(
                FIELD_CLOCK_ID,
                (((spec.ordinal - 1) * 3 + 2) * 1_000_000_000) // 30,
                end,
            ),
        )
        audio_digest = hashlib.sha256(np.asarray(window, dtype="<f4").tobytes()).hexdigest()
        visual_digest = hashlib.sha256(image.tobytes(order="C")).hexdigest()
        plan = build_s2jv_pairing_plan(
            pair_id=f"s2ln-pair-{spec.ordinal:03d}",
            source_contract_id=SOURCE_CONTRACT_ID,
            profile=self._profile,
            auditory=auditory,
            visual=visual,
            auditory_payload_digest=audio_digest,
            visual_payload_digest=visual_digest,
        )
        pair = bind_s2jv_default_live_pair(
            pairing_plan=plan,
            profile=self._profile,
            auditory=auditory,
            visual=visual,
        )
        source_payload = {
            "schema": S2LO_SCHEMA,
            "event_spec_digest": spec.spec_digest,
            "source_id": f"s2ln-source-{spec.ordinal:03d}",
            "pairing_digest": pair.pairing_digest,
            "auditory_payload_digest": audio_digest,
            "visual_payload_digest": visual_digest,
            "auditory_values_digest": plan.auditory_values_digest,
            "visual_values_digest": plan.visual_values_digest,
        }
        source_digest = _digest(source_payload)
        if self._mode == "MAIN" and spec.content_id == "c00" and self._evaluation_values is None:
            self._evaluation_values = (
                tuple(pair.auditory.timed_frame.frame.values),
                tuple(pair.visual.timed_frame.frame.values),
            )
        return S2LOMaterializedEventV1(
            spec,
            source_digest,
            pair.pairing_digest,
            _digest({**source_payload, "source_digest": source_digest}),
            self._field_input(pair.pairing_digest, spec.ordinal, (auditory, visual)),
            pair,
        )

    def _auditory_cue(
        self,
        spec: S2LOEventSpecV1,
        config_digest: str,
        band_plan: auditory_scan.AuditoryBandPlan48V1,
    ) -> S2LOMaterializedEventV1:
        window, state = self._audio_state("L")
        end = spec.ordinal * 100_000_000
        timed = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(state),
            CommonFieldTime(FIELD_CLOCK_ID, end - 10_000_000, end),
        )
        values = tuple(state.energy)
        pcm_digest = hashlib.sha256(np.asarray(window, dtype="<f4").tobytes()).hexdigest()
        cue = auditory_scan.build_masked_auditory_cue_48(
            pcm_payload_digest=pcm_digest,
            receptor_state_digest=state.digest(),
            receptor_values_digest=visual_scan.digest(list(values)),
            config_digest=config_digest,
            auditory_source_clock_id=timed.frame.clock_id,
            auditory_window_start_tick=timed.frame.window_start_tick,
            auditory_window_end_tick=timed.frame.window_end_tick,
            observed_values=tuple(values[index] for index in auditory_scan.OBSERVED_BANDS),
            band_plan=band_plan,
        )
        source_payload = {
            "schema": S2LO_SCHEMA,
            "event_spec_digest": spec.spec_digest,
            "source_id": f"s2ln-source-{spec.ordinal:03d}",
            "pcm_payload_digest": pcm_digest,
            "receptor_state_digest": state.digest(),
            "cue_digest": cue.cue_digest,
        }
        source_digest = _digest(source_payload)
        return S2LOMaterializedEventV1(
            spec,
            source_digest,
            cue.cue_digest,
            _digest({**source_payload, "source_digest": source_digest}),
            self._field_input(cue.cue_digest, spec.ordinal, (timed,)),
            stream.AuditoryCueOperationV1(cue, band_plan),
        )

    def _visual_cue(
        self,
        spec: S2LOEventSpecV1,
        config_digest: str,
    ) -> S2LOMaterializedEventV1:
        image = visual_cues.occluded_visual_image("X")
        state = self._visual.analyze(image, frame_index=(spec.ordinal - 1) * 3 + 2)
        native = from_visual_receptor_state(state)
        end = spec.ordinal * 100_000_000
        timed = OrganismTimedReceptorFrame(
            native,
            CommonFieldTime(
                FIELD_CLOCK_ID,
                (((spec.ordinal - 1) * 3 + 2) * 1_000_000_000) // 30,
                end,
            ),
        )
        values = tuple(state.channel_values)
        rgb_digest = hashlib.sha256(image.tobytes(order="C")).hexdigest()
        source_payload = {
            "schema": S2LO_SCHEMA,
            "event_spec_digest": spec.spec_digest,
            "source_id": f"s2ln-source-{spec.ordinal:03d}",
            "rgb_payload_digest": rgb_digest,
            "receptor_state_digest": state.digest(),
            "receptor_values_digest": visual_scan.digest(list(values)),
        }
        source_digest = _digest(source_payload)
        cue = visual_scan.build_masked_memory_cue_336(
            source_digest=source_digest,
            config_digest=config_digest,
            field_clock_id=FIELD_CLOCK_ID,
            window_start_tick=timed.field_time.window_start_tick,
            window_end_tick=timed.field_time.window_end_tick,
            visual_source_clock_id=native.clock_id,
            visual_window_start_tick=native.window_start_tick,
            visual_window_end_tick=native.window_end_tick,
            values=tuple(
                values[index] if index in visual_scan.VISIBLE_POSITIONS else None
                for index in range(288)
            ),
        )
        return S2LOMaterializedEventV1(
            spec,
            source_digest,
            cue.cue_digest,
            _digest({**source_payload, "cue_digest": cue.cue_digest}),
            self._field_input(cue.cue_digest, spec.ordinal, (timed,)),
            cue,
        )

    def materialize_next(
        self,
        *,
        config_digest: str,
        band_plan: auditory_scan.AuditoryBandPlan48V1,
    ) -> S2LOMaterializedEventV1:
        _require(self._next < len(self._specs), "source stream is exhausted")
        spec = self._specs[self._next]
        if spec.event_type == "COMPLETE_AV_PERCEPTION":
            result = self._formation(spec)
        elif spec.event_type == "PARTIAL_AUDITORY_CUE":
            result = self._auditory_cue(spec, config_digest, band_plan)
        else:
            result = self._visual_cue(spec, config_digest)
        self._next += 1
        return result

    def evaluation_values(self) -> tuple[tuple[float, ...], tuple[float, ...]]:
        _require(
            self._mode == "MAIN"
            and self._next == len(self._specs)
            and self._evaluation_values is not None,
            "evaluation values are unavailable",
        )
        assert self._evaluation_values is not None
        return self._evaluation_values


@dataclass(frozen=True, slots=True)
class S2LOFieldStateV1:
    field: SharedMCMField
    last_end_tick: int
    step_count: int
    state_digest: str


def _field_state(field: SharedMCMField, last_end_tick: int, step_count: int) -> S2LOFieldStateV1:
    if field.last_distribution is None:
        field_digest = _digest(
            {
                "schema": S2LO_SCHEMA,
                "phase": "INITIAL_FIELD",
                "layer_digest": field.layer.digest(),
                "docks": [
                    {
                        "dock_id": dock.dock_id,
                        "modality_id": dock.dock_map.modality_id,
                        "geometry_id": dock.dock_map.receptor_geometry_id,
                        "pairs": [list(pair) for pair in dock.dock_map.pairs],
                    }
                    for dock in field.docks
                ],
            }
        )
    else:
        field_digest = field.snapshot().digest()
    payload = {
        "schema": S2LO_SCHEMA,
        "field_state_digest": field_digest,
        "last_end_tick": last_end_tick,
        "step_count": step_count,
    }
    return S2LOFieldStateV1(field, last_end_tick, step_count, _digest(payload))


def initial_s2lo_field_state(first_input: S2LOFieldInputV1) -> S2LOFieldStateV1:
    _require(type(first_input) is S2LOFieldInputV1, "exact first field input required")
    _require(len(first_input.timed_frames) == 2, "initial field requires both modalities")
    field = build_shared_mcm_field(
        tuple(item.frame for item in first_input.timed_frames),
        field_path.s2jt_default_dock_anatomies(),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    return _field_state(field, 0, 0)


def build_s2lo_field_adapter():
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)

    def advance(state: object, event: stream.PerceptionStreamEvent336V1) -> stream.StreamBranchResultV1:
        _require(type(state) is S2LOFieldStateV1, "exact field state required")
        _require(type(event.field_payload) is S2LOFieldInputV1, "exact field input required")
        field_input = event.field_payload
        _require(
            field_input.perception_digest == event.field_projection_digest
            and field_input.start_tick == state.last_end_tick
            and field_input.end_tick > field_input.start_tick,
            "field input relation differs",
        )
        sequences = tuple(
            ReceptorTimeSequence(
                item.frame.modality_id,
                item.frame.geometry_id,
                FIELD_CLOCK_ID,
                (item,),
            )
            for item in sorted(field_input.timed_frames, key=lambda frame: frame.frame.modality_id)
        )
        step = MCMFieldStepTime(
            FIELD_CLOCK_ID,
            field_input.start_tick,
            field_input.end_tick,
            1_000_000_000.0,
        )
        handoff = handoff_receptor_completion_groups(sequences, (step,))
        _require(
            handoff.source_event_count == len(field_input.timed_frames)
            and handoff.assigned_event_count == handoff.source_event_count
            and handoff.every_in_horizon_event_assigned_once
            and len(handoff.batches) == 1
            and len(handoff.batches[0].completion_groups) == 1,
            "field event assignment differs",
        )
        trajectory = map_proposal_batch_to_transient_docks(handoff.batches[0], state.field.docks)
        local_inputs = project_transient_docks_to_neuron_inputs(trajectory, state.field.docks)
        distribution = ReceptorDistribution(
            CommonFieldTime(FIELD_CLOCK_ID, field_input.start_tick, field_input.end_tick),
            (),
        )
        post_field = advance_neutral_fast_shared_field_transient(
            state.field,
            distribution,
            local_inputs,
            substrate,
            afterimage,
        )
        post = _field_state(post_field, field_input.end_tick, state.step_count + 1)
        receipt = _digest(
            {
                "schema": S2LO_SCHEMA,
                "branch": "FIELD",
                "input_digest": event.field_projection_digest,
                "prestate_digest": state.state_digest,
                "poststate_digest": post.state_digest,
                "source_event_count": handoff.source_event_count,
                "contact_count": local_inputs.contact_count,
            }
        )
        return stream.StreamBranchResultV1(
            "FIELD",
            event.field_projection_digest,
            state.state_digest,
            post,
            post.state_digest,
            receipt,
        )

    return advance


def build_stream_event(value: S2LOMaterializedEventV1) -> stream.PerceptionStreamEvent336V1:
    _require(type(value) is S2LOMaterializedEventV1, "exact materialized event required")
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


def _build_config() -> memory.S2JVCoordinatorConfigV1:
    profile = build_s2jw_default_live_profile()
    return memory.build_s2jv_coordinator_config(
        tspm_config=profile.tspm_config,
        b4_capacity=profile.b4_capacity,
        ledger_limits=build_s2jv_ledger_limits(profile),
    )


def _processor(config: memory.S2JVCoordinatorConfigV1) -> stream.RoleFreePerceptionStreamProcessor:
    return stream.RoleFreePerceptionStreamProcessor(
        field_adapter=build_s2lo_field_adapter(),
        memory_adapter=stream.build_s2jw_memory_adapter(config),
        visual_scan=stream.build_s2kq_visual_scan_adapter(config, baseline=False),
        visual_baseline=stream.build_s2kq_visual_scan_adapter(config, baseline=True),
        auditory_scan=stream.build_s2kz_auditory_scan_adapter(config, baseline=False),
        auditory_baseline=stream.build_s2kz_auditory_scan_adapter(config, baseline=True),
    )


def source_hashes(workspace_root: Path) -> dict[str, str]:
    _require(isinstance(workspace_root, Path) and workspace_root.is_absolute(), "absolute workspace Path required")
    result = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        _require(path.is_file(), f"bound source missing: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _scan_record(value: stream.StreamScanResultV1 | None) -> dict[str, object] | None:
    if value is None:
        return None
    hypothesis = value.hypothesis
    hypothesis_payload = None
    if hypothesis is not None:
        payload_builder = getattr(hypothesis, "payload_without_digest", None)
        _require(callable(payload_builder), "hypothesis payload is unavailable")
        payload = payload_builder()
        _require(type(payload) is dict, "hypothesis payload differs")
        _require(_digest(payload) == hypothesis.hypothesis_digest, "hypothesis digest differs")
        hypothesis_payload = {**payload, "hypothesis_digest": hypothesis.hypothesis_digest}
    return {
        "scan_role": value.scan_role,
        "input_digest": value.input_digest,
        "prestate_digest": value.prestate_digest,
        "poststate_digest": value.poststate_digest,
        "decision": value.decision,
        "hypothesis_digest": value.hypothesis_digest,
        "receipt_digest": value.receipt_digest,
        "hypothesis": hypothesis_payload,
    }


def _memory_observation(
    materialized: S2LOMaterializedEventV1,
    result: stream.PerceptionStreamEventResultV1,
) -> dict[str, object] | None:
    if result.memory_result is None:
        return None
    state = result.memory_result.poststate
    source = materialized.operation_payload
    _require(type(state) is memory.S2JVCompositeStateV1, "memory poststate differs")
    _require(type(source) is S2JVBoundAVPairV1, "formation source differs")

    def slow_slots(slots: tuple[object, ...]) -> list[dict[str, object]]:
        observed = []
        for slot in slots:
            if not slot.occupied:
                continue
            values = tuple(slot.prototype_values)
            observed.append(
                {
                    "slot_id": slot.slot_id,
                    "support_count": slot.support_count,
                    "last_selected_step": slot.last_selected_step,
                    "prototype_values": list(values),
                    "prototype_digest": _digest(list(values)),
                }
            )
        return observed

    auditory_values = tuple(source.auditory.timed_frame.frame.values)
    visual_values = tuple(source.visual.timed_frame.frame.values)
    b4_entries = sorted(
        (entry for entry in state.b4_state.entries if entry.occupied),
        key=lambda entry: entry.formation_index,
    )
    fast_slots = [slot for slot in state.tspm_state.fast_state.slots if slot.occupied]
    return {
        "state_digest": state.state_digest,
        "generation": state.generation,
        "formation_values": {
            "auditory": list(auditory_values),
            "visual": list(visual_values),
            "auditory_digest": _digest(list(auditory_values)),
            "visual_digest": _digest(list(visual_values)),
            "av_digest": _digest(list(auditory_values + visual_values)),
        },
        "b4": [
            {
                "slot_id": entry.slot_id,
                "formation_index": entry.formation_index,
                "values_digest": _digest(list(entry.values)),
            }
            for entry in b4_entries
        ],
        "fast": [
            {
                "slot_id": slot.slot_id,
                "support_count": slot.support_count,
                "last_selected_step": slot.last_selected_step,
                "consolidation_count": slot.consolidation_count,
                "auditory_values_digest": _digest(list(slot.auditory_values)),
                "visual_values_digest": _digest(list(slot.visual_values)),
            }
            for slot in fast_slots
        ],
        "auditory_slow": slow_slots(state.tspm_state.auditory_ppb1_state.slots),
        "visual_slow": slow_slots(state.tspm_state.visual_ppb1_state.slots),
    }


def _event_record(
    materialized: S2LOMaterializedEventV1,
    event: stream.PerceptionStreamEvent336V1,
    result: stream.PerceptionStreamEventResultV1,
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
        "prestate_digest": result.prestate_digest,
        "poststate_digest": result.poststate.state_digest,
        "memory_poststate_digest": result.poststate.memory_state_digest,
        "field_receipt_digest": None if result.field_result is None else result.field_result.receipt_digest,
        "memory_receipt_digest": None if result.memory_result is None else result.memory_result.receipt_digest,
        "memory_observation": _memory_observation(materialized, result),
        "primary_scan": _scan_record(result.primary_scan),
        "baseline_scan": _scan_record(result.baseline_scan),
        "error_codes": list(result.error_codes),
        "owner_status": result.owner_poststate.status,
        "owner_poststate_digest": result.owner_poststate.snapshot_digest,
        "result_digest": result.result_digest,
    }


def _initial_stream(
    config: memory.S2JVCoordinatorConfigV1,
    first: S2LOMaterializedEventV1,
) -> stream.PerceptionStreamStateV1:
    field = initial_s2lo_field_state(first.field_input)
    stored = memory.initial_s2jv_composite_state(config)
    return stream.initial_perception_stream_state(
        stream_id="s2ln-perception-stream",
        field_state=field,
        field_state_digest=field.state_digest,
        memory_state=stored,
        memory_state_digest=stored.state_digest,
    )


def _run_stream(mode: str) -> tuple[dict[str, object], stream.PerceptionStreamStateV1, S2LOSourceStream]:
    config = _build_config()
    source = S2LOSourceStream(config.profile, mode=mode)
    band_plan = auditory_scan.build_auditory_band_plan_48()
    first = source.materialize_next(config_digest=config.config_digest, band_plan=band_plan)
    state = _initial_stream(config, first)
    processor = _processor(config)
    records = []
    materialized = first
    expected = MAIN_EVENT_SPECS if mode == "MAIN" else QUALIFICATION_EVENT_SPECS
    for index, spec in enumerate(expected):
        if index:
            materialized = source.materialize_next(
                config_digest=config.config_digest,
                band_plan=band_plan,
            )
        _require(materialized.spec == spec, "materialized event order differs")
        event = build_stream_event(materialized)
        owner = stream.PerceptionEventOwner(
            f"s2ln-event-owner-{spec.ordinal:03d}",
            state.state_digest,
            event.event_digest,
        )
        result = processor.process_once(state=state, event=event, owner=owner)
        records.append(_event_record(materialized, event, result))
        state = result.poststate
        if result.error_codes:
            raise S2LOError("one stream branch failed")
    counters = {
        "event_count": state.processed_event_count,
        "field_attempt_count": state.field_attempt_count,
        "memory_formation_attempt_count": state.memory_formation_attempt_count,
        "scan_attempt_count": state.scan_attempt_count,
        "final_field_digest": state.field_state_digest,
        "final_memory_digest": state.memory_state_digest,
        "stream_status": state.status,
    }
    return {"events": records, "counters": counters}, state, source


def _score_hypothesis(
    scan_record: dict[str, object],
    target: tuple[float, ...],
) -> dict[str, object]:
    hypothesis = scan_record.get("hypothesis")
    _require(type(hypothesis) is dict, "expected hypothesis is absent")
    positions = hypothesis.get("masked_positions", hypothesis.get("masked_bands"))
    proposed = hypothesis["proposed_values"]
    _require(type(positions) is list and type(proposed) is list and len(positions) == len(proposed), "hypothesis shape differs")
    error = sum(abs(float(value) - target[index]) for index, value in zip(positions, proposed, strict=True))
    return {
        "masked_count": len(positions),
        "current_only_loss": 1.0,
        "context_loss": error / len(positions),
        "area": hypothesis["area"],
    }


def _evaluate_main(
    execution: dict[str, object],
    state: stream.PerceptionStreamStateV1,
    source: S2LOSourceStream,
) -> dict[str, object]:
    auditory_values, visual_values = source.evaluation_values()
    events = execution["events"]
    auditory_event = events[16]
    visual_event = events[17]
    auditory_primary = auditory_event["primary_scan"]
    auditory_baseline = auditory_event["baseline_scan"]
    visual_primary = visual_event["primary_scan"]
    visual_baseline = visual_event["baseline_scan"]
    _require(all(type(item) is dict for item in (auditory_primary, auditory_baseline, visual_primary, visual_baseline)), "scan evidence is absent")
    assert isinstance(auditory_primary, dict)
    assert isinstance(auditory_baseline, dict)
    assert isinstance(visual_primary, dict)
    assert isinstance(visual_baseline, dict)
    auditory_score = _score_hypothesis(auditory_primary, auditory_values)
    visual_score = _score_hypothesis(visual_primary, visual_values)
    auditory_primary_hypothesis = auditory_primary["hypothesis"]
    auditory_baseline_hypothesis = auditory_baseline["hypothesis"]
    visual_primary_hypothesis = visual_primary["hypothesis"]
    visual_baseline_hypothesis = visual_baseline["hypothesis"]
    _require(
        all(
            type(item) is dict
            for item in (
                auditory_primary_hypothesis,
                auditory_baseline_hypothesis,
                visual_primary_hypothesis,
                visual_baseline_hypothesis,
            )
        ),
        "one comparison hypothesis is absent",
    )
    primary_baseline_equal = (
        auditory_primary["decision"] == auditory_baseline["decision"]
        and auditory_primary_hypothesis.get("masked_bands") == auditory_baseline_hypothesis.get("masked_bands")
        and auditory_primary_hypothesis["proposed_values"] == auditory_baseline_hypothesis["proposed_values"]
        and visual_primary["decision"] == visual_baseline["decision"]
        and visual_primary_hypothesis.get("masked_positions") == visual_baseline_hypothesis.get("masked_positions")
        and visual_primary_hypothesis["proposed_values"] == visual_baseline_hypothesis["proposed_values"]
    )
    stored = state.memory_state
    _require(type(stored) is memory.S2JVCompositeStateV1, "final memory state differs")
    auditory_stable = tuple(
        slot for slot in stored.tspm_state.auditory_ppb1_state.slots if slot.occupied and slot.stable
    )
    visual_stable = tuple(
        slot for slot in stored.tspm_state.visual_ppb1_state.slots if slot.occupied and slot.stable
    )
    b4_indexes = tuple(
        sorted(entry.formation_index for entry in stored.b4_state.entries if entry.occupied)
    )
    transition_events = tuple(events[index] for index in (2, 4, 6))

    def transition_valid(modality: str) -> bool:
        bank = f"{modality}_slow"
        prior: tuple[float, ...] | None = None
        for position, event in enumerate(transition_events, start=1):
            observation = event["memory_observation"]
            source_values = tuple(observation["formation_values"][modality])
            slots = observation[bank]
            if len(slots) != 1 or slots[0]["support_count"] != position:
                return False
            actual = tuple(slots[0]["prototype_values"])
            expected = source_values if prior is None else tuple(
                (1.0 - 0.05) * previous + 0.05 * current
                for previous, current in zip(prior, source_values, strict=True)
            )
            if actual != expected or slots[0]["prototype_digest"] != _digest(list(actual)):
                return False
            prior = actual
        return True

    ppb_transition_integrity = {
        "auditory": transition_valid("auditory"),
        "visual": transition_valid("visual"),
        "event_codes": [event["event_code"] for event in transition_events],
        "support_chain": [1, 2, 3],
    }
    target_absent_a = all(
        not entry.occupied or tuple(entry.values) != auditory_values + visual_values
        for entry in stored.b4_state.entries
    ) and all(
        not slot.occupied
        or tuple(slot.auditory_values) != auditory_values
        or tuple(slot.visual_values) != visual_values
        for slot in stored.tspm_state.fast_state.slots
    )
    confirmed = (
        target_absent_a
        and b4_indexes == tuple(range(8, 17))
        and ppb_transition_integrity["auditory"]
        and ppb_transition_integrity["visual"]
        and len(auditory_stable) == len(visual_stable) == 1
        and auditory_stable[0].support_count == visual_stable[0].support_count == 3
        and auditory_primary["decision"] == visual_primary["decision"] == "ADMIT_SINGLE_CONTEXT"
        and auditory_score["area"] == "B_STABLE_AUDITORY"
        and visual_score["area"] == "B_STABLE"
        and auditory_score["context_loss"] < auditory_score["current_only_loss"]
        and visual_score["context_loss"] < visual_score["current_only_loss"]
        and primary_baseline_equal
        and execution["counters"]["event_count"] == MAIN_EVENT_COUNT
        and execution["counters"]["memory_formation_attempt_count"] == MAIN_FORMATION_COUNT
        and execution["counters"]["scan_attempt_count"] == 4
    )
    payload = {
        "status": (
            "S2LN_ROLE_FREE_DISTRIBUTED_AV_EXPERIENCE_CONFIRMED"
            if confirmed
            else "S2LN_FUNCTION_FALSIFIED"
        ),
        "auditory": auditory_score,
        "visual": visual_score,
        "target_absent_from_a_recent": target_absent_a,
        "b4_formation_indexes": list(b4_indexes),
        "ppb_transition_integrity": ppb_transition_integrity,
        "auditory_stable_support": None if not auditory_stable else auditory_stable[0].support_count,
        "visual_stable_support": None if not visual_stable else visual_stable[0].support_count,
        "stable_slot_counts": [len(auditory_stable), len(visual_stable)],
        "primary_baseline_equal": primary_baseline_equal,
        "memory_read_only_during_cues": (
            events[16]["primary_scan"]["prestate_digest"]
            == events[16]["primary_scan"]["poststate_digest"]
            == events[17]["primary_scan"]["prestate_digest"]
            == events[17]["primary_scan"]["poststate_digest"]
            == state.memory_state_digest
        ),
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def neutral_qualification_record(workspace_root: Path) -> dict[str, object]:
    execution, state, _ = _run_stream("QUALIFICATION")
    _require(
        execution["counters"]["event_count"] == 3
        and execution["counters"]["field_attempt_count"] == 3
        and execution["counters"]["memory_formation_attempt_count"] == 1
        and execution["counters"]["scan_attempt_count"] == 4
        and state.status == "OPEN",
        "qualification counters differ",
    )
    payload = {
        "schema": S2LO_RESULT_SCHEMA,
        "mode": "QUALIFICATION",
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": source_hashes(workspace_root),
        "plan": {
            "qualification_id": QUALIFICATION_ID,
            "main_execution_enabled": MAIN_EXECUTION_ENABLED,
            "authorized_run_id": AUTHORIZED_RUN_ID,
            "event_spec_digests": [item.spec_digest for item in QUALIFICATION_EVENT_SPECS],
            "main_story_executed": False,
            "raw_payload_retained": False,
        },
        "execution": execution,
        "evaluation": None,
    }
    return {**payload, "record_digest": _digest(payload)}


def _main_record(workspace_root: Path, run_id: str) -> dict[str, object]:
    execution, state, source = _run_stream("MAIN")
    evaluation = _evaluate_main(execution, state, source)
    payload = {
        "schema": S2LO_RESULT_SCHEMA,
        "mode": "MAIN",
        "run_id": run_id,
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": source_hashes(workspace_root),
        "plan": {
            "event_spec_digests": [item.spec_digest for item in MAIN_EVENT_SPECS],
            "event_count": MAIN_EVENT_COUNT,
            "formation_count": MAIN_FORMATION_COUNT,
            "field_contacts": MAIN_FIELD_CONTACTS,
            "memory_l1_terms": MAIN_MEMORY_L1_TERMS,
            "scan_comparisons_max": MAIN_SCAN_COMPARISONS,
            "raw_bytes_max": MAIN_RAW_BYTES,
            "raw_payload_retained": False,
        },
        "execution": execution,
        "evaluation": evaluation,
    }
    return {**payload, "record_digest": _digest(payload)}


def write_result_once(output_root: Path, run_id: str, record: dict[str, object]) -> Path:
    _require(isinstance(output_root, Path) and output_root.is_absolute(), "absolute output Path required")
    _require(type(run_id) is str and _RUN_ID.fullmatch(run_id) is not None, "run id differs")
    _require(type(record) is dict and record.get("record_digest") is not None, "record differs")
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    target = run_dir / "result.json"
    temporary = run_dir / ".result.json.tmp"
    data = _canonical_bytes(record, newline=True)
    _require(len(data) <= MAX_RESULT_BYTES, "result exceeds its bounded envelope")
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
    _require(MAIN_EXECUTION_ENABLED is True, "main execution gate is closed")
    _require(run_id == AUTHORIZED_RUN_ID, "run id is not authorized")
    _require(not _MAIN_USED and _MAIN_LOCK.acquire(blocking=False), "main execution is already consumed")
    _MAIN_USED = True
    try:
        record = _main_record(workspace_root, run_id)
        return write_result_once(output_root, run_id, record)
    finally:
        MAIN_EXECUTION_ENABLED = False
        _MAIN_LOCK.release()


assert len(MAIN_EVENT_SPECS) == MAIN_EVENT_COUNT
assert sum(item.event_type == "COMPLETE_AV_PERCEPTION" for item in MAIN_EVENT_SPECS) == 16
assert sum(item.event_type == "PARTIAL_AUDITORY_CUE" for item in MAIN_EVENT_SPECS) == 1
assert sum(item.event_type == "PARTIAL_VISUAL_CUE" for item in MAIN_EVENT_SPECS) == 1

__all__: tuple[str, ...] = ()
