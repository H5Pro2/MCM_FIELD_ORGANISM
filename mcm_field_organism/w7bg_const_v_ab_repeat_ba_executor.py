"""Private W7-BG executor for exact AB/R1 repeat followed by BA/R1."""

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
    consume_w7be_const_v_ab_r1,
)
from .w7bf_const_v_ba_r1_repeat_contract import (
    W7BFConstVBAR1RepeatContract,
)
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamily,
)
from .w7y_seven_path_source_plan import W7YSevenPathSourcePlan


class W7BGConstVABRepeatBAExecutorError(ValueError):
    """Raised when repeat gating or BA/R1 materialization differs."""


_EXECUTOR_ID = "w7bg.const-v-ab-repeat-ba-r1-executor.v1"
_OUTCOME = "TECHNICAL_TWO_ROLE_COMPLETE"
_EXECUTION_ORDER = ("ab-r1-exact-repeat", "ba-r1-primary")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _require_exact_ab_repeat(
    contract: W7BFConstVBAR1RepeatContract,
    repeat: W7BEConstVABR1Result,
) -> None:
    if (
        not isinstance(contract, W7BFConstVBAR1RepeatContract)
        or not isinstance(repeat, W7BEConstVABR1Result)
        or repeat.result_digest != contract.required_w7be_result_digest
        or repeat.path_id != "ab"
        or repeat.refinement != 1
        or len(repeat.main_productions) != 5
        or len(repeat.measurements) != 5
        or any(len(item.samples) != 91 for item in repeat.measurements)
    ):
        raise W7BGConstVABRepeatBAExecutorError(
            "AB/R1 repeat differs; BA/R1 remains stopped"
        )


def _result_payload(
    contract_digest: str,
    repeat_digest: str,
    plan_digest: str,
    runtime_adapter_digest: str,
    ba_path_plan_digest: str,
    ba_initial_state_digest: str,
    ba_productions: tuple[W7BEConstVProduction, ...],
    ba_measurements: tuple[W7BEConstVCheckpointMeasurement, ...],
    ba_terminal_state_digest: str,
) -> dict[str, object]:
    return {
        "executor_id": _EXECUTOR_ID,
        "contract_digest": contract_digest,
        "execution_order": _EXECUTION_ORDER,
        "repeat_passed": True,
        "ab_repeat_result_digest": repeat_digest,
        "plan_digest": plan_digest,
        "runtime_adapter_digest": runtime_adapter_digest,
        "ba_path_plan_digest": ba_path_plan_digest,
        "ba_initial_state_digest": ba_initial_state_digest,
        "ba_production_digests": tuple(
            item.production_digest for item in ba_productions
        ),
        "ba_measurement_digests": tuple(
            item.checkpoint_measurement_digest for item in ba_measurements
        ),
        "ba_terminal_state_digest": ba_terminal_state_digest,
        "outcome": _OUTCOME,
        "distance_evaluated": False,
        "epsilon_ready": False,
        "field_function_decision_ready": False,
    }


@dataclass(frozen=True, slots=True)
class W7BGConstVABRepeatBAResult:
    """Terminal technical handoff with no trajectory comparison."""

    executor_id: str
    contract_digest: str
    execution_order: tuple[str, ...]
    repeat_passed: bool
    ab_repeat: W7BEConstVABR1Result = field(repr=False)
    plan_digest: str
    runtime_adapter_digest: str
    ba_path_plan_digest: str
    ba_initial_state: W7BEConstVState = field(repr=False)
    ba_productions: tuple[W7BEConstVProduction, ...] = field(repr=False)
    ba_measurements: tuple[W7BEConstVCheckpointMeasurement, ...] = field(
        repr=False
    )
    ba_terminal_state: W7BEConstVState = field(repr=False)
    outcome: str
    distance_evaluated: bool
    epsilon_ready: bool
    field_function_decision_ready: bool
    result_digest: str

    def __post_init__(self) -> None:
        productions = tuple(self.ba_productions)
        measurements = tuple(self.ba_measurements)
        previous = self.ba_initial_state
        for production in productions:
            if production.initial_state is not previous:
                raise W7BGConstVABRepeatBAExecutorError(
                    "BA/R1 main chain is not contiguous"
                )
            previous = production.end_state
        payload = _result_payload(
            self.contract_digest,
            self.ab_repeat.result_digest,
            self.plan_digest,
            self.runtime_adapter_digest,
            self.ba_path_plan_digest,
            self.ba_initial_state.state_digest,
            productions,
            measurements,
            self.ba_terminal_state.state_digest,
        )
        if (
            self.executor_id != _EXECUTOR_ID
            or tuple(self.execution_order) != _EXECUTION_ORDER
            or self.repeat_passed is not True
            or self.ab_repeat.path_id != "ab"
            or len(productions) != 5
            or len(measurements) != 5
            or self.ba_initial_state.path_id != "ba"
            or self.ba_terminal_state.path_id != "ba"
            or previous is not self.ba_terminal_state
            or self.ba_terminal_state.tick != 8_000_000
            or tuple(item.checkpoint for item in measurements) != tuple(range(5))
            or any(len(item.samples) != 91 for item in measurements)
            or self.outcome != _OUTCOME
            or self.distance_evaluated is not False
            or self.epsilon_ready is not False
            or self.field_function_decision_ready is not False
            or self.result_digest != _digest(payload)
        ):
            raise W7BGConstVABRepeatBAExecutorError(
                "W7-BG terminal technical handoff differs"
            )
        object.__setattr__(self, "ba_productions", productions)
        object.__setattr__(self, "ba_measurements", measurements)


def execute_w7bg_const_v_ab_repeat_then_ba_r1(
    matrix: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    contract: W7BFConstVBAR1RepeatContract,
) -> W7BGConstVABRepeatBAResult:
    """Repeat canonical AB/R1 and run BA/R1 only after exact equality."""

    if (
        not isinstance(contract, W7BFConstVBAR1RepeatContract)
        or contract.required_w7bd_adapter_digest != runtime_adapter.adapter_digest
        or contract.required_w7y_plan_digest != plan.seven_path_plan_digest
        or contract.execution_roles != _EXECUTION_ORDER
    ):
        raise W7BGConstVABRepeatBAExecutorError(
            "W7-BG contract or runtime bindings differ"
        )
    repeat = consume_w7be_const_v_ab_r1(
        matrix,
        family,
        authorization,
        plan,
        runtime_adapter,
    )
    _require_exact_ab_repeat(contract, repeat)
    path, initial, productions, measurements, terminal = (
        _materialize_const_v_r1_path(
            matrix,
            family,
            authorization,
            plan,
            runtime_adapter,
            "ba",
        )
    )
    if (
        path.prefix is None
        or path.prefix.source_role != contract.ba_prefix_role
        or tuple(
            item.source_role.rsplit(".", 1)[0]
            for item in path.continuations
        )
        != (contract.ba_continuation_role,) * 4
    ):
        raise W7BGConstVABRepeatBAExecutorError(
            "BA/R1 source roles differ from W7-BF"
        )
    payload = _result_payload(
        contract.contract_digest,
        repeat.result_digest,
        plan.seven_path_plan_digest,
        runtime_adapter.adapter_digest,
        path.path_plan_digest,
        initial.state_digest,
        productions,
        measurements,
        terminal.state_digest,
    )
    return W7BGConstVABRepeatBAResult(
        _EXECUTOR_ID,
        contract.contract_digest,
        _EXECUTION_ORDER,
        True,
        repeat,
        plan.seven_path_plan_digest,
        runtime_adapter.adapter_digest,
        path.path_plan_digest,
        initial,
        productions,
        measurements,
        terminal,
        _OUTCOME,
        False,
        False,
        False,
        _digest(payload),
    )
