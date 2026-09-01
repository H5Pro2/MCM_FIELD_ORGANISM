"""Private read-only S2-JI adapter for already admitted perceptual context."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2jh_private_controlled_context_admission as admission_contract


S2JK_SCHEMA = "s2jk.end-to-end-admitted-context-use.v1"
FUNCTION_ROLES = ("END_TO_END_ADAPTER", "DIRECT_COMPOSITION_BASELINE")
COMPLETION_STATUSES = (
    "ADMITTED_SINGLE_SOURCE_COMPLETED",
    "ADMITTED_EQUIVALENT_CONTEXT_COMPLETED",
    "CONTEXT_WITHHELD",
)
MAX_ARTIFACT_BYTES = 4095
MAX_LOGICAL_OPERATIONS = 7


class S2JKContextUseError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2JKContextUseError(code, message)


def _canonical_bytes(payload: object) -> bytes:
    try:
        return json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeEncodeError) as error:
        raise S2JKContextUseError("S2JK-E001", "canonical form is invalid") from error


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _valid_digest(value: object) -> bool:
    return type(value) is str and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _serialized_values(values: tuple[float | None, ...]) -> list[float | None]:
    return list(values)


@dataclass(frozen=True, slots=True)
class EndToEndContextUseLedger:
    evidence_validation_count: int
    state_digest_validation_count: int
    status_recomputation_count: int
    applicability_recomputation_count: int
    supplement_source_reference_count: int
    visible_preservation_check_count: int
    masked_copy_count: int
    context_apply_count: int
    logical_operation_count: int
    memory_receptor_or_field_call_count: int
    ledger_digest: str
    schema: str = S2JK_SCHEMA

    def __post_init__(self) -> None:
        values = tuple(
            getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in ("ledger_digest", "schema")
        )
        _require(all(type(value) is int and value >= 0 for value in values), "S2JK-E006", "ledger count differs")
        _require(
            self.evidence_validation_count == 8
            and self.state_digest_validation_count == 4
            and self.status_recomputation_count == 0
            and self.applicability_recomputation_count == 0
            and 0 <= self.supplement_source_reference_count <= 2
            and self.visible_preservation_check_count in (0, 9)
            and self.masked_copy_count in (0, 9)
            and self.context_apply_count in (0, 1)
            and self.visible_preservation_check_count == self.masked_copy_count
            and self.context_apply_count == (1 if self.masked_copy_count else 0)
            and self.supplement_source_reference_count == (0 if not self.context_apply_count else self.supplement_source_reference_count)
            and self.logical_operation_count == MAX_LOGICAL_OPERATIONS
            and self.memory_receptor_or_field_call_count == 0,
            "S2JK-E006",
            "ledger bound differs",
        )
        _require(
            self.ledger_digest == _digest(self.payload_without_digest()),
            "S2JK-E002",
            "ledger digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "evidence_validation_count": self.evidence_validation_count,
            "state_digest_validation_count": self.state_digest_validation_count,
            "status_recomputation_count": self.status_recomputation_count,
            "applicability_recomputation_count": self.applicability_recomputation_count,
            "supplement_source_reference_count": self.supplement_source_reference_count,
            "visible_preservation_check_count": self.visible_preservation_check_count,
            "masked_copy_count": self.masked_copy_count,
            "context_apply_count": self.context_apply_count,
            "logical_operation_count": self.logical_operation_count,
            "memory_receptor_or_field_call_count": self.memory_receptor_or_field_call_count,
        }

    @classmethod
    def build(cls, supplement_source_reference_count: int, completed: bool) -> "EndToEndContextUseLedger":
        values = (
            8,
            4,
            0,
            0,
            supplement_source_reference_count,
            9 if completed else 0,
            9 if completed else 0,
            1 if completed else 0,
            MAX_LOGICAL_OPERATIONS,
            0,
        )
        names = tuple(
            name for name in cls.__dataclass_fields__ if name not in ("ledger_digest", "schema")
        )
        payload = {"schema": S2JK_SCHEMA, **dict(zip(names, values, strict=True))}
        return cls(*values, _digest(payload))


@dataclass(frozen=True, slots=True)
class EndToEndContextUseResult:
    function_role: str
    source_signal_status: str
    admission_decision: str
    completion_status: str
    admitted_role: str | None
    equivalent_role_set_digest: str | None
    common_supplement_digest: str | None
    probe_digest: str
    bundle_digest: str
    signal_result_digest: str
    admission_result_digest: str
    current_only_values: tuple[float | None, ...]
    output_values: tuple[float | None, ...]
    completed_positions: tuple[int, ...]
    prestate_digest: str
    poststate_digest: str
    resource_ledger: EndToEndContextUseLedger
    selected_area: None
    ranking: None
    merged_context_digest: None
    result_digest: str
    schema: str = S2JK_SCHEMA

    def __post_init__(self) -> None:
        _require(self.schema == S2JK_SCHEMA and self.function_role in FUNCTION_ROLES, "S2JK-E001", "result role differs")
        _require(self.source_signal_status in signal_contract.RESULT_STATUSES, "S2JK-E003", "signal status differs")
        _require(self.completion_status in COMPLETION_STATUSES, "S2JK-E003", "completion status differs")
        _require(
            all(
                _valid_digest(value)
                for value in (
                    self.probe_digest,
                    self.bundle_digest,
                    self.signal_result_digest,
                    self.admission_result_digest,
                    self.prestate_digest,
                    self.poststate_digest,
                )
            ),
            "S2JK-E002",
            "result digest binding differs",
        )
        _require(self.prestate_digest == self.poststate_digest, "S2JK-E005", "read-only state changed")
        _require(
            type(self.current_only_values) is tuple
            and type(self.output_values) is tuple
            and len(self.current_only_values) == len(self.output_values) == 18,
            "S2JK-E001",
            "result dimension differs",
        )
        _require(
            type(self.completed_positions) is tuple
            and self.completed_positions in ((), probe_contract.MASKED_POSITIONS),
            "S2JK-E004",
            "completed positions differ",
        )
        _require(
            all(self.current_only_values[position] == self.output_values[position] for position in probe_contract.VISIBLE_POSITIONS),
            "S2JK-E005",
            "visible value changed",
        )
        _require(type(self.resource_ledger) is EndToEndContextUseLedger, "S2JK-E006", "ledger type differs")
        self.resource_ledger.__post_init__()
        _require(
            len(self.completed_positions) == self.resource_ledger.masked_copy_count,
            "S2JK-E006",
            "ledger completion count differs",
        )
        _require(self.selected_area is None and self.ranking is None and self.merged_context_digest is None, "S2JK-E003", "selection field is forbidden")
        if self.completion_status == "ADMITTED_SINGLE_SOURCE_COMPLETED":
            _require(
                self.admission_decision == "ALLOW_CONTEXT"
                and self.source_signal_status == "SINGLE_SOURCE"
                and self.admitted_role in signal_contract.AREAS
                and self.equivalent_role_set_digest is None
                and _valid_digest(self.common_supplement_digest)
                and self.completed_positions == probe_contract.MASKED_POSITIONS,
                "S2JK-E003",
                "single-source completion differs",
            )
            _require(self.resource_ledger.supplement_source_reference_count == 1, "S2JK-E006", "single-source ledger differs")
        elif self.completion_status == "ADMITTED_EQUIVALENT_CONTEXT_COMPLETED":
            _require(
                self.admission_decision == "ALLOW_CONTEXT"
                and self.source_signal_status == "CONSISTENT"
                and self.admitted_role is None
                and _valid_digest(self.equivalent_role_set_digest)
                and _valid_digest(self.common_supplement_digest)
                and self.completed_positions == probe_contract.MASKED_POSITIONS,
                "S2JK-E003",
                "equivalent completion differs",
            )
            _require(self.resource_ledger.supplement_source_reference_count == 2, "S2JK-E006", "equivalent ledger differs")
        else:
            _require(
                self.admission_decision == "PROCEED_WITHOUT_CONTEXT"
                and self.source_signal_status in ("CONFLICT", "NO_CONTEXT", "NO_APPLICABLE_CONTEXT")
                and self.admitted_role is None
                and self.equivalent_role_set_digest is None
                and self.common_supplement_digest is None
                and self.completed_positions == ()
                and self.output_values == self.current_only_values,
                "S2JK-E003",
                "withheld completion differs",
            )
            _require(self.resource_ledger.supplement_source_reference_count == 0, "S2JK-E006", "withheld ledger differs")
        _require(self.result_digest == _digest(self.payload_without_digest()), "S2JK-E002", "result digest differs")
        _require(len(_canonical_bytes(self.payload())) <= MAX_ARTIFACT_BYTES, "S2JK-E006", "result exceeds artifact bound")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "function_role": self.function_role,
            "source_signal_status": self.source_signal_status,
            "admission_decision": self.admission_decision,
            "completion_status": self.completion_status,
            "admitted_role": self.admitted_role,
            "equivalent_role_set_digest": self.equivalent_role_set_digest,
            "common_supplement_digest": self.common_supplement_digest,
            "probe_digest": self.probe_digest,
            "bundle_digest": self.bundle_digest,
            "signal_result_digest": self.signal_result_digest,
            "admission_result_digest": self.admission_result_digest,
            "current_only_values": _serialized_values(self.current_only_values),
            "output_values": _serialized_values(self.output_values),
            "completed_positions": list(self.completed_positions),
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "resource_ledger_digest": self.resource_ledger.ledger_digest,
            "selected_area": self.selected_area,
            "ranking": self.ranking,
            "merged_context_digest": self.merged_context_digest,
        }

    def payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "result_digest": self.result_digest}


def _role_finding_for_area(
    bundle: two_area.TwoAreaContextBundle,
    area: str,
):
    if area == "A_RECENT":
        return bundle.area_findings[0], bundle.area_findings[0].recent_content
    _require(area == "B_STABLE", "S2JK-E003", "area differs")
    return bundle.area_findings[1], bundle.area_findings[1].stable_content


def _candidate_visual_component(role_finding):
    candidate = role_finding.candidate
    if candidate is None:
        return None
    if role_finding.role == "B4_RECENT":
        _require(len(candidate.components) == 1 and candidate.components[0].component_role == "AV_JOINT", "S2JK-E002", "A component differs")
        return candidate.components[0]
    visual = tuple(component for component in candidate.components if component.component_role == "VISUAL")
    _require(len(visual) == 1, "S2JK-E002", "B visual component differs")
    return visual[0]


def _validate_finding_source(
    finding: signal_contract.AreaApplicabilityFinding,
    bundle: two_area.TwoAreaContextBundle,
) -> None:
    area_finding, role_finding = _role_finding_for_area(bundle, finding.area)
    _require(
        finding.area_finding_digest == area_finding.finding_digest
        and finding.role_finding_digest == role_finding.finding_digest,
        "S2JK-E002",
        "area source binding differs",
    )
    component = _candidate_visual_component(role_finding)
    if component is None:
        _require(
            finding.candidate_digest is None
            and finding.component_digest is None
            and finding.component_source_digest is None,
            "S2JK-E002",
            "absent source contains candidate evidence",
        )
        return
    _require(
        role_finding.candidate is not None
        and finding.candidate_digest == role_finding.candidate.candidate_digest
        and finding.component_digest == component.component_digest
        and finding.component_source_digest == component.source_digest,
        "S2JK-E002",
        "candidate source binding differs",
    )
    if finding.status == "APPLICABLE":
        values = component.values[8:] if component.component_role == "AV_JOINT" else component.values
        expected = tuple(values[position] for position in probe_contract.MASKED_POSITIONS)
        _require(finding.masked_values == expected, "S2JK-E004", "masked source values differ")


def _validate_evidence(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    admission_commit: admission_contract.ControlledContextAdmissionCommit,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
) -> admission_contract.ControlledPerceptualContextAdmission:
    _require(type(probe) is probe_contract.MaskedVisualProbe, "S2JK-E001", "probe type differs")
    _require(type(bundle) is two_area.TwoAreaContextBundle, "S2JK-E001", "bundle type differs")
    _require(type(signal_commit) is signal_contract.TwoAreaConflictSignalCommit, "S2JK-E001", "signal commit type differs")
    _require(type(admission_commit) is admission_contract.ControlledContextAdmissionCommit, "S2JK-E001", "admission commit type differs")
    _require(type(a_finding) is signal_contract.AreaApplicabilityFinding and type(b_finding) is signal_contract.AreaApplicabilityFinding, "S2JK-E001", "finding type differs")
    try:
        probe.__post_init__()
        bundle.__post_init__()
        signal_commit.result.__post_init__()
        signal_commit.receipt.__post_init__()
        signal_commit.owner_poststate.__post_init__()
        admission_commit.result.__post_init__()
        admission_commit.receipt.__post_init__()
        admission_commit.owner_poststate.__post_init__()
        a_finding.__post_init__()
        b_finding.__post_init__()
    except Exception as error:
        raise S2JKContextUseError("S2JK-E002", "upstream evidence is invalid") from error

    signal_result = signal_commit.result
    signal_receipt = signal_commit.receipt
    signal_owner = signal_commit.owner_poststate
    result = admission_commit.result
    receipt = admission_commit.receipt
    owner = admission_commit.owner_poststate
    _require(a_finding.area == "A_RECENT" and b_finding.area == "B_STABLE", "S2JK-E003", "canonical areas differ")
    _require(
        signal_result.probe_digest == probe.probe_digest
        and signal_result.bundle_digest == bundle.bundle_digest
        and signal_result.a_applicability_finding_digest == a_finding.finding_digest
        and signal_result.b_applicability_finding_digest == b_finding.finding_digest
        and a_finding.input_digest == b_finding.input_digest == signal_result.input_digest
        and a_finding.probe_digest == b_finding.probe_digest == probe.probe_digest
        and a_finding.bundle_digest == b_finding.bundle_digest == bundle.bundle_digest,
        "S2JK-E002",
        "signal source binding differs",
    )
    _require(
        signal_receipt.input_digest == signal_result.input_digest
        and signal_receipt.result_digest == signal_result.result_digest
        and signal_receipt.a_applicability_finding_digest == a_finding.finding_digest
        and signal_receipt.b_applicability_finding_digest == b_finding.finding_digest
        and signal_receipt.resource_ledger_digest == signal_result.resource_ledger_digest
        and signal_receipt.owner_prestate_digest == signal_owner.prior_owner_digest
        and signal_receipt.owner_poststate_digest == signal_owner.owner_poststate_digest
        and signal_owner.state == "CONSUMED"
        and signal_owner.terminal_binding_digest == signal_result.result_digest,
        "S2JK-E002",
        "signal receipt binding differs",
    )
    _require(
        result.function_role == "ADMISSION"
        and result.source_signal_status == signal_result.status
        and result.signal_result_digest == signal_result.result_digest
        and result.signal_receipt_digest == signal_receipt.receipt_digest
        and result.probe_digest == probe.probe_digest
        and result.bundle_digest == bundle.bundle_digest
        and result.composite_state_digest == bundle.composite_state_digest,
        "S2JK-E002",
        "admission source binding differs",
    )
    _require(
        receipt.function_role == "ADMISSION"
        and receipt.input_digest == result.input_digest
        and receipt.signal_result_digest == signal_result.result_digest
        and receipt.resource_ledger_digest == result.resource_ledger_digest
        and receipt.result_digest == result.result_digest
        and receipt.owner_prestate_digest == owner.prior_owner_digest
        and receipt.owner_poststate_digest == owner.owner_state_digest
        and owner.state == "CONSUMED"
        and owner.terminal_binding_digest == result.result_digest,
        "S2JK-E002",
        "admission receipt binding differs",
    )
    _require(
        signal_result.prestate_digest
        == signal_result.poststate_digest
        == result.prestate_digest
        == result.poststate_digest
        == bundle.prestate_digest
        == bundle.poststate_digest
        == bundle.composite_state_digest,
        "S2JK-E005",
        "state digest binding differs",
    )
    _validate_finding_source(a_finding, bundle)
    _validate_finding_source(b_finding, bundle)
    return result


def _single_source_values(
    result: admission_contract.ControlledPerceptualContextAdmission,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
) -> tuple[float, ...]:
    finding = a_finding if result.admitted_role == "A_RECENT" else b_finding
    _require(
        finding.area == result.admitted_role
        and finding.status == "APPLICABLE"
        and finding.masked_values_digest == result.common_supplement_digest,
        "S2JK-E004",
        "admitted single-source finding differs",
    )
    expected_binding = admission_contract.digest(
        {
            "schema": admission_contract.S2JH_SCHEMA,
            "binding_kind": "UNIQUE_APPLICABLE_CONTEXT",
            "area": finding.area,
            "finding_digest": finding.finding_digest,
            "candidate_digest": finding.candidate_digest,
            "masked_values_digest": finding.masked_values_digest,
        }
    )
    _require(result.admitted_context_binding_digest == expected_binding, "S2JK-E002", "single-source admission binding differs")
    return finding.masked_values


def _consistent_values(
    result: admission_contract.ControlledPerceptualContextAdmission,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
) -> tuple[float, ...]:
    _require(
        a_finding.status == b_finding.status == "APPLICABLE"
        and a_finding.masked_values == b_finding.masked_values
        and a_finding.masked_values_digest == b_finding.masked_values_digest == result.common_supplement_digest,
        "S2JK-E004",
        "equivalent supplement differs",
    )
    role_set_digest = admission_contract.digest(
        {
            "schema": admission_contract.S2JH_SCHEMA,
            "binding_kind": "UNORDERED_EQUIVALENT_ROLE_SET",
            "role_finding_pairs": sorted(
                (
                    (a_finding.area, a_finding.finding_digest),
                    (b_finding.area, b_finding.finding_digest),
                )
            ),
        }
    )
    binding_digest = admission_contract.digest(
        {
            "schema": admission_contract.S2JH_SCHEMA,
            "binding_kind": "UNORDERED_EQUIVALENT_CONTEXTS",
            "equivalent_role_set_digest": role_set_digest,
            "common_masked_values_digest": result.common_supplement_digest,
        }
    )
    _require(
        result.equivalent_role_set_digest == role_set_digest
        and result.admitted_context_binding_digest == binding_digest,
        "S2JK-E002",
        "equivalent admission binding differs",
    )
    return tuple(left for left, right in zip(a_finding.masked_values, b_finding.masked_values, strict=True) if left == right)


def _apply_admitted_supplement(
    probe: probe_contract.MaskedVisualProbe,
    masked_values: tuple[float, ...],
) -> tuple[float | None, ...]:
    _require(type(masked_values) is tuple and len(masked_values) == 9, "S2JK-E004", "supplement dimension differs")
    output = list(probe.values)
    for position, value in zip(probe_contract.MASKED_POSITIONS, masked_values, strict=True):
        _require(type(value) is float and 0.0 <= value <= 1.0, "S2JK-E004", "supplement value differs")
        output[position] = value
    return tuple(output)


def _build_result(
    function_role: str,
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    admission_result: admission_contract.ControlledPerceptualContextAdmission,
    output_values: tuple[float | None, ...],
    completion_status: str,
    supplement_source_reference_count: int,
) -> EndToEndContextUseResult:
    completed = completion_status != "CONTEXT_WITHHELD"
    ledger = EndToEndContextUseLedger.build(supplement_source_reference_count, completed)
    payload = {
        "schema": S2JK_SCHEMA,
        "function_role": function_role,
        "source_signal_status": admission_result.source_signal_status,
        "admission_decision": admission_result.decision,
        "completion_status": completion_status,
        "admitted_role": admission_result.admitted_role,
        "equivalent_role_set_digest": admission_result.equivalent_role_set_digest,
        "common_supplement_digest": admission_result.common_supplement_digest,
        "probe_digest": probe.probe_digest,
        "bundle_digest": bundle.bundle_digest,
        "signal_result_digest": signal_commit.result.result_digest,
        "admission_result_digest": admission_result.result_digest,
        "current_only_values": _serialized_values(probe.values),
        "output_values": _serialized_values(output_values),
        "completed_positions": list(probe_contract.MASKED_POSITIONS if completed else ()),
        "prestate_digest": bundle.prestate_digest,
        "poststate_digest": bundle.poststate_digest,
        "resource_ledger_digest": ledger.ledger_digest,
        "selected_area": None,
        "ranking": None,
        "merged_context_digest": None,
    }
    return EndToEndContextUseResult(
        function_role,
        admission_result.source_signal_status,
        admission_result.decision,
        completion_status,
        admission_result.admitted_role,
        admission_result.equivalent_role_set_digest,
        admission_result.common_supplement_digest,
        probe.probe_digest,
        bundle.bundle_digest,
        signal_commit.result.result_digest,
        admission_result.result_digest,
        probe.values,
        output_values,
        probe_contract.MASKED_POSITIONS if completed else (),
        bundle.prestate_digest,
        bundle.poststate_digest,
        ledger,
        None,
        None,
        None,
        _digest(payload),
    )


def use_admitted_context(
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    admission_commit: admission_contract.ControlledContextAdmissionCommit,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
) -> EndToEndContextUseResult:
    """Apply an already qualified admission without recomputing status or applicability."""

    before = (
        probe.probe_digest,
        bundle.bundle_digest,
        bundle.prestate_digest,
        bundle.poststate_digest,
        signal_commit.result.result_digest,
        admission_commit.result.result_digest,
        a_finding.finding_digest,
        b_finding.finding_digest,
    )
    result = _validate_evidence(probe, bundle, signal_commit, admission_commit, a_finding, b_finding)
    if result.source_signal_status == "SINGLE_SOURCE":
        masked_values = _single_source_values(result, a_finding, b_finding)
        output_values = _apply_admitted_supplement(probe, masked_values)
        completion_status = "ADMITTED_SINGLE_SOURCE_COMPLETED"
        source_count = 1
    elif result.source_signal_status == "CONSISTENT":
        masked_values = _consistent_values(result, a_finding, b_finding)
        output_values = _apply_admitted_supplement(probe, masked_values)
        completion_status = "ADMITTED_EQUIVALENT_CONTEXT_COMPLETED"
        source_count = 2
    else:
        _require(
            result.source_signal_status in ("CONFLICT", "NO_CONTEXT", "NO_APPLICABLE_CONTEXT")
            and result.decision == "PROCEED_WITHOUT_CONTEXT",
            "S2JK-E003",
            "withheld decision differs",
        )
        output_values = probe.values
        completion_status = "CONTEXT_WITHHELD"
        source_count = 0
    after = (
        probe.probe_digest,
        bundle.bundle_digest,
        bundle.prestate_digest,
        bundle.poststate_digest,
        signal_commit.result.result_digest,
        admission_commit.result.result_digest,
        a_finding.finding_digest,
        b_finding.finding_digest,
    )
    _require(before == after, "S2JK-E005", "input evidence changed")
    return _build_result(
        "END_TO_END_ADAPTER",
        probe,
        bundle,
        signal_commit,
        result,
        output_values,
        completion_status,
        source_count,
    )


__all__: tuple[str, ...] = ()
