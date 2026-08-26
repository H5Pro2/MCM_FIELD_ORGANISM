"""Static S1-JZ finite API contract for one-replica orchestration."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jn_finite_materialization_schema_contract import (
    S1_JN_FIELD_IDENTITY_FIXTURES,
)
from .dynamic_substrate_s1jt_finite_adapter_payload_contract import (
    S1_JT_B6_SPEC_DIGEST,
)
from .dynamic_substrate_s1jv_finite_geometry_digest_mapping_contract import (
    S1_JV_GEOMETRY_DIGEST_MAPPINGS,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_REPLICA_RECORDS,
    build_dts1_s1jx_sequence_carry_orchestration_contract,
)
from .dynamic_substrate_s1jy_orchestrator_api_readiness_precheck import (
    build_dts1_s1jy_orchestrator_api_readiness_precheck,
)
from .dynamic_substrate_dts1_private_baseline_adapters import (
    S1_JW_CONFIGURATION_DIGESTS,
)


class DTS1S1JZFiniteOrchestratorAPIContractError(ValueError):
    """Raised when the finite S1-JZ runner API contract is weakened."""


S1_JZ_CONTRACT_ID = "dynamic-substrate.finite-one-replica-orchestrator-api.s1jz.v1"
S1_JZ_SOURCE_S1JY_DIGEST = (
    "e383b88f95ed6f19b8e31cfcaf892f87dc26f642edee326fde70252340750eb7"
)
S1_JZ_SOURCE_S1JX_DIGEST = (
    "4bbf3bfb4997fe7e5ad3364276f127d6a8eb53c6b2452c0b4cac387e097cb5a8"
)
S1_JZ_RUNNER_INPUT_SCHEMA = (
    ("schema_id", "mcm.s1jz.one-replica-runner-input.v1"),
    ("fields", ("schema_id", "replica_id")),
    ("replica_id", "one-exact-S1-JX-replica-id"),
    ("excluded", ("field", "private_state", "profile_result", "candidate_data", "threshold", "retry")),
)
S1_JZ_FRESH_FIELD_SCHEMA = (
    "schema_id",
    "field_id",
    "layer_id",
    "geometry_id",
    "modality_id",
    "sample_offsets",
    "periodic_axes",
    "neurons",
    "dock",
    "last_distribution",
    "substrate",
    "development",
)
S1_JZ_FRESH_NEURON_FIELDS = (
    "node_id",
    "position",
    "activation",
    "afterimage",
    "perception_tick",
    "receptor_contact",
    "local_samples",
)


def _canonical(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, dict):
        return {key: _canonical(value[key]) for key in sorted(value)}
    raise DTS1S1JZFiniteOrchestratorAPIContractError(
        "S1-JZ canonical payload contains an object"
    )


def _digest(value: object) -> str:
    encoded = json.dumps(
        _canonical(value),
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _substrate_payload(role: str, node_ids: tuple[str, ...], internal: str):
    if role not in ("B3", "B4", "B5", "B6"):
        return None
    arm_id, rate = {
        "B3": ("mcm.s1jt.b3.local-leaky", 1.0),
        "B4": ("mcm.s1jt.b4.linear-coupled", 1.0),
        "B5": ("mcm.s1jt.b5.full", 1.0),
        "B6": ("mcm.s1jt.b6.const-v", 0.5),
    }[role]
    return (
        ("arm", (
            ("arm_id", arm_id),
            ("lambda_sm_per_second", rate),
            ("kappa", 0.5),
            ("eta", 1.0),
            ("initial_total_mass", 1.0),
        )),
        ("masses", tuple((node_id, 1.0 / len(node_ids)) for node_id in node_ids)),
        ("edge_inventory_digest", internal),
    )


def _substrate_state_digest(payload) -> str:
    values = dict(payload)
    arm = dict(values["arm"])
    canonical = {
        "arm": arm,
        "masses": [
            {"neuron_id": node_id, "mass": mass}
            for node_id, mass in values["masses"]
        ],
        "edge_inventory_digest": values["edge_inventory_digest"],
    }
    return _digest(canonical)


def _private_payload(role: str, node_ids: tuple[str, ...], internal: str, substrate):
    config = S1_JW_CONFIGURATION_DIGESTS[role]
    if role == "B1":
        rate = 1.2 if len(node_ids) == 2 else 1.1
        edge_rates = tuple(
            {
                "first_node_id": node_ids[index],
                "second_node_id": node_ids[index + 1],
                "rate_per_second": rate,
            }
            for index in range(len(node_ids) - 1)
        )
        state = (
            ("fixed_adapter_payload", {
                "schema_id": "mcm.s1jt.b1-fixed-adapter.v1",
                "backreaction_enabled": True,
                "base_rate_per_second": 1.0,
                "edge_inventory_digest": internal,
                "edge_rates": edge_rates,
            }),
            ("fixed_adapter_configuration_digest", config),
        )
    elif role == "B2":
        state = (
            ("complete_L_state_payload", {
                "schema_id": "mcm.s1jt.b2-private-L.v1",
                "entries": tuple(
                    {"node_id": node_id, "value": 0.0}
                    for node_id in node_ids
                ),
            }),
            ("B2_configuration_digest", config),
        )
    else:
        rows = [("embedded_M_state_digest", _substrate_state_digest(substrate))]
        if role == "B6":
            rows.append(("frozen_CONST_V_spec_digest", S1_JT_B6_SPEC_DIGEST))
        rows.append((f"{role}_configuration_digest", config))
        state = tuple(rows)
    canonical_state = {"model_role": role, "state": dict(state)}
    return state, _digest(canonical_state)


def _fresh_state_records() -> tuple[tuple[object, ...], ...]:
    mappings = {row[0]: row for row in S1_JV_GEOMETRY_DIGEST_MAPPINGS}
    records = []
    for role in ("B1", "B2", "B3", "B4", "B5", "B6"):
        for identity in S1_JN_FIELD_IDENTITY_FIXTURES:
            geometry_role = identity[0]
            mapping = mappings[geometry_role]
            node_ids = mapping[5]
            substrate = _substrate_payload(role, node_ids, mapping[7])
            field_payload = (
                ("schema_id", "mcm.s1jz.fresh-field.v1"),
                ("field_id", identity[1]),
                ("layer_id", identity[2]),
                ("geometry_id", identity[3]),
                ("modality_id", identity[4]),
                ("sample_offsets", identity[6]),
                ("periodic_axes", identity[7]),
                ("neurons", tuple(
                    (
                        ("node_id", node_id),
                        ("position", position),
                        ("activation", 0.0),
                        ("afterimage", 0.0),
                        ("perception_tick", 0),
                        ("receptor_contact", 0.0),
                        ("local_samples", ()),
                    )
                    for node_id, position in identity[5]
                )),
                ("dock", (
                    ("dock_id", identity[9]),
                    ("receptor_geometry_id", identity[10]),
                    ("pairs", identity[11]),
                )),
                ("last_distribution", None),
                ("substrate", substrate),
                ("development", None),
            )
            private_payload, private_digest = _private_payload(
                role, node_ids, mapping[7], substrate
            )
            records.append(
                (
                    role,
                    geometry_role,
                    node_ids,
                    mapping[6],
                    mapping[7],
                    field_payload,
                    _digest(field_payload),
                    private_payload,
                    private_digest,
                )
            )
    return tuple(records)


S1_JZ_FRESH_STATE_RECORDS = _fresh_state_records()
S1_JZ_CHECKPOINT_SCHEMA = (
    ("schema_id", "mcm.s1jz.replica-checkpoint.v1"),
    ("fields", (
        "schema_id", "replica_id", "sequence_key", "sequence_digest",
        "ordinal", "interval_digest", "node_ids", "activation", "afterimage",
        "complete_field_digest", "private_state_digest", "adapter_output_digest",
    )),
    ("vector_order", "canonical-node-order"),
    ("capture", "only-after-registered-true-checkpoint"),
)


def _component_indices() -> tuple[tuple[object, ...], ...]:
    rows = []

    def append_block(profile, comparisons, node_ids):
        offset = 0
        for left_key, left_ordinal, right_key, right_ordinal in comparisons:
            for channel in ("activation", "afterimage"):
                for node_id in node_ids:
                    rows.append((
                        profile, offset, left_key, left_ordinal, right_key,
                        right_ordinal, channel, node_id, "left-minus-right",
                    ))
                    offset += 1

    append_block(
        "P_IE_CAUSAL_TWO_SUBSTEP",
        (("P_IE_F_HIGH", 1, "P_IE_R_HIGH", 1), ("P_IE_F_HIGH", 2, "P_IE_R_HIGH", 2)),
        ("node-a", "node-b"),
    )
    append_block(
        "P_IH_ATTENUATION",
        (("P_IH_A_A_A", 2, "P_IH_A_A_A", 1), ("P_IH_A_A_A", 3, "P_IH_A_A_A", 1)),
        ("node-a", "node-b"),
    )
    append_block(
        "P_IK_INTERFERENCE",
        (("P_IK_A_B_A", 4, "P_IK_A_GAP_A", 4),),
        ("node-a", "node-b", "node-c"),
    )
    append_block(
        "P_IN_RELEASE_REUSE",
        (("P_IN_RECOVERY_ON", 4, "P_IN_RECOVERY_OFF", 4),),
        ("node-a", "node-b", "node-c"),
    )
    return tuple(rows)


S1_JZ_COMPONENT_INDEX_RECORDS = _component_indices()
S1_JZ_REPLICA_OUTPUT_SCHEMA = (
    ("schema_id", "mcm.s1jz.complete-replica-output.v1"),
    ("fields", (
        "schema_id", "replica_id", "model_role", "profile_block", "refinement",
        "sequence_digests", "checkpoints", "signed_components",
        "adapter_diagnostics", "output_digest",
    )),
    ("signed_component_order", "exact-S1-JZ-component-index-order-for-profile"),
    ("publication", "one-complete-output-or-one-error-with-no-partial-value"),
)
S1_JZ_CANONICAL_DIGEST_RULES = (
    "finite-binary64-negative-zero-normalized-to-positive-zero",
    "recursive-primitives-tuples-to-arrays-and-mappings-sorted-by-string-key",
    "UTF-8-JSON-allow_nan_false-sort_keys_true-compact-separators",
    "lowercase-sixty-four-hex-SHA-256",
)
S1_JZ_ERROR_BOUNDARY = (
    ("public_error", "DTS1OneReplicaOrchestratorError"),
    ("partial_output", False),
    ("retry", False),
    ("repair", False),
    ("wrapped_errors", (
        "DTS1CommonIntervalMaterializationError",
        "DTS1PrivateBaselineAdapterError",
        "DTS1S1JZFiniteOrchestratorAPIContractError",
        "SharedMCMFieldError",
        "MCMSubstrateStateError",
        "ValueError",
        "TypeError",
    )),
)
S1_JZ_TECHNICAL_EXEMPLAR = (
    ("replica_id", "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2"),
    ("model_role", "B1"),
    ("profile_block", "P_IE_CAUSAL_TWO_SUBSTEP"),
    ("refinement", 2),
    ("sequence_keys", ("P_IE_F_HIGH", "P_IE_R_HIGH")),
    ("interval_calls_per_repeat", 4),
    ("checkpoint_count_per_repeat", 4),
    ("signed_component_count", 8),
    ("deterministic_repeat_count", 2),
    ("maximum_total_interval_calls", 8),
)
S1_JZ_TECHNICAL_TEST_MATRIX = tuple(
    (f"T{index:02d}", role)
    for index, role in enumerate((
        "exact-S1-JY-and-S1-JX-source-binding",
        "two-field-runner-input-and-forbidden-caller-data",
        "twelve-complete-fresh-state-records",
        "two-and-three-node-complete-fresh-field-payloads",
        "B1-two-and-three-node-fixed-internal-digest-payloads",
        "B2-two-and-three-node-uniform-zero-L-payloads",
        "B3-through-B6-uniform-M-arm-and-private-digest-payloads",
        "versioned-checkpoint-schema-and-canonical-node-vectors",
        "exact-eight-eight-six-six-component-index-records",
        "checkpoint-channel-node-and-left-minus-right-order",
        "versioned-complete-replica-output-schema",
        "canonical-digest-and-single-atomic-error-boundary",
        "one-B1-P-IE-r2-technical-exemplar-and-eight-call-budget",
        "deterministic-tamper-evident-contract",
        "no-initializer-runner-materializer-adapter-or-profile-execution",
    ), start=1)
)
S1_JZ_FORBIDDEN_INTERPRETATIONS = (
    "initializer-or-runner-implemented-or-any-technical-replica-executed",
    "profile-case-matrix-comparison-baseline-closure-rejection-or-candidate-superiority",
    "runtime-readiness-research-evidence-or-physical-timescale",
    "memory-learning-semantics-consciousness-experience-understanding-organic-property-or-artificial-intelligence",
)
S1_JZ_DECISION = (
    "FINITE_ONE_REPLICA_RUNNER_API_INITIALIZERS_COMPONENT_INDEX_OUTPUT_AND_ERROR_CONTRACT_BOUND_NO_EXECUTION"
)


@dataclass(frozen=True, slots=True)
class DTS1S1JZFiniteOrchestratorAPIContract:
    contract_id: str
    source_s1jy_digest: str
    source_s1jx_digest: str
    runner_input_schema: tuple[tuple[str, object], ...]
    fresh_field_schema: tuple[str, ...]
    fresh_neuron_fields: tuple[str, ...]
    fresh_state_records: tuple[tuple[object, ...], ...]
    checkpoint_schema: tuple[tuple[str, object], ...]
    component_index_records: tuple[tuple[object, ...], ...]
    replica_output_schema: tuple[tuple[str, object], ...]
    canonical_digest_rules: tuple[str, ...]
    error_boundary: tuple[tuple[str, object], ...]
    technical_exemplar: tuple[tuple[str, object], ...]
    technical_test_matrix: tuple[tuple[str, str], ...]
    forbidden_interpretations: tuple[str, ...]
    fresh_state_record_count: int
    component_index_count: int
    technical_test_count: int
    finite_orchestrator_api_bound: bool
    initializer_implemented: bool
    orchestrator_implemented: bool
    technical_replicas_executed: int
    profile_cases_executed: int
    baseline_interval_calls_executed: int
    runtime_integration_present: bool
    research_execution_permitted: bool
    research_field_steps_executed: int
    one_replica_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {f.name: getattr(self, f.name) for f in fields(self) if f.name != "contract_digest"}
        if (
            self.contract_id != S1_JZ_CONTRACT_ID
            or self.source_s1jy_digest != S1_JZ_SOURCE_S1JY_DIGEST
            or self.source_s1jx_digest != S1_JZ_SOURCE_S1JX_DIGEST
            or self.runner_input_schema != S1_JZ_RUNNER_INPUT_SCHEMA
            or self.fresh_field_schema != S1_JZ_FRESH_FIELD_SCHEMA
            or self.fresh_neuron_fields != S1_JZ_FRESH_NEURON_FIELDS
            or self.fresh_state_records != S1_JZ_FRESH_STATE_RECORDS
            or self.checkpoint_schema != S1_JZ_CHECKPOINT_SCHEMA
            or self.component_index_records != S1_JZ_COMPONENT_INDEX_RECORDS
            or self.replica_output_schema != S1_JZ_REPLICA_OUTPUT_SCHEMA
            or self.canonical_digest_rules != S1_JZ_CANONICAL_DIGEST_RULES
            or self.error_boundary != S1_JZ_ERROR_BOUNDARY
            or self.technical_exemplar != S1_JZ_TECHNICAL_EXEMPLAR
            or self.technical_test_matrix != S1_JZ_TECHNICAL_TEST_MATRIX
            or self.forbidden_interpretations != S1_JZ_FORBIDDEN_INTERPRETATIONS
            or self.fresh_state_record_count != 12
            or self.component_index_count != 28
            or self.technical_test_count != 15
            or self.finite_orchestrator_api_bound is not True
            or self.initializer_implemented is not False
            or self.orchestrator_implemented is not False
            or self.technical_replicas_executed != 0
            or self.profile_cases_executed != 0
            or self.baseline_interval_calls_executed != 0
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.research_field_steps_executed != 0
            or self.one_replica_implementation_authorized_next_stage is not True
            or self.decision != S1_JZ_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JZFiniteOrchestratorAPIContractError(
                "S1-JZ weakened the finite orchestrator API contract"
            )


def build_dts1_s1jz_finite_orchestrator_api_contract(
) -> DTS1S1JZFiniteOrchestratorAPIContract:
    """Bind the complete API without constructing or executing a runner."""

    audit = build_dts1_s1jy_orchestrator_api_readiness_precheck()
    orchestration = build_dts1_s1jx_sequence_carry_orchestration_contract()
    exemplar_id = dict(S1_JZ_TECHNICAL_EXEMPLAR)["replica_id"]
    if sum(row[0] == exemplar_id for row in S1_JX_REPLICA_RECORDS) != 1:
        raise DTS1S1JZFiniteOrchestratorAPIContractError(
            "technical exemplar is not one unique S1-JX replica"
        )
    values = {
        "contract_id": S1_JZ_CONTRACT_ID,
        "source_s1jy_digest": audit.audit_digest,
        "source_s1jx_digest": orchestration.contract_digest,
        "runner_input_schema": S1_JZ_RUNNER_INPUT_SCHEMA,
        "fresh_field_schema": S1_JZ_FRESH_FIELD_SCHEMA,
        "fresh_neuron_fields": S1_JZ_FRESH_NEURON_FIELDS,
        "fresh_state_records": S1_JZ_FRESH_STATE_RECORDS,
        "checkpoint_schema": S1_JZ_CHECKPOINT_SCHEMA,
        "component_index_records": S1_JZ_COMPONENT_INDEX_RECORDS,
        "replica_output_schema": S1_JZ_REPLICA_OUTPUT_SCHEMA,
        "canonical_digest_rules": S1_JZ_CANONICAL_DIGEST_RULES,
        "error_boundary": S1_JZ_ERROR_BOUNDARY,
        "technical_exemplar": S1_JZ_TECHNICAL_EXEMPLAR,
        "technical_test_matrix": S1_JZ_TECHNICAL_TEST_MATRIX,
        "forbidden_interpretations": S1_JZ_FORBIDDEN_INTERPRETATIONS,
        "fresh_state_record_count": len(S1_JZ_FRESH_STATE_RECORDS),
        "component_index_count": len(S1_JZ_COMPONENT_INDEX_RECORDS),
        "technical_test_count": len(S1_JZ_TECHNICAL_TEST_MATRIX),
        "finite_orchestrator_api_bound": True,
        "initializer_implemented": False,
        "orchestrator_implemented": False,
        "technical_replicas_executed": 0,
        "profile_cases_executed": 0,
        "baseline_interval_calls_executed": 0,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "research_field_steps_executed": 0,
        "one_replica_implementation_authorized_next_stage": True,
        "decision": S1_JZ_DECISION,
    }
    return DTS1S1JZFiniteOrchestratorAPIContract(
        **values, contract_digest=_digest(values)
    )
