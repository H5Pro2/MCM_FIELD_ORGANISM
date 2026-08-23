"""Private PPB-1 bindings for existing reduced receptor geometries."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from ._ppb1_reference import PPB1BankConfig
from .broadband_hearing_path import BroadbandHearingPath
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor


PPB1_PROFILE_SCHEMA_VERSION = "ppb1.receptor-profiles.private.v1"
PPB1_PROFILE_IDS = (
    "browser",
    "controlled",
    "public-av",
    "default-live",
)

PPB1_INVALID_PROFILE = "PPB1_INVALID_PROFILE"
PPB1_PROFILE_PARAMETER_OUT_OF_RANGE = "PPB1_PROFILE_PARAMETER_OUT_OF_RANGE"
PPB1_PROFILE_BINDING_MISMATCH = "PPB1_PROFILE_BINDING_MISMATCH"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class PPB1ReceptorProfileError(ValueError):
    """One fail-closed PPB-1 receptor-profile contract violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _integer_in_range(
    value: object,
    role: str,
    minimum: int,
    maximum: int,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < minimum
        or value > maximum
    ):
        raise PPB1ReceptorProfileError(
            PPB1_PROFILE_PARAMETER_OUT_OF_RANGE,
            f"{role} must be an integer in [{minimum},{maximum}]",
        )
    return value


def _float_in_range(
    value: object,
    role: str,
    minimum: float,
    maximum: float,
) -> float:
    if isinstance(value, bool):
        raise PPB1ReceptorProfileError(
            PPB1_PROFILE_PARAMETER_OUT_OF_RANGE,
            f"{role} must be numeric",
        )
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise PPB1ReceptorProfileError(
            PPB1_PROFILE_PARAMETER_OUT_OF_RANGE,
            f"{role} must be numeric",
        ) from exc
    if not math.isfinite(result) or result < minimum or result > maximum:
        raise PPB1ReceptorProfileError(
            PPB1_PROFILE_PARAMETER_OUT_OF_RANGE,
            f"{role} must be finite and in [{minimum},{maximum}]",
        )
    return result


@dataclass(frozen=True, slots=True)
class PPB1ModalityParameters:
    capacity: int
    match_threshold: float
    update_rate: float
    stable_after: int
    expire_after_steps: int

    def canonical_payload(self) -> dict[str, object]:
        return {
            "capacity": self.capacity,
            "match_threshold": self.match_threshold,
            "update_rate": self.update_rate,
            "stable_after": self.stable_after,
            "expire_after_steps": self.expire_after_steps,
        }


@dataclass(frozen=True, slots=True)
class PPB1ProfileParameters:
    auditory: PPB1ModalityParameters
    visual: PPB1ModalityParameters

    def __post_init__(self) -> None:
        if not isinstance(self.auditory, PPB1ModalityParameters) or not isinstance(
            self.visual, PPB1ModalityParameters
        ):
            raise PPB1ReceptorProfileError(
                PPB1_PROFILE_PARAMETER_OUT_OF_RANGE,
                "auditory and visual parameter records are required",
            )
        auditory = PPB1ModalityParameters(
            _integer_in_range(self.auditory.capacity, "auditory.capacity", 8, 32),
            _float_in_range(
                self.auditory.match_threshold,
                "auditory.match_threshold",
                0.02,
                0.25,
            ),
            _float_in_range(
                self.auditory.update_rate, "auditory.update_rate", 0.05, 0.50
            ),
            _integer_in_range(
                self.auditory.stable_after, "auditory.stable_after", 3, 16
            ),
            _integer_in_range(
                self.auditory.expire_after_steps,
                "auditory.expire_after_steps",
                256,
                8192,
            ),
        )
        visual = PPB1ModalityParameters(
            _integer_in_range(self.visual.capacity, "visual.capacity", 4, 16),
            _float_in_range(
                self.visual.match_threshold,
                "visual.match_threshold",
                0.01,
                0.20,
            ),
            _float_in_range(
                self.visual.update_rate, "visual.update_rate", 0.05, 0.50
            ),
            _integer_in_range(
                self.visual.stable_after, "visual.stable_after", 3, 12
            ),
            _integer_in_range(
                self.visual.expire_after_steps,
                "visual.expire_after_steps",
                64,
                2048,
            ),
        )
        object.__setattr__(self, "auditory", auditory)
        object.__setattr__(self, "visual", visual)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "auditory": self.auditory.canonical_payload(),
            "visual": self.visual.canonical_payload(),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class PPB1ReceptorProfileBinding:
    profile_id: str
    auditory_config: PPB1BankConfig
    visual_config: PPB1BankConfig
    parameter_digest: str
    logical_prototype_value_limit: int
    packed_float64_bytes: int
    auditory_distance_term_limit: int
    visual_distance_term_limit: int
    schema_version: str = PPB1_PROFILE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != PPB1_PROFILE_SCHEMA_VERSION:
            raise PPB1ReceptorProfileError(
                PPB1_PROFILE_BINDING_MISMATCH,
                "profile schema version mismatch",
            )
        if self.profile_id not in PPB1_PROFILE_IDS:
            raise PPB1ReceptorProfileError(
                PPB1_INVALID_PROFILE, "unknown profile_id"
            )
        if (
            not isinstance(self.auditory_config, PPB1BankConfig)
            or self.auditory_config.modality_id != "auditory"
            or not isinstance(self.visual_config, PPB1BankConfig)
            or self.visual_config.modality_id != "visual"
        ):
            raise PPB1ReceptorProfileError(
                PPB1_PROFILE_BINDING_MISMATCH,
                "binding requires separate auditory and visual bank configs",
            )
        if not isinstance(self.parameter_digest, str) or not _DIGEST.fullmatch(
            self.parameter_digest
        ):
            raise PPB1ReceptorProfileError(
                PPB1_PROFILE_BINDING_MISMATCH,
                "parameter_digest must be SHA-256 hex",
            )
        expected_auditory_terms = (
            self.auditory_config.capacity * len(self.auditory_config.carrier_ids)
        )
        expected_visual_terms = (
            self.visual_config.capacity * len(self.visual_config.carrier_ids)
        )
        expected_values = expected_auditory_terms + expected_visual_terms
        if (
            self.auditory_distance_term_limit != expected_auditory_terms
            or self.visual_distance_term_limit != expected_visual_terms
            or self.logical_prototype_value_limit != expected_values
            or self.packed_float64_bytes != expected_values * 8
        ):
            raise PPB1ReceptorProfileError(
                PPB1_PROFILE_BINDING_MISMATCH,
                "binding resource limits do not match its configs",
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "profile_id": self.profile_id,
            "auditory_config": self.auditory_config.canonical_payload(),
            "visual_config": self.visual_config.canonical_payload(),
            "parameter_digest": self.parameter_digest,
            "logical_prototype_value_limit": self.logical_prototype_value_limit,
            "packed_float64_bytes": self.packed_float64_bytes,
            "auditory_distance_term_limit": self.auditory_distance_term_limit,
            "visual_distance_term_limit": self.visual_distance_term_limit,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _source_configs(
    profile_id: str,
) -> tuple[LogSpectralConfig, VisualGridConfig]:
    if profile_id == "browser":
        return (
            LogSpectralConfig(8000, 800, 80, 50.0, 3000.0, 8),
            VisualGridConfig(120, 80, 3, 2, 30.0),
        )
    if profile_id == "controlled":
        return (
            LogSpectralConfig(4000, 400, 40, 50.0, 1500.0, 12),
            VisualGridConfig(24, 16, 6, 4, 10.0),
        )
    if profile_id == "public-av":
        return (
            LogSpectralConfig(),
            VisualGridConfig(320, 240, 10, 8, 29.97),
        )
    if profile_id == "default-live":
        return LogSpectralConfig(), VisualGridConfig()
    raise PPB1ReceptorProfileError(
        PPB1_INVALID_PROFILE, f"unknown profile_id: {profile_id!r}"
    )


def bind_ppb1_receptor_profile(
    profile_id: str,
    parameters: PPB1ProfileParameters,
) -> PPB1ReceptorProfileBinding:
    if profile_id not in PPB1_PROFILE_IDS:
        raise PPB1ReceptorProfileError(
            PPB1_INVALID_PROFILE, f"unknown profile_id: {profile_id!r}"
        )
    if not isinstance(parameters, PPB1ProfileParameters):
        raise PPB1ReceptorProfileError(
            PPB1_PROFILE_PARAMETER_OUT_OF_RANGE,
            "PPB1ProfileParameters are required",
        )
    auditory_source, visual_source = _source_configs(profile_id)
    auditory_receptor = BroadbandHearingPath(
        LogSpectralReceptor(auditory_source)
    )
    visual_receptor = LocalChannelGridReceptor(visual_source)
    auditory = parameters.auditory
    visual = parameters.visual
    auditory_config = PPB1BankConfig(
        f"ppb1.auditory.{profile_id}.v1",
        "auditory",
        auditory_receptor.geometry_id,
        auditory_receptor.receptor.channel_ids,
        auditory.capacity,
        auditory.match_threshold,
        auditory.update_rate,
        auditory.stable_after,
        auditory.expire_after_steps,
    )
    visual_config = PPB1BankConfig(
        f"ppb1.visual.{profile_id}.v1",
        "visual",
        visual_receptor.config.geometry_id,
        visual_receptor.config.carrier_ids,
        visual.capacity,
        visual.match_threshold,
        visual.update_rate,
        visual.stable_after,
        visual.expire_after_steps,
    )
    auditory_terms = auditory.capacity * len(auditory_config.carrier_ids)
    visual_terms = visual.capacity * len(visual_config.carrier_ids)
    values = auditory_terms + visual_terms
    return PPB1ReceptorProfileBinding(
        profile_id,
        auditory_config,
        visual_config,
        parameters.digest(),
        values,
        values * 8,
        auditory_terms,
        visual_terms,
    )
