"""Private S1-EB6 synthetic seven-arm probe for r2/r4/r8 formations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import math

from .e1_confirmation_formation_runner import E1ConfirmationFormationResult
from .e1_confirmation_refinement_planner import (
    E1ConfirmationRefinementPlan,
    S1_EB_CONTRACT_DIGEST,
    build_e1_confirmation_refinement_plans,
)
from .e1_frozen_state_transfer import (
    _distance,
    _field_vector,
    _fresh_field_digest,
)
from .e1_frozen_state_transfer_contract import _probe_digest
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
    advance_frozen_e1_fast_shared_field_transient,
)
from .e1_refined_confirmation_contract import E1RefinedConfirmationContract
from .e1_refined_formation_runner import _digest, _state_payload
from .e1_refined_world_formation_contract import S1_DS_PROBE_DIGEST
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


class E1ConfirmationSevenArmProbeError(ValueError):
    """Raised when an S1-EB6 synthetic probe loses a bound invariant."""


S1_EB6_FIELD_ROLES = (
    "p0",
    "ab_active",
    "ba_active",
    "ab_probe_ablated",
    "ba_probe_ablated",
    "ab_fixed",
    "ba_fixed",
)


def _valid_digest(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _state_digest(state) -> str:
    return _digest(_state_payload(state))


def _max_distance(
    reference: SharedMCMField,
    candidates: tuple[SharedMCMField, ...],
) -> float:
    return max(
        _distance(reference, candidate, role)
        for candidate in candidates
        for role in ("s", "h")
    )


def _vector(field: SharedMCMField, role: str) -> tuple[float, ...]:
    values = tuple(float(value) for value in _field_vector(field, role))
    if not values or any(not math.isfinite(value) for value in values):
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 probe field vector is invalid"
        )
    return values


@dataclass(frozen=True, slots=True)
class E1ConfirmationProbeResult:
    refinement_id: str
    factor: int
    probe_source_digest: str
    probe_plan_digest: str
    field_digests: tuple[tuple[str, str], ...]
    ab_active_s: tuple[float, ...]
    ba_active_s: tuple[float, ...]
    ab_active_h: tuple[float, ...]
    ba_active_h: tuple[float, ...]
    pre_probe_ab_state_digest: str
    pre_probe_ba_state_digest: str
    post_probe_ab_state_digest: str
    post_probe_ba_state_digest: str
    probe_ablation_residual: float
    fixed_adapter_residual: float
    initial_fields_identical_and_separate: bool
    supports_assigned_once: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (self.refinement_id, self.factor) not in {
            ("r2", 2),
            ("r4", 4),
            ("r8", 8),
        }:
            raise E1ConfirmationSevenArmProbeError(
                "S1-EB6 probe refinement changed"
            )
        for role in (
            "probe_source_digest",
            "probe_plan_digest",
            "pre_probe_ab_state_digest",
            "pre_probe_ba_state_digest",
            "post_probe_ab_state_digest",
            "post_probe_ba_state_digest",
            "result_digest",
        ):
            if not _valid_digest(getattr(self, role)):
                raise E1ConfirmationSevenArmProbeError(
                    f"{role} is not SHA-256"
                )
        fields = tuple(self.field_digests)
        if tuple(role for role, _ in fields) != S1_EB6_FIELD_ROLES or any(
            not _valid_digest(value) for _, value in fields
        ):
            raise E1ConfirmationSevenArmProbeError(
                "S1-EB6 probe field inventory changed"
            )
        vectors = (
            tuple(self.ab_active_s),
            tuple(self.ba_active_s),
            tuple(self.ab_active_h),
            tuple(self.ba_active_h),
        )
        if (
            len({len(item) for item in vectors}) != 1
            or not vectors[0]
            or any(not math.isfinite(value) for item in vectors for value in item)
        ):
            raise E1ConfirmationSevenArmProbeError(
                "S1-EB6 probe vectors changed geometry"
            )
        if (
            self.pre_probe_ab_state_digest != self.post_probe_ab_state_digest
            or self.pre_probe_ba_state_digest != self.post_probe_ba_state_digest
        ):
            raise E1ConfirmationSevenArmProbeError(
                "S1-EB6 changed a frozen E1 state"
            )
        for role in ("probe_ablation_residual", "fixed_adapter_residual"):
            value = getattr(self, role)
            if not math.isfinite(value) or value != 0.0:
                raise E1ConfirmationSevenArmProbeError(
                    f"S1-EB6 {role} is not exactly zero"
                )
        if (
            self.initial_fields_identical_and_separate is not True
            or self.supports_assigned_once is not True
        ):
            raise E1ConfirmationSevenArmProbeError(
                "S1-EB6 field identity or support control failed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if self.result_digest != _digest(payload):
            raise E1ConfirmationSevenArmProbeError(
                "S1-EB6 result digest does not match its payload"
            )
        object.__setattr__(self, "field_digests", fields)
        object.__setattr__(self, "ab_active_s", vectors[0])
        object.__setattr__(self, "ba_active_s", vectors[1])
        object.__setattr__(self, "ab_active_h", vectors[2])
        object.__setattr__(self, "ba_active_h", vectors[3])


def run_synthetic_e1_confirmation_seven_arm_probe(
    contract: E1RefinedConfirmationContract,
    formed: E1ConfirmationFormationResult,
    field_factory: Callable[[], SharedMCMField],
    probe_sequences: tuple[ReceptorTimeSequence, ...],
    probe_plan: E1ConfirmationRefinementPlan,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1ConfirmationProbeResult:
    """Run one noncanonical frozen probe without persistence or decisions."""

    if not isinstance(contract, E1RefinedConfirmationContract) or (
        contract.digest() != S1_EB_CONTRACT_DIGEST
    ):
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 requires the current S1-EB contract"
        )
    if not isinstance(formed, E1ConfirmationFormationResult):
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 requires one S1-EB3 formation result"
        )
    sequences = tuple(probe_sequences)
    if (
        tuple(item.modality_id for item in sequences) != ("auditory", "visual")
        or not all(isinstance(item, ReceptorTimeSequence) for item in sequences)
    ):
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 probe source changed"
        )
    source_digest = _probe_digest(sequences)
    if source_digest == S1_DS_PROBE_DIGEST:
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 rejects the canonical probe source"
        )
    if not isinstance(probe_plan, E1ConfirmationRefinementPlan) or (
        (formed.refinement_id, formed.factor)
        != (probe_plan.refinement_id, probe_plan.factor)
    ):
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 formation and probe refinement do not match"
        )
    steps = tuple(probe_plan.proposal_steps)
    expected = build_e1_confirmation_refinement_plans(
        contract,
        sequences,
        horizon_start_tick=probe_plan.horizon_start_tick,
        horizon_end_tick=probe_plan.horizon_end_tick,
        ticks_per_second=steps[0].ticks_per_second,
    )
    expected_plan = next(
        item
        for item in expected.plans
        if item.refinement_id == probe_plan.refinement_id
    )
    if expected_plan.digest() != probe_plan.digest():
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 probe plan does not match its synthetic source"
        )
    if (
        substrate_config != NeutralLocalFieldSubstrateConfig(1.0)
        or afterimage_config != NeutralFastAfterimageConfig(0.5)
        or not callable(field_factory)
    ):
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 field factory or configuration changed"
        )
    fields = tuple(field_factory() for _ in S1_EB6_FIELD_ROLES)
    if any(not isinstance(item, SharedMCMField) for item in fields) or len(
        {id(item) for item in fields}
    ) != len(fields):
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 requires seven object-separated fields"
        )
    initial_digests = tuple(_fresh_field_digest(item) for item in fields)
    if len(set(initial_digests)) != 1:
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 probe fields are not initially identical"
        )
    handoff = probe_plan.handoff
    supports_once = (
        handoff.assigned_event_count == sum(len(item.frames) for item in sequences)
        and handoff.every_in_horizon_event_assigned_once
        and not handoff.completed_before_or_at_start_snapshot_ids
        and not handoff.completed_after_horizon_snapshot_ids
    )
    if not supports_once:
        raise E1ConfirmationSevenArmProbeError(
            "S1-EB6 probe supports are not assigned exactly once"
        )

    current = list(fields)
    ab_state = formed.b_ab
    ba_state = formed.b_ba
    pre_ab_digest = _state_digest(ab_state)
    pre_ba_digest = _state_digest(ba_state)
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(
            batch, current[0].docks
        )
        inputs = project_transient_docks_to_neuron_inputs(
            trajectory, current[0].docks
        )
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        current[0] = advance_neutral_fast_shared_field_transient(
            current[0],
            distribution,
            inputs,
            substrate_config,
            afterimage_config,
        )
        ab_active = advance_frozen_e1_fast_shared_field_transient(
            current[1],
            ab_state,
            distribution,
            inputs,
            substrate_config,
            afterimage_config,
            backreaction_enabled=True,
        )
        ba_active = advance_frozen_e1_fast_shared_field_transient(
            current[2],
            ba_state,
            distribution,
            inputs,
            substrate_config,
            afterimage_config,
            backreaction_enabled=True,
        )
        ab_ablated = advance_frozen_e1_fast_shared_field_transient(
            current[3],
            ab_state,
            distribution,
            inputs,
            substrate_config,
            afterimage_config,
            backreaction_enabled=False,
        )
        ba_ablated = advance_frozen_e1_fast_shared_field_transient(
            current[4],
            ba_state,
            distribution,
            inputs,
            substrate_config,
            afterimage_config,
            backreaction_enabled=False,
        )
        current[1], current[2], current[3], current[4] = (
            ab_active.field,
            ba_active.field,
            ab_ablated.field,
            ba_ablated.field,
        )
        current[5] = advance_fixed_e1_adapter_fast_shared_field_transient(
            current[5],
            ab_active.applied_adapter,
            distribution,
            inputs,
            substrate_config,
            afterimage_config,
        )
        current[6] = advance_fixed_e1_adapter_fast_shared_field_transient(
            current[6],
            ba_active.applied_adapter,
            distribution,
            inputs,
            substrate_config,
            afterimage_config,
        )
        if (
            ab_active.e1_state is not ab_state
            or ab_ablated.e1_state is not ab_state
            or ba_active.e1_state is not ba_state
            or ba_ablated.e1_state is not ba_state
        ):
            raise E1ConfirmationSevenArmProbeError(
                "S1-EB6 changed a frozen E1 state object"
            )

    final = tuple(current)
    values = {
        "refinement_id": formed.refinement_id,
        "factor": formed.factor,
        "probe_source_digest": source_digest,
        "probe_plan_digest": probe_plan.digest(),
        "field_digests": tuple(
            (role, item.snapshot().digest())
            for role, item in zip(S1_EB6_FIELD_ROLES, final, strict=True)
        ),
        "ab_active_s": _vector(final[1], "s"),
        "ba_active_s": _vector(final[2], "s"),
        "ab_active_h": _vector(final[1], "h"),
        "ba_active_h": _vector(final[2], "h"),
        "pre_probe_ab_state_digest": pre_ab_digest,
        "pre_probe_ba_state_digest": pre_ba_digest,
        "post_probe_ab_state_digest": _state_digest(ab_state),
        "post_probe_ba_state_digest": _state_digest(ba_state),
        "probe_ablation_residual": _max_distance(
            final[0], (final[3], final[4])
        ),
        "fixed_adapter_residual": max(
            _max_distance(final[1], (final[5],)),
            _max_distance(final[2], (final[6],)),
        ),
        "initial_fields_identical_and_separate": True,
        "supports_assigned_once": supports_once,
    }
    return E1ConfirmationProbeResult(
        **values,
        result_digest=_digest(values),
    )
