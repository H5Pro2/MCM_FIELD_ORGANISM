"""Bounded multi-arm F3 runner over one shared receptor event handoff."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

from .field_step_time import MCMFieldStepTime
from .mcm_f3_runtime import (
    MCMF3AdvanceDiagnostics,
    activate_mcm_f3_field,
    advance_mcm_f3_shared_field_transient,
)
from .mcm_substrate_state import MCMSubstrateArmContract
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff_audit import (
    ReceptorProposalHandoff,
    handoff_receptor_completion_groups,
)
from .receptor_time_alignment import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField, attach_uniform_mcm_substrate
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class MCMF3CausalRunnerError(ValueError):
    """Raised when comparison arms would not share one causal input boundary."""


_ARM_KEYS = (
    "p0.exact",
    "p1.n",
    "p1.2n",
    "p1.4n",
    "b.eta-null",
    "b.kappa-null",
    "b.kappa-inverted",
)


@dataclass(frozen=True, slots=True)
class MCMF3CausalArmRun:
    """One completed arm over the common bounded receptor handoff."""

    arm_key: str
    refinement: int
    field: SharedMCMField
    diagnostics: tuple[MCMF3AdvanceDiagnostics, ...]

    def __post_init__(self) -> None:
        if self.arm_key not in _ARM_KEYS:
            raise MCMF3CausalRunnerError("unknown F3 causal arm key")
        if (
            isinstance(self.refinement, bool)
            or not isinstance(self.refinement, int)
            or self.refinement < 1
        ):
            raise MCMF3CausalRunnerError("arm refinement must be positive")
        if not isinstance(self.field, SharedMCMField):
            raise MCMF3CausalRunnerError("arm result requires one shared field")
        diagnostics = tuple(self.diagnostics)
        if not diagnostics or any(
            not isinstance(item, MCMF3AdvanceDiagnostics) for item in diagnostics
        ):
            raise MCMF3CausalRunnerError(
                "arm result requires diagnostics for every proposal batch"
            )
        object.__setattr__(self, "diagnostics", diagnostics)


@dataclass(frozen=True, slots=True)
class MCMF3CausalComparison:
    """All fixed F3 arms after exactly one shared receptor handoff."""

    handoff: ReceptorProposalHandoff
    source_support_count: int
    arms: tuple[MCMF3CausalArmRun, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.handoff, ReceptorProposalHandoff):
            raise MCMF3CausalRunnerError(
                "causal comparison requires one receptor handoff"
            )
        if (
            isinstance(self.source_support_count, bool)
            or not isinstance(self.source_support_count, int)
            or self.source_support_count < 1
        ):
            raise MCMF3CausalRunnerError(
                "causal comparison requires source supports"
            )
        arms = tuple(self.arms)
        if tuple(item.arm_key for item in arms) != _ARM_KEYS:
            raise MCMF3CausalRunnerError(
                "causal comparison requires every fixed arm exactly once"
            )
        object.__setattr__(self, "arms", arms)

    def arm(self, arm_key: str) -> MCMF3CausalArmRun:
        for item in self.arms:
            if item.arm_key == arm_key:
                return item
        raise KeyError(arm_key)


def _source_support_key(
    sequence: ReceptorTimeSequence,
    frame_index: int,
) -> tuple:
    frame = sequence.frames[frame_index].frame
    return (
        frame.modality_id,
        frame.clock_id,
        frame.window_start_tick,
        frame.window_end_tick,
    )


def _validate_unique_source_supports(
    sequences: tuple[ReceptorTimeSequence, ...],
) -> int:
    seen: dict[tuple, tuple[float, ...]] = {}
    for sequence in sequences:
        for frame_index, timed_frame in enumerate(sequence.frames):
            key = _source_support_key(sequence, frame_index)
            if key in seen:
                if seen[key] != timed_frame.frame.values:
                    raise MCMF3CausalRunnerError(
                        "conflicting completions share one source support"
                    )
                raise MCMF3CausalRunnerError(
                    "duplicate completion of one source support"
                )
            seen[key] = timed_frame.frame.values
    return len(seen)


def _derived_arm(
    arm_id: str,
    active_arm: MCMSubstrateArmContract,
    *,
    lambda_sm_per_second: float | None = None,
    kappa: float | None = None,
    eta: float | None = None,
) -> MCMSubstrateArmContract:
    return MCMSubstrateArmContract(
        arm_id=arm_id,
        lambda_sm_per_second=(
            active_arm.lambda_sm_per_second
            if lambda_sm_per_second is None
            else lambda_sm_per_second
        ),
        kappa=active_arm.kappa if kappa is None else kappa,
        eta=active_arm.eta if eta is None else eta,
        initial_total_mass=active_arm.initial_total_mass,
    )


def run_mcm_f3_causal_comparison(
    base_field: SharedMCMField,
    sequences: Iterable[ReceptorTimeSequence],
    proposal_steps: Iterable[MCMFieldStepTime],
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    active_arm: MCMSubstrateArmContract,
    *,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> MCMF3CausalComparison:
    """Run every fixed arm over the exact same bounded receptor events."""

    if not isinstance(base_field, SharedMCMField):
        raise MCMF3CausalRunnerError(
            "causal comparison requires one shared base field"
        )
    if base_field.substrate is not None:
        raise MCMF3CausalRunnerError(
            "causal comparison base field must not contain a substrate"
        )
    if not isinstance(active_arm, MCMSubstrateArmContract) or active_arm.is_null_arm:
        raise MCMF3CausalRunnerError(
            "causal comparison requires one active reference arm"
        )
    sequences_in = tuple(sequences)
    if not sequences_in or any(
        not isinstance(item, ReceptorTimeSequence) for item in sequences_in
    ):
        raise MCMF3CausalRunnerError(
            "causal comparison requires receptor time sequences"
        )
    steps_in = tuple(proposal_steps)
    if not steps_in or any(not isinstance(item, MCMFieldStepTime) for item in steps_in):
        raise MCMF3CausalRunnerError(
            "causal comparison requires proposal steps"
        )

    source_support_count = _validate_unique_source_supports(sequences_in)
    try:
        handoff = handoff_receptor_completion_groups(sequences_in, steps_in)
    except ValueError as exc:
        raise MCMF3CausalRunnerError(str(exc)) from exc
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
    ):
        raise MCMF3CausalRunnerError(
            "every supplied completion must remain inside the common horizon"
        )
    if (
        not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != source_support_count
    ):
        raise MCMF3CausalRunnerError(
            "every unique source support must be assigned exactly once"
        )

    p0_arm = _derived_arm(
        "p0.null",
        active_arm,
        lambda_sm_per_second=0.0,
    )
    eta_null_arm = _derived_arm("b.eta-null", active_arm, eta=0.0)
    kappa_null_arm = _derived_arm("b.kappa-null", active_arm, kappa=0.0)
    kappa_inverted_arm = _derived_arm(
        "b.kappa-inverted",
        active_arm,
        kappa=-active_arm.kappa,
    )
    current = {
        "p0.exact": attach_uniform_mcm_substrate(base_field, p0_arm),
        "p1.n": activate_mcm_f3_field(base_field, active_arm),
        "p1.2n": activate_mcm_f3_field(base_field, active_arm),
        "p1.4n": activate_mcm_f3_field(base_field, active_arm),
        "b.eta-null": activate_mcm_f3_field(base_field, eta_null_arm),
        "b.kappa-null": activate_mcm_f3_field(base_field, kappa_null_arm),
        "b.kappa-inverted": activate_mcm_f3_field(
            base_field,
            kappa_inverted_arm,
        ),
    }
    refinements = {
        "p0.exact": 1,
        "p1.n": 1,
        "p1.2n": 2,
        "p1.4n": 4,
        "b.eta-null": 4,
        "b.kappa-null": 4,
        "b.kappa-inverted": 4,
    }
    diagnostics: dict[str, list[MCMF3AdvanceDiagnostics]] = {
        key: [] for key in _ARM_KEYS
    }

    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(
            batch,
            base_field.docks,
        )
        local_inputs = project_transient_docks_to_neuron_inputs(
            trajectory,
            base_field.docks,
        )
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        for arm_key in _ARM_KEYS:
            result = advance_mcm_f3_shared_field_transient(
                current[arm_key],
                distribution,
                local_inputs,
                substrate_config,
                afterimage_config,
                dissipation_config,
                refinement=refinements[arm_key],
            )
            current[arm_key] = result.field
            diagnostics[arm_key].append(result.diagnostics)

    return MCMF3CausalComparison(
        handoff=handoff,
        source_support_count=source_support_count,
        arms=tuple(
            MCMF3CausalArmRun(
                arm_key=arm_key,
                refinement=refinements[arm_key],
                field=current[arm_key],
                diagnostics=tuple(diagnostics[arm_key]),
            )
            for arm_key in _ARM_KEYS
        ),
    )


def mcm_f3_causal_runner_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (MCMF3CausalArmRun, MCMF3CausalComparison)
        for item in fields(cls)
    )
