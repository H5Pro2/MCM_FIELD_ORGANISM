"""S1-HL DTS-1 transfer dimensions and source ceilings without a law."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math


class DTS1S1HLTransferBudgetContractError(ValueError):
    """Raised when transfer dimensions or source ceilings are invalid."""


S1_HL_CONTRACT_ID = "dynamic-substrate.transfer-dimension-budget.s1hl.v1"
S1_HL_SOURCE_S1HK_CONTRACT_DIGEST = (
    "9a0ffe1e19209617373da67c193c17970e6028e56e9932c227032d6b6de635fc"
)
S1_HL_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HL_DIMENSIONS = (
    ("q_i", "resource"),
    ("f_i", "resource"),
    ("b_e", "resource"),
    ("u_e", "resource"),
    ("candidate-transfer-amount", "resource"),
    ("p_e", "dimensionless"),
    ("physical-interval", "time"),
    ("later-interval-response", "dimensionless"),
)
S1_HL_REQUIRED_ZEROES = (
    "engagement-is-zero-when-p_e-is-zero",
    "engagement-is-zero-when-either-endpoint-free-resource-is-zero",
    "turnover-is-zero-when-conductive-bound-source-is-zero",
    "recovery-is-zero-when-refractory-source-is-zero",
    "every-transfer-is-zero-for-a-zero-physical-interval",
)
S1_HL_SOURCE_CEILINGS = (
    "engagement-amount-not-greater-than-two-times-minimum-endpoint-free-resource",
    "turnover-amount-not-greater-than-conductive-bound-source-on-the-edge",
    "recovery-amount-not-greater-than-refractory-source-on-the-edge",
    "incident-engagement-half-shares-not-greater-than-node-free-resource",
)
S1_HL_FORBIDDEN_SHORTCUTS = (
    "clipping-a-transfer-after-overdraw",
    "post-hoc-normalization-of-edge-amounts",
    "using-refractory-resource-directly-for-engagement",
    "using-same-update-produced-resource-as-a-new-source",
    "global-budget-borrowing-between-nonincident-nodes",
    "call-order-based-partial-acceptance",
    "parameter-value-rate-or-time-constant-selection",
)
S1_HL_DECISION = "DTS1_TRANSFER_DIMENSIONS_AND_RESOURCE_CEILINGS_BOUND_NO_LAW"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _resource(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise DTS1S1HLTransferBudgetContractError(
            f"{role} must be numeric, not boolean"
        )
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1S1HLTransferBudgetContractError(
            f"{role} must be numeric"
        ) from exc
    if not math.isfinite(result) or result < 0.0:
        raise DTS1S1HLTransferBudgetContractError(
            f"{role} must be finite and nonnegative"
        )
    return result


@dataclass(frozen=True, slots=True)
class DTS1TransferSourceCeilings:
    """Hard source ceilings; these values are not proposed transfer amounts."""

    engagement_maximum: float
    turnover_maximum: float
    recovery_maximum: float


def compute_dts1_s1hl_transfer_source_ceilings(
    first_endpoint_free: object,
    second_endpoint_free: object,
    conductive_bound_source: object,
    refractory_source: object,
) -> DTS1TransferSourceCeilings:
    """Derive only source ceilings from one closed S1-HI prestate."""

    first_free = _resource(first_endpoint_free, "first_endpoint_free")
    second_free = _resource(second_endpoint_free, "second_endpoint_free")
    conductive = _resource(conductive_bound_source, "conductive_bound_source")
    refractory = _resource(refractory_source, "refractory_source")
    return DTS1TransferSourceCeilings(
        engagement_maximum=2.0 * min(first_free, second_free),
        turnover_maximum=conductive,
        recovery_maximum=refractory,
    )


def validate_dts1_s1hl_incident_engagement_budget(
    node_free_resource: object,
    incident_engagement_amounts: tuple[object, ...],
) -> None:
    """Reject a proposed joint booking that would overdraw one node."""

    free = _resource(node_free_resource, "node_free_resource")
    amounts = tuple(
        _resource(value, "incident_engagement_amount")
        for value in tuple(incident_engagement_amounts)
    )
    if not amounts:
        raise DTS1S1HLTransferBudgetContractError(
            "incident engagement budget requires at least one amount"
        )
    if 0.5 * math.fsum(amounts) > free:
        raise DTS1S1HLTransferBudgetContractError(
            "incident engagement half-shares exceed node free resource"
        )


@dataclass(frozen=True, slots=True)
class DTS1S1HLTransferDimensionBudgetContract:
    contract_id: str
    source_s1hk_contract_digest: str
    candidate_id: str
    dimensions: tuple[tuple[str, str], ...]
    required_zeroes: tuple[str, ...]
    source_ceilings: tuple[str, ...]
    forbidden_shortcuts: tuple[str, ...]
    ceilings_are_not_transfer_amounts: bool
    all_sources_read_one_closed_prestate: bool
    simultaneous_budget_checked_before_output: bool
    transfer_formula_selected: bool
    parameter_values_selected: bool
    rate_selected: bool
    time_law_selected: bool
    integrator_selected: bool
    conflict_resolution_selected: bool
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
            self.contract_id != S1_HL_CONTRACT_ID
            or self.source_s1hk_contract_digest
            != S1_HL_SOURCE_S1HK_CONTRACT_DIGEST
            or self.candidate_id != S1_HL_CANDIDATE_ID
            or self.dimensions != S1_HL_DIMENSIONS
            or self.required_zeroes != S1_HL_REQUIRED_ZEROES
            or self.source_ceilings != S1_HL_SOURCE_CEILINGS
            or self.forbidden_shortcuts != S1_HL_FORBIDDEN_SHORTCUTS
            or any(
                value is not True
                for value in (
                    self.ceilings_are_not_transfer_amounts,
                    self.all_sources_read_one_closed_prestate,
                    self.simultaneous_budget_checked_before_output,
                )
            )
            or any(
                value is not False
                for value in (
                    self.transfer_formula_selected,
                    self.parameter_values_selected,
                    self.rate_selected,
                    self.time_law_selected,
                    self.integrator_selected,
                    self.conflict_resolution_selected,
                    self.field_backreaction_selected,
                    self.runtime_implemented,
                    self.functional_effect_proven,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HL_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1HLTransferBudgetContractError(
                "S1-HL weakened the dimensions-only or no-law boundary"
            )


def build_dts1_s1hl_transfer_dimension_budget_contract(
) -> DTS1S1HLTransferDimensionBudgetContract:
    """Bind dimensions, nulls, and ceilings without choosing a transfer law."""

    values = {
        "contract_id": S1_HL_CONTRACT_ID,
        "source_s1hk_contract_digest": S1_HL_SOURCE_S1HK_CONTRACT_DIGEST,
        "candidate_id": S1_HL_CANDIDATE_ID,
        "dimensions": S1_HL_DIMENSIONS,
        "required_zeroes": S1_HL_REQUIRED_ZEROES,
        "source_ceilings": S1_HL_SOURCE_CEILINGS,
        "forbidden_shortcuts": S1_HL_FORBIDDEN_SHORTCUTS,
        "ceilings_are_not_transfer_amounts": True,
        "all_sources_read_one_closed_prestate": True,
        "simultaneous_budget_checked_before_output": True,
        "transfer_formula_selected": False,
        "parameter_values_selected": False,
        "rate_selected": False,
        "time_law_selected": False,
        "integrator_selected": False,
        "conflict_resolution_selected": False,
        "field_backreaction_selected": False,
        "runtime_implemented": False,
        "functional_effect_proven": False,
        "execution_permitted": False,
        "field_steps_executed": 0,
        "claims_permitted": False,
        "decision": S1_HL_DECISION,
    }
    return DTS1S1HLTransferDimensionBudgetContract(
        **values,
        contract_digest=_digest(values),
    )
