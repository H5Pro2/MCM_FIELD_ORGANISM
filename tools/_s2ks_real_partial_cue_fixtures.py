"""Private receptor-real fixtures for the bounded S2-KS partial-cue run."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import CommonFieldTime, from_auditory_receptor_state, from_visual_receptor_state
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools._s2jw_default_live_av_pairing import S2JVBoundAVPairV1, bind_s2jv_default_live_pair, build_s2jv_pairing_plan
from tools._s2jw_default_live_profile import S2JWDefaultLiveProfileV1
from tools._s2kq_private_partial_cue_retrieval_336 import MaskedMemoryCue336V1, build_masked_memory_cue_336, digest


S2KS_FIXTURE_SCHEMA = "s2ks.real-partial-cue-fixtures.v1"
VISIBLE_POSITIONS = tuple(range(32))
MASKED_POSITIONS = tuple(range(32, 288))
OCCLUDER_BYTE = 17

HISTORIES = {
    "h00": ("X", "X", "X", "X", "Y", "Y", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"),
    "h01": ("B0", "B0", "B0", "B0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "A0"),
    "h02": ("C0", "C1"),
    "h03": ("FC0", "FC1", "FU", "FV", "FU", "FV", "FU", "FV", "FU", "FV", "FT"),
    "h04": ("S0", "S0", "S0", "S0", "S1", "S1", "S1", "S1", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"),
}
FORMATION_COUNT = sum(len(sequence) for sequence in HISTORIES.values())
CASE_ORDER = ("K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8")
CASE_EXECUTION = {
    "K1": ("h00", "D9"),
    "K2": ("h00", "X"),
    "K3": ("h01", "A0"),
    "K4": ("h02", "C1"),
    "K5": ("h03", "FT"),
    "K6": ("h04", "S0"),
    "K7": ("null", "S0"),
    "K8": ("h00", "VISIBLE_MISMATCH"),
}

_ORDINALS = {"X": 0, "Y": 1, **{f"D{index}": index + 1 for index in range(1, 10)}}
_PERIODS = {
    "X": 960, "Y": 600, "D1": 400, "D2": 300, "D3": 240, "D4": 160,
    "D5": 120, "D6": 80, "D7": 60, "D8": 40, "D9": 30,
    "B0": 960, "A0": 960, "C0": 960, "C1": 960,
    "FC0": 960, "FC1": 960, "FU": 960, "FV": 960, "FT": 960,
    "S0": 960, "S1": 960,
}


class S2KSFixtureError(ValueError):
    """A source, time, mask, or receptor binding differs from S2-KS."""


def _bytes_digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _square_window(period: int) -> tuple[float, ...]:
    half = period // 2
    return tuple(0.5 if (index // half) % 2 == 0 else -0.5 for index in range(4800))


def _set_fraction(image: np.ndarray, carrier: int, numerator: int, denominator: int) -> None:
    row, remainder = divmod(carrier, 36)
    column, channel = divmod(remainder, 3)
    block = image[row * 135 : (row + 1) * 135, column * 160 : (column + 1) * 160, channel]
    scaled = 255 * numerator
    low, remainder = divmod(scaled, denominator)
    block.fill(low)
    if remainder:
        high_count = (block.size * remainder) // denominator
        block.flat[:high_count] = low + 1


def visual_image(recipe_id: str) -> np.ndarray:
    image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    if recipe_id in _ORDINALS:
        ordinal = _ORDINALS[recipe_id]
        for carrier in range(288):
            if (carrier + ordinal) % 11 in {1, 3, 4, 5, 9}:
                _set_fraction(image, carrier, 1, 1)
    elif recipe_id in {"A0", "C1"}:
        _set_fraction(image, 32, 1 if recipe_id == "A0" else 2, 255)
    elif recipe_id == "FC0":
        _set_fraction(image, 0, 3, 4)
    elif recipe_id == "FC1":
        _set_fraction(image, 0, 1, 4)
        _set_fraction(image, 32, 1, 1)
    elif recipe_id == "FU":
        _set_fraction(image, 0, 1, 1)
    elif recipe_id == "FV":
        _set_fraction(image, 0, 1, 4)
    elif recipe_id == "FT":
        _set_fraction(image, 0, 1, 2)
        _set_fraction(image, 32, 1, 1)
    elif recipe_id == "S1":
        for carrier in MASKED_POSITIONS:
            _set_fraction(image, carrier, 1, 1)
    elif recipe_id not in {"B0", "C0", "S0"}:
        raise S2KSFixtureError("unknown visual recipe")
    return image


def occluded_visual_image(visible_recipe_id: str) -> np.ndarray:
    """Create the observed source directly; no complete target frame is analyzed."""
    image = visual_image(visible_recipe_id if visible_recipe_id != "VISIBLE_MISMATCH" else "S0")
    if visible_recipe_id == "VISIBLE_MISMATCH":
        _set_fraction(image, 0, 1, 2)
    for carrier in MASKED_POSITIONS:
        _set_fraction(image, carrier, OCCLUDER_BYTE, 255)
    return image


@dataclass(frozen=True, slots=True)
class S2KSSourceReceiptV1:
    history_id: str
    source_id: str
    ordinal: int
    pairing_digest: str
    visual_payload_digest: str
    auditory_payload_digest: str
    visual_values_digest: str
    auditory_values_digest: str
    overlap_start_tick: int
    overlap_end_tick: int
    schema: str = S2KS_FIXTURE_SCHEMA


@dataclass(frozen=True, slots=True)
class S2KSMaskedSourceReceiptV1:
    history_id: str
    cue_id: str
    ordinal: int
    occluded_rgb_digest: str
    occluded_receptor_values_digest: str
    visible_values_digest: str
    mask_digest: str
    window_start_tick: int
    window_end_tick: int
    schema: str = S2KS_FIXTURE_SCHEMA


class S2KSFormationStream:
    def __init__(self, profile: S2JWDefaultLiveProfileV1, history_id: str) -> None:
        if type(profile) is not S2JWDefaultLiveProfileV1 or history_id not in HISTORIES:
            raise S2KSFixtureError("formation stream binding differs")
        self._profile = profile
        self._history_id = history_id
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self._next = 0

    @property
    def next_ordinal(self) -> int:
        return self._next

    def materialize(self, recipe_id: str) -> tuple[S2JVBoundAVPairV1, S2KSSourceReceiptV1]:
        if self._next >= len(HISTORIES[self._history_id]) or HISTORIES[self._history_id][self._next] != recipe_id:
            raise S2KSFixtureError("formation sequence differs")
        ordinal = self._next
        image = visual_image(recipe_id)
        window = _square_window(_PERIODS[recipe_id])
        auditory_state = None
        for hop in range(10):
            auditory_state = self._hearing.push(window[hop * 480 : (hop + 1) * 480])
        if auditory_state is None or auditory_state.snapshot_index != ordinal * 10:
            raise S2KSFixtureError("auditory stream endpoint differs")
        visual_state = self._visual.analyze(image, frame_index=ordinal * 3 + 2)
        clock_id = f"s2ks-{self._history_id}-clock"
        end_tick = 100_000_000 * (ordinal + 1)
        auditory = OrganismTimedReceptorFrame(from_auditory_receptor_state(auditory_state), CommonFieldTime(clock_id, end_tick - 10_000_000, end_tick))
        visual = OrganismTimedReceptorFrame(from_visual_receptor_state(visual_state), CommonFieldTime(clock_id, ((ordinal * 3 + 2) * 1_000_000_000) // 30, end_tick))
        visual_bytes = image.tobytes(order="C")
        auditory_bytes = np.asarray(window, dtype="<f4").tobytes()
        plan = build_s2jv_pairing_plan(
            pair_id=f"s2ks-{self._history_id}-pair-{ordinal:03d}",
            source_contract_id=f"s2ks-{self._history_id}-source",
            profile=self._profile,
            auditory=auditory,
            visual=visual,
            auditory_payload_digest=_bytes_digest(auditory_bytes),
            visual_payload_digest=_bytes_digest(visual_bytes),
        )
        pair = bind_s2jv_default_live_pair(pairing_plan=plan, profile=self._profile, auditory=auditory, visual=visual)
        receipt = S2KSSourceReceiptV1(
            self._history_id, f"src-{ordinal:03d}", ordinal, pair.pairing_digest,
            plan.visual_payload_digest, plan.auditory_payload_digest,
            plan.visual_values_digest, plan.auditory_values_digest,
            plan.overlap_start_tick, plan.overlap_end_tick,
        )
        self._next += 1
        return pair, receipt


def materialize_masked_cue(
    *, profile: S2JWDefaultLiveProfileV1, history_id: str, cue_id: str,
    ordinal: int, visible_recipe_id: str, config_digest: str,
) -> tuple[MaskedMemoryCue336V1, S2KSMaskedSourceReceiptV1]:
    if type(profile) is not S2JWDefaultLiveProfileV1 or type(ordinal) is not int or ordinal < 0:
        raise S2KSFixtureError("masked cue binding differs")
    image = occluded_visual_image(visible_recipe_id)
    state = LocalChannelGridReceptor(VisualGridConfig()).analyze(image, frame_index=ordinal * 3 + 2)
    receptor_values = tuple(state.channel_values)
    visible = tuple(receptor_values[index] for index in VISIBLE_POSITIONS)
    start_tick = 100_000_000 * ordinal
    end_tick = start_tick + 100_000_000
    source_digest = digest({
        "schema": S2KS_FIXTURE_SCHEMA,
        "history_id": history_id,
        "cue_id": cue_id,
        "ordinal": ordinal,
        "occluded_rgb_digest": _bytes_digest(image.tobytes(order="C")),
        "occluded_receptor_values_digest": digest(list(receptor_values)),
        "visible_values_digest": digest(list(visible)),
    })
    values = tuple(receptor_values[index] if index in VISIBLE_POSITIONS else None for index in range(288))
    cue = build_masked_memory_cue_336(
        source_digest=source_digest, config_digest=config_digest,
        field_clock_id=f"s2ks-{history_id}-clock",
        window_start_tick=start_tick, window_end_tick=end_tick, values=values,
    )
    receipt = S2KSMaskedSourceReceiptV1(
        history_id, cue_id, ordinal, _bytes_digest(image.tobytes(order="C")),
        digest(list(receptor_values)), digest(list(visible)), cue.mask_plan_digest,
        start_tick, end_tick,
    )
    return cue, receipt


def evaluation_target_masked_values(recipe_id: str) -> tuple[float, ...]:
    """Evaluation-only literal target; never passed to retrieval or its baseline."""
    image = visual_image(recipe_id)
    grid = image.reshape(8, 135, 12, 160, 3).mean(axis=(1, 3)) / 255.0
    values = tuple(float(value) for value in grid.reshape(-1))
    return tuple(values[index] for index in MASKED_POSITIONS)


assert tuple(len(HISTORIES[key]) for key in HISTORIES) == (15, 14, 2, 11, 17)
assert FORMATION_COUNT == 59
assert len(CASE_EXECUTION) == 8

__all__: tuple[str, ...] = ()
