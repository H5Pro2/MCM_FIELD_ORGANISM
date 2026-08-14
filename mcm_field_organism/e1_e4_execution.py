"""Private S1-CH execution contracts for the preregistered E1 E4 matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from typing import Callable, Mapping

from .e1_e4_baseline_handoffs import (
    E1E4ObservableProfile,
    E1E4ProfileDistance,
    compare_e1_e4_profiles,
)
from .mcm_f3_coupling import MCMF3CouplingResult, MCMF3LocalRate
from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import MCMSubstrateState


class E1E4ExecutionError(ValueError):
    """Raised when an S1-CH execution role leaves the S1-CG contract."""


E1_E4_EXECUTION_MODEL_IDS = (
    "e1",
    "b0",
    "b1",
    "b2",
    "b3",
    "b4",
    "b5",
    "b6",
    "oracle-g",
)
E1_E4_DECISION_BASELINE_IDS = ("b1", "b2", "b3", "b4", "b5", "b6")
E1_E4_ABSOLUTE_TOLERANCE = 1e-12
E1_E4_REFINEMENT_LIMIT = 0.01
E1_E4_PROFILE_LIMIT = 0.05
E1_E4_CONTINUITY_ANCHORS = (
    ("release_hold_s_linf", 0.003720672275362047),
    ("release_hold_h_linf", 0.002329590741211862),
    ("compete_release_s_linf", 0.0029908008917126083),
    ("compete_release_h_linf", 0.0025335555912394947),
    ("hold_p0_s_linf", 0.005960779905044511),
    ("hold_p0_h_linf", 0.0037253303212222977),
    ("release_p0_s_linf", 0.002240107629682464),
    ("release_p0_h_linf", 0.0013957395800104355),
    ("compete_p0_s_linf", 0.0026902423795267943),
    ("compete_p0_h_linf", 0.00238212405542311),
    ("release_analytic_linf", 1.734723475976807e-18),
    ("resource_budget_linf", 4.440892098500626e-16),
    ("release_total_binding_drop", 0.10364242805542052),
    ("compete_total_binding_rebound", 0.11840875933358301),
    ("maximum_refinement_linf", 1.2490009027033011e-15),
)
_EXPECTED_ANCHOR_NAMES = tuple(name for name, _ in E1_E4_CONTINUITY_ANCHORS)


def _nonnegative(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise E1E4ExecutionError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise E1E4ExecutionError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise E1E4ExecutionError(f"{role} must be finite and nonnegative")
    return result


def _digest(value: object) -> str:
    encoded = json.dumps(
        value, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


E1_E4_EXECUTION_CONTRACT_DIGEST = _digest(
    {
        "contract": "s1-cg.e1-e4.v1",
        "models": E1_E4_EXECUTION_MODEL_IDS,
        "decision_baselines": E1_E4_DECISION_BASELINE_IDS,
        "checkpoints": (
            "h8", "g1", "g4", "g8", "c1", "c2", "c3", "c4", "c5",
            "c6", "c7", "c8",
        ),
        "absolute_tolerance": E1_E4_ABSOLUTE_TOLERANCE,
        "refinement_limit": E1_E4_REFINEMENT_LIMIT,
        "profile_limit": E1_E4_PROFILE_LIMIT,
        "continuity_anchors": E1_E4_CONTINUITY_ANCHORS,
    }
)


@dataclass(frozen=True, slots=True)
class E1E4ModelRun:
    """One complete model profile and its technical validity controls."""

    model_id: str
    parameter_digest: str
    profile: E1E4ObservableProfile
    observation_schedule_matches: bool
    ablation_controls_hold: bool
    fixed_reader_controls_hold: bool
    invariants_hold: bool
    technically_compatible: bool
    relative_refinement_linf: float
    maximum_mass_or_budget_error: float
    minimum_internal_resource: float

    def __post_init__(self) -> None:
        if self.model_id not in E1_E4_EXECUTION_MODEL_IDS:
            raise E1E4ExecutionError("unknown E4 execution model")
        if (
            not isinstance(self.parameter_digest, str)
            or len(self.parameter_digest) != 64
        ):
            raise E1E4ExecutionError("model run requires one parameter digest")
        if not isinstance(self.profile, E1E4ObservableProfile):
            raise E1E4ExecutionError("model run requires one observable profile")
        if self.profile.model_id != self.model_id:
            raise E1E4ExecutionError("model and profile identities differ")
        for role in (
            "observation_schedule_matches",
            "ablation_controls_hold",
            "fixed_reader_controls_hold",
            "invariants_hold",
            "technically_compatible",
        ):
            if not isinstance(getattr(self, role), bool):
                raise E1E4ExecutionError(f"{role} must be boolean")
        object.__setattr__(
            self,
            "relative_refinement_linf",
            _nonnegative(self.relative_refinement_linf, "relative_refinement_linf"),
        )
        object.__setattr__(
            self,
            "maximum_mass_or_budget_error",
            _nonnegative(
                self.maximum_mass_or_budget_error,
                "maximum_mass_or_budget_error",
            ),
        )
        resource = float(self.minimum_internal_resource)
        if not math.isfinite(resource):
            raise E1E4ExecutionError("minimum_internal_resource must be finite")
        object.__setattr__(self, "minimum_internal_resource", resource)

    @property
    def controls_hold(self) -> bool:
        return (
            self.observation_schedule_matches
            and self.ablation_controls_hold
            and self.fixed_reader_controls_hold
            and self.invariants_hold
            and self.relative_refinement_linf <= E1_E4_REFINEMENT_LIMIT
        )


@dataclass(frozen=True, slots=True)
class E1E4BaselineMeasurement:
    """One registered baseline distance and its decision eligibility."""

    model_id: str
    distance: E1E4ProfileDistance
    controls_hold: bool
    technically_compatible: bool

    def __post_init__(self) -> None:
        if self.model_id not in E1_E4_DECISION_BASELINE_IDS:
            raise E1E4ExecutionError("measurement is not a decision baseline")
        if (
            not isinstance(self.distance, E1E4ProfileDistance)
            or self.distance.compared_model_id != self.model_id
        ):
            raise E1E4ExecutionError("baseline distance identity differs")
        if not isinstance(self.controls_hold, bool) or not isinstance(
            self.technically_compatible, bool
        ):
            raise E1E4ExecutionError("baseline validity flags must be boolean")

    @property
    def explains_profile(self) -> bool:
        return (
            self.controls_hold
            and self.technically_compatible
            and self.distance.relative_profile_linf_residual
            <= E1_E4_PROFILE_LIMIT
        )


@dataclass(frozen=True, slots=True)
class E1E4RunResult:
    """Complete ordered E4 raw result without an embedded decision."""

    contract_digest: str
    model_runs: tuple[E1E4ModelRun, ...]
    baseline_measurements: tuple[E1E4BaselineMeasurement, ...]
    continuity_anchors: tuple[tuple[str, float], ...]
    continuity_anchors_hold: bool

    def __post_init__(self) -> None:
        if self.contract_digest != E1_E4_EXECUTION_CONTRACT_DIGEST:
            raise E1E4ExecutionError("E4 execution contract digest changed")
        runs = tuple(self.model_runs)
        if tuple(item.model_id for item in runs) != E1_E4_EXECUTION_MODEL_IDS:
            raise E1E4ExecutionError("E4 model runs are incomplete or reordered")
        measurements = tuple(self.baseline_measurements)
        if tuple(item.model_id for item in measurements) != E1_E4_DECISION_BASELINE_IDS:
            raise E1E4ExecutionError("E4 baseline measurements are incomplete")
        anchors = tuple((str(name), float(value)) for name, value in self.continuity_anchors)
        if tuple(name for name, _ in anchors) != _EXPECTED_ANCHOR_NAMES:
            raise E1E4ExecutionError("E4 continuity anchors are incomplete or reordered")
        if any(not math.isfinite(value) for _, value in anchors):
            raise E1E4ExecutionError("E4 continuity anchors must be finite")
        if not isinstance(self.continuity_anchors_hold, bool):
            raise E1E4ExecutionError("continuity_anchors_hold must be boolean")
        object.__setattr__(self, "model_runs", runs)
        object.__setattr__(self, "baseline_measurements", measurements)
        object.__setattr__(self, "continuity_anchors", anchors)


E1E4CouplingCalculator = Callable[
    [MCMNeuronLayer, MCMSubstrateState], MCMF3CouplingResult
]
E1E4ModelRunner = Callable[[], E1E4ModelRun]


def without_e1_e4_f3_backreaction(
    calculator: E1E4CouplingCalculator,
) -> E1E4CouplingCalculator:
    """Keep the original state rate and remove only S/H backreaction."""

    if not callable(calculator):
        raise E1E4ExecutionError("F3 intervention requires one calculator")

    def intervened(
        layer: MCMNeuronLayer, substrate: MCMSubstrateState
    ) -> MCMF3CouplingResult:
        original = calculator(layer, substrate)
        if not isinstance(original, MCMF3CouplingResult):
            raise E1E4ExecutionError("F3 calculator returned an invalid result")
        return MCMF3CouplingResult(
            tuple(
                MCMF3LocalRate(item.neuron_id, item.mass_rate, 0.0)
                for item in original.rates
            )
        )

    return intervened


def build_frozen_e1_e4_f3_reader(
    calculator: E1E4CouplingCalculator,
    fixed_substrate: MCMSubstrateState,
) -> E1E4CouplingCalculator:
    """Keep M fixed while retaining its original current-S reader."""

    if not callable(calculator) or not isinstance(fixed_substrate, MCMSubstrateState):
        raise E1E4ExecutionError("frozen F3 reader requires calculator and M state")

    def frozen(
        layer: MCMNeuronLayer, runtime_substrate: MCMSubstrateState
    ) -> MCMF3CouplingResult:
        if not isinstance(runtime_substrate, MCMSubstrateState):
            raise E1E4ExecutionError("frozen F3 reader requires runtime geometry")
        if (
            runtime_substrate.neuron_ids != fixed_substrate.neuron_ids
            or runtime_substrate.edge_inventory_digest
            != fixed_substrate.edge_inventory_digest
        ):
            raise E1E4ExecutionError("frozen F3 probe geometry changed")
        original = calculator(layer, fixed_substrate)
        if not isinstance(original, MCMF3CouplingResult):
            raise E1E4ExecutionError("F3 calculator returned an invalid result")
        return MCMF3CouplingResult(
            tuple(
                MCMF3LocalRate(
                    item.neuron_id,
                    0.0,
                    item.activation_backreaction,
                )
                for item in original.rates
            )
        )

    return frozen


def preflight_e1_e4_runners(
    runners: Mapping[str, E1E4ModelRunner],
) -> tuple[E1E4ModelRunner, ...]:
    """Bind an exact runner inventory without executing any runner."""

    if not isinstance(runners, Mapping) or tuple(sorted(runners)) != tuple(
        sorted(E1_E4_EXECUTION_MODEL_IDS)
    ):
        raise E1E4ExecutionError("E4 runner inventory is incomplete or contains extras")
    ordered = tuple(runners[model_id] for model_id in E1_E4_EXECUTION_MODEL_IDS)
    if any(not callable(runner) for runner in ordered):
        raise E1E4ExecutionError("every E4 model runner must be callable")
    return ordered


def compose_e1_e4_run_result(
    runners: Mapping[str, E1E4ModelRunner],
    continuity_anchors: tuple[tuple[str, float], ...],
) -> E1E4RunResult:
    """Execute an injected complete matrix in the fixed S1-CG order."""

    ordered_runners = preflight_e1_e4_runners(runners)
    model_runs = tuple(runner() for runner in ordered_runners)
    if tuple(item.model_id for item in model_runs) != E1_E4_EXECUTION_MODEL_IDS:
        raise E1E4ExecutionError("an E4 runner returned the wrong model identity")
    reference = model_runs[0].profile
    by_id = {item.model_id: item for item in model_runs}
    measurements = tuple(
        E1E4BaselineMeasurement(
            model_id,
            compare_e1_e4_profiles(reference, by_id[model_id].profile),
            by_id[model_id].controls_hold,
            by_id[model_id].technically_compatible,
        )
        for model_id in E1_E4_DECISION_BASELINE_IDS
    )
    anchors = tuple((str(name), float(value)) for name, value in continuity_anchors)
    anchors_hold = (
        len(anchors) == len(E1_E4_CONTINUITY_ANCHORS)
        and tuple(name for name, _ in anchors) == _EXPECTED_ANCHOR_NAMES
        and all(
            abs(actual - expected) <= E1_E4_ABSOLUTE_TOLERANCE
            for (_, actual), (_, expected) in zip(
                anchors, E1_E4_CONTINUITY_ANCHORS, strict=True
            )
        )
    )
    return E1E4RunResult(
        E1_E4_EXECUTION_CONTRACT_DIGEST,
        model_runs,
        measurements,
        anchors,
        anchors_hold,
    )


def evaluate_e1_e4_run(result: E1E4RunResult) -> str:
    """Apply only the fixed S1-CE/S1-CG decision order."""

    if not isinstance(result, E1E4RunResult):
        raise E1E4ExecutionError("E4 evaluation requires one complete result")
    by_id = {item.model_id: item for item in result.model_runs}
    p0_is_zero = all(value == 0.0 for value in by_id["b0"].profile.components)
    oracle_distance = compare_e1_e4_profiles(
        by_id["e1"].profile, by_id["oracle-g"].profile
    )
    if (
        not result.continuity_anchors_hold
        or not all(item.controls_hold for item in result.model_runs)
        or not p0_is_zero
        or oracle_distance.profile_linf_residual > E1_E4_ABSOLUTE_TOLERANCE
    ):
        return "INVALID_E4_RUN"
    if not all(item.technically_compatible for item in result.model_runs):
        return "TECHNICALLY_INCOMPATIBLE_BASELINE_SET"
    if any(item.explains_profile for item in result.baseline_measurements):
        return "E4_EXPLAINED_BY_NARROW_BASELINE"
    return "E4_RESIDUAL_AFTER_REGISTERED_BASELINES"


def e1_e4_execution_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (E1E4ModelRun, E1E4BaselineMeasurement, E1E4RunResult)
        for item in fields(cls)
    )
