"""Read-only measurements for S2-JZ receptor and memory evidence."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from mcm_field_organism._ppb1_reference import normalized_mean_l1_distance
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools._s2jz_perceptual_variation_fixtures import S2JZReducedFixtureV1


S2JZ_MEASUREMENT_SCHEMA = "s2jz.perceptual-variation-measurement.v1"


class S2JZMeasurementError(ValueError):
    """A read-only measurement is incomplete or not source-bound."""


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class S2JZReceptorDistanceV1:
    reference_fixture_digest: str
    candidate_fixture_digest: str
    candidate_role: str
    auditory_distance: float
    visual_distance: float
    measurement_digest: str
    schema: str = S2JZ_MEASUREMENT_SCHEMA

    def __post_init__(self) -> None:
        if (
            self.schema != S2JZ_MEASUREMENT_SCHEMA
            or not math.isfinite(self.auditory_distance)
            or not math.isfinite(self.visual_distance)
            or self.auditory_distance < 0.0
            or self.visual_distance < 0.0
            or self.measurement_digest != _digest(self.payload_without_digest())
        ):
            raise S2JZMeasurementError("receptor distance binding differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "reference_fixture_digest": self.reference_fixture_digest,
            "candidate_fixture_digest": self.candidate_fixture_digest,
            "candidate_role": self.candidate_role,
            "auditory_distance": self.auditory_distance,
            "visual_distance": self.visual_distance,
        }


def measure_receptor_distance(
    reference: S2JZReducedFixtureV1,
    candidate: S2JZReducedFixtureV1,
) -> S2JZReceptorDistanceV1:
    if type(reference) is not S2JZReducedFixtureV1 or type(candidate) is not S2JZReducedFixtureV1:
        raise S2JZMeasurementError("exact reduced fixtures required")
    auditory = normalized_mean_l1_distance(
        reference.pair.auditory.timed_frame.frame.values,
        candidate.pair.auditory.timed_frame.frame.values,
    )
    visual = normalized_mean_l1_distance(
        reference.pair.visual.timed_frame.frame.values,
        candidate.pair.visual.timed_frame.frame.values,
    )
    payload = {
        "schema": S2JZ_MEASUREMENT_SCHEMA,
        "reference_fixture_digest": reference.fixture_digest,
        "candidate_fixture_digest": candidate.fixture_digest,
        "candidate_role": candidate.role,
        "auditory_distance": auditory,
        "visual_distance": visual,
    }
    return S2JZReceptorDistanceV1(
        reference.fixture_digest,
        candidate.fixture_digest,
        candidate.role,
        auditory,
        visual,
        _digest(payload),
    )


def validate_variation_measurements(
    measurements: tuple[S2JZReceptorDistanceV1, ...],
) -> tuple[S2JZReceptorDistanceV1, ...]:
    by_role = {item.candidate_role: item for item in measurements}
    if len(measurements) != 6 or set(by_role) != {"R0", "E0", "V1", "A1", "C1", "Z1"}:
        raise S2JZMeasurementError("complete unique variation inventory required")
    r0, e0, v1, a1, c1, z1 = (by_role[key] for key in ("R0", "E0", "V1", "A1", "C1", "Z1"))
    close = lambda left, right: math.isclose(left, right, rel_tol=0.0, abs_tol=1e-15)
    valid = (
        close(r0.auditory_distance, 0.0)
        and close(r0.visual_distance, 0.0)
        and close(e0.auditory_distance, 0.0)
        and close(e0.visual_distance, 0.0)
        and close(v1.auditory_distance, 0.0)
        and close(v1.visual_distance, 2.0 / 255.0)
        and close(a1.visual_distance, 0.0)
        and 0.0 < a1.auditory_distance < 0.01
        and close(c1.auditory_distance, a1.auditory_distance)
        and close(c1.visual_distance, v1.visual_distance)
        and z1.auditory_distance > 0.02
        and z1.visual_distance > 0.2
    )
    if not valid:
        raise S2JZMeasurementError("materialized variation lies outside its frozen interval")
    return measurements


def state_slot_projection(state: coordinator.S2JVCompositeStateV1) -> dict[str, object]:
    if type(state) is not coordinator.S2JVCompositeStateV1:
        raise S2JZMeasurementError("exact composite state required")
    return {
        "generation": state.generation,
        "state_digest": state.state_digest,
        "b4": [
            [entry.slot_id, entry.formation_index]
            for entry in state.b4_state.entries
            if entry.occupied
        ],
        "fast": [
            [slot.slot_id, slot.support_count, slot.last_selected_step, slot.digest()]
            for slot in state.tspm_state.fast_state.slots
            if slot.occupied
        ],
        "auditory_slow": [
            [slot.slot_id, slot.support_count, slot.last_selected_step, _digest(slot.canonical_payload())]
            for slot in state.tspm_state.auditory_ppb1_state.slots
            if slot.occupied
        ],
        "visual_slow": [
            [slot.slot_id, slot.support_count, slot.last_selected_step, _digest(slot.canonical_payload())]
            for slot in state.tspm_state.visual_ppb1_state.slots
            if slot.occupied
        ],
    }


def measure_transition(
    prestate: coordinator.S2JVCompositeStateV1,
    result: coordinator.S2JVFormationResultV1,
) -> dict[str, object]:
    if type(prestate) is not coordinator.S2JVCompositeStateV1 or type(result) is not coordinator.S2JVFormationResultV1:
        raise S2JZMeasurementError("exact formation transition required")
    poststate = result.poststate
    if poststate.generation != prestate.generation + 1 or poststate.parent_state_digest != prestate.state_digest:
        raise S2JZMeasurementError("formation transition relation differs")
    before = state_slot_projection(prestate)
    after = state_slot_projection(poststate)
    return {
        "prestate_digest": prestate.state_digest,
        "poststate_digest": poststate.state_digest,
        "b4_event": result.receipt.b4_event,
        "b4_slot_id": result.receipt.b4_slot_id,
        "fast_before": before["fast"],
        "fast_after": after["fast"],
        "auditory_slow_before": before["auditory_slow"],
        "auditory_slow_after": after["auditory_slow"],
        "visual_slow_before": before["visual_slow"],
        "visual_slow_after": after["visual_slow"],
        "measurement_digest": _digest({"before": before, "after": after, "receipt": result.receipt.receipt_digest}),
    }


def direct_l1_prototype_baseline(
    config: coordinator.S2JVCoordinatorConfigV1,
    state: coordinator.S2JVCompositeStateV1,
    fixture: S2JZReducedFixtureV1,
) -> dict[str, object]:
    if type(fixture) is not S2JZReducedFixtureV1:
        raise S2JZMeasurementError("exact fixture required")
    auditory = fixture.pair.auditory.timed_frame.frame.values
    visual = fixture.pair.visual.timed_frame.frame.values
    fast = []
    for slot in state.tspm_state.fast_state.slots:
        if slot.occupied:
            fast.append({
                "slot_id": slot.slot_id,
                "auditory_distance": normalized_mean_l1_distance(auditory, slot.auditory_values),
                "visual_distance": normalized_mean_l1_distance(visual, slot.visual_values),
            })
    auditory_slow = []
    for slot in state.tspm_state.auditory_ppb1_state.slots:
        if slot.occupied:
            auditory_slow.append({
                "slot_id": slot.slot_id,
                "support": slot.support_count,
                "distance": normalized_mean_l1_distance(auditory, slot.prototype_values),
            })
    visual_slow = []
    for slot in state.tspm_state.visual_ppb1_state.slots:
        if slot.occupied:
            visual_slow.append({
                "slot_id": slot.slot_id,
                "support": slot.support_count,
                "distance": normalized_mean_l1_distance(visual, slot.prototype_values),
            })
    payload = {
        "state_digest": state.state_digest,
        "fixture_digest": fixture.fixture_digest,
        "fast_thresholds": [
            config.tspm_config.fast_config.auditory_match_threshold,
            config.tspm_config.fast_config.visual_match_threshold,
        ],
        "slow_thresholds": [
            config.profile.profile.auditory_config.match_threshold,
            config.profile.profile.visual_config.match_threshold,
        ],
        "fast": fast,
        "auditory_slow": auditory_slow,
        "visual_slow": visual_slow,
    }
    return {**payload, "baseline_digest": _digest(payload)}

