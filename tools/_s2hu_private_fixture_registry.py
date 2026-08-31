"""Private execution fixtures and registry binding for S2-HU.

This module contains execution inputs and explicit requested roles only. It
does not contain evaluation targets, call project functions, create files, or
run the experiment.
"""

from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import json
from pathlib import Path
import re


S2HU_SCHEMA = "s2hu.private.execution-fixtures.v1"
OPERATION_REGISTRY_RELATIVE_PATH = "docs/S2HS_OPERATION_REGISTRY.csv"
OPERATION_REGISTRY_SHA256 = (
    "31df0a4aada81b0b6fdf451c18072c8a2c18bf883f266a822f3c57b189b3b2fa"
)
SUCCESS_OPERATION_COUNT = 60
SUCCESS_EVENT_COUNT = 120
MAX_FAILURE_OPERATION_COUNT = 62
MAX_FAILURE_EVENT_COUNT = 124
MAX_INDIVIDUAL_ARTIFACT_BYTES = 4_096
MAX_EVENT_BYTES = 1_536
MAX_SUCCESS_PATH_BYTES = 321_046
MAX_FAILURE_PATH_BYTES = 328_214
MAX_SOURCE_DIGESTS = 24

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9._-]{1,95}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2HURegistryError(ValueError):
    """One static or materialized S2-HU registry violation."""


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
        raise S2HURegistryError("one absolute existing file path is required")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2HURegistryError(message)


@dataclass(frozen=True, slots=True)
class HistoryStep:
    ordinal: int
    visual_fixture_id: str
    auditory_fixture_id: str
    window_start: int
    window_end: int

    def __post_init__(self) -> None:
        _require(type(self.ordinal) is int and 1 <= self.ordinal <= 5, "step ordinal differs")
        _require(
            all(
                isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None
                for value in (self.visual_fixture_id, self.auditory_fixture_id)
            ),
            "step fixture identifier differs",
        )
        _require(
            type(self.window_start) is int
            and type(self.window_end) is int
            and self.window_start == self.ordinal - 1
            and self.window_end == self.ordinal,
            "step time window differs",
        )


@dataclass(frozen=True, slots=True)
class HistoryFixture:
    history_id: str
    steps: tuple[HistoryStep, ...]
    full_probe_visual_id: str
    full_probe_auditory_id: str
    probe_window_start: int
    probe_window_end: int
    history_digest: str

    def __post_init__(self) -> None:
        _require(self.history_id in {"h0", "h1"}, "history id differs")
        _require(
            type(self.steps) is tuple
            and len(self.steps) == 5
            and tuple(item.ordinal for item in self.steps) == (1, 2, 3, 4, 5),
            "history step anatomy differs",
        )
        for item in self.steps:
            item.__post_init__()
        _require(
            isinstance(self.full_probe_visual_id, str)
            and isinstance(self.full_probe_auditory_id, str)
            and self.probe_window_start == 5
            and self.probe_window_end == 6,
            "history probe anatomy differs",
        )
        _require(
            self.history_digest == canonical_digest(self.payload_without_digest()),
            "history digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": S2HU_SCHEMA,
            "history_id": self.history_id,
            "steps": [
                [
                    item.ordinal,
                    item.visual_fixture_id,
                    item.auditory_fixture_id,
                    item.window_start,
                    item.window_end,
                ]
                for item in self.steps
            ],
            "full_probe_visual_id": self.full_probe_visual_id,
            "full_probe_auditory_id": self.full_probe_auditory_id,
            "probe_window": [self.probe_window_start, self.probe_window_end],
        }

    @classmethod
    def build(
        cls,
        history_id: str,
        formation_pairs: tuple[tuple[str, str], ...],
        full_probe_visual_id: str,
        full_probe_auditory_id: str,
    ) -> "HistoryFixture":
        steps = tuple(
            HistoryStep(index, visual, auditory, index - 1, index)
            for index, (visual, auditory) in enumerate(formation_pairs, 1)
        )
        payload = {
            "schema": S2HU_SCHEMA,
            "history_id": history_id,
            "steps": [
                [
                    item.ordinal,
                    item.visual_fixture_id,
                    item.auditory_fixture_id,
                    item.window_start,
                    item.window_end,
                ]
                for item in steps
            ],
            "full_probe_visual_id": full_probe_visual_id,
            "full_probe_auditory_id": full_probe_auditory_id,
            "probe_window": [5, 6],
        }
        return cls(
            history_id,
            steps,
            full_probe_visual_id,
            full_probe_auditory_id,
            5,
            6,
            canonical_digest(payload),
        )


@dataclass(frozen=True, slots=True)
class DirectedCaseFixture:
    case_id: str
    history_id: str
    requested_area: str
    case_digest: str

    def __post_init__(self) -> None:
        _require(
            self.case_id in {"c01", "c02", "c03", "c04"}
            and self.history_id in {"h0", "h1"}
            and self.requested_area in {"A_RECENT", "B_STABLE"},
            "directed case differs",
        )
        _require(
            self.case_digest == canonical_digest(self.payload_without_digest()),
            "directed case digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": S2HU_SCHEMA,
            "case_id": self.case_id,
            "history_id": self.history_id,
            "requested_area": self.requested_area,
        }

    @classmethod
    def build(
        cls,
        case_id: str,
        history_id: str,
        requested_area: str,
    ) -> "DirectedCaseFixture":
        payload = {
            "schema": S2HU_SCHEMA,
            "case_id": case_id,
            "history_id": history_id,
            "requested_area": requested_area,
        }
        return cls(case_id, history_id, requested_area, canonical_digest(payload))


HISTORIES = (
    HistoryFixture.build(
        "h0",
        (("v1", "m1"),) * 4 + (("v0", "m0"),),
        "q0",
        "mq",
    ),
    HistoryFixture.build(
        "h1",
        (("v0", "m0"),) * 4 + (("v1", "m1"),),
        "q1",
        "mq",
    ),
)
HISTORY_BY_ID = {item.history_id: item for item in HISTORIES}

DIRECTED_CASES = (
    DirectedCaseFixture.build("c01", "h0", "A_RECENT"),
    DirectedCaseFixture.build("c02", "h0", "B_STABLE"),
    DirectedCaseFixture.build("c03", "h1", "A_RECENT"),
    DirectedCaseFixture.build("c04", "h1", "B_STABLE"),
)
CASE_BY_ID = {item.case_id: item for item in DIRECTED_CASES}

MASKED_PROBE_SOURCE_DIGEST = canonical_digest(
    {
        "schema": S2HU_SCHEMA,
        "role": "COMMON_MASKED_VISUAL_PROBE",
        "visible_positions": [0, 2, 4, 6, 8, 10, 12, 14, 16],
        "masked_positions": [1, 3, 5, 7, 9, 11, 13, 15, 17],
    }
)

EXECUTION_FIXTURE_DIGEST = canonical_digest(
    {
        "schema": S2HU_SCHEMA,
        "histories": [item.history_digest for item in HISTORIES],
        "directed_cases": [item.case_digest for item in DIRECTED_CASES],
        "masked_probe_source_digest": MASKED_PROBE_SOURCE_DIGEST,
        "counts": [2, 10, 2, 4, SUCCESS_OPERATION_COUNT, SUCCESS_EVENT_COUNT],
        "budgets": [MAX_SUCCESS_PATH_BYTES, MAX_FAILURE_PATH_BYTES],
    }
)

EXECUTION_CONTRACT_DIGEST = canonical_digest(
    {
        "schema": "s2hs.execution-contract-root.v1",
        "fixture_digest": EXECUTION_FIXTURE_DIGEST,
        "operation_registry_sha256": OPERATION_REGISTRY_SHA256,
        "thresholds": ["44/765", "1/5"],
        "terminal_states": ["START_BLOCKED", "NOT_EVALUABLE", "COMPLETE"],
        "automatic_selection": None,
    }
)


RECEIPT_LIMITS = {
    "S2HSRunPreparationReceipt": 1_536,
    "S2HSSourceManifestReceipt": 3_584,
    "S2HSMaskedProbeReceipt": 1_280,
    "S2HSHistoryInitialReceipt": 1_280,
    "S2HSReceptorReceipt": 2_765,
    "S2HSFormationReceipt": 2_801,
    "S2HSReadOnlyReceipt": 2_048,
    "S2HSS2GCProjectionReceipt": 3_174,
    "S2HSS2GIProjectionReceipt": 2_978,
    "S2HSHistoryEvidenceReceipt": 2_048,
    "S2HSRoleBindingReceipt": 1_792,
    "S2HSArmReceipt": 2_560,
    "S2HSCaseEvidenceReceipt": 1_536,
    "S2HSExecutionEvidencePackage": 1_792,
    "S2HSEvaluationRunBinding": 1_024,
    "S2HSEvaluationFinding": 1_536,
    "S2HSAggregateFinding": 1_280,
    "S2HSTerminalFinding": 1_024,
    "S2HSCompletionMarker": 1_024,
}


ERROR_CODES = (
    "HS-E001",
    "HS-E002",
    "HS-E003",
    "HS-E004",
    "HS-E005",
    "HS-E006",
    "HS-E007",
    "HS-E008",
    "HS-E009",
    "HS-E010",
    "HS-E011",
    "HS-E012",
)


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
    source_digest: str
    bundle_digest: str


def _target_path(index: int, receipt_type: str, case_id: str | None) -> str:
    if index == 1:
        return "reservation.json"
    if index == 2:
        return "manifest.json"
    if index == 52:
        return "evidence/execution.json"
    if index == 53:
        return "evaluation/binding.json"
    if 54 <= index <= 57:
        assert case_id is not None
        return f"evaluation/{case_id}.json"
    if index == 58:
        return "evaluation/aggregate.json"
    if index == 59:
        return "terminal/prepared.json"
    if index == 60:
        return "terminal/complete/COMPLETE"
    return f"receipts/hs-op-{index:03d}.json"


def _states(index: int) -> tuple[str, str]:
    if index <= 51:
        return "ACTIVE", "ACTIVE"
    if index == 52:
        return "ACTIVE", "EXECUTION_SEALED"
    if index == 53:
        return "EXECUTION_SEALED", "EVALUATING"
    if 54 <= index <= 58:
        return "EVALUATING", "EVALUATING"
    if index == 59:
        return "EVALUATING", "COMPLETING"
    if index == 60:
        return "COMPLETING", "COMPLETE"
    raise S2HURegistryError("operation index exceeds registry")


def _read_csv(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return tuple(dict(row) for row in csv.DictReader(handle))


def load_operation_registry(workspace_root: Path) -> RegistryBundle:
    """Load the immutable S2-HS CSV without touching the S2-GT registry."""

    _require(
        isinstance(workspace_root, Path) and workspace_root.is_absolute(),
        "absolute pathlib.Path workspace root required",
    )
    path = workspace_root / OPERATION_REGISTRY_RELATIVE_PATH
    source_digest = file_digest(path)
    _require(source_digest == OPERATION_REGISTRY_SHA256, "operation registry digest differs")
    raw_rows = _read_csv(path)
    _require(len(raw_rows) == SUCCESS_OPERATION_COUNT, "operation count differs")
    ids = tuple(f"hs-op-{index:03d}" for index in range(1, 61))
    rows: list[OperationRow] = []
    for expected_index, raw in enumerate(raw_rows, 1):
        operation_id = raw.get("operation_id", "")
        _require(
            raw.get("index") == str(expected_index)
            and operation_id == ids[expected_index - 1],
            "operation identity differs",
        )
        parents = tuple(raw.get("parent_operations", "").split("|"))
        for parent in parents:
            if parent.startswith("hs-op-"):
                _require(parent in ids[: expected_index - 1], "operation parent is missing or cyclic")
            else:
                _require(
                    expected_index == 1 and parent == "ROOT"
                    or expected_index == 53 and parent == "external-evaluation-plan-seal",
                    "unknown external operation parent",
                )
        receipt_type = raw.get("receipt_type", "")
        _require(receipt_type in RECEIPT_LIMITS, "receipt type has no byte limit")
        required, success = _states(expected_index)
        rows.append(
            OperationRow(
                expected_index,
                operation_id,
                raw.get("phase", ""),
                raw.get("operation_class", ""),
                raw.get("history_id") or None,
                raw.get("case_id") or None,
                parents,
                raw.get("owner_role", ""),
                receipt_type,
                _target_path(expected_index, receipt_type, raw.get("case_id") or None),
                RECEIPT_LIMITS[receipt_type],
                required,
                success,
            )
        )
    payload = {
        "schema": S2HU_SCHEMA,
        "source_digest": source_digest,
        "operation_ids": [row.operation_id for row in rows],
        "parents": [list(row.parent_operations) for row in rows],
        "targets": [row.target_path for row in rows],
        "limits": [row.output_max_bytes for row in rows],
        "states": [[row.required_state, row.success_state] for row in rows],
        "execution_contract_digest": EXECUTION_CONTRACT_DIGEST,
    }
    return RegistryBundle(tuple(rows), source_digest, canonical_digest(payload))


def validate_literal_fixtures() -> None:
    _require(len(HISTORIES) == 2 and len(HISTORY_BY_ID) == 2, "history count differs")
    _require(sum(len(item.steps) for item in HISTORIES) == 10, "formation count differs")
    _require(len(DIRECTED_CASES) == 4 and len(CASE_BY_ID) == 4, "case count differs")
    for history in HISTORIES:
        history.__post_init__()
    for case in DIRECTED_CASES:
        case.__post_init__()
    _require(
        tuple(item.history_id for item in DIRECTED_CASES) == ("h0", "h0", "h1", "h1")
        and tuple(item.requested_area for item in DIRECTED_CASES)
        == ("A_RECENT", "B_STABLE", "A_RECENT", "B_STABLE"),
        "case symmetry differs",
    )


__all__: tuple[str, ...] = ()
