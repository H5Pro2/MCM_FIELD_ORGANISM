"""Pure post-consumption evaluator for the bounded S2-GK task."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from tools import _s2gk_private_direct_mask_fill_baseline as baseline
from tools import _s2gk_private_masked_visual_context_consumer as consumer


S2GK_EVALUATOR_SCHEMA = "s2gk.masked-visual-completion-evaluator.v1"
CASE_KINDS = (
    "CORRECT_CONTEXT",
    "FOREIGN_CONTEXT",
    "ABSENT_CONTEXT",
    "CONFLICT_CONTEXT",
)
EVALUATION_STATUSES = (
    "S2GJ_FUNCTION_VALID_DIRECT_MASK_FILL_EXPLAINS",
    "S2GJ_FOREIGN_CONTEXT_LIMIT_OBSERVED",
    "S2GJ_CONTROL_VALID",
    "S2GJ_FUNCTION_FALSIFIED",
    "S2GJ_NOT_EVALUABLE",
)

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class MaskedVisualTargetFixture:
    values: tuple[float, ...]
    fixture_digest: str
    schema: str = S2GK_EVALUATOR_SCHEMA

    def __post_init__(self) -> None:
        if not (
            type(self.values) is tuple
            and len(self.values) == 18
            and all(
                type(value) in (int, float)
                and math.isfinite(float(value))
                and -1.0 <= float(value) <= 1.0
                for value in self.values
            )
        ):
            raise ValueError("target fixture must contain exactly 18 finite values")
        if not (
            self.schema == S2GK_EVALUATOR_SCHEMA
            and self.fixture_digest == _digest(self.payload_without_digest())
        ):
            raise ValueError("target fixture digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {"schema": self.schema, "values": list(self.values)}

    @classmethod
    def build(cls, values: tuple[float, ...]) -> "MaskedVisualTargetFixture":
        payload = {"schema": S2GK_EVALUATOR_SCHEMA, "values": list(values)}
        return cls(values, _digest(payload))


@dataclass(frozen=True, slots=True)
class CompletionEvaluation:
    case_kind: str
    status: str
    visible_preservation_count: int | None
    completed_mask_count: int | None
    masked_mean_absolute_error: float | None
    full_mean_absolute_error: float | None
    baseline_equivalent: bool | None
    consumer_result_digest: str | None
    baseline_result_digest: str | None
    fixture_digest: str
    evaluation_digest: str
    schema: str = S2GK_EVALUATOR_SCHEMA

    def __post_init__(self) -> None:
        if self.case_kind not in CASE_KINDS or self.status not in EVALUATION_STATUSES:
            raise ValueError("evaluation case or status differs")
        for count in (self.visible_preservation_count, self.completed_mask_count):
            if count is not None and (type(count) is not int or not 0 <= count <= 9):
                raise ValueError("evaluation count differs")
        for value in (self.masked_mean_absolute_error, self.full_mean_absolute_error):
            if value is not None and (not math.isfinite(value) or value < 0.0):
                raise ValueError("evaluation error metric differs")
        if self.baseline_equivalent is not None and type(self.baseline_equivalent) is not bool:
            raise ValueError("baseline equivalence differs")
        if not _valid_digest(self.fixture_digest):
            raise ValueError("evaluation fixture digest differs")
        if self.consumer_result_digest is not None and not _valid_digest(self.consumer_result_digest):
            raise ValueError("consumer result digest differs")
        if self.baseline_result_digest is not None and not _valid_digest(self.baseline_result_digest):
            raise ValueError("baseline result digest differs")
        if not (
            self.schema == S2GK_EVALUATOR_SCHEMA
            and self.evaluation_digest == _digest(self.payload_without_digest())
        ):
            raise ValueError("evaluation digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "case_kind": self.case_kind,
            "status": self.status,
            "visible_preservation_count": self.visible_preservation_count,
            "completed_mask_count": self.completed_mask_count,
            "masked_mean_absolute_error": self.masked_mean_absolute_error,
            "full_mean_absolute_error": self.full_mean_absolute_error,
            "baseline_equivalent": self.baseline_equivalent,
            "consumer_result_digest": self.consumer_result_digest,
            "baseline_result_digest": self.baseline_result_digest,
            "fixture_digest": self.fixture_digest,
        }


def _build_evaluation(
    *,
    case_kind: str,
    status: str,
    fixture: MaskedVisualTargetFixture,
    visible_count: int | None,
    completed_count: int | None,
    masked_error: float | None,
    full_error: float | None,
    baseline_equivalent: bool | None,
    consumer_digest: str | None,
    baseline_digest: str | None,
) -> CompletionEvaluation:
    payload = {
        "schema": S2GK_EVALUATOR_SCHEMA,
        "case_kind": case_kind,
        "status": status,
        "visible_preservation_count": visible_count,
        "completed_mask_count": completed_count,
        "masked_mean_absolute_error": masked_error,
        "full_mean_absolute_error": full_error,
        "baseline_equivalent": baseline_equivalent,
        "consumer_result_digest": consumer_digest,
        "baseline_result_digest": baseline_digest,
        "fixture_digest": fixture.fixture_digest,
    }
    return CompletionEvaluation(
        case_kind,
        status,
        visible_count,
        completed_count,
        masked_error,
        full_error,
        baseline_equivalent,
        consumer_digest,
        baseline_digest,
        fixture.fixture_digest,
        _digest(payload),
    )


def _not_evaluable(
    case_kind: str,
    fixture: MaskedVisualTargetFixture,
    consumer_digest: str | None,
    baseline_digest: str | None,
) -> CompletionEvaluation:
    return _build_evaluation(
        case_kind=case_kind,
        status="S2GJ_NOT_EVALUABLE",
        fixture=fixture,
        visible_count=None,
        completed_count=None,
        masked_error=None,
        full_error=None,
        baseline_equivalent=None,
        consumer_digest=consumer_digest if _valid_digest(consumer_digest) else None,
        baseline_digest=baseline_digest if _valid_digest(baseline_digest) else None,
    )


def _errors(
    values: tuple[float | None, ...],
    fixture: MaskedVisualTargetFixture,
) -> tuple[float | None, float | None]:
    if any(value is None for value in values):
        return None, None
    normalized = tuple(float(value) for value in values)
    masked = sum(
        abs(normalized[index] - float(fixture.values[index]))
        for index in consumer.MASKED_POSITIONS
    ) / 9.0
    full = sum(
        abs(normalized[index] - float(fixture.values[index])) for index in range(18)
    ) / 18.0
    return masked, full


def evaluate_completion_case(
    case_kind: str,
    fixture: MaskedVisualTargetFixture,
    current_only: consumer.MaskedVisualCompletionResult,
    context_result: consumer.MaskedVisualCompletionResult,
    direct_result: baseline.DirectMaskFillResult | None = None,
) -> CompletionEvaluation:
    """Evaluate already completed outputs; no consumer or baseline call occurs."""

    if type(fixture) is not MaskedVisualTargetFixture:
        raise TypeError("exact target fixture required")
    try:
        fixture.__post_init__()
    except ValueError:
        raise
    if case_kind not in CASE_KINDS:
        raise ValueError("unknown evaluation case")

    consumer_digest = getattr(context_result, "result_digest", None)
    baseline_digest = None if direct_result is None else getattr(direct_result, "result_digest", None)
    try:
        if type(current_only) is not consumer.MaskedVisualCompletionResult:
            raise TypeError
        if type(context_result) is not consumer.MaskedVisualCompletionResult:
            raise TypeError
        current_only.__post_init__()
        context_result.__post_init__()
        if direct_result is not None:
            if type(direct_result) is not baseline.DirectMaskFillResult:
                raise TypeError
            direct_result.__post_init__()
    except (TypeError, ValueError, consumer.S2GKConsumerError, baseline.S2GKBaselineError):
        return _not_evaluable(case_kind, fixture, consumer_digest, baseline_digest)

    if not (
        current_only.method == consumer.METHOD_CURRENT_ONLY
        and current_only.status == "INSUFFICIENT_INFORMATION"
        and context_result.method == consumer.METHOD_PLUS_CONTEXT
        and current_only.probe_digest == context_result.probe_digest
        and current_only.probe_source_digest == context_result.probe_source_digest
        and current_only.input_values == context_result.input_values
    ):
        return _not_evaluable(case_kind, fixture, consumer_digest, baseline_digest)

    if direct_result is not None and not (
        direct_result.probe_digest == context_result.probe_digest
        and direct_result.probe_source_digest == context_result.probe_source_digest
        and direct_result.input_values == context_result.input_values
        and direct_result.context_bundle_digest == context_result.context_bundle_digest
        and direct_result.context_source_digest == context_result.context_source_digest
        and direct_result.prestate_digest == context_result.prestate_digest
        and direct_result.poststate_digest == context_result.poststate_digest
    ):
        return _not_evaluable(case_kind, fixture, consumer_digest, baseline_digest)

    visible_count = sum(
        current_only.input_values[index] == fixture.values[index]
        and context_result.output_values[index] == current_only.input_values[index]
        for index in consumer.VISIBLE_POSITIONS
    )
    if visible_count != 9:
        return _not_evaluable(case_kind, fixture, consumer_digest, baseline_digest)

    completed_count = len(context_result.completed_positions)
    masked_error, full_error = _errors(context_result.output_values, fixture)
    equivalent = None
    if direct_result is not None:
        equivalent = (
            direct_result.output_values == context_result.output_values
            and direct_result.completed_positions == context_result.completed_positions
            and direct_result.resource_ledger.mask_validation_count
            == context_result.resource_ledger.mask_validation_count
            and direct_result.resource_ledger.visible_compare_count
            == context_result.resource_ledger.visible_compare_count
            and direct_result.resource_ledger.masked_copy_count
            == context_result.resource_ledger.masked_copy_count
            and direct_result.resource_ledger.area_lookup_count
            == context_result.resource_ledger.area_lookup_count
            and direct_result.resource_ledger.candidate_reference_count
            == context_result.resource_ledger.candidate_reference_count
            and direct_result.resource_ledger.value_reference_count
            == context_result.resource_ledger.value_reference_count
        )

    if case_kind == "CORRECT_CONTEXT":
        success = (
            direct_result is not None
            and context_result.status == "CONTEXT_COMPLETED"
            and direct_result.status == "DIRECT_COMPLETED"
            and completed_count == 9
            and masked_error == 0.0
            and equivalent is True
        )
        status = (
            "S2GJ_FUNCTION_VALID_DIRECT_MASK_FILL_EXPLAINS"
            if success
            else "S2GJ_FUNCTION_FALSIFIED"
        )
    elif case_kind == "FOREIGN_CONTEXT":
        observed = (
            direct_result is not None
            and context_result.status == "CONTEXT_COMPLETED"
            and direct_result.status == "DIRECT_COMPLETED"
            and completed_count == 9
            and masked_error is not None
            and masked_error > 0.0
            and equivalent is True
        )
        status = (
            "S2GJ_FOREIGN_CONTEXT_LIMIT_OBSERVED"
            if observed
            else "S2GJ_FUNCTION_FALSIFIED"
        )
    elif case_kind == "ABSENT_CONTEXT":
        control = (
            context_result.status == "CONTEXT_ABSENT"
            and completed_count == 0
            and context_result.output_values == current_only.output_values
        )
        status = "S2GJ_CONTROL_VALID" if control else "S2GJ_FUNCTION_FALSIFIED"
    else:
        control = (
            context_result.status == "CONTEXT_CONFLICT"
            and completed_count == 0
            and context_result.output_values == current_only.output_values
        )
        status = "S2GJ_CONTROL_VALID" if control else "S2GJ_FUNCTION_FALSIFIED"

    return _build_evaluation(
        case_kind=case_kind,
        status=status,
        fixture=fixture,
        visible_count=visible_count,
        completed_count=completed_count,
        masked_error=masked_error,
        full_error=full_error,
        baseline_equivalent=equivalent,
        consumer_digest=context_result.result_digest,
        baseline_digest=None if direct_result is None else direct_result.result_digest,
    )


__all__: tuple[str, ...] = ()
