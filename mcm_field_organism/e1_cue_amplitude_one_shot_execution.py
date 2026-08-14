"""Private S1-CY exactly-once execution for the cue-amplitude curve."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Mapping

from .e1_cue_amplitude_curve_contract import E1CueAmplitudeCurveContract
from .e1_cue_amplitude_curve_execution import (
    E1CueAmplitudeObservation,
    compose_e1_cue_amplitude_curve_result,
    evaluate_e1_cue_amplitude_curve_result,
)
from .e1_cue_amplitude_one_shot_contract import (
    E1CueAmplitudeOneShotContract,
    S1_CW_RUNNER_INVENTORY_DIGEST,
)
from .e1_cue_amplitude_runner_inventory import E1CueAmplitudeRunner


class E1CueAmplitudeOneShotExecutionError(RuntimeError):
    """Raised when the registered S1-CY attempt cannot complete."""


@dataclass(frozen=True, slots=True)
class E1CueAmplitudeOneShotReceipt:
    execution_id: str
    report_path: str
    report_sha256: str
    result_sha256: str
    one_shot_contract_digest: str
    technical_decision: str
    observation_count: int
    atomic_publish_complete: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != "e1.cue-amplitude.s1cy.once.v1"
            or len(self.report_sha256) != 64
            or len(self.result_sha256) != 64
            or len(self.one_shot_contract_digest) != 64
            or self.observation_count != 72
            or self.atomic_publish_complete is not True
        ):
            raise E1CueAmplitudeOneShotExecutionError("invalid curve receipt")


def _keys(contract: E1CueAmplitudeCurveContract) -> tuple[tuple[str, str, str, float], ...]:
    return tuple(
        (model, history, side, amplitude)
        for model in contract.model_arms
        for history in contract.history_arms
        for side in contract.cue_sides
        for amplitude in contract.amplitudes
    )


def _exclusive_marker(path: Path, value: object) -> None:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"
    try:
        with path.open("x", encoding="ascii", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise E1CueAmplitudeOneShotExecutionError(
            f"curve one-shot marker already exists: {path.name}"
        ) from exc


def _canonical_result(result: object) -> tuple[dict[str, object], str]:
    value = asdict(result)
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return value, hashlib.sha256(encoded).hexdigest()


def _atomic_publish(target: Path, value: dict[str, object]) -> bytes:
    encoded = (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=False,
        )
        + "\n"
    ).encode("ascii")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=target.name + ".tmp.", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if json.loads(temporary.read_text(encoding="ascii")) != json.loads(encoded):
            raise E1CueAmplitudeOneShotExecutionError("curve temporary reread failed")
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise E1CueAmplitudeOneShotExecutionError("curve report already exists") from exc
        if target.read_bytes() != encoded:
            raise E1CueAmplitudeOneShotExecutionError("curve published report differs")
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


def execute_e1_cue_amplitude_one_shot(
    one_shot_contract: E1CueAmplitudeOneShotContract,
    curve_contract: E1CueAmplitudeCurveContract,
    runners: Mapping[tuple[str, str, str, float], E1CueAmplitudeRunner],
    runner_inventory_digest: str,
) -> E1CueAmplitudeOneShotReceipt:
    """Execute, compose, decide and atomically publish one curve attempt."""

    if not isinstance(one_shot_contract, E1CueAmplitudeOneShotContract):
        raise E1CueAmplitudeOneShotExecutionError("curve execution needs one-shot contract")
    if not isinstance(curve_contract, E1CueAmplitudeCurveContract) or (
        curve_contract.digest() != one_shot_contract.curve_contract_digest
    ):
        raise E1CueAmplitudeOneShotExecutionError("curve contract digest changed")
    if runner_inventory_digest != S1_CW_RUNNER_INVENTORY_DIGEST or (
        runner_inventory_digest != one_shot_contract.runner_inventory_digest
    ):
        raise E1CueAmplitudeOneShotExecutionError("curve inventory digest changed")
    keys = _keys(curve_contract)
    if tuple(runners) != keys or len(runners) != 72 or any(
        not callable(runners[key]) for key in keys
    ):
        raise E1CueAmplitudeOneShotExecutionError("curve inventory is incomplete")
    target = Path(one_shot_contract.report_path)
    attempt = Path(one_shot_contract.attempt_path)
    lock = Path(one_shot_contract.lock_path)
    if any(path.exists() for path in (target, attempt, lock)):
        raise E1CueAmplitudeOneShotExecutionError("curve one-shot path is already used")

    _exclusive_marker(lock, {"execution_id": one_shot_contract.execution_id})
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": one_shot_contract.execution_id,
                "one_shot_contract_digest": one_shot_contract.digest(),
                "curve_contract_digest": curve_contract.digest(),
                "runner_inventory_digest": runner_inventory_digest,
            },
        )
        attempt_created = True
        observations: dict[tuple[str, str, str, float], E1CueAmplitudeObservation] = {}
        for key in keys:
            observation = runners[key]()
            if not isinstance(observation, E1CueAmplitudeObservation) or (
                observation.model_id,
                observation.history_id,
                observation.cue_side,
                observation.amplitude,
            ) != key:
                raise E1CueAmplitudeOneShotExecutionError("curve runner identity changed")
            observations[key] = observation
        result = compose_e1_cue_amplitude_curve_result(curve_contract, observations)
        decision = evaluate_e1_cue_amplitude_curve_result(curve_contract, result)
        if decision not in one_shot_contract.allowed_decisions:
            raise E1CueAmplitudeOneShotExecutionError("curve evaluator decision changed")
        result_value, result_digest = _canonical_result(result)
        report = {
            "execution_id": one_shot_contract.execution_id,
            "one_shot_contract_digest": one_shot_contract.digest(),
            "curve_contract_digest": curve_contract.digest(),
            "runner_inventory_digest": runner_inventory_digest,
            "result_digest": result_digest,
            "technical_decision": decision,
            "result": result_value,
        }
        if tuple(report) != one_shot_contract.report_fields:
            raise E1CueAmplitudeOneShotExecutionError("curve report fields changed")
        encoded = _atomic_publish(target, report)
        attempt.unlink()
        return E1CueAmplitudeOneShotReceipt(
            one_shot_contract.execution_id,
            str(target),
            hashlib.sha256(encoded).hexdigest(),
            result_digest,
            one_shot_contract.digest(),
            decision,
            len(observations),
            True,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
