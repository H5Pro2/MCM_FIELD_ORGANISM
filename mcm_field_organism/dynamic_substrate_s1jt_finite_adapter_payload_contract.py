"""Static S1-JT finite private adapter payload and output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    S1_JA_CONFIGURATION_RECORDS,
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from .dynamic_substrate_s1jn_finite_materialization_schema_contract import (
    S1_JN_FIELD_PAYLOAD_SCHEMA,
    build_dts1_s1jn_finite_materialization_schema_contract,
)
from .dynamic_substrate_s1js_adapter_payload_readiness_precheck import (
    build_dts1_s1js_adapter_payload_readiness_precheck,
)


class DTS1S1JTFiniteAdapterPayloadContractError(ValueError):
    """Raised when the finite S1-JT payload contract is weakened."""


S1_JT_CONTRACT_ID = "dynamic-substrate.finite-adapter-payloads.s1jt.v1"
S1_JT_SOURCE_S1JS_DIGEST = (
    "196bce51777bf841476aae35f156ba6affe8a04fd5c9b1d14985559c97da8324"
)
S1_JT_SOURCE_S1JN_DIGEST = (
    "b0edec20c6d27d98ba8a523c3034d8890b01cfe514eede1d72d05c2e548dd281"
)
S1_JT_SOURCE_S1JA_DIGEST = (
    "331168f2a6f937b454742d2be57de3f022f75ca5ca521fbff31f101bd4ea1fbc"
)
S1_JT_CONFIGURATION_DIGESTS = tuple(
    (role, digest) for role, _source, _payload, digest in S1_JA_CONFIGURATION_RECORDS
    if role != "DTS1"
)
S1_JT_COMMON_FAST_RUNTIME_RECORD = (
    ("substrate_config_type", "NeutralLocalFieldSubstrateConfig"),
    ("response_time_seconds", 1.0),
    ("afterimage_config_type", "NeutralFastAfterimageConfig"),
    ("afterimage_time_constant_seconds", 0.5),
    ("dissipation_config_type", "NeutralFieldDissipationConfig"),
    ("leak_rate_per_second", 0.0),
)
S1_JT_B1_FIXED_ADAPTER_SCHEMA = (
    ("schema_id", "mcm.s1jt.b1-fixed-adapter.v1"),
    ("fields", (
        "schema_id",
        "backreaction_enabled",
        "base_rate_per_second",
        "edge_inventory_digest",
        "edge_rates",
    )),
    ("edge_rate_fields", ("first_node_id", "second_node_id", "rate_per_second")),
    ("backreaction_enabled", True),
    ("base_rate_per_second", 1.0),
    ("two_node_edges", (("node-a", "node-b", 1.2),)),
    ("three_node_edges", (("node-a", "node-b", 1.1), ("node-b", "node-c", 1.1))),
    ("derivation", "rate=1/response_time*(1+0.5*fixed_conductive/capacity_per_node)"),
    ("roundtrip", "payload-to-DTS1BackreactionResult-to-exact-canonical-payload"),
)
S1_JT_B2_L_SCHEMA = (
    ("schema_id", "mcm.s1jt.b2-private-L.v1"),
    ("fields", ("schema_id", "entries")),
    ("entry_fields", ("node_id", "value")),
    ("order", "strict-canonical-field-node-order"),
    ("shape", "exactly-one-entry-for-every-field-node-with-no-extra-node"),
    ("domain", "finite-binary64-closed-minus-one-plus-one"),
    ("initial", "bit-exact-positive-zero-for-every-node"),
    ("roundtrip", "payload-to-S2ReferenceState-development-to-exact-canonical-payload"),
)
S1_JT_B2_FIELD_COMMIT = (
    "read-S-H-from-the-materialized-field-and-L-from-the-complete-private-payload-in-canonical-node-order",
    "derive-the-symmetric-generator-and-boundary-only-from-common-field-geometry-distribution-and-the-bound-fast-response-record",
    "call-model-b2-once-over-the-complete-step-time-elapsed-seconds-with-the-exact-S1-JA-B2-config",
    "commit-result-S-H-through-one-SharedMCMField.advance-using-the-original-distribution-and-step-time",
    "the-commit-preserves-field-layer-dock-and-neuron-identities-and-produces-the-standard-next-tick-perceptions-local-samples-and-last-distribution",
    "return-result-development-as-the-complete-next-B2-private-L-payload-with-the-unchanged-B2-configuration-digest",
)
S1_JT_F3_RUNTIME_RECORDS = (
    (
        "B3",
        "mcm.s1jt.b3.local-leaky",
        1.0,
        0.5,
        1.0,
        1.0,
        "compute_mcm_f3_local_leaky_baseline",
        "e80711e16fbac78279f5b8ab43031ff71b1adea181db15fecfb03b22551679d9",
    ),
    (
        "B4",
        "mcm.s1jt.b4.linear-coupled",
        1.0,
        0.5,
        1.0,
        1.0,
        "compute_mcm_f3_linear_coupled_baseline",
        "fa36b68073f4bef8405496b1dd42cd2fd85af6d5bfedd99146efb25443ca6f06",
    ),
    (
        "B5",
        "mcm.s1jt.b5.full",
        1.0,
        0.5,
        1.0,
        1.0,
        "compute_mcm_f3_coupling",
        "f7c463f8c4d167704d6c150610b2678ecac83e4df19042843b70c62253f02225",
    ),
    (
        "B6",
        "mcm.s1jt.b6.const-v",
        0.5,
        0.5,
        1.0,
        1.0,
        "compute_w7n_coupling_baseline:const-v",
        "dba608c0c01cf8b5080b6735bd71e8952fd6b3a4a382223619cda28ad832b30d",
    ),
)
S1_JT_F3_RUNTIME_RECORD_FIELDS = (
    "role",
    "arm_id",
    "lambda_sm_per_second",
    "kappa",
    "eta",
    "initial_total_mass",
    "calculator_identity",
    "configuration_digest",
)
S1_JT_B6_SPEC_PAYLOAD = (
    ("schema_id", "mcm.s1jt.b6-const-v-spec.v1"),
    ("model_id", "const-v"),
    ("equation_id", "baseline.k2-f3.const-v.v1"),
    ("equation_contract", "use=compute_mcm_f3_coupling;lambda_sm=V_initial"),
    ("persistent_scalars_per_neuron", 1),
    ("parameter_bindings", (("eta", 1.0), ("kappa", 0.5), ("lambda_sm", 0.5))),
    ("organism_runtime_allowed", False),
)
S1_JT_ROLE_PRIVATE_PAYLOAD_SCHEMAS = (
    ("B1", "fixed_adapter_payload", "mcm.s1jt.b1-fixed-adapter.v1", "fixed_adapter_configuration_digest"),
    ("B2", "complete_L_state_payload", "mcm.s1jt.b2-private-L.v1", "B2_configuration_digest"),
    ("B3", "embedded_M_state_digest", "complete-field-MCMSubstrateState-v1", "B3_configuration_digest"),
    ("B4", "embedded_M_state_digest", "complete-field-MCMSubstrateState-v1", "B4_configuration_digest"),
    ("B5", "embedded_M_state_digest", "complete-field-MCMSubstrateState-v1", "B5_configuration_digest"),
    ("B6", "embedded_M_state_digest", "complete-field-MCMSubstrateState-v1-plus-mcm.s1jt.b6-const-v-spec.v1", "B6_configuration_digest"),
)
S1_JT_PRIVATE_STATE_RETURN_RULES = (
    "B1-returns-the-bit-identical-fixed-adapter-payload-and-configuration-digest",
    "B2-returns-the-complete-node-bound-result-L-payload-and-unchanged-configuration-digest",
    "B3-through-B5-return-the-result-field-substrate-digest-and-unchanged-role-configuration-digest",
    "B6-returns-the-result-field-substrate-digest-and-unchanged-frozen-spec-and-configuration-digests",
    "every-returned-private-state-must-pass-the-exact-S1-JN-role-key-order-and-S1-JT-payload-roundtrip",
)
S1_JT_DIAGNOSTIC_UNION = (
    (
        "B1_EXACT",
        "mcm.s1jt.diagnostics.b1-exact.v1",
        ("method_id", "maximum_abs_activation", "maximum_abs_afterimage"),
        ("method_id=exact-spectral", "finite-nonnegative-maxima"),
    ),
    (
        "B2_EXACT",
        "mcm.s1jt.diagnostics.b2-exact.v1",
        ("method_id", "partition_error", "maximum_abs_activation", "maximum_abs_afterimage", "maximum_abs_development"),
        ("method_id=exact-matrix-exponential", "partition_error=0.0", "finite-nonnegative-values"),
    ),
    (
        "B3_B6_F3",
        "mcm.s1jt.diagnostics.f3-runtime.v1",
        (
            "method_id",
            "substep_count",
            "refinement",
            "safe_step_seconds",
            "maximum_step_seconds",
            "maximum_mass_error",
            "minimum_mass",
            "maximum_abs_activation",
            "maximum_abs_afterimage",
        ),
        ("exact-MCMF3AdvanceDiagnostics-field-order", "finite-domain-validation"),
    ),
)
S1_JT_OUTPUT_PAYLOAD_SCHEMA = (
    ("schema_id", "mcm.s1jt.complete-baseline-adapter-output.v1"),
    ("fields", ("schema_id", "model_role", "complete_field", "next_private_state", "diagnostics")),
    ("complete_field", S1_JN_FIELD_PAYLOAD_SCHEMA),
    ("next_private_state", "exact-S1-JN-role-key-order-with-S1-JT-finite-value-payload"),
    ("diagnostics", "exactly-one-S1-JT-diagnostic-union-variant-for-the-role"),
    ("excluded", ("control_label", "envelope", "sequence", "ordinal", "checkpoint", "integrity_digests", "candidate_sidecar")),
)
S1_JT_CANONICAL_DIGEST_API = (
    ("numbers", "finite-binary64-negative-zero-to-positive-zero"),
    ("values", "recursive-primitives-tuples-to-lists-mappings-sorted-string-keys"),
    ("json", "UTF-8-allow_nan_false-sort_keys_true-separators-comma-colon"),
    ("digest", "lowercase-sixty-four-hex-SHA-256"),
)
S1_JT_VALIDATION_ORDER = (
    "role-control-mode-control-label-and-exact-S1-JA-configuration-digest",
    "private-payload-schema-id-exact-keys-order-domain-and-roundtrip",
    "model-invocation-field-geometry-distribution-step-time-and-common-fast-runtime-record",
    "typed-runtime-object-construction-and-reverse-payload-identity",
    "kernel-output-complete-field-time-state-invariants-and-role-diagnostics",
    "next-private-state-roundtrip-complete-output-canonicalization-digest-and-atomic-publication",
)
S1_JT_ERROR_BOUNDARY = (
    ("public_error", "DTS1PrivateBaselineAdapterError"),
    ("partial_output", False),
    ("retry", False),
    ("repair", False),
    ("wrapped_error_families", (
        "DTS1BackreactionError",
        "DTS1CoupledStepError",
        "S2ReferenceBaselineError",
        "MCMF3RuntimeError",
        "MCMF3BaselineCouplingError",
        "MCMF3CouplingError",
        "W7NCapacityFunctionBaselineError",
        "MCMSubstrateStateError",
        "SharedMCMFieldError",
        "MCMNeuronLayerError",
        "ValueError",
        "TypeError",
    )),
)
S1_JT_TECHNICAL_TEST_MATRIX = tuple(
    (f"T{index:02d}", role)
    for index, role in enumerate((
        "source-and-six-configuration-digest-binding",
        "common-fast-runtime-record",
        "B1-two-node-payload-roundtrip",
        "B1-three-node-payload-roundtrip",
        "B1-reject-rate-edge-geometry-or-config-drift",
        "B2-two-node-L-roundtrip",
        "B2-three-node-L-roundtrip",
        "B2-field-commit-and-private-L-return",
        "B2-reject-node-order-shape-domain-or-config-drift",
        "B3-runtime-record-M-and-config-roundtrip",
        "B4-runtime-record-M-and-config-roundtrip",
        "B5-runtime-record-M-and-config-roundtrip",
        "B6-frozen-spec-payload-digest-and-typed-roundtrip",
        "B6-runtime-record-M-spec-and-config-roundtrip",
        "three-diagnostic-union-variants",
        "complete-output-payload-and-excluded-control-data",
        "canonical-number-json-and-output-digest-determinism",
        "validation-order-single-error-and-atomic-no-output",
        "exact-control-bit-identity-payload-excludes-label",
        "no-adapter-kernel-runtime-profile-or-research-execution",
    ), start=1)
)
S1_JT_FORBIDDEN_INTERPRETATIONS = (
    "implemented-constructed-or-executed-adapter-context-output-or-baseline",
    "numerical-admissibility-profile-fit-baseline-closure-rejection-or-candidate-superiority",
    "runtime-readiness-completed-twenty-four-case-matrix-or-physical-timescale",
    "memory-learning-semantics-consciousness-experience-understanding-organic-property-or-artificial-intelligence",
)
S1_JT_DECISION = (
    "FINITE_PRIVATE_ADAPTER_PAYLOAD_ROUNDTRIP_OUTPUT_AND_ERROR_SCHEMAS_BOUND_NO_IMPLEMENTATION_OR_EXECUTION"
)


def _canonicalize(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise DTS1S1JTFiniteAdapterPayloadContractError(
                "canonical numbers must be finite"
            )
        return 0.0 if value == 0.0 else value
    if isinstance(value, (tuple, list)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise DTS1S1JTFiniteAdapterPayloadContractError(
                "canonical mapping keys must be strings"
            )
        return {key: _canonicalize(value[key]) for key in sorted(value)}
    raise DTS1S1JTFiniteAdapterPayloadContractError(
        "canonical payload contains a non-value object"
    )


def _digest(payload: object) -> str:
    encoded = json.dumps(
        _canonicalize(payload),
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


S1_JT_B6_SPEC_DIGEST = _digest(dict(S1_JT_B6_SPEC_PAYLOAD))


@dataclass(frozen=True, slots=True)
class DTS1S1JTFiniteAdapterPayloadContract:
    contract_id: str
    source_s1js_digest: str
    source_s1jn_digest: str
    source_s1ja_digest: str
    configuration_digests: tuple[tuple[str, str], ...]
    common_fast_runtime_record: tuple[tuple[str, object], ...]
    b1_fixed_adapter_schema: tuple[tuple[str, object], ...]
    b2_l_schema: tuple[tuple[str, object], ...]
    b2_field_commit: tuple[str, ...]
    f3_runtime_record_fields: tuple[str, ...]
    f3_runtime_records: tuple[tuple[object, ...], ...]
    b6_spec_payload: tuple[tuple[str, object], ...]
    b6_spec_digest: str
    role_private_payload_schemas: tuple[tuple[str, str, str, str], ...]
    private_state_return_rules: tuple[str, ...]
    diagnostic_union: tuple[tuple[str, str, tuple[str, ...], tuple[str, ...]], ...]
    output_payload_schema: tuple[tuple[str, object], ...]
    canonical_digest_api: tuple[tuple[str, str], ...]
    validation_order: tuple[str, ...]
    error_boundary: tuple[tuple[str, object], ...]
    technical_test_matrix: tuple[tuple[str, str], ...]
    forbidden_interpretations: tuple[str, ...]
    private_payload_schema_count: int
    diagnostic_variant_count: int
    technical_test_count: int
    finite_payload_and_output_contract_bound: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    private_adapter_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_JT_CONTRACT_ID
            or self.source_s1js_digest != S1_JT_SOURCE_S1JS_DIGEST
            or self.source_s1jn_digest != S1_JT_SOURCE_S1JN_DIGEST
            or self.source_s1ja_digest != S1_JT_SOURCE_S1JA_DIGEST
            or self.configuration_digests != S1_JT_CONFIGURATION_DIGESTS
            or self.common_fast_runtime_record != S1_JT_COMMON_FAST_RUNTIME_RECORD
            or self.b1_fixed_adapter_schema != S1_JT_B1_FIXED_ADAPTER_SCHEMA
            or self.b2_l_schema != S1_JT_B2_L_SCHEMA
            or self.b2_field_commit != S1_JT_B2_FIELD_COMMIT
            or self.f3_runtime_record_fields != S1_JT_F3_RUNTIME_RECORD_FIELDS
            or self.f3_runtime_records != S1_JT_F3_RUNTIME_RECORDS
            or self.b6_spec_payload != S1_JT_B6_SPEC_PAYLOAD
            or self.b6_spec_digest != S1_JT_B6_SPEC_DIGEST
            or self.role_private_payload_schemas != S1_JT_ROLE_PRIVATE_PAYLOAD_SCHEMAS
            or self.private_state_return_rules != S1_JT_PRIVATE_STATE_RETURN_RULES
            or self.diagnostic_union != S1_JT_DIAGNOSTIC_UNION
            or self.output_payload_schema != S1_JT_OUTPUT_PAYLOAD_SCHEMA
            or self.canonical_digest_api != S1_JT_CANONICAL_DIGEST_API
            or self.validation_order != S1_JT_VALIDATION_ORDER
            or self.error_boundary != S1_JT_ERROR_BOUNDARY
            or self.technical_test_matrix != S1_JT_TECHNICAL_TEST_MATRIX
            or self.forbidden_interpretations != S1_JT_FORBIDDEN_INTERPRETATIONS
            or self.private_payload_schema_count != 6
            or self.diagnostic_variant_count != 3
            or self.technical_test_count != 20
            or self.finite_payload_and_output_contract_bound is not True
            or self.adapters_implemented is not False
            or self.baseline_models_executed is not False
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.private_adapter_implementation_authorized_next_stage is not True
            or self.decision != S1_JT_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JTFiniteAdapterPayloadContractError(
                "S1-JT weakened the finite adapter payload contract"
            )


def build_dts1_s1jt_finite_adapter_payload_contract(
) -> DTS1S1JTFiniteAdapterPayloadContract:
    """Bind finite adapter payloads without constructing or running adapters."""

    source = build_dts1_s1js_adapter_payload_readiness_precheck()
    materialization_source = build_dts1_s1jn_finite_materialization_schema_contract()
    configuration_source = build_dts1_s1ja_finite_configuration_matrix_contract()
    values = {
        "contract_id": S1_JT_CONTRACT_ID,
        "source_s1js_digest": source.audit_digest,
        "source_s1jn_digest": materialization_source.contract_digest,
        "source_s1ja_digest": configuration_source.contract_digest,
        "configuration_digests": S1_JT_CONFIGURATION_DIGESTS,
        "common_fast_runtime_record": S1_JT_COMMON_FAST_RUNTIME_RECORD,
        "b1_fixed_adapter_schema": S1_JT_B1_FIXED_ADAPTER_SCHEMA,
        "b2_l_schema": S1_JT_B2_L_SCHEMA,
        "b2_field_commit": S1_JT_B2_FIELD_COMMIT,
        "f3_runtime_record_fields": S1_JT_F3_RUNTIME_RECORD_FIELDS,
        "f3_runtime_records": S1_JT_F3_RUNTIME_RECORDS,
        "b6_spec_payload": S1_JT_B6_SPEC_PAYLOAD,
        "b6_spec_digest": S1_JT_B6_SPEC_DIGEST,
        "role_private_payload_schemas": S1_JT_ROLE_PRIVATE_PAYLOAD_SCHEMAS,
        "private_state_return_rules": S1_JT_PRIVATE_STATE_RETURN_RULES,
        "diagnostic_union": S1_JT_DIAGNOSTIC_UNION,
        "output_payload_schema": S1_JT_OUTPUT_PAYLOAD_SCHEMA,
        "canonical_digest_api": S1_JT_CANONICAL_DIGEST_API,
        "validation_order": S1_JT_VALIDATION_ORDER,
        "error_boundary": S1_JT_ERROR_BOUNDARY,
        "technical_test_matrix": S1_JT_TECHNICAL_TEST_MATRIX,
        "forbidden_interpretations": S1_JT_FORBIDDEN_INTERPRETATIONS,
        "private_payload_schema_count": len(S1_JT_ROLE_PRIVATE_PAYLOAD_SCHEMAS),
        "diagnostic_variant_count": len(S1_JT_DIAGNOSTIC_UNION),
        "technical_test_count": len(S1_JT_TECHNICAL_TEST_MATRIX),
        "finite_payload_and_output_contract_bound": True,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "private_adapter_implementation_authorized_next_stage": True,
        "decision": S1_JT_DECISION,
    }
    return DTS1S1JTFiniteAdapterPayloadContract(
        **values, contract_digest=_digest(values)
    )
