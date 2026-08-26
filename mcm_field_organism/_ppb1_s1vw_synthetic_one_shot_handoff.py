"""Private S1-VW synthetic one-shot handoff with production hard-blocked."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
from tempfile import gettempdir
from typing import Callable

from ._ppb1_s1vq_corrected_matrix import S1VQMatrixResult
from ._ppb1_s1vt_result_pipeline import (
    S1VTCompositionResult,
    S1VTEvaluationResult,
    S1VTSealedMatrixResult,
    compose_s1vt_arm_records,
    evaluate_s1vt_composition,
    s1vt_receipt_digest,
    seal_s1vt_matrix_result,
)


S1VW_SCHEMA_VERSION = "ppb1.s1vw.private.synthetic.v1"
S1VW_PREFLIGHT_DIGEST = (
    "31147b026d7f7faacba93f15e607e077fa55ace537500bf4c450f8c7d278258c"
)
S1VW_PARENT_PLAN_DIGEST = (
    "35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3"
)
S1VW_CORRECTED_PLAN_DIGEST = (
    "f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210"
)
S1VW_EXPECTED_CASE_COUNT = 528
S1VW_EXPECTED_CALL_COUNT = 75808
S1VW_EXPECTED_REPEAT_COUNT = 144
S1VW_SYNTHETIC_RESOURCE_GATE_DIGEST = hashlib.sha256(
    b"s1vw.synthetic.resource-gate.no-production-resources.v1"
).hexdigest()
S1VW_CONTRACT_DIGEST = hashlib.sha256(
    json.dumps(
        {
            "schema_version": S1VW_SCHEMA_VERSION,
            "preflight_digest": S1VW_PREFLIGHT_DIGEST,
            "parent_plan_digest": S1VW_PARENT_PLAN_DIGEST,
            "corrected_plan_digest": S1VW_CORRECTED_PLAN_DIGEST,
            "case_count": S1VW_EXPECTED_CASE_COUNT,
            "call_count": S1VW_EXPECTED_CALL_COUNT,
            "stages": [f"H{index}" for index in range(8)],
            "mode": "SYNTHETIC_ONLY",
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()

S1VW_PRODUCTION_EXECUTION_BLOCKED = "S1VW_PRODUCTION_EXECUTION_BLOCKED"
S1VW_INVALID_SYNTHETIC_INPUT = "S1VW_INVALID_SYNTHETIC_INPUT"
S1VW_AUTHORIZATION_ALREADY_CONSUMED = "S1VW_AUTHORIZATION_ALREADY_CONSUMED"

S1VW_ERROR_CODES = (
    "PRODUCER_FAILED",
    "LEGACY_RESULT_INVALID",
    "S1VT_SEAL_FAILED",
    "S1VT_COMPOSITION_FAILED",
    "S1VT_EVALUATION_FAILED",
    "TERMINAL_PUBLICATION_FAILED",
)
S1VW_ERROR_STAGES = ("H2", "H3", "H4", "H5", "H6", "H7")

_EXECUTION_ID = re.compile(r"^s1vw\.synthetic\.[a-z0-9][a-z0-9.-]{2,80}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_SYNTHETIC_ROOT_NAME = "s1vw-synthetic-artifacts"


class S1VWOrchestratorError(ValueError):
    """One pre-consumption S1-VW boundary violation."""

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


def _source_digest(value: object) -> str:
    source = inspect.getsourcefile(value)
    if source is None:
        raise S1VWOrchestratorError(
            S1VW_INVALID_SYNTHETIC_INPUT, "bound module source is unavailable"
        )
    return hashlib.sha256(Path(source).read_bytes()).hexdigest()


def _source_digests() -> tuple[tuple[str, str], ...]:
    return (
        ("s1vq_result", _source_digest(S1VQMatrixResult)),
        ("s1vt_pipeline", _source_digest(S1VTSealedMatrixResult)),
        ("s1vw_orchestrator", hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),
    )


class S1VWSyntheticAuthorizationToken:
    """Synthetic-only token consumed by durable lock creation."""

    __slots__ = ("execution_id", "authorization_digest", "_consumed")

    def __init__(self, execution_id: str) -> None:
        if not isinstance(execution_id, str) or not _EXECUTION_ID.fullmatch(
            execution_id
        ):
            raise S1VWOrchestratorError(
                S1VW_INVALID_SYNTHETIC_INPUT, "invalid synthetic execution id"
            )
        self.execution_id = execution_id
        self.authorization_digest = _digest(
            {
                "schema_version": S1VW_SCHEMA_VERSION,
                "execution_id": execution_id,
                "mode": "SYNTHETIC_ONLY",
                "contract_digest": S1VW_CONTRACT_DIGEST,
                "preflight_digest": S1VW_PREFLIGHT_DIGEST,
                "resource_gate_digest": S1VW_SYNTHETIC_RESOURCE_GATE_DIGEST,
                "parent_plan_digest": S1VW_PARENT_PLAN_DIGEST,
                "corrected_plan_digest": S1VW_CORRECTED_PLAN_DIGEST,
                "case_count": S1VW_EXPECTED_CASE_COUNT,
                "call_count": S1VW_EXPECTED_CALL_COUNT,
                "retry_permitted": False,
            }
        )
        self._consumed = False

    @property
    def consumed(self) -> bool:
        return self._consumed

    def _mark_consumed(self) -> None:
        if self._consumed:
            raise S1VWOrchestratorError(
                S1VW_AUTHORIZATION_ALREADY_CONSUMED,
                "synthetic authorization was already consumed",
            )
        self._consumed = True


@dataclass(frozen=True, slots=True)
class S1VWLockMarker:
    execution_id: str
    authorization_digest: str
    source_digests: tuple[tuple[str, str], ...]
    authorization_consumed: bool
    retry_permitted: bool
    marker_digest: str

    def __post_init__(self) -> None:
        payload = self.payload_without_digest()
        if (
            not _EXECUTION_ID.fullmatch(self.execution_id)
            or not _valid_digest(self.authorization_digest)
            or len(self.source_digests) != 3
            or any(
                not isinstance(role, str) or not _valid_digest(value)
                for role, value in self.source_digests
            )
            or self.authorization_consumed is not True
            or self.retry_permitted is not False
            or self.marker_digest != _digest(payload)
        ):
            raise S1VWOrchestratorError(
                S1VW_INVALID_SYNTHETIC_INPUT, "invalid lock marker"
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1VW_SCHEMA_VERSION,
            "execution_id": self.execution_id,
            "mode": "SYNTHETIC_ONLY",
            "authorization_digest": self.authorization_digest,
            "contract_digest": S1VW_CONTRACT_DIGEST,
            "preflight_digest": S1VW_PREFLIGHT_DIGEST,
            "resource_gate_digest": S1VW_SYNTHETIC_RESOURCE_GATE_DIGEST,
            "parent_plan_digest": S1VW_PARENT_PLAN_DIGEST,
            "corrected_plan_digest": S1VW_CORRECTED_PLAN_DIGEST,
            "source_digests": [
                {"role": role, "digest": value}
                for role, value in self.source_digests
            ],
            "case_count": S1VW_EXPECTED_CASE_COUNT,
            "call_count": S1VW_EXPECTED_CALL_COUNT,
            "authorization_consumed": self.authorization_consumed,
            "retry_permitted": self.retry_permitted,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "marker_digest": self.marker_digest}


def _success_payload(values: dict[str, object]) -> dict[str, object]:
    source_digests = values["source_digests"]
    matrix = values["matrix_result"]
    composition = values["composition_result"]
    evaluation = values["evaluation_result"]
    return {
        "schema_version": S1VW_SCHEMA_VERSION,
        "execution_id": values["execution_id"],
        "mode": "SYNTHETIC_ONLY",
        "status": "SUCCESS",
        "authorization_digest": values["authorization_digest"],
        "contract_digest": S1VW_CONTRACT_DIGEST,
        "preflight_digest": S1VW_PREFLIGHT_DIGEST,
        "resource_gate_digest": S1VW_SYNTHETIC_RESOURCE_GATE_DIGEST,
        "parent_plan_digest": S1VW_PARENT_PLAN_DIGEST,
        "corrected_plan_digest": S1VW_CORRECTED_PLAN_DIGEST,
        "source_digests": [
            {"role": role, "digest": digest} for role, digest in source_digests
        ],
        "marker_digest": values["marker_digest"],
        "case_count": S1VW_EXPECTED_CASE_COUNT,
        "accepted_call_count": S1VW_EXPECTED_CALL_COUNT,
        "legacy_result_digest": values["legacy_result_digest"],
        "matrix_result_digest": values["matrix_result_digest"],
        "composition_result_digest": values["composition_result_digest"],
        "evaluation_result_digest": values["evaluation_result_digest"],
        "matrix_result": matrix.canonical_payload(),
        "composition_result": composition.canonical_payload(),
        "evaluation_result": evaluation.canonical_payload(),
        "authorization_consumed": values["authorization_consumed"],
        "exactly_once_completed": values["exactly_once_completed"],
        "retry_permitted": values["retry_permitted"],
        "s1vo_v1_bypassed": values["s1vo_v1_bypassed"],
        "partial_result_exposed": values["partial_result_exposed"],
    }


@dataclass(frozen=True, slots=True)
class S1VWSuccessOutcome:
    execution_id: str
    authorization_digest: str
    marker_digest: str
    source_digests: tuple[tuple[str, str], ...]
    legacy_result_digest: str
    matrix_result_digest: str
    composition_result_digest: str
    evaluation_result_digest: str
    authorization_consumed: bool
    exactly_once_completed: bool
    retry_permitted: bool
    s1vo_v1_bypassed: bool
    partial_result_exposed: bool
    terminal_digest: str
    matrix_result: S1VTSealedMatrixResult = field(repr=False, compare=False)
    composition_result: S1VTCompositionResult = field(repr=False, compare=False)
    evaluation_result: S1VTEvaluationResult = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        payload = self.payload_without_digest()
        if (
            not _EXECUTION_ID.fullmatch(self.execution_id)
            or any(
                not _valid_digest(value)
                for value in (
                    self.authorization_digest,
                    self.marker_digest,
                    self.legacy_result_digest,
                    self.matrix_result_digest,
                    self.composition_result_digest,
                    self.evaluation_result_digest,
                )
            )
            or self.matrix_result.digest() != self.matrix_result_digest
            or self.composition_result.digest() != self.composition_result_digest
            or self.evaluation_result.digest() != self.evaluation_result_digest
            or self.authorization_consumed is not True
            or self.exactly_once_completed is not True
            or self.retry_permitted is not False
            or self.s1vo_v1_bypassed is not False
            or self.partial_result_exposed is not False
            or self.terminal_digest != _digest(payload)
        ):
            raise S1VWOrchestratorError(
                S1VW_INVALID_SYNTHETIC_INPUT, "invalid terminal success outcome"
            )

    def payload_without_digest(self) -> dict[str, object]:
        return _success_payload(
            {name: getattr(self, name) for name in self.__dataclass_fields__}
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "terminal_digest": self.terminal_digest,
        }


@dataclass(frozen=True, slots=True)
class S1VWErrorOutcome:
    execution_id: str
    authorization_digest: str
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
        payload = self.payload_without_digest()
        if (
            not _EXECUTION_ID.fullmatch(self.execution_id)
            or self.error_stage not in S1VW_ERROR_STAGES
            or self.error_code not in S1VW_ERROR_CODES
            or self.last_completed_stage not in tuple(f"H{i}" for i in range(7))
            or any(
                not _valid_digest(value)
                for value in (
                    self.authorization_digest,
                    self.marker_digest,
                    self.error_detail_digest,
                )
            )
            or (
                self.known_accepted_call_count is not None
                and (
                    isinstance(self.known_accepted_call_count, bool)
                    or not isinstance(self.known_accepted_call_count, int)
                    or self.known_accepted_call_count < 0
                )
            )
            or self.authorization_consumed is not True
            or self.exactly_once_completed is not False
            or self.retry_permitted is not False
            or self.partial_result_exposed is not False
            or self.terminal_digest != _digest(payload)
        ):
            raise S1VWOrchestratorError(
                S1VW_INVALID_SYNTHETIC_INPUT, "invalid terminal error outcome"
            )

    def payload_without_digest(self) -> dict[str, object]:
        return _error_payload(
            {name: getattr(self, name) for name in self.__dataclass_fields__}
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "terminal_digest": self.terminal_digest,
        }


def _error_payload(values: dict[str, object]) -> dict[str, object]:
    source_digests = values["source_digests"]
    return {
            "schema_version": S1VW_SCHEMA_VERSION,
            "execution_id": values["execution_id"],
            "mode": "SYNTHETIC_ONLY",
            "status": "ERROR",
            "authorization_digest": values["authorization_digest"],
            "contract_digest": S1VW_CONTRACT_DIGEST,
            "preflight_digest": S1VW_PREFLIGHT_DIGEST,
            "resource_gate_digest": S1VW_SYNTHETIC_RESOURCE_GATE_DIGEST,
            "parent_plan_digest": S1VW_PARENT_PLAN_DIGEST,
            "corrected_plan_digest": S1VW_CORRECTED_PLAN_DIGEST,
            "source_digests": [
                {"role": role, "digest": digest}
                for role, digest in source_digests
            ],
            "marker_digest": values["marker_digest"],
            "error_stage": values["error_stage"],
            "error_code": values["error_code"],
            "error_detail_digest": values["error_detail_digest"],
            "last_completed_stage": values["last_completed_stage"],
            "known_accepted_call_count": values["known_accepted_call_count"],
            "authorization_consumed": values["authorization_consumed"],
            "exactly_once_completed": values["exactly_once_completed"],
            "retry_permitted": values["retry_permitted"],
            "partial_result_exposed": values["partial_result_exposed"],
        }


Producer = Callable[[], S1VQMatrixResult]
SealAdapter = Callable[[tuple], S1VTSealedMatrixResult]
ComposeAdapter = Callable[[S1VTSealedMatrixResult], S1VTCompositionResult]
EvaluateAdapter = Callable[[S1VTCompositionResult], S1VTEvaluationResult]
Publisher = Callable[[Path, Path, Path, dict[str, object]], None]


def _legacy_result_digest(result: S1VQMatrixResult) -> str:
    return _digest(
        {
            "corrected_plan_digest": result.corrected_plan_digest,
            "receipt_digests": [s1vt_receipt_digest(item) for item in result.receipts],
            "accepted_call_count": result.accepted_call_count,
            "repeat_comparison_digests": [
                list(item) for item in result.repeat_comparison_digests
            ],
        }
    )


def _validate_legacy_result(result: object) -> S1VQMatrixResult:
    if (
        not isinstance(result, S1VQMatrixResult)
        or result.corrected_plan_digest != S1VW_CORRECTED_PLAN_DIGEST
        or len(result.receipts) != S1VW_EXPECTED_CASE_COUNT
        or result.accepted_call_count != S1VW_EXPECTED_CALL_COUNT
        or len(result.repeat_comparison_digests) != S1VW_EXPECTED_REPEAT_COUNT
    ):
        raise S1VWOrchestratorError(
            S1VW_INVALID_SYNTHETIC_INPUT, "legacy synthetic result is incomplete"
        )
    return result


def _artifact_paths(root: Path, execution_id: str) -> dict[str, Path]:
    return {
        "lock": root / f"{execution_id}.lock.json",
        "success": root / f"{execution_id}.success.json",
        "error": root / f"{execution_id}.error.json",
        "temp": root / f"{execution_id}.tmp",
    }


def _validate_synthetic_root(root: object) -> Path:
    if not isinstance(root, Path):
        raise S1VWOrchestratorError(
            S1VW_INVALID_SYNTHETIC_INPUT, "artifact root must be a Path"
        )
    resolved = root.resolve()
    production = (Path.cwd() / "data/generated/ppb1/one_shot").resolve()
    temporary_base = Path(gettempdir()).resolve()
    if (
        resolved.name != _SYNTHETIC_ROOT_NAME
        or not resolved.is_dir()
        or temporary_base not in resolved.parents
        or resolved == production
        or production in resolved.parents
        or resolved in production.parents
    ):
        raise S1VWOrchestratorError(
            S1VW_INVALID_SYNTHETIC_INPUT,
            "synthetic artifacts require a separate temporary test root",
        )
    return resolved


def _exclusive_json(path: Path, payload: dict[str, object]) -> None:
    encoded = _canonical_bytes(payload)
    with path.open("xb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def _atomic_publish(
    target: Path,
    temporary: Path,
    counterpart: Path,
    payload: dict[str, object],
) -> None:
    if target.exists() or temporary.exists() or counterpart.exists():
        raise S1VWOrchestratorError(
            S1VW_INVALID_SYNTHETIC_INPUT, "terminal artifact path is not free"
        )
    _exclusive_json(temporary, payload)
    os.replace(temporary, target)


def _lock_marker(
    token: S1VWSyntheticAuthorizationToken,
    source_digests: tuple[tuple[str, str], ...],
    lock_path: Path,
) -> S1VWLockMarker:
    values = {
        "execution_id": token.execution_id,
        "authorization_digest": token.authorization_digest,
        "source_digests": source_digests,
        "authorization_consumed": True,
        "retry_permitted": False,
    }
    marker = S1VWLockMarker(
        **values, marker_digest=_digest({
            "schema_version": S1VW_SCHEMA_VERSION,
            "execution_id": token.execution_id,
            "mode": "SYNTHETIC_ONLY",
            "authorization_digest": token.authorization_digest,
            "contract_digest": S1VW_CONTRACT_DIGEST,
            "preflight_digest": S1VW_PREFLIGHT_DIGEST,
            "resource_gate_digest": S1VW_SYNTHETIC_RESOURCE_GATE_DIGEST,
            "parent_plan_digest": S1VW_PARENT_PLAN_DIGEST,
            "corrected_plan_digest": S1VW_CORRECTED_PLAN_DIGEST,
            "source_digests": [
                {"role": role, "digest": value}
                for role, value in source_digests
            ],
            "case_count": S1VW_EXPECTED_CASE_COUNT,
            "call_count": S1VW_EXPECTED_CALL_COUNT,
            "authorization_consumed": True,
            "retry_permitted": False,
        })
    )
    _exclusive_json(lock_path, marker.canonical_payload())
    token._mark_consumed()
    return marker


def _error_detail_digest(stage: str, error: BaseException) -> str:
    return _digest(
        {
            "stage": stage,
            "error_type": type(error).__name__,
            "error_code": getattr(error, "code", "UNCLASSIFIED"),
        }
    )


def _error_outcome(
    token: S1VWSyntheticAuthorizationToken,
    marker: S1VWLockMarker,
    source_digests: tuple[tuple[str, str], ...],
    stage: str,
    code: str,
    error: BaseException,
    last_completed: str,
    accepted: int | None,
) -> S1VWErrorOutcome:
    values = {
        "execution_id": token.execution_id,
        "authorization_digest": token.authorization_digest,
        "marker_digest": marker.marker_digest,
        "source_digests": source_digests,
        "error_stage": stage,
        "error_code": code,
        "error_detail_digest": _error_detail_digest(stage, error),
        "last_completed_stage": last_completed,
        "known_accepted_call_count": accepted,
        "authorization_consumed": True,
        "exactly_once_completed": False,
        "retry_permitted": False,
        "partial_result_exposed": False,
    }
    return S1VWErrorOutcome(**values, terminal_digest=_digest(_error_payload(values)))


def _publish_error(
    outcome: S1VWErrorOutcome,
    paths: dict[str, Path],
    publisher: Publisher,
) -> S1VWErrorOutcome:
    try:
        publisher(
            paths["error"],
            paths["temp"],
            paths["success"],
            outcome.canonical_payload(),
        )
        return outcome
    except Exception as exc:
        values = {
            "execution_id": outcome.execution_id,
            "authorization_digest": outcome.authorization_digest,
            "marker_digest": outcome.marker_digest,
            "source_digests": outcome.source_digests,
            "error_stage": "H7",
            "error_code": "TERMINAL_PUBLICATION_FAILED",
            "error_detail_digest": _error_detail_digest("H7", exc),
            "last_completed_stage": outcome.last_completed_stage,
            "known_accepted_call_count": outcome.known_accepted_call_count,
            "authorization_consumed": True,
            "exactly_once_completed": False,
            "retry_permitted": False,
            "partial_result_exposed": False,
        }
        return S1VWErrorOutcome(
            **values, terminal_digest=_digest(_error_payload(values))
        )


def _success_outcome(
    token: S1VWSyntheticAuthorizationToken,
    marker: S1VWLockMarker,
    source_digests: tuple[tuple[str, str], ...],
    legacy_digest: str,
    matrix: S1VTSealedMatrixResult,
    composition: S1VTCompositionResult,
    evaluation: S1VTEvaluationResult,
) -> S1VWSuccessOutcome:
    values = {
        "execution_id": token.execution_id,
        "authorization_digest": token.authorization_digest,
        "marker_digest": marker.marker_digest,
        "source_digests": source_digests,
        "legacy_result_digest": legacy_digest,
        "matrix_result_digest": matrix.digest(),
        "composition_result_digest": composition.digest(),
        "evaluation_result_digest": evaluation.digest(),
        "authorization_consumed": True,
        "exactly_once_completed": True,
        "retry_permitted": False,
        "s1vo_v1_bypassed": False,
        "partial_result_exposed": False,
        "matrix_result": matrix,
        "composition_result": composition,
        "evaluation_result": evaluation,
    }
    return S1VWSuccessOutcome(
        **values, terminal_digest=_digest(_success_payload(values))
    )


def run_s1vw_synthetic_once(
    token: S1VWSyntheticAuthorizationToken,
    producer: Producer,
    artifact_root: Path,
    *,
    seal_adapter: SealAdapter = seal_s1vt_matrix_result,
    compose_adapter: ComposeAdapter = compose_s1vt_arm_records,
    evaluate_adapter: EvaluateAdapter = evaluate_s1vt_composition,
    publisher: Publisher = _atomic_publish,
) -> S1VWSuccessOutcome | S1VWErrorOutcome:
    """Run only an injected synthetic producer through H0-H7 exactly once."""

    if (
        not isinstance(token, S1VWSyntheticAuthorizationToken)
        or token.consumed
        or not all(
            callable(value)
            for value in (
                producer,
                seal_adapter,
                compose_adapter,
                evaluate_adapter,
                publisher,
            )
        )
    ):
        raise S1VWOrchestratorError(
            S1VW_INVALID_SYNTHETIC_INPUT, "synthetic H0 inputs are invalid"
        )
    root = _validate_synthetic_root(artifact_root)
    paths = _artifact_paths(root, token.execution_id)
    if any(path.exists() for path in paths.values()):
        raise S1VWOrchestratorError(
            S1VW_INVALID_SYNTHETIC_INPUT,
            "synthetic execution id or artifact path was already used",
        )
    source_digests = _source_digests()
    marker = _lock_marker(token, source_digests, paths["lock"])

    try:
        legacy = producer()
    except Exception as exc:
        return _publish_error(
            _error_outcome(
                token, marker, source_digests, "H2", "PRODUCER_FAILED", exc, "H1", None
            ),
            paths,
            publisher,
        )
    try:
        legacy = _validate_legacy_result(legacy)
        legacy_digest = _legacy_result_digest(legacy)
    except Exception as exc:
        return _publish_error(
            _error_outcome(
                token,
                marker,
                source_digests,
                "H3",
                "LEGACY_RESULT_INVALID",
                exc,
                "H2",
                getattr(legacy, "accepted_call_count", None),
            ),
            paths,
            publisher,
        )
    try:
        matrix = seal_adapter(tuple(legacy.receipts))
        if not isinstance(matrix, S1VTSealedMatrixResult):
            raise TypeError("seal adapter returned the wrong role")
    except Exception as exc:
        return _publish_error(
            _error_outcome(
                token, marker, source_digests, "H4", "S1VT_SEAL_FAILED",
                exc, "H3", legacy.accepted_call_count
            ),
            paths,
            publisher,
        )
    try:
        composition = compose_adapter(matrix)
        if not isinstance(composition, S1VTCompositionResult):
            raise TypeError("compose adapter returned the wrong role")
    except Exception as exc:
        return _publish_error(
            _error_outcome(
                token, marker, source_digests, "H5", "S1VT_COMPOSITION_FAILED",
                exc, "H4", legacy.accepted_call_count
            ),
            paths,
            publisher,
        )
    try:
        evaluation = evaluate_adapter(composition)
        if not isinstance(evaluation, S1VTEvaluationResult):
            raise TypeError("evaluate adapter returned the wrong role")
    except Exception as exc:
        return _publish_error(
            _error_outcome(
                token, marker, source_digests, "H6", "S1VT_EVALUATION_FAILED",
                exc, "H5", legacy.accepted_call_count
            ),
            paths,
            publisher,
        )

    success = _success_outcome(
        token,
        marker,
        source_digests,
        legacy_digest,
        matrix,
        composition,
        evaluation,
    )
    try:
        publisher(
            paths["success"],
            paths["temp"],
            paths["error"],
            success.canonical_payload(),
        )
        return success
    except Exception as exc:
        return _publish_error(
            _error_outcome(
                token,
                marker,
                source_digests,
                "H7",
                "TERMINAL_PUBLICATION_FAILED",
                exc,
                "H6",
                legacy.accepted_call_count,
            ),
            paths,
            publisher,
        )


def execute_s1vw_production_once() -> None:
    """Keep the real producer and production artifact path unavailable."""

    raise S1VWOrchestratorError(
        S1VW_PRODUCTION_EXECUTION_BLOCKED,
        "S1-VW authorizes synthetic injected producers only",
    )
