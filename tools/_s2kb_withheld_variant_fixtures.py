"""Real source fixtures for the private S2-KB withheld-variant experiment."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

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


S2KB_FIXTURE_SCHEMA = "s2kb.withheld-variant-fixture.v1"
TRAINING_ROLES = ("T_PLUS", "T_MINUS", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9")
HOLDOUT_ROLES = ("H1", "N0")
FIXTURE_ROLES = ("T_PLUS", "T_MINUS", "H1", "N0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9")
FORMATION_SEQUENCE = (
    "T_PLUS", "T_PLUS",
    "T_MINUS", "T_MINUS", "T_MINUS", "T_MINUS", "T_MINUS", "T_MINUS",
    "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9",
)
CHECKPOINTS = (("C0", 0), ("C1", 1), ("C2", 8), ("C3", 17))
PROBE_ROLES = ("H1", "N0")
SOURCE_CONTRACT_ID = "s2kb-default-live-source"
FIELD_CLOCK_ID = "s2kb-default-live-clock"
_DISTRACTOR_PERIODS = {
    "D1": 400,
    "D2": 300,
    "D3": 240,
    "D4": 160,
    "D5": 120,
    "D6": 80,
    "D7": 60,
    "D8": 40,
    "D9": 30,
}


class S2KBFixtureError(ValueError):
    """One source fixture is malformed or used in the wrong role."""


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
    "schema": S2KB_FIXTURE_SCHEMA,
    "visual": {
        "shape": [1080, 1920, 3],
        "grid": [8, 12, 3],
        "split_ordinal": 144,
        "T_PLUS": [132, 130],
        "T_MINUS": [132, 126],
        "H1": [128, 128],
        "N0": [0, 0],
        "distractor_residues": [1, 3, 4, 5, 9],
        "distractor_ordinals": list(range(2, 11)),
    },
    "auditory": {
        "sample_rate": 48000,
        "window_size": 4800,
        "hop_size": 480,
        "positive_period": 960,
        "positive_amplitude": 0.5,
        "negative_kind": "zero",
        "distractor_periods": _DISTRACTOR_PERIODS,
    },
    "formation_sequence": list(FORMATION_SEQUENCE),
    "checkpoints": [list(item) for item in CHECKPOINTS],
    "probe_roles": list(PROBE_ROLES),
}
FIXTURE_RECIPE_DIGEST = _digest(_RECIPE)


@dataclass(frozen=True, slots=True)
class S2KBReducedFixtureV1:
    role: str
    block_index: int
    visual_payload_digest: str
    auditory_payload_digest: str
    visual_values_digest: str
    auditory_values_digest: str
    pairing_digest: str
    fixture_digest: str
    pair: S2JVBoundAVPairV1
    schema: str = S2KB_FIXTURE_SCHEMA

    def __post_init__(self) -> None:
        if (
            self.schema != S2KB_FIXTURE_SCHEMA
            or self.role not in FIXTURE_ROLES
            or type(self.block_index) is not int
            or self.block_index < 0
            or type(self.pair) is not S2JVBoundAVPairV1
            or self.pairing_digest != self.pair.pairing_digest
            or self.fixture_digest != _digest(self.payload_without_digest())
        ):
            raise S2KBFixtureError("reduced fixture binding differs")

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


def _visual_grid(role: str) -> np.ndarray:
    if role not in FIXTURE_ROLES:
        raise S2KBFixtureError("unknown fixture role")
    grid = np.zeros((8, 12, 3), dtype=np.uint8)
    flat = grid.reshape(-1)
    if role == "T_PLUS":
        flat[:144], flat[144:] = 132, 130
    elif role == "T_MINUS":
        flat[:144], flat[144:] = 132, 126
    elif role == "H1":
        flat[:] = 128
    elif role == "N0":
        flat[:] = 0
    else:
        ordinal = int(role[1:]) + 1
        for index in range(288):
            flat[index] = 255 if (index + ordinal) % 11 in {1, 3, 4, 5, 9} else 0
    return grid


def _visual_image(role: str) -> np.ndarray:
    return np.repeat(np.repeat(_visual_grid(role), 135, axis=0), 160, axis=1)


def _audio_window(role: str) -> tuple[float, ...]:
    if role == "N0":
        return (0.0,) * 4800
    period = _DISTRACTOR_PERIODS.get(role, 960)
    half = period // 2
    return tuple(0.5 if (index // half) % 2 == 0 else -0.5 for index in range(4800))


class S2KBFixtureStream:
    """Reduce one ordered raw stream and retain no RGB or PCM payload."""

    def __init__(self, profile: S2JWDefaultLiveProfileV1, clock_id: str = FIELD_CLOCK_ID) -> None:
        if type(profile) is not S2JWDefaultLiveProfileV1:
            raise S2KBFixtureError("exact default-live profile required")
        if not isinstance(clock_id, str) or not clock_id:
            raise S2KBFixtureError("clock_id is required")
        self._profile = profile
        self._clock_id = clock_id
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self._next_block = 0

    def materialize(self, role: str, block_index: int) -> S2KBReducedFixtureV1:
        if role not in FIXTURE_ROLES or block_index != self._next_block:
            raise S2KBFixtureError("fixture role or stream order differs")
        image = _visual_image(role)
        window = _audio_window(role)
        visual_payload_digest = hashlib.sha256(image.tobytes(order="C")).hexdigest()
        auditory_payload_digest = hashlib.sha256(np.asarray(window, dtype="<f4").tobytes()).hexdigest()

        auditory_state = None
        for hop_index in range(10):
            start = hop_index * 480
            auditory_state = self._hearing.push(window[start : start + 480])
        if auditory_state is None or auditory_state.snapshot_index != block_index * 10:
            raise S2KBFixtureError("auditory rolling endpoint differs")
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
            pair_id=f"s2kb-pair-{block_index:03d}",
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
            "schema": S2KB_FIXTURE_SCHEMA,
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
        return S2KBReducedFixtureV1(
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


def assert_training_role(role: str) -> str:
    if role not in TRAINING_ROLES or role in HOLDOUT_ROLES:
        raise S2KBFixtureError("holdout or unknown role cannot enter training")
    return role
