"""Device-neutral audio source contracts for controlled test worlds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


class AudioCaptureError(RuntimeError):
    """Raised when a finite source cannot satisfy the capture contract."""


class AudioFrameSource(Protocol):
    overflow_count: int

    def read_frame(self) -> tuple[float, ...]: ...


@dataclass(slots=True)
class SyntheticAudioFrameSource:
    """Deterministic source for controlled finite audio histories."""

    frames: tuple[tuple[float, ...], ...]
    overflow_count: int = 0
    _cursor: int = 0

    def __init__(self, frames: Iterable[Iterable[float]]) -> None:
        self.frames = tuple(tuple(float(sample) for sample in frame) for frame in frames)
        self.overflow_count = 0
        self._cursor = 0

    @property
    def read_count(self) -> int:
        return self._cursor

    def read_frame(self) -> tuple[float, ...]:
        if self._cursor >= len(self.frames):
            raise AudioCaptureError("audio source ended before the finite capture completed")
        frame = self.frames[self._cursor]
        self._cursor += 1
        return frame
