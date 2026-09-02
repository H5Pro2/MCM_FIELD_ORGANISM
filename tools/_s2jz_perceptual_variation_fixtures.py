"""Real RGB/PCM fixtures for the private S2-JZ variation experiment."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import struct

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools._s2jw_default_live_av_pairing import (
    S2JVBoundAVPairV1,
    bind_s2jv_default_live_pair,
    build_s2jv_pairing_plan,
)
from tools._s2jw_default_live_profile import S2JWDefaultLiveProfileV1


S2JZ_FIXTURE_SCHEMA = "s2jz.perceptual-variation-fixtures.v1"
FIXTURE_ROLES = ("R0", "E0", "V1", "A1", "C1", "Z1")
REFERENCE_ROLE = "R0"
SOURCE_CONTRACT_ID = "s2jz-default-live-source"
FIELD_CLOCK_ID = "s2jz-default-live-clock"
A1_SAMPLE = struct.unpack("<f", struct.pack("<f", 0.495))[0]


class S2JZFixtureError(ValueError):
    """One generated fixture is not the prospectively bound source."""


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


_RECIPE = {
    "schema": S2JZ_FIXTURE_SCHEMA,
    "visual": {
        "shape": [1080, 1920, 3],
        "grid": [8, 12, 3],
        "base_active_residues": [1, 3, 4, 5, 9],
        "base_bytes": [0, 255],
        "variation_bytes": [2, 253],
        "distractor_ordinal": 2,
    },
    "auditory": {
        "sample_rate": 48000,
        "window_size": 4800,
        "hop_size": 480,
        "base_period": 960,
        "distractor_period": 400,
        "base_sample_hex": struct.pack("<f", 0.5).hex(),
        "variation_sample_hex": struct.pack("<f", A1_SAMPLE).hex(),
    },
    "roles": {
        "R0": ["base", "base"],
        "E0": ["base", "base"],
        "V1": ["variation", "base"],
        "A1": ["base", "variation"],
        "C1": ["variation", "variation"],
        "Z1": ["distractor", "distractor"],
    },
}
FIXTURE_RECIPE_DIGEST = _digest(_RECIPE)


@dataclass(frozen=True, slots=True)
class S2JZReducedFixtureV1:
    role: str
    block_index: int
    visual_payload_digest: str
    auditory_payload_digest: str
    visual_values_digest: str
    auditory_values_digest: str
    pairing_digest: str
    fixture_digest: str
    pair: S2JVBoundAVPairV1
    schema: str = S2JZ_FIXTURE_SCHEMA

    def __post_init__(self) -> None:
        payload = self.payload_without_digest()
        if (
            self.schema != S2JZ_FIXTURE_SCHEMA
            or self.role not in FIXTURE_ROLES
            or type(self.block_index) is not int
            or self.block_index < 0
            or type(self.pair) is not S2JVBoundAVPairV1
            or self.pairing_digest != self.pair.pairing_digest
            or self.fixture_digest != _digest(payload)
        ):
            raise S2JZFixtureError("reduced fixture binding differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "fixture_recipe_digest": FIXTURE_RECIPE_DIGEST,
            "role": self.role,
            "block_index": self.block_index,
            "visual_payload_digest": self.visual_payload_digest,
            "auditory_payload_digest": self.auditory_payload_digest,
            "visual_values_digest": self.visual_values_digest,
            "auditory_values_digest": self.auditory_values_digest,
            "pairing_digest": self.pairing_digest,
        }


def _visual_image(role: str) -> np.ndarray:
    grid = np.zeros((8, 12, 3), dtype=np.uint8)
    flat = grid.reshape(-1)
    ordinal = 2 if role == "Z1" else 0
    varied = role in {"V1", "C1"}
    for index in range(288):
        active = (index + ordinal) % 11 in {1, 3, 4, 5, 9}
        if varied:
            flat[index] = 253 if active else 2
        else:
            flat[index] = 255 if active else 0
    return np.repeat(np.repeat(grid, 135, axis=0), 160, axis=1)


def _audio_window(role: str) -> tuple[float, ...]:
    period = 400 if role == "Z1" else 960
    amplitude = A1_SAMPLE if role in {"A1", "C1"} else 0.5
    half = period // 2
    return tuple(
        amplitude if (index // half) % 2 == 0 else -amplitude
        for index in range(4800)
    )


class S2JZFixtureStream:
    """Create one ordered source stream and release raw payloads after reduction."""

    def __init__(self, profile: S2JWDefaultLiveProfileV1, clock_id: str = FIELD_CLOCK_ID) -> None:
        if type(profile) is not S2JWDefaultLiveProfileV1:
            raise S2JZFixtureError("exact default-live profile required")
        if not isinstance(clock_id, str) or not clock_id:
            raise S2JZFixtureError("clock_id is required")
        self._profile = profile
        self._clock_id = clock_id
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self._next_block = 0

    def materialize(self, role: str, block_index: int) -> S2JZReducedFixtureV1:
        if role not in FIXTURE_ROLES or block_index != self._next_block:
            raise S2JZFixtureError("fixture role or stream order differs")
        image = _visual_image(role)
        visual_bytes = image.tobytes(order="C")
        window = _audio_window(role)
        auditory_bytes = np.asarray(window, dtype="<f4").tobytes()
        visual_payload_digest = hashlib.sha256(visual_bytes).hexdigest()
        auditory_payload_digest = hashlib.sha256(auditory_bytes).hexdigest()

        auditory_state = None
        for hop_index in range(10):
            start = hop_index * 480
            auditory_state = self._hearing.push(window[start : start + 480])
        if auditory_state is None or auditory_state.snapshot_index != block_index * 10:
            raise S2JZFixtureError("auditory rolling endpoint differs")
        visual_state = self._visual.analyze(image, frame_index=3 * block_index + 2)
        auditory_values_digest = _digest(list(auditory_state.energy))
        visual_values_digest = _digest(list(visual_state.channel_values))

        auditory = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(auditory_state),
            CommonFieldTime(
                self._clock_id,
                100_000_000 * block_index + 90_000_000,
                100_000_000 * (block_index + 1),
            ),
        )
        visual = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual_state),
            CommonFieldTime(
                self._clock_id,
                ((3 * block_index + 2) * 1_000_000_000) // 30,
                100_000_000 * (block_index + 1),
            ),
        )
        plan = build_s2jv_pairing_plan(
            pair_id=f"s2jz-pair-{block_index:02d}",
            source_contract_id=SOURCE_CONTRACT_ID,
            profile=self._profile,
            auditory=auditory,
            visual=visual,
            auditory_payload_digest=auditory_payload_digest,
            visual_payload_digest=visual_payload_digest,
        )
        pair = bind_s2jv_default_live_pair(
            pairing_plan=plan,
            profile=self._profile,
            auditory=auditory,
            visual=visual,
        )
        payload = {
            "schema": S2JZ_FIXTURE_SCHEMA,
            "fixture_recipe_digest": FIXTURE_RECIPE_DIGEST,
            "role": role,
            "block_index": block_index,
            "visual_payload_digest": visual_payload_digest,
            "auditory_payload_digest": auditory_payload_digest,
            "visual_values_digest": visual_values_digest,
            "auditory_values_digest": auditory_values_digest,
            "pairing_digest": pair.pairing_digest,
        }
        self._next_block += 1
        return S2JZReducedFixtureV1(
            role,
            block_index,
            visual_payload_digest,
            auditory_payload_digest,
            visual_values_digest,
            auditory_values_digest,
            pair.pairing_digest,
            _digest(payload),
            pair,
        )

