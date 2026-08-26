"""Camera-free reduction of controlled browser payloads into receptor sequences."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re
from typing import Iterable

import numpy as np

from .broadband_hearing_path import BroadbandHearingPath
from .browser_world_contract import BrowserWorldContract
from .finite_video_path import LocalChannelGridReceptor
from .receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
    technical_identifier,
)
from .receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


class BrowserReceptorBridgeError(ValueError):
    """Raised when controlled browser payloads violate the bridge contract."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class BrowserReceptorBridgeConfig:
    clock_id: str = "browser.sequence.ns"
    ticks_per_second: float = 1_000_000_000.0
    sequence_start_tick: int = 0

    def __post_init__(self) -> None:
        try:
            clock_id = technical_identifier(self.clock_id, "clock_id")
        except ValueError as exc:
            raise BrowserReceptorBridgeError(str(exc)) from exc
        rate = float(self.ticks_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise BrowserReceptorBridgeError(
                "ticks_per_second must be finite and greater than zero"
            )
        if (
            isinstance(self.sequence_start_tick, bool)
            or not isinstance(self.sequence_start_tick, int)
            or self.sequence_start_tick < 0
        ):
            raise BrowserReceptorBridgeError(
                "sequence_start_tick must be a non-negative integer"
            )
        object.__setattr__(self, "clock_id", clock_id)
        object.__setattr__(self, "ticks_per_second", rate)


@dataclass(frozen=True, slots=True)
class BrowserReceptorSequenceBatch:
    contract_id: str
    contract_digest: str
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    raw_payloads_retained: bool = False

    def __post_init__(self) -> None:
        try:
            contract_id = technical_identifier(self.contract_id, "contract_id")
        except ValueError as exc:
            raise BrowserReceptorBridgeError(str(exc)) from exc
        if not isinstance(self.contract_digest, str) or not _SHA256.fullmatch(
            self.contract_digest
        ):
            raise BrowserReceptorBridgeError(
                "contract_digest must be a lowercase SHA-256 digest"
            )
        sequences = tuple(self.sequences)
        if (
            len(sequences) != 2
            or any(not isinstance(item, ReceptorTimeSequence) for item in sequences)
            or tuple(item.modality_id for item in sequences)
            != ("auditory", "visual")
            or sequences[0].clock_id != sequences[1].clock_id
        ):
            raise BrowserReceptorBridgeError(
                "batch requires auditory and visual sequences on one clock"
            )
        if self.raw_payloads_retained:
            raise BrowserReceptorBridgeError("browser raw payload retention is forbidden")
        object.__setattr__(self, "contract_id", contract_id)
        object.__setattr__(self, "sequences", sequences)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_digest": self.contract_digest,
            "contract_id": self.contract_id,
            "raw_payloads_retained": self.raw_payloads_retained,
            "sequences": [
                {
                    "clock_id": sequence.clock_id,
                    "frames": [
                        {
                            "field_time": {
                                "window_end_tick": item.field_time.window_end_tick,
                                "window_start_tick": item.field_time.window_start_tick,
                            },
                            "receptor": {
                                "carrier_ids": list(item.frame.carrier_ids),
                                "geometry_id": item.frame.geometry_id,
                                "snapshot_id": item.frame.snapshot_id,
                                "values": list(item.frame.values),
                            },
                        }
                        for item in sequence.frames
                    ],
                    "geometry_id": sequence.geometry_id,
                    "modality_id": sequence.modality_id,
                }
                for sequence in self.sequences
            ],
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


class BrowserReceptorBridge:
    """Immediately reduce ordered PNG and PCM payloads without retaining them."""

    def __init__(
        self,
        contract: BrowserWorldContract,
        visual_receptor: LocalChannelGridReceptor,
        auditory_path: BroadbandHearingPath,
        config: BrowserReceptorBridgeConfig = BrowserReceptorBridgeConfig(),
    ) -> None:
        if not isinstance(contract, BrowserWorldContract):
            raise BrowserReceptorBridgeError(
                "bridge requires one BrowserWorldContract"
            )
        if not isinstance(visual_receptor, LocalChannelGridReceptor):
            raise BrowserReceptorBridgeError(
                "bridge requires one LocalChannelGridReceptor"
            )
        if not isinstance(auditory_path, BroadbandHearingPath):
            raise BrowserReceptorBridgeError(
                "bridge requires one BroadbandHearingPath"
            )
        if not auditory_path.is_fresh:
            raise BrowserReceptorBridgeError("auditory path must be fresh")
        if not isinstance(config, BrowserReceptorBridgeConfig):
            raise BrowserReceptorBridgeError(
                "config must be a BrowserReceptorBridgeConfig"
            )

        duration_seconds = contract.total_duration_ns / 1_000_000_000.0
        visual_count_exact = (
            duration_seconds * visual_receptor.config.frames_per_second
        )
        visual_count = round(visual_count_exact)
        if visual_count <= 0 or not math.isclose(
            visual_count_exact, visual_count, rel_tol=0.0, abs_tol=1e-10
        ):
            raise BrowserReceptorBridgeError(
                "browser duration must contain a whole number of visual frames"
            )

        audio_config = auditory_path.receptor.config
        audio_numerator = contract.total_duration_ns * audio_config.sample_rate
        audio_denominator = 1_000_000_000 * audio_config.hop_size
        audio_count, remainder = divmod(audio_numerator, audio_denominator)
        if audio_count <= 0 or remainder:
            raise BrowserReceptorBridgeError(
                "browser duration must contain a whole number of audio hops"
            )

        self.contract = contract
        self.visual_receptor = visual_receptor
        self.auditory_path = auditory_path
        self.config = config
        self.expected_visual_frame_count = visual_count
        self.expected_audio_chunk_count = audio_count
        self._visual_frames: list[OrganismTimedReceptorFrame] = []
        self._auditory_frames: list[OrganismTimedReceptorFrame] = []
        self._visual_inputs = 0
        self._audio_inputs = 0
        self._finalized = False

    @property
    def raw_payloads_retained(self) -> bool:
        return False

    def _tick_for_visual_boundary(self, index: int) -> int:
        return self.config.sequence_start_tick + math.floor(
            index
            * self.config.ticks_per_second
            / self.visual_receptor.config.frames_per_second
        )

    def _tick_for_audio_sample(self, sample_index: int) -> int:
        return self.config.sequence_start_tick + math.floor(
            sample_index
            * self.config.ticks_per_second
            / self.auditory_path.receptor.config.sample_rate
        )

    def push_visual_png(self, payload: bytes, *, frame_index: int) -> None:
        if self._finalized:
            raise BrowserReceptorBridgeError("bridge is already finalized")
        if (
            isinstance(frame_index, bool)
            or not isinstance(frame_index, int)
            or frame_index != self._visual_inputs
            or frame_index >= self.expected_visual_frame_count
        ):
            raise BrowserReceptorBridgeError(
                "visual frame index changed or is out of order"
            )
        if not isinstance(payload, bytes) or not payload.startswith(
            b"\x89PNG\r\n\x1a\n"
        ):
            raise BrowserReceptorBridgeError("visual payload must be PNG bytes")
        try:
            import cv2

            encoded = np.frombuffer(payload, dtype=np.uint8)
            bgr = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
            if bgr is None:
                raise BrowserReceptorBridgeError("visual PNG cannot be decoded")
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            state = self.visual_receptor.analyze(rgb, frame_index=frame_index)
        except BrowserReceptorBridgeError:
            raise
        except Exception as exc:
            raise BrowserReceptorBridgeError("visual PNG reduction failed") from exc

        start_tick = self._tick_for_visual_boundary(frame_index)
        end_tick = self._tick_for_visual_boundary(frame_index + 1)
        self._visual_frames.append(
            OrganismTimedReceptorFrame(
                from_visual_receptor_state(state),
                CommonFieldTime(self.config.clock_id, start_tick, end_tick),
            )
        )
        self._visual_inputs += 1

    def push_audio_chunk(
        self,
        samples: Iterable[float],
        *,
        chunk_index: int,
    ) -> None:
        if self._finalized:
            raise BrowserReceptorBridgeError("bridge is already finalized")
        if (
            isinstance(chunk_index, bool)
            or not isinstance(chunk_index, int)
            or chunk_index != self._audio_inputs
            or chunk_index >= self.expected_audio_chunk_count
        ):
            raise BrowserReceptorBridgeError(
                "audio chunk index changed or is out of order"
            )
        try:
            chunk = tuple(float(value) for value in samples)
        except (TypeError, ValueError) as exc:
            raise BrowserReceptorBridgeError(
                "audio chunk must contain numeric samples"
            ) from exc
        expected_size = self.auditory_path.receptor.config.hop_size
        if len(chunk) != expected_size or any(
            not math.isfinite(value) or abs(value) > 1.0 for value in chunk
        ):
            raise BrowserReceptorBridgeError(
                "audio chunk must contain one finite normalized receptor hop"
            )
        try:
            state = self.auditory_path.push(chunk)
        except ValueError as exc:
            raise BrowserReceptorBridgeError("audio chunk reduction failed") from exc
        self._audio_inputs += 1
        if state is None:
            return
        self._auditory_frames.append(
            OrganismTimedReceptorFrame(
                from_auditory_receptor_state(state),
                CommonFieldTime(
                    self.config.clock_id,
                    self._tick_for_audio_sample(
                        state.window_end_sample
                        - self.auditory_path.receptor.config.hop_size
                    ),
                    self._tick_for_audio_sample(state.window_end_sample),
                ),
            )
        )

    def finalize(self) -> BrowserReceptorSequenceBatch:
        if self._finalized:
            raise BrowserReceptorBridgeError("bridge can be finalized only once")
        if (
            self._visual_inputs != self.expected_visual_frame_count
            or self._audio_inputs != self.expected_audio_chunk_count
        ):
            raise BrowserReceptorBridgeError(
                "browser payload inventory is incomplete"
            )
        if not self._visual_frames or not self._auditory_frames:
            raise BrowserReceptorBridgeError(
                "both receptors must produce at least one reduced state"
            )

        auditory = ReceptorTimeSequence(
            modality_id="auditory",
            geometry_id=self.auditory_path.geometry_id,
            clock_id=self.config.clock_id,
            frames=tuple(self._auditory_frames),
        )
        visual = ReceptorTimeSequence(
            modality_id="visual",
            geometry_id=self.visual_receptor.config.geometry_id,
            clock_id=self.config.clock_id,
            frames=tuple(self._visual_frames),
        )
        expected_end_tick = self.config.sequence_start_tick + math.floor(
            self.contract.total_duration_ns
            * self.config.ticks_per_second
            / 1_000_000_000.0
        )
        if (
            self._tick_for_visual_boundary(self._visual_inputs)
            != expected_end_tick
            or self._tick_for_audio_sample(
                self._audio_inputs * self.auditory_path.receptor.config.hop_size
            )
            != expected_end_tick
        ):
            raise BrowserReceptorBridgeError(
                "receptor input boundaries do not reach the browser world end"
            )

        batch = BrowserReceptorSequenceBatch(
            contract_id=self.contract.contract_id,
            contract_digest=self.contract.digest(),
            sequences=(auditory, visual),
        )
        self._auditory_frames.clear()
        self._visual_frames.clear()
        self._finalized = True
        return batch


def browser_receptor_bridge_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for role in (BrowserReceptorBridgeConfig, BrowserReceptorSequenceBatch)
        for item in fields(role)
    )
