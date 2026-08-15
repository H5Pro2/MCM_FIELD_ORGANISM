"""Static S1-IY finite fixture contract for corrected common boundaries."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1ix_corrected_event_boundary_contract import (
    build_dts1_s1ix_corrected_event_boundary_contract,
)


class DTS1S1IYFiniteBoundaryFixtureContractError(ValueError):
    """Raised when the finite S1-IY fixture boundary is weakened."""


S1_IY_CONTRACT_ID = "dynamic-substrate.finite-common-boundary-fixture.s1iy.v1"
S1_IY_SOURCE_S1IX_DIGEST = (
    "7606b7b175cc7bbad64a89d917fa752ea56448ca054a703df62ccdab800064d3"
)
S1_IY_GEOMETRY = (
    ("node_order", ("node-a", "node-b", "node-c")),
    ("edge_order", ("A=(node-a,node-b)", "B=(node-b,node-c)")),
    ("topology", "open-undirected-three-node-line"),
    ("numeric_format", "IEEE-754-binary64"),
)
S1_IY_BOUNDARY_FIXTURES = (
    (
        "A_BOUNDARY",
        (-0.5, 0.5, 0.5),
        (0.0, 0.0, 0.0),
        (0.25, 0.0),
    ),
    (
        "B_BOUNDARY",
        (-0.5, -0.5, 0.5),
        (0.0, 0.0, 0.0),
        (0.0, 0.25),
    ),
    (
        "GAP_BOUNDARY",
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (0.0, 0.0),
    ),
    (
        "PROBE_BOUNDARY",
        (-0.5, 0.0, 0.5),
        (-0.125, 0.0, 0.125),
        (0.0625, 0.0625),
    ),
)
S1_IY_DURATIONS = (
    ("A_ACTIVE", 0.5, "synthetic-time-units"),
    ("B_ACTIVE", 0.5, "synthetic-time-units"),
    ("GAP_ACTIVE", 0.5, "synthetic-time-units"),
    ("COMMON_ZERO_CONTACT_READOUT", 0.5, "synthetic-time-units"),
)
S1_IY_CONTACTS = (
    ("all_active_and_readout_intervals", (0.0, 0.0, 0.0)),
    ("boundary_operator_duration", 0.0),
)
S1_IY_STRUCTURAL_RULES = (
    "all-four-S-and-H-vectors-have-complete-canonical-three-node-width",
    "all-boundary-values-are-finite-exact-binary-fractions-inside-the-closed-normalized-field-domain",
    "A-and-B-boundaries-are-node-reversal-and-sign-symmetric-with-equal-positive-participation",
    "A-boundary-has-bit-exact-zero-B-participation-and-B-boundary-has-bit-exact-zero-A-participation",
    "gap-boundary-has-bit-exact-zero-S-H-and-participation-on-both-edges",
    "probe-boundary-is-distinct-from-every-active-boundary-and-from-the-quarantined-old-probe-vector",
    "all-active-and-readout-contacts-are-bit-exact-positive-zero-at-all-three-nodes",
    "every-duration-is-positive-equal-and-fixed-before-any-implementation",
)
S1_IY_TOLERANCES = (
    ("canonical_vector_digest_and_cross_model_boundary_identity", "bit-exact"),
    ("structural_zero_and_dyadic_participation_identity", "bit-exact"),
    ("finite_domain_and_later_ledger_roundoff_floor", 1.1368683772161603e-13),
    ("outcome_acceptance_or_baseline_fit_tolerance", "not-bound-in-S1-IY"),
)
S1_IY_CALL_BUDGET = (
    ("models", 7),
    ("P_IK_boundary_applications_per_model", 8),
    ("P_IK_interval_invocations_per_model", 8),
    ("P_IN_boundary_applications_per_model", 8),
    ("P_IN_interval_invocations_per_model", 8),
    ("single_full_fixture_boundary_applications", 112),
    ("single_full_fixture_interval_invocations", 112),
    ("double_audit_max_boundary_applications", 224),
    ("double_audit_max_interval_invocations", 224),
    ("research_field_steps", 0),
)
S1_IY_QUARANTINE_RULES = (
    "do-not-import-copy-scale-fit-or-reinterpret-any-old-P_IK-or-P_IN-field-result-vector",
    "new-probe-S-and-H-vectors-differ-from-the-old-minus-one-zero-plus-one-and-minus-point-two-zero-plus-point-two-vectors",
    "retain-old-direct-resource-ledgers-only-as-prior-direct-evidence-not-as-fixture-values",
)
S1_IY_FORBIDDEN_INTERPRETATIONS = (
    "implemented-admissible-runtime-ready-or-executed-boundary-fixture",
    "selected-baseline-parameters-configuration-digests-result-thresholds-or-model-fit",
    "baseline-closure-candidate-superiority-memory-learning-or-artificial-intelligence",
)
S1_IY_DECISION = "FINITE_COMMON_EVENT_BOUNDARY_FIXTURE_BOUND_NO_IMPLEMENTATION_OR_EXECUTION"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IYFiniteBoundaryFixtureContract:
    contract_id: str
    source_s1ix_digest: str
    geometry: tuple[tuple[str, object], ...]
    boundary_fixtures: tuple[
        tuple[str, tuple[float, ...], tuple[float, ...], tuple[float, ...]], ...
    ]
    durations: tuple[tuple[str, float, str], ...]
    contacts: tuple[tuple[str, object], ...]
    structural_rules: tuple[str, ...]
    tolerances: tuple[tuple[str, object], ...]
    call_budget: tuple[tuple[str, int], ...]
    quarantine_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    boundary_role_count: int
    boundary_values_selected: bool
    durations_selected: bool
    tolerances_selected: bool
    call_budget_bound: bool
    adapter_configuration_selected: bool
    configuration_digests_bound: bool
    boundary_operator_implemented: bool
    fixtures_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    private_boundary_fixture_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_IY_CONTRACT_ID
            or self.source_s1ix_digest != S1_IY_SOURCE_S1IX_DIGEST
            or self.geometry != S1_IY_GEOMETRY
            or self.boundary_fixtures != S1_IY_BOUNDARY_FIXTURES
            or self.durations != S1_IY_DURATIONS
            or self.contacts != S1_IY_CONTACTS
            or self.structural_rules != S1_IY_STRUCTURAL_RULES
            or self.tolerances != S1_IY_TOLERANCES
            or self.call_budget != S1_IY_CALL_BUDGET
            or self.quarantine_rules != S1_IY_QUARANTINE_RULES
            or self.forbidden_interpretations != S1_IY_FORBIDDEN_INTERPRETATIONS
            or self.boundary_role_count != 4
            or any(
                value is not True
                for value in (
                    self.boundary_values_selected,
                    self.durations_selected,
                    self.tolerances_selected,
                    self.call_budget_bound,
                    self.private_boundary_fixture_implementation_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.adapter_configuration_selected,
                    self.configuration_digests_bound,
                    self.boundary_operator_implemented,
                    self.fixtures_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_IY_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IYFiniteBoundaryFixtureContractError(
                "S1-IY weakened the finite boundary fixture contract"
            )


def build_dts1_s1iy_finite_boundary_fixture_contract() -> DTS1S1IYFiniteBoundaryFixtureContract:
    """Bind finite common boundary values without implementing or running them."""

    source = build_dts1_s1ix_corrected_event_boundary_contract()
    values = {
        "contract_id": S1_IY_CONTRACT_ID,
        "source_s1ix_digest": source.contract_digest,
        "geometry": S1_IY_GEOMETRY,
        "boundary_fixtures": S1_IY_BOUNDARY_FIXTURES,
        "durations": S1_IY_DURATIONS,
        "contacts": S1_IY_CONTACTS,
        "structural_rules": S1_IY_STRUCTURAL_RULES,
        "tolerances": S1_IY_TOLERANCES,
        "call_budget": S1_IY_CALL_BUDGET,
        "quarantine_rules": S1_IY_QUARANTINE_RULES,
        "forbidden_interpretations": S1_IY_FORBIDDEN_INTERPRETATIONS,
        "boundary_role_count": len(S1_IY_BOUNDARY_FIXTURES),
        "boundary_values_selected": True,
        "durations_selected": True,
        "tolerances_selected": True,
        "call_budget_bound": True,
        "adapter_configuration_selected": False,
        "configuration_digests_bound": False,
        "boundary_operator_implemented": False,
        "fixtures_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "private_boundary_fixture_implementation_authorized_next_stage": True,
        "decision": S1_IY_DECISION,
    }
    return DTS1S1IYFiniteBoundaryFixtureContract(
        **values, contract_digest=_digest(values)
    )
