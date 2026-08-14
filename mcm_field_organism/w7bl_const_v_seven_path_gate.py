"""Static W7-BL gate for the missing CONST-V seven-path materialization."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .w7bj_const_v_r4_convergence_contract import (
    W7BJConstVR4ConvergenceContract,
)
from .w7y_seven_path_source_plan import W7YSevenPathSourcePlan


class W7BLConstVSevenPathGateError(ValueError):
    """Raised when the seven-path prerequisite is not preserved."""


_GATE_ID = "w7bl.const-v-seven-path-materialization-gate.v1"
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_RESOLUTIONS = (1, 2, 4)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _payload(
    contract_digest: str,
    plan_digest: str,
    path_ids: tuple[str, ...],
    resolutions: tuple[int, ...],
) -> dict[str, object]:
    return {
        "gate_id": _GATE_ID,
        "contract_digest": contract_digest,
        "plan_digest": plan_digest,
        "required_path_ids": path_ids,
        "required_resolutions": resolutions,
        "required_role_count": len(path_ids) * 5,
        "required_component_count": len(path_ids) * 5 * 2,
        "numeric_evaluation_allowed": False,
        "convergence_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7BLConstVSevenPathGate:
    """Immutable prerequisite before the registered 70 comparisons."""

    gate_id: str
    contract_digest: str
    plan_digest: str
    required_path_ids: tuple[str, ...]
    required_resolutions: tuple[int, ...]
    required_role_count: int
    required_component_count: int
    numeric_evaluation_allowed: bool
    convergence_decision_allowed: bool
    memory_claim_allowed: bool
    gate_digest: str

    def __post_init__(self) -> None:
        payload = _payload(
            self.contract_digest,
            self.plan_digest,
            tuple(self.required_path_ids),
            tuple(self.required_resolutions),
        )
        observed = {key: getattr(self, key) for key in payload}
        if observed != payload or self.gate_digest != _digest(payload):
            raise W7BLConstVSevenPathGateError("W7-BL gate binding differs")


def build_w7bl_const_v_seven_path_gate(
    plan: W7YSevenPathSourcePlan,
    contract: W7BJConstVR4ConvergenceContract,
) -> W7BLConstVSevenPathGate:
    """Register the missing seven-path prerequisite without executing it."""

    if (
        not isinstance(plan, W7YSevenPathSourcePlan)
        or not isinstance(contract, W7BJConstVR4ConvergenceContract)
    ):
        raise W7BLConstVSevenPathGateError("W7-BL seven-path binding differs")
    path_ids = tuple(item.path_id for item in plan.paths)
    resolutions = tuple(_RESOLUTIONS)
    if (
        path_ids != _PATH_IDS
        or contract.convergence_roles != 35
        or contract.convergence_comparison_count != 70
    ):
        raise W7BLConstVSevenPathGateError("W7-BL seven-path binding differs")
    payload = _payload(
        contract.contract_digest,
        plan.seven_path_plan_digest,
        path_ids,
        resolutions,
    )
    return W7BLConstVSevenPathGate(
        _GATE_ID,
        contract.contract_digest,
        plan.seven_path_plan_digest,
        path_ids,
        resolutions,
        35,
        70,
        False,
        False,
        False,
        _digest(payload),
    )
