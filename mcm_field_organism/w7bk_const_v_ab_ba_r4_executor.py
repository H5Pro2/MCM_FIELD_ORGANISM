"""Private W7-BK executor for AB/BA R4 before convergence evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json

from .w7bd_const_v_runtime_adapter import W7BDConstVRuntimeAdapter
from .w7be_const_v_ab_r1_consumer import (
    W7BEConstVCheckpointMeasurement,
    W7BEConstVProduction,
    W7BEConstVState,
    _materialize_const_v_r1_path,
)
from .w7bh_const_v_r2_repeat_contract import W7BHConstVR2RepeatContract
from .w7bi_const_v_ab_ba_r2_executor import W7BIConstVABBAR2Result
from .w7bj_const_v_r4_convergence_contract import (
    W7BJConstVR4ConvergenceContract,
)
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamily,
)
from .w7y_seven_path_source_plan import W7YSevenPathSourcePlan


class W7BKConstVABBAR4ExecutorError(ValueError):
    """Raised when R4 execution leaves the W7-BJ boundary."""


_EXECUTOR_ID = "w7bk.const-v-ab-ba-r4-executor.v1"
_EXECUTION_ORDER = ("ab-r4-exact-repeat", "ba-r4-primary")
_OUTCOME = "R4_TECHNICAL_ROLES_COMPLETE"


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
    initial: W7BEConstVState,
    productions: tuple[W7BEConstVProduction, ...],
    measurements: tuple[W7BEConstVCheckpointMeasurement, ...],
    terminal: W7BEConstVState,
) -> str:
    return _digest(
        {
            "path_id": path_id,
            "refinement": 4,
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
class W7BKR4Role:
    """One R4 role, held as raw technical material for later comparison."""

    path_id: str
    r2_role_digest: str
    r4_role_digest: str
    r4_initial_state: W7BEConstVState = field(repr=False)
    r4_productions: tuple[W7BEConstVProduction, ...] = field(repr=False)
    r4_measurements: tuple[W7BEConstVCheckpointMeasurement, ...] = field(
        repr=False
    )
    r4_terminal_state: W7BEConstVState = field(repr=False)

    def __post_init__(self) -> None:
        productions = tuple(self.r4_productions)
        measurements = tuple(self.r4_measurements)
        if (
            self.path_id not in {"ab", "ba"}
            or not self.r2_role_digest
            or self.r4_initial_state.path_id != self.path_id
            or self.r4_initial_state.refinement != 4
            or self.r4_terminal_state.path_id != self.path_id
            or self.r4_terminal_state.refinement != 4
            or len(productions) != 5
            or len(measurements) != 5
            or any(len(item.samples) != 91 for item in measurements)
            or self.r4_role_digest
            != _role_digest(
                self.path_id,
                self.r4_initial_state,
                productions,
                measurements,
                self.r4_terminal_state,
            )
        ):
            raise W7BKConstVABBAR4ExecutorError("R4 role binding differs")
        object.__setattr__(self, "r4_productions", productions)
        object.__setattr__(self, "r4_measurements", measurements)


def _result_payload(
    contract_digest: str,
    plan_digest: str,
    adapter_digest: str,
    roles: tuple[W7BKR4Role, ...],
) -> dict[str, object]:
    return {
        "executor_id": _EXECUTOR_ID,
        "contract_digest": contract_digest,
        "plan_digest": plan_digest,
        "adapter_digest": adapter_digest,
        "execution_order": _EXECUTION_ORDER,
        "r2_role_digests": tuple(item.r2_role_digest for item in roles),
        "r4_role_digests": tuple(item.r4_role_digest for item in roles),
        "outcome": _OUTCOME,
        "convergence_evaluated": False,
        "epsilon_ready": False,
        "effect_floor_ready": False,
    }


@dataclass(frozen=True, slots=True)
class W7BKConstVABBAR4Result:
    """Terminal R4 technical handoff before separate convergence evaluation."""

    executor_id: str
    contract_digest: str
    plan_digest: str
    adapter_digest: str
    execution_order: tuple[str, ...]
    roles: tuple[W7BKR4Role, ...] = field(repr=False)
    outcome: str
    convergence_evaluated: bool
    epsilon_ready: bool
    effect_floor_ready: bool
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
            or self.convergence_evaluated is not False
            or self.epsilon_ready is not False
            or self.effect_floor_ready is not False
            or self.result_digest != _digest(payload)
        ):
            raise W7BKConstVABBAR4ExecutorError("R4 result binding differs")
        object.__setattr__(self, "roles", roles)


def execute_w7bk_const_v_ab_ba_r4(
    matrix: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    contract: W7BJConstVR4ConvergenceContract,
    bi_result: W7BIConstVABBAR2Result,
) -> W7BKConstVABBAR4Result:
    """Execute AB/R4 and BA/R4 without applying the convergence rule."""

    if (
        not isinstance(contract, W7BJConstVR4ConvergenceContract)
        or not isinstance(bi_result, W7BIConstVABBAR2Result)
        or contract.required_w7bi_result_digest != bi_result.result_digest
        or contract.required_w7bd_adapter_digest != runtime_adapter.adapter_digest
        or contract.required_w7y_plan_digest != plan.seven_path_plan_digest
        or contract.execution_roles != _EXECUTION_ORDER
        or contract.refinement != 4
    ):
        raise W7BKConstVABBAR4ExecutorError("W7-BJ bindings differ")
    r2_digests = tuple(item.r2_role_digest for item in bi_result.roles)
    roles = []
    for path_id, r2_digest in zip(("ab", "ba"), r2_digests, strict=True):
        path, initial, productions, measurements, terminal = (
            _materialize_const_v_r1_path(
                matrix,
                family,
                authorization,
                plan,
                runtime_adapter,
                path_id,
                refinement=4,
            )
        )
        del path
        roles.append(
            W7BKR4Role(
                path_id,
                r2_digest,
                _role_digest(path_id, initial, productions, measurements, terminal),
                initial,
                productions,
                measurements,
                terminal,
            )
        )
    roles_out = tuple(roles)
    payload = _result_payload(
        contract.contract_digest,
        plan.seven_path_plan_digest,
        runtime_adapter.adapter_digest,
        roles_out,
    )
    return W7BKConstVABBAR4Result(
        _EXECUTOR_ID,
        contract.contract_digest,
        plan.seven_path_plan_digest,
        runtime_adapter.adapter_digest,
        _EXECUTION_ORDER,
        roles_out,
        _OUTCOME,
        False,
        False,
        False,
        _digest(payload),
    )
