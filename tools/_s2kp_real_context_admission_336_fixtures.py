"""Private receptor-real fixtures for the bounded S2-KP admission run."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

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


S2KP_FIXTURE_SCHEMA = "s2kp.real-context-admission-336-fixtures.v1"
S2JX_HISTORY = (
    "X", "X", "X", "X", "Y", "Y", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"
)
AMBIGUOUS_HISTORY = (
    "B0", "B0", "B0", "B0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "A0"
)
INTERNAL_CONFLICT_HISTORY = ("C0", "C1")
HISTORIES = {
    "h00": S2JX_HISTORY,
    "h01": AMBIGUOUS_HISTORY,
    "h02": INTERNAL_CONFLICT_HISTORY,
}
CASE_ORDER = ("R1", "R2", "R3", "R4", "R5", "R6")
FORMATION_COUNT = sum(len(value) for value in HISTORIES.values())
FULL_PROBE_COUNT = 5
MASKED_PROBE_COUNT = 6
VISIBLE_POSITIONS = tuple(range(32))
MASKED_POSITIONS = tuple(range(32, 288))

_ORDINALS = {
    "X": 0,
    "Y": 1,
    "D1": 2,
    "D2": 3,
    "D3": 4,
    "D4": 5,
    "D5": 6,
    "D6": 7,
    "D7": 8,
    "D8": 9,
    "D9": 10,
}
_PERIODS = {
    "X": 960,
    "Y": 600,
    "D1": 400,
    "D2": 300,
    "D3": 240,
    "D4": 160,
    "D5": 120,
    "D6": 80,
    "D7": 60,
    "D8": 40,
    "D9": 30,
    "B0": 960,
    "A0": 960,
    "C0": 960,
    "C1": 960,
    "D9_VISIBLE_MISMATCH": 30,
}


class S2KPFixtureError(ValueError):
    """A raw fixture, receptor value, or source-time relation is invalid."""


def _digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _square_window(period: int) -> tuple[float, ...]:
    half = period // 2
    return tuple(0.5 if (index // half) % 2 == 0 else -0.5 for index in range(4800))


def _carrier_grid(recipe_id: str) -> np.ndarray:
    grid = np.zeros((8, 12, 3), dtype=np.uint8)
    flat = grid.reshape(-1)
    if recipe_id in _ORDINALS:
        ordinal = _ORDINALS[recipe_id]
        for index in range(288):
            flat[index] = 255 if (index + ordinal) % 11 in {1, 3, 4, 5, 9} else 0
    elif recipe_id in {"A0", "C1"}:
        flat[32] = 1 if recipe_id == "A0" else 2
    elif recipe_id not in {"B0", "C0"}:
        if recipe_id != "D9_VISIBLE_MISMATCH":
            raise S2KPFixtureError("unknown visual recipe")
        ordinal = _ORDINALS["D9"]
        for index in range(288):
            flat[index] = 255 if (index + ordinal) % 11 in {1, 3, 4, 5, 9} else 0
        if flat[0] != 0:
            raise S2KPFixtureError("D9 visible mismatch anchor differs")
        flat[0] = 255
    return grid


def visual_image(recipe_id: str) -> np.ndarray:
    grid = _carrier_grid(recipe_id)
    return np.repeat(np.repeat(grid, 135, axis=0), 160, axis=1)


@dataclass(frozen=True, slots=True)
class S2KPSourceSummaryV1:
    history_id: str
    recipe_id: str
    block_index: int
    pairing_digest: str
    visual_payload_digest: str
    auditory_payload_digest: str
    visual_values_digest: str
    auditory_values_digest: str
    overlap_start_tick: int
    overlap_end_tick: int
    schema: str = S2KP_FIXTURE_SCHEMA


class S2KPFixtureStream:
    """Create one strictly ordered real AV source stream for one fresh state."""

    def __init__(self, profile: S2JWDefaultLiveProfileV1, history_id: str) -> None:
        if type(profile) is not S2JWDefaultLiveProfileV1:
            raise S2KPFixtureError("exact default-live profile required")
        if not history_id or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in history_id):
            raise S2KPFixtureError("history_id is not canonical")
        self._profile = profile
        self._history_id = history_id
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self._next_block = 0

    @property
    def next_block(self) -> int:
        return self._next_block

    def materialize(self, recipe_id: str) -> tuple[S2JVBoundAVPairV1, S2KPSourceSummaryV1]:
        if recipe_id not in _PERIODS:
            raise S2KPFixtureError("fixture recipe is not bound")
        block_index = self._next_block
        image = visual_image(recipe_id)
        visual_bytes = image.tobytes(order="C")
        window = _square_window(_PERIODS[recipe_id])
        auditory_bytes = np.asarray(window, dtype="<f4").tobytes()

        auditory_state = None
        for hop_index in range(10):
            start = hop_index * 480
            auditory_state = self._hearing.push(window[start : start + 480])
        if auditory_state is None or auditory_state.snapshot_index != block_index * 10:
            raise S2KPFixtureError("auditory rolling endpoint differs")
        visual_state = self._visual.analyze(image, frame_index=3 * block_index + 2)

        clock_id = f"s2kp-{self._history_id}-clock"
        auditory = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(auditory_state),
            CommonFieldTime(
                clock_id,
                100_000_000 * block_index + 90_000_000,
                100_000_000 * (block_index + 1),
            ),
        )
        visual = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual_state),
            CommonFieldTime(
                clock_id,
                ((3 * block_index + 2) * 1_000_000_000) // 30,
                100_000_000 * (block_index + 1),
            ),
        )
        pair_id = f"s2kp-{self._history_id}-pair-{block_index:03d}"
        plan = build_s2jv_pairing_plan(
            pair_id=pair_id,
            source_contract_id=f"s2kp-{self._history_id}-source",
            profile=self._profile,
            auditory=auditory,
            visual=visual,
            auditory_payload_digest=_digest_bytes(auditory_bytes),
            visual_payload_digest=_digest_bytes(visual_bytes),
        )
        pair = bind_s2jv_default_live_pair(
            pairing_plan=plan,
            profile=self._profile,
            auditory=auditory,
            visual=visual,
        )
        summary = S2KPSourceSummaryV1(
            self._history_id,
            recipe_id,
            block_index,
            pair.pairing_digest,
            plan.visual_payload_digest,
            plan.auditory_payload_digest,
            plan.visual_values_digest,
            plan.auditory_values_digest,
            plan.overlap_start_tick,
            plan.overlap_end_tick,
        )
        self._next_block += 1
        return pair, summary


def masked_visual_values(pair: S2JVBoundAVPairV1) -> tuple[float | None, ...]:
    if type(pair) is not S2JVBoundAVPairV1:
        raise S2KPFixtureError("exact bound AV pair required")
    visual = tuple(pair.visual.timed_frame.frame.values)
    if len(visual) != 288:
        raise S2KPFixtureError("masked source visual dimension differs")
    return tuple(visual[index] if index in VISIBLE_POSITIONS else None for index in range(288))


def assert_strictly_later(
    earlier: S2KPSourceSummaryV1,
    later: S2KPSourceSummaryV1,
) -> None:
    if (
        type(earlier) is not S2KPSourceSummaryV1
        or type(later) is not S2KPSourceSummaryV1
        or earlier.history_id != later.history_id
        or later.block_index <= earlier.block_index
        or later.overlap_start_tick <= earlier.overlap_end_tick
    ):
        raise S2KPFixtureError("masked probe is not strictly later than retrieval")


__all__: tuple[str, ...] = ()
