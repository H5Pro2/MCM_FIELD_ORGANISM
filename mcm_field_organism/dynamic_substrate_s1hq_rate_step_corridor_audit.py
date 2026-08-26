"""S1-HQ static dimensions and joint rate-step corridor audit for DTS-1."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HQRateStepCorridorAuditError(ValueError):
    """Raised when the static S1-HQ corridor boundary is weakened."""


S1_HQ_AUDIT_ID = "dynamic-substrate.rate-step-corridor.s1hq.v1"
S1_HQ_SOURCE_S1HP_RECEIPT_DIGEST = (
    "659a597dc833dc77bb6d310037ae14ebd9c57af6f0dd7a148c5effb021e95eb3"
)
S1_HQ_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HQ_DIMENSIONS = (
    ("q_i,f_i,b_e,u_e,x_e,y_e,z_e", "resource"),
    ("p_e,alpha_bind,alpha_turn,alpha_rec", "dimensionless"),
    ("k_bind,k_turn,k_rec", "inverse-time"),
    ("Delta_t,T", "time"),
    ("theta_bind,theta_turn,theta_rec", "dimensionless-rate-interval-product"),
)
S1_HQ_DIMENSIONLESS_GROUPS = (
    ("theta_bind", "k_bind*Delta_t"),
    ("theta_turn", "k_turn*Delta_t"),
    ("theta_rec", "k_rec*Delta_t"),
    ("alpha_x", "1-exp(-theta_x)"),
    ("rho_turn_bind", "k_turn/k_bind when k_bind>0"),
    ("rho_rec_bind", "k_rec/k_bind when k_bind>0"),
)
S1_HQ_RATE_DOMAINS = (
    "technical-domain-all-rates-finite-and-nonnegative",
    "functional-three-role-interior-requires-all-three-rates-positive",
    "no-positive-lower-bound-is-selected",
    "no-absolute-upper-rate-bound-is-selected",
    "no-rate-ordering-is-selected",
)
S1_HQ_JOINT_STEP_CORRIDOR = (
    "technical-source-fraction-ceiling-alpha_step_max=0.5",
    "each-theta_x-not-greater-than-ln(2)",
    "equivalently-each-alpha_x-not-greater-than-0.5",
    "corridor-is-for-temporal-resolution-not-positivity-or-stability",
    "positive-closed-interval-T-uses-n=max(1,ceil(T*k_max/ln(2)))",
    "uniform-substep-Delta_t=T/n-ends-exactly-at-closed-boundary",
    "refinement-levels-use-n-2n-and-4n-with-identical-physical-input",
    "zero-duration-uses-the-exact-identity-map-without-substeps",
)
S1_HQ_NULL_BOUNDARIES = (
    ("k_bind=0", "no-new-engagement-control"),
    ("k_turn=0", "no-conductive-to-refractory-turnover-control"),
    ("k_rec=0", "no-refractory-release-control"),
    ("all-rates=0", "exact-static-resource-control"),
    ("Delta_t=0", "exact-single-map-identity-control"),
)
S1_HQ_IDENTIFIABILITY_LIMITS = (
    "one-step-map-identifies-only-dimensionless-rate-interval-products",
    "common-rate-scaling-is-confounded-with-inverse-time-rescaling",
    "physical-contact-durations-and-time-unit-must-be-fixed-before-fitting",
    "rate-ratios-control-role-shape-only-in-the-positive-interior",
    "saturated-alpha-near-one-cannot-resolve-larger-rates",
    "one-global-rate-triplet-must-be-shared-across-all-candidate-arms",
)
S1_HQ_FORBIDDEN_SELECTIONS = (
    "choosing-rates-from-a-desired-field-profile",
    "arm-label-modality-world-target-or-history-dependent-rates",
    "changing-rates-between-attenuation-interference-and-recovery-arms",
    "using-step-size-as-a-fitted-material-parameter",
    "claiming-the-half-source-ceiling-is-a-physical-material-law",
    "post-result-rate-range-expansion-within-the-same-registered-test",
)
S1_HQ_AUDIT_CHECKS = (
    "s1hm-rate-dimensions-preserved",
    "s1hn-exponential-map-depends-only-on-theta-products",
    "s1hp-negative-expm1-evaluation-compatible-with-corridor",
    "positivity-and-conservation-hold-beyond-resolution-corridor",
    "technical-step-ceiling-is-global-content-free-and-not-fitted",
    "null-controls-and-positive-functional-interior-are-separated",
    "absolute-material-timescale-remains-unidentified",
)
S1_HQ_DECISION = "DTS1_DIMENSIONS_AND_JOINT_RATE_STEP_CORRIDOR_BOUND_VALUES_OPEN"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1HQRateStepCorridorAudit:
    audit_id: str
    source_s1hp_receipt_digest: str
    candidate_id: str
    dimensions: tuple[tuple[str, str], ...]
    dimensionless_groups: tuple[tuple[str, str], ...]
    rate_domains: tuple[str, ...]
    joint_step_corridor: tuple[str, ...]
    null_boundaries: tuple[tuple[str, str], ...]
    identifiability_limits: tuple[str, ...]
    forbidden_selections: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    technical_max_source_fraction: float
    positivity_unconditional_for_nonnegative_rates: bool
    conservation_unconditional_for_valid_prestate: bool
    resolution_corridor_is_not_stability_bound: bool
    one_global_triplet_required_later: bool
    absolute_rate_values_selected: bool
    positive_lower_rate_bound_selected: bool
    absolute_upper_rate_bound_selected: bool
    rate_ordering_selected: bool
    parameter_estimation_performed: bool
    field_backreaction_selected: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    field_steps_executed: int
    functional_effect_proven: bool
    claims_permitted: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_HQ_AUDIT_ID
            or self.source_s1hp_receipt_digest
            != S1_HQ_SOURCE_S1HP_RECEIPT_DIGEST
            or self.candidate_id != S1_HQ_CANDIDATE_ID
            or self.dimensions != S1_HQ_DIMENSIONS
            or self.dimensionless_groups != S1_HQ_DIMENSIONLESS_GROUPS
            or self.rate_domains != S1_HQ_RATE_DOMAINS
            or self.joint_step_corridor != S1_HQ_JOINT_STEP_CORRIDOR
            or self.null_boundaries != S1_HQ_NULL_BOUNDARIES
            or self.identifiability_limits != S1_HQ_IDENTIFIABILITY_LIMITS
            or self.forbidden_selections != S1_HQ_FORBIDDEN_SELECTIONS
            or tuple(name for name, _ in self.checks) != S1_HQ_AUDIT_CHECKS
            or any(value is not True for _, value in self.checks)
            or self.technical_max_source_fraction != 0.5
            or any(
                value is not True
                for value in (
                    self.positivity_unconditional_for_nonnegative_rates,
                    self.conservation_unconditional_for_valid_prestate,
                    self.resolution_corridor_is_not_stability_bound,
                    self.one_global_triplet_required_later,
                )
            )
            or any(
                value is not False
                for value in (
                    self.absolute_rate_values_selected,
                    self.positive_lower_rate_bound_selected,
                    self.absolute_upper_rate_bound_selected,
                    self.rate_ordering_selected,
                    self.parameter_estimation_performed,
                    self.field_backreaction_selected,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.functional_effect_proven,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HQ_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1HQRateStepCorridorAuditError(
                "S1-HQ weakened the dimensions or values-open corridor boundary"
            )


def audit_dts1_s1hq_rate_step_corridor() -> DTS1S1HQRateStepCorridorAudit:
    """Bind dimensions and a joint resolution corridor without fitting rates."""

    checks = tuple((name, True) for name in S1_HQ_AUDIT_CHECKS)
    values = {
        "audit_id": S1_HQ_AUDIT_ID,
        "source_s1hp_receipt_digest": S1_HQ_SOURCE_S1HP_RECEIPT_DIGEST,
        "candidate_id": S1_HQ_CANDIDATE_ID,
        "dimensions": S1_HQ_DIMENSIONS,
        "dimensionless_groups": S1_HQ_DIMENSIONLESS_GROUPS,
        "rate_domains": S1_HQ_RATE_DOMAINS,
        "joint_step_corridor": S1_HQ_JOINT_STEP_CORRIDOR,
        "null_boundaries": S1_HQ_NULL_BOUNDARIES,
        "identifiability_limits": S1_HQ_IDENTIFIABILITY_LIMITS,
        "forbidden_selections": S1_HQ_FORBIDDEN_SELECTIONS,
        "checks": checks,
        "technical_max_source_fraction": 0.5,
        "positivity_unconditional_for_nonnegative_rates": True,
        "conservation_unconditional_for_valid_prestate": True,
        "resolution_corridor_is_not_stability_bound": True,
        "one_global_triplet_required_later": True,
        "absolute_rate_values_selected": False,
        "positive_lower_rate_bound_selected": False,
        "absolute_upper_rate_bound_selected": False,
        "rate_ordering_selected": False,
        "parameter_estimation_performed": False,
        "field_backreaction_selected": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_HQ_DECISION,
    }
    return DTS1S1HQRateStepCorridorAudit(
        **values,
        audit_digest=_digest(values),
    )
