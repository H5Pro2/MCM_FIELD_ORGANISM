"""Fixed controlled histories and one freshly reduced shared AV probe."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .controlled_audio_video_test_world import (
    ControlledAudioVideoTestWorld,
    _scheduled_phase_sequences,
    controlled_history_holdout_world_family,
)
from .receptor_time_alignment import ReceptorTimeSequence


class MCMF3ControlledHistorySourceError(ValueError):
    """Raised when histories and the shared probe are not cleanly separated."""


_CLOCK_ID = "organism.mcm_f3_history"
_TICKS_PER_SECOND = 1_000_000.0


def _sequence_payload(sequences: tuple[ReceptorTimeSequence, ...]) -> list[dict]:
    return [
        {
            "modality_id": sequence.modality_id,
            "geometry_id": sequence.geometry_id,
            "clock_id": sequence.clock_id,
            "frames": [
                {
                    "snapshot_id": item.frame.snapshot_id,
                    "source_clock_id": item.frame.clock_id,
                    "source_start": item.frame.window_start_tick,
                    "source_end": item.frame.window_end_tick,
                    "field_start": item.field_time.window_start_tick,
                    "field_end": item.field_time.window_end_tick,
                    "carrier_ids": list(item.frame.carrier_ids),
                    "values": list(item.frame.values),
                }
                for item in sequence.frames
            ],
        }
        for sequence in sequences
    ]


def mcm_f3_receptor_sequences_digest(
    sequences: tuple[ReceptorTimeSequence, ...],
) -> str:
    if not sequences or any(
        not isinstance(item, ReceptorTimeSequence) for item in sequences
    ):
        raise MCMF3ControlledHistorySourceError(
            "sequence digest requires receptor time sequences"
        )
    payload = json.dumps(
        _sequence_payload(sequences),
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _combine_phase_sequences(
    phases: tuple[tuple[ReceptorTimeSequence, ReceptorTimeSequence], ...],
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    if not phases:
        raise MCMF3ControlledHistorySourceError("history phases are required")
    combined = []
    for modality_index in range(2):
        reference = phases[0][modality_index]
        combined.append(
            ReceptorTimeSequence(
                reference.modality_id,
                reference.geometry_id,
                reference.clock_id,
                tuple(
                    frame
                    for phase in phases
                    for frame in phase[modality_index].frames
                ),
            )
        )
    return tuple(combined)  # type: ignore[return-value]


def _history_sequences(
    world: ControlledAudioVideoTestWorld,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    audio_source, video_source, auditory_path, visual_receptor = world.open_sources()
    phase_sequences = []
    audio_cursor = 0
    video_cursor = 0
    for phase in world.phases[:-1]:
        phase_sequences.append(
            _scheduled_phase_sequences(
                world,
                phase,
                audio_source,
                video_source,
                auditory_path,
                visual_receptor,
                audio_frame_start=audio_cursor,
                video_frame_start=video_cursor,
                clock_id=_CLOCK_ID,
                ticks_per_second=_TICKS_PER_SECOND,
            )
        )
        audio_cursor += round(phase.duration_seconds / world.audio_config.hop_seconds)
        video_cursor += round(
            phase.duration_seconds * world.visual_config.frames_per_second
        )
    return _combine_phase_sequences(tuple(phase_sequences))


def _shared_probe_sequences(
    template: ControlledAudioVideoTestWorld,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    probe = template.phases[-1]
    probe_world = ControlledAudioVideoTestWorld(
        "world.history.shared-probe",
        (probe,),
        template.audio_config,
        template.visual_config,
        template.background_channels,
    )
    audio_source, video_source, auditory_path, visual_receptor = (
        probe_world.open_sources()
    )
    history_duration = sum(item.duration_seconds for item in template.phases[:-1])
    audio_start = round(history_duration / template.audio_config.hop_seconds)
    video_start = round(history_duration * template.visual_config.frames_per_second)
    return _scheduled_phase_sequences(
        probe_world,
        probe,
        audio_source,
        video_source,
        auditory_path,
        visual_receptor,
        audio_frame_start=audio_start,
        video_frame_start=video_start,
        clock_id=_CLOCK_ID,
        ticks_per_second=_TICKS_PER_SECOND,
    )


@dataclass(frozen=True, slots=True)
class MCMF3ControlledHistoryInputs:
    same_world_digest: str
    changed_world_digest: str
    same_history: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    changed_history: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    shared_probe: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    same_history_digest: str
    changed_history_digest: str
    shared_probe_digest: str
    clock_id: str
    ticks_per_second: float

    def __post_init__(self) -> None:
        if self.same_history_digest == self.changed_history_digest:
            raise MCMF3ControlledHistorySourceError(
                "controlled histories must differ"
            )
        if self.clock_id != _CLOCK_ID or self.ticks_per_second != _TICKS_PER_SECOND:
            raise MCMF3ControlledHistorySourceError("controlled history clock changed")
        for sequences in (self.same_history, self.changed_history, self.shared_probe):
            if tuple(item.modality_id for item in sequences) != (
                "auditory",
                "visual",
            ):
                raise MCMF3ControlledHistorySourceError(
                    "every controlled input requires audio and video"
                )
        if self.same_history[0].frames[-1].field_time.window_end_tick != 3_000_000:
            raise MCMF3ControlledHistorySourceError("history duration changed")
        if (
            self.shared_probe[0].frames[0].field_time.window_start_tick < 3_000_000
            or self.shared_probe[-1].frames[-1].field_time.window_end_tick
            != 4_000_000
        ):
            raise MCMF3ControlledHistorySourceError("shared probe interval changed")


def build_mcm_f3_controlled_history_inputs() -> MCMF3ControlledHistoryInputs:
    """Reduce both histories separately and the common probe exactly once."""

    same, changed = controlled_history_holdout_world_family()
    same_history = _history_sequences(same)
    changed_history = _history_sequences(changed)
    shared_probe = _shared_probe_sequences(same)
    return MCMF3ControlledHistoryInputs(
        same_world_digest=same.digest(),
        changed_world_digest=changed.digest(),
        same_history=same_history,
        changed_history=changed_history,
        shared_probe=shared_probe,
        same_history_digest=mcm_f3_receptor_sequences_digest(same_history),
        changed_history_digest=mcm_f3_receptor_sequences_digest(changed_history),
        shared_probe_digest=mcm_f3_receptor_sequences_digest(shared_probe),
        clock_id=_CLOCK_ID,
        ticks_per_second=_TICKS_PER_SECOND,
    )


def mcm_f3_controlled_history_source_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(MCMF3ControlledHistoryInputs))
