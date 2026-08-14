"""S1-EC35 static audit of the EC34 P0 identifiability boundary."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .e1_refined_formation_runner import _digest
from .e1_repetition_formation_planner import E1RepetitionFormationPlanSet
from .e1_repetition_pilot_once_runner import (
    E1PilotOnceArmMeasurement,
    E1PilotOnceBatchContrast,
)
from .e1_repetition_pilot_release_contract import E1RepetitionPilotReleaseContract


class E1RepetitionPilotP0IdentifiabilityAuditError(ValueError):
    """Raised when S1-EC35 cannot preserve its static-only boundary."""


S1_EC35_AUDIT_ID = "e1.repetition-pilot-p0-identifiability-audit.s1ec35.v1"
S1_EC35_DECISION = "P0_MAGNITUDE_NOT_IDENTIFIABLE_FROM_EC34_SCHEMA"
S1_EC35_REQUIRED_CHECKS = (
    "n1-schedules-time-identical",
    "n2-schedules-time-distinct",
    "n2-exposure-and-final-completion-matched",
    "p0-measurement-retains-digest-only",
    "p0-contrast-retains-equality-only",
    "no-p0-component-distance-retained",
    "no-new-field-execution",
    "no-result-or-memory-claim",
)


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotP0IdentifiabilityAudit:
    audit_id: str
    source_contract_digest: str
    source_plan_set_digest: str
    checks: tuple[tuple[str, bool], ...]
    decision: str
    causal_note: str
    missing_measurements: tuple[str, ...]
    corrected_runner_implementation_permitted: bool
    field_execution_permitted: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.audit_id != S1_EC35_AUDIT_ID
            or len(self.source_contract_digest) != 64
            or len(self.source_plan_set_digest) != 64
            or tuple(name for name, _ in self.checks) != S1_EC35_REQUIRED_CHECKS
            or not all(value for _, value in self.checks)
            or self.decision != S1_EC35_DECISION
            or self.causal_note
            != "equal-exposure-does-not-imply-equal-terminal-dynamic-state"
            or self.missing_measurements
            != (
                "p0-terminal-activation-linf",
                "p0-terminal-afterimage-linf",
                "p0-r2-r4-r8-component-residuals",
            )
            or self.corrected_runner_implementation_permitted is not True
            or any(
                value is not False
                for value in (
                    self.field_execution_permitted,
                    self.result_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotP0IdentifiabilityAuditError(
                "S1-EC35 audit changed or exceeded static scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1RepetitionPilotP0IdentifiabilityAuditError(
                "S1-EC35 audit digest changed"
            )


def audit_e1_repetition_pilot_p0_identifiability(
    contract: E1RepetitionPilotReleaseContract,
    plans: E1RepetitionFormationPlanSet,
) -> E1RepetitionPilotP0IdentifiabilityAudit:
    """Audit retained P0 observables without consuming the EC34 raw result."""

    if not isinstance(contract, E1RepetitionPilotReleaseContract):
        raise E1RepetitionPilotP0IdentifiabilityAuditError(
            "S1-EC35 requires the EC29 contract"
        )
    if not isinstance(plans, E1RepetitionFormationPlanSet):
        raise E1RepetitionPilotP0IdentifiabilityAuditError(
            "S1-EC35 requires the EC27 plan set"
        )
    contract.__post_init__()
    plans.__post_init__()
    if plans.plan_set_digest != contract.source_plan_set_digest:
        raise E1RepetitionPilotP0IdentifiabilityAuditError(
            "S1-EC35 upstream plans changed"
        )
    n1, n2 = plans.pairs[:2]
    measurement_roles = tuple(item.name for item in fields(E1PilotOnceArmMeasurement))
    contrast_roles = tuple(item.name for item in fields(E1PilotOnceBatchContrast))
    n1_repeated_times = tuple(
        (item.field_time.window_start_tick, item.field_time.window_end_tick)
        for sequence in n1.repeated_sequences
        for item in sequence.frames
    )
    n1_continuous_times = tuple(
        (item.field_time.window_start_tick, item.field_time.window_end_tick)
        for sequence in n1.continuous_sequences
        for item in sequence.frames
    )
    n2_repeated_times = tuple(
        (item.field_time.window_start_tick, item.field_time.window_end_tick)
        for sequence in n2.repeated_sequences
        for item in sequence.frames
    )
    n2_continuous_times = tuple(
        (item.field_time.window_start_tick, item.field_time.window_end_tick)
        for sequence in n2.continuous_sequences
        for item in sequence.frames
    )
    checks = (
        ("n1-schedules-time-identical", n1_repeated_times == n1_continuous_times),
        ("n2-schedules-time-distinct", n2_repeated_times != n2_continuous_times),
        ("n2-exposure-and-final-completion-matched", (
            n2.total_exposure_identical
            and max(end for _, end in n2_repeated_times)
            == max(end for _, end in n2_continuous_times)
        )),
        ("p0-measurement-retains-digest-only", (
            "output_digest" in measurement_roles
            and "output_activation" not in measurement_roles
            and "output_afterimage" not in measurement_roles
        )),
        ("p0-contrast-retains-equality-only", (
            "p0_output_digests_equal" in contrast_roles
        )),
        ("no-p0-component-distance-retained", (
            "p0_activation_linf" not in contrast_roles
            and "p0_afterimage_linf" not in contrast_roles
        )),
        ("no-new-field-execution", True),
        ("no-result-or-memory-claim", True),
    )
    if not all(value for _, value in checks):
        raise E1RepetitionPilotP0IdentifiabilityAuditError(
            "S1-EC35 static checks failed"
        )
    payload = {
        "audit_id": S1_EC35_AUDIT_ID,
        "source_contract_digest": contract.contract_digest,
        "source_plan_set_digest": plans.plan_set_digest,
        "checks": checks,
        "decision": S1_EC35_DECISION,
        "causal_note": (
            "equal-exposure-does-not-imply-equal-terminal-dynamic-state"
        ),
        "missing_measurements": (
            "p0-terminal-activation-linf",
            "p0-terminal-afterimage-linf",
            "p0-r2-r4-r8-component-residuals",
        ),
        "corrected_runner_implementation_permitted": True,
        "field_execution_permitted": False,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1RepetitionPilotP0IdentifiabilityAudit(
        **payload,
        audit_digest=_digest(payload),
    )

