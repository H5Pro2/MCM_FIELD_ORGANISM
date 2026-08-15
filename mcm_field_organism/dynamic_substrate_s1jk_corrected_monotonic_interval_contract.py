"""Static S1-JK corrected monotonic interval and digest contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jh_finite_common_interval_fixture_contract import (
    S1_JH_CANDIDATE_SIDECARS,
    S1_JH_CONTACT_FIXTURES,
    S1_JH_GEOMETRIES,
    S1_JH_REFINEMENT_AND_BUDGET,
    S1_JH_SEQUENCE_BLUEPRINTS,
    S1_JH_SOURCE_FIXTURES,
    build_dts1_s1jh_finite_common_interval_fixture_contract,
)
from .dynamic_substrate_s1jj_interval_clock_compatibility_precheck import (
    build_dts1_s1jj_interval_clock_compatibility_precheck,
)


class DTS1S1JKCorrectedMonotonicIntervalContractError(ValueError):
    """Raised when the corrected S1-JK interval contract is weakened."""


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


S1_JK_CONTRACT_ID = "dynamic-substrate.corrected-monotonic-intervals.s1jk.v1"
S1_JK_SOURCE_S1JJ_DIGEST = (
    "8436374fc2d4674d425b3441d23ca2fe5f2ec470037c797ceaffca59da10b603"
)
S1_JK_SOURCE_S1JH_DIGEST = (
    "740bcc9fe1f29258d68278ba78a58005ff46c1da548dcf3b465eb8b5f1ed9e56"
)
S1_JK_CLOCK_ID = "mcm.s1jk.common.interval"
S1_JK_TICKS_PER_SYNTHETIC_TIME_UNIT = 2.0
S1_JK_ORDINAL_STEP_TIMES = (
    (1, S1_JK_CLOCK_ID, 0, 1, S1_JK_TICKS_PER_SYNTHETIC_TIME_UNIT),
    (2, S1_JK_CLOCK_ID, 1, 2, S1_JK_TICKS_PER_SYNTHETIC_TIME_UNIT),
    (3, S1_JK_CLOCK_ID, 2, 3, S1_JK_TICKS_PER_SYNTHETIC_TIME_UNIT),
    (4, S1_JK_CLOCK_ID, 3, 4, S1_JK_TICKS_PER_SYNTHETIC_TIME_UNIT),
)


def _build_sequence_fixtures() -> tuple[tuple[str, str, str, int, str], ...]:
    geometry_by_id = {row[0]: row for row in S1_JH_GEOMETRIES}
    source_by_role = {row[0]: row for row in S1_JH_SOURCE_FIXTURES}
    contact_by_geometry = {row[1]: row for row in S1_JH_CONTACT_FIXTURES}
    time_by_ordinal = {row[0]: row[1:] for row in S1_JK_ORDINAL_STEP_TIMES}
    rows = []
    for key, profile, geometry_id, events in S1_JH_SEQUENCE_BLUEPRINTS:
        commitments = tuple(
            (
                ordinal,
                directive,
                (
                    "PREVIOUS_INTERVAL"
                    if source_role == "PREVIOUS_INTERVAL"
                    else source_by_role[source_role][-1]
                ),
                contact_by_geometry[geometry_id][-1],
                time_by_ordinal[ordinal],
                checkpoint,
            )
            for ordinal, (directive, source_role, checkpoint) in enumerate(events, 1)
        )
        sequence_core = (
            key,
            profile,
            geometry_id,
            geometry_by_id[geometry_id][-1],
            commitments,
        )
        rows.append((key, profile, geometry_id, len(events), _digest(sequence_core)))
    return tuple(rows)


S1_JK_SEQUENCE_FIXTURES = _build_sequence_fixtures()


def _build_envelope_fixtures() -> tuple[tuple[object, ...], ...]:
    geometry_by_id = {row[0]: row for row in S1_JH_GEOMETRIES}
    source_by_role = {row[0]: row for row in S1_JH_SOURCE_FIXTURES}
    contact_by_geometry = {row[1]: row for row in S1_JH_CONTACT_FIXTURES}
    sequence_digest_by_key = {row[0]: row[4] for row in S1_JK_SEQUENCE_FIXTURES}
    time_by_ordinal = {row[0]: row[1:] for row in S1_JK_ORDINAL_STEP_TIMES}
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
                raise DTS1S1JKCorrectedMonotonicIntervalContractError(
                    "carry directive has no prior corrected interval"
                )
            core = (
                sequence_digest_by_key[key],
                ordinal,
                geometry[1],
                geometry[-1],
                directive,
                source_digest,
                contact[2],
                time_by_ordinal[ordinal],
                checkpoint,
            )
            prior_digest = _digest(core)
            envelopes.append((*core, prior_digest))
    return tuple(envelopes)


S1_JK_ENVELOPE_FIXTURES = _build_envelope_fixtures()
S1_JK_TEMPORAL_RULES = (
    "each-independent-sequence-starts-at-relative-tick-zero-with-a-fresh-model-state",
    "within-one-sequence-each-start-tick-equals-the-prior-envelope-end-tick",
    "within-one-sequence-each-end-tick-is-strictly-greater-than-the-prior-end-tick",
    "every-envelope-duration-remains-one-tick-and-one-half-synthetic-time-unit",
    "the-same-sequence-relative-window-is-delivered-to-DTS1-and-B1-through-B6",
    "no-explicit-ordinal-profile-arm-case-boundary-or-target-label-enters-the-model-facing-view",
    "private-refinement-substeps-partition-one-high-level-window-without-changing-its-physical-duration",
)
S1_JK_DIGEST_RULES = (
    "sequence-digest-commits-to-key-profile-geometry-digest-and-all-ordered-event-commitments",
    "each-event-commitment-includes-directive-source-fixture-or-carry-marker-contact-digest-step-time-and-checkpoint",
    "interval-digest-commits-to-all-nine-prior-S1-JG-envelope-fields",
    "carry-prestate-source-digest-equals-the-immediately-prior-corrected-interval-digest",
    "all-digests-use-SHA-256-over-ASCII-JSON-with-sorted-keys-and-compact-separators",
    "no-result-model-output-refinement-residual-or-future-state-enters-any-preregistered-digest",
)
S1_JK_PRESERVATION_RULES = (
    "reuse-S1-JH-geometries-source-fixtures-contact-fixtures-sidecars-and-refinement-budgets-bit-for-bit",
    "supersede-only-S1-JH-step-times-sequence-digests-interval-digests-and-dependent-carry-digests",
    "retain-old-P_IH-P_IK-P_IN-field-vector-quarantine-without-numeric-reuse",
    "retain-the-S1-JG-information-barrier-and-all-twenty-four-blocked-baseline-case-identities",
)
S1_JK_FAIL_CLOSED_RULES = (
    "reject-any-clock-window-duration-contiguity-or-sequence-restart-drift",
    "reject-any-cross-model-step-time-or-refinement-horizon-mismatch",
    "reject-any-source-contact-geometry-sequence-interval-or-carry-digest-mismatch",
    "one-invalid-envelope-blocks-all-later-materialization-without-partial-output",
)
S1_JK_FORBIDDEN_INTERPRETATIONS = (
    "materialization-schema-complete-or-common-envelope-implemented-materialized-or-executed",
    "selected-outcome-threshold-baseline-fit-baseline-closure-or-candidate-superiority",
    "physical-timescale-memory-learning-or-artificial-intelligence",
)
S1_JK_DECISION = (
    "CORRECTED_MONOTONIC_COMMON_INTERVAL_TIMES_AND_DIGESTS_BOUND_NO_IMPLEMENTATION_OR_EXECUTION"
)


@dataclass(frozen=True, slots=True)
class DTS1S1JKCorrectedMonotonicIntervalContract:
    contract_id: str
    source_s1jj_digest: str
    source_s1jh_digest: str
    clock_id: str
    ticks_per_synthetic_time_unit: float
    ordinal_step_times: tuple[tuple[int, str, int, int, float], ...]
    sequence_fixtures: tuple[tuple[str, str, str, int, str], ...]
    envelope_fixtures: tuple[tuple[object, ...], ...]
    preserved_geometries: tuple[tuple[object, ...], ...]
    preserved_source_fixtures: tuple[tuple[object, ...], ...]
    preserved_contact_fixtures: tuple[tuple[object, ...], ...]
    preserved_candidate_sidecars: tuple[tuple[object, ...], ...]
    preserved_refinement_and_budget: tuple[tuple[str, object], ...]
    temporal_rules: tuple[str, ...]
    digest_rules: tuple[str, ...]
    preservation_rules: tuple[str, ...]
    fail_closed_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    sequence_count: int
    envelope_count: int
    corrected_continuation_envelope_count: int
    monotonic_time_and_digests_bound: bool
    materialization_schema_complete: bool
    common_interval_fixture_implemented: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    corrected_materialization_schema_contract_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_JK_CONTRACT_ID
            or self.source_s1jj_digest != S1_JK_SOURCE_S1JJ_DIGEST
            or self.source_s1jh_digest != S1_JK_SOURCE_S1JH_DIGEST
            or self.clock_id != S1_JK_CLOCK_ID
            or self.ticks_per_synthetic_time_unit
            != S1_JK_TICKS_PER_SYNTHETIC_TIME_UNIT
            or self.ordinal_step_times != S1_JK_ORDINAL_STEP_TIMES
            or self.sequence_fixtures != S1_JK_SEQUENCE_FIXTURES
            or self.envelope_fixtures != S1_JK_ENVELOPE_FIXTURES
            or self.preserved_geometries != S1_JH_GEOMETRIES
            or self.preserved_source_fixtures != S1_JH_SOURCE_FIXTURES
            or self.preserved_contact_fixtures != S1_JH_CONTACT_FIXTURES
            or self.preserved_candidate_sidecars != S1_JH_CANDIDATE_SIDECARS
            or self.preserved_refinement_and_budget != S1_JH_REFINEMENT_AND_BUDGET
            or self.temporal_rules != S1_JK_TEMPORAL_RULES
            or self.digest_rules != S1_JK_DIGEST_RULES
            or self.preservation_rules != S1_JK_PRESERVATION_RULES
            or self.fail_closed_rules != S1_JK_FAIL_CLOSED_RULES
            or self.forbidden_interpretations != S1_JK_FORBIDDEN_INTERPRETATIONS
            or self.sequence_count != 7
            or self.envelope_count != 23
            or self.corrected_continuation_envelope_count != 16
            or self.monotonic_time_and_digests_bound is not True
            or self.materialization_schema_complete is not False
            or self.common_interval_fixture_implemented is not False
            or self.adapters_implemented is not False
            or self.baseline_models_executed is not False
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.corrected_materialization_schema_contract_authorized_next_stage
            is not True
            or self.decision != S1_JK_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JKCorrectedMonotonicIntervalContractError(
                "S1-JK weakened the corrected monotonic interval contract"
            )


def build_dts1_s1jk_corrected_monotonic_interval_contract(
) -> DTS1S1JKCorrectedMonotonicIntervalContract:
    """Bind corrected monotonic times and digests without materialization."""

    source = build_dts1_s1jj_interval_clock_compatibility_precheck()
    fixture_source = build_dts1_s1jh_finite_common_interval_fixture_contract()
    values = {
        "contract_id": S1_JK_CONTRACT_ID,
        "source_s1jj_digest": source.audit_digest,
        "source_s1jh_digest": fixture_source.contract_digest,
        "clock_id": S1_JK_CLOCK_ID,
        "ticks_per_synthetic_time_unit": S1_JK_TICKS_PER_SYNTHETIC_TIME_UNIT,
        "ordinal_step_times": S1_JK_ORDINAL_STEP_TIMES,
        "sequence_fixtures": S1_JK_SEQUENCE_FIXTURES,
        "envelope_fixtures": S1_JK_ENVELOPE_FIXTURES,
        "preserved_geometries": S1_JH_GEOMETRIES,
        "preserved_source_fixtures": S1_JH_SOURCE_FIXTURES,
        "preserved_contact_fixtures": S1_JH_CONTACT_FIXTURES,
        "preserved_candidate_sidecars": S1_JH_CANDIDATE_SIDECARS,
        "preserved_refinement_and_budget": S1_JH_REFINEMENT_AND_BUDGET,
        "temporal_rules": S1_JK_TEMPORAL_RULES,
        "digest_rules": S1_JK_DIGEST_RULES,
        "preservation_rules": S1_JK_PRESERVATION_RULES,
        "fail_closed_rules": S1_JK_FAIL_CLOSED_RULES,
        "forbidden_interpretations": S1_JK_FORBIDDEN_INTERPRETATIONS,
        "sequence_count": len(S1_JK_SEQUENCE_FIXTURES),
        "envelope_count": len(S1_JK_ENVELOPE_FIXTURES),
        "corrected_continuation_envelope_count": 16,
        "monotonic_time_and_digests_bound": True,
        "materialization_schema_complete": False,
        "common_interval_fixture_implemented": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "corrected_materialization_schema_contract_authorized_next_stage": True,
        "decision": S1_JK_DECISION,
    }
    return DTS1S1JKCorrectedMonotonicIntervalContract(
        **values, contract_digest=_digest(values)
    )
