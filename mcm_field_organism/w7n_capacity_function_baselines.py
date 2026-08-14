"""Pure W7-N baseline kernels without source paths or matrix execution."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math

from .mcm_f3_baseline_coupling import (
    MCMF3BaselineCouplingError,
    compute_mcm_f3_linear_coupled_baseline,
)
from .mcm_f3_coupling import (
    MCMF3CouplingError,
    MCMF3CouplingResult,
    MCMF3LocalRate,
    compute_mcm_f3_coupling,
)
from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import (
    MCMSubstrateArmContract,
    MCMSubstrateState,
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)
from .w7m_capacity_function_matrix import W7MBaselineSpec


class W7NCapacityFunctionBaselineError(ValueError):
    """Raised when a frozen W7-N baseline leaves its technical contract."""


_LOCAL_EQUATIONS = {
    "leak": "dz_i/dt=(S_i-z_i)/tau;R_i=0",
    "sat": "du_i/dt=(S_i-u_i)/tau;z_i=tanh(u_i);R_i=0",
    "norm": "z_i=leak(S_i);observer_i=z_i/(epsilon+sum_j(abs(z_j)))",
}
_COUPLING_EQUATIONS = {
    "lin": "use=compute_mcm_f3_linear_coupled_baseline",
    "f3": "use=compute_mcm_f3_coupling",
    "const-v": "use=compute_mcm_f3_coupling;lambda_sm=V_initial",
    "mob": "q_i_to_j=lambda*M_i*(1-M_i/C_site)*(1+kappa*dS_ij)",
}


def _parameters(spec: W7MBaselineSpec) -> dict[str, float]:
    if not isinstance(spec, W7MBaselineSpec):
        raise W7NCapacityFunctionBaselineError(
            "W7-N requires one frozen W7-M baseline specification"
        )
    return dict(spec.parameter_bindings)


def _validated_values(values, role: str) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise W7NCapacityFunctionBaselineError(
            f"{role} must contain numeric values"
        ) from exc
    if not result or any(not math.isfinite(value) for value in result):
        raise W7NCapacityFunctionBaselineError(
            f"{role} must be nonempty and finite"
        )
    return result


@dataclass(frozen=True, slots=True)
class W7NLocalBaselineState:
    """One independent scalar state per field location."""

    model_id: str
    latent: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.model_id not in _LOCAL_EQUATIONS:
            raise W7NCapacityFunctionBaselineError(
                "unknown W7-N local baseline model"
            )
        object.__setattr__(
            self,
            "latent",
            _validated_values(self.latent, "local baseline latent state"),
        )


@dataclass(frozen=True, slots=True)
class W7NLocalBaselineResult:
    """Completed pure local state and its observer-only output."""

    state: W7NLocalBaselineState
    output: tuple[float, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.state, W7NLocalBaselineState):
            raise W7NCapacityFunctionBaselineError(
                "local baseline result requires one state"
            )
        output = _validated_values(self.output, "local baseline output")
        if len(output) != len(self.state.latent):
            raise W7NCapacityFunctionBaselineError(
                "local baseline output must match its state"
            )
        object.__setattr__(self, "output", output)


def build_zero_w7n_local_baseline(
    spec: W7MBaselineSpec,
    location_count: int,
) -> W7NLocalBaselineState:
    """Build a zero local baseline state without reading a field."""

    _parameters(spec)
    if spec.model_id not in _LOCAL_EQUATIONS:
        raise W7NCapacityFunctionBaselineError(
            "W7-N zero state requires LEAK, SAT, or NORM"
        )
    if spec.equation_contract != _LOCAL_EQUATIONS[spec.model_id]:
        raise W7NCapacityFunctionBaselineError(
            "W7-N local equation differs from its frozen contract"
        )
    if (
        isinstance(location_count, bool)
        or not isinstance(location_count, int)
        or location_count < 1
    ):
        raise W7NCapacityFunctionBaselineError(
            "location_count must be a positive integer"
        )
    return W7NLocalBaselineState(spec.model_id, (0.0,) * location_count)


def advance_w7n_local_baseline(
    spec: W7MBaselineSpec,
    state: W7NLocalBaselineState,
    evidence,
    duration_seconds: float,
) -> W7NLocalBaselineResult:
    """Advance one frozen local baseline exactly over constant evidence."""

    parameters = _parameters(spec)
    if spec.model_id not in _LOCAL_EQUATIONS:
        raise W7NCapacityFunctionBaselineError(
            "W7-N local advance requires LEAK, SAT, or NORM"
        )
    if spec.equation_contract != _LOCAL_EQUATIONS[spec.model_id]:
        raise W7NCapacityFunctionBaselineError(
            "W7-N local equation differs from its frozen contract"
        )
    if not isinstance(state, W7NLocalBaselineState):
        raise W7NCapacityFunctionBaselineError(
            "W7-N local advance requires one local state"
        )
    if state.model_id != spec.model_id:
        raise W7NCapacityFunctionBaselineError(
            "W7-N local state and specification differ"
        )
    current_evidence = _validated_values(evidence, "local baseline evidence")
    if len(current_evidence) != len(state.latent):
        raise W7NCapacityFunctionBaselineError(
            "local baseline evidence must match its state"
        )
    if any(value < -1.0 or value > 1.0 for value in current_evidence):
        raise W7NCapacityFunctionBaselineError(
            "local baseline evidence left the normalized field domain"
        )
    if isinstance(duration_seconds, bool):
        raise W7NCapacityFunctionBaselineError(
            "duration_seconds must be numeric, not boolean"
        )
    try:
        duration = float(duration_seconds)
    except (TypeError, ValueError) as exc:
        raise W7NCapacityFunctionBaselineError(
            "duration_seconds must be numeric"
        ) from exc
    if not math.isfinite(duration) or duration < 0.0:
        raise W7NCapacityFunctionBaselineError(
            "duration_seconds must be finite and nonnegative"
        )
    tau = parameters.get("time_constant_seconds")
    if tau is None or tau <= 0.0:
        raise W7NCapacityFunctionBaselineError(
            "local baseline time constant must be positive"
        )
    retention = math.exp(-duration / tau)
    latent = tuple(
        retention * previous + (1.0 - retention) * value
        for previous, value in zip(
            state.latent,
            current_evidence,
            strict=True,
        )
    )
    if spec.model_id == "sat":
        output = tuple(math.tanh(value) for value in latent)
    elif spec.model_id == "norm":
        epsilon = parameters.get("epsilon")
        if epsilon is None or epsilon <= 0.0:
            raise W7NCapacityFunctionBaselineError(
                "NORM epsilon must be positive"
            )
        denominator = epsilon + math.fsum(abs(value) for value in latent)
        output = tuple(value / denominator for value in latent)
    else:
        output = latent
    return W7NLocalBaselineResult(
        W7NLocalBaselineState(spec.model_id, latent),
        output,
    )


def _validated_coupling_inputs(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
) -> tuple[tuple[str, ...], tuple[tuple[str, str], ...]]:
    if not isinstance(layer, MCMNeuronLayer):
        raise W7NCapacityFunctionBaselineError(
            "W7-N coupling requires one MCM neuron layer"
        )
    if not isinstance(substrate, MCMSubstrateState):
        raise W7NCapacityFunctionBaselineError(
            "W7-N coupling requires one scalar state per field location"
        )
    neuron_ids = tuple(neuron.neuron_id for neuron in layer.neurons)
    if substrate.neuron_ids != neuron_ids:
        raise W7NCapacityFunctionBaselineError(
            "W7-N coupling state and field locations differ"
        )
    try:
        edges = mcm_substrate_edge_inventory(layer)
        edge_digest = mcm_substrate_edge_inventory_digest(layer)
    except MCMSubstrateStateError as exc:
        raise W7NCapacityFunctionBaselineError(str(exc)) from exc
    if substrate.edge_inventory_digest != edge_digest:
        raise W7NCapacityFunctionBaselineError(
            "W7-N coupling geometry differs from the field"
        )
    return neuron_ids, edges


def _mobility_coupling(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
    site_capacity: float,
) -> MCMF3CouplingResult:
    neuron_ids, edges = _validated_coupling_inputs(layer, substrate)
    if not math.isfinite(site_capacity) or site_capacity <= 0.0:
        raise W7NCapacityFunctionBaselineError(
            "MOB site_capacity must be finite and positive"
        )
    activation = tuple(float(item.activation) for item in layer.neurons)
    mass = tuple(float(item.mass) for item in substrate.masses)
    if any(value < 0.0 or value > site_capacity for value in mass):
        raise W7NCapacityFunctionBaselineError(
            "MOB pre-state must remain inside its comparison scale"
        )
    mobility = tuple(1.0 - value / site_capacity for value in mass)
    index = {neuron_id: offset for offset, neuron_id in enumerate(neuron_ids)}
    mass_rate = [0.0] * len(neuron_ids)
    arm = substrate.arm
    for first_id, second_id in edges:
        first = index[first_id]
        second = index[second_id]
        activation_delta = activation[second] - activation[first]
        first_factor = 1.0 + arm.kappa * activation_delta
        second_factor = 1.0 - arm.kappa * activation_delta
        if first_factor < 0.0 or second_factor < 0.0:
            raise W7NCapacityFunctionBaselineError(
                "MOB directed field factors must remain nonnegative"
            )
        first_to_second = (
            arm.lambda_sm_per_second
            * mass[first]
            * mobility[first]
            * first_factor
        )
        second_to_first = (
            arm.lambda_sm_per_second
            * mass[second]
            * mobility[second]
            * second_factor
        )
        net = first_to_second - second_to_first
        mass_rate[first] -= net
        mass_rate[second] += net
    total_mass = arm.initial_total_mass
    return MCMF3CouplingResult(
        tuple(
            MCMF3LocalRate(
                neuron_id,
                mass_rate[offset],
                -arm.eta
                * (1.0 - activation[offset] * activation[offset])
                * mass_rate[offset]
                / total_mass,
            )
            for offset, neuron_id in enumerate(neuron_ids)
        )
    )


def _substrate_with_frozen_arm(
    substrate: MCMSubstrateState,
    arm_id: str,
    parameters: dict[str, float],
) -> MCMSubstrateState:
    try:
        arm = MCMSubstrateArmContract(
            arm_id,
            parameters["lambda_sm"],
            parameters["kappa"],
            parameters["eta"],
            substrate.arm.initial_total_mass,
        )
    except KeyError as exc:
        raise W7NCapacityFunctionBaselineError(
            "W7-N coupling parameters are incomplete"
        ) from exc
    return replace(substrate, arm=arm)


def compute_w7n_coupling_baseline(
    spec: W7MBaselineSpec,
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
) -> MCMF3CouplingResult:
    """Evaluate one frozen LIN, F3, CONST-V, or MOB derivative."""

    parameters = _parameters(spec)
    if spec.model_id not in _COUPLING_EQUATIONS:
        raise W7NCapacityFunctionBaselineError(
            "W7-N coupling requires LIN, F3, CONST-V, or MOB"
        )
    if spec.equation_contract != _COUPLING_EQUATIONS[spec.model_id]:
        raise W7NCapacityFunctionBaselineError(
            "W7-N coupling equation differs from its frozen contract"
        )
    try:
        if spec.model_id == "lin":
            frozen = _substrate_with_frozen_arm(
                substrate,
                "w7n.lin",
                parameters,
            )
            return compute_mcm_f3_linear_coupled_baseline(layer, frozen)
        if spec.model_id == "f3":
            frozen = _substrate_with_frozen_arm(
                substrate,
                "w7n.f3",
                parameters,
            )
            return compute_mcm_f3_coupling(layer, frozen)
        if spec.model_id == "const-v":
            frozen = _substrate_with_frozen_arm(
                substrate,
                "w7n.const-v",
                parameters,
            )
            return compute_mcm_f3_coupling(layer, frozen)
        frozen = _substrate_with_frozen_arm(
            substrate,
            "w7n.mob",
            parameters,
        )
        return _mobility_coupling(
            layer,
            frozen,
            parameters["site_capacity"],
        )
    except (
        KeyError,
        MCMF3BaselineCouplingError,
        MCMF3CouplingError,
        MCMSubstrateStateError,
    ) as exc:
        raise W7NCapacityFunctionBaselineError(str(exc)) from exc
