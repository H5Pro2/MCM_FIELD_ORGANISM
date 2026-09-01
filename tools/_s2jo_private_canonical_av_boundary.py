"""Private canonical AV boundary and finite simulation reference for S2-JO."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
import hashlib
import json
import math
import re
import struct

import numpy as np

from mcm_field_organism.broadband_hearing_path import (
    AuditoryReceptorState,
    BroadbandHearingPath,
)
from mcm_field_organism.finite_video_path import (
    LocalChannelGridReceptor,
    VisualGridConfig,
    VisualReceptorState,
)
from mcm_field_organism.log_spectral_receptor import (
    LogSpectralConfig,
    LogSpectralReceptor,
)
from mcm_field_organism.receptor_contract import technical_identifier


S2JO_VISUAL_SCHEMA = "s2jo.canonical-visual-frame.v1"
S2JO_AUDIO_SCHEMA = "s2jo.canonical-pcm-audio-hop.v1"
S2JO_PROVENANCE_SCHEMA = "s2jo.source-audit-provenance.v1"
S2JO_INPUT_BINDING_SCHEMA = "s2jo.canonical-input-binding.v1"
S2JO_EPISODE_SCHEMA = "s2jo.canonical-av-episode-receipt.v1"
S2JO_REDUCED_SCHEMA = "s2jo.reduced-receptor-sequence-receipt.v1"
S2JO_LEDGER_SCHEMA = "s2jo.streaming-resource-ledger.v1"

S2JO_EPISODE_ID = "s2jn.digital.av.episode.v1"
S2JO_CLOCK_ID = "s2jn.digital.av.clock"
S2JO_TICKS_PER_SECOND = 1_000_000_000
S2JO_DURATION_TICKS = 200_000_000

S2JO_VISUAL_CONFIG = VisualGridConfig(1920, 1080, 12, 8, 30.0)
S2JO_AUDIO_CONFIG = LogSpectralConfig(48000, 4800, 480, 50.0, 18000.0, 48)

S2JO_FRAME_COUNT = 6
S2JO_HOP_COUNT = 20
S2JO_AUDIO_STATE_COUNT = 11
S2JO_FRAME_BYTES = 6_220_800
S2JO_HOP_BYTES = 1_920
S2JO_RAW_BYTES = 37_363_200
S2JO_OPERATION_COUNT = 55

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SOURCE_CLASSES = frozenset(
    {
        "BROWSER_VIEWPORT",
        "DESKTOP_CAPTURE",
        "VIDEO_DECODE",
        "SIMULATION_RENDER",
        "CAMERA_CAPTURE",
        "VIDEO_AUDIO",
        "SYSTEM_AUDIO",
        "SIMULATION_AUDIO",
        "MICROPHONE_CAPTURE",
    }
)


class S2JOCanonicalBoundaryError(ValueError):
    """One fail-closed violation of the private S2-JO boundary."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _require_digest(value: object, role: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise S2JOCanonicalBoundaryError(
            "S2JO_INVALID_DIGEST", f"{role} must be lowercase SHA-256"
        )
    return value


def _require_identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise S2JOCanonicalBoundaryError("S2JO_INVALID_ID", str(exc)) from exc


def _require_index(value: object, role: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise S2JOCanonicalBoundaryError(
            "S2JO_INVALID_POSITION", f"{role} must be a non-negative integer"
        )
    return value


def _require_window(start: object, end: object) -> tuple[int, int]:
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or start < 0
        or end <= start
        or end > S2JO_DURATION_TICKS
    ):
        raise S2JOCanonicalBoundaryError(
            "S2JO_INVALID_TIME", "window must be positive within the episode"
        )
    return start, end


def _visual_functional_payload(
    *,
    episode_id: str,
    frame_index: int,
    shape: tuple[int, int, int],
    clock_id: str,
    window_start_tick: int,
    window_end_tick: int,
    pixel_digest: str,
) -> dict[str, object]:
    return {
        "schema": S2JO_VISUAL_SCHEMA,
        "episode_id": episode_id,
        "frame_index": frame_index,
        "pixel_format": "RGB8",
        "dtype": "uint8",
        "shape": list(shape),
        "geometry_id": S2JO_VISUAL_CONFIG.geometry_id,
        "clock_id": clock_id,
        "window_start_tick": window_start_tick,
        "window_end_tick": window_end_tick,
        "pixel_digest": pixel_digest,
    }


@dataclass(frozen=True, slots=True)
class CanonicalVisualFrameV1:
    schema: str
    episode_id: str
    frame_index: int
    pixel_format: str
    dtype: str
    shape: tuple[int, int, int]
    geometry_id: str
    clock_id: str
    window_start_tick: int
    window_end_tick: int
    pixel_bytes: bytes = field(repr=False, compare=False)
    pixel_digest: str
    functional_input_digest: str

    def __post_init__(self) -> None:
        if self.schema != S2JO_VISUAL_SCHEMA:
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_SCHEMA", "visual schema changed"
            )
        episode_id = _require_identifier(self.episode_id, "episode_id")
        clock_id = _require_identifier(self.clock_id, "clock_id")
        frame_index = _require_index(self.frame_index, "frame_index")
        start, end = _require_window(self.window_start_tick, self.window_end_tick)
        shape = tuple(self.shape)
        if (
            self.pixel_format != "RGB8"
            or self.dtype != "uint8"
            or shape != (1080, 1920, 3)
            or self.geometry_id != S2JO_VISUAL_CONFIG.geometry_id
        ):
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_VISUAL_FORM", "visual form differs from default-live"
            )
        if type(self.pixel_bytes) is not bytes or len(self.pixel_bytes) != S2JO_FRAME_BYTES:
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_VISUAL_FORM", "visual payload must be exact RGB8 bytes"
            )
        pixel_digest = hashlib.sha256(self.pixel_bytes).hexdigest()
        if self.pixel_digest != pixel_digest:
            raise S2JOCanonicalBoundaryError(
                "S2JO_PAYLOAD_DIGEST_MISMATCH", "visual payload digest differs"
            )
        payload = _visual_functional_payload(
            episode_id=episode_id,
            frame_index=frame_index,
            shape=shape,
            clock_id=clock_id,
            window_start_tick=start,
            window_end_tick=end,
            pixel_digest=pixel_digest,
        )
        if self.functional_input_digest != _digest(payload):
            raise S2JOCanonicalBoundaryError(
                "S2JO_FUNCTIONAL_DIGEST_MISMATCH",
                "visual functional digest contains different or coupled data",
            )
        object.__setattr__(self, "episode_id", episode_id)
        object.__setattr__(self, "clock_id", clock_id)
        object.__setattr__(self, "shape", shape)

    @classmethod
    def build(
        cls,
        *,
        episode_id: str,
        frame_index: int,
        clock_id: str,
        window_start_tick: int,
        window_end_tick: int,
        pixel_bytes: bytes,
    ) -> "CanonicalVisualFrameV1":
        pixel_digest = hashlib.sha256(pixel_bytes).hexdigest()
        payload = _visual_functional_payload(
            episode_id=episode_id,
            frame_index=frame_index,
            shape=(1080, 1920, 3),
            clock_id=clock_id,
            window_start_tick=window_start_tick,
            window_end_tick=window_end_tick,
            pixel_digest=pixel_digest,
        )
        return cls(
            S2JO_VISUAL_SCHEMA,
            episode_id,
            frame_index,
            "RGB8",
            "uint8",
            (1080, 1920, 3),
            S2JO_VISUAL_CONFIG.geometry_id,
            clock_id,
            window_start_tick,
            window_end_tick,
            pixel_bytes,
            pixel_digest,
            _digest(payload),
        )


def _audio_functional_payload(
    *,
    episode_id: str,
    hop_index: int,
    clock_id: str,
    window_start_tick: int,
    window_end_tick: int,
    pcm_digest: str,
) -> dict[str, object]:
    return {
        "schema": S2JO_AUDIO_SCHEMA,
        "episode_id": episode_id,
        "hop_index": hop_index,
        "encoding": "PCM_F32LE",
        "channels": 1,
        "sample_rate_hz": 48000,
        "sample_count": 480,
        "sample_domain": "finite[-1,1]",
        "clock_id": clock_id,
        "window_start_tick": window_start_tick,
        "window_end_tick": window_end_tick,
        "pcm_digest": pcm_digest,
    }


@dataclass(frozen=True, slots=True)
class CanonicalPCMAudioHopV1:
    schema: str
    episode_id: str
    hop_index: int
    encoding: str
    channels: int
    sample_rate_hz: int
    sample_count: int
    sample_domain: str
    clock_id: str
    window_start_tick: int
    window_end_tick: int
    pcm_bytes: bytes = field(repr=False, compare=False)
    pcm_digest: str
    functional_input_digest: str

    def __post_init__(self) -> None:
        if self.schema != S2JO_AUDIO_SCHEMA:
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_SCHEMA", "audio schema changed"
            )
        episode_id = _require_identifier(self.episode_id, "episode_id")
        clock_id = _require_identifier(self.clock_id, "clock_id")
        hop_index = _require_index(self.hop_index, "hop_index")
        start, end = _require_window(self.window_start_tick, self.window_end_tick)
        if (
            self.encoding != "PCM_F32LE"
            or self.channels != 1
            or self.sample_rate_hz != 48000
            or self.sample_count != 480
            or self.sample_domain != "finite[-1,1]"
        ):
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_AUDIO_FORM", "audio form differs from default-live"
            )
        if type(self.pcm_bytes) is not bytes or len(self.pcm_bytes) != S2JO_HOP_BYTES:
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_AUDIO_FORM", "audio payload must be exact PCM_F32LE"
            )
        samples = struct.unpack("<480f", self.pcm_bytes)
        if any(not math.isfinite(value) or abs(value) > 1.0 for value in samples):
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_AUDIO_VALUE", "PCM samples must be finite within -1..1"
            )
        pcm_digest = hashlib.sha256(self.pcm_bytes).hexdigest()
        if self.pcm_digest != pcm_digest:
            raise S2JOCanonicalBoundaryError(
                "S2JO_PAYLOAD_DIGEST_MISMATCH", "audio payload digest differs"
            )
        payload = _audio_functional_payload(
            episode_id=episode_id,
            hop_index=hop_index,
            clock_id=clock_id,
            window_start_tick=start,
            window_end_tick=end,
            pcm_digest=pcm_digest,
        )
        if self.functional_input_digest != _digest(payload):
            raise S2JOCanonicalBoundaryError(
                "S2JO_FUNCTIONAL_DIGEST_MISMATCH",
                "audio functional digest contains different or coupled data",
            )
        object.__setattr__(self, "episode_id", episode_id)
        object.__setattr__(self, "clock_id", clock_id)

    @classmethod
    def build(
        cls,
        *,
        episode_id: str,
        hop_index: int,
        clock_id: str,
        window_start_tick: int,
        window_end_tick: int,
        pcm_bytes: bytes,
    ) -> "CanonicalPCMAudioHopV1":
        pcm_digest = hashlib.sha256(pcm_bytes).hexdigest()
        payload = _audio_functional_payload(
            episode_id=episode_id,
            hop_index=hop_index,
            clock_id=clock_id,
            window_start_tick=window_start_tick,
            window_end_tick=window_end_tick,
            pcm_digest=pcm_digest,
        )
        return cls(
            S2JO_AUDIO_SCHEMA,
            episode_id,
            hop_index,
            "PCM_F32LE",
            1,
            48000,
            480,
            "finite[-1,1]",
            clock_id,
            window_start_tick,
            window_end_tick,
            pcm_bytes,
            pcm_digest,
            _digest(payload),
        )

    def samples(self) -> tuple[float, ...]:
        return struct.unpack("<480f", self.pcm_bytes)


@dataclass(frozen=True, slots=True)
class SourceAuditProvenanceV1:
    schema: str
    source_class: str
    source_instance_digest: str
    adapter_digest: str
    adapter_version: str
    adapter_config_digest: str
    native_payload_digest: str
    capture_status: str
    validation_status: str
    raw_payload_disposition: str
    provenance_digest: str

    def __post_init__(self) -> None:
        if self.schema != S2JO_PROVENANCE_SCHEMA or self.source_class not in _SOURCE_CLASSES:
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_PROVENANCE", "source provenance role is invalid"
            )
        for role in (
            "source_instance_digest",
            "adapter_digest",
            "adapter_config_digest",
            "native_payload_digest",
        ):
            _require_digest(getattr(self, role), role)
        adapter_version = _require_identifier(self.adapter_version, "adapter_version")
        if (
            self.capture_status != "COMPLETE"
            or self.validation_status != "VALID"
            or self.raw_payload_disposition != "DISCARDED_AFTER_REDUCTION"
        ):
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_PROVENANCE", "source provenance is not complete"
            )
        if self.provenance_digest != _digest(self.canonical_payload()):
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_PROVENANCE", "provenance digest differs"
            )
        object.__setattr__(self, "adapter_version", adapter_version)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "source_class": self.source_class,
            "source_instance_digest": self.source_instance_digest,
            "adapter_digest": self.adapter_digest,
            "adapter_version": self.adapter_version,
            "adapter_config_digest": self.adapter_config_digest,
            "native_payload_digest": self.native_payload_digest,
            "capture_status": self.capture_status,
            "validation_status": self.validation_status,
            "raw_payload_disposition": self.raw_payload_disposition,
        }

    @classmethod
    def build(
        cls,
        *,
        source_class: str,
        variant: str,
        native_payload_digest: str,
    ) -> "SourceAuditProvenanceV1":
        variant = _require_identifier(variant, "variant")
        payload = {
            "schema": S2JO_PROVENANCE_SCHEMA,
            "source_class": source_class,
            "source_instance_digest": _digest(
                {"source_class": source_class, "variant": variant}
            ),
            "adapter_digest": _digest(
                {"adapter": "s2jo.simulation", "variant": variant}
            ),
            "adapter_version": "s2jo.simulation.v1",
            "adapter_config_digest": _digest(
                {
                    "visual_geometry": S2JO_VISUAL_CONFIG.geometry_id,
                    "audio": {
                        "sample_rate": S2JO_AUDIO_CONFIG.sample_rate,
                        "window_size": S2JO_AUDIO_CONFIG.window_size,
                        "hop_size": S2JO_AUDIO_CONFIG.hop_size,
                        "band_count": S2JO_AUDIO_CONFIG.band_count,
                    },
                }
            ),
            "native_payload_digest": _require_digest(
                native_payload_digest, "native_payload_digest"
            ),
            "capture_status": "COMPLETE",
            "validation_status": "VALID",
            "raw_payload_disposition": "DISCARDED_AFTER_REDUCTION",
        }
        return cls(**payload, provenance_digest=_digest(payload))


@dataclass(frozen=True, slots=True)
class CanonicalInputBindingV1:
    schema: str
    role: str
    position: int
    window_start_tick: int
    window_end_tick: int
    payload_digest: str
    functional_input_digest: str

    def __post_init__(self) -> None:
        if self.schema != S2JO_INPUT_BINDING_SCHEMA or self.role not in {
            "VISUAL_FRAME",
            "AUDIO_HOP",
        }:
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_BINDING", "canonical input binding role is invalid"
            )
        _require_index(self.position, "position")
        _require_window(self.window_start_tick, self.window_end_tick)
        _require_digest(self.payload_digest, "payload_digest")
        _require_digest(self.functional_input_digest, "functional_input_digest")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "role": self.role,
            "position": self.position,
            "window_start_tick": self.window_start_tick,
            "window_end_tick": self.window_end_tick,
            "payload_digest": self.payload_digest,
            "functional_input_digest": self.functional_input_digest,
        }


@dataclass(frozen=True, slots=True)
class CanonicalAVEpisodeReceiptV1:
    schema: str
    episode_id: str
    clock_id: str
    visual_geometry_id: str
    audio_geometry_id: str
    frame_count: int
    hop_count: int
    bindings: tuple[CanonicalInputBindingV1, ...]
    functional_episode_digest: str

    def __post_init__(self) -> None:
        if self.schema != S2JO_EPISODE_SCHEMA:
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_SCHEMA", "episode receipt schema changed"
            )
        _require_identifier(self.episode_id, "episode_id")
        _require_identifier(self.clock_id, "clock_id")
        bindings = tuple(self.bindings)
        if (
            self.frame_count != S2JO_FRAME_COUNT
            or self.hop_count != S2JO_HOP_COUNT
            or len(bindings) != S2JO_FRAME_COUNT + S2JO_HOP_COUNT
            or any(not isinstance(item, CanonicalInputBindingV1) for item in bindings)
        ):
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVENTORY_MISMATCH", "episode receipt inventory differs"
            )
        payload = self.canonical_payload()
        if self.functional_episode_digest != _digest(payload):
            raise S2JOCanonicalBoundaryError(
                "S2JO_FUNCTIONAL_DIGEST_MISMATCH", "episode digest differs"
            )
        object.__setattr__(self, "bindings", bindings)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "episode_id": self.episode_id,
            "clock_id": self.clock_id,
            "visual_geometry_id": self.visual_geometry_id,
            "audio_geometry_id": self.audio_geometry_id,
            "frame_count": self.frame_count,
            "hop_count": self.hop_count,
            "bindings": [item.canonical_payload() for item in self.bindings],
        }

    @classmethod
    def build(
        cls,
        bindings: tuple[CanonicalInputBindingV1, ...],
        audio_geometry_id: str,
    ) -> "CanonicalAVEpisodeReceiptV1":
        payload = {
            "schema": S2JO_EPISODE_SCHEMA,
            "episode_id": S2JO_EPISODE_ID,
            "clock_id": S2JO_CLOCK_ID,
            "visual_geometry_id": S2JO_VISUAL_CONFIG.geometry_id,
            "audio_geometry_id": audio_geometry_id,
            "frame_count": S2JO_FRAME_COUNT,
            "hop_count": S2JO_HOP_COUNT,
            "bindings": [item.canonical_payload() for item in bindings],
        }
        return cls(
            S2JO_EPISODE_SCHEMA,
            S2JO_EPISODE_ID,
            S2JO_CLOCK_ID,
            S2JO_VISUAL_CONFIG.geometry_id,
            audio_geometry_id,
            S2JO_FRAME_COUNT,
            S2JO_HOP_COUNT,
            bindings,
            _digest(payload),
        )


def _visual_state_payload(state: VisualReceptorState) -> dict[str, object]:
    return {
        "modality_id": state.modality_id,
        "geometry_id": state.geometry_id,
        "frame_index": state.frame_index,
        "carrier_ids": list(state.carrier_ids),
        "channel_values": list(state.channel_values),
        "contact": state.contact.value,
    }


def _auditory_state_payload(state: AuditoryReceptorState) -> dict[str, object]:
    return {
        "modality_id": state.modality_id,
        "geometry_id": state.geometry_id,
        "snapshot_index": state.snapshot_index,
        "window_start_sample": state.window_start_sample,
        "window_end_sample": state.window_end_sample,
        "carrier_ids": list(state.carrier_ids),
        "energy": list(state.energy),
        "contact": state.contact.value,
    }


@dataclass(frozen=True, slots=True)
class CanonicalReducedReceptorSequenceReceiptV1:
    schema: str
    input_episode_digest: str
    visual_state_count: int
    auditory_state_count: int
    visual_state_digests: tuple[str, ...]
    auditory_state_digests: tuple[str, ...]
    reduced_sequence_digest: str

    def __post_init__(self) -> None:
        if self.schema != S2JO_REDUCED_SCHEMA:
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_SCHEMA", "reduced receipt schema changed"
            )
        _require_digest(self.input_episode_digest, "input_episode_digest")
        visual = tuple(self.visual_state_digests)
        auditory = tuple(self.auditory_state_digests)
        if (
            self.visual_state_count != S2JO_FRAME_COUNT
            or self.auditory_state_count != S2JO_AUDIO_STATE_COUNT
            or len(visual) != S2JO_FRAME_COUNT
            or len(auditory) != S2JO_AUDIO_STATE_COUNT
        ):
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVENTORY_MISMATCH", "reduced state inventory differs"
            )
        for digest in visual + auditory:
            _require_digest(digest, "state_digest")
        payload = self.canonical_payload()
        if self.reduced_sequence_digest != _digest(payload):
            raise S2JOCanonicalBoundaryError(
                "S2JO_FUNCTIONAL_DIGEST_MISMATCH", "reduced digest differs"
            )
        object.__setattr__(self, "visual_state_digests", visual)
        object.__setattr__(self, "auditory_state_digests", auditory)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "input_episode_digest": self.input_episode_digest,
            "visual_state_count": self.visual_state_count,
            "auditory_state_count": self.auditory_state_count,
            "visual_state_digests": list(self.visual_state_digests),
            "auditory_state_digests": list(self.auditory_state_digests),
        }

    @classmethod
    def build(
        cls,
        input_episode_digest: str,
        visual_states: tuple[VisualReceptorState, ...],
        auditory_states: tuple[AuditoryReceptorState, ...],
    ) -> "CanonicalReducedReceptorSequenceReceiptV1":
        visual = tuple(_digest(_visual_state_payload(item)) for item in visual_states)
        auditory = tuple(
            _digest(_auditory_state_payload(item)) for item in auditory_states
        )
        payload = {
            "schema": S2JO_REDUCED_SCHEMA,
            "input_episode_digest": input_episode_digest,
            "visual_state_count": len(visual),
            "auditory_state_count": len(auditory),
            "visual_state_digests": list(visual),
            "auditory_state_digests": list(auditory),
        }
        return cls(
            S2JO_REDUCED_SCHEMA,
            input_episode_digest,
            len(visual),
            len(auditory),
            visual,
            auditory,
            _digest(payload),
        )


@dataclass(frozen=True, slots=True)
class StreamingResourceLedgerV1:
    schema: str
    frame_count: int
    hop_count: int
    visual_payload_bytes: int
    audio_payload_bytes: int
    raw_payload_bytes: int
    max_live_visual_frames: int
    max_live_audio_hops: int
    max_live_payloads: int
    operation_count: int
    raw_payloads_retained: bool

    def __post_init__(self) -> None:
        if (
            self.schema != S2JO_LEDGER_SCHEMA
            or self.frame_count != S2JO_FRAME_COUNT
            or self.hop_count != S2JO_HOP_COUNT
            or self.visual_payload_bytes != S2JO_FRAME_COUNT * S2JO_FRAME_BYTES
            or self.audio_payload_bytes != S2JO_HOP_COUNT * S2JO_HOP_BYTES
            or self.raw_payload_bytes != S2JO_RAW_BYTES
            or self.max_live_visual_frames > 1
            or self.max_live_audio_hops > 1
            or self.max_live_payloads > 1
            or self.operation_count != S2JO_OPERATION_COUNT
            or self.raw_payloads_retained
        ):
            raise S2JOCanonicalBoundaryError(
                "S2JO_RESOURCE_LIMIT", "streaming resource ledger differs"
            )


@dataclass(frozen=True, slots=True)
class CanonicalReductionResultV1:
    episode_receipt: CanonicalAVEpisodeReceiptV1
    reduced_receipt: CanonicalReducedReceptorSequenceReceiptV1
    visual_states: tuple[VisualReceptorState, ...]
    auditory_states: tuple[AuditoryReceptorState, ...]
    ledger: StreamingResourceLedgerV1


@dataclass(frozen=True, slots=True)
class SimulationReferenceResultV1:
    reduction: CanonicalReductionResultV1
    visual_provenance: SourceAuditProvenanceV1
    audio_provenance: SourceAuditProvenanceV1


def _visual_window(frame_index: int) -> tuple[int, int]:
    return (
        math.floor(frame_index * S2JO_TICKS_PER_SECOND / 30),
        math.floor((frame_index + 1) * S2JO_TICKS_PER_SECOND / 30),
    )


def _audio_window(hop_index: int) -> tuple[int, int]:
    return hop_index * 10_000_000, (hop_index + 1) * 10_000_000


def _event_schedule() -> tuple[tuple[str, int], ...]:
    events = [("VISUAL_FRAME", index) for index in range(S2JO_FRAME_COUNT)]
    events.extend(("AUDIO_HOP", index) for index in range(S2JO_HOP_COUNT))
    return tuple(
        sorted(
            events,
            key=lambda item: (
                _visual_window(item[1])[0]
                if item[0] == "VISUAL_FRAME"
                else _audio_window(item[1])[0],
                0 if item[0] == "VISUAL_FRAME" else 1,
                item[1],
            ),
        )
    )


def _simulation_visual_bytes(
    frame_index: int,
    pixel_mutation: tuple[int, int, int, int, int] | None,
) -> bytes:
    image = np.empty((1080, 1920, 3), dtype=np.uint8)
    image[:, :] = (16, 32, 48)
    row_start = 2 * 135
    column_start = frame_index * 160
    image[row_start : row_start + 135, column_start : column_start + 160] = (
        224,
        64,
        32,
    )
    if pixel_mutation is not None and pixel_mutation[0] == frame_index:
        _, y, x, channel, value = pixel_mutation
        if (
            isinstance(y, bool)
            or isinstance(x, bool)
            or isinstance(channel, bool)
            or isinstance(value, bool)
            or not isinstance(y, int)
            or not isinstance(x, int)
            or not isinstance(channel, int)
            or not isinstance(value, int)
            or y < 0
            or y >= 1080
            or x < 0
            or x >= 1920
            or channel < 0
            or channel >= 3
            or value < 0
            or value > 255
        ):
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_MUTATION", "pixel mutation is invalid"
            )
        image[y, x, channel] = value
    return image.tobytes(order="C")


def _simulation_audio_bytes(
    hop_index: int,
    sample_mutation: tuple[int, int, float] | None,
) -> bytes:
    samples = [value for _ in range(120) for value in (0.0, 0.5, 0.0, -0.5)]
    if sample_mutation is not None and sample_mutation[0] == hop_index:
        _, sample_index, value = sample_mutation
        if (
            isinstance(sample_index, bool)
            or not isinstance(sample_index, int)
            or sample_index < 0
            or sample_index >= 480
            or isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or abs(float(value)) > 1.0
        ):
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVALID_MUTATION", "sample mutation is invalid"
            )
        samples[sample_index] = float(value)
    return struct.pack("<480f", *samples)


def build_s2jo_visual_frame(
    frame_index: int,
    *,
    pixel_mutation: tuple[int, int, int, int, int] | None = None,
    window: tuple[int, int] | None = None,
) -> CanonicalVisualFrameV1:
    _require_index(frame_index, "frame_index")
    if frame_index >= S2JO_FRAME_COUNT:
        raise S2JOCanonicalBoundaryError(
            "S2JO_INVALID_POSITION", "frame_index exceeds the bound episode"
        )
    start, end = _visual_window(frame_index) if window is None else window
    return CanonicalVisualFrameV1.build(
        episode_id=S2JO_EPISODE_ID,
        frame_index=frame_index,
        clock_id=S2JO_CLOCK_ID,
        window_start_tick=start,
        window_end_tick=end,
        pixel_bytes=_simulation_visual_bytes(frame_index, pixel_mutation),
    )


def build_s2jo_audio_hop(
    hop_index: int,
    *,
    sample_mutation: tuple[int, int, float] | None = None,
    window: tuple[int, int] | None = None,
) -> CanonicalPCMAudioHopV1:
    _require_index(hop_index, "hop_index")
    if hop_index >= S2JO_HOP_COUNT:
        raise S2JOCanonicalBoundaryError(
            "S2JO_INVALID_POSITION", "hop_index exceeds the bound episode"
        )
    start, end = _audio_window(hop_index) if window is None else window
    return CanonicalPCMAudioHopV1.build(
        episode_id=S2JO_EPISODE_ID,
        hop_index=hop_index,
        clock_id=S2JO_CLOCK_ID,
        window_start_tick=start,
        window_end_tick=end,
        pcm_bytes=_simulation_audio_bytes(hop_index, sample_mutation),
    )


def iter_s2jo_simulation_episode(
    *,
    pixel_mutation: tuple[int, int, int, int, int] | None = None,
    sample_mutation: tuple[int, int, float] | None = None,
) -> Iterator[CanonicalVisualFrameV1 | CanonicalPCMAudioHopV1]:
    """Yield one canonical payload at a time in the bound shared-time order."""

    for role, position in _event_schedule():
        if role == "VISUAL_FRAME":
            yield build_s2jo_visual_frame(
                position,
                pixel_mutation=pixel_mutation,
            )
        else:
            yield build_s2jo_audio_hop(
                position,
                sample_mutation=sample_mutation,
            )


def _binding_for(
    item: CanonicalVisualFrameV1 | CanonicalPCMAudioHopV1,
) -> CanonicalInputBindingV1:
    if isinstance(item, CanonicalVisualFrameV1):
        return CanonicalInputBindingV1(
            S2JO_INPUT_BINDING_SCHEMA,
            "VISUAL_FRAME",
            item.frame_index,
            item.window_start_tick,
            item.window_end_tick,
            item.pixel_digest,
            item.functional_input_digest,
        )
    if isinstance(item, CanonicalPCMAudioHopV1):
        return CanonicalInputBindingV1(
            S2JO_INPUT_BINDING_SCHEMA,
            "AUDIO_HOP",
            item.hop_index,
            item.window_start_tick,
            item.window_end_tick,
            item.pcm_digest,
            item.functional_input_digest,
        )
    raise S2JOCanonicalBoundaryError(
        "S2JO_INVALID_INPUT", "stream item has an unknown type"
    )


def reduce_canonical_av_stream(
    items: Iterable[CanonicalVisualFrameV1 | CanonicalPCMAudioHopV1],
) -> CanonicalReductionResultV1:
    """Reduce one exact streaming episode without retaining canonical payloads."""

    iterator = iter(items)
    if iterator is not items:
        raise S2JOCanonicalBoundaryError(
            "S2JO_STREAM_REQUIRED", "canonical episode must be a one-pass iterator"
        )
    schedule = _event_schedule()
    visual_receptor = LocalChannelGridReceptor(S2JO_VISUAL_CONFIG)
    auditory_path = BroadbandHearingPath(LogSpectralReceptor(S2JO_AUDIO_CONFIG))
    bindings: list[CanonicalInputBindingV1] = []
    visual_states: list[VisualReceptorState] = []
    auditory_states: list[AuditoryReceptorState] = []
    visual_bytes = 0
    audio_bytes = 0
    max_live_visual = 0
    max_live_audio = 0
    max_live_total = 0
    live_visual = 0
    live_audio = 0
    operation_count = 1  # source open

    for cursor, item in enumerate(iterator):
        if cursor >= len(schedule):
            raise S2JOCanonicalBoundaryError(
                "S2JO_INVENTORY_MISMATCH", "episode contains additional payloads"
            )
        expected_role, expected_position = schedule[cursor]
        binding = _binding_for(item)
        if binding.role != expected_role or binding.position != expected_position:
            raise S2JOCanonicalBoundaryError(
                "S2JO_SEQUENCE_MISMATCH", "payload order or position changed"
            )
        expected_window = (
            _visual_window(expected_position)
            if expected_role == "VISUAL_FRAME"
            else _audio_window(expected_position)
        )
        if (
            binding.window_start_tick,
            binding.window_end_tick,
        ) != expected_window:
            raise S2JOCanonicalBoundaryError(
                "S2JO_TIME_MISMATCH", "payload time binding changed"
            )
        bindings.append(binding)
        operation_count += 1  # canonicalization

        if isinstance(item, CanonicalVisualFrameV1):
            live_visual += 1
            max_live_visual = max(max_live_visual, live_visual)
            max_live_total = max(max_live_total, live_visual + live_audio)
            frame = np.frombuffer(item.pixel_bytes, dtype=np.uint8).reshape(item.shape)
            state = visual_receptor.analyze(frame, frame_index=item.frame_index)
            visual_states.append(state)
            visual_bytes += len(item.pixel_bytes)
            del frame
            live_visual -= 1
        else:
            live_audio += 1
            max_live_audio = max(max_live_audio, live_audio)
            max_live_total = max(max_live_total, live_visual + live_audio)
            state = auditory_path.push(item.samples())
            if state is not None:
                auditory_states.append(state)
            audio_bytes += len(item.pcm_bytes)
            live_audio -= 1
        operation_count += 1  # unchanged receptor call or push
        del item

    if len(bindings) != len(schedule):
        raise S2JOCanonicalBoundaryError(
            "S2JO_INVENTORY_MISMATCH", "episode ended before its bound inventory"
        )
    visual_tuple = tuple(visual_states)
    auditory_tuple = tuple(auditory_states)
    if (
        len(visual_tuple) != S2JO_FRAME_COUNT
        or len(auditory_tuple) != S2JO_AUDIO_STATE_COUNT
    ):
        raise S2JOCanonicalBoundaryError(
            "S2JO_INVENTORY_MISMATCH", "receptor state inventory differs"
        )
    operation_count += 1  # inventory validation
    episode_receipt = CanonicalAVEpisodeReceiptV1.build(
        tuple(bindings), auditory_path.geometry_id
    )
    reduced_receipt = CanonicalReducedReceptorSequenceReceiptV1.build(
        episode_receipt.functional_episode_digest,
        visual_tuple,
        auditory_tuple,
    )
    operation_count += 1  # source close
    ledger = StreamingResourceLedgerV1(
        S2JO_LEDGER_SCHEMA,
        len(visual_tuple),
        S2JO_HOP_COUNT,
        visual_bytes,
        audio_bytes,
        visual_bytes + audio_bytes,
        max_live_visual,
        max_live_audio,
        max_live_total,
        operation_count,
        False,
    )
    return CanonicalReductionResultV1(
        episode_receipt,
        reduced_receipt,
        visual_tuple,
        auditory_tuple,
        ledger,
    )


def run_s2jo_simulation_reference(
    provenance_variant: str,
    *,
    pixel_mutation: tuple[int, int, int, int, int] | None = None,
    sample_mutation: tuple[int, int, float] | None = None,
) -> SimulationReferenceResultV1:
    """Run the private finite simulation reference through unchanged receptors."""

    variant = _require_identifier(provenance_variant, "provenance_variant")
    reduction = reduce_canonical_av_stream(
        iter_s2jo_simulation_episode(
            pixel_mutation=pixel_mutation,
            sample_mutation=sample_mutation,
        )
    )
    native_payload_digest = _digest(
        {
            "schema": "s2jo.native-payload-sequence.v1",
            "payload_digests": [
                item.payload_digest for item in reduction.episode_receipt.bindings
            ],
        }
    )
    visual_provenance = SourceAuditProvenanceV1.build(
        source_class="SIMULATION_RENDER",
        variant=f"{variant}.visual",
        native_payload_digest=native_payload_digest,
    )
    audio_provenance = SourceAuditProvenanceV1.build(
        source_class="SIMULATION_AUDIO",
        variant=f"{variant}.audio",
        native_payload_digest=native_payload_digest,
    )
    return SimulationReferenceResultV1(
        reduction,
        visual_provenance,
        audio_provenance,
    )
