"""Prospective PCM fixtures for the private S2-KC auditory holdout test."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import struct

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import CommonFieldTime, from_auditory_receptor_state, from_visual_receptor_state
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools._s2jw_default_live_av_pairing import S2JVBoundAVPairV1, bind_s2jv_default_live_pair, build_s2jv_pairing_plan
from tools._s2jw_default_live_profile import S2JWDefaultLiveProfileV1


S2KE_FIXTURE_SCHEMA = "s2ke.auditory-holdout-fixture.v1"
S2KE_PLAN_SCHEMA = "s2ke.auditory-pcm-plan.v1"
GEOMETRY_BLOCKED = "S2KC_AUDIO_GEOMETRY_NOT_MATERIALIZABLE"
TRAINING_ROLES = ("T_PLUS", "T_MINUS", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9")
HOLDOUT_ROLES = ("H_AUDIO", "N_AUDIO")
FIXTURE_ROLES = ("T_PLUS", "T_MINUS", "H_AUDIO", "N_AUDIO", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9")
FORMATION_SEQUENCE = ("T_PLUS", "T_PLUS") + ("T_MINUS",) * 6 + tuple(f"D{i}" for i in range(1, 10))
CHECKPOINTS = (("C0", 0), ("C1", 1), ("C2", 8), ("C3", 17))
SOURCE_CONTRACT_ID = "s2ke-default-live-source"
FIELD_CLOCK_ID = "s2ke-default-live-clock"
_DISTRACTOR_PERIODS = {"D1": 400, "D2": 300, "D3": 240, "D4": 160, "D5": 120, "D6": 80, "D7": 60, "D8": 40, "D9": 30}


class S2KEFixtureError(ValueError):
    """One fixed PCM source or its use differs from S2-KD."""


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _f32_hex(value: float) -> str:
    return struct.pack("<f", value).hex()


def _pcm_digest(values: tuple[float, ...]) -> str:
    return hashlib.sha256(np.asarray(values, dtype="<f4").tobytes()).hexdigest()


def _basis(frequency: int) -> tuple[float, ...]:
    return tuple(_f32(math.sin((2.0 * math.pi * frequency * index) / 48_000.0)) for index in range(4_800))


def _analyze_fresh(values: tuple[float, ...]) -> tuple[float, ...]:
    path = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
    state = None
    for hop in range(10):
        state = path.push(values[hop * 480 : (hop + 1) * 480])
    if state is None or state.snapshot_index != 0:
        raise S2KEFixtureError("basis receptor endpoint differs")
    return tuple(state.energy)


@dataclass(frozen=True, slots=True)
class S2KEPCMPlanV1:
    m_u: float
    m_v: float
    alpha_u: float
    alpha_hv: float
    alpha_bv: float
    alpha_plus_v: float
    alpha_minus_v: float
    u_pcm_digest: str
    v_pcm_digest: str
    u_values_digest: str
    v_values_digest: str
    overlap_channels: tuple[int, ...]
    overlap_l1_contribution: float
    sample_extrema: tuple[tuple[str, float, float], ...]
    samples_valid: bool
    first_invalid_sample: tuple[str, int] | None
    plan_digest: str
    schema: str = S2KE_PLAN_SCHEMA

    def __post_init__(self) -> None:
        if (
            self.schema != S2KE_PLAN_SCHEMA
            or self.plan_digest != _digest(self.payload_without_digest())
            or not all(math.isfinite(item) for item in (
                self.m_u, self.m_v, self.alpha_u, self.alpha_hv, self.alpha_bv,
                self.alpha_plus_v, self.alpha_minus_v, self.overlap_l1_contribution,
            ))
            or self.m_u <= 0.0
            or self.m_v <= 0.0
        ):
            raise S2KEFixtureError("PCM plan binding differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "m_u": self.m_u,
            "m_v": self.m_v,
            "alpha_u": self.alpha_u,
            "alpha_hv": self.alpha_hv,
            "alpha_bv": self.alpha_bv,
            "alpha_plus_v": self.alpha_plus_v,
            "alpha_minus_v": self.alpha_minus_v,
            "coefficient_f32_hex": [_f32_hex(item) for item in (self.alpha_u, self.alpha_hv, self.alpha_bv, self.alpha_plus_v, self.alpha_minus_v)],
            "u_pcm_digest": self.u_pcm_digest,
            "v_pcm_digest": self.v_pcm_digest,
            "u_values_digest": self.u_values_digest,
            "v_values_digest": self.v_values_digest,
            "overlap_channels": list(self.overlap_channels),
            "overlap_l1_contribution": self.overlap_l1_contribution,
            "sample_extrema": [list(item) for item in self.sample_extrema],
            "samples_valid": self.samples_valid,
            "first_invalid_sample": list(self.first_invalid_sample) if self.first_invalid_sample else None,
        }


class S2KEPCMMaterializer:
    """Derive exactly one coefficient set from exactly one U/V evaluation."""

    def __init__(self) -> None:
        self._consumed = False

    def derive_once(self) -> S2KEPCMPlanV1:
        if self._consumed:
            raise S2KEFixtureError("U/V materialization is single-use")
        self._consumed = True
        u = _basis(100)
        v = _basis(8_000)
        ru = _analyze_fresh(u)
        rv = _analyze_fresh(v)
        m_u = sum(abs(item) for item in ru) / 48.0
        m_v = sum(abs(item) for item in rv) / 48.0
        if not math.isfinite(m_u) or not math.isfinite(m_v) or m_u <= 0.0 or m_v <= 0.0:
            raise S2KEFixtureError("basis norm is not finite and positive")
        alpha_u = _f32((33.0 / 2000.0) / m_u)
        alpha_hv = _f32((1.0 / 100.0) / m_v)
        alpha_bv = _f32((1.0 / 200.0) / m_v)
        alpha_plus_v = _f32(alpha_hv + alpha_bv)
        alpha_minus_v = _f32(alpha_hv - alpha_bv)
        if not (alpha_u > 0.0 and alpha_hv > alpha_bv > 0.0 and alpha_plus_v > alpha_hv > alpha_minus_v > 0.0):
            raise S2KEFixtureError("coefficient ordering differs")
        windows = _central_windows(u, v, alpha_u, alpha_hv, alpha_plus_v, alpha_minus_v)
        extrema = []
        invalid = None
        for role, window in windows.items():
            extrema.append((role, min(window), max(window)))
            if invalid is None:
                invalid = next(((role, index) for index, sample in enumerate(window) if not math.isfinite(sample) or abs(sample) > 1.0), None)
        overlap = tuple(index for index, (left, right) in enumerate(zip(ru, rv, strict=True)) if left != 0.0 and right != 0.0)
        overlap_l1 = sum(min(abs(left), abs(right)) for left, right in zip(ru, rv, strict=True)) / 48.0
        payload = {
            "schema": S2KE_PLAN_SCHEMA,
            "m_u": m_u, "m_v": m_v,
            "alpha_u": alpha_u, "alpha_hv": alpha_hv, "alpha_bv": alpha_bv,
            "alpha_plus_v": alpha_plus_v, "alpha_minus_v": alpha_minus_v,
            "coefficient_f32_hex": [_f32_hex(item) for item in (alpha_u, alpha_hv, alpha_bv, alpha_plus_v, alpha_minus_v)],
            "u_pcm_digest": _pcm_digest(u), "v_pcm_digest": _pcm_digest(v),
            "u_values_digest": _digest(list(ru)), "v_values_digest": _digest(list(rv)),
            "overlap_channels": list(overlap), "overlap_l1_contribution": overlap_l1,
            "sample_extrema": [list(item) for item in extrema],
            "samples_valid": invalid is None,
            "first_invalid_sample": list(invalid) if invalid else None,
        }
        return S2KEPCMPlanV1(
            m_u, m_v, alpha_u, alpha_hv, alpha_bv, alpha_plus_v, alpha_minus_v,
            payload["u_pcm_digest"], payload["v_pcm_digest"], payload["u_values_digest"], payload["v_values_digest"],
            overlap, overlap_l1, tuple(extrema), invalid is None, invalid, _digest(payload),
        )


def _central_windows(
    u: tuple[float, ...], v: tuple[float, ...], alpha_u: float,
    alpha_hv: float, alpha_plus_v: float, alpha_minus_v: float,
) -> dict[str, tuple[float, ...]]:
    h, plus, minus = [], [], []
    for u_value, v_value in zip(u, v, strict=True):
        u_term = _f32(alpha_u * u_value)
        h_term = _f32(alpha_hv * v_value)
        plus_term = _f32(alpha_plus_v * v_value)
        minus_term = _f32(alpha_minus_v * v_value)
        h.append(h_term)
        plus.append(_f32(u_term + plus_term))
        minus.append(_f32(u_term + minus_term))
    return {"T_PLUS": tuple(plus), "T_MINUS": tuple(minus), "H_AUDIO": tuple(h), "N_AUDIO": (0.0,) * 4_800}


def _pcm_window(role: str, plan: S2KEPCMPlanV1) -> tuple[float, ...]:
    if type(plan) is not S2KEPCMPlanV1 or plan.plan_digest != _digest(plan.payload_without_digest()):
        raise S2KEFixtureError("PCM plan binding differs")
    if role in {"T_PLUS", "T_MINUS", "H_AUDIO", "N_AUDIO"}:
        windows = _central_windows(_basis(100), _basis(8_000), plan.alpha_u, plan.alpha_hv, plan.alpha_plus_v, plan.alpha_minus_v)
        return windows[role]
    period = _DISTRACTOR_PERIODS[role]
    half = period // 2
    return tuple(0.5 if (index // half) % 2 == 0 else -0.5 for index in range(4_800))


def _visual_image(role: str) -> np.ndarray:
    grid = np.zeros((8, 12, 3), dtype=np.uint8)
    flat = grid.reshape(-1)
    ordinal = int(role[1:]) + 1 if role.startswith("D") else 0
    for index in range(288):
        flat[index] = 255 if (index + ordinal) % 11 in {1, 3, 4, 5, 9} else 0
    return np.repeat(np.repeat(grid, 135, axis=0), 160, axis=1)


@dataclass(frozen=True, slots=True)
class S2KEReducedFixtureV1:
    role: str
    block_index: int
    visual_payload_digest: str
    auditory_payload_digest: str
    visual_values_digest: str
    auditory_values_digest: str
    pairing_digest: str
    fixture_digest: str
    pair: S2JVBoundAVPairV1
    schema: str = S2KE_FIXTURE_SCHEMA

    def __post_init__(self) -> None:
        if (
            self.schema != S2KE_FIXTURE_SCHEMA
            or self.role not in FIXTURE_ROLES
            or type(self.block_index) is not int
            or self.block_index < 0
            or self.fixture_digest != _digest(self.payload_without_digest())
            or self.pairing_digest != self.pair.pairing_digest
        ):
            raise S2KEFixtureError("reduced fixture binding differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {"schema": self.schema, "role": self.role, "block_index": self.block_index, "visual_payload_digest": self.visual_payload_digest, "auditory_payload_digest": self.auditory_payload_digest, "visual_values_digest": self.visual_values_digest, "auditory_values_digest": self.auditory_values_digest, "pairing_digest": self.pairing_digest}


class S2KEFixtureStream:
    def __init__(self, profile: S2JWDefaultLiveProfileV1, plan: S2KEPCMPlanV1, clock_id: str = FIELD_CLOCK_ID) -> None:
        if type(profile) is not S2JWDefaultLiveProfileV1 or type(plan) is not S2KEPCMPlanV1 or not plan.samples_valid:
            raise S2KEFixtureError("valid exact profile and PCM plan required")
        self._profile, self._plan, self._clock_id = profile, plan, clock_id
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self._next_block = 0

    def materialize(self, role: str, block_index: int) -> S2KEReducedFixtureV1:
        if role not in FIXTURE_ROLES or block_index != self._next_block:
            raise S2KEFixtureError("fixture role or order differs")
        image, window = _visual_image(role), _pcm_window(role, self._plan)
        if any(not math.isfinite(item) or abs(item) > 1.0 for item in window):
            raise S2KEFixtureError(GEOMETRY_BLOCKED)
        auditory_state = None
        for hop in range(10):
            auditory_state = self._hearing.push(window[hop * 480 : (hop + 1) * 480])
        if auditory_state is None or auditory_state.snapshot_index != block_index * 10:
            raise S2KEFixtureError("auditory endpoint differs")
        visual_state = self._visual.analyze(image, frame_index=3 * block_index + 2)
        visual_payload_digest = hashlib.sha256(image.tobytes(order="C")).hexdigest()
        auditory_payload_digest = _pcm_digest(window)
        auditory = OrganismTimedReceptorFrame(from_auditory_receptor_state(auditory_state), CommonFieldTime(self._clock_id, block_index * 100_000_000 + 90_000_000, (block_index + 1) * 100_000_000))
        visual = OrganismTimedReceptorFrame(from_visual_receptor_state(visual_state), CommonFieldTime(self._clock_id, ((3 * block_index + 2) * 1_000_000_000) // 30, (block_index + 1) * 100_000_000))
        pairing_plan = build_s2jv_pairing_plan(pair_id=f"s2ke-pair-{block_index:03d}", source_contract_id=SOURCE_CONTRACT_ID, profile=self._profile, auditory=auditory, visual=visual, auditory_payload_digest=auditory_payload_digest, visual_payload_digest=visual_payload_digest)
        pair = bind_s2jv_default_live_pair(pairing_plan=pairing_plan, profile=self._profile, auditory=auditory, visual=visual)
        payload = {"schema": S2KE_FIXTURE_SCHEMA, "role": role, "block_index": block_index, "visual_payload_digest": visual_payload_digest, "auditory_payload_digest": auditory_payload_digest, "visual_values_digest": _digest(list(visual_state.channel_values)), "auditory_values_digest": _digest(list(auditory_state.energy)), "pairing_digest": pair.pairing_digest}
        self._next_block += 1
        return S2KEReducedFixtureV1(role, block_index, visual_payload_digest, auditory_payload_digest, payload["visual_values_digest"], payload["auditory_values_digest"], pair.pairing_digest, _digest(payload), pair)


def assert_training_role(role: str) -> str:
    if role not in TRAINING_ROLES or role in HOLDOUT_ROLES:
        raise S2KEFixtureError("holdout or unknown role cannot enter training")
    return role
