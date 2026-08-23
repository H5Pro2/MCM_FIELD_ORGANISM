"""Private S1-VT result envelope, compositor, and corrected evaluator."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from ._ppb1_s1vn_matrix import (
    S1VN_BASELINE_IDS,
    S1VN_FAMILY_IDS,
    S1VN_FIXTURE_IDS,
    S1VN_MODALITY_IDS,
    S1VN_PARAMETER_IDS,
    S1VNCaseReceipt,
    S1VNStepObservation,
    s1vn_config,
)
from ._ppb1_s1vq_corrected_matrix import (
    S1VQ_EXPECTED_BASELINE_CALLS,
    S1VQ_EXPECTED_CASE_COUNT,
    S1VQ_EXPECTED_PPB_CALLS,
    S1VQ_EXPECTED_TOTAL_CALLS,
    S1VQ_PARENT_PLAN_DIGEST,
    S1VQCaseReceipt,
    S1VQIdentityObservation,
    S1VQPathPlan,
    prepare_s1vq_corrected_runner,
    s1vq_corrected_matrix_plan,
)


S1VT_SCHEMA_VERSION = "ppb1.s1vt.private.v1"
S1VT_EXPECTED_CORRECTED_PLAN_DIGEST = (
    "f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210"
)
S1VT_EXPECTED_REPEAT_COMPARISON_COUNT = 144
S1VT_EXPECTED_ARM_COUNT = 48
S1VT_SELECTIONS = S1VN_PARAMETER_IDS + ("NO_ADMISSIBLE_CONFIGURATION",)

S1VT_INVALID_MATRIX_RESULT = "S1VT_INVALID_MATRIX_RESULT"
S1VT_INVALID_ARM_COMPOSITION = "S1VT_INVALID_ARM_COMPOSITION"
S1VT_INVALID_EVALUATION_INPUT = "S1VT_INVALID_EVALUATION_INPUT"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_R0_FIXTURES = S1VN_FIXTURE_IDS
_R1_FIXTURES = ("F04", "F05", "F06")
_DIAGNOSTIC_POSITIONS = (
    ("F02", -1),
    ("F03", -2),
    ("F03", -1),
    ("F04", -1),
    ("F05", -2),
    ("F05", -1),
)


class S1VTResultPipelineError(ValueError):
    """One fail-closed S1-VT result-pipeline violation."""

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


def _require_digest(value: object, role: str, code: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise S1VTResultPipelineError(code, f"{role} must be a SHA-256 digest")
    return value


def _identity_payload(receipt: S1VQCaseReceipt) -> list[dict[str, object]]:
    return [item.canonical_payload() for item in receipt.identity_observations]


def _receipt_payload(receipt: S1VQCaseReceipt) -> dict[str, object]:
    return {
        "path": receipt.path.canonical_payload(),
        "base_receipt": receipt.base_receipt.canonical_payload(),
        "identity_observations": _identity_payload(receipt),
    }


def s1vt_receipt_digest(receipt: S1VQCaseReceipt) -> str:
    if not isinstance(receipt, S1VQCaseReceipt):
        raise S1VTResultPipelineError(
            S1VT_INVALID_MATRIX_RESULT, "receipt has the wrong type"
        )
    return _digest(_receipt_payload(receipt))


@dataclass(frozen=True, slots=True)
class S1VTRepeatComparison:
    family_id: str
    parameter_id: str
    modality_id: str
    fixture_id: str
    r0_path_id: str
    r1_path_id: str
    r0_normalized_digest: str
    r1_normalized_digest: str
    bit_equal: bool

    def __post_init__(self) -> None:
        if (
            self.family_id not in S1VN_FAMILY_IDS
            or self.parameter_id not in S1VN_PARAMETER_IDS
            or self.modality_id not in S1VN_MODALITY_IDS
            or self.fixture_id not in _R1_FIXTURES
            or not isinstance(self.r0_path_id, str)
            or not isinstance(self.r1_path_id, str)
            or not isinstance(self.bit_equal, bool)
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT, "invalid repeat comparison roles"
            )
        _require_digest(
            self.r0_normalized_digest,
            "r0_normalized_digest",
            S1VT_INVALID_MATRIX_RESULT,
        )
        _require_digest(
            self.r1_normalized_digest,
            "r1_normalized_digest",
            S1VT_INVALID_MATRIX_RESULT,
        )
        if self.bit_equal != (
            self.r0_normalized_digest == self.r1_normalized_digest
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT,
                "repeat equality does not match its two digests",
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "family_id": self.family_id,
            "parameter_id": self.parameter_id,
            "modality_id": self.modality_id,
            "fixture_id": self.fixture_id,
            "r0_path_id": self.r0_path_id,
            "r1_path_id": self.r1_path_id,
            "r0_normalized_digest": self.r0_normalized_digest,
            "r1_normalized_digest": self.r1_normalized_digest,
            "bit_equal": self.bit_equal,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _repeat_comparisons(
    receipts: tuple[S1VQCaseReceipt, ...],
) -> tuple[S1VTRepeatComparison, ...]:
    primary: dict[tuple[str, str, str, str], S1VQCaseReceipt] = {}
    comparisons: list[S1VTRepeatComparison] = []
    for receipt in receipts:
        path = receipt.path
        key = (
            path.family_id,
            path.parameter_id,
            path.modality_id,
            path.fixture_id,
        )
        if path.repeat_id == "R0":
            primary[key] = receipt
            continue
        first = primary.get(key)
        if first is None:
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT, "R1 has no preceding R0 receipt"
            )
        left = first.repeat_comparison_digest()
        right = receipt.repeat_comparison_digest()
        comparisons.append(
            S1VTRepeatComparison(
                path.family_id,
                path.parameter_id,
                path.modality_id,
                path.fixture_id,
                first.path.path_id,
                path.path_id,
                left,
                right,
                left == right,
            )
        )
    return tuple(comparisons)


def _validate_receipt(path: S1VQPathPlan, receipt: S1VQCaseReceipt) -> None:
    base = receipt.base_receipt
    if (
        not isinstance(base, S1VNCaseReceipt)
        or receipt.path != path
        or (
            base.path_id,
            base.family_id,
            base.accepted_call_count,
        )
        != (path.path_id, path.family_id, path.expected_call_count)
    ):
        raise S1VTResultPipelineError(
            S1VT_INVALID_MATRIX_RESULT, "receipt does not match its planned path"
        )
    if not (
        len(base.events)
        == len(base.observations)
        == len(receipt.identity_observations)
        == path.expected_call_count
    ):
        raise S1VTResultPipelineError(
            S1VT_INVALID_MATRIX_RESULT, "receipt step inventories are incomplete"
        )
    for index, (event, observation, identity) in enumerate(
        zip(
            base.events,
            base.observations,
            receipt.identity_observations,
            strict=True,
        ),
        start=1,
    ):
        if (
            not isinstance(event, str)
            or not isinstance(observation, S1VNStepObservation)
            or not isinstance(identity, S1VQIdentityObservation)
            or observation.step != index
            or identity.step != index
            or observation.event != event
            or any(
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
                for value in (
                    identity.active_identity_count,
                    observation.logical_value_count,
                    observation.occupied_slot_count,
                    observation.stabilized_slot_count,
                )
            )
            or any(
                value is not None and not isinstance(value, str)
                for value in (
                    identity.selected_entry_id,
                    identity.written_entry_id,
                )
            )
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT,
                "receipt observations are not atomically step-aligned",
            )
        for value in (
            observation.distance,
            observation.selected_state_displacement,
        ):
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise S1VTResultPipelineError(
                    S1VT_INVALID_MATRIX_RESULT,
                    "receipt contains a non-finite observation",
                )
        _require_digest(
            identity.active_identity_digest,
            "active_identity_digest",
            S1VT_INVALID_MATRIX_RESULT,
        )
        if event == "MATCHED" and identity.selected_entry_id is None:
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT,
                "matched observation requires a selected identity",
            )
        if (
            path.family_id != "PPB1"
            and identity.selected_entry_id is not None
            and identity.selected_prestate_digest is None
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT,
                "selected identity requires its prestate digest",
            )
        if identity.selected_prestate_digest is not None:
            _require_digest(
                identity.selected_prestate_digest,
                "selected_prestate_digest",
                S1VT_INVALID_MATRIX_RESULT,
            )
    _require_digest(
        base.input_history_digest,
        "input_history_digest",
        S1VT_INVALID_MATRIX_RESULT,
    )
    _require_digest(
        base.final_state_digest,
        "final_state_digest",
        S1VT_INVALID_MATRIX_RESULT,
    )


@dataclass(frozen=True, slots=True)
class S1VTSealedMatrixResult:
    parent_plan_digest: str
    corrected_plan_digest: str
    receipts: tuple[S1VQCaseReceipt, ...]
    repeat_comparisons: tuple[S1VTRepeatComparison, ...]
    ppb_call_count: int
    baseline_call_count: int
    total_call_count: int
    receipt_list_digest: str
    comparison_list_digest: str

    def __post_init__(self) -> None:
        preparation = prepare_s1vq_corrected_runner()
        plan = s1vq_corrected_matrix_plan()
        receipts = tuple(self.receipts)
        comparisons = tuple(self.repeat_comparisons)
        if (
            self.parent_plan_digest != S1VQ_PARENT_PLAN_DIGEST
            or preparation.parent_plan_digest != self.parent_plan_digest
            or self.corrected_plan_digest != S1VT_EXPECTED_CORRECTED_PLAN_DIGEST
            or preparation.corrected_plan_digest != self.corrected_plan_digest
            or len(receipts) != S1VQ_EXPECTED_CASE_COUNT
            or len(receipts) != len(plan)
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT, "matrix plan identity drifted"
            )
        for path, receipt in zip(plan, receipts, strict=True):
            _validate_receipt(path, receipt)

        expected_comparisons = _repeat_comparisons(receipts)
        if (
            len(comparisons) != S1VT_EXPECTED_REPEAT_COMPARISON_COUNT
            or comparisons != expected_comparisons
            or not all(item.bit_equal for item in comparisons)
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT,
                "repeat comparison inventory is incomplete or unequal",
            )

        ppb_calls = sum(
            item.base_receipt.accepted_call_count
            for item in receipts
            if item.path.family_id == "PPB1"
        )
        baseline_calls = sum(
            item.base_receipt.accepted_call_count
            for item in receipts
            if item.path.family_id != "PPB1"
        )
        if (
            self.ppb_call_count != ppb_calls
            or self.ppb_call_count != S1VQ_EXPECTED_PPB_CALLS
            or self.baseline_call_count != baseline_calls
            or self.baseline_call_count != S1VQ_EXPECTED_BASELINE_CALLS
            or self.total_call_count != ppb_calls + baseline_calls
            or self.total_call_count != S1VQ_EXPECTED_TOTAL_CALLS
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT, "matrix call ledger drifted"
            )

        history_groups: dict[tuple[str, str, str], set[str]] = {}
        for receipt in receipts:
            key = (
                receipt.path.parameter_id,
                receipt.path.modality_id,
                receipt.path.fixture_id,
            )
            history_groups.setdefault(key, set()).add(
                receipt.base_receipt.input_history_digest
            )
        if len(history_groups) != 48 or any(
            len(values) != 1 for values in history_groups.values()
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT,
                "families or repeats do not share the bound input history",
            )

        expected_receipt_digest = _digest(
            [_receipt_payload(item) for item in receipts]
        )
        expected_comparison_digest = _digest(
            [item.canonical_payload() for item in comparisons]
        )
        if (
            self.receipt_list_digest != expected_receipt_digest
            or self.comparison_list_digest != expected_comparison_digest
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_MATRIX_RESULT, "matrix result seal is not canonical"
            )
        object.__setattr__(self, "receipts", receipts)
        object.__setattr__(self, "repeat_comparisons", comparisons)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VT_SCHEMA_VERSION,
            "parent_plan_digest": self.parent_plan_digest,
            "corrected_plan_digest": self.corrected_plan_digest,
            "receipts": [_receipt_payload(item) for item in self.receipts],
            "repeat_comparisons": [
                item.canonical_payload() for item in self.repeat_comparisons
            ],
            "ppb_call_count": self.ppb_call_count,
            "baseline_call_count": self.baseline_call_count,
            "total_call_count": self.total_call_count,
            "receipt_list_digest": self.receipt_list_digest,
            "comparison_list_digest": self.comparison_list_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def seal_s1vt_matrix_result(
    receipts: tuple[S1VQCaseReceipt, ...],
) -> S1VTSealedMatrixResult:
    """Seal one complete constructed result; this function runs no path."""

    values = tuple(receipts)
    comparisons = _repeat_comparisons(values)
    ppb_calls = sum(
        item.base_receipt.accepted_call_count
        for item in values
        if item.path.family_id == "PPB1"
    )
    baseline_calls = sum(
        item.base_receipt.accepted_call_count
        for item in values
        if item.path.family_id != "PPB1"
    )
    return S1VTSealedMatrixResult(
        S1VQ_PARENT_PLAN_DIGEST,
        S1VT_EXPECTED_CORRECTED_PLAN_DIGEST,
        values,
        comparisons,
        ppb_calls,
        baseline_calls,
        ppb_calls + baseline_calls,
        _digest([_receipt_payload(item) for item in values]),
        _digest([item.canonical_payload() for item in comparisons]),
    )


def _assignment_identity(receipt: S1VQCaseReceipt, index: int) -> str | None:
    event = receipt.base_receipt.events[index]
    identity = receipt.identity_observations[index]
    if event == "MATCHED":
        return identity.selected_entry_id
    return identity.written_entry_id


@dataclass(frozen=True, slots=True)
class S1VTArmEvidence:
    family_id: str
    parameter_id: str
    modality_id: str
    source_receipt_digests: tuple[str, ...]
    diagnostic_events: tuple[str, ...]
    diagnostic_assignment_ids: tuple[str | None, ...]
    diagnostic_distances: tuple[float | None, ...]
    f05_displacements: tuple[float | None, ...]
    fixture_peaks: tuple[tuple[str, int, int, int, int], ...]
    repeat_comparison_digests: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.family_id not in S1VN_FAMILY_IDS
            or self.parameter_id not in S1VN_PARAMETER_IDS
            or self.modality_id not in S1VN_MODALITY_IDS
            or len(self.source_receipt_digests) != 11
            or len(self.diagnostic_events) != 6
            or len(self.diagnostic_assignment_ids) != 6
            or len(self.diagnostic_distances) != 6
            or len(self.f05_displacements) != 11
            or len(self.fixture_peaks) != 8
            or tuple(item[0] for item in self.fixture_peaks) != _R0_FIXTURES
            or len(self.repeat_comparison_digests) != 3
            or any(not isinstance(item, str) for item in self.diagnostic_events)
            or any(
                item is not None and not isinstance(item, str)
                for item in self.diagnostic_assignment_ids
            )
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_ARM_COMPOSITION, "invalid evidence inventory"
            )
        for value in (
            *self.diagnostic_distances,
            *self.f05_displacements,
        ):
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise S1VTResultPipelineError(
                    S1VT_INVALID_ARM_COMPOSITION,
                    "evidence contains a non-finite measurement",
                )
        if any(
            len(item) != 5
            or any(
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
                for value in item[1:]
            )
            for item in self.fixture_peaks
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_ARM_COMPOSITION, "invalid fixture peak ledger"
            )
        for value in (
            *self.source_receipt_digests,
            *self.repeat_comparison_digests,
        ):
            _require_digest(
                value, "evidence digest role", S1VT_INVALID_ARM_COMPOSITION
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "family_id": self.family_id,
            "parameter_id": self.parameter_id,
            "modality_id": self.modality_id,
            "source_receipt_digests": list(self.source_receipt_digests),
            "diagnostic_events": list(self.diagnostic_events),
            "diagnostic_assignment_ids": list(self.diagnostic_assignment_ids),
            "diagnostic_distances": list(self.diagnostic_distances),
            "f05_displacements": list(self.f05_displacements),
            "fixture_peaks": [
                {
                    "fixture_id": item[0],
                    "logical_values": item[1],
                    "identity_records": item[2],
                    "occupied_slots": item[3],
                    "stabilized_slots": item[4],
                }
                for item in self.fixture_peaks
            ],
            "repeat_comparison_digests": list(
                self.repeat_comparison_digests
            ),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class S1VTArmRecord:
    family_id: str
    parameter_id: str
    modality_id: str
    corrected_plan_digest: str
    source_receipt_digests: tuple[str, ...]
    lifecycle_mask: tuple[bool, ...]
    diagnostic_match_mask: tuple[bool, ...]
    near_assignment_consistent: bool
    separated_assignment_distinct: bool
    repeatability_mask: tuple[bool, ...]
    peak_logical_value_count: int
    peak_identity_metadata_value_count: int
    r0_accepted_call_count: int
    r1_accepted_call_count: int
    total_accepted_call_count: int
    evidence_digest: str

    def __post_init__(self) -> None:
        if (
            self.family_id not in S1VN_FAMILY_IDS
            or self.parameter_id not in S1VN_PARAMETER_IDS
            or self.modality_id not in S1VN_MODALITY_IDS
            or self.corrected_plan_digest != S1VT_EXPECTED_CORRECTED_PLAN_DIGEST
            or len(self.source_receipt_digests) != 11
            or len(self.lifecycle_mask) != 4
            or len(self.diagnostic_match_mask) != 6
            or len(self.repeatability_mask) != 3
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_ARM_COMPOSITION, "invalid arm record inventory"
            )
        for value in (
            *self.lifecycle_mask,
            *self.diagnostic_match_mask,
            self.near_assignment_consistent,
            self.separated_assignment_distinct,
            *self.repeatability_mask,
        ):
            if not isinstance(value, bool):
                raise S1VTResultPipelineError(
                    S1VT_INVALID_ARM_COMPOSITION,
                    "arm truth roles must be boolean",
                )
        for role, value in (
            ("peak_logical_value_count", self.peak_logical_value_count),
            (
                "peak_identity_metadata_value_count",
                self.peak_identity_metadata_value_count,
            ),
            ("r0_accepted_call_count", self.r0_accepted_call_count),
            ("r1_accepted_call_count", self.r1_accepted_call_count),
            ("total_accepted_call_count", self.total_accepted_call_count),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise S1VTResultPipelineError(
                    S1VT_INVALID_ARM_COMPOSITION, f"invalid {role}"
                )
        if (
            self.r0_accepted_call_count <= 0
            or self.r1_accepted_call_count <= 0
            or self.total_accepted_call_count
            != self.r0_accepted_call_count + self.r1_accepted_call_count
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_ARM_COMPOSITION, "arm call ledger is inconsistent"
            )
        for role, value in (
            ("source_receipt_digest", item)
            for item in self.source_receipt_digests
        ):
            _require_digest(value, role, S1VT_INVALID_ARM_COMPOSITION)
        _require_digest(
            self.evidence_digest, "evidence_digest", S1VT_INVALID_ARM_COMPOSITION
        )

    @property
    def lifecycle_valid(self) -> bool:
        return all(self.lifecycle_mask)

    @property
    def diagnostic_match_count(self) -> int:
        return sum(self.diagnostic_match_mask)

    @property
    def repeatability_confirmed(self) -> bool:
        return all(self.repeatability_mask)

    @property
    def admissible(self) -> bool:
        return all(
            (
                self.lifecycle_valid,
                0 < self.diagnostic_match_count < 6,
                self.near_assignment_consistent,
                self.separated_assignment_distinct,
                self.repeatability_confirmed,
            )
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VT_SCHEMA_VERSION,
            "family_id": self.family_id,
            "parameter_id": self.parameter_id,
            "modality_id": self.modality_id,
            "corrected_plan_digest": self.corrected_plan_digest,
            "source_receipt_digests": list(self.source_receipt_digests),
            "lifecycle_mask": list(self.lifecycle_mask),
            "lifecycle_valid": self.lifecycle_valid,
            "diagnostic_match_mask": list(self.diagnostic_match_mask),
            "diagnostic_match_count": self.diagnostic_match_count,
            "near_assignment_consistent": self.near_assignment_consistent,
            "separated_assignment_distinct": self.separated_assignment_distinct,
            "repeatability_mask": list(self.repeatability_mask),
            "repeatability_confirmed": self.repeatability_confirmed,
            "peak_logical_value_count": self.peak_logical_value_count,
            "peak_identity_metadata_value_count": (
                self.peak_identity_metadata_value_count
            ),
            "r0_accepted_call_count": self.r0_accepted_call_count,
            "r1_accepted_call_count": self.r1_accepted_call_count,
            "total_accepted_call_count": self.total_accepted_call_count,
            "evidence_digest": self.evidence_digest,
            "admissible": self.admissible,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class S1VTCompositionResult:
    matrix_result_digest: str
    arms: tuple[S1VTArmRecord, ...]
    evidence: tuple[S1VTArmEvidence, ...]

    def __post_init__(self) -> None:
        _require_digest(
            self.matrix_result_digest,
            "matrix_result_digest",
            S1VT_INVALID_ARM_COMPOSITION,
        )
        expected_keys = tuple(
            (family, parameter, modality)
            for family in S1VN_FAMILY_IDS
            for parameter in S1VN_PARAMETER_IDS
            for modality in S1VN_MODALITY_IDS
        )
        arm_keys = tuple(
            (item.family_id, item.parameter_id, item.modality_id)
            for item in self.arms
        )
        evidence_keys = tuple(
            (item.family_id, item.parameter_id, item.modality_id)
            for item in self.evidence
        )
        corrected_plan = s1vq_corrected_matrix_plan()
        expected_call_ledgers = {
            (parameter, modality): (
                sum(
                    path.expected_call_count
                    for path in corrected_plan
                    if path.family_id == "PPB1"
                    and path.parameter_id == parameter
                    and path.modality_id == modality
                    and path.repeat_id == "R0"
                ),
                sum(
                    path.expected_call_count
                    for path in corrected_plan
                    if path.family_id == "PPB1"
                    and path.parameter_id == parameter
                    and path.modality_id == modality
                    and path.repeat_id == "R1"
                ),
            )
            for parameter in S1VN_PARAMETER_IDS
            for modality in S1VN_MODALITY_IDS
        }
        if (
            len(self.arms) != S1VT_EXPECTED_ARM_COUNT
            or arm_keys != expected_keys
            or evidence_keys != expected_keys
            or any(
                arm.evidence_digest != evidence.digest()
                for arm, evidence in zip(self.arms, self.evidence, strict=True)
            )
            or any(
                (
                    arm.r0_accepted_call_count,
                    arm.r1_accepted_call_count,
                )
                != expected_call_ledgers[(arm.parameter_id, arm.modality_id)]
                for arm in self.arms
            )
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_ARM_COMPOSITION,
                "composition is not the exact ordered 48-arm cross product",
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VT_SCHEMA_VERSION,
            "matrix_result_digest": self.matrix_result_digest,
            "arms": [item.canonical_payload() for item in self.arms],
            "evidence": [item.canonical_payload() for item in self.evidence],
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _fixture_receipt(
    inventory: dict[tuple[str, str, str, str, str], S1VQCaseReceipt],
    family: str,
    parameter: str,
    modality: str,
    fixture: str,
    repeat: str,
) -> S1VQCaseReceipt:
    try:
        return inventory[(family, parameter, modality, fixture, repeat)]
    except KeyError as exc:
        raise S1VTResultPipelineError(
            S1VT_INVALID_ARM_COMPOSITION, "arm source receipt is missing"
        ) from exc


def _max_or_zero(values: tuple[int, ...]) -> int:
    return max(values, default=0)


def compose_s1vt_arm_records(
    matrix: S1VTSealedMatrixResult,
) -> S1VTCompositionResult:
    """Purely compose the sealed result into the exact 48 technical arms."""

    if not isinstance(matrix, S1VTSealedMatrixResult):
        raise S1VTResultPipelineError(
            S1VT_INVALID_ARM_COMPOSITION, "sealed matrix result is required"
        )
    inventory = {
        (
            item.path.family_id,
            item.path.parameter_id,
            item.path.modality_id,
            item.path.fixture_id,
            item.path.repeat_id,
        ): item
        for item in matrix.receipts
    }
    comparison_inventory = {
        (
            item.family_id,
            item.parameter_id,
            item.modality_id,
            item.fixture_id,
        ): item
        for item in matrix.repeat_comparisons
    }
    arms: list[S1VTArmRecord] = []
    evidence_rows: list[S1VTArmEvidence] = []
    for family in S1VN_FAMILY_IDS:
        for parameter in S1VN_PARAMETER_IDS:
            for modality in S1VN_MODALITY_IDS:
                r0 = {
                    fixture: _fixture_receipt(
                        inventory, family, parameter, modality, fixture, "R0"
                    )
                    for fixture in _R0_FIXTURES
                }
                r1 = {
                    fixture: _fixture_receipt(
                        inventory, family, parameter, modality, fixture, "R1"
                    )
                    for fixture in _R1_FIXTURES
                }
                sources = tuple(r0[item] for item in _R0_FIXTURES) + tuple(
                    r1[item] for item in _R1_FIXTURES
                )
                source_digests = tuple(s1vt_receipt_digest(item) for item in sources)

                diagnostic_rows = tuple(
                    (r0[fixture], index) for fixture, index in _DIAGNOSTIC_POSITIONS
                )
                diagnostic_events = tuple(
                    receipt.base_receipt.events[index]
                    for receipt, index in diagnostic_rows
                )
                diagnostic_ids = tuple(
                    _assignment_identity(receipt, index)
                    for receipt, index in diagnostic_rows
                )
                diagnostic_distances = tuple(
                    receipt.base_receipt.observations[index].distance
                    for receipt, index in diagnostic_rows
                )
                diagnostic_mask = tuple(
                    event == "MATCHED"
                    and receipt.identity_observations[index].selected_entry_id
                    is not None
                    for (receipt, index), event in zip(
                        diagnostic_rows, diagnostic_events, strict=True
                    )
                )

                f01_first = _assignment_identity(r0["F01"], 0)
                f01_last_identity = r0["F01"].identity_observations[-1]
                f01_repeat = (
                    f01_first is not None
                    and r0["F01"].base_receipt.events[-1] == "MATCHED"
                    and f01_last_identity.selected_entry_id == f01_first
                )
                config = s1vn_config(parameter, modality)
                f06 = r0["F06"]
                f06_bounded = all(
                    observation.occupied_slot_count <= config.capacity
                    and identity.active_identity_count <= config.capacity
                    for observation, identity in zip(
                        f06.base_receipt.observations,
                        f06.identity_observations,
                        strict=True,
                    )
                ) and (
                    f06.base_receipt.accepted_call_count
                    == f06.path.expected_call_count
                )
                f07_release = (
                    r0["F07"].identity_observations[-1].selected_entry_id is None
                )
                f08_first = _assignment_identity(r0["F08"], 0)
                f08_retention = (
                    f08_first is not None
                    and r0["F08"].base_receipt.events[-1] == "MATCHED"
                    and r0["F08"].identity_observations[-1].selected_entry_id
                    == f08_first
                )
                lifecycle_mask = (
                    f01_repeat,
                    f06_bounded,
                    f07_release,
                    f08_retention,
                )

                f02_assignments = tuple(
                    _assignment_identity(r0["F02"], index)
                    for index in range(len(r0["F02"].base_receipt.events))
                )
                near_consistent = (
                    all(item is not None for item in f02_assignments)
                    and len(set(f02_assignments)) == 1
                )
                f03 = r0["F03"]
                low_first = _assignment_identity(f03, 0)
                high_first = _assignment_identity(f03, 1)
                low_last = _assignment_identity(f03, -2)
                high_last = _assignment_identity(f03, -1)
                separated = (
                    low_first is not None
                    and high_first is not None
                    and low_first != high_first
                    and low_last == low_first
                    and high_last == high_first
                )

                comparisons = tuple(
                    comparison_inventory[(family, parameter, modality, fixture)]
                    for fixture in _R1_FIXTURES
                )
                repeat_mask = tuple(item.bit_equal for item in comparisons)
                peak_logical = _max_or_zero(
                    tuple(
                        observation.logical_value_count
                        for receipt in sources
                        for observation in receipt.base_receipt.observations
                    )
                )
                peak_identities = _max_or_zero(
                    tuple(
                        identity.active_identity_count
                        for receipt in sources
                        for identity in receipt.identity_observations
                    )
                )
                r0_calls = sum(
                    item.base_receipt.accepted_call_count for item in r0.values()
                )
                r1_calls = sum(
                    item.base_receipt.accepted_call_count for item in r1.values()
                )
                fixture_peaks = tuple(
                    (
                        fixture,
                        _max_or_zero(
                            tuple(
                                item.logical_value_count
                                for item in r0[fixture].base_receipt.observations
                            )
                        ),
                        _max_or_zero(
                            tuple(
                                item.active_identity_count
                                for item in r0[fixture].identity_observations
                            )
                        ),
                        _max_or_zero(
                            tuple(
                                item.occupied_slot_count
                                for item in r0[fixture].base_receipt.observations
                            )
                        ),
                        _max_or_zero(
                            tuple(
                                item.stabilized_slot_count
                                for item in r0[fixture].base_receipt.observations
                            )
                        ),
                    )
                    for fixture in _R0_FIXTURES
                )
                evidence = S1VTArmEvidence(
                    family,
                    parameter,
                    modality,
                    source_digests,
                    diagnostic_events,
                    diagnostic_ids,
                    diagnostic_distances,
                    tuple(
                        item.selected_state_displacement
                        for item in r0["F05"].base_receipt.observations
                    ),
                    fixture_peaks,
                    tuple(item.digest() for item in comparisons),
                )
                evidence_rows.append(evidence)
                arms.append(
                    S1VTArmRecord(
                        family,
                        parameter,
                        modality,
                        matrix.corrected_plan_digest,
                        source_digests,
                        lifecycle_mask,
                        diagnostic_mask,
                        near_consistent,
                        separated,
                        repeat_mask,
                        peak_logical,
                        peak_identities,
                        r0_calls,
                        r1_calls,
                        r0_calls + r1_calls,
                        evidence.digest(),
                    )
                )
    return S1VTCompositionResult(
        matrix.digest(), tuple(arms), tuple(evidence_rows)
    )


@dataclass(frozen=True, slots=True)
class S1VTModalityDecision:
    modality_id: str
    selection: str
    admissible_parameter_ids: tuple[str, ...]
    reduced_parameter_ids: tuple[str, ...]
    explaining_baseline_ids: tuple[str, ...]
    reason: str

    def __post_init__(self) -> None:
        if (
            self.modality_id not in S1VN_MODALITY_IDS
            or self.selection not in S1VT_SELECTIONS
            or len(set(self.admissible_parameter_ids))
            != len(self.admissible_parameter_ids)
            or len(set(self.reduced_parameter_ids))
            != len(self.reduced_parameter_ids)
            or any(
                item not in S1VN_PARAMETER_IDS
                for item in (
                    *self.admissible_parameter_ids,
                    *self.reduced_parameter_ids,
                )
            )
            or any(
                item not in S1VN_BASELINE_IDS
                for item in self.explaining_baseline_ids
            )
            or not isinstance(self.reason, str)
            or not self.reason
        ):
            raise S1VTResultPipelineError(
                S1VT_INVALID_EVALUATION_INPUT, "invalid modality decision"
            )

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
class S1VTEvaluationResult:
    decisions: tuple[S1VTModalityDecision, ...]
    composition_digest: str

    def __post_init__(self) -> None:
        if tuple(item.modality_id for item in self.decisions) != S1VN_MODALITY_IDS:
            raise S1VTResultPipelineError(
                S1VT_INVALID_EVALUATION_INPUT,
                "evaluation must contain both modalities in bound order",
            )
        _require_digest(
            self.composition_digest,
            "composition_digest",
            S1VT_INVALID_EVALUATION_INPUT,
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VT_SCHEMA_VERSION,
            "decisions": [item.canonical_payload() for item in self.decisions],
            "composition_digest": self.composition_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _baseline_equivalent(ppb: S1VTArmRecord, baseline: S1VTArmRecord) -> bool:
    return (
        baseline.family_id != "B07"
        and baseline.admissible
        and baseline.diagnostic_match_mask == ppb.diagnostic_match_mask
        and baseline.lifecycle_mask == ppb.lifecycle_mask
        and baseline.near_assignment_consistent == ppb.near_assignment_consistent
        and baseline.separated_assignment_distinct
        == ppb.separated_assignment_distinct
        and baseline.repeatability_mask == ppb.repeatability_mask
        and baseline.peak_logical_value_count <= ppb.peak_logical_value_count
        and baseline.peak_identity_metadata_value_count
        <= ppb.peak_identity_metadata_value_count
        and baseline.total_accepted_call_count <= ppb.total_accepted_call_count
    )


def evaluate_s1vt_composition(
    composition: S1VTCompositionResult,
) -> S1VTEvaluationResult:
    """Apply the corrected pure stop, equivalence, and simplicity order."""

    if not isinstance(composition, S1VTCompositionResult):
        raise S1VTResultPipelineError(
            S1VT_INVALID_EVALUATION_INPUT, "composition result is required"
        )
    by_key = {
        (item.family_id, item.parameter_id, item.modality_id): item
        for item in composition.arms
    }
    if len(by_key) != S1VT_EXPECTED_ARM_COUNT:
        raise S1VTResultPipelineError(
            S1VT_INVALID_EVALUATION_INPUT, "arm cross product is incomplete"
        )

    decisions: list[S1VTModalityDecision] = []
    for modality in S1VN_MODALITY_IDS:
        admissible: list[S1VTArmRecord] = []
        reduced: list[str] = []
        explainers: set[str] = set()
        for parameter in S1VN_PARAMETER_IDS:
            ppb = by_key[("PPB1", parameter, modality)]
            if not ppb.admissible:
                continue
            matching = tuple(
                baseline
                for baseline in S1VN_BASELINE_IDS
                if _baseline_equivalent(
                    ppb, by_key[(baseline, parameter, modality)]
                )
            )
            if matching:
                reduced.append(parameter)
                explainers.update(matching)
            else:
                admissible.append(ppb)
        admissible.sort(
            key=lambda item: (
                item.peak_logical_value_count,
                item.peak_identity_metadata_value_count,
                item.total_accepted_call_count,
                S1VN_PARAMETER_IDS.index(item.parameter_id),
            )
        )
        if admissible:
            selection = admissible[0].parameter_id
            reason = "LEAST_TOTAL_STATE_ADMISSIBLE_NONREDUCED_RECORD"
        elif reduced:
            selection = "NO_ADMISSIBLE_CONFIGURATION"
            reason = "ALL_ADMISSIBLE_RECORDS_REDUCED_BY_EQUIVALENT_BASELINE"
        else:
            selection = "NO_ADMISSIBLE_CONFIGURATION"
            reason = "NO_RECORD_PASSES_BOUND_STOP_RULES"
        decisions.append(
            S1VTModalityDecision(
                modality,
                selection,
                tuple(item.parameter_id for item in admissible),
                tuple(reduced),
                tuple(sorted(explainers)),
                reason,
            )
        )
    return S1VTEvaluationResult(tuple(decisions), composition.digest())
