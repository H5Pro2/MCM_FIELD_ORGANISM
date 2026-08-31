"""Private S2-IG fixtures and the closed 183-operation registry.

Execution fixtures contain sources, ordering, and budgets only. Expected
statuses remain in the independent evaluator/verifier root.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


S2IG_SCHEMA = "s2ig.private.execution-fixtures.v1"
SUCCESS_OPERATION_COUNT = 183
SUCCESS_EVENT_COUNT = 366
MAX_FAILURE_OPERATION_COUNT = 185
MAX_FAILURE_EVENT_COUNT = 370
MAX_EVENT_BYTES = 1_536
MAX_INDIVIDUAL_ARTIFACT_BYTES = 4_095
MAX_SOURCE_DIGESTS = 24
FORMATION_COUNT = 38
HISTORY_COUNT = 6
FUNCTION_CASE_COUNT = 8
PARENT_SET_SCHEMA = "s2ij.parent-set.v1"
MAX_PARENT_SET_PREIMAGE_BYTES = 2_816
COMPACT_PARENT_OPERATION_COUNT = 76
COMPACT_PARENT_REFERENCE_COUNT = 188
TOTAL_INTERNAL_PARENT_REFERENCE_COUNT = 294

VISIBLE_POSITIONS = (0, 2, 4, 6, 8, 10, 12, 14, 16)
MASKED_POSITIONS = (1, 3, 5, 7, 9, 11, 13, 15, 17)

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9._-]{1,95}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_OPERATION_ID = re.compile(r"^ie-op-[0-9]{3}$")


class S2IGRegistryError(ValueError):
    """One closed fixture or operation-registry violation."""


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("ascii")


def canonical_digest(payload: object) -> str:
    return hashlib.sha256(canonical_bytes(payload).rstrip(b"\n")).hexdigest()


def file_digest(path: Path) -> str:
    if not isinstance(path, Path) or not path.is_absolute() or not path.is_file():
        raise S2IGRegistryError("one absolute existing file path is required")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2IGRegistryError(message)


@dataclass(frozen=True, slots=True)
class SourceRef:
    visual_id: str
    auditory_id: str

    def __post_init__(self) -> None:
        _require(
            all(
                isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None
                for value in (self.visual_id, self.auditory_id)
            ),
            "source reference differs",
        )


@dataclass(frozen=True, slots=True)
class HistoryStep:
    ordinal: int
    source: SourceRef
    window_start: int
    window_end: int

    def __post_init__(self) -> None:
        _require(type(self.ordinal) is int and self.ordinal >= 1, "step ordinal differs")
        self.source.__post_init__()
        _require(
            type(self.window_start) is int
            and type(self.window_end) is int
            and self.window_start == self.ordinal - 1
            and self.window_end == self.ordinal,
            "step window differs",
        )


@dataclass(frozen=True, slots=True)
class HistoryFixture:
    history_id: str
    steps: tuple[HistoryStep, ...]
    retrieval_source: SourceRef
    probe_window_start: int
    probe_window_end: int
    history_digest: str

    def __post_init__(self) -> None:
        _require(self.history_id in {"h-c", "h-x0", "h-x1", "h-sa", "h-sb", "h-n"}, "history id differs")
        _require(type(self.steps) is tuple and self.steps, "history steps differ")
        _require(
            tuple(item.ordinal for item in self.steps) == tuple(range(1, len(self.steps) + 1)),
            "history ordinals differ",
        )
        for step in self.steps:
            step.__post_init__()
        self.retrieval_source.__post_init__()
        _require(
            self.probe_window_start == len(self.steps)
            and self.probe_window_end == self.probe_window_start + 1,
            "retrieval window differs",
        )
        _require(self.history_digest == canonical_digest(self.payload_without_digest()), "history digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": S2IG_SCHEMA,
            "history_id": self.history_id,
            "steps": [
                [item.ordinal, item.source.visual_id, item.source.auditory_id, item.window_start, item.window_end]
                for item in self.steps
            ],
            "retrieval_source": [self.retrieval_source.visual_id, self.retrieval_source.auditory_id],
            "probe_window": [self.probe_window_start, self.probe_window_end],
        }

    @classmethod
    def build(
        cls,
        history_id: str,
        formation_sources: tuple[tuple[str, str], ...],
        retrieval_source: tuple[str, str],
    ) -> "HistoryFixture":
        steps = tuple(
            HistoryStep(index, SourceRef(*source), index - 1, index)
            for index, source in enumerate(formation_sources, 1)
        )
        retrieval = SourceRef(*retrieval_source)
        payload = {
            "schema": S2IG_SCHEMA,
            "history_id": history_id,
            "steps": [
                [item.ordinal, item.source.visual_id, item.source.auditory_id, item.window_start, item.window_end]
                for item in steps
            ],
            "retrieval_source": [retrieval.visual_id, retrieval.auditory_id],
            "probe_window": [len(steps), len(steps) + 1],
        }
        return cls(history_id, steps, retrieval, len(steps), len(steps) + 1, canonical_digest(payload))


HISTORIES = (
    HistoryFixture.build("h-c", (("p1", "p1"),) * 4, ("p1", "p1")),
    HistoryFixture.build("h-x0", (("v1", "m1"),) * 4 + (("v0", "m0"),), ("q0", "mq")),
    HistoryFixture.build("h-x1", (("v0", "m0"),) * 4 + (("v1", "m1"),), ("q1", "mq")),
    HistoryFixture.build("h-sa", (("p11", "p11"),), ("p11", "p11")),
    HistoryFixture.build(
        "h-sb",
        (("p1", "p1"),) * 4 + tuple((f"p{index}", f"p{index}") for index in range(2, 11)),
        ("p1", "p1"),
    ),
    HistoryFixture.build(
        "h-n",
        (("p11", "p11"),) + tuple((f"p{index}", f"p{index}") for index in range(2, 11)),
        ("p11", "p11"),
    ),
)
HISTORY_BY_ID = {item.history_id: item for item in HISTORIES}


@dataclass(frozen=True, slots=True)
class FunctionCaseFixture:
    case_id: str
    history_id: str
    signal_visual_id: str
    case_plan_id: str
    case_digest: str

    def __post_init__(self) -> None:
        _require(self.case_id in {f"c{index:02d}" for index in range(1, 9)}, "case id differs")
        _require(self.history_id in HISTORY_BY_ID, "case history differs")
        _require(
            isinstance(self.signal_visual_id, str)
            and _IDENTIFIER.fullmatch(self.signal_visual_id) is not None
            and isinstance(self.case_plan_id, str)
            and _IDENTIFIER.fullmatch(self.case_plan_id) is not None,
            "case source differs",
        )
        _require(self.case_digest == canonical_digest(self.payload_without_digest()), "case digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": S2IG_SCHEMA,
            "case_id": self.case_id,
            "history_id": self.history_id,
            "signal_visual_id": self.signal_visual_id,
            "case_plan_id": self.case_plan_id,
            "context_role": "CONTEXT_RETRIEVAL_PROBE",
            "signal_role": "MASKED_SIGNAL_PROBE",
        }

    @classmethod
    def build(cls, case_id: str, history_id: str, signal_visual_id: str) -> "FunctionCaseFixture":
        plan_id = f"s2ig.case-plan.{case_id}"
        payload = {
            "schema": S2IG_SCHEMA,
            "case_id": case_id,
            "history_id": history_id,
            "signal_visual_id": signal_visual_id,
            "case_plan_id": plan_id,
            "context_role": "CONTEXT_RETRIEVAL_PROBE",
            "signal_role": "MASKED_SIGNAL_PROBE",
        }
        return cls(case_id, history_id, signal_visual_id, plan_id, canonical_digest(payload))


FUNCTION_CASES = (
    FunctionCaseFixture.build("c01", "h-c", "p1"),
    FunctionCaseFixture.build("c02", "h-x0", "q0"),
    FunctionCaseFixture.build("c03", "h-x1", "q1"),
    FunctionCaseFixture.build("c04", "h-sa", "p11"),
    FunctionCaseFixture.build("c05", "h-sb", "p1"),
    FunctionCaseFixture.build("c06", "h-n", "p11"),
    FunctionCaseFixture.build("c07", "h-x0", "z0"),
    FunctionCaseFixture.build("c08", "h-x1", "z1"),
)
CASE_BY_ID = {item.case_id: item for item in FUNCTION_CASES}


Z_VISUAL_BLOCKS = {
    "z0": (254, 127, 0, 128, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0),
    "z1": (255, 128, 1, 127, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0),
}

FUNCTIONAL_BUDGET = {
    "visual_receptor_analyses": 52,
    "composite_formations": 38,
    "composite_read_only_probes": 6,
    "s2gc_projections": 6,
    "s2gi_projections": 6,
    "masked_probe_projections": 8,
    "signal_calls": 8,
    "baseline_calls": 8,
    "formation_write_words": 23_446,
    "formation_distance_terms": 17_784,
    "formation_control_terms": 2_052,
    "probe_write_words": 84,
    "probe_distance_terms": 2_808,
    "probe_control_terms": 288,
}

RECEIPT_LIMITS = {
    "S2IGRunPreparationReceipt": 1_536,
    "S2IGSourceManifestReceipt": 3_584,
    "S2IGHistoryInitialReceipt": 1_280,
    "S2IGReceptorReceipt": 2_765,
    "S2IGFormationReceipt": 2_801,
    "S2IGReadOnlyReceipt": 2_048,
    "S2IGS2GCProjectionReceipt": 3_174,
    "S2IGS2GIProjectionReceipt": 2_978,
    "S2IGHistoryEvidenceReceipt": 2_048,
    "S2IGMaskedSignalProbeReceipt": 1_792,
    "S2IGDualProbeBindingReceipt": 2_048,
    "S2IGSignalArmReceipt": 3_584,
    "S2IGBaselineArmReceipt": 3_584,
    "S2IGDualOwnerCommitReceipt": 1_792,
    "S2IGCaseEvidenceReceipt": 3_584,
    "S2IGExecutionEvidencePackage": 3_072,
    "S2IGEvaluationRunBinding": 1_024,
    "S2IGEvaluationFinding": 1_536,
    "S2IGAggregateFinding": 1_280,
    "S2IGTerminalFinding": 1_024,
    "S2IGCompletionMarker": 1_024,
}

ERROR_CODES = tuple(f"IG-E{index:03d}" for index in range(1, 13))


@dataclass(frozen=True, slots=True)
class OperationRow:
    index: int
    operation_id: str
    phase: str
    operation_class: str
    history_id: str | None
    case_id: str | None
    parent_operations: tuple[str, ...]
    owner_role: str
    receipt_type: str
    target_path: str
    output_max_bytes: int
    required_state: str
    success_state: str


@dataclass(frozen=True, slots=True)
class RegistryBundle:
    rows: tuple[OperationRow, ...]
    bundle_digest: str
    maximum_success_bytes: int
    maximum_failure_bytes: int


@dataclass(frozen=True, slots=True)
class ParentSetEntryV1:
    parent_role: str
    parent_operation_id: str
    parent_artifact_digest: str

    def __post_init__(self) -> None:
        _require(
            isinstance(self.parent_role, str) and self.parent_role in RECEIPT_LIMITS,
            "parent role differs",
        )
        _require(
            isinstance(self.parent_operation_id, str)
            and _OPERATION_ID.fullmatch(self.parent_operation_id) is not None,
            "parent operation id differs",
        )
        _require(
            isinstance(self.parent_artifact_digest, str)
            and _DIGEST.fullmatch(self.parent_artifact_digest) is not None,
            "parent artifact digest differs",
        )

    def payload(self) -> dict[str, str]:
        return {
            "parent_role": self.parent_role,
            "parent_operation_id": self.parent_operation_id,
            "parent_artifact_digest": self.parent_artifact_digest,
        }


@dataclass(frozen=True, slots=True)
class ParentSetV1:
    registry_bundle_digest: str
    reservation_digest: str
    child_operation_id: str
    parents: tuple[ParentSetEntryV1, ...]
    parent_set_digest: str
    schema: str = PARENT_SET_SCHEMA

    def __post_init__(self) -> None:
        _require(self.schema == PARENT_SET_SCHEMA, "parent set schema differs")
        _require(
            isinstance(self.registry_bundle_digest, str)
            and _DIGEST.fullmatch(self.registry_bundle_digest) is not None
            and isinstance(self.reservation_digest, str)
            and _DIGEST.fullmatch(self.reservation_digest) is not None
            and isinstance(self.parent_set_digest, str)
            and _DIGEST.fullmatch(self.parent_set_digest) is not None,
            "parent set digest role differs",
        )
        _require(
            isinstance(self.child_operation_id, str)
            and _OPERATION_ID.fullmatch(self.child_operation_id) is not None,
            "parent set child differs",
        )
        _require(type(self.parents) is tuple and len(self.parents) >= 2, "parent set count differs")
        for parent in self.parents:
            _require(type(parent) is ParentSetEntryV1, "parent set entry type differs")
            parent.__post_init__()
        identifiers = tuple(item.parent_operation_id for item in self.parents)
        digests = tuple(item.parent_artifact_digest for item in self.parents)
        _require(identifiers == tuple(sorted(identifiers)), "parent set order differs")
        _require(len(set(identifiers)) == len(identifiers), "duplicate parent operation")
        _require(len(set(digests)) == len(digests), "duplicate parent artifact")
        payload = self.payload_without_digest()
        _require(
            len(canonical_bytes(payload)) <= MAX_PARENT_SET_PREIMAGE_BYTES,
            "parent set preimage exceeds bound",
        )
        _require(self.parent_set_digest == canonical_digest(payload), "parent set digest differs")

    @property
    def parent_count(self) -> int:
        return len(self.parents)

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "registry_bundle_digest": self.registry_bundle_digest,
            "reservation_digest": self.reservation_digest,
            "child_operation_id": self.child_operation_id,
            "parent_count": self.parent_count,
            "parents": [item.payload() for item in self.parents],
        }


def materialize_parent_set(
    child: OperationRow,
    registry: RegistryBundle,
    reservation_digest: str,
    parent_artifacts: tuple[tuple[str, str], ...],
) -> ParentSetV1:
    """Build one compact digest from already validated parent artifacts."""

    _require(type(child) is OperationRow and type(registry) is RegistryBundle, "parent set registry differs")
    _require(
        isinstance(reservation_digest, str)
        and _DIGEST.fullmatch(reservation_digest) is not None,
        "parent set reservation differs",
    )
    _require(type(parent_artifacts) is tuple, "parent artifact collection differs")
    _require(
        all(
            type(item) is tuple
            and len(item) == 2
            and isinstance(item[0], str)
            and isinstance(item[1], str)
            and _DIGEST.fullmatch(item[1]) is not None
            for item in parent_artifacts
        ),
        "parent artifact collection differs",
    )
    expected_ids = tuple(
        item for item in child.parent_operations if _OPERATION_ID.fullmatch(item) is not None
    )
    _require(len(expected_ids) >= 2, "compact parent set is not required")
    supplied_ids = tuple(item[0] for item in parent_artifacts)
    _require(len(set(supplied_ids)) == len(supplied_ids), "duplicate parent operation")
    _require(set(supplied_ids) == set(expected_ids), "missing or foreign parent operation")
    by_id = {row.operation_id: row for row in registry.rows}
    _require(child.operation_id in by_id and by_id[child.operation_id] == child, "foreign child operation")
    _require(all(item in by_id for item in expected_ids), "foreign parent operation")
    digest_by_id = dict(parent_artifacts)
    ordered_ids = tuple(sorted(expected_ids, key=lambda item: (by_id[item].index, item)))
    _require(all(by_id[item].index < child.index for item in ordered_ids), "late parent operation")
    entries = tuple(
        ParentSetEntryV1(
            by_id[item].receipt_type,
            item,
            digest_by_id[item],
        )
        for item in ordered_ids
    )
    payload = {
        "schema": PARENT_SET_SCHEMA,
        "registry_bundle_digest": registry.bundle_digest,
        "reservation_digest": reservation_digest,
        "child_operation_id": child.operation_id,
        "parent_count": len(entries),
        "parents": [item.payload() for item in entries],
    }
    value = ParentSetV1(
        registry.bundle_digest,
        reservation_digest,
        child.operation_id,
        entries,
        canonical_digest(payload),
    )
    value.__post_init__()
    return value


def _row(
    rows: list[OperationRow],
    operation_class: str,
    parents: tuple[str, ...],
    receipt_type: str,
    *,
    history_id: str | None = None,
    case_id: str | None = None,
    phase: str = "EXECUTION",
    owner_role: str = "run_owner",
    target_path: str | None = None,
    required_state: str = "ACTIVE",
    success_state: str = "ACTIVE",
) -> str:
    index = len(rows) + 1
    operation_id = f"ie-op-{index:03d}"
    path = target_path or f"receipts/{operation_id}.json"
    rows.append(
        OperationRow(
            index,
            operation_id,
            phase,
            operation_class,
            history_id,
            case_id,
            parents,
            owner_role,
            receipt_type,
            path,
            RECEIPT_LIMITS[receipt_type],
            required_state,
            success_state,
        )
    )
    return operation_id


def _build_rows() -> tuple[OperationRow, ...]:
    rows: list[OperationRow] = []
    prepare = _row(
        rows,
        "RUN_PREPARE",
        ("ROOT",),
        "S2IGRunPreparationReceipt",
        target_path="reservation.json",
    )
    manifest = _row(
        rows,
        "SOURCE_MANIFEST",
        (prepare,),
        "S2IGSourceManifestReceipt",
        target_path="manifest.json",
    )

    initial_by_history: dict[str, str] = {}
    final_formation_by_history: dict[str, str] = {}
    for history in HISTORIES:
        initial_by_history[history.history_id] = _row(
            rows,
            "HISTORY_INITIALIZE",
            (manifest,),
            "S2IGHistoryInitialReceipt",
            history_id=history.history_id,
            owner_role="history_owner",
        )

    for history in HISTORIES:
        state_parent = initial_by_history[history.history_id]
        for step in history.steps:
            receptor = _row(
                rows,
                "FORMATION_RECEPTOR_ANALYSIS",
                (state_parent,),
                "S2IGReceptorReceipt",
                history_id=history.history_id,
            )
            state_parent = _row(
                rows,
                "COMPOSITE_FORMATION",
                (state_parent, receptor),
                "S2IGFormationReceipt",
                history_id=history.history_id,
                owner_role="formation_owner",
            )
        final_formation_by_history[history.history_id] = state_parent

    history_seal_by_id: dict[str, str] = {}
    for history in HISTORIES:
        final_state = final_formation_by_history[history.history_id]
        receptor = _row(
            rows,
            "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS",
            (final_state,),
            "S2IGReceptorReceipt",
            history_id=history.history_id,
        )
        read_only = _row(
            rows,
            "COMPOSITE_READ_ONLY_PROBE",
            (final_state, receptor),
            "S2IGReadOnlyReceipt",
            history_id=history.history_id,
            owner_role="probe_owner",
        )
        s2gc = _row(
            rows,
            "S2GC_PROJECT",
            (read_only,),
            "S2IGS2GCProjectionReceipt",
            history_id=history.history_id,
        )
        s2gi = _row(
            rows,
            "S2GI_PROJECT",
            (s2gc,),
            "S2IGS2GIProjectionReceipt",
            history_id=history.history_id,
        )
        history_seal_by_id[history.history_id] = _row(
            rows,
            "HISTORY_EVIDENCE_SEAL",
            (final_state, receptor, read_only, s2gc, s2gi),
            "S2IGHistoryEvidenceReceipt",
            history_id=history.history_id,
            owner_role="history_owner",
        )

    case_evidence_by_id: dict[str, str] = {}
    for case in FUNCTION_CASES:
        history_parent = history_seal_by_id[case.history_id]
        signal_receptor = _row(
            rows,
            "SIGNAL_PROBE_RECEPTOR",
            (history_parent,),
            "S2IGReceptorReceipt",
            history_id=case.history_id,
            case_id=case.case_id,
        )
        masked = _row(
            rows,
            "MASKED_SIGNAL_PROBE_PROJECT",
            (signal_receptor,),
            "S2IGMaskedSignalProbeReceipt",
            history_id=case.history_id,
            case_id=case.case_id,
        )
        dual = _row(
            rows,
            "DUAL_PROBE_AND_ARM_INPUTS_BIND",
            (history_parent, masked),
            "S2IGDualProbeBindingReceipt",
            history_id=case.history_id,
            case_id=case.case_id,
            owner_role="dual_probe_case_owner",
        )
        signal = _row(
            rows,
            "SIGNAL_INVOKE",
            (dual,),
            "S2IGSignalArmReceipt",
            history_id=case.history_id,
            case_id=case.case_id,
            owner_role="signal_owner",
        )
        baseline = _row(
            rows,
            "BASELINE_INVOKE",
            (dual,),
            "S2IGBaselineArmReceipt",
            history_id=case.history_id,
            case_id=case.case_id,
            owner_role="baseline_owner",
        )
        commit = _row(
            rows,
            "DUAL_PROBE_CASE_OWNER_COMMIT",
            (signal, baseline),
            "S2IGDualOwnerCommitReceipt",
            history_id=case.history_id,
            case_id=case.case_id,
            owner_role="dual_probe_case_owner",
        )
        case_evidence_by_id[case.case_id] = _row(
            rows,
            "CASE_EVIDENCE_SEAL",
            (commit,),
            "S2IGCaseEvidenceReceipt",
            history_id=case.history_id,
            case_id=case.case_id,
            owner_role="dual_probe_case_owner",
        )

    execution = _row(
        rows,
        "EXECUTION_EVIDENCE_SEAL",
        tuple(history_seal_by_id.values()) + tuple(case_evidence_by_id.values()),
        "S2IGExecutionEvidencePackage",
        target_path="evidence/execution.json",
        success_state="EXECUTION_SEALED",
    )
    evaluation_binding = _row(
        rows,
        "EVALUATION_RUN_BIND",
        (execution, "external-evaluation-plan-seal"),
        "S2IGEvaluationRunBinding",
        phase="EVALUATION",
        target_path="evaluation/binding.json",
        required_state="EXECUTION_SEALED",
        success_state="EVALUATING",
        owner_role="evaluation_owner",
    )
    evaluation_rows = []
    for case in FUNCTION_CASES:
        evaluation_rows.append(
            _row(
                rows,
                "CASE_EVALUATE",
                (evaluation_binding, case_evidence_by_id[case.case_id]),
                "S2IGEvaluationFinding",
                phase="EVALUATION",
                case_id=case.case_id,
                target_path=f"evaluation/{case.case_id}.json",
                required_state="EVALUATING",
                success_state="EVALUATING",
                owner_role="evaluation_owner",
            )
        )
    aggregate = _row(
        rows,
        "AGGREGATE_EVALUATION",
        tuple(evaluation_rows),
        "S2IGAggregateFinding",
        phase="EVALUATION",
        target_path="evaluation/aggregate.json",
        required_state="EVALUATING",
        success_state="EVALUATING",
        owner_role="evaluation_owner",
    )
    terminal = _row(
        rows,
        "TERMINAL_PREPARE",
        (aggregate,),
        "S2IGTerminalFinding",
        phase="COMPLETION",
        target_path="terminal/prepared.json",
        required_state="EVALUATING",
        success_state="COMPLETING",
    )
    _row(
        rows,
        "COMPLETION_MARKER_PUBLISH",
        (terminal,),
        "S2IGCompletionMarker",
        phase="COMPLETION",
        target_path="terminal/complete/COMPLETE",
        required_state="COMPLETING",
        success_state="COMPLETE",
    )
    _require(len(rows) == SUCCESS_OPERATION_COUNT, "success registry count differs")
    return tuple(rows)


def _registry_payload(rows: tuple[OperationRow, ...]) -> dict[str, object]:
    return {
        "schema": S2IG_SCHEMA,
        "rows": [
            {
                "index": row.index,
                "operation_id": row.operation_id,
                "phase": row.phase,
                "operation_class": row.operation_class,
                "history_id": row.history_id,
                "case_id": row.case_id,
                "parent_operations": row.parent_operations,
                "owner_role": row.owner_role,
                "receipt_type": row.receipt_type,
                "target_path": row.target_path,
                "output_max_bytes": row.output_max_bytes,
                "required_state": row.required_state,
                "success_state": row.success_state,
            }
            for row in rows
        ],
    }


OPERATION_ROWS = _build_rows()
REGISTRY_BUNDLE_DIGEST = canonical_digest(_registry_payload(OPERATION_ROWS))
MAX_SUCCESS_PATH_BYTES = (
    sum(row.output_max_bytes for row in OPERATION_ROWS)
    + SUCCESS_EVENT_COUNT * MAX_EVENT_BYTES
)
MAX_FAILURE_PATH_BYTES = max(
    sum(row.output_max_bytes for row in OPERATION_ROWS[: index - 1])
    + (2 * index + 4) * MAX_EVENT_BYTES
    + 2_048
    for index in range(1, SUCCESS_OPERATION_COUNT + 1)
)
REGISTRY = RegistryBundle(
    OPERATION_ROWS,
    REGISTRY_BUNDLE_DIGEST,
    MAX_SUCCESS_PATH_BYTES,
    MAX_FAILURE_PATH_BYTES,
)

EXECUTION_FIXTURE_DIGEST = canonical_digest(
    {
        "schema": S2IG_SCHEMA,
        "histories": [item.history_digest for item in HISTORIES],
        "cases": [item.case_digest for item in FUNCTION_CASES],
        "z_visual_blocks": Z_VISUAL_BLOCKS,
        "positions": [VISIBLE_POSITIONS, MASKED_POSITIONS],
        "functional_budget": FUNCTIONAL_BUDGET,
        "registry_bundle_digest": REGISTRY_BUNDLE_DIGEST,
    }
)
EXECUTION_CONTRACT_DIGEST = canonical_digest(
    {
        "schema": "s2if.dual-probe-execution-contract.v1",
        "fixture_digest": EXECUTION_FIXTURE_DIGEST,
        "operation_count": SUCCESS_OPERATION_COUNT,
        "event_count": SUCCESS_EVENT_COUNT,
        "parent_set_schema": PARENT_SET_SCHEMA,
        "compact_parent_minimum": 2,
        "compact_parent_operation_count": COMPACT_PARENT_OPERATION_COUNT,
        "compact_parent_reference_count": COMPACT_PARENT_REFERENCE_COUNT,
        "total_internal_parent_reference_count": TOTAL_INTERNAL_PARENT_REFERENCE_COUNT,
        "maximum_parent_set_preimage_bytes": MAX_PARENT_SET_PREIMAGE_BYTES,
        "context_role": "CONTEXT_RETRIEVAL_PROBE",
        "signal_role": "MASKED_SIGNAL_PROBE",
        "automatic_selection": None,
    }
)


def load_operation_registry() -> RegistryBundle:
    """Return the immutable in-module registry after complete validation."""

    rows = OPERATION_ROWS
    _require(len(rows) == SUCCESS_OPERATION_COUNT, "operation count differs")
    _require(tuple(row.index for row in rows) == tuple(range(1, 184)), "operation indices differ")
    _require(tuple(row.operation_id for row in rows) == tuple(f"ie-op-{index:03d}" for index in range(1, 184)), "operation ids differ")
    known = {"ROOT", "external-evaluation-plan-seal"}
    compact_operation_count = 0
    compact_parent_reference_count = 0
    total_internal_parent_reference_count = 0
    for row in rows:
        _require(row.receipt_type in RECEIPT_LIMITS, "receipt limit missing")
        _require(row.output_max_bytes == RECEIPT_LIMITS[row.receipt_type], "receipt limit differs")
        internal_parents = tuple(
            parent for parent in row.parent_operations if _OPERATION_ID.fullmatch(parent) is not None
        )
        total_internal_parent_reference_count += len(internal_parents)
        if len(internal_parents) >= 2:
            compact_operation_count += 1
            compact_parent_reference_count += len(internal_parents)
        for parent in row.parent_operations:
            _require(parent in known, "operation parent is missing or cyclic")
        known.add(row.operation_id)
    _require(compact_operation_count == COMPACT_PARENT_OPERATION_COUNT, "compact operation count differs")
    _require(compact_parent_reference_count == COMPACT_PARENT_REFERENCE_COUNT, "compact parent count differs")
    _require(
        total_internal_parent_reference_count == TOTAL_INTERNAL_PARENT_REFERENCE_COUNT,
        "total parent count differs",
    )
    _require(canonical_digest(_registry_payload(rows)) == REGISTRY_BUNDLE_DIGEST, "registry digest differs")
    return REGISTRY


def validate_literal_fixtures() -> None:
    _require(len(HISTORIES) == HISTORY_COUNT and len(HISTORY_BY_ID) == HISTORY_COUNT, "history count differs")
    _require(sum(len(item.steps) for item in HISTORIES) == FORMATION_COUNT, "formation count differs")
    _require(len(FUNCTION_CASES) == FUNCTION_CASE_COUNT and len(CASE_BY_ID) == FUNCTION_CASE_COUNT, "case count differs")
    _require(sum(item.output_max_bytes for item in OPERATION_ROWS) + SUCCESS_EVENT_COUNT * MAX_EVENT_BYTES == MAX_SUCCESS_PATH_BYTES, "success budget differs")
    for history in HISTORIES:
        history.__post_init__()
    for case in FUNCTION_CASES:
        case.__post_init__()
    load_operation_registry()


__all__: tuple[str, ...] = ()
