"""Bound deterministic Z4-A audio worlds to neutral receptor sequences."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json

from .auditory_baselines import AuditoryProbeConfig
from .broadband_hearing_path import BroadbandHearingPath
from .controlled_audio_phase_source import (
    ControlledAudioPhaseSource,
    shifted_sound_mute_sound_20s_source,
    sound_mute_sound_20s_source,
)
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .mcm_f3_controlled_history_source import mcm_f3_receptor_sequences_digest
from .receptor_contract import CommonFieldTime, from_auditory_receptor_state
from .receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


class Z4AAudioReceptorSourceError(ValueError):
    """Raised when the fixed Z4-A audio binding drifts or cannot reproduce."""


_REFERENCE_WORLD_ID = "z4a.audio.sound-mute-sound.v1"
_INDEPENDENT_WORLD_ID = "z4a.audio.shifted-sound-mute-sound.v1"
_REFERENCE_FREQUENCIES = (250.0, 1000.0, 4000.0)
_INDEPENDENT_FREQUENCIES = (375.0, 1500.0, 6000.0)
_SEQUENCE_CLOCK_ID = "z4a.audio.sample"
_EXPECTED_GEOMETRY_ID = "auditory.log48.50-18000.w4800.h480.v1"
_EXPECTED_SOURCE_FRAMES = 6000
_EXPECTED_RECEPTOR_STATES = 5991
_EXPECTED_ACTIVE_ZERO = 1991
_EXPECTED_ACTIVE_ENERGY = 4000


@dataclass(frozen=True, slots=True)
class Z4AAudioSourceContract:
    """One of the two exact audio contracts admitted by Z4-A1."""

    world_id: str
    frequencies_hz: tuple[float, float, float]

    def __post_init__(self) -> None:
        frequencies = tuple(float(value) for value in self.frequencies_hz)
        allowed = {
            (_REFERENCE_WORLD_ID, _REFERENCE_FREQUENCIES),
            (_INDEPENDENT_WORLD_ID, _INDEPENDENT_FREQUENCIES),
        }
        if (self.world_id, frequencies) not in allowed:
            raise Z4AAudioReceptorSourceError(
                "Z4-A1 admits only the bound reference and independent contracts"
            )
        object.__setattr__(self, "frequencies_hz", frequencies)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "component_amplitude": 0.2,
            "frequencies_hz": list(self.frequencies_hz),
            "phase_local_sample_reset": True,
            "phases": [
                {
                    "duration_seconds": 20.0,
                    "gain": 1.0,
                    "phase_id": "contact.1",
                },
                {
                    "duration_seconds": 20.0,
                    "gain": 0.0,
                    "phase_id": "mute",
                },
                {
                    "duration_seconds": 20.0,
                    "gain": 1.0,
                    "phase_id": "contact.2",
                },
            ],
            "sample_rate": 48000,
            "source_frame_size": 480,
            "world_id": self.world_id,
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        return hashlib.sha256(encoded).hexdigest()

    def open_source(self) -> ControlledAudioPhaseSource:
        factory = (
            sound_mute_sound_20s_source
            if self.world_id == _REFERENCE_WORLD_ID
            else shifted_sound_mute_sound_20s_source
        )
        return factory(config=AuditoryProbeConfig(sample_rate=48000, frame_size=480))


def reference_z4a_audio_source_contract() -> Z4AAudioSourceContract:
    return Z4AAudioSourceContract(_REFERENCE_WORLD_ID, _REFERENCE_FREQUENCIES)


def independent_z4a_audio_source_contract() -> Z4AAudioSourceContract:
    return Z4AAudioSourceContract(_INDEPENDENT_WORLD_ID, _INDEPENDENT_FREQUENCIES)


def _hearing_path() -> BroadbandHearingPath:
    return BroadbandHearingPath(
        LogSpectralReceptor(
            LogSpectralConfig(
                sample_rate=48000,
                window_size=4800,
                hop_size=480,
                min_frequency=50.0,
                max_frequency=18000.0,
                band_count=48,
            )
        )
    )


def build_z4a_audio_receptor_sequence(
    contract: Z4AAudioSourceContract,
) -> ReceptorTimeSequence:
    """Reduce one fresh bound source without retaining generated samples."""

    if not isinstance(contract, Z4AAudioSourceContract):
        raise Z4AAudioReceptorSourceError(
            "audio sequence requires one bound Z4-A1 source contract"
        )
    source = contract.open_source()
    path = _hearing_path()
    if source.total_frames != _EXPECTED_SOURCE_FRAMES:
        raise Z4AAudioReceptorSourceError("Z4-A1 source frame count changed")

    timed_frames = []
    for _ in range(source.total_frames):
        state = path.push(source.read_frame())
        if state is None:
            continue
        frame = from_auditory_receptor_state(state)
        timed_frames.append(
            OrganismTimedReceptorFrame(
                frame,
                CommonFieldTime(
                    _SEQUENCE_CLOCK_ID,
                    frame.window_end_tick - path.receptor.config.hop_size,
                    frame.window_end_tick,
                ),
            )
        )

    sequence = ReceptorTimeSequence(
        modality_id="auditory",
        geometry_id=path.geometry_id,
        clock_id=_SEQUENCE_CLOCK_ID,
        frames=tuple(timed_frames),
    )
    if len(sequence.frames) != _EXPECTED_RECEPTOR_STATES:
        raise Z4AAudioReceptorSourceError("Z4-A1 receptor state count changed")
    if sequence.geometry_id != _EXPECTED_GEOMETRY_ID:
        raise Z4AAudioReceptorSourceError("Z4-A1 receptor geometry changed")
    if (
        sequence.frames[0].field_time.window_start_tick != 4320
        or sequence.frames[0].field_time.window_end_tick != 4800
        or sequence.frames[-1].field_time.window_start_tick != 2_879_520
        or sequence.frames[-1].field_time.window_end_tick != 2_880_000
    ):
        raise Z4AAudioReceptorSourceError("Z4-A1 completion support changed")
    return sequence


@dataclass(frozen=True, slots=True)
class Z4AAudioSequenceBinding:
    world_id: str
    source_contract_digest: str
    receptor_sequence_digest: str
    reproduction_sequence_digest: str
    geometry_id: str
    sequence_clock_id: str
    source_frame_count: int
    receptor_state_count: int
    first_completion_support: tuple[int, int]
    last_completion_support: tuple[int, int]
    active_zero_count: int
    active_energy_count: int
    reproduction_exact: bool

    def __post_init__(self) -> None:
        if self.world_id not in {_REFERENCE_WORLD_ID, _INDEPENDENT_WORLD_ID}:
            raise Z4AAudioReceptorSourceError("unknown Z4-A1 binding world")
        if self.source_frame_count != _EXPECTED_SOURCE_FRAMES:
            raise Z4AAudioReceptorSourceError("binding source count changed")
        if self.receptor_state_count != _EXPECTED_RECEPTOR_STATES:
            raise Z4AAudioReceptorSourceError("binding receptor count changed")
        if self.geometry_id != _EXPECTED_GEOMETRY_ID:
            raise Z4AAudioReceptorSourceError("binding geometry changed")
        if self.sequence_clock_id != _SEQUENCE_CLOCK_ID:
            raise Z4AAudioReceptorSourceError("binding sequence clock changed")
        if self.first_completion_support != (4320, 4800):
            raise Z4AAudioReceptorSourceError("binding first support changed")
        if self.last_completion_support != (2_879_520, 2_880_000):
            raise Z4AAudioReceptorSourceError("binding last support changed")
        if (
            self.active_zero_count != _EXPECTED_ACTIVE_ZERO
            or self.active_energy_count != _EXPECTED_ACTIVE_ENERGY
        ):
            raise Z4AAudioReceptorSourceError("binding contact inventory changed")
        if not self.reproduction_exact:
            raise Z4AAudioReceptorSourceError("binding reproduction differs")


def _sequence_binding(
    contract: Z4AAudioSourceContract,
) -> Z4AAudioSequenceBinding:
    sequence = build_z4a_audio_receptor_sequence(contract)
    repeated = build_z4a_audio_receptor_sequence(contract)
    digest = mcm_f3_receptor_sequences_digest((sequence,))
    repeated_digest = mcm_f3_receptor_sequences_digest((repeated,))
    active_zero = sum(
        all(value == 0.0 for value in item.frame.values)
        for item in sequence.frames
    )
    return Z4AAudioSequenceBinding(
        world_id=contract.world_id,
        source_contract_digest=contract.digest(),
        receptor_sequence_digest=digest,
        reproduction_sequence_digest=repeated_digest,
        geometry_id=sequence.geometry_id,
        sequence_clock_id=sequence.clock_id,
        source_frame_count=_EXPECTED_SOURCE_FRAMES,
        receptor_state_count=len(sequence.frames),
        first_completion_support=(
            sequence.frames[0].field_time.window_start_tick,
            sequence.frames[0].field_time.window_end_tick,
        ),
        last_completion_support=(
            sequence.frames[-1].field_time.window_start_tick,
            sequence.frames[-1].field_time.window_end_tick,
        ),
        active_zero_count=active_zero,
        active_energy_count=len(sequence.frames) - active_zero,
        reproduction_exact=digest == repeated_digest,
    )


@dataclass(frozen=True, slots=True)
class Z4AAudioBindingAudit:
    audit_id: str
    reference: Z4AAudioSequenceBinding
    independent: Z4AAudioSequenceBinding
    controls: tuple[tuple[str, bool], ...]
    raw_samples_retained: bool = False
    receptor_sequences_retained: bool = False

    def __post_init__(self) -> None:
        if self.audit_id != "z4a.audio-binding.v1":
            raise Z4AAudioReceptorSourceError("Z4-A1 audit identity changed")
        if tuple(name for name, _ in self.controls) != (
            "reference_reproduction_exact",
            "independent_reproduction_exact",
            "reference_and_independent_differ",
            "geometry_and_support_match",
            "contact_inventories_match",
        ):
            raise Z4AAudioReceptorSourceError("Z4-A1 control inventory changed")
        if not all(value for _, value in self.controls):
            raise Z4AAudioReceptorSourceError("Z4-A1 binding controls failed")
        if self.raw_samples_retained or self.receptor_sequences_retained:
            raise Z4AAudioReceptorSourceError("Z4-A1 audit cannot retain source data")


def audit_z4a_audio_binding() -> Z4AAudioBindingAudit:
    """Reproduce both exact worlds and return only scalar binding evidence."""

    reference = _sequence_binding(reference_z4a_audio_source_contract())
    independent = _sequence_binding(independent_z4a_audio_source_contract())
    return Z4AAudioBindingAudit(
        audit_id="z4a.audio-binding.v1",
        reference=reference,
        independent=independent,
        controls=(
            ("reference_reproduction_exact", reference.reproduction_exact),
            ("independent_reproduction_exact", independent.reproduction_exact),
            (
                "reference_and_independent_differ",
                reference.receptor_sequence_digest
                != independent.receptor_sequence_digest,
            ),
            (
                "geometry_and_support_match",
                reference.geometry_id == independent.geometry_id
                and reference.sequence_clock_id == independent.sequence_clock_id
                and reference.first_completion_support
                == independent.first_completion_support
                and reference.last_completion_support
                == independent.last_completion_support,
            ),
            (
                "contact_inventories_match",
                reference.active_zero_count == independent.active_zero_count
                and reference.active_energy_count == independent.active_energy_count,
            ),
        ),
    )


def z4a_audio_binding_json_value(
    audit: Z4AAudioBindingAudit,
) -> dict[str, object]:
    if not isinstance(audit, Z4AAudioBindingAudit):
        raise Z4AAudioReceptorSourceError("JSON projection requires a Z4-A1 audit")
    return asdict(audit)


def z4a_audio_receptor_source_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            Z4AAudioSourceContract,
            Z4AAudioSequenceBinding,
            Z4AAudioBindingAudit,
        )
        for item in fields(cls)
    )
