"""Static S1-JE finite two-node P_IH boundary fixture contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jd_corrected_pih_exposure_contract import (
    build_dts1_s1jd_corrected_pih_exposure_contract,
)


class DTS1S1JEFinitePIHBoundaryFixtureContractError(ValueError):
    """Raised when the finite S1-JE fixture contract is weakened."""


S1_JE_CONTRACT_ID = "dynamic-substrate.finite-pih-two-node-boundary.s1je.v1"
S1_JE_SOURCE_S1JD_DIGEST = (
    "273d2272ad660bc60a8a089c3910488b3a8375cb4c7742fed0040102dcb1ee3e"
)
S1_JE_GEOMETRY = (
    ("node_order", ("node-a", "node-b")),
    ("edge_order", ("A=(node-a,node-b)",)),
    ("topology", "open-undirected-two-node-line"),
    ("numeric_format", "IEEE-754-binary64"),
)
S1_JE_BOUNDARY_FIXTURE = (
    ("role", "A_BOUNDARY_2N"),
    ("S", (-0.5, 0.5)),
    ("H", (0.0, 0.0)),
    ("expected_S1_HK_participation", (0.25,)),
)
S1_JE_INTERVAL_FIXTURE = (
    ("role", "A_ACTIVE_2N"),
    ("duration", 0.5),
    ("duration_unit", "synthetic-time-units"),
    ("receptor_contact", (0.0, 0.0)),
    ("boundary_operator_duration", 0.0),
)
S1_JE_STRUCTURAL_RULES = (
    "S-and-H-have-complete-canonical-two-node-width",
    "all-values-are-finite-exact-binary-fractions-inside-the-closed-normalized-field-domain",
    "S-is-antisymmetric-H-is-bit-exact-positive-zero-and-S1-HK-participation-is-exactly-one-quarter",
    "boundary-S-and-H-differ-from-the-quarantined-old-minus-one-plus-one-and-minus-point-two-plus-point-two-vectors",
    "all-three-P_IH-events-reuse-one-bit-identical-boundary-duration-and-zero-contact",
    "boundary-consumes-zero-time-and-each-active-interval-has-one-positive-fixed-duration",
)
S1_JE_TOLERANCES = (
    ("canonical_fixture_digest_and_cross_model_boundary_identity", "bit-exact"),
    ("structural_zero_antisymmetry_and_dyadic_participation", "bit-exact"),
    ("finite_domain_and_later_ledger_roundoff_floor", 1.1368683772161603e-13),
    ("outcome_acceptance_or_baseline_fit_tolerance", "not-bound-in-S1-JE"),
)
S1_JE_CALL_BUDGET = (
    ("models", 7),
    ("active_intervals_per_model_per_refinement", 3),
    ("refinement_levels", 3),
    ("single_complete_audit_boundary_applications", 63),
    ("single_complete_audit_interval_invocations", 63),
    ("double_audit_max_boundary_applications", 126),
    ("double_audit_max_interval_invocations", 126),
    ("research_field_steps", 0),
)
S1_JE_REFINEMENT_RULES = (
    "use-the-S1-JA-levels-two-four-eight-with-level-four-as-primary",
    "apply-the-boundary-once-before-each-complete-physical-interval-at-each-level",
    "do-not-count-private-internal-substeps-as-additional-boundary-applications-or-high-level-interval-invocations",
    "do-not-fit-boundary-duration-or-configuration-to-any-refinement-output",
)
S1_JE_QUARANTINE_RULES = (
    "do-not-import-copy-scale-fit-or-reinterpret-any-old-P_IH-field-result-vector",
    "retain-old-P_IH-direct-resource-ledgers-only-as-separate-direct-evidence",
    "new-P_IH-field-profile-must-be-reregistered-from-the-corrected-common-exposure",
)
S1_JE_FORBIDDEN_INTERPRETATIONS = (
    "implemented-admissible-runtime-ready-or-executed-two-node-boundary",
    "selected-result-threshold-baseline-fit-baseline-closure-or-candidate-superiority",
    "physical-timescale-memory-learning-or-artificial-intelligence",
)
S1_JE_DECISION = "FINITE_P_IH_TWO_NODE_BOUNDARY_FIXTURE_BOUND_NO_IMPLEMENTATION_OR_EXECUTION"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JEFinitePIHBoundaryFixtureContract:
    contract_id: str
    source_s1jd_digest: str
    geometry: tuple[tuple[str, object], ...]
    boundary_fixture: tuple[tuple[str, object], ...]
    interval_fixture: tuple[tuple[str, object], ...]
    structural_rules: tuple[str, ...]
    tolerances: tuple[tuple[str, object], ...]
    call_budget: tuple[tuple[str, int], ...]
    refinement_rules: tuple[str, ...]
    quarantine_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    boundary_role_count: int
    boundary_values_selected: bool
    duration_selected: bool
    tolerances_selected: bool
    call_budget_bound: bool
    two_node_boundary_implemented: bool
    common_interval_envelope_bound: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    private_two_node_boundary_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_JE_CONTRACT_ID
            or self.source_s1jd_digest != S1_JE_SOURCE_S1JD_DIGEST
            or self.geometry != S1_JE_GEOMETRY
            or self.boundary_fixture != S1_JE_BOUNDARY_FIXTURE
            or self.interval_fixture != S1_JE_INTERVAL_FIXTURE
            or self.structural_rules != S1_JE_STRUCTURAL_RULES
            or self.tolerances != S1_JE_TOLERANCES
            or self.call_budget != S1_JE_CALL_BUDGET
            or self.refinement_rules != S1_JE_REFINEMENT_RULES
            or self.quarantine_rules != S1_JE_QUARANTINE_RULES
            or self.forbidden_interpretations != S1_JE_FORBIDDEN_INTERPRETATIONS
            or self.boundary_role_count != 1
            or any(
                value is not True
                for value in (
                    self.boundary_values_selected,
                    self.duration_selected,
                    self.tolerances_selected,
                    self.call_budget_bound,
                    self.private_two_node_boundary_implementation_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.two_node_boundary_implemented,
                    self.common_interval_envelope_bound,
                    self.adapters_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_JE_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JEFinitePIHBoundaryFixtureContractError(
                "S1-JE weakened the finite P_IH two-node boundary fixture"
            )


def build_dts1_s1je_finite_pih_boundary_fixture_contract() -> DTS1S1JEFinitePIHBoundaryFixtureContract:
    """Bind the finite P_IH boundary fixture without implementation or execution."""

    source = build_dts1_s1jd_corrected_pih_exposure_contract()
    values = {
        "contract_id": S1_JE_CONTRACT_ID,
        "source_s1jd_digest": source.contract_digest,
        "geometry": S1_JE_GEOMETRY,
        "boundary_fixture": S1_JE_BOUNDARY_FIXTURE,
        "interval_fixture": S1_JE_INTERVAL_FIXTURE,
        "structural_rules": S1_JE_STRUCTURAL_RULES,
        "tolerances": S1_JE_TOLERANCES,
        "call_budget": S1_JE_CALL_BUDGET,
        "refinement_rules": S1_JE_REFINEMENT_RULES,
        "quarantine_rules": S1_JE_QUARANTINE_RULES,
        "forbidden_interpretations": S1_JE_FORBIDDEN_INTERPRETATIONS,
        "boundary_role_count": 1,
        "boundary_values_selected": True,
        "duration_selected": True,
        "tolerances_selected": True,
        "call_budget_bound": True,
        "two_node_boundary_implemented": False,
        "common_interval_envelope_bound": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "private_two_node_boundary_implementation_authorized_next_stage": True,
        "decision": S1_JE_DECISION,
    }
    return DTS1S1JEFinitePIHBoundaryFixtureContract(
        **values, contract_digest=_digest(values)
    )
