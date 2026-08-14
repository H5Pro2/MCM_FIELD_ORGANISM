"""S1-EC55 small nonpersistent n2/r2 real-wrapper fixture."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .e1_common_probe_real_binding_contract import E1CommonProbeRealBindingContract
from .e1_common_probe_real_wrappers import (
    build_e1_common_probe_fresh_field,
    resolve_e1_common_probe_real_slot,
    run_e1_common_probe_real_formation_wrapper,
    run_e1_common_probe_real_probe_wrapper,
)
from .e1_confirmation_refinement_planner import E1ConfirmationRefinementPlanSet
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_formation_runner import _digest
from .e1_repetition_formation_planner import E1RepetitionFormationPlanSet
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField


class E1CommonProbeSmallRealFixtureError(ValueError):
    """Raised when EC55 leaves its three-slot n2/r2 technical boundary."""


S1_EC55_FIXTURE_ID = "e1.common-probe-small-real-fixture.s1ec55.v1"
S1_EC55_EC52_CONTRACT_DIGEST = (
    "291ea70c96ad26b3f6e696588ebd55d3e6f7163967b45de9a689bd731cb7bf7b"
)
S1_EC55_ROLES = (
    "p0-reset-ab",
    "e1-active-ab",
    "e1-probe-feedback-ablated-ab",
)


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


@dataclass(frozen=True, slots=True)
class E1CommonProbeSmallRealFixtureResult:
    fixture_id: str
    source_contract_digest: str
    contact_count: int
    refinement_id: str
    roles: tuple[str, ...]
    formation_result_digest: str
    p0_result_digest: str
    active_result_digest: str
    feedback_ablated_result_digest: str
    active_feedback_activation_linf: float
    active_feedback_afterimage_linf: float
    formation_field_steps: int
    probe_field_steps: tuple[int, ...]
    total_field_steps: int
    all_initial_fields_identical_and_separate: bool
    frozen_state_preserved_in_both_e1_slots: bool
    input_objects_preserved: bool
    fixture_complete: bool
    full_matrix_executed: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.fixture_id != S1_EC55_FIXTURE_ID
            or self.source_contract_digest != S1_EC55_EC52_CONTRACT_DIGEST
            or self.contact_count != 2
            or self.refinement_id != "r2"
            or self.roles != S1_EC55_ROLES
            or any(len(value) != 64 for value in (
                self.formation_result_digest,
                self.p0_result_digest,
                self.active_result_digest,
                self.feedback_ablated_result_digest,
            ))
            or any(not math.isfinite(value) or value < 0.0 for value in (
                self.active_feedback_activation_linf,
                self.active_feedback_afterimage_linf,
            ))
            or self.formation_field_steps != 402
            or self.probe_field_steps != (200, 200, 200)
            or self.total_field_steps != 1002
            or any(value is not True for value in (
                self.all_initial_fields_identical_and_separate,
                self.frozen_state_preserved_in_both_e1_slots,
                self.input_objects_preserved,
                self.fixture_complete,
            ))
            or any(value is not False for value in (
                self.full_matrix_executed,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
        ):
            raise E1CommonProbeSmallRealFixtureError(
                "S1-EC55 result changed or crossed its small-fixture scope"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "result_digest"}
        if self.result_digest != _digest(payload):
            raise E1CommonProbeSmallRealFixtureError(
                "S1-EC55 result digest changed"
            )


def run_e1_common_probe_small_real_fixture(
    contract: E1CommonProbeRealBindingContract,
    formation_plans: E1RepetitionFormationPlanSet,
    probe_sequences: tuple[ReceptorTimeSequence, ...],
    probe_plans: E1ConfirmationRefinementPlanSet,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
) -> E1CommonProbeSmallRealFixtureResult:
    """Run only P0, active AB, and feedback-off AB for n2/r2 in memory."""

    if not isinstance(contract, E1CommonProbeRealBindingContract) or contract.contract_digest != S1_EC55_EC52_CONTRACT_DIGEST:
        raise E1CommonProbeSmallRealFixtureError("S1-EC55 requires EC52")
    bindings = tuple(
        next(x for x in contract.slot_bindings if (x.contact_count, x.refinement_id, x.role_id) == (2, "r2", role))
        for role in S1_EC55_ROLES
    )
    resolved = tuple(
        resolve_e1_common_probe_real_slot(
            contract, binding, formation_plans, probe_sequences, probe_plans
        )
        for binding in bindings
    )
    formation = run_e1_common_probe_real_formation_wrapper(
        resolved[1], initial_field, initial_state
    )
    fresh = tuple(
        build_e1_common_probe_fresh_field(binding, initial_field)
        for binding in bindings
    )
    outputs = (
        run_e1_common_probe_real_probe_wrapper(resolved[0], fresh[0], None),
        run_e1_common_probe_real_probe_wrapper(
            resolved[1], fresh[1], formation.output_state
        ),
        run_e1_common_probe_real_probe_wrapper(
            resolved[2], fresh[2], formation.output_state
        ),
    )
    values = {
        "fixture_id": S1_EC55_FIXTURE_ID,
        "source_contract_digest": contract.contract_digest,
        "contact_count": 2,
        "refinement_id": "r2",
        "roles": S1_EC55_ROLES,
        "formation_result_digest": formation.result_digest,
        "p0_result_digest": outputs[0].result_digest,
        "active_result_digest": outputs[1].result_digest,
        "feedback_ablated_result_digest": outputs[2].result_digest,
        "active_feedback_activation_linf": _linf(
            outputs[1].activation, outputs[2].activation
        ),
        "active_feedback_afterimage_linf": _linf(
            outputs[1].afterimage, outputs[2].afterimage
        ),
        "formation_field_steps": len(resolved[1].formation_plan.proposal_steps),
        "probe_field_steps": tuple(x.field_step_count for x in outputs),
        "total_field_steps": (
            len(resolved[1].formation_plan.proposal_steps)
            + sum(x.field_step_count for x in outputs)
        ),
        "all_initial_fields_identical_and_separate": (
            len({x.initial_field_digest for x in fresh}) == 1
            and len({id(x.field) for x in fresh}) == 3
        ),
        "frozen_state_preserved_in_both_e1_slots": (
            outputs[1].frozen_state_preserved
            and outputs[2].frozen_state_preserved
        ),
        "input_objects_preserved": formation.input_objects_preserved,
        "fixture_complete": True,
        "full_matrix_executed": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeSmallRealFixtureResult(**values, result_digest=_digest(values))
