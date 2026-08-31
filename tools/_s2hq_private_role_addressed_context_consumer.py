"""Private read-only consumer for one explicitly addressed two-area role."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract


S2HQ_SCHEMA = "s2hq.private.role-addressed-context-consumer.v1"
METHOD_ROLE_ADDRESSED = "EXPLICIT_TWO_AREA_ROLE_MASK_FILL"
ALLOWED_AREAS = ("A_RECENT", "B_STABLE")
RESULT_STATUSES = ("ROLE_CONTEXT_COMPLETED", "ROLE_CONTEXT_CONFLICT")

S2HQ_INVALID_TYPE_OR_SCHEMA = "S2HQ_INVALID_TYPE_OR_SCHEMA"
S2HQ_PROBE_INVALID = "S2HQ_PROBE_INVALID"
S2HQ_BINDING_INVALID = "S2HQ_BINDING_INVALID"
S2HQ_BUNDLE_INVALID = "S2HQ_BUNDLE_INVALID"
S2HQ_ROLE_INVALID = "S2HQ_ROLE_INVALID"
S2HQ_ROLE_UNAVAILABLE = "S2HQ_ROLE_UNAVAILABLE"
S2HQ_COMPONENT_INVALID = "S2HQ_COMPONENT_INVALID"
S2HQ_DIGEST_MISMATCH = "S2HQ_DIGEST_MISMATCH"
S2HQ_CAPACITY_EXCEEDED = "S2HQ_CAPACITY_EXCEEDED"
S2HQ_READ_ONLY_VIOLATION = "S2HQ_READ_ONLY_VIOLATION"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2HQConsumerError(RuntimeError):
    """One terminal fail-closed S2-HQ consumer error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2HQConsumerError(code, message)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _serialized(values: tuple[float | None, ...]) -> list[float | None]:
    return list(values)


@dataclass(frozen=True, slots=True)
class RoleAddressedContextUseBinding:
    current_probe_digest: str
    current_probe_source_digest: str
    context_bundle_digest: str
    context_source_digest: str
    context_state_digest: str
    requested_area: str
    selected_area_finding_digest: str
    binding_digest: str
    schema: str = S2HQ_SCHEMA

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
                    self.selected_area_finding_digest,
                )
            ),
            S2HQ_BINDING_INVALID,
            "role-addressed source binding differs",
        )
        _require(
            self.requested_area in ALLOWED_AREAS,
            S2HQ_ROLE_INVALID,
            "requested area must be explicit",
        )
        _require(
            self.schema == S2HQ_SCHEMA
            and self.binding_digest == _digest(self.payload_without_digest()),
            S2HQ_DIGEST_MISMATCH,
            "role-addressed binding digest differs",
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
            "selected_area_finding_digest": self.selected_area_finding_digest,
        }

    @classmethod
    def build(
        cls,
        probe: probe_contract.MaskedVisualProbe,
        bundle: two_area.TwoAreaContextBundle,
        requested_area: str,
    ) -> "RoleAddressedContextUseBinding":
        _require(
            type(probe) is probe_contract.MaskedVisualProbe,
            S2HQ_INVALID_TYPE_OR_SCHEMA,
            "exact masked probe required",
        )
        _require(
            type(bundle) is two_area.TwoAreaContextBundle,
            S2HQ_INVALID_TYPE_OR_SCHEMA,
            "exact two-area bundle required",
        )
        _require(
            requested_area in ALLOWED_AREAS,
            S2HQ_ROLE_INVALID,
            "requested area must be explicit",
        )
        area = bundle.area_findings[0] if requested_area == "A_RECENT" else bundle.area_findings[1]
        payload = {
            "schema": S2HQ_SCHEMA,
            "current_probe_digest": probe.probe_digest,
            "current_probe_source_digest": probe.source_digest,
            "context_bundle_digest": bundle.bundle_digest,
            "context_source_digest": bundle.source_digest,
            "context_state_digest": bundle.composite_state_digest,
            "requested_area": requested_area,
            "selected_area_finding_digest": area.finding_digest,
        }
        return cls(
            probe.probe_digest,
            probe.source_digest,
            bundle.bundle_digest,
            bundle.source_digest,
            bundle.composite_state_digest,
            requested_area,
            area.finding_digest,
            _digest(payload),
        )


@dataclass(frozen=True, slots=True)
class RoleAddressedResourceLedger:
    mask_validation_count: int
    visible_compare_count: int
    masked_copy_count: int
    area_lookup_count: int
    candidate_reference_count: int
    component_reference_count: int
    value_reference_count: int
    digest_operation_count: int
    ledger_digest: str
    schema: str = S2HQ_SCHEMA

    def __post_init__(self) -> None:
        counts = (
            self.mask_validation_count,
            self.visible_compare_count,
            self.masked_copy_count,
            self.area_lookup_count,
            self.candidate_reference_count,
            self.component_reference_count,
            self.value_reference_count,
            self.digest_operation_count,
        )
        _require(
            all(type(value) is int and value >= 0 for value in counts),
            S2HQ_CAPACITY_EXCEEDED,
            "resource count differs",
        )
        _require(
            self.mask_validation_count == 18
            and self.visible_compare_count == 9
            and self.masked_copy_count in (0, 9)
            and self.area_lookup_count == 1
            and self.candidate_reference_count == 1
            and self.component_reference_count == 1
            and self.value_reference_count == 18
            and self.digest_operation_count == 2,
            S2HQ_CAPACITY_EXCEEDED,
            "role-addressed resource bound differs",
        )
        _require(
            self.schema == S2HQ_SCHEMA
            and self.ledger_digest == _digest(self.payload_without_digest()),
            S2HQ_DIGEST_MISMATCH,
            "resource ledger digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "mask_validation_count": self.mask_validation_count,
            "visible_compare_count": self.visible_compare_count,
            "masked_copy_count": self.masked_copy_count,
            "area_lookup_count": self.area_lookup_count,
            "candidate_reference_count": self.candidate_reference_count,
            "component_reference_count": self.component_reference_count,
            "value_reference_count": self.value_reference_count,
            "digest_operation_count": self.digest_operation_count,
        }


@dataclass(frozen=True, slots=True)
class RoleAddressedCompletionResult:
    method: str
    status: str
    requested_area: str
    probe_digest: str
    probe_source_digest: str
    input_values: tuple[float | None, ...]
    output_values: tuple[float | None, ...]
    completed_positions: tuple[int, ...]
    context_bundle_digest: str
    selected_area_finding_digest: str
    selected_role_finding_digest: str
    selected_candidate_digest: str
    selected_component_digest: str
    selected_component_source_digest: str
    prestate_digest: str
    poststate_digest: str
    resource_ledger: RoleAddressedResourceLedger
    result_digest: str
    schema: str = S2HQ_SCHEMA

    def __post_init__(self) -> None:
        _require(
            self.method == METHOD_ROLE_ADDRESSED
            and self.status in RESULT_STATUSES
            and self.requested_area in ALLOWED_AREAS,
            S2HQ_INVALID_TYPE_OR_SCHEMA,
            "result method, status or role differs",
        )
        _require(
            type(self.input_values) is tuple
            and type(self.output_values) is tuple
            and len(self.input_values) == len(self.output_values) == 18,
            S2HQ_COMPONENT_INVALID,
            "result value dimension differs",
        )
        _require(
            all(
                self.output_values[index] == self.input_values[index]
                for index in probe_contract.VISIBLE_POSITIONS
            ),
            S2HQ_READ_ONLY_VIOLATION,
            "visible values changed",
        )
        expected_completed = (
            probe_contract.MASKED_POSITIONS
            if self.status == "ROLE_CONTEXT_COMPLETED"
            else ()
        )
        _require(
            self.completed_positions == expected_completed,
            S2HQ_COMPONENT_INVALID,
            "completed positions differ",
        )
        if expected_completed:
            _require(
                all(
                    type(self.output_values[index]) in (int, float)
                    and math.isfinite(float(self.output_values[index]))
                    for index in probe_contract.MASKED_POSITIONS
                ),
                S2HQ_COMPONENT_INVALID,
                "completed mask contains an invalid value",
            )
        else:
            _require(
                all(
                    self.output_values[index] is None
                    for index in probe_contract.MASKED_POSITIONS
                ),
                S2HQ_COMPONENT_INVALID,
                "conflict result contains a partial fill",
            )
        _require(
            all(
                _valid_digest(value)
                for value in (
                    self.probe_digest,
                    self.probe_source_digest,
                    self.context_bundle_digest,
                    self.selected_area_finding_digest,
                    self.selected_role_finding_digest,
                    self.selected_candidate_digest,
                    self.selected_component_digest,
                    self.selected_component_source_digest,
                    self.prestate_digest,
                    self.poststate_digest,
                )
            )
            and self.prestate_digest == self.poststate_digest
            and type(self.resource_ledger) is RoleAddressedResourceLedger,
            S2HQ_READ_ONLY_VIOLATION,
            "result source or state binding differs",
        )
        self.resource_ledger.__post_init__()
        _require(
            self.schema == S2HQ_SCHEMA
            and self.result_digest == _digest(self.payload_without_digest()),
            S2HQ_DIGEST_MISMATCH,
            "result digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "method": self.method,
            "status": self.status,
            "requested_area": self.requested_area,
            "probe_digest": self.probe_digest,
            "probe_source_digest": self.probe_source_digest,
            "input_values": _serialized(self.input_values),
            "output_values": _serialized(self.output_values),
            "completed_positions": list(self.completed_positions),
            "context_bundle_digest": self.context_bundle_digest,
            "selected_area_finding_digest": self.selected_area_finding_digest,
            "selected_role_finding_digest": self.selected_role_finding_digest,
            "selected_candidate_digest": self.selected_candidate_digest,
            "selected_component_digest": self.selected_component_digest,
            "selected_component_source_digest": self.selected_component_source_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "resource_ledger_digest": self.resource_ledger.ledger_digest,
        }


def _validate_probe(probe: probe_contract.MaskedVisualProbe) -> None:
    _require(
        type(probe) is probe_contract.MaskedVisualProbe,
        S2HQ_INVALID_TYPE_OR_SCHEMA,
        "exact masked visual probe required",
    )
    try:
        probe.__post_init__()
    except probe_contract.S2GKConsumerError as error:
        raise S2HQConsumerError(S2HQ_PROBE_INVALID, "masked probe validation failed") from error


def _validate_bundle(bundle: two_area.TwoAreaContextBundle) -> None:
    _require(
        type(bundle) is two_area.TwoAreaContextBundle
        and type(bundle.area_findings) is tuple
        and len(bundle.area_findings) == 2
        and tuple(item.area for item in bundle.area_findings) == ALLOWED_AREAS,
        S2HQ_BUNDLE_INVALID,
        "exact two-area bundle required",
    )
    area_a, area_b = bundle.area_findings
    try:
        for finding in (
            area_a.recent_content,
            area_a.fast_internal,
            area_b.stable_content,
        ):
            if finding.candidate is not None:
                for component in finding.candidate.components:
                    component.__post_init__()
                finding.candidate.__post_init__()
            finding.__post_init__()
        for reference in area_a.short_sequence.references:
            reference.__post_init__()
        area_a.short_sequence.__post_init__()
        area_a.__post_init__()
        area_b.__post_init__()
        bundle.resource_ledger.__post_init__()
        bundle.__post_init__()
    except (context.S2GBProjectionError, two_area.S2GIProjectionError) as error:
        code = S2HQ_DIGEST_MISMATCH if "DIGEST" in getattr(error, "code", "") else S2HQ_BUNDLE_INVALID
        raise S2HQConsumerError(code, "two-area bundle validation failed") from error


def _validate_binding(
    binding: RoleAddressedContextUseBinding,
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
) -> None:
    _require(
        type(binding) is RoleAddressedContextUseBinding,
        S2HQ_INVALID_TYPE_OR_SCHEMA,
        "exact role-addressed binding required",
    )
    binding.__post_init__()
    selected_area = bundle.area_findings[0] if binding.requested_area == "A_RECENT" else bundle.area_findings[1]
    _require(
        binding.current_probe_digest == probe.probe_digest
        and binding.current_probe_source_digest == probe.source_digest
        and binding.context_bundle_digest == bundle.bundle_digest
        and binding.context_source_digest == bundle.source_digest
        and binding.context_state_digest == bundle.composite_state_digest
        and binding.selected_area_finding_digest == selected_area.finding_digest,
        S2HQ_BINDING_INVALID,
        "role, probe, bundle or state relation differs",
    )


def _selected_visual(
    bundle: two_area.TwoAreaContextBundle,
    requested_area: str,
) -> tuple[
    str,
    context.PerceptualContextRoleFinding,
    context.PerceptualContextCandidate,
    context.PerceptualContextComponent,
    tuple[float, ...],
]:
    if requested_area == "A_RECENT":
        area = bundle.area_findings[0]
        finding = area.recent_content
        _require(finding.role == "B4_RECENT", S2HQ_ROLE_INVALID, "A recent role differs")
        _require(finding.status == "AVAILABLE_COMPLETE", S2HQ_ROLE_UNAVAILABLE, "A recent role is unavailable")
        candidate = finding.candidate
        _require(candidate is not None and candidate.role == "B4_RECENT", S2HQ_COMPONENT_INVALID, "A candidate differs")
        _require(
            len(candidate.components) == 1
            and candidate.components[0].component_role == "AV_JOINT"
            and len(candidate.components[0].values) == 26,
            S2HQ_COMPONENT_INVALID,
            "A candidate must contain one joint AV component",
        )
        component = candidate.components[0]
        visual = tuple(component.values[8:])
        return area.finding_digest, finding, candidate, component, visual

    _require(requested_area == "B_STABLE", S2HQ_ROLE_INVALID, "unknown requested area")
    area = bundle.area_findings[1]
    finding = area.stable_content
    _require(finding.role == "TSPM_SLOW", S2HQ_ROLE_INVALID, "B stable role differs")
    _require(finding.status in ("AVAILABLE_COMPLETE", "AVAILABLE_PARTIAL"), S2HQ_ROLE_UNAVAILABLE, "B stable role is unavailable")
    candidate = finding.candidate
    _require(candidate is not None and candidate.role == "TSPM_SLOW", S2HQ_COMPONENT_INVALID, "B candidate differs")
    visual_components = tuple(
        component for component in candidate.components if component.component_role == "VISUAL"
    )
    _require(len(visual_components) == 1, S2HQ_COMPONENT_INVALID, "B visual component is missing or ambiguous")
    component = visual_components[0]
    _require(component.stable is True and len(component.values) == 18, S2HQ_COMPONENT_INVALID, "B visual component is not stable")
    return area.finding_digest, finding, candidate, component, tuple(component.values)


def _ledger(masked_copy_count: int) -> RoleAddressedResourceLedger:
    payload = {
        "schema": S2HQ_SCHEMA,
        "mask_validation_count": 18,
        "visible_compare_count": 9,
        "masked_copy_count": masked_copy_count,
        "area_lookup_count": 1,
        "candidate_reference_count": 1,
        "component_reference_count": 1,
        "value_reference_count": 18,
        "digest_operation_count": 2,
    }
    return RoleAddressedResourceLedger(
        18,
        9,
        masked_copy_count,
        1,
        1,
        1,
        18,
        2,
        _digest(payload),
    )


def _result(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    binding: RoleAddressedContextUseBinding,
    area_finding_digest: str,
    role_finding: context.PerceptualContextRoleFinding,
    candidate: context.PerceptualContextCandidate,
    component: context.PerceptualContextComponent,
    status: str,
    output_values: tuple[float | None, ...],
    completed_positions: tuple[int, ...],
    ledger: RoleAddressedResourceLedger,
) -> RoleAddressedCompletionResult:
    payload = {
        "schema": S2HQ_SCHEMA,
        "method": METHOD_ROLE_ADDRESSED,
        "status": status,
        "requested_area": binding.requested_area,
        "probe_digest": probe.probe_digest,
        "probe_source_digest": probe.source_digest,
        "input_values": _serialized(probe.values),
        "output_values": _serialized(output_values),
        "completed_positions": list(completed_positions),
        "context_bundle_digest": bundle.bundle_digest,
        "selected_area_finding_digest": area_finding_digest,
        "selected_role_finding_digest": role_finding.finding_digest,
        "selected_candidate_digest": candidate.candidate_digest,
        "selected_component_digest": component.component_digest,
        "selected_component_source_digest": component.source_digest,
        "prestate_digest": bundle.prestate_digest,
        "poststate_digest": bundle.poststate_digest,
        "resource_ledger_digest": ledger.ledger_digest,
    }
    return RoleAddressedCompletionResult(
        METHOD_ROLE_ADDRESSED,
        status,
        binding.requested_area,
        probe.probe_digest,
        probe.source_digest,
        probe.values,
        output_values,
        completed_positions,
        bundle.bundle_digest,
        area_finding_digest,
        role_finding.finding_digest,
        candidate.candidate_digest,
        component.component_digest,
        component.source_digest,
        bundle.prestate_digest,
        bundle.poststate_digest,
        ledger,
        _digest(payload),
    )


def complete_from_explicit_area(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    binding: RoleAddressedContextUseBinding,
) -> RoleAddressedCompletionResult:
    """Fill only from the explicitly bound A_RECENT or B_STABLE role."""

    _validate_probe(probe)
    _validate_bundle(bundle)
    _validate_binding(binding, probe, bundle)
    before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
    area_digest, finding, candidate, component, visual = _selected_visual(
        bundle,
        binding.requested_area,
    )

    visible_match = all(
        float(probe.values[index]) == float(visual[index])
        for index in probe_contract.VISIBLE_POSITIONS
    )
    if visible_match:
        output = list(probe.values)
        for index in probe_contract.MASKED_POSITIONS:
            output[index] = visual[index]
        status = "ROLE_CONTEXT_COMPLETED"
        completed = probe_contract.MASKED_POSITIONS
        copied = 9
    else:
        status = "ROLE_CONTEXT_CONFLICT"
        output = list(probe.values)
        completed = ()
        copied = 0

    result = _result(
        probe,
        bundle,
        binding,
        area_digest,
        finding,
        candidate,
        component,
        status,
        tuple(output),
        completed,
        _ledger(copied),
    )
    _require(
        before == (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        and bundle.prestate_digest == bundle.poststate_digest,
        S2HQ_READ_ONLY_VIOLATION,
        "two-area input changed during role-addressed consumption",
    )
    return result


__all__: tuple[str, ...] = ()
