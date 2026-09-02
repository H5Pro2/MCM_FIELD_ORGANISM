"""Private pure binding of active receptor batches to PPB-1 input provenance."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import PPB1BankConfig, _input_projection
from .browser_receptor_bridge import BrowserReceptorSequenceBatch
from .browser_world_contract import BrowserWorldContract
from .receptor_contract import ReceptorContactFrame, technical_identifier
from .receptor_time_model import OrganismTimedReceptorFrame, ReceptorTimeSequence


PPB1_ACTIVE_BATCH_SCHEMA_VERSION = "ppb1.private.active-receptor-batch-binding.v1"
PPB1_ACTIVE_BATCH_INVALID_CONTRACT = "PPB1_ACTIVE_BATCH_INVALID_CONTRACT"
PPB1_ACTIVE_BATCH_CONTRACT_SOURCE_MISMATCH = (
    "PPB1_ACTIVE_BATCH_CONTRACT_SOURCE_MISMATCH"
)
PPB1_ACTIVE_BATCH_PROVENANCE_MISMATCH = "PPB1_ACTIVE_BATCH_PROVENANCE_MISMATCH"
PPB1_ACTIVE_BATCH_INPUT_MISMATCH = "PPB1_ACTIVE_BATCH_INPUT_MISMATCH"
PPB1_ACTIVE_BATCH_SOURCE_CLOCK_CHANGED = (
    "PPB1_ACTIVE_BATCH_SOURCE_CLOCK_CHANGED_WITHIN_MODALITY"
)
PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED = (
    "PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED"
)

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class PPB1ActiveReceptorBatchBindingError(ValueError):
    """One fail-closed private active-batch binding violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _identifier(value: object, role: str, code: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise PPB1ActiveReceptorBatchBindingError(code, str(exc)) from exc


@dataclass(frozen=True, slots=True)
class PPB1ActiveReceptorTimedFrameBinding:
    timed_frame: OrganismTimedReceptorFrame
    snapshot_id: str
    source_clock_id: str
    source_window_start_tick: int
    source_window_end_tick: int
    field_clock_id: str
    field_window_start_tick: int
    field_window_end_tick: int
    ppb1_input_projection_digest: str
    timed_frame_provenance_digest: str
    schema_version: str = PPB1_ACTIVE_BATCH_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if type(self.timed_frame) is not OrganismTimedReceptorFrame:
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
                "timed frame binding requires one exact timed receptor frame",
            )
        frame = self.timed_frame.frame
        field_time = self.timed_frame.field_time
        if (
            self.schema_version != PPB1_ACTIVE_BATCH_SCHEMA_VERSION
            or self.snapshot_id != frame.snapshot_id
            or self.source_clock_id != frame.clock_id
            or self.source_window_start_tick != frame.window_start_tick
            or self.source_window_end_tick != frame.window_end_tick
            or self.field_clock_id != field_time.clock_id
            or self.field_window_start_tick != field_time.window_start_tick
            or self.field_window_end_tick != field_time.window_end_tick
            or not _valid_digest(self.ppb1_input_projection_digest)
            or not _valid_digest(self.timed_frame_provenance_digest)
        ):
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
                "timed frame identity, time or digest binding is invalid",
            )
        if self.ppb1_input_projection_digest != _digest(_input_projection(frame)):
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
                "PPB-1 input projection digest mismatch",
            )
        if self.timed_frame_provenance_digest != _digest(
            self.payload_without_digest()
        ):
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
                "timed frame provenance digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "snapshot_id": self.snapshot_id,
            "source_clock_id": self.source_clock_id,
            "source_window_start_tick": self.source_window_start_tick,
            "source_window_end_tick": self.source_window_end_tick,
            "field_clock_id": self.field_clock_id,
            "field_window_start_tick": self.field_window_start_tick,
            "field_window_end_tick": self.field_window_end_tick,
            "ppb1_input_projection_digest": self.ppb1_input_projection_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "timed_frame_provenance_digest": self.timed_frame_provenance_digest,
        }


@dataclass(frozen=True, slots=True)
class PPB1ActiveReceptorStreamBinding:
    modality_id: str
    geometry_id: str
    source_clock_id: str
    bank_config_digest: str
    carrier_ids: tuple[str, ...]
    frame_count: int
    timed_frames: tuple[PPB1ActiveReceptorTimedFrameBinding, ...]
    stream_digest: str
    schema_version: str = PPB1_ACTIVE_BATCH_SCHEMA_VERSION

    def __post_init__(self) -> None:
        frames = tuple(self.timed_frames)
        carriers = tuple(self.carrier_ids)
        if (
            self.schema_version != PPB1_ACTIVE_BATCH_SCHEMA_VERSION
            or self.modality_id not in {"auditory", "visual"}
            or not frames
            or self.frame_count != len(frames)
            or not carriers
            or len(set(carriers)) != len(carriers)
            or not _valid_digest(self.bank_config_digest)
            or not _valid_digest(self.stream_digest)
            or any(
                type(item) is not PPB1ActiveReceptorTimedFrameBinding
                or item.timed_frame.frame.modality_id != self.modality_id
                or item.timed_frame.frame.geometry_id != self.geometry_id
                or item.timed_frame.frame.carrier_ids != carriers
                or item.source_clock_id != self.source_clock_id
                for item in frames
            )
        ):
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
                "stream identity, inventory or digest binding is invalid",
            )
        object.__setattr__(self, "carrier_ids", carriers)
        object.__setattr__(self, "timed_frames", frames)
        if self.stream_digest != _digest(self.payload_without_digest()):
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
                "stream digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "modality_id": self.modality_id,
            "geometry_id": self.geometry_id,
            "source_clock_id": self.source_clock_id,
            "bank_config_digest": self.bank_config_digest,
            "carrier_ids": list(self.carrier_ids),
            "frame_count": self.frame_count,
            "timed_frame_provenance_digests": [
                item.timed_frame_provenance_digest for item in self.timed_frames
            ],
        }

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "stream_digest": self.stream_digest}


@dataclass(frozen=True, slots=True)
class PPB1ActiveReceptorBatchEnvelope:
    binding_id: str
    source_contract_id: str
    source_contract_digest: str
    source_batch_digest: str
    profile_id: str
    profile_binding_digest: str
    parameter_digest: str
    common_field_clock_id: str
    auditory_stream: PPB1ActiveReceptorStreamBinding
    visual_stream: PPB1ActiveReceptorStreamBinding
    envelope_digest: str
    schema_version: str = PPB1_ACTIVE_BATCH_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _identifier(
            self.binding_id,
            "binding_id",
            PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
        )
        _identifier(
            self.source_contract_id,
            "source_contract_id",
            PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
        )
        _identifier(
            self.common_field_clock_id,
            "common_field_clock_id",
            PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
        )
        if (
            self.schema_version != PPB1_ACTIVE_BATCH_SCHEMA_VERSION
            or self.profile_id not in {"browser", "default-live"}
            or not all(
                _valid_digest(value)
                for value in (
                    self.source_contract_digest,
                    self.source_batch_digest,
                    self.profile_binding_digest,
                    self.parameter_digest,
                    self.envelope_digest,
                )
            )
            or type(self.auditory_stream) is not PPB1ActiveReceptorStreamBinding
            or type(self.visual_stream) is not PPB1ActiveReceptorStreamBinding
            or self.auditory_stream.modality_id != "auditory"
            or self.visual_stream.modality_id != "visual"
            or any(
                item.field_clock_id != self.common_field_clock_id
                for stream in (self.auditory_stream, self.visual_stream)
                for item in stream.timed_frames
            )
        ):
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
                "envelope identity, modality, clock or digest binding is invalid",
            )
        if self.envelope_digest != _digest(self.payload_without_digest()):
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
                "envelope digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "binding_id": self.binding_id,
            "source_contract_id": self.source_contract_id,
            "source_contract_digest": self.source_contract_digest,
            "source_batch_digest": self.source_batch_digest,
            "profile_id": self.profile_id,
            "profile_binding_digest": self.profile_binding_digest,
            "parameter_digest": self.parameter_digest,
            "common_field_clock_id": self.common_field_clock_id,
            "auditory_stream_digest": self.auditory_stream.stream_digest,
            "visual_stream_digest": self.visual_stream.stream_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "envelope_digest": self.envelope_digest,
        }


def _build_timed_frame(
    item: OrganismTimedReceptorFrame,
) -> PPB1ActiveReceptorTimedFrameBinding:
    frame = item.frame
    field_time = item.field_time
    projection_digest = _digest(_input_projection(frame))
    values = {
        "schema_version": PPB1_ACTIVE_BATCH_SCHEMA_VERSION,
        "snapshot_id": frame.snapshot_id,
        "source_clock_id": frame.clock_id,
        "source_window_start_tick": frame.window_start_tick,
        "source_window_end_tick": frame.window_end_tick,
        "field_clock_id": field_time.clock_id,
        "field_window_start_tick": field_time.window_start_tick,
        "field_window_end_tick": field_time.window_end_tick,
        "ppb1_input_projection_digest": projection_digest,
    }
    return PPB1ActiveReceptorTimedFrameBinding(
        item,
        frame.snapshot_id,
        frame.clock_id,
        frame.window_start_tick,
        frame.window_end_tick,
        field_time.clock_id,
        field_time.window_start_tick,
        field_time.window_end_tick,
        projection_digest,
        _digest(values),
    )


def _build_stream(
    sequence: ReceptorTimeSequence,
    config: PPB1BankConfig,
) -> PPB1ActiveReceptorStreamBinding:
    if (
        sequence.modality_id != config.modality_id
        or sequence.geometry_id != config.geometry_id
    ):
        raise PPB1ActiveReceptorBatchBindingError(
            PPB1_ACTIVE_BATCH_INPUT_MISMATCH,
            "sequence modality or geometry does not match PPB-1 browser profile",
        )
    first = sequence.frames[0]
    source_clock_id = first.frame.clock_id
    previous_end: int | None = None
    for item in sequence.frames:
        frame = item.frame
        if frame.clock_id != source_clock_id:
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_SOURCE_CLOCK_CHANGED,
                "source clock changed within one modality stream",
            )
        if frame.carrier_ids != config.carrier_ids:
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_INPUT_MISMATCH,
                "frame carrier inventory or order does not match PPB-1 browser profile",
            )
        if previous_end is not None and frame.window_end_tick <= previous_end:
            raise PPB1ActiveReceptorBatchBindingError(
                PPB1_ACTIVE_BATCH_INPUT_MISMATCH,
                "source window end did not strictly advance within stream clock",
            )
        previous_end = frame.window_end_tick
    timed_frames = tuple(_build_timed_frame(item) for item in sequence.frames)
    values = {
        "schema_version": PPB1_ACTIVE_BATCH_SCHEMA_VERSION,
        "modality_id": sequence.modality_id,
        "geometry_id": sequence.geometry_id,
        "source_clock_id": source_clock_id,
        "bank_config_digest": config.digest(),
        "carrier_ids": list(config.carrier_ids),
        "frame_count": len(timed_frames),
        "timed_frame_provenance_digests": [
            item.timed_frame_provenance_digest for item in timed_frames
        ],
    }
    return PPB1ActiveReceptorStreamBinding(
        sequence.modality_id,
        sequence.geometry_id,
        source_clock_id,
        config.digest(),
        config.carrier_ids,
        len(timed_frames),
        timed_frames,
        _digest(values),
    )


def bind_ppb1_active_receptor_batch(
    binding_id: str,
    browser_world_contract: BrowserWorldContract,
    batch: BrowserReceptorSequenceBatch,
    profile: PPB1ReceptorProfileBinding,
) -> PPB1ActiveReceptorBatchEnvelope:
    """Bind one reduced audiovisual batch without advancing PPB-1 or field state."""

    validated_binding_id = _identifier(
        binding_id,
        "binding_id",
        PPB1_ACTIVE_BATCH_INPUT_MISMATCH,
    )
    if type(browser_world_contract) is not BrowserWorldContract:
        raise PPB1ActiveReceptorBatchBindingError(
            PPB1_ACTIVE_BATCH_INVALID_CONTRACT,
            "one exact BrowserWorldContract is required",
        )
    if type(batch) is not BrowserReceptorSequenceBatch:
        raise PPB1ActiveReceptorBatchBindingError(
            PPB1_ACTIVE_BATCH_PROVENANCE_MISMATCH,
            "one exact BrowserReceptorSequenceBatch is required",
        )
    if (
        type(profile) is not PPB1ReceptorProfileBinding
        or profile.profile_id != "browser"
    ):
        raise PPB1ActiveReceptorBatchBindingError(
            PPB1_ACTIVE_BATCH_PROVENANCE_MISMATCH,
            "one exact PPB-1 browser profile binding is required",
        )

    contract_digest_before = browser_world_contract.digest()
    contract_payload_digest_before = _digest(
        browser_world_contract.canonical_payload()
    )
    batch_digest_before = batch.digest()
    profile_digest_before = profile.digest()
    auditory_config_digest_before = profile.auditory_config.digest()
    visual_config_digest_before = profile.visual_config.digest()
    frame_projection_digests_before = tuple(
        _digest(_input_projection(item.frame))
        for sequence in batch.sequences
        for item in sequence.frames
    )

    if browser_world_contract.contract_id != batch.contract_id:
        raise PPB1ActiveReceptorBatchBindingError(
            PPB1_ACTIVE_BATCH_CONTRACT_SOURCE_MISMATCH,
            "browser world contract id does not match batch contract id",
        )
    if contract_digest_before != batch.contract_digest:
        raise PPB1ActiveReceptorBatchBindingError(
            PPB1_ACTIVE_BATCH_CONTRACT_SOURCE_MISMATCH,
            "recomputed browser world contract digest does not match batch",
        )
    if batch.raw_payloads_retained:
        raise PPB1ActiveReceptorBatchBindingError(
            PPB1_ACTIVE_BATCH_INPUT_MISMATCH,
            "raw-retaining batches are forbidden",
        )
    if (
        len(batch.sequences) != 2
        or tuple(item.modality_id for item in batch.sequences)
        != ("auditory", "visual")
        or batch.sequences[0].clock_id != batch.sequences[1].clock_id
    ):
        raise PPB1ActiveReceptorBatchBindingError(
            PPB1_ACTIVE_BATCH_INPUT_MISMATCH,
            "batch requires auditory then visual sequences on one field clock",
        )

    auditory_stream = _build_stream(
        batch.sequences[0],
        profile.auditory_config,
    )
    visual_stream = _build_stream(
        batch.sequences[1],
        profile.visual_config,
    )
    values = {
        "schema_version": PPB1_ACTIVE_BATCH_SCHEMA_VERSION,
        "binding_id": validated_binding_id,
        "source_contract_id": browser_world_contract.contract_id,
        "source_contract_digest": contract_digest_before,
        "source_batch_digest": batch_digest_before,
        "profile_id": profile.profile_id,
        "profile_binding_digest": profile_digest_before,
        "parameter_digest": profile.parameter_digest,
        "common_field_clock_id": batch.sequences[0].clock_id,
        "auditory_stream_digest": auditory_stream.stream_digest,
        "visual_stream_digest": visual_stream.stream_digest,
    }
    envelope = PPB1ActiveReceptorBatchEnvelope(
        validated_binding_id,
        browser_world_contract.contract_id,
        contract_digest_before,
        batch_digest_before,
        profile.profile_id,
        profile_digest_before,
        profile.parameter_digest,
        batch.sequences[0].clock_id,
        auditory_stream,
        visual_stream,
        _digest(values),
    )

    frame_projection_digests_after = tuple(
        _digest(_input_projection(item.frame))
        for sequence in batch.sequences
        for item in sequence.frames
    )
    if (
        browser_world_contract.digest() != contract_digest_before
        or _digest(browser_world_contract.canonical_payload())
        != contract_payload_digest_before
        or batch.digest() != batch_digest_before
        or profile.digest() != profile_digest_before
        or profile.auditory_config.digest() != auditory_config_digest_before
        or profile.visual_config.digest() != visual_config_digest_before
        or frame_projection_digests_after != frame_projection_digests_before
    ):
        raise PPB1ActiveReceptorBatchBindingError(
            PPB1_ACTIVE_BATCH_ATOMIC_RESULT_REQUIRED,
            "contract, batch, profile, config or frame changed during binding",
        )
    return envelope
