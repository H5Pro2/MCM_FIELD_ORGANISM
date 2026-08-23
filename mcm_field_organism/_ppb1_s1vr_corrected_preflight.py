"""Final static S1-VR preflight for the corrected private PPB-1 matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from ._ppb1_s1vn_matrix import (
    S1VN_FAMILY_IDS,
    S1VN_MODALITY_IDS,
    S1VN_PARAMETER_IDS,
    prepare_s1vn_matrix_runner,
    s1vn_matrix_plan,
)
from ._ppb1_s1vo_evaluator import S1VOArmSummary
from ._ppb1_s1vq_corrected_matrix import (
    S1VQ_EXPECTED_BASELINE_CALLS,
    S1VQ_EXPECTED_CASE_COUNT,
    S1VQ_EXPECTED_PPB_CALLS,
    S1VQ_EXPECTED_TOTAL_CALLS,
    S1VQ_MATRIX_EXECUTION_BLOCKED,
    S1VQ_PARENT_PLAN_DIGEST,
    S1VQ_REPEAT_FIXTURE_IDS,
    S1VQBaselineCarry,
    S1VQBaselineReadout,
    S1VQCaseReceipt,
    S1VQIdentityObservation,
    S1VQMatrixError,
    S1VQMatrixResult,
    execute_s1vq_corrected_matrix,
    prepare_s1vq_corrected_runner,
    s1vq_corrected_matrix_plan,
)


S1VR_SCHEMA_VERSION = "ppb1.s1vr.private.v1"
S1VR_EXPECTED_CORRECTED_PLAN_DIGEST = (
    "f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210"
)
S1VR_CLOSED_S1VO_BLOCKERS = (
    "BASELINE_SELECTED_ENTRY_IDENTITY_NOT_RECORDED",
    "F04_F05_F06_REPEATABILITY_PATHS_NOT_REGISTERED",
)
S1VR_BLOCKERS = (
    "CORRECTED_MATRIX_RESULT_NOT_CANONICALLY_SEALED",
    "CORRECTED_RECEIPT_TO_EVALUATOR_SUMMARY_COMPOSITOR_MISSING",
    "EVALUATOR_SUMMARY_LACKS_IDENTITY_METADATA_BUDGET",
)
S1VR_PREFLIGHT_DECISION = "BLOCKED_RESULT_PIPELINE_CORRECTION_REQUIRED_NO_EXECUTION"

S1VR_PREFLIGHT_DRIFT = "S1VR_PREFLIGHT_DRIFT"


class S1VRPreflightError(ValueError):
    """One fail-closed S1-VR audit violation."""

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
class S1VRPreflightResult:
    decision: str
    parent_plan_digest: str
    corrected_plan_digest: str
    case_count: int
    ppb_call_budget: int
    baseline_call_budget: int
    total_call_budget: int
    accepted_call_count: int
    checks: tuple[tuple[str, bool], ...]
    closed_s1vo_blockers: tuple[str, ...]
    blockers: tuple[str, ...]

    @property
    def ready_for_execution(self) -> bool:
        return not self.blockers and all(passed for _, passed in self.checks)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VR_SCHEMA_VERSION,
            "decision": self.decision,
            "parent_plan_digest": self.parent_plan_digest,
            "corrected_plan_digest": self.corrected_plan_digest,
            "case_count": self.case_count,
            "ppb_call_budget": self.ppb_call_budget,
            "baseline_call_budget": self.baseline_call_budget,
            "total_call_budget": self.total_call_budget,
            "accepted_call_count": self.accepted_call_count,
            "checks": [
                {"role": role, "passed": passed} for role, passed in self.checks
            ],
            "closed_s1vo_blockers": list(self.closed_s1vo_blockers),
            "blockers": list(self.blockers),
            "ready_for_execution": self.ready_for_execution,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _r0_preserves_parent_plan() -> bool:
    parent = s1vn_matrix_plan()
    corrected_r0 = tuple(
        path for path in s1vq_corrected_matrix_plan() if path.repeat_id == "R0"
    )
    return len(parent) == len(corrected_r0) and all(
        (
            child.parent_path_id,
            child.family_id,
            child.parameter_id,
            child.modality_id,
            child.fixture_id,
            child.expected_call_count,
            child.config_digest,
        )
        == (
            source.path_id,
            source.family_id,
            source.parameter_id,
            source.modality_id,
            source.fixture_id,
            source.expected_call_count,
            source.config_digest,
        )
        for source, child in zip(parent, corrected_r0, strict=True)
    )


def _repeat_paths_are_fresh_and_adjacent() -> bool:
    plan = s1vq_corrected_matrix_plan()
    repeat_count = 0
    for index, path in enumerate(plan):
        if path.repeat_id != "R1":
            continue
        repeat_count += 1
        if index == 0:
            return False
        primary = plan[index - 1]
        if (
            primary.repeat_id != "R0"
            or path.fixture_id not in S1VQ_REPEAT_FIXTURE_IDS
            or (
                primary.parent_path_id,
                primary.family_id,
                primary.parameter_id,
                primary.modality_id,
                primary.fixture_id,
                primary.expected_call_count,
                primary.config_digest,
            )
            != (
                path.parent_path_id,
                path.family_id,
                path.parameter_id,
                path.modality_id,
                path.fixture_id,
                path.expected_call_count,
                path.config_digest,
            )
        ):
            return False
    expected = (
        len(S1VN_FAMILY_IDS)
        * len(S1VN_PARAMETER_IDS)
        * len(S1VN_MODALITY_IDS)
        * len(S1VQ_REPEAT_FIXTURE_IDS)
    )
    return repeat_count == expected


def run_s1vr_static_preflight() -> S1VRPreflightResult:
    """Audit the corrected result path without running a registered case."""

    parent = prepare_s1vn_matrix_runner()
    corrected = prepare_s1vq_corrected_runner()
    plan = s1vq_corrected_matrix_plan()

    execution_gate_active = False
    try:
        execute_s1vq_corrected_matrix()
    except S1VQMatrixError as exc:
        execution_gate_active = exc.code == S1VQ_MATRIX_EXECUTION_BLOCKED

    baseline_readout_roles = {
        "selected_entry_id",
        "written_entry_id",
        "selected_prestate_digest",
        "active_identity_count",
        "active_identity_digest",
        "postcarry_digest",
    }.issubset({item.name for item in fields(S1VQBaselineReadout)})
    identity_carry_roles = {
        "base_state",
        "entry_ids",
        "slot_generations",
    }.issubset({item.name for item in fields(S1VQBaselineCarry)})
    identity_observation_roles = {
        "selected_entry_id",
        "written_entry_id",
        "selected_prestate_digest",
        "active_identity_count",
        "active_identity_digest",
    }.issubset({item.name for item in fields(S1VQIdentityObservation)})
    receipt_roles = {
        "path",
        "base_receipt",
        "identity_observations",
    }.issubset({item.name for item in fields(S1VQCaseReceipt)}) and all(
        callable(getattr(S1VQCaseReceipt, role, None))
        for role in ("normalized_repeat_payload", "repeat_comparison_digest")
    )

    matrix_result_sealed = (
        callable(getattr(S1VQMatrixResult, "canonical_payload", None))
        and callable(getattr(S1VQMatrixResult, "digest", None))
        and "__post_init__" in S1VQMatrixResult.__dict__
    )
    result_compositor_present = callable(
        getattr(S1VQMatrixResult, "to_s1vo_summaries", None)
    )
    summary_roles = {item.name for item in fields(S1VOArmSummary)}
    identity_metadata_budget_present = (
        "peak_identity_metadata_value_count" in summary_roles
    )

    corrected_identity_closed = (
        baseline_readout_roles and identity_carry_roles and identity_observation_roles
    )
    corrected_repeats_closed = _repeat_paths_are_fresh_and_adjacent()
    closed_s1vo_blockers = tuple(
        blocker
        for blocker, closed in zip(
            S1VR_CLOSED_S1VO_BLOCKERS,
            (corrected_identity_closed, corrected_repeats_closed),
            strict=True,
        )
        if closed
    )

    checks = (
        ("PARENT_PLAN_DIGEST_PRESERVED", parent.plan_digest == S1VQ_PARENT_PLAN_DIGEST),
        ("R0_PLAN_PRESERVES_ALL_384_PARENT_PATHS", _r0_preserves_parent_plan()),
        (
            "CORRECTED_PLAN_DIGEST_MATCHES_S1VQ",
            corrected.corrected_plan_digest == S1VR_EXPECTED_CORRECTED_PLAN_DIGEST,
        ),
        ("EXACT_528_CASES", corrected.case_count == S1VQ_EXPECTED_CASE_COUNT),
        ("EXACT_9476_PPB_CALLS", corrected.ppb_call_count == S1VQ_EXPECTED_PPB_CALLS),
        (
            "EXACT_66332_BASELINE_CALLS",
            corrected.baseline_call_count == S1VQ_EXPECTED_BASELINE_CALLS,
        ),
        (
            "EXACT_75808_TOTAL_CALLS",
            corrected.total_call_count == S1VQ_EXPECTED_TOTAL_CALLS,
        ),
        ("ZERO_REGISTERED_CALLS_EXECUTED", corrected.accepted_call_count == 0),
        ("EXECUTION_GATE_ACTIVE", execution_gate_active),
        ("PATH_IDS_ARE_UNIQUE", len({item.path_id for item in plan}) == len(plan)),
        ("BASELINE_IDENTITY_ROLES_PRESENT", corrected_identity_closed),
        ("F04_F05_F06_R0_R1_PATHS_PRESENT", corrected_repeats_closed),
        ("NORMALIZED_REPEAT_RECEIPT_ROLES_PRESENT", receipt_roles),
        ("CORRECTED_MATRIX_RESULT_CANONICALLY_SEALED", matrix_result_sealed),
        (
            "CORRECTED_RECEIPT_TO_48_SUMMARY_COMPOSITOR_PRESENT",
            result_compositor_present,
        ),
        (
            "EVALUATOR_SUMMARY_COUNTS_IDENTITY_METADATA",
            identity_metadata_budget_present,
        ),
    )
    blockers = tuple(
        blocker
        for blocker, resolved in zip(
            S1VR_BLOCKERS,
            (
                matrix_result_sealed,
                result_compositor_present,
                identity_metadata_budget_present,
            ),
            strict=True,
        )
        if not resolved
    )
    if (
        closed_s1vo_blockers != S1VR_CLOSED_S1VO_BLOCKERS
        or blockers != S1VR_BLOCKERS
        or any(
            not passed
            for role, passed in checks
            if role
            not in {
                "CORRECTED_MATRIX_RESULT_CANONICALLY_SEALED",
                "CORRECTED_RECEIPT_TO_48_SUMMARY_COMPOSITOR_PRESENT",
                "EVALUATOR_SUMMARY_COUNTS_IDENTITY_METADATA",
            }
        )
    ):
        raise S1VRPreflightError(
            S1VR_PREFLIGHT_DRIFT,
            "corrected preflight inventory no longer matches the bound audit",
        )

    return S1VRPreflightResult(
        S1VR_PREFLIGHT_DECISION,
        corrected.parent_plan_digest,
        corrected.corrected_plan_digest,
        corrected.case_count,
        corrected.ppb_call_count,
        corrected.baseline_call_count,
        corrected.total_call_count,
        corrected.accepted_call_count,
        checks,
        closed_s1vo_blockers,
        blockers,
    )
