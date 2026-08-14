"""Contract for one controlled audiovisual browser world outside MCM runtime."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re


class BrowserWorldContractError(ValueError):
    """Raised when the external browser world violates its research boundary."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


@dataclass(frozen=True, slots=True)
class BrowserWorldPhase:
    phase_id: str
    duration_ns: int
    visual_mode: str
    tone_gain: float

    def __post_init__(self) -> None:
        if not isinstance(self.phase_id, str) or not _IDENTIFIER.fullmatch(self.phase_id):
            raise BrowserWorldContractError(
                "phase_id must be a lowercase technical identifier"
            )
        if (
            isinstance(self.duration_ns, bool)
            or not isinstance(self.duration_ns, int)
            or self.duration_ns <= 0
        ):
            raise BrowserWorldContractError("duration_ns must be a positive integer")
        if self.visual_mode not in {"static", "moving"}:
            raise BrowserWorldContractError("visual_mode must be static or moving")
        gain = float(self.tone_gain)
        if not math.isfinite(gain) or gain < 0.0 or gain > 1.0:
            raise BrowserWorldContractError("tone_gain must stay within 0..1")
        object.__setattr__(self, "tone_gain", gain)


@dataclass(frozen=True, slots=True)
class BrowserWorldContract:
    contract_id: str
    startup_frame_count: int
    start_lead_ns: int
    movement_cycles: int
    tone_frequency_hz: float
    phases: tuple[BrowserWorldPhase, ...]
    raw_frames_retained: bool = False
    direct_sensor_feed: bool = False
    writes_back: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.contract_id, str) or not _IDENTIFIER.fullmatch(
            self.contract_id
        ):
            raise BrowserWorldContractError(
                "contract_id must be a lowercase technical identifier"
            )
        integer_roles = (
            ("startup_frame_count", self.startup_frame_count),
            ("start_lead_ns", self.start_lead_ns),
            ("movement_cycles", self.movement_cycles),
        )
        for role, value in integer_roles:
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise BrowserWorldContractError(f"{role} must be a positive integer")
        frequency = float(self.tone_frequency_hz)
        if not math.isfinite(frequency) or frequency <= 0.0:
            raise BrowserWorldContractError(
                "tone_frequency_hz must be finite and positive"
            )
        phase_set = tuple(self.phases)
        if len(phase_set) not in (3, 4):
            raise BrowserWorldContractError(
                "browser world requires exactly three or four phases"
            )
        if any(not isinstance(phase, BrowserWorldPhase) for phase in phase_set):
            raise BrowserWorldContractError(
                "phases must contain BrowserWorldPhase values"
            )
        if len({phase.phase_id for phase in phase_set}) != len(phase_set):
            raise BrowserWorldContractError("phase identifiers must be unique")
        modes = tuple(phase.visual_mode for phase in phase_set)
        gains = tuple(phase.tone_gain for phase in phase_set)
        if len(phase_set) == 3:
            if modes != ("static", "moving", "static"):
                raise BrowserWorldContractError(
                    "three-phase browser world must remain static-moving-static"
                )
            if gains[0] != 0.0 or gains[2] != 0.0 or gains[1] <= 0.0:
                raise BrowserWorldContractError(
                    "three-phase browser world requires audible movement and silent rests"
                )
        else:
            if modes != ("static", "moving", "static", "static"):
                raise BrowserWorldContractError(
                    "four-phase browser world must remain static-moving-static-static"
                )
            active_tone_phases = tuple(
                index for index, gain in enumerate(gains) if gain > 0.0
            )
            if gains[0] != 0.0 or gains[3] != 0.0 or active_tone_phases not in (
                (1,),
                (2,),
            ):
                raise BrowserWorldContractError(
                    "four-phase browser world requires one tone in phase one or two"
                )
        if self.raw_frames_retained or self.direct_sensor_feed or self.writes_back:
            raise BrowserWorldContractError(
                "browser world must remain external, non-retaining, and passive"
            )
        object.__setattr__(self, "tone_frequency_hz", frequency)
        object.__setattr__(self, "phases", phase_set)

    @property
    def total_duration_ns(self) -> int:
        return sum(phase.duration_ns for phase in self.phases)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "startup_frame_count": self.startup_frame_count,
            "start_lead_ns": self.start_lead_ns,
            "movement_cycles": self.movement_cycles,
            "tone_frequency_hz": self.tone_frequency_hz,
            "phases": [
                {
                    "phase_id": phase.phase_id,
                    "duration_ns": phase.duration_ns,
                    "visual_mode": phase.visual_mode,
                    "tone_gain": phase.tone_gain,
                }
                for phase in self.phases
            ],
            "raw_frames_retained": self.raw_frames_retained,
            "direct_sensor_feed": self.direct_sensor_feed,
            "writes_back": self.writes_back,
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def reference_browser_world_contract() -> BrowserWorldContract:
    second = 1_000_000_000
    return BrowserWorldContract(
        contract_id="browser.world.audiovisual.v1",
        startup_frame_count=30,
        start_lead_ns=3 * second,
        movement_cycles=3,
        tone_frequency_hz=660.0,
        phases=(
            BrowserWorldPhase("rest.before", 7 * second, "static", 0.0),
            BrowserWorldPhase("change", 7 * second, "moving", 0.18),
            BrowserWorldPhase("rest.after", 21 * second, "static", 0.0),
        ),
    )


def browser_world_contract_public_roles() -> tuple[str, ...]:
    return tuple(item.name for cls in (BrowserWorldPhase, BrowserWorldContract) for item in fields(cls))
