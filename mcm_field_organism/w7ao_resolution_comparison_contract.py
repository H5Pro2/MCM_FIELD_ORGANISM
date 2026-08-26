"""Static W7-AO comparison contract without reading W7-AN values."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class W7AOResolutionComparisonContractError(ValueError):
    """Raised when the static W7-AO contract is changed inconsistently."""


_CONTRACT_ID = "w7ao.r1-r2-r4-resolution-comparison-contract.v1"
_W7AN_CONTAINER_DIGEST = (
    "4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5"
)
_RESOLUTIONS = (("r1", 1), ("r2", 2), ("r4", 4))
_COMPARISONS = (("r1-r2", "r1", "r2"), ("r2-r4", "r2", "r4"))
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_ROLES = tuple(
    (path_id, checkpoint)
    for path_id in _PATH_IDS
    for checkpoint in range(5)
)
_PRIMARY_METRICS = ("S_linf", "H_linf")
_DIAGNOSTIC_METRICS = ("SH_l2",)
_EFFECT_FLOOR_FACTOR = 10.0


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
        "w7an_container_digest": _W7AN_CONTAINER_DIGEST,
        "resolutions": _RESOLUTIONS,
        "comparisons": _COMPARISONS,
        "roles": _ROLES,
        "primary_metrics": _PRIMARY_METRICS,
        "diagnostic_metrics": _DIAGNOSTIC_METRICS,
        "epsilon_source": "maximum-r2-r4-primary-linf-distance",
        "effect_floor_factor": _EFFECT_FLOOR_FACTOR,
        "convergence_rule": "rolewise-r2-r4-strictly-smaller-than-r1-r2-or-both-zero",
        "repeat_baseline": "primary-repeat-exact-zero",
        "identity_baseline": "same-resolution-self-distance-exact-zero",
        "p0_reused_once": True,
        "evaluate_values": False,
        "field_function_decision_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7AOResolutionComparisonContract:
    """Immutable preregistration for a later raw S/H comparison."""

    contract_id: str
    w7an_container_digest: str
    resolutions: tuple[tuple[str, int], ...]
    comparisons: tuple[tuple[str, str, str], ...]
    roles: tuple[tuple[str, int], ...]
    primary_metrics: tuple[str, ...]
    diagnostic_metrics: tuple[str, ...]
    epsilon_source: str
    effect_floor_factor: float
    convergence_rule: str
    repeat_baseline: str
    identity_baseline: str
    p0_reused_once: bool
    evaluate_values: bool
    field_function_decision_allowed: bool
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != _CONTRACT_ID
            or self.w7an_container_digest != _W7AN_CONTAINER_DIGEST
            or tuple(self.resolutions) != _RESOLUTIONS
            or tuple(self.comparisons) != _COMPARISONS
            or tuple(self.roles) != _ROLES
            or tuple(self.primary_metrics) != _PRIMARY_METRICS
            or tuple(self.diagnostic_metrics) != _DIAGNOSTIC_METRICS
            or self.epsilon_source
            != "maximum-r2-r4-primary-linf-distance"
            or self.effect_floor_factor != _EFFECT_FLOOR_FACTOR
            or self.convergence_rule
            != "rolewise-r2-r4-strictly-smaller-than-r1-r2-or-both-zero"
            or self.repeat_baseline != "primary-repeat-exact-zero"
            or self.identity_baseline
            != "same-resolution-self-distance-exact-zero"
            or self.p0_reused_once is not True
            or self.evaluate_values is not False
            or self.field_function_decision_allowed is not False
            or self.contract_digest != _digest(_payload())
        ):
            raise W7AOResolutionComparisonContractError(
                "W7-AO comparison contract differs"
            )


def build_w7ao_resolution_comparison_contract(
) -> W7AOResolutionComparisonContract:
    """Build the static contract without accepting a W7-AN container."""

    payload = _payload()
    return W7AOResolutionComparisonContract(
        _CONTRACT_ID,
        _W7AN_CONTAINER_DIGEST,
        _RESOLUTIONS,
        _COMPARISONS,
        _ROLES,
        _PRIMARY_METRICS,
        _DIAGNOSTIC_METRICS,
        "maximum-r2-r4-primary-linf-distance",
        _EFFECT_FLOOR_FACTOR,
        "rolewise-r2-r4-strictly-smaller-than-r1-r2-or-both-zero",
        "primary-repeat-exact-zero",
        "same-resolution-self-distance-exact-zero",
        True,
        False,
        False,
        _digest(payload),
    )
