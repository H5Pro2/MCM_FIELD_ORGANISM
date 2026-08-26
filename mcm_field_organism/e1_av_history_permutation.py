"""Private reduced AV source permutation for the S1-DE history corridor."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math

from .controlled_audio_video_test_world import (
    ControlledAudioVideoTestWorld,
    controlled_reentry_world_family,
    reduce_controlled_test_world_sequences,
)
from .receptor_contract import CommonFieldTime
from .receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


class E1AVHistoryPermutationError(ValueError):
    """Raised when AB and BA cannot differ by temporal order alone."""


_CLOCK_ID = "organism.e1.av-history"
_TICKS_PER_SECOND = 1_000_000.0
_WARMUP_TICKS = 1_000_000
_BLOCK_TICKS = 1_000_000


def _sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _frame_payload(item: OrganismTimedReceptorFrame) -> dict[str, object]:
    frame = item.frame
    return {
        "modality_id": frame.modality_id,
        "geometry_id": frame.geometry_id,
        "snapshot_id": frame.snapshot_id,
        "source_clock_id": frame.clock_id,
        "source_start_tick": frame.window_start_tick,
        "source_end_tick": frame.window_end_tick,
        "carrier_ids": list(frame.carrier_ids),
        "values": list(frame.values),
    }


def _source_support_payload(
    item: OrganismTimedReceptorFrame,
) -> tuple[object, ...]:
    frame = item.frame
    return (
        frame.modality_id,
        frame.clock_id,
        frame.window_start_tick,
        frame.window_end_tick,
    )


def _slot_payload(item: OrganismTimedReceptorFrame) -> tuple[object, ...]:
    return (
        item.field_time.clock_id,
        item.field_time.window_start_tick,
        item.field_time.window_end_tick,
    )


def _sequence_payload(sequence: ReceptorTimeSequence) -> dict[str, object]:
    return {
        "modality_id": sequence.modality_id,
        "geometry_id": sequence.geometry_id,
        "clock_id": sequence.clock_id,
        "frames": [
            {
                "frame": _frame_payload(item),
                "field_time": list(_slot_payload(item)),
            }
            for item in sequence.frames
        ],
    }


def _sequences_digest(sequences: tuple[ReceptorTimeSequence, ...]) -> str:
    return _sha256([_sequence_payload(item) for item in sequences])


@dataclass(frozen=True, slots=True)
class E1AVHistoryModalityAudit:
    """Exact source and slot inventory comparison for one modality."""

    modality_id: str
    frame_count: int
    first_block_count: int
    second_block_count: int
    payload_inventory_digest: str
    permuted_payload_inventory_digest: str
    source_support_inventory_digest: str
    permuted_source_support_inventory_digest: str
    organism_slot_inventory_digest: str
    permuted_organism_slot_inventory_digest: str
    total_absolute_mass: float
    permuted_total_absolute_mass: float
    quadratic_energy: float
    permuted_quadratic_energy: float

    def __post_init__(self) -> None:
        if self.modality_id not in {"auditory", "visual"}:
            raise E1AVHistoryPermutationError("audit modality is invalid")
        if (
            isinstance(self.frame_count, bool)
            or not isinstance(self.frame_count, int)
            or self.frame_count < 2
            or self.first_block_count != self.second_block_count
            or self.frame_count != self.first_block_count + self.second_block_count
        ):
            raise E1AVHistoryPermutationError(
                "history blocks must contain equal positive frame counts"
            )
        digest_pairs = (
            (
                self.payload_inventory_digest,
                self.permuted_payload_inventory_digest,
            ),
            (
                self.source_support_inventory_digest,
                self.permuted_source_support_inventory_digest,
            ),
            (
                self.organism_slot_inventory_digest,
                self.permuted_organism_slot_inventory_digest,
            ),
        )
        if any(
            len(value) != 64
            or any(char not in "0123456789abcdef" for char in value)
            for pair in digest_pairs
            for value in pair
        ):
            raise E1AVHistoryPermutationError(
                "history audit digests must be lowercase SHA-256"
            )
        if any(first != second for first, second in digest_pairs):
            raise E1AVHistoryPermutationError(
                "permutation changed a required source or slot inventory"
            )
        numeric_pairs = (
            (self.total_absolute_mass, self.permuted_total_absolute_mass),
            (self.quadratic_energy, self.permuted_quadratic_energy),
        )
        if any(
            not math.isfinite(value) or value < 0.0
            for pair in numeric_pairs
            for value in pair
        ) or any(first != second for first, second in numeric_pairs):
            raise E1AVHistoryPermutationError(
                "permutation changed total input mass or quadratic energy"
            )


@dataclass(frozen=True, slots=True)
class E1AVHistoryPermutation:
    """One AB source and its BA block permutation without field execution."""

    history_ab: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    history_ba: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    split_tick: int
    history_ab_digest: str
    history_ba_digest: str
    permutation_digest: str
    modality_audits: tuple[E1AVHistoryModalityAudit, ...]

    def __post_init__(self) -> None:
        expected_modalities = ("auditory", "visual")
        for sequences in (self.history_ab, self.history_ba):
            if (
                tuple(item.modality_id for item in sequences)
                != expected_modalities
                or any(item.clock_id != _CLOCK_ID for item in sequences)
            ):
                raise E1AVHistoryPermutationError(
                    "history requires auditory and visual sequences on one clock"
                )
        if self.split_tick != _BLOCK_TICKS:
            raise E1AVHistoryPermutationError("history split tick changed")
        for digest in (
            self.history_ab_digest,
            self.history_ba_digest,
            self.permutation_digest,
        ):
            if len(digest) != 64 or any(
                char not in "0123456789abcdef" for char in digest
            ):
                raise E1AVHistoryPermutationError(
                    "history digests must be lowercase SHA-256"
                )
        if self.history_ab_digest == self.history_ba_digest:
            raise E1AVHistoryPermutationError(
                "AB and BA ordered sequence digests must differ"
            )
        audits = tuple(self.modality_audits)
        if tuple(item.modality_id for item in audits) != expected_modalities:
            raise E1AVHistoryPermutationError(
                "history requires one ordered audit per modality"
            )
        object.__setattr__(self, "modality_audits", audits)


def _inventory_digest(
    frames: tuple[OrganismTimedReceptorFrame, ...],
    payload,
) -> str:
    return _sha256(sorted((payload(item) for item in frames), key=repr))


def _input_totals(
    frames: tuple[OrganismTimedReceptorFrame, ...],
) -> tuple[float, float]:
    values = tuple(value for item in frames for value in item.frame.values)
    return (
        math.fsum(abs(value) for value in values),
        math.fsum(value * value for value in values),
    )


def _audit_modality(
    source: ReceptorTimeSequence,
    permuted: ReceptorTimeSequence,
    split_tick: int,
) -> E1AVHistoryModalityAudit:
    source_frames = source.frames
    permuted_frames = permuted.frames
    first_count = sum(
        item.field_time.window_end_tick <= split_tick
        for item in source_frames
    )
    second_count = len(source_frames) - first_count
    source_mass, source_energy = _input_totals(source_frames)
    permuted_mass, permuted_energy = _input_totals(permuted_frames)
    return E1AVHistoryModalityAudit(
        modality_id=source.modality_id,
        frame_count=len(source_frames),
        first_block_count=first_count,
        second_block_count=second_count,
        payload_inventory_digest=_inventory_digest(
            source_frames, _frame_payload
        ),
        permuted_payload_inventory_digest=_inventory_digest(
            permuted_frames, _frame_payload
        ),
        source_support_inventory_digest=_inventory_digest(
            source_frames, _source_support_payload
        ),
        permuted_source_support_inventory_digest=_inventory_digest(
            permuted_frames, _source_support_payload
        ),
        organism_slot_inventory_digest=_inventory_digest(
            source_frames, _slot_payload
        ),
        permuted_organism_slot_inventory_digest=_inventory_digest(
            permuted_frames, _slot_payload
        ),
        total_absolute_mass=source_mass,
        permuted_total_absolute_mass=permuted_mass,
        quadratic_energy=source_energy,
        permuted_quadratic_energy=permuted_energy,
    )


def permute_reduced_av_history_blocks(
    history_ab: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    *,
    split_tick: int = _BLOCK_TICKS,
) -> E1AVHistoryPermutation:
    """Swap complete reduced A/B frame blocks onto existing organism slots."""

    sequences = tuple(history_ab)
    if (
        len(sequences) != 2
        or tuple(item.modality_id for item in sequences)
        != ("auditory", "visual")
        or any(item.clock_id != _CLOCK_ID for item in sequences)
    ):
        raise E1AVHistoryPermutationError(
            "AB history requires auditory and visual sequences on the S1-DE clock"
        )
    if (
        isinstance(split_tick, bool)
        or not isinstance(split_tick, int)
        or split_tick <= 0
    ):
        raise E1AVHistoryPermutationError("split_tick must be a positive integer")

    permuted_sequences = []
    for sequence in sequences:
        first = tuple(
            item
            for item in sequence.frames
            if item.field_time.window_end_tick <= split_tick
        )
        second = tuple(
            item
            for item in sequence.frames
            if item.field_time.window_start_tick >= split_tick
        )
        if (
            len(first) != len(second)
            or not first
            or len(first) + len(second) != len(sequence.frames)
        ):
            raise E1AVHistoryPermutationError(
                f"{sequence.modality_id} history blocks must be equal and nonoverlapping"
            )
        target_slots = tuple(item.field_time for item in sequence.frames)
        reordered_frames = tuple(item.frame for item in second + first)
        permuted_sequences.append(
            ReceptorTimeSequence(
                sequence.modality_id,
                sequence.geometry_id,
                sequence.clock_id,
                tuple(
                    OrganismTimedReceptorFrame(frame, slot)
                    for frame, slot in zip(
                        reordered_frames, target_slots, strict=True
                    )
                ),
            )
        )
    history_ba = tuple(permuted_sequences)
    history_ab_typed = (sequences[0], sequences[1])
    history_ba_typed = (history_ba[0], history_ba[1])
    audits = tuple(
        _audit_modality(source, permuted, split_tick)
        for source, permuted in zip(
            history_ab_typed, history_ba_typed, strict=True
        )
    )
    ab_digest = _sequences_digest(history_ab_typed)
    ba_digest = _sequences_digest(history_ba_typed)
    permutation_digest = _sha256(
        {
            "contract_id": "e1.av-history.reduced-ab-ba-permutation.v1",
            "split_tick": split_tick,
            "history_ab_digest": ab_digest,
            "history_ba_digest": ba_digest,
            "audits": [
                {
                    "modality_id": item.modality_id,
                    "frame_count": item.frame_count,
                    "payload_inventory_digest": item.payload_inventory_digest,
                    "source_support_inventory_digest": (
                        item.source_support_inventory_digest
                    ),
                    "organism_slot_inventory_digest": (
                        item.organism_slot_inventory_digest
                    ),
                    "total_absolute_mass": item.total_absolute_mass,
                    "quadratic_energy": item.quadratic_energy,
                }
                for item in audits
            ],
        }
    )
    return E1AVHistoryPermutation(
        history_ab=history_ab_typed,
        history_ba=history_ba_typed,
        split_tick=split_tick,
        history_ab_digest=ab_digest,
        history_ba_digest=ba_digest,
        permutation_digest=permutation_digest,
        modality_audits=audits,
    )


def _canonical_reduced_ab_history(
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    same, changed = controlled_reentry_world_family()
    warmup = replace(same.phases[1], phase_id="warmup.0")
    phase_a = replace(same.phases[0], phase_id="history.a")
    phase_b = replace(changed.phases[2], phase_id="history.b")
    world = ControlledAudioVideoTestWorld(
        "world.e1.av-history.source",
        (warmup, phase_a, phase_b),
        same.audio_config,
        same.visual_config,
        same.background_channels,
    )
    reduced = reduce_controlled_test_world_sequences(
        world,
        clock_id=_CLOCK_ID,
        ticks_per_second=_TICKS_PER_SECOND,
    )
    histories = []
    for sequence in reduced:
        frames = tuple(
            OrganismTimedReceptorFrame(
                item.frame,
                CommonFieldTime(
                    _CLOCK_ID,
                    item.field_time.window_start_tick - _WARMUP_TICKS,
                    item.field_time.window_end_tick - _WARMUP_TICKS,
                ),
            )
            for item in sequence.frames
            if item.field_time.window_start_tick >= _WARMUP_TICKS
        )
        histories.append(
            ReceptorTimeSequence(
                sequence.modality_id,
                sequence.geometry_id,
                sequence.clock_id,
                frames,
            )
        )
    return (histories[0], histories[1])


def build_e1_av_history_permutation() -> E1AVHistoryPermutation:
    """Build the warmed reduced AB source and its exact BA permutation."""

    return permute_reduced_av_history_blocks(_canonical_reduced_ab_history())
