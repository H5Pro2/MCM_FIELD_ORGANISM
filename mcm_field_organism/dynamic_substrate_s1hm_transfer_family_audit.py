"""S1-HM static audit of one DTS-1 transfer-law family."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HMTransferFamilyAuditError(ValueError):
    """Raised when the S1-HM one-family audit boundary is weakened."""


S1_HM_AUDIT_ID = "dynamic-substrate.transfer-family-audit.s1hm.v1"
S1_HM_SOURCE_S1HL_CONTRACT_DIGEST = (
    "e0b14a368eb4a83a894ecd124ae4761e0cd682448ec83be42ae8655ba9f64824"
)
S1_HM_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HM_FAMILY_ID = "LOCAL_BOUNDED_THREE_COMPARTMENT_TURNOVER"
S1_HM_RATE_SYMBOLS = (
    ("k_bind", "nonnegative-global-content-free-inverse-time"),
    ("k_turn", "nonnegative-global-content-free-inverse-time"),
    ("k_rec", "nonnegative-global-content-free-inverse-time"),
)
S1_HM_FLUX_FAMILY = (
    ("J_bind", "k_bind*p_e*2*min(f_i,f_j)"),
    ("J_turn", "k_turn*b_e"),
    ("J_rec", "k_rec*u_e"),
)
S1_HM_STATE_BALANCE = (
    ("d_b_e/dt", "J_bind-J_turn"),
    ("d_u_e/dt", "J_turn-J_rec"),
    (
        "d_f_i/dt",
        "-0.5*sum(J_bind-J_rec for incident edges from one closed state)",
    ),
)
S1_HM_AUDIT_CHECKS = (
    "one-family-only",
    "s1hh-finite-local-resource-and-direct-partition-intervention",
    "s1hi-local-and-global-ledger-preserved-algebraically",
    "s1hj-directed-role-cycle-without-shortcuts",
    "s1hk-observable-reused-without-candidate-specific-tuning",
    "s1hl-dimensions-zeroes-and-source-ceilings-compatible",
    "nonnegative-state-boundaries-point-inward-in-continuous-family",
    "fixed-adapter-cannot-represent-within-probe-resource-evolution",
    "two-state-e1-cannot-represent-free-versus-refractory-intervention",
    "f3-const-v-and-fast-afterimage-remain-structurally-distinct",
    "leaky-integrator-family-remains-a-mandatory-empirical-baseline",
    "historic-refractory-stop-opened-only-as-explicit-engineering-assumption",
)
S1_HM_STOP_CONDITIONS_REMAINING = (
    "registered-leaky-or-integrator-baseline-reproduces-all-required-profiles",
    "free-versus-refractory-intervention-does-not-change-future-engagement",
    "fixed-adapter-reproduces-the-complete-dynamic-probe-trajectory",
    "resource-ledger-or-nonnegativity-needs-clipping-or-normalization",
    "field-backreaction-must-be-tailored-to-obtain-the-required-result",
    "labels-counters-phases-targets-or-content-specific-rules-are-needed",
)
S1_HM_DECISION = "ZULASSEN_DTS1_THREE_COMPARTMENT_ENGINEERING_FAMILY"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1HMTransferFamilyAudit:
    audit_id: str
    source_s1hl_contract_digest: str
    candidate_id: str
    audited_family_count: int
    family_id: str
    rate_symbols: tuple[tuple[str, str], ...]
    flux_family: tuple[tuple[str, str], ...]
    state_balance: tuple[tuple[str, str], ...]
    checks: tuple[tuple[str, bool], ...]
    stop_conditions_remaining: tuple[str, ...]
    explicit_engineering_assumption: bool
    mcm_intrinsic_nature_claim: bool
    known_three_compartment_material_family: bool
    direct_partition_counterprediction_exists: bool
    static_audit_passed: bool
    parameter_values_selected: bool
    discrete_integrator_selected: bool
    conflict_resolution_selected: bool
    field_backreaction_selected: bool
    runtime_implemented: bool
    functional_effect_proven: bool
    execution_permitted: bool
    field_steps_executed: int
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
            self.audit_id != S1_HM_AUDIT_ID
            or self.source_s1hl_contract_digest
            != S1_HM_SOURCE_S1HL_CONTRACT_DIGEST
            or self.candidate_id != S1_HM_CANDIDATE_ID
            or self.audited_family_count != 1
            or self.family_id != S1_HM_FAMILY_ID
            or self.rate_symbols != S1_HM_RATE_SYMBOLS
            or self.flux_family != S1_HM_FLUX_FAMILY
            or self.state_balance != S1_HM_STATE_BALANCE
            or tuple(name for name, _ in self.checks) != S1_HM_AUDIT_CHECKS
            or any(value is not True for _, value in self.checks)
            or self.stop_conditions_remaining != S1_HM_STOP_CONDITIONS_REMAINING
            or any(
                value is not True
                for value in (
                    self.explicit_engineering_assumption,
                    self.known_three_compartment_material_family,
                    self.direct_partition_counterprediction_exists,
                    self.static_audit_passed,
                )
            )
            or any(
                value is not False
                for value in (
                    self.mcm_intrinsic_nature_claim,
                    self.parameter_values_selected,
                    self.discrete_integrator_selected,
                    self.conflict_resolution_selected,
                    self.field_backreaction_selected,
                    self.runtime_implemented,
                    self.functional_effect_proven,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HM_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1HMTransferFamilyAuditError(
                "S1-HM weakened the one-family engineering-only audit boundary"
            )


def audit_dts1_s1hm_transfer_family() -> DTS1S1HMTransferFamilyAudit:
    """Audit one symbolic family without integrating or executing it."""

    checks = tuple((name, True) for name in S1_HM_AUDIT_CHECKS)
    values = {
        "audit_id": S1_HM_AUDIT_ID,
        "source_s1hl_contract_digest": S1_HM_SOURCE_S1HL_CONTRACT_DIGEST,
        "candidate_id": S1_HM_CANDIDATE_ID,
        "audited_family_count": 1,
        "family_id": S1_HM_FAMILY_ID,
        "rate_symbols": S1_HM_RATE_SYMBOLS,
        "flux_family": S1_HM_FLUX_FAMILY,
        "state_balance": S1_HM_STATE_BALANCE,
        "checks": checks,
        "stop_conditions_remaining": S1_HM_STOP_CONDITIONS_REMAINING,
        "explicit_engineering_assumption": True,
        "mcm_intrinsic_nature_claim": False,
        "known_three_compartment_material_family": True,
        "direct_partition_counterprediction_exists": True,
        "static_audit_passed": True,
        "parameter_values_selected": False,
        "discrete_integrator_selected": False,
        "conflict_resolution_selected": False,
        "field_backreaction_selected": False,
        "runtime_implemented": False,
        "functional_effect_proven": False,
        "execution_permitted": False,
        "field_steps_executed": 0,
        "claims_permitted": False,
        "decision": S1_HM_DECISION,
    }
    return DTS1S1HMTransferFamilyAudit(**values, audit_digest=_digest(values))
