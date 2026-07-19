"""Passive fixed baselines for the continuous two-relation world."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
import math

from .continuous_two_relation_world import (
    CONTROL_IDS,
    ContinuousTwoRelationWorldError,
    ContinuousWorldObservation,
    _branch_events,
    run_continuous_two_relation_world_probe,
)


BASELINE_IDS = tuple(f"b{index}" for index in range(10))
_LEAKY_DECAYS = (0.25, 0.5, 0.75, 0.9, 0.99)


@dataclass(frozen=True, slots=True)
class ContinuousWorldControlScore:
    control_id: str
    total: int
    answered: int
    correct: int

    def __post_init__(self) -> None:
        if self.control_id not in CONTROL_IDS:
            raise ContinuousTwoRelationWorldError("unknown baseline control")
        if not 0 <= self.correct <= self.answered <= self.total:
            raise ContinuousTwoRelationWorldError("invalid control score counts")

    @property
    def coverage(self) -> float:
        return self.answered / self.total

    @property
    def accuracy(self) -> float | None:
        return None if self.answered == 0 else self.correct / self.answered


@dataclass(frozen=True, slots=True)
class ContinuousWorldBaselineScore:
    baseline_id: str
    total: int
    answered: int
    correct: int
    controls: tuple[ContinuousWorldControlScore, ...]

    def __post_init__(self) -> None:
        if self.baseline_id not in BASELINE_IDS:
            raise ContinuousTwoRelationWorldError("unknown baseline")
        if not 0 <= self.correct <= self.answered <= self.total:
            raise ContinuousTwoRelationWorldError("invalid baseline score counts")
        controls = tuple(self.controls)
        if tuple(item.control_id for item in controls) != CONTROL_IDS:
            raise ContinuousTwoRelationWorldError(
                "baseline controls must use canonical K0 through K7 order"
            )
        if sum(item.total for item in controls) != self.total:
            raise ContinuousTwoRelationWorldError("baseline control totals mismatch")
        if sum(item.answered for item in controls) != self.answered:
            raise ContinuousTwoRelationWorldError("baseline answer totals mismatch")
        if sum(item.correct for item in controls) != self.correct:
            raise ContinuousTwoRelationWorldError("baseline correct totals mismatch")
        object.__setattr__(self, "controls", controls)

    @property
    def coverage(self) -> float:
        return self.answered / self.total

    @property
    def accuracy(self) -> float | None:
        return None if self.answered == 0 else self.correct / self.answered

    def control(self, control_id: str) -> ContinuousWorldControlScore:
        return next(item for item in self.controls if item.control_id == control_id)


@dataclass(frozen=True, slots=True)
class ContinuousWorldBaselineResult:
    scores: tuple[ContinuousWorldBaselineScore, ...]
    b0_fast_state_is_exact_null: bool
    b6_solves_after_new_experience: bool
    b6_and_b9_are_functionally_equal: bool
    b7_fails_shifted_switch_positions: bool
    exact_template_has_partial_coverage: bool
    writes_back: bool
    adds_memory_role: bool
    changes_field_transition: bool

    def __post_init__(self) -> None:
        scores = tuple(self.scores)
        if tuple(item.baseline_id for item in scores) != BASELINE_IDS:
            raise ContinuousTwoRelationWorldError(
                "baseline result must contain B0 through B9"
            )
        if self.writes_back or self.adds_memory_role or self.changes_field_transition:
            raise ContinuousTwoRelationWorldError(
                "passive baselines cannot release runtime behavior"
            )
        object.__setattr__(self, "scores", scores)

    def score(self, baseline_id: str) -> ContinuousWorldBaselineScore:
        return next(item for item in self.scores if item.baseline_id == baseline_id)

    def digest(self) -> str:
        encoded = json.dumps(
            asdict(self),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def _sign(value: float) -> int | None:
    if math.isclose(value, 0.0, rel_tol=0.0, abs_tol=1e-15):
        return None
    return 1 if value > 0.0 else -1


def _history(
    observation: ContinuousWorldObservation,
):
    events, holdout = _branch_events(
        observation.control_id,
        observation.experience_count,
        observation.return_experience_count,
        observation.switch_contact_count,
        observation.order_variant,
        observation.duration_shift,
        observation.holdout_ingress,
    )
    return events, holdout


def _event_signature(event) -> tuple[object, ...]:
    return (
        event.ingress,
        event.exit_sign,
        event.occlusion_ticks,
        event.gap_ticks,
        event.pixel_value,
    )


def _template_bank(
    observations: tuple[ContinuousWorldObservation, ...],
) -> dict[tuple[tuple[object, ...], ...], int]:
    candidates: dict[tuple[tuple[object, ...], ...], set[int]] = {}
    for observation in observations:
        if observation.control_id not in ("k0", "k1"):
            continue
        events, _ = _history(observation)
        key = tuple(_event_signature(event) for event in events)
        relation_sign = 1 if observation.control_id == "k0" else -1
        candidates.setdefault(key, set()).add(relation_sign)
    return {
        key: next(iter(values))
        for key, values in candidates.items()
        if len(values) == 1
    }


def _predict(
    baseline_id: str,
    observation: ContinuousWorldObservation,
    template_bank: dict[tuple[tuple[object, ...], ...], int],
) -> int | None:
    events, _ = _history(observation)
    ingress = observation.holdout_ingress
    exits = tuple(event.exit_sign for event in events)
    relations = tuple(event.ingress * event.exit_sign for event in events)

    if baseline_id == "b0":
        weighted = sum(
            (index - (len(observation.pre_holdout_activation) - 1) / 2.0) * value
            for index, value in enumerate(observation.pre_holdout_activation)
        )
        return _sign(weighted)

    if baseline_id == "b1":
        votes = []
        for decay in _LEAKY_DECAYS:
            trace = 0.0
            for exit_sign in exits:
                trace = decay * trace + exit_sign
            vote = _sign(trace)
            if vote is not None:
                votes.append(vote)
        return _sign(sum(votes))

    if baseline_id == "b2":
        relation = _sign(sum(relations))
        return None if relation is None else relation * ingress

    if baseline_id == "b3":
        trace = 0.0
        for relation in relations:
            trace = 0.75 * trace + relation
        relation = _sign(trace)
        return None if relation is None else relation * ingress

    if baseline_id == "b4":
        return exits[-1] if exits else None

    if baseline_id == "b5":
        return ingress

    if baseline_id == "b6":
        return relations[-1] * ingress if relations else None

    if baseline_id == "b7":
        count = observation.completed_contacts
        relation = 1 if count < 8 or count >= 16 else -1
        return relation * ingress

    if baseline_id == "b8":
        key = tuple(_event_signature(event) for event in events)
        relation = template_bank.get(key)
        return None if relation is None else relation * ingress

    if baseline_id == "b9":
        # Both relation tables are permanent; the fixed reader selects the
        # relation evidenced by the latest completed contact.
        return relations[-1] * ingress if relations else None

    raise ContinuousTwoRelationWorldError("unknown baseline")


def _score(
    baseline_id: str,
    observations: tuple[ContinuousWorldObservation, ...],
    template_bank: dict[tuple[tuple[object, ...], ...], int],
) -> ContinuousWorldBaselineScore:
    controls = []
    for control_id in CONTROL_IDS:
        selected = tuple(
            item for item in observations if item.control_id == control_id
        )
        predictions = tuple(
            (_predict(baseline_id, item, template_bank), item.holdout_exit)
            for item in selected
        )
        answered = sum(prediction is not None for prediction, _ in predictions)
        correct = sum(
            prediction == target
            for prediction, target in predictions
            if prediction is not None
        )
        controls.append(
            ContinuousWorldControlScore(
                control_id=control_id,
                total=len(selected),
                answered=answered,
                correct=correct,
            )
        )
    return ContinuousWorldBaselineScore(
        baseline_id=baseline_id,
        total=sum(item.total for item in controls),
        answered=sum(item.answered for item in controls),
        correct=sum(item.correct for item in controls),
        controls=tuple(controls),
    )


def run_continuous_world_baselines() -> ContinuousWorldBaselineResult:
    """Evaluate fixed offline baselines against the frozen world observations."""

    world = run_continuous_two_relation_world_probe()
    observations = world.observations
    templates = _template_bank(observations)
    scores = tuple(
        _score(baseline_id, observations, templates)
        for baseline_id in BASELINE_IDS
    )
    by_id = {item.baseline_id: item for item in scores}
    b7_shifted = any(
        by_id["b7"].control(control_id).accuracy != 1.0
        for control_id in ("k0", "k2", "k3", "k6", "k7")
    )
    return ContinuousWorldBaselineResult(
        scores=scores,
        b0_fast_state_is_exact_null=all(
            all(value == 0.0 for value in item.pre_holdout_activation)
            and all(value == 0.0 for value in item.pre_holdout_afterimage)
            for item in observations
            if not item.observer_cue_present
        ),
        b6_solves_after_new_experience=all(
            _predict("b6", item, templates) == item.holdout_exit
            for item in observations
            if (
                item.control_id == "k3"
                and item.experience_count > 0
            )
            or (
                item.control_id == "k7"
                and item.return_experience_count > 0
            )
        ),
        b6_and_b9_are_functionally_equal=(
            by_id["b6"].total,
            by_id["b6"].answered,
            by_id["b6"].correct,
            by_id["b6"].controls,
        )
        == (
            by_id["b9"].total,
            by_id["b9"].answered,
            by_id["b9"].correct,
            by_id["b9"].controls,
        ),
        b7_fails_shifted_switch_positions=b7_shifted,
        exact_template_has_partial_coverage=0.0 < by_id["b8"].coverage < 1.0,
        writes_back=False,
        adds_memory_role=False,
        changes_field_transition=False,
    )


def continuous_world_baseline_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            ContinuousWorldControlScore,
            ContinuousWorldBaselineScore,
            ContinuousWorldBaselineResult,
        )
        for item in fields(contract)
    )
