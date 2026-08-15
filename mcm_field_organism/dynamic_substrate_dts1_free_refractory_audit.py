"""Finite private S1-IB execution of the preregistered S1-IA audit."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from .dynamic_substrate_dts1_step import (
    DTS1EdgeParticipation,
    DTS1StepRates,
    DTS1StepResult,
    compute_dts1_closed_prestate_step,
)
from .dynamic_substrate_s1hi_resource_anatomy import (
    DTS1EdgeResource,
    DTS1NodeCapacity,
    DTS1ResourceAnatomy,
)
from .dynamic_substrate_s1hz_free_refractory_intervention_contract import (
    S1_HZ_BASELINE_COUNTERPREDICTIONS,
)


class DTS1FreeRefractoryAuditError(ValueError):
    """Raised when the closed S1-IB audit result is internally invalid."""


S1_IB_AUDIT_ID = "dynamic-substrate.free-refractory-audit.s1ib.v1"
S1_IB_SOURCE_S1IA_CONTRACT_DIGEST = (
    "c59c5d1c05ac5f9fed8d91088a1490e136ad08ed28bfa72cc34f54b6c45dc650"
)
S1_IB_CASE_IDS = (
    "C01_DIRECT_INTERVENTION_PAIR",
    "N01_EQUAL_PARTITION_REPEAT",
    "N02_ZERO_PARTICIPATION",
    "N03_ZERO_BINDING_RATE",
)
S1_IB_ARM_IDS = (
    "F_HIGH_MORE_FREE_LESS_REFRACTORY",
    "R_HIGH_LESS_FREE_MORE_REFRACTORY",
)
S1_IB_EXPECTED_F_HIGH_ENGAGEMENT = 0.2537769456908254
S1_IB_EXPECTED_R_HIGH_ENGAGEMENT = 0.14501539753761447
S1_IB_EXPECTED_ENGAGEMENT_DIFFERENCE = 0.1087615481532109
S1_IB_ROUNDOFF_FLOOR = 1.1368683772161603e-13
S1_IB_SINGLE_AUDIT_PURE_STEP_CALLS = 8
S1_IB_DOUBLE_AUDIT_PURE_STEP_CALLS = 16
S1_IB_PASS = "PASS_DTS1_DIRECT_FREE_REFRACTORY_ENGAGEMENT"
S1_IB_STOPP = "STOPP_DTS1_DIRECT_FREE_REFRACTORY_ENGAGEMENT"

_NODE_IDS = ("node-a", "node-b")
_EDGE = _NODE_IDS
_CAPACITY = 1.0
_CONDUCTIVE = 0.4
_F_HIGH_REFRACTORY = 0.2
_R_HIGH_REFRACTORY = 0.8
_ELAPSED_TIME = 0.5
_POSITIVE_PARTICIPATION = 1.0
_POSITIVE_RATES = DTS1StepRates(0.4, 0.3, 0.2)
_ZERO_BINDING_RATES = DTS1StepRates(0.0, 0.3, 0.2)
_BASELINE_RECORD_VALUE = "STATE_SPACE_DISTINCT_NO_EXECUTION"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_nonnegative(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise DTS1FreeRefractoryAuditError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1FreeRefractoryAuditError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise DTS1FreeRefractoryAuditError(
            f"{role} must be finite and nonnegative"
        )
    return result


@dataclass(frozen=True, slots=True)
class DTS1S1IBCaseRecord:
    case_id: str
    arm_ids: tuple[str, ...]
    input_anatomy_digests: tuple[str, ...]
    result_payloads: tuple[tuple[object, ...], ...]
    exact_checks: tuple[tuple[str, bool], ...]
    maximum_local_ledger_residual: float
    maximum_global_ledger_residual: float
    pure_step_calls: int

    def __post_init__(self) -> None:
        if self.case_id not in S1_IB_CASE_IDS:
            raise DTS1FreeRefractoryAuditError("unknown S1-IB case")
        if len(self.arm_ids) != 2 or len(self.input_anatomy_digests) != 2:
            raise DTS1FreeRefractoryAuditError(
                "S1-IB case requires exactly two complete arm records"
            )
        if len(self.result_payloads) != 2 or any(
            len(payload) != 9 for payload in self.result_payloads
        ):
            raise DTS1FreeRefractoryAuditError(
                "S1-IB case requires two complete result payloads"
            )
        if not self.exact_checks or any(
            not isinstance(value, bool) for _, value in self.exact_checks
        ):
            raise DTS1FreeRefractoryAuditError(
                "S1-IB exact checks must be complete booleans"
            )
        for digest in self.input_anatomy_digests:
            if not isinstance(digest, str) or len(digest) != 64:
                raise DTS1FreeRefractoryAuditError(
                    "S1-IB input anatomy digest must be one SHA-256 value"
                )
        if self.pure_step_calls != 2:
            raise DTS1FreeRefractoryAuditError(
                "each S1-IB case requires exactly two pure step calls"
            )
        object.__setattr__(
            self,
            "maximum_local_ledger_residual",
            _finite_nonnegative(
                self.maximum_local_ledger_residual,
                "maximum_local_ledger_residual",
            ),
        )
        object.__setattr__(
            self,
            "maximum_global_ledger_residual",
            _finite_nonnegative(
                self.maximum_global_ledger_residual,
                "maximum_global_ledger_residual",
            ),
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "arm_ids": list(self.arm_ids),
            "input_anatomy_digests": list(self.input_anatomy_digests),
            "result_payloads": [list(payload) for payload in self.result_payloads],
            "exact_checks": [[name, value] for name, value in self.exact_checks],
            "maximum_local_ledger_residual": self.maximum_local_ledger_residual,
            "maximum_global_ledger_residual": self.maximum_global_ledger_residual,
            "pure_step_calls": self.pure_step_calls,
        }


@dataclass(frozen=True, slots=True)
class _DTS1S1IBSingleAuditResult:
    case_records: tuple[DTS1S1IBCaseRecord, ...]
    f_high_engagement: float
    r_high_engagement: float
    engagement_difference: float
    roundoff_floor: float
    baseline_records: tuple[tuple[str, str], ...]
    pure_step_calls: int
    field_steps: int
    stopp_reasons: tuple[str, ...]
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = self.canonical_payload(include_digest=False)
        if (
            tuple(record.case_id for record in self.case_records) != S1_IB_CASE_IDS
            or self.baseline_records != _baseline_records()
            or self.pure_step_calls != S1_IB_SINGLE_AUDIT_PURE_STEP_CALLS
            or self.field_steps != 0
            or self.decision not in (S1_IB_PASS, S1_IB_STOPP)
            or (self.decision == S1_IB_PASS) != (not self.stopp_reasons)
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1FreeRefractoryAuditError(
                "single S1-IB audit result is incomplete or inconsistent"
            )
        for role in (
            "f_high_engagement",
            "r_high_engagement",
            "engagement_difference",
            "roundoff_floor",
        ):
            object.__setattr__(
                self,
                role,
                _finite_nonnegative(getattr(self, role), role),
            )

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "case_records": [
                record.canonical_payload() for record in self.case_records
            ],
            "f_high_engagement": self.f_high_engagement,
            "r_high_engagement": self.r_high_engagement,
            "engagement_difference": self.engagement_difference,
            "roundoff_floor": self.roundoff_floor,
            "baseline_records": [list(record) for record in self.baseline_records],
            "pure_step_calls": self.pure_step_calls,
            "field_steps": self.field_steps,
            "stopp_reasons": list(self.stopp_reasons),
            "decision": self.decision,
        }
        if include_digest:
            payload["receipt_digest"] = self.receipt_digest
        return payload


@dataclass(frozen=True, slots=True)
class DTS1S1IBDoubleAuditResult:
    audit_id: str
    source_s1ia_contract_digest: str
    case_records: tuple[DTS1S1IBCaseRecord, ...]
    f_high_engagement: float
    r_high_engagement: float
    engagement_difference: float
    roundoff_floor: float
    baseline_records: tuple[tuple[str, str], ...]
    first_receipt_digest: str
    repeat_receipt_digest: str
    repeated_receipts_identical: bool
    pure_resource_step_calls: int
    field_steps: int
    research_field_steps: int
    stopp_reasons: tuple[str, ...]
    decision: str
    audit_receipt_digest: str

    def __post_init__(self) -> None:
        payload = self.canonical_payload(include_digest=False)
        if (
            self.audit_id != S1_IB_AUDIT_ID
            or self.source_s1ia_contract_digest
            != S1_IB_SOURCE_S1IA_CONTRACT_DIGEST
            or tuple(record.case_id for record in self.case_records)
            != S1_IB_CASE_IDS
            or self.baseline_records != _baseline_records()
            or self.repeated_receipts_identical
            != (self.first_receipt_digest == self.repeat_receipt_digest)
            or self.pure_resource_step_calls
            != S1_IB_DOUBLE_AUDIT_PURE_STEP_CALLS
            or self.field_steps != 0
            or self.research_field_steps != 0
            or self.decision not in (S1_IB_PASS, S1_IB_STOPP)
            or (self.decision == S1_IB_PASS)
            != (not self.stopp_reasons and self.repeated_receipts_identical)
            or self.audit_receipt_digest != _digest(payload)
        ):
            raise DTS1FreeRefractoryAuditError(
                "double S1-IB audit result violates the preregistered boundary"
            )

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "audit_id": self.audit_id,
            "source_s1ia_contract_digest": self.source_s1ia_contract_digest,
            "case_records": [
                record.canonical_payload() for record in self.case_records
            ],
            "f_high_engagement": self.f_high_engagement,
            "r_high_engagement": self.r_high_engagement,
            "engagement_difference": self.engagement_difference,
            "roundoff_floor": self.roundoff_floor,
            "baseline_records": [list(record) for record in self.baseline_records],
            "first_receipt_digest": self.first_receipt_digest,
            "repeat_receipt_digest": self.repeat_receipt_digest,
            "repeated_receipts_identical": self.repeated_receipts_identical,
            "pure_resource_step_calls": self.pure_resource_step_calls,
            "field_steps": self.field_steps,
            "research_field_steps": self.research_field_steps,
            "stopp_reasons": list(self.stopp_reasons),
            "decision": self.decision,
        }
        if include_digest:
            payload["audit_receipt_digest"] = self.audit_receipt_digest
        return payload


def _anatomy(refractory: float) -> DTS1ResourceAnatomy:
    return DTS1ResourceAnatomy(
        tuple(DTS1NodeCapacity(node_id, _CAPACITY) for node_id in _NODE_IDS),
        (DTS1EdgeResource(*_EDGE, _CONDUCTIVE, refractory),),
    )


def _participations(value: float) -> tuple[DTS1EdgeParticipation, ...]:
    return (DTS1EdgeParticipation(*_EDGE, value),)


def _baseline_records() -> tuple[tuple[str, str], ...]:
    return tuple(
        (baseline_id, _BASELINE_RECORD_VALUE)
        for baseline_id, _ in S1_HZ_BASELINE_COUNTERPREDICTIONS
    )


def _result_payload(result: DTS1StepResult) -> tuple[object, ...]:
    transfer = result.edge_transfers[0]
    return (
        transfer.engagement,
        transfer.turnover,
        transfer.recovery,
        result.input_anatomy_digest,
        result.output_anatomy_digest,
        result.maximum_local_ledger_residual,
        result.global_ledger_residual,
        result.next_anatomy.global_accounted_resource,
        result.next_anatomy.global_capacity,
    )


def _matching_preflight() -> tuple[DTS1ResourceAnatomy, DTS1ResourceAnatomy]:
    f_high = _anatomy(_F_HIGH_REFRACTORY)
    r_high = _anatomy(_R_HIGH_REFRACTORY)
    f_ledgers = f_high.local_ledgers()
    r_ledgers = r_high.local_ledgers()
    valid = (
        f_high.node_capacities == r_high.node_capacities
        and tuple(edge.edge for edge in f_high.edge_resources)
        == tuple(edge.edge for edge in r_high.edge_resources)
        and f_high.edge_resources[0].conductive_bound
        == r_high.edge_resources[0].conductive_bound
        == _CONDUCTIVE
        and tuple(ledger.free for ledger in f_ledgers) == (0.7, 0.7)
        and tuple(ledger.free for ledger in r_ledgers)
        == (0.3999999999999999, 0.3999999999999999)
        and all(ledger.residual == 0.0 for ledger in f_ledgers + r_ledgers)
        and f_high.global_capacity == r_high.global_capacity == 2.0
        and f_high.global_accounted_resource
        == r_high.global_accounted_resource
        == 2.0
        and f_high.global_residual == r_high.global_residual == 0.0
        and 0.5 * S1_IB_EXPECTED_F_HIGH_ENGAGEMENT < f_ledgers[0].free
        and 0.5 * S1_IB_EXPECTED_R_HIGH_ENGAGEMENT < r_ledgers[0].free
    )
    if not valid:
        raise DTS1FreeRefractoryAuditError(
            "S1-IB matching, ledger, interior, or nonsaturation preflight failed"
        )
    return f_high, r_high


def _call(
    anatomy: DTS1ResourceAnatomy,
    participation: float,
    rates: DTS1StepRates,
    counter: list[int],
) -> DTS1StepResult:
    counter[0] += 1
    return compute_dts1_closed_prestate_step(
        anatomy,
        _participations(participation),
        _ELAPSED_TIME,
        rates,
    )


def _case_record(
    case_id: str,
    arm_ids: tuple[str, str],
    results: tuple[DTS1StepResult, DTS1StepResult],
    exact_checks: tuple[tuple[str, bool], ...],
) -> DTS1S1IBCaseRecord:
    return DTS1S1IBCaseRecord(
        case_id=case_id,
        arm_ids=arm_ids,
        input_anatomy_digests=tuple(
            result.input_anatomy_digest for result in results
        ),
        result_payloads=tuple(_result_payload(result) for result in results),
        exact_checks=exact_checks,
        maximum_local_ledger_residual=max(
            result.maximum_local_ledger_residual for result in results
        ),
        maximum_global_ledger_residual=max(
            result.global_ledger_residual for result in results
        ),
        pure_step_calls=2,
    )


def _execute_once() -> _DTS1S1IBSingleAuditResult:
    f_high, r_high = _matching_preflight()
    counter = [0]

    c01_results = (
        _call(f_high, _POSITIVE_PARTICIPATION, _POSITIVE_RATES, counter),
        _call(r_high, _POSITIVE_PARTICIPATION, _POSITIVE_RATES, counter),
    )
    f_engagement = c01_results[0].edge_transfers[0].engagement
    r_engagement = c01_results[1].edge_transfers[0].engagement
    difference = f_engagement - r_engagement
    c01 = _case_record(
        S1_IB_CASE_IDS[0],
        S1_IB_ARM_IDS,
        c01_results,
        (
            (
                "F_HIGH_matches_preregistered_engagement",
                abs(f_engagement - S1_IB_EXPECTED_F_HIGH_ENGAGEMENT)
                <= S1_IB_ROUNDOFF_FLOOR,
            ),
            (
                "R_HIGH_matches_preregistered_engagement",
                abs(r_engagement - S1_IB_EXPECTED_R_HIGH_ENGAGEMENT)
                <= S1_IB_ROUNDOFF_FLOOR,
            ),
            (
                "engagement_difference_above_floor",
                difference > S1_IB_ROUNDOFF_FLOOR,
            ),
            ("F_HIGH_strictly_greater", f_engagement > r_engagement),
        ),
    )

    n01_results = (
        _call(f_high, _POSITIVE_PARTICIPATION, _POSITIVE_RATES, counter),
        _call(f_high, _POSITIVE_PARTICIPATION, _POSITIVE_RATES, counter),
    )
    n01 = _case_record(
        S1_IB_CASE_IDS[1],
        (S1_IB_ARM_IDS[0], S1_IB_ARM_IDS[0]),
        n01_results,
        (("complete_results_bit_exact", n01_results[0] == n01_results[1]),),
    )

    n02_results = (
        _call(f_high, 0.0, _POSITIVE_RATES, counter),
        _call(r_high, 0.0, _POSITIVE_RATES, counter),
    )
    n02 = _case_record(
        S1_IB_CASE_IDS[2],
        S1_IB_ARM_IDS,
        n02_results,
        (
            (
                "both_engagements_exact_zero",
                all(result.edge_transfers[0].engagement == 0.0 for result in n02_results),
            ),
        ),
    )

    n03_results = (
        _call(f_high, _POSITIVE_PARTICIPATION, _ZERO_BINDING_RATES, counter),
        _call(r_high, _POSITIVE_PARTICIPATION, _ZERO_BINDING_RATES, counter),
    )
    n03 = _case_record(
        S1_IB_CASE_IDS[3],
        S1_IB_ARM_IDS,
        n03_results,
        (
            (
                "both_engagements_exact_zero",
                all(result.edge_transfers[0].engagement == 0.0 for result in n03_results),
            ),
        ),
    )

    cases = (c01, n01, n02, n03)
    reasons = []
    if counter[0] != S1_IB_SINGLE_AUDIT_PURE_STEP_CALLS:
        reasons.append("pure-step-call-count-drift")
    if any(not value for case in cases for _, value in case.exact_checks):
        reasons.append("preregistered-exact-or-directed-check-failed")
    if any(
        max(
            case.maximum_local_ledger_residual,
            case.maximum_global_ledger_residual,
        )
        > S1_IB_ROUNDOFF_FLOOR
        for case in cases
    ):
        reasons.append("resource-ledger-residual-exceeds-floor")
    if abs(difference - S1_IB_EXPECTED_ENGAGEMENT_DIFFERENCE) > S1_IB_ROUNDOFF_FLOOR:
        reasons.append("engagement-difference-deviates-from-preregistration")
    decision = S1_IB_PASS if not reasons else S1_IB_STOPP
    values = {
        "case_records": cases,
        "f_high_engagement": f_engagement,
        "r_high_engagement": r_engagement,
        "engagement_difference": difference,
        "roundoff_floor": S1_IB_ROUNDOFF_FLOOR,
        "baseline_records": _baseline_records(),
        "pure_step_calls": counter[0],
        "field_steps": 0,
        "stopp_reasons": tuple(reasons),
        "decision": decision,
    }
    digest_payload = {
        **values,
        "case_records": [case.canonical_payload() for case in cases],
        "baseline_records": [list(record) for record in values["baseline_records"]],
        "stopp_reasons": list(values["stopp_reasons"]),
    }
    return _DTS1S1IBSingleAuditResult(
        **values,
        receipt_digest=_digest(digest_payload),
    )


def execute_dts1_s1ib_preregistered_double_audit() -> DTS1S1IBDoubleAuditResult:
    """Execute exactly two deterministic eight-call pure resource audits."""

    first = _execute_once()
    repeated = _execute_once()
    repeat_equal = first.receipt_digest == repeated.receipt_digest
    reasons = list(first.stopp_reasons)
    if repeated.stopp_reasons != first.stopp_reasons:
        reasons.append("repeat-stopp-reasons-differ")
    if not repeat_equal:
        reasons.append("repeated-receipt-digest-mismatch")
    decision = S1_IB_PASS if not reasons and repeat_equal else S1_IB_STOPP
    values = {
        "audit_id": S1_IB_AUDIT_ID,
        "source_s1ia_contract_digest": S1_IB_SOURCE_S1IA_CONTRACT_DIGEST,
        "case_records": first.case_records,
        "f_high_engagement": first.f_high_engagement,
        "r_high_engagement": first.r_high_engagement,
        "engagement_difference": first.engagement_difference,
        "roundoff_floor": first.roundoff_floor,
        "baseline_records": first.baseline_records,
        "first_receipt_digest": first.receipt_digest,
        "repeat_receipt_digest": repeated.receipt_digest,
        "repeated_receipts_identical": repeat_equal,
        "pure_resource_step_calls": (
            first.pure_step_calls + repeated.pure_step_calls
        ),
        "field_steps": 0,
        "research_field_steps": 0,
        "stopp_reasons": tuple(dict.fromkeys(reasons)),
        "decision": decision,
    }
    digest_payload = {
        **values,
        "case_records": [
            case.canonical_payload() for case in first.case_records
        ],
        "baseline_records": [list(record) for record in first.baseline_records],
        "stopp_reasons": list(values["stopp_reasons"]),
    }
    return DTS1S1IBDoubleAuditResult(
        **values,
        audit_receipt_digest=_digest(digest_payload),
    )
