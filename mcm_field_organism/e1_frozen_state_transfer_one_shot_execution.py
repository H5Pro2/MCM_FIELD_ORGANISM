"""Private S1-DN exactly-once publication for frozen-state transfer."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Callable

from .e1_frozen_state_transfer_contract import (
    S1_DK_ARMS,
    S1_DK_METRICS,
    S1_DK_REQUIRED_IDENTITIES,
)
from .e1_frozen_state_transfer_one_shot_contract import (
    E1FrozenStateTransferOneShotContract,
    S1_DL_IMPLEMENTATION_DIGEST,
    S1_DM_PARTITIONS,
    S1_DM_TECHNICAL_STATUSES,
    current_s1_dl_implementation_digest,
    s1_dm_configuration_digest,
)


class E1FrozenStateTransferOneShotExecutionError(RuntimeError):
    """Raised when the registered S1-DN attempt cannot complete."""


def _sha256_payload(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1FrozenStateTransferPartitionResult:
    partition_id: str
    boundaries: tuple[int, ...]
    arm_field_digests: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        expected = dict(S1_DM_PARTITIONS).get(self.partition_id)
        if expected is None or self.boundaries != expected:
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer partition binding changed"
            )
        if tuple(role for role, _ in self.arm_field_digests) != S1_DK_ARMS:
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer partition arms are incomplete"
            )
        if any(not _valid_digest(value) for _, value in self.arm_field_digests):
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer partition arm digest is invalid"
            )
        values = dict(self.arm_field_digests)
        if not (
            values["p0"] == values["ab0"] == values["ba0"]
            and values["ab1"] == values["abf"]
            and values["ba1"] == values["baf"]
        ):
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer partition identity control failed"
            )

    def digest(self) -> str:
        return _sha256_payload(asdict(self))


@dataclass(frozen=True, slots=True)
class E1FrozenStateTransferExecutionResult:
    partitions: tuple[E1FrozenStateTransferPartitionResult, ...]
    metrics: tuple[tuple[str, float], ...]
    controls: tuple[tuple[str, bool], ...]
    technical_status: str

    def __post_init__(self) -> None:
        if tuple(item.partition_id for item in self.partitions) != tuple(
            role for role, _ in S1_DM_PARTITIONS
        ):
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer partitions are incomplete"
            )
        if tuple(role for role, _ in self.metrics) != S1_DK_METRICS:
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer metrics are incomplete"
            )
        values = dict(self.metrics)
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) < 0.0
            for value in values.values()
        ):
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer metric is invalid"
            )
        if tuple(role for role, _ in self.controls) != S1_DK_REQUIRED_IDENTITIES:
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer controls are incomplete"
            )
        if any(value is not True for _, value in self.controls):
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer controls failed"
            )
        if (
            values["d_pre_s"] != 0.0
            or values["d_pre_h"] != 0.0
            or values["d_ablation"] != 0.0
            or values["d_fixed_adapter"] != 0.0
            or values["frozen_state_change"] != 0.0
        ):
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer identity residual is nonzero"
            )
        active = max(float(values["d_active_s"]), float(values["d_active_h"]))
        partition = float(values["d_probe_partition"])
        if active > partition:
            expected_status = "REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE"
        elif active == 0.0 and partition == 0.0:
            expected_status = "NO_REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE"
        else:
            expected_status = "TECHNICALLY_UNDECIDABLE"
        if (
            self.technical_status not in S1_DM_TECHNICAL_STATUSES
            or self.technical_status != expected_status
        ):
            raise E1FrozenStateTransferOneShotExecutionError(
                "transfer technical status does not follow the metrics"
            )


E1FrozenStateTransferResultProducer = Callable[
    [], E1FrozenStateTransferExecutionResult
]


@dataclass(frozen=True, slots=True)
class E1FrozenStateTransferOneShotReceipt:
    execution_id: str
    report_path: str
    report_sha256: str
    result_sha256: str
    one_shot_contract_digest: str
    technical_status: str
    metrics: tuple[tuple[str, float], ...]
    atomic_publish_complete: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != "e1.frozen-state-transfer.s1dn.once.v1"
            or not _valid_digest(self.report_sha256)
            or not _valid_digest(self.result_sha256)
            or not _valid_digest(self.one_shot_contract_digest)
            or self.technical_status not in S1_DM_TECHNICAL_STATUSES
            or tuple(role for role, _ in self.metrics) != S1_DK_METRICS
            or self.atomic_publish_complete is not True
        ):
            raise E1FrozenStateTransferOneShotExecutionError(
                "invalid frozen-state transfer one-shot receipt"
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
        raise E1FrozenStateTransferOneShotExecutionError(
            f"frozen-state transfer marker already exists: {path.name}"
        ) from exc


def _canonical_result(
    result: E1FrozenStateTransferExecutionResult,
) -> tuple[dict[str, object], str]:
    value = asdict(result)
    return value, _sha256_payload(value)


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
            raise E1FrozenStateTransferOneShotExecutionError(
                "frozen-state transfer temporary report reread failed"
            )
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise E1FrozenStateTransferOneShotExecutionError(
                "frozen-state transfer report already exists"
            ) from exc
        if target.read_bytes() != encoded:
            raise E1FrozenStateTransferOneShotExecutionError(
                "frozen-state transfer published report differs"
            )
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


def execute_e1_frozen_state_transfer_one_shot(
    contract: E1FrozenStateTransferOneShotContract,
    producer: E1FrozenStateTransferResultProducer,
    transfer_implementation_digest: str,
) -> E1FrozenStateTransferOneShotReceipt:
    """Validate and atomically publish one registered transfer result."""

    if not isinstance(contract, E1FrozenStateTransferOneShotContract):
        raise E1FrozenStateTransferOneShotExecutionError(
            "frozen-state transfer execution requires its static contract"
        )
    current_implementation = current_s1_dl_implementation_digest()
    if (
        transfer_implementation_digest != S1_DL_IMPLEMENTATION_DIGEST
        or transfer_implementation_digest != contract.transfer_implementation_digest
        or transfer_implementation_digest != current_implementation
    ):
        raise E1FrozenStateTransferOneShotExecutionError(
            "frozen-state transfer implementation digest changed"
        )
    if contract.configuration_digest != s1_dm_configuration_digest():
        raise E1FrozenStateTransferOneShotExecutionError(
            "frozen-state transfer configuration digest changed"
        )
    if not callable(producer):
        raise E1FrozenStateTransferOneShotExecutionError(
            "frozen-state transfer producer is not callable"
        )
    target = Path(contract.report_path)
    attempt = Path(contract.attempt_path)
    lock = Path(contract.lock_path)
    if any(path.exists() for path in (target, attempt, lock)):
        raise E1FrozenStateTransferOneShotExecutionError(
            "frozen-state transfer one-shot path is already used"
        )

    _exclusive_marker(lock, {"execution_id": contract.execution_id})
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": contract.execution_id,
                "one_shot_contract_digest": contract.digest(),
                "s1_dk_contract_digest": contract.s1_dk_contract_digest,
                "transfer_implementation_digest": transfer_implementation_digest,
                "configuration_digest": contract.configuration_digest,
                "probe_digest": contract.probe_digest,
            },
        )
        attempt_created = True
        result = producer()
        if not isinstance(result, E1FrozenStateTransferExecutionResult):
            raise E1FrozenStateTransferOneShotExecutionError(
                "frozen-state transfer producer returned an invalid result"
            )
        result_value, result_digest = _canonical_result(result)
        partition_digests = tuple(
            (item.partition_id, item.digest()) for item in result.partitions
        )
        report = {
            "execution_id": contract.execution_id,
            "one_shot_contract_digest": contract.digest(),
            "s1_dk_contract_digest": contract.s1_dk_contract_digest,
            "transfer_implementation_digest": transfer_implementation_digest,
            "history_report_sha256": contract.history_report_sha256,
            "history_result_sha256": contract.history_result_sha256,
            "b_ab_digest": contract.b_ab_digest,
            "b_ba_digest": contract.b_ba_digest,
            "probe_digest": contract.probe_digest,
            "partition_result_digests": partition_digests,
            "technical_status": result.technical_status,
            "metrics": result.metrics,
            "controls": result.controls,
            "result": result_value,
        }
        if tuple(report) != contract.report_fields:
            raise E1FrozenStateTransferOneShotExecutionError(
                "frozen-state transfer report fields changed"
            )
        encoded = _atomic_publish(target, report)
        attempt.unlink()
        return E1FrozenStateTransferOneShotReceipt(
            execution_id=contract.execution_id,
            report_path=str(target),
            report_sha256=hashlib.sha256(encoded).hexdigest(),
            result_sha256=result_digest,
            one_shot_contract_digest=contract.digest(),
            technical_status=result.technical_status,
            metrics=result.metrics,
            atomic_publish_complete=True,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
