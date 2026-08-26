"""Private S1-CS static one-shot contract for the partial-cue matrix."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_partial_cue_contract import S1_CO_DECISIONS, build_e1_partial_cue_contract


class E1PartialCueOneShotContractError(ValueError):
    """Raised when the S1-CS one-shot boundary is changed or already used."""


S1_CR_RUNNER_INVENTORY_DIGEST = (
    "e91148ff48e289a7fcf6b3dbe8f8832a25907f496e24bc73fdce5950f0d34925"
)
S1_CS_REPORT_FIELDS = (
    "execution_id",
    "one_shot_contract_digest",
    "cue_contract_digest",
    "runner_inventory_digest",
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
class E1PartialCueOneShotContract:
    """Immutable paths and digests for one future partial-cue attempt."""

    execution_id: str
    report_path: str
    attempt_path: str
    lock_path: str
    cue_contract_digest: str
    runner_inventory_digest: str
    report_fields: tuple[str, ...]
    allowed_decisions: tuple[str, ...]
    result_digest_method: str
    atomic_publish_method: str
    failure_policy: str
    execution_permitted: bool
    execution_started: bool

    def __post_init__(self) -> None:
        if self.execution_id != "e1.partial-cue.s1ct.once.v1":
            raise E1PartialCueOneShotContractError("cue execution identity changed")
        if self.cue_contract_digest != build_e1_partial_cue_contract().digest():
            raise E1PartialCueOneShotContractError("S1-CO contract digest changed")
        if self.runner_inventory_digest != S1_CR_RUNNER_INVENTORY_DIGEST:
            raise E1PartialCueOneShotContractError("S1-CR inventory digest changed")
        if self.report_fields != S1_CS_REPORT_FIELDS:
            raise E1PartialCueOneShotContractError("cue report fields changed")
        if self.allowed_decisions != S1_CO_DECISIONS:
            raise E1PartialCueOneShotContractError("cue decision order changed")
        if (
            self.result_digest_method != "sha256-canonical-json-result"
            or self.atomic_publish_method != "same-directory-exclusive-link"
            or self.failure_policy != "retain-attempt-marker-no-automatic-retry"
        ):
            raise E1PartialCueOneShotContractError("cue persistence contract changed")
        if self.execution_permitted is not True or self.execution_started is not False:
            raise E1PartialCueOneShotContractError("cue contract must be ready but unstarted")
        paths = tuple(Path(value) for value in self._path_values())
        if len(set(paths)) != 3 or len({path.parent for path in paths}) != 1:
            raise E1PartialCueOneShotContractError("cue one-shot paths must be distinct siblings")

    def _path_values(self) -> tuple[str, str, str]:
        return self.report_path, self.attempt_path, self.lock_path

    def digest(self) -> str:
        return _digest(
            {
                name: getattr(self, name)
                for name in self.__dataclass_fields__
            }
        )


def prepare_e1_partial_cue_one_shot_contract(
    report_directory: Path,
) -> E1PartialCueOneShotContract:
    """Bind pristine output paths without reserving or executing the run."""

    directory = Path(report_directory).resolve()
    if not directory.is_dir():
        raise E1PartialCueOneShotContractError("cue report directory does not exist")
    report = directory / "e1_partial_cue_s1ct_once_v1.json"
    attempt = directory / "e1_partial_cue_s1ct_once_v1.attempt.json"
    lock = directory / "e1_partial_cue_s1ct_once_v1.lock"
    if any(path.exists() for path in (report, attempt, lock)):
        raise E1PartialCueOneShotContractError("cue one-shot path is already used")
    return E1PartialCueOneShotContract(
        execution_id="e1.partial-cue.s1ct.once.v1",
        report_path=str(report),
        attempt_path=str(attempt),
        lock_path=str(lock),
        cue_contract_digest=build_e1_partial_cue_contract().digest(),
        runner_inventory_digest=S1_CR_RUNNER_INVENTORY_DIGEST,
        report_fields=S1_CS_REPORT_FIELDS,
        allowed_decisions=S1_CO_DECISIONS,
        result_digest_method="sha256-canonical-json-result",
        atomic_publish_method="same-directory-exclusive-link",
        failure_policy="retain-attempt-marker-no-automatic-retry",
        execution_permitted=True,
        execution_started=False,
    )
