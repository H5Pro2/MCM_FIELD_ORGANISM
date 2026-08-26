"""Fixed controlled source segments for the K2-B lifecycle baseline."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace

from .controlled_audio_video_test_world import (
    ControlledAudioVideoTestWorld,
    ControlledWorldPhase,
    _scheduled_phase_sequences,
    controlled_history_holdout_world_family,
)
from .mcm_f3_controlled_history_source import (
    _combine_phase_sequences,
    mcm_f3_receptor_sequences_digest,
)
from .receptor_time_alignment import ReceptorTimeSequence


class MCMF3K2BSourceError(ValueError):
    """Raised when a K2-B source segment loses its fixed timing contract."""


_CLOCK_ID = "organism.mcm_f3_k2b"
_TICKS_PER_SECOND = 1_000_000.0
_REPETITIONS = 4
_EXPECTED_CONTACT_A_DIGEST = "d1ca7803a6fa8ec93992933f8320252a6e0eb64ea2cab98784abadfa5e538953"
_EXPECTED_CONTACT_B_STEP_DIGESTS = (
    "5d38f7e13d996b1276484969c8dd05461bf1bc41cee2501c58199d4814184856",
    "2df447f0811c2ea471b12fc7e9dc3c0b23d2c18c6c9ffecb5498ac698b0e8a8b",
    "8f18e1eaf72fff07827ff255e1a521ecc45c4f73b012e4fa8740441bf983fea9",
    "3dd23501e0dd604712b8df5202ff36980e430fce79682080655469771c0aeee2",
)
_EXPECTED_INTERRUPTION_STEP_DIGESTS = (
    "209446fbd5c2652cc3aab3bfbe46739ebdd46baf27e248aca38cd6b5701a714c",
    "de950779d3674dc1dcaa6a2513bcbbe73b07ce9e2cfad297fcbfdb63f185c092",
    "70dcf7a43b787564312f3753ed4f07268fa8aae93bc6e9864d37f6f1ef3f2483",
    "1337395e1a8258899110db320afad12cd662775330ea7d5536ae5ff998f93436",
)
_EXPECTED_PROBE_DIGESTS = (
    "b975e8dc428c5ec93991b050c4949dc5dbaf08c5401c756b22a8aeca34579161",
    "1f50ee4bf57c374a85ddb2dc22238ba2fe59bc02771b2a375cffa33f5ed38574",
    "15c65c4610ce2070ba828e40e3f3ef14243f15d405f2760f43266d5133a0f192",
    "0ecac3d52c1a9c29088ee9c13255e2cdd836708bb46b4207124458054793bd4a",
    "783b9e29f0b16c482af54e8616a59ffb2b8bb3f7bce5fa6d3775e2845c64de43",
)


@dataclass(frozen=True, slots=True)
class MCMF3K2BSource:
    contact_a: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    contact_b_steps: tuple[
        tuple[ReceptorTimeSequence, ReceptorTimeSequence], ...
    ]
    interruption_steps: tuple[
        tuple[ReceptorTimeSequence, ReceptorTimeSequence], ...
    ]
    probes: tuple[tuple[ReceptorTimeSequence, ReceptorTimeSequence], ...]
    contact_a_digest: str
    contact_b_step_digests: tuple[str, ...]
    interruption_step_digests: tuple[str, ...]
    probe_digests: tuple[str, ...]
    clock_id: str
    ticks_per_second: float

    def __post_init__(self) -> None:
        if self.clock_id != _CLOCK_ID or self.ticks_per_second != _TICKS_PER_SECOND:
            raise MCMF3K2BSourceError("K2-B source clock changed")
        if not (
            len(self.contact_b_steps)
            == len(self.interruption_steps)
            == _REPETITIONS
            and len(self.probes) == _REPETITIONS + 1
        ):
            raise MCMF3K2BSourceError("K2-B checkpoint inventory changed")
        if not (
            len(self.contact_b_step_digests)
            == len(self.interruption_step_digests)
            == _REPETITIONS
            and len(self.probe_digests) == _REPETITIONS + 1
        ):
            raise MCMF3K2BSourceError("K2-B digest inventory changed")


def _phase_steps(
    phase: ControlledWorldPhase,
    template: ControlledAudioVideoTestWorld,
    *,
    world_id: str,
    start_second: int,
    repetitions: int,
    snapshot_namespace: str | None = None,
) -> tuple[tuple[ReceptorTimeSequence, ReceptorTimeSequence], ...]:
    phases = tuple(
        replace(phase, phase_id=f"{world_id}.{index}")
        for index in range(repetitions)
    )
    world = ControlledAudioVideoTestWorld(
        world_id,
        phases,
        template.audio_config,
        template.visual_config,
        template.background_channels,
    )
    audio_source, video_source, auditory_path, visual_receptor = world.open_sources()
    audio_cursor = round(start_second / world.audio_config.hop_seconds)
    video_cursor = round(start_second * world.visual_config.frames_per_second)
    result = []
    for current in world.phases:
        sequences = _scheduled_phase_sequences(
                world,
                current,
                audio_source,
                video_source,
                auditory_path,
                visual_receptor,
                audio_frame_start=audio_cursor,
                video_frame_start=video_cursor,
                clock_id=_CLOCK_ID,
                ticks_per_second=_TICKS_PER_SECOND,
            )
        if snapshot_namespace is not None:
            sequences = tuple(
                ReceptorTimeSequence(
                    sequence.modality_id,
                    sequence.geometry_id,
                    sequence.clock_id,
                    tuple(
                        replace(
                            item,
                            frame=replace(
                                item.frame,
                                snapshot_id=(
                                    f"{snapshot_namespace}."
                                    f"{item.frame.snapshot_id}"
                                ),
                            ),
                        )
                        for item in sequence.frames
                    ),
                )
                for sequence in sequences
            )
        result.append(sequences)
        audio_cursor += round(current.duration_seconds / world.audio_config.hop_seconds)
        video_cursor += round(
            current.duration_seconds * world.visual_config.frames_per_second
        )
    return tuple(result)


def build_mcm_f3_k2b_source() -> MCMF3K2BSource:
    """Reduce A, B, interruption and all checkpoint probes exactly once."""

    same, changed = controlled_history_holdout_world_family()
    contact_a_phase = same.phases[0]
    interruption_phase = same.phases[1]
    contact_b_phase = changed.phases[2]
    probe_phase = same.phases[-1]

    contact_a_steps = _phase_steps(
        contact_a_phase,
        same,
        world_id="k2b.contact-a",
        start_second=0,
        repetitions=_REPETITIONS,
    )
    contact_b_steps = _phase_steps(
        contact_b_phase,
        same,
        world_id="k2b.contact-b",
        start_second=_REPETITIONS,
        repetitions=_REPETITIONS,
    )
    interruption_steps = _phase_steps(
        interruption_phase,
        same,
        world_id="k2b.interruption",
        start_second=_REPETITIONS,
        repetitions=_REPETITIONS,
    )
    probes = tuple(
        _phase_steps(
            probe_phase,
            same,
            world_id=f"k2b.probe-{checkpoint}",
            start_second=_REPETITIONS + checkpoint,
            repetitions=1,
        )[0]
        for checkpoint in range(_REPETITIONS + 1)
    )
    contact_a = _combine_phase_sequences(contact_a_steps)
    result = MCMF3K2BSource(
        contact_a,
        contact_b_steps,
        interruption_steps,
        probes,
        mcm_f3_receptor_sequences_digest(contact_a),
        tuple(
            mcm_f3_receptor_sequences_digest(item) for item in contact_b_steps
        ),
        tuple(
            mcm_f3_receptor_sequences_digest(item) for item in interruption_steps
        ),
        tuple(mcm_f3_receptor_sequences_digest(item) for item in probes),
        _CLOCK_ID,
        _TICKS_PER_SECOND,
    )
    observed = (
        result.contact_a_digest,
        result.contact_b_step_digests,
        result.interruption_step_digests,
        result.probe_digests,
    )
    expected = (
        _EXPECTED_CONTACT_A_DIGEST,
        _EXPECTED_CONTACT_B_STEP_DIGESTS,
        _EXPECTED_INTERRUPTION_STEP_DIGESTS,
        _EXPECTED_PROBE_DIGESTS,
    )
    if observed != expected:
        raise MCMF3K2BSourceError("K2-B reduced source digests changed")
    return result


def mcm_f3_k2b_source_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(MCMF3K2BSource))
