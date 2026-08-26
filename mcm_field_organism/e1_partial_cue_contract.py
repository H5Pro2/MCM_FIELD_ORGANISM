"""Private S1-CO static contract for an E1 partial-cue interaction check."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math


class E1PartialCueContractError(ValueError):
    """Raised when the S1-CO preregistration is changed or incomplete."""


S1_CO_HISTORY_ARMS = ("left-g4", "right-g4", "neutral")
S1_CO_MODEL_ARMS = ("e1", "p0", "b1-static-h8")
S1_CO_DECISIONS = (
    "INVALID_S1_CO_RUN",
    "NO_MEASURABLE_PARTIAL_CUE_EFFECT",
    "PARTIAL_CUE_EXPLAINED_BY_P0_OR_STATIC_GAIN",
    "HISTORY_SPECIFIC_PARTIAL_CUE_EFFECT",
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


def _energy(values: tuple[float, ...]) -> float:
    return math.fsum(value * value for value in values)


@dataclass(frozen=True, slots=True)
class E1PartialCueContract:
    """Complete static world, controls and decision order for S1-CO."""

    contract_id: str
    history_arms: tuple[str, ...]
    model_arms: tuple[str, ...]
    left_history_contact: tuple[float, float, float]
    right_history_contact: tuple[float, float, float]
    history_repetitions: int
    history_interval_seconds: float
    gap_seconds: float
    left_full_cue: tuple[float, float, float]
    right_full_cue: tuple[float, float, float]
    left_partial_cue: tuple[float, float, float]
    right_partial_cue: tuple[float, float, float]
    cue_interval_seconds: float
    ticks_per_second: float
    observable_roles: tuple[str, ...]
    metric_roles: tuple[str, ...]
    decision_order: tuple[str, ...]
    absolute_tolerance: float
    relative_refinement_limit: float
    execution_permitted: bool
    executed: bool

    def __post_init__(self) -> None:
        if self.contract_id != "s1-co.e1-partial-cue.v1":
            raise E1PartialCueContractError("partial-cue contract identity changed")
        if self.history_arms != S1_CO_HISTORY_ARMS:
            raise E1PartialCueContractError("partial-cue history arms changed")
        if self.model_arms != S1_CO_MODEL_ARMS:
            raise E1PartialCueContractError("partial-cue model arms changed")
        if (
            self.left_history_contact != (1.0, 0.0, 0.0)
            or self.right_history_contact != (0.0, 0.0, 1.0)
            or self.left_full_cue != self.left_history_contact
            or self.right_full_cue != self.right_history_contact
        ):
            raise E1PartialCueContractError("full contacts must retain mirrored H8 values")
        if (
            self.left_partial_cue != (0.25, 0.0, 0.0)
            or self.right_partial_cue != (0.0, 0.0, 0.25)
            or _energy(self.left_partial_cue) != _energy(self.right_partial_cue)
            or not _energy(self.left_partial_cue) < _energy(self.left_full_cue)
        ):
            raise E1PartialCueContractError("partial cues must be mirrored and weaker")
        if (
            self.history_repetitions != 8
            or self.history_interval_seconds != 1.0
            or self.gap_seconds != 4.0
            or self.cue_interval_seconds != 1.0
            or self.ticks_per_second != 20.0
        ):
            raise E1PartialCueContractError("partial-cue timing changed")
        if self.observable_roles != (
            "signed-delta-s",
            "signed-delta-h",
            "left-right-mirror",
        ):
            raise E1PartialCueContractError("partial-cue observables changed")
        if self.metric_roles != (
            "partial-history-cue-interaction-linf",
            "full-history-cue-interaction-linf",
            "partial-full-direction-dot",
            "p0-interaction-linf",
            "b1-static-interaction-linf",
            "crossed-history-linf",
            "mirror-error-linf",
            "relative-refinement-linf",
        ):
            raise E1PartialCueContractError("partial-cue metrics changed")
        if self.decision_order != S1_CO_DECISIONS:
            raise E1PartialCueContractError("partial-cue decision order changed")
        if self.absolute_tolerance != 1e-12 or self.relative_refinement_limit != 0.01:
            raise E1PartialCueContractError("partial-cue tolerances changed")
        if self.execution_permitted is not False or self.executed is not False:
            raise E1PartialCueContractError("S1-CO must remain static and unexecuted")

    def digest(self) -> str:
        return _digest(
            {
                name: getattr(self, name)
                for name in self.__dataclass_fields__
            }
        )


def build_e1_partial_cue_contract() -> E1PartialCueContract:
    """Return the fixed S1-CO preregistration without running any field."""

    return E1PartialCueContract(
        contract_id="s1-co.e1-partial-cue.v1",
        history_arms=S1_CO_HISTORY_ARMS,
        model_arms=S1_CO_MODEL_ARMS,
        left_history_contact=(1.0, 0.0, 0.0),
        right_history_contact=(0.0, 0.0, 1.0),
        history_repetitions=8,
        history_interval_seconds=1.0,
        gap_seconds=4.0,
        left_full_cue=(1.0, 0.0, 0.0),
        right_full_cue=(0.0, 0.0, 1.0),
        left_partial_cue=(0.25, 0.0, 0.0),
        right_partial_cue=(0.0, 0.0, 0.25),
        cue_interval_seconds=1.0,
        ticks_per_second=20.0,
        observable_roles=("signed-delta-s", "signed-delta-h", "left-right-mirror"),
        metric_roles=(
            "partial-history-cue-interaction-linf",
            "full-history-cue-interaction-linf",
            "partial-full-direction-dot",
            "p0-interaction-linf",
            "b1-static-interaction-linf",
            "crossed-history-linf",
            "mirror-error-linf",
            "relative-refinement-linf",
        ),
        decision_order=S1_CO_DECISIONS,
        absolute_tolerance=1e-12,
        relative_refinement_limit=0.01,
        execution_permitted=False,
        executed=False,
    )
