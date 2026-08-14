"""Private single-role CONST-V shard executor for W7-BM."""

from __future__ import annotations

from dataclasses import dataclass
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
from .w7bm_const_v_seven_path_executor import (
    W7BMConstVSevenPathExecutorError,
    W7BMConstVSevenPathRole,
)
from .w7bj_const_v_r4_convergence_contract import W7BJConstVR4ConvergenceContract
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7w_symmetric_source_family import W7WSourceAuthorization, W7WSymmetricSourceFamily
from .w7y_seven_path_source_plan import W7YSevenPathSourcePlan


class W7BNConstVShardExecutorError(ValueError):
    """Raised when one shard leaves the registered W7-BL boundary."""


_EXECUTOR_ID = "w7bn.const-v-single-role-shard-executor.v1"
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_REFINEMENTS = (1, 2, 4)


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class W7BNConstVShard:
    executor_id: str
    path_id: str
    refinement: int
    role: W7BMConstVSevenPathRole
    shard_digest: str

    def __post_init__(self) -> None:
        payload = {
            "executor_id": _EXECUTOR_ID,
            "path_id": self.path_id,
            "refinement": self.refinement,
            "role_digest": self.role.role_digest,
        }
        if (
            self.executor_id != _EXECUTOR_ID
            or self.path_id not in _PATH_IDS
            or self.refinement not in _REFINEMENTS
            or self.role.path_id != self.path_id
            or self.role.refinement != self.refinement
            or self.shard_digest != _digest(payload)
        ):
            raise W7BNConstVShardExecutorError("CONST-V shard binding differs")


def execute_w7bn_const_v_role_shard(
    matrix: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    contract: W7BJConstVR4ConvergenceContract,
    gate: W7BLConstVSevenPathGate,
    path_id: str,
    refinement: int,
) -> W7BNConstVShard:
    """Materialize exactly one private path/refinement role."""

    if (
        not isinstance(gate, W7BLConstVSevenPathGate)
        or not isinstance(contract, W7BJConstVR4ConvergenceContract)
        or gate.contract_digest != contract.contract_digest
        or gate.plan_digest != plan.seven_path_plan_digest
        or path_id not in _PATH_IDS
        or refinement not in _REFINEMENTS
    ):
        raise W7BNConstVShardExecutorError("W7-BL shard bindings differ")
    try:
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
        role_payload = {
            "path_id": path_id,
            "refinement": refinement,
            "initial_state_digest": initial.state_digest,
            "production_digests": tuple(item.production_digest for item in productions),
            "measurement_digests": tuple(item.checkpoint_measurement_digest for item in measurements),
            "terminal_state_digest": terminal.state_digest,
        }
        role = W7BMConstVSevenPathRole(
            path_id,
            refinement,
            initial,
            productions,
            measurements,
            terminal,
            _digest(role_payload),
        )
    except Exception as exc:
        if isinstance(exc, W7BMConstVSevenPathExecutorError):
            raise
        raise W7BNConstVShardExecutorError("CONST-V shard materialization failed") from exc
    payload = {
        "executor_id": _EXECUTOR_ID,
        "path_id": path_id,
        "refinement": refinement,
        "role_digest": role.role_digest,
    }
    return W7BNConstVShard(_EXECUTOR_ID, path_id, refinement, role, _digest(payload))
