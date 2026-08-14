"""Static W7-AY contract for CAP field lifecycle profiles."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class W7AYCAPFieldProfileContractError(ValueError):
    """Raised when the CAP field profile preregistration changes."""


_CONTRACT_ID = "w7ay.cap-field-profile-contract.v1"
_W7AG_HANDOFF_DIGEST = (
    "898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8"
)
_W7AK_COMPOSITION_DIGEST = (
    "ca047546d37a0ebd5728ee6adcf27d083c2a7fce3aad82f882284f08629f1fc3"
)
_W7AT_EVALUATION_DIGEST = (
    "b6ff73ac1b85344a5aa925506dba599bb9b3956abeb4eca0e6b0f9e63087b99c"
)
_W7AT_EFFECT_FLOOR = 1.8915768951188738e-07
_PATHS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_CONTRASTS = (
    ("ab_old_a_under_b", "ab", "ub"),
    ("ab_old_a_after_gap", "ag", "ug"),
    ("ab_new_b_after_a", "ab", "ag"),
    ("ab_new_b_after_neutral", "ub", "ug"),
    ("ba_old_b_under_a", "ba", "ua"),
    ("ba_old_b_after_gap", "bg", "ug"),
    ("ba_new_a_after_b", "ba", "bg"),
    ("ba_new_a_after_neutral", "ua", "ug"),
)
_PROFILE_MAPPING = (
    (
        "ab",
        "ab_old_a_under_b",
        "ab_old_a_after_gap",
        "ab_new_b_after_a",
        "ab_new_b_after_neutral",
    ),
    (
        "ba",
        "ba_old_b_under_a",
        "ba_old_b_after_gap",
        "ba_new_a_after_b",
        "ba_new_a_after_neutral",
    ),
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _payload() -> dict[str, object]:
    return {
        "contract_id": _CONTRACT_ID,
        "required_w7ag_handoff_digest": _W7AG_HANDOFF_DIGEST,
        "required_w7ak_composition_digest": _W7AK_COMPOSITION_DIGEST,
        "required_w7at_evaluation_digest": _W7AT_EVALUATION_DIGEST,
        "w7at_effect_floor": _W7AT_EFFECT_FLOOR,
        "model_id": "cap",
        "measurement_surface": "field",
        "source_paths": _PATHS,
        "checkpoint_count": 5,
        "contrast_inventory": _CONTRASTS,
        "profile_mapping": _PROFILE_MAPPING,
        "effect_metric": "max-of-samplewise-S-linf-and-H-linf",
        "alignment_rule": "ticks-and-s-h-geometry-must-match-exactly",
        "denominator_rule": "initial-old-effect-strictly-above-w7at-floor",
        "unresolved_policy": "no-epsilon-rescue",
        "normalization_rule": "cap-profile-by-own-initial-old-effect",
        "neutral_contrast_role": "required-audit-control-not-profile-coordinate",
        "w7ak_role": "cap-p0-provenance-and-alignment-control-only",
        "w7ak_values_used_as_path_effects": False,
        "accept_result_values": False,
        "profile_composition_allowed": False,
        "observer_explanation_allowed": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7AYCAPFieldProfileContract:
    """Immutable mapping from existing CAP trajectories to later profiles."""

    contract_id: str
    required_w7ag_handoff_digest: str
    required_w7ak_composition_digest: str
    required_w7at_evaluation_digest: str
    w7at_effect_floor: float
    model_id: str
    measurement_surface: str
    source_paths: tuple[str, ...]
    checkpoint_count: int
    contrast_inventory: tuple[tuple[str, str, str], ...]
    profile_mapping: tuple[tuple[str, ...], ...]
    effect_metric: str
    alignment_rule: str
    denominator_rule: str
    unresolved_policy: str
    normalization_rule: str
    neutral_contrast_role: str
    w7ak_role: str
    w7ak_values_used_as_path_effects: bool
    accept_result_values: bool
    profile_composition_allowed: bool
    observer_explanation_allowed: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != _CONTRACT_ID
            or self.required_w7ag_handoff_digest != _W7AG_HANDOFF_DIGEST
            or self.required_w7ak_composition_digest
            != _W7AK_COMPOSITION_DIGEST
            or self.required_w7at_evaluation_digest
            != _W7AT_EVALUATION_DIGEST
            or self.w7at_effect_floor != _W7AT_EFFECT_FLOOR
            or self.model_id != "cap"
            or self.measurement_surface != "field"
            or tuple(self.source_paths) != _PATHS
            or self.checkpoint_count != 5
            or tuple(tuple(item) for item in self.contrast_inventory)
            != _CONTRASTS
            or tuple(tuple(item) for item in self.profile_mapping)
            != _PROFILE_MAPPING
            or self.effect_metric
            != "max-of-samplewise-S-linf-and-H-linf"
            or self.alignment_rule
            != "ticks-and-s-h-geometry-must-match-exactly"
            or self.denominator_rule
            != "initial-old-effect-strictly-above-w7at-floor"
            or self.unresolved_policy != "no-epsilon-rescue"
            or self.normalization_rule
            != "cap-profile-by-own-initial-old-effect"
            or self.neutral_contrast_role
            != "required-audit-control-not-profile-coordinate"
            or self.w7ak_role
            != "cap-p0-provenance-and-alignment-control-only"
            or self.w7ak_values_used_as_path_effects is not False
            or self.accept_result_values is not False
            or self.profile_composition_allowed is not False
            or self.observer_explanation_allowed is not False
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
            or self.contract_digest != _digest(_payload())
        ):
            raise W7AYCAPFieldProfileContractError(
                "W7-AY CAP field profile contract differs"
            )


def build_w7ay_cap_field_profile_contract() -> W7AYCAPFieldProfileContract:
    """Build the CAP profile preregistration without accepting trajectories."""

    payload = _payload()
    return W7AYCAPFieldProfileContract(
        _CONTRACT_ID,
        _W7AG_HANDOFF_DIGEST,
        _W7AK_COMPOSITION_DIGEST,
        _W7AT_EVALUATION_DIGEST,
        _W7AT_EFFECT_FLOOR,
        "cap",
        "field",
        _PATHS,
        5,
        _CONTRASTS,
        _PROFILE_MAPPING,
        "max-of-samplewise-S-linf-and-H-linf",
        "ticks-and-s-h-geometry-must-match-exactly",
        "initial-old-effect-strictly-above-w7at-floor",
        "no-epsilon-rescue",
        "cap-profile-by-own-initial-old-effect",
        "required-audit-control-not-profile-coordinate",
        "cap-p0-provenance-and-alignment-control-only",
        False,
        False,
        False,
        False,
        False,
        False,
        _digest(payload),
    )
