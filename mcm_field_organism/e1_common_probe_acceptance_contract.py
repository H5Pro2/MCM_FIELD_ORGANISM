"""S1-EC46 static numerical acceptance contract for the EC45 common probe."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .e1_common_probe_identifiability_contract import (
    E1CommonProbeIdentifiabilityContract,
    build_e1_common_probe_identifiability_contract,
)
from .e1_confirmation_full_probe_result_audit import S1_EC24_SIGNAL_MARGIN
from .e1_e3_probe_run import E1_E3_PROBE_ABSOLUTE_TOLERANCE
from .e1_e4_execution import E1_E4_REFINEMENT_LIMIT
from .e1_refined_formation_runner import _digest


class E1CommonProbeAcceptanceContractError(ValueError):
    """Raised when EC46 changes its preregistered numerical boundary."""


S1_EC46_CONTRACT_ID = "e1.common-probe-acceptance.s1ec46.v1"
S1_EC46_EC45_CONTRACT_DIGEST = (
    "6087bc99a8331671c077da4fc7b76959c7608611bbbda8c4815957e89c78ed00"
)
S1_EC46_DECISIONS = (
    "INVALID_COMMON_PROBE_CONTROLS",
    "NO_MEASURABLE_COMMON_PROBE_DIFFERENCE",
    "NUMERICALLY_UNDECIDABLE_COMMON_PROBE_DIFFERENCE",
    "NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE",
)


def _nonnegative(value: float, role: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) < 0.0
    ):
        raise E1CommonProbeAcceptanceContractError(
            f"S1-EC46 {role} must be finite and nonnegative"
        )
    return float(value)


def decide_common_probe_evidence(
    *,
    active_s: float,
    active_h: float,
    coarse_s: float,
    coarse_h: float,
    fine_s: float,
    fine_h: float,
    p0_reset_s: float,
    p0_reset_h: float,
    feedback_ablation_s: float,
    feedback_ablation_h: float,
    formation_ablation_s: float,
    formation_ablation_h: float,
) -> str:
    """Apply only inherited EC24/E3/E4 numerical rules."""

    values = {
        name: _nonnegative(value, name)
        for name, value in locals().items()
    }
    tolerance = E1_E3_PROBE_ABSOLUTE_TOLERANCE
    controls = (
        values["p0_reset_s"],
        values["p0_reset_h"],
        values["feedback_ablation_s"],
        values["feedback_ablation_h"],
        values["formation_ablation_s"],
        values["formation_ablation_h"],
    )
    if any(value > tolerance for value in controls):
        return "INVALID_COMMON_PROBE_CONTROLS"
    if values["active_s"] <= tolerance and values["active_h"] <= tolerance:
        return "NO_MEASURABLE_COMMON_PROBE_DIFFERENCE"

    converged = (
        values["fine_s"] <= values["coarse_s"]
        and values["fine_h"] <= values["coarse_h"]
        and values["fine_s"] / max(values["active_s"], tolerance)
        <= E1_E4_REFINEMENT_LIMIT
        and values["fine_h"] / max(values["active_h"], tolerance)
        <= E1_E4_REFINEMENT_LIMIT
    )
    clear = (
        values["active_s"]
        > max(tolerance, S1_EC24_SIGNAL_MARGIN * values["fine_s"])
        and values["active_h"]
        > max(tolerance, S1_EC24_SIGNAL_MARGIN * values["fine_h"])
    )
    if converged and clear:
        return "NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE"
    return "NUMERICALLY_UNDECIDABLE_COMMON_PROBE_DIFFERENCE"


@dataclass(frozen=True, slots=True)
class E1CommonProbeAcceptanceContract:
    contract_id: str
    source_identifiability_digest: str
    source_absolute_tolerance_role: str
    source_signal_margin_role: str
    source_relative_refinement_role: str
    absolute_control_tolerance: float
    strict_signal_margin: float
    relative_refinement_limit: float
    metric_components: tuple[str, ...]
    null_controls: tuple[str, ...]
    refinement_levels: tuple[str, ...]
    decision_order: tuple[str, ...]
    signal_rule: str
    convergence_rule: str
    posthoc_change_permitted: bool
    common_probe_implementation_permitted: bool
    field_execution_permitted: bool
    persistence_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != S1_EC46_CONTRACT_ID
            or self.source_identifiability_digest
            != S1_EC46_EC45_CONTRACT_DIGEST
            or self.source_absolute_tolerance_role
            != "S1-E3 common-probe absolute tolerance"
            or self.source_signal_margin_role
            != "S1-EC24 strict eight-times-fine-residual margin"
            or self.source_relative_refinement_role
            != "S1-E4 relative refinement limit"
            or self.absolute_control_tolerance != 1e-12
            or self.absolute_control_tolerance
            != E1_E3_PROBE_ABSOLUTE_TOLERANCE
            or self.strict_signal_margin != 8.0
            or self.strict_signal_margin != S1_EC24_SIGNAL_MARGIN
            or self.relative_refinement_limit != 0.01
            or self.relative_refinement_limit != E1_E4_REFINEMENT_LIMIT
            or self.metric_components != ("activation", "afterimage")
            or self.null_controls != (
                "p0-reset-order",
                "e1-probe-feedback-ablated-order",
                "e1-formation-ablated-order",
            )
            or self.refinement_levels != ("r2", "r4", "r8")
            or self.decision_order != S1_EC46_DECISIONS
            or self.signal_rule
            != "r8>max(1e-12,8*r4-r8-residual):strict:both-components"
            or self.convergence_rule
            != "fine<=coarse-and-fine/max(r8,1e-12)<=0.01:both-components"
            or self.posthoc_change_permitted is not False
            or self.common_probe_implementation_permitted is not True
            or any(value is not False for value in (
                self.field_execution_permitted,
                self.persistence_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision != "ACCEPTANCE_BOUND_REGISTERED_IMPLEMENTATION_MISSING"
            or not self.reason
        ):
            raise E1CommonProbeAcceptanceContractError(
                "S1-EC46 changed or crossed its static acceptance scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if self.contract_digest != _digest(payload):
            raise E1CommonProbeAcceptanceContractError(
                "S1-EC46 contract digest changed"
            )


def build_e1_common_probe_acceptance_contract(
    identifiability: E1CommonProbeIdentifiabilityContract | None = None,
) -> E1CommonProbeAcceptanceContract:
    """Bind inherited tolerances without executing or observing a probe."""

    source = identifiability or build_e1_common_probe_identifiability_contract()
    if not isinstance(source, E1CommonProbeIdentifiabilityContract):
        raise E1CommonProbeAcceptanceContractError(
            "S1-EC46 requires the typed EC45 contract"
        )
    source.__post_init__()
    if source.contract_digest != S1_EC46_EC45_CONTRACT_DIGEST:
        raise E1CommonProbeAcceptanceContractError(
            "S1-EC46 EC45 binding changed"
        )
    values = {
        "contract_id": S1_EC46_CONTRACT_ID,
        "source_identifiability_digest": source.contract_digest,
        "source_absolute_tolerance_role": (
            "S1-E3 common-probe absolute tolerance"
        ),
        "source_signal_margin_role": (
            "S1-EC24 strict eight-times-fine-residual margin"
        ),
        "source_relative_refinement_role": "S1-E4 relative refinement limit",
        "absolute_control_tolerance": E1_E3_PROBE_ABSOLUTE_TOLERANCE,
        "strict_signal_margin": S1_EC24_SIGNAL_MARGIN,
        "relative_refinement_limit": E1_E4_REFINEMENT_LIMIT,
        "metric_components": ("activation", "afterimage"),
        "null_controls": (
            "p0-reset-order",
            "e1-probe-feedback-ablated-order",
            "e1-formation-ablated-order",
        ),
        "refinement_levels": ("r2", "r4", "r8"),
        "decision_order": S1_EC46_DECISIONS,
        "signal_rule": (
            "r8>max(1e-12,8*r4-r8-residual):strict:both-components"
        ),
        "convergence_rule": (
            "fine<=coarse-and-fine/max(r8,1e-12)<=0.01:both-components"
        ),
        "posthoc_change_permitted": False,
        "common_probe_implementation_permitted": True,
        "field_execution_permitted": False,
        "persistence_permitted": False,
        "memory_claim_permitted": False,
        "decision": "ACCEPTANCE_BOUND_REGISTERED_IMPLEMENTATION_MISSING",
        "reason": (
            "inherited-absolute-margin-and-refinement-rules-registered;"
            "common-probe-runner-not-yet-implemented-or-released"
        ),
    }
    return E1CommonProbeAcceptanceContract(
        **values,
        contract_digest=_digest(values),
    )
