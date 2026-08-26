"""Static S1-JH finite fixture contract for the common interval envelope."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_common_boundary import (
    build_dts1_s1iz_implementation_receipt,
)
from .dynamic_substrate_s1id_causal_field_readout_audit_contract import (
    build_dts1_s1id_causal_field_readout_audit_contract,
)
from .dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from .dynamic_substrate_s1jg_common_interval_envelope_contract import (
    build_dts1_s1jg_common_interval_envelope_contract,
)


class DTS1S1JHFiniteCommonIntervalFixtureContractError(ValueError):
    """Raised when the finite S1-JH fixture boundary is weakened."""


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


S1_JH_CONTRACT_ID = "dynamic-substrate.finite-common-interval-fixture.s1jh.v1"
S1_JH_SOURCE_S1JG_DIGEST = (
    "dfdc0b2a1f8fd280804d3b87e950418de0c6686b6f2af0ec7dfd796f9cc3616d"
)
S1_JH_SOURCE_S1ID_DIGEST = (
    "aeadd736c2d8a1982a2b37d874494542603b67586852c78d081eca69ae187750"
)
S1_JH_SOURCE_S1IZ_DIGEST = (
    "346f4778686642b0fa907c7ee1a5c95b2b8968172efc7a4f1cf0340de0e77828"
)
S1_JH_SOURCE_S1JA_DIGEST = (
    "331168f2a6f937b454742d2be57de3f022f75ca5ca521fbff31f101bd4ea1fbc"
)
S1_JH_COMMON_STEP_TIME = ("mcm.s1jh.common.interval", 0, 1, 2.0)
S1_JH_GEOMETRY_CORES = (
    ("TWO_NODE_OPEN_LINE", ("node-a", "node-b"), (("node-a", "node-b"),)),
    (
        "THREE_NODE_OPEN_LINE",
        ("node-a", "node-b", "node-c"),
        (("node-a", "node-b"), ("node-b", "node-c")),
    ),
)
S1_JH_GEOMETRIES = tuple((*row, _digest(row)) for row in S1_JH_GEOMETRY_CORES)

_SOURCE_FIXTURE_CORES = (
    (
        "P_IE_INITIAL_SH",
        "TWO_NODE_OPEN_LINE",
        (-1.0, 1.0),
        (-0.2, 0.2),
        S1_JH_SOURCE_S1ID_DIGEST,
    ),
    (
        "A_BOUNDARY_2N",
        "TWO_NODE_OPEN_LINE",
        (-0.5, 0.5),
        (0.0, 0.0),
        S1_JH_SOURCE_S1JG_DIGEST,
    ),
    (
        "A_BOUNDARY",
        "THREE_NODE_OPEN_LINE",
        (-0.5, 0.5, 0.5),
        (0.0, 0.0, 0.0),
        S1_JH_SOURCE_S1IZ_DIGEST,
    ),
    (
        "B_BOUNDARY",
        "THREE_NODE_OPEN_LINE",
        (-0.5, -0.5, 0.5),
        (0.0, 0.0, 0.0),
        S1_JH_SOURCE_S1IZ_DIGEST,
    ),
    (
        "GAP_BOUNDARY",
        "THREE_NODE_OPEN_LINE",
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        S1_JH_SOURCE_S1IZ_DIGEST,
    ),
    (
        "PROBE_BOUNDARY",
        "THREE_NODE_OPEN_LINE",
        (-0.5, 0.0, 0.5),
        (-0.125, 0.0, 0.125),
        S1_JH_SOURCE_S1IZ_DIGEST,
    ),
)
S1_JH_SOURCE_FIXTURES = tuple(
    (*row, _digest(row)) for row in _SOURCE_FIXTURE_CORES
)

_CONTACT_FIXTURE_CORES = (
    (
        "ZERO_CONTACT_2N",
        "TWO_NODE_OPEN_LINE",
        (0.0, 0.0),
        "mcm.s1jh.common.source",
        0,
        1,
        "mcm.s1jh.zero.2n",
        ("carrier-a", "carrier-b"),
    ),
    (
        "ZERO_CONTACT_3N",
        "THREE_NODE_OPEN_LINE",
        (0.0, 0.0, 0.0),
        "mcm.s1jh.common.source",
        0,
        1,
        "mcm.s1jh.zero.3n",
        ("carrier-a", "carrier-b", "carrier-c"),
    ),
)
S1_JH_CONTACT_FIXTURES = tuple(
    (*row, _digest(row)) for row in _CONTACT_FIXTURE_CORES
)

# Event tuple: prestate directive, source role, checkpoint after interval.
S1_JH_SEQUENCE_BLUEPRINTS = (
    (
        "P_IE_F_HIGH",
        "P_IE_CAUSAL_TWO_SUBSTEP",
        "TWO_NODE_OPEN_LINE",
        (("INITIAL_REGISTERED_SH", "P_IE_INITIAL_SH", True), ("CARRY_PRIOR_SH", "PREVIOUS_INTERVAL", True)),
    ),
    (
        "P_IE_R_HIGH",
        "P_IE_CAUSAL_TWO_SUBSTEP",
        "TWO_NODE_OPEN_LINE",
        (("INITIAL_REGISTERED_SH", "P_IE_INITIAL_SH", True), ("CARRY_PRIOR_SH", "PREVIOUS_INTERVAL", True)),
    ),
    (
        "P_IH_A_A_A",
        "P_IH_ATTENUATION",
        "TWO_NODE_OPEN_LINE",
        (("APPLY_BOUNDARY_2N", "A_BOUNDARY_2N", True),) * 3,
    ),
    (
        "P_IK_A_B_A",
        "P_IK_INTERFERENCE",
        "THREE_NODE_OPEN_LINE",
        (("APPLY_BOUNDARY_3N", "A_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "B_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "A_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "PROBE_BOUNDARY", True)),
    ),
    (
        "P_IK_A_GAP_A",
        "P_IK_INTERFERENCE",
        "THREE_NODE_OPEN_LINE",
        (("APPLY_BOUNDARY_3N", "A_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "GAP_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "A_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "PROBE_BOUNDARY", True)),
    ),
    (
        "P_IN_RECOVERY_ON",
        "P_IN_RELEASE_REUSE",
        "THREE_NODE_OPEN_LINE",
        (("APPLY_BOUNDARY_3N", "A_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "GAP_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "B_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "PROBE_BOUNDARY", True)),
    ),
    (
        "P_IN_RECOVERY_OFF",
        "P_IN_RELEASE_REUSE",
        "THREE_NODE_OPEN_LINE",
        (("APPLY_BOUNDARY_3N", "A_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "GAP_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "B_BOUNDARY", False), ("APPLY_BOUNDARY_3N", "PROBE_BOUNDARY", True)),
    ),
)


def _build_sequence_fixtures() -> tuple[tuple[str, str, str, int, str], ...]:
    return tuple(
        (key, profile, geometry, len(events), _digest((key, profile, geometry, events)))
        for key, profile, geometry, events in S1_JH_SEQUENCE_BLUEPRINTS
    )


S1_JH_SEQUENCE_FIXTURES = _build_sequence_fixtures()


def _build_envelope_fixtures() -> tuple[tuple[object, ...], ...]:
    geometry_by_id = {row[0]: row for row in S1_JH_GEOMETRIES}
    source_by_role = {row[0]: row for row in S1_JH_SOURCE_FIXTURES}
    contact_by_geometry = {row[1]: row for row in S1_JH_CONTACT_FIXTURES}
    sequence_digest_by_key = {row[0]: row[4] for row in S1_JH_SEQUENCE_FIXTURES}
    envelopes: list[tuple[object, ...]] = []
    for key, _profile, geometry_id, events in S1_JH_SEQUENCE_BLUEPRINTS:
        geometry = geometry_by_id[geometry_id]
        contact = contact_by_geometry[geometry_id]
        prior_digest: str | None = None
        for ordinal, (directive, source_role, checkpoint) in enumerate(events, 1):
            source_digest = (
                prior_digest
                if source_role == "PREVIOUS_INTERVAL"
                else source_by_role[source_role][-1]
            )
            if source_digest is None:
                raise DTS1S1JHFiniteCommonIntervalFixtureContractError(
                    "carry directive has no prior interval"
                )
            core = (
                sequence_digest_by_key[key],
                ordinal,
                geometry[1],
                geometry[-1],
                directive,
                source_digest,
                contact[2],
                S1_JH_COMMON_STEP_TIME,
                checkpoint,
            )
            prior_digest = _digest(core)
            envelopes.append((*core, prior_digest))
    return tuple(envelopes)


S1_JH_ENVELOPE_FIXTURES = _build_envelope_fixtures()
S1_JH_CANDIDATE_SIDECARS = tuple(
    (*row, _digest(row))
    for row in (
        ("P_IE_F_HIGH", "INITIAL_ANATOMY", (1.0, 1.0), (0.4,), (0.2,)),
        ("P_IE_R_HIGH", "INITIAL_ANATOMY", (1.0, 1.0), (0.4,), (0.8,)),
        ("P_IN_RECOVERY_ON", "GAP_RECOVERY_RATE", (0.2,)),
        ("P_IN_RECOVERY_OFF", "GAP_RECOVERY_RATE", (0.0,)),
    )
)
S1_JH_REFINEMENT_AND_BUDGET = (
    ("refinement_levels", (2, 4, 8)),
    ("primary_refinement_level", 4),
    ("models", 7),
    ("envelopes_per_model_per_refinement", 23),
    ("single_fixture_interval_invocations", 483),
    ("single_fixture_boundary_applications", 399),
    ("single_fixture_checkpoint_captures", 231),
    ("double_fixture_max_interval_invocations", 966),
    ("double_fixture_max_boundary_applications", 798),
    ("double_fixture_max_checkpoint_captures", 462),
    ("research_field_steps", 0),
)
S1_JH_INFORMATION_BARRIER_RULES = (
    "all-envelope-and-sequence-labels-remain-orchestrator-only",
    "all-intervals-use-one-value-identical-clock-tick-range-and-duration",
    "all-two-node-intervals-use-one-value-identical-zero-contact-and-all-three-node-intervals-another",
    "model-facing-input-digest-is-created-only-after-materialization-and-is-not-preregistered-here",
    "candidate-sidecars-are-not-envelope-fields-and-are-never-delivered-to-B1-through-B6",
)
S1_JH_FAIL_CLOSED_RULES = (
    "reject-any-source-geometry-contact-sequence-envelope-or-sidecar-digest-drift",
    "reject-any-nonzero-contact-nonpositive-duration-or-profile-specific-clock",
    "reject-any-carry-source-other-than-the-immediately-prior-interval-digest",
    "reject-any-sequence-order-cardinality-checkpoint-or-refinement-drift",
    "one-invalid-fixture-blocks-all-later-implementation-without-partial-output",
)
S1_JH_QUARANTINE_RULES = (
    "do-not-import-copy-scale-fit-or-reinterpret-old-P_IH-P_IK-or-P_IN-field-result-vectors",
    "retain-old-direct-resource-ledgers-only-as-separate-prior-direct-evidence",
    "all-corrected-field-profiles-must-be-reregistered-after-a-later-common-envelope-implementation",
)
S1_JH_FORBIDDEN_INTERPRETATIONS = (
    "implemented-materialized-executed-or-numerically-admissible-common-envelope",
    "selected-outcome-threshold-baseline-fit-baseline-closure-or-candidate-superiority",
    "physical-timescale-memory-learning-or-artificial-intelligence",
)
S1_JH_DECISION = "FINITE_COMMON_INTERVAL_FIXTURE_BOUND_NO_IMPLEMENTATION_OR_EXECUTION"


@dataclass(frozen=True, slots=True)
class DTS1S1JHFiniteCommonIntervalFixtureContract:
    contract_id: str
    source_s1jg_digest: str
    source_s1id_digest: str
    source_s1iz_digest: str
    source_s1ja_digest: str
    common_step_time: tuple[str, int, int, float]
    geometries: tuple[tuple[object, ...], ...]
    source_fixtures: tuple[tuple[object, ...], ...]
    contact_fixtures: tuple[tuple[object, ...], ...]
    sequence_fixtures: tuple[tuple[str, str, str, int, str], ...]
    envelope_fixtures: tuple[tuple[object, ...], ...]
    candidate_sidecars: tuple[tuple[object, ...], ...]
    refinement_and_budget: tuple[tuple[str, object], ...]
    information_barrier_rules: tuple[str, ...]
    fail_closed_rules: tuple[str, ...]
    quarantine_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    sequence_count: int
    envelope_count: int
    concrete_values_and_digests_bound: bool
    common_interval_fixture_implemented: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    private_fixture_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected = (
            self.contract_id == S1_JH_CONTRACT_ID
            and self.source_s1jg_digest == S1_JH_SOURCE_S1JG_DIGEST
            and self.source_s1id_digest == S1_JH_SOURCE_S1ID_DIGEST
            and self.source_s1iz_digest == S1_JH_SOURCE_S1IZ_DIGEST
            and self.source_s1ja_digest == S1_JH_SOURCE_S1JA_DIGEST
            and self.common_step_time == S1_JH_COMMON_STEP_TIME
            and self.geometries == S1_JH_GEOMETRIES
            and self.source_fixtures == S1_JH_SOURCE_FIXTURES
            and self.contact_fixtures == S1_JH_CONTACT_FIXTURES
            and self.sequence_fixtures == S1_JH_SEQUENCE_FIXTURES
            and self.envelope_fixtures == S1_JH_ENVELOPE_FIXTURES
            and self.candidate_sidecars == S1_JH_CANDIDATE_SIDECARS
            and self.refinement_and_budget == S1_JH_REFINEMENT_AND_BUDGET
            and self.information_barrier_rules == S1_JH_INFORMATION_BARRIER_RULES
            and self.fail_closed_rules == S1_JH_FAIL_CLOSED_RULES
            and self.quarantine_rules == S1_JH_QUARANTINE_RULES
            and self.forbidden_interpretations == S1_JH_FORBIDDEN_INTERPRETATIONS
            and self.sequence_count == 7
            and self.envelope_count == 23
            and self.concrete_values_and_digests_bound is True
            and self.common_interval_fixture_implemented is False
            and self.adapters_implemented is False
            and self.baseline_models_executed is False
            and self.runtime_integration_present is False
            and self.research_execution_permitted is False
            and self.technical_field_steps_executed == 0
            and self.research_field_steps_executed == 0
            and self.private_fixture_implementation_authorized_next_stage is True
            and self.decision == S1_JH_DECISION
            and self.contract_digest == _digest(payload)
        )
        if not expected:
            raise DTS1S1JHFiniteCommonIntervalFixtureContractError(
                "S1-JH weakened the finite common interval fixture"
            )


def build_dts1_s1jh_finite_common_interval_fixture_contract(
) -> DTS1S1JHFiniteCommonIntervalFixtureContract:
    """Bind finite common interval fixtures without constructing or running them."""

    sources = (
        build_dts1_s1jg_common_interval_envelope_contract().contract_digest,
        build_dts1_s1id_causal_field_readout_audit_contract().contract_digest,
        build_dts1_s1iz_implementation_receipt().receipt_digest,
        build_dts1_s1ja_finite_configuration_matrix_contract().contract_digest,
    )
    values = {
        "contract_id": S1_JH_CONTRACT_ID,
        "source_s1jg_digest": sources[0],
        "source_s1id_digest": sources[1],
        "source_s1iz_digest": sources[2],
        "source_s1ja_digest": sources[3],
        "common_step_time": S1_JH_COMMON_STEP_TIME,
        "geometries": S1_JH_GEOMETRIES,
        "source_fixtures": S1_JH_SOURCE_FIXTURES,
        "contact_fixtures": S1_JH_CONTACT_FIXTURES,
        "sequence_fixtures": S1_JH_SEQUENCE_FIXTURES,
        "envelope_fixtures": S1_JH_ENVELOPE_FIXTURES,
        "candidate_sidecars": S1_JH_CANDIDATE_SIDECARS,
        "refinement_and_budget": S1_JH_REFINEMENT_AND_BUDGET,
        "information_barrier_rules": S1_JH_INFORMATION_BARRIER_RULES,
        "fail_closed_rules": S1_JH_FAIL_CLOSED_RULES,
        "quarantine_rules": S1_JH_QUARANTINE_RULES,
        "forbidden_interpretations": S1_JH_FORBIDDEN_INTERPRETATIONS,
        "sequence_count": len(S1_JH_SEQUENCE_FIXTURES),
        "envelope_count": len(S1_JH_ENVELOPE_FIXTURES),
        "concrete_values_and_digests_bound": True,
        "common_interval_fixture_implemented": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "private_fixture_implementation_authorized_next_stage": True,
        "decision": S1_JH_DECISION,
    }
    return DTS1S1JHFiniteCommonIntervalFixtureContract(
        **values, contract_digest=_digest(values)
    )
