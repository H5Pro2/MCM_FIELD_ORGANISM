"""Private W7-BI executor for AB/BA R2 and raw D12 preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json

from .w7bd_const_v_runtime_adapter import W7BDConstVRuntimeAdapter
from .w7be_const_v_ab_r1_consumer import (
    W7BEConstVABR1Result,
    W7BEConstVCheckpointMeasurement,
    W7BEConstVProduction,
    W7BEConstVState,
    _materialize_const_v_r1_path,
)
from .w7bg_const_v_ab_repeat_ba_executor import W7BGConstVABRepeatBAResult
from .w7bh_const_v_r2_repeat_contract import W7BHConstVR2RepeatContract
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamily,
)
from .w7y_seven_path_source_plan import W7YSevenPathSourcePlan


class W7BIConstVABBAR2ExecutorError(ValueError):
    """Raised when R2 execution or raw D12 preparation leaves W7-BH."""


_EXECUTOR_ID = "w7bi.const-v-ab-ba-r2-d12-preparation.v1"
_EXECUTION_ORDER = ("ab-r2-exact-repeat", "ba-r2-primary")
_OUTCOME = "RAW_D12_PREPARED"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _role_digest(
    path_id: str,
    refinement: int,
    initial: W7BEConstVState,
    productions: tuple[W7BEConstVProduction, ...],
    measurements: tuple[W7BEConstVCheckpointMeasurement, ...],
    terminal: W7BEConstVState,
) -> str:
    return _digest(
        {
            "path_id": path_id,
            "refinement": refinement,
            "initial_state_digest": initial.state_digest,
            "production_digests": tuple(
                item.production_digest for item in productions
            ),
            "measurement_digests": tuple(
                item.checkpoint_measurement_digest for item in measurements
            ),
            "terminal_state_digest": terminal.state_digest,
        }
    )


@dataclass(frozen=True, slots=True)
class W7BIRawD12Role:
    """One role's raw R1/R2 identity pair without a distance value."""

    path_id: str
    r1_role_digest: str
    r2_role_digest: str
    r2_initial_state: W7BEConstVState = field(repr=False)
    r2_productions: tuple[W7BEConstVProduction, ...] = field(repr=False)
    r2_measurements: tuple[W7BEConstVCheckpointMeasurement, ...] = field(
        repr=False
    )
    r2_terminal_state: W7BEConstVState = field(repr=False)
    raw_d12_digest: str

    def __post_init__(self) -> None:
        productions = tuple(self.r2_productions)
        measurements = tuple(self.r2_measurements)
        payload = {
            "path_id": self.path_id,
            "r1_role_digest": self.r1_role_digest,
            "r2_role_digest": self.r2_role_digest,
            "r2_initial_state_digest": self.r2_initial_state.state_digest,
            "r2_production_digests": tuple(
                item.production_digest for item in productions
            ),
            "r2_measurement_digests": tuple(
                item.checkpoint_measurement_digest for item in measurements
            ),
            "r2_terminal_state_digest": self.r2_terminal_state.state_digest,
            "distance_value": None,
        }
        if (
            self.path_id not in {"ab", "ba"}
            or not self.r1_role_digest
            or not self.r2_role_digest
            or self.r2_initial_state.path_id != self.path_id
            or self.r2_initial_state.refinement != 2
            or len(productions) != 5
            or len(measurements) != 5
            or self.r2_terminal_state.path_id != self.path_id
            or self.r2_terminal_state.refinement != 2
            or self.raw_d12_digest != _digest(payload)
        ):
            raise W7BIConstVABBAR2ExecutorError("raw D12 role binding differs")
        object.__setattr__(self, "r2_productions", productions)
        object.__setattr__(self, "r2_measurements", measurements)


def _result_payload(
    contract_digest: str,
    plan_digest: str,
    adapter_digest: str,
    roles: tuple[W7BIRawD12Role, ...],
) -> dict[str, object]:
    return {
        "executor_id": _EXECUTOR_ID,
        "contract_digest": contract_digest,
        "plan_digest": plan_digest,
        "adapter_digest": adapter_digest,
        "execution_order": _EXECUTION_ORDER,
        "role_digests": tuple(item.raw_d12_digest for item in roles),
        "outcome": _OUTCOME,
        "distance_values": None,
        "epsilon_ready": False,
        "effect_floor_ready": False,
        "profile_ready": False,
    }


@dataclass(frozen=True, slots=True)
class W7BIConstVABBAR2Result:
    """Terminal raw D12 handoff with no distance or convergence decision."""

    executor_id: str
    contract_digest: str
    plan_digest: str
    adapter_digest: str
    execution_order: tuple[str, ...]
    roles: tuple[W7BIRawD12Role, ...] = field(repr=False)
    outcome: str
    distance_values: None
    epsilon_ready: bool
    effect_floor_ready: bool
    profile_ready: bool
    result_digest: str

    def __post_init__(self) -> None:
        roles = tuple(self.roles)
        payload = _result_payload(
            self.contract_digest,
            self.plan_digest,
            self.adapter_digest,
            roles,
        )
        if (
            self.executor_id != _EXECUTOR_ID
            or tuple(self.execution_order) != _EXECUTION_ORDER
            or tuple(item.path_id for item in roles) != ("ab", "ba")
            or self.outcome != _OUTCOME
            or self.distance_values is not None
            or self.epsilon_ready is not False
            or self.effect_floor_ready is not False
            or self.profile_ready is not False
            or self.result_digest != _digest(payload)
        ):
            raise W7BIConstVABBAR2ExecutorError("W7-BI result binding differs")
        object.__setattr__(self, "roles", roles)


def _validate_contract_bindings(
    contract: W7BHConstVR2RepeatContract,
    bg_result: W7BGConstVABRepeatBAResult,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    plan: W7YSevenPathSourcePlan,
) -> None:
    if (
        not isinstance(contract, W7BHConstVR2RepeatContract)
        or not isinstance(bg_result, W7BGConstVABRepeatBAResult)
        or contract.required_w7bg_result_digest != bg_result.result_digest
        or contract.required_w7bd_adapter_digest != runtime_adapter.adapter_digest
        or contract.required_w7y_plan_digest != plan.seven_path_plan_digest
        or contract.execution_roles != _EXECUTION_ORDER
        or contract.refinement != 2
        or not contract.raw_d12_preparation_allowed
    ):
        raise W7BIConstVABBAR2ExecutorError("W7-BH bindings differ")


def execute_w7bi_const_v_ab_ba_r2(
    matrix: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    contract: W7BHConstVR2RepeatContract,
    bg_result: W7BGConstVABRepeatBAResult,
) -> W7BIConstVABBAR2Result:
    """Execute AB/R2 then BA/R2 and prepare raw role-local D12 identities."""

    _validate_contract_bindings(contract, bg_result, runtime_adapter, plan)
    roles = []
    for path_id, r1_role_digest in (
        ("ab", bg_result.ab_repeat.result_digest),
        (
            "ba",
            _role_digest(
                "ba",
                1,
                bg_result.ba_initial_state,
                bg_result.ba_productions,
                bg_result.ba_measurements,
                bg_result.ba_terminal_state,
            ),
        ),
    ):
        path, initial, productions, measurements, terminal = (
            _materialize_const_v_r1_path(
                matrix,
                family,
                authorization,
                plan,
                runtime_adapter,
                path_id,
                refinement=2,
            )
        )
        r2_digest = _role_digest(
            path_id,
            2,
            initial,
            productions,
            measurements,
            terminal,
        )
        raw_payload = {
            "path_id": path_id,
            "r1_role_digest": r1_role_digest,
            "r2_role_digest": r2_digest,
            "r2_initial_state_digest": initial.state_digest,
            "r2_production_digests": tuple(
                item.production_digest for item in productions
            ),
            "r2_measurement_digests": tuple(
                item.checkpoint_measurement_digest for item in measurements
            ),
            "r2_terminal_state_digest": terminal.state_digest,
            "distance_value": None,
        }
        roles.append(
            W7BIRawD12Role(
                path_id,
                r1_role_digest,
                r2_digest,
                initial,
                productions,
                measurements,
                terminal,
                _digest(raw_payload),
            )
        )
    roles_out = tuple(roles)
    payload = _result_payload(
        contract.contract_digest,
        plan.seven_path_plan_digest,
        runtime_adapter.adapter_digest,
        roles_out,
    )
    return W7BIConstVABBAR2Result(
        _EXECUTOR_ID,
        contract.contract_digest,
        plan.seven_path_plan_digest,
        runtime_adapter.adapter_digest,
        _EXECUTION_ORDER,
        roles_out,
        _OUTCOME,
        None,
        False,
        False,
        False,
        _digest(payload),
    )
