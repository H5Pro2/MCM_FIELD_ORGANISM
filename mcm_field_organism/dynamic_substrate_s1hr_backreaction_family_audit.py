"""S1-HR static audit of one DTS-1 field-backreaction family."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HRBackreactionFamilyAuditError(ValueError):
    """Raised when the one-family S1-HR audit boundary is weakened."""


S1_HR_AUDIT_ID = "dynamic-substrate.backreaction-family-audit.s1hr.v1"
S1_HR_SOURCE_S1HQ_AUDIT_DIGEST = (
    "86f5f0c990525800e9d51b01169a4885bf630eeb19a0ab25c743c6b0bd2fd457"
)
S1_HR_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HR_FAMILY_ID = "SYMMETRIC_BOUNDED_CONDUCTANCE_AUGMENTATION"
S1_HR_FAMILY_FORM = (
    ("c_e", "b_e/(2*min(q_i,q_j))"),
    ("r_0", "1/response_time"),
    ("r_e_active", "r_0*(1+c_e)"),
    ("r_e_ablated", "r_0"),
    ("edge_flux_i_from_j", "r_e*(S_j-S_i)"),
)
S1_HR_BOUNDS = (
    "s1hi-ledger-implies-zero-not-greater-than-c_e-not-greater-than-one",
    "active-rate-between-r_0-and-two-times-r_0",
    "ablated-rate-equals-r_0-for-every-edge",
    "same-nonnegative-rate-used-in-both-directions-of-one-undirected-edge",
)
S1_HR_GENERATOR_PROPERTIES = (
    "symmetric-internal-edge-generator",
    "zero-row-sum-and-no-additive-field-source",
    "negative-semidefinite-diffusion-form",
    "constant-field-nullspace-preserved",
    "receptor-boundary-and-fast-afterimage-unchanged",
)
S1_HR_COUNTERPREDICTIONS = (
    (
        "fixed-adapter",
        "one pre-probe frozen rate ledger stays fixed while changing b_e changes later candidate rates",
    ),
    (
        "same-b-different-free-refractory",
        "immediate rates match but later rates diverge after the identical next participation",
    ),
    (
        "dynamic-two-state-e1",
        "must fail the same free-versus-refractory intervention under the same conductance reader",
    ),
    (
        "leaky-integrator-f3-const-v-fast-afterimage",
        "remain mandatory whole-profile baselines under the s1hh falsification contract",
    ),
)
S1_HR_ABLATION_ARMS = (
    "P0-existing-neutral-field-without-dts1-state",
    "A0-same-dts1-state-and-turnover-with-backreaction-disabled",
    "A1-same-dts1-state-and-turnover-with-backreaction-enabled",
    "F0-pre-probe-frozen-a1-edge-rate-ledger",
    "U0-uniform-fixed-rate-ledger-matched-to-the-a1-rate-range",
    "E1-two-state-dynamic-resource-with-the-same-reader-family",
)
S1_HR_STOP_CONDITIONS = (
    "fixed-pre-probe-rate-ledger-reproduces-the-complete-candidate-trajectory",
    "same-b-free-versus-refractory-intervention-does-not-alter-later-rates",
    "two-state-e1-with-the-same-reader-reproduces-all-required-profiles",
    "registered-leaky-integrator-f3-const-v-or-fast-afterimage-baseline-suffices",
    "nonlinear-threshold-signed-or-content-specific-reader-is-needed",
    "extra-backreaction-gain-must-be-fitted-to-obtain-the-required-result",
    "receptor-or-afterimage-boundary-must-be-changed",
    "generator-symmetry-conservation-or-nonpositivity-is-lost",
)
S1_HR_AUDIT_CHECKS = (
    "exactly-one-linear-positive-conductance-family",
    "only-conductive-bound-resource-is-read",
    "heterogeneous-node-capacity-normalization-is-local-and-bounded",
    "no-new-backreaction-strength-parameter",
    "technical-ablation-removes-only-the-reader-effect",
    "instantaneous-fixed-adapter-equivalence-is-explicit",
    "trajectory-counterprediction-requires-dts1-state-evolution",
    "frozen-e1-branch-remains-stopped-and-only-serves-as-baseline",
)
S1_HR_DECISION = "ZULASSEN_DTS1_SYMMETRIC_BOUNDED_CONDUCTANCE_BACKREACTION"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1HRBackreactionFamilyAudit:
    audit_id: str
    source_s1hq_audit_digest: str
    candidate_id: str
    audited_family_count: int
    family_id: str
    family_form: tuple[tuple[str, str], ...]
    bounds: tuple[str, ...]
    generator_properties: tuple[str, ...]
    counterpredictions: tuple[tuple[str, str], ...]
    ablation_arms: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    known_adapter_family: bool
    instantaneous_fixed_adapter_equivalence: bool
    trajectory_counterprediction_requires_dynamic_state: bool
    parameterless_reader: bool
    frozen_e1_branch_remains_stopped: bool
    static_audit_passed: bool
    backreaction_family_selected: bool
    backreaction_implementation_present: bool
    coupled_integrator_selected: bool
    material_rate_values_selected: bool
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
            self.audit_id != S1_HR_AUDIT_ID
            or self.source_s1hq_audit_digest != S1_HR_SOURCE_S1HQ_AUDIT_DIGEST
            or self.candidate_id != S1_HR_CANDIDATE_ID
            or self.audited_family_count != 1
            or self.family_id != S1_HR_FAMILY_ID
            or self.family_form != S1_HR_FAMILY_FORM
            or self.bounds != S1_HR_BOUNDS
            or self.generator_properties != S1_HR_GENERATOR_PROPERTIES
            or self.counterpredictions != S1_HR_COUNTERPREDICTIONS
            or self.ablation_arms != S1_HR_ABLATION_ARMS
            or self.stop_conditions != S1_HR_STOP_CONDITIONS
            or tuple(name for name, _ in self.checks) != S1_HR_AUDIT_CHECKS
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.known_adapter_family,
                    self.instantaneous_fixed_adapter_equivalence,
                    self.trajectory_counterprediction_requires_dynamic_state,
                    self.parameterless_reader,
                    self.frozen_e1_branch_remains_stopped,
                    self.static_audit_passed,
                    self.backreaction_family_selected,
                )
            )
            or any(
                value is not False
                for value in (
                    self.backreaction_implementation_present,
                    self.coupled_integrator_selected,
                    self.material_rate_values_selected,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.functional_effect_proven,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HR_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1HRBackreactionFamilyAuditError(
                "S1-HR weakened the one-family static backreaction audit"
            )


def audit_dts1_s1hr_backreaction_family(
) -> DTS1S1HRBackreactionFamilyAudit:
    """Audit one parameterless reader family without coupling it to a field."""

    checks = tuple((name, True) for name in S1_HR_AUDIT_CHECKS)
    values = {
        "audit_id": S1_HR_AUDIT_ID,
        "source_s1hq_audit_digest": S1_HR_SOURCE_S1HQ_AUDIT_DIGEST,
        "candidate_id": S1_HR_CANDIDATE_ID,
        "audited_family_count": 1,
        "family_id": S1_HR_FAMILY_ID,
        "family_form": S1_HR_FAMILY_FORM,
        "bounds": S1_HR_BOUNDS,
        "generator_properties": S1_HR_GENERATOR_PROPERTIES,
        "counterpredictions": S1_HR_COUNTERPREDICTIONS,
        "ablation_arms": S1_HR_ABLATION_ARMS,
        "stop_conditions": S1_HR_STOP_CONDITIONS,
        "checks": checks,
        "known_adapter_family": True,
        "instantaneous_fixed_adapter_equivalence": True,
        "trajectory_counterprediction_requires_dynamic_state": True,
        "parameterless_reader": True,
        "frozen_e1_branch_remains_stopped": True,
        "static_audit_passed": True,
        "backreaction_family_selected": True,
        "backreaction_implementation_present": False,
        "coupled_integrator_selected": False,
        "material_rate_values_selected": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_HR_DECISION,
    }
    return DTS1S1HRBackreactionFamilyAudit(
        **values,
        audit_digest=_digest(values),
    )
