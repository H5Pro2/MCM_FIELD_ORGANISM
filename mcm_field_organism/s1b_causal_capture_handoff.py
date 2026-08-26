"""Digest-bound capture and organism-time handoff for the W6-D check."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .audio_video_field_geometry import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .browser_payload_source import BrowserPayloadCaptureReceipt
from .browser_receptor_bridge import (
    BrowserReceptorBridgeConfig,
    BrowserReceptorSequenceBatch,
)
from .field_step_time import MCMFieldStepTime
from .mcm_local_development_state import MCMLocalDevelopmentContract
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_time_model import ReceptorTimeSequence
from .s1b_causal_browser_world import (
    S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST,
    S1BCausalBrowserWorldSet,
    s1b_causal_browser_world_set,
)
from .s1b_causal_two_stage import (
    S1BCausalTwoStageResult,
    run_s1b_causal_two_stage,
)
from .shared_mcm_field import build_shared_mcm_field


class S1BCausalCaptureHandoffError(ValueError):
    """Raised when reduced browser captures cannot enter the causal check."""


_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_CLOCK_ID = "organism.w6f.browser.ns"
_TICKS_PER_SECOND = 1_000_000_000.0
_EQUATION_ID = "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1"


@dataclass(frozen=True, slots=True)
class S1BCausalCaptureSchedule:
    """Aligned alternative formations followed by one disjoint probe stage."""

    history_a_bridge_config: BrowserReceptorBridgeConfig
    history_b_bridge_config: BrowserReceptorBridgeConfig
    probe_bridge_config: BrowserReceptorBridgeConfig
    history_step: MCMFieldStepTime
    probe_step: MCMFieldStepTime

    def __post_init__(self) -> None:
        configs = (
            self.history_a_bridge_config,
            self.history_b_bridge_config,
            self.probe_bridge_config,
        )
        if any(not isinstance(item, BrowserReceptorBridgeConfig) for item in configs):
            raise S1BCausalCaptureHandoffError("capture schedule configs are invalid")
        if any(
            item.clock_id != _CLOCK_ID
            or item.ticks_per_second != _TICKS_PER_SECOND
            for item in configs
        ):
            raise S1BCausalCaptureHandoffError(
                "capture schedule requires one fixed organism clock"
            )
        if (
            configs[0].sequence_start_tick != 0
            or configs[1].sequence_start_tick != 0
            or configs[2].sequence_start_tick != self.history_step.end_tick
        ):
            raise S1BCausalCaptureHandoffError(
                "capture schedule stages are not aligned"
            )
        if (
            not isinstance(self.history_step, MCMFieldStepTime)
            or not isinstance(self.probe_step, MCMFieldStepTime)
            or self.history_step.clock_id != _CLOCK_ID
            or self.probe_step.clock_id != _CLOCK_ID
            or self.history_step.start_tick != 0
            or self.history_step.end_tick != self.probe_step.start_tick
            or self.history_step.ticks_per_second != _TICKS_PER_SECOND
            or self.probe_step.ticks_per_second != _TICKS_PER_SECOND
        ):
            raise S1BCausalCaptureHandoffError(
                "capture schedule requires contiguous formation and probe steps"
            )


@dataclass(frozen=True, slots=True)
class S1BCausalCaptureHandoff:
    """Reduced immutable H_A/H_B/P inputs ready for the W6-E adapter."""

    history_a_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    history_b_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    probe_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    history_step: MCMFieldStepTime
    probe_step: MCMFieldStepTime
    world_set_digest: str
    history_a_batch_digest: str
    history_b_batch_digest: str
    probe_batch_digest: str
    asset_digests: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        sequence_sets = (
            self.history_a_sequences,
            self.history_b_sequences,
            self.probe_sequences,
        )
        if any(
            len(items) != 2
            or tuple(item.modality_id for item in items)
            != ("auditory", "visual")
            for items in sequence_sets
        ):
            raise S1BCausalCaptureHandoffError(
                "capture handoff requires three auditory/visual sequence pairs"
            )
        for role in (
            "world_set_digest",
            "history_a_batch_digest",
            "history_b_batch_digest",
            "probe_batch_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S1BCausalCaptureHandoffError(f"invalid {role}")
        if self.world_set_digest != S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST:
            raise S1BCausalCaptureHandoffError("capture world set digest changed")
        if not self.asset_digests or any(
            not _DIGEST.fullmatch(digest) for _, digest in self.asset_digests
        ):
            raise S1BCausalCaptureHandoffError("capture asset digests are invalid")


def s1b_causal_capture_schedule(
    world_set: S1BCausalBrowserWorldSet | None = None,
) -> S1BCausalCaptureSchedule:
    """Return the fixed aligned formation/probe organism-time schedule."""

    worlds = s1b_causal_browser_world_set() if world_set is None else world_set
    if not isinstance(worlds, S1BCausalBrowserWorldSet):
        raise S1BCausalCaptureHandoffError("capture schedule requires one world set")
    if worlds.digest() != S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST:
        raise S1BCausalCaptureHandoffError("capture schedule world set changed")
    history_end = worlds.history_a_contract.total_duration_ns
    if history_end != worlds.history_b_contract.total_duration_ns:
        raise S1BCausalCaptureHandoffError("capture history durations differ")
    probe_end = history_end + worlds.probe_contract.total_duration_ns
    history_step = MCMFieldStepTime(
        _CLOCK_ID,
        0,
        history_end,
        _TICKS_PER_SECOND,
    )
    probe_step = MCMFieldStepTime(
        _CLOCK_ID,
        history_end,
        probe_end,
        _TICKS_PER_SECOND,
    )
    return S1BCausalCaptureSchedule(
        BrowserReceptorBridgeConfig(
            _CLOCK_ID,
            _TICKS_PER_SECOND,
            0,
        ),
        BrowserReceptorBridgeConfig(
            _CLOCK_ID,
            _TICKS_PER_SECOND,
            0,
        ),
        BrowserReceptorBridgeConfig(
            _CLOCK_ID,
            _TICKS_PER_SECOND,
            history_end,
        ),
        history_step,
        probe_step,
    )


def _sequence_time_signature(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
) -> tuple[object, ...]:
    return tuple(
        (
            sequence.modality_id,
            sequence.geometry_id,
            tuple(
                (
                    item.field_time.window_start_tick,
                    item.field_time.window_end_tick,
                    item.frame.carrier_ids,
                )
                for item in sequence.frames
            ),
        )
        for sequence in sequences
    )


def _sequence_bounds(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
) -> tuple[int, int]:
    frames = tuple(item for sequence in sequences for item in sequence.frames)
    return (
        min(item.field_time.window_start_tick for item in frames),
        max(item.field_time.window_end_tick for item in frames),
    )


def _validate_capture_part(
    batch: BrowserReceptorSequenceBatch,
    receipt: BrowserPayloadCaptureReceipt,
    *,
    contract_id: str,
    contract_digest: str,
    source_id: str,
    source_digest: str,
) -> None:
    if not isinstance(batch, BrowserReceptorSequenceBatch) or not isinstance(
        receipt,
        BrowserPayloadCaptureReceipt,
    ):
        raise S1BCausalCaptureHandoffError(
            "capture handoff requires complete batch and receipt pairs"
        )
    if batch.raw_payloads_retained or receipt.raw_payloads_retained:
        raise S1BCausalCaptureHandoffError("capture handoff cannot retain raw payloads")
    if (
        batch.contract_id != contract_id
        or batch.contract_digest != contract_digest
        or receipt.world_contract_digest != contract_digest
        or receipt.source_id != source_id
        or receipt.source_config_digest != source_digest
        or receipt.batch_digest != batch.digest()
    ):
        raise S1BCausalCaptureHandoffError("capture handoff digest binding differs")


def prepare_s1b_causal_capture_handoff(
    history_a_batch: BrowserReceptorSequenceBatch,
    history_a_receipt: BrowserPayloadCaptureReceipt,
    history_b_batch: BrowserReceptorSequenceBatch,
    history_b_receipt: BrowserPayloadCaptureReceipt,
    probe_batch: BrowserReceptorSequenceBatch,
    probe_receipt: BrowserPayloadCaptureReceipt,
    *,
    world_set: S1BCausalBrowserWorldSet | None = None,
) -> S1BCausalCaptureHandoff:
    """Validate three reduced captures without retaining browser payloads."""

    worlds = s1b_causal_browser_world_set() if world_set is None else world_set
    schedule = s1b_causal_capture_schedule(worlds)
    parts = (
        (
            history_a_batch,
            history_a_receipt,
            worlds.history_a_contract,
            worlds.history_a_source,
        ),
        (
            history_b_batch,
            history_b_receipt,
            worlds.history_b_contract,
            worlds.history_b_source,
        ),
        (probe_batch, probe_receipt, worlds.probe_contract, worlds.probe_source),
    )
    for batch, receipt, contract, source in parts:
        _validate_capture_part(
            batch,
            receipt,
            contract_id=contract.contract_id,
            contract_digest=contract.digest(),
            source_id=source.source_id,
            source_digest=source.digest(),
        )
    receipts = (history_a_receipt, history_b_receipt, probe_receipt)
    if len({receipt.asset_digests for receipt in receipts}) != 1:
        raise S1BCausalCaptureHandoffError(
            "capture handoff requires one immutable asset inventory"
        )
    if _sequence_time_signature(history_a_batch.sequences) != (
        _sequence_time_signature(history_b_batch.sequences)
    ):
        raise S1BCausalCaptureHandoffError(
            "capture histories require identical reduced temporal support"
        )
    expected_history_bounds = (
        schedule.history_step.start_tick,
        schedule.history_step.end_tick,
    )
    expected_probe_bounds = (
        schedule.probe_step.start_tick,
        schedule.probe_step.end_tick,
    )
    if (
        _sequence_bounds(history_a_batch.sequences) != expected_history_bounds
        or _sequence_bounds(history_b_batch.sequences) != expected_history_bounds
        or _sequence_bounds(probe_batch.sequences) != expected_probe_bounds
    ):
        raise S1BCausalCaptureHandoffError(
            "capture sequences do not fill the fixed organism-time stages"
        )
    if any(
        sequence.clock_id != _CLOCK_ID
        for batch in (history_a_batch, history_b_batch, probe_batch)
        for sequence in batch.sequences
    ):
        raise S1BCausalCaptureHandoffError("capture sequences changed organism clock")

    return S1BCausalCaptureHandoff(
        history_a_sequences=history_a_batch.sequences,
        history_b_sequences=history_b_batch.sequences,
        probe_sequences=probe_batch.sequences,
        history_step=schedule.history_step,
        probe_step=schedule.probe_step,
        world_set_digest=worlds.digest(),
        history_a_batch_digest=history_a_batch.digest(),
        history_b_batch_digest=history_b_batch.digest(),
        probe_batch_digest=probe_batch.digest(),
        asset_digests=history_a_receipt.asset_digests,
    )


def run_s1b_causal_capture_handoff(
    handoff: S1BCausalCaptureHandoff,
) -> S1BCausalTwoStageResult:
    """Run the W6-E adapter only on one validated reduced capture handoff."""

    if not isinstance(handoff, S1BCausalCaptureHandoff):
        raise S1BCausalCaptureHandoffError(
            "causal capture execution requires one validated handoff"
        )
    reference_frames = (
        handoff.history_a_sequences[0].frames[0].frame,
        handoff.history_a_sequences[1].frames[0].frame,
    )
    field = build_shared_mcm_field(
        reference_frames,
        audio_video_dock_anatomies(
            auditory_carrier_count=len(reference_frames[0].carrier_ids),
            visual_grid_columns=3,
            visual_grid_rows=2,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    return run_s1b_causal_two_stage(
        field,
        handoff.history_a_sequences,
        handoff.history_b_sequences,
        handoff.probe_sequences,
        (handoff.history_step,),
        (handoff.probe_step,),
        NeutralLocalFieldSubstrateConfig(1.0),
        MCMLocalDevelopmentContract(_EQUATION_ID, 8.0, 0.25),
        MCMLocalDevelopmentContract(_EQUATION_ID, 8.0, 0.0),
        NeutralFastAfterimageConfig(0.5),
    )
