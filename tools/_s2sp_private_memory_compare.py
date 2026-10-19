"""Private read-only S2-SP comparison over actual S2-JW memory candidates."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import math

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import CommonFieldTime, from_auditory_receptor_state, from_visual_receptor_state
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2jw_default_live_av_pairing as pairing
from tools import _s2jw_default_live_profile as profile_module
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2sp_private_shift_hint as shift


SCHEMA = "s2sp.private-memory-compare.v1"
OFFSETS = shift.OFFSETS
BACKGROUND = (24, 32, 48)
RED = (224, 64, 64)
GREEN = (64, 224, 64)
BLUE = (64, 64, 224)
YELLOW = (224, 224, 64)

COMPETITOR_1 = (YELLOW,) * 12
COMPETITOR_1_VARIANT = (RED,) + COMPETITOR_1[1:]
COMPETITOR_2 = (RED,) * 12
COMPETITOR_3 = (GREEN,) * 12
COMPETITOR_4 = (BLUE,) * 12
AUDIO_FREQUENCIES = {
    "base": None,
    "tone-0430": 430.0,
    "tone-1710": 1710.0,
    "tone-4300": 4300.0,
    "tone-9000": 9000.0,
}

TARGET = (BACKGROUND, RED, GREEN, BLUE, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND)
SHIFTED = (BACKGROUND,) + TARGET[:-1]
FOREIGN = SHIFTED[:4] + (YELLOW,) + SHIFTED[5:]
BOUNDARY = TARGET[:9] + (YELLOW,) + TARGET[10:]


class S2SPMemoryError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise S2SPMemoryError(code)


def canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _window(audio_mode: str = "base") -> tuple[float, ...]:
    frequency = AUDIO_FREQUENCIES.get(audio_mode)
    _require(audio_mode in AUDIO_FREQUENCIES, "AUDIO_MODE_INVALID")
    if frequency is None:
        return tuple(0.5 if (index // 480) % 2 == 0 else -0.5 for index in range(4800))
    return tuple(0.5 * math.sin(2.0 * math.pi * frequency * index / 48_000.0) for index in range(4800))


def _frame(cells: tuple[tuple[int, int, int], ...]) -> np.ndarray:
    image = np.empty((1080, 1920, 3), dtype=np.uint8)
    image[:, :, :] = BACKGROUND
    for column, color in enumerate(cells):
        image[0:135, column * 160 : (column + 1) * 160, :] = color
    return image


class Sources:
    """Sequential real receptor sources; raw frames and PCM are transient."""

    def __init__(self, profile: profile_module.S2JWDefaultLiveProfileV1) -> None:
        self.profile = profile
        self.hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self.visual = LocalChannelGridReceptor()
        self.audio_analyses = 0
        self.visual_analyses = 0

    def formation(
        self,
        *,
        event_id: str,
        ordinal: int,
        cells: tuple[tuple[int, int, int], ...],
        audio_mode: str = "base",
    ):
        window = _window(audio_mode)
        audio = None
        for hop in range(10):
            audio = self.hearing.push(window[hop * 480 : (hop + 1) * 480])
        _require(audio is not None, "AUDIO_ENDPOINT_MISSING")
        image = _frame(cells)
        visual = self.visual.analyze(image, frame_index=ordinal * 3 + 2)
        audio_bytes = np.asarray(window, dtype="<f4").tobytes()
        visual_bytes = image.tobytes(order="C")
        del window, image
        self.audio_analyses += 1
        self.visual_analyses += 1
        clock = "s2sp-memory-clock"
        auditory = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(audio),
            CommonFieldTime(clock, ordinal * 100_000_000 + 90_000_000, (ordinal + 1) * 100_000_000),
        )
        visible = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual),
            CommonFieldTime(clock, ordinal * 100_000_000, (ordinal + 1) * 100_000_000),
        )
        plan = pairing.build_s2jv_pairing_plan(
            pair_id=f"s2sp-pair-{ordinal:02d}", source_contract_id="s2sp-private-source", profile=self.profile,
            auditory=auditory, visual=visible,
            auditory_payload_digest=hashlib.sha256(audio_bytes).hexdigest(), visual_payload_digest=hashlib.sha256(visual_bytes).hexdigest(),
        )
        pair = pairing.bind_s2jv_default_live_pair(pairing_plan=plan, profile=self.profile, auditory=auditory, visual=visible)
        return pair, tuple(visual.channel_values)

    def cue(self, *, ordinal: int, cells: tuple[tuple[int, int, int], ...]) -> tuple[float, ...]:
        image = _frame(cells)
        state = self.visual.analyze(image, frame_index=ordinal * 3 + 2)
        del image
        self.visual_analyses += 1
        values = tuple(state.channel_values)
        _require(len(values) == 288 and all(math.isfinite(value) for value in values), "CUE_VALUES_INVALID")
        return values


def _candidate_rows(state: coordinator.S2JVCompositeStateV1) -> dict[str, tuple[tuple[str, tuple[float, ...]], ...]]:
    rows: dict[str, list[tuple[str, tuple[float, ...]]]] = {"B4": [], "FAST": [], "VISUAL_SLOW": []}
    for item in state.b4_state.entries:
        if item.occupied:
            rows["B4"].append((f"B4:{item.slot_id}:{digest(asdict(item))}", tuple(item.values[48:])))
    for item in state.tspm_state.fast_state.slots:
        if item.occupied:
            rows["FAST"].append((f"FAST:{item.slot_id}:{item.digest()}", tuple(item.visual_values)))
    for item in state.tspm_state.visual_ppb1_state.slots:
        if item.occupied:
            rows["VISUAL_SLOW"].append((f"VISUAL_SLOW:{item.slot_id}:{digest(item.canonical_payload())}", tuple(item.prototype_values)))
    return {bank: tuple(values) for bank, values in rows.items()}


def compare_state(*, state: coordinator.S2JVCompositeStateV1, cue_values: tuple[float, ...]) -> dict[str, object]:
    candidates = _candidate_rows(state)
    banks = []
    for bank, items in candidates.items():
        hints = shift.collect_shift_hints(cue_values, items)
        exact = tuple(candidate_id for candidate_id, values in items if shift.exact_visible_match(cue_values, values))
        banks.append({
            "bank": bank,
            "candidate_ids": [candidate_id for candidate_id, _ in items],
            "exact_baseline_candidate_ids": list(exact),
            "hint_status": hints.status,
            "hint_candidate_ids": list(hints.candidate_ids),
            "hint_findings": [
                {"status": finding.status, "matching_offsets": list(finding.matching_offsets), "overlap_cells": list(finding.overlap_cells)}
                for finding in hints.findings
            ],
        })
    payload = {
        "state_digest": state.state_digest,
        "banks": banks,
    }
    return {**payload, "comparison_digest": digest(payload)}


def form(
    *, config: coordinator.S2JVCoordinatorConfigV1, state: coordinator.S2JVCompositeStateV1,
    pair: pairing.S2JVBoundAVPairV1, event_id: str, run_id: str,
    ppb_update_mode: str = coordinator.tspm1.PPB_UPDATE_HISTORICAL,
) -> coordinator.S2JVFormationResultV1:
    source = coordinator.bind_s2jv_coordinator_input(config=config, source=pair)
    owner = coordinator.S2JVFormationOwner(
        f"s2sp-owner-{event_id}", f"s2sp-authorize-{event_id}", f"s2sp-consume-{event_id}",
        config.config_digest, state.state_digest, source.input_digest, ppb_update_mode,
    )
    return coordinator.advance_s2jv_atomic(config=config, prestate=state, source=source, owner=owner)


def transition_evidence(
    *, prestate: coordinator.S2JVCompositeStateV1, result: coordinator.S2JVFormationResultV1,
) -> dict[str, object]:
    """Expose only data already produced by the atomic transition receipt."""

    receipt = result.tspm_transition_receipt
    selected = receipt.selected_slot_id
    pre_slot = next((slot for slot in prestate.tspm_state.fast_state.slots if slot.slot_id == selected), None)
    post_slot = next((slot for slot in result.poststate.tspm_state.fast_state.slots if slot.slot_id == selected), None)
    visual_readout = result.visual_ppb1_readout
    visual_payload = None if visual_readout is None else {
        "event": visual_readout.event,
        "slot_id": visual_readout.slot_id,
        "input_digest": visual_readout.input_digest,
        "prestate_digest": visual_readout.prestate_digest,
        "poststate_digest": visual_readout.poststate_digest,
        "support_count": visual_readout.support_count,
        "prototype_digest": digest(list(visual_readout.prototype_values)),
        "readout_digest": visual_readout.digest(),
    }
    payload = {
        "formation_generation_before": prestate.generation,
        "formation_generation_after": result.poststate.generation,
        "selected_fast_slot_id": selected,
        "fast_primary_event": receipt.primary_event,
        "fast_match_decision": "MATCHED" if receipt.primary_event == "FAST_UPDATED" else "NOT_MATCHED",
        "fast_support_before": None if pre_slot is None else pre_slot.support_count,
        "fast_support_after": None if post_slot is None else post_slot.support_count,
        "consolidation_eligible": receipt.consolidation_status == "COMMITTED",
        "consolidation_status": receipt.consolidation_status,
        "fast_generation": None,
        "fast_generation_status": "NOT_AVAILABLE_IN_NATIVE_SLOT",
        "visual_ppb_action": "ADVANCED" if receipt.consolidation_status == "COMMITTED" else "NOT_ADVANCED",
        "visual_ppb_readout_digest": receipt.visual_ppb1_readout_digest,
        "visual_ppb_readout": visual_payload,
        "visual_ppb_stabilized": receipt.visual_ppb1_stabilized,
        "visual_ppb_generation_before": prestate.tspm_state.visual_ppb1_state.accepted_step_count,
        "visual_ppb_generation_after": result.poststate.tspm_state.visual_ppb1_state.accepted_step_count,
        "native_transition_receipt_digest": receipt.receipt_digest,
    }
    return {**payload, "transition_evidence_digest": digest(payload)}


def build_config() -> coordinator.S2JVCoordinatorConfigV1:
    profile = profile_module.build_s2jw_default_live_profile()
    return coordinator.build_s2jv_coordinator_config(
        tspm_config=profile.tspm_config, b4_capacity=9,
        ledger_limits=coordinator.build_s2jv_ledger_limits(profile),
    )
