"""Private S1-EC54 real wrappers for one contact-aware common-probe slot."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import inspect

from .e1_common_probe_real_binding_contract import (
    E1CommonProbeRealBindingContract,
    E1CommonProbeRealSlotBinding,
)
from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
    run_prepared_real_formation_arm_in_memory,
)
from .e1_confirmation_refinement_planner import (
    E1ConfirmationRefinementPlan,
    E1ConfirmationRefinementPlanSet,
)
from .e1_frozen_state_transfer_contract import _probe_digest
from .e1_frozen_transient_probe import advance_frozen_e1_fast_shared_field_transient
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest, _state_payload
from .e1_repetition_formation_planner import (
    E1RepetitionFormationPlanSet,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1CommonProbeRealWrapperError(ValueError):
    """Raised when one EC54 private wrapper leaves its bound slot."""


S1_EC54_IMPLEMENTATION_ID = "e1.common-probe-real-wrappers.s1ec54.v1"
S1_EC54_EC52_CONTRACT_DIGEST = (
    "291ea70c96ad26b3f6e696588ebd55d3e6f7163967b45de9a689bd731cb7bf7b"
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeResolvedSlot:
    binding: E1CommonProbeRealSlotBinding
    formation_sequences: tuple[ReceptorTimeSequence, ...] | None
    formation_plan: E1ConfirmationRefinementPlan | None
    probe_sequences: tuple[ReceptorTimeSequence, ...]
    probe_plan: E1ConfirmationRefinementPlan
    context_digest: str

    def __post_init__(self) -> None:
        is_p0 = self.binding.state_role is None
        if (
            not isinstance(self.binding, E1CommonProbeRealSlotBinding)
            or (self.formation_sequences is None) is not is_p0
            or (self.formation_plan is None) is not is_p0
            or not self.probe_sequences
            or not isinstance(self.probe_plan, E1ConfirmationRefinementPlan)
            or self.probe_plan.refinement_id != self.binding.refinement_id
        ):
            raise E1CommonProbeRealWrapperError(
                "S1-EC54 resolved slot changed"
            )
        payload = {
            "binding_digest": self.binding.binding_digest,
            "formation_sequence_digest": (
                None if is_p0 else _probe_digest(self.formation_sequences)
            ),
            "formation_plan_digest": (
                None if is_p0 else self.formation_plan.digest()
            ),
            "probe_sequence_digest": _probe_digest(self.probe_sequences),
            "probe_plan_digest": self.probe_plan.digest(),
        }
        if self.context_digest != _digest(payload):
            raise E1CommonProbeRealWrapperError(
                "S1-EC54 resolved slot digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeFreshField:
    binding_digest: str
    initial_field_digest: str
    field: SharedMCMField


@dataclass(frozen=True, slots=True)
class E1CommonProbeRealProbeOutput:
    binding_digest: str
    terminal_field_digest: str
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    field_step_count: int
    source_support_count: int
    frozen_state_digest_before: str | None
    frozen_state_digest_after: str | None
    frozen_state_preserved: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            len(self.binding_digest) != 64
            or len(self.terminal_field_digest) != 64
            or not self.activation
            or len(self.activation) != len(self.afterimage)
            or self.field_step_count < 1
            or self.source_support_count < 1
            or self.frozen_state_preserved is not True
            or any(value is not False for value in (
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
        ):
            raise E1CommonProbeRealWrapperError(
                "S1-EC54 real probe output crossed its technical scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if self.result_digest != _digest(payload):
            raise E1CommonProbeRealWrapperError(
                "S1-EC54 real probe output digest changed"
            )


def resolve_e1_common_probe_real_slot(
    contract: E1CommonProbeRealBindingContract,
    binding: E1CommonProbeRealSlotBinding,
    formation_plans: E1RepetitionFormationPlanSet,
    probe_sequences: tuple[ReceptorTimeSequence, ...],
    probe_plans: E1ConfirmationRefinementPlanSet,
) -> E1CommonProbeResolvedSlot:
    """Resolve only plans and sources; never advance a field."""

    if not isinstance(contract, E1CommonProbeRealBindingContract) or contract.contract_digest != S1_EC54_EC52_CONTRACT_DIGEST:
        raise E1CommonProbeRealWrapperError("S1-EC54 requires the EC52 contract")
    contract.__post_init__()
    if not isinstance(binding, E1CommonProbeRealSlotBinding) or binding not in contract.slot_bindings:
        raise E1CommonProbeRealWrapperError("S1-EC54 binding is outside EC52")
    if not isinstance(formation_plans, E1RepetitionFormationPlanSet) or formation_plans.plan_set_digest != contract.source_plan_set_digest:
        raise E1CommonProbeRealWrapperError("S1-EC54 formation plans changed")
    if not isinstance(probe_plans, E1ConfirmationRefinementPlanSet):
        raise E1CommonProbeRealWrapperError("S1-EC54 probe plans are missing")
    formation_plans.__post_init__()
    probe_plans.__post_init__()
    sequences = tuple(probe_sequences)
    if _probe_digest(sequences) != contract.probe_source_digest:
        raise E1CommonProbeRealWrapperError("S1-EC54 common probe source changed")
    pair = formation_plans.pairs[binding.contact_count - 1]
    probe_plan = next(x for x in probe_plans.plans if x.refinement_id == binding.refinement_id)
    if binding.formation_schedule == "none":
        formation_sequences = None
        formation_plan = None
    else:
        formation_sequences = getattr(pair, f"{binding.formation_schedule}_sequences")
        plan_set = getattr(pair, f"{binding.formation_schedule}_plans")
        formation_plan = next(x for x in plan_set.plans if x.refinement_id == binding.refinement_id)
    payload = {
        "binding_digest": binding.binding_digest,
        "formation_sequence_digest": None if formation_sequences is None else _probe_digest(formation_sequences),
        "formation_plan_digest": None if formation_plan is None else formation_plan.digest(),
        "probe_sequence_digest": _probe_digest(sequences),
        "probe_plan_digest": probe_plan.digest(),
    }
    return E1CommonProbeResolvedSlot(
        binding, formation_sequences, formation_plan, sequences, probe_plan,
        _digest(payload),
    )


def run_e1_common_probe_real_formation_wrapper(
    resolved: E1CommonProbeResolvedSlot,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
) -> E1PreparedRealFormationArmResult:
    """Invoke the bound real formation kernel for one non-P0 state role."""

    if not isinstance(resolved, E1CommonProbeResolvedSlot) or resolved.binding.formation_arm_id is None or resolved.formation_plan is None or resolved.formation_sequences is None:
        raise E1CommonProbeRealWrapperError("S1-EC54 formation wrapper requires one E1 slot")
    arm = resolved.binding.formation_arm_id
    return run_prepared_real_formation_arm_in_memory(
        arm,
        resolved.binding.refinement_id,
        resolved.formation_sequences,
        resolved.formation_plan.proposal_steps,
        initial_field,
        initial_state,
        not arm.endswith("formation_ablated"),
    )


def build_e1_common_probe_fresh_field(
    binding: E1CommonProbeRealSlotBinding,
    initial_field: SharedMCMField,
) -> E1CommonProbeFreshField:
    """Create one object-separated field with an identical initial digest."""

    if not isinstance(binding, E1CommonProbeRealSlotBinding) or not isinstance(initial_field, SharedMCMField):
        raise E1CommonProbeRealWrapperError("S1-EC54 fresh-field inputs changed")
    initial_digest = _initial_field_digest(initial_field)
    field = copy.deepcopy(initial_field)
    if field is initial_field or _initial_field_digest(field) != initial_digest:
        raise E1CommonProbeRealWrapperError("S1-EC54 fresh field is not an identical separate copy")
    return E1CommonProbeFreshField(binding.binding_digest, initial_digest, field)


def run_e1_common_probe_real_probe_wrapper(
    resolved: E1CommonProbeResolvedSlot,
    fresh: E1CommonProbeFreshField,
    frozen_state: E1LocalEdgePlasticityState | None,
) -> E1CommonProbeRealProbeOutput:
    """Invoke exactly one bound real common-probe slot in memory."""

    if not isinstance(resolved, E1CommonProbeResolvedSlot) or not isinstance(fresh, E1CommonProbeFreshField) or fresh.binding_digest != resolved.binding.binding_digest:
        raise E1CommonProbeRealWrapperError("S1-EC54 probe wrapper inputs changed")
    is_p0 = resolved.binding.state_role is None
    if (frozen_state is None) is not is_p0:
        raise E1CommonProbeRealWrapperError("S1-EC54 probe state route changed")
    before = None if frozen_state is None else _digest(_state_payload(frozen_state))
    current = fresh.field
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    handoff = resolved.probe_plan.handoff
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, current.docks)
        inputs = project_transient_docks_to_neuron_inputs(trajectory, current.docks)
        distribution = ReceptorDistribution(
            CommonFieldTime(batch.step_time.clock_id, batch.step_time.start_tick, batch.step_time.end_tick),
            (),
        )
        if is_p0:
            current = advance_neutral_fast_shared_field_transient(
                current, distribution, inputs, substrate, afterimage
            )
        else:
            output = advance_frozen_e1_fast_shared_field_transient(
                current, frozen_state, distribution, inputs, substrate,
                afterimage,
                backreaction_enabled=resolved.binding.backreaction_enabled,
            )
            current = output.field
            if output.e1_state is not frozen_state:
                raise E1CommonProbeRealWrapperError("S1-EC54 frozen state object changed")
    snapshot = current.snapshot()
    after = None if frozen_state is None else _digest(_state_payload(frozen_state))
    values = {
        "binding_digest": resolved.binding.binding_digest,
        "terminal_field_digest": snapshot.digest(),
        "activation": snapshot.activation,
        "afterimage": snapshot.afterimage,
        "field_step_count": len(resolved.probe_plan.proposal_steps),
        "source_support_count": handoff.source_event_count,
        "frozen_state_digest_before": before,
        "frozen_state_digest_after": after,
        "frozen_state_preserved": before == after,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeRealProbeOutput(**values, result_digest=_digest(values))


@dataclass(frozen=True, slots=True)
class E1CommonProbeRealWrappersAudit:
    implementation_id: str
    source_contract_digest: str
    wrapper_names: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    wrappers_implemented: bool
    small_fixture_permitted: bool
    full_matrix_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.implementation_id != S1_EC54_IMPLEMENTATION_ID
            or self.source_contract_digest != S1_EC54_EC52_CONTRACT_DIGEST
            or self.wrapper_names != (
                "resolve_e1_common_probe_real_slot",
                "run_e1_common_probe_real_formation_wrapper",
                "build_e1_common_probe_fresh_field",
                "run_e1_common_probe_real_probe_wrapper",
            )
            or any(value is not True for _, value in self.checks)
            or self.wrappers_implemented is not True
            or self.small_fixture_permitted is not True
            or any(value is not False for value in (
                self.full_matrix_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision != "REAL_WRAPPERS_IMPLEMENTED_SMALL_FIXTURE_MISSING"
        ):
            raise E1CommonProbeRealWrapperError("S1-EC54 audit crossed its scope")
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "audit_digest"}
        if self.audit_digest != _digest(payload):
            raise E1CommonProbeRealWrapperError("S1-EC54 audit digest changed")


def audit_e1_common_probe_real_wrappers() -> E1CommonProbeRealWrappersAudit:
    """Audit wrapper source without invoking any wrapper."""

    wrappers = (
        resolve_e1_common_probe_real_slot,
        run_e1_common_probe_real_formation_wrapper,
        build_e1_common_probe_fresh_field,
        run_e1_common_probe_real_probe_wrapper,
    )
    sources = tuple(inspect.getsource(item) for item in wrappers)
    checks = (
        ("resolver-binds-no-field-kernel", "advance_neutral_fast_shared_field_transient(" not in sources[0]),
        ("formation-wrapper-calls-bound-kernel", "run_prepared_real_formation_arm_in_memory(" in sources[1]),
        ("fresh-field-wrapper-deepcopies", "copy.deepcopy(initial_field)" in sources[2]),
        ("probe-wrapper-calls-neutral-kernel", "advance_neutral_fast_shared_field_transient(" in sources[3]),
        ("probe-wrapper-calls-frozen-kernel", "advance_frozen_e1_fast_shared_field_transient(" in sources[3]),
        ("probe-wrapper-preserves-frozen-object", "output.e1_state is not frozen_state" in sources[3]),
        ("all-wrappers-have-no-write-path", all(
            token not in source
            for source in sources
            for token in ("write_text", "write_bytes", "open(")
        )),
    )
    values = {
        "implementation_id": S1_EC54_IMPLEMENTATION_ID,
        "source_contract_digest": S1_EC54_EC52_CONTRACT_DIGEST,
        "wrapper_names": tuple(item.__name__ for item in wrappers),
        "checks": checks,
        "wrappers_implemented": True,
        "small_fixture_permitted": True,
        "full_matrix_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "REAL_WRAPPERS_IMPLEMENTED_SMALL_FIXTURE_MISSING",
    }
    return E1CommonProbeRealWrappersAudit(**values, audit_digest=_digest(values))
