"""Private S1-CX static one-shot contract for the amplitude curve."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_cue_amplitude_curve_contract import (
    S1_CU_DECISIONS,
    build_e1_cue_amplitude_curve_contract,
)


class E1CueAmplitudeOneShotContractError(ValueError):
    """Raised when the S1-CX one-shot boundary is changed or already used."""


S1_CW_RUNNER_INVENTORY_DIGEST = (
    "d3a40cbf9e76bffb6ccab1a1a2a3facedef8ad8af7f0f2198bc876e7ef276cd9"
)
S1_CX_REPORT_FIELDS = (
    "execution_id",
    "one_shot_contract_digest",
    "curve_contract_digest",
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
class E1CueAmplitudeOneShotContract:
    """Immutable paths and digests for one future amplitude-curve attempt."""

    execution_id: str
    report_path: str
    attempt_path: str
    lock_path: str
    curve_contract_digest: str
    runner_inventory_digest: str
    report_fields: tuple[str, ...]
    allowed_decisions: tuple[str, ...]
    result_digest_method: str
    atomic_publish_method: str
    failure_policy: str
    execution_permitted: bool
    execution_started: bool

    def __post_init__(self) -> None:
        if self.execution_id != "e1.cue-amplitude.s1cy.once.v1":
            raise E1CueAmplitudeOneShotContractError("curve execution identity changed")
        if self.curve_contract_digest != build_e1_cue_amplitude_curve_contract().digest():
            raise E1CueAmplitudeOneShotContractError("S1-CU contract digest changed")
        if self.runner_inventory_digest != S1_CW_RUNNER_INVENTORY_DIGEST:
            raise E1CueAmplitudeOneShotContractError("S1-CW inventory digest changed")
        if self.report_fields != S1_CX_REPORT_FIELDS:
            raise E1CueAmplitudeOneShotContractError("curve report fields changed")
        if self.allowed_decisions != S1_CU_DECISIONS:
            raise E1CueAmplitudeOneShotContractError("curve decision order changed")
        if (
            self.result_digest_method != "sha256-canonical-json-result"
            or self.atomic_publish_method != "same-directory-exclusive-link"
            or self.failure_policy != "retain-attempt-marker-no-automatic-retry"
        ):
            raise E1CueAmplitudeOneShotContractError("curve persistence contract changed")
        if self.execution_permitted is not True or self.execution_started is not False:
            raise E1CueAmplitudeOneShotContractError("curve contract must be ready but unstarted")
        paths = tuple(Path(value) for value in self._path_values())
        if len(set(paths)) != 3 or len({path.parent for path in paths}) != 1:
            raise E1CueAmplitudeOneShotContractError("curve paths must be distinct siblings")

    def _path_values(self) -> tuple[str, str, str]:
        return self.report_path, self.attempt_path, self.lock_path

    def digest(self) -> str:
        return _digest(
            {
                name: getattr(self, name)
                for name in self.__dataclass_fields__
            }
        )


def prepare_e1_cue_amplitude_one_shot_contract(
    report_directory: Path,
) -> E1CueAmplitudeOneShotContract:
    """Bind pristine curve output paths without reserving or executing them."""

    directory = Path(report_directory).resolve()
    if not directory.is_dir():
        raise E1CueAmplitudeOneShotContractError("curve report directory does not exist")
    report = directory / "e1_cue_amplitude_s1cy_once_v1.json"
    attempt = directory / "e1_cue_amplitude_s1cy_once_v1.attempt.json"
    lock = directory / "e1_cue_amplitude_s1cy_once_v1.lock"
    if any(path.exists() for path in (report, attempt, lock)):
        raise E1CueAmplitudeOneShotContractError("curve one-shot path is already used")
    return E1CueAmplitudeOneShotContract(
        execution_id="e1.cue-amplitude.s1cy.once.v1",
        report_path=str(report),
        attempt_path=str(attempt),
        lock_path=str(lock),
        curve_contract_digest=build_e1_cue_amplitude_curve_contract().digest(),
        runner_inventory_digest=S1_CW_RUNNER_INVENTORY_DIGEST,
        report_fields=S1_CX_REPORT_FIELDS,
        allowed_decisions=S1_CU_DECISIONS,
        result_digest_method="sha256-canonical-json-result",
        atomic_publish_method="same-directory-exclusive-link",
        failure_policy="retain-attempt-marker-no-automatic-retry",
        execution_permitted=True,
        execution_started=False,
    )
