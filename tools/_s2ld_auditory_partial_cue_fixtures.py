"""Bound real receptor fixtures for the private S2-LD auditory run."""

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
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2jx_default_live_memory_fixtures as visual_fixtures
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as retrieval
from tools._s2jw_default_live_av_pairing import (
    S2JVBoundAVPairV1,
    bind_s2jv_default_live_pair,
    build_s2jv_pairing_plan,
)
from tools._s2jw_default_live_profile import S2JWDefaultLiveProfileV1


S2LD_FIXTURE_SCHEMA = "s2ld.auditory-partial-cue-fixtures.v1"
SOURCE_CONTRACT_ID = "s2ld-default-live-source"
HISTORIES = {
    "h-a": ("L",),
    "h-b": ("P",) * 4 + tuple(f"E{index}" for index in range(1, 10)),
    "h-ab": ("P",) * 4 + tuple(f"E{index}" for index in range(1, 10)) + ("L",),
    "h-ambig": ("P", "M"),
}
FORMATION_COUNT = sum(len(history) for history in HISTORIES.values())
CASE_ORDER = ("LC01", "LC02", "LC03", "LC04", "LC05", "LC06")
CASE_EXECUTION = {
    "LC01": ("h-a", "L"),
    "LC02": ("h-b", "L"),
    "LC03": ("h-b", "H"),
    "LC04": ("h-ab", "L"),
    "LC05": ("h-ambig", "L"),
    "LC06": ("h-null", "L"),
}

_AUDIO_ROLES = ("L", "P", "M", "H", "D_FAR")
_ROLE_TO_MEASUREMENT = {
    "L": "CUE_LOW",
    "P": "CANDIDATE_PLUS",
    "M": "CANDIDATE_MINUS",
    "H": "CANDIDATE_HIGH",
}
_EXPECTED_PCM_DIGESTS = {
    "L": "4adcbeccdcf900b606483908bc3dbd1e29c0658a904f333dffeff10456a7cd0e",
    "P": "14b8249af4a83c8363150d0fce188e0210e99da865ccad6c777144d43440a20f",
    "M": "1c443f41631219164279bb1b60ef696483d5d95faf8cc39c6422cfddc051b95b",
    "H": "e01a75a668a5317660943ff42f8770a0071570bb2d4b1ece879b0e146673b261",
    "D_FAR": "97a11dfcb89615b257d430ab718505b2ec207b8b8684c012ec5bdc6adcea4f5b",
}
_EXPECTED_VALUE_DIGESTS = {
    "L": "150033c23e54c561747fd029d2191319b93695bba6e626183ba853ef28b2b949",
    "P": "dc28fbb4ee22315131333a2c871ee82d958600d832a05c7d972db1e3acb4a023",
    "M": "b1415ce46e379d4750463d0fc4183ac968ab9e4cef18e369720534042d54211e",
    "H": "971e4e5a4a8f46293c42ec3cafe451eef81bb9c5171d2500358485bb5b08bb81",
    "D_FAR": "4cb2bf1dda6e02d9c5e482bfc749b3efe5910e46ea72e8195f376a67874774f0",
}


class S2LDFixtureError(ValueError):
    """One S2-LD source recipe or temporal binding differs."""


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _pcm_digest(values: tuple[float, ...]) -> str:
    return hashlib.sha256(np.asarray(values, dtype="<f4").tobytes()).hexdigest()


def _basis(frequency: int) -> tuple[float, ...]:
    return tuple(
        _f32(math.sin((2.0 * math.pi * frequency * index) / 48_000.0))
        for index in range(4_800)
    )


def _ky_pcm(role: str) -> tuple[float, ...]:
    if role not in _ROLE_TO_MEASUREMENT:
        raise S2LDFixtureError("unknown S2-KY auditory role")
    u = _basis(100)
    v = _basis(8_000)
    alpha_u = 0.49968934059143066
    alpha_hv = 0.37617719173431396
    alpha_plus_v = 0.564265787601471
    alpha_minus_v = 0.18808859586715698
    values: list[float] = []
    for u_value, v_value in zip(u, v, strict=True):
        u_term = _f32(alpha_u * u_value)
        high_term = _f32(alpha_hv * v_value)
        plus_term = _f32(alpha_plus_v * v_value)
        minus_term = _f32(alpha_minus_v * v_value)
        if role == "L":
            values.append(u_term)
        elif role == "P":
            values.append(_f32(u_term + plus_term))
        elif role == "M":
            values.append(_f32(u_term + minus_term))
        else:
            values.append(high_term)
    return tuple(values)


def _d_far_pcm() -> tuple[float, ...]:
    f0 = 50.0
    f1 = 890.0
    duration = 0.1
    ratio = f1 / f0
    phase_scale = 2.0 * math.pi * f0 * duration / math.log(ratio)
    initial_phase = math.pi / 7.0
    scale = _f32(0.9800000190734863)
    return tuple(
        _f32(
            scale
            if math.sin(
                initial_phase
                + phase_scale * (ratio ** ((index / 48_000.0) / duration) - 1.0)
            )
            >= 0.0
            else -scale
        )
        for index in range(4_800)
    )


def auditory_pcm(role: str) -> tuple[float, ...]:
    values = _d_far_pcm() if role == "D_FAR" else _ky_pcm(role)
    if (
        role not in _AUDIO_ROLES
        or len(values) != 4_800
        or any(not math.isfinite(value) or abs(value) > 1.0 for value in values)
        or _pcm_digest(values) != _EXPECTED_PCM_DIGESTS[role]
    ):
        raise S2LDFixtureError("auditory PCM recipe or digest differs")
    return values


def visual_image(role: str) -> np.ndarray:
    label = "X" if role in {"L", "P", "M"} else role.replace("E", "D", 1)
    if label not in visual_fixtures.FIXTURE_BY_LABEL:
        raise S2LDFixtureError("unknown visual companion role")
    spec = visual_fixtures.FIXTURE_BY_LABEL[label]
    image = visual_fixtures._visual_image(spec.ordinal)
    if hashlib.sha256(image.tobytes(order="C")).hexdigest() != spec.visual_payload_digest:
        raise S2LDFixtureError("visual source digest differs")
    return image


@dataclass(frozen=True, slots=True)
class S2LDFormationSourceReceiptV1:
    history_id: str
    source_id: str
    ordinal: int
    fixture_role: str
    pairing_digest: str
    visual_payload_digest: str
    auditory_payload_digest: str
    visual_values_digest: str
    auditory_values_digest: str
    auditory_source_clock_id: str
    auditory_window_start_tick: int
    auditory_window_end_tick: int
    receipt_digest: str
    schema: str = S2LD_FIXTURE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }


@dataclass(frozen=True, slots=True)
class S2LDCueSourceReceiptV1:
    history_id: str
    source_id: str
    ordinal: int
    cue_role: str
    pcm_payload_digest: str
    receptor_state_digest: str
    receptor_values_digest: str
    observed_values_digest: str
    auditory_source_clock_id: str
    auditory_window_start_tick: int
    auditory_window_end_tick: int
    cue_digest: str
    receipt_digest: str
    schema: str = S2LD_FIXTURE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }


class S2LDSourceStream:
    """Keep one native audio clock continuous for one independent history."""

    def __init__(self, profile: S2JWDefaultLiveProfileV1, history_id: str) -> None:
        if type(profile) is not S2JWDefaultLiveProfileV1 or history_id not in (*HISTORIES, "h-null", "h-neutral"):
            raise S2LDFixtureError("exact profile and bound history required")
        self._profile = profile
        self._history_id = history_id
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self._next_ordinal = 0
        self._field_clock_id = f"s2ld-{history_id}-field-clock"

    @property
    def next_ordinal(self) -> int:
        return self._next_ordinal

    def _analyze_audio(self, role: str):
        window = auditory_pcm(role)
        state = None
        for hop in range(10):
            state = self._hearing.push(window[hop * 480 : (hop + 1) * 480])
        if state is None or state.snapshot_index != self._next_ordinal * 10:
            raise S2LDFixtureError("auditory rolling endpoint differs")
        if _digest(list(state.energy)) != _EXPECTED_VALUE_DIGESTS[role]:
            raise S2LDFixtureError("auditory receptor values differ")
        return window, state

    def materialize_formation(self, role: str) -> tuple[S2JVBoundAVPairV1, S2LDFormationSourceReceiptV1]:
        history = HISTORIES.get(self._history_id)
        if (
            history is None
            or self._next_ordinal >= len(history)
            or role != history[self._next_ordinal]
            or role == "H"
        ):
            raise S2LDFixtureError("formation role is not bound to this history")
        ordinal = self._next_ordinal
        audio_role = "D_FAR" if role.startswith("E") else role
        window, auditory_state = self._analyze_audio(audio_role)
        image = visual_image(role)
        visual_state = self._visual.analyze(image, frame_index=3 * ordinal + 2)
        visual_label = "X" if role in {"L", "P", "M"} else role.replace("E", "D", 1)
        visual_spec = visual_fixtures.FIXTURE_BY_LABEL[visual_label]
        visual_values_digest = _digest(list(visual_state.channel_values))
        if visual_values_digest != visual_spec.visual_values_digest:
            raise S2LDFixtureError("visual receptor values differ")
        auditory = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(auditory_state),
            CommonFieldTime(self._field_clock_id, ordinal * 100_000_000 + 90_000_000, (ordinal + 1) * 100_000_000),
        )
        visual = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual_state),
            CommonFieldTime(self._field_clock_id, ((3 * ordinal + 2) * 1_000_000_000) // 30, (ordinal + 1) * 100_000_000),
        )
        source_id = f"s2ld-{self._history_id}-source-{ordinal + 1:03d}"
        plan = build_s2jv_pairing_plan(
            pair_id=f"s2ld-{self._history_id}-pair-{ordinal + 1:03d}",
            source_contract_id=SOURCE_CONTRACT_ID,
            profile=self._profile,
            auditory=auditory,
            visual=visual,
            auditory_payload_digest=_pcm_digest(window),
            visual_payload_digest=visual_spec.visual_payload_digest,
        )
        pair = bind_s2jv_default_live_pair(
            pairing_plan=plan,
            profile=self._profile,
            auditory=auditory,
            visual=visual,
        )
        payload = {
            "schema": S2LD_FIXTURE_SCHEMA,
            "history_id": self._history_id,
            "source_id": source_id,
            "ordinal": ordinal + 1,
            "fixture_role": role,
            "pairing_digest": pair.pairing_digest,
            "visual_payload_digest": visual_spec.visual_payload_digest,
            "auditory_payload_digest": _pcm_digest(window),
            "visual_values_digest": visual_values_digest,
            "auditory_values_digest": _digest(list(auditory_state.energy)),
            "auditory_source_clock_id": auditory.frame.clock_id,
            "auditory_window_start_tick": auditory.frame.window_start_tick,
            "auditory_window_end_tick": auditory.frame.window_end_tick,
        }
        receipt = S2LDFormationSourceReceiptV1(
            history_id=self._history_id,
            source_id=source_id,
            ordinal=ordinal + 1,
            fixture_role=role,
            pairing_digest=pair.pairing_digest,
            visual_payload_digest=visual_spec.visual_payload_digest,
            auditory_payload_digest=_pcm_digest(window),
            visual_values_digest=visual_values_digest,
            auditory_values_digest=_digest(list(auditory_state.energy)),
            auditory_source_clock_id=auditory.frame.clock_id,
            auditory_window_start_tick=auditory.frame.window_start_tick,
            auditory_window_end_tick=auditory.frame.window_end_tick,
            receipt_digest=_digest(payload),
        )
        if receipt.receipt_digest != _digest(receipt.payload_without_digest()):
            raise S2LDFixtureError("formation source receipt differs")
        self._next_ordinal += 1
        return pair, receipt

    def materialize_cue(
        self,
        *,
        cue_id: str,
        cue_role: str,
        config_digest: str,
        band_plan: retrieval.AuditoryBandPlan48V1,
    ) -> tuple[retrieval.MaskedAuditoryCue48V1, S2LDCueSourceReceiptV1]:
        if cue_role not in {"L", "H"}:
            raise S2LDFixtureError("cue role differs")
        ordinal = self._next_ordinal
        window, auditory_state = self._analyze_audio(cue_role)
        receptor_frame = from_auditory_receptor_state(auditory_state)
        cue = retrieval.build_masked_auditory_cue_48(
            pcm_payload_digest=_pcm_digest(window),
            receptor_state_digest=auditory_state.digest(),
            receptor_values_digest=_digest(list(auditory_state.energy)),
            config_digest=config_digest,
            auditory_source_clock_id=receptor_frame.clock_id,
            auditory_window_start_tick=receptor_frame.window_start_tick,
            auditory_window_end_tick=receptor_frame.window_end_tick,
            observed_values=tuple(auditory_state.energy[:24]),
            band_plan=band_plan,
        )
        payload = {
            "schema": S2LD_FIXTURE_SCHEMA,
            "history_id": self._history_id,
            "source_id": cue_id,
            "ordinal": ordinal + 1,
            "cue_role": cue_role,
            "pcm_payload_digest": _pcm_digest(window),
            "receptor_state_digest": auditory_state.digest(),
            "receptor_values_digest": _digest(list(auditory_state.energy)),
            "observed_values_digest": _digest(list(auditory_state.energy[:24])),
            "auditory_source_clock_id": receptor_frame.clock_id,
            "auditory_window_start_tick": receptor_frame.window_start_tick,
            "auditory_window_end_tick": receptor_frame.window_end_tick,
            "cue_digest": cue.cue_digest,
        }
        receipt = S2LDCueSourceReceiptV1(
            history_id=self._history_id,
            source_id=cue_id,
            ordinal=ordinal + 1,
            cue_role=cue_role,
            pcm_payload_digest=_pcm_digest(window),
            receptor_state_digest=auditory_state.digest(),
            receptor_values_digest=_digest(list(auditory_state.energy)),
            observed_values_digest=_digest(list(auditory_state.energy[:24])),
            auditory_source_clock_id=receptor_frame.clock_id,
            auditory_window_start_tick=receptor_frame.window_start_tick,
            auditory_window_end_tick=receptor_frame.window_end_tick,
            cue_digest=cue.cue_digest,
            receipt_digest=_digest(payload),
        )
        if receipt.receipt_digest != _digest(receipt.payload_without_digest()):
            raise S2LDFixtureError("cue source receipt differs")
        self._next_ordinal += 1
        return cue, receipt


__all__: tuple[str, ...] = ()
