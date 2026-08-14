"""Private S1-EB8 synthetic exactly-once report executor."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .e1_confirmation_chain_contract import (
    E1ConfirmationChainContract,
    S1_EB4_REPORT_FIELDS,
)
from .e1_confirmation_result_core import E1ConfirmationChainResult
from .e1_refined_confirmation_contract import S1_EB_DECISIONS


class E1ConfirmationSyntheticExecutorError(RuntimeError):
    """Raised when S1-EB8 synthetic publication cannot complete safely."""


S1_EB4_CONTRACT_DIGEST = (
    "acf1136fa9142747729a78dda719bd36086ce2eed9e015dbfbdb58d8302fa650"
)


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationSyntheticReceipt:
    execution_id: str
    report_path: str
    report_sha256: str
    result_sha256: str
    chain_contract_digest: str
    technical_decision: str
    atomic_publish_complete: bool
    synthetic_only: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id
            != "e1.refined-confirmation.s1eb8.synthetic.once.v1"
            or not _valid_digest(self.report_sha256)
            or not _valid_digest(self.result_sha256)
            or self.chain_contract_digest != S1_EB4_CONTRACT_DIGEST
            or self.technical_decision not in S1_EB_DECISIONS
            or self.atomic_publish_complete is not True
            or self.synthetic_only is not True
        ):
            raise E1ConfirmationSyntheticExecutorError(
                "S1-EB8 synthetic receipt is invalid"
            )


E1ConfirmationResultProducer = Callable[[], E1ConfirmationChainResult]


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
        raise E1ConfirmationSyntheticExecutorError(
            f"S1-EB8 synthetic marker already exists: {path.name}"
        ) from exc


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
        if json.loads(temporary.read_text(encoding="ascii")) != json.loads(
            encoded
        ):
            raise E1ConfirmationSyntheticExecutorError(
                "S1-EB8 temporary report reread failed"
            )
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise E1ConfirmationSyntheticExecutorError(
                "S1-EB8 synthetic report already exists"
            ) from exc
        if target.read_bytes() != encoded:
            raise E1ConfirmationSyntheticExecutorError(
                "S1-EB8 published report differs"
            )
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


def execute_synthetic_e1_confirmation_once(
    contract: E1ConfirmationChainContract,
    producer: E1ConfirmationResultProducer,
    synthetic_directory: Path,
) -> E1ConfirmationSyntheticReceipt:
    """Publish one synthetic report outside all registered project targets."""

    if not isinstance(contract, E1ConfirmationChainContract) or (
        contract.digest() != S1_EB4_CONTRACT_DIGEST
    ):
        raise E1ConfirmationSyntheticExecutorError(
            "S1-EB8 requires the current S1-EB4 contract"
        )
    if contract.execution_permitted is not False:
        raise E1ConfirmationSyntheticExecutorError(
            "S1-EB8 requires canonical execution to remain blocked"
        )
    if not callable(producer):
        raise E1ConfirmationSyntheticExecutorError(
            "S1-EB8 synthetic producer is not callable"
        )
    directory = Path(synthetic_directory).resolve()
    if not directory.is_dir():
        raise E1ConfirmationSyntheticExecutorError(
            "S1-EB8 synthetic directory does not exist"
        )
    if directory == Path(contract.report_path).parent.resolve():
        raise E1ConfirmationSyntheticExecutorError(
            "S1-EB8 cannot use the registered target directory"
        )
    target = directory / "e1_confirmation_s1eb8_synthetic_once_v1.json"
    attempt = directory / (
        "e1_confirmation_s1eb8_synthetic_once_v1.attempt.json"
    )
    lock = directory / "e1_confirmation_s1eb8_synthetic_once_v1.lock"
    if any(path.exists() for path in (target, attempt, lock)):
        raise E1ConfirmationSyntheticExecutorError(
            "S1-EB8 synthetic one-shot path is already used"
        )

    execution_id = "e1.refined-confirmation.s1eb8.synthetic.once.v1"
    _exclusive_marker(lock, {"execution_id": execution_id})
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": execution_id,
                "chain_contract_digest": contract.digest(),
                "synthetic_only": True,
            },
        )
        attempt_created = True
        result = producer()
        if not isinstance(result, E1ConfirmationChainResult) or (
            result.contract_digest != contract.digest()
        ):
            raise E1ConfirmationSyntheticExecutorError(
                "S1-EB8 producer returned an invalid result"
            )
        result.__post_init__()
        report = {
            "execution_id": execution_id,
            "confirmation_contract_digest": (
                contract.confirmation_contract_digest
            ),
            "canonical_preflight_digest": contract.canonical_preflight_digest,
            "implementation_digests": contract.implementation_digests,
            "source_digests": (
                contract.history_ab_digest,
                contract.history_ba_digest,
                contract.permutation_digest,
                contract.probe_digest,
            ),
            "plan_digests": (
                contract.ab_plan_digest,
                contract.ba_plan_digest,
                contract.probe_plan_digest,
            ),
            "refinement_result_digests": tuple(
                (item.refinement_id, item.digest())
                for item in result.refinements
            ),
            "result_digest": result.result_digest,
            "technical_decision": result.technical_decision,
            "metrics": result.metrics,
            "controls": result.controls,
            "result": asdict(result),
        }
        if tuple(report) != S1_EB4_REPORT_FIELDS:
            raise E1ConfirmationSyntheticExecutorError(
                "S1-EB8 report fields changed"
            )
        encoded = _atomic_publish(target, report)
        attempt.unlink()
        return E1ConfirmationSyntheticReceipt(
            execution_id=execution_id,
            report_path=str(target),
            report_sha256=hashlib.sha256(encoded).hexdigest(),
            result_sha256=result.result_digest,
            chain_contract_digest=contract.digest(),
            technical_decision=result.technical_decision,
            atomic_publish_complete=True,
            synthetic_only=True,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
