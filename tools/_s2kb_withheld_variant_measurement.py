"""Measurements and independent baselines for the private S2-KB experiment."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from mcm_field_organism._ppb1_reference import normalized_mean_l1_distance
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools._s2kb_withheld_variant_fixtures import (
    FIXTURE_ROLES,
    FORMATION_SEQUENCE,
    HOLDOUT_ROLES,
    S2KBReducedFixtureV1,
    assert_training_role,
)


S2KB_PREFLIGHT_SCHEMA = "s2kb.withheld-variant-preflight.v1"
S2KB_BASELINE_SCHEMA = "s2kb.withheld-variant-baseline.v1"
AUDITORY_THRESHOLD = 0.02
VISUAL_THRESHOLD = 0.01
UPDATE_RATE = 0.05
STABLE_AFTER = 3


class S2KBMeasurementError(ValueError):
    """Measured evidence or one independent baseline is invalid."""


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _values(fixture: S2KBReducedFixtureV1) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if type(fixture) is not S2KBReducedFixtureV1:
        raise S2KBMeasurementError("exact reduced fixture required")
    return (
        tuple(fixture.pair.auditory.timed_frame.frame.values),
        tuple(fixture.pair.visual.timed_frame.frame.values),
    )


def _distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return normalized_mean_l1_distance(left, right)


def _pair_distance(left: S2KBReducedFixtureV1, right: S2KBReducedFixtureV1) -> tuple[float, float]:
    left_a, left_v = _values(left)
    right_a, right_v = _values(right)
    return _distance(left_a, right_a), _distance(left_v, right_v)


def materialize_preflight(fixtures: tuple[S2KBReducedFixtureV1, ...]) -> dict[str, object]:
    if len(fixtures) != len(FIXTURE_ROLES):
        raise S2KBMeasurementError("complete fixture inventory required")
    by_role = {fixture.role: fixture for fixture in fixtures}
    if len(by_role) != len(fixtures) or tuple(by_role) != FIXTURE_ROLES:
        raise S2KBMeasurementError("fixture roles or order differ")
    if any(len(_values(item)[0]) != 48 or len(_values(item)[1]) != 288 for item in fixtures):
        raise S2KBMeasurementError("default-live dimensions differ")

    expected_visual = {
        "T_PLUS": (132, 130),
        "T_MINUS": (132, 126),
        "H1": (128, 128),
        "N0": (0, 0),
    }
    for role, codes in expected_visual.items():
        visual = _values(by_role[role])[1]
        expected = (codes[0] / 255.0,) * 144 + (codes[1] / 255.0,) * 144
        if visual != expected:
            raise S2KBMeasurementError("actual visual receptor values differ")

    pairwise = []
    for left_index, left in enumerate(fixtures):
        for right in fixtures[left_index + 1 :]:
            auditory, visual = _pair_distance(left, right)
            pairwise.append({
                "left_role": left.role,
                "right_role": right.role,
                "auditory_distance": auditory,
                "visual_distance": visual,
            })

    plus_a, plus_v = _values(by_role["T_PLUS"])
    minus_a, minus_v = _values(by_role["T_MINUS"])
    holdout_a, holdout_v = _values(by_role["H1"])
    negative_a, negative_v = _values(by_role["N0"])
    adaptive_a, adaptive_v = plus_a, plus_v
    update_distances = []
    for _ in range(6):
        update_distances.append({
            "auditory": _distance(adaptive_a, minus_a),
            "visual": _distance(adaptive_v, minus_v),
        })
        adaptive_a = tuple((1.0 - UPDATE_RATE) * old + UPDATE_RATE * new for old, new in zip(adaptive_a, minus_a, strict=True))
        adaptive_v = tuple((1.0 - UPDATE_RATE) * old + UPDATE_RATE * new for old, new in zip(adaptive_v, minus_v, strict=True))

    payload = {
        "schema": S2KB_PREFLIGHT_SCHEMA,
        "fixture_digests": {role: by_role[role].fixture_digest for role in FIXTURE_ROLES},
        "value_digests": {
            role: [by_role[role].auditory_values_digest, by_role[role].visual_values_digest]
            for role in FIXTURE_ROLES
        },
        "pairwise_distances": pairwise,
        "holdout_static_distances": {
            "auditory": _distance(holdout_a, plus_a),
            "visual": _distance(holdout_v, plus_v),
        },
        "holdout_nearest_training_distances": {
            "auditory": min(_distance(holdout_a, item) for item in (plus_a, minus_a)),
            "visual": min(_distance(holdout_v, item) for item in (plus_v, minus_v)),
        },
        "holdout_adaptive_distances": {
            "auditory": _distance(holdout_a, adaptive_a),
            "visual": _distance(holdout_v, adaptive_v),
        },
        "negative_adaptive_distances": {
            "auditory": _distance(negative_a, adaptive_a),
            "visual": _distance(negative_v, adaptive_v),
        },
        "adaptive_update_distances": update_distances,
        "adaptive_prototype_digests": [_digest(list(adaptive_a)), _digest(list(adaptive_v))],
        "training_roles": list(FORMATION_SEQUENCE),
        "holdout_roles": list(HOLDOUT_ROLES),
        "preflight_visual_analyses": 13,
        "preflight_audio_hops": 130,
        "preflight_raw_bytes": 81_120_000,
    }
    result = {**payload, "preflight_digest": _digest(payload)}
    validate_preflight_payload(result)
    return result


def _lookup_pair(payload: dict[str, object], left: str, right: str) -> dict[str, object]:
    pairs = payload.get("pairwise_distances")
    if not isinstance(pairs, list):
        raise S2KBMeasurementError("pairwise measurements missing")
    matches = [
        item for item in pairs
        if isinstance(item, dict) and {item.get("left_role"), item.get("right_role")} == {left, right}
    ]
    if len(matches) != 1:
        raise S2KBMeasurementError("pairwise measurement relation differs")
    return matches[0]


def validate_preflight_payload(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise S2KBMeasurementError("preflight must be one object")
    payload = dict(value)
    stored = payload.pop("preflight_digest", None)
    if stored != _digest(payload) or payload.get("schema") != S2KB_PREFLIGHT_SCHEMA:
        raise S2KBMeasurementError("preflight digest or schema differs")
    fixture_digests = payload.get("fixture_digests")
    value_digests = payload.get("value_digests")
    if (
        not isinstance(fixture_digests, dict)
        or set(fixture_digests) != set(FIXTURE_ROLES)
        or not isinstance(value_digests, dict)
        or set(value_digests) != set(FIXTURE_ROLES)
    ):
        raise S2KBMeasurementError("fixture digest inventory differs")
    if payload.get("training_roles") != list(FORMATION_SEQUENCE) or payload.get("holdout_roles") != list(HOLDOUT_ROLES):
        raise S2KBMeasurementError("training and holdout roles differ")
    pairs = payload.get("pairwise_distances")
    if not isinstance(pairs, list) or len(pairs) != 78:
        raise S2KBMeasurementError("pairwise distance count differs")
    plus_holdout = _lookup_pair(payload, "T_PLUS", "H1")
    minus_holdout = _lookup_pair(payload, "T_MINUS", "H1")
    training_pair = _lookup_pair(payload, "T_PLUS", "T_MINUS")
    close = lambda left, right: math.isclose(left, right, rel_tol=0.0, abs_tol=1e-15)
    if not (
        close(plus_holdout["visual_distance"], 3.0 / 255.0)
        and close(minus_holdout["visual_distance"], 3.0 / 255.0)
        and close(training_pair["visual_distance"], 2.0 / 255.0)
        and plus_holdout["auditory_distance"] == 0.0
        and minus_holdout["auditory_distance"] == 0.0
    ):
        raise S2KBMeasurementError("central actual receptor distances differ")
    static = payload.get("holdout_static_distances")
    nearest = payload.get("holdout_nearest_training_distances")
    adaptive = payload.get("holdout_adaptive_distances")
    negative = payload.get("negative_adaptive_distances")
    updates = payload.get("adaptive_update_distances")
    if not all(isinstance(item, dict) for item in (static, nearest, adaptive, negative)) or not isinstance(updates, list):
        raise S2KBMeasurementError("prototype measurement form differs")
    if not (
        static["visual"] > VISUAL_THRESHOLD
        and nearest["visual"] > VISUAL_THRESHOLD
        and adaptive["visual"] <= VISUAL_THRESHOLD
        and adaptive["auditory"] <= AUDITORY_THRESHOLD
        and negative["visual"] > 0.2
        and len(updates) == 6
        and all(item["visual"] <= VISUAL_THRESHOLD and item["auditory"] <= AUDITORY_THRESHOLD for item in updates)
    ):
        raise S2KBMeasurementError("adaptive counterprediction is not materialized")
    seen_relations = set()
    for item in pairs:
        if not isinstance(item, dict):
            raise S2KBMeasurementError("pairwise measurement form differs")
        relation = frozenset((item.get("left_role"), item.get("right_role")))
        if len(relation) != 2 or relation in seen_relations:
            raise S2KBMeasurementError("pairwise measurement relation differs")
        seen_relations.add(relation)
        if str(item["left_role"]).startswith("D") or str(item["right_role"]).startswith("D"):
            if item["visual_distance"] <= 0.2 or item["auditory_distance"] <= AUDITORY_THRESHOLD:
                raise S2KBMeasurementError("distractor separation differs")
    if (payload.get("preflight_visual_analyses"), payload.get("preflight_audio_hops"), payload.get("preflight_raw_bytes")) != (13, 130, 81_120_000):
        raise S2KBMeasurementError("preflight resource binding differs")
    return value


@dataclass(frozen=True, slots=True)
class S2KBBaselineStateV1:
    formation_count: int
    replay: tuple[tuple[str, tuple[float, ...], tuple[float, ...]], ...]
    frozen_auditory: tuple[float, ...] | None
    frozen_visual: tuple[float, ...] | None
    adaptive_auditory: tuple[float, ...] | None
    adaptive_visual: tuple[float, ...] | None
    adaptive_support: int
    state_digest: str
    schema: str = S2KB_BASELINE_SCHEMA

    def __post_init__(self) -> None:
        if self.schema != S2KB_BASELINE_SCHEMA or self.state_digest != _digest(self.payload_without_digest()):
            raise S2KBMeasurementError("baseline state binding differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "formation_count": self.formation_count,
            "replay": [[role, _digest(list(auditory)), _digest(list(visual))] for role, auditory, visual in self.replay],
            "frozen_digests": None if self.frozen_auditory is None else [_digest(list(self.frozen_auditory)), _digest(list(self.frozen_visual))],
            "adaptive_digests": None if self.adaptive_auditory is None else [_digest(list(self.adaptive_auditory)), _digest(list(self.adaptive_visual))],
            "adaptive_support": self.adaptive_support,
        }


def initial_baseline_state() -> S2KBBaselineStateV1:
    payload = {
        "schema": S2KB_BASELINE_SCHEMA,
        "formation_count": 0,
        "replay": [],
        "frozen_digests": None,
        "adaptive_digests": None,
        "adaptive_support": 0,
    }
    return S2KBBaselineStateV1(0, (), None, None, None, None, 0, _digest(payload))


def advance_baselines(state: S2KBBaselineStateV1, fixture: S2KBReducedFixtureV1) -> S2KBBaselineStateV1:
    if type(state) is not S2KBBaselineStateV1:
        raise S2KBMeasurementError("exact baseline state required")
    role = assert_training_role(fixture.role)
    index = state.formation_count + 1
    if index > len(FORMATION_SEQUENCE) or FORMATION_SEQUENCE[index - 1] != role:
        raise S2KBMeasurementError("baseline training sequence differs")
    auditory, visual = _values(fixture)
    replay = state.replay + ((role, auditory, visual),)
    frozen_a, frozen_v = state.frozen_auditory, state.frozen_visual
    adaptive_a, adaptive_v = state.adaptive_auditory, state.adaptive_visual
    support = state.adaptive_support
    if index == 2:
        frozen_a, frozen_v = auditory, visual
        adaptive_a, adaptive_v = auditory, visual
        support = 1
    elif 3 <= index <= 8:
        if adaptive_a is None or adaptive_v is None:
            raise S2KBMeasurementError("adaptive baseline prestate missing")
        adaptive_a = tuple((1.0 - UPDATE_RATE) * old + UPDATE_RATE * new for old, new in zip(adaptive_a, auditory, strict=True))
        adaptive_v = tuple((1.0 - UPDATE_RATE) * old + UPDATE_RATE * new for old, new in zip(adaptive_v, visual, strict=True))
        support = min(STABLE_AFTER, support + 1)
    payload = {
        "schema": S2KB_BASELINE_SCHEMA,
        "formation_count": index,
        "replay": [[item_role, _digest(list(item_a)), _digest(list(item_v))] for item_role, item_a, item_v in replay],
        "frozen_digests": None if frozen_a is None else [_digest(list(frozen_a)), _digest(list(frozen_v))],
        "adaptive_digests": None if adaptive_a is None else [_digest(list(adaptive_a)), _digest(list(adaptive_v))],
        "adaptive_support": support,
    }
    return S2KBBaselineStateV1(index, replay, frozen_a, frozen_v, adaptive_a, adaptive_v, support, _digest(payload))


def _match(auditory_distance: float, visual_distance: float) -> bool:
    return auditory_distance <= AUDITORY_THRESHOLD and visual_distance <= VISUAL_THRESHOLD


def probe_baselines(state: S2KBBaselineStateV1, fixture: S2KBReducedFixtureV1) -> dict[str, object]:
    if type(state) is not S2KBBaselineStateV1 or fixture.role not in HOLDOUT_ROLES:
        raise S2KBMeasurementError("baseline probe requires one exact holdout")
    auditory, visual = _values(fixture)

    frozen = None
    if state.frozen_auditory is not None and state.frozen_visual is not None:
        frozen_a = _distance(auditory, state.frozen_auditory)
        frozen_v = _distance(visual, state.frozen_visual)
        frozen = {"auditory_distance": frozen_a, "visual_distance": frozen_v, "match": _match(frozen_a, frozen_v)}

    replay = None
    if state.replay:
        candidates = []
        for role, item_a, item_v in state.replay:
            distance_a, distance_v = _distance(auditory, item_a), _distance(visual, item_v)
            candidates.append((max(distance_a, distance_v), distance_a + distance_v, role, distance_a, distance_v))
        _, _, role, replay_a, replay_v = min(candidates)
        replay = {"nearest_role": role, "auditory_distance": replay_a, "visual_distance": replay_v, "match": _match(replay_a, replay_v)}

    adaptive = None
    if state.adaptive_auditory is not None and state.adaptive_visual is not None:
        adaptive_a = _distance(auditory, state.adaptive_auditory)
        adaptive_v = _distance(visual, state.adaptive_visual)
        adaptive = {
            "support": state.adaptive_support,
            "stable": state.adaptive_support >= STABLE_AFTER,
            "auditory_distance": adaptive_a,
            "visual_distance": adaptive_v,
            "match": state.adaptive_support >= STABLE_AFTER and _match(adaptive_a, adaptive_v),
        }
    payload = {
        "schema": S2KB_BASELINE_SCHEMA,
        "baseline_prestate_digest": state.state_digest,
        "baseline_poststate_digest": state.state_digest,
        "probe_fixture_digest": fixture.fixture_digest,
        "frozen_first": frozen,
        "replay_nearest": replay,
        "adaptive_prototype": adaptive,
    }
    return {**payload, "baseline_finding_digest": _digest(payload)}


def state_slot_projection(state: coordinator.S2JVCompositeStateV1) -> dict[str, object]:
    if type(state) is not coordinator.S2JVCompositeStateV1:
        raise S2KBMeasurementError("exact composite state required")
    return {
        "generation": state.generation,
        "state_digest": state.state_digest,
        "b4": [[entry.slot_id, entry.formation_index] for entry in state.b4_state.entries if entry.occupied],
        "fast": [[slot.slot_id, slot.support_count, slot.last_selected_step, slot.digest()] for slot in state.tspm_state.fast_state.slots if slot.occupied],
        "auditory_slow": [[slot.slot_id, slot.support_count, slot.last_selected_step, _digest(slot.canonical_payload())] for slot in state.tspm_state.auditory_ppb1_state.slots if slot.occupied],
        "visual_slow": [[slot.slot_id, slot.support_count, slot.last_selected_step, _digest(slot.canonical_payload())] for slot in state.tspm_state.visual_ppb1_state.slots if slot.occupied],
    }
