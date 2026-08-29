"""Private fixtures for retention, consolidation, and capacity-pressure checks.

The identifiers in this module are experiment metadata. Consumers must pass
only receptor-derived values and bound source objects to memory operators.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


FIXTURE_SCHEMA = "retention.capacity.private.fixtures.v1"
FUNCTIONAL_VISUAL_THRESHOLD = Fraction(44, 765)
FUNCTIONAL_AUDITORY_THRESHOLD = Fraction(1, 5)


@dataclass(frozen=True, slots=True)
class PatternFixture:
    pattern_id: str
    high_positions: str
    cell_values: tuple[int, ...]
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]

    @property
    def av_values(self) -> tuple[float, ...]:
        return self.auditory_values + self.visual_values


@dataclass(frozen=True, slots=True)
class ExposureFixture:
    step: int
    pattern_id: str
    window_start_tick: int
    window_end_tick: int


@dataclass(frozen=True, slots=True)
class ProbeCheckpoint:
    after_step: int
    target_pattern_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FastStepExpectation:
    step: int
    primary_event: str
    ppb_calls_per_modality_after_step: int
    expired_pattern_ids: tuple[str, ...] = ()
    replaced_pattern_id: str | None = None
    visual_slow_replaced_pattern_id: str | None = None


@dataclass(frozen=True, slots=True)
class StoryFixture:
    story_id: str
    exposures: tuple[ExposureFixture, ...]
    checkpoints: tuple[ProbeCheckpoint, ...]
    fast_expectations: tuple[FastStepExpectation, ...]
    expected_ppb_calls_per_modality: int

    @property
    def exposure_count(self) -> int:
        return len(self.exposures)

    @property
    def content_probe_count(self) -> int:
        return sum(len(checkpoint.target_pattern_ids) for checkpoint in self.checkpoints)


@dataclass(frozen=True, slots=True)
class BudgetBinding:
    story_count: int
    arm_count: int
    exposure_count_per_arm: int
    exposure_count_total: int
    content_probe_count_total: int
    sequence_status_count_total: int
    image_analysis_count_total: int
    event_count_total: int
    state_word_limit: int
    formation_write_limit: int
    formation_distance_limit: int
    probe_distance_limit: int
    sequence_functional_distance_limit: int
    sequence_validation_distance_limit: int
    b4_native_state_words: int
    b4_native_formation_writes: int
    tspm1_state_word_limit: int
    tspm1_formation_write_limit: int


def _pattern(pattern_id: str, high_positions: str, cells: tuple[int, ...]) -> PatternFixture:
    visual = tuple(value / 255.0 for value in cells for _ in range(3))
    return PatternFixture(pattern_id, high_positions, cells, (0.0,) * 8, visual)


PATTERNS = (
    _pattern("N1", "013", (200, 200, 40, 200, 40, 40)),
    _pattern("N2", "014", (200, 200, 40, 40, 200, 40)),
    _pattern("N3", "015", (200, 200, 40, 40, 40, 200)),
    _pattern("N4", "023", (200, 40, 200, 200, 40, 40)),
    _pattern("D1", "024", (200, 40, 200, 40, 200, 40)),
    _pattern("D2", "025", (200, 40, 200, 40, 40, 200)),
    _pattern("D3", "034", (200, 40, 40, 200, 200, 40)),
    _pattern("D4", "035", (200, 40, 40, 200, 40, 200)),
    _pattern("D5", "123", (40, 200, 200, 200, 40, 40)),
    _pattern("D6", "124", (40, 200, 200, 40, 200, 40)),
    _pattern("D7", "125", (40, 200, 200, 40, 40, 200)),
)


def _exposures(pattern_ids: tuple[str, ...]) -> tuple[ExposureFixture, ...]:
    return tuple(
        ExposureFixture(step, pattern_id, step - 1, step)
        for step, pattern_id in enumerate(pattern_ids, start=1)
    )


def _expectations(
    primary_events: tuple[str, ...],
    ppb_calls: tuple[int, ...],
    *,
    expired: dict[int, tuple[str, ...]] | None = None,
    replaced: dict[int, str] | None = None,
    slow_replaced: dict[int, str] | None = None,
) -> tuple[FastStepExpectation, ...]:
    expired = expired or {}
    replaced = replaced or {}
    slow_replaced = slow_replaced or {}
    return tuple(
        FastStepExpectation(
            step,
            event,
            ppb_calls[step - 1],
            expired.get(step, ()),
            replaced.get(step),
            slow_replaced.get(step),
        )
        for step, event in enumerate(primary_events, start=1)
    )


U = StoryFixture(
    "U",
    _exposures(("N1", "N1", "D1", "D2", "D3", "D4")),
    tuple(ProbeCheckpoint(step, ("N1",)) for step in (2, 4, 5, 6)),
    _expectations(
        ("FAST_CREATED", "FAST_UPDATED", "FAST_CREATED", "FAST_CREATED", "FAST_REPLACED", "FAST_REPLACED"),
        (0, 1, 1, 1, 1, 1),
        replaced={5: "N1", 6: "D1"},
    ),
    1,
)

V = StoryFixture(
    "V",
    _exposures(("N1", "N1", "N1", "N1", "D1", "D2", "D3", "D4")),
    tuple(ProbeCheckpoint(step, ("N1",)) for step in (4, 6, 7, 8)),
    _expectations(
        ("FAST_CREATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_CREATED", "FAST_CREATED", "FAST_REPLACED", "FAST_REPLACED"),
        (0, 1, 2, 3, 3, 3, 3, 3),
        replaced={7: "N1", 8: "D1"},
    ),
    3,
)

_C_IDS = (
    ("N1",) * 4
    + ("N2",) * 4
    + ("N3",) * 4
    + ("N4",) * 4
    + ("D1",) * 4
    + ("D2",) * 4
)
C = StoryFixture(
    "C",
    _exposures(_C_IDS),
    tuple(
        ProbeCheckpoint(step, ("N1", "N2", "N3", "N4", "D1", "D2"))
        for step in (16, 17, 18, 20, 21, 22, 24)
    ),
    _expectations(
        (
            "FAST_CREATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED",
            "FAST_CREATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED",
            "FAST_CREATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED",
            "FAST_CREATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED",
            "FAST_CREATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED",
            "FAST_CREATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED",
        ),
        (0, 1, 2, 3, 3, 4, 5, 6, 6, 7, 8, 9, 9, 10, 11, 12, 12, 13, 14, 15, 15, 16, 17, 18),
        expired={12: ("N1",), 16: ("N2",), 20: ("N3",), 24: ("N4",)},
        slow_replaced={18: "N1", 22: "N2"},
    ),
    18,
)

A = StoryFixture(
    "A",
    _exposures(("N1",) * 4 + ("D1",) * 2 + ("D2",) * 2 + ("D1", "D2", "D1", "D2", "D1")),
    tuple(ProbeCheckpoint(step, ("N1",)) for step in (11, 12, 13)),
    _expectations(
        (
            "FAST_CREATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED",
            "FAST_CREATED", "FAST_UPDATED", "FAST_CREATED", "FAST_UPDATED",
            "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED", "FAST_UPDATED",
        ),
        (0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9, 10),
        expired={12: ("N1",)},
    ),
    10,
)

_S1_IDS = ("N1", "N2", "N3", "N4", "D1", "D2", "D3", "D4", "D5", "D6", "D7")
_S2_IDS = ("N1", "N3", "N2", "N4", "D1", "D2", "D3", "D4", "D5", "D6", "D7")
_S_EVENTS = ("FAST_CREATED", "FAST_CREATED", "FAST_CREATED") + ("FAST_REPLACED",) * 8
_S_PPB_CALLS = (0,) * 11
_S_CHECKPOINTS = tuple(
    ProbeCheckpoint(step, ("N1", "N2", "N3", "N4")) for step in (4, 9, 10, 11)
)
S1 = StoryFixture(
    "S1",
    _exposures(_S1_IDS),
    _S_CHECKPOINTS,
    _expectations(
        _S_EVENTS,
        _S_PPB_CALLS,
        replaced={4: "N1", 5: "N2", 6: "N3", 7: "N4", 8: "D1", 9: "D2", 10: "D3", 11: "D4"},
    ),
    0,
)
S2 = StoryFixture(
    "S2",
    _exposures(_S2_IDS),
    _S_CHECKPOINTS,
    _expectations(
        _S_EVENTS,
        _S_PPB_CALLS,
        replaced={4: "N1", 5: "N3", 6: "N2", 7: "N4", 8: "D1", 9: "D2", 10: "D3", 11: "D4"},
    ),
    0,
)

STORIES = (U, V, C, A, S1, S2)

BUDGET = BudgetBinding(
    story_count=6,
    arm_count=2,
    exposure_count_per_arm=73,
    exposure_count_total=146,
    content_probe_count_total=170,
    sequence_status_count_total=16,
    image_analysis_count_total=316,
    event_count_total=1296,
    state_word_limit=269,
    formation_write_limit=293,
    formation_distance_limit=234,
    probe_distance_limit=234,
    sequence_functional_distance_limit=416,
    sequence_validation_distance_limit=416,
    b4_native_state_words=255,
    b4_native_formation_writes=27,
    tspm1_state_word_limit=269,
    tspm1_formation_write_limit=293,
)


def pattern_fixture(pattern_id: str) -> PatternFixture:
    matches = tuple(pattern for pattern in PATTERNS if pattern.pattern_id == pattern_id)
    if len(matches) != 1:
        raise ValueError("unknown or ambiguous fixture pattern")
    return matches[0]


def story_fixture(story_id: str) -> StoryFixture:
    matches = tuple(story for story in STORIES if story.story_id == story_id)
    if len(matches) != 1:
        raise ValueError("unknown or ambiguous fixture story")
    return matches[0]
