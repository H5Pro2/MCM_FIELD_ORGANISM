"""Private S1-CN exactly-once execution for the registered E1 E4 matrix."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Callable, Mapping

from .e1_e4_execution import (
    E1E4ModelRunner,
    compose_e1_e4_run_result,
    evaluate_e1_e4_run,
    preflight_e1_e4_runners,
)
from .e1_e4_one_shot_contract import (
    E1E4OneShotContract,
    E1_E4_RUNNER_INVENTORY_DIGEST,
)
from .e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    build_neutral_e1_state,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import ReceptorContactFrame
from .shared_mcm_field import ReceptorDockAnatomy, build_shared_mcm_field


class E1E4OneShotExecutionError(RuntimeError):
    """Raised when the registered S1-CN attempt cannot complete."""


@dataclass(frozen=True, slots=True)
class E1E4OneShotReceipt:
    execution_id: str
    report_path: str
    report_sha256: str
    result_sha256: str
    one_shot_contract_digest: str
    technical_decision: str
    atomic_publish_complete: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != "e1.e4.s1cn.once.v1"
            or len(self.report_sha256) != 64
            or len(self.result_sha256) != 64
            or len(self.one_shot_contract_digest) != 64
            or self.atomic_publish_complete is not True
        ):
            raise E1E4OneShotExecutionError("invalid E4 one-shot receipt")


def build_canonical_e1_e4_inputs():
    """Build the fixed fresh three-node field and neutral E1 input."""

    reference = ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.line.v1",
        snapshot_id="auditory.reference",
        clock_id="auditory.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=(
            "auditory.carrier.0",
            "auditory.carrier.1",
            "auditory.carrier.2",
        ),
        values=(0.0, 0.0, 0.0),
    )
    field = build_shared_mcm_field(
        (reference,),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,), (1,), (2,)),
            )
        },
        sample_offsets=((-1,), (1,)),
    )
    e1_contract = E1LocalEdgePlasticityContract(
        E1_CONTRACT_ID,
        1.0,
        1.5,
        0.25,
        0.5,
    )
    return (
        field,
        build_neutral_e1_state(field.layer, e1_contract),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


def _exclusive_marker(path: Path, value: object) -> None:
    encoded = (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    )
    try:
        with path.open("x", encoding="ascii", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise E1E4OneShotExecutionError(
            f"E4 one-shot marker already exists: {path.name}"
        ) from exc


def _canonical_result(result: object) -> tuple[dict[str, object], bytes, str]:
    value = asdict(result)
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return value, encoded, hashlib.sha256(encoded).hexdigest()


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
            raise E1E4OneShotExecutionError("E4 temporary report reread failed")
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise E1E4OneShotExecutionError("E4 report already exists") from exc
        if target.read_bytes() != encoded:
            raise E1E4OneShotExecutionError("E4 published report differs")
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


def execute_e1_e4_one_shot(
    contract: E1E4OneShotContract,
    runners: Mapping[str, E1E4ModelRunner],
    continuity_anchor_supplier: Callable[[], tuple[tuple[str, float], ...]],
    runner_inventory_digest: str,
) -> E1E4OneShotReceipt:
    """Execute, decide and atomically publish the registered E4 attempt once."""

    if not isinstance(contract, E1E4OneShotContract):
        raise E1E4OneShotExecutionError("E4 execution requires its static contract")
    if runner_inventory_digest != E1_E4_RUNNER_INVENTORY_DIGEST or (
        runner_inventory_digest != contract.runner_inventory_digest
    ):
        raise E1E4OneShotExecutionError("E4 runner inventory digest changed")
    preflight_e1_e4_runners(runners)
    if not callable(continuity_anchor_supplier):
        raise E1E4OneShotExecutionError("E4 continuity supplier is not callable")
    target = Path(contract.report_path)
    attempt = Path(contract.attempt_path)
    lock = Path(contract.lock_path)
    if any(path.exists() for path in (target, attempt, lock)):
        raise E1E4OneShotExecutionError("E4 one-shot path is already used")

    _exclusive_marker(lock, {"execution_id": contract.execution_id})
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": contract.execution_id,
                "one_shot_contract_digest": contract.digest(),
                "runner_inventory_digest": runner_inventory_digest,
            },
        )
        attempt_created = True
        anchors = continuity_anchor_supplier()
        result = compose_e1_e4_run_result(runners, anchors)
        decision = evaluate_e1_e4_run(result)
        if decision not in contract.allowed_decisions:
            raise E1E4OneShotExecutionError("E4 evaluator returned an unknown decision")
        result_value, _, result_digest = _canonical_result(result)
        report = {
            "execution_id": contract.execution_id,
            "one_shot_contract_digest": contract.digest(),
            "runner_inventory_digest": runner_inventory_digest,
            "execution_contract_digest": contract.execution_contract_digest,
            "result_digest": result_digest,
            "technical_decision": decision,
            "result": result_value,
        }
        if tuple(report) != contract.report_fields:
            raise E1E4OneShotExecutionError("E4 report field order changed")
        encoded = _atomic_publish(target, report)
        attempt.unlink()
        return E1E4OneShotReceipt(
            contract.execution_id,
            str(target),
            hashlib.sha256(encoded).hexdigest(),
            result_digest,
            contract.digest(),
            decision,
            True,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
