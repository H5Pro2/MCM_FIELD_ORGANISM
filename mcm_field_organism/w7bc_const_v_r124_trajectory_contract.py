"""Static W7-BC contract for CONST-V R1/R2/R4 seven-path trajectories."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class W7BCConstVTrajectoryContractError(ValueError):
    """Raised when the preregistered CONST-V trajectory boundary changes."""


_CONTRACT_ID = "w7bc.const-v-r124-seven-path-trajectory-contract.v1"
_W7M_MATRIX_DIGEST = (
    "a1e3f8a08fbef760c8f0b147f99cbebfcc05621c2265a70d853dd3d4863ffb6a"
)
_W7Y_PLAN_DIGEST = (
    "c771a3c28c04e04a61fa24d187416ef65b17597f9af759682deb576a28c25b32"
)
_W7AT_EVALUATION_DIGEST = (
    "b6ff73ac1b85344a5aa925506dba599bb9b3956abeb4eca0e6b0f9e63087b99c"
)
_CAP_EPSILON = 1.891576895118874e-08
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_RESOLUTIONS = (1, 2, 4)
_PRIMARY_ORDER = (1, 2, 4)
_REPEAT_ORDER = (4, 2, 1)
_COMPONENTS = ("s", "h", "technical_scalar")
_INTEGRATION_WITNESSES = (
    "substrate-bounds",
    "substrate-mass-conservation",
    "finite-state",
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
        "required_w7m_matrix_digest": _W7M_MATRIX_DIGEST,
        "required_w7y_plan_digest": _W7Y_PLAN_DIGEST,
        "required_w7at_evaluation_digest": _W7AT_EVALUATION_DIGEST,
        "cap_epsilon_provenance_only": _CAP_EPSILON,
        "model_id": "const-v",
        "equation_id": "baseline.k2-f3.const-v.v1",
        "equation_contract": "use=compute_mcm_f3_coupling;lambda_sm=V_initial",
        "parameter_bindings": (("eta", 1.0), ("kappa", 0.5), ("lambda_sm", 0.5)),
        "persistent_scalars_per_neuron": 1,
        "organism_runtime_allowed": False,
        "runtime_provider": "mcm_f3_runtime.advance_mcm_f3_shared_field_transient",
        "coupling_provider": "w7n.compute_w7n_coupling_baseline",
        "initialization_rule": "fresh-w7m-initial-field-with-const-v-arm-before-safe-step",
        "path_ids": _PATH_IDS,
        "checkpoint_count": 5,
        "resolutions": _RESOLUTIONS,
        "primary_order": _PRIMARY_ORDER,
        "exact_repeat_order": _REPEAT_ORDER,
        "response_per_second": 1.0,
        "afterimage_decay_per_second": 0.5,
        "dissipation_per_second": 0.0,
        "checkpoint_rule": "align-s-and-h-to-zero-on-full-state-probe-copy",
        "preserve_scalar_on_alignment": True,
        "probe_returns_to_main": False,
        "sampled_components": _COMPONENTS,
        "sample_boundary": "receptor-completion-and-final-boundaries",
        "trajectory_role_count_per_resolution": 35,
        "primary_trajectory_count": 105,
        "exact_repeat_trajectory_count": 105,
        "convergence_component_ids": ("s", "h"),
        "convergence_comparison_count": 70,
        "convergence_rule": "d24-less-than-d12-or-both-exact-zero-per-role-and-component",
        "const_v_epsilon_rule": "maximum-of-all-70-r2-r4-s-h-linf-distances",
        "common_epsilon_rule": "maximum-of-cap-epsilon-and-const-v-epsilon",
        "common_effect_floor_rule": "ten-times-common-epsilon",
        "integration_witnesses": _INTEGRATION_WITNESSES,
        "cap_capacity_ledger_allowed": False,
        "cap_target_capacity_role_allowed": False,
        "technical_scalar_is_memory": False,
        "accept_result_values": False,
        "execution_allowed": False,
        "profile_decision_allowed": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7BCConstVTrajectoryContract:
    """Immutable construction and convergence rules for a later consumer."""

    contract_id: str
    required_w7m_matrix_digest: str
    required_w7y_plan_digest: str
    required_w7at_evaluation_digest: str
    cap_epsilon_provenance_only: float
    model_id: str
    equation_id: str
    equation_contract: str
    parameter_bindings: tuple[tuple[str, float], ...]
    persistent_scalars_per_neuron: int
    organism_runtime_allowed: bool
    runtime_provider: str
    coupling_provider: str
    initialization_rule: str
    path_ids: tuple[str, ...]
    checkpoint_count: int
    resolutions: tuple[int, ...]
    primary_order: tuple[int, ...]
    exact_repeat_order: tuple[int, ...]
    response_per_second: float
    afterimage_decay_per_second: float
    dissipation_per_second: float
    checkpoint_rule: str
    preserve_scalar_on_alignment: bool
    probe_returns_to_main: bool
    sampled_components: tuple[str, ...]
    sample_boundary: str
    trajectory_role_count_per_resolution: int
    primary_trajectory_count: int
    exact_repeat_trajectory_count: int
    convergence_component_ids: tuple[str, ...]
    convergence_comparison_count: int
    convergence_rule: str
    const_v_epsilon_rule: str
    common_epsilon_rule: str
    common_effect_floor_rule: str
    integration_witnesses: tuple[str, ...]
    cap_capacity_ledger_allowed: bool
    cap_target_capacity_role_allowed: bool
    technical_scalar_is_memory: bool
    accept_result_values: bool
    execution_allowed: bool
    profile_decision_allowed: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    contract_digest: str

    def __post_init__(self) -> None:
        payload = _payload()
        observed = {key: getattr(self, key) for key in payload}
        if observed != payload or self.contract_digest != _digest(payload):
            raise W7BCConstVTrajectoryContractError(
                "W7-BC CONST-V trajectory contract differs"
            )


def build_w7bc_const_v_r124_trajectory_contract(
) -> W7BCConstVTrajectoryContract:
    """Build the preregistration without accepting data or advancing state."""

    payload = _payload()
    return W7BCConstVTrajectoryContract(
        *(payload[key] for key in payload),
        _digest(payload),
    )
