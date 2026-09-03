"""Pure post-hoc evaluator for the private S2-KK context task."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from tools import _s2kk_context_utility_baselines as baselines
from tools import _s2kk_context_utility_fixtures as fixtures
from tools import _s2kk_visual_context_consumer as consumer


S2KK_TARGET_SCHEMA = "s2kk.evaluation-target-336.v1"
S2KK_EVALUATION_SCHEMA = "s2kk.context-utility-evaluation.v1"
CONFIRMED_STATUS = "S2KK_LEARNED_VISUAL_CONTEXT_UTILITY_CONFIRMED_DIRECT_ADAPTIVE_FILL_EXPLAINS"
FALSIFIED_STATUS = "S2KK_CONTEXT_UTILITY_FALSIFIED"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2KKEvaluationError(ValueError):
    """The post-hoc evidence cannot be evaluated."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2KKEvaluationError(message)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class EvaluationTarget336V1:
    visual_values: tuple[float, ...]
    visual_payload_digest: str
    evaluation_plan_digest: str
    target_digest: str
    schema: str = S2KK_TARGET_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "visual_values": list(self.visual_values),
            "visual_payload_digest": self.visual_payload_digest,
            "evaluation_plan_digest": self.evaluation_plan_digest,
        }


@dataclass(frozen=True, slots=True)
class ArmScore336V1:
    method: str
    delivered_masked_values: int
    unresolved_masked_values: int
    visible_unchanged: bool
    masked_mae: float | None
    full_vector_loss: float
    result_digest: str

    def payload(self) -> dict[str, object]:
        return {
            "method": self.method,
            "delivered_masked_values": self.delivered_masked_values,
            "unresolved_masked_values": self.unresolved_masked_values,
            "visible_unchanged": self.visible_unchanged,
            "masked_mae": self.masked_mae,
            "full_vector_loss": self.full_vector_loss,
            "result_digest": self.result_digest,
        }


@dataclass(frozen=True, slots=True)
class S2KKContextUtilityEvaluationV1:
    status: str
    target_digest: str
    probe_digest: str
    scores: tuple[ArmScore336V1, ...]
    context_equals_direct_baseline: bool
    context_improves_current_only: bool
    all_inputs_read_only: bool
    evaluation_digest: str
    schema: str = S2KK_EVALUATION_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "status": self.status,
            "target_digest": self.target_digest,
            "probe_digest": self.probe_digest,
            "scores": [score.payload() for score in self.scores],
            "context_equals_direct_baseline": self.context_equals_direct_baseline,
            "context_improves_current_only": self.context_improves_current_only,
            "all_inputs_read_only": self.all_inputs_read_only,
        }


def bind_evaluation_target(
    *,
    visual_values: tuple[float, ...],
    visual_payload_digest: str,
    evaluation_plan_digest: str,
) -> EvaluationTarget336V1:
    try:
        values = baselines._values(visual_values, 288, "evaluation target")
    except baselines.S2KKBaselineError as exc:
        raise S2KKEvaluationError("target values differ") from exc
    _require(
        all(
            isinstance(item, str) and _DIGEST.fullmatch(item) is not None
            for item in (visual_payload_digest, evaluation_plan_digest)
        ),
        "target source binding differs",
    )
    payload = {
        "schema": S2KK_TARGET_SCHEMA,
        "visual_values": list(values),
        "visual_payload_digest": visual_payload_digest,
        "evaluation_plan_digest": evaluation_plan_digest,
    }
    return EvaluationTarget336V1(values, visual_payload_digest, evaluation_plan_digest, _digest(payload))


def _validate_target(value: object) -> EvaluationTarget336V1:
    _require(type(value) is EvaluationTarget336V1, "exact evaluation target required")
    assert isinstance(value, EvaluationTarget336V1)
    try:
        baselines._values(value.visual_values, 288, "evaluation target")
    except baselines.S2KKBaselineError as exc:
        raise S2KKEvaluationError("target values differ") from exc
    _require(
        value.schema == S2KK_TARGET_SCHEMA
        and _DIGEST.fullmatch(value.visual_payload_digest) is not None
        and _DIGEST.fullmatch(value.evaluation_plan_digest) is not None
        and value.target_digest == _digest(value.payload_without_digest()),
        "target relation differs",
    )
    return value


def _validate_consumer_result(value: object) -> consumer.VisualCompletion336V1:
    try:
        return consumer._validate_result(value)
    except consumer.S2KKConsumerError as exc:
        raise S2KKEvaluationError("consumer evidence differs") from exc


def _validate_baseline_result(value: object) -> baselines.BaselineCompletion336V1:
    _require(type(value) is baselines.BaselineCompletion336V1, "exact baseline completion required")
    assert isinstance(value, baselines.BaselineCompletion336V1)
    _require(
        value.schema == baselines.S2KK_BASELINE_SCHEMA
        and value.method in {"FROZEN_FIRST_PROTOTYPE", "REPLAY_NEAREST_EXEMPLAR", "DIRECT_ADAPTIVE_MASK_FILL"}
        and value.status in {"NO_MATCH", "COMPLETED", "VISIBLE_CONFLICT"}
        and len(value.input_values) == len(value.output_values) == 288
        and value.completed_positions in ((), fixtures.MASKED_POSITIONS)
        and value.prestate_digest == value.poststate_digest
        and value.result_digest == baselines._digest(value.payload_without_digest()),
        "baseline completion relation differs",
    )
    _require(
        all(value.output_values[index] == value.input_values[index] for index in fixtures.VISIBLE_POSITIONS),
        "baseline visible values changed",
    )
    return value


def _score(
    method: str,
    output: tuple[float | None, ...],
    input_values: tuple[float | None, ...],
    result_digest: str,
    target: EvaluationTarget336V1,
) -> ArmScore336V1:
    visible_unchanged = all(output[index] == input_values[index] for index in fixtures.VISIBLE_POSITIONS)
    delivered = sum(output[index] is not None for index in fixtures.MASKED_POSITIONS)
    unresolved = len(fixtures.MASKED_POSITIONS) - delivered
    delivered_errors = [
        abs(float(output[index]) - target.visual_values[index])
        for index in fixtures.MASKED_POSITIONS
        if output[index] is not None
    ]
    visible_error = sum(
        abs(float(output[index]) - target.visual_values[index])
        for index in fixtures.VISIBLE_POSITIONS
        if output[index] is not None
    )
    masked_mae = None if not delivered_errors else sum(delivered_errors) / len(delivered_errors)
    loss = (visible_error + sum(delivered_errors) + unresolved) / 288
    _require(math.isfinite(loss) and 0.0 <= loss <= 1.0, "evaluation loss differs")
    return ArmScore336V1(
        method,
        delivered,
        unresolved,
        visible_unchanged,
        masked_mae,
        loss,
        result_digest,
    )


def evaluate_context_utility(
    *,
    current_only: consumer.VisualCompletion336V1,
    frozen: baselines.BaselineCompletion336V1,
    replay: baselines.BaselineCompletion336V1,
    adaptive_context: consumer.VisualCompletion336V1,
    direct_adaptive: baselines.BaselineCompletion336V1,
    target: EvaluationTarget336V1,
) -> S2KKContextUtilityEvaluationV1:
    target = _validate_target(target)
    current_only = _validate_consumer_result(current_only)
    adaptive_context = _validate_consumer_result(adaptive_context)
    frozen = _validate_baseline_result(frozen)
    replay = _validate_baseline_result(replay)
    direct_adaptive = _validate_baseline_result(direct_adaptive)
    expected_methods = (
        "CURRENT_PERCEPTION_ONLY",
        "FROZEN_FIRST_PROTOTYPE",
        "REPLAY_NEAREST_EXEMPLAR",
        "ADAPTIVE_B_STABLE_CONTEXT",
        "DIRECT_ADAPTIVE_MASK_FILL",
    )
    results = (current_only, frozen, replay, adaptive_context, direct_adaptive)
    _require(tuple(item.method for item in results) == expected_methods, "arm order or method differs")
    probe_digests = {item.probe_digest for item in results}
    _require(len(probe_digests) == 1, "arms did not receive one masked probe")
    scores = tuple(
        _score(item.method, item.output_values, item.input_values, item.result_digest, target)
        for item in results
    )
    all_read_only = (
        current_only.prestate_digest == current_only.poststate_digest
        and adaptive_context.prestate_digest == adaptive_context.poststate_digest
        and all(item.prestate_digest == item.poststate_digest for item in (frozen, replay, direct_adaptive))
    )
    context_equal = (
        adaptive_context.output_values == direct_adaptive.output_values
        and adaptive_context.completed_positions == direct_adaptive.completed_positions
        and adaptive_context.masked_copy_count == direct_adaptive.masked_copy_count
        and adaptive_context.visible_compare_count == direct_adaptive.visible_compare_count
    )
    improves = scores[3].full_vector_loss < scores[0].full_vector_loss
    confirmed = (
        current_only.status == "INSUFFICIENT_INFORMATION"
        and frozen.status == "NO_MATCH"
        and replay.status == "NO_MATCH"
        and adaptive_context.status == "COMPLETED"
        and direct_adaptive.status == "COMPLETED"
        and tuple(score.delivered_masked_values for score in scores) == (0, 0, 0, 256, 256)
        and all(score.visible_unchanged for score in scores)
        and context_equal
        and improves
        and all_read_only
    )
    payload = {
        "schema": S2KK_EVALUATION_SCHEMA,
        "status": CONFIRMED_STATUS if confirmed else FALSIFIED_STATUS,
        "target_digest": target.target_digest,
        "probe_digest": next(iter(probe_digests)),
        "scores": [score.payload() for score in scores],
        "context_equals_direct_baseline": context_equal,
        "context_improves_current_only": improves,
        "all_inputs_read_only": all_read_only,
    }
    return S2KKContextUtilityEvaluationV1(
        payload["status"],
        target.target_digest,
        payload["probe_digest"],
        scores,
        context_equal,
        improves,
        all_read_only,
        _digest(payload),
    )


__all__ = ()
