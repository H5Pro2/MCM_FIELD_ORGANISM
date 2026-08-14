"""Private S1-EC13 one-shot lifecycle for full prepared AV formation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .e1_confirmation_full_formation_resource_preflight import (
    E1FullFormationResourcePreflight,
    S1_EC12_EXPECTED_REFINEMENTS,
    preflight_prepared_full_formation_resources,
)
from .e1_confirmation_prepared_execution_bundle import (
    E1PreparedExecutionBundle,
    E1PreparedSyntheticReceipt,
    execute_prepared_bundle_synthetically,
)
from .e1_confirmation_prepared_formation_consumer import (
    _typed_values_from_bundle,
)
from .e1_confirmation_research_corridor import S1_EC3_RUN_ID
from .e1_confirmation_small_five_arm_formation import (
    E1SmallFiveArmFormationResult,
    run_small_five_arm_formation_in_memory,
)
from .e1_confirmation_small_refinement_matrix import (
    _refinement_residual,
    _state_distance,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullFormationLifecycleError(ValueError):
    """Raised when the S1-EC13 full formation lifecycle fails closed."""


@dataclass(frozen=True, slots=True)
class E1PreparedFullFormationResult:
    execution_id: str
    run_contract_digest: str
    bundle_digest: str
    pre_attempt_preflight_digest: str
    in_attempt_preflight_digest: str
    refinements: tuple[E1SmallFiveArmFormationResult, ...]
    refinement_step_counts: tuple[tuple[str, int, int, int], ...]
    history_state_distances: tuple[tuple[str, float], ...]
    r2_r4_state_residual: float
    r4_r8_state_residual: float
    convergence_nonincreasing: bool
    attempt_present_during_execution: bool
    all_five_arm_controls_passed: bool
    prepared_inputs_preserved: bool
    real_field_kernels_executed: bool
    full_prepared_formation_executed: bool
    temporary_lifecycle_only: bool
    canonical_execution_permitted: bool
    probe_execution_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        refinements = tuple(self.refinements)
        expected_ids = tuple(item[0] for item in S1_EC12_EXPECTED_REFINEMENTS)
        if (
            self.execution_id != S1_EC3_RUN_ID
            or len(self.run_contract_digest) != 64
            or len(self.bundle_digest) != 64
            or self.pre_attempt_preflight_digest
            != self.in_attempt_preflight_digest
            or len(self.pre_attempt_preflight_digest) != 64
            or tuple(item.refinement_id for item in refinements) != expected_ids
            or self.refinement_step_counts != S1_EC12_EXPECTED_REFINEMENTS
            or tuple(name for name, _ in self.history_state_distances)
            != expected_ids
            or self.convergence_nonincreasing
            is not (self.r4_r8_state_residual <= self.r2_r4_state_residual)
            or self.attempt_present_during_execution is not True
            or self.all_five_arm_controls_passed is not True
            or self.prepared_inputs_preserved is not True
            or self.real_field_kernels_executed is not True
            or self.full_prepared_formation_executed is not True
            or self.temporary_lifecycle_only is not True
            or self.canonical_execution_permitted is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullFormationLifecycleError(
                "S1-EC13 full formation result changed"
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
            raise E1ConfirmationFullFormationLifecycleError(
                "S1-EC13 result digest does not match its payload"
            )
        object.__setattr__(self, "refinements", refinements)


def consume_prepared_full_formation(
    bundle: E1PreparedExecutionBundle,
    expected_preflight: E1FullFormationResourcePreflight,
    *,
    attempt_path: Path | None = None,
    runtime_guard: Callable[[], None] | None = None,
) -> E1PreparedFullFormationResult:
    """Consume full prepared plans only after Attempt and a repeated gate."""

    if not isinstance(expected_preflight, E1FullFormationResourcePreflight):
        raise E1ConfirmationFullFormationLifecycleError(
            "S1-EC13 requires the pre-Attempt S1-EC12 result"
        )
    guarded_attempt = (
        Path(bundle.attempt_path) if attempt_path is None else Path(attempt_path)
    )
    attempt_present = guarded_attempt.is_file()
    if not attempt_present:
        raise E1ConfirmationFullFormationLifecycleError(
            "S1-EC13/S1-EC19 requires an active Attempt marker"
        )
    if runtime_guard is not None and not callable(runtime_guard):
        raise E1ConfirmationFullFormationLifecycleError(
            "S1-EC19 runtime guard is invalid"
        )
    in_attempt_preflight = preflight_prepared_full_formation_resources(bundle)
    if in_attempt_preflight.result_digest != expected_preflight.result_digest:
        raise E1ConfirmationFullFormationLifecycleError(
            "S1-EC13 resource preflight changed across Attempt"
        )
    values = _typed_values_from_bundle(bundle)
    source = values.av_permutation
    formed = []
    for ab, ba in zip(
        values.history_ab_plans.plans,
        values.history_ba_plans.plans,
        strict=True,
    ):
        if runtime_guard is not None:
            runtime_guard()
        formed.append(
            run_small_five_arm_formation_in_memory(
                ab.refinement_id,
                source.history_ab,
                source.history_ba,
                ab.proposal_steps,
                ba.proposal_steps,
                values.initial_field,
                values.initial_state,
            )
        )
        if runtime_guard is not None:
            runtime_guard()
    refinements = tuple(formed)
    history_distances = tuple(
        (
            item.refinement_id,
            _state_distance(item.arms[0].output_state, item.arms[1].output_state),
        )
        for item in refinements
    )
    r2_r4 = _refinement_residual(refinements[0], refinements[1])
    r4_r8 = _refinement_residual(refinements[1], refinements[2])
    controls = all(
        item.ab_identity_repeated
        and item.ablation_states_neutral
        and item.output_states_object_separated
        and item.history_backreaction_field_controls_equal
        and item.resource_budget_preserved
        for item in refinements
    )
    payload = {
        "execution_id": bundle.execution_id,
        "run_contract_digest": bundle.run_contract_digest,
        "bundle_digest": bundle.bundle_digest,
        "pre_attempt_preflight_digest": expected_preflight.result_digest,
        "in_attempt_preflight_digest": in_attempt_preflight.result_digest,
        "refinements": refinements,
        "refinement_step_counts": in_attempt_preflight.refinement_step_counts,
        "history_state_distances": history_distances,
        "r2_r4_state_residual": r2_r4,
        "r4_r8_state_residual": r4_r8,
        "convergence_nonincreasing": r4_r8 <= r2_r4,
        "attempt_present_during_execution": attempt_present,
        "all_five_arm_controls_passed": controls,
        "prepared_inputs_preserved": all(
            item.prepared_inputs_preserved for item in refinements
        ),
        "real_field_kernels_executed": True,
        "full_prepared_formation_executed": True,
        "temporary_lifecycle_only": True,
        "canonical_execution_permitted": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }
    digest_payload = {
        name: value for name, value in payload.items() if name != "refinements"
    }
    digest_payload["refinement_result_digests"] = tuple(
        item.result_digest for item in refinements
    )
    return E1PreparedFullFormationResult(
        **payload,
        result_digest=_digest(digest_payload),
    )


@dataclass(frozen=True, slots=True)
class E1FullFormationLifecycleResult:
    preflight: E1FullFormationResourcePreflight
    formation: E1PreparedFullFormationResult
    receipt: E1PreparedSyntheticReceipt

    def __post_init__(self) -> None:
        if (
            self.formation.pre_attempt_preflight_digest
            != self.preflight.result_digest
            or self.receipt.consumer_digest != self.formation.result_digest
            or self.receipt.bundle_digest != self.formation.bundle_digest
            or self.receipt.run_contract_digest
            != self.formation.run_contract_digest
        ):
            raise E1ConfirmationFullFormationLifecycleError(
                "S1-EC13 receipt does not bind preflight and formation"
            )


def execute_prepared_full_formation_lifecycle(
    bundle: E1PreparedExecutionBundle,
) -> E1FullFormationLifecycleResult:
    """Execute one full temporary formation after the S1-EC12 gate."""

    preflight = preflight_prepared_full_formation_resources(bundle)
    formed: list[E1PreparedFullFormationResult] = []

    def consumer(received: E1PreparedExecutionBundle) -> str:
        result = consume_prepared_full_formation(received, preflight)
        formed.append(result)
        return result.result_digest

    receipt = execute_prepared_bundle_synthetically(bundle, consumer)
    if len(formed) != 1:
        raise E1ConfirmationFullFormationLifecycleError(
            "S1-EC13 full formation execution count changed"
        )
    return E1FullFormationLifecycleResult(preflight, formed[0], receipt)
