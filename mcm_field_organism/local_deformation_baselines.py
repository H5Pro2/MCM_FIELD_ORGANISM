"""Passive fixed L0-L9 baselines for the local deformation world."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
import math

from .local_deformation_world import (
    FORM_ANCHORS,
    GROUP_IDS,
    LocalDeformationObservation,
    LocalDeformationWorldError,
    _branch_history,
    run_local_deformation_world_probe,
)


BASELINE_IDS = tuple(f"l{index}" for index in range(10))


@dataclass(frozen=True, slots=True)
class DeformationGroupScore:
    group_id: str
    total: int
    answered: int
    correct: int

    def __post_init__(self) -> None:
        if self.group_id not in GROUP_IDS:
            raise LocalDeformationWorldError("unknown baseline group")
        if not 0 <= self.correct <= self.answered <= self.total:
            raise LocalDeformationWorldError("invalid group score")

    @property
    def coverage(self) -> float:
        return self.answered / self.total

    @property
    def accuracy(self) -> float | None:
        return None if not self.answered else self.correct / self.answered


@dataclass(frozen=True, slots=True)
class DeformationBaselineScore:
    baseline_id: str
    total: int
    answered: int
    correct: int
    groups: tuple[DeformationGroupScore, ...]

    def __post_init__(self) -> None:
        if self.baseline_id not in BASELINE_IDS:
            raise LocalDeformationWorldError("unknown baseline")
        if tuple(item.group_id for item in self.groups) != GROUP_IDS:
            raise LocalDeformationWorldError("baseline groups must be canonical")
        if not 0 <= self.correct <= self.answered <= self.total:
            raise LocalDeformationWorldError("invalid baseline score")
        if sum(item.total for item in self.groups) != self.total:
            raise LocalDeformationWorldError("group total mismatch")
        if sum(item.answered for item in self.groups) != self.answered:
            raise LocalDeformationWorldError("group answer mismatch")
        if sum(item.correct for item in self.groups) != self.correct:
            raise LocalDeformationWorldError("group correct mismatch")

    @property
    def coverage(self) -> float:
        return self.answered / self.total

    @property
    def accuracy(self) -> float | None:
        return None if not self.answered else self.correct / self.answered

    def group(self, group_id: str) -> DeformationGroupScore:
        return next(item for item in self.groups if item.group_id == group_id)


@dataclass(frozen=True, slots=True)
class LocalDeformationBaselineResult:
    scores: tuple[DeformationBaselineScore, ...]
    l4_solves_all_identifiable_valid_holdouts: bool
    l4_requires_bracketing_contacts: bool
    l9_archive_does_not_outperform_l4: bool
    d5_breaks_local_interpolation: bool
    old_history_is_irrelevant_after_d4: bool
    writes_back: bool
    adds_memory_role: bool
    changes_field_transition: bool

    def __post_init__(self) -> None:
        if tuple(item.baseline_id for item in self.scores) != BASELINE_IDS:
            raise LocalDeformationWorldError("result must contain L0 through L9")
        if self.writes_back or self.adds_memory_role or self.changes_field_transition:
            raise LocalDeformationWorldError("passive baselines cannot change runtime")

    def score(self, baseline_id: str) -> DeformationBaselineScore:
        return next(item for item in self.scores if item.baseline_id == baseline_id)

    def digest(self) -> str:
        encoded = json.dumps(
            asdict(self),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def _history(item: LocalDeformationObservation):
    events, _, _ = _branch_history(
        item.group_id,
        item.stage_id,
        item.world_variant,
        item.order_variant,
        item.duration_shift,
    )
    return events


def _latest_by_x(events) -> dict[int, int]:
    latest = {}
    for event in events:
        latest[event.ingress] = event.exit
    return latest


def _linear(x: int, left: tuple[int, int], right: tuple[int, int]) -> int | None:
    x0, y0 = left
    x1, y1 = right
    if x0 == x1:
        return None
    value = y0 + (x - x0) * (y1 - y0) / (x1 - x0)
    return round(value)


def _bracket(points: dict[int, int], x: int) -> tuple[tuple[int, int], tuple[int, int]] | None:
    left = [position for position in points if position < x]
    right = [position for position in points if position > x]
    if not left or not right:
        return None
    x0 = max(left)
    x1 = min(right)
    return (x0, points[x0]), (x1, points[x1])


def _nearest_two(points: dict[int, int], x: int):
    ordered = sorted(points.items(), key=lambda item: (abs(item[0] - x), item[0]))
    return None if len(ordered) < 2 else (ordered[0], ordered[1])


def _last_two_distinct(events):
    selected = []
    seen = set()
    for event in reversed(events):
        if event.ingress not in seen:
            selected.append((event.ingress, event.exit))
            seen.add(event.ingress)
        if len(selected) == 2:
            return tuple(reversed(selected))
    return None


def _lagrange(points: tuple[tuple[int, int], ...], x: int) -> int | None:
    if len(points) < 3:
        return None
    value = 0.0
    for i, (xi, yi) in enumerate(points):
        term = float(yi)
        for j, (xj, _) in enumerate(points):
            if i != j:
                term *= (x - xj) / (xi - xj)
        value += term
    return round(value)


def _least_squares(points: dict[int, int], x: int) -> int | None:
    if len(points) < 2:
        return None
    xs = tuple(points)
    ys = tuple(points[position] for position in xs)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((value - mean_x) ** 2 for value in xs)
    if math.isclose(denominator, 0.0):
        return None
    slope = sum((px - mean_x) * (py - mean_y) for px, py in zip(xs, ys)) / denominator
    return round(mean_y + slope * (x - mean_x))


def _template_prediction(points: dict[int, int], x: int) -> int | None:
    if not points:
        return None
    candidates = []
    for form_id in ("f0", "f1"):
        template = dict(FORM_ANCHORS[form_id])
        error = sum((template[px] - py) ** 2 for px, py in points.items())
        candidates.append((error, form_id))
    candidates.sort()
    if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
        return None
    return dict(FORM_ANCHORS[candidates[0][1]]).get(x) or _piecewise(
        dict(FORM_ANCHORS[candidates[0][1]]), x
    )


def _piecewise(points: dict[int, int], x: int) -> int | None:
    if x in points:
        return points[x]
    bracket = _bracket(points, x)
    return None if bracket is None else _linear(x, *bracket)


def _reservoir_prediction(events, x: int) -> int | None:
    state = [0.0, 0.0, 0.0]
    for event in events:
        displacement = (event.exit - event.ingress) / 12.0
        state = [
            math.tanh(0.65 * state[0] + event.ingress / 12.0),
            math.tanh(0.55 * state[1] + event.exit / 12.0),
            math.tanh(0.45 * state[2] + displacement),
        ]
    if not events:
        return None
    return round(x + 12.0 * state[2])


def _predict(baseline_id: str, item: LocalDeformationObservation) -> int | None:
    events = _history(item)
    x = item.holdout_ingress
    points = _latest_by_x(events)

    if baseline_id == "l0":
        if not item.pre_holdout_activation:
            return None
        maximum = max(item.pre_holdout_activation)
        if math.isclose(maximum, 0.0, abs_tol=1e-15):
            return None
        winners = [
            index
            for index, value in enumerate(item.pre_holdout_activation)
            if math.isclose(value, maximum, rel_tol=0.0, abs_tol=1e-15)
        ]
        return winners[0] if len(winners) == 1 else None
    if baseline_id == "l1":
        return None if not events else x + events[-1].exit - events[-1].ingress
    if baseline_id == "l2":
        pair = _last_two_distinct(events)
        return None if pair is None else _linear(x, *pair)
    if baseline_id == "l3":
        pair = _nearest_two(points, x)
        return None if pair is None else _linear(x, *pair)
    if baseline_id == "l4":
        return _piecewise(points, x)
    if baseline_id == "l5":
        nearest = tuple(
            sorted(points.items(), key=lambda point: (abs(point[0] - x), point[0]))[:3]
        )
        return _lagrange(nearest, x)
    if baseline_id == "l6":
        return _least_squares(points, x)
    if baseline_id == "l7":
        return _template_prediction(points, x)
    if baseline_id == "l8":
        return _reservoir_prediction(events, x)
    if baseline_id == "l9":
        return _piecewise(_latest_by_x(events), x)
    raise LocalDeformationWorldError("unknown baseline")


def _score(
    baseline_id: str,
    observations: tuple[LocalDeformationObservation, ...],
) -> DeformationBaselineScore:
    groups = []
    for group_id in GROUP_IDS:
        selected = tuple(item for item in observations if item.group_id == group_id)
        predictions = tuple((_predict(baseline_id, item), item.holdout_exit) for item in selected)
        answered = sum(prediction is not None for prediction, _ in predictions)
        correct = sum(
            prediction == target
            for prediction, target in predictions
            if prediction is not None
        )
        groups.append(
            DeformationGroupScore(group_id, len(selected), answered, correct)
        )
    return DeformationBaselineScore(
        baseline_id,
        sum(item.total for item in groups),
        sum(item.answered for item in groups),
        sum(item.correct for item in groups),
        tuple(groups),
    )


def run_local_deformation_baselines() -> LocalDeformationBaselineResult:
    """Evaluate frozen offline baselines against the deformation world."""

    world = run_local_deformation_world_probe()
    observations = world.observations
    scores = tuple(_score(baseline_id, observations) for baseline_id in BASELINE_IDS)
    valid_identifiable = tuple(
        item
        for item in observations
        if item.local_pairing_valid and item.identifiable_holdout
    )
    d4 = tuple(
        item
        for item in observations
        if item.local_pairing_valid and item.stage_id == "d4"
    )
    d5 = tuple(item for item in observations if item.group_id == "g7")
    l4_d4 = tuple(_predict("l4", item) for item in d4)
    l9_d4 = tuple(_predict("l9", item) for item in d4)
    g5_d4 = tuple(
        item for item in observations if item.group_id == "g5" and item.stage_id == "d4"
    )
    g5_predictions = {}
    g5_variants = {}
    for item in g5_d4:
        key = (item.order_variant, item.duration_shift, item.holdout_ingress)
        g5_predictions.setdefault(key, set()).add(_predict("l4", item))
        g5_variants.setdefault(key, set()).add(item.world_variant)
    return LocalDeformationBaselineResult(
        scores=scores,
        l4_solves_all_identifiable_valid_holdouts=all(
            _predict("l4", item) == item.holdout_exit for item in valid_identifiable
        ),
        l4_requires_bracketing_contacts=all(
            _predict("l4", item) is None
            for item in observations
            if item.group_id in ("g0", "g1") and item.stage_id in ("d0", "d1")
        ),
        l9_archive_does_not_outperform_l4=l4_d4 == l9_d4,
        d5_breaks_local_interpolation=any(
            _predict("l4", item) != item.holdout_exit for item in d5
        ),
        old_history_is_irrelevant_after_d4=(
            bool(g5_predictions)
            and all(len(predictions) == 1 for predictions in g5_predictions.values())
            and all(variants == {"a", "b"} for variants in g5_variants.values())
        ),
        writes_back=False,
        adds_memory_role=False,
        changes_field_transition=False,
    )


def local_deformation_baseline_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            DeformationGroupScore,
            DeformationBaselineScore,
            LocalDeformationBaselineResult,
        )
        for item in fields(contract)
    )
