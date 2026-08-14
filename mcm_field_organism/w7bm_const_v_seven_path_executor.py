"""Private CONST-V seven-path materializer for W7-BL."""

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
from .w7bl_const_v_seven_path_gate import W7BLConstVSevenPathGate
from .w7bj_const_v_r4_convergence_contract import W7BJConstVR4ConvergenceContract
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamily,
)
from .w7y_seven_path_source_plan import W7YSevenPathSourcePlan


class W7BMConstVSevenPathExecutorError(ValueError):
    """Raised when the private seven-path boundary is violated."""


_EXECUTOR_ID = "w7bm.const-v-seven-path-r124-executor.v1"
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_REFINEMENTS = (1, 2, 4)


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class W7BMConstVSevenPathRole:
    path_id: str
    refinement: int
    initial_state: W7BEConstVState = field(repr=False)
    productions: tuple[W7BEConstVProduction, ...] = field(repr=False)
    measurements: tuple[W7BEConstVCheckpointMeasurement, ...] = field(repr=False)
    terminal_state: W7BEConstVState = field(repr=False)
    role_digest: str

    def __post_init__(self) -> None:
        productions = tuple(self.productions)
        measurements = tuple(self.measurements)
        expected_productions = 4 if self.path_id.startswith("u") else 5
        payload = {
            "path_id": self.path_id,
            "refinement": self.refinement,
            "initial_state_digest": self.initial_state.state_digest,
            "production_digests": tuple(item.production_digest for item in productions),
            "measurement_digests": tuple(item.checkpoint_measurement_digest for item in measurements),
            "terminal_state_digest": self.terminal_state.state_digest,
        }
        if (
            self.path_id not in _PATH_IDS
            or self.refinement not in _REFINEMENTS
            or self.initial_state.path_id != self.path_id
            or self.initial_state.refinement != self.refinement
            or self.terminal_state.path_id != self.path_id
            or self.terminal_state.refinement != self.refinement
            or len(productions) != expected_productions
            or len(measurements) != 5
            or any(len(item.samples) != 91 for item in measurements)
            or self.role_digest != _digest(payload)
        ):
            raise W7BMConstVSevenPathExecutorError("seven-path role binding differs")
        object.__setattr__(self, "productions", productions)
        object.__setattr__(self, "measurements", measurements)


@dataclass(frozen=True, slots=True)
class W7BMConstVSevenPathResult:
    executor_id: str
    gate_digest: str
    contract_digest: str
    plan_digest: str
    roles: tuple[W7BMConstVSevenPathRole, ...] = field(repr=False)
    numeric_evaluation_allowed: bool
    convergence_decision_allowed: bool
    memory_claim_allowed: bool
    result_digest: str

    def __post_init__(self) -> None:
        roles = tuple(self.roles)
        payload = {
            "executor_id": _EXECUTOR_ID,
            "gate_digest": self.gate_digest,
            "contract_digest": self.contract_digest,
            "plan_digest": self.plan_digest,
            "role_digests": tuple(item.role_digest for item in roles),
            "numeric_evaluation_allowed": False,
            "convergence_decision_allowed": False,
            "memory_claim_allowed": False,
        }
        if (
            self.executor_id != _EXECUTOR_ID
            or tuple((item.path_id, item.refinement) for item in roles)
            != tuple((path_id, refinement) for refinement in _REFINEMENTS for path_id in _PATH_IDS)
            or self.numeric_evaluation_allowed
            or self.convergence_decision_allowed
            or self.memory_claim_allowed
            or self.result_digest != _digest(payload)
        ):
            raise W7BMConstVSevenPathExecutorError("seven-path result binding differs")
        object.__setattr__(self, "roles", roles)


def execute_w7bm_const_v_seven_path_r124(
    matrix: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    contract: W7BJConstVR4ConvergenceContract,
    gate: W7BLConstVSevenPathGate,
) -> W7BMConstVSevenPathResult:
    """Materialize all seven paths at R1/R2/R4 without numerical evaluation."""

    if (
        not isinstance(gate, W7BLConstVSevenPathGate)
        or not isinstance(contract, W7BJConstVR4ConvergenceContract)
        or gate.contract_digest != contract.contract_digest
        or gate.plan_digest != plan.seven_path_plan_digest
        or gate.numeric_evaluation_allowed
        or gate.convergence_decision_allowed
        or gate.memory_claim_allowed
    ):
        raise W7BMConstVSevenPathExecutorError("W7-BL gate binding differs")
    roles = []
    for refinement in _REFINEMENTS:
        for path_id in _PATH_IDS:
            path, initial, productions, measurements, terminal = _materialize_const_v_r1_path(
                matrix,
                family,
                authorization,
                plan,
                runtime_adapter,
                path_id,
                refinement=refinement,
            )
            del path
            payload = {
                "path_id": path_id,
                "refinement": refinement,
                "initial_state_digest": initial.state_digest,
                "production_digests": tuple(item.production_digest for item in productions),
                "measurement_digests": tuple(item.checkpoint_measurement_digest for item in measurements),
                "terminal_state_digest": terminal.state_digest,
            }
            roles.append(
                W7BMConstVSevenPathRole(
                    path_id,
                    refinement,
                    initial,
                    productions,
                    measurements,
                    terminal,
                    _digest(payload),
                )
            )
    roles_out = tuple(roles)
    payload = {
        "executor_id": _EXECUTOR_ID,
        "gate_digest": gate.gate_digest,
        "contract_digest": contract.contract_digest,
        "plan_digest": plan.seven_path_plan_digest,
        "role_digests": tuple(item.role_digest for item in roles_out),
        "numeric_evaluation_allowed": False,
        "convergence_decision_allowed": False,
        "memory_claim_allowed": False,
    }
    return W7BMConstVSevenPathResult(
        _EXECUTOR_ID,
        gate.gate_digest,
        contract.contract_digest,
        plan.seven_path_plan_digest,
        roles_out,
        False,
        False,
        False,
        _digest(payload),
    )
