"""Private S1-EB5 r2/r4/r8 result and preregistered decision core."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math

from .e1_confirmation_chain_contract import (
    E1ConfirmationChainContract,
    S1_EB4_FORMATION_ARMS,
    S1_EB4_METRICS,
    S1_EB4_PROBE_ARMS,
)
from .e1_refined_confirmation_contract import (
    S1_EB_DECISIONS,
    S1_EB_REFINEMENTS,
)
from .e1_refined_world_formation_contract import S1_DS_REQUIRED_CONTROLS


class E1ConfirmationResultCoreError(ValueError):
    """Raised when S1-EB5 evidence or its decision is inconsistent."""


S1_EB4_CONTRACT_DIGEST = (
    "acf1136fa9142747729a78dda719bd36086ce2eed9e015dbfbdb58d8302fa650"
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


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _nonnegative(value: object, role: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise E1ConfirmationResultCoreError(f"{role} must be numeric")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise E1ConfirmationResultCoreError(
            f"{role} must be finite and non-negative"
        )
    return result


@dataclass(frozen=True, slots=True)
class E1ConfirmationRefinementResult:
    refinement_id: str
    factor: int
    formation_state_digests: tuple[tuple[str, str], ...]
    probe_field_digests: tuple[tuple[str, str], ...]
    d_state: float
    d_total_binding: float
    d_probe_s: float
    d_probe_h: float

    def __post_init__(self) -> None:
        if (self.refinement_id, self.factor) not in S1_EB_REFINEMENTS:
            raise E1ConfirmationResultCoreError(
                "S1-EB5 refinement identity changed"
            )
        if tuple(role for role, _ in self.formation_state_digests) != (
            S1_EB4_FORMATION_ARMS
        ):
            raise E1ConfirmationResultCoreError(
                "S1-EB5 formation state inventory is incomplete"
            )
        if tuple(role for role, _ in self.probe_field_digests) != (
            S1_EB4_PROBE_ARMS
        ):
            raise E1ConfirmationResultCoreError(
                "S1-EB5 probe field inventory is incomplete"
            )
        if any(
            not _valid_digest(value)
            for _, value in self.formation_state_digests
        ) or any(
            not _valid_digest(value) for _, value in self.probe_field_digests
        ):
            raise E1ConfirmationResultCoreError(
                "S1-EB5 arm digest is invalid"
            )
        for role in ("d_state", "d_total_binding", "d_probe_s", "d_probe_h"):
            _nonnegative(getattr(self, role), role)

    def digest(self) -> str:
        return _digest(asdict(self))


def _expected_decision(
    refinements: tuple[E1ConfirmationRefinementResult, ...],
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
        return "NO_CONFIRMED_REFINED_EFFECT"
    fine = refinements[-1]
    state_converges = (
        metrics["state_refinement_r4_r8"]
        <= metrics["state_refinement_r2_r4"]
    )
    probe_converges = (
        metrics["probe_refinement_r4_r8"]
        <= metrics["probe_refinement_r2_r4"]
    )
    state_clear = fine.d_state > (
        8.0 * metrics["state_refinement_r4_r8"]
    )
    probe_s_clear = fine.d_probe_s > (
        8.0 * metrics["probe_refinement_r4_r8"]
    )
    probe_h_clear = fine.d_probe_h > (
        8.0 * metrics["probe_refinement_r4_r8"]
    )
    if (
        state_converges
        and probe_converges
        and state_clear
        and probe_s_clear
        and probe_h_clear
    ):
        return "CONFIRMED_REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT"
    return "NUMERICALLY_UNDECIDABLE"


@dataclass(frozen=True, slots=True)
class E1ConfirmationChainResult:
    contract_digest: str
    refinements: tuple[E1ConfirmationRefinementResult, ...]
    metrics: tuple[tuple[str, float], ...]
    controls: tuple[tuple[str, bool], ...]
    technical_decision: str
    result_digest: str

    def __post_init__(self) -> None:
        if self.contract_digest != S1_EB4_CONTRACT_DIGEST:
            raise E1ConfirmationResultCoreError(
                "S1-EB5 contract binding changed"
            )
        refinements = tuple(self.refinements)
        if tuple(
            (item.refinement_id, item.factor) for item in refinements
        ) != S1_EB_REFINEMENTS:
            raise E1ConfirmationResultCoreError(
                "S1-EB5 results require ordered r2, r4, and r8"
            )
        metrics = tuple(self.metrics)
        if tuple(role for role, _ in metrics) != S1_EB4_METRICS:
            raise E1ConfirmationResultCoreError(
                "S1-EB5 metrics are incomplete"
            )
        metric_values = {
            role: _nonnegative(value, role) for role, value in metrics
        }
        controls = tuple(self.controls)
        if tuple(role for role, _ in controls) != S1_DS_REQUIRED_CONTROLS:
            raise E1ConfirmationResultCoreError(
                "S1-EB5 controls are incomplete"
            )
        if any(not isinstance(value, bool) for _, value in controls):
            raise E1ConfirmationResultCoreError(
                "S1-EB5 controls must be boolean"
            )
        fine = refinements[-1]
        if (
            metric_values["d_state"] != fine.d_state
            or metric_values["d_total_binding"] != fine.d_total_binding
            or metric_values["d_probe_s"] != fine.d_probe_s
            or metric_values["d_probe_h"] != fine.d_probe_h
        ):
            raise E1ConfirmationResultCoreError(
                "S1-EB5 fine metrics do not match r8"
            )
        control_values = dict(controls)
        exact_residuals = (
            ("ab_identity_replicates_are_bit_exact", "identity_residual"),
            (
                "formation_ablation_remains_neutral",
                "formation_ablation_residual",
            ),
            (
                "probe_ablation_equals_p0_bit_exact",
                "probe_ablation_residual",
            ),
            (
                "active_probe_equals_matching_fixed_adapter_bit_exact",
                "fixed_adapter_residual",
            ),
        )
        if any(
            control_values[control] is True and metric_values[metric] != 0.0
            for control, metric in exact_residuals
        ):
            raise E1ConfirmationResultCoreError(
                "S1-EB5 exact control contradicts its residual"
            )
        if metric_values["resource_budget_error"] > 1e-12:
            raise E1ConfirmationResultCoreError(
                "S1-EB5 resource budget error exceeds tolerance"
            )
        expected = _expected_decision(refinements, metric_values, controls)
        if (
            self.technical_decision not in S1_EB_DECISIONS
            or self.technical_decision != expected
        ):
            raise E1ConfirmationResultCoreError(
                "S1-EB5 decision does not follow preregistered rules"
            )
        payload = {
            "contract_digest": self.contract_digest,
            "refinements": tuple(asdict(item) for item in refinements),
            "metrics": metrics,
            "controls": controls,
            "technical_decision": self.technical_decision,
        }
        if self.result_digest != _digest(payload):
            raise E1ConfirmationResultCoreError(
                "S1-EB5 result digest does not match its payload"
            )
        object.__setattr__(self, "refinements", refinements)
        object.__setattr__(self, "metrics", metrics)
        object.__setattr__(self, "controls", controls)


def build_e1_confirmation_chain_result(
    contract: E1ConfirmationChainContract,
    refinements: tuple[E1ConfirmationRefinementResult, ...],
    metrics: tuple[tuple[str, float], ...],
    controls: tuple[tuple[str, bool], ...],
) -> E1ConfirmationChainResult:
    """Evaluate supplied result evidence without running or persisting it."""

    if not isinstance(contract, E1ConfirmationChainContract) or (
        contract.digest() != S1_EB4_CONTRACT_DIGEST
    ):
        raise E1ConfirmationResultCoreError(
            "S1-EB5 requires the current S1-EB4 contract"
        )
    refinements_in = tuple(refinements)
    metrics_in = tuple(metrics)
    controls_in = tuple(controls)
    if tuple(
        (item.refinement_id, item.factor) for item in refinements_in
    ) != S1_EB_REFINEMENTS:
        raise E1ConfirmationResultCoreError(
            "S1-EB5 results require ordered r2, r4, and r8"
        )
    if tuple(role for role, _ in metrics_in) != S1_EB4_METRICS:
        raise E1ConfirmationResultCoreError(
            "S1-EB5 metrics are incomplete"
        )
    if tuple(role for role, _ in controls_in) != S1_DS_REQUIRED_CONTROLS:
        raise E1ConfirmationResultCoreError(
            "S1-EB5 controls are incomplete"
        )
    if any(not isinstance(value, bool) for _, value in controls_in):
        raise E1ConfirmationResultCoreError(
            "S1-EB5 controls must be boolean"
        )
    metric_values = {
        role: _nonnegative(value, role) for role, value in metrics_in
    }
    decision = _expected_decision(
        refinements_in,
        metric_values,
        controls_in,
    )
    payload = {
        "contract_digest": contract.digest(),
        "refinements": tuple(asdict(item) for item in refinements_in),
        "metrics": metrics_in,
        "controls": controls_in,
        "technical_decision": decision,
    }
    return E1ConfirmationChainResult(
        contract_digest=contract.digest(),
        refinements=refinements_in,
        metrics=metrics_in,
        controls=controls_in,
        technical_decision=decision,
        result_digest=_digest(payload),
    )
