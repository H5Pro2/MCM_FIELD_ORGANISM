"""Private S2-SP bridge for already materialized OA half-profile AV pairs."""

from __future__ import annotations

from dataclasses import dataclass

from tools import _s2jw_default_live_av_pairing as pairing
from tools import _s2nl_private_half_profile_binding as half_profile
from tools import _s2ob_private_caller_binding as oa


SCHEMA = "s2sp.oa-materialization-adapter.v1"


class S2SPOAAdapterError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise S2SPOAAdapterError(code)


@dataclass(frozen=True, slots=True)
class S2SPOAMaterializedPairV1:
    event_id: str
    ordinal: int
    pair: pairing.S2JVBoundAVPairV1
    pcm_digest: str
    rgb_digest: str
    runtime_clock_id: str
    audio_window: tuple[int, int]
    visual_window: tuple[int, int]
    common_window: tuple[int, int]
    evidence_digest: str
    schema: str = SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "event_id": self.event_id,
            "ordinal": self.ordinal,
            "pairing_digest": self.pair.pairing_digest,
            "pcm_digest": self.pcm_digest,
            "rgb_digest": self.rgb_digest,
            "runtime_clock_id": self.runtime_clock_id,
            "audio_window": list(self.audio_window),
            "visual_window": list(self.visual_window),
            "common_window": list(self.common_window),
        }


def materialize_next(materializer: oa.Materializer, event: oa.Event) -> S2SPOAMaterializedPairV1:
    """Consume one OA AV event; no receptor or NJ work is repeated here."""
    _require(event.kind == oa.AV, "OA_AV_EVENT_REQUIRED")
    _require(event.pcm is not None and event.rgb is not None, "OA_AV_PAYLOAD_REQUIRED")
    _require(event.audio_common is not None and event.visual_common is not None, "OA_TIME_REQUIRED")
    item = materializer.next(event)
    pair = item.event.operation_payload
    _require(type(pair) is pairing.S2JVBoundAVPairV1, "OA_PAIR_REQUIRED")
    _require(pair.schema == pairing.HALF_PAIRING_SCHEMA, "HALF_PAIR_REQUIRED")
    _require(pair.plan.pair_id == event.event_id, "PAIR_ID_MISMATCH")
    _require(pair.plan.auditory_payload_digest == event.pcm.sha256, "PCM_BINDING_MISMATCH")
    _require(pair.plan.visual_payload_digest == event.rgb.sha256, "RGB_BINDING_MISMATCH")
    audio = pair.auditory.timed_frame
    visual = pair.visual.timed_frame
    _require(audio.field_time.clock_id == visual.field_time.clock_id == oa.CLOCK, "RUNTIME_CLOCK_MISMATCH")
    field_input = event.field_payload
    _require(type(field_input) is oa.r.ng.field.S2LOFieldInputV1, "FIELD_INPUT_TYPE_INVALID")
    _require(field_input.timed_frames == (audio, visual)
             and field_input.start_tick <= audio.field_time.window_start_tick
             and field_input.end_tick == audio.field_time.window_end_tick
             and field_input.end_tick == visual.field_time.window_end_tick, "FIELD_TIME_MISMATCH")
    _require(audio.field_time.window_start_tick == event.audio_common[0]
             and audio.field_time.window_end_tick == event.audio_common[1], "AUDIO_TIME_MISMATCH")
    _require(visual.field_time.window_start_tick == event.visual_common[0]
             and visual.field_time.window_end_tick == event.visual_common[1], "VISUAL_TIME_MISMATCH")
    _require(pair.plan.common_field_clock_id == oa.CLOCK, "PAIR_CLOCK_MISMATCH")
    payload = {
        "schema": SCHEMA,
        "event_id": event.event_id,
        "ordinal": event.ordinal,
        "pairing_digest": pair.pairing_digest,
        "pcm_digest": event.pcm.sha256,
        "rgb_digest": event.rgb.sha256,
        "runtime_clock_id": oa.CLOCK,
        "audio_window": list(event.audio_common),
        "visual_window": list(event.visual_common),
        "common_window": [event.field_window[0], event.field_window[1]],
    }
    return S2SPOAMaterializedPairV1(
        event.event_id, event.ordinal, pair, event.pcm.sha256, event.rgb.sha256,
        oa.CLOCK, event.audio_common, event.visual_common, event.field_window,
        oa.digest(payload),
    )


def bind_materialized_input(
    item: oa.Input,
    *,
    event_id: str,
    ordinal: int,
    pcm_digest: str,
    rgb_digest: str,
) -> S2SPOAMaterializedPairV1:
    """Adapt one already bound OA AV input without another receptor/NJ call."""
    _require(type(item) is oa.Input, "OA_INPUT_REQUIRED")
    event = item.event
    _require(event.event_type == oa.AV and event.ordinal == ordinal and event.event_id == event_id,
             "OA_INPUT_EVENT_MISMATCH")
    pair = event.operation_payload
    _require(type(pair) is pairing.S2JVBoundAVPairV1 and pair.schema == pairing.HALF_PAIRING_SCHEMA,
             "OA_PAIR_REQUIRED")
    _require(pair.plan.pair_id == event_id and pair.plan.auditory_payload_digest == pcm_digest
             and pair.plan.visual_payload_digest == rgb_digest, "OA_PAIR_BINDING_MISMATCH")
    audio = pair.auditory.timed_frame
    visual = pair.visual.timed_frame
    _require(audio.field_time.clock_id == visual.field_time.clock_id == oa.CLOCK, "RUNTIME_CLOCK_MISMATCH")
    field_input = event.field_payload
    _require(type(field_input) is oa.r.ng.field.S2LOFieldInputV1, "FIELD_INPUT_TYPE_INVALID")
    _require(field_input.timed_frames == (audio, visual)
             and field_input.start_tick <= audio.field_time.window_start_tick
             and field_input.end_tick == audio.field_time.window_end_tick
             and field_input.end_tick == visual.field_time.window_end_tick, "FIELD_TIME_MISMATCH")
    payload = {
        "schema": SCHEMA,
        "event_id": event_id,
        "ordinal": ordinal,
        "pairing_digest": pair.pairing_digest,
        "pcm_digest": pcm_digest,
        "rgb_digest": rgb_digest,
        "runtime_clock_id": oa.CLOCK,
        "audio_window": [audio.field_time.window_start_tick, audio.field_time.window_end_tick],
        "visual_window": [visual.field_time.window_start_tick, visual.field_time.window_end_tick],
        "common_window": [field_input.start_tick, field_input.end_tick],
    }
    return S2SPOAMaterializedPairV1(
        event_id, ordinal, pair, pcm_digest, rgb_digest, oa.CLOCK,
        tuple(payload["audio_window"]), tuple(payload["visual_window"]), tuple(payload["common_window"]),
        oa.digest(payload),
    )


def validate_half_profile_pair(value: S2SPOAMaterializedPairV1) -> None:
    _require(type(value) is S2SPOAMaterializedPairV1 and value.schema == SCHEMA, "ADAPTER_FORM_INVALID")
    _require(value.pair.schema == pairing.HALF_PAIRING_SCHEMA, "HALF_PAIR_REQUIRED")
    _require(value.pair.plan.profile_binding_digest == half_profile.build_private_half_profile().profile.digest(),
             "PROFILE_BINDING_MISMATCH")
    _require(value.evidence_digest == oa.digest(value.payload_without_digest()), "ADAPTER_DIGEST_INVALID")
