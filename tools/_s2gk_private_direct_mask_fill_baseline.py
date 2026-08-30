"""Independent direct B_STABLE mask-fill baseline for S2-GK."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as contract


S2GK_BASELINE_SCHEMA = "s2gk.direct-b-stable-mask-fill.v1"
DIRECT_METHOD = "DIRECT_B_STABLE_MASK_FILL"
DIRECT_STATUSES = ("DIRECT_COMPLETED", "DIRECT_ABSENT", "DIRECT_CONFLICT")

S2GK_BASELINE_INVALID = "S2GK_BASELINE_INVALID"
S2GK_BASELINE_BINDING_INVALID = "S2GK_BASELINE_BINDING_INVALID"
S2GK_BASELINE_CONTEXT_INVALID = "S2GK_BASELINE_CONTEXT_INVALID"
S2GK_BASELINE_CAPACITY_EXCEEDED = "S2GK_BASELINE_CAPACITY_EXCEEDED"
S2GK_BASELINE_DIGEST_MISMATCH = "S2GK_BASELINE_DIGEST_MISMATCH"
S2GK_BASELINE_READ_ONLY_VIOLATION = "S2GK_BASELINE_READ_ONLY_VIOLATION"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2GKBaselineError(RuntimeError):
    """One terminal, fail-closed direct-baseline error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2GKBaselineError(code, message)


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


def _serialized(values: tuple[float | None, ...]) -> list[float | None]:
    return list(values)


@dataclass(frozen=True, slots=True)
class DirectMaskFillResourceLedger:
    mask_validation_count: int
    visible_compare_count: int
    masked_copy_count: int
    area_lookup_count: int
    candidate_reference_count: int
    value_reference_count: int
    digest_operation_count: int
    ledger_digest: str
    schema: str = S2GK_BASELINE_SCHEMA

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
            S2GK_BASELINE_INVALID,
            "baseline ledger count differs",
        )
        _require(
            self.mask_validation_count == 18
            and self.visible_compare_count <= 9
            and self.masked_copy_count <= 9
            and self.area_lookup_count == 1
            and self.candidate_reference_count <= 1
            and self.value_reference_count <= 18
            and self.digest_operation_count == 2,
            S2GK_BASELINE_CAPACITY_EXCEEDED,
            "baseline resource bound exceeded",
        )
        _require(
            self.schema == S2GK_BASELINE_SCHEMA
            and self.ledger_digest == _digest(self.payload_without_digest()),
            S2GK_BASELINE_DIGEST_MISMATCH,
            "baseline ledger digest differs",
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
class DirectMaskFillResult:
    method: str
    status: str
    probe_digest: str
    probe_source_digest: str
    input_values: tuple[float | None, ...]
    output_values: tuple[float | None, ...]
    visible_positions: tuple[int, ...]
    completed_positions: tuple[int, ...]
    requested_area: str
    context_bundle_digest: str
    context_candidate_digest: str | None
    context_component_digest: str | None
    context_source_digest: str
    prestate_digest: str
    poststate_digest: str
    resource_ledger: DirectMaskFillResourceLedger
    result_digest: str
    schema: str = S2GK_BASELINE_SCHEMA

    def __post_init__(self) -> None:
        _require(
            self.method == DIRECT_METHOD and self.status in DIRECT_STATUSES,
            S2GK_BASELINE_INVALID,
            "baseline method or status differs",
        )
        _require(
            len(self.input_values) == len(self.output_values) == 18
            and self.visible_positions == contract.VISIBLE_POSITIONS
            and self.completed_positions in ((), contract.MASKED_POSITIONS),
            S2GK_BASELINE_INVALID,
            "baseline output anatomy differs",
        )
        _require(
            all(
                self.output_values[index] == self.input_values[index]
                for index in contract.VISIBLE_POSITIONS
            ),
            S2GK_BASELINE_READ_ONLY_VIOLATION,
            "baseline changed a visible value",
        )
        if self.completed_positions:
            _require(
                all(type(self.output_values[index]) in (int, float) for index in contract.MASKED_POSITIONS),
                S2GK_BASELINE_INVALID,
                "baseline completion contains a marker",
            )
        else:
            _require(
                all(self.output_values[index] is None for index in contract.MASKED_POSITIONS),
                S2GK_BASELINE_INVALID,
                "baseline noncompletion contains a value",
            )
        _require(
            self.requested_area == "B_STABLE"
            and all(
                _valid_digest(value)
                for value in (
                    self.probe_digest,
                    self.probe_source_digest,
                    self.context_bundle_digest,
                    self.context_source_digest,
                    self.prestate_digest,
                    self.poststate_digest,
                )
            )
            and self.prestate_digest == self.poststate_digest,
            S2GK_BASELINE_BINDING_INVALID,
            "baseline binding differs",
        )
        if self.status in ("DIRECT_COMPLETED", "DIRECT_CONFLICT"):
            _require(
                _valid_digest(self.context_candidate_digest)
                and _valid_digest(self.context_component_digest),
                S2GK_BASELINE_BINDING_INVALID,
                "baseline candidate binding differs",
            )
        else:
            _require(
                self.context_candidate_digest is None
                and self.context_component_digest is None,
                S2GK_BASELINE_CONTEXT_INVALID,
                "absent baseline context exposes a candidate",
            )
        _require(
            type(self.resource_ledger) is DirectMaskFillResourceLedger
            and self.schema == S2GK_BASELINE_SCHEMA
            and self.result_digest == _digest(self.payload_without_digest()),
            S2GK_BASELINE_DIGEST_MISMATCH,
            "baseline result digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "method": self.method,
            "status": self.status,
            "probe_digest": self.probe_digest,
            "probe_source_digest": self.probe_source_digest,
            "input_values": _serialized(self.input_values),
            "output_values": _serialized(self.output_values),
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


def _validate_probe(probe: contract.MaskedVisualProbe) -> None:
    _require(
        type(probe) is contract.MaskedVisualProbe,
        S2GK_BASELINE_INVALID,
        "exact masked probe required",
    )
    _require(
        type(probe.values) is tuple
        and len(probe.values) == 18
        and probe.visible_positions == contract.VISIBLE_POSITIONS
        and probe.masked_positions == contract.MASKED_POSITIONS,
        S2GK_BASELINE_INVALID,
        "masked probe anatomy differs",
    )
    for index, value in enumerate(probe.values):
        if index in contract.VISIBLE_POSITIONS:
            _require(
                type(value) in (int, float)
                and math.isfinite(float(value))
                and -1.0 <= float(value) <= 1.0,
                S2GK_BASELINE_INVALID,
                "visible probe value differs",
            )
        else:
            _require(value is None, S2GK_BASELINE_INVALID, "mask marker differs")
    _require(
        probe.schema == contract.S2GK_SCHEMA
        and _valid_digest(probe.source_digest)
        and probe.probe_digest == _digest(probe.payload_without_digest()),
        S2GK_BASELINE_BINDING_INVALID,
        "probe source or digest differs",
    )


def _validate_bundle(bundle: two_area.TwoAreaContextBundle) -> None:
    _require(
        type(bundle) is two_area.TwoAreaContextBundle
        and len(bundle.area_findings) == 2
        and tuple(item.area for item in bundle.area_findings) == two_area.AREAS,
        S2GK_BASELINE_CONTEXT_INVALID,
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
        code = (
            S2GK_BASELINE_CAPACITY_EXCEEDED
            if "CAPACITY" in getattr(error, "code", "")
            else S2GK_BASELINE_CONTEXT_INVALID
        )
        raise S2GKBaselineError(code, "two-area bundle differs") from error


def _validate_binding(
    binding: contract.ContextUseBinding,
    probe: contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
) -> None:
    _require(
        type(binding) is contract.ContextUseBinding,
        S2GK_BASELINE_BINDING_INVALID,
        "exact context-use binding required",
    )
    _require(
        binding.schema == contract.S2GK_SCHEMA
        and binding.requested_area == "B_STABLE"
        and all(
            _valid_digest(value)
            for value in (
                binding.current_probe_digest,
                binding.current_probe_source_digest,
                binding.context_bundle_digest,
                binding.context_source_digest,
                binding.context_state_digest,
            )
        )
        and binding.binding_digest == _digest(binding.payload_without_digest())
        and binding.current_probe_digest == probe.probe_digest
        and binding.current_probe_source_digest == probe.source_digest
        and binding.context_bundle_digest == bundle.bundle_digest
        and binding.context_source_digest == bundle.source_digest
        and binding.context_state_digest == bundle.composite_state_digest,
        S2GK_BASELINE_BINDING_INVALID,
        "baseline source relation differs",
    )


def _make_ledger(
    visible_compare_count: int,
    masked_copy_count: int,
    candidate_reference_count: int,
    value_reference_count: int,
) -> DirectMaskFillResourceLedger:
    payload = {
        "schema": S2GK_BASELINE_SCHEMA,
        "mask_validation_count": 18,
        "visible_compare_count": visible_compare_count,
        "masked_copy_count": masked_copy_count,
        "area_lookup_count": 1,
        "candidate_reference_count": candidate_reference_count,
        "value_reference_count": value_reference_count,
        "digest_operation_count": 2,
    }
    return DirectMaskFillResourceLedger(
        18,
        visible_compare_count,
        masked_copy_count,
        1,
        candidate_reference_count,
        value_reference_count,
        2,
        _digest(payload),
    )


def _make_result(
    probe: contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    status: str,
    output_values: tuple[float | None, ...],
    completed_positions: tuple[int, ...],
    candidate_digest: str | None,
    component_digest: str | None,
    ledger: DirectMaskFillResourceLedger,
) -> DirectMaskFillResult:
    payload = {
        "schema": S2GK_BASELINE_SCHEMA,
        "method": DIRECT_METHOD,
        "status": status,
        "probe_digest": probe.probe_digest,
        "probe_source_digest": probe.source_digest,
        "input_values": _serialized(probe.values),
        "output_values": _serialized(output_values),
        "visible_positions": list(contract.VISIBLE_POSITIONS),
        "completed_positions": list(completed_positions),
        "requested_area": "B_STABLE",
        "context_bundle_digest": bundle.bundle_digest,
        "context_candidate_digest": candidate_digest,
        "context_component_digest": component_digest,
        "context_source_digest": bundle.source_digest,
        "prestate_digest": bundle.prestate_digest,
        "poststate_digest": bundle.poststate_digest,
        "resource_ledger_digest": ledger.ledger_digest,
    }
    return DirectMaskFillResult(
        DIRECT_METHOD,
        status,
        probe.probe_digest,
        probe.source_digest,
        probe.values,
        output_values,
        contract.VISIBLE_POSITIONS,
        completed_positions,
        "B_STABLE",
        bundle.bundle_digest,
        candidate_digest,
        component_digest,
        bundle.source_digest,
        bundle.prestate_digest,
        bundle.poststate_digest,
        ledger,
        _digest(payload),
    )


def direct_b_stable_mask_fill(
    probe: contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    binding: contract.ContextUseBinding,
) -> DirectMaskFillResult:
    """Fill the fixed mask directly, without calling the context consumer."""

    _validate_probe(probe)
    _validate_bundle(bundle)
    _validate_binding(binding, probe, bundle)
    before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
    stable_finding = bundle.area_findings[1].stable_content
    component = None
    if stable_finding.status != "ABSENT_VALID":
        candidate = stable_finding.candidate
        _require(candidate is not None, S2GK_BASELINE_CONTEXT_INVALID, "B candidate missing")
        visual = tuple(item for item in candidate.components if item.component_role == "VISUAL")
        _require(len(visual) <= 1, S2GK_BASELINE_CONTEXT_INVALID, "visual component ambiguous")
        component = visual[0] if visual else None
        if component is not None:
            _require(component.stable is True, S2GK_BASELINE_CONTEXT_INVALID, "visual component not stable")

    if component is None:
        result = _make_result(
            probe,
            bundle,
            "DIRECT_ABSENT",
            probe.values,
            (),
            None,
            None,
            _make_ledger(0, 0, 0, 0),
        )
    else:
        matches = all(
            float(probe.values[index]) == float(component.values[index])
            for index in contract.VISIBLE_POSITIONS
        )
        if matches:
            values = list(probe.values)
            for index in contract.MASKED_POSITIONS:
                values[index] = component.values[index]
            status = "DIRECT_COMPLETED"
            output = tuple(values)
            completed = contract.MASKED_POSITIONS
            copied = 9
        else:
            status = "DIRECT_CONFLICT"
            output = probe.values
            completed = ()
            copied = 0
        result = _make_result(
            probe,
            bundle,
            status,
            output,
            completed,
            stable_finding.candidate.candidate_digest,
            component.component_digest,
            _make_ledger(9, copied, 1, 18),
        )

    _require(
        before == (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        and bundle.prestate_digest == bundle.poststate_digest,
        S2GK_BASELINE_READ_ONLY_VIOLATION,
        "baseline changed its context input",
    )
    return result


__all__: tuple[str, ...] = ()
