"""Private S1-EC11 temporary lifecycle for the small real formation matrix."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .e1_confirmation_prepared_execution_bundle import (
    E1PreparedExecutionBundle,
    E1PreparedRuntimeInput,
    E1PreparedSyntheticReceipt,
    execute_prepared_bundle_synthetically,
    prepare_e1_confirmation_execution_bundle_from_run_contract,
)
from .e1_confirmation_research_corridor import (
    E1ConfirmationSyntheticRunContract,
    S1_EC3_RUN_ID,
)
from .e1_confirmation_small_five_arm_formation import (
    E1SmallFiveArmFormationResult,
    run_small_five_arm_formation_in_memory,
)
from .e1_confirmation_small_refinement_matrix import (
    S1_EC10_REFINEMENTS,
)
from .e1_frozen_state_transfer_contract import _probe_digest
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest
from .field_step_time import MCMFieldStepTime
from .shared_mcm_field import SharedMCMField


class E1ConfirmationSmallRealLifecycleError(ValueError):
    """Raised when the S1-EC11 temporary real lifecycle fails closed."""


S1_EC11_INPUT_ROLES = (
    "history_ab",
    "history_ba",
    "r2_steps",
    "r4_steps",
    "r8_steps",
    "initial_field",
    "initial_state",
)
S1_EC11_STEP_COUNTS = (("r2", 4), ("r4", 8), ("r8", 16))


def _steps_digest(steps: tuple[MCMFieldStepTime, ...]) -> str:
    return _digest(tuple(asdict(item) for item in steps))


@dataclass(frozen=True, slots=True)
class E1SmallRealLifecyclePreparedInputs:
    history_ab: tuple[Any, ...]
    history_ba: tuple[Any, ...]
    refinement_steps: tuple[tuple[str, tuple[MCMFieldStepTime, ...]], ...]
    initial_field: SharedMCMField
    initial_state: E1LocalEdgePlasticityState

    def __post_init__(self) -> None:
        history_ab = tuple(self.history_ab)
        history_ba = tuple(self.history_ba)
        refinement_steps = tuple(
            (name, tuple(steps)) for name, steps in self.refinement_steps
        )
        histories = history_ab + history_ba
        clock_ids = {item.clock_id for item in histories}
        expected_ids = tuple(name for name, _ in S1_EC10_REFINEMENTS)
        if (
            not history_ab
            or not history_ba
            or len(clock_ids) != 1
            or tuple(name for name, _ in refinement_steps) != expected_ids
            or tuple((name, len(steps)) for name, steps in refinement_steps)
            != S1_EC11_STEP_COUNTS
            or any(
                not isinstance(step, MCMFieldStepTime)
                or step.clock_id not in clock_ids
                for _, steps in refinement_steps
                for step in steps
            )
            or not isinstance(self.initial_field, SharedMCMField)
            or not isinstance(self.initial_state, E1LocalEdgePlasticityState)
        ):
            raise E1ConfirmationSmallRealLifecycleError(
                "S1-EC11 prepared small real inputs changed"
            )
        object.__setattr__(self, "history_ab", history_ab)
        object.__setattr__(self, "history_ba", history_ba)
        object.__setattr__(self, "refinement_steps", refinement_steps)


def prepare_small_real_formation_bundle_from_run_contract(
    run_contract: E1ConfirmationSyntheticRunContract,
    values: E1SmallRealLifecyclePreparedInputs,
) -> E1PreparedExecutionBundle:
    """Bind every small real formation input before Lock and Attempt."""

    if not isinstance(values, E1SmallRealLifecyclePreparedInputs):
        raise E1ConfirmationSmallRealLifecycleError(
            "S1-EC11 requires prepared small real inputs"
        )
    values.__post_init__()
    steps = dict(values.refinement_steps)
    bindings = (
        ("history_ab", values.history_ab, _probe_digest),
        ("history_ba", values.history_ba, _probe_digest),
        ("r2_steps", steps["r2"], _steps_digest),
        ("r4_steps", steps["r4"], _steps_digest),
        ("r8_steps", steps["r8"], _steps_digest),
        ("initial_field", values.initial_field, _initial_field_digest),
        ("initial_state", values.initial_state, _initial_state_digest),
    )
    prepared = tuple(
        E1PreparedRuntimeInput(role, value, reader(value), reader)
        for role, value, reader in bindings
    )
    return prepare_e1_confirmation_execution_bundle_from_run_contract(
        run_contract,
        lambda: prepared,
    )


@dataclass(frozen=True, slots=True)
class E1PreparedSmallRealFormationResult:
    execution_id: str
    run_contract_digest: str
    bundle_digest: str
    refinements: tuple[E1SmallFiveArmFormationResult, ...]
    step_counts: tuple[tuple[str, int], ...]
    attempt_present_during_execution: bool
    all_five_arm_controls_passed: bool
    prepared_inputs_preserved: bool
    real_field_kernels_executed: bool
    synthetic_lifecycle_only: bool
    canonical_execution_permitted: bool
    probe_execution_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        refinements = tuple(self.refinements)
        if (
            self.execution_id != S1_EC3_RUN_ID
            or len(self.run_contract_digest) != 64
            or len(self.bundle_digest) != 64
            or tuple(item.refinement_id for item in refinements)
            != tuple(name for name, _ in S1_EC10_REFINEMENTS)
            or self.step_counts != S1_EC11_STEP_COUNTS
            or self.attempt_present_during_execution is not True
            or self.all_five_arm_controls_passed is not True
            or self.prepared_inputs_preserved is not True
            or self.real_field_kernels_executed is not True
            or self.synthetic_lifecycle_only is not True
            or self.canonical_execution_permitted is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationSmallRealLifecycleError(
                "S1-EC11 prepared real formation result changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"refinements", "result_digest"}
        }
        payload["refinement_result_digests"] = tuple(
            item.result_digest for item in refinements
        )
        if self.result_digest != _digest(payload):
            raise E1ConfirmationSmallRealLifecycleError(
                "S1-EC11 result digest does not match its payload"
            )
        object.__setattr__(self, "refinements", refinements)


def consume_prepared_small_real_formation(
    bundle: E1PreparedExecutionBundle,
) -> E1PreparedSmallRealFormationResult:
    """Execute only the already bound small real inputs after Attempt."""

    if (
        not isinstance(bundle, E1PreparedExecutionBundle)
        or tuple(role for role, _ in bundle.input_manifest) != S1_EC11_INPUT_ROLES
    ):
        raise E1ConfirmationSmallRealLifecycleError(
            "S1-EC11 requires its complete ordered prepared manifest"
        )
    attempt_present = Path(bundle.attempt_path).is_file()
    histories = (bundle.value("history_ab"), bundle.value("history_ba"))
    field = bundle.value("initial_field")
    state = bundle.value("initial_state")
    refinements = tuple(
        run_small_five_arm_formation_in_memory(
            refinement_id,
            histories[0],
            histories[1],
            bundle.value(f"{refinement_id}_steps"),
            bundle.value(f"{refinement_id}_steps"),
            field,
            state,
        )
        for refinement_id, _ in S1_EC10_REFINEMENTS
    )
    controls = all(
        item.ab_identity_repeated
        and item.ablation_states_neutral
        and item.output_states_object_separated
        and item.history_backreaction_field_controls_equal
        and item.resource_budget_preserved
        for item in refinements
    )
    values = {
        "execution_id": bundle.execution_id,
        "run_contract_digest": bundle.run_contract_digest,
        "bundle_digest": bundle.bundle_digest,
        "refinements": refinements,
        "step_counts": tuple(
            (name, len(bundle.value(f"{name}_steps")))
            for name, _ in S1_EC10_REFINEMENTS
        ),
        "attempt_present_during_execution": attempt_present,
        "all_five_arm_controls_passed": controls,
        "prepared_inputs_preserved": all(
            item.prepared_inputs_preserved for item in refinements
        ),
        "real_field_kernels_executed": True,
        "synthetic_lifecycle_only": True,
        "canonical_execution_permitted": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }
    payload = {
        name: value for name, value in values.items() if name != "refinements"
    }
    payload["refinement_result_digests"] = tuple(
        item.result_digest for item in refinements
    )
    return E1PreparedSmallRealFormationResult(
        **values,
        result_digest=_digest(payload),
    )


@dataclass(frozen=True, slots=True)
class E1SmallRealFormationLifecycleResult:
    formation: E1PreparedSmallRealFormationResult
    receipt: E1PreparedSyntheticReceipt

    def __post_init__(self) -> None:
        if (
            not isinstance(self.formation, E1PreparedSmallRealFormationResult)
            or not isinstance(self.receipt, E1PreparedSyntheticReceipt)
            or self.receipt.consumer_digest != self.formation.result_digest
            or self.receipt.bundle_digest != self.formation.bundle_digest
            or self.receipt.run_contract_digest
            != self.formation.run_contract_digest
        ):
            raise E1ConfirmationSmallRealLifecycleError(
                "S1-EC11 lifecycle receipt does not bind the formation"
            )


def execute_prepared_small_real_formation_lifecycle(
    bundle: E1PreparedExecutionBundle,
) -> E1SmallRealFormationLifecycleResult:
    """Run the temporary Exactly-once lifecycle with one real consumer."""

    formed: list[E1PreparedSmallRealFormationResult] = []

    def consumer(received: E1PreparedExecutionBundle) -> str:
        result = consume_prepared_small_real_formation(received)
        formed.append(result)
        return result.result_digest

    receipt = execute_prepared_bundle_synthetically(bundle, consumer)
    if len(formed) != 1:
        raise E1ConfirmationSmallRealLifecycleError(
            "S1-EC11 real consumer execution count changed"
        )
    return E1SmallRealFormationLifecycleResult(formed[0], receipt)
