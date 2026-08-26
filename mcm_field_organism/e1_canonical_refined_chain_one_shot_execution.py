"""Private S1-EA6 explicit canonical one-shot execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .e1_canonical_refined_chain_executor_adapter import (
    _atomic_publish,
    _exclusive_marker,
    _report_value,
    prepare_e1_canonical_executor_adapter,
)
from .e1_canonical_refined_chain_final_gate import (
    prepare_e1_canonical_refined_chain_final_gate,
)
from .e1_canonical_refined_chain_wiring import (
    produce_e1_canonical_refined_chain_result,
)
from .e1_refined_chain_canonical_producer import (
    prepare_e1_refined_chain_canonical_producer,
)
from .e1_refined_chain_one_shot_contract import (
    prepare_e1_refined_chain_one_shot_contract,
)
from .e1_refined_chain_one_shot_execution import E1RefinedChainExecutionResult
from .e1_refined_world_formation_contract import S1_DS_DECISIONS


class E1CanonicalRefinedChainOneShotExecutionError(RuntimeError):
    """Raised when the explicit S1-EA6 one-shot cannot proceed safely."""


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _source_digest() -> str:
    path = Path(__file__)
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1CanonicalOneShotRelease:
    release_id: str
    authorization_basis: str
    final_gate_digest: str
    executor_adapter_digest: str
    execution_implementation_digest: str
    report_path: str
    attempt_path: str
    lock_path: str
    execution_permitted: bool
    exactly_once: bool
    automatic_retry_permitted: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if (
            self.release_id != "e1.canonical-refined-chain.s1ea6.once.v1"
            or self.authorization_basis
            != "explicit-continuation-after-s1ea5-ready-gate"
        ):
            raise E1CanonicalRefinedChainOneShotExecutionError(
                "S1-EA6 release identity changed"
            )
        for role in (
            "final_gate_digest",
            "executor_adapter_digest",
            "execution_implementation_digest",
        ):
            if not _valid_digest(getattr(self, role)):
                raise E1CanonicalRefinedChainOneShotExecutionError(
                    f"{role} is not SHA-256"
                )
        if self.execution_implementation_digest != _source_digest():
            raise E1CanonicalRefinedChainOneShotExecutionError(
                "S1-EA6 execution implementation changed"
            )
        targets = tuple(Path(value) for value in (
            self.report_path, self.attempt_path, self.lock_path
        ))
        if (
            len(set(targets)) != 3
            or len({item.parent for item in targets}) != 1
            or any(item.exists() for item in targets)
        ):
            raise E1CanonicalRefinedChainOneShotExecutionError(
                "S1-EA6 target paths are not distinct and free"
            )
        if (
            self.execution_permitted is not True
            or self.exactly_once is not True
            or self.automatic_retry_permitted is not False
            or self.memory_claim_permitted is not False
            or self.ai_claim_permitted is not False
        ):
            raise E1CanonicalRefinedChainOneShotExecutionError(
                "S1-EA6 release flags changed"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True, slots=True)
class E1CanonicalOneShotReceipt:
    execution_id: str
    report_path: str
    report_sha256: str
    result_sha256: str
    release_digest: str
    technical_decision: str
    atomic_publish_complete: bool
    canonical: bool
    exactly_once: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != "e1.refined-formation-transfer.s1ea.once.v1"
            or not _valid_digest(self.report_sha256)
            or not _valid_digest(self.result_sha256)
            or not _valid_digest(self.release_digest)
            or self.technical_decision not in S1_DS_DECISIONS
            or self.atomic_publish_complete is not True
            or self.canonical is not True
            or self.exactly_once is not True
        ):
            raise E1CanonicalRefinedChainOneShotExecutionError(
                "S1-EA6 receipt is invalid"
            )


def prepare_e1_canonical_one_shot_release(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1CanonicalOneShotRelease:
    """Create the explicit release only while the final gate remains ready."""

    gate = prepare_e1_canonical_refined_chain_final_gate(
        report_directory, upstream_report_path
    )
    adapter = prepare_e1_canonical_executor_adapter(
        report_directory, upstream_report_path
    )
    if (
        gate.status != "READY_FOR_EXPLICIT_ONE_SHOT_RELEASE"
        or gate.technical_one_shot_ready is not True
        or gate.execution_permitted is not False
    ):
        raise E1CanonicalRefinedChainOneShotExecutionError(
            "S1-EA6 final gate is not ready for explicit release"
        )
    return E1CanonicalOneShotRelease(
        release_id="e1.canonical-refined-chain.s1ea6.once.v1",
        authorization_basis="explicit-continuation-after-s1ea5-ready-gate",
        final_gate_digest=gate.digest(),
        executor_adapter_digest=adapter.digest(),
        execution_implementation_digest=_source_digest(),
        report_path=gate.report_path,
        attempt_path=gate.attempt_path,
        lock_path=gate.lock_path,
        execution_permitted=True,
        exactly_once=True,
        automatic_retry_permitted=False,
        memory_claim_permitted=False,
        ai_claim_permitted=False,
    )


def execute_e1_canonical_refined_chain_once(
    release: E1CanonicalOneShotRelease,
    report_directory: Path,
    upstream_report_path: Path,
) -> E1CanonicalOneShotReceipt:
    """Execute and publish the bound canonical chain exactly once."""

    if not isinstance(release, E1CanonicalOneShotRelease):
        raise E1CanonicalRefinedChainOneShotExecutionError(
            "S1-EA6 requires its explicit release"
        )
    current = prepare_e1_canonical_one_shot_release(
        report_directory, upstream_report_path
    )
    if current.digest() != release.digest():
        raise E1CanonicalRefinedChainOneShotExecutionError(
            "S1-EA6 release changed before execution"
        )
    contract = prepare_e1_refined_chain_one_shot_contract(
        report_directory, upstream_report_path
    )
    binding = prepare_e1_refined_chain_canonical_producer(
        report_directory, upstream_report_path
    )
    target = Path(release.report_path)
    attempt = Path(release.attempt_path)
    lock = Path(release.lock_path)
    if (target, attempt, lock) != (
        Path(contract.report_path),
        Path(contract.attempt_path),
        Path(contract.lock_path),
    ):
        raise E1CanonicalRefinedChainOneShotExecutionError(
            "S1-EA6 target paths changed before execution"
        )
    execution_id = contract.execution_id
    _exclusive_marker(
        lock,
        {"execution_id": execution_id, "release_digest": release.digest()},
    )
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": execution_id,
                "release_digest": release.digest(),
                "canonical": True,
                "automatic_retry_permitted": False,
            },
        )
        attempt_created = True
        result = produce_e1_canonical_refined_chain_result(binding)
        if not isinstance(result, E1RefinedChainExecutionResult):
            raise E1CanonicalRefinedChainOneShotExecutionError(
                "S1-EA6 producer returned an invalid result"
            )
        report, result_digest = _report_value(contract, result)
        encoded = _atomic_publish(target, report)
        attempt.unlink()
        return E1CanonicalOneShotReceipt(
            execution_id=execution_id,
            report_path=str(target),
            report_sha256=hashlib.sha256(encoded).hexdigest(),
            result_sha256=result_digest,
            release_digest=release.digest(),
            technical_decision=result.technical_decision,
            atomic_publish_complete=True,
            canonical=True,
            exactly_once=True,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
