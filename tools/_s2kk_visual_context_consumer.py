"""Private read-only visual context consumer for S2-KK."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from tools import _s2kj_two_area_perceptual_context_336 as context336
from tools import _s2kj_validated_perceptual_finding_336 as finding336
from tools import _s2kk_context_utility_fixtures as fixtures


S2KK_CONSUMER_SCHEMA = "s2kk.visual-context-consumer.v1"
REQUESTED_ROLE = "B_STABLE_VISUAL"


class S2KKConsumerError(ValueError):
    """A context consumption binding is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2KKConsumerError(message)


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
class VisualCompletion336V1:
    method: str
    status: str
    probe_digest: str
    input_values: tuple[float | None, ...]
    output_values: tuple[float | None, ...]
    visible_positions: tuple[int, ...]
    completed_positions: tuple[int, ...]
    requested_role: str | None
    context_bundle_digest: str | None
    context_candidate_digest: str | None
    context_state_digest: str | None
    prestate_digest: str | None
    poststate_digest: str | None
    visible_compare_count: int
    masked_copy_count: int
    result_digest: str
    schema: str = S2KK_CONSUMER_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "method": self.method,
            "status": self.status,
            "probe_digest": self.probe_digest,
            "input_values": list(self.input_values),
            "output_values": list(self.output_values),
            "visible_positions": list(self.visible_positions),
            "completed_positions": list(self.completed_positions),
            "requested_role": self.requested_role,
            "context_bundle_digest": self.context_bundle_digest,
            "context_candidate_digest": self.context_candidate_digest,
            "context_state_digest": self.context_state_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "visible_compare_count": self.visible_compare_count,
            "masked_copy_count": self.masked_copy_count,
        }


def _make_result(
    *,
    method: str,
    status: str,
    probe: fixtures.MaskedVisualPerception336V1,
    output: tuple[float | None, ...],
    completed: tuple[int, ...],
    requested_role: str | None,
    bundle_digest: str | None,
    candidate_digest: str | None,
    state_digest: str | None,
    visible_compare_count: int,
    masked_copy_count: int,
) -> VisualCompletion336V1:
    payload = {
        "schema": S2KK_CONSUMER_SCHEMA,
        "method": method,
        "status": status,
        "probe_digest": probe.probe_digest,
        "input_values": list(probe.values),
        "output_values": list(output),
        "visible_positions": list(fixtures.VISIBLE_POSITIONS),
        "completed_positions": list(completed),
        "requested_role": requested_role,
        "context_bundle_digest": bundle_digest,
        "context_candidate_digest": candidate_digest,
        "context_state_digest": state_digest,
        "prestate_digest": state_digest,
        "poststate_digest": state_digest,
        "visible_compare_count": visible_compare_count,
        "masked_copy_count": masked_copy_count,
    }
    result = VisualCompletion336V1(
        method,
        status,
        probe.probe_digest,
        probe.values,
        output,
        fixtures.VISIBLE_POSITIONS,
        completed,
        requested_role,
        bundle_digest,
        candidate_digest,
        state_digest,
        state_digest,
        state_digest,
        visible_compare_count,
        masked_copy_count,
        _digest(payload),
    )
    _validate_result(result)
    return result


def _validate_result(value: object) -> VisualCompletion336V1:
    _require(type(value) is VisualCompletion336V1, "exact completion result required")
    assert isinstance(value, VisualCompletion336V1)
    _require(
        value.schema == S2KK_CONSUMER_SCHEMA
        and value.method in {"CURRENT_PERCEPTION_ONLY", "ADAPTIVE_B_STABLE_CONTEXT"}
        and value.status in {"INSUFFICIENT_INFORMATION", "COMPLETED", "CONTEXT_ABSENT", "VISIBLE_CONFLICT"}
        and len(value.input_values) == len(value.output_values) == 288
        and value.visible_positions == fixtures.VISIBLE_POSITIONS
        and value.completed_positions in ((), fixtures.MASKED_POSITIONS)
        and all(value.output_values[index] == value.input_values[index] for index in fixtures.VISIBLE_POSITIONS)
        and value.prestate_digest == value.poststate_digest
        and value.result_digest == _digest(value.payload_without_digest()),
        "completion result relation differs",
    )
    if value.method == "CURRENT_PERCEPTION_ONLY":
        _require(
            value.status == "INSUFFICIENT_INFORMATION"
            and value.requested_role is None
            and value.context_bundle_digest is None
            and value.context_candidate_digest is None
            and value.context_state_digest is None
            and value.prestate_digest is None,
            "current-only result contains context",
        )
    else:
        _require(
            value.requested_role == REQUESTED_ROLE
            and value.context_bundle_digest is not None
            and value.context_state_digest is not None
            and value.prestate_digest == value.context_state_digest,
            "context result binding differs",
        )
    if value.completed_positions:
        _require(
            value.status == "COMPLETED"
            and value.masked_copy_count == 256
            and all(type(value.output_values[index]) in (int, float) for index in fixtures.MASKED_POSITIONS),
            "completed result anatomy differs",
        )
    else:
        _require(
            value.masked_copy_count == 0
            and all(value.output_values[index] is None for index in fixtures.MASKED_POSITIONS),
            "noncompletion contains masked values",
        )
    return value


def current_perception_only(
    probe: fixtures.MaskedVisualPerception336V1,
) -> VisualCompletion336V1:
    probe = fixtures._validate_masked(probe)
    return _make_result(
        method="CURRENT_PERCEPTION_ONLY",
        status="INSUFFICIENT_INFORMATION",
        probe=probe,
        output=probe.values,
        completed=(),
        requested_role=None,
        bundle_digest=None,
        candidate_digest=None,
        state_digest=None,
        visible_compare_count=0,
        masked_copy_count=0,
    )


def consume_b_stable_visual(
    *,
    probe: fixtures.MaskedVisualPerception336V1,
    context: context336.TwoAreaPerceptualContext336,
    requested_role: str,
) -> VisualCompletion336V1:
    probe = fixtures._validate_masked(probe)
    try:
        context = context336._validate_context(context)
    except context336.S2KJContextError as exc:
        raise S2KKConsumerError("context binding differs") from exc
    _require(requested_role == REQUESTED_ROLE, "explicit visual B role is required")
    before = context.bundle_digest
    visual = context.b_stable.visual
    if visual.status == "ABSENT_VALID":
        return _make_result(
            method="ADAPTIVE_B_STABLE_CONTEXT",
            status="CONTEXT_ABSENT",
            probe=probe,
            output=probe.values,
            completed=(),
            requested_role=REQUESTED_ROLE,
            bundle_digest=context.bundle_digest,
            candidate_digest=None,
            state_digest=context.composite_state_digest,
            visible_compare_count=0,
            masked_copy_count=0,
        )
    _require(
        visual.status == "AVAILABLE"
        and type(visual.candidate) is finding336.StableModalityCandidate336V1
        and visual.candidate.role == REQUESTED_ROLE
        and visual.candidate.modality == "VISUAL"
        and visual.candidate.dimension == 288,
        "visual B candidate differs",
    )
    candidate = visual.candidate
    conflicts = tuple(
        index
        for index in fixtures.VISIBLE_POSITIONS
        if probe.values[index] != candidate.values[index]
    )
    if conflicts:
        result = _make_result(
            method="ADAPTIVE_B_STABLE_CONTEXT",
            status="VISIBLE_CONFLICT",
            probe=probe,
            output=probe.values,
            completed=(),
            requested_role=REQUESTED_ROLE,
            bundle_digest=context.bundle_digest,
            candidate_digest=candidate.candidate_digest,
            state_digest=context.composite_state_digest,
            visible_compare_count=len(fixtures.VISIBLE_POSITIONS),
            masked_copy_count=0,
        )
    else:
        output = tuple(
            probe.values[index]
            if index in fixtures.VISIBLE_POSITIONS
            else candidate.values[index]
            for index in range(288)
        )
        result = _make_result(
            method="ADAPTIVE_B_STABLE_CONTEXT",
            status="COMPLETED",
            probe=probe,
            output=output,
            completed=fixtures.MASKED_POSITIONS,
            requested_role=REQUESTED_ROLE,
            bundle_digest=context.bundle_digest,
            candidate_digest=candidate.candidate_digest,
            state_digest=context.composite_state_digest,
            visible_compare_count=len(fixtures.VISIBLE_POSITIONS),
            masked_copy_count=len(fixtures.MASKED_POSITIONS),
        )
    _require(before == context.bundle_digest, "context changed during consumption")
    return result


__all__ = ()
