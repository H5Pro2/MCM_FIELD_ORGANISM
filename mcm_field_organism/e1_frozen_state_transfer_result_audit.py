"""Private S1-DQ static audit of the published frozen-state transfer."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_frozen_state_transfer_one_shot_contract import (
    S1_DK_CONTRACT_DIGEST,
    S1_DL_IMPLEMENTATION_DIGEST,
    S1_DM_REPORT_FIELDS,
)
from .e1_frozen_state_transfer_one_shot_execution import (
    E1FrozenStateTransferExecutionResult,
    E1FrozenStateTransferPartitionResult,
)


class E1FrozenStateTransferResultAuditError(ValueError):
    """Raised when the published S1-DQ report no longer matches evidence."""


S1_DQ_REPORT_SHA256 = (
    "cddcf121cf2fcca7145f406157cfff49c91cff526db8937520ae1c7705431ef9"
)
S1_DQ_RESULT_SHA256 = (
    "4dbf7f6b27e1731a7d4c3949a299cab6185d06461a1ed363def33dd9c234d52a"
)
S1_DM_PROJECT_CONTRACT_DIGEST = (
    "3b98967f3922f8f06fdf0576be5e09043e7f230858f2e9f45bf5e5b02dc93d9c"
)
S1_DQ_STATUS = "REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE"


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
class E1FrozenStateTransferResultAudit:
    report_sha256: str
    result_sha256: str
    contract_digest: str
    technical_status: str
    d_active_s: float
    d_active_h: float
    d_probe_partition: float
    controls_complete: bool
    attempt_marker_absent: bool
    lock_marker_absent: bool
    full_s1_dc_decision_permitted: bool
    memory_claim_permitted: bool
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.report_sha256 != S1_DQ_REPORT_SHA256
            or self.result_sha256 != S1_DQ_RESULT_SHA256
            or self.contract_digest != S1_DM_PROJECT_CONTRACT_DIGEST
            or self.technical_status != S1_DQ_STATUS
            or self.controls_complete is not True
            or self.attempt_marker_absent is not True
            or self.lock_marker_absent is not True
            or self.full_s1_dc_decision_permitted is not False
            or self.memory_claim_permitted is not False
            or len(self.audit_digest) != 64
        ):
            raise E1FrozenStateTransferResultAuditError(
                "published transfer audit boundary changed"
            )


def audit_e1_frozen_state_transfer_result(
    report_path: Path,
) -> E1FrozenStateTransferResultAudit:
    """Recompute report, result, partition and status evidence statically."""

    path = Path(report_path)
    if not path.is_file():
        raise E1FrozenStateTransferResultAuditError(
            "S1-DQ transfer report is missing"
        )
    raw = path.read_bytes()
    report_sha256 = hashlib.sha256(raw).hexdigest()
    if report_sha256 != S1_DQ_REPORT_SHA256:
        raise E1FrozenStateTransferResultAuditError(
            "S1-DQ transfer report digest changed"
        )
    try:
        report = json.loads(raw.decode("ascii"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise E1FrozenStateTransferResultAuditError(
            "S1-DQ transfer report is invalid"
        ) from exc
    if tuple(report) != S1_DM_REPORT_FIELDS:
        raise E1FrozenStateTransferResultAuditError(
            "S1-DQ transfer report fields changed"
        )
    if (
        report["execution_id"] != "e1.frozen-state-transfer.s1dn.once.v1"
        or report["one_shot_contract_digest"]
        != S1_DM_PROJECT_CONTRACT_DIGEST
        or report["s1_dk_contract_digest"] != S1_DK_CONTRACT_DIGEST
        or report["transfer_implementation_digest"]
        != S1_DL_IMPLEMENTATION_DIGEST
    ):
        raise E1FrozenStateTransferResultAuditError(
            "S1-DQ registered execution binding changed"
        )
    result_payload = report["result"]
    result_sha256 = _digest(result_payload)
    if result_sha256 != S1_DQ_RESULT_SHA256:
        raise E1FrozenStateTransferResultAuditError(
            "S1-DQ transfer result digest changed"
        )
    try:
        partitions = tuple(
            E1FrozenStateTransferPartitionResult(
                partition_id=item["partition_id"],
                boundaries=tuple(item["boundaries"]),
                arm_field_digests=tuple(
                    (role, digest) for role, digest in item["arm_field_digests"]
                ),
            )
            for item in result_payload["partitions"]
        )
        result = E1FrozenStateTransferExecutionResult(
            partitions=partitions,
            metrics=tuple((role, value) for role, value in result_payload["metrics"]),
            controls=tuple((role, value) for role, value in result_payload["controls"]),
            technical_status=result_payload["technical_status"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise E1FrozenStateTransferResultAuditError(
            "S1-DQ typed result reconstruction failed"
        ) from exc
    expected_partition_digests = [
        [item.partition_id, item.digest()] for item in result.partitions
    ]
    if report["partition_result_digests"] != expected_partition_digests:
        raise E1FrozenStateTransferResultAuditError(
            "S1-DQ partition result digest changed"
        )
    if (
        report["technical_status"] != result.technical_status
        or report["metrics"] != result_payload["metrics"]
        or report["controls"] != result_payload["controls"]
    ):
        raise E1FrozenStateTransferResultAuditError(
            "S1-DQ report and result mirrors differ"
        )
    metrics = dict(result.metrics)
    controls_complete = all(value is True for _, value in result.controls)
    attempt = path.with_name(path.name.replace(".json", ".attempt.json"))
    lock = path.with_name(path.name.replace(".json", ".lock"))
    audit_payload = {
        "report_sha256": report_sha256,
        "result_sha256": result_sha256,
        "contract_digest": report["one_shot_contract_digest"],
        "technical_status": result.technical_status,
        "metrics": result.metrics,
        "controls": result.controls,
        "partition_result_digests": expected_partition_digests,
        "attempt_marker_absent": not attempt.exists(),
        "lock_marker_absent": not lock.exists(),
        "full_s1_dc_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1FrozenStateTransferResultAudit(
        report_sha256=report_sha256,
        result_sha256=result_sha256,
        contract_digest=report["one_shot_contract_digest"],
        technical_status=result.technical_status,
        d_active_s=float(metrics["d_active_s"]),
        d_active_h=float(metrics["d_active_h"]),
        d_probe_partition=float(metrics["d_probe_partition"]),
        controls_complete=controls_complete,
        attempt_marker_absent=not attempt.exists(),
        lock_marker_absent=not lock.exists(),
        full_s1_dc_decision_permitted=False,
        memory_claim_permitted=False,
        audit_digest=_digest(audit_payload),
    )
