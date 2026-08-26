"""Private source-bound single-prototype control for the active PPB-1 path."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from ._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorBatchEnvelope,
    PPB1ActiveReceptorStreamBinding,
)
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import PPB1BankConfig, normalized_mean_l1_distance


S2BD_BASELINE_SCHEMA_VERSION = "ppb1.s2bd.active-static-prototype-baseline.v1"
S2BD_BASELINE_INVALID_INPUT = "S2BD_BASELINE_INVALID_INPUT"
S2BD_BASELINE_SOURCE_MISMATCH = "S2BD_BASELINE_SOURCE_MISMATCH"
S2BD_BASELINE_SINGLE_PROTOTYPE_REQUIRED = (
    "S2BD_BASELINE_SINGLE_PROTOTYPE_REQUIRED"
)
S2BD_BASELINE_ATOMIC_RESULT_REQUIRED = "S2BD_BASELINE_ATOMIC_RESULT_REQUIRED"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2BDStaticPrototypeBaselineError(ValueError):
    """One fail-closed static-baseline contract violation."""

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
    return isinstance(value, str) and bool(_DIGEST.fullmatch(value))


def _bounded_values(values: object) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise S2BDStaticPrototypeBaselineError(
            S2BD_BASELINE_INVALID_INPUT,
            "prototype values must be numeric and iterable",
        ) from exc
    if (
        not result
        or any(not math.isfinite(value) or abs(value) > 1.0 for value in result)
    ):
        raise S2BDStaticPrototypeBaselineError(
            S2BD_BASELINE_INVALID_INPUT,
            "prototype values must be finite, non-empty and in [-1,1]",
        )
    return result


@dataclass(frozen=True, slots=True)
class S2BBStaticPrototypeState:
    modality_id: str
    geometry_id: str
    carrier_ids: tuple[str, ...]
    profile_binding_digest: str
    formation_envelope_digest: str
    ordered_formation_projection_digests: tuple[str, ...]
    prototype_values: tuple[float, ...]
    formation_frame_count: int
    state_digest: str
    schema_version: str = S2BD_BASELINE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        carriers = tuple(self.carrier_ids)
        projections = tuple(self.ordered_formation_projection_digests)
        values = _bounded_values(self.prototype_values)
        if (
            self.schema_version != S2BD_BASELINE_SCHEMA_VERSION
            or self.modality_id not in {"auditory", "visual"}
            or not isinstance(self.geometry_id, str)
            or not self.geometry_id
            or not carriers
            or len(set(carriers)) != len(carriers)
            or len(values) != len(carriers)
            or not projections
            or self.formation_frame_count != len(projections)
            or any(not _valid_digest(value) for value in projections)
            or not _valid_digest(self.profile_binding_digest)
            or not _valid_digest(self.formation_envelope_digest)
            or not _valid_digest(self.state_digest)
        ):
            raise S2BDStaticPrototypeBaselineError(
                S2BD_BASELINE_ATOMIC_RESULT_REQUIRED,
                "static prototype state is incomplete or invalid",
            )
        object.__setattr__(self, "carrier_ids", carriers)
        object.__setattr__(self, "ordered_formation_projection_digests", projections)
        object.__setattr__(self, "prototype_values", values)
        if self.state_digest != _digest(self.payload_without_digest()):
            raise S2BDStaticPrototypeBaselineError(
                S2BD_BASELINE_ATOMIC_RESULT_REQUIRED,
                "static prototype state digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "modality_id": self.modality_id,
            "geometry_id": self.geometry_id,
            "carrier_ids": list(self.carrier_ids),
            "profile_binding_digest": self.profile_binding_digest,
            "formation_envelope_digest": self.formation_envelope_digest,
            "ordered_formation_projection_digests": list(
                self.ordered_formation_projection_digests
            ),
            "prototype_values": list(self.prototype_values),
            "formation_frame_count": self.formation_frame_count,
        }

    def digest(self) -> str:
        return self.state_digest


@dataclass(frozen=True, slots=True)
class S2BBStaticPrototypeFormationReceipt:
    modality_id: str
    baseline_state_digest: str
    source_contract_digest: str
    source_batch_digest: str
    profile_binding_digest: str
    formation_envelope_digest: str
    ordered_formation_projection_digest: str
    used_vector_count: int
    used_scalar_count: int
    receipt_digest: str
    schema_version: str = S2BD_BASELINE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        digests = (
            self.baseline_state_digest,
            self.source_contract_digest,
            self.source_batch_digest,
            self.profile_binding_digest,
            self.formation_envelope_digest,
            self.ordered_formation_projection_digest,
            self.receipt_digest,
        )
        if (
            self.schema_version != S2BD_BASELINE_SCHEMA_VERSION
            or self.modality_id not in {"auditory", "visual"}
            or any(not _valid_digest(value) for value in digests)
            or isinstance(self.used_vector_count, bool)
            or self.used_vector_count <= 0
            or isinstance(self.used_scalar_count, bool)
            or self.used_scalar_count <= 0
            or self.receipt_digest != _digest(self.payload_without_digest())
        ):
            raise S2BDStaticPrototypeBaselineError(
                S2BD_BASELINE_ATOMIC_RESULT_REQUIRED,
                "baseline formation receipt is incomplete or invalid",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "modality_id": self.modality_id,
            "baseline_state_digest": self.baseline_state_digest,
            "source_contract_digest": self.source_contract_digest,
            "source_batch_digest": self.source_batch_digest,
            "profile_binding_digest": self.profile_binding_digest,
            "formation_envelope_digest": self.formation_envelope_digest,
            "ordered_formation_projection_digest": (
                self.ordered_formation_projection_digest
            ),
            "used_vector_count": self.used_vector_count,
            "used_scalar_count": self.used_scalar_count,
        }


@dataclass(frozen=True, slots=True)
class S2BBStaticPrototypeProbeFinding:
    modality_id: str
    baseline_state_digest: str
    probe_projection_digest: str
    match_distance: float
    recognized: bool
    postprobe_state_digest: str
    finding_digest: str
    schema_version: str = S2BD_BASELINE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        distance = float(self.match_distance)
        if (
            self.schema_version != S2BD_BASELINE_SCHEMA_VERSION
            or self.modality_id not in {"auditory", "visual"}
            or any(
                not _valid_digest(value)
                for value in (
                    self.baseline_state_digest,
                    self.probe_projection_digest,
                    self.postprobe_state_digest,
                    self.finding_digest,
                )
            )
            or not math.isfinite(distance)
            or distance < 0.0
            or distance > 2.0
            or not isinstance(self.recognized, bool)
            or self.postprobe_state_digest != self.baseline_state_digest
            or self.finding_digest != _digest(self.payload_without_digest())
        ):
            raise S2BDStaticPrototypeBaselineError(
                S2BD_BASELINE_ATOMIC_RESULT_REQUIRED,
                "baseline probe finding is incomplete or invalid",
            )
        object.__setattr__(self, "match_distance", distance)

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "modality_id": self.modality_id,
            "baseline_state_digest": self.baseline_state_digest,
            "probe_projection_digest": self.probe_projection_digest,
            "match_distance": self.match_distance,
            "recognized": self.recognized,
            "postprobe_state_digest": self.postprobe_state_digest,
        }


@dataclass(frozen=True, slots=True)
class S2BDBaselineFormationBundle:
    auditory_state: S2BBStaticPrototypeState
    visual_state: S2BBStaticPrototypeState
    auditory_receipt: S2BBStaticPrototypeFormationReceipt
    visual_receipt: S2BBStaticPrototypeFormationReceipt
    bundle_digest: str
    schema_version: str = S2BD_BASELINE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if (
            self.schema_version != S2BD_BASELINE_SCHEMA_VERSION
            or type(self.auditory_state) is not S2BBStaticPrototypeState
            or type(self.visual_state) is not S2BBStaticPrototypeState
            or type(self.auditory_receipt) is not S2BBStaticPrototypeFormationReceipt
            or type(self.visual_receipt) is not S2BBStaticPrototypeFormationReceipt
            or self.auditory_state.modality_id != "auditory"
            or self.visual_state.modality_id != "visual"
            or self.auditory_receipt.baseline_state_digest
            != self.auditory_state.digest()
            or self.visual_receipt.baseline_state_digest != self.visual_state.digest()
            or not _valid_digest(self.bundle_digest)
            or self.bundle_digest != _digest(self.payload_without_digest())
        ):
            raise S2BDStaticPrototypeBaselineError(
                S2BD_BASELINE_ATOMIC_RESULT_REQUIRED,
                "baseline formation bundle is incomplete or invalid",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "auditory_state_digest": self.auditory_state.digest(),
            "visual_state_digest": self.visual_state.digest(),
            "auditory_receipt_digest": self.auditory_receipt.receipt_digest,
            "visual_receipt_digest": self.visual_receipt.receipt_digest,
        }


def _form_modality(
    stream: PPB1ActiveReceptorStreamBinding,
    config: PPB1BankConfig,
    profile_digest: str,
    envelope: PPB1ActiveReceptorBatchEnvelope,
) -> tuple[S2BBStaticPrototypeState, S2BBStaticPrototypeFormationReceipt]:
    if (
        stream.modality_id != config.modality_id
        or stream.geometry_id != config.geometry_id
        or stream.carrier_ids != config.carrier_ids
        or stream.bank_config_digest != config.digest()
    ):
        raise S2BDStaticPrototypeBaselineError(
            S2BD_BASELINE_SOURCE_MISMATCH,
            "baseline stream and profile config do not match",
        )
    projections = tuple(
        item.ppb1_input_projection_digest for item in stream.timed_frames
    )
    prototype = _bounded_values(stream.timed_frames[0].timed_frame.frame.values)
    for item in stream.timed_frames[1:]:
        current = _bounded_values(item.timed_frame.frame.values)
        distance = normalized_mean_l1_distance(prototype, current)
        if distance > config.match_threshold:
            raise S2BDStaticPrototypeBaselineError(
                S2BD_BASELINE_SINGLE_PROTOTYPE_REQUIRED,
                "formation requires more than one static prototype",
            )
        prototype = tuple(
            (1.0 - config.update_rate) * previous
            + config.update_rate * current_value
            for previous, current_value in zip(prototype, current, strict=True)
        )
    state_values = {
        "modality_id": stream.modality_id,
        "geometry_id": stream.geometry_id,
        "carrier_ids": stream.carrier_ids,
        "profile_binding_digest": profile_digest,
        "formation_envelope_digest": envelope.envelope_digest,
        "ordered_formation_projection_digests": projections,
        "prototype_values": prototype,
        "formation_frame_count": stream.frame_count,
    }
    state = S2BBStaticPrototypeState(
        **state_values,
        state_digest=_digest(
            {"schema_version": S2BD_BASELINE_SCHEMA_VERSION, **state_values}
        ),
    )
    receipt_values = {
        "modality_id": stream.modality_id,
        "baseline_state_digest": state.digest(),
        "source_contract_digest": envelope.source_contract_digest,
        "source_batch_digest": envelope.source_batch_digest,
        "profile_binding_digest": profile_digest,
        "formation_envelope_digest": envelope.envelope_digest,
        "ordered_formation_projection_digest": _digest(list(projections)),
        "used_vector_count": stream.frame_count,
        "used_scalar_count": stream.frame_count * len(stream.carrier_ids),
    }
    receipt = S2BBStaticPrototypeFormationReceipt(
        **receipt_values,
        receipt_digest=_digest(
            {"schema_version": S2BD_BASELINE_SCHEMA_VERSION, **receipt_values}
        ),
    )
    return state, receipt


def form_s2bb_active_static_prototype_baseline(
    formation_envelope: PPB1ActiveReceptorBatchEnvelope,
    profile: PPB1ReceptorProfileBinding,
) -> S2BDBaselineFormationBundle:
    """Form two frozen baseline prototypes without candidate-state access."""

    if (
        type(formation_envelope) is not PPB1ActiveReceptorBatchEnvelope
        or type(profile) is not PPB1ReceptorProfileBinding
    ):
        raise S2BDStaticPrototypeBaselineError(
            S2BD_BASELINE_INVALID_INPUT,
            "exact active envelope and receptor profile types are required",
        )
    profile_digest = profile.digest()
    if (
        formation_envelope.profile_id != profile.profile_id
        or formation_envelope.profile_binding_digest != profile_digest
        or formation_envelope.parameter_digest != profile.parameter_digest
        or formation_envelope.auditory_stream.bank_config_digest
        != profile.auditory_config.digest()
        or formation_envelope.visual_stream.bank_config_digest
        != profile.visual_config.digest()
    ):
        raise S2BDStaticPrototypeBaselineError(
            S2BD_BASELINE_SOURCE_MISMATCH,
            "formation envelope and profile do not share one source",
        )
    before = (formation_envelope.envelope_digest, profile_digest)
    auditory_state, auditory_receipt = _form_modality(
        formation_envelope.auditory_stream,
        profile.auditory_config,
        profile_digest,
        formation_envelope,
    )
    visual_state, visual_receipt = _form_modality(
        formation_envelope.visual_stream,
        profile.visual_config,
        profile_digest,
        formation_envelope,
    )
    if before != (formation_envelope.envelope_digest, profile.digest()):
        raise S2BDStaticPrototypeBaselineError(
            S2BD_BASELINE_ATOMIC_RESULT_REQUIRED,
            "baseline inputs changed during formation",
        )
    values = {
        "auditory_state": auditory_state,
        "visual_state": visual_state,
        "auditory_receipt": auditory_receipt,
        "visual_receipt": visual_receipt,
    }
    payload = {
        "schema_version": S2BD_BASELINE_SCHEMA_VERSION,
        "auditory_state_digest": auditory_state.digest(),
        "visual_state_digest": visual_state.digest(),
        "auditory_receipt_digest": auditory_receipt.receipt_digest,
        "visual_receipt_digest": visual_receipt.receipt_digest,
    }
    return S2BDBaselineFormationBundle(**values, bundle_digest=_digest(payload))


def probe_s2bb_static_prototype_read_only(
    state: S2BBStaticPrototypeState,
    stream: PPB1ActiveReceptorStreamBinding,
    config: PPB1BankConfig,
) -> S2BBStaticPrototypeProbeFinding:
    """Probe one frozen baseline state without returning or changing state."""

    if (
        type(state) is not S2BBStaticPrototypeState
        or type(stream) is not PPB1ActiveReceptorStreamBinding
        or type(config) is not PPB1BankConfig
        or stream.frame_count != 1
        or stream.modality_id != state.modality_id
        or stream.modality_id != config.modality_id
        or stream.geometry_id != state.geometry_id
        or stream.geometry_id != config.geometry_id
        or stream.carrier_ids != state.carrier_ids
        or stream.carrier_ids != config.carrier_ids
        or stream.bank_config_digest != config.digest()
    ):
        raise S2BDStaticPrototypeBaselineError(
            S2BD_BASELINE_SOURCE_MISMATCH,
            "baseline state, probe stream and config do not match",
        )
    before = state.digest()
    item = stream.timed_frames[0]
    distance = normalized_mean_l1_distance(
        state.prototype_values,
        item.timed_frame.frame.values,
    )
    values = {
        "modality_id": state.modality_id,
        "baseline_state_digest": before,
        "probe_projection_digest": item.ppb1_input_projection_digest,
        "match_distance": distance,
        "recognized": distance <= config.match_threshold,
        "postprobe_state_digest": state.digest(),
    }
    if state.digest() != before:
        raise S2BDStaticPrototypeBaselineError(
            S2BD_BASELINE_ATOMIC_RESULT_REQUIRED,
            "baseline state changed during read-only probe",
        )
    return S2BBStaticPrototypeProbeFinding(
        **values,
        finding_digest=_digest(
            {"schema_version": S2BD_BASELINE_SCHEMA_VERSION, **values}
        ),
    )
