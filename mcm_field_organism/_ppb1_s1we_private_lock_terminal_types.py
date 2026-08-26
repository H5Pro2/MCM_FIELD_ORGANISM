"""Private S1-WE lock and terminal roles for temporary filesystem tests."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
from tempfile import gettempdir

from ._ppb1_s1wb_private_production_h0_types import (
    S1WB_CALIBRATED_SOURCE_DIGESTS,
    S1WB_CALIBRATION_DIGEST,
    S1WB_CONTRACT_DIGEST,
    S1WB_CORRECTED_PLAN_DIGEST,
    S1WB_MAXIMUM_CALL_COUNT,
    S1WB_PARENT_PLAN_DIGEST,
    S1WB_RESOURCE_CONTRACT_DIGEST,
)


S1WE_SCHEMA_VERSION = "ppb1.s1we.private.lock-terminal.v1"
S1WE_INVALID_SYNTHETIC_ROLE = "S1WE_INVALID_SYNTHETIC_ROLE"
S1WE_INVALID_TEMPORARY_ROOT = "S1WE_INVALID_TEMPORARY_ROOT"
S1WE_PRODUCTION_ROOT_BLOCKED = "S1WE_PRODUCTION_ROOT_BLOCKED"
S1WE_ARTIFACT_ROLE_OCCUPIED = "S1WE_ARTIFACT_ROLE_OCCUPIED"
S1WE_LOCK_REQUIRED = "S1WE_LOCK_REQUIRED"
S1WE_LOCK_MISMATCH = "S1WE_LOCK_MISMATCH"
S1WE_PRODUCTION_EXECUTION_BLOCKED = "S1WE_PRODUCTION_EXECUTION_BLOCKED"

S1WE_CASE_COUNT = 528
S1WE_MAXIMUM_CALL_COUNT = S1WB_MAXIMUM_CALL_COUNT
S1WE_TEMPORARY_ROOT_NAME = "s1we-lock-terminal-fixtures"

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_EXECUTION_ID = re.compile(r"^s1we\.synthetic\.[a-z0-9][a-z0-9.-]{2,80}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_ERROR_CODE = re.compile(r"^[A-Z][A-Z0-9_]{2,80}$")
_ERROR_PREDECESSOR = {
    "H2": "H1",
    "H3": "H2",
    "H4": "H3",
    "H5": "H4",
    "H6": "H5",
    "H7": "H6",
}


class S1WEValidationError(ValueError):
    """One fail-closed S1-WE boundary violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _source_payload(
    source_digests: tuple[tuple[str, str], ...],
) -> list[dict[str, str]]:
    return [
        {"role": role, "digest": digest}
        for role, digest in source_digests
    ]


def _valid_common(
    execution_id: object,
    authorization_digest: object,
    resource_gate_digest: object,
    source_digests: object,
) -> bool:
    return (
        isinstance(execution_id, str)
        and _EXECUTION_ID.fullmatch(execution_id) is not None
        and _valid_digest(authorization_digest)
        and _valid_digest(resource_gate_digest)
        and source_digests == S1WB_CALIBRATED_SOURCE_DIGESTS
    )


def _common_payload(values: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": S1WE_SCHEMA_VERSION,
        "mode": "TEMPORARY_TEST_ONLY",
        "execution_id": values["execution_id"],
        "authorization_digest": values["authorization_digest"],
        "contract_digest": S1WB_CONTRACT_DIGEST,
        "calibration_digest": S1WB_CALIBRATION_DIGEST,
        "resource_contract_digest": S1WB_RESOURCE_CONTRACT_DIGEST,
        "resource_gate_digest": values["resource_gate_digest"],
        "parent_plan_digest": S1WB_PARENT_PLAN_DIGEST,
        "corrected_plan_digest": S1WB_CORRECTED_PLAN_DIGEST,
        "source_digests": _source_payload(values["source_digests"]),
        "case_count": S1WE_CASE_COUNT,
        "maximum_registered_call_count": S1WE_MAXIMUM_CALL_COUNT,
    }


@dataclass(frozen=True, slots=True)
class S1WAProductionLockMarker:
    execution_id: str
    authorization_digest: str
    resource_gate_digest: str
    source_digests: tuple[tuple[str, str], ...]
    authorization_consumed: bool
    retry_permitted: bool
    marker_digest: str

    def __post_init__(self) -> None:
        if (
            not _valid_common(
                self.execution_id,
                self.authorization_digest,
                self.resource_gate_digest,
                self.source_digests,
            )
            or self.authorization_consumed is not True
            or self.retry_permitted is not False
            or self.marker_digest != _digest(self.payload_without_digest())
        ):
            raise S1WEValidationError(
                S1WE_INVALID_SYNTHETIC_ROLE,
                "invalid temporary lock marker",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            **_common_payload(
                {name: getattr(self, name) for name in self.__dataclass_fields__}
            ),
            "role": "S1WAProductionLockMarker",
            "authorization_consumed": self.authorization_consumed,
            "retry_permitted": self.retry_permitted,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "marker_digest": self.marker_digest,
        }


def _terminal_payload(
    values: dict[str, object], status: str
) -> dict[str, object]:
    payload = {
        **_common_payload(values),
        "role": f"S1WAProduction{status.title()}Outcome",
        "status": status,
        "marker_digest": values["marker_digest"],
        "authorization_consumed": values["authorization_consumed"],
        "exactly_once_completed": values["exactly_once_completed"],
        "retry_permitted": values["retry_permitted"],
        "partial_result_exposed": values["partial_result_exposed"],
    }
    if status == "SUCCESS":
        payload.update(
            {
                "accepted_call_count": values["accepted_call_count"],
                "matrix_result_digest": values["matrix_result_digest"],
                "composition_result_digest": values[
                    "composition_result_digest"
                ],
                "evaluation_result_digest": values[
                    "evaluation_result_digest"
                ],
            }
        )
    else:
        payload.update(
            {
                "error_stage": values["error_stage"],
                "error_code": values["error_code"],
                "error_detail_digest": values["error_detail_digest"],
                "last_completed_stage": values["last_completed_stage"],
                "known_accepted_call_count": values[
                    "known_accepted_call_count"
                ],
            }
        )
    return payload


@dataclass(frozen=True, slots=True)
class S1WAProductionSuccessOutcome:
    execution_id: str
    authorization_digest: str
    resource_gate_digest: str
    marker_digest: str
    source_digests: tuple[tuple[str, str], ...]
    accepted_call_count: int
    matrix_result_digest: str
    composition_result_digest: str
    evaluation_result_digest: str
    authorization_consumed: bool
    exactly_once_completed: bool
    retry_permitted: bool
    partial_result_exposed: bool
    terminal_digest: str

    def __post_init__(self) -> None:
        if (
            not _valid_common(
                self.execution_id,
                self.authorization_digest,
                self.resource_gate_digest,
                self.source_digests,
            )
            or any(
                not _valid_digest(value)
                for value in (
                    self.marker_digest,
                    self.matrix_result_digest,
                    self.composition_result_digest,
                    self.evaluation_result_digest,
                )
            )
            or self.accepted_call_count != S1WE_MAXIMUM_CALL_COUNT
            or self.authorization_consumed is not True
            or self.exactly_once_completed is not True
            or self.retry_permitted is not False
            or self.partial_result_exposed is not False
            or self.terminal_digest != _digest(self.payload_without_digest())
        ):
            raise S1WEValidationError(
                S1WE_INVALID_SYNTHETIC_ROLE,
                "invalid temporary success outcome",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return _terminal_payload(
            {name: getattr(self, name) for name in self.__dataclass_fields__},
            "SUCCESS",
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "terminal_digest": self.terminal_digest,
        }


@dataclass(frozen=True, slots=True)
class S1WAProductionErrorOutcome:
    execution_id: str
    authorization_digest: str
    resource_gate_digest: str
    marker_digest: str
    source_digests: tuple[tuple[str, str], ...]
    error_stage: str
    error_code: str
    error_detail_digest: str
    last_completed_stage: str
    known_accepted_call_count: int | None
    authorization_consumed: bool
    exactly_once_completed: bool
    retry_permitted: bool
    partial_result_exposed: bool
    terminal_digest: str

    def __post_init__(self) -> None:
        accepted = self.known_accepted_call_count
        if (
            not _valid_common(
                self.execution_id,
                self.authorization_digest,
                self.resource_gate_digest,
                self.source_digests,
            )
            or not _valid_digest(self.marker_digest)
            or self.error_stage not in _ERROR_PREDECESSOR
            or not isinstance(self.error_code, str)
            or _ERROR_CODE.fullmatch(self.error_code) is None
            or not _valid_digest(self.error_detail_digest)
            or self.last_completed_stage
            != _ERROR_PREDECESSOR.get(self.error_stage)
            or (
                accepted is not None
                and (
                    isinstance(accepted, bool)
                    or not isinstance(accepted, int)
                    or not 0 <= accepted <= S1WE_MAXIMUM_CALL_COUNT
                )
            )
            or self.authorization_consumed is not True
            or self.exactly_once_completed is not False
            or self.retry_permitted is not False
            or self.partial_result_exposed is not False
            or self.terminal_digest != _digest(self.payload_without_digest())
        ):
            raise S1WEValidationError(
                S1WE_INVALID_SYNTHETIC_ROLE,
                "invalid temporary error outcome",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return _terminal_payload(
            {name: getattr(self, name) for name in self.__dataclass_fields__},
            "ERROR",
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "terminal_digest": self.terminal_digest,
        }


def build_s1we_synthetic_lock_marker(
    execution_id: str,
    authorization_digest: str,
    resource_gate_digest: str,
) -> S1WAProductionLockMarker:
    values = {
        "execution_id": execution_id,
        "authorization_digest": authorization_digest,
        "resource_gate_digest": resource_gate_digest,
        "source_digests": S1WB_CALIBRATED_SOURCE_DIGESTS,
        "authorization_consumed": True,
        "retry_permitted": False,
    }
    payload = {
        **_common_payload(values),
        "role": "S1WAProductionLockMarker",
        "authorization_consumed": True,
        "retry_permitted": False,
    }
    return S1WAProductionLockMarker(
        **values,
        marker_digest=_digest(payload),
    )


def build_s1we_synthetic_success_outcome(
    marker: S1WAProductionLockMarker,
    matrix_result_digest: str,
    composition_result_digest: str,
    evaluation_result_digest: str,
) -> S1WAProductionSuccessOutcome:
    if not isinstance(marker, S1WAProductionLockMarker):
        raise S1WEValidationError(
            S1WE_INVALID_SYNTHETIC_ROLE,
            "success outcome requires a temporary lock marker",
        )
    values = {
        "execution_id": marker.execution_id,
        "authorization_digest": marker.authorization_digest,
        "resource_gate_digest": marker.resource_gate_digest,
        "marker_digest": marker.marker_digest,
        "source_digests": marker.source_digests,
        "accepted_call_count": S1WE_MAXIMUM_CALL_COUNT,
        "matrix_result_digest": matrix_result_digest,
        "composition_result_digest": composition_result_digest,
        "evaluation_result_digest": evaluation_result_digest,
        "authorization_consumed": True,
        "exactly_once_completed": True,
        "retry_permitted": False,
        "partial_result_exposed": False,
    }
    return S1WAProductionSuccessOutcome(
        **values,
        terminal_digest=_digest(_terminal_payload(values, "SUCCESS")),
    )


def build_s1we_synthetic_error_outcome(
    marker: S1WAProductionLockMarker,
    error_stage: str,
    error_code: str,
    error_detail_digest: str,
    known_accepted_call_count: int | None,
) -> S1WAProductionErrorOutcome:
    if not isinstance(marker, S1WAProductionLockMarker):
        raise S1WEValidationError(
            S1WE_INVALID_SYNTHETIC_ROLE,
            "error outcome requires a temporary lock marker",
        )
    values = {
        "execution_id": marker.execution_id,
        "authorization_digest": marker.authorization_digest,
        "resource_gate_digest": marker.resource_gate_digest,
        "marker_digest": marker.marker_digest,
        "source_digests": marker.source_digests,
        "error_stage": error_stage,
        "error_code": error_code,
        "error_detail_digest": error_detail_digest,
        "last_completed_stage": _ERROR_PREDECESSOR.get(error_stage, ""),
        "known_accepted_call_count": known_accepted_call_count,
        "authorization_consumed": True,
        "exactly_once_completed": False,
        "retry_permitted": False,
        "partial_result_exposed": False,
    }
    return S1WAProductionErrorOutcome(
        **values,
        terminal_digest=_digest(_terminal_payload(values, "ERROR")),
    )


def _validate_temporary_root(root: object) -> Path:
    if not isinstance(root, Path):
        raise S1WEValidationError(
            S1WE_INVALID_TEMPORARY_ROOT,
            "artifact root must be a Path",
        )
    resolved = root.resolve()
    production = (_PROJECT_ROOT / "data/generated/ppb1/one_shot").resolve()
    temporary = Path(gettempdir()).resolve()
    if resolved == production or production in resolved.parents:
        raise S1WEValidationError(
            S1WE_PRODUCTION_ROOT_BLOCKED,
            "S1-WE cannot write the production artifact root",
        )
    if (
        resolved.name != S1WE_TEMPORARY_ROOT_NAME
        or not resolved.is_dir()
        or temporary not in resolved.parents
    ):
        raise S1WEValidationError(
            S1WE_INVALID_TEMPORARY_ROOT,
            "S1-WE requires a dedicated operating-system temporary root",
        )
    return resolved


def _artifact_paths(root: Path, execution_id: str) -> dict[str, Path]:
    return {
        "lock": root / f"{execution_id}.lock.json",
        "success": root / f"{execution_id}.success.json",
        "error": root / f"{execution_id}.error.json",
        "temporary": root / f"{execution_id}.tmp",
    }


def _exclusive_json(path: Path, payload: dict[str, object]) -> None:
    with path.open("xb") as handle:
        handle.write(_canonical_bytes(payload))
        handle.flush()
        os.fsync(handle.fileno())


def _atomic_move_without_replace(source: Path, target: Path) -> None:
    if os.name == "nt":
        os.rename(source, target)
        return
    os.link(source, target)
    source.unlink()


def write_s1we_synthetic_lock(
    root: Path,
    marker: S1WAProductionLockMarker,
) -> Path:
    resolved = _validate_temporary_root(root)
    if not isinstance(marker, S1WAProductionLockMarker):
        raise S1WEValidationError(
            S1WE_INVALID_SYNTHETIC_ROLE,
            "lock publication requires a temporary lock marker",
        )
    paths = _artifact_paths(resolved, marker.execution_id)
    if any(path.exists() for path in paths.values()):
        raise S1WEValidationError(
            S1WE_ARTIFACT_ROLE_OCCUPIED,
            "one lock or terminal artifact role is occupied",
        )
    try:
        _exclusive_json(paths["lock"], marker.canonical_payload())
    except FileExistsError as exc:
        raise S1WEValidationError(
            S1WE_ARTIFACT_ROLE_OCCUPIED,
            "lock marker already exists",
        ) from exc
    return paths["lock"]


def publish_s1we_synthetic_terminal(
    root: Path,
    outcome: S1WAProductionSuccessOutcome | S1WAProductionErrorOutcome,
) -> Path:
    resolved = _validate_temporary_root(root)
    if not isinstance(
        outcome,
        (S1WAProductionSuccessOutcome, S1WAProductionErrorOutcome),
    ):
        raise S1WEValidationError(
            S1WE_INVALID_SYNTHETIC_ROLE,
            "terminal publication requires one temporary terminal outcome",
        )
    paths = _artifact_paths(resolved, outcome.execution_id)
    if not paths["lock"].is_file():
        raise S1WEValidationError(
            S1WE_LOCK_REQUIRED,
            "terminal publication requires the durable lock",
        )
    try:
        lock_payload = json.loads(paths["lock"].read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise S1WEValidationError(
            S1WE_LOCK_MISMATCH,
            "durable lock is unreadable",
        ) from exc
    lock_without_digest = {
        key: value for key, value in lock_payload.items() if key != "marker_digest"
    }
    if (
        lock_payload.get("role") != "S1WAProductionLockMarker"
        or lock_payload.get("mode") != "TEMPORARY_TEST_ONLY"
        or lock_payload.get("authorization_consumed") is not True
        or lock_payload.get("retry_permitted") is not False
        or lock_payload.get("marker_digest") != _digest(lock_without_digest)
        or lock_payload.get("execution_id") != outcome.execution_id
        or lock_payload.get("authorization_digest")
        != outcome.authorization_digest
        or lock_payload.get("resource_gate_digest")
        != outcome.resource_gate_digest
        or lock_payload.get("marker_digest") != outcome.marker_digest
    ):
        raise S1WEValidationError(
            S1WE_LOCK_MISMATCH,
            "terminal outcome does not match the durable lock",
        )
    target_role = (
        "success"
        if isinstance(outcome, S1WAProductionSuccessOutcome)
        else "error"
    )
    counterpart_role = "error" if target_role == "success" else "success"
    if (
        paths[target_role].exists()
        or paths[counterpart_role].exists()
        or paths["temporary"].exists()
    ):
        raise S1WEValidationError(
            S1WE_ARTIFACT_ROLE_OCCUPIED,
            "terminal outcome or temporary role is occupied",
        )
    try:
        _exclusive_json(paths["temporary"], outcome.canonical_payload())
        _atomic_move_without_replace(paths["temporary"], paths[target_role])
    except (FileExistsError, OSError) as exc:
        raise S1WEValidationError(
            S1WE_ARTIFACT_ROLE_OCCUPIED,
            "terminal outcome could not be published atomically",
        ) from exc
    finally:
        if paths["temporary"].exists():
            paths["temporary"].unlink()
    return paths[target_role]


def execute_s1we_production_once() -> None:
    raise S1WEValidationError(
        S1WE_PRODUCTION_EXECUTION_BLOCKED,
        "S1-WE authorizes temporary lock and terminal tests only",
    )
