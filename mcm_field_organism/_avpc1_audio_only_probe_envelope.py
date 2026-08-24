"""Private pure provenance binding for one later AVPC-1 auditory probe."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from ._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorTimedFrameBinding,
)
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import (
    PPB1BankState,
    _input_projection,
    _validate_state,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from .browser_receptor_bridge import BrowserReceptorSequenceBatch
from .browser_world_contract import BrowserWorldContract
from .receptor_contract import technical_identifier
from .receptor_time_model import OrganismTimedReceptorFrame, ReceptorTimeSequence


AVPC1_AUDIO_ONLY_SCHEMA_VERSION = "avpc1.private.audio-only-probe-envelope.v1"
AVPC1_AUDIO_ONLY_CONTRACT_DIGEST = (
    "94c4694ee8fc1fbec91fa5508cc530ca2a7442d4f6024564d552c7f0964cfb1c"
)
AVPC1_AUDIO_ONLY_PREFLIGHT_DIGEST = (
    "a1ba763ad4a7bf78f9e2f6ef21cdc29d7675395e6d8eada689830cc771f60da8"
)

AVPC1_AUDIO_ONLY_INVALID_CONTRACT = "AVPC1_AUDIO_ONLY_INVALID_CONTRACT"
AVPC1_AUDIO_ONLY_SOURCE_MISMATCH = "AVPC1_AUDIO_ONLY_SOURCE_MISMATCH"
AVPC1_AUDIO_ONLY_PROFILE_OR_CONFIG_MISMATCH = (
    "AVPC1_AUDIO_ONLY_PROFILE_OR_CONFIG_MISMATCH"
)
AVPC1_AUDIO_ONLY_INPUT_MISMATCH = "AVPC1_AUDIO_ONLY_INPUT_MISMATCH"
AVPC1_AUDIO_ONLY_TIME_OR_PARTITION_MISMATCH = (
    "AVPC1_AUDIO_ONLY_TIME_OR_PARTITION_MISMATCH"
)
AVPC1_AUDIO_ONLY_VISUAL_INPUT_FORBIDDEN = (
    "AVPC1_AUDIO_ONLY_VISUAL_INPUT_FORBIDDEN"
)
AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED = (
    "AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED"
)

_SOURCE_KIND = "browser.reduced.auditory-sequence.v1"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class AVPC1AudioOnlyProbeEnvelopeError(ValueError):
    """One fail-closed private audio-only provenance violation."""

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
        raise AVPC1AudioOnlyProbeEnvelopeError(code, str(exc)) from exc


def _sequence_payload(sequence: ReceptorTimeSequence) -> dict[str, object]:
    return {
        "modality_id": sequence.modality_id,
        "geometry_id": sequence.geometry_id,
        "field_clock_id": sequence.clock_id,
        "frames": [
            {
                "snapshot_id": item.frame.snapshot_id,
                "source_clock_id": item.frame.clock_id,
                "source_window_start_tick": item.frame.window_start_tick,
                "source_window_end_tick": item.frame.window_end_tick,
                "field_window_start_tick": item.field_time.window_start_tick,
                "field_window_end_tick": item.field_time.window_end_tick,
                "carrier_ids": list(item.frame.carrier_ids),
                "reduced_values": list(item.frame.values),
            }
            for item in sequence.frames
        ],
    }


def _sequence_digest(sequence: ReceptorTimeSequence) -> str:
    return _digest(_sequence_payload(sequence))


def _timed_frame_binding(
    item: OrganismTimedReceptorFrame,
) -> PPB1ActiveReceptorTimedFrameBinding:
    frame = item.frame
    field_time = item.field_time
    projection_digest = _digest(_input_projection(frame))
    values = {
        "schema_version": "ppb1.private.active-receptor-batch-binding.v1",
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


@dataclass(frozen=True, slots=True)
class AVPC1PrivateAuditoryProbeSourceBinding:
    source_contract: BrowserWorldContract
    source_contract_id: str
    source_contract_digest: str
    source_kind_id: str
    modality_id: str
    geometry_id: str
    source_clock_id: str
    field_clock_id: str
    source_sequence_digest: str
    raw_payloads_retained: bool
    source_binding_digest: str
    schema_version: str = AVPC1_AUDIO_ONLY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if type(self.source_contract) is not BrowserWorldContract:
            raise AVPC1AudioOnlyProbeEnvelopeError(
                AVPC1_AUDIO_ONLY_INVALID_CONTRACT,
                "one exact browser world contract is required",
            )
        if (
            self.schema_version != AVPC1_AUDIO_ONLY_SCHEMA_VERSION
            or self.source_contract_id != self.source_contract.contract_id
            or self.source_contract_digest != self.source_contract.digest()
            or self.source_kind_id != _SOURCE_KIND
            or self.modality_id != "auditory"
            or self.raw_payloads_retained
            or not all(
                _valid_digest(value)
                for value in (
                    self.source_contract_digest,
                    self.source_sequence_digest,
                    self.source_binding_digest,
                )
            )
        ):
            raise AVPC1AudioOnlyProbeEnvelopeError(
                AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED,
                "auditory source binding is incomplete or inconsistent",
            )
        for role, value in (
            ("source_contract_id", self.source_contract_id),
            ("source_kind_id", self.source_kind_id),
            ("geometry_id", self.geometry_id),
            ("source_clock_id", self.source_clock_id),
            ("field_clock_id", self.field_clock_id),
        ):
            _identifier(value, role, AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED)
        if self.source_binding_digest != _digest(self.payload_without_digest()):
            raise AVPC1AudioOnlyProbeEnvelopeError(
                AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED,
                "auditory source binding digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "contract_digest": AVPC1_AUDIO_ONLY_CONTRACT_DIGEST,
            "preflight_digest": AVPC1_AUDIO_ONLY_PREFLIGHT_DIGEST,
            "source_contract_id": self.source_contract_id,
            "source_contract_digest": self.source_contract_digest,
            "source_kind_id": self.source_kind_id,
            "modality_id": self.modality_id,
            "geometry_id": self.geometry_id,
            "source_clock_id": self.source_clock_id,
            "field_clock_id": self.field_clock_id,
            "source_sequence_digest": self.source_sequence_digest,
            "raw_payloads_retained": self.raw_payloads_retained,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "source_binding_digest": self.source_binding_digest,
        }


@dataclass(frozen=True, slots=True)
class AVPC1FrozenRelationHistoryPartitionBinding:
    field_clock_id: str
    exposure_count: int
    max_relation_field_window_end_tick: int
    ordered_modality_ids: tuple[str, ...]
    ordered_snapshot_ids: tuple[str, ...]
    ordered_timed_frame_provenance_digests: tuple[str, ...]
    relation_history_partition_digest: str
    schema_version: str = AVPC1_AUDIO_ONLY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        modalities = tuple(self.ordered_modality_ids)
        snapshots = tuple(self.ordered_snapshot_ids)
        provenance = tuple(self.ordered_timed_frame_provenance_digests)
        _identifier(
            self.field_clock_id,
            "field_clock_id",
            AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED,
        )
        if (
            self.schema_version != AVPC1_AUDIO_ONLY_SCHEMA_VERSION
            or isinstance(self.exposure_count, bool)
            or not isinstance(self.exposure_count, int)
            or self.exposure_count <= 0
            or self.exposure_count != len(modalities)
            or len(snapshots) != self.exposure_count
            or len(provenance) != self.exposure_count
            or set(modalities) != {"auditory", "visual"}
            or len(set(zip(modalities, snapshots, strict=True)))
            != self.exposure_count
            or len(set(provenance)) != self.exposure_count
            or any(not _valid_digest(value) for value in provenance)
            or isinstance(self.max_relation_field_window_end_tick, bool)
            or not isinstance(self.max_relation_field_window_end_tick, int)
            or self.max_relation_field_window_end_tick <= 0
            or not _valid_digest(self.relation_history_partition_digest)
        ):
            raise AVPC1AudioOnlyProbeEnvelopeError(
                AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED,
                "relation history partition is incomplete or inconsistent",
            )
        object.__setattr__(self, "ordered_modality_ids", modalities)
        object.__setattr__(self, "ordered_snapshot_ids", snapshots)
        object.__setattr__(
            self,
            "ordered_timed_frame_provenance_digests",
            provenance,
        )
        if self.relation_history_partition_digest != _digest(
            self.payload_without_digest()
        ):
            raise AVPC1AudioOnlyProbeEnvelopeError(
                AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED,
                "relation history partition digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "contract_digest": AVPC1_AUDIO_ONLY_CONTRACT_DIGEST,
            "preflight_digest": AVPC1_AUDIO_ONLY_PREFLIGHT_DIGEST,
            "field_clock_id": self.field_clock_id,
            "exposure_count": self.exposure_count,
            "max_relation_field_window_end_tick": (
                self.max_relation_field_window_end_tick
            ),
            "ordered_modality_ids": list(self.ordered_modality_ids),
            "ordered_snapshot_ids": list(self.ordered_snapshot_ids),
            "ordered_timed_frame_provenance_digests": list(
                self.ordered_timed_frame_provenance_digests
            ),
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "relation_history_partition_digest": (
                self.relation_history_partition_digest
            ),
        }


@dataclass(frozen=True, slots=True)
class AVPC1PrivateAuditoryOnlyProbeEnvelope:
    binding_id: str
    source_binding: AVPC1PrivateAuditoryProbeSourceBinding
    relation_partition: AVPC1FrozenRelationHistoryPartitionBinding
    timed_frame_binding: PPB1ActiveReceptorTimedFrameBinding
    source_contract_id: str
    source_contract_digest: str
    source_sequence_digest: str
    profile_id: str
    profile_binding_digest: str
    parameter_digest: str
    auditory_bank_config_digest: str
    auditory_bank_state_identity_digest: str
    auditory_bank_state_digest: str
    relation_history_partition_digest: str
    source_clock_id: str
    field_clock_id: str
    snapshot_id: str
    source_window_start_tick: int
    source_window_end_tick: int
    field_window_start_tick: int
    field_window_end_tick: int
    auditory_input_projection_digest: str
    auditory_input_count: int
    visual_input_count: int
    envelope_digest: str
    schema_version: str = AVPC1_AUDIO_ONLY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _identifier(
            self.binding_id,
            "binding_id",
            AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED,
        )
        timed = self.timed_frame_binding
        frame = timed.timed_frame.frame
        field_time = timed.timed_frame.field_time
        if (
            self.schema_version != AVPC1_AUDIO_ONLY_SCHEMA_VERSION
            or type(self.source_binding)
            is not AVPC1PrivateAuditoryProbeSourceBinding
            or type(self.relation_partition)
            is not AVPC1FrozenRelationHistoryPartitionBinding
            or type(timed) is not PPB1ActiveReceptorTimedFrameBinding
            or frame.modality_id != "auditory"
            or self.source_contract_id != self.source_binding.source_contract_id
            or self.source_contract_digest
            != self.source_binding.source_contract_digest
            or self.source_sequence_digest
            != self.source_binding.source_sequence_digest
            or self.relation_history_partition_digest
            != self.relation_partition.relation_history_partition_digest
            or self.source_clock_id != frame.clock_id
            or self.field_clock_id != field_time.clock_id
            or self.snapshot_id != frame.snapshot_id
            or self.source_window_start_tick != frame.window_start_tick
            or self.source_window_end_tick != frame.window_end_tick
            or self.field_window_start_tick != field_time.window_start_tick
            or self.field_window_end_tick != field_time.window_end_tick
            or self.auditory_input_projection_digest
            != timed.ppb1_input_projection_digest
            or self.auditory_input_count != 1
            or self.visual_input_count != 0
            or not all(
                _valid_digest(value)
                for value in (
                    self.source_contract_digest,
                    self.source_sequence_digest,
                    self.profile_binding_digest,
                    self.parameter_digest,
                    self.auditory_bank_config_digest,
                    self.auditory_bank_state_identity_digest,
                    self.auditory_bank_state_digest,
                    self.relation_history_partition_digest,
                    self.auditory_input_projection_digest,
                    self.envelope_digest,
                )
            )
        ):
            raise AVPC1AudioOnlyProbeEnvelopeError(
                AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED,
                "audio-only probe envelope is incomplete or inconsistent",
            )
        if self.envelope_digest != _digest(self.payload_without_digest()):
            raise AVPC1AudioOnlyProbeEnvelopeError(
                AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED,
                "audio-only probe envelope digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "contract_digest": AVPC1_AUDIO_ONLY_CONTRACT_DIGEST,
            "preflight_digest": AVPC1_AUDIO_ONLY_PREFLIGHT_DIGEST,
            "binding_id": self.binding_id,
            "source_binding_digest": self.source_binding.source_binding_digest,
            "source_contract_id": self.source_contract_id,
            "source_contract_digest": self.source_contract_digest,
            "source_sequence_digest": self.source_sequence_digest,
            "profile_id": self.profile_id,
            "profile_binding_digest": self.profile_binding_digest,
            "parameter_digest": self.parameter_digest,
            "auditory_bank_config_digest": self.auditory_bank_config_digest,
            "auditory_bank_state_identity_digest": (
                self.auditory_bank_state_identity_digest
            ),
            "auditory_bank_state_digest": self.auditory_bank_state_digest,
            "relation_history_partition_digest": (
                self.relation_history_partition_digest
            ),
            "source_clock_id": self.source_clock_id,
            "field_clock_id": self.field_clock_id,
            "snapshot_id": self.snapshot_id,
            "source_window_start_tick": self.source_window_start_tick,
            "source_window_end_tick": self.source_window_end_tick,
            "field_window_start_tick": self.field_window_start_tick,
            "field_window_end_tick": self.field_window_end_tick,
            "auditory_input_projection_digest": (
                self.auditory_input_projection_digest
            ),
            "auditory_input_count": self.auditory_input_count,
            "visual_input_count": self.visual_input_count,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "envelope_digest": self.envelope_digest,
        }


def bind_avpc1_private_auditory_probe_source(
    source_contract: BrowserWorldContract,
    source_batch: BrowserReceptorSequenceBatch,
) -> AVPC1PrivateAuditoryProbeSourceBinding:
    """Bind only one auditory sequence from an exact immutable browser source."""

    if type(source_contract) is not BrowserWorldContract:
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_INVALID_CONTRACT,
            "one exact BrowserWorldContract is required",
        )
    if type(source_batch) is not BrowserReceptorSequenceBatch:
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_SOURCE_MISMATCH,
            "one exact BrowserReceptorSequenceBatch is required",
        )
    contract_digest = source_contract.digest()
    batch_digest = source_batch.digest()
    if (
        source_batch.contract_id != source_contract.contract_id
        or source_batch.contract_digest != contract_digest
        or source_batch.raw_payloads_retained
    ):
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_SOURCE_MISMATCH,
            "source contract and batch do not share one raw-free source",
        )
    auditory = source_batch.sequences[0]
    if auditory.modality_id != "auditory" or len(auditory.frames) != 1:
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_INPUT_MISMATCH,
            "source requires exactly one reduced auditory timed frame",
        )
    frame = auditory.frames[0].frame
    values = {
        "schema_version": AVPC1_AUDIO_ONLY_SCHEMA_VERSION,
        "contract_digest": AVPC1_AUDIO_ONLY_CONTRACT_DIGEST,
        "preflight_digest": AVPC1_AUDIO_ONLY_PREFLIGHT_DIGEST,
        "source_contract_id": source_contract.contract_id,
        "source_contract_digest": contract_digest,
        "source_kind_id": _SOURCE_KIND,
        "modality_id": "auditory",
        "geometry_id": auditory.geometry_id,
        "source_clock_id": frame.clock_id,
        "field_clock_id": auditory.clock_id,
        "source_sequence_digest": _sequence_digest(auditory),
        "raw_payloads_retained": False,
    }
    result = AVPC1PrivateAuditoryProbeSourceBinding(
        source_contract,
        source_contract.contract_id,
        contract_digest,
        _SOURCE_KIND,
        "auditory",
        auditory.geometry_id,
        frame.clock_id,
        auditory.clock_id,
        values["source_sequence_digest"],
        False,
        _digest(values),
    )
    if (
        source_contract.digest() != contract_digest
        or source_batch.digest() != batch_digest
    ):
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED,
            "source contract or batch changed during auditory binding",
        )
    return result


def bind_avpc1_frozen_relation_history_partition(
    exposures: tuple[tuple[str, PPB1ActiveReceptorTimedFrameBinding], ...],
) -> AVPC1FrozenRelationHistoryPartitionBinding:
    """Bind only the immutable time boundary of prior relation exposures."""

    items = tuple(exposures)
    if not items:
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_TIME_OR_PARTITION_MISMATCH,
            "relation exposure bindings are required",
        )
    for item in items:
        if (
            not isinstance(item, tuple)
            or len(item) != 2
            or item[0] not in {"auditory", "visual"}
            or type(item[1]) is not PPB1ActiveReceptorTimedFrameBinding
            or item[1].timed_frame.frame.modality_id != item[0]
        ):
            raise AVPC1AudioOnlyProbeEnvelopeError(
                AVPC1_AUDIO_ONLY_TIME_OR_PARTITION_MISMATCH,
                "each exposure requires one exact matching modality and timed binding",
            )
    if {item[0] for item in items} != {"auditory", "visual"}:
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_TIME_OR_PARTITION_MISMATCH,
            "relation partition requires auditory and visual exposures",
        )
    clocks = {item[1].field_clock_id for item in items}
    identities = {
        (item[0], item[1].snapshot_id) for item in items
    }
    provenance = {
        item[1].timed_frame_provenance_digest for item in items
    }
    if (
        len(clocks) != 1
        or len(identities) != len(items)
        or len(provenance) != len(items)
    ):
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_TIME_OR_PARTITION_MISMATCH,
            "relation exposures require one clock and unique provenance",
        )
    field_clock_id = next(iter(clocks))
    modalities = tuple(item[0] for item in items)
    snapshots = tuple(item[1].snapshot_id for item in items)
    digests = tuple(item[1].timed_frame_provenance_digest for item in items)
    maximum_end = max(item[1].field_window_end_tick for item in items)
    values = {
        "schema_version": AVPC1_AUDIO_ONLY_SCHEMA_VERSION,
        "contract_digest": AVPC1_AUDIO_ONLY_CONTRACT_DIGEST,
        "preflight_digest": AVPC1_AUDIO_ONLY_PREFLIGHT_DIGEST,
        "field_clock_id": field_clock_id,
        "exposure_count": len(items),
        "max_relation_field_window_end_tick": maximum_end,
        "ordered_modality_ids": list(modalities),
        "ordered_snapshot_ids": list(snapshots),
        "ordered_timed_frame_provenance_digests": list(digests),
    }
    return AVPC1FrozenRelationHistoryPartitionBinding(
        field_clock_id,
        len(items),
        maximum_end,
        modalities,
        snapshots,
        digests,
        _digest(values),
    )


def bind_avpc1_private_auditory_only_probe_envelope(
    binding_id: str,
    source_binding: AVPC1PrivateAuditoryProbeSourceBinding,
    source_sequence: ReceptorTimeSequence,
    profile: PPB1ReceptorProfileBinding,
    auditory_bank_state: PPB1BankState,
    relation_partition: AVPC1FrozenRelationHistoryPartitionBinding,
) -> AVPC1PrivateAuditoryOnlyProbeEnvelope:
    """Bind one later auditory frame without probing or changing bank state."""

    validated_binding_id = _identifier(
        binding_id,
        "binding_id",
        AVPC1_AUDIO_ONLY_INPUT_MISMATCH,
    )
    if (
        type(source_binding) is not AVPC1PrivateAuditoryProbeSourceBinding
        or type(source_sequence) is not ReceptorTimeSequence
        or type(profile) is not PPB1ReceptorProfileBinding
        or type(auditory_bank_state) is not PPB1BankState
        or type(relation_partition)
        is not AVPC1FrozenRelationHistoryPartitionBinding
    ):
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_INPUT_MISMATCH,
            "exact private source, sequence, profile, state and partition are required",
        )
    if profile.profile_id != "browser":
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_PROFILE_OR_CONFIG_MISMATCH,
            "the current materializable source path requires the browser profile",
        )
    if source_sequence.modality_id != "auditory" or len(source_sequence.frames) != 1:
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_INPUT_MISMATCH,
            "probe envelope requires exactly one auditory timed frame",
        )
    config = profile.auditory_config
    try:
        validated_state = _validate_state(config, auditory_bank_state)
    except Exception as exc:
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_PROFILE_OR_CONFIG_MISMATCH,
            "auditory bank state does not match the profile config",
        ) from exc
    frame_item = source_sequence.frames[0]
    frame = frame_item.frame
    field_time = frame_item.field_time
    sequence_digest = _sequence_digest(source_sequence)
    if (
        source_binding.source_sequence_digest != sequence_digest
        or source_binding.modality_id != source_sequence.modality_id
        or source_binding.geometry_id != source_sequence.geometry_id
        or source_binding.source_clock_id != frame.clock_id
        or source_binding.field_clock_id != source_sequence.clock_id
    ):
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_SOURCE_MISMATCH,
            "auditory source binding does not match the exact probe sequence",
        )
    if (
        config.modality_id != "auditory"
        or source_sequence.geometry_id != config.geometry_id
        or frame.geometry_id != config.geometry_id
        or frame.carrier_ids != config.carrier_ids
        or len(frame.values) != len(config.carrier_ids)
    ):
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_PROFILE_OR_CONFIG_MISMATCH,
            "probe modality, geometry or carriers do not match the auditory config",
        )
    if (
        validated_state.source_clock_id is None
        or validated_state.last_source_window_end_tick is None
        or frame.clock_id != validated_state.source_clock_id
        or frame.window_end_tick <= validated_state.last_source_window_end_tick
        or field_time.clock_id != relation_partition.field_clock_id
        or field_time.window_start_tick
        < relation_partition.max_relation_field_window_end_tick
    ):
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_TIME_OR_PARTITION_MISMATCH,
            "probe is not later on its bound source and field clocks",
        )
    before = (
        source_binding.source_binding_digest,
        source_binding.source_contract.digest(),
        sequence_digest,
        profile.digest(),
        config.digest(),
        validated_state.digest(),
        relation_partition.relation_history_partition_digest,
    )
    timed = _timed_frame_binding(frame_item)
    state_identity_digest = _digest(_state_identity_payload(validated_state))
    values = {
        "schema_version": AVPC1_AUDIO_ONLY_SCHEMA_VERSION,
        "contract_digest": AVPC1_AUDIO_ONLY_CONTRACT_DIGEST,
        "preflight_digest": AVPC1_AUDIO_ONLY_PREFLIGHT_DIGEST,
        "binding_id": validated_binding_id,
        "source_binding_digest": source_binding.source_binding_digest,
        "source_contract_id": source_binding.source_contract_id,
        "source_contract_digest": source_binding.source_contract_digest,
        "source_sequence_digest": sequence_digest,
        "profile_id": profile.profile_id,
        "profile_binding_digest": profile.digest(),
        "parameter_digest": profile.parameter_digest,
        "auditory_bank_config_digest": config.digest(),
        "auditory_bank_state_identity_digest": state_identity_digest,
        "auditory_bank_state_digest": validated_state.digest(),
        "relation_history_partition_digest": (
            relation_partition.relation_history_partition_digest
        ),
        "source_clock_id": frame.clock_id,
        "field_clock_id": field_time.clock_id,
        "snapshot_id": frame.snapshot_id,
        "source_window_start_tick": frame.window_start_tick,
        "source_window_end_tick": frame.window_end_tick,
        "field_window_start_tick": field_time.window_start_tick,
        "field_window_end_tick": field_time.window_end_tick,
        "auditory_input_projection_digest": timed.ppb1_input_projection_digest,
        "auditory_input_count": 1,
        "visual_input_count": 0,
    }
    envelope = AVPC1PrivateAuditoryOnlyProbeEnvelope(
        binding_id=validated_binding_id,
        source_binding=source_binding,
        relation_partition=relation_partition,
        timed_frame_binding=timed,
        source_contract_id=source_binding.source_contract_id,
        source_contract_digest=source_binding.source_contract_digest,
        source_sequence_digest=sequence_digest,
        profile_id=profile.profile_id,
        profile_binding_digest=profile.digest(),
        parameter_digest=profile.parameter_digest,
        auditory_bank_config_digest=config.digest(),
        auditory_bank_state_identity_digest=state_identity_digest,
        auditory_bank_state_digest=validated_state.digest(),
        relation_history_partition_digest=(
            relation_partition.relation_history_partition_digest
        ),
        source_clock_id=frame.clock_id,
        field_clock_id=field_time.clock_id,
        snapshot_id=frame.snapshot_id,
        source_window_start_tick=frame.window_start_tick,
        source_window_end_tick=frame.window_end_tick,
        field_window_start_tick=field_time.window_start_tick,
        field_window_end_tick=field_time.window_end_tick,
        auditory_input_projection_digest=timed.ppb1_input_projection_digest,
        auditory_input_count=1,
        visual_input_count=0,
        envelope_digest=_digest(values),
    )
    after = (
        source_binding.source_binding_digest,
        source_binding.source_contract.digest(),
        _sequence_digest(source_sequence),
        profile.digest(),
        config.digest(),
        validated_state.digest(),
        relation_partition.relation_history_partition_digest,
    )
    if after != before:
        raise AVPC1AudioOnlyProbeEnvelopeError(
            AVPC1_AUDIO_ONLY_ATOMIC_RESULT_REQUIRED,
            "source, profile, state or partition changed during envelope binding",
        )
    return envelope
