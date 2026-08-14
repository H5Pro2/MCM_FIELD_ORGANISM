"""Private E1 E4 profile, S2-B2, and CONST-V baseline handoffs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
import math
import re

import numpy as np

from .mcm_f3_coupling import MCMF3CouplingResult
from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import (
    MCMSubstrateArmContract,
    MCMSubstrateState,
    build_uniform_mcm_substrate,
    mcm_substrate_edge_inventory_digest,
)
from .s2_reference_baselines import (
    S2ReferenceAdvance,
    S2ReferenceBaselineError,
    S2ReferenceModelConfig,
    S2ReferenceState,
    _matrix_exponential,
    advance_s2_reference_model,
)
from .w7m_capacity_function_matrix import (
    W7MBaselineSpec,
    build_w7m_capacity_function_matrix_adapter,
)
from .w7n_capacity_function_baselines import (
    W7NCapacityFunctionBaselineError,
    compute_w7n_coupling_baseline,
)


class E1E4BaselineHandoffError(ValueError):
    """Raised when an E4 profile or baseline handoff leaves S1-CE."""


E1_E4_CHECKPOINT_IDS = (
    "h8",
    "g1",
    "g4",
    "g8",
    "c1",
    "c2",
    "c3",
    "c4",
    "c5",
    "c6",
    "c7",
    "c8",
)
E1_E4_MODEL_IDS = ("e1", "b0", "b1", "b2", "b3", "b4", "b5", "b6", "oracle-g")
E1_E4_PROFILE_COMPONENT_COUNT = 72
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9.-]*$")


def _finite_vector(values, role: str, *, length: int = 3) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise E1E4BaselineHandoffError(f"{role} must be numeric") from exc
    if len(result) != length or any(not math.isfinite(value) for value in result):
        raise E1E4BaselineHandoffError(
            f"{role} must contain exactly {length} finite values"
        )
    return result


@dataclass(frozen=True, slots=True)
class E1E4CheckpointEffect:
    """One signed S/H effect at one registered lifecycle checkpoint."""

    checkpoint_id: str
    activation_effect: tuple[float, ...]
    afterimage_effect: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.checkpoint_id not in E1_E4_CHECKPOINT_IDS:
            raise E1E4BaselineHandoffError("unknown E4 checkpoint")
        object.__setattr__(
            self,
            "activation_effect",
            _finite_vector(self.activation_effect, "activation_effect"),
        )
        object.__setattr__(
            self,
            "afterimage_effect",
            _finite_vector(self.afterimage_effect, "afterimage_effect"),
        )


@dataclass(frozen=True, slots=True)
class E1E4ObservableProfile:
    """Canonical signed 12-checkpoint, 72-component observable profile."""

    model_id: str
    checkpoints: tuple[E1E4CheckpointEffect, ...]

    def __post_init__(self) -> None:
        if self.model_id not in E1_E4_MODEL_IDS:
            raise E1E4BaselineHandoffError("unknown E4 model id")
        checkpoints = tuple(self.checkpoints)
        if tuple(item.checkpoint_id for item in checkpoints) != E1_E4_CHECKPOINT_IDS:
            raise E1E4BaselineHandoffError("E4 checkpoints must be complete and ordered")
        object.__setattr__(self, "checkpoints", checkpoints)

    @property
    def components(self) -> tuple[float, ...]:
        result = tuple(
            value
            for item in self.checkpoints
            for vector in (item.activation_effect, item.afterimage_effect)
            for value in vector
        )
        if len(result) != E1_E4_PROFILE_COMPONENT_COUNT:
            raise E1E4BaselineHandoffError("E4 profile component count changed")
        return result

    def digest(self) -> str:
        payload = {
            "model_id": self.model_id,
            "checkpoints": [asdict(item) for item in self.checkpoints],
        }
        encoded = json.dumps(
            payload, allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("ascii")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class E1E4ProfileDistance:
    """Raw profile residuals in the fixed reference scale."""

    reference_model_id: str
    compared_model_id: str
    profile_linf_residual: float
    profile_l1_residual: float
    candidate_profile_linf: float
    relative_profile_linf_residual: float
    release_segment_linf_residual: float
    competition_segment_linf_residual: float

    def __post_init__(self) -> None:
        if self.reference_model_id != "e1" or self.compared_model_id not in E1_E4_MODEL_IDS:
            raise E1E4BaselineHandoffError("invalid E4 profile comparison identity")
        for item in fields(self):
            if item.name.endswith("_id"):
                continue
            value = float(getattr(self, item.name))
            if not math.isfinite(value) or value < 0.0:
                raise E1E4BaselineHandoffError(f"{item.name} must be finite and nonnegative")
            object.__setattr__(self, item.name, value)


def compare_e1_e4_profiles(
    reference: E1E4ObservableProfile,
    compared: E1E4ObservableProfile,
) -> E1E4ProfileDistance:
    """Compare one baseline with the signed E1 lifecycle profile."""

    if not isinstance(reference, E1E4ObservableProfile) or reference.model_id != "e1":
        raise E1E4BaselineHandoffError("profile reference must be E1")
    if not isinstance(compared, E1E4ObservableProfile) or compared.model_id == "e1":
        raise E1E4BaselineHandoffError("compared profile must be one baseline")
    first = np.asarray(reference.components, dtype=np.float64)
    second = np.asarray(compared.components, dtype=np.float64)
    residual = np.abs(first - second)
    scale = float(np.max(np.abs(first)))
    if scale == 0.0:
        raise E1E4BaselineHandoffError("E1 reference profile has no measurable effect")
    release_end = 4 * 6
    return E1E4ProfileDistance(
        "e1",
        compared.model_id,
        float(np.max(residual)),
        float(np.sum(residual)),
        scale,
        float(np.max(residual)) / scale,
        float(np.max(residual[:release_end])),
        float(np.max(residual[release_end:])),
    )


@dataclass(frozen=True, slots=True)
class E1E4S2B2Handoff:
    """Frozen binding of S2 B2/B1 to one three-node E4 geometry."""

    handoff_id: str
    geometry_digest: str
    config: S2ReferenceModelConfig
    node_count: int = 3

    def __post_init__(self) -> None:
        if self.handoff_id != "e1.e4.s2-b2-handoff.v1":
            raise E1E4BaselineHandoffError("S2-B2 handoff identity changed")
        if not isinstance(self.geometry_digest, str) or len(self.geometry_digest) != 64:
            raise E1E4BaselineHandoffError("S2-B2 geometry digest is invalid")
        if self.config != S2ReferenceModelConfig() or self.node_count != 3:
            raise E1E4BaselineHandoffError("S2-B2 frozen configuration changed")


@dataclass(frozen=True, slots=True)
class E1E4S2FrozenProbeResult:
    """S2 S/H probe result with an unchanged fixed L vector."""

    state: S2ReferenceState
    backreaction_enabled: bool

    def __post_init__(self) -> None:
        if not isinstance(self.state, S2ReferenceState) or not isinstance(
            self.backreaction_enabled, bool
        ):
            raise E1E4BaselineHandoffError("invalid frozen S2-B2 probe result")


def build_e1_e4_s2_b2_handoff(layer: MCMNeuronLayer) -> E1E4S2B2Handoff:
    if not isinstance(layer, MCMNeuronLayer) or len(layer.neurons) != 3:
        raise E1E4BaselineHandoffError("S2-B2 handoff requires three field nodes")
    return E1E4S2B2Handoff(
        "e1.e4.s2-b2-handoff.v1",
        mcm_substrate_edge_inventory_digest(layer),
        S2ReferenceModelConfig(),
    )


def build_zero_e1_e4_s2_state(handoff: E1E4S2B2Handoff) -> S2ReferenceState:
    if not isinstance(handoff, E1E4S2B2Handoff):
        raise E1E4BaselineHandoffError("zero S2 state requires its handoff")
    zero = (0.0,) * handoff.node_count
    return S2ReferenceState(zero, zero, zero)


def advance_e1_e4_s2_b2(
    handoff: E1E4S2B2Handoff,
    state: S2ReferenceState,
    generator: np.ndarray,
    boundary: np.ndarray,
    elapsed_seconds: float,
    *,
    backreaction_enabled: bool,
) -> S2ReferenceAdvance:
    """Advance B2, or its existing B1 no-backreaction intervention."""

    if not isinstance(handoff, E1E4S2B2Handoff) or not isinstance(
        backreaction_enabled, bool
    ):
        raise E1E4BaselineHandoffError("invalid S2-B2 advance control")
    if not isinstance(state, S2ReferenceState) or len(state.activation) != handoff.node_count:
        raise E1E4BaselineHandoffError("S2-B2 state and handoff geometry differ")
    try:
        return advance_s2_reference_model(
            "b2" if backreaction_enabled else "b1",
            state,
            generator,
            boundary,
            elapsed_seconds,
            handoff.config,
        )
    except S2ReferenceBaselineError as exc:
        raise E1E4BaselineHandoffError(str(exc)) from exc


def advance_frozen_e1_e4_s2_b2_probe(
    handoff: E1E4S2B2Handoff,
    state: S2ReferenceState,
    generator: np.ndarray,
    boundary: np.ndarray,
    elapsed_seconds: float,
    *,
    backreaction_enabled: bool,
) -> E1E4S2FrozenProbeResult:
    """Advance S/H while retaining the exact fixed S2 development vector."""

    if not isinstance(handoff, E1E4S2B2Handoff) or not isinstance(
        state, S2ReferenceState
    ) or len(state.activation) != handoff.node_count:
        raise E1E4BaselineHandoffError("frozen S2 probe geometry differs")
    if not isinstance(backreaction_enabled, bool):
        raise E1E4BaselineHandoffError("frozen S2 probe control must be boolean")
    try:
        if not backreaction_enabled:
            neutral = advance_s2_reference_model(
                "b0", state, generator, boundary, elapsed_seconds, handoff.config
            ).state
            return E1E4S2FrozenProbeResult(neutral, False)
        generator = np.asarray(generator, dtype=np.float64)
        boundary = np.asarray(boundary, dtype=np.float64)
        count = handoff.node_count
        if generator.shape != (count, count) or boundary.shape != (count,):
            raise E1E4BaselineHandoffError("frozen S2 probe matrices differ")
        elapsed = float(elapsed_seconds)
        if not math.isfinite(elapsed) or elapsed <= 0.0:
            raise E1E4BaselineHandoffError("frozen S2 probe time is invalid")
        config = handoff.config
        identity = np.eye(count, dtype=np.float64)
        zero = np.zeros((count, count), dtype=np.float64)
        tracking = 1.0 / config.afterimage_time_seconds
        matrix = np.block(
            [
                [generator - config.coupling_rate_per_second * identity, zero, (
                    boundary
                    + config.coupling_rate_per_second
                    * np.asarray(state.development, dtype=np.float64)
                )[:, None]],
                [tracking * identity, -tracking * identity, np.zeros((count, 1))],
                [np.zeros((1, count)), np.zeros((1, count)), np.zeros((1, 1))],
            ]
        )
        initial = np.concatenate(
            (
                np.asarray(state.activation, dtype=np.float64),
                np.asarray(state.afterimage, dtype=np.float64),
                np.ones(1, dtype=np.float64),
            )
        )
        result = _matrix_exponential(matrix * elapsed) @ initial
        frozen = S2ReferenceState(
            tuple(float(value) for value in result[:count]),
            tuple(float(value) for value in result[count : 2 * count]),
            state.development,
        )
        return E1E4S2FrozenProbeResult(frozen, True)
    except S2ReferenceBaselineError as exc:
        raise E1E4BaselineHandoffError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class E1E4ConstVHandoff:
    """Canonical W7-N CONST-V spec bound to one current field geometry."""

    handoff_id: str
    geometry_digest: str
    baseline_spec: W7MBaselineSpec
    initial_substrate: MCMSubstrateState

    def __post_init__(self) -> None:
        if self.handoff_id != "e1.e4.const-v-handoff.v1":
            raise E1E4BaselineHandoffError("CONST-V handoff identity changed")
        if self.baseline_spec.model_id != "const-v":
            raise E1E4BaselineHandoffError("CONST-V handoff requires its frozen spec")
        if dict(self.baseline_spec.parameter_bindings) != {
            "eta": 1.0,
            "kappa": 0.5,
            "lambda_sm": 0.5,
        }:
            raise E1E4BaselineHandoffError("CONST-V parameters changed")
        if self.initial_substrate.edge_inventory_digest != self.geometry_digest:
            raise E1E4BaselineHandoffError("CONST-V substrate geometry changed")


def build_e1_e4_const_v_handoff(layer: MCMNeuronLayer) -> E1E4ConstVHandoff:
    if not isinstance(layer, MCMNeuronLayer) or len(layer.neurons) != 3:
        raise E1E4BaselineHandoffError("CONST-V handoff requires three field nodes")
    matrix = build_w7m_capacity_function_matrix_adapter()
    matches = tuple(item for item in matrix.baselines if item.model_id == "const-v")
    if len(matches) != 1:
        raise E1E4BaselineHandoffError("canonical CONST-V spec is unavailable")
    spec = matches[0]
    parameters = dict(spec.parameter_bindings)
    arm = MCMSubstrateArmContract(
        "e1.e4.const-v",
        parameters["lambda_sm"],
        parameters["kappa"],
        parameters["eta"],
        1.0,
    )
    substrate = build_uniform_mcm_substrate(layer, arm)
    return E1E4ConstVHandoff(
        "e1.e4.const-v-handoff.v1",
        mcm_substrate_edge_inventory_digest(layer),
        spec,
        substrate,
    )


def compute_e1_e4_const_v_coupling(
    handoff: E1E4ConstVHandoff,
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
) -> MCMF3CouplingResult:
    """Delegate the target geometry to the unchanged W7-N CONST-V kernel."""

    if not isinstance(handoff, E1E4ConstVHandoff):
        raise E1E4BaselineHandoffError("CONST-V coupling requires its handoff")
    if mcm_substrate_edge_inventory_digest(layer) != handoff.geometry_digest:
        raise E1E4BaselineHandoffError("CONST-V field geometry differs")
    if substrate.edge_inventory_digest != handoff.geometry_digest:
        raise E1E4BaselineHandoffError("CONST-V state geometry differs")
    try:
        return compute_w7n_coupling_baseline(
            handoff.baseline_spec, layer, substrate
        )
    except W7NCapacityFunctionBaselineError as exc:
        raise E1E4BaselineHandoffError(str(exc)) from exc
