"""S1-HN static discrete integration contract for the DTS-1 family."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HNDiscreteIntegrationContractError(ValueError):
    """Raised when the static S1-HN integration boundary is weakened."""


S1_HN_CONTRACT_ID = "dynamic-substrate.discrete-integration.s1hn.v1"
S1_HN_SOURCE_S1HM_AUDIT_DIGEST = (
    "fd3f836db6e330996077f3a0a476a9aa00780bef566858b3c1a58ec8128800be"
)
S1_HN_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HN_MAP_ID = "CLOSED_PRESTATE_EXPONENTIAL_TRANSFER_MAP"
S1_HN_INTERVAL_FRACTIONS = (
    ("alpha_bind", "1-exp(-k_bind*Delta_t)"),
    ("alpha_turn", "1-exp(-k_turn*Delta_t)"),
    ("alpha_rec", "1-exp(-k_rec*Delta_t)"),
)
S1_HN_CLOSED_PRESTATE_OFFERS = (
    ("d_e", "alpha_bind*p_e*2*min(f_i,f_j)"),
    ("D_i", "0.5*sum(d_e for incident edges)"),
    ("a_i", "1 if D_i=0 else min(1,f_i/D_i)"),
    ("x_e", "d_e*min(a_i,a_j)"),
    ("y_e", "alpha_turn*b_e"),
    ("z_e", "alpha_rec*u_e"),
)
S1_HN_ATOMIC_COMMIT = (
    ("b_e_next", "b_e+x_e-y_e"),
    ("u_e_next", "u_e+y_e-z_e"),
    (
        "f_i_next",
        "f_i-0.5*sum(x_e for incident edges)"
        "+0.5*sum(z_e for incident edges)",
    ),
)
S1_HN_PROOF_OBLIGATIONS = (
    "zero-interval-is-the-identity-map",
    "all-transfer-sources-read-one-closed-prestate",
    "newly-produced-resource-is-not-reused-in-the-same-step",
    "engagement-admission-is-simultaneous-and-edge-order-independent",
    "engagement-half-shares-do-not-overdraw-node-free-resource",
    "turnover-does-not-overdraw-conductive-bound-resource",
    "recovery-does-not-overdraw-refractory-resource",
    "all-three-next-state-roles-remain-nonnegative",
    "local-and-global-resource-identities-are-preserved-algebraically",
    "small-interval-map-is-first-order-consistent-with-s1hm-family",
    "no-post-hoc-clipping-normalization-or-state-repair",
)
S1_HN_FAIL_CLOSED_CONDITIONS = (
    "negative-nonfinite-or-boolean-interval-or-rate-input",
    "invalid-s1hi-prestate-or-resource-ledger",
    "missing-duplicate-or-noncanonical-edge",
    "nonfinite-participation-or-participation-outside-unit-interval",
    "transfer-source-ceiling-or-joint-node-budget-violation",
    "nonnegative-state-or-conservation-proof-obligation-failure",
    "post-hoc-clipping-normalization-or-state-repair-required",
    "call-order-dependent-partial-admission",
)
S1_HN_DECISION = "DTS1_POSITIVITY_CONSERVATION_DISCRETE_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1HNDiscreteIntegrationContract:
    contract_id: str
    source_s1hm_audit_digest: str
    candidate_id: str
    map_id: str
    interval_fractions: tuple[tuple[str, str], ...]
    closed_prestate_offers: tuple[tuple[str, str], ...]
    atomic_commit: tuple[tuple[str, str], ...]
    proof_obligations: tuple[tuple[str, bool], ...]
    fail_closed_conditions: tuple[str, ...]
    one_closed_prestate: bool
    simultaneous_local_admission_selected: bool
    edge_order_independent: bool
    positivity_preserved_by_construction: bool
    conservation_preserved_by_construction: bool
    post_hoc_clipping_permitted: bool
    post_hoc_normalization_permitted: bool
    parameter_values_selected: bool
    executable_step_implemented: bool
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
            self.contract_id != S1_HN_CONTRACT_ID
            or self.source_s1hm_audit_digest
            != S1_HN_SOURCE_S1HM_AUDIT_DIGEST
            or self.candidate_id != S1_HN_CANDIDATE_ID
            or self.map_id != S1_HN_MAP_ID
            or self.interval_fractions != S1_HN_INTERVAL_FRACTIONS
            or self.closed_prestate_offers != S1_HN_CLOSED_PRESTATE_OFFERS
            or self.atomic_commit != S1_HN_ATOMIC_COMMIT
            or tuple(name for name, _ in self.proof_obligations)
            != S1_HN_PROOF_OBLIGATIONS
            or any(value is not True for _, value in self.proof_obligations)
            or self.fail_closed_conditions != S1_HN_FAIL_CLOSED_CONDITIONS
            or any(
                value is not True
                for value in (
                    self.one_closed_prestate,
                    self.simultaneous_local_admission_selected,
                    self.edge_order_independent,
                    self.positivity_preserved_by_construction,
                    self.conservation_preserved_by_construction,
                )
            )
            or any(
                value is not False
                for value in (
                    self.post_hoc_clipping_permitted,
                    self.post_hoc_normalization_permitted,
                    self.parameter_values_selected,
                    self.executable_step_implemented,
                    self.field_backreaction_selected,
                    self.runtime_implemented,
                    self.functional_effect_proven,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HN_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1HNDiscreteIntegrationContractError(
                "S1-HN weakened the static positivity/conservation boundary"
            )


def build_dts1_s1hn_discrete_integration_contract(
) -> DTS1S1HNDiscreteIntegrationContract:
    """Bind one discrete map symbolically without implementing a step."""

    proof_obligations = tuple((name, True) for name in S1_HN_PROOF_OBLIGATIONS)
    values = {
        "contract_id": S1_HN_CONTRACT_ID,
        "source_s1hm_audit_digest": S1_HN_SOURCE_S1HM_AUDIT_DIGEST,
        "candidate_id": S1_HN_CANDIDATE_ID,
        "map_id": S1_HN_MAP_ID,
        "interval_fractions": S1_HN_INTERVAL_FRACTIONS,
        "closed_prestate_offers": S1_HN_CLOSED_PRESTATE_OFFERS,
        "atomic_commit": S1_HN_ATOMIC_COMMIT,
        "proof_obligations": proof_obligations,
        "fail_closed_conditions": S1_HN_FAIL_CLOSED_CONDITIONS,
        "one_closed_prestate": True,
        "simultaneous_local_admission_selected": True,
        "edge_order_independent": True,
        "positivity_preserved_by_construction": True,
        "conservation_preserved_by_construction": True,
        "post_hoc_clipping_permitted": False,
        "post_hoc_normalization_permitted": False,
        "parameter_values_selected": False,
        "executable_step_implemented": False,
        "field_backreaction_selected": False,
        "runtime_implemented": False,
        "functional_effect_proven": False,
        "execution_permitted": False,
        "field_steps_executed": 0,
        "claims_permitted": False,
        "decision": S1_HN_DECISION,
    }
    return DTS1S1HNDiscreteIntegrationContract(
        **values,
        contract_digest=_digest(values),
    )
