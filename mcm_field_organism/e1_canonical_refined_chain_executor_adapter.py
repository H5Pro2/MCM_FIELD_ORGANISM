"""Private S1-EA4 canonical exactly-once adapter with mirror-only testing."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Callable

from .e1_canonical_refined_chain_release_preflight import (
    E1CanonicalRefinedChainReleasePreflight,
    prepare_e1_canonical_refined_chain_release_preflight,
)
from .e1_refined_chain_one_shot_contract import (
    E1RefinedChainOneShotContract,
    S1_DW_REPORT_FIELDS,
    prepare_e1_refined_chain_one_shot_contract,
)
from .e1_refined_chain_one_shot_execution import E1RefinedChainExecutionResult
from .e1_refined_world_formation_contract import S1_DS_DECISIONS


class E1CanonicalRefinedChainExecutorAdapterError(RuntimeError):
    """Raised when the S1-EA4 adapter cannot preserve exactly-once rules."""


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
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
        raise E1CanonicalRefinedChainExecutorAdapterError(
            f"S1-EA4 marker already exists: {path.name}"
        ) from exc


def _atomic_publish(target: Path, report: dict[str, object]) -> bytes:
    encoded = (
        json.dumps(
            report,
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
            raise E1CanonicalRefinedChainExecutorAdapterError(
                "S1-EA4 temporary report reread failed"
            )
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise E1CanonicalRefinedChainExecutorAdapterError(
                "S1-EA4 report already exists"
            ) from exc
        if target.read_bytes() != encoded:
            raise E1CanonicalRefinedChainExecutorAdapterError(
                "S1-EA4 published report differs"
            )
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


@dataclass(frozen=True, slots=True)
class E1CanonicalExecutorAdapterBinding:
    binding_id: str
    release_preflight_digest: str
    one_shot_contract_digest: str
    report_name: str
    attempt_name: str
    lock_name: str
    report_fields: tuple[str, ...]
    canonical_executor_bound: bool
    mirror_execution_permitted: bool
    canonical_execution_permitted: bool
    canonical_persistence_permitted: bool
    automatic_retry_permitted: bool

    def __post_init__(self) -> None:
        if self.binding_id != "e1.canonical-executor-adapter.s1ea4.v1":
            raise E1CanonicalRefinedChainExecutorAdapterError(
                "S1-EA4 binding identity changed"
            )
        if not _valid_digest(self.release_preflight_digest) or not _valid_digest(
            self.one_shot_contract_digest
        ):
            raise E1CanonicalRefinedChainExecutorAdapterError(
                "S1-EA4 upstream digest is invalid"
            )
        if (
            self.report_name != "e1_refined_formation_transfer_s1ea_once_v1.json"
            or self.attempt_name
            != "e1_refined_formation_transfer_s1ea_once_v1.attempt.json"
            or self.lock_name != "e1_refined_formation_transfer_s1ea_once_v1.lock"
            or self.report_fields != S1_DW_REPORT_FIELDS
            or self.canonical_executor_bound is not True
            or self.mirror_execution_permitted is not True
        ):
            raise E1CanonicalRefinedChainExecutorAdapterError(
                "S1-EA4 path, report, or executor binding changed"
            )
        if any(
            value is not False
            for value in (
                self.canonical_execution_permitted,
                self.canonical_persistence_permitted,
                self.automatic_retry_permitted,
            )
        ):
            raise E1CanonicalRefinedChainExecutorAdapterError(
                "S1-EA4 cannot release canonical execution"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True, slots=True)
class E1CanonicalExecutorMirrorReceipt:
    execution_id: str
    report_path: str
    report_sha256: str
    result_sha256: str
    adapter_binding_digest: str
    technical_decision: str
    atomic_publish_complete: bool
    mirror_only: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != "e1.refined-formation-transfer.s1ea.once.v1"
            or not _valid_digest(self.report_sha256)
            or not _valid_digest(self.result_sha256)
            or not _valid_digest(self.adapter_binding_digest)
            or self.technical_decision not in S1_DS_DECISIONS
            or self.atomic_publish_complete is not True
            or self.mirror_only is not True
        ):
            raise E1CanonicalRefinedChainExecutorAdapterError(
                "S1-EA4 mirror receipt is invalid"
            )


def prepare_e1_canonical_executor_adapter(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1CanonicalExecutorAdapterBinding:
    """Bind the adapter without invoking a producer or touching a target."""

    release = prepare_e1_canonical_refined_chain_release_preflight(
        report_directory, upstream_report_path
    )
    contract = prepare_e1_refined_chain_one_shot_contract(
        report_directory, upstream_report_path
    )
    return E1CanonicalExecutorAdapterBinding(
        binding_id="e1.canonical-executor-adapter.s1ea4.v1",
        release_preflight_digest=release.digest(),
        one_shot_contract_digest=contract.digest(),
        report_name=Path(contract.report_path).name,
        attempt_name=Path(contract.attempt_path).name,
        lock_name=Path(contract.lock_path).name,
        report_fields=contract.report_fields,
        canonical_executor_bound=True,
        mirror_execution_permitted=True,
        canonical_execution_permitted=False,
        canonical_persistence_permitted=False,
        automatic_retry_permitted=False,
    )


def _report_value(
    contract: E1RefinedChainOneShotContract,
    result: E1RefinedChainExecutionResult,
) -> tuple[dict[str, object], str]:
    result_value = asdict(result)
    result_digest = _digest(result_value)
    report = {
        "execution_id": contract.execution_id,
        "one_shot_contract_digest": contract.digest(),
        "s1_ds_contract_digest": contract.s1_ds_contract_digest,
        "s1_du_preflight_digest": contract.s1_du_preflight_digest,
        "formation_implementation_digest": contract.formation_implementation_digest,
        "transfer_implementation_digest": contract.transfer_implementation_digest,
        "source_digests": (
            contract.history_ab_digest,
            contract.history_ba_digest,
            contract.permutation_digest,
        ),
        "probe_digest": contract.probe_digest,
        "refinement_result_digests": tuple(
            (item.refinement_id, item.digest()) for item in result.refinements
        ),
        "result_digest": result_digest,
        "technical_decision": result.technical_decision,
        "metrics": result.metrics,
        "controls": result.controls,
        "result": result_value,
    }
    if tuple(report) != S1_DW_REPORT_FIELDS:
        raise E1CanonicalRefinedChainExecutorAdapterError(
            "S1-EA4 report fields changed"
        )
    return report, result_digest


def execute_mirrored_e1_canonical_refined_chain_one_shot(
    adapter: E1CanonicalExecutorAdapterBinding,
    contract: E1RefinedChainOneShotContract,
    producer: Callable[[], E1RefinedChainExecutionResult],
    mirror_directory: Path,
) -> E1CanonicalExecutorMirrorReceipt:
    """Exercise canonical path semantics only in an isolated mirror directory."""

    if not isinstance(adapter, E1CanonicalExecutorAdapterBinding) or not isinstance(
        contract, E1RefinedChainOneShotContract
    ):
        raise E1CanonicalRefinedChainExecutorAdapterError(
            "S1-EA4 mirror requires current adapter and contract"
        )
    if adapter.one_shot_contract_digest != contract.digest() or not callable(producer):
        raise E1CanonicalRefinedChainExecutorAdapterError(
            "S1-EA4 mirror contract or producer changed"
        )
    directory = Path(mirror_directory).resolve()
    canonical_directory = Path(contract.report_path).parent.resolve()
    if not directory.is_dir() or directory == canonical_directory:
        raise E1CanonicalRefinedChainExecutorAdapterError(
            "S1-EA4 mirror directory is invalid or canonical"
        )
    target = directory / adapter.report_name
    attempt = directory / adapter.attempt_name
    lock = directory / adapter.lock_name
    if any(path.exists() for path in (target, attempt, lock)):
        raise E1CanonicalRefinedChainExecutorAdapterError(
            "S1-EA4 mirror one-shot path is already used"
        )
    execution_id = contract.execution_id
    _exclusive_marker(lock, {"execution_id": execution_id, "mirror_only": True})
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": execution_id,
                "adapter_binding_digest": adapter.digest(),
                "mirror_only": True,
            },
        )
        attempt_created = True
        result = producer()
        if not isinstance(result, E1RefinedChainExecutionResult):
            raise E1CanonicalRefinedChainExecutorAdapterError(
                "S1-EA4 producer returned an invalid result"
            )
        report, result_digest = _report_value(contract, result)
        encoded = _atomic_publish(target, report)
        attempt.unlink()
        return E1CanonicalExecutorMirrorReceipt(
            execution_id=execution_id,
            report_path=str(target),
            report_sha256=hashlib.sha256(encoded).hexdigest(),
            result_sha256=result_digest,
            adapter_binding_digest=adapter.digest(),
            technical_decision=result.technical_decision,
            atomic_publish_complete=True,
            mirror_only=True,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)


def execute_e1_canonical_refined_chain_one_shot(
    adapter: E1CanonicalExecutorAdapterBinding,
    contract: E1RefinedChainOneShotContract,
    producer: Callable[[], E1RefinedChainExecutionResult],
):
    """Reserved canonical entrypoint; S1-EA5 must release it explicitly."""

    del contract, producer
    if not isinstance(adapter, E1CanonicalExecutorAdapterBinding):
        raise E1CanonicalRefinedChainExecutorAdapterError(
            "S1-EA4 canonical execution requires its adapter binding"
        )
    raise E1CanonicalRefinedChainExecutorAdapterError(
        "S1-EA4 canonical execution remains locked until S1-EA5"
    )
