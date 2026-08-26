"""S1-HJ local DTS-1 role-transition contract without a dynamics law."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HJRoleTransitionContractError(ValueError):
    """Raised when the S1-HJ causal or no-dynamics boundary is weakened."""


S1_HJ_CONTRACT_ID = "dynamic-substrate.local-role-transitions.s1hj.v1"
S1_HJ_SOURCE_S1HI_CONTRACT_DIGEST = (
    "35110510a4b9d08a24f60557faf9b83b26b416bdf893112d42801ef5a16c7ede"
)
S1_HJ_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HJ_ROLE_CYCLE = (
    ("free", "conductive-bound"),
    ("conductive-bound", "refractory"),
    ("refractory", "free"),
)
S1_HJ_FORBIDDEN_TRANSITIONS = (
    ("free", "refractory"),
    ("conductive-bound", "free"),
    ("refractory", "conductive-bound"),
    ("any-role-on-edge-e1", "any-role-on-distinct-edge-e2"),
    ("nothing", "any-resource-role"),
    ("any-resource-role", "nothing"),
)
S1_HJ_ALLOWED_CAUSAL_INPUTS = (
    "closed-valid-dts1-prestate",
    "existing-undirected-edge-and-its-two-endpoints",
    "derived-free-resource-at-both-edge-endpoints",
    "current-symmetric-edge-local-fast-field-participation-for-engagement-only",
    "positive-physical-interval-without-phase-or-age-counter",
)
S1_HJ_FORBIDDEN_CAUSAL_INPUTS = (
    "afterimage-h",
    "fixed-adapter-or-gain-value",
    "global-field-ranking-or-normalization",
    "observer-measurement-or-desired-result",
    "label-reward-loss-class-object-episode-or-source-identity",
    "repetition-history-phase-or-age-counter",
    "replay-buffer-raw-input-feature-vector-or-embedding",
    "different-rule-by-edge-modality-or-test-arm",
)
S1_HJ_CONCURRENCY_RULES = (
    "incident-edge-intents-must-share-one-closed-prestate",
    "combined-intents-must-not-overdraw-either-endpoint-capacity",
    "call-order-must-not-select-a-winning-edge",
    "unresolved-overdraw-must-fail-closed-without-partial-state",
)
S1_HJ_DECISION = "DTS1_LOCAL_ROLE_CYCLE_AND_CAUSAL_ELIGIBILITY_BOUND_NO_DYNAMICS"


def _digest(payload: object) -> str:
    def encode_dataclass(value: object) -> dict[str, object]:
        try:
            return {field.name: getattr(value, field.name) for field in fields(value)}
        except TypeError as exc:
            raise TypeError(f"cannot digest {type(value).__name__}") from exc

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=encode_dataclass,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1LocalRoleTransition:
    """One permitted role change and its necessary causal eligibility."""

    transition_id: str
    source_role: str
    target_role: str
    causal_eligibility: str
    ledger_effect: str
    same_edge_only: bool
    content_free: bool

    def __post_init__(self) -> None:
        if (
            not isinstance(self.transition_id, str)
            or not self.transition_id
            or (self.source_role, self.target_role) not in S1_HJ_ROLE_CYCLE
            or not isinstance(self.causal_eligibility, str)
            or not self.causal_eligibility
            or not isinstance(self.ledger_effect, str)
            or not self.ledger_effect
            or self.same_edge_only is not True
            or self.content_free is not True
        ):
            raise DTS1S1HJRoleTransitionContractError(
                "S1-HJ transition must stay in the local content-free role cycle"
            )


S1_HJ_TRANSITIONS = (
    DTS1LocalRoleTransition(
        transition_id="local-engagement",
        source_role="free",
        target_role="conductive-bound",
        causal_eligibility=(
            "a closed valid prestate has free resource at both endpoints and current "
            "symmetric fast-field participation on this existing edge"
        ),
        ledger_effect=(
            "the same booked amount enters conductive-bound on the edge and exactly "
            "half leaves derived free resource at each endpoint"
        ),
        same_edge_only=True,
        content_free=True,
    ),
    DTS1LocalRoleTransition(
        transition_id="local-turnover",
        source_role="conductive-bound",
        target_role="refractory",
        causal_eligibility=(
            "conductive-bound resource exists on this edge during a positive physical "
            "interval; no contact class phase or age counter is consulted"
        ),
        ledger_effect=(
            "the same booked amount leaves conductive-bound and enters refractory on "
            "the identical edge while endpoint free resource is unchanged"
        ),
        same_edge_only=True,
        content_free=True,
    ),
    DTS1LocalRoleTransition(
        transition_id="local-recovery",
        source_role="refractory",
        target_role="free",
        causal_eligibility=(
            "refractory resource exists on this edge during a positive physical "
            "interval; no reset phase or field-content test is consulted"
        ),
        ledger_effect=(
            "the same booked amount leaves refractory on the edge and exactly half "
            "returns to derived free resource at each endpoint"
        ),
        same_edge_only=True,
        content_free=True,
    ),
)


@dataclass(frozen=True, slots=True)
class DTS1S1HJLocalRoleTransitionContract:
    contract_id: str
    source_s1hi_contract_digest: str
    candidate_id: str
    role_cycle: tuple[tuple[str, str], ...]
    transitions: tuple[DTS1LocalRoleTransition, ...]
    forbidden_transitions: tuple[tuple[str, str], ...]
    allowed_causal_inputs: tuple[str, ...]
    forbidden_causal_inputs: tuple[str, ...]
    concurrency_rules: tuple[str, ...]
    eligibility_is_not_transition_amount: bool
    ledger_effect_is_not_dynamics_equation: bool
    exact_field_observable_selected: bool
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
            self.contract_id != S1_HJ_CONTRACT_ID
            or self.source_s1hi_contract_digest
            != S1_HJ_SOURCE_S1HI_CONTRACT_DIGEST
            or self.candidate_id != S1_HJ_CANDIDATE_ID
            or self.role_cycle != S1_HJ_ROLE_CYCLE
            or self.transitions != S1_HJ_TRANSITIONS
            or tuple(
                (item.source_role, item.target_role) for item in self.transitions
            )
            != self.role_cycle
            or self.forbidden_transitions != S1_HJ_FORBIDDEN_TRANSITIONS
            or self.allowed_causal_inputs != S1_HJ_ALLOWED_CAUSAL_INPUTS
            or self.forbidden_causal_inputs != S1_HJ_FORBIDDEN_CAUSAL_INPUTS
            or self.concurrency_rules != S1_HJ_CONCURRENCY_RULES
            or any(
                value is not True
                for value in (
                    self.eligibility_is_not_transition_amount,
                    self.ledger_effect_is_not_dynamics_equation,
                )
            )
            or any(
                value is not False
                for value in (
                    self.exact_field_observable_selected,
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
            or self.decision != S1_HJ_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1HJRoleTransitionContractError(
                "S1-HJ weakened the local role-cycle or no-dynamics boundary"
            )


def build_dts1_s1hj_local_role_transition_contract(
) -> DTS1S1HJLocalRoleTransitionContract:
    """Bind causal eligibility and bookkeeping without executing a transition."""

    values = {
        "contract_id": S1_HJ_CONTRACT_ID,
        "source_s1hi_contract_digest": S1_HJ_SOURCE_S1HI_CONTRACT_DIGEST,
        "candidate_id": S1_HJ_CANDIDATE_ID,
        "role_cycle": S1_HJ_ROLE_CYCLE,
        "transitions": S1_HJ_TRANSITIONS,
        "forbidden_transitions": S1_HJ_FORBIDDEN_TRANSITIONS,
        "allowed_causal_inputs": S1_HJ_ALLOWED_CAUSAL_INPUTS,
        "forbidden_causal_inputs": S1_HJ_FORBIDDEN_CAUSAL_INPUTS,
        "concurrency_rules": S1_HJ_CONCURRENCY_RULES,
        "eligibility_is_not_transition_amount": True,
        "ledger_effect_is_not_dynamics_equation": True,
        "exact_field_observable_selected": False,
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
        "decision": S1_HJ_DECISION,
    }
    return DTS1S1HJLocalRoleTransitionContract(
        **values,
        contract_digest=_digest(values),
    )
