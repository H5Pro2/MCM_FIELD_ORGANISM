"""S1-HK symmetric DTS-1 edge-participation observable without dynamics."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math


class DTS1S1HKEdgeParticipationContractError(ValueError):
    """Raised when the S1-HK observable or its static boundary is invalid."""


S1_HK_CONTRACT_ID = "dynamic-substrate.edge-participation.s1hk.v1"
S1_HK_SOURCE_S1HJ_CONTRACT_DIGEST = (
    "f9113a6a1972cc2aa2737fdc6091a6fb4344f53899bcfd1faa5923db410a423c"
)
S1_HK_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HK_OBSERVABLE_ID = "NORMALIZED_SQUARED_FAST_FIELD_EDGE_DIFFERENCE"
S1_HK_FORMULA = "p_e=((S_i-S_j)/2)^2"
S1_HK_DOMAIN = "S_i,S_j in [-1,1]"
S1_HK_RANGE = "p_e in [0,1]"
S1_HK_NULL_CASES = (
    "equal-endpoint-fast-field-values",
    "uniform-fast-field-on-every-edge",
    "zero-fast-field-at-both-endpoints",
)
S1_HK_INVARIANCES = (
    "endpoint-exchange",
    "joint-fast-field-sign-inversion",
    "edge-identity-and-modality-independent-rule",
)
S1_HK_EXCLUSIONS = (
    "afterimage-h",
    "adapter-or-gain-value",
    "resource-role-values",
    "labels-reward-loss-or-target",
    "history-repetition-phase-or-age-counter",
    "global-normalization-ranking-or-neighbor-comparison",
    "threshold-clipping-or-case-specific-branch",
)
S1_HK_DECISION = (
    "DTS1_SYMMETRIC_LOCAL_FAST_FIELD_PARTICIPATION_BOUND_NO_TRANSFER_LAW"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _normalized_fast_field_value(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise DTS1S1HKEdgeParticipationContractError(
            f"{role} must be numeric, not boolean"
        )
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1S1HKEdgeParticipationContractError(
            f"{role} must be numeric"
        ) from exc
    if not math.isfinite(result) or result < -1.0 or result > 1.0:
        raise DTS1S1HKEdgeParticipationContractError(
            f"{role} must be finite and within [-1,1]"
        )
    return result


def compute_dts1_s1hk_edge_participation(
    first_fast_field_value: object,
    second_fast_field_value: object,
) -> float:
    """Compute only the local observable; never change resource or field state."""

    first = _normalized_fast_field_value(
        first_fast_field_value, "first_fast_field_value"
    )
    second = _normalized_fast_field_value(
        second_fast_field_value, "second_fast_field_value"
    )
    return ((first - second) / 2.0) ** 2


@dataclass(frozen=True, slots=True)
class DTS1S1HKEdgeParticipationContract:
    contract_id: str
    source_s1hj_contract_digest: str
    candidate_id: str
    observable_id: str
    formula: str
    domain: str
    range: str
    null_cases: tuple[str, ...]
    invariances: tuple[str, ...]
    excluded_inputs_and_operations: tuple[str, ...]
    same_observable_as_e1_baseline: bool
    observable_is_eligibility_not_transfer: bool
    zero_blocks_engagement_eligibility_only: bool
    turnover_and_recovery_ignore_observable: bool
    threshold_selected: bool
    transfer_amount_selected: bool
    rate_selected: bool
    time_law_selected: bool
    integrator_selected: bool
    field_backreaction_selected: bool
    runtime_implemented: bool
    functional_effect_proven: bool
    execution_permitted: bool
    field_steps_executed: int
    claims_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_HK_CONTRACT_ID
            or self.source_s1hj_contract_digest
            != S1_HK_SOURCE_S1HJ_CONTRACT_DIGEST
            or self.candidate_id != S1_HK_CANDIDATE_ID
            or self.observable_id != S1_HK_OBSERVABLE_ID
            or self.formula != S1_HK_FORMULA
            or self.domain != S1_HK_DOMAIN
            or self.range != S1_HK_RANGE
            or self.null_cases != S1_HK_NULL_CASES
            or self.invariances != S1_HK_INVARIANCES
            or self.excluded_inputs_and_operations != S1_HK_EXCLUSIONS
            or any(
                value is not True
                for value in (
                    self.same_observable_as_e1_baseline,
                    self.observable_is_eligibility_not_transfer,
                    self.zero_blocks_engagement_eligibility_only,
                    self.turnover_and_recovery_ignore_observable,
                )
            )
            or any(
                value is not False
                for value in (
                    self.threshold_selected,
                    self.transfer_amount_selected,
                    self.rate_selected,
                    self.time_law_selected,
                    self.integrator_selected,
                    self.field_backreaction_selected,
                    self.runtime_implemented,
                    self.functional_effect_proven,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HK_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1HKEdgeParticipationContractError(
                "S1-HK weakened the observable-only or no-transfer boundary"
            )


def build_dts1_s1hk_edge_participation_contract(
) -> DTS1S1HKEdgeParticipationContract:
    """Bind one local observable and its null cases without a transfer law."""

    values = {
        "contract_id": S1_HK_CONTRACT_ID,
        "source_s1hj_contract_digest": S1_HK_SOURCE_S1HJ_CONTRACT_DIGEST,
        "candidate_id": S1_HK_CANDIDATE_ID,
        "observable_id": S1_HK_OBSERVABLE_ID,
        "formula": S1_HK_FORMULA,
        "domain": S1_HK_DOMAIN,
        "range": S1_HK_RANGE,
        "null_cases": S1_HK_NULL_CASES,
        "invariances": S1_HK_INVARIANCES,
        "excluded_inputs_and_operations": S1_HK_EXCLUSIONS,
        "same_observable_as_e1_baseline": True,
        "observable_is_eligibility_not_transfer": True,
        "zero_blocks_engagement_eligibility_only": True,
        "turnover_and_recovery_ignore_observable": True,
        "threshold_selected": False,
        "transfer_amount_selected": False,
        "rate_selected": False,
        "time_law_selected": False,
        "integrator_selected": False,
        "field_backreaction_selected": False,
        "runtime_implemented": False,
        "functional_effect_proven": False,
        "execution_permitted": False,
        "field_steps_executed": 0,
        "claims_permitted": False,
        "decision": S1_HK_DECISION,
    }
    return DTS1S1HKEdgeParticipationContract(
        **values,
        contract_digest=_digest(values),
    )
