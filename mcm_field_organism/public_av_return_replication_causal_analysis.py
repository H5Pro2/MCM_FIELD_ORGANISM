"""Technical causal-contrast analysis for the preregistered six-arm result."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .public_av_return_replication_execution import PublicAVReturnReplicationExecution
from .public_av_return_replication_preregistration import (
    public_av_return_replication_preregistration,
)


class PublicAVReturnReplicationCausalAnalysisError(ValueError):
    """Raised when analysis exceeds the preregistered technical contrasts."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnTechnicalContrast:
    causal_question: str
    left_arm_id: str
    right_arm_id: str
    activation_linf: float
    afterimage_linf: float
    layer_digest_equal: bool
    snapshot_digest_equal: bool
    activation_technically_distinct: bool
    afterimage_technically_distinct: bool
    field_digest_technically_distinct: bool


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationCausalAnalysis:
    execution_id: str
    preregistration_id: str
    primary_contrasts: tuple[PublicAVReturnTechnicalContrast, ...]
    component_auxiliary_contrasts: tuple[PublicAVReturnTechnicalContrast, ...]
    all_stage_one_snapshots_equal: bool
    thresholds_defined: bool
    causal_mechanism_proven: bool
    memory_claim_allowed: bool
    organization_claim_allowed: bool
    meaning_claim_allowed: bool
    ai_claim_allowed: bool

    def __post_init__(self) -> None:
        if len(self.primary_contrasts) != 4 or len(self.component_auxiliary_contrasts) != 2:
            raise PublicAVReturnReplicationCausalAnalysisError("four primary and two component contrasts are required")
        if any((
            self.thresholds_defined,
            self.causal_mechanism_proven,
            self.memory_claim_allowed,
            self.organization_claim_allowed,
            self.meaning_claim_allowed,
            self.ai_claim_allowed,
        )):
            raise PublicAVReturnReplicationCausalAnalysisError("analysis cannot define thresholds or release claims")
        object.__setattr__(self, "primary_contrasts", tuple(self.primary_contrasts))
        object.__setattr__(self, "component_auxiliary_contrasts", tuple(self.component_auxiliary_contrasts))


def analyze_public_av_return_replication_causal_contrasts(
    execution: PublicAVReturnReplicationExecution,
) -> PublicAVReturnReplicationCausalAnalysis:
    if not isinstance(execution, PublicAVReturnReplicationExecution):
        raise PublicAVReturnReplicationCausalAnalysisError("six-arm execution result is required")
    plan = public_av_return_replication_preregistration()
    arm_index = {arm.arm_id: index for index, arm in enumerate(execution.arms)}

    def contrast(question: str, left: str, right: str) -> PublicAVReturnTechnicalContrast:
        i, j = arm_index[left], arm_index[right]
        activation = execution.pairwise_activation_linf[i][j]
        afterimage = execution.pairwise_afterimage_linf[i][j]
        layer_equal = execution.layer_digest_equality[i][j]
        snapshot_equal = execution.snapshot_digest_equality[i][j]
        return PublicAVReturnTechnicalContrast(
            causal_question=question,
            left_arm_id=left,
            right_arm_id=right,
            activation_linf=activation,
            afterimage_linf=afterimage,
            layer_digest_equal=layer_equal,
            snapshot_digest_equal=snapshot_equal,
            activation_technically_distinct=activation > 0.0,
            afterimage_technically_distinct=afterimage > 0.0,
            field_digest_technically_distinct=not layer_equal or not snapshot_equal,
        )

    questions = plan.causal_questions
    full = "return.continued.full_state"
    fresh = "return.fresh_stage_two"
    activation_only = "control.activation_only_carry"
    afterimage_only = "control.afterimage_only_carry"
    permuted = "control.stage_two_order_permuted"
    withheld = "control.stage_two_sequence_withheld"
    primary = (
        contrast(questions[0], full, fresh),
        contrast(questions[1], activation_only, afterimage_only),
        contrast(questions[2], full, permuted),
        contrast(questions[3], full, withheld),
    )
    auxiliary = (
        contrast(questions[1], full, activation_only),
        contrast(questions[1], fresh, afterimage_only),
    )
    stage_one = {arm.stage_one_snapshot_digest for arm in execution.arms}
    return PublicAVReturnReplicationCausalAnalysis(
        execution_id=execution.execution_id,
        preregistration_id=plan.preregistration_id,
        primary_contrasts=primary,
        component_auxiliary_contrasts=auxiliary,
        all_stage_one_snapshots_equal=len(stage_one) == 1,
        thresholds_defined=False,
        causal_mechanism_proven=False,
        memory_claim_allowed=False,
        organization_claim_allowed=False,
        meaning_claim_allowed=False,
        ai_claim_allowed=False,
    )


def public_av_return_replication_causal_analysis_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVReturnTechnicalContrast, PublicAVReturnReplicationCausalAnalysis)
        for item in fields(cls)
    )
