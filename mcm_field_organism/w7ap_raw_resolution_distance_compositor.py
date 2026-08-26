"""W7-AP raw R1/R2 and R2/R4 residual distances without evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

from .w7an_r124_resolution_container import W7ANR124ResolutionContainer
from .w7ao_resolution_comparison_contract import (
    W7AOResolutionComparisonContract,
)


class W7APRawResolutionDistanceError(ValueError):
    """Raised when raw resolution distances leave the W7-AO contract."""


_COMPOSITOR_ID = "w7ap.raw-r1-r2-r2-r4-resolution-distance-compositor.v1"
_W7AN_CONTAINER_DIGEST = (
    "4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5"
)
_W7AO_CONTRACT_DIGEST = (
    "14455f15e6f3d0f96106aa766ae544ec76f19b5c94308329ec45fd0cd12067dc"
)
_RESOLUTIONS = ("r1", "r2", "r4")
_COMPARISONS = (("r1-r2", "r1", "r2"), ("r2-r4", "r2", "r4"))
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_ROLES = tuple(
    (path_id, checkpoint)
    for path_id in _PATH_IDS
    for checkpoint in range(5)
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_vector(values, role: str) -> tuple[float, ...]:
    result = tuple(float(item) for item in values)
    if not result or any(not math.isfinite(item) for item in result):
        raise W7APRawResolutionDistanceError(f"{role} must be finite")
    return result


def _nonnegative(value: float, role: str) -> float:
    if isinstance(value, bool):
        raise W7APRawResolutionDistanceError(f"{role} must be numeric")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise W7APRawResolutionDistanceError(
            f"{role} must be finite and nonnegative"
        )
    return result


def _sample_payload(
    tick: int,
    s_deltas: tuple[float, ...],
    h_deltas: tuple[float, ...],
) -> dict[str, object]:
    return {
        "tick": tick,
        "s_deltas": s_deltas,
        "h_deltas": h_deltas,
    }


@dataclass(frozen=True, slots=True)
class W7APResolutionDistanceSample:
    """One directed left-minus-right residual difference."""

    tick: int
    s_deltas: tuple[float, ...]
    h_deltas: tuple[float, ...]
    distance_sample_digest: str

    def __post_init__(self) -> None:
        if isinstance(self.tick, bool) or not isinstance(self.tick, int):
            raise W7APRawResolutionDistanceError(
                "distance sample tick must be an integer"
            )
        s_values = _finite_vector(self.s_deltas, "S deltas")
        h_values = _finite_vector(self.h_deltas, "H deltas")
        if len(s_values) != len(h_values):
            raise W7APRawResolutionDistanceError(
                "distance sample S/H geometry differs"
            )
        if self.distance_sample_digest != _digest(
            _sample_payload(self.tick, s_values, h_values)
        ):
            raise W7APRawResolutionDistanceError(
                "distance sample digest differs"
            )
        object.__setattr__(self, "s_deltas", s_values)
        object.__setattr__(self, "h_deltas", h_values)


def _distance_samples(left_samples, right_samples):
    left_samples = tuple(left_samples)
    right_samples = tuple(right_samples)
    if not left_samples or len(left_samples) != len(right_samples):
        raise W7APRawResolutionDistanceError(
            "resolution comparison sample inventory differs"
        )
    result = []
    for left, right in zip(left_samples, right_samples, strict=True):
        if left.tick != right.tick:
            raise W7APRawResolutionDistanceError(
                "resolution comparison sample ticks differ"
            )
        left_s = _finite_vector(left.s_residuals, "left S residuals")
        right_s = _finite_vector(right.s_residuals, "right S residuals")
        left_h = _finite_vector(left.h_residuals, "left H residuals")
        right_h = _finite_vector(right.h_residuals, "right H residuals")
        if len({len(left_s), len(right_s), len(left_h), len(right_h)}) != 1:
            raise W7APRawResolutionDistanceError(
                "resolution comparison sample geometry differs"
            )
        s_deltas = tuple(a - b for a, b in zip(left_s, right_s, strict=True))
        h_deltas = tuple(a - b for a, b in zip(left_h, right_h, strict=True))
        payload = _sample_payload(left.tick, s_deltas, h_deltas)
        result.append(
            W7APResolutionDistanceSample(
                left.tick,
                s_deltas,
                h_deltas,
                _digest(payload),
            )
        )
    return tuple(result)


def _metrics(samples) -> tuple[float, float, float]:
    samples = tuple(samples)
    s_values = tuple(value for sample in samples for value in sample.s_deltas)
    h_values = tuple(value for sample in samples for value in sample.h_deltas)
    if not s_values or not h_values:
        raise W7APRawResolutionDistanceError(
            "resolution distance requires samples"
        )
    return (
        max(abs(value) for value in s_values),
        max(abs(value) for value in h_values),
        math.sqrt(
            math.fsum(value * value for value in s_values)
            + math.fsum(value * value for value in h_values)
        ),
    )


def _role_payload(
    comparison_id: str,
    left_resolution_id: str,
    right_resolution_id: str,
    path_id: str,
    checkpoint: int,
    plan_checkpoint_digest: str,
    observation_ticks: tuple[int, ...],
    samples: tuple[W7APResolutionDistanceSample, ...],
    s_linf: float,
    h_linf: float,
    sh_l2: float,
) -> dict[str, object]:
    return {
        "comparison_id": comparison_id,
        "left_resolution_id": left_resolution_id,
        "right_resolution_id": right_resolution_id,
        "path_id": path_id,
        "checkpoint": checkpoint,
        "plan_checkpoint_digest": plan_checkpoint_digest,
        "observation_ticks": observation_ticks,
        "distance_sample_digests": tuple(
            item.distance_sample_digest for item in samples
        ),
        "S_linf": s_linf,
        "H_linf": h_linf,
        "SH_l2": sh_l2,
        "evaluated": False,
    }


@dataclass(frozen=True, slots=True)
class W7APRoleDistance:
    """One of 70 aligned raw role distances without a decision."""

    comparison_id: str
    left_resolution_id: str
    right_resolution_id: str
    path_id: str
    checkpoint: int
    plan_checkpoint_digest: str
    observation_ticks: tuple[int, ...]
    distance_samples: tuple[W7APResolutionDistanceSample, ...] = field(
        repr=False
    )
    S_linf: float
    H_linf: float
    SH_l2: float
    evaluated: bool
    role_distance_digest: str

    def __post_init__(self) -> None:
        samples = tuple(self.distance_samples)
        ticks = tuple(self.observation_ticks)
        comparison = (
            self.comparison_id,
            self.left_resolution_id,
            self.right_resolution_id,
        )
        if (
            comparison not in _COMPARISONS
            or (self.path_id, self.checkpoint) not in _ROLES
            or not self.plan_checkpoint_digest
            or ticks != tuple(item.tick for item in samples)
            or self.evaluated is not False
        ):
            raise W7APRawResolutionDistanceError(
                "role distance binding is invalid"
            )
        for role in ("S_linf", "H_linf", "SH_l2"):
            object.__setattr__(self, role, _nonnegative(getattr(self, role), role))
        if (self.S_linf, self.H_linf, self.SH_l2) != _metrics(samples):
            raise W7APRawResolutionDistanceError(
                "role distance metrics differ from samples"
            )
        payload = _role_payload(
            *comparison,
            self.path_id,
            self.checkpoint,
            self.plan_checkpoint_digest,
            ticks,
            samples,
            self.S_linf,
            self.H_linf,
            self.SH_l2,
        )
        if self.role_distance_digest != _digest(payload):
            raise W7APRawResolutionDistanceError("role distance digest differs")
        object.__setattr__(self, "observation_ticks", ticks)
        object.__setattr__(self, "distance_samples", samples)


def _build_role_distance(comparison, left_pair, right_pair) -> W7APRoleDistance:
    comparison_id, left_resolution_id, right_resolution_id = comparison
    if (
        (left_pair.path_id, left_pair.checkpoint)
        != (right_pair.path_id, right_pair.checkpoint)
        or left_pair.plan_checkpoint_digest
        != right_pair.plan_checkpoint_digest
        or tuple(left_pair.observation_ticks)
        != tuple(right_pair.observation_ticks)
    ):
        raise W7APRawResolutionDistanceError(
            "resolution role bindings do not align"
        )
    samples = _distance_samples(
        left_pair.residual_samples,
        right_pair.residual_samples,
    )
    metrics = _metrics(samples)
    payload = _role_payload(
        comparison_id,
        left_resolution_id,
        right_resolution_id,
        left_pair.path_id,
        left_pair.checkpoint,
        left_pair.plan_checkpoint_digest,
        tuple(left_pair.observation_ticks),
        samples,
        *metrics,
    )
    return W7APRoleDistance(
        comparison_id,
        left_resolution_id,
        right_resolution_id,
        left_pair.path_id,
        left_pair.checkpoint,
        left_pair.plan_checkpoint_digest,
        tuple(left_pair.observation_ticks),
        samples,
        *metrics,
        False,
        _digest(payload),
    )


def _identity_payload(resolution_id: str, path_id: str, checkpoint: int):
    return {
        "resolution_id": resolution_id,
        "path_id": path_id,
        "checkpoint": checkpoint,
        "S_linf": 0.0,
        "H_linf": 0.0,
        "SH_l2": 0.0,
    }


@dataclass(frozen=True, slots=True)
class W7APIdentityDistance:
    """One exact same-resolution zero control."""

    resolution_id: str
    path_id: str
    checkpoint: int
    S_linf: float
    H_linf: float
    SH_l2: float
    identity_distance_digest: str

    def __post_init__(self) -> None:
        if (
            self.resolution_id not in _RESOLUTIONS
            or (self.path_id, self.checkpoint) not in _ROLES
            or (self.S_linf, self.H_linf, self.SH_l2) != (0.0, 0.0, 0.0)
            or self.identity_distance_digest
            != _digest(
                _identity_payload(
                    self.resolution_id,
                    self.path_id,
                    self.checkpoint,
                )
            )
        ):
            raise W7APRawResolutionDistanceError(
                "identity distance is not exact zero"
            )


def _result_payload(
    role_distances: tuple[W7APRoleDistance, ...],
    identity_distances: tuple[W7APIdentityDistance, ...],
    identity_countercontrol_digest: str,
    order_countercontrol_digest: str,
) -> dict[str, object]:
    return {
        "compositor_id": _COMPOSITOR_ID,
        "w7an_container_digest": _W7AN_CONTAINER_DIGEST,
        "w7ao_contract_digest": _W7AO_CONTRACT_DIGEST,
        "role_distance_digests": tuple(
            item.role_distance_digest for item in role_distances
        ),
        "identity_distance_digests": tuple(
            item.identity_distance_digest for item in identity_distances
        ),
        "identity_countercontrol_digest": identity_countercontrol_digest,
        "order_countercontrol_digest": order_countercontrol_digest,
        "repeat_baseline_bound_to_canonical_w7an": True,
        "convergence_evaluated": False,
        "epsilon_num_ready": False,
        "effect_floor_ready": False,
        "field_function_decision_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7APRawResolutionDistanceComposition:
    """All preregistered raw distances with decisions still locked."""

    compositor_id: str
    w7an_container_digest: str
    w7ao_contract_digest: str
    role_distances: tuple[W7APRoleDistance, ...] = field(repr=False)
    identity_distances: tuple[W7APIdentityDistance, ...] = field(repr=False)
    identity_countercontrol_digest: str
    order_countercontrol_digest: str
    repeat_baseline_bound_to_canonical_w7an: bool
    convergence_evaluated: bool
    epsilon_num_ready: bool
    effect_floor_ready: bool
    field_function_decision_allowed: bool
    raw_resolution_distance_composition_digest: str

    def __post_init__(self) -> None:
        role_distances = tuple(self.role_distances)
        identity_distances = tuple(self.identity_distances)
        expected_comparisons = tuple(
            (comparison_id, left_id, right_id, path_id, checkpoint)
            for comparison_id, left_id, right_id in _COMPARISONS
            for path_id, checkpoint in _ROLES
        )
        expected_identities = tuple(
            (resolution_id, path_id, checkpoint)
            for resolution_id in _RESOLUTIONS
            for path_id, checkpoint in _ROLES
        )
        if (
            self.compositor_id != _COMPOSITOR_ID
            or self.w7an_container_digest != _W7AN_CONTAINER_DIGEST
            or self.w7ao_contract_digest != _W7AO_CONTRACT_DIGEST
            or tuple(
                (
                    item.comparison_id,
                    item.left_resolution_id,
                    item.right_resolution_id,
                    item.path_id,
                    item.checkpoint,
                )
                for item in role_distances
            )
            != expected_comparisons
            or tuple(
                (item.resolution_id, item.path_id, item.checkpoint)
                for item in identity_distances
            )
            != expected_identities
            or not self.identity_countercontrol_digest
            or not self.order_countercontrol_digest
            or self.repeat_baseline_bound_to_canonical_w7an is not True
            or self.convergence_evaluated is not False
            or self.epsilon_num_ready is not False
            or self.effect_floor_ready is not False
            or self.field_function_decision_allowed is not False
        ):
            raise W7APRawResolutionDistanceError(
                "raw resolution distance composition binding is invalid"
            )
        payload = _result_payload(
            role_distances,
            identity_distances,
            self.identity_countercontrol_digest,
            self.order_countercontrol_digest,
        )
        if self.raw_resolution_distance_composition_digest != _digest(payload):
            raise W7APRawResolutionDistanceError(
                "raw resolution distance composition digest differs"
            )
        object.__setattr__(self, "role_distances", role_distances)
        object.__setattr__(self, "identity_distances", identity_distances)


def compose_w7ap_raw_resolution_distances(
    container: W7ANR124ResolutionContainer,
    contract: W7AOResolutionComparisonContract,
) -> W7APRawResolutionDistanceComposition:
    """Materialize 70 raw distances without applying any decision rule."""

    if not isinstance(container, W7ANR124ResolutionContainer) or not isinstance(
        contract, W7AOResolutionComparisonContract
    ):
        raise W7APRawResolutionDistanceError(
            "W7-AP requires W7-AN and W7-AO inputs"
        )
    if (
        container.resolution_container_digest != _W7AN_CONTAINER_DIGEST
        or contract.contract_digest != _W7AO_CONTRACT_DIGEST
        or contract.w7an_container_digest != _W7AN_CONTAINER_DIGEST
        or tuple(contract.comparisons) != _COMPARISONS
        or tuple(contract.roles) != _ROLES
        or contract.evaluate_values is not False
        or contract.field_function_decision_allowed is not False
        or container.convergence_compared is not False
        or container.effect_floor_ready is not False
    ):
        raise W7APRawResolutionDistanceError("W7-AP input binding differs")
    input_digest = container.resolution_container_digest
    resolutions = {item.resolution_id: item for item in container.resolutions}
    if tuple(resolutions) != _RESOLUTIONS:
        raise W7APRawResolutionDistanceError(
            "W7-AP resolution inventory differs"
        )
    pairs_by_resolution = {}
    for resolution_id, resolution in resolutions.items():
        pairs = tuple(resolution.pair_container.pairs)
        if (
            resolution.evaluated is not False
            or resolution.pair_container.evaluated is not False
            or tuple((item.path_id, item.checkpoint) for item in pairs) != _ROLES
        ):
            raise W7APRawResolutionDistanceError(
                "W7-AP role inventory differs"
            )
        pairs_by_resolution[resolution_id] = {
            (item.path_id, item.checkpoint): item for item in pairs
        }

    role_distances = tuple(
        _build_role_distance(
            comparison,
            pairs_by_resolution[comparison[1]][role],
            pairs_by_resolution[comparison[2]][role],
        )
        for comparison in _COMPARISONS
        for role in _ROLES
    )
    actual = {
        (
            item.comparison_id,
            item.left_resolution_id,
            item.right_resolution_id,
            item.path_id,
            item.checkpoint,
        ): item.role_distance_digest
        for item in role_distances
    }
    reversed_distances = tuple(
        _build_role_distance(
            comparison,
            pairs_by_resolution[comparison[1]][role],
            pairs_by_resolution[comparison[2]][role],
        )
        for comparison in reversed(_COMPARISONS)
        for role in reversed(_ROLES)
    )
    if any(
        actual[
            (
                item.comparison_id,
                item.left_resolution_id,
                item.right_resolution_id,
                item.path_id,
                item.checkpoint,
            )
        ]
        != item.role_distance_digest
        for item in reversed_distances
    ):
        raise W7APRawResolutionDistanceError(
            "reverse construction changed a role distance"
        )
    order_digest = _digest(
        {
            "canonical_role_distance_digests": tuple(
                item.role_distance_digest for item in role_distances
            ),
            "reverse_role_distance_digests": tuple(
                item.role_distance_digest for item in reversed_distances
            ),
        }
    )

    identity_distances = []
    for resolution_id in _RESOLUTIONS:
        for path_id, checkpoint in _ROLES:
            pair = pairs_by_resolution[resolution_id][(path_id, checkpoint)]
            identity_samples = _distance_samples(
                pair.residual_samples,
                pair.residual_samples,
            )
            if _metrics(identity_samples) != (0.0, 0.0, 0.0):
                raise W7APRawResolutionDistanceError(
                    "same-resolution identity distance is nonzero"
                )
            payload = _identity_payload(resolution_id, path_id, checkpoint)
            identity_distances.append(
                W7APIdentityDistance(
                    resolution_id,
                    path_id,
                    checkpoint,
                    0.0,
                    0.0,
                    0.0,
                    _digest(payload),
                )
            )
    identity_distances = tuple(identity_distances)
    identity_digest = _digest(
        tuple(item.identity_distance_digest for item in identity_distances)
    )
    if container.resolution_container_digest != input_digest:
        raise W7APRawResolutionDistanceError("W7-AP mutated its input")
    payload = _result_payload(
        role_distances,
        identity_distances,
        identity_digest,
        order_digest,
    )
    return W7APRawResolutionDistanceComposition(
        _COMPOSITOR_ID,
        _W7AN_CONTAINER_DIGEST,
        _W7AO_CONTRACT_DIGEST,
        role_distances,
        identity_distances,
        identity_digest,
        order_digest,
        True,
        False,
        False,
        False,
        False,
        _digest(payload),
    )
