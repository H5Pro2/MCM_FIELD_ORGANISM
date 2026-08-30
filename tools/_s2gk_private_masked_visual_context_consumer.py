"""Private read-only S2-GK consumer for one explicitly named B context."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area


S2GK_SCHEMA = "s2gk.masked-visual-context-consumer.v1"
METHOD_CURRENT_ONLY = "CURRENT_PERCEPTION_ONLY"
METHOD_PLUS_CONTEXT = "CURRENT_PERCEPTION_PLUS_TWO_AREA_CONTEXT"
VISIBLE_POSITIONS = (0, 2, 4, 6, 8, 10, 12, 14, 16)
MASKED_POSITIONS = (1, 3, 5, 7, 9, 11, 13, 15, 17)
RESULT_STATUSES = (
    "INSUFFICIENT_INFORMATION",
    "CONTEXT_COMPLETED",
    "CONTEXT_ABSENT",
    "CONTEXT_CONFLICT",
)

S2GK_INVALID_TYPE_OR_SCHEMA = "S2GK_INVALID_TYPE_OR_SCHEMA"
S2GK_PROBE_INVALID = "S2GK_PROBE_INVALID"
S2GK_MASK_INVALID = "S2GK_MASK_INVALID"
S2GK_BINDING_INVALID = "S2GK_BINDING_INVALID"
S2GK_CONTEXT_INVALID = "S2GK_CONTEXT_INVALID"
S2GK_ROLE_INVALID = "S2GK_ROLE_INVALID"
S2GK_DIMENSION_INVALID = "S2GK_DIMENSION_INVALID"
S2GK_CAPACITY_EXCEEDED = "S2GK_CAPACITY_EXCEEDED"
S2GK_DIGEST_MISMATCH = "S2GK_DIGEST_MISMATCH"
S2GK_READ_ONLY_VIOLATION = "S2GK_READ_ONLY_VIOLATION"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2GKConsumerError(RuntimeError):
    """One terminal, fail-closed S2-GK consumer error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2GKConsumerError(code, message)


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


def _serialized_values(values: tuple[float | None, ...]) -> list[float | None]:
    return list(values)


@dataclass(frozen=True, slots=True)
class MaskedVisualProbe:
    values: tuple[float | None, ...]
    visible_positions: tuple[int, ...]
    masked_positions: tuple[int, ...]
    source_digest: str
    probe_digest: str
    schema: str = S2GK_SCHEMA

    def __post_init__(self) -> None:
        _require(
            type(self.values) is tuple and len(self.values) == 18,
            S2GK_DIMENSION_INVALID,
            "masked visual probe must contain exactly 18 positions",
        )
        _require(
            self.visible_positions == VISIBLE_POSITIONS
            and self.masked_positions == MASKED_POSITIONS,
            S2GK_MASK_INVALID,
            "fixed S2-GJ mask differs",
        )
        for index, value in enumerate(self.values):
            if index in VISIBLE_POSITIONS:
                _require(
                    type(value) in (int, float)
                    and math.isfinite(float(value))
                    and -1.0 <= float(value) <= 1.0,
                    S2GK_PROBE_INVALID,
                    "visible position is not one finite numeric value",
                )
            else:
                _require(
                    value is None,
                    S2GK_MASK_INVALID,
                    "masked position must use the canonical None marker",
                )
        _require(
            _valid_digest(self.source_digest),
            S2GK_BINDING_INVALID,
            "probe source digest differs",
        )
        _require(
            self.schema == S2GK_SCHEMA
            and self.probe_digest == _digest(self.payload_without_digest()),
            S2GK_DIGEST_MISMATCH,
            "masked probe digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "values": _serialized_values(self.values),
            "visible_positions": list(self.visible_positions),
            "masked_positions": list(self.masked_positions),
            "source_digest": self.source_digest,
        }

    @classmethod
    def build(
        cls,
        values: tuple[float | None, ...],
        source_digest: str,
    ) -> "MaskedVisualProbe":
        payload = {
            "schema": S2GK_SCHEMA,
            "values": _serialized_values(values),
            "visible_positions": list(VISIBLE_POSITIONS),
            "masked_positions": list(MASKED_POSITIONS),
            "source_digest": source_digest,
        }
        return cls(
            values,
            VISIBLE_POSITIONS,
            MASKED_POSITIONS,
            source_digest,
            _digest(payload),
        )


@dataclass(frozen=True, slots=True)
class ContextUseBinding:
    current_probe_digest: str
    current_probe_source_digest: str
    context_bundle_digest: str
    context_source_digest: str
    context_state_digest: str
    requested_area: str
    binding_digest: str
    schema: str = S2GK_SCHEMA

    def __post_init__(self) -> None:
        _require(
            all(
                _valid_digest(value)
                for value in (
                    self.current_probe_digest,
                    self.current_probe_source_digest,
                    self.context_bundle_digest,
                    self.context_source_digest,
                    self.context_state_digest,
                )
            ),
            S2GK_BINDING_INVALID,
            "context-use source binding differs",
        )
        _require(
            self.requested_area == "B_STABLE",
            S2GK_ROLE_INVALID,
            "only explicitly named B_STABLE is permitted",
        )
        _require(
            self.schema == S2GK_SCHEMA
            and self.binding_digest == _digest(self.payload_without_digest()),
            S2GK_DIGEST_MISMATCH,
            "context-use binding digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "current_probe_digest": self.current_probe_digest,
            "current_probe_source_digest": self.current_probe_source_digest,
            "context_bundle_digest": self.context_bundle_digest,
            "context_source_digest": self.context_source_digest,
            "context_state_digest": self.context_state_digest,
            "requested_area": self.requested_area,
        }

    @classmethod
    def build(
        cls,
        probe: MaskedVisualProbe,
        bundle: two_area.TwoAreaContextBundle,
        requested_area: str = "B_STABLE",
    ) -> "ContextUseBinding":
        _require(
            type(probe) is MaskedVisualProbe,
            S2GK_INVALID_TYPE_OR_SCHEMA,
            "exact masked probe required",
        )
        _require(
            type(bundle) is two_area.TwoAreaContextBundle,
            S2GK_INVALID_TYPE_OR_SCHEMA,
            "exact S2-GI bundle required",
        )
        payload = {
            "schema": S2GK_SCHEMA,
            "current_probe_digest": probe.probe_digest,
            "current_probe_source_digest": probe.source_digest,
            "context_bundle_digest": bundle.bundle_digest,
            "context_source_digest": bundle.source_digest,
            "context_state_digest": bundle.composite_state_digest,
            "requested_area": requested_area,
        }
        return cls(
            probe.probe_digest,
            probe.source_digest,
            bundle.bundle_digest,
            bundle.source_digest,
            bundle.composite_state_digest,
            requested_area,
            _digest(payload),
        )


@dataclass(frozen=True, slots=True)
class ContextConsumerResourceLedger:
    mask_validation_count: int
    visible_compare_count: int
    masked_copy_count: int
    area_lookup_count: int
    candidate_reference_count: int
    value_reference_count: int
    digest_operation_count: int
    ledger_digest: str
    schema: str = S2GK_SCHEMA

    def __post_init__(self) -> None:
        counts = (
            self.mask_validation_count,
            self.visible_compare_count,
            self.masked_copy_count,
            self.area_lookup_count,
            self.candidate_reference_count,
            self.value_reference_count,
            self.digest_operation_count,
        )
        _require(
            all(type(value) is int and value >= 0 for value in counts),
            S2GK_CONTEXT_INVALID,
            "consumer ledger count differs",
        )
        _require(
            self.mask_validation_count == 18
            and self.visible_compare_count <= 9
            and self.masked_copy_count <= 9
            and self.area_lookup_count <= 1
            and self.candidate_reference_count <= 1
            and self.value_reference_count <= 18
            and self.digest_operation_count == 2,
            S2GK_CAPACITY_EXCEEDED,
            "consumer resource bound exceeded",
        )
        _require(
            self.schema == S2GK_SCHEMA
            and self.ledger_digest == _digest(self.payload_without_digest()),
            S2GK_DIGEST_MISMATCH,
            "consumer ledger digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "mask_validation_count": self.mask_validation_count,
            "visible_compare_count": self.visible_compare_count,
            "masked_copy_count": self.masked_copy_count,
            "area_lookup_count": self.area_lookup_count,
            "candidate_reference_count": self.candidate_reference_count,
            "value_reference_count": self.value_reference_count,
            "digest_operation_count": self.digest_operation_count,
        }


@dataclass(frozen=True, slots=True)
class MaskedVisualCompletionResult:
    method: str
    status: str
    probe_digest: str
    probe_source_digest: str
    input_values: tuple[float | None, ...]
    output_values: tuple[float | None, ...]
    visible_positions: tuple[int, ...]
    completed_positions: tuple[int, ...]
    requested_area: str | None
    context_bundle_digest: str | None
    context_candidate_digest: str | None
    context_component_digest: str | None
    context_source_digest: str | None
    prestate_digest: str | None
    poststate_digest: str | None
    resource_ledger: ContextConsumerResourceLedger
    result_digest: str
    schema: str = S2GK_SCHEMA

    def __post_init__(self) -> None:
        _require(
            self.method in (METHOD_CURRENT_ONLY, METHOD_PLUS_CONTEXT)
            and self.status in RESULT_STATUSES,
            S2GK_INVALID_TYPE_OR_SCHEMA,
            "completion method or status differs",
        )
        _require(
            type(self.input_values) is tuple
            and type(self.output_values) is tuple
            and len(self.input_values) == len(self.output_values) == 18
            and self.visible_positions == VISIBLE_POSITIONS
            and type(self.completed_positions) is tuple,
            S2GK_DIMENSION_INVALID,
            "completion result dimension differs",
        )
        _require(
            self.completed_positions in ((), MASKED_POSITIONS),
            S2GK_MASK_INVALID,
            "completion positions differ",
        )
        _require(
            all(self.output_values[index] == self.input_values[index] for index in VISIBLE_POSITIONS),
            S2GK_READ_ONLY_VIOLATION,
            "visible perception was modified",
        )
        if self.completed_positions:
            _require(
                all(type(self.output_values[index]) in (int, float) for index in MASKED_POSITIONS),
                S2GK_CONTEXT_INVALID,
                "completed mask contains a marker",
            )
        else:
            _require(
                all(self.output_values[index] is None for index in MASKED_POSITIONS),
                S2GK_CONTEXT_INVALID,
                "uncompleted mask contains a value",
            )
        _require(
            _valid_digest(self.probe_digest)
            and _valid_digest(self.probe_source_digest)
            and type(self.resource_ledger) is ContextConsumerResourceLedger,
            S2GK_BINDING_INVALID,
            "result probe or ledger binding differs",
        )
        if self.method == METHOD_CURRENT_ONLY:
            _require(
                self.status == "INSUFFICIENT_INFORMATION"
                and self.requested_area is None
                and self.context_bundle_digest is None
                and self.context_candidate_digest is None
                and self.context_component_digest is None
                and self.context_source_digest is None
                and self.prestate_digest is None
                and self.poststate_digest is None,
                S2GK_CONTEXT_INVALID,
                "current-only result contains context",
            )
        else:
            _require(
                self.requested_area == "B_STABLE"
                and _valid_digest(self.context_bundle_digest)
                and _valid_digest(self.context_source_digest)
                and _valid_digest(self.prestate_digest)
                and self.prestate_digest == self.poststate_digest,
                S2GK_READ_ONLY_VIOLATION,
                "context result binding or state differs",
            )
            if self.status in ("CONTEXT_COMPLETED", "CONTEXT_CONFLICT"):
                _require(
                    _valid_digest(self.context_candidate_digest)
                    and _valid_digest(self.context_component_digest),
                    S2GK_BINDING_INVALID,
                    "context candidate binding differs",
                )
            else:
                _require(
                    self.context_candidate_digest is None
                    and self.context_component_digest is None,
                    S2GK_CONTEXT_INVALID,
                    "absent context exposes a candidate",
                )
        _require(
            self.schema == S2GK_SCHEMA
            and self.result_digest == _digest(self.payload_without_digest()),
            S2GK_DIGEST_MISMATCH,
            "completion result digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "method": self.method,
            "status": self.status,
            "probe_digest": self.probe_digest,
            "probe_source_digest": self.probe_source_digest,
            "input_values": _serialized_values(self.input_values),
            "output_values": _serialized_values(self.output_values),
            "visible_positions": list(self.visible_positions),
            "completed_positions": list(self.completed_positions),
            "requested_area": self.requested_area,
            "context_bundle_digest": self.context_bundle_digest,
            "context_candidate_digest": self.context_candidate_digest,
            "context_component_digest": self.context_component_digest,
            "context_source_digest": self.context_source_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "resource_ledger_digest": self.resource_ledger.ledger_digest,
        }


def _make_ledger(
    *,
    visible_compare_count: int,
    masked_copy_count: int,
    area_lookup_count: int,
    candidate_reference_count: int,
    value_reference_count: int,
) -> ContextConsumerResourceLedger:
    payload = {
        "schema": S2GK_SCHEMA,
        "mask_validation_count": 18,
        "visible_compare_count": visible_compare_count,
        "masked_copy_count": masked_copy_count,
        "area_lookup_count": area_lookup_count,
        "candidate_reference_count": candidate_reference_count,
        "value_reference_count": value_reference_count,
        "digest_operation_count": 2,
    }
    return ContextConsumerResourceLedger(
        18,
        visible_compare_count,
        masked_copy_count,
        area_lookup_count,
        candidate_reference_count,
        value_reference_count,
        2,
        _digest(payload),
    )


def _make_result(
    *,
    method: str,
    status: str,
    probe: MaskedVisualProbe,
    output_values: tuple[float | None, ...],
    completed_positions: tuple[int, ...],
    requested_area: str | None,
    context_bundle_digest: str | None,
    context_candidate_digest: str | None,
    context_component_digest: str | None,
    context_source_digest: str | None,
    prestate_digest: str | None,
    poststate_digest: str | None,
    ledger: ContextConsumerResourceLedger,
) -> MaskedVisualCompletionResult:
    payload = {
        "schema": S2GK_SCHEMA,
        "method": method,
        "status": status,
        "probe_digest": probe.probe_digest,
        "probe_source_digest": probe.source_digest,
        "input_values": _serialized_values(probe.values),
        "output_values": _serialized_values(output_values),
        "visible_positions": list(VISIBLE_POSITIONS),
        "completed_positions": list(completed_positions),
        "requested_area": requested_area,
        "context_bundle_digest": context_bundle_digest,
        "context_candidate_digest": context_candidate_digest,
        "context_component_digest": context_component_digest,
        "context_source_digest": context_source_digest,
        "prestate_digest": prestate_digest,
        "poststate_digest": poststate_digest,
        "resource_ledger_digest": ledger.ledger_digest,
    }
    return MaskedVisualCompletionResult(
        method,
        status,
        probe.probe_digest,
        probe.source_digest,
        probe.values,
        output_values,
        VISIBLE_POSITIONS,
        completed_positions,
        requested_area,
        context_bundle_digest,
        context_candidate_digest,
        context_component_digest,
        context_source_digest,
        prestate_digest,
        poststate_digest,
        ledger,
        _digest(payload),
    )


def _validate_probe(probe: MaskedVisualProbe) -> None:
    _require(
        type(probe) is MaskedVisualProbe,
        S2GK_INVALID_TYPE_OR_SCHEMA,
        "exact masked probe required",
    )
    probe.__post_init__()


def _validate_role_finding(finding: context.PerceptualContextRoleFinding) -> None:
    _require(
        type(finding) is context.PerceptualContextRoleFinding,
        S2GK_INVALID_TYPE_OR_SCHEMA,
        "context role finding type differs",
    )
    try:
        if finding.candidate is not None:
            for component in finding.candidate.components:
                component.__post_init__()
            finding.candidate.__post_init__()
        finding.__post_init__()
    except context.S2GBProjectionError as error:
        if error.code == context.S2GB_DIMENSION_INVALID:
            code = S2GK_DIMENSION_INVALID
        elif error.code == context.S2GB_CAPACITY_EXCEEDED:
            code = S2GK_CAPACITY_EXCEEDED
        elif error.code == context.S2GB_DIGEST_MISMATCH:
            code = S2GK_DIGEST_MISMATCH
        else:
            code = S2GK_CONTEXT_INVALID
        raise S2GKConsumerError(code, "S2-GI nested context differs") from error


def _validate_bundle(bundle: two_area.TwoAreaContextBundle) -> None:
    _require(
        type(bundle) is two_area.TwoAreaContextBundle,
        S2GK_INVALID_TYPE_OR_SCHEMA,
        "exact S2-GI bundle required",
    )
    _require(
        type(bundle.area_findings) is tuple
        and len(bundle.area_findings) == 2
        and tuple(item.area for item in bundle.area_findings) == two_area.AREAS,
        S2GK_ROLE_INVALID,
        "two-area order differs",
    )
    area_a, area_b = bundle.area_findings
    _validate_role_finding(area_a.recent_content)
    _validate_role_finding(area_a.fast_internal)
    _validate_role_finding(area_b.stable_content)
    try:
        for reference in area_a.short_sequence.references:
            reference.__post_init__()
        area_a.short_sequence.__post_init__()
        area_a.__post_init__()
        area_b.__post_init__()
        bundle.resource_ledger.__post_init__()
        bundle.__post_init__()
    except (context.S2GBProjectionError, two_area.S2GIProjectionError) as error:
        source_code = getattr(error, "code", "")
        if "CAPACITY" in source_code:
            code = S2GK_CAPACITY_EXCEEDED
        elif "DIGEST" in source_code:
            code = S2GK_DIGEST_MISMATCH
        elif "ROLE" in source_code:
            code = S2GK_ROLE_INVALID
        elif "READ_ONLY" in source_code:
            code = S2GK_READ_ONLY_VIOLATION
        else:
            code = S2GK_CONTEXT_INVALID
        raise S2GKConsumerError(code, "S2-GI bundle validation failed") from error


def _validate_binding(
    binding: ContextUseBinding,
    probe: MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
) -> None:
    _require(
        type(binding) is ContextUseBinding,
        S2GK_INVALID_TYPE_OR_SCHEMA,
        "exact context-use binding required",
    )
    binding.__post_init__()
    _require(
        binding.current_probe_digest == probe.probe_digest
        and binding.current_probe_source_digest == probe.source_digest
        and binding.context_bundle_digest == bundle.bundle_digest
        and binding.context_source_digest == bundle.source_digest
        and binding.context_state_digest == bundle.composite_state_digest,
        S2GK_BINDING_INVALID,
        "probe, source, bundle or state binding differs",
    )


def _visual_component(
    stable_finding: context.PerceptualContextRoleFinding,
) -> context.PerceptualContextComponent | None:
    if stable_finding.status == "ABSENT_VALID":
        return None
    candidate = stable_finding.candidate
    _require(candidate is not None, S2GK_CONTEXT_INVALID, "B candidate is missing")
    visual = tuple(
        component for component in candidate.components if component.component_role == "VISUAL"
    )
    _require(len(visual) <= 1, S2GK_CONTEXT_INVALID, "B visual component is ambiguous")
    if not visual:
        return None
    _require(visual[0].stable is True, S2GK_CONTEXT_INVALID, "B visual component is not stable")
    return visual[0]


def current_perception_only(
    probe: MaskedVisualProbe,
) -> MaskedVisualCompletionResult:
    """Return the bounded current-perception-only finding without guessing."""

    _validate_probe(probe)
    ledger = _make_ledger(
        visible_compare_count=0,
        masked_copy_count=0,
        area_lookup_count=0,
        candidate_reference_count=0,
        value_reference_count=9,
    )
    return _make_result(
        method=METHOD_CURRENT_ONLY,
        status="INSUFFICIENT_INFORMATION",
        probe=probe,
        output_values=probe.values,
        completed_positions=(),
        requested_area=None,
        context_bundle_digest=None,
        context_candidate_digest=None,
        context_component_digest=None,
        context_source_digest=None,
        prestate_digest=None,
        poststate_digest=None,
        ledger=ledger,
    )


def complete_with_named_b_stable(
    probe: MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    binding: ContextUseBinding,
) -> MaskedVisualCompletionResult:
    """Complete masked values from explicitly named B_STABLE, read-only."""

    _validate_probe(probe)
    _validate_bundle(bundle)
    _validate_binding(binding, probe, bundle)
    source_bundle_digest = bundle.bundle_digest
    source_prestate_digest = bundle.prestate_digest
    source_poststate_digest = bundle.poststate_digest
    stable_finding = bundle.area_findings[1].stable_content
    component = _visual_component(stable_finding)

    if component is None:
        ledger = _make_ledger(
            visible_compare_count=0,
            masked_copy_count=0,
            area_lookup_count=1,
            candidate_reference_count=0,
            value_reference_count=0,
        )
        result = _make_result(
            method=METHOD_PLUS_CONTEXT,
            status="CONTEXT_ABSENT",
            probe=probe,
            output_values=probe.values,
            completed_positions=(),
            requested_area="B_STABLE",
            context_bundle_digest=bundle.bundle_digest,
            context_candidate_digest=None,
            context_component_digest=None,
            context_source_digest=bundle.source_digest,
            prestate_digest=bundle.prestate_digest,
            poststate_digest=bundle.poststate_digest,
            ledger=ledger,
        )
    else:
        visible_matches = all(
            float(probe.values[index]) == float(component.values[index])
            for index in VISIBLE_POSITIONS
        )
        if not visible_matches:
            status = "CONTEXT_CONFLICT"
            output = probe.values
            completed = ()
            copied = 0
        else:
            status = "CONTEXT_COMPLETED"
            values = list(probe.values)
            for index in MASKED_POSITIONS:
                values[index] = component.values[index]
            output = tuple(values)
            completed = MASKED_POSITIONS
            copied = 9
        ledger = _make_ledger(
            visible_compare_count=9,
            masked_copy_count=copied,
            area_lookup_count=1,
            candidate_reference_count=1,
            value_reference_count=18,
        )
        result = _make_result(
            method=METHOD_PLUS_CONTEXT,
            status=status,
            probe=probe,
            output_values=output,
            completed_positions=completed,
            requested_area="B_STABLE",
            context_bundle_digest=bundle.bundle_digest,
            context_candidate_digest=stable_finding.candidate.candidate_digest,
            context_component_digest=component.component_digest,
            context_source_digest=bundle.source_digest,
            prestate_digest=bundle.prestate_digest,
            poststate_digest=bundle.poststate_digest,
            ledger=ledger,
        )

    _require(
        bundle.bundle_digest == source_bundle_digest
        and bundle.prestate_digest == source_prestate_digest
        and bundle.poststate_digest == source_poststate_digest
        and source_prestate_digest == source_poststate_digest,
        S2GK_READ_ONLY_VIOLATION,
        "context bundle changed during consumption",
    )
    return result


__all__: tuple[str, ...] = ()
