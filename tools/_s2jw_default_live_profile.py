"""Private default-live profile binding for the S2-JW memory adapters."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    PPB1ReceptorProfileBinding,
    bind_ppb1_receptor_profile,
)


S2JW_PROFILE_SCHEMA = "s2jw.default-live-profile.v1"
S2JV_SOURCE_PROFILE_SCHEMA = "s2jv.default-live-source-profile.v1"

EXPECTED_PARAMETER_DIGEST = "b3cfa693d7cc10ae0795946c0c6c1473e6535005ca84b388dc73a392cbab42e1"
EXPECTED_AUDITORY_CONFIG_DIGEST = "3852b41b0bed61862abcccbcf7c5839c73d246391966d97c8dd088ba71723252"
EXPECTED_VISUAL_CONFIG_DIGEST = "fe8b06bad66204dec3e7c80cb24bb73d740544eba23af9a8c9e1da3d3c5d9fec"
EXPECTED_PROFILE_BINDING_DIGEST = "27a87f2beb3b498e3fd7eac3f0977ef585163e9abb4cda48fc1a53ab7081fd86"
EXPECTED_FAST_CONFIG_DIGEST = "32640b5bb40e9bcfe4735748b3dcbab659680212a515384e432ddbef776aa19e"
EXPECTED_TSPM_CONFIG_DIGEST = "3611e0a8dfad395b496bc5d653f7c73c80de09f375e3ad4568b5d4f3e4a7f456"
EXPECTED_SOURCE_PROFILE_DIGEST = "fa6bc21e216068e6d2d02ab016d083d7456819c4505db4db8161b8ec03e5f0f5"

AUDITORY_DIMENSION = 48
VISUAL_DIMENSION = 288
AV_DIMENSION = 336
B4_CAPACITY = 9


class S2JWProfileError(ValueError):
    """The bound default-live profile differs from S2-JV."""


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _source_profile_payload() -> dict[str, object]:
    return {
        "schema": S2JV_SOURCE_PROFILE_SCHEMA,
        "profile_id": "default-live",
        "visual_config": {
            "source_width": 1920,
            "source_height": 1080,
            "grid_columns": 12,
            "grid_rows": 8,
            "frames_per_second": 30.0,
            "carrier_order": "grid_row-grid_column-rgb_channel",
        },
        "auditory_config": {
            "sample_rate": 48000,
            "window_size": 4800,
            "hop_size": 480,
            "min_frequency": 50.0,
            "max_frequency": 18000.0,
            "band_count": 48,
        },
        "ppb_parameter_digest": EXPECTED_PARAMETER_DIGEST,
        "ppb_profile_binding_digest": EXPECTED_PROFILE_BINDING_DIGEST,
        "tspm_fast_config_digest": EXPECTED_FAST_CONFIG_DIGEST,
        "tspm_config_binding_digest": EXPECTED_TSPM_CONFIG_DIGEST,
    }


@dataclass(frozen=True, slots=True)
class S2JWDefaultLiveProfileV1:
    profile: PPB1ReceptorProfileBinding
    tspm_config: tspm1.TSPM1ConfigBinding
    auditory_dimension: int
    visual_dimension: int
    av_dimension: int
    b4_capacity: int
    source_profile_digest: str
    binding_digest: str
    schema: str = S2JW_PROFILE_SCHEMA

    def __post_init__(self) -> None:
        if (
            self.schema != S2JW_PROFILE_SCHEMA
            or type(self.profile) is not PPB1ReceptorProfileBinding
            or type(self.tspm_config) is not tspm1.TSPM1ConfigBinding
            or self.profile.profile_id != "default-live"
            or self.auditory_dimension != len(self.profile.auditory_config.carrier_ids)
            or self.visual_dimension != len(self.profile.visual_config.carrier_ids)
            or self.av_dimension != self.auditory_dimension + self.visual_dimension
            or (self.auditory_dimension, self.visual_dimension, self.av_dimension)
            != (AUDITORY_DIMENSION, VISUAL_DIMENSION, AV_DIMENSION)
            or self.b4_capacity != B4_CAPACITY
            or self.source_profile_digest != EXPECTED_SOURCE_PROFILE_DIGEST
            or self.binding_digest != _digest(self.payload_without_digest())
        ):
            raise S2JWProfileError("default-live profile binding differs from S2-JV")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "profile_binding_digest": self.profile.digest(),
            "tspm_config_binding_digest": self.tspm_config.config_binding_digest,
            "auditory_dimension": self.auditory_dimension,
            "visual_dimension": self.visual_dimension,
            "av_dimension": self.av_dimension,
            "b4_capacity": self.b4_capacity,
            "source_profile_digest": self.source_profile_digest,
        }


def build_s2jw_default_live_profile() -> S2JWDefaultLiveProfileV1:
    parameters = PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )
    profile = bind_ppb1_receptor_profile("default-live", parameters)
    fast = tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8)
    tspm_config = tspm1.TSPM1ConfigBinding.build(fast, profile)
    actual = (
        parameters.digest(),
        profile.auditory_config.digest(),
        profile.visual_config.digest(),
        profile.digest(),
        fast.digest(),
        tspm_config.config_binding_digest,
        _digest(_source_profile_payload()),
    )
    expected = (
        EXPECTED_PARAMETER_DIGEST,
        EXPECTED_AUDITORY_CONFIG_DIGEST,
        EXPECTED_VISUAL_CONFIG_DIGEST,
        EXPECTED_PROFILE_BINDING_DIGEST,
        EXPECTED_FAST_CONFIG_DIGEST,
        EXPECTED_TSPM_CONFIG_DIGEST,
        EXPECTED_SOURCE_PROFILE_DIGEST,
    )
    if actual != expected:
        raise S2JWProfileError("default-live source or memory digest changed")
    payload = {
        "schema": S2JW_PROFILE_SCHEMA,
        "profile_binding_digest": profile.digest(),
        "tspm_config_binding_digest": tspm_config.config_binding_digest,
        "auditory_dimension": len(profile.auditory_config.carrier_ids),
        "visual_dimension": len(profile.visual_config.carrier_ids),
        "av_dimension": len(profile.auditory_config.carrier_ids)
        + len(profile.visual_config.carrier_ids),
        "b4_capacity": B4_CAPACITY,
        "source_profile_digest": EXPECTED_SOURCE_PROFILE_DIGEST,
    }
    return S2JWDefaultLiveProfileV1(
        profile,
        tspm_config,
        payload["auditory_dimension"],  # type: ignore[arg-type]
        payload["visual_dimension"],  # type: ignore[arg-type]
        payload["av_dimension"],  # type: ignore[arg-type]
        B4_CAPACITY,
        EXPECTED_SOURCE_PROFILE_DIGEST,
        _digest(payload),
    )
