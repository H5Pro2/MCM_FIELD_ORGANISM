"""Private source-neutral AV pairing for one default-live memory input."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from mcm_field_organism import _ppb1_active_receptor_batch_binding as active
from mcm_field_organism._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from tools._s2jw_default_live_profile import (
    EXPECTED_SOURCE_PROFILE_DIGEST,
    S2JWDefaultLiveProfileV1,
)


S2JW_PAIRING_SCHEMA = "s2jw.default-live-av-pairing.v1"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9.-]{1,95}$")


class S2JWPairingError(ValueError):
    """A reduced AV pair is not bound to one valid source window."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2JWPairingError(message)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _identifier(value: object, role: str) -> str:
    _require(
        isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None,
        f"{role} is not a canonical identifier",
    )
    return value


def _values_digest(frame: OrganismTimedReceptorFrame) -> str:
    values = frame.frame.values
    _require(
        type(values) is tuple
        and all(
            type(value) in (int, float)
            and math.isfinite(float(value))
            and 0.0 <= float(value) <= 1.0
            for value in values
        ),
        "receptor values must be one finite nonnegative tuple",
    )
    return _digest(list(values))


def _validate_timed_frame(
    frame: object,
    *,
    modality: str,
    profile: PPB1ReceptorProfileBinding,
) -> OrganismTimedReceptorFrame:
    _require(type(frame) is OrganismTimedReceptorFrame, "exact timed frame required")
    assert isinstance(frame, OrganismTimedReceptorFrame)
    config = (
        profile.auditory_config if modality == "auditory" else profile.visual_config
    )
    receptor = frame.frame
    _require(
        receptor.modality_id == modality
        and receptor.geometry_id == config.geometry_id
        and receptor.carrier_ids == config.carrier_ids
        and len(receptor.values) == len(config.carrier_ids),
        f"{modality} geometry or carrier binding differs",
    )
    _values_digest(frame)
    return frame


def _plan_payload(
    *,
    pair_id: str,
    source_contract_id: str,
    source_profile_digest: str,
    profile_binding_digest: str,
    auditory_payload_digest: str,
    visual_payload_digest: str,
    auditory_timed_frame_digest: str,
    visual_timed_frame_digest: str,
    auditory_values_digest: str,
    visual_values_digest: str,
    common_field_clock_id: str,
    overlap_start_tick: int,
    overlap_end_tick: int,
) -> dict[str, object]:
    return {
        "schema": S2JW_PAIRING_SCHEMA,
        "pair_id": pair_id,
        "source_contract_id": source_contract_id,
        "source_profile_digest": source_profile_digest,
        "profile_binding_digest": profile_binding_digest,
        "auditory_payload_digest": auditory_payload_digest,
        "visual_payload_digest": visual_payload_digest,
        "auditory_timed_frame_digest": auditory_timed_frame_digest,
        "visual_timed_frame_digest": visual_timed_frame_digest,
        "auditory_values_digest": auditory_values_digest,
        "visual_values_digest": visual_values_digest,
        "common_field_clock_id": common_field_clock_id,
        "overlap_start_tick": overlap_start_tick,
        "overlap_end_tick": overlap_end_tick,
    }


@dataclass(frozen=True, slots=True)
class S2JVPairingPlanV1:
    pair_id: str
    source_contract_id: str
    source_profile_digest: str
    profile_binding_digest: str
    auditory_payload_digest: str
    visual_payload_digest: str
    auditory_timed_frame_digest: str
    visual_timed_frame_digest: str
    auditory_values_digest: str
    visual_values_digest: str
    common_field_clock_id: str
    overlap_start_tick: int
    overlap_end_tick: int
    plan_digest: str
    schema: str = S2JW_PAIRING_SCHEMA

    def __post_init__(self) -> None:
        _identifier(self.pair_id, "pair_id")
        _identifier(self.source_contract_id, "source_contract_id")
        _identifier(self.common_field_clock_id, "common_field_clock_id")
        digests = (
            self.source_profile_digest,
            self.profile_binding_digest,
            self.auditory_payload_digest,
            self.visual_payload_digest,
            self.auditory_timed_frame_digest,
            self.visual_timed_frame_digest,
            self.auditory_values_digest,
            self.visual_values_digest,
        )
        _require(
            self.schema == S2JW_PAIRING_SCHEMA
            and all(_valid_digest(value) for value in digests)
            and self.source_profile_digest == EXPECTED_SOURCE_PROFILE_DIGEST
            and type(self.overlap_start_tick) is int
            and type(self.overlap_end_tick) is int
            and 0 <= self.overlap_start_tick < self.overlap_end_tick
            and self.plan_digest == _digest(self.payload_without_digest()),
            "pairing plan is incomplete or digest inconsistent",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return _plan_payload(
            pair_id=self.pair_id,
            source_contract_id=self.source_contract_id,
            source_profile_digest=self.source_profile_digest,
            profile_binding_digest=self.profile_binding_digest,
            auditory_payload_digest=self.auditory_payload_digest,
            visual_payload_digest=self.visual_payload_digest,
            auditory_timed_frame_digest=self.auditory_timed_frame_digest,
            visual_timed_frame_digest=self.visual_timed_frame_digest,
            auditory_values_digest=self.auditory_values_digest,
            visual_values_digest=self.visual_values_digest,
            common_field_clock_id=self.common_field_clock_id,
            overlap_start_tick=self.overlap_start_tick,
            overlap_end_tick=self.overlap_end_tick,
        )


def build_s2jv_pairing_plan(
    *,
    pair_id: str,
    source_contract_id: str,
    profile: S2JWDefaultLiveProfileV1,
    auditory: OrganismTimedReceptorFrame,
    visual: OrganismTimedReceptorFrame,
    auditory_payload_digest: str,
    visual_payload_digest: str,
) -> S2JVPairingPlanV1:
    _require(type(profile) is S2JWDefaultLiveProfileV1, "exact profile binding required")
    auditory = _validate_timed_frame(auditory, modality="auditory", profile=profile.profile)
    visual = _validate_timed_frame(visual, modality="visual", profile=profile.profile)
    _require(
        _valid_digest(auditory_payload_digest) and _valid_digest(visual_payload_digest),
        "raw payload digests are missing",
    )
    _require(
        auditory.field_time.clock_id == visual.field_time.clock_id,
        "AV frames require one common field clock",
    )
    overlap_start = max(
        auditory.field_time.window_start_tick,
        visual.field_time.window_start_tick,
    )
    overlap_end = min(
        auditory.field_time.window_end_tick,
        visual.field_time.window_end_tick,
    )
    _require(overlap_start < overlap_end, "AV source windows do not overlap")
    auditory_binding = active._build_stream(
        ReceptorTimeSequence(
            "auditory",
            profile.profile.auditory_config.geometry_id,
            auditory.field_time.clock_id,
            (auditory,),
        ),
        profile.profile.auditory_config,
    ).timed_frames[0]
    visual_binding = active._build_stream(
        ReceptorTimeSequence(
            "visual",
            profile.profile.visual_config.geometry_id,
            visual.field_time.clock_id,
            (visual,),
        ),
        profile.profile.visual_config,
    ).timed_frames[0]
    payload = _plan_payload(
        pair_id=_identifier(pair_id, "pair_id"),
        source_contract_id=_identifier(source_contract_id, "source_contract_id"),
        source_profile_digest=profile.source_profile_digest,
        profile_binding_digest=profile.profile.digest(),
        auditory_payload_digest=auditory_payload_digest,
        visual_payload_digest=visual_payload_digest,
        auditory_timed_frame_digest=auditory_binding.timed_frame_provenance_digest,
        visual_timed_frame_digest=visual_binding.timed_frame_provenance_digest,
        auditory_values_digest=_values_digest(auditory),
        visual_values_digest=_values_digest(visual),
        common_field_clock_id=auditory.field_time.clock_id,
        overlap_start_tick=overlap_start,
        overlap_end_tick=overlap_end,
    )
    return S2JVPairingPlanV1(
        payload["pair_id"],  # type: ignore[arg-type]
        payload["source_contract_id"],  # type: ignore[arg-type]
        profile.source_profile_digest,
        profile.profile.digest(),
        auditory_payload_digest,
        visual_payload_digest,
        auditory_binding.timed_frame_provenance_digest,
        visual_binding.timed_frame_provenance_digest,
        payload["auditory_values_digest"],  # type: ignore[arg-type]
        payload["visual_values_digest"],  # type: ignore[arg-type]
        auditory.field_time.clock_id,
        overlap_start,
        overlap_end,
        _digest(payload),
    )


@dataclass(frozen=True, slots=True)
class S2JVBoundAVPairV1:
    plan: S2JVPairingPlanV1
    envelope: active.PPB1ActiveReceptorBatchEnvelope
    auditory: active.PPB1ActiveReceptorTimedFrameBinding
    visual: active.PPB1ActiveReceptorTimedFrameBinding
    av_values_digest: str
    pairing_digest: str
    schema: str = S2JW_PAIRING_SCHEMA

    def __post_init__(self) -> None:
        av_values = self.auditory.timed_frame.frame.values + self.visual.timed_frame.frame.values
        payload = {
            "schema": self.schema,
            "plan_digest": self.plan.plan_digest,
            "envelope_digest": self.envelope.envelope_digest,
            "auditory_timed_frame_digest": self.auditory.timed_frame_provenance_digest,
            "visual_timed_frame_digest": self.visual.timed_frame_provenance_digest,
            "av_values_digest": self.av_values_digest,
        }
        _require(
            self.schema == S2JW_PAIRING_SCHEMA
            and type(self.plan) is S2JVPairingPlanV1
            and type(self.envelope) is active.PPB1ActiveReceptorBatchEnvelope
            and type(self.auditory) is active.PPB1ActiveReceptorTimedFrameBinding
            and type(self.visual) is active.PPB1ActiveReceptorTimedFrameBinding
            and self.envelope.profile_id == "default-live"
            and self.auditory in self.envelope.auditory_stream.timed_frames
            and self.visual in self.envelope.visual_stream.timed_frames
            and self.av_values_digest == _digest(list(av_values))
            and self.pairing_digest == _digest(payload),
            "bound AV pair is incomplete or digest inconsistent",
        )


def bind_s2jv_default_live_pair(
    *,
    pairing_plan: S2JVPairingPlanV1,
    profile: S2JWDefaultLiveProfileV1,
    auditory: OrganismTimedReceptorFrame,
    visual: OrganismTimedReceptorFrame,
) -> S2JVBoundAVPairV1:
    _require(type(pairing_plan) is S2JVPairingPlanV1, "exact pairing plan required")
    _require(type(profile) is S2JWDefaultLiveProfileV1, "exact profile binding required")
    rebuilt = build_s2jv_pairing_plan(
        pair_id=pairing_plan.pair_id,
        source_contract_id=pairing_plan.source_contract_id,
        profile=profile,
        auditory=auditory,
        visual=visual,
        auditory_payload_digest=pairing_plan.auditory_payload_digest,
        visual_payload_digest=pairing_plan.visual_payload_digest,
    )
    _require(rebuilt == pairing_plan, "pairing plan does not match receptor sources")
    auditory_stream = active._build_stream(
        ReceptorTimeSequence(
            "auditory",
            profile.profile.auditory_config.geometry_id,
            auditory.field_time.clock_id,
            (auditory,),
        ),
        profile.profile.auditory_config,
    )
    visual_stream = active._build_stream(
        ReceptorTimeSequence(
            "visual",
            profile.profile.visual_config.geometry_id,
            visual.field_time.clock_id,
            (visual,),
        ),
        profile.profile.visual_config,
    )
    source_batch_payload = {
        "schema": S2JW_PAIRING_SCHEMA,
        "pairing_plan_digest": pairing_plan.plan_digest,
        "auditory_stream_digest": auditory_stream.stream_digest,
        "visual_stream_digest": visual_stream.stream_digest,
    }
    source_batch_digest = _digest(source_batch_payload)
    envelope_payload = {
        "schema_version": active.PPB1_ACTIVE_BATCH_SCHEMA_VERSION,
        "binding_id": pairing_plan.pair_id,
        "source_contract_id": pairing_plan.source_contract_id,
        "source_contract_digest": profile.source_profile_digest,
        "source_batch_digest": source_batch_digest,
        "profile_id": "default-live",
        "profile_binding_digest": profile.profile.digest(),
        "parameter_digest": profile.profile.parameter_digest,
        "common_field_clock_id": pairing_plan.common_field_clock_id,
        "auditory_stream_digest": auditory_stream.stream_digest,
        "visual_stream_digest": visual_stream.stream_digest,
    }
    envelope = active.PPB1ActiveReceptorBatchEnvelope(
        pairing_plan.pair_id,
        pairing_plan.source_contract_id,
        profile.source_profile_digest,
        source_batch_digest,
        "default-live",
        profile.profile.digest(),
        profile.profile.parameter_digest,
        pairing_plan.common_field_clock_id,
        auditory_stream,
        visual_stream,
        active._digest(envelope_payload),
    )
    auditory_binding = auditory_stream.timed_frames[0]
    visual_binding = visual_stream.timed_frames[0]
    av_digest = _digest(
        list(auditory_binding.timed_frame.frame.values)
        + list(visual_binding.timed_frame.frame.values)
    )
    payload = {
        "schema": S2JW_PAIRING_SCHEMA,
        "plan_digest": pairing_plan.plan_digest,
        "envelope_digest": envelope.envelope_digest,
        "auditory_timed_frame_digest": auditory_binding.timed_frame_provenance_digest,
        "visual_timed_frame_digest": visual_binding.timed_frame_provenance_digest,
        "av_values_digest": av_digest,
    }
    return S2JVBoundAVPairV1(
        pairing_plan,
        envelope,
        auditory_binding,
        visual_binding,
        av_digest,
        _digest(payload),
    )
