"""Private, read-only horizontal partial-structure hints for visible visual cells."""

from __future__ import annotations

from dataclasses import dataclass
import math


SCHEMA = "s2sp.private.visible-shift-hint.v1"
VISIBLE_WIDTH = 32
COMPLETE_CELL_COUNT = 10
OFFSETS = (-1, 0, 1)


class S2SPError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def _values(values: object, role: str) -> tuple[float, ...]:
    if type(values) is not tuple or len(values) != 288:
        raise S2SPError("VALUE_SHAPE_INVALID", f"{role} must contain 288 values")
    result = tuple(float(item) for item in values)
    if not all(math.isfinite(item) and 0.0 <= item <= 1.0 for item in result):
        raise S2SPError("VALUE_DOMAIN_INVALID", f"{role} must be finite and in [0, 1]")
    return result


def _cells(values: tuple[float, ...]) -> tuple[tuple[float, float, float], ...]:
    return tuple(tuple(values[3 * cell : 3 * cell + 3]) for cell in range(COMPLETE_CELL_COUNT))


@dataclass(frozen=True, slots=True)
class ShiftFinding:
    status: str
    matching_offsets: tuple[int, ...]
    overlap_cells: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class ShiftHint:
    status: str
    candidate_ids: tuple[str, ...]
    findings: tuple[ShiftFinding, ...]


def exact_visible_match(cue_values: object, candidate_values: object) -> bool:
    """The unchanged 32-value visual exact-comparison baseline."""

    cue = _values(cue_values, "cue values")
    candidate = _values(candidate_values, "candidate values")
    return cue[:VISIBLE_WIDTH] == candidate[:VISIBLE_WIDTH]


def compare_shift_hint(cue_values: object, candidate_values: object) -> ShiftFinding:
    """Find a unique exact whole-overlap offset in the fixed one-cell range."""

    cue = _cells(_values(cue_values, "cue values"))
    candidate = _cells(_values(candidate_values, "candidate values"))
    matches: list[int] = []
    overlaps: dict[int, tuple[int, ...]] = {}
    for offset in OFFSETS:
        positions = tuple(column for column in range(COMPLETE_CELL_COUNT) if 0 <= column - offset < COMPLETE_CELL_COUNT)
        if all(cue[column] == candidate[column - offset] for column in positions):
            matches.append(offset)
            overlaps[offset] = positions
    if len(matches) == 1:
        offset = matches[0]
        return ShiftFinding("SHIFT_MATCH", (offset,), overlaps[offset])
    if len(matches) > 1:
        return ShiftFinding("SHIFT_OFFSET_AMBIGUOUS", tuple(matches), ())
    return ShiftFinding("SHIFT_NOT_APPLICABLE", (), ())


def collect_shift_hints(cue_values: object, candidates: object) -> ShiftHint:
    """Return all compatible candidates without ranking or public admission."""

    _values(cue_values, "cue values")
    if type(candidates) is not tuple:
        raise S2SPError("CANDIDATE_SET_INVALID", "candidates must be a tuple")
    candidate_ids: list[str] = []
    findings: list[ShiftFinding] = []
    ambiguous_offset = False
    for item in candidates:
        if type(item) is not tuple or len(item) != 2 or type(item[0]) is not str or not item[0]:
            raise S2SPError("CANDIDATE_SET_INVALID", "each candidate requires a non-empty technical id and values")
        finding = compare_shift_hint(cue_values, item[1])
        findings.append(finding)
        if finding.status == "SHIFT_MATCH":
            candidate_ids.append(item[0])
        ambiguous_offset = ambiguous_offset or finding.status == "SHIFT_OFFSET_AMBIGUOUS"
    if len(candidate_ids) == 1:
        status = "HINT_SINGLE"
    elif len(candidate_ids) > 1:
        status = "HINT_CANDIDATE_AMBIGUOUS"
    elif ambiguous_offset:
        status = "HINT_OFFSET_AMBIGUOUS"
    else:
        status = "HINT_NOT_APPLICABLE"
    return ShiftHint(status, tuple(candidate_ids), tuple(findings))
