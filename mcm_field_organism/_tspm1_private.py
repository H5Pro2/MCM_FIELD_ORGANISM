"""Private bounded two-scale perceptual memory engineering component."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from threading import Lock

from ._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorBatchEnvelope,
    PPB1ActiveReceptorTimedFrameBinding,
)
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import (
    PPB1BankState,
    PPB1Readout,
    PPB1StepResult,
    _validate_state as _validate_ppb1_state,
    advance_ppb1_bank,
    initial_ppb1_bank_state,
    normalized_mean_l1_distance,
)
from ._ppb1_s1wu_read_only_perceptual_probe import (
    S1WUReadOnlyPerceptualFinding,
    probe_s1wu_perceptual_state,
)
from .receptor_contract import technical_identifier


TSPM1_SCHEMA_VERSION = "tspm1.private.v1"
TSPM1_ARCHITECTURE_ID = "tspm1"
TSPM1_S2DE_CONTRACT_DIGEST = (
    "6c90ca594cb1d64a72614dccb4fa7435cb05e752645e74c02a86caacff8f737e"
)
TSPM1_S2DG_CONTRACT_DIGEST = (
    "a67ba54df357486ad57d5bb6d7873ad95782900896d205cf77c2bb2ff8a61502"
)

TSPM1_OWNER_BUSY = "TSPM1_OWNER_BUSY"
TSPM1_OWNER_TERMINAL = "TSPM1_OWNER_TERMINAL"
TSPM1_INVALID_TYPE_OR_SCHEMA = "TSPM1_INVALID_TYPE_OR_SCHEMA"
TSPM1_CONFIG_OR_CONTRACT_MISMATCH = "TSPM1_CONFIG_OR_CONTRACT_MISMATCH"
TSPM1_OWNER_AUTHORIZATION_MISMATCH = "TSPM1_OWNER_AUTHORIZATION_MISMATCH"
TSPM1_COMPOSITE_OR_FAST_STATE_INVALID = "TSPM1_COMPOSITE_OR_FAST_STATE_INVALID"
TSPM1_SOURCE_PROVENANCE_MISMATCH = "TSPM1_SOURCE_PROVENANCE_MISMATCH"
TSPM1_MODALITY_GEOMETRY_OR_CARRIER_MISMATCH = (
    "TSPM1_MODALITY_GEOMETRY_OR_CARRIER_MISMATCH"
)
TSPM1_CLOCK_ORDER_OR_FIELD_OVERLAP_INVALID = (
    "TSPM1_CLOCK_ORDER_OR_FIELD_OVERLAP_INVALID"
)
TSPM1_ATOMIC_RESULT_REQUIRED = "TSPM1_ATOMIC_RESULT_REQUIRED"
TSPM1_ATTEMPT_FAILED = "TSPM1_ATTEMPT_FAILED"
TSPM1_READ_ONLY_REJECTED = "TSPM1_READ_ONLY_REJECTED"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_PRIMARY_EVENTS = {"FAST_CREATED", "FAST_UPDATED", "FAST_REPLACED"}
_CONSOLIDATION_STATUSES = {"NOT_ELIGIBLE", "COMMITTED"}
_SLOW_STATUSES = {"SLOW_UNAVAILABLE", "SLOW_NOT_RECOGNIZED", "SLOW_RECOGNIZED"}
_CONTEXT_SOURCES = {
    "SLOW_PPB1_CONTEXT",
    "FAST_ASSOCIATIVE_CONTEXT",
    "NO_COMPLETE_CONTEXT",
}
_OWNER_STATES = {"AUTHORIZED", "CONSUMED", "FAILED"}


class TSPM1Error(ValueError):
    """One fail-closed private TSPM-1 contract violation."""

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
        raise TSPM1Error(code, str(exc)) from exc


def _positive_integer(value: object, role: str, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise TSPM1Error(code, f"{role} must be a positive integer")
    return value


def _nonnegative_integer(value: object, role: str, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TSPM1Error(code, f"{role} must be a nonnegative integer")
    return value


def _finite(value: object, role: str, code: str) -> float:
    if isinstance(value, bool):
        raise TSPM1Error(code, f"{role} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise TSPM1Error(code, f"{role} must be numeric") from exc
    if not math.isfinite(result):
        raise TSPM1Error(code, f"{role} must be finite")
    return result


def _bounded_values(values: object, role: str, code: str) -> tuple[float, ...]:
    try:
        result = tuple(_finite(value, role, code) for value in values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise TSPM1Error(code, f"{role} must be iterable") from exc
    if not result or any(abs(value) > 1.0 for value in result):
        raise TSPM1Error(code, f"{role} must be nonempty and in [-1,1]")
    return result


@dataclass(frozen=True, slots=True)
class TSPM1FastConfig:
    fast_bank_id: str
    capacity: int
    auditory_match_threshold: float
    visual_match_threshold: float
    update_factor: float
    consolidate_after: int
    expire_after_exposures: int
    schema_version: str = TSPM1_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != TSPM1_SCHEMA_VERSION:
            raise TSPM1Error(
                TSPM1_INVALID_TYPE_OR_SCHEMA,
                "fast config schema mismatch",
            )
        object.__setattr__(
            self,
            "fast_bank_id",
            _identifier(
                self.fast_bank_id,
                "fast_bank_id",
                TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
            ),
        )
        capacity = _positive_integer(
            self.capacity,
            "capacity",
            TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
        )
        auditory_threshold = _finite(
            self.auditory_match_threshold,
            "auditory_match_threshold",
            TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
        )
        visual_threshold = _finite(
            self.visual_match_threshold,
            "visual_match_threshold",
            TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
        )
        update_factor = _finite(
            self.update_factor,
            "update_factor",
            TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
        )
        consolidate_after = _positive_integer(
            self.consolidate_after,
            "consolidate_after",
            TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
        )
        expire_after = _positive_integer(
            self.expire_after_exposures,
            "expire_after_exposures",
            TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
        )
        if (
            not 0.0 <= auditory_threshold <= 2.0
            or not 0.0 <= visual_threshold <= 2.0
            or not 0.0 < update_factor <= 1.0
            or consolidate_after < 2
            or expire_after <= consolidate_after
        ):
            raise TSPM1Error(
                TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
                "fast config bounds are invalid",
            )
        object.__setattr__(self, "capacity", capacity)
        object.__setattr__(self, "auditory_match_threshold", auditory_threshold)
        object.__setattr__(self, "visual_match_threshold", visual_threshold)
        object.__setattr__(self, "update_factor", update_factor)
        object.__setattr__(self, "consolidate_after", consolidate_after)
        object.__setattr__(self, "expire_after_exposures", expire_after)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "fast_bank_id": self.fast_bank_id,
            "capacity": self.capacity,
            "auditory_match_threshold": self.auditory_match_threshold,
            "visual_match_threshold": self.visual_match_threshold,
            "update_factor": self.update_factor,
            "consolidate_after": self.consolidate_after,
            "expire_after_exposures": self.expire_after_exposures,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class TSPM1ConfigBinding:
    fast_config: TSPM1FastConfig
    profile: PPB1ReceptorProfileBinding
    s2de_contract_digest: str
    s2dg_contract_digest: str
    fast_config_digest: str
    profile_binding_digest: str
    auditory_ppb1_config_digest: str
    visual_ppb1_config_digest: str
    config_binding_digest: str
    schema_version: str = TSPM1_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if (
            self.schema_version != TSPM1_SCHEMA_VERSION
            or type(self.fast_config) is not TSPM1FastConfig
            or type(self.profile) is not PPB1ReceptorProfileBinding
            or self.profile.auditory_config.modality_id != "auditory"
            or self.profile.visual_config.modality_id != "visual"
        ):
            raise TSPM1Error(
                TSPM1_INVALID_TYPE_OR_SCHEMA,
                "config binding requires exact fast and PPB-1 profile types",
            )
        if (
            self.s2de_contract_digest != TSPM1_S2DE_CONTRACT_DIGEST
            or self.s2dg_contract_digest != TSPM1_S2DG_CONTRACT_DIGEST
            or self.fast_config_digest != self.fast_config.digest()
            or self.profile_binding_digest != self.profile.digest()
            or self.auditory_ppb1_config_digest
            != self.profile.auditory_config.digest()
            or self.visual_ppb1_config_digest != self.profile.visual_config.digest()
            or self.config_binding_digest != _digest(self.payload_without_digest())
        ):
            raise TSPM1Error(
                TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
                "config binding digest or source mismatch",
            )

    @classmethod
    def build(
        cls,
        fast_config: TSPM1FastConfig,
        profile: PPB1ReceptorProfileBinding,
    ) -> TSPM1ConfigBinding:
        if type(fast_config) is not TSPM1FastConfig or type(
            profile
        ) is not PPB1ReceptorProfileBinding:
            raise TSPM1Error(
                TSPM1_INVALID_TYPE_OR_SCHEMA,
                "exact fast config and PPB-1 profile are required",
            )
        fields = {
            "schema_version": TSPM1_SCHEMA_VERSION,
            "s2de_contract_digest": TSPM1_S2DE_CONTRACT_DIGEST,
            "s2dg_contract_digest": TSPM1_S2DG_CONTRACT_DIGEST,
            "fast_config_digest": fast_config.digest(),
            "profile_binding_digest": profile.digest(),
            "auditory_ppb1_config_digest": profile.auditory_config.digest(),
            "visual_ppb1_config_digest": profile.visual_config.digest(),
        }
        return cls(
            fast_config,
            profile,
            TSPM1_S2DE_CONTRACT_DIGEST,
            TSPM1_S2DG_CONTRACT_DIGEST,
            fast_config.digest(),
            profile.digest(),
            profile.auditory_config.digest(),
            profile.visual_config.digest(),
            _digest(fields),
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "s2de_contract_digest": self.s2de_contract_digest,
            "s2dg_contract_digest": self.s2dg_contract_digest,
            "fast_config_digest": self.fast_config_digest,
            "profile_binding_digest": self.profile_binding_digest,
            "auditory_ppb1_config_digest": self.auditory_ppb1_config_digest,
            "visual_ppb1_config_digest": self.visual_ppb1_config_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "config_binding_digest": self.config_binding_digest,
        }


def _source_payload(
    config_binding_digest: str,
    envelope: PPB1ActiveReceptorBatchEnvelope,
    auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
    overlap_start: int,
    overlap_end: int,
    schema_version: str,
) -> dict[str, object]:
    return {
        "schema_version": schema_version,
        "config_binding_digest": config_binding_digest,
        "envelope_digest": envelope.envelope_digest,
        "source_batch_digest": envelope.source_batch_digest,
        "profile_binding_digest": envelope.profile_binding_digest,
        "auditory_timed_frame_digest": auditory.timed_frame_provenance_digest,
        "visual_timed_frame_digest": visual.timed_frame_provenance_digest,
        "auditory_input_projection_digest": auditory.ppb1_input_projection_digest,
        "visual_input_projection_digest": visual.ppb1_input_projection_digest,
        "common_field_clock_id": envelope.common_field_clock_id,
        "overlap_start_tick": overlap_start,
        "overlap_end_tick": overlap_end,
    }


def _validate_source_objects(
    envelope: object,
    auditory: object,
    visual: object,
) -> tuple[
    PPB1ActiveReceptorBatchEnvelope,
    PPB1ActiveReceptorTimedFrameBinding,
    PPB1ActiveReceptorTimedFrameBinding,
    int,
    int,
]:
    if (
        type(envelope) is not PPB1ActiveReceptorBatchEnvelope
        or type(auditory) is not PPB1ActiveReceptorTimedFrameBinding
        or type(visual) is not PPB1ActiveReceptorTimedFrameBinding
    ):
        raise TSPM1Error(
            TSPM1_INVALID_TYPE_OR_SCHEMA,
            "exact envelope and timed frame binding types are required",
        )
    if (
        sum(item is auditory for item in envelope.auditory_stream.timed_frames) != 1
        or sum(item is visual for item in envelope.visual_stream.timed_frames) != 1
    ):
        raise TSPM1Error(
            TSPM1_SOURCE_PROVENANCE_MISMATCH,
            "timed frame bindings must be identity members of their envelope streams",
        )
    if (
        auditory.timed_frame.frame.modality_id != "auditory"
        or visual.timed_frame.frame.modality_id != "visual"
    ):
        raise TSPM1Error(
            TSPM1_MODALITY_GEOMETRY_OR_CARRIER_MISMATCH,
            "source modalities are invalid or swapped",
        )
    if (
        auditory.field_clock_id != envelope.common_field_clock_id
        or visual.field_clock_id != envelope.common_field_clock_id
    ):
        raise TSPM1Error(
            TSPM1_CLOCK_ORDER_OR_FIELD_OVERLAP_INVALID,
            "source field clocks do not match the envelope",
        )
    overlap_start = max(
        auditory.field_window_start_tick,
        visual.field_window_start_tick,
    )
    overlap_end = min(
        auditory.field_window_end_tick,
        visual.field_window_end_tick,
    )
    if overlap_start >= overlap_end:
        raise TSPM1Error(
            TSPM1_CLOCK_ORDER_OR_FIELD_OVERLAP_INVALID,
            "auditory and visual field windows do not overlap positively",
        )
    return envelope, auditory, visual, overlap_start, overlap_end


@dataclass(frozen=True, slots=True)
class TSPM1BoundExposure:
    config_binding_digest: str
    envelope: PPB1ActiveReceptorBatchEnvelope
    auditory: PPB1ActiveReceptorTimedFrameBinding
    visual: PPB1ActiveReceptorTimedFrameBinding
    envelope_digest: str
    source_batch_digest: str
    profile_binding_digest: str
    auditory_timed_frame_digest: str
    visual_timed_frame_digest: str
    auditory_input_projection_digest: str
    visual_input_projection_digest: str
    common_field_clock_id: str
    overlap_start_tick: int
    overlap_end_tick: int
    exposure_digest: str
    schema_version: str = "tspm1.private.bound-exposure.v1"

    def __post_init__(self) -> None:
        envelope, auditory, visual, start, end = _validate_source_objects(
            self.envelope,
            self.auditory,
            self.visual,
        )
        if (
            self.schema_version != "tspm1.private.bound-exposure.v1"
            or not _valid_digest(self.config_binding_digest)
            or self.envelope_digest != envelope.envelope_digest
            or self.source_batch_digest != envelope.source_batch_digest
            or self.profile_binding_digest != envelope.profile_binding_digest
            or self.auditory_timed_frame_digest
            != auditory.timed_frame_provenance_digest
            or self.visual_timed_frame_digest != visual.timed_frame_provenance_digest
            or self.auditory_input_projection_digest
            != auditory.ppb1_input_projection_digest
            or self.visual_input_projection_digest
            != visual.ppb1_input_projection_digest
            or self.common_field_clock_id != envelope.common_field_clock_id
            or self.overlap_start_tick != start
            or self.overlap_end_tick != end
            or self.exposure_digest != _digest(self.payload_without_digest())
        ):
            raise TSPM1Error(
                TSPM1_SOURCE_PROVENANCE_MISMATCH,
                "bound exposure is incomplete or digest inconsistent",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return _source_payload(
            self.config_binding_digest,
            self.envelope,
            self.auditory,
            self.visual,
            self.overlap_start_tick,
            self.overlap_end_tick,
            self.schema_version,
        )

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "exposure_digest": self.exposure_digest}


@dataclass(frozen=True, slots=True)
class TSPM1BoundProbe:
    config_binding_digest: str
    envelope: PPB1ActiveReceptorBatchEnvelope
    auditory: PPB1ActiveReceptorTimedFrameBinding
    visual: PPB1ActiveReceptorTimedFrameBinding
    envelope_digest: str
    source_batch_digest: str
    profile_binding_digest: str
    auditory_timed_frame_digest: str
    visual_timed_frame_digest: str
    auditory_input_projection_digest: str
    visual_input_projection_digest: str
    common_field_clock_id: str
    overlap_start_tick: int
    overlap_end_tick: int
    probe_digest: str
    schema_version: str = "tspm1.private.bound-probe.v1"

    def __post_init__(self) -> None:
        envelope, auditory, visual, start, end = _validate_source_objects(
            self.envelope,
            self.auditory,
            self.visual,
        )
        if (
            self.schema_version != "tspm1.private.bound-probe.v1"
            or not _valid_digest(self.config_binding_digest)
            or self.envelope_digest != envelope.envelope_digest
            or self.source_batch_digest != envelope.source_batch_digest
            or self.profile_binding_digest != envelope.profile_binding_digest
            or self.auditory_timed_frame_digest
            != auditory.timed_frame_provenance_digest
            or self.visual_timed_frame_digest != visual.timed_frame_provenance_digest
            or self.auditory_input_projection_digest
            != auditory.ppb1_input_projection_digest
            or self.visual_input_projection_digest
            != visual.ppb1_input_projection_digest
            or self.common_field_clock_id != envelope.common_field_clock_id
            or self.overlap_start_tick != start
            or self.overlap_end_tick != end
            or self.probe_digest != _digest(self.payload_without_digest())
        ):
            raise TSPM1Error(
                TSPM1_SOURCE_PROVENANCE_MISMATCH,
                "bound probe is incomplete or digest inconsistent",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return _source_payload(
            self.config_binding_digest,
            self.envelope,
            self.auditory,
            self.visual,
            self.overlap_start_tick,
            self.overlap_end_tick,
            self.schema_version,
        )

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "probe_digest": self.probe_digest}


def _bind_source(
    config: TSPM1ConfigBinding,
    envelope: PPB1ActiveReceptorBatchEnvelope,
    auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
    *,
    probe: bool,
) -> TSPM1BoundExposure | TSPM1BoundProbe:
    _validate_config(config)
    bound_envelope, bound_auditory, bound_visual, start, end = (
        _validate_source_objects(envelope, auditory, visual)
    )
    if (
        bound_envelope.profile_binding_digest != config.profile_binding_digest
        or bound_envelope.parameter_digest != config.profile.parameter_digest
        or bound_envelope.auditory_stream.bank_config_digest
        != config.auditory_ppb1_config_digest
        or bound_envelope.visual_stream.bank_config_digest
        != config.visual_ppb1_config_digest
    ):
        raise TSPM1Error(
            TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
            "source envelope does not match TSPM-1 config binding",
        )
    schema = (
        "tspm1.private.bound-probe.v1"
        if probe
        else "tspm1.private.bound-exposure.v1"
    )
    payload = _source_payload(
        config.config_binding_digest,
        bound_envelope,
        bound_auditory,
        bound_visual,
        start,
        end,
        schema,
    )
    values = (
        config.config_binding_digest,
        bound_envelope,
        bound_auditory,
        bound_visual,
        bound_envelope.envelope_digest,
        bound_envelope.source_batch_digest,
        bound_envelope.profile_binding_digest,
        bound_auditory.timed_frame_provenance_digest,
        bound_visual.timed_frame_provenance_digest,
        bound_auditory.ppb1_input_projection_digest,
        bound_visual.ppb1_input_projection_digest,
        bound_envelope.common_field_clock_id,
        start,
        end,
        _digest(payload),
    )
    if probe:
        return TSPM1BoundProbe(*values)
    return TSPM1BoundExposure(*values)


def bind_tspm1_exposure(
    config: TSPM1ConfigBinding,
    envelope: PPB1ActiveReceptorBatchEnvelope,
    auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
) -> TSPM1BoundExposure:
    result = _bind_source(config, envelope, auditory, visual, probe=False)
    assert type(result) is TSPM1BoundExposure
    return result


def bind_tspm1_probe(
    config: TSPM1ConfigBinding,
    envelope: PPB1ActiveReceptorBatchEnvelope,
    auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
) -> TSPM1BoundProbe:
    result = _bind_source(config, envelope, auditory, visual, probe=True)
    assert type(result) is TSPM1BoundProbe
    return result


@dataclass(frozen=True, slots=True)
class TSPM1FastSlot:
    slot_id: str
    occupied: bool
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    support_count: int | None
    last_selected_step: int | None
    consolidation_count: int
    last_consolidation_exposure_digest: str | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "slot_id",
            _identifier(
                self.slot_id,
                "slot_id",
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            ),
        )
        if not isinstance(self.occupied, bool):
            raise TSPM1Error(
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                "occupied must be boolean",
            )
        consolidation_count = _nonnegative_integer(
            self.consolidation_count,
            "consolidation_count",
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
        )
        object.__setattr__(self, "consolidation_count", consolidation_count)
        if self.occupied:
            auditory = _bounded_values(
                self.auditory_values,
                "auditory_values",
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            )
            visual = _bounded_values(
                self.visual_values,
                "visual_values",
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            )
            support = _positive_integer(
                self.support_count,
                "support_count",
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            )
            selected = _positive_integer(
                self.last_selected_step,
                "last_selected_step",
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            )
            if consolidation_count == 0:
                if self.last_consolidation_exposure_digest is not None:
                    raise TSPM1Error(
                        TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                        "unconsolidated slot cannot carry a consolidation digest",
                    )
            elif not _valid_digest(self.last_consolidation_exposure_digest):
                raise TSPM1Error(
                    TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                    "consolidated slot requires one exposure digest",
                )
            object.__setattr__(self, "auditory_values", auditory)
            object.__setattr__(self, "visual_values", visual)
            object.__setattr__(self, "support_count", support)
            object.__setattr__(self, "last_selected_step", selected)
        elif (
            tuple(self.auditory_values)
            or tuple(self.visual_values)
            or self.support_count is not None
            or self.last_selected_step is not None
            or consolidation_count != 0
            or self.last_consolidation_exposure_digest is not None
        ):
            raise TSPM1Error(
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                "free slot contains hidden state",
            )

    @classmethod
    def free(cls, slot_id: str) -> TSPM1FastSlot:
        return cls(slot_id, False, (), (), None, None, 0, None)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "slot_id": self.slot_id,
            "occupied": self.occupied,
            "auditory_values": list(self.auditory_values),
            "visual_values": list(self.visual_values),
            "support_count": self.support_count,
            "last_selected_step": self.last_selected_step,
            "consolidation_count": self.consolidation_count,
            "last_consolidation_exposure_digest": (
                self.last_consolidation_exposure_digest
            ),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class TSPM1FastState:
    fast_bank_id: str
    fast_config_digest: str
    accepted_exposure_count: int
    auditory_source_clock_id: str | None
    auditory_last_end_tick: int | None
    visual_source_clock_id: str | None
    visual_last_end_tick: int | None
    slots: tuple[TSPM1FastSlot, ...]
    fast_state_digest: str
    schema_version: str = TSPM1_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != TSPM1_SCHEMA_VERSION:
            raise TSPM1Error(
                TSPM1_INVALID_TYPE_OR_SCHEMA,
                "fast state schema mismatch",
            )
        _identifier(
            self.fast_bank_id,
            "fast_bank_id",
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
        )
        _nonnegative_integer(
            self.accepted_exposure_count,
            "accepted_exposure_count",
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
        )
        slots = tuple(self.slots)
        if (
            not _valid_digest(self.fast_config_digest)
            or any(type(slot) is not TSPM1FastSlot for slot in slots)
            or self.fast_state_digest != _digest(self.payload_without_digest())
        ):
            raise TSPM1Error(
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                "fast state is incomplete or digest inconsistent",
            )
        object.__setattr__(self, "slots", slots)

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "fast_bank_id": self.fast_bank_id,
            "fast_config_digest": self.fast_config_digest,
            "accepted_exposure_count": self.accepted_exposure_count,
            "auditory_source_clock_id": self.auditory_source_clock_id,
            "auditory_last_end_tick": self.auditory_last_end_tick,
            "visual_source_clock_id": self.visual_source_clock_id,
            "visual_last_end_tick": self.visual_last_end_tick,
            "slots": [slot.canonical_payload() for slot in self.slots],
        }

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "fast_state_digest": self.fast_state_digest}


def _make_fast_state(
    config: TSPM1FastConfig,
    accepted_exposure_count: int,
    auditory_source_clock_id: str | None,
    auditory_last_end_tick: int | None,
    visual_source_clock_id: str | None,
    visual_last_end_tick: int | None,
    slots: tuple[TSPM1FastSlot, ...],
) -> TSPM1FastState:
    values = {
        "schema_version": TSPM1_SCHEMA_VERSION,
        "fast_bank_id": config.fast_bank_id,
        "fast_config_digest": config.digest(),
        "accepted_exposure_count": accepted_exposure_count,
        "auditory_source_clock_id": auditory_source_clock_id,
        "auditory_last_end_tick": auditory_last_end_tick,
        "visual_source_clock_id": visual_source_clock_id,
        "visual_last_end_tick": visual_last_end_tick,
        "slots": [slot.canonical_payload() for slot in slots],
    }
    return TSPM1FastState(
        config.fast_bank_id,
        config.digest(),
        accepted_exposure_count,
        auditory_source_clock_id,
        auditory_last_end_tick,
        visual_source_clock_id,
        visual_last_end_tick,
        slots,
        _digest(values),
    )


def _initial_fast_state(config: TSPM1FastConfig) -> TSPM1FastState:
    slots = tuple(
        TSPM1FastSlot.free(f"{config.fast_bank_id}.slot.{index:03d}")
        for index in range(config.capacity)
    )
    return _make_fast_state(config, 0, None, None, None, None, slots)


def _validate_config(config: object) -> TSPM1ConfigBinding:
    if type(config) is not TSPM1ConfigBinding:
        raise TSPM1Error(
            TSPM1_INVALID_TYPE_OR_SCHEMA,
            "exact TSPM1ConfigBinding is required",
        )
    if (
        config.s2de_contract_digest != TSPM1_S2DE_CONTRACT_DIGEST
        or config.s2dg_contract_digest != TSPM1_S2DG_CONTRACT_DIGEST
        or config.fast_config_digest != config.fast_config.digest()
        or config.profile_binding_digest != config.profile.digest()
        or config.auditory_ppb1_config_digest
        != config.profile.auditory_config.digest()
        or config.visual_ppb1_config_digest != config.profile.visual_config.digest()
        or config.config_binding_digest != _digest(config.payload_without_digest())
    ):
        raise TSPM1Error(
            TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
            "TSPM-1 config binding changed",
        )
    return config


def _validate_fast_state(
    config: TSPM1ConfigBinding,
    state: object,
) -> TSPM1FastState:
    if type(state) is not TSPM1FastState:
        raise TSPM1Error(
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            "exact fast state is required",
        )
    fast = config.fast_config
    expected_ids = tuple(
        f"{fast.fast_bank_id}.slot.{index:03d}" for index in range(fast.capacity)
    )
    if (
        state.fast_bank_id != fast.fast_bank_id
        or state.fast_config_digest != fast.digest()
        or len(state.slots) != fast.capacity
        or tuple(slot.slot_id for slot in state.slots) != expected_ids
        or state.fast_state_digest != _digest(state.payload_without_digest())
    ):
        raise TSPM1Error(
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            "fast state does not match its configuration",
        )
    auditory_dimension = len(config.profile.auditory_config.carrier_ids)
    visual_dimension = len(config.profile.visual_config.carrier_ids)
    for slot in state.slots:
        if slot.occupied and (
            len(slot.auditory_values) != auditory_dimension
            or len(slot.visual_values) != visual_dimension
            or slot.support_count is None
            or slot.support_count > fast.consolidate_after
            or slot.last_selected_step is None
            or slot.last_selected_step > state.accepted_exposure_count
            or slot.consolidation_count > state.accepted_exposure_count
        ):
            raise TSPM1Error(
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                "occupied fast slot violates dimensions or counters",
            )
    clocks = (
        state.auditory_source_clock_id,
        state.visual_source_clock_id,
    )
    ticks = (
        state.auditory_last_end_tick,
        state.visual_last_end_tick,
    )
    if state.accepted_exposure_count == 0:
        if any(value is not None for value in clocks + ticks):
            raise TSPM1Error(
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                "initial fast state cannot carry source time",
            )
    else:
        if any(value is None for value in clocks + ticks):
            raise TSPM1Error(
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                "advanced fast state requires complete source time",
            )
        _identifier(clocks[0], "auditory_source_clock_id", TSPM1_COMPOSITE_OR_FAST_STATE_INVALID)
        _identifier(clocks[1], "visual_source_clock_id", TSPM1_COMPOSITE_OR_FAST_STATE_INVALID)
        _positive_integer(ticks[0], "auditory_last_end_tick", TSPM1_COMPOSITE_OR_FAST_STATE_INVALID)
        _positive_integer(ticks[1], "visual_last_end_tick", TSPM1_COMPOSITE_OR_FAST_STATE_INVALID)
    return state


@dataclass(frozen=True, slots=True)
class TSPM1CompositeState:
    architecture_id: str
    config_binding_digest: str
    generation: int
    parent_composite_state_digest: str | None
    last_exposure_digest: str | None
    fast_state: TSPM1FastState
    auditory_ppb1_state: PPB1BankState
    visual_ppb1_state: PPB1BankState
    composite_state_digest: str
    schema_version: str = TSPM1_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if (
            self.schema_version != TSPM1_SCHEMA_VERSION
            or self.architecture_id != TSPM1_ARCHITECTURE_ID
            or not _valid_digest(self.config_binding_digest)
            or type(self.fast_state) is not TSPM1FastState
            or type(self.auditory_ppb1_state) is not PPB1BankState
            or type(self.visual_ppb1_state) is not PPB1BankState
            or self.composite_state_digest != _digest(self.payload_without_digest())
        ):
            raise TSPM1Error(
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                "composite state is incomplete or digest inconsistent",
            )
        generation = _nonnegative_integer(
            self.generation,
            "generation",
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
        )
        if generation == 0:
            if (
                self.parent_composite_state_digest is not None
                or self.last_exposure_digest is not None
            ):
                raise TSPM1Error(
                    TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                    "initial composite state cannot have lineage",
                )
        elif not _valid_digest(self.parent_composite_state_digest) or not _valid_digest(
            self.last_exposure_digest
        ):
            raise TSPM1Error(
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                "advanced composite state requires complete lineage",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "architecture_id": self.architecture_id,
            "config_binding_digest": self.config_binding_digest,
            "generation": self.generation,
            "parent_composite_state_digest": self.parent_composite_state_digest,
            "last_exposure_digest": self.last_exposure_digest,
            "fast_state_digest": self.fast_state.fast_state_digest,
            "auditory_ppb1_state_digest": self.auditory_ppb1_state.digest(),
            "visual_ppb1_state_digest": self.visual_ppb1_state.digest(),
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "composite_state_digest": self.composite_state_digest,
        }


def _make_composite_state(
    config: TSPM1ConfigBinding,
    generation: int,
    parent_digest: str | None,
    exposure_digest: str | None,
    fast_state: TSPM1FastState,
    auditory_state: PPB1BankState,
    visual_state: PPB1BankState,
) -> TSPM1CompositeState:
    values = {
        "schema_version": TSPM1_SCHEMA_VERSION,
        "architecture_id": TSPM1_ARCHITECTURE_ID,
        "config_binding_digest": config.config_binding_digest,
        "generation": generation,
        "parent_composite_state_digest": parent_digest,
        "last_exposure_digest": exposure_digest,
        "fast_state_digest": fast_state.fast_state_digest,
        "auditory_ppb1_state_digest": auditory_state.digest(),
        "visual_ppb1_state_digest": visual_state.digest(),
    }
    return TSPM1CompositeState(
        TSPM1_ARCHITECTURE_ID,
        config.config_binding_digest,
        generation,
        parent_digest,
        exposure_digest,
        fast_state,
        auditory_state,
        visual_state,
        _digest(values),
    )


def _validate_composite_state(
    config: TSPM1ConfigBinding,
    state: object,
) -> TSPM1CompositeState:
    if type(state) is not TSPM1CompositeState:
        raise TSPM1Error(
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            "exact composite state is required",
        )
    if (
        state.config_binding_digest != config.config_binding_digest
        or state.composite_state_digest != _digest(state.payload_without_digest())
        or state.fast_state.accepted_exposure_count != state.generation
    ):
        raise TSPM1Error(
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            "composite identity or generation mismatch",
        )
    _validate_fast_state(config, state.fast_state)
    try:
        auditory = _validate_ppb1_state(
            config.profile.auditory_config,
            state.auditory_ppb1_state,
        )
        visual = _validate_ppb1_state(
            config.profile.visual_config,
            state.visual_ppb1_state,
        )
    except Exception as exc:
        raise TSPM1Error(
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            "composite PPB-1 states are invalid",
        ) from exc
    if auditory.accepted_step_count != visual.accepted_step_count:
        raise TSPM1Error(
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            "slow PPB-1 generations must remain paired",
        )
    if auditory.accepted_step_count > state.generation:
        raise TSPM1Error(
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            "slow PPB-1 state cannot exceed fast generation",
        )
    if state.generation == 0 and (
        auditory.accepted_step_count != 0
        or visual.accepted_step_count != 0
        or state.fast_state.accepted_exposure_count != 0
    ):
        raise TSPM1Error(
            TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
            "initial composite requires three fresh banks",
        )
    fast = state.fast_state
    for ppb, clock, tick in (
        (auditory, fast.auditory_source_clock_id, fast.auditory_last_end_tick),
        (visual, fast.visual_source_clock_id, fast.visual_last_end_tick),
    ):
        if ppb.source_clock_id is not None and (
            ppb.source_clock_id != clock
            or ppb.last_source_window_end_tick is None
            or tick is None
            or ppb.last_source_window_end_tick > tick
        ):
            raise TSPM1Error(
                TSPM1_COMPOSITE_OR_FAST_STATE_INVALID,
                "slow PPB-1 time exceeds or diverges from fast time",
            )
    return state


def initial_tspm1_composite_state(
    config: TSPM1ConfigBinding,
) -> TSPM1CompositeState:
    binding = _validate_config(config)
    return _make_composite_state(
        binding,
        0,
        None,
        None,
        _initial_fast_state(binding.fast_config),
        initial_ppb1_bank_state(binding.profile.auditory_config),
        initial_ppb1_bank_state(binding.profile.visual_config),
    )


def _validate_bound_source_provenance(
    config: TSPM1ConfigBinding,
    source: TSPM1BoundExposure | TSPM1BoundProbe,
) -> None:
    envelope, auditory, visual = source.envelope, source.auditory, source.visual
    if (
        source.config_binding_digest != config.config_binding_digest
        or source.profile_binding_digest != config.profile_binding_digest
        or envelope.profile_binding_digest != config.profile_binding_digest
        or envelope.auditory_stream.bank_config_digest
        != config.auditory_ppb1_config_digest
        or envelope.visual_stream.bank_config_digest
        != config.visual_ppb1_config_digest
    ):
        raise TSPM1Error(
            TSPM1_CONFIG_OR_CONTRACT_MISMATCH,
            "bound source does not match TSPM-1 configuration",
        )
    if (
        sum(item is auditory for item in envelope.auditory_stream.timed_frames) != 1
        or sum(item is visual for item in envelope.visual_stream.timed_frames) != 1
        or source.envelope_digest != envelope.envelope_digest
        or source.source_batch_digest != envelope.source_batch_digest
        or source.auditory_timed_frame_digest
        != auditory.timed_frame_provenance_digest
        or source.visual_timed_frame_digest != visual.timed_frame_provenance_digest
        or source.auditory_input_projection_digest
        != auditory.ppb1_input_projection_digest
        or source.visual_input_projection_digest
        != visual.ppb1_input_projection_digest
    ):
        raise TSPM1Error(
            TSPM1_SOURCE_PROVENANCE_MISMATCH,
            "bound source provenance changed",
        )
    expected_digest = _digest(source.payload_without_digest())
    source_digest = (
        source.exposure_digest
        if type(source) is TSPM1BoundExposure
        else source.probe_digest
    )
    if source_digest != expected_digest:
        raise TSPM1Error(
            TSPM1_SOURCE_PROVENANCE_MISMATCH,
            "bound source digest changed",
        )


def _validate_bound_source_geometry(
    config: TSPM1ConfigBinding,
    source: TSPM1BoundExposure | TSPM1BoundProbe,
) -> None:
    auditory_frame = source.auditory.timed_frame.frame
    visual_frame = source.visual.timed_frame.frame
    if (
        auditory_frame.modality_id != "auditory"
        or visual_frame.modality_id != "visual"
        or auditory_frame.geometry_id != config.profile.auditory_config.geometry_id
        or auditory_frame.carrier_ids
        != config.profile.auditory_config.carrier_ids
        or visual_frame.geometry_id != config.profile.visual_config.geometry_id
        or visual_frame.carrier_ids != config.profile.visual_config.carrier_ids
    ):
        raise TSPM1Error(
            TSPM1_MODALITY_GEOMETRY_OR_CARRIER_MISMATCH,
            "bound source geometry or carrier order mismatch",
        )


def _validate_bound_source_time(
    state: TSPM1FastState,
    source: TSPM1BoundExposure | TSPM1BoundProbe,
    *,
    strictly_later: bool,
) -> None:
    auditory = source.auditory
    visual = source.visual
    overlap_start = max(
        auditory.field_window_start_tick,
        visual.field_window_start_tick,
    )
    overlap_end = min(
        auditory.field_window_end_tick,
        visual.field_window_end_tick,
    )
    if (
        auditory.field_clock_id != source.envelope.common_field_clock_id
        or visual.field_clock_id != source.envelope.common_field_clock_id
        or source.common_field_clock_id != source.envelope.common_field_clock_id
        or overlap_start >= overlap_end
        or source.overlap_start_tick != overlap_start
        or source.overlap_end_tick != overlap_end
    ):
        raise TSPM1Error(
            TSPM1_CLOCK_ORDER_OR_FIELD_OVERLAP_INVALID,
            "bound source field clock or overlap changed",
        )
    _validate_source_after_state(state, source, strictly_later=strictly_later)


def _validate_bound_source_against_config(
    config: TSPM1ConfigBinding,
    source: TSPM1BoundExposure | TSPM1BoundProbe,
) -> None:
    _validate_bound_source_provenance(config, source)
    _validate_bound_source_geometry(config, source)


def _validate_source_after_state(
    state: TSPM1FastState,
    source: TSPM1BoundExposure | TSPM1BoundProbe,
    *,
    strictly_later: bool,
) -> None:
    auditory_frame = source.auditory.timed_frame.frame
    visual_frame = source.visual.timed_frame.frame
    if state.auditory_source_clock_id is None:
        return
    assert state.auditory_last_end_tick is not None
    assert state.visual_source_clock_id is not None
    assert state.visual_last_end_tick is not None
    invalid = (
        auditory_frame.clock_id != state.auditory_source_clock_id
        or visual_frame.clock_id != state.visual_source_clock_id
    )
    if strictly_later:
        invalid = invalid or (
            auditory_frame.window_end_tick <= state.auditory_last_end_tick
            or visual_frame.window_end_tick <= state.visual_last_end_tick
        )
    if invalid:
        raise TSPM1Error(
            TSPM1_CLOCK_ORDER_OR_FIELD_OVERLAP_INVALID,
            "bound source is stale or changed source clock",
        )


@dataclass(frozen=True, slots=True)
class TSPM1FastTransitionCandidate:
    poststate: TSPM1FastState
    primary_event: str
    partial_association_conflict: bool
    expired_slot_digests: tuple[str, ...]
    replaced_slot_digest: str | None
    selected_slot_id: str
    auditory_match_distance: float | None
    visual_match_distance: float | None
    consolidation_eligible: bool
    candidate_digest: str

    def __post_init__(self) -> None:
        expired = tuple(self.expired_slot_digests)
        if (
            type(self.poststate) is not TSPM1FastState
            or self.primary_event not in _PRIMARY_EVENTS
            or not isinstance(self.partial_association_conflict, bool)
            or any(not _valid_digest(value) for value in expired)
            or not isinstance(self.consolidation_eligible, bool)
            or self.candidate_digest != _digest(self.payload_without_digest())
        ):
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "fast candidate is incomplete or digest inconsistent",
            )
        _identifier(
            self.selected_slot_id,
            "selected_slot_id",
            TSPM1_ATOMIC_RESULT_REQUIRED,
        )
        if self.primary_event == "FAST_REPLACED":
            if not _valid_digest(self.replaced_slot_digest):
                raise TSPM1Error(
                    TSPM1_ATOMIC_RESULT_REQUIRED,
                    "replacement requires discarded slot digest",
                )
        elif self.replaced_slot_digest is not None:
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "only replacement may carry a discarded slot digest",
            )
        if self.primary_event == "FAST_UPDATED" and self.partial_association_conflict:
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "matched update cannot carry a partial association conflict",
            )
        if self.primary_event == "FAST_UPDATED":
            for distance in (
                self.auditory_match_distance,
                self.visual_match_distance,
            ):
                value = _finite(
                    distance,
                    "match_distance",
                    TSPM1_ATOMIC_RESULT_REQUIRED,
                )
                if not 0.0 <= value <= 2.0:
                    raise TSPM1Error(
                        TSPM1_ATOMIC_RESULT_REQUIRED,
                        "match distance out of range",
                    )
        elif (
            self.auditory_match_distance is not None
            or self.visual_match_distance is not None
            or self.consolidation_eligible
        ):
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "new or replaced fast slot cannot be a matched consolidation",
            )
        object.__setattr__(self, "expired_slot_digests", expired)

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": TSPM1_SCHEMA_VERSION,
            "poststate_digest": self.poststate.fast_state_digest,
            "primary_event": self.primary_event,
            "partial_association_conflict": self.partial_association_conflict,
            "expired_slot_digests": list(self.expired_slot_digests),
            "replaced_slot_digest": self.replaced_slot_digest,
            "selected_slot_id": self.selected_slot_id,
            "auditory_match_distance": self.auditory_match_distance,
            "visual_match_distance": self.visual_match_distance,
            "consolidation_eligible": self.consolidation_eligible,
        }


def _make_candidate(
    poststate: TSPM1FastState,
    primary_event: str,
    partial_conflict: bool,
    expired_digests: tuple[str, ...],
    replaced_digest: str | None,
    selected_slot_id: str,
    auditory_distance: float | None,
    visual_distance: float | None,
    eligible: bool,
) -> TSPM1FastTransitionCandidate:
    values = {
        "schema_version": TSPM1_SCHEMA_VERSION,
        "poststate_digest": poststate.fast_state_digest,
        "primary_event": primary_event,
        "partial_association_conflict": partial_conflict,
        "expired_slot_digests": list(expired_digests),
        "replaced_slot_digest": replaced_digest,
        "selected_slot_id": selected_slot_id,
        "auditory_match_distance": auditory_distance,
        "visual_match_distance": visual_distance,
        "consolidation_eligible": eligible,
    }
    return TSPM1FastTransitionCandidate(
        poststate,
        primary_event,
        partial_conflict,
        expired_digests,
        replaced_digest,
        selected_slot_id,
        auditory_distance,
        visual_distance,
        eligible,
        _digest(values),
    )


def advance_tspm1_fast(
    config: TSPM1ConfigBinding,
    prestate: TSPM1FastState,
    exposure: TSPM1BoundExposure,
) -> TSPM1FastTransitionCandidate:
    if type(exposure) is not TSPM1BoundExposure:
        raise TSPM1Error(
            TSPM1_INVALID_TYPE_OR_SCHEMA,
            "fast transition requires one exact bound exposure",
        )
    binding = _validate_config(config)
    state = _validate_fast_state(binding, prestate)
    _validate_bound_source_against_config(binding, exposure)
    _validate_bound_source_time(state, exposure, strictly_later=True)

    auditory_values = tuple(exposure.auditory.timed_frame.frame.values)
    visual_values = tuple(exposure.visual.timed_frame.frame.values)
    step = state.accepted_exposure_count + 1
    slots: list[TSPM1FastSlot] = []
    expired: list[tuple[str, str]] = []
    for slot in state.slots:
        if (
            slot.occupied
            and slot.last_selected_step is not None
            and step - slot.last_selected_step
            >= binding.fast_config.expire_after_exposures
        ):
            expired.append((slot.slot_id, slot.digest()))
            slots.append(TSPM1FastSlot.free(slot.slot_id))
        else:
            slots.append(slot)

    joint_matches: list[tuple[float, float, str, int, float, float]] = []
    any_auditory_match = False
    any_visual_match = False
    for index, slot in enumerate(slots):
        if not slot.occupied:
            continue
        auditory_distance = normalized_mean_l1_distance(
            auditory_values,
            slot.auditory_values,
        )
        visual_distance = normalized_mean_l1_distance(
            visual_values,
            slot.visual_values,
        )
        auditory_match = (
            auditory_distance <= binding.fast_config.auditory_match_threshold
        )
        visual_match = visual_distance <= binding.fast_config.visual_match_threshold
        any_auditory_match = any_auditory_match or auditory_match
        any_visual_match = any_visual_match or visual_match
        if auditory_match and visual_match:
            joint_matches.append(
                (
                    max(auditory_distance, visual_distance),
                    auditory_distance + visual_distance,
                    slot.slot_id,
                    index,
                    auditory_distance,
                    visual_distance,
                )
            )

    replaced_digest: str | None = None
    selected_auditory_distance: float | None = None
    selected_visual_distance: float | None = None
    partial_conflict = False
    eligible = False
    if joint_matches:
        (
            _,
            _,
            _,
            selected_index,
            selected_auditory_distance,
            selected_visual_distance,
        ) = min(joint_matches)
        selected = slots[selected_index]
        assert selected.support_count is not None
        updated_auditory = tuple(
            (1.0 - binding.fast_config.update_factor) * previous
            + binding.fast_config.update_factor * current
            for previous, current in zip(
                selected.auditory_values,
                auditory_values,
                strict=True,
            )
        )
        updated_visual = tuple(
            (1.0 - binding.fast_config.update_factor) * previous
            + binding.fast_config.update_factor * current
            for previous, current in zip(
                selected.visual_values,
                visual_values,
                strict=True,
            )
        )
        support = min(
            binding.fast_config.consolidate_after,
            selected.support_count + 1,
        )
        slots[selected_index] = TSPM1FastSlot(
            selected.slot_id,
            True,
            updated_auditory,
            updated_visual,
            support,
            step,
            selected.consolidation_count,
            selected.last_consolidation_exposure_digest,
        )
        primary_event = "FAST_UPDATED"
        eligible = support >= binding.fast_config.consolidate_after
    else:
        partial_conflict = any_auditory_match or any_visual_match
        free_indices = [index for index, slot in enumerate(slots) if not slot.occupied]
        if free_indices:
            selected_index = min(free_indices, key=lambda index: slots[index].slot_id)
            primary_event = "FAST_CREATED"
        else:
            selected_index = min(
                range(len(slots)),
                key=lambda index: (
                    slots[index].last_selected_step,
                    slots[index].slot_id,
                ),
            )
            replaced_digest = slots[selected_index].digest()
            primary_event = "FAST_REPLACED"
        selected = slots[selected_index]
        slots[selected_index] = TSPM1FastSlot(
            selected.slot_id,
            True,
            auditory_values,
            visual_values,
            1,
            step,
            0,
            None,
        )

    auditory_frame = exposure.auditory.timed_frame.frame
    visual_frame = exposure.visual.timed_frame.frame
    poststate = _make_fast_state(
        binding.fast_config,
        step,
        auditory_frame.clock_id,
        auditory_frame.window_end_tick,
        visual_frame.clock_id,
        visual_frame.window_end_tick,
        tuple(slots),
    )
    expired_digests = tuple(value for _, value in sorted(expired))
    return _make_candidate(
        poststate,
        primary_event,
        partial_conflict,
        expired_digests,
        replaced_digest,
        slots[selected_index].slot_id,
        selected_auditory_distance,
        selected_visual_distance,
        eligible,
    )


def _validate_fast_candidate_relations(
    config: TSPM1ConfigBinding,
    prestate: TSPM1FastState,
    exposure: TSPM1BoundExposure,
    candidate: object,
) -> TSPM1FastTransitionCandidate:
    if type(candidate) is not TSPM1FastTransitionCandidate:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "exact fast transition candidate is required",
        )
    state = _validate_fast_state(config, prestate)
    poststate = _validate_fast_state(config, candidate.poststate)
    step = state.accepted_exposure_count + 1
    auditory_frame = exposure.auditory.timed_frame.frame
    visual_frame = exposure.visual.timed_frame.frame
    auditory_values = tuple(auditory_frame.values)
    visual_values = tuple(visual_frame.values)

    slots: list[TSPM1FastSlot] = []
    expired: list[tuple[str, str]] = []
    for slot in state.slots:
        if (
            slot.occupied
            and slot.last_selected_step is not None
            and step - slot.last_selected_step
            >= config.fast_config.expire_after_exposures
        ):
            expired.append((slot.slot_id, slot.digest()))
            slots.append(TSPM1FastSlot.free(slot.slot_id))
        else:
            slots.append(slot)

    joint_matches: list[tuple[float, float, str, int, float, float]] = []
    any_auditory_match = False
    any_visual_match = False
    for index, slot in enumerate(slots):
        if not slot.occupied:
            continue
        auditory_distance = normalized_mean_l1_distance(
            auditory_values,
            slot.auditory_values,
        )
        visual_distance = normalized_mean_l1_distance(
            visual_values,
            slot.visual_values,
        )
        auditory_match = (
            auditory_distance <= config.fast_config.auditory_match_threshold
        )
        visual_match = visual_distance <= config.fast_config.visual_match_threshold
        any_auditory_match = any_auditory_match or auditory_match
        any_visual_match = any_visual_match or visual_match
        if auditory_match and visual_match:
            joint_matches.append(
                (
                    max(auditory_distance, visual_distance),
                    auditory_distance + visual_distance,
                    slot.slot_id,
                    index,
                    auditory_distance,
                    visual_distance,
                )
            )

    expected_replaced_digest: str | None = None
    expected_auditory_distance: float | None = None
    expected_visual_distance: float | None = None
    expected_eligible = False
    if joint_matches:
        (
            _,
            _,
            _,
            selected_index,
            expected_auditory_distance,
            expected_visual_distance,
        ) = min(joint_matches)
        selected = slots[selected_index]
        assert selected.support_count is not None
        support = min(
            config.fast_config.consolidate_after,
            selected.support_count + 1,
        )
        slots[selected_index] = TSPM1FastSlot(
            selected.slot_id,
            True,
            tuple(
                (1.0 - config.fast_config.update_factor) * previous
                + config.fast_config.update_factor * current
                for previous, current in zip(
                    selected.auditory_values,
                    auditory_values,
                    strict=True,
                )
            ),
            tuple(
                (1.0 - config.fast_config.update_factor) * previous
                + config.fast_config.update_factor * current
                for previous, current in zip(
                    selected.visual_values,
                    visual_values,
                    strict=True,
                )
            ),
            support,
            step,
            selected.consolidation_count,
            selected.last_consolidation_exposure_digest,
        )
        expected_event = "FAST_UPDATED"
        expected_conflict = False
        expected_eligible = support >= config.fast_config.consolidate_after
    else:
        expected_conflict = any_auditory_match or any_visual_match
        free_indices = [index for index, slot in enumerate(slots) if not slot.occupied]
        if free_indices:
            selected_index = min(free_indices, key=lambda index: slots[index].slot_id)
            expected_event = "FAST_CREATED"
        else:
            selected_index = min(
                range(len(slots)),
                key=lambda index: (
                    slots[index].last_selected_step,
                    slots[index].slot_id,
                ),
            )
            expected_replaced_digest = slots[selected_index].digest()
            expected_event = "FAST_REPLACED"
        selected = slots[selected_index]
        slots[selected_index] = TSPM1FastSlot(
            selected.slot_id,
            True,
            auditory_values,
            visual_values,
            1,
            step,
            0,
            None,
        )

    expected_poststate = _make_fast_state(
        config.fast_config,
        step,
        auditory_frame.clock_id,
        auditory_frame.window_end_tick,
        visual_frame.clock_id,
        visual_frame.window_end_tick,
        tuple(slots),
    )
    expected_expired_digests = tuple(value for _, value in sorted(expired))
    if (
        poststate != expected_poststate
        or candidate.primary_event != expected_event
        or candidate.partial_association_conflict != expected_conflict
        or candidate.expired_slot_digests != expected_expired_digests
        or candidate.replaced_slot_digest != expected_replaced_digest
        or candidate.selected_slot_id != slots[selected_index].slot_id
        or candidate.auditory_match_distance != expected_auditory_distance
        or candidate.visual_match_distance != expected_visual_distance
        or candidate.consolidation_eligible != expected_eligible
    ):
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "fast candidate violates its prestate and exposure relation",
        )
    return candidate


def _commit_fast_consolidation(
    config: TSPM1ConfigBinding,
    candidate: TSPM1FastTransitionCandidate,
    exposure: TSPM1BoundExposure,
) -> TSPM1FastState:
    slots = list(candidate.poststate.slots)
    indices = [
        index
        for index, slot in enumerate(slots)
        if slot.slot_id == candidate.selected_slot_id
    ]
    if len(indices) != 1:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "candidate selected slot is not unique",
        )
    index = indices[0]
    slot = slots[index]
    if not slot.occupied or slot.support_count is None:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "consolidation candidate slot is not occupied",
        )
    slots[index] = TSPM1FastSlot(
        slot.slot_id,
        True,
        slot.auditory_values,
        slot.visual_values,
        slot.support_count,
        slot.last_selected_step,
        slot.consolidation_count + 1,
        exposure.exposure_digest,
    )
    state = candidate.poststate
    return _make_fast_state(
        config.fast_config,
        state.accepted_exposure_count,
        state.auditory_source_clock_id,
        state.auditory_last_end_tick,
        state.visual_source_clock_id,
        state.visual_last_end_tick,
        tuple(slots),
    )


def _validate_fast_consolidation_relation(
    config: TSPM1ConfigBinding,
    candidate: TSPM1FastTransitionCandidate,
    exposure: TSPM1BoundExposure,
    poststate: object,
) -> TSPM1FastState:
    if not candidate.consolidation_eligible or candidate.primary_event != "FAST_UPDATED":
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "fast consolidation requires one eligible matched candidate",
        )
    state = _validate_fast_state(config, poststate)
    slots = list(candidate.poststate.slots)
    selected_indices = [
        index
        for index, slot in enumerate(slots)
        if slot.slot_id == candidate.selected_slot_id
    ]
    if len(selected_indices) != 1:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "fast consolidation selected slot is not unique",
        )
    index = selected_indices[0]
    selected = slots[index]
    if not selected.occupied or selected.support_count is None:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "fast consolidation selected slot is not occupied",
        )
    slots[index] = TSPM1FastSlot(
        selected.slot_id,
        True,
        selected.auditory_values,
        selected.visual_values,
        selected.support_count,
        selected.last_selected_step,
        selected.consolidation_count + 1,
        exposure.exposure_digest,
    )
    expected = _make_fast_state(
        config.fast_config,
        candidate.poststate.accepted_exposure_count,
        candidate.poststate.auditory_source_clock_id,
        candidate.poststate.auditory_last_end_tick,
        candidate.poststate.visual_source_clock_id,
        candidate.poststate.visual_last_end_tick,
        tuple(slots),
    )
    if state != expected:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "fast consolidation changed fields outside its selected slot relation",
        )
    return state


def _validate_ppb1_step_result(
    config,
    prestate: PPB1BankState,
    source: PPB1ActiveReceptorTimedFrameBinding,
    result: object,
) -> PPB1StepResult:
    if (
        type(result) is not PPB1StepResult
        or type(result.poststate) is not PPB1BankState
        or type(result.readout) is not PPB1Readout
    ):
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "PPB-1 step requires exact result, state, and readout types",
        )
    try:
        poststate = _validate_ppb1_state(config, result.poststate)
    except Exception as exc:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "PPB-1 result poststate is invalid",
        ) from exc
    readout = result.readout
    frame = source.timed_frame.frame
    matching_slots = [
        slot for slot in poststate.slots if slot.slot_id == readout.slot_id
    ]
    if (
        len(matching_slots) != 1
        or readout.bank_id != config.bank_id
        or readout.modality_id != config.modality_id
        or readout.config_digest != config.digest()
        or readout.prestate_digest != prestate.digest()
        or readout.input_digest != source.ppb1_input_projection_digest
        or readout.poststate_digest != poststate.digest()
        or poststate.accepted_step_count != prestate.accepted_step_count + 1
        or poststate.source_clock_id != frame.clock_id
        or poststate.last_source_window_end_tick != frame.window_end_tick
    ):
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "PPB-1 result does not match config, prestate, input, or poststate",
        )
    selected = matching_slots[0]
    if (
        not selected.occupied
        or selected.support_count != readout.support_count
        or selected.prototype_values != readout.prototype_values
        or readout.stabilized != (readout.support_count >= config.stable_after)
    ):
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "PPB-1 readout does not match its selected poststate slot",
        )
    return result


@dataclass(frozen=True, slots=True)
class TSPM1TransitionReceipt:
    config_binding_digest: str
    owner_authorization_prestate_digest: str
    exposure_digest: str
    composite_prestate_digest: str
    fast_candidate_digest: str
    primary_event: str
    partial_association_conflict: bool
    expired_slot_digests: tuple[str, ...]
    replaced_slot_digest: str | None
    selected_slot_id: str
    consolidation_status: str
    consolidation_decision_digest: str
    auditory_ppb1_readout_digest: str | None
    visual_ppb1_readout_digest: str | None
    auditory_ppb1_stabilized: bool | None
    visual_ppb1_stabilized: bool | None
    fast_poststate_digest: str
    auditory_ppb1_poststate_digest: str
    visual_ppb1_poststate_digest: str
    composite_poststate_digest: str
    receipt_digest: str
    schema_version: str = TSPM1_SCHEMA_VERSION

    def __post_init__(self) -> None:
        expired = tuple(self.expired_slot_digests)
        required_digests = (
            self.config_binding_digest,
            self.owner_authorization_prestate_digest,
            self.exposure_digest,
            self.composite_prestate_digest,
            self.fast_candidate_digest,
            self.consolidation_decision_digest,
            self.fast_poststate_digest,
            self.auditory_ppb1_poststate_digest,
            self.visual_ppb1_poststate_digest,
            self.composite_poststate_digest,
            self.receipt_digest,
        )
        if (
            self.schema_version != TSPM1_SCHEMA_VERSION
            or self.primary_event not in _PRIMARY_EVENTS
            or self.consolidation_status not in _CONSOLIDATION_STATUSES
            or not isinstance(self.partial_association_conflict, bool)
            or any(not _valid_digest(value) for value in required_digests)
            or any(not _valid_digest(value) for value in expired)
            or self.receipt_digest != _digest(self.payload_without_digest())
        ):
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "transition receipt is incomplete or digest inconsistent",
            )
        _identifier(
            self.selected_slot_id,
            "selected_slot_id",
            TSPM1_ATOMIC_RESULT_REQUIRED,
        )
        if self.primary_event == "FAST_REPLACED":
            if not _valid_digest(self.replaced_slot_digest):
                raise TSPM1Error(
                    TSPM1_ATOMIC_RESULT_REQUIRED,
                    "replacement receipt requires discarded slot digest",
                )
        elif self.replaced_slot_digest is not None:
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "nonreplacement receipt cannot carry discarded slot digest",
            )
        if self.primary_event == "FAST_UPDATED" and self.partial_association_conflict:
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "matched receipt cannot carry a partial association conflict",
            )
        committed_values = (
            self.auditory_ppb1_readout_digest,
            self.visual_ppb1_readout_digest,
        )
        stabilized_values = (
            self.auditory_ppb1_stabilized,
            self.visual_ppb1_stabilized,
        )
        if self.consolidation_status == "COMMITTED":
            if (
                self.primary_event != "FAST_UPDATED"
                or any(not _valid_digest(value) for value in committed_values)
                or any(not isinstance(value, bool) for value in stabilized_values)
            ):
                raise TSPM1Error(
                    TSPM1_ATOMIC_RESULT_REQUIRED,
                    "committed receipt requires both PPB-1 findings",
                )
        elif any(value is not None for value in committed_values + stabilized_values):
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "ineligible receipt cannot carry PPB-1 findings",
            )
        object.__setattr__(self, "expired_slot_digests", expired)

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "config_binding_digest": self.config_binding_digest,
            "owner_authorization_prestate_digest": (
                self.owner_authorization_prestate_digest
            ),
            "exposure_digest": self.exposure_digest,
            "composite_prestate_digest": self.composite_prestate_digest,
            "fast_candidate_digest": self.fast_candidate_digest,
            "primary_event": self.primary_event,
            "partial_association_conflict": self.partial_association_conflict,
            "expired_slot_digests": list(self.expired_slot_digests),
            "replaced_slot_digest": self.replaced_slot_digest,
            "selected_slot_id": self.selected_slot_id,
            "consolidation_status": self.consolidation_status,
            "consolidation_decision_digest": self.consolidation_decision_digest,
            "auditory_ppb1_readout_digest": self.auditory_ppb1_readout_digest,
            "visual_ppb1_readout_digest": self.visual_ppb1_readout_digest,
            "auditory_ppb1_stabilized": self.auditory_ppb1_stabilized,
            "visual_ppb1_stabilized": self.visual_ppb1_stabilized,
            "fast_poststate_digest": self.fast_poststate_digest,
            "auditory_ppb1_poststate_digest": self.auditory_ppb1_poststate_digest,
            "visual_ppb1_poststate_digest": self.visual_ppb1_poststate_digest,
            "composite_poststate_digest": self.composite_poststate_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "receipt_digest": self.receipt_digest}


@dataclass(frozen=True, slots=True)
class TSPM1CoordinatorOwnerSnapshot:
    owner_id: str
    authorization_id: str
    consumption_id: str
    authorized_config_binding_digest: str
    authorized_composite_prestate_digest: str
    authorized_exposure_digest: str
    status: str
    attempt_count: int
    use_count: int
    generation: int
    committed_result_digest: str | None
    failure_code: str | None
    failure_digest: str | None
    owner_state_digest: str

    def __post_init__(self) -> None:
        for role in ("owner_id", "authorization_id", "consumption_id"):
            _identifier(getattr(self, role), role, TSPM1_ATOMIC_RESULT_REQUIRED)
        if (
            self.status not in _OWNER_STATES
            or any(
                not _valid_digest(value)
                for value in (
                    self.authorized_config_binding_digest,
                    self.authorized_composite_prestate_digest,
                    self.authorized_exposure_digest,
                    self.owner_state_digest,
                )
            )
            or not self._shape_valid()
            or self.owner_state_digest != _digest(self.payload_without_digest())
        ):
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "owner snapshot is invalid",
            )

    def _shape_valid(self) -> bool:
        if self.status == "AUTHORIZED":
            return (
                (self.attempt_count, self.use_count, self.generation) == (0, 0, 0)
                and self.committed_result_digest is None
                and self.failure_code is None
                and self.failure_digest is None
            )
        if self.status == "CONSUMED":
            return (
                (self.attempt_count, self.use_count, self.generation) == (1, 1, 1)
                and _valid_digest(self.committed_result_digest)
                and self.failure_code is None
                and self.failure_digest is None
            )
        return (
            (self.attempt_count, self.use_count, self.generation) == (1, 0, 1)
            and self.committed_result_digest is None
            and isinstance(self.failure_code, str)
            and bool(self.failure_code)
            and _valid_digest(self.failure_digest)
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": TSPM1_SCHEMA_VERSION,
            "owner_id": self.owner_id,
            "authorization_id": self.authorization_id,
            "consumption_id": self.consumption_id,
            "authorized_config_binding_digest": self.authorized_config_binding_digest,
            "authorized_composite_prestate_digest": (
                self.authorized_composite_prestate_digest
            ),
            "authorized_exposure_digest": self.authorized_exposure_digest,
            "status": self.status,
            "attempt_count": self.attempt_count,
            "use_count": self.use_count,
            "generation": self.generation,
            "committed_result_digest": self.committed_result_digest,
            "failure_code": self.failure_code,
            "failure_digest": self.failure_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "owner_state_digest": self.owner_state_digest}

    def result_projection_payload(self) -> dict[str, object]:
        payload = self.payload_without_digest()
        payload.pop("committed_result_digest")
        return payload


def _snapshot(owner: TSPM1CoordinatorOwner) -> TSPM1CoordinatorOwnerSnapshot:
    values = {
        "schema_version": TSPM1_SCHEMA_VERSION,
        "owner_id": owner._owner_id,
        "authorization_id": owner._authorization_id,
        "consumption_id": owner._consumption_id,
        "authorized_config_binding_digest": owner._authorized_config_binding_digest,
        "authorized_composite_prestate_digest": (
            owner._authorized_composite_prestate_digest
        ),
        "authorized_exposure_digest": owner._authorized_exposure_digest,
        "status": owner._status,
        "attempt_count": owner._attempt_count,
        "use_count": owner._use_count,
        "generation": owner._generation,
        "committed_result_digest": owner._committed_result_digest,
        "failure_code": owner._failure_code,
        "failure_digest": owner._failure_digest,
    }
    return TSPM1CoordinatorOwnerSnapshot(
        owner._owner_id,
        owner._authorization_id,
        owner._consumption_id,
        owner._authorized_config_binding_digest,
        owner._authorized_composite_prestate_digest,
        owner._authorized_exposure_digest,
        owner._status,
        owner._attempt_count,
        owner._use_count,
        owner._generation,
        owner._committed_result_digest,
        owner._failure_code,
        owner._failure_digest,
        _digest(values),
    )


@dataclass(frozen=True, slots=True)
class TSPM1StepResult:
    poststate: TSPM1CompositeState
    receipt: TSPM1TransitionReceipt
    owner_poststate: TSPM1CoordinatorOwnerSnapshot
    result_digest: str

    def __post_init__(self) -> None:
        if (
            type(self.poststate) is not TSPM1CompositeState
            or type(self.receipt) is not TSPM1TransitionReceipt
            or type(self.owner_poststate) is not TSPM1CoordinatorOwnerSnapshot
            or self.owner_poststate.status != "CONSUMED"
            or self.owner_poststate.committed_result_digest != self.result_digest
            or self.receipt.config_binding_digest
            != self.poststate.config_binding_digest
            or self.owner_poststate.authorized_config_binding_digest
            != self.receipt.config_binding_digest
            or self.owner_poststate.authorized_composite_prestate_digest
            != self.receipt.composite_prestate_digest
            or self.owner_poststate.authorized_exposure_digest
            != self.receipt.exposure_digest
            or self.receipt.composite_poststate_digest
            != self.poststate.composite_state_digest
            or self.result_digest != _digest(self.payload_without_digest())
        ):
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "step result is incomplete or digest inconsistent",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": TSPM1_SCHEMA_VERSION,
            "poststate_digest": self.poststate.composite_state_digest,
            "receipt_digest": self.receipt.receipt_digest,
            "owner_poststate_projection": self.owner_poststate.result_projection_payload(),
        }

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "result_digest": self.result_digest}


def _decision_digest(
    config: TSPM1ConfigBinding,
    prestate: TSPM1CompositeState,
    candidate: TSPM1FastTransitionCandidate,
    exposure: TSPM1BoundExposure,
    auditory_readout: PPB1Readout | None,
    visual_readout: PPB1Readout | None,
) -> str:
    return _digest(
        {
            "schema_version": TSPM1_SCHEMA_VERSION,
            "config_binding_digest": config.config_binding_digest,
            "composite_prestate_digest": prestate.composite_state_digest,
            "fast_candidate_digest": candidate.candidate_digest,
            "fast_candidate_poststate_digest": candidate.poststate.fast_state_digest,
            "exposure_digest": exposure.exposure_digest,
            "eligible": candidate.consolidation_eligible,
            "auditory_original_input_digest": (
                exposure.auditory_input_projection_digest
            ),
            "visual_original_input_digest": exposure.visual_input_projection_digest,
            "auditory_ppb1_readout_digest": (
                auditory_readout.digest() if auditory_readout is not None else None
            ),
            "visual_ppb1_readout_digest": (
                visual_readout.digest() if visual_readout is not None else None
            ),
        }
    )


def _make_receipt(
    config: TSPM1ConfigBinding,
    owner_prestate_digest: str,
    exposure: TSPM1BoundExposure,
    composite_prestate: TSPM1CompositeState,
    candidate: TSPM1FastTransitionCandidate,
    consolidation_status: str,
    decision_digest: str,
    auditory_readout: PPB1Readout | None,
    visual_readout: PPB1Readout | None,
    poststate: TSPM1CompositeState,
) -> TSPM1TransitionReceipt:
    values = {
        "schema_version": TSPM1_SCHEMA_VERSION,
        "config_binding_digest": config.config_binding_digest,
        "owner_authorization_prestate_digest": owner_prestate_digest,
        "exposure_digest": exposure.exposure_digest,
        "composite_prestate_digest": composite_prestate.composite_state_digest,
        "fast_candidate_digest": candidate.candidate_digest,
        "primary_event": candidate.primary_event,
        "partial_association_conflict": candidate.partial_association_conflict,
        "expired_slot_digests": list(candidate.expired_slot_digests),
        "replaced_slot_digest": candidate.replaced_slot_digest,
        "selected_slot_id": candidate.selected_slot_id,
        "consolidation_status": consolidation_status,
        "consolidation_decision_digest": decision_digest,
        "auditory_ppb1_readout_digest": (
            auditory_readout.digest() if auditory_readout is not None else None
        ),
        "visual_ppb1_readout_digest": (
            visual_readout.digest() if visual_readout is not None else None
        ),
        "auditory_ppb1_stabilized": (
            auditory_readout.stabilized if auditory_readout is not None else None
        ),
        "visual_ppb1_stabilized": (
            visual_readout.stabilized if visual_readout is not None else None
        ),
        "fast_poststate_digest": poststate.fast_state.fast_state_digest,
        "auditory_ppb1_poststate_digest": poststate.auditory_ppb1_state.digest(),
        "visual_ppb1_poststate_digest": poststate.visual_ppb1_state.digest(),
        "composite_poststate_digest": poststate.composite_state_digest,
    }
    return TSPM1TransitionReceipt(
        config.config_binding_digest,
        owner_prestate_digest,
        exposure.exposure_digest,
        composite_prestate.composite_state_digest,
        candidate.candidate_digest,
        candidate.primary_event,
        candidate.partial_association_conflict,
        candidate.expired_slot_digests,
        candidate.replaced_slot_digest,
        candidate.selected_slot_id,
        consolidation_status,
        decision_digest,
        values["auditory_ppb1_readout_digest"],  # type: ignore[arg-type]
        values["visual_ppb1_readout_digest"],  # type: ignore[arg-type]
        values["auditory_ppb1_stabilized"],  # type: ignore[arg-type]
        values["visual_ppb1_stabilized"],  # type: ignore[arg-type]
        poststate.fast_state.fast_state_digest,
        poststate.auditory_ppb1_state.digest(),
        poststate.visual_ppb1_state.digest(),
        poststate.composite_state_digest,
        _digest(values),
    )


def _validate_composite_transition(
    config: TSPM1ConfigBinding,
    prestate: TSPM1CompositeState,
    exposure: TSPM1BoundExposure,
    candidate: TSPM1FastTransitionCandidate,
    auditory_result: PPB1StepResult | None,
    visual_result: PPB1StepResult | None,
    poststate: object,
) -> TSPM1CompositeState:
    state = _validate_composite_state(config, poststate)
    if candidate.consolidation_eligible:
        if auditory_result is None or visual_result is None:
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "eligible composite transition requires both PPB-1 results",
            )
        expected_fast = _validate_fast_consolidation_relation(
            config,
            candidate,
            exposure,
            state.fast_state,
        )
        expected_auditory = auditory_result.poststate
        expected_visual = visual_result.poststate
    else:
        if auditory_result is not None or visual_result is not None:
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "ineligible composite transition cannot carry PPB-1 results",
            )
        expected_fast = candidate.poststate
        expected_auditory = prestate.auditory_ppb1_state
        expected_visual = prestate.visual_ppb1_state
        if (
            state.auditory_ppb1_state is not expected_auditory
            or state.visual_ppb1_state is not expected_visual
        ):
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "ineligible transition must retain both PPB-1 prestate objects",
            )
    expected = _make_composite_state(
        config,
        prestate.generation + 1,
        prestate.composite_state_digest,
        exposure.exposure_digest,
        expected_fast,
        expected_auditory,
        expected_visual,
    )
    if state != expected:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "composite poststate violates fast, PPB-1, or lineage relation",
        )
    return state


def _validate_receipt_relations(
    config: TSPM1ConfigBinding,
    owner_prestate_digest: str,
    exposure: TSPM1BoundExposure,
    composite_prestate: TSPM1CompositeState,
    candidate: TSPM1FastTransitionCandidate,
    consolidation_status: str,
    decision_digest: str,
    auditory_readout: PPB1Readout | None,
    visual_readout: PPB1Readout | None,
    poststate: TSPM1CompositeState,
    receipt: object,
) -> TSPM1TransitionReceipt:
    if type(receipt) is not TSPM1TransitionReceipt:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "exact TSPM-1 transition receipt is required",
        )
    expected_status = (
        "COMMITTED" if candidate.consolidation_eligible else "NOT_ELIGIBLE"
    )
    if consolidation_status != expected_status:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "receipt consolidation status does not match fast eligibility",
        )
    expected = _make_receipt(
        config,
        owner_prestate_digest,
        exposure,
        composite_prestate,
        candidate,
        consolidation_status,
        decision_digest,
        auditory_readout,
        visual_readout,
        poststate,
    )
    if receipt != expected:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "receipt does not match owner, source, candidate, and poststate",
        )
    return receipt


def _validate_step_result_relations(
    config: TSPM1ConfigBinding,
    prestate: TSPM1CompositeState,
    exposure: TSPM1BoundExposure,
    result: object,
) -> TSPM1StepResult:
    if type(result) is not TSPM1StepResult:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "exact TSPM-1 step result is required",
        )
    if (
        result.receipt.config_binding_digest != config.config_binding_digest
        or result.receipt.composite_prestate_digest
        != prestate.composite_state_digest
        or result.receipt.exposure_digest != exposure.exposure_digest
        or result.owner_poststate.authorized_config_binding_digest
        != config.config_binding_digest
        or result.owner_poststate.authorized_composite_prestate_digest
        != prestate.composite_state_digest
        or result.owner_poststate.authorized_exposure_digest
        != exposure.exposure_digest
        or result.receipt.composite_poststate_digest
        != result.poststate.composite_state_digest
    ):
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "step result does not match config, source, prestate, receipt, and owner",
        )
    return result


class TSPM1CoordinatorOwner:
    """Private authority for one terminal TSPM-1 exposure attempt."""

    def __init__(
        self,
        owner_id: str,
        authorization_id: str,
        consumption_id: str,
        authorized_config_binding_digest: str,
        authorized_composite_prestate_digest: str,
        authorized_exposure_digest: str,
    ) -> None:
        self._owner_id = _identifier(owner_id, "owner_id", TSPM1_INVALID_TYPE_OR_SCHEMA)
        self._authorization_id = _identifier(
            authorization_id,
            "authorization_id",
            TSPM1_INVALID_TYPE_OR_SCHEMA,
        )
        self._consumption_id = _identifier(
            consumption_id,
            "consumption_id",
            TSPM1_INVALID_TYPE_OR_SCHEMA,
        )
        digests = (
            authorized_config_binding_digest,
            authorized_composite_prestate_digest,
            authorized_exposure_digest,
        )
        if any(not _valid_digest(value) for value in digests):
            raise TSPM1Error(
                TSPM1_OWNER_AUTHORIZATION_MISMATCH,
                "owner authorization requires three digests",
            )
        self._authorized_config_binding_digest = authorized_config_binding_digest
        self._authorized_composite_prestate_digest = (
            authorized_composite_prestate_digest
        )
        self._authorized_exposure_digest = authorized_exposure_digest
        self._status = "AUTHORIZED"
        self._attempt_count = 0
        self._use_count = 0
        self._generation = 0
        self._committed_result_digest: str | None = None
        self._failure_code: str | None = None
        self._failure_digest: str | None = None
        self._lock = Lock()

    def snapshot(self) -> TSPM1CoordinatorOwnerSnapshot:
        with self._lock:
            return _snapshot(self)

    def consume_once(
        self,
        config: TSPM1ConfigBinding,
        prestate: TSPM1CompositeState,
        exposure: TSPM1BoundExposure,
    ) -> TSPM1StepResult:
        if not self._lock.acquire(blocking=False):
            raise TSPM1Error(TSPM1_OWNER_BUSY, "coordinator owner is busy")
        try:
            if self._status != "AUTHORIZED":
                raise TSPM1Error(
                    TSPM1_OWNER_TERMINAL,
                    f"coordinator owner is terminal: {self._status}",
                )
            owner_prestate_digest = _snapshot(self).owner_state_digest
            self._status = "IN_PROGRESS"
            self._attempt_count = 1
            try:
                if (
                    type(config) is not TSPM1ConfigBinding
                    or type(prestate) is not TSPM1CompositeState
                    or type(exposure) is not TSPM1BoundExposure
                ):
                    raise TSPM1Error(
                        TSPM1_INVALID_TYPE_OR_SCHEMA,
                        "consume_once requires exact config, prestate, and exposure types",
                    )
                binding = _validate_config(config)
                if (
                    binding.config_binding_digest
                    != self._authorized_config_binding_digest
                    or prestate.composite_state_digest
                    != self._authorized_composite_prestate_digest
                    or exposure.exposure_digest != self._authorized_exposure_digest
                ):
                    raise TSPM1Error(
                        TSPM1_OWNER_AUTHORIZATION_MISMATCH,
                        "owner authorization does not match call inputs",
                    )
                state = _validate_composite_state(binding, prestate)
                _validate_bound_source_provenance(binding, exposure)
                _validate_bound_source_geometry(binding, exposure)
                _validate_bound_source_time(
                    state.fast_state,
                    exposure,
                    strictly_later=True,
                )
                before = (
                    binding.config_binding_digest,
                    state.composite_state_digest,
                    exposure.exposure_digest,
                    exposure.auditory.timed_frame_provenance_digest,
                    exposure.visual.timed_frame_provenance_digest,
                )
                candidate = advance_tspm1_fast(
                    binding,
                    state.fast_state,
                    exposure,
                )
                candidate = _validate_fast_candidate_relations(
                    binding,
                    state.fast_state,
                    exposure,
                    candidate,
                )
                auditory_result = None
                visual_result = None
                if candidate.consolidation_eligible:
                    auditory_result = advance_ppb1_bank(
                        binding.profile.auditory_config,
                        state.auditory_ppb1_state,
                        exposure.auditory.timed_frame.frame,
                    )
                    visual_result = advance_ppb1_bank(
                        binding.profile.visual_config,
                        state.visual_ppb1_state,
                        exposure.visual.timed_frame.frame,
                    )
                    auditory_result = _validate_ppb1_step_result(
                        binding.profile.auditory_config,
                        state.auditory_ppb1_state,
                        exposure.auditory,
                        auditory_result,
                    )
                    visual_result = _validate_ppb1_step_result(
                        binding.profile.visual_config,
                        state.visual_ppb1_state,
                        exposure.visual,
                        visual_result,
                    )
                    fast_poststate = _commit_fast_consolidation(
                        binding,
                        candidate,
                        exposure,
                    )
                    fast_poststate = _validate_fast_consolidation_relation(
                        binding,
                        candidate,
                        exposure,
                        fast_poststate,
                    )
                    auditory_poststate = auditory_result.poststate
                    visual_poststate = visual_result.poststate
                    consolidation_status = "COMMITTED"
                else:
                    fast_poststate = candidate.poststate
                    auditory_poststate = state.auditory_ppb1_state
                    visual_poststate = state.visual_ppb1_state
                    consolidation_status = "NOT_ELIGIBLE"
                auditory_readout = (
                    auditory_result.readout if auditory_result is not None else None
                )
                visual_readout = (
                    visual_result.readout if visual_result is not None else None
                )
                decision_digest = _decision_digest(
                    binding,
                    state,
                    candidate,
                    exposure,
                    auditory_readout,
                    visual_readout,
                )
                poststate = _make_composite_state(
                    binding,
                    state.generation + 1,
                    state.composite_state_digest,
                    exposure.exposure_digest,
                    fast_poststate,
                    auditory_poststate,
                    visual_poststate,
                )
                poststate = _validate_composite_transition(
                    binding,
                    state,
                    exposure,
                    candidate,
                    auditory_result,
                    visual_result,
                    poststate,
                )
                receipt = _make_receipt(
                    binding,
                    owner_prestate_digest,
                    exposure,
                    state,
                    candidate,
                    consolidation_status,
                    decision_digest,
                    auditory_readout,
                    visual_readout,
                    poststate,
                )
                receipt = _validate_receipt_relations(
                    binding,
                    owner_prestate_digest,
                    exposure,
                    state,
                    candidate,
                    consolidation_status,
                    decision_digest,
                    auditory_readout,
                    visual_readout,
                    poststate,
                    receipt,
                )
                after = (
                    binding.config_binding_digest,
                    state.composite_state_digest,
                    exposure.exposure_digest,
                    exposure.auditory.timed_frame_provenance_digest,
                    exposure.visual.timed_frame_provenance_digest,
                )
                if before != after:
                    raise TSPM1Error(
                        TSPM1_ATOMIC_RESULT_REQUIRED,
                        "source or prestate changed during coordinator step",
                    )
                owner_projection = {
                    "schema_version": TSPM1_SCHEMA_VERSION,
                    "owner_id": self._owner_id,
                    "authorization_id": self._authorization_id,
                    "consumption_id": self._consumption_id,
                    "authorized_config_binding_digest": (
                        self._authorized_config_binding_digest
                    ),
                    "authorized_composite_prestate_digest": (
                        self._authorized_composite_prestate_digest
                    ),
                    "authorized_exposure_digest": self._authorized_exposure_digest,
                    "status": "CONSUMED",
                    "attempt_count": 1,
                    "use_count": 1,
                    "generation": 1,
                    "failure_code": None,
                    "failure_digest": None,
                }
                result_payload = {
                    "schema_version": TSPM1_SCHEMA_VERSION,
                    "poststate_digest": poststate.composite_state_digest,
                    "receipt_digest": receipt.receipt_digest,
                    "owner_poststate_projection": owner_projection,
                }
                result_digest = _digest(result_payload)
                self._status = "CONSUMED"
                self._use_count = 1
                self._generation = 1
                self._committed_result_digest = result_digest
                owner_poststate = _snapshot(self)
                result = TSPM1StepResult(
                    poststate,
                    receipt,
                    owner_poststate,
                    result_digest,
                )
                return _validate_step_result_relations(
                    binding,
                    state,
                    exposure,
                    result,
                )
            except Exception as exc:
                if self._status == "CONSUMED":
                    self._status = "IN_PROGRESS"
                    self._use_count = 0
                    self._committed_result_digest = None
                inner_code = getattr(exc, "code", TSPM1_ATOMIC_RESULT_REQUIRED)
                self._status = "FAILED"
                self._generation = 1
                self._failure_code = str(inner_code)
                self._failure_digest = _digest(
                    {
                        "schema_version": TSPM1_SCHEMA_VERSION,
                        "owner_id": self._owner_id,
                        "authorization_id": self._authorization_id,
                        "consumption_id": self._consumption_id,
                        "failure_code": self._failure_code,
                        "exception_type": type(exc).__name__,
                    }
                )
                raise TSPM1Error(
                    TSPM1_ATTEMPT_FAILED,
                    "TSPM-1 attempt failed without publishing a result",
                ) from exc
        finally:
            self._lock.release()


@dataclass(frozen=True, slots=True)
class TSPM1ReadOnlyFinding:
    config_binding_digest: str
    observed_composite_state_digest: str
    probe_digest: str
    fast_recognized: bool
    fast_slot_id: str | None
    fast_slot_digest: str | None
    auditory_fast_distance: float | None
    visual_fast_distance: float | None
    auditory_slow_status: str
    visual_slow_status: str
    auditory_s1wu_finding_digest: str | None
    visual_s1wu_finding_digest: str | None
    context_source: str
    finding_digest: str
    schema_version: str = TSPM1_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if (
            self.schema_version != TSPM1_SCHEMA_VERSION
            or not _valid_digest(self.config_binding_digest)
            or not _valid_digest(self.observed_composite_state_digest)
            or not _valid_digest(self.probe_digest)
            or not isinstance(self.fast_recognized, bool)
            or self.auditory_slow_status not in _SLOW_STATUSES
            or self.visual_slow_status not in _SLOW_STATUSES
            or self.context_source not in _CONTEXT_SOURCES
            or self.finding_digest != _digest(self.payload_without_digest())
        ):
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "read-only finding is incomplete or digest inconsistent",
            )
        if self.fast_recognized:
            _identifier(
                self.fast_slot_id,
                "fast_slot_id",
                TSPM1_ATOMIC_RESULT_REQUIRED,
            )
            if (
                not _valid_digest(self.fast_slot_digest)
                or self.auditory_fast_distance is None
                or self.visual_fast_distance is None
            ):
                raise TSPM1Error(
                    TSPM1_ATOMIC_RESULT_REQUIRED,
                    "recognized fast result requires slot and distances",
                )
            for distance in (
                self.auditory_fast_distance,
                self.visual_fast_distance,
            ):
                value = _finite(
                    distance,
                    "fast_distance",
                    TSPM1_ATOMIC_RESULT_REQUIRED,
                )
                if not 0.0 <= value <= 2.0:
                    raise TSPM1Error(
                        TSPM1_ATOMIC_RESULT_REQUIRED,
                        "fast distance out of range",
                    )
        elif any(
            value is not None
            for value in (
                self.fast_slot_id,
                self.fast_slot_digest,
                self.auditory_fast_distance,
                self.visual_fast_distance,
            )
        ):
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "negative fast result must be empty",
            )
        for status, digest_value in (
            (self.auditory_slow_status, self.auditory_s1wu_finding_digest),
            (self.visual_slow_status, self.visual_s1wu_finding_digest),
        ):
            if status == "SLOW_UNAVAILABLE":
                if digest_value is not None:
                    raise TSPM1Error(
                        TSPM1_ATOMIC_RESULT_REQUIRED,
                        "unavailable slow result cannot carry finding digest",
                    )
            elif not _valid_digest(digest_value):
                raise TSPM1Error(
                    TSPM1_ATOMIC_RESULT_REQUIRED,
                    "queried slow result requires finding digest",
                )
        both_slow_recognized = (
            self.auditory_slow_status == "SLOW_RECOGNIZED"
            and self.visual_slow_status == "SLOW_RECOGNIZED"
        )
        if (
            (self.context_source == "SLOW_PPB1_CONTEXT" and not both_slow_recognized)
            or (
                self.context_source == "FAST_ASSOCIATIVE_CONTEXT"
                and (both_slow_recognized or not self.fast_recognized)
            )
            or (
                self.context_source == "NO_COMPLETE_CONTEXT"
                and (both_slow_recognized or self.fast_recognized)
            )
        ):
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "context source does not follow fast and slow findings",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "config_binding_digest": self.config_binding_digest,
            "observed_composite_state_digest": self.observed_composite_state_digest,
            "probe_digest": self.probe_digest,
            "fast_recognized": self.fast_recognized,
            "fast_slot_id": self.fast_slot_id,
            "fast_slot_digest": self.fast_slot_digest,
            "auditory_fast_distance": self.auditory_fast_distance,
            "visual_fast_distance": self.visual_fast_distance,
            "auditory_slow_status": self.auditory_slow_status,
            "visual_slow_status": self.visual_slow_status,
            "auditory_s1wu_finding_digest": self.auditory_s1wu_finding_digest,
            "visual_s1wu_finding_digest": self.visual_s1wu_finding_digest,
            "context_source": self.context_source,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "finding_digest": self.finding_digest}


def _slow_probe(
    config,
    state: PPB1BankState,
    frame,
    probe_id: str,
    expected_input_digest: str,
) -> tuple[str, str | None]:
    if state.accepted_step_count == 0:
        return "SLOW_UNAVAILABLE", None
    finding = probe_s1wu_perceptual_state(config, state, frame, probe_id)
    if (
        type(finding) is not S1WUReadOnlyPerceptualFinding
        or finding.probe_id != probe_id
        or finding.bank_id != config.bank_id
        or finding.modality_id != config.modality_id
        or finding.bank_config_digest != config.digest()
        or finding.observed_bank_state_digest != state.digest()
        or finding.probe_input_digest != expected_input_digest
    ):
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "S1-WU finding does not match its probe source and bank",
        )
    return (
        "SLOW_RECOGNIZED" if finding.recognized else "SLOW_NOT_RECOGNIZED",
        finding.finding_digest,
    )


def _validate_read_only_finding_relations(
    config: TSPM1ConfigBinding,
    state: TSPM1CompositeState,
    probe: TSPM1BoundProbe,
    finding: object,
) -> TSPM1ReadOnlyFinding:
    if type(finding) is not TSPM1ReadOnlyFinding:
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "exact TSPM-1 read-only finding is required",
        )
    if (
        finding.config_binding_digest != config.config_binding_digest
        or finding.observed_composite_state_digest
        != state.composite_state_digest
        or finding.probe_digest != probe.probe_digest
        or (finding.auditory_slow_status == "SLOW_UNAVAILABLE")
        != (state.auditory_ppb1_state.accepted_step_count == 0)
        or (finding.visual_slow_status == "SLOW_UNAVAILABLE")
        != (state.visual_ppb1_state.accepted_step_count == 0)
    ):
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "read-only finding does not match config, state, probe, or slow availability",
        )
    auditory_values = tuple(probe.auditory.timed_frame.frame.values)
    visual_values = tuple(probe.visual.timed_frame.frame.values)
    matches = []
    for slot in state.fast_state.slots:
        if not slot.occupied:
            continue
        auditory_distance = normalized_mean_l1_distance(
            auditory_values,
            slot.auditory_values,
        )
        visual_distance = normalized_mean_l1_distance(
            visual_values,
            slot.visual_values,
        )
        if (
            auditory_distance <= config.fast_config.auditory_match_threshold
            and visual_distance <= config.fast_config.visual_match_threshold
        ):
            matches.append(
                (
                    max(auditory_distance, visual_distance),
                    auditory_distance + visual_distance,
                    slot.slot_id,
                    auditory_distance,
                    visual_distance,
                    slot.digest(),
                )
            )
    if matches:
        (
            _,
            _,
            expected_slot_id,
            expected_auditory_distance,
            expected_visual_distance,
            expected_slot_digest,
        ) = min(matches)
        expected_recognized = True
    else:
        expected_recognized = False
        expected_slot_id = None
        expected_slot_digest = None
        expected_auditory_distance = None
        expected_visual_distance = None
    if (
        finding.fast_recognized != expected_recognized
        or finding.fast_slot_id != expected_slot_id
        or finding.fast_slot_digest != expected_slot_digest
        or finding.auditory_fast_distance != expected_auditory_distance
        or finding.visual_fast_distance != expected_visual_distance
    ):
        raise TSPM1Error(
            TSPM1_ATOMIC_RESULT_REQUIRED,
            "read-only finding does not match the ranked fast result",
        )
    return finding


def probe_tspm1_read_only(
    config: TSPM1ConfigBinding,
    state: TSPM1CompositeState,
    probe: TSPM1BoundProbe,
) -> TSPM1ReadOnlyFinding:
    try:
        if (
            type(config) is not TSPM1ConfigBinding
            or type(state) is not TSPM1CompositeState
            or type(probe) is not TSPM1BoundProbe
        ):
            raise TSPM1Error(
                TSPM1_INVALID_TYPE_OR_SCHEMA,
                "read-only path requires exact config, state, and probe types",
            )
        binding = _validate_config(config)
        composite = _validate_composite_state(binding, state)
        _validate_bound_source_provenance(binding, probe)
        _validate_bound_source_geometry(binding, probe)
        _validate_bound_source_time(
            composite.fast_state,
            probe,
            strictly_later=True,
        )
        before = (
            composite.fast_state.fast_state_digest,
            composite.auditory_ppb1_state.digest(),
            composite.visual_ppb1_state.digest(),
            composite.composite_state_digest,
        )
        auditory_values = tuple(probe.auditory.timed_frame.frame.values)
        visual_values = tuple(probe.visual.timed_frame.frame.values)
        matches = []
        for slot in composite.fast_state.slots:
            if not slot.occupied:
                continue
            auditory_distance = normalized_mean_l1_distance(
                auditory_values,
                slot.auditory_values,
            )
            visual_distance = normalized_mean_l1_distance(
                visual_values,
                slot.visual_values,
            )
            if (
                auditory_distance <= binding.fast_config.auditory_match_threshold
                and visual_distance <= binding.fast_config.visual_match_threshold
            ):
                matches.append(
                    (
                        max(auditory_distance, visual_distance),
                        auditory_distance + visual_distance,
                        slot.slot_id,
                        auditory_distance,
                        visual_distance,
                        slot,
                    )
                )
        if matches:
            _, _, _, auditory_distance, visual_distance, fast_slot = min(matches)
            fast_recognized = True
            fast_slot_id = fast_slot.slot_id
            fast_slot_digest = fast_slot.digest()
        else:
            fast_recognized = False
            fast_slot_id = None
            fast_slot_digest = None
            auditory_distance = None
            visual_distance = None
        auditory_status, auditory_finding_digest = _slow_probe(
            binding.profile.auditory_config,
            composite.auditory_ppb1_state,
            probe.auditory.timed_frame.frame,
            f"tspm1.probe.auditory.{probe.probe_digest}",
            probe.auditory_input_projection_digest,
        )
        visual_status, visual_finding_digest = _slow_probe(
            binding.profile.visual_config,
            composite.visual_ppb1_state,
            probe.visual.timed_frame.frame,
            f"tspm1.probe.visual.{probe.probe_digest}",
            probe.visual_input_projection_digest,
        )
        if (
            auditory_status == "SLOW_RECOGNIZED"
            and visual_status == "SLOW_RECOGNIZED"
        ):
            context_source = "SLOW_PPB1_CONTEXT"
        elif fast_recognized:
            context_source = "FAST_ASSOCIATIVE_CONTEXT"
        else:
            context_source = "NO_COMPLETE_CONTEXT"
        after = (
            composite.fast_state.fast_state_digest,
            composite.auditory_ppb1_state.digest(),
            composite.visual_ppb1_state.digest(),
            composite.composite_state_digest,
        )
        if before != after:
            raise TSPM1Error(
                TSPM1_ATOMIC_RESULT_REQUIRED,
                "read-only probe changed source state",
            )
        values = {
            "schema_version": TSPM1_SCHEMA_VERSION,
            "config_binding_digest": binding.config_binding_digest,
            "observed_composite_state_digest": composite.composite_state_digest,
            "probe_digest": probe.probe_digest,
            "fast_recognized": fast_recognized,
            "fast_slot_id": fast_slot_id,
            "fast_slot_digest": fast_slot_digest,
            "auditory_fast_distance": auditory_distance,
            "visual_fast_distance": visual_distance,
            "auditory_slow_status": auditory_status,
            "visual_slow_status": visual_status,
            "auditory_s1wu_finding_digest": auditory_finding_digest,
            "visual_s1wu_finding_digest": visual_finding_digest,
            "context_source": context_source,
        }
        finding = TSPM1ReadOnlyFinding(
            binding.config_binding_digest,
            composite.composite_state_digest,
            probe.probe_digest,
            fast_recognized,
            fast_slot_id,
            fast_slot_digest,
            auditory_distance,
            visual_distance,
            auditory_status,
            visual_status,
            auditory_finding_digest,
            visual_finding_digest,
            context_source,
            _digest(values),
        )
        return _validate_read_only_finding_relations(
            binding,
            composite,
            probe,
            finding,
        )
    except TSPM1Error:
        raise
    except Exception as exc:
        raise TSPM1Error(
            TSPM1_READ_ONLY_REJECTED,
            "read-only TSPM-1 probe failed closed",
        ) from exc
