"""Independent direct role-addressed mask-fill baseline for S2-HQ."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2hq_private_role_addressed_context_consumer as contract


S2HQ_BASELINE_SCHEMA = "s2hq.private.direct-role-addressed-baseline.v1"
DIRECT_METHOD = "DIRECT_EXPLICIT_AREA_MASK_FILL"
DIRECT_STATUSES = ("DIRECT_ROLE_COMPLETED", "DIRECT_ROLE_CONFLICT")

S2HQ_BASELINE_INVALID = "S2HQ_BASELINE_INVALID"
S2HQ_BASELINE_BINDING_INVALID = "S2HQ_BASELINE_BINDING_INVALID"
S2HQ_BASELINE_ROLE_INVALID = "S2HQ_BASELINE_ROLE_INVALID"
S2HQ_BASELINE_ROLE_UNAVAILABLE = "S2HQ_BASELINE_ROLE_UNAVAILABLE"
S2HQ_BASELINE_COMPONENT_INVALID = "S2HQ_BASELINE_COMPONENT_INVALID"
S2HQ_BASELINE_CAPACITY_EXCEEDED = "S2HQ_BASELINE_CAPACITY_EXCEEDED"
S2HQ_BASELINE_DIGEST_MISMATCH = "S2HQ_BASELINE_DIGEST_MISMATCH"
S2HQ_BASELINE_READ_ONLY_VIOLATION = "S2HQ_BASELINE_READ_ONLY_VIOLATION"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2HQBaselineError(RuntimeError):
    """One terminal fail-closed direct-baseline error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2HQBaselineError(code, message)


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


@dataclass(frozen=True, slots=True)
class DirectRoleAddressedLedger:
    mask_validation_count: int
    visible_compare_count: int
    masked_copy_count: int
    area_lookup_count: int
    candidate_reference_count: int
    component_reference_count: int
    value_reference_count: int
    digest_operation_count: int
    ledger_digest: str
    schema: str = S2HQ_BASELINE_SCHEMA

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
            all(type(value) is int and value >= 0 for value in counts)
            and self.mask_validation_count == 18
            and self.visible_compare_count == 9
            and self.masked_copy_count in (0, 9)
            and self.area_lookup_count == 1
            and self.candidate_reference_count == 1
            and self.component_reference_count == 1
            and self.value_reference_count == 18
            and self.digest_operation_count == 2,
            S2HQ_BASELINE_CAPACITY_EXCEEDED,
            "direct baseline resource bound differs",
        )
        _require(
            self.schema == S2HQ_BASELINE_SCHEMA
            and self.ledger_digest == _digest(self.payload_without_digest()),
            S2HQ_BASELINE_DIGEST_MISMATCH,
            "direct baseline ledger digest differs",
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
class DirectRoleAddressedResult:
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
    resource_ledger: DirectRoleAddressedLedger
    result_digest: str
    schema: str = S2HQ_BASELINE_SCHEMA

    def __post_init__(self) -> None:
        _require(
            self.method == DIRECT_METHOD
            and self.status in DIRECT_STATUSES
            and self.requested_area in contract.ALLOWED_AREAS,
            S2HQ_BASELINE_INVALID,
            "direct result method, status or role differs",
        )
        _require(
            type(self.input_values) is tuple
            and type(self.output_values) is tuple
            and type(self.completed_positions) is tuple
            and len(self.input_values) == len(self.output_values) == 18
            and all(
                self.output_values[index] == self.input_values[index]
                for index in probe_contract.VISIBLE_POSITIONS
            ),
            S2HQ_BASELINE_READ_ONLY_VIOLATION,
            "direct result changed visible values",
        )
        expected = probe_contract.MASKED_POSITIONS if self.status == "DIRECT_ROLE_COMPLETED" else ()
        _require(self.completed_positions == expected, S2HQ_BASELINE_INVALID, "direct completion positions differ")
        if expected:
            _require(
                all(
                    type(self.output_values[index]) in (int, float)
                    and math.isfinite(float(self.output_values[index]))
                    for index in expected
                ),
                S2HQ_BASELINE_INVALID,
                "direct completed mask differs",
            )
        else:
            _require(
                all(self.output_values[index] is None for index in probe_contract.MASKED_POSITIONS),
                S2HQ_BASELINE_INVALID,
                "direct conflict contains a partial fill",
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
            and type(self.resource_ledger) is DirectRoleAddressedLedger,
            S2HQ_BASELINE_READ_ONLY_VIOLATION,
            "direct result source or state binding differs",
        )
        self.resource_ledger.__post_init__()
        _require(
            self.schema == S2HQ_BASELINE_SCHEMA
            and self.result_digest == _digest(self.payload_without_digest()),
            S2HQ_BASELINE_DIGEST_MISMATCH,
            "direct result digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "method": self.method,
            "status": self.status,
            "requested_area": self.requested_area,
            "probe_digest": self.probe_digest,
            "probe_source_digest": self.probe_source_digest,
            "input_values": list(self.input_values),
            "output_values": list(self.output_values),
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


def _validate_inputs(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    binding: contract.RoleAddressedContextUseBinding,
) -> None:
    _require(type(probe) is probe_contract.MaskedVisualProbe, S2HQ_BASELINE_INVALID, "exact masked probe required")
    _require(type(bundle) is two_area.TwoAreaContextBundle, S2HQ_BASELINE_INVALID, "exact two-area bundle required")
    _require(type(binding) is contract.RoleAddressedContextUseBinding, S2HQ_BASELINE_BINDING_INVALID, "exact role binding required")
    try:
        probe.__post_init__()
        area_a, area_b = bundle.area_findings
        for finding in (area_a.recent_content, area_a.fast_internal, area_b.stable_content):
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
        binding.__post_init__()
    except (probe_contract.S2GKConsumerError, context.S2GBProjectionError, two_area.S2GIProjectionError, contract.S2HQConsumerError) as error:
        raise S2HQBaselineError(S2HQ_BASELINE_INVALID, "direct baseline input validation failed") from error
    selected_area = bundle.area_findings[0] if binding.requested_area == "A_RECENT" else bundle.area_findings[1]
    _require(
        binding.current_probe_digest == probe.probe_digest
        and binding.current_probe_source_digest == probe.source_digest
        and binding.context_bundle_digest == bundle.bundle_digest
        and binding.context_source_digest == bundle.source_digest
        and binding.context_state_digest == bundle.composite_state_digest
        and binding.selected_area_finding_digest == selected_area.finding_digest,
        S2HQ_BASELINE_BINDING_INVALID,
        "direct baseline binding differs",
    )


def _direct_selected_visual(
    bundle: two_area.TwoAreaContextBundle,
    requested_area: str,
) -> tuple[str, context.PerceptualContextRoleFinding, context.PerceptualContextCandidate, context.PerceptualContextComponent, tuple[float, ...]]:
    if requested_area == "A_RECENT":
        area = bundle.area_findings[0]
        finding = area.recent_content
        _require(finding.role == "B4_RECENT" and finding.status == "AVAILABLE_COMPLETE", S2HQ_BASELINE_ROLE_UNAVAILABLE, "direct A role unavailable")
        candidate = finding.candidate
        _require(candidate is not None and candidate.role == "B4_RECENT" and len(candidate.components) == 1, S2HQ_BASELINE_COMPONENT_INVALID, "direct A candidate differs")
        component = candidate.components[0]
        _require(component.component_role == "AV_JOINT" and len(component.values) == 26, S2HQ_BASELINE_COMPONENT_INVALID, "direct A component differs")
        return area.finding_digest, finding, candidate, component, tuple(component.values[8:])

    _require(requested_area == "B_STABLE", S2HQ_BASELINE_ROLE_INVALID, "direct requested area differs")
    area = bundle.area_findings[1]
    finding = area.stable_content
    _require(finding.role == "TSPM_SLOW" and finding.status in ("AVAILABLE_COMPLETE", "AVAILABLE_PARTIAL"), S2HQ_BASELINE_ROLE_UNAVAILABLE, "direct B role unavailable")
    candidate = finding.candidate
    _require(candidate is not None and candidate.role == "TSPM_SLOW", S2HQ_BASELINE_COMPONENT_INVALID, "direct B candidate differs")
    visual = tuple(item for item in candidate.components if item.component_role == "VISUAL")
    _require(len(visual) == 1 and visual[0].stable is True and len(visual[0].values) == 18, S2HQ_BASELINE_COMPONENT_INVALID, "direct B visual component differs")
    return area.finding_digest, finding, candidate, visual[0], tuple(visual[0].values)


def _ledger(masked_copy_count: int) -> DirectRoleAddressedLedger:
    payload = {
        "schema": S2HQ_BASELINE_SCHEMA,
        "mask_validation_count": 18,
        "visible_compare_count": 9,
        "masked_copy_count": masked_copy_count,
        "area_lookup_count": 1,
        "candidate_reference_count": 1,
        "component_reference_count": 1,
        "value_reference_count": 18,
        "digest_operation_count": 2,
    }
    return DirectRoleAddressedLedger(18, 9, masked_copy_count, 1, 1, 1, 18, 2, _digest(payload))


def direct_fill_from_explicit_area(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    binding: contract.RoleAddressedContextUseBinding,
) -> DirectRoleAddressedResult:
    """Fill directly from one explicit role without calling the consumer."""

    _validate_inputs(probe, bundle, binding)
    before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
    area_digest, finding, candidate, component, visual = _direct_selected_visual(bundle, binding.requested_area)
    visible_match = all(
        float(probe.values[index]) == float(visual[index])
        for index in probe_contract.VISIBLE_POSITIONS
    )
    output = list(probe.values)
    if visible_match:
        for index in probe_contract.MASKED_POSITIONS:
            output[index] = visual[index]
        status = "DIRECT_ROLE_COMPLETED"
        completed = probe_contract.MASKED_POSITIONS
        copied = 9
    else:
        status = "DIRECT_ROLE_CONFLICT"
        completed = ()
        copied = 0
    ledger = _ledger(copied)
    payload = {
        "schema": S2HQ_BASELINE_SCHEMA,
        "method": DIRECT_METHOD,
        "status": status,
        "requested_area": binding.requested_area,
        "probe_digest": probe.probe_digest,
        "probe_source_digest": probe.source_digest,
        "input_values": list(probe.values),
        "output_values": list(output),
        "completed_positions": list(completed),
        "context_bundle_digest": bundle.bundle_digest,
        "selected_area_finding_digest": area_digest,
        "selected_role_finding_digest": finding.finding_digest,
        "selected_candidate_digest": candidate.candidate_digest,
        "selected_component_digest": component.component_digest,
        "selected_component_source_digest": component.source_digest,
        "prestate_digest": bundle.prestate_digest,
        "poststate_digest": bundle.poststate_digest,
        "resource_ledger_digest": ledger.ledger_digest,
    }
    result = DirectRoleAddressedResult(
        DIRECT_METHOD,
        status,
        binding.requested_area,
        probe.probe_digest,
        probe.source_digest,
        probe.values,
        tuple(output),
        completed,
        bundle.bundle_digest,
        area_digest,
        finding.finding_digest,
        candidate.candidate_digest,
        component.component_digest,
        component.source_digest,
        bundle.prestate_digest,
        bundle.poststate_digest,
        ledger,
        _digest(payload),
    )
    _require(
        before == (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        and bundle.prestate_digest == bundle.poststate_digest,
        S2HQ_BASELINE_READ_ONLY_VIOLATION,
        "direct baseline changed its two-area input",
    )
    return result


__all__: tuple[str, ...] = ()
