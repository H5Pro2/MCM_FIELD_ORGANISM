"""Independent frozen, replay, and adaptive baselines for S2-KK."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from tools import _s2kk_context_utility_fixtures as fixtures


S2KK_BASELINE_SCHEMA = "s2kk.context-utility-baseline.v1"
AUDITORY_THRESHOLD = 0.02
VISUAL_THRESHOLD = 0.01
UPDATE_RATE = 0.05
STABLE_AFTER = 3
FORMATION_COUNT = 17
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2KKBaselineError(ValueError):
    """One independent baseline input or relation is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2KKBaselineError(message)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _values(value: object, dimension: int, label: str) -> tuple[float, ...]:
    _require(type(value) is tuple and len(value) == dimension, f"{label} dimension differs")
    assert isinstance(value, tuple)
    _require(
        all(
            type(item) in (int, float)
            and not isinstance(item, bool)
            and math.isfinite(float(item))
            and 0.0 <= float(item) <= 1.0
            for item in value
        ),
        f"{label} values differ",
    )
    return tuple(float(item) for item in value)


def _distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    _require(len(left) == len(right) and bool(left), "distance dimensions differ")
    return sum(abs(a - b) for a, b in zip(left, right, strict=True)) / len(left)


@dataclass(frozen=True, slots=True)
class BaselineTrainingInput336V1:
    formation_ordinal: int
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    source_digest: str
    input_digest: str
    schema: str = S2KK_BASELINE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "kind": "TRAINING_INPUT",
            "formation_ordinal": self.formation_ordinal,
            "auditory_values": list(self.auditory_values),
            "visual_values": list(self.visual_values),
            "source_digest": self.source_digest,
        }


@dataclass(frozen=True, slots=True)
class BaselineProbe336V1:
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    source_digest: str
    probe_digest: str
    schema: str = S2KK_BASELINE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "kind": "FULL_RETRIEVAL_PROBE",
            "auditory_values": list(self.auditory_values),
            "visual_values": list(self.visual_values),
            "source_digest": self.source_digest,
        }


@dataclass(frozen=True, slots=True)
class S2KKBaselineStateV1:
    formation_count: int
    replay: tuple[tuple[str, tuple[float, ...], tuple[float, ...]], ...]
    frozen_auditory: tuple[float, ...] | None
    frozen_visual: tuple[float, ...] | None
    adaptive_auditory: tuple[float, ...] | None
    adaptive_visual: tuple[float, ...] | None
    adaptive_support: int
    state_digest: str
    schema: str = S2KK_BASELINE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "kind": "BASELINE_STATE",
            "formation_count": self.formation_count,
            "replay": [
                [source_digest, _digest(list(auditory)), _digest(list(visual))]
                for source_digest, auditory, visual in self.replay
            ],
            "frozen_digests": None
            if self.frozen_auditory is None
            else [_digest(list(self.frozen_auditory)), _digest(list(self.frozen_visual))],
            "adaptive_digests": None
            if self.adaptive_auditory is None
            else [_digest(list(self.adaptive_auditory)), _digest(list(self.adaptive_visual))],
            "adaptive_support": self.adaptive_support,
        }


@dataclass(frozen=True, slots=True)
class BaselineRetrieval336V1:
    method: str
    status: str
    probe_digest: str
    candidate_values: tuple[float, ...] | None
    candidate_values_digest: str | None
    auditory_distance: float
    visual_distance: float
    state_digest: str
    prestate_digest: str
    poststate_digest: str
    retrieval_digest: str
    schema: str = S2KK_BASELINE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "kind": "BASELINE_RETRIEVAL",
            "method": self.method,
            "status": self.status,
            "probe_digest": self.probe_digest,
            "candidate_values": None if self.candidate_values is None else list(self.candidate_values),
            "candidate_values_digest": self.candidate_values_digest,
            "auditory_distance": self.auditory_distance,
            "visual_distance": self.visual_distance,
            "state_digest": self.state_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
        }


@dataclass(frozen=True, slots=True)
class BaselineCompletion336V1:
    method: str
    status: str
    probe_digest: str
    retrieval_digest: str
    input_values: tuple[float | None, ...]
    output_values: tuple[float | None, ...]
    completed_positions: tuple[int, ...]
    prestate_digest: str
    poststate_digest: str
    visible_compare_count: int
    masked_copy_count: int
    result_digest: str
    schema: str = S2KK_BASELINE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "kind": "BASELINE_COMPLETION",
            "method": self.method,
            "status": self.status,
            "probe_digest": self.probe_digest,
            "retrieval_digest": self.retrieval_digest,
            "input_values": list(self.input_values),
            "output_values": list(self.output_values),
            "completed_positions": list(self.completed_positions),
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "visible_compare_count": self.visible_compare_count,
            "masked_copy_count": self.masked_copy_count,
        }


def bind_training_input(
    *,
    formation_ordinal: int,
    auditory_values: tuple[float, ...],
    visual_values: tuple[float, ...],
    source_digest: str,
) -> BaselineTrainingInput336V1:
    auditory = _values(auditory_values, 48, "training auditory")
    visual = _values(visual_values, 288, "training visual")
    _require(
        type(formation_ordinal) is int
        and 1 <= formation_ordinal <= FORMATION_COUNT
        and isinstance(source_digest, str)
        and _DIGEST.fullmatch(source_digest) is not None,
        "training source binding differs",
    )
    payload = {
        "schema": S2KK_BASELINE_SCHEMA,
        "kind": "TRAINING_INPUT",
        "formation_ordinal": formation_ordinal,
        "auditory_values": list(auditory),
        "visual_values": list(visual),
        "source_digest": source_digest,
    }
    return BaselineTrainingInput336V1(
        formation_ordinal,
        auditory,
        visual,
        source_digest,
        _digest(payload),
    )


def bind_full_probe(
    *,
    auditory_values: tuple[float, ...],
    visual_values: tuple[float, ...],
    source_digest: str,
) -> BaselineProbe336V1:
    auditory = _values(auditory_values, 48, "probe auditory")
    visual = _values(visual_values, 288, "probe visual")
    _require(
        isinstance(source_digest, str) and _DIGEST.fullmatch(source_digest) is not None,
        "probe source binding differs",
    )
    payload = {
        "schema": S2KK_BASELINE_SCHEMA,
        "kind": "FULL_RETRIEVAL_PROBE",
        "auditory_values": list(auditory),
        "visual_values": list(visual),
        "source_digest": source_digest,
    }
    return BaselineProbe336V1(auditory, visual, source_digest, _digest(payload))


def _validate_training(value: object) -> BaselineTrainingInput336V1:
    _require(type(value) is BaselineTrainingInput336V1, "exact training input required")
    assert isinstance(value, BaselineTrainingInput336V1)
    _values(value.auditory_values, 48, "training auditory")
    _values(value.visual_values, 288, "training visual")
    _require(
        value.schema == S2KK_BASELINE_SCHEMA
        and 1 <= value.formation_ordinal <= FORMATION_COUNT
        and _DIGEST.fullmatch(value.source_digest) is not None
        and value.input_digest == _digest(value.payload_without_digest()),
        "training input relation differs",
    )
    return value


def _validate_probe(value: object) -> BaselineProbe336V1:
    _require(type(value) is BaselineProbe336V1, "exact full probe required")
    assert isinstance(value, BaselineProbe336V1)
    _values(value.auditory_values, 48, "probe auditory")
    _values(value.visual_values, 288, "probe visual")
    _require(
        value.schema == S2KK_BASELINE_SCHEMA
        and _DIGEST.fullmatch(value.source_digest) is not None
        and value.probe_digest == _digest(value.payload_without_digest()),
        "probe relation differs",
    )
    return value


def _validate_state(value: object) -> S2KKBaselineStateV1:
    _require(type(value) is S2KKBaselineStateV1, "exact baseline state required")
    assert isinstance(value, S2KKBaselineStateV1)
    _require(
        value.schema == S2KK_BASELINE_SCHEMA
        and type(value.formation_count) is int
        and 0 <= value.formation_count <= FORMATION_COUNT
        and len(value.replay) == value.formation_count
        and value.state_digest == _digest(value.payload_without_digest()),
        "baseline state relation differs",
    )
    for source_digest, auditory, visual in value.replay:
        _require(_DIGEST.fullmatch(source_digest) is not None, "replay source digest differs")
        _values(auditory, 48, "replay auditory")
        _values(visual, 288, "replay visual")
    if value.formation_count < 2:
        _require(
            value.frozen_auditory is value.frozen_visual is value.adaptive_auditory is value.adaptive_visual is None
            and value.adaptive_support == 0,
            "premature baseline state differs",
        )
    else:
        _values(value.frozen_auditory, 48, "frozen auditory")
        _values(value.frozen_visual, 288, "frozen visual")
        _values(value.adaptive_auditory, 48, "adaptive auditory")
        _values(value.adaptive_visual, 288, "adaptive visual")
        _require(1 <= value.adaptive_support <= STABLE_AFTER, "adaptive support differs")
    return value


def initial_baseline_state() -> S2KKBaselineStateV1:
    payload = {
        "schema": S2KK_BASELINE_SCHEMA,
        "kind": "BASELINE_STATE",
        "formation_count": 0,
        "replay": [],
        "frozen_digests": None,
        "adaptive_digests": None,
        "adaptive_support": 0,
    }
    return S2KKBaselineStateV1(0, (), None, None, None, None, 0, _digest(payload))


def advance_baselines(
    state: S2KKBaselineStateV1,
    training: BaselineTrainingInput336V1,
) -> S2KKBaselineStateV1:
    state = _validate_state(state)
    training = _validate_training(training)
    ordinal = state.formation_count + 1
    _require(training.formation_ordinal == ordinal, "baseline formation order differs")
    replay = state.replay + ((training.source_digest, training.auditory_values, training.visual_values),)
    frozen_a, frozen_v = state.frozen_auditory, state.frozen_visual
    adaptive_a, adaptive_v = state.adaptive_auditory, state.adaptive_visual
    support = state.adaptive_support
    if ordinal == 2:
        frozen_a, frozen_v = training.auditory_values, training.visual_values
        adaptive_a, adaptive_v = training.auditory_values, training.visual_values
        support = 1
    elif 3 <= ordinal <= 8:
        _require(adaptive_a is not None and adaptive_v is not None, "adaptive prestate missing")
        adaptive_a = tuple(
            (1.0 - UPDATE_RATE) * old + UPDATE_RATE * new
            for old, new in zip(adaptive_a, training.auditory_values, strict=True)
        )
        adaptive_v = tuple(
            (1.0 - UPDATE_RATE) * old + UPDATE_RATE * new
            for old, new in zip(adaptive_v, training.visual_values, strict=True)
        )
        support = min(STABLE_AFTER, support + 1)
    payload = {
        "schema": S2KK_BASELINE_SCHEMA,
        "kind": "BASELINE_STATE",
        "formation_count": ordinal,
        "replay": [
            [source_digest, _digest(list(auditory)), _digest(list(visual))]
            for source_digest, auditory, visual in replay
        ],
        "frozen_digests": None
        if frozen_a is None
        else [_digest(list(frozen_a)), _digest(list(frozen_v))],
        "adaptive_digests": None
        if adaptive_a is None
        else [_digest(list(adaptive_a)), _digest(list(adaptive_v))],
        "adaptive_support": support,
    }
    return _validate_state(
        S2KKBaselineStateV1(
            ordinal,
            replay,
            frozen_a,
            frozen_v,
            adaptive_a,
            adaptive_v,
            support,
            _digest(payload),
        )
    )


def _make_retrieval(
    method: str,
    state: S2KKBaselineStateV1,
    probe: BaselineProbe336V1,
    candidate: tuple[float, ...] | None,
    auditory_distance: float,
    visual_distance: float,
) -> BaselineRetrieval336V1:
    matched = (
        candidate is not None
        and auditory_distance <= AUDITORY_THRESHOLD
        and visual_distance <= VISUAL_THRESHOLD
    )
    exposed = candidate if matched else None
    payload = {
        "schema": S2KK_BASELINE_SCHEMA,
        "kind": "BASELINE_RETRIEVAL",
        "method": method,
        "status": "MATCH" if matched else "NO_MATCH",
        "probe_digest": probe.probe_digest,
        "candidate_values": None if exposed is None else list(exposed),
        "candidate_values_digest": None if exposed is None else _digest(list(exposed)),
        "auditory_distance": auditory_distance,
        "visual_distance": visual_distance,
        "state_digest": state.state_digest,
        "prestate_digest": state.state_digest,
        "poststate_digest": state.state_digest,
    }
    return BaselineRetrieval336V1(
        method,
        payload["status"],
        probe.probe_digest,
        exposed,
        payload["candidate_values_digest"],
        auditory_distance,
        visual_distance,
        state.state_digest,
        state.state_digest,
        state.state_digest,
        _digest(payload),
    )


def probe_baselines(
    state: S2KKBaselineStateV1,
    probe: BaselineProbe336V1,
) -> tuple[BaselineRetrieval336V1, BaselineRetrieval336V1, BaselineRetrieval336V1]:
    state = _validate_state(state)
    probe = _validate_probe(probe)
    _require(state.formation_count == FORMATION_COUNT, "complete baseline training required")
    assert state.frozen_auditory is not None and state.frozen_visual is not None
    assert state.adaptive_auditory is not None and state.adaptive_visual is not None
    frozen = _make_retrieval(
        "FROZEN_FIRST_PROTOTYPE",
        state,
        probe,
        state.frozen_visual,
        _distance(probe.auditory_values, state.frozen_auditory),
        _distance(probe.visual_values, state.frozen_visual),
    )
    nearest = min(
        state.replay,
        key=lambda item: (
            _distance(probe.auditory_values, item[1]) + _distance(probe.visual_values, item[2]),
            item[0],
        ),
    )
    replay = _make_retrieval(
        "REPLAY_NEAREST_EXEMPLAR",
        state,
        probe,
        nearest[2],
        _distance(probe.auditory_values, nearest[1]),
        _distance(probe.visual_values, nearest[2]),
    )
    adaptive_candidate = state.adaptive_visual if state.adaptive_support >= STABLE_AFTER else None
    adaptive = _make_retrieval(
        "DIRECT_ADAPTIVE_MASK_FILL",
        state,
        probe,
        adaptive_candidate,
        _distance(probe.auditory_values, state.adaptive_auditory),
        _distance(probe.visual_values, state.adaptive_visual),
    )
    _require(state.state_digest == frozen.poststate_digest == replay.poststate_digest == adaptive.poststate_digest, "baseline probe changed state")
    return frozen, replay, adaptive


def complete_from_baseline(
    *,
    retrieval: BaselineRetrieval336V1,
    masked_probe: fixtures.MaskedVisualPerception336V1,
) -> BaselineCompletion336V1:
    _require(type(retrieval) is BaselineRetrieval336V1, "exact baseline retrieval required")
    masked_probe = fixtures._validate_masked(masked_probe)
    _require(
        retrieval.method in {"FROZEN_FIRST_PROTOTYPE", "REPLAY_NEAREST_EXEMPLAR", "DIRECT_ADAPTIVE_MASK_FILL"}
        and retrieval.prestate_digest == retrieval.state_digest == retrieval.poststate_digest
        and retrieval.retrieval_digest == _digest(retrieval.payload_without_digest()),
        "baseline retrieval relation differs",
    )
    completed: tuple[int, ...] = ()
    output = masked_probe.values
    status = "NO_MATCH"
    visible_compares = 0
    masked_copies = 0
    if retrieval.status == "MATCH":
        candidate = _values(retrieval.candidate_values, 288, "retrieval candidate")
        visible_compares = len(fixtures.VISIBLE_POSITIONS)
        if all(masked_probe.values[index] == candidate[index] for index in fixtures.VISIBLE_POSITIONS):
            output = tuple(
                masked_probe.values[index]
                if index in fixtures.VISIBLE_POSITIONS
                else candidate[index]
                for index in range(288)
            )
            completed = fixtures.MASKED_POSITIONS
            status = "COMPLETED"
            masked_copies = len(fixtures.MASKED_POSITIONS)
        else:
            status = "VISIBLE_CONFLICT"
    else:
        _require(retrieval.status == "NO_MATCH" and retrieval.candidate_values is None, "baseline no-match anatomy differs")
    payload = {
        "schema": S2KK_BASELINE_SCHEMA,
        "kind": "BASELINE_COMPLETION",
        "method": retrieval.method,
        "status": status,
        "probe_digest": masked_probe.probe_digest,
        "retrieval_digest": retrieval.retrieval_digest,
        "input_values": list(masked_probe.values),
        "output_values": list(output),
        "completed_positions": list(completed),
        "prestate_digest": retrieval.state_digest,
        "poststate_digest": retrieval.state_digest,
        "visible_compare_count": visible_compares,
        "masked_copy_count": masked_copies,
    }
    return BaselineCompletion336V1(
        retrieval.method,
        status,
        masked_probe.probe_digest,
        retrieval.retrieval_digest,
        masked_probe.values,
        output,
        completed,
        retrieval.state_digest,
        retrieval.state_digest,
        visible_compares,
        masked_copies,
        _digest(payload),
    )


__all__ = ()
