"""Private S1-EC10 small real r2/r4/r8 five-arm refinement matrix."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from .e1_completion_aligned_refinement import _refined_steps
from .e1_confirmation_small_five_arm_formation import (
    E1SmallFiveArmFormationResult,
    run_small_five_arm_formation_in_memory,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest
from .shared_mcm_field import SharedMCMField


class E1ConfirmationSmallRefinementMatrixError(ValueError):
    """Raised when one S1-EC10 small refinement control fails."""


S1_EC10_REFINEMENTS = (("r2", 2), ("r4", 4), ("r8", 8))
S1_EC10_BOUNDARIES = (0, 1_000_000, 2_000_000)
S1_EC10_RATE = 1_000_000.0


def _state_distance(
    first: E1LocalEdgePlasticityState,
    second: E1LocalEdgePlasticityState,
) -> float:
    first_values = {item.edge: item.binding for item in first.edge_bindings}
    second_values = {item.edge: item.binding for item in second.edge_bindings}
    if first_values.keys() != second_values.keys():
        raise E1ConfirmationSmallRefinementMatrixError(
            "S1-EC10 state edge inventories differ"
        )
    return max(
        abs(first_values[edge] - second_values[edge])
        for edge in first_values
    )


def _refinement_residual(
    first: E1SmallFiveArmFormationResult,
    second: E1SmallFiveArmFormationResult,
) -> float:
    if tuple(item.arm_id for item in first.arms) != tuple(
        item.arm_id for item in second.arms
    ):
        raise E1ConfirmationSmallRefinementMatrixError(
            "S1-EC10 refinement arm inventories differ"
        )
    return max(
        _state_distance(left.output_state, right.output_state)
        for left, right in zip(first.arms, second.arms, strict=True)
    )


@dataclass(frozen=True, slots=True)
class E1SmallRefinementMatrixResult:
    refinements: tuple[E1SmallFiveArmFormationResult, ...]
    step_counts: tuple[tuple[str, int], ...]
    history_state_distances: tuple[tuple[str, float], ...]
    r2_r4_state_residual: float
    r4_r8_state_residual: float
    convergence_nonincreasing: bool
    all_five_arm_controls_passed: bool
    prepared_inputs_preserved: bool
    canonical_execution_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        refinements = tuple(self.refinements)
        expected_ids = tuple(item[0] for item in S1_EC10_REFINEMENTS)
        numeric = (
            *(value for _, value in self.history_state_distances),
            self.r2_r4_state_residual,
            self.r4_r8_state_residual,
        )
        if (
            tuple(item.refinement_id for item in refinements) != expected_ids
            or self.step_counts != (("r2", 4), ("r4", 8), ("r8", 16))
            or tuple(role for role, _ in self.history_state_distances)
            != expected_ids
            or any(not math.isfinite(value) or value < 0.0 for value in numeric)
            or self.convergence_nonincreasing
            is not (self.r4_r8_state_residual <= self.r2_r4_state_residual)
            or self.all_five_arm_controls_passed is not True
            or self.prepared_inputs_preserved is not True
            or self.canonical_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationSmallRefinementMatrixError(
                "S1-EC10 small refinement matrix control failed"
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
            raise E1ConfirmationSmallRefinementMatrixError(
                "S1-EC10 result digest does not match its payload"
            )
        object.__setattr__(self, "refinements", refinements)

    def digest(self) -> str:
        return _digest(asdict(self))


def run_small_real_refinement_matrix(
    history_ab: Any,
    history_ba: Any,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
) -> E1SmallRefinementMatrixResult:
    """Run the small five-arm matrix at r2, r4, and r8 without persistence."""

    sequences = (tuple(history_ab), tuple(history_ba))
    clock_ids = {
        sequence.clock_id
        for history in sequences
        for sequence in history
    }
    if len(clock_ids) != 1:
        raise E1ConfirmationSmallRefinementMatrixError(
            "S1-EC10 histories must share one clock"
        )
    field_digest = _initial_field_digest(initial_field)
    state_digest = _initial_state_digest(initial_state)
    clock_id = next(iter(clock_ids))
    results = []
    step_counts = []
    for refinement_id, factor in S1_EC10_REFINEMENTS:
        steps = _refined_steps(
            clock_id,
            S1_EC10_RATE,
            S1_EC10_BOUNDARIES,
            factor,
        )
        step_counts.append((refinement_id, len(steps)))
        results.append(
            run_small_five_arm_formation_in_memory(
                refinement_id,
                sequences[0],
                sequences[1],
                steps,
                steps,
                initial_field,
                initial_state,
            )
        )
    refinements = tuple(results)
    history_distances = tuple(
        (
            item.refinement_id,
            _state_distance(
                item.arms[0].output_state,
                item.arms[1].output_state,
            ),
        )
        for item in refinements
    )
    r2_r4 = _refinement_residual(refinements[0], refinements[1])
    r4_r8 = _refinement_residual(refinements[1], refinements[2])
    controls_passed = all(
        item.ab_identity_repeated
        and item.ablation_states_neutral
        and item.output_states_object_separated
        and item.history_backreaction_field_controls_equal
        and item.resource_budget_preserved
        for item in refinements
    )
    inputs_preserved = (
        _initial_field_digest(initial_field) == field_digest
        and _initial_state_digest(initial_state) == state_digest
        and all(item.prepared_inputs_preserved for item in refinements)
    )
    values = {
        "refinements": refinements,
        "step_counts": tuple(step_counts),
        "history_state_distances": history_distances,
        "r2_r4_state_residual": r2_r4,
        "r4_r8_state_residual": r4_r8,
        "convergence_nonincreasing": r4_r8 <= r2_r4,
        "all_five_arm_controls_passed": controls_passed,
        "prepared_inputs_preserved": inputs_preserved,
        "canonical_execution_permitted": False,
        "claims_permitted": False,
    }
    payload = {
        name: value for name, value in values.items() if name != "refinements"
    }
    payload["refinement_result_digests"] = tuple(
        item.result_digest for item in refinements
    )
    return E1SmallRefinementMatrixResult(
        **values,
        result_digest=_digest(payload),
    )
