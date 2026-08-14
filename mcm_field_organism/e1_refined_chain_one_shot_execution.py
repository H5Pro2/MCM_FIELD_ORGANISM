"""Private S1-DX result validation and synthetic exactly-once publication."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Callable

from .e1_refined_chain_one_shot_contract import (
    E1RefinedChainOneShotContract,
    S1_DW_REPORT_FIELDS,
)
from .e1_refined_world_formation_contract import (
    S1_DS_DECISIONS,
    S1_DS_METRICS,
    S1_DS_REQUIRED_CONTROLS,
    S1_DS_REFINEMENTS,
)


class E1RefinedChainOneShotExecutionError(RuntimeError):
    """Raised when an S1-DX synthetic attempt cannot complete safely."""


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
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _nonnegative(value: object, role: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise E1RefinedChainOneShotExecutionError(
            f"{role} must be numeric"
        )
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise E1RefinedChainOneShotExecutionError(
            f"{role} must be finite and non-negative"
        )
    return result


@dataclass(frozen=True, slots=True)
class E1RefinedChainRefinementResult:
    refinement_id: str
    factor: int
    formation_state_digests: tuple[tuple[str, str], ...]
    probe_field_digests: tuple[tuple[str, str], ...]
    d_state: float
    d_total_binding: float
    d_probe_s: float
    d_probe_h: float

    def __post_init__(self) -> None:
        if (self.refinement_id, self.factor) not in S1_DS_REFINEMENTS:
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain result refinement changed"
            )
        if tuple(role for role, _ in self.formation_state_digests) != (
            "ab",
            "ba",
            "ab_identity",
            "ab_formation_ablated",
            "ba_formation_ablated",
        ):
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain formation state inventory is incomplete"
            )
        if tuple(role for role, _ in self.probe_field_digests) != (
            "p0",
            "ab_active",
            "ba_active",
            "ab_probe_ablated",
            "ba_probe_ablated",
            "ab_fixed",
            "ba_fixed",
        ):
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain probe field inventory is incomplete"
            )
        if any(
            not _valid_digest(value)
            for _, value in self.formation_state_digests
        ) or any(
            not _valid_digest(value) for _, value in self.probe_field_digests
        ):
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain arm digest is invalid"
            )
        for role in ("d_state", "d_total_binding", "d_probe_s", "d_probe_h"):
            _nonnegative(getattr(self, role), role)

    def digest(self) -> str:
        return _digest(asdict(self))


def _expected_decision(
    refinements: tuple[E1RefinedChainRefinementResult, ...],
    metrics: dict[str, float],
    controls: tuple[tuple[str, bool], ...],
) -> str:
    if any(value is not True for _, value in controls):
        return "TECHNICALLY_INVALID"
    if all(
        item.d_state == 0.0
        and item.d_probe_s == 0.0
        and item.d_probe_h == 0.0
        for item in refinements
    ):
        return "NO_REFINED_WORLD_FORMATION_EFFECT"
    fine = refinements[-1]
    state_converges = (
        metrics["state_refinement_r2_r4"]
        <= metrics["state_refinement_r1_r2"]
    )
    probe_converges = (
        metrics["probe_refinement_r2_r4"]
        <= metrics["probe_refinement_r1_r2"]
    )
    state_clear = fine.d_state > (
        8.0 * metrics["state_refinement_r2_r4"]
    )
    probe_s_clear = fine.d_probe_s > (
        8.0 * metrics["probe_refinement_r2_r4"]
    )
    probe_h_clear = fine.d_probe_h > (
        8.0 * metrics["probe_refinement_r2_r4"]
    )
    if state_converges and probe_converges and state_clear and probe_s_clear and probe_h_clear:
        return "REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT"
    return "NUMERICALLY_UNDECIDABLE"


@dataclass(frozen=True, slots=True)
class E1RefinedChainExecutionResult:
    refinements: tuple[E1RefinedChainRefinementResult, ...]
    metrics: tuple[tuple[str, float], ...]
    controls: tuple[tuple[str, bool], ...]
    technical_decision: str

    def __post_init__(self) -> None:
        refinements = tuple(self.refinements)
        if tuple(
            (item.refinement_id, item.factor) for item in refinements
        ) != S1_DS_REFINEMENTS:
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain results require ordered r1, r2, and r4"
            )
        if tuple(role for role, _ in self.metrics) != S1_DS_METRICS:
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain metrics are incomplete"
            )
        metric_values = {
            role: _nonnegative(value, role) for role, value in self.metrics
        }
        if tuple(role for role, _ in self.controls) != S1_DS_REQUIRED_CONTROLS:
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain controls are incomplete"
            )
        if any(not isinstance(value, bool) for _, value in self.controls):
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain controls must be boolean"
            )
        fine = refinements[-1]
        if (
            metric_values["d_state"] != fine.d_state
            or metric_values["d_total_binding"] != fine.d_total_binding
            or metric_values["d_probe_s"] != fine.d_probe_s
            or metric_values["d_probe_h"] != fine.d_probe_h
        ):
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain fine metrics do not match r4"
            )
        controls = dict(self.controls)
        exact_residuals = (
            (
                "ab_identity_replicates_are_bit_exact",
                "identity_residual",
            ),
            ("formation_ablation_remains_neutral", "formation_ablation_residual"),
            ("probe_ablation_equals_p0_bit_exact", "probe_ablation_residual"),
            (
                "active_probe_equals_matching_fixed_adapter_bit_exact",
                "fixed_adapter_residual",
            ),
        )
        if any(
            controls[control] is True and metric_values[metric] != 0.0
            for control, metric in exact_residuals
        ):
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain exact control contradicts its residual"
            )
        if metric_values["resource_budget_error"] > 1e-12:
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain resource budget error exceeds tolerance"
            )
        expected = _expected_decision(refinements, metric_values, self.controls)
        if (
            self.technical_decision not in S1_DS_DECISIONS
            or self.technical_decision != expected
        ):
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain decision does not follow preregistered rules"
            )
        object.__setattr__(self, "refinements", refinements)


E1RefinedChainResultProducer = Callable[[], E1RefinedChainExecutionResult]


@dataclass(frozen=True, slots=True)
class E1RefinedChainOneShotReceipt:
    execution_id: str
    report_path: str
    report_sha256: str
    result_sha256: str
    one_shot_contract_digest: str
    technical_decision: str
    atomic_publish_complete: bool
    synthetic_only: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != "e1.refined-formation-transfer.s1dx.synthetic.v1"
            or not _valid_digest(self.report_sha256)
            or not _valid_digest(self.result_sha256)
            or not _valid_digest(self.one_shot_contract_digest)
            or self.technical_decision not in S1_DS_DECISIONS
            or self.atomic_publish_complete is not True
            or self.synthetic_only is not True
        ):
            raise E1RefinedChainOneShotExecutionError(
                "invalid refined-chain synthetic receipt"
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
        raise E1RefinedChainOneShotExecutionError(
            f"refined-chain synthetic marker already exists: {path.name}"
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
        prefix=target.name + ".tmp.", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if json.loads(temporary.read_text(encoding="ascii")) != json.loads(encoded):
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain synthetic temporary report reread failed"
            )
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain synthetic report already exists"
            ) from exc
        if target.read_bytes() != encoded:
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain synthetic published report differs"
            )
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


def execute_synthetic_e1_refined_chain_one_shot(
    contract: E1RefinedChainOneShotContract,
    producer: E1RefinedChainResultProducer,
    synthetic_directory: Path,
) -> E1RefinedChainOneShotReceipt:
    """Exercise S1-DX persistence outside the registered project targets."""

    if not isinstance(contract, E1RefinedChainOneShotContract):
        raise E1RefinedChainOneShotExecutionError(
            "refined-chain synthetic execution requires the S1-DW contract"
        )
    try:
        contract.__post_init__()
    except ValueError as exc:
        raise E1RefinedChainOneShotExecutionError(
            "refined-chain S1-DW contract is no longer current"
        ) from exc
    if contract.execution_permitted is not False:
        raise E1RefinedChainOneShotExecutionError(
            "S1-DX requires canonical execution to remain blocked"
        )
    if not callable(producer):
        raise E1RefinedChainOneShotExecutionError(
            "refined-chain synthetic producer is not callable"
        )
    directory = Path(synthetic_directory).resolve()
    if not directory.is_dir():
        raise E1RefinedChainOneShotExecutionError(
            "refined-chain synthetic directory does not exist"
        )
    if directory == Path(contract.report_path).parent.resolve():
        raise E1RefinedChainOneShotExecutionError(
            "S1-DX cannot use the registered canonical target directory"
        )
    target = directory / "e1_refined_chain_s1dx_synthetic_once_v1.json"
    attempt = directory / "e1_refined_chain_s1dx_synthetic_once_v1.attempt.json"
    lock = directory / "e1_refined_chain_s1dx_synthetic_once_v1.lock"
    if any(path.exists() for path in (target, attempt, lock)):
        raise E1RefinedChainOneShotExecutionError(
            "refined-chain synthetic one-shot path is already used"
        )
    execution_id = "e1.refined-formation-transfer.s1dx.synthetic.v1"
    _exclusive_marker(lock, {"execution_id": execution_id})
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": execution_id,
                "one_shot_contract_digest": contract.digest(),
                "synthetic_only": True,
            },
        )
        attempt_created = True
        result = producer()
        if not isinstance(result, E1RefinedChainExecutionResult):
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain synthetic producer returned an invalid result"
            )
        result_value = asdict(result)
        result_digest = _digest(result_value)
        report = {
            "execution_id": execution_id,
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
            raise E1RefinedChainOneShotExecutionError(
                "refined-chain synthetic report fields changed"
            )
        encoded = _atomic_publish(target, report)
        attempt.unlink()
        return E1RefinedChainOneShotReceipt(
            execution_id=execution_id,
            report_path=str(target),
            report_sha256=hashlib.sha256(encoded).hexdigest(),
            result_sha256=result_digest,
            one_shot_contract_digest=contract.digest(),
            technical_decision=result.technical_decision,
            atomic_publish_complete=True,
            synthetic_only=True,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
