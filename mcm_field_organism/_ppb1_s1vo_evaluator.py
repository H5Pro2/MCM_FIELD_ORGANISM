"""Private pure S1-VO evaluator and static PPB-1 matrix preflight."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from ._ppb1_s1vn_matrix import (
    S1VN_BASELINE_IDS,
    S1VN_EXPECTED_BASELINE_CALLS,
    S1VN_EXPECTED_CASE_COUNT,
    S1VN_EXPECTED_PPB_CALLS,
    S1VN_EXPECTED_TOTAL_CALLS,
    S1VN_FAMILY_IDS,
    S1VN_FIXTURE_IDS,
    S1VN_MATRIX_EXECUTION_BLOCKED,
    S1VN_MODALITY_IDS,
    S1VN_PARAMETER_IDS,
    S1VNBaselineReadout,
    S1VNCaseReceipt,
    S1VNMatrixError,
    S1VNMatrixResult,
    execute_s1vn_matrix,
    prepare_s1vn_matrix_runner,
    s1vn_config,
    s1vn_matrix_plan,
)


S1VO_SCHEMA_VERSION = "ppb1.s1vo.private.v1"
S1VO_EXPECTED_SUMMARY_COUNT = 48
S1VO_EXPECTED_DIAGNOSTIC_PROBE_COUNT = 6
S1VO_EXPECTED_PLAN_DIGEST = (
    "35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3"
)
S1VO_BLOCKERS = (
    "BASELINE_SELECTED_ENTRY_IDENTITY_NOT_RECORDED",
    "F04_F05_F06_REPEATABILITY_PATHS_NOT_REGISTERED",
)
S1VO_PREFLIGHT_DECISION = "BLOCKED_CONTRACT_CORRECTION_REQUIRED_NO_EXECUTION"
S1VO_SELECTIONS = S1VN_PARAMETER_IDS + ("NO_ADMISSIBLE_CONFIGURATION",)

S1VO_INVALID_SUMMARY = "S1VO_INVALID_SUMMARY"
S1VO_INVALID_EVALUATION_INPUT = "S1VO_INVALID_EVALUATION_INPUT"
S1VO_PREFLIGHT_DRIFT = "S1VO_PREFLIGHT_DRIFT"


class S1VOEvaluatorError(ValueError):
    """One fail-closed S1-VO evaluator or preflight violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class S1VOArmSummary:
    family_id: str
    parameter_id: str
    modality_id: str
    lifecycle_valid: bool
    diagnostic_probe_count: int
    diagnostic_match_count: int
    near_assignment_consistent: bool
    separated_assignment_distinct: bool
    repeatability_confirmed: bool
    peak_logical_value_count: int
    accepted_call_count: int

    def __post_init__(self) -> None:
        if (
            self.family_id not in S1VN_FAMILY_IDS
            or self.parameter_id not in S1VN_PARAMETER_IDS
            or self.modality_id not in S1VN_MODALITY_IDS
        ):
            raise S1VOEvaluatorError(
                S1VO_INVALID_SUMMARY, "unknown family, parameter, or modality"
            )
        for role in (
            "lifecycle_valid",
            "near_assignment_consistent",
            "separated_assignment_distinct",
            "repeatability_confirmed",
        ):
            if not isinstance(getattr(self, role), bool):
                raise S1VOEvaluatorError(
                    S1VO_INVALID_SUMMARY, f"{role} must be boolean"
                )
        if (
            self.diagnostic_probe_count != S1VO_EXPECTED_DIAGNOSTIC_PROBE_COUNT
            or isinstance(self.diagnostic_match_count, bool)
            or not isinstance(self.diagnostic_match_count, int)
            or self.diagnostic_match_count < 0
            or self.diagnostic_match_count > self.diagnostic_probe_count
            or isinstance(self.peak_logical_value_count, bool)
            or not isinstance(self.peak_logical_value_count, int)
            or self.peak_logical_value_count < 0
            or isinstance(self.accepted_call_count, bool)
            or not isinstance(self.accepted_call_count, int)
            or self.accepted_call_count <= 0
        ):
            raise S1VOEvaluatorError(
                S1VO_INVALID_SUMMARY, "summary counts are outside the contract"
            )

    @property
    def avoids_always_and_never_match(self) -> bool:
        return 0 < self.diagnostic_match_count < self.diagnostic_probe_count

    @property
    def admissible(self) -> bool:
        return all(
            (
                self.lifecycle_valid,
                self.avoids_always_and_never_match,
                self.near_assignment_consistent,
                self.separated_assignment_distinct,
                self.repeatability_confirmed,
            )
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VO_SCHEMA_VERSION,
            "family_id": self.family_id,
            "parameter_id": self.parameter_id,
            "modality_id": self.modality_id,
            "lifecycle_valid": self.lifecycle_valid,
            "diagnostic_probe_count": self.diagnostic_probe_count,
            "diagnostic_match_count": self.diagnostic_match_count,
            "near_assignment_consistent": self.near_assignment_consistent,
            "separated_assignment_distinct": self.separated_assignment_distinct,
            "repeatability_confirmed": self.repeatability_confirmed,
            "peak_logical_value_count": self.peak_logical_value_count,
            "accepted_call_count": self.accepted_call_count,
        }


@dataclass(frozen=True, slots=True)
class S1VOModalityDecision:
    modality_id: str
    selection: str
    admissible_parameter_ids: tuple[str, ...]
    reduced_parameter_ids: tuple[str, ...]
    explaining_baseline_ids: tuple[str, ...]
    reason: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "modality_id": self.modality_id,
            "selection": self.selection,
            "admissible_parameter_ids": list(self.admissible_parameter_ids),
            "reduced_parameter_ids": list(self.reduced_parameter_ids),
            "explaining_baseline_ids": list(self.explaining_baseline_ids),
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class S1VOEvaluationResult:
    decisions: tuple[S1VOModalityDecision, ...]
    input_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VO_SCHEMA_VERSION,
            "decisions": [item.canonical_payload() for item in self.decisions],
            "input_digest": self.input_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _expected_calls(parameter_id: str, modality_id: str) -> int:
    config = s1vn_config(parameter_id, modality_id)
    return 42 + config.capacity + 2 * config.expire_after_steps


def _baseline_explains(
    ppb: S1VOArmSummary, baseline: S1VOArmSummary
) -> bool:
    return (
        baseline.family_id != "B07"
        and baseline.admissible
        and baseline.peak_logical_value_count <= ppb.peak_logical_value_count
        and baseline.accepted_call_count <= ppb.accepted_call_count
    )


def evaluate_s1vo_summaries(
    summaries: tuple[S1VOArmSummary, ...],
) -> S1VOEvaluationResult:
    """Apply the S1-VM stop, reduction, and simplicity order purely."""

    if len(summaries) != S1VO_EXPECTED_SUMMARY_COUNT:
        raise S1VOEvaluatorError(
            S1VO_INVALID_EVALUATION_INPUT,
            "exactly 48 family/parameter/modality summaries are required",
        )
    by_key: dict[tuple[str, str, str], S1VOArmSummary] = {}
    for summary in summaries:
        key = (summary.family_id, summary.parameter_id, summary.modality_id)
        if key in by_key or summary.accepted_call_count != _expected_calls(
            summary.parameter_id, summary.modality_id
        ):
            raise S1VOEvaluatorError(
                S1VO_INVALID_EVALUATION_INPUT,
                "summary inventory or accepted call count drifted",
            )
        by_key[key] = summary
    expected = {
        (family, parameter, modality)
        for family in S1VN_FAMILY_IDS
        for parameter in S1VN_PARAMETER_IDS
        for modality in S1VN_MODALITY_IDS
    }
    if set(by_key) != expected:
        raise S1VOEvaluatorError(
            S1VO_INVALID_EVALUATION_INPUT, "summary cross product is incomplete"
        )

    decisions: list[S1VOModalityDecision] = []
    for modality_id in S1VN_MODALITY_IDS:
        admissible: list[S1VOArmSummary] = []
        reduced: list[str] = []
        explainers: set[str] = set()
        for parameter_id in S1VN_PARAMETER_IDS:
            ppb = by_key[("PPB1", parameter_id, modality_id)]
            if not ppb.admissible:
                continue
            matching_baselines = tuple(
                baseline_id
                for baseline_id in S1VN_BASELINE_IDS
                if _baseline_explains(
                    ppb, by_key[(baseline_id, parameter_id, modality_id)]
                )
            )
            if matching_baselines:
                reduced.append(parameter_id)
                explainers.update(matching_baselines)
            else:
                admissible.append(ppb)
        admissible.sort(
            key=lambda item: (
                item.peak_logical_value_count,
                S1VN_PARAMETER_IDS.index(item.parameter_id),
            )
        )
        if admissible:
            selection = admissible[0].parameter_id
            reason = "LEAST_STATE_ADMISSIBLE_NONREDUCED_RECORD"
        elif reduced:
            selection = "NO_ADMISSIBLE_CONFIGURATION"
            reason = "ALL_ADMISSIBLE_RECORDS_REDUCED_BY_SIMPLER_BASELINE"
        else:
            selection = "NO_ADMISSIBLE_CONFIGURATION"
            reason = "NO_RECORD_PASSES_BOUND_STOP_RULES"
        decisions.append(
            S1VOModalityDecision(
                modality_id,
                selection,
                tuple(item.parameter_id for item in admissible),
                tuple(reduced),
                tuple(sorted(explainers)),
                reason,
            )
        )
    input_digest = _digest(
        [item.canonical_payload() for item in sorted(
            summaries,
            key=lambda row: (
                S1VN_FAMILY_IDS.index(row.family_id),
                S1VN_PARAMETER_IDS.index(row.parameter_id),
                S1VN_MODALITY_IDS.index(row.modality_id),
            ),
        )]
    )
    return S1VOEvaluationResult(tuple(decisions), input_digest)


@dataclass(frozen=True, slots=True)
class S1VOPreflightResult:
    decision: str
    plan_digest: str
    case_count: int
    total_call_budget: int
    accepted_call_count: int
    checks: tuple[tuple[str, bool], ...]
    blockers: tuple[str, ...]

    @property
    def ready_for_execution(self) -> bool:
        return not self.blockers and all(value for _, value in self.checks)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VO_SCHEMA_VERSION,
            "decision": self.decision,
            "plan_digest": self.plan_digest,
            "case_count": self.case_count,
            "total_call_budget": self.total_call_budget,
            "accepted_call_count": self.accepted_call_count,
            "checks": [{"role": role, "passed": passed} for role, passed in self.checks],
            "blockers": list(self.blockers),
            "ready_for_execution": self.ready_for_execution,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def run_s1vo_static_preflight() -> S1VOPreflightResult:
    """Audit S1-VN statically and keep the registered matrix unexecuted."""

    preparation = prepare_s1vn_matrix_runner()
    plan = s1vn_matrix_plan()
    execution_gate_active = False
    try:
        execute_s1vn_matrix()
    except S1VNMatrixError as exc:
        execution_gate_active = exc.code == S1VN_MATRIX_EXECUTION_BLOCKED

    family_history_groups: dict[tuple[str, str, str], set[tuple[int, str]]] = {}
    for path in plan:
        key = (path.parameter_id, path.modality_id, path.fixture_id)
        family_history_groups.setdefault(key, set()).add(
            (path.expected_call_count, path.config_digest)
        )
    common_histories_bound = (
        len(family_history_groups)
        == len(S1VN_PARAMETER_IDS) * len(S1VN_MODALITY_IDS) * len(S1VN_FIXTURE_IDS)
        and all(len(values) == 1 for values in family_history_groups.values())
    )

    repeatability_paths_present = all(
        sum(
            path.family_id == family
            and path.parameter_id == parameter
            and path.modality_id == modality
            and path.fixture_id == fixture
            for path in plan
        )
        >= 2
        for family in S1VN_FAMILY_IDS
        for parameter in S1VN_PARAMETER_IDS
        for modality in S1VN_MODALITY_IDS
        for fixture in ("F04", "F05", "F06")
    )
    baseline_readout_fields = {item.name for item in fields(S1VNBaselineReadout)}
    baseline_selected_identity_recorded = "selected_entry_id" in baseline_readout_fields
    result_roles_present = {
        "path_id",
        "family_id",
        "accepted_call_count",
        "observations",
        "input_history_digest",
        "final_state_digest",
    }.issubset({item.name for item in fields(S1VNCaseReceipt)}) and {
        "plan_digest",
        "case_receipts",
        "accepted_call_count",
    }.issubset({item.name for item in fields(S1VNMatrixResult)})

    checks = (
        ("PLAN_DIGEST_MATCHES_S1VN", preparation.plan_digest == S1VO_EXPECTED_PLAN_DIGEST),
        ("EXACT_384_CASES", preparation.case_count == S1VN_EXPECTED_CASE_COUNT),
        ("EXACT_9296_PPB_CALLS", preparation.ppb_call_count == S1VN_EXPECTED_PPB_CALLS),
        ("EXACT_65072_BASELINE_CALLS", preparation.baseline_call_count == S1VN_EXPECTED_BASELINE_CALLS),
        ("EXACT_74368_TOTAL_CALLS", preparation.total_call_count == S1VN_EXPECTED_TOTAL_CALLS),
        ("ZERO_REGISTERED_CALLS_EXECUTED", preparation.accepted_call_count == 0),
        ("EXECUTION_GATE_ACTIVE", execution_gate_active),
        ("COMMON_CAUSAL_HISTORIES_BOUND", common_histories_bound),
        ("TYPED_RESULT_ROLES_PRESENT", result_roles_present),
        ("BASELINE_SELECTED_IDENTITY_RECORDED", baseline_selected_identity_recorded),
        ("F04_F05_F06_REPEATABILITY_PATHS_PRESENT", repeatability_paths_present),
    )
    blockers = tuple(
        blocker
        for blocker, passed in (
            (S1VO_BLOCKERS[0], baseline_selected_identity_recorded),
            (S1VO_BLOCKERS[1], repeatability_paths_present),
        )
        if not passed
    )
    if blockers != S1VO_BLOCKERS:
        raise S1VOEvaluatorError(
            S1VO_PREFLIGHT_DRIFT, "preflight blockers do not match the static audit"
        )
    return S1VOPreflightResult(
        S1VO_PREFLIGHT_DECISION,
        preparation.plan_digest,
        preparation.case_count,
        preparation.total_call_count,
        preparation.accepted_call_count,
        checks,
        blockers,
    )
