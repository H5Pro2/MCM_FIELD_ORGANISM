"""Private linear-SFA method candidate; intentionally outside the MCM runtime."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Iterable, Sequence

import numpy as np


SCHEMA_VERSION = "s2.sfa.visual.method.v1"
EPSILON = 2.0**-40
RESIDUAL_ATOL = 1.0e-10
TIE_ATOL = 0.0


class SFAError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


PLANNED_CORPUS_BINDING = {
    "schema_version": SCHEMA_VERSION,
    "frame_shape": [1080, 1920, 3],
    "receptor_width": 288,
    "frame_count": 32,
    "episode_times_ms": [0, 100, 200, 300],
    "episodes": ("L1", "L2", "RA", "RB", "QA", "QB", "QAB", "QC"),
    "learning_episodes": ("L1", "L2"),
    "reference_episodes": ("RA", "RB"),
    "test_episodes": ("QA", "QB", "QAB", "QC"),
    "transition_policy": "within_episode_only",
    "feature_count": 1,
    "epsilon": EPSILON,
    "tie_atol": TIE_ATOL,
}
PLANNED_CORPUS_DIGEST = _digest(PLANNED_CORPUS_BINDING)


@dataclass(frozen=True, slots=True)
class LinearSFAConfig:
    epsilon: float = EPSILON
    residual_atol: float = RESIDUAL_ATOL
    tie_atol: float = TIE_ATOL

    def __post_init__(self) -> None:
        if not np.isfinite(self.epsilon) or self.epsilon <= 0.0:
            raise SFAError("SFA_CONFIG_INVALID", "epsilon must be finite and positive")
        if not np.isfinite(self.residual_atol) or self.residual_atol < 0.0:
            raise SFAError("SFA_CONFIG_INVALID", "residual_atol must be finite and non-negative")
        if self.tie_atol != 0.0:
            raise SFAError("SFA_CONFIG_INVALID", "tie_atol is fixed to exact equality")


@dataclass(frozen=True, slots=True)
class FrozenLinearSFA:
    mean: tuple[float, ...]
    raw_scales: tuple[float, ...]
    constant_indices: tuple[int, ...]
    retained_rank: int
    direction: tuple[float, ...]
    slowest_eigenvalue: float
    config: LinearSFAConfig

    @property
    def width(self) -> int:
        return len(self.mean)

    def transform_raw(self, sequence: object) -> np.ndarray:
        values = _sequence(sequence, width=self.width, role="raw sequence")
        mean = np.asarray(self.mean, dtype=np.float64)
        scales = np.asarray(self.raw_scales, dtype=np.float64)
        centered = values - mean
        return np.divide(centered, scales, out=centered.copy(), where=scales > self.config.epsilon)

    def transform_feature(self, sequence: object) -> np.ndarray:
        values = _sequence(sequence, width=self.width, role="feature sequence")
        direction = np.asarray(self.direction, dtype=np.float64)
        return ((values - np.asarray(self.mean, dtype=np.float64)) @ direction).reshape(-1, 1)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "mean": list(self.mean),
            "raw_scales": list(self.raw_scales),
            "constant_indices": list(self.constant_indices),
            "retained_rank": self.retained_rank,
            "direction": list(self.direction),
            "slowest_eigenvalue": self.slowest_eigenvalue,
            "config": {
                "epsilon": self.config.epsilon,
                "residual_atol": self.config.residual_atol,
                "tie_atol": self.config.tie_atol,
            },
        }

    @property
    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class RankDecision:
    expected_reference: str
    selected_reference: str | None
    status: str
    expected_score: float
    other_score: float


@dataclass(frozen=True, slots=True)
class ComparisonSummary:
    additional_correct: tuple[str, ...]
    losses: tuple[str, ...]
    confusions: tuple[str, ...]
    abstentions: tuple[str, ...]


class LinearSFALearner:
    """Private learning boundary that accepts only prior segments until frozen."""

    def __init__(self, *, config: LinearSFAConfig = LinearSFAConfig()) -> None:
        self._config = config
        self._segments: list[np.ndarray] = []
        self._frozen: FrozenLinearSFA | None = None

    def observe(self, segment: object) -> None:
        if self._frozen is not None:
            raise SFAError("SFA_LEARNER_FROZEN", "learning input is forbidden after freeze")
        values = _sequence(segment, width=None, role="learning segment")
        self._segments.append(values.copy())

    def freeze(self) -> FrozenLinearSFA:
        if self._frozen is None:
            self._frozen = fit_linear_sfa(self._segments, config=self._config)
        return self._frozen


def _sequence(value: object, *, width: int | None, role: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != 2 or array.shape[0] < 2 or (width is not None and array.shape[1] != width):
        raise SFAError("SFA_INPUT_INVALID", f"{role} must be a finite two-dimensional sequence")
    if not np.all(np.isfinite(array)):
        raise SFAError("SFA_INPUT_INVALID", f"{role} must be finite")
    return array


def _learning_sequences(segments: Iterable[object]) -> tuple[np.ndarray, ...]:
    materialized = tuple(_sequence(item, width=None, role="learning segment") for item in segments)
    if len(materialized) < 1:
        raise SFAError("SFA_INPUT_INVALID", "at least one learning segment is required")
    width = materialized[0].shape[1]
    if width < 2 or any(item.shape[1] != width for item in materialized):
        raise SFAError("SFA_INPUT_INVALID", "learning segments require a shared width of at least two")
    return materialized


def _require_simple_slowest(values: np.ndarray, *, epsilon: float) -> tuple[float, np.ndarray]:
    eigenvalues, eigenvectors = np.linalg.eigh(values)
    if not np.all(np.isfinite(eigenvalues)) or not np.all(np.isfinite(eigenvectors)) or len(eigenvalues) < 2:
        raise SFAError("SFA_TRAINING_DEGENERATE", "slow feature eigensystem is invalid")
    first, second = float(eigenvalues[0]), float(eigenvalues[1])
    if second - first <= epsilon * max(1.0, abs(first), abs(second)):
        raise SFAError("SFA_TRAINING_DEGENERATE", "slowest direction is not unique")
    return first, eigenvectors[:, 0]


def fit_linear_sfa(segments: Iterable[object], *, config: LinearSFAConfig = LinearSFAConfig()) -> FrozenLinearSFA:
    """Fit one frozen, basis-invariant linear SFA direction from prior segments only."""

    learning = _learning_sequences(segments)
    stacked = np.concatenate(learning, axis=0)
    mean = stacked.mean(axis=0)
    centered = stacked - mean
    covariance = centered.T @ centered / float(len(stacked))
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    largest = float(eigenvalues[-1])
    if not np.isfinite(largest) or largest <= 0.0:
        raise SFAError("SFA_TRAINING_DEGENERATE", "learning covariance has no positive variance")
    retained = eigenvalues > config.epsilon * largest
    if int(np.count_nonzero(retained)) < 2:
        raise SFAError("SFA_TRAINING_DEGENERATE", "learning covariance rank is insufficient")
    basis = eigenvectors[:, retained]
    scales = np.sqrt(eigenvalues[retained])
    whitening = basis / scales
    transitions = np.concatenate(tuple(np.diff(segment, axis=0) for segment in learning), axis=0)
    derivative_covariance = transitions.T @ transitions / float(len(transitions))
    projected_derivative = whitening.T @ derivative_covariance @ whitening
    slowest, vector = _require_simple_slowest(projected_derivative, epsilon=config.epsilon)
    direction = whitening @ vector
    first_nonzero = np.flatnonzero(np.abs(direction) >= config.epsilon)
    if len(first_nonzero) == 0:
        raise SFAError("SFA_TRAINING_DEGENERATE", "slow direction has no canonical sign")
    if direction[int(first_nonzero[0])] < 0.0:
        direction = -direction
    residual = derivative_covariance @ direction - slowest * (covariance @ direction)
    normalization = float(direction @ covariance @ direction)
    if np.max(np.abs(residual)) > config.residual_atol or abs(normalization - 1.0) > config.residual_atol:
        raise SFAError("SFA_NUMERICAL_RESIDUAL_INVALID", "projected eigensolution failed independent residual checks")
    raw_scales = np.sqrt(np.mean(np.square(centered), axis=0))
    constants = tuple(int(index) for index in np.flatnonzero(raw_scales <= config.epsilon))
    return FrozenLinearSFA(
        tuple(float(item) for item in mean),
        tuple(float(item) for item in raw_scales),
        constants,
        int(np.count_nonzero(retained)),
        tuple(float(item) for item in direction),
        slowest,
        config,
    )


def sequence_score(query: object, reference: object) -> float:
    left = _sequence(query, width=None, role="query")
    right = _sequence(reference, width=left.shape[1], role="reference")
    if left.shape != right.shape:
        raise SFAError("SFA_INPUT_INVALID", "query and reference shapes must match")
    return float(np.mean(np.abs(left - right)))


def rank_two_references(
    query: object,
    reference_a: object,
    reference_b: object,
    *,
    expected_reference: str,
    config: LinearSFAConfig = LinearSFAConfig(),
) -> RankDecision:
    if expected_reference not in {"A", "B"}:
        raise SFAError("SFA_EVALUATION_INVALID", "expected reference must be A or B")
    a_score = sequence_score(query, reference_a)
    b_score = sequence_score(query, reference_b)
    expected_score, other_score = (a_score, b_score) if expected_reference == "A" else (b_score, a_score)
    if a_score == b_score:
        return RankDecision(expected_reference, None, "ABSTAIN_TIE", expected_score, other_score)
    selected = "A" if a_score < b_score else "B"
    return RankDecision(
        expected_reference,
        selected,
        "CORRECT" if selected == expected_reference else "CONFUSION",
        expected_score,
        other_score,
    )


def summarize_comparison(rows: Sequence[tuple[str, RankDecision, RankDecision]]) -> ComparisonSummary:
    additional: list[str] = []
    losses: list[str] = []
    confusions: list[str] = []
    abstentions: list[str] = []
    for case_id, raw, sfa in rows:
        if raw.status == "CORRECT" and sfa.status != "CORRECT":
            losses.append(case_id)
        if raw.status != "CORRECT" and sfa.status == "CORRECT":
            additional.append(case_id)
        if sfa.status == "CONFUSION":
            confusions.append(case_id)
        if sfa.status == "ABSTAIN_TIE":
            abstentions.append(case_id)
    return ComparisonSummary(tuple(additional), tuple(losses), tuple(confusions), tuple(abstentions))
