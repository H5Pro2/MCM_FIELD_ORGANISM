"""Bounded media-window schedule before receptor and runtime processing."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


VERSION = "s2tv.sampled-media-adapter.v1"
FRAME_RATE = (30000, 1001)
VIDEO_TIME_BASE = (1, 30000)
AUDIO_TIME_BASE = (1, 48000)
WINDOW_SECONDS = Fraction(1, 10)
SAMPLE_TIMES = tuple(Fraction(index, 2) for index in range(10))
MAX_EVENTS = 28
MAX_FORMATIONS = 20
MAX_AUDIO_HINTS = 2
MAX_VISUAL_HINTS = 6


class S2TVError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _need(value: bool, code: str) -> None:
    if not value:
        raise S2TVError(code)


@dataclass(frozen=True, slots=True)
class MediaEvent:
    event_id: str
    ordinal: int
    pass_number: int
    media_start: Fraction
    kind: str
    runtime_time: int

    @property
    def midpoint(self) -> Fraction:
        return self.media_start + WINDOW_SECONDS / 2


def schedule() -> tuple[MediaEvent, ...]:
    """Two fixed passes. Hints precede their second-pass formation."""
    events: list[MediaEvent] = []
    for pass_number in (1, 2):
        for media_start in SAMPLE_TIMES:
            if pass_number == 2 and media_start in (Fraction(1), Fraction(4)):
                for kind in ("AUDIO_HINT", "VISUAL_HINT"):
                    ordinal = len(events) + 1
                    events.append(MediaEvent(
                        f"s2tv-p{pass_number}-{kind.lower()}-{float(media_start):.1f}", ordinal,
                        pass_number, media_start, kind, ordinal * 100_000))
            ordinal = len(events) + 1
            events.append(MediaEvent(
                f"s2tv-p{pass_number}-formation-{float(media_start):.1f}", ordinal,
                pass_number, media_start, "FORMATION", ordinal * 100_000))
    return tuple(events)


def budget(events: tuple[MediaEvent, ...]) -> dict[str, int]:
    _need(events == schedule(), "SCHEDULE_BINDING_INVALID")
    formations = sum(event.kind == "FORMATION" for event in events)
    audio_hints = sum(event.kind == "AUDIO_HINT" for event in events)
    visual_hints = sum(event.kind == "VISUAL_HINT" for event in events)
    value = dict(
        events=len(events), formations=formations, audio_hints=audio_hints,
        visual_hints=visual_hints, audio_analyses=formations + audio_hints,
        nj_projections=formations + audio_hints, visual_analyses=formations + visual_hints,
        scans=2 * (audio_hints + visual_hints),
        field_contacts=336 * formations + 48 * audio_hints + 288 * visual_hints,
    )
    _need(value["events"] <= MAX_EVENTS and value["formations"] <= MAX_FORMATIONS,
          "EVENT_BUDGET_INVALID")
    _need(value["audio_hints"] <= MAX_AUDIO_HINTS and value["visual_hints"] <= MAX_VISUAL_HINTS,
          "HINT_BUDGET_INVALID")
    return value


def bind_frame(event: MediaEvent, *, frame_pts: int, next_frame_pts: int,
               time_base: tuple[int, int] = VIDEO_TIME_BASE,
               frame_rate: tuple[int, int] = FRAME_RATE) -> dict[str, object]:
    _need(event in schedule(), "EVENT_BINDING_INVALID")
    _need(time_base == VIDEO_TIME_BASE and frame_rate == FRAME_RATE, "VIDEO_PROFILE_INVALID")
    _need(type(frame_pts) is int and type(next_frame_pts) is int and 0 <= frame_pts < next_frame_pts,
          "FRAME_PTS_INVALID")
    selected = frame_pts * Fraction(*time_base)
    successor = next_frame_pts * Fraction(*time_base)
    _need(selected <= event.midpoint < successor, "FRAME_SELECTION_INVALID")
    return dict(version=VERSION, event_id=event.event_id, pass_number=event.pass_number,
                selection_time=str(event.media_start), midpoint=str(event.midpoint),
                frame_pts=frame_pts, next_frame_pts=next_frame_pts,
                video_time_base=list(time_base), frame_rate=list(frame_rate),
                runtime_time=event.runtime_time)


class SampleSession:
    """Start/status/stop boundary; it never reads a payload or a future event."""

    def __init__(self, events: tuple[MediaEvent, ...]) -> None:
        self._events = events
        self._index = 0
        self._open = False
        self._stopped = False

    def open(self) -> dict[str, object]:
        _need(not self._open and not self._stopped, "SESSION_ALREADY_USED")
        _need(self._events == schedule(), "SCHEDULE_BINDING_INVALID")
        budget(self._events)
        self._open = True
        return self.status()

    def next(self, receipt: dict[str, object]) -> MediaEvent:
        _need(self._open and not self._stopped, "SESSION_CLOSED")
        _need(self._index < len(self._events), "SESSION_COMPLETE")
        event = self._events[self._index]
        _need(receipt.get("event_id") == event.event_id and receipt.get("runtime_time") == event.runtime_time,
              "RECEIPT_BINDING_INVALID")
        self._index += 1
        return event

    def status(self) -> dict[str, object]:
        return dict(version=VERSION, open=self._open and not self._stopped,
                    completed=self._index, total=len(self._events),
                    next_event=None if self._index == len(self._events) else self._events[self._index].event_id)

    def stop(self) -> dict[str, object]:
        _need(self._open and not self._stopped, "SESSION_CLOSED")
        self._stopped = True
        return dict(**self.status(), closure="COMPLETE" if self._index == len(self._events) else "INCOMPLETE")
