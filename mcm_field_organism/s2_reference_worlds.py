"""Canonical controlled worlds and task inventory for S2 reference work."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from .controlled_audio_video_test_world import (
    ControlledAudioVideoTestWorld,
    ControlledWorldPhase,
    reduce_controlled_test_world_sequences,
)
from .field_step_time import MCMFieldStepTime
from .finite_video_path import VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig
from .receptor_time_alignment import ReceptorTimeSequence


class S2ReferenceWorldError(ValueError):
    """Raised when the preregistered S2 world inventory is violated."""


S2_WORLD_IDS = (
    "r1.a",
    "c1.a",
    "r2.a",
    "c2.a",
    "r4.a",
    "c4.a",
    "r8.a",
    "c8.a",
    "r8.b",
    "c8.b",
    "n8",
)
S2_MODEL_IDS = ("b0", "b1", "b2", "b3", "b4", "b5")
S2_INTERVENTION_WORLD_IDS = ("r8.a", "c8.a", "r8.b", "c8.b", "n8")
S2_SWAP_PARTNERS = {
    "r8.a": "r8.b",
    "r8.b": "r8.a",
    "c8.a": "c8.b",
    "c8.b": "c8.a",
    "n8": "n8",
}


def _canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _configs() -> tuple[LogSpectralConfig, VisualGridConfig]:
    return (
        LogSpectralConfig(
            sample_rate=4000,
            window_size=400,
            hop_size=40,
            min_frequency=50.0,
            max_frequency=1500.0,
            band_count=12,
        ),
        VisualGridConfig(
            source_width=24,
            source_height=16,
            grid_columns=6,
            grid_rows=4,
            frames_per_second=10.0,
        ),
    )


def _phase(phase_id: str, duration: float, contact: str) -> ControlledWorldPhase:
    if contact == "a":
        return ControlledWorldPhase(
            phase_id,
            duration,
            320.0,
            0.25,
            (2, 3),
            (0, 0),
            (6, 5),
            (220, 70, 45),
        )
    if contact == "b":
        return ControlledWorldPhase(
            phase_id,
            duration,
            760.0,
            0.25,
            (15, 8),
            (0, 0),
            (6, 5),
            (45, 120, 230),
        )
    if contact == "n":
        return ControlledWorldPhase(
            phase_id,
            duration,
            0.0,
            0.0,
            (0, 0),
            (0, 0),
            (1, 1),
            (16, 16, 16),
        )
    raise S2ReferenceWorldError(f"unknown S2 contact: {contact}")


def _split_neutral_duration(duration: float) -> tuple[float, ...]:
    """Return AV-compatible neutral phases whose sum is the requested span."""

    units = round(duration / 0.2)
    if not math.isclose(duration, units * 0.2, abs_tol=1e-12):
        raise S2ReferenceWorldError("neutral duration must use 0.2-s units")
    return () if units == 0 else (units * 0.2,)


def _world(world_id: str) -> ControlledAudioVideoTestWorld:
    audio_config, visual_config = _configs()
    if world_id == "n8":
        phases = (_phase("neutral.0", 8.0, "n"),)
    else:
        mode, address = world_id.split(".", maxsplit=1)
        count = int(mode[1:])
        contact = address
        block_duration = (
            count * 0.4 if mode.startswith("c") else (2 * count - 1) * 0.4
        )
        side_duration = (8.0 - block_duration) / 2.0
        phases_out: list[ControlledWorldPhase] = []
        for duration in _split_neutral_duration(side_duration):
            phases_out.append(_phase("neutral.pre", duration, "n"))
        if mode.startswith("c"):
            phases_out.append(_phase("contact.0", count * 0.4, contact))
        else:
            for index in range(count):
                phases_out.append(_phase(f"contact.{index}", 0.4, contact))
                if index + 1 < count:
                    phases_out.append(_phase(f"neutral.gap.{index}", 0.4, "n"))
        for duration in _split_neutral_duration(side_duration):
            phases_out.append(_phase("neutral.post", duration, "n"))
        phases = tuple(phases_out)
    return ControlledAudioVideoTestWorld(
        f"s2.{world_id}",
        phases,
        audio_config,
        visual_config,
        (16, 16, 16),
    )


def build_s2_reference_worlds() -> tuple[ControlledAudioVideoTestWorld, ...]:
    worlds = tuple(_world(world_id) for world_id in S2_WORLD_IDS)
    if tuple(world.world_id.removeprefix("s2.") for world in worlds) != S2_WORLD_IDS:
        raise S2ReferenceWorldError("S2 worlds must use canonical order")
    if any(not math.isclose(world.duration_seconds, 8.0) for world in worlds):
        raise S2ReferenceWorldError("every S2 formation world must last 8.0 s")
    return worlds


def build_s2_probe_world() -> ControlledAudioVideoTestWorld:
    audio_config, visual_config = _configs()
    return ControlledAudioVideoTestWorld(
        "s2.probe.p",
        (
            ControlledWorldPhase(
                "probe.0",
                0.4,
                1120.0,
                0.20,
                (8, 2),
                (0, 0),
                (5, 6),
                (65, 210, 105),
            ),
        ),
        audio_config,
        visual_config,
        (16, 16, 16),
    )


@dataclass(frozen=True, slots=True)
class S2ReferenceTask:
    task_id: str
    kind: str
    world_id: str
    model_id: str
    intervention_id: str

    def canonical_payload(self) -> dict[str, str]:
        return {
            "task_id": self.task_id,
            "kind": self.kind,
            "world_id": self.world_id,
            "model_id": self.model_id,
            "intervention_id": self.intervention_id,
        }


def build_s2_reference_tasks() -> tuple[S2ReferenceTask, ...]:
    tasks: list[S2ReferenceTask] = []
    for world_id in S2_WORLD_IDS:
        for model_id in S2_MODEL_IDS:
            tasks.append(
                S2ReferenceTask(
                    f"main.{world_id}.{model_id}",
                    "main",
                    world_id,
                    model_id,
                    "intact",
                )
            )
    for world_id in S2_INTERVENTION_WORLD_IDS:
        for intervention_id in ("swap", "neutral", "resume"):
            tasks.append(
                S2ReferenceTask(
                    f"intervention.{world_id}.b2.{intervention_id}",
                    "intervention",
                    world_id,
                    "b2",
                    intervention_id,
                )
            )
    for world_id in S2_INTERVENTION_WORLD_IDS:
        tasks.append(
            S2ReferenceTask(
                f"observer.{world_id}.b2.off",
                "observer",
                world_id,
                "b2",
                "observer-off",
            )
        )
    for world_id in S2_WORLD_IDS:
        for model_id in S2_MODEL_IDS:
            tasks.append(
                S2ReferenceTask(
                    f"reproduction.{world_id}.{model_id}",
                    "reproduction",
                    world_id,
                    model_id,
                    "intact",
                )
            )
    result = tuple(tasks)
    if len(result) != 152 or len({task.task_id for task in result}) != 152:
        raise S2ReferenceWorldError("S2 requires 152 unique logical tasks")
    return result


def s2_reference_inventory_digest() -> str:
    return _canonical_digest(
        {
            "worlds": [
                world.canonical_payload() for world in build_s2_reference_worlds()
            ],
            "probe": build_s2_probe_world().canonical_payload(),
            "tasks": [task.canonical_payload() for task in build_s2_reference_tasks()],
            "swap_partners": S2_SWAP_PARTNERS,
        }
    )


def _sequence_digest(sequence: ReceptorTimeSequence) -> str:
    return _canonical_digest(
        {
            "modality_id": sequence.modality_id,
            "geometry_id": sequence.geometry_id,
            "clock_id": sequence.clock_id,
            "frames": [
                {
                    "snapshot_id": item.frame.snapshot_id,
                    "field_start": item.field_time.window_start_tick,
                    "field_end": item.field_time.window_end_tick,
                    "carrier_ids": item.frame.carrier_ids,
                    "values": item.frame.values,
                }
                for item in sequence.frames
            ],
        }
    )


@dataclass(frozen=True, slots=True)
class S2PreparedWorldPlan:
    world_id: str
    world_digest: str
    sequence_digests: tuple[str, str]
    start_seconds: float
    clock_id: str
    ticks_per_second: float
    receptor_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    proposal_steps: tuple[MCMFieldStepTime, ...]

    def __post_init__(self) -> None:
        if self.world_id != "r1.a":
            raise S2ReferenceWorldError("S2-C3 permits only world r1.a")
        digests = (self.world_digest, *self.sequence_digests)
        if not all(
            len(item) == 64 and all(character in "0123456789abcdef" for character in item)
            for item in digests
        ):
            raise S2ReferenceWorldError("prepared world digests are invalid")
        if self.world_digest != _world("r1.a").digest():
            raise S2ReferenceWorldError("prepared world digest is not canonical r1.a")
        start = float(self.start_seconds)
        rate = float(self.ticks_per_second)
        if not math.isfinite(start) or start < 0.0:
            raise S2ReferenceWorldError("prepared world start is invalid")
        if not math.isfinite(rate) or rate <= 0.0:
            raise S2ReferenceWorldError("prepared world tick rate is invalid")
        sequences = tuple(self.receptor_sequences)
        if tuple(item.modality_id for item in sequences) != ("auditory", "visual"):
            raise S2ReferenceWorldError("prepared world requires auditory and visual sequences")
        if tuple(_sequence_digest(item) for item in sequences) != self.sequence_digests:
            raise S2ReferenceWorldError("prepared world sequence digests differ")
        steps = tuple(self.proposal_steps)
        if len(steps) != 3 or any(step.clock_id != self.clock_id for step in steps):
            raise S2ReferenceWorldError("prepared world steps must share one clock")
        if any(step.ticks_per_second != rate for step in steps):
            raise S2ReferenceWorldError("prepared world steps must share one rate")
        if any(first.end_tick != second.start_tick for first, second in zip(steps, steps[1:])):
            raise S2ReferenceWorldError("prepared world steps must be contiguous")
        expected_start = round(start * rate)
        expected_end = expected_start + round(8.0 * rate)
        if steps[0].start_tick != expected_start or steps[-1].end_tick != expected_end:
            raise S2ReferenceWorldError("prepared world horizon differs from r1.a")
        object.__setattr__(self, "start_seconds", start)
        object.__setattr__(self, "ticks_per_second", rate)
        object.__setattr__(self, "receptor_sequences", sequences)
        object.__setattr__(self, "proposal_steps", steps)

    @property
    def source_support_count(self) -> int:
        return sum(len(sequence.frames) for sequence in self.receptor_sequences)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "world_id": self.world_id,
            "world_digest": self.world_digest,
            "sequence_digests": list(self.sequence_digests),
            "start_seconds": self.start_seconds,
            "clock_id": self.clock_id,
            "ticks_per_second": self.ticks_per_second,
            "source_support_count": self.source_support_count,
            "steps": [
                {
                    "start_tick": step.start_tick,
                    "end_tick": step.end_tick,
                }
                for step in self.proposal_steps
            ],
        }

    def digest(self) -> str:
        return _canonical_digest(self.canonical_payload())


def prepare_s2c3_r1_receptor_plan(
    *,
    start_seconds: float = 0.0,
    clock_id: str = "organism.s2.reference",
    ticks_per_second: float = 1_000_000.0,
) -> S2PreparedWorldPlan:
    """Reduce only canonical r1.a and bind its phase-sized proposal steps."""

    world = _world("r1.a")
    sequences = reduce_controlled_test_world_sequences(
        world,
        start_seconds=start_seconds,
        clock_id=clock_id,
        ticks_per_second=ticks_per_second,
    )
    start_tick = round(float(start_seconds) * float(ticks_per_second))
    cursor = start_tick
    steps = []
    for phase in world.phases:
        end = cursor + round(phase.duration_seconds * float(ticks_per_second))
        steps.append(MCMFieldStepTime(clock_id, cursor, end, ticks_per_second))
        cursor = end
    return S2PreparedWorldPlan(
        world_id="r1.a",
        world_digest=world.digest(),
        sequence_digests=tuple(_sequence_digest(item) for item in sequences),
        start_seconds=float(start_seconds),
        clock_id=clock_id,
        ticks_per_second=float(ticks_per_second),
        receptor_sequences=sequences,
        proposal_steps=tuple(steps),
    )


@dataclass(frozen=True, slots=True)
class S2PreparedC1Plan:
    world_id: str
    world_digest: str
    sequence_digests: tuple[str, str]
    clock_id: str
    ticks_per_second: float
    receptor_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    proposal_steps: tuple[MCMFieldStepTime, ...]

    def __post_init__(self) -> None:
        if self.world_id != "c1.a":
            raise S2ReferenceWorldError("S2-C8 permits only world c1.a")
        digests = (self.world_digest, *self.sequence_digests)
        if not all(
            len(item) == 64
            and all(character in "0123456789abcdef" for character in item)
            for item in digests
        ):
            raise S2ReferenceWorldError("prepared c1.a digests are invalid")
        if self.world_digest != _world("c1.a").digest():
            raise S2ReferenceWorldError("prepared world digest is not canonical c1.a")
        rate = float(self.ticks_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise S2ReferenceWorldError("prepared c1.a tick rate is invalid")
        sequences = tuple(self.receptor_sequences)
        if tuple(item.modality_id for item in sequences) != ("auditory", "visual"):
            raise S2ReferenceWorldError("prepared c1.a requires auditory and visual sequences")
        if tuple(_sequence_digest(item) for item in sequences) != self.sequence_digests:
            raise S2ReferenceWorldError("prepared c1.a sequence digests differ")
        steps = tuple(self.proposal_steps)
        if len(steps) != 3 or any(step.clock_id != self.clock_id for step in steps):
            raise S2ReferenceWorldError("prepared c1.a requires three steps on one clock")
        if any(step.ticks_per_second != rate for step in steps):
            raise S2ReferenceWorldError("prepared c1.a steps must share one rate")
        if any(
            first.end_tick != second.start_tick
            for first, second in zip(steps, steps[1:])
        ):
            raise S2ReferenceWorldError("prepared c1.a steps must be contiguous")
        if steps[0].start_tick != 0 or steps[-1].end_tick != round(8.0 * rate):
            raise S2ReferenceWorldError("prepared c1.a must span 0.0 through 8.0 s")
        object.__setattr__(self, "ticks_per_second", rate)
        object.__setattr__(self, "receptor_sequences", sequences)
        object.__setattr__(self, "proposal_steps", steps)

    @property
    def source_support_count(self) -> int:
        return sum(len(sequence.frames) for sequence in self.receptor_sequences)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "world_id": self.world_id,
            "world_digest": self.world_digest,
            "sequence_digests": list(self.sequence_digests),
            "clock_id": self.clock_id,
            "ticks_per_second": self.ticks_per_second,
            "source_support_count": self.source_support_count,
            "steps": [
                {"start_tick": step.start_tick, "end_tick": step.end_tick}
                for step in self.proposal_steps
            ],
        }

    def digest(self) -> str:
        return _canonical_digest(self.canonical_payload())


def prepare_s2c8_c1_receptor_plan(
    *,
    clock_id: str = "organism.s2.reference",
    ticks_per_second: float = 1_000_000.0,
) -> S2PreparedC1Plan:
    """Reduce only canonical c1.a at the fixed 0.0-through-8.0-s horizon."""

    world = _world("c1.a")
    sequences = reduce_controlled_test_world_sequences(
        world,
        start_seconds=0.0,
        clock_id=clock_id,
        ticks_per_second=ticks_per_second,
    )
    cursor = 0
    steps = []
    for phase in world.phases:
        end = cursor + round(phase.duration_seconds * float(ticks_per_second))
        steps.append(MCMFieldStepTime(clock_id, cursor, end, ticks_per_second))
        cursor = end
    return S2PreparedC1Plan(
        world_id="c1.a",
        world_digest=world.digest(),
        sequence_digests=tuple(_sequence_digest(item) for item in sequences),
        clock_id=clock_id,
        ticks_per_second=float(ticks_per_second),
        receptor_sequences=sequences,
        proposal_steps=tuple(steps),
    )


@dataclass(frozen=True, slots=True)
class S2PreparedR2C2Plan:
    world_id: str
    world_digest: str
    sequence_digests: tuple[str, str]
    clock_id: str
    ticks_per_second: float
    receptor_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    proposal_steps: tuple[MCMFieldStepTime, ...]

    def __post_init__(self) -> None:
        if self.world_id not in ("r2.a", "c2.a"):
            raise S2ReferenceWorldError("S2-C9 permits only r2.a or c2.a")
        digests = (self.world_digest, *self.sequence_digests)
        if not all(
            len(item) == 64
            and all(character in "0123456789abcdef" for character in item)
            for item in digests
        ):
            raise S2ReferenceWorldError("prepared r2/c2 digests are invalid")
        if self.world_digest != _world(self.world_id).digest():
            raise S2ReferenceWorldError("prepared world digest is not canonical r2/c2")
        rate = float(self.ticks_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise S2ReferenceWorldError("prepared r2/c2 tick rate is invalid")
        sequences = tuple(self.receptor_sequences)
        if tuple(item.modality_id for item in sequences) != ("auditory", "visual"):
            raise S2ReferenceWorldError("prepared r2/c2 requires auditory and visual sequences")
        if tuple(_sequence_digest(item) for item in sequences) != self.sequence_digests:
            raise S2ReferenceWorldError("prepared r2/c2 sequence digests differ")
        steps = tuple(self.proposal_steps)
        expected_count = 5 if self.world_id == "r2.a" else 3
        if len(steps) != expected_count or any(
            step.clock_id != self.clock_id for step in steps
        ):
            raise S2ReferenceWorldError("prepared r2/c2 phase count or clock differs")
        if any(step.ticks_per_second != rate for step in steps):
            raise S2ReferenceWorldError("prepared r2/c2 steps must share one rate")
        if any(
            first.end_tick != second.start_tick
            for first, second in zip(steps, steps[1:])
        ):
            raise S2ReferenceWorldError("prepared r2/c2 steps must be contiguous")
        if steps[0].start_tick != 0 or steps[-1].end_tick != round(8.0 * rate):
            raise S2ReferenceWorldError("prepared r2/c2 must span 0.0 through 8.0 s")
        object.__setattr__(self, "ticks_per_second", rate)
        object.__setattr__(self, "receptor_sequences", sequences)
        object.__setattr__(self, "proposal_steps", steps)

    @property
    def source_support_count(self) -> int:
        return sum(len(sequence.frames) for sequence in self.receptor_sequences)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "world_id": self.world_id,
            "world_digest": self.world_digest,
            "sequence_digests": list(self.sequence_digests),
            "clock_id": self.clock_id,
            "ticks_per_second": self.ticks_per_second,
            "source_support_count": self.source_support_count,
            "steps": [
                {"start_tick": step.start_tick, "end_tick": step.end_tick}
                for step in self.proposal_steps
            ],
        }

    def digest(self) -> str:
        return _canonical_digest(self.canonical_payload())


def prepare_s2c9_r2c2_receptor_plans(
    *,
    clock_id: str = "organism.s2.reference",
    ticks_per_second: float = 1_000_000.0,
) -> tuple[S2PreparedR2C2Plan, S2PreparedR2C2Plan]:
    """Reduce only canonical r2.a and c2.a on one fixed eight-second clock."""

    plans = []
    for world_id in ("r2.a", "c2.a"):
        world = _world(world_id)
        sequences = reduce_controlled_test_world_sequences(
            world,
            start_seconds=0.0,
            clock_id=clock_id,
            ticks_per_second=ticks_per_second,
        )
        cursor = 0
        steps = []
        for phase in world.phases:
            end = cursor + round(phase.duration_seconds * float(ticks_per_second))
            steps.append(MCMFieldStepTime(clock_id, cursor, end, ticks_per_second))
            cursor = end
        plans.append(
            S2PreparedR2C2Plan(
                world_id=world_id,
                world_digest=world.digest(),
                sequence_digests=tuple(_sequence_digest(item) for item in sequences),
                clock_id=clock_id,
                ticks_per_second=float(ticks_per_second),
                receptor_sequences=sequences,
                proposal_steps=tuple(steps),
            )
        )
    return plans[0], plans[1]


@dataclass(frozen=True, slots=True)
class S2PreparedR4C4Plan:
    world_id: str
    world_digest: str
    sequence_digests: tuple[str, str]
    clock_id: str
    ticks_per_second: float
    receptor_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    proposal_steps: tuple[MCMFieldStepTime, ...]

    def __post_init__(self) -> None:
        if self.world_id not in ("r4.a", "c4.a"):
            raise S2ReferenceWorldError("S2-C10 permits only r4.a or c4.a")
        digests = (self.world_digest, *self.sequence_digests)
        if not all(
            len(item) == 64
            and all(character in "0123456789abcdef" for character in item)
            for item in digests
        ):
            raise S2ReferenceWorldError("prepared r4/c4 digests are invalid")
        if self.world_digest != _world(self.world_id).digest():
            raise S2ReferenceWorldError("prepared world digest is not canonical r4/c4")
        rate = float(self.ticks_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise S2ReferenceWorldError("prepared r4/c4 tick rate is invalid")
        sequences = tuple(self.receptor_sequences)
        if tuple(item.modality_id for item in sequences) != ("auditory", "visual"):
            raise S2ReferenceWorldError("prepared r4/c4 requires auditory and visual sequences")
        if tuple(_sequence_digest(item) for item in sequences) != self.sequence_digests:
            raise S2ReferenceWorldError("prepared r4/c4 sequence digests differ")
        steps = tuple(self.proposal_steps)
        expected_count = 9 if self.world_id == "r4.a" else 3
        if len(steps) != expected_count or any(
            step.clock_id != self.clock_id for step in steps
        ):
            raise S2ReferenceWorldError("prepared r4/c4 phase count or clock differs")
        if any(step.ticks_per_second != rate for step in steps):
            raise S2ReferenceWorldError("prepared r4/c4 steps must share one rate")
        if any(
            first.end_tick != second.start_tick
            for first, second in zip(steps, steps[1:])
        ):
            raise S2ReferenceWorldError("prepared r4/c4 steps must be contiguous")
        if steps[0].start_tick != 0 or steps[-1].end_tick != round(8.0 * rate):
            raise S2ReferenceWorldError("prepared r4/c4 must span 0.0 through 8.0 s")
        object.__setattr__(self, "ticks_per_second", rate)
        object.__setattr__(self, "receptor_sequences", sequences)
        object.__setattr__(self, "proposal_steps", steps)

    @property
    def source_support_count(self) -> int:
        return sum(len(sequence.frames) for sequence in self.receptor_sequences)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "world_id": self.world_id,
            "world_digest": self.world_digest,
            "sequence_digests": list(self.sequence_digests),
            "clock_id": self.clock_id,
            "ticks_per_second": self.ticks_per_second,
            "source_support_count": self.source_support_count,
            "steps": [
                {"start_tick": step.start_tick, "end_tick": step.end_tick}
                for step in self.proposal_steps
            ],
        }

    def digest(self) -> str:
        return _canonical_digest(self.canonical_payload())


def prepare_s2c10_r4c4_receptor_plans(
    *,
    clock_id: str = "organism.s2.reference",
    ticks_per_second: float = 1_000_000.0,
) -> tuple[S2PreparedR4C4Plan, S2PreparedR4C4Plan]:
    """Reduce only canonical r4.a and c4.a on one fixed eight-second clock."""

    plans = []
    for world_id in ("r4.a", "c4.a"):
        world = _world(world_id)
        sequences = reduce_controlled_test_world_sequences(
            world,
            start_seconds=0.0,
            clock_id=clock_id,
            ticks_per_second=ticks_per_second,
        )
        cursor = 0
        steps = []
        for phase in world.phases:
            end = cursor + round(phase.duration_seconds * float(ticks_per_second))
            steps.append(MCMFieldStepTime(clock_id, cursor, end, ticks_per_second))
            cursor = end
        plans.append(
            S2PreparedR4C4Plan(
                world_id=world_id,
                world_digest=world.digest(),
                sequence_digests=tuple(_sequence_digest(item) for item in sequences),
                clock_id=clock_id,
                ticks_per_second=float(ticks_per_second),
                receptor_sequences=sequences,
                proposal_steps=tuple(steps),
            )
        )
    return plans[0], plans[1]


@dataclass(frozen=True, slots=True)
class S2PreparedR8C8Plan:
    world_id: str
    world_digest: str
    sequence_digests: tuple[str, str]
    clock_id: str
    ticks_per_second: float
    receptor_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    proposal_steps: tuple[MCMFieldStepTime, ...]

    def __post_init__(self) -> None:
        if self.world_id not in ("r8.a", "c8.a"):
            raise S2ReferenceWorldError("S2-C11 permits only r8.a or c8.a")
        digests = (self.world_digest, *self.sequence_digests)
        if not all(
            len(item) == 64
            and all(character in "0123456789abcdef" for character in item)
            for item in digests
        ):
            raise S2ReferenceWorldError("prepared r8/c8 digests are invalid")
        if self.world_digest != _world(self.world_id).digest():
            raise S2ReferenceWorldError("prepared world digest is not canonical r8/c8")
        rate = float(self.ticks_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise S2ReferenceWorldError("prepared r8/c8 tick rate is invalid")
        sequences = tuple(self.receptor_sequences)
        if tuple(item.modality_id for item in sequences) != ("auditory", "visual"):
            raise S2ReferenceWorldError("prepared r8/c8 requires auditory and visual sequences")
        if tuple(_sequence_digest(item) for item in sequences) != self.sequence_digests:
            raise S2ReferenceWorldError("prepared r8/c8 sequence digests differ")
        steps = tuple(self.proposal_steps)
        expected_count = 17 if self.world_id == "r8.a" else 3
        if len(steps) != expected_count or any(
            step.clock_id != self.clock_id for step in steps
        ):
            raise S2ReferenceWorldError("prepared r8/c8 phase count or clock differs")
        if any(step.ticks_per_second != rate for step in steps):
            raise S2ReferenceWorldError("prepared r8/c8 steps must share one rate")
        if any(
            first.end_tick != second.start_tick
            for first, second in zip(steps, steps[1:])
        ):
            raise S2ReferenceWorldError("prepared r8/c8 steps must be contiguous")
        if steps[0].start_tick != 0 or steps[-1].end_tick != round(8.0 * rate):
            raise S2ReferenceWorldError("prepared r8/c8 must span 0.0 through 8.0 s")
        object.__setattr__(self, "ticks_per_second", rate)
        object.__setattr__(self, "receptor_sequences", sequences)
        object.__setattr__(self, "proposal_steps", steps)

    @property
    def source_support_count(self) -> int:
        return sum(len(sequence.frames) for sequence in self.receptor_sequences)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "world_id": self.world_id,
            "world_digest": self.world_digest,
            "sequence_digests": list(self.sequence_digests),
            "clock_id": self.clock_id,
            "ticks_per_second": self.ticks_per_second,
            "source_support_count": self.source_support_count,
            "steps": [
                {"start_tick": step.start_tick, "end_tick": step.end_tick}
                for step in self.proposal_steps
            ],
        }

    def digest(self) -> str:
        return _canonical_digest(self.canonical_payload())


def prepare_s2c11_r8c8_receptor_plans(
    *,
    clock_id: str = "organism.s2.reference",
    ticks_per_second: float = 1_000_000.0,
) -> tuple[S2PreparedR8C8Plan, S2PreparedR8C8Plan]:
    """Reduce only canonical r8.a and c8.a on one fixed eight-second clock."""

    plans = []
    for world_id in ("r8.a", "c8.a"):
        world = _world(world_id)
        sequences = reduce_controlled_test_world_sequences(
            world,
            start_seconds=0.0,
            clock_id=clock_id,
            ticks_per_second=ticks_per_second,
        )
        cursor = 0
        steps = []
        for phase in world.phases:
            end = cursor + round(phase.duration_seconds * float(ticks_per_second))
            steps.append(MCMFieldStepTime(clock_id, cursor, end, ticks_per_second))
            cursor = end
        plans.append(
            S2PreparedR8C8Plan(
                world_id=world_id,
                world_digest=world.digest(),
                sequence_digests=tuple(_sequence_digest(item) for item in sequences),
                clock_id=clock_id,
                ticks_per_second=float(ticks_per_second),
                receptor_sequences=sequences,
                proposal_steps=tuple(steps),
            )
        )
    return plans[0], plans[1]


@dataclass(frozen=True, slots=True)
class S2PreparedR8BC8BPlan:
    world_id: str
    world_digest: str
    sequence_digests: tuple[str, str]
    clock_id: str
    ticks_per_second: float
    receptor_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    proposal_steps: tuple[MCMFieldStepTime, ...]

    def __post_init__(self) -> None:
        if self.world_id not in ("r8.b", "c8.b"):
            raise S2ReferenceWorldError("S2-C13 permits only r8.b or c8.b")
        digests = (self.world_digest, *self.sequence_digests)
        if not all(
            len(item) == 64
            and all(character in "0123456789abcdef" for character in item)
            for item in digests
        ):
            raise S2ReferenceWorldError("prepared r8.b/c8.b digests are invalid")
        if self.world_digest != _world(self.world_id).digest():
            raise S2ReferenceWorldError("prepared world digest is not canonical r8.b/c8.b")
        rate = float(self.ticks_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise S2ReferenceWorldError("prepared r8.b/c8.b tick rate is invalid")
        sequences = tuple(self.receptor_sequences)
        if tuple(item.modality_id for item in sequences) != ("auditory", "visual"):
            raise S2ReferenceWorldError("prepared r8.b/c8.b requires auditory and visual sequences")
        if tuple(_sequence_digest(item) for item in sequences) != self.sequence_digests:
            raise S2ReferenceWorldError("prepared r8.b/c8.b sequence digests differ")
        steps = tuple(self.proposal_steps)
        expected_count = 17 if self.world_id == "r8.b" else 3
        if len(steps) != expected_count or any(
            step.clock_id != self.clock_id for step in steps
        ):
            raise S2ReferenceWorldError("prepared r8.b/c8.b phase count or clock differs")
        if any(step.ticks_per_second != rate for step in steps):
            raise S2ReferenceWorldError("prepared r8.b/c8.b steps must share one rate")
        if any(
            first.end_tick != second.start_tick
            for first, second in zip(steps, steps[1:])
        ):
            raise S2ReferenceWorldError("prepared r8.b/c8.b steps must be contiguous")
        if steps[0].start_tick != 0 or steps[-1].end_tick != round(8.0 * rate):
            raise S2ReferenceWorldError("prepared r8.b/c8.b must span 0.0 through 8.0 s")
        object.__setattr__(self, "ticks_per_second", rate)
        object.__setattr__(self, "receptor_sequences", sequences)
        object.__setattr__(self, "proposal_steps", steps)

    @property
    def source_support_count(self) -> int:
        return sum(len(sequence.frames) for sequence in self.receptor_sequences)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "world_id": self.world_id,
            "world_digest": self.world_digest,
            "sequence_digests": list(self.sequence_digests),
            "clock_id": self.clock_id,
            "ticks_per_second": self.ticks_per_second,
            "source_support_count": self.source_support_count,
            "steps": [
                {"start_tick": step.start_tick, "end_tick": step.end_tick}
                for step in self.proposal_steps
            ],
        }

    def digest(self) -> str:
        return _canonical_digest(self.canonical_payload())


def prepare_s2c13_r8bc8b_receptor_plans(
    *,
    clock_id: str = "organism.s2.reference",
    ticks_per_second: float = 1_000_000.0,
) -> tuple[S2PreparedR8BC8BPlan, S2PreparedR8BC8BPlan]:
    """Reduce only canonical r8.b and c8.b on one fixed eight-second clock."""

    plans = []
    for world_id in ("r8.b", "c8.b"):
        world = _world(world_id)
        sequences = reduce_controlled_test_world_sequences(
            world,
            start_seconds=0.0,
            clock_id=clock_id,
            ticks_per_second=ticks_per_second,
        )
        cursor = 0
        steps = []
        for phase in world.phases:
            end = cursor + round(phase.duration_seconds * float(ticks_per_second))
            steps.append(MCMFieldStepTime(clock_id, cursor, end, ticks_per_second))
            cursor = end
        plans.append(
            S2PreparedR8BC8BPlan(
                world_id=world_id,
                world_digest=world.digest(),
                sequence_digests=tuple(_sequence_digest(item) for item in sequences),
                clock_id=clock_id,
                ticks_per_second=float(ticks_per_second),
                receptor_sequences=sequences,
                proposal_steps=tuple(steps),
            )
        )
    return plans[0], plans[1]


@dataclass(frozen=True, slots=True)
class S2PreparedN8Plan:
    world_id: str
    world_digest: str
    sequence_digests: tuple[str, str]
    clock_id: str
    ticks_per_second: float
    receptor_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    proposal_step: MCMFieldStepTime

    def __post_init__(self) -> None:
        if self.world_id != "n8":
            raise S2ReferenceWorldError("S2-C5 permits only world n8")
        digests = (self.world_digest, *self.sequence_digests)
        if not all(
            len(item) == 64
            and all(character in "0123456789abcdef" for character in item)
            for item in digests
        ):
            raise S2ReferenceWorldError("prepared n8 digests are invalid")
        if self.world_digest != _world("n8").digest():
            raise S2ReferenceWorldError("prepared world digest is not canonical n8")
        rate = float(self.ticks_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise S2ReferenceWorldError("prepared n8 tick rate is invalid")
        sequences = tuple(self.receptor_sequences)
        if tuple(item.modality_id for item in sequences) != ("auditory", "visual"):
            raise S2ReferenceWorldError("prepared n8 requires auditory and visual sequences")
        if tuple(_sequence_digest(item) for item in sequences) != self.sequence_digests:
            raise S2ReferenceWorldError("prepared n8 sequence digests differ")
        if not isinstance(self.proposal_step, MCMFieldStepTime):
            raise S2ReferenceWorldError("prepared n8 requires one proposal step")
        if (
            self.proposal_step.clock_id != self.clock_id
            or self.proposal_step.ticks_per_second != rate
            or self.proposal_step.start_tick != 0
            or self.proposal_step.end_tick != round(8.0 * rate)
        ):
            raise S2ReferenceWorldError("prepared n8 must span 0.0 through 8.0 s")
        object.__setattr__(self, "ticks_per_second", rate)
        object.__setattr__(self, "receptor_sequences", sequences)

    @property
    def source_support_count(self) -> int:
        return sum(len(sequence.frames) for sequence in self.receptor_sequences)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "world_id": self.world_id,
            "world_digest": self.world_digest,
            "sequence_digests": list(self.sequence_digests),
            "clock_id": self.clock_id,
            "ticks_per_second": self.ticks_per_second,
            "source_support_count": self.source_support_count,
            "start_tick": self.proposal_step.start_tick,
            "end_tick": self.proposal_step.end_tick,
        }

    def digest(self) -> str:
        return _canonical_digest(self.canonical_payload())


def prepare_s2c5_n8_receptor_plan(
    *,
    clock_id: str = "organism.s2.reference",
    ticks_per_second: float = 1_000_000.0,
) -> S2PreparedN8Plan:
    """Reduce only canonical n8 at the fixed 0.0-through-8.0-s horizon."""

    world = _world("n8")
    sequences = reduce_controlled_test_world_sequences(
        world,
        start_seconds=0.0,
        clock_id=clock_id,
        ticks_per_second=ticks_per_second,
    )
    return S2PreparedN8Plan(
        world_id="n8",
        world_digest=world.digest(),
        sequence_digests=tuple(_sequence_digest(item) for item in sequences),
        clock_id=clock_id,
        ticks_per_second=float(ticks_per_second),
        receptor_sequences=sequences,
        proposal_step=MCMFieldStepTime(
            clock_id,
            0,
            round(8.0 * float(ticks_per_second)),
            ticks_per_second,
        ),
    )


@dataclass(frozen=True, slots=True)
class S2PreparedProbePlan:
    probe_digest: str
    sequence_digests: tuple[str, str]
    clock_id: str
    ticks_per_second: float
    receptor_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    proposal_step: MCMFieldStepTime

    def __post_init__(self) -> None:
        digests = (self.probe_digest, *self.sequence_digests)
        if not all(
            len(item) == 64
            and all(character in "0123456789abcdef" for character in item)
            for item in digests
        ):
            raise S2ReferenceWorldError("prepared probe digests are invalid")
        if self.probe_digest != build_s2_probe_world().digest():
            raise S2ReferenceWorldError("prepared probe digest is not canonical P")
        rate = float(self.ticks_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise S2ReferenceWorldError("prepared probe tick rate is invalid")
        sequences = tuple(self.receptor_sequences)
        if tuple(item.modality_id for item in sequences) != ("auditory", "visual"):
            raise S2ReferenceWorldError("prepared probe requires auditory and visual sequences")
        if tuple(_sequence_digest(item) for item in sequences) != self.sequence_digests:
            raise S2ReferenceWorldError("prepared probe sequence digests differ")
        if not isinstance(self.proposal_step, MCMFieldStepTime):
            raise S2ReferenceWorldError("prepared probe requires one proposal step")
        if (
            self.proposal_step.clock_id != self.clock_id
            or self.proposal_step.ticks_per_second != rate
            or self.proposal_step.start_tick != round(8.0 * rate)
            or self.proposal_step.end_tick != round(8.4 * rate)
        ):
            raise S2ReferenceWorldError("prepared probe must span 8.0 through 8.4 s")
        object.__setattr__(self, "ticks_per_second", rate)
        object.__setattr__(self, "receptor_sequences", sequences)

    @property
    def source_support_count(self) -> int:
        return sum(len(sequence.frames) for sequence in self.receptor_sequences)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "probe_digest": self.probe_digest,
            "sequence_digests": list(self.sequence_digests),
            "clock_id": self.clock_id,
            "ticks_per_second": self.ticks_per_second,
            "source_support_count": self.source_support_count,
            "start_tick": self.proposal_step.start_tick,
            "end_tick": self.proposal_step.end_tick,
        }

    def digest(self) -> str:
        return _canonical_digest(self.canonical_payload())


def prepare_s2c4_probe_plan(
    *,
    clock_id: str = "organism.s2.reference",
    ticks_per_second: float = 1_000_000.0,
) -> S2PreparedProbePlan:
    """Reduce only canonical probe P at the fixed 8.0-s continuation offset."""

    probe = build_s2_probe_world()
    sequences = reduce_controlled_test_world_sequences(
        probe,
        start_seconds=8.0,
        clock_id=clock_id,
        ticks_per_second=ticks_per_second,
    )
    return S2PreparedProbePlan(
        probe_digest=probe.digest(),
        sequence_digests=tuple(_sequence_digest(item) for item in sequences),
        clock_id=clock_id,
        ticks_per_second=float(ticks_per_second),
        receptor_sequences=sequences,
        proposal_step=MCMFieldStepTime(
            clock_id,
            round(8.0 * float(ticks_per_second)),
            round(8.4 * float(ticks_per_second)),
            ticks_per_second,
        ),
    )
