"""Private prospective RGB/PCM fixtures for S2-KK."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

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


S2KK_FIXTURE_SCHEMA = "s2kk.context-utility-fixture.v1"
S2KK_MASKED_SCHEMA = "s2kk.masked-visual-perception-336.v1"
S2KK_FAST_SEPARATION_SCHEMA = "s2kk.fast-separation-preflight.v1"
S2KK_CONTRACT_DIGEST = "edc532796e9dfd3c4bfa3c2702c0dc3bc02bfb91b32c81cf997264bd1911f2de"
FAST_AUDITORY_THRESHOLD = 0.2
FAST_VISUAL_THRESHOLD = 0.2
VISIBLE_POSITIONS = tuple(range(32))
MASKED_POSITIONS = tuple(range(32, 288))
FORMATION_SEQUENCE = (
    "T_PLUS",
    "T_PLUS",
    "T_MINUS",
    "T_MINUS",
    "T_MINUS",
    "T_MINUS",
    "T_MINUS",
    "T_MINUS",
    "D1",
    "D2",
    "D3",
    "D4",
    "D5",
    "D6",
    "D7",
    "D8",
    "D9",
)
FIXTURE_ROLES = ("T_PLUS", "T_MINUS", "H_FULL", "H_MASKED") + tuple(
    f"D{index}" for index in range(1, 10)
)
_DISTRACTOR_PERIODS = (400, 300, 240, 160, 120, 80, 60, 40, 30)
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2KKFixtureError(ValueError):
    """One prospective source or mask binding differs."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2KKFixtureError(message)


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


MASK_PLAN_DIGEST = _digest(
    {
        "schema": S2KK_MASKED_SCHEMA,
        "contract_digest": S2KK_CONTRACT_DIGEST,
        "dimension": 288,
        "visible_positions": list(VISIBLE_POSITIONS),
        "masked_positions": list(MASKED_POSITIONS),
        "occluder_byte": 0,
        "derivation": "INDEPENDENT_LITERAL_POSITION_MASK",
    }
)


@dataclass(frozen=True, slots=True)
class S2KKReducedAVFixtureV1:
    role: str
    block_index: int
    visual_payload_digest: str
    auditory_payload_digest: str
    visual_values_digest: str
    auditory_values_digest: str
    pairing_digest: str
    fixture_digest: str
    pair: S2JVBoundAVPairV1
    schema: str = S2KK_FIXTURE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "contract_digest": S2KK_CONTRACT_DIGEST,
            "role": self.role,
            "block_index": self.block_index,
            "visual_payload_digest": self.visual_payload_digest,
            "auditory_payload_digest": self.auditory_payload_digest,
            "visual_values_digest": self.visual_values_digest,
            "auditory_values_digest": self.auditory_values_digest,
            "pairing_digest": self.pairing_digest,
        }


@dataclass(frozen=True, slots=True)
class MaskedVisualPerception336V1:
    source_fixture_digest: str
    source_pairing_digest: str
    raw_visual_values_digest: str
    auditory_values_digest: str
    mask_plan_digest: str
    values: tuple[float | None, ...]
    visible_positions: tuple[int, ...]
    masked_positions: tuple[int, ...]
    probe_digest: str
    schema: str = S2KK_MASKED_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "contract_digest": S2KK_CONTRACT_DIGEST,
            "source_fixture_digest": self.source_fixture_digest,
            "source_pairing_digest": self.source_pairing_digest,
            "raw_visual_values_digest": self.raw_visual_values_digest,
            "auditory_values_digest": self.auditory_values_digest,
            "mask_plan_digest": self.mask_plan_digest,
            "values": list(self.values),
            "visible_positions": list(self.visible_positions),
            "masked_positions": list(self.masked_positions),
        }


@dataclass(frozen=True, slots=True)
class FastSeparationRelationV1:
    left_role: str
    right_role: str
    auditory_distance: float
    visual_distance: float
    native_fast_match: bool
    relation_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "left_role": self.left_role,
            "right_role": self.right_role,
            "auditory_distance": self.auditory_distance,
            "visual_distance": self.visual_distance,
            "native_fast_match": self.native_fast_match,
        }


@dataclass(frozen=True, slots=True)
class FastSeparationPreflightV1:
    relation_count: int
    anchor_relation_count: int
    distractor_pair_count: int
    native_fast_match_count: int
    relation_digests: tuple[str, ...]
    preflight_digest: str
    schema: str = S2KK_FAST_SEPARATION_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "contract_digest": S2KK_CONTRACT_DIGEST,
            "relation_count": self.relation_count,
            "anchor_relation_count": self.anchor_relation_count,
            "distractor_pair_count": self.distractor_pair_count,
            "native_fast_match_count": self.native_fast_match_count,
            "relation_digests": list(self.relation_digests),
        }


def _validate_fixture(value: object) -> S2KKReducedAVFixtureV1:
    _require(type(value) is S2KKReducedAVFixtureV1, "exact reduced AV fixture required")
    assert isinstance(value, S2KKReducedAVFixtureV1)
    _require(
        value.schema == S2KK_FIXTURE_SCHEMA
        and value.role in FIXTURE_ROLES
        and type(value.block_index) is int
        and value.block_index >= 0
        and type(value.pair) is S2JVBoundAVPairV1
        and value.pairing_digest == value.pair.pairing_digest
        and all(
            _valid_digest(item)
            for item in (
                value.visual_payload_digest,
                value.auditory_payload_digest,
                value.visual_values_digest,
                value.auditory_values_digest,
                value.pairing_digest,
                value.fixture_digest,
            )
        )
        and len(value.pair.auditory.timed_frame.frame.values) == 48
        and len(value.pair.visual.timed_frame.frame.values) == 288
        and value.auditory_values_digest
        == _digest(list(value.pair.auditory.timed_frame.frame.values))
        and value.visual_values_digest
        == _digest(list(value.pair.visual.timed_frame.frame.values))
        and value.fixture_digest == _digest(value.payload_without_digest()),
        "reduced AV fixture relation differs",
    )
    return value


def _validate_masked(value: object) -> MaskedVisualPerception336V1:
    _require(type(value) is MaskedVisualPerception336V1, "exact masked perception required")
    assert isinstance(value, MaskedVisualPerception336V1)
    _require(
        value.schema == S2KK_MASKED_SCHEMA
        and value.visible_positions == VISIBLE_POSITIONS
        and value.masked_positions == MASKED_POSITIONS
        and value.mask_plan_digest == MASK_PLAN_DIGEST
        and len(value.values) == 288
        and all(_valid_digest(item) for item in (
            value.source_fixture_digest,
            value.source_pairing_digest,
            value.raw_visual_values_digest,
            value.auditory_values_digest,
            value.probe_digest,
        ))
        and all(
            type(value.values[index]) in (int, float)
            and math.isfinite(float(value.values[index]))
            and 0.0 <= float(value.values[index]) <= 1.0
            for index in VISIBLE_POSITIONS
        )
        and all(value.values[index] is None for index in MASKED_POSITIONS)
        and value.probe_digest == _digest(value.payload_without_digest()),
        "masked perception relation differs",
    )
    return value


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    _require(len(left) == len(right) and bool(left), "distance dimensions differ")
    return sum(abs(a - b) for a, b in zip(left, right, strict=True)) / len(left)


def _fast_separated(auditory_distance: float, visual_distance: float) -> bool:
    _require(
        type(auditory_distance) in (int, float)
        and not isinstance(auditory_distance, bool)
        and type(visual_distance) in (int, float)
        and not isinstance(visual_distance, bool)
        and math.isfinite(float(auditory_distance))
        and math.isfinite(float(visual_distance))
        and auditory_distance >= 0.0
        and visual_distance >= 0.0,
        "Fast distances differ",
    )
    return not (
        auditory_distance <= FAST_AUDITORY_THRESHOLD
        and visual_distance <= FAST_VISUAL_THRESHOLD
    )


def validate_fast_separation_preflight(
    reduced: tuple[S2KKReducedAVFixtureV1, ...],
) -> FastSeparationPreflightV1:
    """Reject only an actual joint Fast match for the bound distractors."""

    _require(type(reduced) is tuple, "exact fixture tuple required")
    inventory: dict[str, S2KKReducedAVFixtureV1] = {}
    for item in reduced:
        item = _validate_fixture(item)
        if item.role != "H_MASKED" and item.role not in inventory:
            inventory[item.role] = item
    required = ("T_PLUS", "T_MINUS", "H_FULL") + tuple(f"D{index}" for index in range(1, 10))
    _require(tuple(role for role in required if role in inventory) == required, "Fast fixture inventory differs")

    def relation(left: S2KKReducedAVFixtureV1, right: S2KKReducedAVFixtureV1) -> FastSeparationRelationV1:
        left_a = tuple(left.pair.auditory.timed_frame.frame.values)
        left_v = tuple(left.pair.visual.timed_frame.frame.values)
        right_a = tuple(right.pair.auditory.timed_frame.frame.values)
        right_v = tuple(right.pair.visual.timed_frame.frame.values)
        auditory = _mean_l1(left_a, right_a)
        visual = _mean_l1(left_v, right_v)
        native_match = not _fast_separated(auditory, visual)
        payload = {
            "left_role": left.role,
            "right_role": right.role,
            "auditory_distance": auditory,
            "visual_distance": visual,
            "native_fast_match": native_match,
        }
        return FastSeparationRelationV1(
            left.role,
            right.role,
            auditory,
            visual,
            native_match,
            _digest(payload),
        )

    anchors = tuple(inventory[role] for role in ("T_PLUS", "T_MINUS", "H_FULL"))
    distractors = tuple(inventory[f"D{index}"] for index in range(1, 10))
    anchor_relations = tuple(relation(item, anchor) for item in distractors for anchor in anchors)
    pair_relations = tuple(
        relation(left, right)
        for left_index, left in enumerate(distractors)
        for right in distractors[left_index + 1 :]
    )
    relations = anchor_relations + pair_relations
    match_count = sum(item.native_fast_match for item in relations)
    _require(
        len(anchor_relations) == 27
        and len(pair_relations) == 36
        and len(relations) == 63
        and match_count == 0,
        "a distractor has a joint Fast match",
    )
    payload = {
        "schema": S2KK_FAST_SEPARATION_SCHEMA,
        "contract_digest": S2KK_CONTRACT_DIGEST,
        "relation_count": len(relations),
        "anchor_relation_count": len(anchor_relations),
        "distractor_pair_count": len(pair_relations),
        "native_fast_match_count": match_count,
        "relation_digests": [item.relation_digest for item in relations],
    }
    return FastSeparationPreflightV1(
        len(relations),
        len(anchor_relations),
        len(pair_relations),
        match_count,
        tuple(item.relation_digest for item in relations),
        _digest(payload),
    )


def _visual_grid(role: str) -> np.ndarray:
    _require(role in FIXTURE_ROLES, "unknown fixture role")
    flat = np.zeros(288, dtype=np.uint8)
    if role == "T_PLUS":
        flat[32:160] = 132
        flat[160:] = 130
    elif role == "T_MINUS":
        flat[32:160] = 132
        flat[160:] = 126
    elif role == "H_FULL":
        flat[32:] = 128
    elif role != "H_MASKED":
        ordinal = int(role[1:]) + 1
        for index in range(288):
            flat[index] = 255 if (index + ordinal) % 11 in {1, 3, 4, 5, 9} else 0
    return flat.reshape(8, 12, 3)


def _visual_image(role: str) -> np.ndarray:
    return np.repeat(np.repeat(_visual_grid(role), 135, axis=0), 160, axis=1)


def _audio_window(role: str) -> tuple[float, ...]:
    period = _DISTRACTOR_PERIODS[int(role[1:]) - 1] if role.startswith("D") else 960
    half = period // 2
    return tuple(0.5 if (index // half) % 2 == 0 else -0.5 for index in range(4800))


class S2KKFixtureStream:
    """Materialize one ordered source stream while retaining no raw payload."""

    def __init__(
        self,
        profile: S2JWDefaultLiveProfileV1,
        clock_id: str = "s2kk-default-live-clock",
    ) -> None:
        _require(type(profile) is S2JWDefaultLiveProfileV1, "exact default-live profile required")
        _require(isinstance(clock_id, str) and bool(clock_id), "clock id is required")
        self._profile = profile
        self._clock_id = clock_id
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self._next_block = 0

    def materialize(self, role: str, block_index: int) -> S2KKReducedAVFixtureV1:
        _require(role in FIXTURE_ROLES and block_index == self._next_block, "fixture order differs")
        image = _visual_image(role)
        window = _audio_window(role)
        visual_payload_digest = hashlib.sha256(image.tobytes(order="C")).hexdigest()
        auditory_payload_digest = hashlib.sha256(
            np.asarray(window, dtype="<f4").tobytes()
        ).hexdigest()
        auditory_state = None
        for hop_index in range(10):
            auditory_state = self._hearing.push(window[hop_index * 480 : (hop_index + 1) * 480])
        _require(
            auditory_state is not None
            and auditory_state.snapshot_index == block_index * 10
            and auditory_state.window_start_sample == block_index * 4800
            and auditory_state.window_end_sample == (block_index + 1) * 4800,
            "auditory source time differs",
        )
        visual_state = self._visual.analyze(image, frame_index=3 * block_index + 2)
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
            pair_id=f"s2kk-pair-{block_index:03d}",
            source_contract_id="s2kk-default-live-source",
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
            "schema": S2KK_FIXTURE_SCHEMA,
            "contract_digest": S2KK_CONTRACT_DIGEST,
            "role": role,
            "block_index": block_index,
            "visual_payload_digest": visual_payload_digest,
            "auditory_payload_digest": auditory_payload_digest,
            "visual_values_digest": _digest(list(visual_state.channel_values)),
            "auditory_values_digest": _digest(list(auditory_state.energy)),
            "pairing_digest": pair.pairing_digest,
        }
        self._next_block += 1
        return _validate_fixture(
            S2KKReducedAVFixtureV1(
                role,
                block_index,
                visual_payload_digest,
                auditory_payload_digest,
                payload["visual_values_digest"],
                payload["auditory_values_digest"],
                pair.pairing_digest,
                _digest(payload),
                pair,
            )
        )


def bind_masked_visual_perception(
    fixture: S2KKReducedAVFixtureV1,
    *,
    mask_plan_digest: str,
) -> MaskedVisualPerception336V1:
    fixture = _validate_fixture(fixture)
    _require(fixture.role == "H_MASKED", "masked source role differs")
    _require(mask_plan_digest == MASK_PLAN_DIGEST, "independent mask binding differs")
    raw = tuple(fixture.pair.visual.timed_frame.frame.values)
    values = tuple(raw[index] if index in VISIBLE_POSITIONS else None for index in range(288))
    payload = {
        "schema": S2KK_MASKED_SCHEMA,
        "contract_digest": S2KK_CONTRACT_DIGEST,
        "source_fixture_digest": fixture.fixture_digest,
        "source_pairing_digest": fixture.pairing_digest,
        "raw_visual_values_digest": fixture.visual_values_digest,
        "auditory_values_digest": fixture.auditory_values_digest,
        "mask_plan_digest": MASK_PLAN_DIGEST,
        "values": list(values),
        "visible_positions": list(VISIBLE_POSITIONS),
        "masked_positions": list(MASKED_POSITIONS),
    }
    return _validate_masked(
        MaskedVisualPerception336V1(
            fixture.fixture_digest,
            fixture.pairing_digest,
            fixture.visual_values_digest,
            fixture.auditory_values_digest,
            MASK_PLAN_DIGEST,
            values,
            VISIBLE_POSITIONS,
            MASKED_POSITIONS,
            _digest(payload),
        )
    )


__all__ = ()
