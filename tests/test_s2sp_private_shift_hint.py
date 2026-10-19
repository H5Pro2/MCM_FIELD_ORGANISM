from __future__ import annotations

import unittest

from tools import _s2sp_private_shift_hint as shift


BACKGROUND = (24.0 / 255.0, 32.0 / 255.0, 48.0 / 255.0)
RED = (224.0 / 255.0, 64.0 / 255.0, 64.0 / 255.0)
GREEN = (64.0 / 255.0, 224.0 / 255.0, 64.0 / 255.0)
BLUE = (64.0 / 255.0, 64.0 / 255.0, 224.0 / 255.0)
YELLOW = (224.0 / 255.0, 224.0 / 255.0, 64.0 / 255.0)


def vector(cells: tuple[tuple[float, float, float], ...], *, hidden: float = 0.0) -> tuple[float, ...]:
    values = [hidden] * 288
    for column, triplet in enumerate(cells):
        values[3 * column : 3 * column + 3] = triplet
    return tuple(values)


def target_cells() -> tuple[tuple[float, float, float], ...]:
    return (BACKGROUND, RED, GREEN, BLUE, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND)


def right_shift(cells: tuple[tuple[float, float, float], ...]) -> tuple[tuple[float, float, float], ...]:
    return (BACKGROUND,) + cells[:-1]


class ShiftHintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.target = vector(target_cells())
        self.shifted = vector(right_shift(target_cells()))

    def test_one_cell_shift_is_a_unique_hint_but_not_an_exact_baseline_match(self) -> None:
        finding = shift.compare_shift_hint(self.shifted, self.target)
        self.assertEqual(finding.status, "SHIFT_MATCH")
        self.assertEqual(finding.matching_offsets, (1,))
        self.assertEqual(finding.overlap_cells, tuple(range(1, 10)))
        self.assertFalse(shift.exact_visible_match(self.shifted, self.target))

    def test_foreign_interior_change_does_not_match(self) -> None:
        foreign_cells = list(right_shift(target_cells()))
        foreign_cells[4] = YELLOW
        finding = shift.compare_shift_hint(self.shifted, vector(tuple(foreign_cells)))
        self.assertEqual(finding.status, "SHIFT_NOT_APPLICABLE")

    def test_unpaired_boundary_difference_is_visible_as_candidate_ambiguity(self) -> None:
        boundary = list(target_cells())
        boundary[9] = YELLOW
        hint = shift.collect_shift_hints(self.shifted, (("slot.a", self.target), ("slot.b", vector(tuple(boundary)))))
        self.assertEqual(hint.status, "HINT_CANDIDATE_AMBIGUOUS")
        self.assertEqual(hint.candidate_ids, ("slot.a", "slot.b"))

    def test_uniform_visible_row_has_offset_ambiguity(self) -> None:
        uniform = vector((BACKGROUND,) * 10)
        finding = shift.compare_shift_hint(uniform, uniform)
        self.assertEqual(finding.status, "SHIFT_OFFSET_AMBIGUOUS")
        self.assertEqual(finding.matching_offsets, (-1, 0, 1))
        hint = shift.collect_shift_hints(uniform, (("slot.uniform", uniform),))
        self.assertEqual(hint.status, "HINT_OFFSET_AMBIGUOUS")

    def test_masked_and_partial_visible_values_cannot_change_the_hint(self) -> None:
        changed = list(self.target)
        changed[30] = 1.0
        changed[31] = 1.0
        changed[100] = 1.0
        finding = shift.compare_shift_hint(self.shifted, tuple(changed))
        self.assertEqual(finding.status, "SHIFT_MATCH")
        self.assertEqual(finding.matching_offsets, (1,))

    def test_invalid_values_and_candidate_shapes_fail_closed(self) -> None:
        with self.assertRaises(shift.S2SPError) as bad_values:
            shift.compare_shift_hint(tuple([0.0] * 287), self.target)
        self.assertEqual(bad_values.exception.code, "VALUE_SHAPE_INVALID")
        with self.assertRaises(shift.S2SPError) as bad_candidates:
            shift.collect_shift_hints(self.target, (("", self.target),))
        self.assertEqual(bad_candidates.exception.code, "CANDIDATE_SET_INVALID")
