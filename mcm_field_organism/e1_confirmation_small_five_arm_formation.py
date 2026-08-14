"""Private S1-EC9 real five-arm formation on a small in-memory fixture."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from .e1_confirmation_prepared_formation_consumer import (
    S1_EC7_FORMATION_ARMS,
)
from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
    run_prepared_real_formation_arm_in_memory,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest
from .shared_mcm_field import SharedMCMField


class E1ConfirmationSmallFiveArmFormationError(ValueError):
    """Raised when one S1-EC9 five-arm control fails."""


@dataclass(frozen=True, slots=True)
class E1SmallFiveArmFormationResult:
    refinement_id: str
    arms: tuple[E1PreparedRealFormationArmResult, ...]
    ab_identity_repeated: bool
    ablation_states_neutral: bool
    output_states_object_separated: bool
    history_backreaction_field_controls_equal: bool
    resource_budget_preserved: bool
    prepared_inputs_preserved: bool
    maximum_resource_budget_error: float
    canonical_execution_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        arms = tuple(self.arms)
        if (
            tuple(item.arm_id for item in arms) != S1_EC7_FORMATION_ARMS
            or any(item.refinement_id != self.refinement_id for item in arms)
            or self.ab_identity_repeated is not True
            or self.ablation_states_neutral is not True
            or self.output_states_object_separated is not True
            or self.history_backreaction_field_controls_equal is not True
            or self.resource_budget_preserved is not True
            or self.prepared_inputs_preserved is not True
            or not math.isfinite(self.maximum_resource_budget_error)
            or self.maximum_resource_budget_error < 0.0
            or self.maximum_resource_budget_error > 1e-12
            or self.canonical_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationSmallFiveArmFormationError(
                "S1-EC9 five-arm formation control failed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"arms", "result_digest"}
        }
        payload["arm_result_digests"] = tuple(
            item.result_digest for item in arms
        )
        if self.result_digest != _digest(payload):
            raise E1ConfirmationSmallFiveArmFormationError(
                "S1-EC9 result digest does not match its payload"
            )
        object.__setattr__(self, "arms", arms)

    def digest(self) -> str:
        return _digest(asdict(self))


def run_small_five_arm_formation_in_memory(
    refinement_id: str,
    history_ab: Any,
    history_ba: Any,
    ab_proposal_steps: Any,
    ba_proposal_steps: Any,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
) -> E1SmallFiveArmFormationResult:
    """Run five real copied-input arms and enforce the formation controls."""

    field_digest = _initial_field_digest(initial_field)
    state_digest = _initial_state_digest(initial_state)
    specs = (
        ("ab", history_ab, ab_proposal_steps, True),
        ("ba", history_ba, ba_proposal_steps, True),
        ("ab_identity", history_ab, ab_proposal_steps, True),
        ("ab_formation_ablated", history_ab, ab_proposal_steps, False),
        ("ba_formation_ablated", history_ba, ba_proposal_steps, False),
    )
    arms = tuple(
        run_prepared_real_formation_arm_in_memory(
            arm_id,
            refinement_id,
            sequences,
            steps,
            initial_field,
            initial_state,
            formation_enabled,
        )
        for arm_id, sequences, steps, formation_enabled in specs
    )
    states = tuple(item.output_state for item in arms)
    ab_identity = states[0] == states[2]
    ablation_neutral = all(
        edge.binding == 0.0
        for state in (states[3], states[4])
        for edge in state.edge_bindings
    )
    separated = len({id(item) for item in states}) == len(states)
    field_controls = (
        arms[0].audit.field_digest
        == arms[2].audit.field_digest
        == arms[3].audit.field_digest
        and arms[1].audit.field_digest == arms[4].audit.field_digest
    )
    maximum_budget_error = max(
        item.audit.resource_budget_error for item in arms
    )
    resource_preserved = maximum_budget_error <= 1e-12
    inputs_preserved = (
        _initial_field_digest(initial_field) == field_digest
        and _initial_state_digest(initial_state) == state_digest
        and all(item.input_objects_preserved for item in arms)
    )
    values = {
        "refinement_id": refinement_id,
        "arms": arms,
        "ab_identity_repeated": ab_identity,
        "ablation_states_neutral": ablation_neutral,
        "output_states_object_separated": separated,
        "history_backreaction_field_controls_equal": field_controls,
        "resource_budget_preserved": resource_preserved,
        "prepared_inputs_preserved": inputs_preserved,
        "maximum_resource_budget_error": maximum_budget_error,
        "canonical_execution_permitted": False,
        "claims_permitted": False,
    }
    payload = {
        name: value for name, value in values.items() if name != "arms"
    }
    payload["arm_result_digests"] = tuple(
        item.result_digest for item in arms
    )
    return E1SmallFiveArmFormationResult(
        **values,
        result_digest=_digest(payload),
    )
