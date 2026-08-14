"""One-shot corrected decision-support entry point for Z1 Lauf 196."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields

from .mcm_f3_z1_completion_support import (
    MCMF3Z1CompletionSupportAudit,
    apply_mcm_f3_z1_completion_support,
)
from .mcm_f3_z1_evaluation import (
    MCMF3Z1EvaluationResult,
    evaluate_mcm_f3_z1_packet,
)
from .mcm_f3_z1_runner import execute_mcm_f3_z1_technical_packet


class MCMF3Z1Run196Error(ValueError):
    """Raised when the corrected Lauf-196 result contract changes."""


@dataclass(frozen=True, slots=True)
class MCMF3Z1Run196SupportMeasurement:
    arm_id: str
    full_sample_count: int
    decision_sample_count: int
    full_support_unchanged: bool

    def __post_init__(self) -> None:
        for role in ("full_sample_count", "decision_sample_count"):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 2:
                raise MCMF3Z1Run196Error("Lauf-196 support count is invalid")
        if self.decision_sample_count > self.full_sample_count:
            raise MCMF3Z1Run196Error("Lauf-196 decision support exceeds full support")


@dataclass(frozen=True, slots=True)
class MCMF3Z1Run196Result:
    run_id: str
    correction_id: str
    support_controls: tuple[tuple[str, bool], ...]
    support_measurements: tuple[MCMF3Z1Run196SupportMeasurement, ...]
    evaluation: MCMF3Z1EvaluationResult

    def __post_init__(self) -> None:
        if self.run_id != "lauf-196":
            raise MCMF3Z1Run196Error("Z1 corrected run identity changed")
        if self.correction_id != "mcm.f3.z1.completion-support.v1":
            raise MCMF3Z1Run196Error("Z1 correction identity changed")
        if tuple(name for name, _ in self.support_controls) != (
            "source_contracts_match",
            "all_required_ticks_present",
            "reference_partition_support_equal",
            "nonpartition_support_unchanged",
            "partition_empty_support_removed",
        ):
            raise MCMF3Z1Run196Error("Lauf-196 support controls changed")
        if len(self.support_measurements) != 7:
            raise MCMF3Z1Run196Error("Lauf-196 requires seven support measurements")
        if not isinstance(self.evaluation, MCMF3Z1EvaluationResult):
            raise MCMF3Z1Run196Error("Lauf-196 requires one fixed Z1 evaluation")


def _support_measurements(
    audit: MCMF3Z1CompletionSupportAudit,
) -> tuple[MCMF3Z1Run196SupportMeasurement, ...]:
    return tuple(
        MCMF3Z1Run196SupportMeasurement(
            item.arm_id,
            item.full_sample_count,
            item.decision_sample_count,
            item.full_support_unchanged,
        )
        for item in audit.arms
    )


def execute_mcm_f3_z1_run196() -> MCMF3Z1Run196Result:
    """Execute the corrected matrix once and apply only completion support."""

    full_packet = execute_mcm_f3_z1_technical_packet()
    support = apply_mcm_f3_z1_completion_support(full_packet)
    if not all(value for _, value in support.controls):
        raise MCMF3Z1Run196Error("Lauf-196 completion-support controls failed")
    evaluation = evaluate_mcm_f3_z1_packet(support.packet)
    return MCMF3Z1Run196Result(
        "lauf-196",
        support.support_id,
        support.controls,
        _support_measurements(support),
        evaluation,
    )


def mcm_f3_z1_run196_json_value(
    result: MCMF3Z1Run196Result,
) -> dict[str, object]:
    if not isinstance(result, MCMF3Z1Run196Result):
        raise MCMF3Z1Run196Error("Lauf-196 JSON projection requires one result")
    payload = asdict(result)
    payload["schema_id"] = "mcm.f3.z1.run196.v1"
    return payload


def mcm_f3_z1_run196_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (MCMF3Z1Run196SupportMeasurement, MCMF3Z1Run196Result)
        for item in fields(cls)
    )
