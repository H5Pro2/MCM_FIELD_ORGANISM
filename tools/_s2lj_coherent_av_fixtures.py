"""Private real RGB/PCM fixtures for the bounded S2-LJ integration path."""

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
from tools import _s2kq_private_partial_cue_retrieval_336 as visual_retrieval
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as auditory_retrieval
from tools import _s2ks_real_partial_cue_fixtures as visual_cues
from tools import _s2ld_auditory_partial_cue_fixtures as auditory_sources
from tools._s2jw_default_live_av_pairing import (
    S2JVBoundAVPairV1,
    bind_s2jv_default_live_pair,
    build_s2jv_pairing_plan,
)
from tools._s2jw_default_live_profile import S2JWDefaultLiveProfileV1


S2LJ_FIXTURE_SCHEMA = "s2lj.coherent-av-fixture.v1"
SOURCE_CONTRACT_ID = "s2lj-coherent-av-source"
MAIN_FORMATION_COUNT = 13
MAIN_SEQUENCE = ("P",) * 4 + tuple(f"E{index}" for index in range(1, 10))
QUALIFICATION_SEQUENCE = ("E1",)
VISUAL_CUE_ORDINAL = 14
AUDITORY_CUE_ORDINAL = 13
FIELD_CLOCK_ID = "s2lj-coherent-av-clock"


class S2LJFixtureError(ValueError):
    """One source, time, profile, or cue binding differs."""


def _digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _values_digest(values: tuple[float, ...]) -> str:
    return visual_retrieval.digest(list(values))


@dataclass(frozen=True, slots=True)
class S2LJFormationSourceV1:
    source_id: str
    ordinal: int
    pairing_digest: str
    auditory_payload_digest: str
    visual_payload_digest: str
    auditory_values_digest: str
    visual_values_digest: str
    overlap_start_tick: int
    overlap_end_tick: int
    source_digest: str
    schema: str = S2LJ_FIXTURE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "source_digest"
        }


@dataclass(frozen=True, slots=True)
class S2LJAuditoryCueSourceV1:
    source_id: str
    ordinal: int
    pcm_payload_digest: str
    receptor_state_digest: str
    receptor_values_digest: str
    observed_values_digest: str
    cue_digest: str
    source_digest: str
    schema: str = S2LJ_FIXTURE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "source_digest"
        }


@dataclass(frozen=True, slots=True)
class S2LJVisualCueSourceV1:
    source_id: str
    ordinal: int
    rgb_payload_digest: str
    receptor_state_digest: str
    receptor_values_digest: str
    visible_values_digest: str
    cue_digest: str
    source_digest: str
    schema: str = S2LJ_FIXTURE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "source_digest"
        }


class S2LJSourceStream:
    """Materialize one strictly ordered source stream without retaining raw payloads."""

    def __init__(self, profile: S2JWDefaultLiveProfileV1, *, mode: str) -> None:
        if type(profile) is not S2JWDefaultLiveProfileV1 or mode not in {"MAIN", "QUALIFICATION"}:
            raise S2LJFixtureError("profile or stream mode differs")
        self._profile = profile
        self._mode = mode
        self._sequence = MAIN_SEQUENCE if mode == "MAIN" else QUALIFICATION_SEQUENCE
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self._next = 0
        self._target_auditory: tuple[float, ...] | None = None
        self._target_visual: tuple[float, ...] | None = None

    @property
    def next_ordinal(self) -> int:
        return self._next

    def _audio_state(self, recipe: str):
        audio_recipe = "D_FAR" if recipe.startswith("E") else recipe
        window = auditory_sources.auditory_pcm(audio_recipe)
        state = None
        for hop in range(10):
            state = self._hearing.push(window[hop * 480 : (hop + 1) * 480])
        if state is None or state.snapshot_index != self._next * 10:
            raise S2LJFixtureError("auditory endpoint differs")
        return window, state

    def materialize_next_formation(
        self,
    ) -> tuple[S2JVBoundAVPairV1, S2LJFormationSourceV1]:
        if self._next >= len(self._sequence):
            raise S2LJFixtureError("formation stream is exhausted")
        recipe = self._sequence[self._next]
        ordinal = self._next
        window, auditory_state = self._audio_state(recipe)
        image = auditory_sources.visual_image(recipe)
        visual_state = self._visual.analyze(image, frame_index=ordinal * 3 + 2)
        end_tick = (ordinal + 1) * 100_000_000
        auditory = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(auditory_state),
            CommonFieldTime(FIELD_CLOCK_ID, end_tick - 10_000_000, end_tick),
        )
        visual = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual_state),
            CommonFieldTime(
                FIELD_CLOCK_ID,
                ((ordinal * 3 + 2) * 1_000_000_000) // 30,
                end_tick,
            ),
        )
        auditory_bytes = np.asarray(window, dtype="<f4").tobytes()
        visual_bytes = image.tobytes(order="C")
        source_id = f"s2lj-source-{ordinal + 1:03d}"
        plan = build_s2jv_pairing_plan(
            pair_id=f"s2lj-pair-{ordinal + 1:03d}",
            source_contract_id=SOURCE_CONTRACT_ID,
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
        payload = {
            "schema": S2LJ_FIXTURE_SCHEMA,
            "source_id": source_id,
            "ordinal": ordinal + 1,
            "pairing_digest": pair.pairing_digest,
            "auditory_payload_digest": plan.auditory_payload_digest,
            "visual_payload_digest": plan.visual_payload_digest,
            "auditory_values_digest": plan.auditory_values_digest,
            "visual_values_digest": plan.visual_values_digest,
            "overlap_start_tick": plan.overlap_start_tick,
            "overlap_end_tick": plan.overlap_end_tick,
        }
        receipt = S2LJFormationSourceV1(
            source_id,
            ordinal + 1,
            pair.pairing_digest,
            plan.auditory_payload_digest,
            plan.visual_payload_digest,
            plan.auditory_values_digest,
            plan.visual_values_digest,
            plan.overlap_start_tick,
            plan.overlap_end_tick,
            visual_retrieval.digest(payload),
        )
        if receipt.source_digest != visual_retrieval.digest(receipt.payload_without_digest()):
            raise S2LJFixtureError("formation source digest differs")
        if self._mode == "MAIN" and ordinal == 0:
            self._target_auditory = tuple(pair.auditory.timed_frame.frame.values)
            self._target_visual = tuple(pair.visual.timed_frame.frame.values)
        self._next += 1
        return pair, receipt

    def materialize_auditory_cue(
        self,
        *,
        config_digest: str,
        band_plan: auditory_retrieval.AuditoryBandPlan48V1,
    ) -> tuple[
        auditory_retrieval.MaskedAuditoryCue48V1,
        OrganismTimedReceptorFrame,
        S2LJAuditoryCueSourceV1,
    ]:
        if self._mode != "MAIN" or self._next != MAIN_FORMATION_COUNT:
            raise S2LJFixtureError("auditory cue is not at its bound position")
        window, state = self._audio_state("L")
        end_tick = (AUDITORY_CUE_ORDINAL + 1) * 100_000_000
        timed = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(state),
            CommonFieldTime(FIELD_CLOCK_ID, end_tick - 10_000_000, end_tick),
        )
        values = tuple(state.energy)
        pcm_digest = _digest_bytes(np.asarray(window, dtype="<f4").tobytes())
        cue = auditory_retrieval.build_masked_auditory_cue_48(
            pcm_payload_digest=pcm_digest,
            receptor_state_digest=state.digest(),
            receptor_values_digest=_values_digest(values),
            config_digest=config_digest,
            auditory_source_clock_id=timed.frame.clock_id,
            auditory_window_start_tick=timed.frame.window_start_tick,
            auditory_window_end_tick=timed.frame.window_end_tick,
            observed_values=tuple(values[index] for index in auditory_retrieval.OBSERVED_BANDS),
            band_plan=band_plan,
        )
        payload = {
            "schema": S2LJ_FIXTURE_SCHEMA,
            "source_id": "s2lj-cue-016",
            "ordinal": 16,
            "pcm_payload_digest": pcm_digest,
            "receptor_state_digest": state.digest(),
            "receptor_values_digest": _values_digest(values),
            "observed_values_digest": _values_digest(tuple(values[:24])),
            "cue_digest": cue.cue_digest,
        }
        receipt = S2LJAuditoryCueSourceV1(
            "s2lj-cue-016",
            16,
            pcm_digest,
            state.digest(),
            _values_digest(values),
            _values_digest(tuple(values[:24])),
            cue.cue_digest,
            visual_retrieval.digest(payload),
        )
        self._next += 1
        return cue, timed, receipt

    def materialize_visual_cue(
        self,
        *,
        config_digest: str,
    ) -> tuple[
        visual_retrieval.MaskedMemoryCue336V1,
        OrganismTimedReceptorFrame,
        S2LJVisualCueSourceV1,
    ]:
        if self._mode != "MAIN" or self._next != MAIN_FORMATION_COUNT + 1:
            raise S2LJFixtureError("visual cue is not at its bound position")
        image = visual_cues.occluded_visual_image("X")
        state = self._visual.analyze(image, frame_index=VISUAL_CUE_ORDINAL * 3 + 2)
        native = from_visual_receptor_state(state)
        end_tick = (VISUAL_CUE_ORDINAL + 1) * 100_000_000
        timed = OrganismTimedReceptorFrame(
            native,
            CommonFieldTime(
                FIELD_CLOCK_ID,
                ((VISUAL_CUE_ORDINAL * 3 + 2) * 1_000_000_000) // 30,
                end_tick,
            ),
        )
        values = tuple(state.channel_values)
        visible = tuple(values[index] for index in visual_retrieval.VISIBLE_POSITIONS)
        rgb_digest = _digest_bytes(image.tobytes(order="C"))
        source_payload = {
            "schema": S2LJ_FIXTURE_SCHEMA,
            "source_id": "s2lj-cue-017",
            "ordinal": 17,
            "rgb_payload_digest": rgb_digest,
            "receptor_state_digest": state.digest(),
            "receptor_values_digest": _values_digest(values),
            "visible_values_digest": _values_digest(visible),
        }
        source_digest = visual_retrieval.digest(source_payload)
        cue_values = tuple(
            values[index] if index in visual_retrieval.VISIBLE_POSITIONS else None
            for index in range(288)
        )
        cue = visual_retrieval.build_masked_memory_cue_336(
            source_digest=source_digest,
            config_digest=config_digest,
            field_clock_id=FIELD_CLOCK_ID,
            window_start_tick=timed.field_time.window_start_tick,
            window_end_tick=timed.field_time.window_end_tick,
            visual_source_clock_id=native.clock_id,
            visual_window_start_tick=native.window_start_tick,
            visual_window_end_tick=native.window_end_tick,
            values=cue_values,
        )
        payload = {**source_payload, "cue_digest": cue.cue_digest}
        receipt = S2LJVisualCueSourceV1(
            "s2lj-cue-017",
            17,
            rgb_digest,
            state.digest(),
            _values_digest(values),
            _values_digest(visible),
            cue.cue_digest,
            visual_retrieval.digest(payload),
        )
        self._next += 1
        return cue, timed, receipt

    def evaluation_targets(self) -> tuple[tuple[float, ...], tuple[float, ...]]:
        if (
            self._mode != "MAIN"
            or self._next != MAIN_FORMATION_COUNT + 2
            or self._target_auditory is None
            or self._target_visual is None
        ):
            raise S2LJFixtureError("evaluation targets are not yet available")
        return self._target_auditory, self._target_visual


assert len(MAIN_SEQUENCE) == MAIN_FORMATION_COUNT

__all__: tuple[str, ...] = ()
