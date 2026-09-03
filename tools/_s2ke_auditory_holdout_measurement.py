"""Measured start gate and independent auditory baselines for S2-KE."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from mcm_field_organism._ppb1_reference import normalized_mean_l1_distance
from tools._s2jw_default_live_profile import S2JWDefaultLiveProfileV1
from tools._s2ke_auditory_holdout_fixtures import (
    CHECKPOINTS, FIXTURE_ROLES, FORMATION_SEQUENCE, GEOMETRY_BLOCKED,
    HOLDOUT_ROLES, S2KEFixtureStream, S2KEPCMMaterializer,
    S2KEPCMPlanV1, S2KEReducedFixtureV1, assert_training_role,
)


S2KE_PREFLIGHT_SCHEMA = "s2ke.auditory-start-gate.v1"
S2KE_BASELINE_SCHEMA = "s2ke.auditory-baseline.v1"
READY = "S2KF_AUDIO_GEOMETRY_MATERIALIZED"
AUDITORY_THRESHOLD = 0.02
UPDATE_RATE = 0.05


class S2KEMeasurementError(ValueError):
    pass


def _digest(value: object) -> str:
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _auditory(fixture: S2KEReducedFixtureV1) -> tuple[float, ...]:
    if type(fixture) is not S2KEReducedFixtureV1:
        raise S2KEMeasurementError("exact reduced fixture required")
    values = tuple(fixture.pair.auditory.timed_frame.frame.values)
    if len(values) != 48:
        raise S2KEMeasurementError("auditory dimension differs")
    return values


def _distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return normalized_mean_l1_distance(left, right)


def materialize_start_gate_with_plan(profile: S2JWDefaultLiveProfileV1) -> tuple[dict[str, object], S2KEPCMPlanV1]:
    if type(profile) is not S2JWDefaultLiveProfileV1:
        raise S2KEMeasurementError("exact default-live profile required")
    materializer = S2KEPCMMaterializer()
    plan = materializer.derive_once()
    plan_payload = {**plan.payload_without_digest(), "plan_digest": plan.plan_digest}
    if not plan.samples_valid:
        payload = {
            "schema": S2KE_PREFLIGHT_SCHEMA,
            "status": GEOMETRY_BLOCKED,
            "pcm_plan": plan_payload,
            "basis_evaluations": 2,
            "coefficient_sets": 1,
            "memory_calls": 0,
            "reason": "PCM_SAMPLE_BOUND_EXCEEDED",
        }
        return {**payload, "preflight_digest": _digest(payload)}, plan

    stream = S2KEFixtureStream(profile, plan, "s2ke-preflight-clock")
    fixtures = tuple(stream.materialize(role, index) for index, role in enumerate(FIXTURE_ROLES))
    by_role = {item.role: item for item in fixtures}
    if tuple(by_role) != FIXTURE_ROLES:
        raise S2KEMeasurementError("fixture inventory differs")
    plus, minus, holdout, negative = (_auditory(by_role[role]) for role in ("T_PLUS", "T_MINUS", "H_AUDIO", "N_AUDIO"))
    prototype = plus
    updates = []
    for update_index in range(1, 7):
        pre_distance = _distance(prototype, minus)
        prototype = tuple((1.0 - UPDATE_RATE) * previous + UPDATE_RATE * current for previous, current in zip(prototype, minus, strict=True))
        updates.append({"update_index": update_index, "pre_distance": pre_distance, "prototype_digest": _digest(list(prototype))})
    distances = {
        "holdout_plus": _distance(holdout, plus),
        "holdout_minus": _distance(holdout, minus),
        "training_pair": _distance(plus, minus),
        "holdout_adaptive": _distance(holdout, prototype),
        "negative_plus": _distance(negative, plus),
        "negative_minus": _distance(negative, minus),
        "negative_adaptive": _distance(negative, prototype),
    }
    distractor_distances = []
    for role in FIXTURE_ROLES[4:]:
        values = _auditory(by_role[role])
        distractor_distances.append({"role": role, "plus": _distance(values, plus), "minus": _distance(values, minus), "adaptive": _distance(values, prototype)})
    visual_digests = {role: by_role[role].visual_values_digest for role in ("T_PLUS", "T_MINUS", "H_AUDIO", "N_AUDIO")}
    valid = (
        0.02010 <= distances["holdout_plus"] <= 0.02120
        and 0.02010 <= distances["holdout_minus"] <= 0.02120
        and 0.00900 <= distances["training_pair"] <= 0.01020
        and distances["holdout_adaptive"] <= 0.01850
        and 0.02900 <= distances["negative_plus"] <= 0.03150
        and 0.02010 <= distances["negative_minus"] <= 0.02120
        and distances["negative_adaptive"] >= 0.02700
        and all(item["pre_distance"] <= AUDITORY_THRESHOLD for item in updates)
        and len(set(visual_digests.values())) == 1
        and all(min(item["plus"], item["minus"], item["adaptive"]) > AUDITORY_THRESHOLD for item in distractor_distances)
    )
    payload = {
        "schema": S2KE_PREFLIGHT_SCHEMA,
        "status": READY if valid else GEOMETRY_BLOCKED,
        "pcm_plan": plan_payload,
        "fixture_digests": {role: by_role[role].fixture_digest for role in FIXTURE_ROLES},
        "auditory_values_digests": {role: by_role[role].auditory_values_digest for role in FIXTURE_ROLES},
        "shared_visual_values_digest": next(iter(visual_digests.values())) if len(set(visual_digests.values())) == 1 else None,
        "distances": distances,
        "adaptive_updates": updates,
        "adaptive_prototype_digest": _digest(list(prototype)),
        "distractor_distances": distractor_distances,
        "basis_evaluations": 2,
        "coefficient_sets": 1,
        "memory_calls": 0,
        "reason": None if valid else "MEASURED_DISTANCE_GATE_FAILED",
    }
    return {**payload, "preflight_digest": _digest(payload)}, plan


def materialize_start_gate(profile: S2JWDefaultLiveProfileV1) -> dict[str, object]:
    return materialize_start_gate_with_plan(profile)[0]


def validate_start_gate(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise S2KEMeasurementError("start gate must be one object")
    payload = dict(value)
    stored = payload.pop("preflight_digest", None)
    if stored != _digest(payload) or payload.get("schema") != S2KE_PREFLIGHT_SCHEMA:
        raise S2KEMeasurementError("start gate digest differs")
    if payload.get("basis_evaluations") != 2 or payload.get("coefficient_sets") != 1 or payload.get("memory_calls") != 0:
        raise S2KEMeasurementError("one-pass materialization binding differs")
    status = payload.get("status")
    if status not in {READY, GEOMETRY_BLOCKED}:
        raise S2KEMeasurementError("start gate status differs")
    if status == READY:
        distances, updates = payload.get("distances"), payload.get("adaptive_updates")
        fixture_digests = payload.get("fixture_digests")
        if not isinstance(distances, dict) or not isinstance(updates, list) or len(updates) != 6:
            raise S2KEMeasurementError("measured geometry is incomplete")
        if not isinstance(fixture_digests, dict) or set(fixture_digests) != set(FIXTURE_ROLES):
            raise S2KEMeasurementError("fixture inventory differs")
    return value


@dataclass(frozen=True, slots=True)
class S2KEBaselineStateV1:
    formation_count: int
    replay: tuple[tuple[str, tuple[float, ...]], ...]
    frozen: tuple[float, ...] | None
    adaptive: tuple[float, ...] | None
    support: int
    state_digest: str

    def __post_init__(self) -> None:
        if (
            type(self.formation_count) is not int
            or not 0 <= self.formation_count <= len(FORMATION_SEQUENCE)
            or type(self.support) is not int
            or not 0 <= self.support <= 3
            or self.state_digest != _state_digest(
                self.formation_count, self.replay, self.frozen, self.adaptive, self.support
            )
        ):
            raise S2KEMeasurementError("baseline state binding differs")


def initial_baseline_state() -> S2KEBaselineStateV1:
    payload = {"schema": S2KE_BASELINE_SCHEMA, "formation_count": 0, "replay": [], "frozen": None, "adaptive": None, "support": 0}
    return S2KEBaselineStateV1(0, (), None, None, 0, _digest(payload))


def _state_digest(count: int, replay: tuple[tuple[str, tuple[float, ...]], ...], frozen: tuple[float, ...] | None, adaptive: tuple[float, ...] | None, support: int) -> str:
    return _digest({"schema": S2KE_BASELINE_SCHEMA, "formation_count": count, "replay": [[role, _digest(list(values))] for role, values in replay], "frozen": _digest(list(frozen)) if frozen else None, "adaptive": _digest(list(adaptive)) if adaptive else None, "support": support})


def advance_baselines(state: S2KEBaselineStateV1, fixture: S2KEReducedFixtureV1) -> S2KEBaselineStateV1:
    if type(state) is not S2KEBaselineStateV1 or type(fixture) is not S2KEReducedFixtureV1:
        raise S2KEMeasurementError("exact baseline state and fixture required")
    role = assert_training_role(fixture.role)
    index = state.formation_count + 1
    if index > 17 or FORMATION_SEQUENCE[index - 1] != role:
        raise S2KEMeasurementError("baseline training order differs")
    values = _auditory(fixture)
    replay = state.replay + ((role, values),)
    frozen, adaptive, support = state.frozen, state.adaptive, state.support
    if index == 2:
        frozen = adaptive = values
        support = 1
    elif 3 <= index <= 8:
        if adaptive is None:
            raise S2KEMeasurementError("adaptive prestate missing")
        adaptive = tuple((1.0 - UPDATE_RATE) * previous + UPDATE_RATE * current for previous, current in zip(adaptive, values, strict=True))
        support = min(3, support + 1)
    return S2KEBaselineStateV1(index, replay, frozen, adaptive, support, _state_digest(index, replay, frozen, adaptive, support))


def probe_baselines(state: S2KEBaselineStateV1, fixture: S2KEReducedFixtureV1) -> dict[str, object]:
    if type(state) is not S2KEBaselineStateV1 or type(fixture) is not S2KEReducedFixtureV1 or fixture.role not in HOLDOUT_ROLES:
        raise S2KEMeasurementError("baseline probe requires holdout")
    values = _auditory(fixture)
    frozen = None if state.frozen is None else {"distance": _distance(values, state.frozen), "match": _distance(values, state.frozen) <= AUDITORY_THRESHOLD}
    nearest = None
    if state.replay:
        distance, role = min((_distance(values, item), role) for role, item in state.replay)
        nearest = {"nearest_role": role, "distance": distance, "match": distance <= AUDITORY_THRESHOLD}
    adaptive = None if state.adaptive is None else {"support": state.support, "distance": _distance(values, state.adaptive), "match": state.support >= 3 and _distance(values, state.adaptive) <= AUDITORY_THRESHOLD}
    payload = {"schema": S2KE_BASELINE_SCHEMA, "prestate_digest": state.state_digest, "poststate_digest": state.state_digest, "fixture_digest": fixture.fixture_digest, "frozen": frozen, "nearest": nearest, "adaptive": adaptive}
    return {**payload, "finding_digest": _digest(payload)}
