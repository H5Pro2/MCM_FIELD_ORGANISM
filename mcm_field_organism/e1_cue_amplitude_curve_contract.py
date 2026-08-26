"""Private S1-CU preregistration for the E1 cue-amplitude curve."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math


class E1CueAmplitudeCurveContractError(ValueError):
    """Raised when the S1-CU amplitude-curve contract is changed."""


S1_CU_AMPLITUDES = (0.125, 0.25, 0.5, 1.0)
S1_CU_MODELS = ("e1", "p0", "b1-static-h8")
S1_CU_HISTORIES = ("left-g4", "right-g4", "neutral")
S1_CU_SIDES = ("left", "right")
S1_CU_DECISIONS = (
    "INVALID_S1_CU_RUN",
    "NO_MEASURABLE_HISTORY_INTERACTION",
    "AMPLITUDE_CURVE_EXPLAINED_BY_LINEAR_SCALING",
    "NONLINEAR_HISTORY_INTERACTION_RESIDUAL",
)
S1_CT_REPORT_SHA256 = (
    "ee569666e63ab7f4821f5778c3fb80d62a02f47bf3269c871b8e05bf1a450d26"
)
S1_CT_FULL_INTERACTION_LINF = 0.0021516247701185154


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
class E1CueAmplitudeCurveContract:
    """Fixed worlds, null prediction and decisions for S1-CU."""

    contract_id: str
    amplitudes: tuple[float, ...]
    model_arms: tuple[str, ...]
    history_arms: tuple[str, ...]
    cue_sides: tuple[str, ...]
    history_repetitions: int
    history_interval_seconds: float
    gap_seconds: float
    cue_interval_seconds: float
    ticks_per_second: float
    linear_null_model: str
    s1ct_report_sha256: str
    s1ct_full_interaction_linf: float
    metric_roles: tuple[str, ...]
    decision_order: tuple[str, ...]
    absolute_tolerance: float
    relative_refinement_limit: float
    relative_linearity_limit: float
    execution_permitted: bool
    executed: bool

    def __post_init__(self) -> None:
        if self.contract_id != "s1-cu.e1-cue-amplitude-curve.v1":
            raise E1CueAmplitudeCurveContractError("amplitude contract identity changed")
        if self.amplitudes != S1_CU_AMPLITUDES or any(
            not math.isfinite(value) or value <= 0.0 or value > 1.0
            for value in self.amplitudes
        ):
            raise E1CueAmplitudeCurveContractError("cue amplitudes changed")
        if tuple(sorted(self.amplitudes)) != self.amplitudes:
            raise E1CueAmplitudeCurveContractError("cue amplitudes must be ordered")
        if (
            self.model_arms != S1_CU_MODELS
            or self.history_arms != S1_CU_HISTORIES
            or self.cue_sides != S1_CU_SIDES
        ):
            raise E1CueAmplitudeCurveContractError("amplitude curve arms changed")
        if (
            self.history_repetitions != 8
            or self.history_interval_seconds != 1.0
            or self.gap_seconds != 4.0
            or self.cue_interval_seconds != 1.0
            or self.ticks_per_second != 20.0
        ):
            raise E1CueAmplitudeCurveContractError("amplitude curve timing changed")
        if self.linear_null_model != "interaction(q)=q*interaction(1.0)":
            raise E1CueAmplitudeCurveContractError("linear null model changed")
        if (
            self.s1ct_report_sha256 != S1_CT_REPORT_SHA256
            or self.s1ct_full_interaction_linf != S1_CT_FULL_INTERACTION_LINF
        ):
            raise E1CueAmplitudeCurveContractError("S1-CT anchor changed")
        if self.metric_roles != (
            "interaction-linf-by-amplitude",
            "componentwise-linear-residual-by-amplitude",
            "maximum-relative-linear-residual",
            "p0-interaction-floor",
            "b1-static-interaction-floor",
            "mirror-error-linf",
            "relative-refinement-linf",
            "s1ct-anchor-error-linf",
        ):
            raise E1CueAmplitudeCurveContractError("amplitude metrics changed")
        if self.decision_order != S1_CU_DECISIONS:
            raise E1CueAmplitudeCurveContractError("amplitude decisions changed")
        if (
            self.absolute_tolerance != 1e-12
            or self.relative_refinement_limit != 0.01
            or self.relative_linearity_limit != 0.05
        ):
            raise E1CueAmplitudeCurveContractError("amplitude tolerances changed")
        if self.execution_permitted is not False or self.executed is not False:
            raise E1CueAmplitudeCurveContractError("S1-CU must remain unexecuted")

    def cue(self, side: str, amplitude: float) -> tuple[float, float, float]:
        if side not in self.cue_sides or amplitude not in self.amplitudes:
            raise E1CueAmplitudeCurveContractError("unknown amplitude cue")
        return (amplitude, 0.0, 0.0) if side == "left" else (0.0, 0.0, amplitude)

    def digest(self) -> str:
        return _digest(
            {
                name: getattr(self, name)
                for name in self.__dataclass_fields__
            }
        )


def build_e1_cue_amplitude_curve_contract() -> E1CueAmplitudeCurveContract:
    """Return the fixed S1-CU contract without executing any cue."""

    return E1CueAmplitudeCurveContract(
        contract_id="s1-cu.e1-cue-amplitude-curve.v1",
        amplitudes=S1_CU_AMPLITUDES,
        model_arms=S1_CU_MODELS,
        history_arms=S1_CU_HISTORIES,
        cue_sides=S1_CU_SIDES,
        history_repetitions=8,
        history_interval_seconds=1.0,
        gap_seconds=4.0,
        cue_interval_seconds=1.0,
        ticks_per_second=20.0,
        linear_null_model="interaction(q)=q*interaction(1.0)",
        s1ct_report_sha256=S1_CT_REPORT_SHA256,
        s1ct_full_interaction_linf=S1_CT_FULL_INTERACTION_LINF,
        metric_roles=(
            "interaction-linf-by-amplitude",
            "componentwise-linear-residual-by-amplitude",
            "maximum-relative-linear-residual",
            "p0-interaction-floor",
            "b1-static-interaction-floor",
            "mirror-error-linf",
            "relative-refinement-linf",
            "s1ct-anchor-error-linf",
        ),
        decision_order=S1_CU_DECISIONS,
        absolute_tolerance=1e-12,
        relative_refinement_limit=0.01,
        relative_linearity_limit=0.05,
        execution_permitted=False,
        executed=False,
    )
