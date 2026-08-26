"""Private S1-CM static contract for the future E1 E4 one-shot run."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_e4_execution import E1_E4_EXECUTION_CONTRACT_DIGEST


class E1E4OneShotContractError(ValueError):
    """Raised when the static E4 one-shot boundary is not pristine."""


E1_E4_RUNNER_INVENTORY_DIGEST = (
    "e76d4154ed6e9d68a68b770c2df26012e63ca1abc02149b7c29b8b2a0c1c25c1"
)
E1_E4_ONE_SHOT_DECISIONS = (
    "INVALID_E4_RUN",
    "TECHNICALLY_INCOMPATIBLE_BASELINE_SET",
    "E4_EXPLAINED_BY_NARROW_BASELINE",
    "E4_RESIDUAL_AFTER_REGISTERED_BASELINES",
)
E1_E4_ONE_SHOT_REPORT_FIELDS = (
    "execution_id",
    "one_shot_contract_digest",
    "runner_inventory_digest",
    "execution_contract_digest",
    "result_digest",
    "technical_decision",
    "result",
)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class E1E4OneShotContract:
    """Immutable paths and checks for exactly one future E4 attempt."""

    execution_id: str
    report_path: str
    attempt_path: str
    lock_path: str
    runner_inventory_digest: str
    execution_contract_digest: str
    report_fields: tuple[str, ...]
    allowed_decisions: tuple[str, ...]
    result_digest_method: str
    atomic_publish_method: str
    failure_policy: str
    execution_permitted: bool
    execution_started: bool

    def __post_init__(self) -> None:
        if self.execution_id != "e1.e4.s1cn.once.v1":
            raise E1E4OneShotContractError("unexpected E4 execution identity")
        if self.runner_inventory_digest != E1_E4_RUNNER_INVENTORY_DIGEST:
            raise E1E4OneShotContractError("E4 runner inventory digest changed")
        if self.execution_contract_digest != E1_E4_EXECUTION_CONTRACT_DIGEST:
            raise E1E4OneShotContractError("E4 execution contract digest changed")
        if self.report_fields != E1_E4_ONE_SHOT_REPORT_FIELDS:
            raise E1E4OneShotContractError("E4 report field order changed")
        if self.allowed_decisions != E1_E4_ONE_SHOT_DECISIONS:
            raise E1E4OneShotContractError("E4 decision set changed")
        if (
            self.result_digest_method != "sha256-canonical-json-result"
            or self.atomic_publish_method != "same-directory-exclusive-link"
            or self.failure_policy != "retain-attempt-marker-no-automatic-retry"
        ):
            raise E1E4OneShotContractError("E4 persistence contract changed")
        if self.execution_permitted is not True or self.execution_started is not False:
            raise E1E4OneShotContractError("E4 contract must be ready but unstarted")
        paths = tuple(Path(value) for value in self._path_values())
        if len(set(paths)) != 3 or len({path.parent for path in paths}) != 1:
            raise E1E4OneShotContractError("E4 one-shot paths must be distinct siblings")

    def _path_values(self) -> tuple[str, str, str]:
        return self.report_path, self.attempt_path, self.lock_path

    def digest(self) -> str:
        return _digest(
            {
                "execution_id": self.execution_id,
                "report_path": self.report_path,
                "attempt_path": self.attempt_path,
                "lock_path": self.lock_path,
                "runner_inventory_digest": self.runner_inventory_digest,
                "execution_contract_digest": self.execution_contract_digest,
                "report_fields": self.report_fields,
                "allowed_decisions": self.allowed_decisions,
                "result_digest_method": self.result_digest_method,
                "atomic_publish_method": self.atomic_publish_method,
                "failure_policy": self.failure_policy,
                "execution_permitted": self.execution_permitted,
                "execution_started": self.execution_started,
            }
        )


def prepare_e1_e4_one_shot_contract(
    report_directory: Path,
) -> E1E4OneShotContract:
    """Bind pristine output paths without executing or reserving the E4 run."""

    directory = Path(report_directory).resolve()
    if not directory.is_dir():
        raise E1E4OneShotContractError("E4 report directory does not exist")
    report = directory / "e1_e4_s1cn_once_v1.json"
    attempt = directory / "e1_e4_s1cn_once_v1.attempt.json"
    lock = directory / "e1_e4_s1cn_once_v1.lock"
    if any(path.exists() for path in (report, attempt, lock)):
        raise E1E4OneShotContractError("E4 one-shot path is already used")
    return E1E4OneShotContract(
        execution_id="e1.e4.s1cn.once.v1",
        report_path=str(report),
        attempt_path=str(attempt),
        lock_path=str(lock),
        runner_inventory_digest=E1_E4_RUNNER_INVENTORY_DIGEST,
        execution_contract_digest=E1_E4_EXECUTION_CONTRACT_DIGEST,
        report_fields=E1_E4_ONE_SHOT_REPORT_FIELDS,
        allowed_decisions=E1_E4_ONE_SHOT_DECISIONS,
        result_digest_method="sha256-canonical-json-result",
        atomic_publish_method="same-directory-exclusive-link",
        failure_policy="retain-attempt-marker-no-automatic-retry",
        execution_permitted=True,
        execution_started=False,
    )
