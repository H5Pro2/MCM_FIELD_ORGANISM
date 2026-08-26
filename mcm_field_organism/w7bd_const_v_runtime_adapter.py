"""Private W7-BD state and runtime adapter for the CONST-V baseline."""

from __future__ import annotations

import copy
from dataclasses import dataclass, replace
import hashlib
import json

from .mcm_f3_runtime import (
    MCMF3AdvanceResult,
    advance_mcm_f3_shared_field_transient,
)
from .mcm_substrate_state import MCMSubstrateArmContract
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField
from .transient_neuron_input import TransientNeuronInputSet
from .w7bc_const_v_r124_trajectory_contract import (
    W7BCConstVTrajectoryContract,
)
from .w7m_capacity_function_matrix import (
    W7MBaselineSpec,
    W7MCapacityFunctionMatrixAdapter,
)
from .w7n_capacity_function_baselines import compute_w7n_coupling_baseline


class W7BDConstVRuntimeAdapterError(ValueError):
    """Raised when CONST-V state or runtime wiring leaves W7-BC."""


_ADAPTER_ID = "w7bd.const-v-state-runtime-adapter.v1"
_ARM_ID = "w7n.const-v"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _const_v_spec(
    matrix: W7MCapacityFunctionMatrixAdapter,
) -> W7MBaselineSpec:
    matches = tuple(item for item in matrix.baselines if item.model_id == "const-v")
    if len(matches) != 1:
        raise W7BDConstVRuntimeAdapterError(
            "W7-BD requires exactly one CONST-V baseline specification"
        )
    return matches[0]


def _adapter_payload(
    matrix_digest: str,
    contract_digest: str,
    spec: W7MBaselineSpec,
) -> dict[str, object]:
    return {
        "adapter_id": _ADAPTER_ID,
        "matrix_digest": matrix_digest,
        "trajectory_contract_digest": contract_digest,
        "model_id": spec.model_id,
        "equation_id": spec.equation_id,
        "equation_contract": spec.equation_contract,
        "parameter_bindings": spec.parameter_bindings,
        "arm_id": _ARM_ID,
        "response_time_seconds": 1.0,
        "afterimage_time_seconds": 0.5,
        "dissipation_per_second": 0.0,
        "runtime_provider": "mcm_f3_runtime.advance_mcm_f3_shared_field_transient",
        "coupling_provider": "w7n.compute_w7n_coupling_baseline",
        "state_observer_policy": "read-only-copies-and-no-return",
        "public_export_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7BDConstVRuntimeAdapter:
    """Frozen private wiring; it stores no trajectory and no result."""

    adapter_id: str
    matrix_digest: str
    trajectory_contract_digest: str
    baseline_spec: W7MBaselineSpec
    arm_id: str
    substrate_config: NeutralLocalFieldSubstrateConfig
    afterimage_config: NeutralFastAfterimageConfig
    dissipation_per_second: float
    runtime_provider: str
    coupling_provider: str
    state_observer_policy: str
    public_export_allowed: bool
    adapter_digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.baseline_spec, W7MBaselineSpec):
            raise W7BDConstVRuntimeAdapterError(
                "W7-BD adapter requires one frozen baseline specification"
            )
        payload = _adapter_payload(
            self.matrix_digest,
            self.trajectory_contract_digest,
            self.baseline_spec,
        )
        if (
            self.adapter_id != _ADAPTER_ID
            or self.arm_id != _ARM_ID
            or self.substrate_config != NeutralLocalFieldSubstrateConfig(1.0)
            or self.afterimage_config != NeutralFastAfterimageConfig(0.5)
            or self.dissipation_per_second != 0.0
            or self.runtime_provider
            != "mcm_f3_runtime.advance_mcm_f3_shared_field_transient"
            or self.coupling_provider != "w7n.compute_w7n_coupling_baseline"
            or self.state_observer_policy != "read-only-copies-and-no-return"
            or self.public_export_allowed is not False
            or self.adapter_digest != _digest(payload)
        ):
            raise W7BDConstVRuntimeAdapterError("W7-BD adapter differs")


def build_w7bd_const_v_runtime_adapter(
    matrix: W7MCapacityFunctionMatrixAdapter,
    contract: W7BCConstVTrajectoryContract,
) -> W7BDConstVRuntimeAdapter:
    """Bind the canonical CONST-V spec without constructing trajectories."""

    if not isinstance(matrix, W7MCapacityFunctionMatrixAdapter) or not isinstance(
        contract,
        W7BCConstVTrajectoryContract,
    ):
        raise W7BDConstVRuntimeAdapterError(
            "W7-BD requires the W7-M matrix and W7-BC contract"
        )
    if (
        matrix.matrix_digest != contract.required_w7m_matrix_digest
        or contract.model_id != "const-v"
    ):
        raise W7BDConstVRuntimeAdapterError(
            "W7-BD matrix or model differs from W7-BC"
        )
    spec = _const_v_spec(matrix)
    if (
        spec.equation_id != contract.equation_id
        or spec.equation_contract != contract.equation_contract
        or spec.parameter_bindings != contract.parameter_bindings
        or spec.persistent_scalars_per_neuron
        != contract.persistent_scalars_per_neuron
        or spec.organism_runtime_allowed is not False
    ):
        raise W7BDConstVRuntimeAdapterError(
            "canonical CONST-V specification differs from W7-BC"
        )
    payload = _adapter_payload(matrix.matrix_digest, contract.contract_digest, spec)
    return W7BDConstVRuntimeAdapter(
        _ADAPTER_ID,
        matrix.matrix_digest,
        contract.contract_digest,
        spec,
        _ARM_ID,
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
        0.0,
        "mcm_f3_runtime.advance_mcm_f3_shared_field_transient",
        "w7n.compute_w7n_coupling_baseline",
        "read-only-copies-and-no-return",
        False,
        _digest(payload),
    )


def prepare_w7bd_const_v_initial_field(
    matrix: W7MCapacityFunctionMatrixAdapter,
    adapter: W7BDConstVRuntimeAdapter,
) -> SharedMCMField:
    """Create one fresh initial field whose safe-step sees the CONST-V arm."""

    if (
        not isinstance(matrix, W7MCapacityFunctionMatrixAdapter)
        or not isinstance(adapter, W7BDConstVRuntimeAdapter)
        or matrix.matrix_digest != adapter.matrix_digest
    ):
        raise W7BDConstVRuntimeAdapterError(
            "W7-BD initial state requires its bound matrix and adapter"
        )
    current = copy.deepcopy(matrix.initial_field)
    if current.last_distribution is not None or current.substrate is None:
        raise W7BDConstVRuntimeAdapterError(
            "W7-BD requires one fresh substrate field"
        )
    parameters = dict(adapter.baseline_spec.parameter_bindings)
    arm = MCMSubstrateArmContract(
        adapter.arm_id,
        parameters["lambda_sm"],
        parameters["kappa"],
        parameters["eta"],
        current.substrate.arm.initial_total_mass,
    )
    return replace(current, substrate=replace(current.substrate, arm=arm))


def _validate_const_v_field(
    adapter: W7BDConstVRuntimeAdapter,
    field: SharedMCMField,
) -> None:
    if not isinstance(adapter, W7BDConstVRuntimeAdapter):
        raise W7BDConstVRuntimeAdapterError("invalid W7-BD runtime adapter")
    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise W7BDConstVRuntimeAdapterError(
            "CONST-V runtime requires one substrate field"
        )
    parameters = dict(adapter.baseline_spec.parameter_bindings)
    arm = field.substrate.arm
    if (
        arm.arm_id != adapter.arm_id
        or arm.lambda_sm_per_second != parameters["lambda_sm"]
        or arm.kappa != parameters["kappa"]
        or arm.eta != parameters["eta"]
    ):
        raise W7BDConstVRuntimeAdapterError(
            "field does not carry the frozen CONST-V arm"
        )


def advance_w7bd_const_v_transient(
    adapter: W7BDConstVRuntimeAdapter,
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    *,
    refinement: int,
    _state_observer=None,
) -> MCMF3AdvanceResult:
    """Delegate one transient interval to SSPRK33 with CONST-V coupling."""

    _validate_const_v_field(adapter, field)

    def coupling(layer, substrate):
        return compute_w7n_coupling_baseline(
            adapter.baseline_spec,
            layer,
            substrate,
        )

    state_observer = None
    if _state_observer is not None:
        if not callable(_state_observer):
            raise W7BDConstVRuntimeAdapterError(
                "CONST-V state observer must be callable"
            )

        def state_observer(tick, activation, afterimage, scalar):
            activation.setflags(write=False)
            afterimage.setflags(write=False)
            scalar.setflags(write=False)
            if _state_observer(tick, activation, afterimage, scalar) is not None:
                raise W7BDConstVRuntimeAdapterError(
                    "CONST-V state observer must not return state"
                )

    return advance_mcm_f3_shared_field_transient(
        field,
        distribution,
        transient_inputs,
        adapter.substrate_config,
        adapter.afterimage_config,
        None,
        refinement=refinement,
        _coupling_calculator=coupling,
        _state_observer=state_observer,
    )
