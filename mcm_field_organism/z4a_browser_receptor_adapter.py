"""Direct camera-free browser payload reduction for the bound Z4-A2 worlds."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np

from .broadband_hearing_path import BroadbandHearingPath
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .mcm_f3_controlled_history_source import mcm_f3_receptor_sequences_digest
from .receptor_contract import CommonFieldTime, from_auditory_receptor_state, from_visual_receptor_state
from .receptor_time_alignment import OrganismTimedReceptorFrame, ReceptorTimeSequence


class Z4ABrowserReceptorError(ValueError):
    """Raised when direct browser payloads violate the fixed Z4-A2 contract."""


Z4A_BROWSER_REFERENCE_WORLD_ID = "z4a.browser.direct.reference.v2"
Z4A_BROWSER_INDEPENDENT_WORLD_ID = "z4a.browser.direct.independent.v2"
Z4A_BROWSER_SEQUENCE_CLOCK_ID = "z4a.browser.ns"
Z4A_BROWSER_VISUAL_FRAME_COUNT = 875
Z4A_BROWSER_AUDIO_CHUNK_COUNT = 3500
Z4A_BROWSER_AUDIO_STATE_COUNT = 3491


@dataclass(frozen=True, slots=True)
class Z4ABrowserWorldContract:
    world_id: str
    contract_id: str
    motion_axis: str
    tone_frequency_hz: float

    def __post_init__(self) -> None:
        frequency = float(self.tone_frequency_hz)
        allowed = {
            (
                Z4A_BROWSER_REFERENCE_WORLD_ID,
                "browser.world.direct.audiovisual.v2",
                "horizontal",
                660.0,
            ),
            (
                Z4A_BROWSER_INDEPENDENT_WORLD_ID,
                "browser.world.direct.audiovisual.control.v2",
                "vertical",
                990.0,
            ),
        }
        if (self.world_id, self.contract_id, self.motion_axis, frequency) not in allowed:
            raise Z4ABrowserReceptorError("Z4-A2 admits only two bound browser worlds")
        object.__setattr__(self, "tone_frequency_hz", frequency)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "audio": {
                "channel_count": 1,
                "oscillator_type": "sine",
                "sample_rate": 48000,
                "source_frame_size": 480,
                "tone_frequency_hz": self.tone_frequency_hz,
            },
            "capture": {
                "external_network_allowed": False,
                "media_devices_allowed": False,
                "raw_retention": False,
                "writes_back": False,
            },
            "contract_id": self.contract_id,
            "phases": [
                {"duration_ns": 7_000_000_000, "phase_id": "rest.before", "tone_gain": 0.0, "visual_mode": "static"},
                {"duration_ns": 7_000_000_000, "phase_id": "change", "tone_gain": 0.18, "visual_mode": "moving"},
                {"duration_ns": 21_000_000_000, "phase_id": "rest.after", "tone_gain": 0.0, "visual_mode": "static"},
            ],
            "visual": {
                "background_rgb": [32, 36, 40],
                "canvas_height": 480,
                "canvas_width": 480,
                "device_scale_factor": 1,
                "motion_amplitude_px": 144.0,
                "motion_axis": self.motion_axis,
                "motion_direction": "positive-first",
                "movement_cycles": 3,
                "sample_rate_hz": 25,
                "square_height_px": 86.4,
                "square_rgb": [245, 247, 248],
                "square_width_px": 86.4,
            },
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


def reference_z4a_browser_world_contract() -> Z4ABrowserWorldContract:
    return Z4ABrowserWorldContract(
        Z4A_BROWSER_REFERENCE_WORLD_ID,
        "browser.world.direct.audiovisual.v2",
        "horizontal",
        660.0,
    )


def independent_z4a_browser_world_contract() -> Z4ABrowserWorldContract:
    return Z4ABrowserWorldContract(
        Z4A_BROWSER_INDEPENDENT_WORLD_ID,
        "browser.world.direct.audiovisual.control.v2",
        "vertical",
        990.0,
    )


def z4a_browser_asset_digests(asset_directory: Path) -> tuple[tuple[str, str], ...]:
    root = Path(asset_directory)
    expected = ("index.html", "styles.css", "world.js")
    if not root.is_dir():
        raise Z4ABrowserReceptorError("Z4-A2 asset directory does not exist")
    output = []
    for name in expected:
        path = root / name
        if not path.is_file():
            raise Z4ABrowserReceptorError(f"missing Z4-A2 asset: {name}")
        output.append((name, hashlib.sha256(path.read_bytes()).hexdigest()))
    return tuple(output)


def _auditory_path() -> BroadbandHearingPath:
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


class Z4ABrowserReceptorAdapter:
    """Immediately reduce ordered PNG and PCM payloads without retaining raw data."""

    def __init__(self, contract: Z4ABrowserWorldContract) -> None:
        if not isinstance(contract, Z4ABrowserWorldContract):
            raise Z4ABrowserReceptorError("adapter requires one bound Z4-A2 contract")
        self.contract = contract
        self._visual_receptor = LocalChannelGridReceptor(
            VisualGridConfig(480, 480, 10, 8, 25.0)
        )
        self._auditory_path = _auditory_path()
        self._visual_frames: list[OrganismTimedReceptorFrame] = []
        self._auditory_frames: list[OrganismTimedReceptorFrame] = []
        self._visual_inputs = 0
        self._audio_inputs = 0
        self._finished = False

    @property
    def raw_payloads_retained(self) -> bool:
        return False

    def push_visual_png(self, png_bytes: bytes, *, frame_index: int) -> None:
        if self._finished:
            raise Z4ABrowserReceptorError("adapter is already finalized")
        if frame_index != self._visual_inputs or frame_index >= Z4A_BROWSER_VISUAL_FRAME_COUNT:
            raise Z4ABrowserReceptorError("visual PNG index changed or is out of order")
        if not isinstance(png_bytes, bytes) or not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            raise Z4ABrowserReceptorError("visual input must be browser PNG bytes")
        try:
            import cv2

            encoded = np.frombuffer(png_bytes, dtype=np.uint8)
            bgr = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
            if bgr is None:
                raise Z4ABrowserReceptorError("browser PNG cannot be decoded")
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            state = self._visual_receptor.analyze(rgb, frame_index=frame_index)
        except Z4ABrowserReceptorError:
            raise
        except Exception as exc:
            raise Z4ABrowserReceptorError("browser PNG reduction failed") from exc
        start = 40_000_000 * frame_index
        self._visual_frames.append(
            OrganismTimedReceptorFrame(
                from_visual_receptor_state(state),
                CommonFieldTime(Z4A_BROWSER_SEQUENCE_CLOCK_ID, start, start + 40_000_000),
            )
        )
        self._visual_inputs += 1

    def push_audio_chunk(self, samples: Iterable[float], *, chunk_index: int) -> None:
        if self._finished:
            raise Z4ABrowserReceptorError("adapter is already finalized")
        if chunk_index != self._audio_inputs or chunk_index >= Z4A_BROWSER_AUDIO_CHUNK_COUNT:
            raise Z4ABrowserReceptorError("audio chunk index changed or is out of order")
        chunk = tuple(float(value) for value in samples)
        if len(chunk) != 480 or any(not math.isfinite(value) for value in chunk):
            raise Z4ABrowserReceptorError("audio chunk must contain 480 finite samples")
        try:
            state = self._auditory_path.push(chunk)
        except Exception as exc:
            raise Z4ABrowserReceptorError("browser PCM reduction failed") from exc
        self._audio_inputs += 1
        if state is None:
            return
        state_index = len(self._auditory_frames)
        end = 100_000_000 + 10_000_000 * state_index
        self._auditory_frames.append(
            OrganismTimedReceptorFrame(
                from_auditory_receptor_state(state),
                CommonFieldTime(Z4A_BROWSER_SEQUENCE_CLOCK_ID, end - 10_000_000, end),
            )
        )

    def finalize(self) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
        if self._finished:
            raise Z4ABrowserReceptorError("adapter can be finalized only once")
        if self._visual_inputs != Z4A_BROWSER_VISUAL_FRAME_COUNT or self._audio_inputs != Z4A_BROWSER_AUDIO_CHUNK_COUNT:
            raise Z4ABrowserReceptorError("browser payload inventory is incomplete")
        if len(self._visual_frames) != Z4A_BROWSER_VISUAL_FRAME_COUNT or len(self._auditory_frames) != Z4A_BROWSER_AUDIO_STATE_COUNT:
            raise Z4ABrowserReceptorError("receptor state inventory changed")
        auditory = ReceptorTimeSequence(
            "auditory",
            self._auditory_path.geometry_id,
            Z4A_BROWSER_SEQUENCE_CLOCK_ID,
            tuple(self._auditory_frames),
        )
        visual = ReceptorTimeSequence(
            "visual",
            self._visual_receptor.config.geometry_id,
            Z4A_BROWSER_SEQUENCE_CLOCK_ID,
            tuple(self._visual_frames),
        )
        self._auditory_frames.clear()
        self._visual_frames.clear()
        self._finished = True
        return auditory, visual


@dataclass(frozen=True, slots=True)
class Z4ABrowserSequenceReceipt:
    world_id: str
    contract_digest: str
    auditory_sequence_digest: str
    visual_sequence_digest: str
    combined_sequence_digest: str
    auditory_state_count: int
    visual_state_count: int
    raw_payloads_retained: bool = False


def z4a_browser_sequence_receipt(
    contract: Z4ABrowserWorldContract,
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
) -> Z4ABrowserSequenceReceipt:
    if tuple(item.modality_id for item in sequences) != ("auditory", "visual"):
        raise Z4ABrowserReceptorError("receipt requires auditory and visual sequences")
    auditory, visual = sequences
    return Z4ABrowserSequenceReceipt(
        world_id=contract.world_id,
        contract_digest=contract.digest(),
        auditory_sequence_digest=mcm_f3_receptor_sequences_digest((auditory,)),
        visual_sequence_digest=mcm_f3_receptor_sequences_digest((visual,)),
        combined_sequence_digest=mcm_f3_receptor_sequences_digest(sequences),
        auditory_state_count=len(auditory.frames),
        visual_state_count=len(visual.frames),
    )


def z4a_browser_receptor_adapter_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (Z4ABrowserWorldContract, Z4ABrowserSequenceReceipt)
        for item in fields(cls)
    )
