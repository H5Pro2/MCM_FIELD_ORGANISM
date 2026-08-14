"""Private S1-DI exactly-once execution for canonical A0 AV histories."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Callable

from .e1_a0_av_history_one_shot_contract import (
    E1A0AVHistoryOneShotContract,
    S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
    S1_DH_TECHNICAL_STATUSES,
    current_s1_dg_producer_implementation_digest,
    s1_dh_configuration_digest,
)
from .e1_a0_av_history_producer import E1A0AVHistoryProduction


class E1A0AVHistoryOneShotExecutionError(RuntimeError):
    """Raised when the registered S1-DI attempt cannot complete."""


E1A0AVHistoryProducer = Callable[[], E1A0AVHistoryProduction]


@dataclass(frozen=True, slots=True)
class E1A0AVHistoryOneShotReceipt:
    execution_id: str
    report_path: str
    report_sha256: str
    result_sha256: str
    one_shot_contract_digest: str
    technical_status: str
    d_state: float
    d_total_binding: float
    atomic_publish_complete: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != "e1.a0-av-history.s1di.once.v1"
            or len(self.report_sha256) != 64
            or len(self.result_sha256) != 64
            or len(self.one_shot_contract_digest) != 64
            or self.technical_status not in S1_DH_TECHNICAL_STATUSES
            or not math.isfinite(self.d_state)
            or self.d_state < 0.0
            or not math.isfinite(self.d_total_binding)
            or self.d_total_binding < 0.0
            or self.atomic_publish_complete is not True
        ):
            raise E1A0AVHistoryOneShotExecutionError(
                "invalid A0 AV history one-shot receipt"
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
        raise E1A0AVHistoryOneShotExecutionError(
            f"A0 AV history one-shot marker already exists: {path.name}"
        ) from exc


def _canonical_result(
    result: E1A0AVHistoryProduction,
) -> tuple[dict[str, object], str]:
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
        prefix=target.name + ".tmp.",
        dir=target.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if json.loads(temporary.read_text(encoding="ascii")) != json.loads(encoded):
            raise E1A0AVHistoryOneShotExecutionError(
                "A0 AV history temporary report reread failed"
            )
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise E1A0AVHistoryOneShotExecutionError(
                "A0 AV history report already exists"
            ) from exc
        if target.read_bytes() != encoded:
            raise E1A0AVHistoryOneShotExecutionError(
                "A0 AV history published report differs"
            )
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


def _history_metrics(
    result: E1A0AVHistoryProduction,
) -> tuple[float, float]:
    left = result.b_ab
    right = result.b_ba
    if (
        left.edges != right.edges
        or left.edge_inventory_digest != right.edge_inventory_digest
        or left.contract != right.contract
    ):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history E1 inventories are incompatible"
        )
    left_values = tuple(item.binding for item in left.edge_bindings)
    right_values = tuple(item.binding for item in right.edge_bindings)
    if not left_values or len(left_values) != len(right_values):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history E1 binding inventory is empty"
        )
    d_state = max(
        abs(first - second)
        for first, second in zip(left_values, right_values, strict=True)
    )
    d_total_binding = abs(math.fsum(left_values) - math.fsum(right_values))
    if not math.isfinite(d_state) or not math.isfinite(d_total_binding):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history metrics are non-finite"
        )
    return d_state, d_total_binding


def _validate_result_binding(
    contract: E1A0AVHistoryOneShotContract,
    result: E1A0AVHistoryProduction,
) -> None:
    if not isinstance(result, E1A0AVHistoryProduction):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history producer returned an invalid result"
        )
    if (
        result.history_ab_digest != contract.history_ab_digest
        or result.history_ba_digest != contract.history_ba_digest
        or result.permutation_digest != contract.permutation_digest
    ):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history result source binding changed"
        )
    if tuple(item.history_id for item in result.arm_audits) != ("ab", "ba"):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history result audits are incomplete"
        )
    if any(
        item.source_support_count != 220
        or item.assigned_event_count != 220
        or item.p0_field_digest != item.a0_field_digest
        or item.all_adapters_ablated is not True
        for item in result.arm_audits
    ):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history result controls are incomplete"
        )


def execute_e1_a0_av_history_one_shot(
    contract: E1A0AVHistoryOneShotContract,
    producer: E1A0AVHistoryProducer,
    producer_implementation_digest: str,
) -> E1A0AVHistoryOneShotReceipt:
    """Produce, measure and atomically publish one registered history attempt."""

    if not isinstance(contract, E1A0AVHistoryOneShotContract):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history execution requires its static contract"
        )
    current_implementation = current_s1_dg_producer_implementation_digest()
    if (
        producer_implementation_digest != S1_DG_PRODUCER_IMPLEMENTATION_DIGEST
        or producer_implementation_digest != contract.producer_implementation_digest
        or producer_implementation_digest != current_implementation
    ):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history producer implementation digest changed"
        )
    if contract.configuration_digest != s1_dh_configuration_digest():
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history configuration digest changed"
        )
    if not callable(producer):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history producer is not callable"
        )
    target = Path(contract.report_path)
    attempt = Path(contract.attempt_path)
    lock = Path(contract.lock_path)
    if any(path.exists() for path in (target, attempt, lock)):
        raise E1A0AVHistoryOneShotExecutionError(
            "A0 AV history one-shot path is already used"
        )

    _exclusive_marker(lock, {"execution_id": contract.execution_id})
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": contract.execution_id,
                "one_shot_contract_digest": contract.digest(),
                "history_ab_digest": contract.history_ab_digest,
                "history_ba_digest": contract.history_ba_digest,
                "permutation_digest": contract.permutation_digest,
                "producer_implementation_digest": (
                    producer_implementation_digest
                ),
                "configuration_digest": contract.configuration_digest,
            },
        )
        attempt_created = True
        result = producer()
        _validate_result_binding(contract, result)
        d_state, d_total_binding = _history_metrics(result)
        result_value, result_digest = _canonical_result(result)
        technical_status = S1_DH_TECHNICAL_STATUSES[0]
        report = {
            "execution_id": contract.execution_id,
            "one_shot_contract_digest": contract.digest(),
            "history_ab_digest": contract.history_ab_digest,
            "history_ba_digest": contract.history_ba_digest,
            "permutation_digest": contract.permutation_digest,
            "producer_implementation_digest": producer_implementation_digest,
            "configuration_digest": contract.configuration_digest,
            "result_digest": result_digest,
            "technical_status": technical_status,
            "d_state": d_state,
            "d_total_binding": d_total_binding,
            "result": result_value,
        }
        if tuple(report) != contract.report_fields:
            raise E1A0AVHistoryOneShotExecutionError(
                "A0 AV history report fields changed"
            )
        encoded = _atomic_publish(target, report)
        attempt.unlink()
        return E1A0AVHistoryOneShotReceipt(
            execution_id=contract.execution_id,
            report_path=str(target),
            report_sha256=hashlib.sha256(encoded).hexdigest(),
            result_sha256=result_digest,
            one_shot_contract_digest=contract.digest(),
            technical_status=technical_status,
            d_state=d_state,
            d_total_binding=d_total_binding,
            atomic_publish_complete=True,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
