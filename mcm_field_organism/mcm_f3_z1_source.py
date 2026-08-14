"""Fixed source transformations for the Z1 field-trajectory audit."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .asynchronous_receptor_events import audit_asynchronous_receptor_events
from .controlled_audio_video_test_world import (
    ControlledAudioVideoTestWorld,
    ControlledWorldPhase,
    _base_configs,
    _scheduled_phase_sequences,
)
from .field_step_time import MCMFieldStepTime
from .field_time_partition import partition_receptor_completion_time
from .mcm_f3_controlled_history_source import mcm_f3_receptor_sequences_digest
from .receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


class MCMF3Z1SourceError(ValueError):
    """Raised when a Z1 source arm violates the preregistered transform."""


_CLOCK_ID = "organism.mcm_f3_z1"
_TICKS_PER_SECOND = 1_000_000.0
_REFERENCE_END_TICK = 1_000_000
_ARM_IDS = (
    "a.reference",
    "a.partitioned",
    "a.stretched",
    "a.compressed",
    "a.reversed",
    "a.permuted",
    "b.independent",
)
_BLOCK_ORDER = (0, 3, 2, 1)
_EXPECTED_ARM_CONTRACTS = {
    "a.reference": (
        "5e0afdb8a1861edd7732cb50a5f5c66a44a4bae96a6a177f2f9b28f49e259bb8",
        "23901add0b257a699b47acc9921d53c6865cbafa68fd5d583fbaa0bb033347d8",
        101,
        91,
        91,
        1_000_000,
    ),
    "a.partitioned": (
        "5e0afdb8a1861edd7732cb50a5f5c66a44a4bae96a6a177f2f9b28f49e259bb8",
        "7c1b4270b193ccebd2693f6efb808039c10fa5d5af9c4484a4b9787b1d253129",
        101,
        91,
        182,
        1_000_000,
    ),
    "a.stretched": (
        "4e17e0ebef71eb084cdd57cc37148d6033cf1e35cae54ec52446b72d0d4c1859",
        "b187ba724fa8f18617dd5ffda320c626821792410c76d3a36bd42624e278752c",
        101,
        91,
        91,
        2_000_000,
    ),
    "a.compressed": (
        "c3bf0c167acd64ddd602937c78b8f552183d51acf6aa46c36115f46c975055e2",
        "75991c488630bd5ce077b324b461deff9da2817037a962e1a402926171954a49",
        101,
        91,
        91,
        500_000,
    ),
    "a.reversed": (
        "6261285e07b55a2f47742d7848821e783eb46ec6b0b4be8559ed76f6873e09b0",
        "808a53aa2c889262197c50e2136aaf66a66e38e2d3e662f530e0955474c3a774",
        101,
        91,
        91,
        1_000_000,
    ),
    "a.permuted": (
        "1bb5806990d68873631a283da859d2bc48f450b3fecef8576af20bc3d1864247",
        "a765cc542ae0a871a5cc77b8f395cc443d3912ce5763365866dfa2ace3d84d8d",
        101,
        91,
        91,
        1_000_000,
    ),
    "b.independent": (
        "bc1cd6b64b84f1e6496f1e78d87528a46274fc170ede7ca8d93e019280ed826a",
        "bd582ba84c0b72270c201e0c593c74165cbce47ff03990e615b8bff1ba13ffb0",
        101,
        91,
        91,
        1_000_000,
    ),
}


@dataclass(frozen=True, slots=True)
class MCMF3Z1SourceArm:
    arm_id: str
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    proposal_steps: tuple[MCMFieldStepTime, ...]
    sequence_digest: str
    execution_digest: str
    event_count: int
    completion_group_count: int
    start_tick: int
    end_tick: int

    def __post_init__(self) -> None:
        if self.arm_id not in _ARM_IDS:
            raise MCMF3Z1SourceError("unknown Z1 source arm")
        if tuple(item.modality_id for item in self.sequences) != (
            "auditory",
            "visual",
        ):
            raise MCMF3Z1SourceError("Z1 source requires auditory and visual sequences")
        if not self.proposal_steps:
            raise MCMF3Z1SourceError("Z1 source requires proposal steps")
        if self.start_tick != 0 or self.end_tick <= self.start_tick:
            raise MCMF3Z1SourceError("Z1 source horizon changed")
        if self.proposal_steps[0].start_tick != self.start_tick:
            raise MCMF3Z1SourceError("Z1 proposal partition does not start at zero")
        if self.proposal_steps[-1].end_tick != self.end_tick:
            raise MCMF3Z1SourceError("Z1 proposal partition does not cover its horizon")
        for earlier, later in zip(self.proposal_steps, self.proposal_steps[1:]):
            if earlier.end_tick != later.start_tick:
                raise MCMF3Z1SourceError("Z1 proposal partition contains a gap")


@dataclass(frozen=True, slots=True)
class MCMF3Z1SourceSet:
    source_id: str
    clock_id: str
    ticks_per_second: float
    arms: tuple[MCMF3Z1SourceArm, ...]

    def __post_init__(self) -> None:
        if self.source_id != "mcm.f3.z1.controlled-av.v1":
            raise MCMF3Z1SourceError("Z1 source identity changed")
        if self.clock_id != _CLOCK_ID or self.ticks_per_second != _TICKS_PER_SECOND:
            raise MCMF3Z1SourceError("Z1 source clock changed")
        if tuple(item.arm_id for item in self.arms) != _ARM_IDS:
            raise MCMF3Z1SourceError("Z1 source arm inventory changed")

    def arm(self, arm_id: str) -> MCMF3Z1SourceArm:
        for item in self.arms:
            if item.arm_id == arm_id:
                return item
        raise KeyError(arm_id)


def _world(world_id: str, *, independent: bool) -> ControlledAudioVideoTestWorld:
    audio_config, visual_config = _base_configs()
    phase = (
        ControlledWorldPhase(
            "contact.0",
            1.0,
            760.0,
            0.25,
            (15, 8),
            (-1, 0),
            (6, 5),
            (45, 120, 230),
        )
        if independent
        else ControlledWorldPhase(
            "contact.0",
            1.0,
            320.0,
            0.25,
            (2, 3),
            (1, 0),
            (6, 5),
            (220, 70, 45),
        )
    )
    return ControlledAudioVideoTestWorld(
        world_id,
        (phase,),
        audio_config,
        visual_config,
    )


def _sequences(
    world: ControlledAudioVideoTestWorld,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    audio_source, video_source, auditory_path, visual_receptor = world.open_sources()
    return _scheduled_phase_sequences(
        world,
        world.phases[0],
        audio_source,
        video_source,
        auditory_path,
        visual_receptor,
        audio_frame_start=0,
        video_frame_start=0,
        clock_id=_CLOCK_ID,
        ticks_per_second=_TICKS_PER_SECOND,
    )


def _with_field_times(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    transform,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    transformed = []
    for sequence in sequences:
        frames = tuple(
            OrganismTimedReceptorFrame(item.frame, transform(item.field_time))
            for item in sequence.frames
        )
        transformed.append(
            ReceptorTimeSequence(
                sequence.modality_id,
                sequence.geometry_id,
                sequence.clock_id,
                frames,
            )
        )
    return tuple(transformed)  # type: ignore[return-value]


def _scaled(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    numerator: int,
    denominator: int,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    def transform(field_time):
        start_product = field_time.window_start_tick * numerator
        end_product = field_time.window_end_tick * numerator
        if start_product % denominator or end_product % denominator:
            raise MCMF3Z1SourceError("Z1 time scaling is not exact in clock ticks")
        return type(field_time)(
            field_time.clock_id,
            start_product // denominator,
            end_product // denominator,
        )

    return _with_field_times(sequences, transform)


def _reassigned(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    frame_order,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    transformed = []
    for sequence in sequences:
        source_frames = tuple(frame_order(sequence.frames))
        if len(source_frames) != len(sequence.frames):
            raise MCMF3Z1SourceError("Z1 frame transform changed event count")
        frames = tuple(
            OrganismTimedReceptorFrame(source.frame, target.field_time)
            for source, target in zip(source_frames, sequence.frames, strict=True)
        )
        transformed.append(
            ReceptorTimeSequence(
                sequence.modality_id,
                sequence.geometry_id,
                sequence.clock_id,
                frames,
            )
        )
    return tuple(transformed)  # type: ignore[return-value]


def _permuted_frames(frames):
    block_size = _REFERENCE_END_TICK // 4
    blocks = []
    for block_index in range(4):
        blocks.append(
            tuple(
                item
                for item in frames
                if min(
                    3,
                    (item.field_time.window_end_tick - 1) // block_size,
                )
                == block_index
            )
        )
    ordered = tuple(item for block in _BLOCK_ORDER for item in blocks[block])
    if len(ordered) != len(frames):
        raise MCMF3Z1SourceError("Z1 block permutation lost frames")
    target_sizes = tuple(len(block) for block in blocks)
    source_sizes = tuple(len(blocks[index]) for index in _BLOCK_ORDER)
    if target_sizes != source_sizes:
        raise MCMF3Z1SourceError("Z1 block permutation changed modality inventory")
    return ordered


def _completion_steps(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    end_tick: int,
) -> tuple[MCMFieldStepTime, ...]:
    return tuple(
        item.step_time
        for item in partition_receptor_completion_time(
            sequences,
            horizon_start_tick=0,
            horizon_end_tick=end_tick,
            ticks_per_second=_TICKS_PER_SECOND,
        ).slices
    )


def _split_steps(
    steps: tuple[MCMFieldStepTime, ...],
) -> tuple[MCMFieldStepTime, ...]:
    result = []
    for step in steps:
        middle = step.start_tick + step.elapsed_ticks // 2
        if middle <= step.start_tick or middle >= step.end_tick:
            raise MCMF3Z1SourceError("Z1 proposal step cannot be bisected")
        result.extend(
            (
                MCMFieldStepTime(
                    step.clock_id,
                    step.start_tick,
                    middle,
                    step.ticks_per_second,
                ),
                MCMFieldStepTime(
                    step.clock_id,
                    middle,
                    step.end_tick,
                    step.ticks_per_second,
                ),
            )
        )
    return tuple(result)


def _execution_digest(
    sequence_digest: str,
    steps: tuple[MCMFieldStepTime, ...],
) -> str:
    payload = {
        "sequence_digest": sequence_digest,
        "steps": [
            {
                "clock_id": item.clock_id,
                "start_tick": item.start_tick,
                "end_tick": item.end_tick,
                "ticks_per_second": item.ticks_per_second,
            }
            for item in steps
        ],
    }
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _arm(
    arm_id: str,
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    steps: tuple[MCMFieldStepTime, ...],
) -> MCMF3Z1SourceArm:
    audit = audit_asynchronous_receptor_events(sequences)
    sequence_digest = mcm_f3_receptor_sequences_digest(sequences)
    return MCMF3Z1SourceArm(
        arm_id,
        sequences,
        steps,
        sequence_digest,
        _execution_digest(sequence_digest, steps),
        audit.total_event_count,
        len(audit.completion_groups),
        steps[0].start_tick,
        steps[-1].end_tick,
    )


def build_mcm_f3_z1_source() -> MCMF3Z1SourceSet:
    """Build all preregistered Z1 source arms without advancing a field."""

    reference = _sequences(_world("world.z1.reference", independent=False))
    independent = _sequences(_world("world.z1.independent", independent=True))
    stretched = _scaled(reference, 2, 1)
    compressed = _scaled(reference, 1, 2)
    reversed_sequences = _reassigned(reference, lambda frames: reversed(frames))
    permuted = _reassigned(reference, _permuted_frames)

    reference_steps = _completion_steps(reference, _REFERENCE_END_TICK)
    arm_data = (
        ("a.reference", reference, reference_steps),
        ("a.partitioned", reference, _split_steps(reference_steps)),
        ("a.stretched", stretched, _completion_steps(stretched, 2_000_000)),
        ("a.compressed", compressed, _completion_steps(compressed, 500_000)),
        (
            "a.reversed",
            reversed_sequences,
            _completion_steps(reversed_sequences, _REFERENCE_END_TICK),
        ),
        ("a.permuted", permuted, _completion_steps(permuted, _REFERENCE_END_TICK)),
        (
            "b.independent",
            independent,
            _completion_steps(independent, _REFERENCE_END_TICK),
        ),
    )
    arms = tuple(_arm(*item) for item in arm_data)
    event_counts = {item.event_count for item in arms}
    if len(event_counts) != 1:
        raise MCMF3Z1SourceError("Z1 arms do not share one event budget")
    if arms[0].sequence_digest != arms[1].sequence_digest:
        raise MCMF3Z1SourceError("partition arm changed receptor sequences")
    observed_contracts = {
        item.arm_id: (
            item.sequence_digest,
            item.execution_digest,
            item.event_count,
            item.completion_group_count,
            len(item.proposal_steps),
            item.end_tick,
        )
        for item in arms
    }
    if observed_contracts != _EXPECTED_ARM_CONTRACTS:
        raise MCMF3Z1SourceError("Z1 source or execution digests changed")
    return MCMF3Z1SourceSet(
        "mcm.f3.z1.controlled-av.v1",
        _CLOCK_ID,
        _TICKS_PER_SECOND,
        arms,
    )


def mcm_f3_z1_source_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (MCMF3Z1SourceArm, MCMF3Z1SourceSet)
        for item in fields(cls)
    )
