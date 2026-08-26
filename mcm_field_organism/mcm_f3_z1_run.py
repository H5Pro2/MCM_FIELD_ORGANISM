"""One-shot research entry point for preregistered Z1 Lauf 195."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields

from .mcm_f3_z1_evaluation import (
    MCMF3Z1EvaluationResult,
    evaluate_mcm_f3_z1_packet,
)
from .mcm_f3_z1_runner import execute_mcm_f3_z1_technical_packet


class MCMF3Z1RunError(ValueError):
    """Raised when the fixed Lauf-195 result contract changes."""


@dataclass(frozen=True, slots=True)
class MCMF3Z1RunResult:
    run_id: str
    evaluation: MCMF3Z1EvaluationResult

    def __post_init__(self) -> None:
        if self.run_id != "lauf-195":
            raise MCMF3Z1RunError("Z1 run identity changed")
        if not isinstance(self.evaluation, MCMF3Z1EvaluationResult):
            raise MCMF3Z1RunError("Z1 run requires one preregistered evaluation")


def execute_mcm_f3_z1_run() -> MCMF3Z1RunResult:
    """Execute the real Z1 matrix once and immediately apply the fixed evaluation."""

    packet = execute_mcm_f3_z1_technical_packet()
    return MCMF3Z1RunResult("lauf-195", evaluate_mcm_f3_z1_packet(packet))


def mcm_f3_z1_run_json_value(result: MCMF3Z1RunResult) -> dict[str, object]:
    if not isinstance(result, MCMF3Z1RunResult):
        raise MCMF3Z1RunError("Z1 JSON projection requires one run result")
    payload = asdict(result)
    payload["schema_id"] = "mcm.f3.z1.run.v1"
    return payload


def mcm_f3_z1_run_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(MCMF3Z1RunResult))
