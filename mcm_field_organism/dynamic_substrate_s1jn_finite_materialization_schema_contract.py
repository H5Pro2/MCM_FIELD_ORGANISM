"""Static S1-JN finite identity and API contract for pure materialization."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)
from .dynamic_substrate_s1jm_exposure_prestate_integrity_contract import (
    build_dts1_s1jm_exposure_prestate_integrity_contract,
)


class DTS1S1JNFiniteMaterializationSchemaContractError(ValueError):
    """Raised when the finite S1-JN materialization schema is weakened."""


S1_JN_CONTRACT_ID = "dynamic-substrate.finite-materialization-schema.s1jn.v1"
S1_JN_SOURCE_S1JM_DIGEST = (
    "1ca29d466c4244bf279eccfc3caf07d55e1ddcd73ab666ca48caf4eacdcb2f43"
)
S1_JN_SOURCE_S1JK_DIGEST = (
    "64ca5b895146fef453eb27945a1074f5d2b8e4c8834a94cc6f9b0a855a61824f"
)
S1_JN_FIELD_IDENTITY_FIXTURES = (
    (
        "TWO_NODE_OPEN_LINE",
        "mcm.s1jn.field.2n",
        "mcm.s1jn.layer.2n",
        "mcm.s1jn.geometry.2n",
        "auditory",
        (("node-a", (0,)), ("node-b", (1,))),
        ((-1,), (1,)),
        (),
        ("node-a", "node-b"),
        "dock.s1jn.auditory.2n",
        "mcm.s1jn.receptor.2n",
        (("carrier-a", "node-a"), ("carrier-b", "node-b")),
    ),
    (
        "THREE_NODE_OPEN_LINE",
        "mcm.s1jn.field.3n",
        "mcm.s1jn.layer.3n",
        "mcm.s1jn.geometry.3n",
        "auditory",
        (("node-a", (0,)), ("node-b", (1,)), ("node-c", (2,))),
        ((-1,), (1,)),
        (),
        ("node-a", "node-b", "node-c"),
        "dock.s1jn.auditory.3n",
        "mcm.s1jn.receptor.3n",
        (("carrier-a", "node-a"), ("carrier-b", "node-b"), ("carrier-c", "node-c")),
    ),
)
S1_JN_RECEPTOR_COMPLETION_FIXTURES = (
    (
        "ZERO_CONTACT_2N",
        "TWO_NODE_OPEN_LINE",
        "auditory",
        "mcm.s1jn.receptor.2n",
        "dock.s1jn.auditory.2n",
        "mcm.s1jh.zero.2n",
        "mcm.s1jh.common.source",
        0,
        1,
        ("carrier-a", "carrier-b"),
        (0.0, 0.0),
    ),
    (
        "ZERO_CONTACT_3N",
        "THREE_NODE_OPEN_LINE",
        "auditory",
        "mcm.s1jn.receptor.3n",
        "dock.s1jn.auditory.3n",
        "mcm.s1jh.zero.3n",
        "mcm.s1jh.common.source",
        0,
        1,
        ("carrier-a", "carrier-b", "carrier-c"),
        (0.0, 0.0, 0.0),
    ),
)
S1_JN_FRESH_FIELD_RULES = (
    "each-independent-sequence-starts-from-one-complete-role-owned-field-matching-the-exact-geometry-fixture",
    "fresh-layer-tick-is-zero-last_distribution-is-null-and-every-neuron-perception-has-tick-zero-no-local-samples-and-zero-dock-contact",
    "fresh-fast-state-S-and-H-is-bit-exact-positive-zero-before-the-registered-initial-or-boundary-operation",
    "DTS1-B1-and-B2-fresh-fields-have-no-embedded-M-or-L-state",
    "B3-through-B6-fresh-fields-contain-only-their-own-valid-preregistered-uniform-M-state",
    "B2-L-DTS1-anatomy-B1-fixed-adapter-and-B6-frozen-spec-remain-external-private-state-payloads",
)
S1_JN_PRIVATE_STATE_SCHEMAS = (
    ("DTS1", ("complete_resource_anatomy_payload", "candidate_sidecar_digest_or_null")),
    ("B1", ("fixed_adapter_payload", "fixed_adapter_configuration_digest")),
    ("B2", ("complete_L_state_payload", "B2_configuration_digest")),
    ("B3", ("embedded_M_state_digest", "B3_configuration_digest")),
    ("B4", ("embedded_M_state_digest", "B4_configuration_digest")),
    ("B5", ("embedded_M_state_digest", "B5_configuration_digest")),
    ("B6", ("embedded_M_state_digest", "frozen_CONST_V_spec_digest", "B6_configuration_digest")),
)
S1_JN_ENVELOPE_FIXTURE_OBJECT_SCHEMA = (
    "sequence_digest",
    "ordinal",
    "canonical_node_ids",
    "edge_inventory_digest",
    "prestate_directive",
    "prestate_source_digest",
    "receptor_contact",
    "step_time",
    "checkpoint_after_interval",
    "interval_digest",
)
S1_JN_MATERIALIZER_INPUT_SCHEMA = (
    ("envelope_fixture", "one-exact-immutable-S1-JK-envelope-fixture-object"),
    ("model_role", "one-exact-DTS1-or-B1-through-B6-orchestrator-role"),
    ("input_field", "one-complete-immutable-role-owned-SharedMCMField"),
    ("private_state", "one-complete-immutable-role-matching-private-state-payload"),
    ("prior_envelope_digest", "null-at-ordinal-one-otherwise-exact-prior-envelope-digest-in-the-same-sequence"),
    ("prior_output_digest", "null-at-ordinal-one-otherwise-exact-recorded-prior-complete-model-output-digest"),
)
S1_JN_MATERIALIZER_OUTPUT_SCHEMA = (
    (
        "model_invocation",
        ("materialized_field", "receptor_distribution", "step_time", "geometry_digest"),
    ),
    (
        "integrity_record",
        ("common_exposure_digest", "private_prestate_digest", "materialized_input_digest", "orchestration_control_digest"),
    ),
)
S1_JN_FIELD_PAYLOAD_SCHEMA = (
    ("schema_id", "mcm.s1jn.complete-field.v1"),
    ("layer", ("layer_id", "sample_offsets", "periodic_axes", "receptor_dock_ids", "neurons")),
    ("docks", ("dock_id", "modality_id", "receptor_geometry_id", "pairs")),
    ("last_distribution", "null-or-complete-ReceptorDistribution-canonical-payload"),
    ("substrate", "null-or-complete-MCMSubstrateState-canonical-payload"),
    ("development", "null-or-complete-MCMLocalDevelopmentState-canonical-payload"),
)
S1_JN_PRESTATE_OPERATION_RULES = (
    "INITIAL_REGISTERED_SH-requires-ordinal-one-P_IE-source-and-replaces-only-S-H-with-the-registered-P_IE-values",
    "CARRY_PRIOR_SH-requires-noninitial-P_IE-and-preserves-the-complete-input-field-by-identity",
    "APPLY_BOUNDARY_2N-requires-the-exact-two-node-source-role-and-replaces-only-S-H",
    "APPLY_BOUNDARY_3N-requires-one-exact-three-node-source-role-and-replaces-only-S-H",
    "all-replacement-operations-preserve-layer-and-neuron-identities-perceptions-docks-time-M-L-and-other-private-state",
    "no-operation-consumes-time-calls-a-model-or-reads-a-result-threshold",
)
S1_JN_PROVENANCE_RULES = (
    "ordinal-one-requires-null-prior-envelope-and-output-digests-and-a-fresh-field",
    "every-later-ordinal-requires-the-exact-prior-S1-JK-envelope-digest-and-recorded-prior-output-digest",
    "every-later-input-field-last-distribution-must-end-at-the-current-S1-JK-start-tick-on-the-same-clock",
    "P_IE-carry-prestate-source-digest-additionally-equals-the-prior-envelope-digest",
    "boundary-source-digests-identify-only-the-registered-S-H-fixture-not-the-private-carried-state",
)
S1_JN_DISTRIBUTION_AND_TIME_RULES = (
    "construct-one-ReceptorContactFrame-from-the-exact-width-matching-completion-fixture",
    "wrap-it-in-one-DistributedReceptorContact-with-the-exact-dock-id",
    "construct-one-ReceptorDistribution-with-field-time-exactly-equal-to-the-S1-JK-step-window",
    "construct-one-MCMFieldStepTime-exactly-equal-to-that-field-time-and-the-S1-JK-rate",
    "require-carriers-dock-map-neurons-node-order-contact-width-and-geometry-to-match-completely",
)
S1_JN_CANONICAL_DIGEST_API = (
    ("canonicalize_number", "finite-binary64-negative-zero-to-positive-zero"),
    ("canonicalize_value", "recursive-primitives-tuples-to-lists-and-mappings-with-sorted-string-keys"),
    ("canonical_json", "UTF-8-allow_nan_false-sort_keys_true-separators-comma-colon"),
    ("canonical_sha256", "lowercase-sixty-four-hex-character-SHA-256"),
)
S1_JN_VALIDATION_PHASES = (
    "validate-contract-source-exact-envelope-membership-digest-and-sequence-predecessor",
    "validate-model-role-private-state-schema-field-identity-geometry-and-fresh-or-carried-provenance",
    "build-and-cross-model-gate-the-common-exposure-payload-and-digest-before-state-transformation",
    "build-the-private-prestate-payload-and-digest-without-cross-model-equality-testing",
    "apply-exactly-one-registered-prestate-operation-and-verify-all-required-preservations",
    "construct-and-validate-distribution-step-time-and-four-field-model-invocation",
    "build-wrapper-only-materialized-input-and-orchestration-control-digests",
    "return-one-complete-immutable-record-or-one-public-materialization-error-with-no-partial-output",
)
S1_JN_ERROR_BOUNDARY = (
    ("public_error", "DTS1CommonIntervalMaterializationError"),
    ("translated_sources", ("contract", "field", "neuron", "layer", "substrate", "development", "receptor", "distribution", "time", "boundary", "canonicalization")),
    ("partial_output", False),
    ("retry_or_repair", False),
)
S1_JN_TECHNICAL_TEST_MATRIX = (
    ("T01", "exact-two-node-identity-fixture"),
    ("T02", "exact-three-node-identity-fixture"),
    ("T03", "all-seven-private-state-schema-roles"),
    ("T04", "exact-twenty-three-envelope-object-registration"),
    ("T05", "fresh-field-ordinal-one-preconditions"),
    ("T06", "noninitial-prior-envelope-and-output-provenance"),
    ("T07", "P_IE-initial-S-H-replacement"),
    ("T08", "P_IE-complete-carry-by-identity"),
    ("T09", "P_IH-two-node-boundary-preservation"),
    ("T10", "P_IK-P_IN-three-node-boundary-preservation"),
    ("T11", "width-specific-distribution-and-monotonic-time"),
    ("T12", "common-exposure-cross-model-equality-matrix"),
    ("T13", "private-prestate-no-cross-model-equality-gate"),
    ("T14", "four-model-invocation-fields-and-all-exclusions"),
    ("T15", "four-wrapper-integrity-digest-roles"),
    ("T16", "negative-zero-and-nonfinite-canonicalization"),
    ("T17", "identity-geometry-dock-carrier-and-source-mismatch-failures"),
    ("T18", "sequence-order-carry-clock-and-prior-output-mismatch-failures"),
    ("T19", "determinism-input-immutability-and-no-partial-output"),
    ("T20", "no-model-adapter-runtime-export-or-field-step"),
)
S1_JN_FORBIDDEN_INTERPRETATIONS = (
    "implemented-executable-materialized-or-numerically-admissible-common-envelope",
    "adapter-implemented-baseline-case-unblocked-or-model-executed",
    "baseline-fit-baseline-closure-candidate-superiority-memory-learning-or-artificial-intelligence",
)
S1_JN_DECISION = (
    "FINITE_COMMON_INTERVAL_MATERIALIZATION_IDENTITIES_AND_API_BOUND_NO_IMPLEMENTATION_OR_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JNFiniteMaterializationSchemaContract:
    contract_id: str
    source_s1jm_digest: str
    source_s1jk_digest: str
    field_identity_fixtures: tuple[tuple[object, ...], ...]
    receptor_completion_fixtures: tuple[tuple[object, ...], ...]
    fresh_field_rules: tuple[str, ...]
    private_state_schemas: tuple[tuple[str, tuple[str, ...]], ...]
    envelope_fixture_object_schema: tuple[str, ...]
    materializer_input_schema: tuple[tuple[str, str], ...]
    materializer_output_schema: tuple[tuple[str, tuple[str, ...]], ...]
    field_payload_schema: tuple[tuple[str, object], ...]
    prestate_operation_rules: tuple[str, ...]
    provenance_rules: tuple[str, ...]
    distribution_and_time_rules: tuple[str, ...]
    canonical_digest_api: tuple[tuple[str, str], ...]
    validation_phases: tuple[str, ...]
    error_boundary: tuple[tuple[str, object], ...]
    technical_test_matrix: tuple[tuple[str, str], ...]
    forbidden_interpretations: tuple[str, ...]
    geometry_fixture_count: int
    model_role_count: int
    technical_test_count: int
    complete_identity_and_api_schema_bound: bool
    common_interval_fixture_implemented: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    private_pure_materializer_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_JN_CONTRACT_ID
            or self.source_s1jm_digest != S1_JN_SOURCE_S1JM_DIGEST
            or self.source_s1jk_digest != S1_JN_SOURCE_S1JK_DIGEST
            or self.field_identity_fixtures != S1_JN_FIELD_IDENTITY_FIXTURES
            or self.receptor_completion_fixtures
            != S1_JN_RECEPTOR_COMPLETION_FIXTURES
            or self.fresh_field_rules != S1_JN_FRESH_FIELD_RULES
            or self.private_state_schemas != S1_JN_PRIVATE_STATE_SCHEMAS
            or self.envelope_fixture_object_schema
            != S1_JN_ENVELOPE_FIXTURE_OBJECT_SCHEMA
            or self.materializer_input_schema != S1_JN_MATERIALIZER_INPUT_SCHEMA
            or self.materializer_output_schema != S1_JN_MATERIALIZER_OUTPUT_SCHEMA
            or self.field_payload_schema != S1_JN_FIELD_PAYLOAD_SCHEMA
            or self.prestate_operation_rules != S1_JN_PRESTATE_OPERATION_RULES
            or self.provenance_rules != S1_JN_PROVENANCE_RULES
            or self.distribution_and_time_rules
            != S1_JN_DISTRIBUTION_AND_TIME_RULES
            or self.canonical_digest_api != S1_JN_CANONICAL_DIGEST_API
            or self.validation_phases != S1_JN_VALIDATION_PHASES
            or self.error_boundary != S1_JN_ERROR_BOUNDARY
            or self.technical_test_matrix != S1_JN_TECHNICAL_TEST_MATRIX
            or self.forbidden_interpretations != S1_JN_FORBIDDEN_INTERPRETATIONS
            or self.geometry_fixture_count != 2
            or self.model_role_count != 7
            or self.technical_test_count != 20
            or self.complete_identity_and_api_schema_bound is not True
            or self.common_interval_fixture_implemented is not False
            or self.adapters_implemented is not False
            or self.baseline_models_executed is not False
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.private_pure_materializer_implementation_authorized_next_stage
            is not True
            or self.decision != S1_JN_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JNFiniteMaterializationSchemaContractError(
                "S1-JN weakened the finite materialization identity and API schema"
            )


def build_dts1_s1jn_finite_materialization_schema_contract(
) -> DTS1S1JNFiniteMaterializationSchemaContract:
    """Bind exact identities and pure API without implementing materialization."""

    source = build_dts1_s1jm_exposure_prestate_integrity_contract()
    fixture_source = build_dts1_s1jk_corrected_monotonic_interval_contract()
    values = {
        "contract_id": S1_JN_CONTRACT_ID,
        "source_s1jm_digest": source.contract_digest,
        "source_s1jk_digest": fixture_source.contract_digest,
        "field_identity_fixtures": S1_JN_FIELD_IDENTITY_FIXTURES,
        "receptor_completion_fixtures": S1_JN_RECEPTOR_COMPLETION_FIXTURES,
        "fresh_field_rules": S1_JN_FRESH_FIELD_RULES,
        "private_state_schemas": S1_JN_PRIVATE_STATE_SCHEMAS,
        "envelope_fixture_object_schema": S1_JN_ENVELOPE_FIXTURE_OBJECT_SCHEMA,
        "materializer_input_schema": S1_JN_MATERIALIZER_INPUT_SCHEMA,
        "materializer_output_schema": S1_JN_MATERIALIZER_OUTPUT_SCHEMA,
        "field_payload_schema": S1_JN_FIELD_PAYLOAD_SCHEMA,
        "prestate_operation_rules": S1_JN_PRESTATE_OPERATION_RULES,
        "provenance_rules": S1_JN_PROVENANCE_RULES,
        "distribution_and_time_rules": S1_JN_DISTRIBUTION_AND_TIME_RULES,
        "canonical_digest_api": S1_JN_CANONICAL_DIGEST_API,
        "validation_phases": S1_JN_VALIDATION_PHASES,
        "error_boundary": S1_JN_ERROR_BOUNDARY,
        "technical_test_matrix": S1_JN_TECHNICAL_TEST_MATRIX,
        "forbidden_interpretations": S1_JN_FORBIDDEN_INTERPRETATIONS,
        "geometry_fixture_count": len(S1_JN_FIELD_IDENTITY_FIXTURES),
        "model_role_count": len(S1_JN_PRIVATE_STATE_SCHEMAS),
        "technical_test_count": len(S1_JN_TECHNICAL_TEST_MATRIX),
        "complete_identity_and_api_schema_bound": True,
        "common_interval_fixture_implemented": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "private_pure_materializer_implementation_authorized_next_stage": True,
        "decision": S1_JN_DECISION,
    }
    return DTS1S1JNFiniteMaterializationSchemaContract(
        **values, contract_digest=_digest(values)
    )
