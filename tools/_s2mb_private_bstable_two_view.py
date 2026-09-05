"""Private projection of real visual B_STABLE slots for S2-MB."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from tools import _s2ly_private_two_view_projection as projection
from tools import _s2ma_private_arecent_two_view_integration as integration
from tools import _s2jw_profiled_memory_coordinator as coordinator


SCHEMA = "s2mb.private-bstable-two-view.v1"


class S2MBBStableError(ValueError):
    """A B_STABLE candidate or two-view binding is invalid."""


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MBBStableError(message)


def _valid_digest(value: object) -> bool:
    return type(value) is str and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


@dataclass(frozen=True, slots=True)
class BStableCalibrationBindingV1:
    slot_id: str
    calibration_id: str
    calibration_radius: float
    calibration_digest: str
    expected_prototype_values_digest: str

    def __post_init__(self) -> None:
        _require(type(self.slot_id) is str and self.slot_id, "slot id differs")
        _require(
            type(self.calibration_id) is str and self.calibration_id,
            "calibration id differs",
        )
        _require(
            type(self.calibration_radius) is float
            and math.isfinite(self.calibration_radius)
            and self.calibration_radius >= 0.0,
            "calibration radius differs",
        )
        _require(
            _valid_digest(self.calibration_digest)
            and _valid_digest(self.expected_prototype_values_digest),
            "calibration digest differs",
        )


@dataclass(frozen=True, slots=True)
class BStableVisualCandidateV1:
    slot_id: str
    support: int
    slot_digest: str
    prototype_values_digest: str
    form_values: tuple[float, ...]
    form_values_digest: str
    calibration_id: str
    calibration_radius: float
    calibration_digest: str
    candidate_digest: str

    def __post_init__(self) -> None:
        _require(type(self.slot_id) is str and self.slot_id, "candidate slot differs")
        _require(type(self.support) is int and self.support >= 1, "candidate support differs")
        _require(
            _valid_digest(self.slot_digest)
            and _valid_digest(self.prototype_values_digest)
            and _valid_digest(self.form_values_digest)
            and _valid_digest(self.calibration_digest),
            "candidate digest binding differs",
        )
        _require(
            type(self.form_values) is tuple
            and len(self.form_values) == 144
            and all(type(value) is float and math.isfinite(value) for value in self.form_values)
            and self.form_values_digest == _digest(list(self.form_values)),
            "candidate form differs",
        )
        _require(
            type(self.calibration_id) is str
            and self.calibration_id
            and type(self.calibration_radius) is float
            and math.isfinite(self.calibration_radius)
            and self.calibration_radius >= 0.0
            and self.candidate_digest == _digest(self.payload_without_digest()),
            "candidate calibration differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "slot_id": self.slot_id,
            "support": self.support,
            "slot_digest": self.slot_digest,
            "prototype_values_digest": self.prototype_values_digest,
            "form_values": list(self.form_values),
            "form_values_digest": self.form_values_digest,
            "calibration_id": self.calibration_id,
            "calibration_radius": self.calibration_radius,
            "calibration_digest": self.calibration_digest,
        }


@dataclass(frozen=True, slots=True)
class BStableVisualCandidateSetV1:
    config_digest: str
    memory_state_digest: str
    union_mask_digest: str
    union_positions: tuple[int, ...]
    candidates: tuple[BStableVisualCandidateV1, ...]
    prestate_digest: str
    poststate_digest: str
    candidate_set_digest: str

    def __post_init__(self) -> None:
        _require(
            _valid_digest(self.config_digest)
            and _valid_digest(self.memory_state_digest)
            and _valid_digest(self.union_mask_digest)
            and _valid_digest(self.prestate_digest)
            and _valid_digest(self.poststate_digest),
            "candidate-set digest binding differs",
        )
        _require(
            type(self.union_positions) is tuple
            and len(self.union_positions) == 192
            and len(set(self.union_positions)) == 192
            and type(self.candidates) is tuple
            and bool(self.candidates)
            and all(type(item) is BStableVisualCandidateV1 for item in self.candidates)
            and len({item.slot_id for item in self.candidates}) == len(self.candidates),
            "candidate-set inventory differs",
        )
        _require(
            self.memory_state_digest == self.prestate_digest == self.poststate_digest
            and self.candidate_set_digest == _digest(self.payload_without_digest()),
            "candidate-set read-only relation differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "config_digest": self.config_digest,
            "memory_state_digest": self.memory_state_digest,
            "union_mask_digest": self.union_mask_digest,
            "union_positions": list(self.union_positions),
            "candidate_digests": [item.candidate_digest for item in self.candidates],
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
        }

    def model_envelopes(self) -> dict[str, tuple[tuple[float, ...], float]]:
        return {
            item.slot_id: (item.form_values, item.calibration_radius)
            for item in self.candidates
        }


def bind_visual_bstable_candidates(
    *,
    config: coordinator.S2JVCoordinatorConfigV1,
    state: coordinator.S2JVCompositeStateV1,
    bindings: tuple[BStableCalibrationBindingV1, ...],
    union_mask_digest: str,
    union_positions: tuple[int, ...],
) -> BStableVisualCandidateSetV1:
    config = coordinator._validate_config(config)
    state = coordinator._validate_state(config, state)
    _require(
        type(bindings) is tuple
        and bindings
        and all(type(item) is BStableCalibrationBindingV1 for item in bindings),
        "calibration bindings differ",
    )
    _require(
        _valid_digest(union_mask_digest)
        and type(union_positions) is tuple
        and len(union_positions) == 192
        and len(set(union_positions)) == 192,
        "union binding differs",
    )
    before = state.state_digest
    slots = tuple(
        slot
        for slot in state.tspm_state.visual_ppb1_state.slots
        if slot.occupied
    )
    binding_by_slot = {item.slot_id: item for item in bindings}
    _require(
        len(binding_by_slot) == len(bindings)
        and {slot.slot_id for slot in slots} == set(binding_by_slot),
        "stable slot inventory differs",
    )
    candidates = []
    stable_after = config.profile.profile.visual_config.stable_after
    for slot in sorted(slots, key=lambda item: item.slot_id):
        binding = binding_by_slot[slot.slot_id]
        _require(
            slot.support_count is not None
            and slot.support_count >= stable_after
            and len(slot.prototype_values) == config.visual_dimension,
            "visual slot is not public B_STABLE evidence",
        )
        prototype_values = tuple(float(value) for value in slot.prototype_values)
        prototype_digest = _digest(list(prototype_values))
        _require(
            prototype_digest == binding.expected_prototype_values_digest,
            "prototype transition binding differs",
        )
        view = projection.ObservedVisualViewV1(
            mask_id="UNION_192",
            mask_digest=union_mask_digest,
            source_values_digest=prototype_digest,
            observed_positions=union_positions,
            observed_values=tuple(prototype_values[index] for index in union_positions),
            observed_values_digest=_digest(
                [prototype_values[index] for index in union_positions]
            ),
        )
        form = projection.project_mask_conditioned_form(view)
        slot_digest = _digest(slot.canonical_payload())
        payload = {
            "schema": SCHEMA,
            "slot_id": slot.slot_id,
            "support": slot.support_count,
            "slot_digest": slot_digest,
            "prototype_values_digest": prototype_digest,
            "form_values": list(form.values),
            "form_values_digest": _digest(list(form.values)),
            "calibration_id": binding.calibration_id,
            "calibration_radius": binding.calibration_radius,
            "calibration_digest": binding.calibration_digest,
        }
        candidates.append(
            BStableVisualCandidateV1(
                slot.slot_id,
                slot.support_count,
                slot_digest,
                prototype_digest,
                form.values,
                payload["form_values_digest"],
                binding.calibration_id,
                binding.calibration_radius,
                binding.calibration_digest,
                _digest(payload),
            )
        )
    after = state.state_digest
    _require(before == after, "candidate projection changed memory")
    payload = {
        "schema": SCHEMA,
        "config_digest": config.config_digest,
        "memory_state_digest": before,
        "union_mask_digest": union_mask_digest,
        "union_positions": list(union_positions),
        "candidate_digests": [item.candidate_digest for item in candidates],
        "prestate_digest": before,
        "poststate_digest": after,
    }
    return BStableVisualCandidateSetV1(
        config.config_digest,
        before,
        union_mask_digest,
        union_positions,
        tuple(candidates),
        before,
        after,
        _digest(payload),
    )


def direct_bstable_two_view_baseline(
    *,
    first: integration.ARecentObservedLookV1,
    second: integration.ARecentObservedLookV1,
    candidates: BStableVisualCandidateSetV1,
    geometry_digest: str,
    view_a_mask_digest: str,
    view_b_mask_digest: str,
) -> dict[str, object]:
    """Independent direct comparison; it does not call S2-MA or S2-LZ decisions."""

    _require(
        type(first) is integration.ARecentObservedLookV1
        and type(second) is integration.ARecentObservedLookV1
        and type(candidates) is BStableVisualCandidateSetV1,
        "baseline inputs differ",
    )
    same_source = first.source_id == second.source_id
    same_payload = (
        first.payload_sha256 == second.payload_sha256
        and first.source_values_digest == second.source_values_digest
    )
    compatible = (
        first.geometry_digest == second.geometry_digest == geometry_digest
        and first.mask_id == "VIEW_A_96"
        and second.mask_id == "VIEW_B_96"
        and first.mask_digest == view_a_mask_digest
        and second.mask_digest == view_b_mask_digest
        and first.case_plan_digest == second.case_plan_digest
        and same_source
        and same_payload
        and second.tick - first.tick == 1
        and first.observed_positions + second.observed_positions
        == candidates.union_positions
    )
    if not compatible:
        compatibility_payload = {
            "case_plan_digest": first.case_plan_digest,
            "view_a_observation_digest": first.source_observation_digest,
            "view_b_observation_digest": second.source_observation_digest,
            "same_source_id": same_source,
            "same_payload_digest": same_payload,
            "tick_gap": second.tick - first.tick,
            "maximum_tick_gap": 1,
            "compatible": False,
        }
        parent_digest = _digest(compatibility_payload)
        payload = {
            "status": "ABSTAINED",
            "selected_model_id": None,
            "reason": "PAIR_INCOMPATIBLE_NO_UNION",
            "parent_digest": parent_digest,
        }
        return {**payload, "decision_digest": _digest(payload)}

    union_values = first.observed_values + second.observed_values
    union_view = projection.ObservedVisualViewV1(
        mask_id="UNION_192",
        mask_digest=candidates.union_mask_digest,
        source_values_digest=first.source_values_digest,
        observed_positions=candidates.union_positions,
        observed_values=union_values,
        observed_values_digest=_digest(list(union_values)),
    )
    form = projection.project_mask_conditioned_form(union_view)
    rows = []
    eligible = []
    for candidate in candidates.candidates:
        distance = math.fsum(
            abs(left - right)
            for left, right in zip(form.values, candidate.form_values, strict=True)
        ) / len(form.values)
        accepted = distance <= candidate.calibration_radius
        rows.append(
            {
                "model_id": candidate.slot_id,
                "mean_l1": distance,
                "calibration_radius": candidate.calibration_radius,
                "within_envelope": accepted,
            }
        )
        if accepted:
            eligible.append(candidate.slot_id)
    if len(eligible) == 1:
        status, selected, reason = (
            "ADMITTED",
            eligible[0],
            "EXACTLY_ONE_MODEL_WITHIN_ENVELOPE",
        )
    elif not eligible:
        status, selected, reason = "ABSTAINED", None, "NO_MODEL_WITHIN_ENVELOPE"
    else:
        status, selected, reason = (
            "ABSTAINED",
            None,
            "MULTIPLE_MODELS_WITHIN_ENVELOPE",
        )
    payload = {
        "status": status,
        "selected_model_id": selected,
        "reason": reason,
        "eligible_model_ids": eligible,
        "distances": rows,
    }
    return {**payload, "decision_digest": _digest(payload)}


__all__: tuple[str, ...] = ()
