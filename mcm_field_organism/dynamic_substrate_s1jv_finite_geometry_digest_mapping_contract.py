"""Static S1-JV outer-to-internal geometry digest mapping contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jn_finite_materialization_schema_contract import (
    S1_JN_FIELD_IDENTITY_FIXTURES,
    build_dts1_s1jn_finite_materialization_schema_contract,
)
from .dynamic_substrate_s1ju_geometry_digest_role_precheck import (
    S1_JU_GEOMETRY_DIGEST_RECORDS,
    build_dts1_s1ju_geometry_digest_role_precheck,
)


class DTS1S1JVFiniteGeometryDigestMappingContractError(ValueError):
    """Raised when the finite S1-JV digest mapping is weakened."""


S1_JV_CONTRACT_ID = "dynamic-substrate.finite-geometry-digest-mapping.s1jv.v1"
S1_JV_SOURCE_S1JU_DIGEST = (
    "77ce8f1e14f6db2bbfa4bfeacaf911a9b20a5b5a59849c1d376649b79ed482c3"
)
S1_JV_SOURCE_S1JN_DIGEST = (
    "b0edec20c6d27d98ba8a523c3034d8890b01cfe514eede1d72d05c2e548dd281"
)
S1_JV_MAPPING_FIELDS = (
    "geometry_role",
    "field_id",
    "layer_id",
    "geometry_id",
    "node_inventory",
    "canonical_node_ids",
    "outer_common_geometry_digest",
    "internal_edge_inventory_digest",
)
S1_JV_GEOMETRY_DIGEST_MAPPINGS = (
    (
        "TWO_NODE_OPEN_LINE",
        "mcm.s1jn.field.2n",
        "mcm.s1jn.layer.2n",
        "mcm.s1jn.geometry.2n",
        (("node-a", (0,)), ("node-b", (1,))),
        ("node-a", "node-b"),
        "5f7bdc4e0e657a613262c237fbd3bdd5a8bff0073be0aa5890ce6b4f58ae810d",
        "77595b855f2d1ed9b208508fea1225364162ad5b8156c9532bbff52fc9ee6b72",
    ),
    (
        "THREE_NODE_OPEN_LINE",
        "mcm.s1jn.field.3n",
        "mcm.s1jn.layer.3n",
        "mcm.s1jn.geometry.3n",
        (("node-a", (0,)), ("node-b", (1,)), ("node-c", (2,))),
        ("node-a", "node-b", "node-c"),
        "2efcf504573780a314947cb0fba3c64e152ff5f776666af7d4283b75b564aa49",
        "2536e5e2bc075c703ef9d707132b97ce626857ab7f7fe70d0080d7b7de84273a",
    ),
)
S1_JV_SELECTION_RULES = (
    "select-exactly-one-registered-row-by-field-id-and-complete-ordered-node-inventory",
    "field-id-and-node-inventory-must-agree-with-layer-id-geometry-id-and-canonical-node-ids-in-the-same-row",
    "reject-unknown-duplicate-partial-reordered-or-cross-paired-identities-before-any-adapter-object",
    "never-select-by-model-role-profile-control-label-configuration-refinement-or-observed-output",
)
S1_JV_ROLE_DIGEST_BINDINGS = (
    (
        "B1",
        "outer-common-digest-validates-the-model-invocation-against-the-selected-row",
        "fixed-adapter-payload-edge_inventory_digest-is-exactly-the-selected-internal-digest",
        "both-digest-roles-are-checked-and-never-compared-for-equality",
    ),
    (
        "B2",
        "outer-common-digest-validates-the-model-invocation-against-the-selected-row",
        "selected-internal-digest-validates-the-complete-materialized-layer-inventory",
        "S2ReferenceState-receives-no-edge-digest-field",
    ),
    (
        "B3-B6",
        "outer-common-digest-validates-the-model-invocation-against-the-selected-row",
        "embedded-M-state-edge_inventory_digest-is-exactly-the-selected-internal-digest",
        "both-digest-roles-are-checked-and-never-compared-for-equality",
    ),
)
S1_JV_S1JT_CORRECTION_OVERLAY = (
    "S1-JT-remains-an-immutable-historical-source-contract",
    "S1-JV-supersedes-only-the-ambiguous-B1-edge_inventory_digest-role-wording",
    "all-S1-JT-rates-payload-shapes-runtime-records-diagnostics-output-and-error-rules-remain-bit-identical",
    "every-future-adapter-contract-or-implementation-must-bind-S1-JV-in-addition-to-S1-JT",
)
S1_JV_FAIL_CLOSED_RULES = (
    "reject-an-outer-digest-that-does-not-equal-the-selected-row-outer-digest",
    "reject-an-internal-digest-that-does-not-equal-the-selected-row-internal-digest",
    "reject-an-outer-digest-used-in-any-B1-or-M-state-internal-edge-digest-field",
    "reject-an-internal-digest-used-as-the-model-facing-common-exposure-geometry-digest",
    "reject-any-attempt-to-equate-drop-recompute-relabel-repair-or-infer-either-role",
    "publish-no-partial-adapter-context-output-diagnostic-or-private-state-on-failure",
)
S1_JV_TECHNICAL_TEST_MATRIX = tuple(
    (f"T{index:02d}", role)
    for index, role in enumerate(
        (
            "exact-S1-JU-and-S1-JN-source-binding",
            "exact-two-node-field-and-node-inventory-key",
            "exact-three-node-field-and-node-inventory-key",
            "two-finite-unequal-outer-internal-digest-pairs",
            "unique-complete-selection-and-no-role-or-control-selection",
            "B1-outer-validation-and-internal-payload-binding",
            "B2-dual-role-validation-without-S2-digest-injection",
            "B3-through-B6-outer-and-embedded-M-internal-validation",
            "S1-JT-ambiguity-only-correction-and-value-preservation",
            "cross-pair-role-swap-partial-and-unknown-fail-closed-rules",
            "deterministic-tamper-evident-contract-digest",
            "no-adapter-kernel-runtime-profile-or-research-execution",
        ),
        start=1,
    )
)
S1_JV_FORBIDDEN_INTERPRETATIONS = (
    "adapter-context-payload-output-or-baseline-implemented-constructed-or-executed",
    "digest-pair-equality-interchangeability-or-new-geometry-registration",
    "numerical-admissibility-profile-fit-baseline-closure-rejection-or-candidate-superiority",
    "memory-learning-semantics-consciousness-experience-understanding-organic-property-or-artificial-intelligence",
)
S1_JV_DECISION = (
    "FINITE_OUTER_TO_INTERNAL_GEOMETRY_DIGEST_MAPPING_BOUND_NO_IMPLEMENTATION_OR_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JVFiniteGeometryDigestMappingContract:
    contract_id: str
    source_s1ju_digest: str
    source_s1jn_digest: str
    mapping_fields: tuple[str, ...]
    geometry_digest_mappings: tuple[tuple[object, ...], ...]
    selection_rules: tuple[str, ...]
    role_digest_bindings: tuple[tuple[str, str, str, str], ...]
    s1jt_correction_overlay: tuple[str, ...]
    fail_closed_rules: tuple[str, ...]
    technical_test_matrix: tuple[tuple[str, str], ...]
    forbidden_interpretations: tuple[str, ...]
    mapping_count: int
    unique_selection_key_count: int
    unequal_digest_pair_count: int
    finite_digest_mapping_bound: bool
    adapters_implemented: bool
    baseline_kernels_called: bool
    profile_cases_executed: int
    runtime_integration_present: bool
    research_execution_permitted: bool
    research_field_steps_executed: int
    corrected_adapter_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_JV_CONTRACT_ID
            or self.source_s1ju_digest != S1_JV_SOURCE_S1JU_DIGEST
            or self.source_s1jn_digest != S1_JV_SOURCE_S1JN_DIGEST
            or self.mapping_fields != S1_JV_MAPPING_FIELDS
            or self.geometry_digest_mappings != S1_JV_GEOMETRY_DIGEST_MAPPINGS
            or self.selection_rules != S1_JV_SELECTION_RULES
            or self.role_digest_bindings != S1_JV_ROLE_DIGEST_BINDINGS
            or self.s1jt_correction_overlay != S1_JV_S1JT_CORRECTION_OVERLAY
            or self.fail_closed_rules != S1_JV_FAIL_CLOSED_RULES
            or self.technical_test_matrix != S1_JV_TECHNICAL_TEST_MATRIX
            or self.forbidden_interpretations != S1_JV_FORBIDDEN_INTERPRETATIONS
            or self.mapping_count != 2
            or self.unique_selection_key_count != 2
            or self.unequal_digest_pair_count != 2
            or self.finite_digest_mapping_bound is not True
            or self.adapters_implemented is not False
            or self.baseline_kernels_called is not False
            or self.profile_cases_executed != 0
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.research_field_steps_executed != 0
            or self.corrected_adapter_implementation_authorized_next_stage is not True
            or self.decision != S1_JV_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JVFiniteGeometryDigestMappingContractError(
                "S1-JV weakened the finite geometry digest mapping"
            )


def build_dts1_s1jv_finite_geometry_digest_mapping_contract(
) -> DTS1S1JVFiniteGeometryDigestMappingContract:
    """Bind two digest mappings without constructing or running adapters."""

    stop_source = build_dts1_s1ju_geometry_digest_role_precheck()
    identity_source = build_dts1_s1jn_finite_materialization_schema_contract()
    identity_keys = {
        (row[1], row[5]) for row in S1_JN_FIELD_IDENTITY_FIXTURES
    }
    mapping_keys = {
        (row[1], row[4]) for row in S1_JV_GEOMETRY_DIGEST_MAPPINGS
    }
    stop_pairs = {(row[0], row[1], row[2], row[3]) for row in S1_JU_GEOMETRY_DIGEST_RECORDS}
    mapping_pairs = {(row[0], row[5], row[6], row[7]) for row in S1_JV_GEOMETRY_DIGEST_MAPPINGS}
    if identity_keys != mapping_keys or stop_pairs != mapping_pairs:
        raise DTS1S1JVFiniteGeometryDigestMappingContractError(
            "S1-JV mappings do not exactly match their registered sources"
        )
    values = {
        "contract_id": S1_JV_CONTRACT_ID,
        "source_s1ju_digest": stop_source.audit_digest,
        "source_s1jn_digest": identity_source.contract_digest,
        "mapping_fields": S1_JV_MAPPING_FIELDS,
        "geometry_digest_mappings": S1_JV_GEOMETRY_DIGEST_MAPPINGS,
        "selection_rules": S1_JV_SELECTION_RULES,
        "role_digest_bindings": S1_JV_ROLE_DIGEST_BINDINGS,
        "s1jt_correction_overlay": S1_JV_S1JT_CORRECTION_OVERLAY,
        "fail_closed_rules": S1_JV_FAIL_CLOSED_RULES,
        "technical_test_matrix": S1_JV_TECHNICAL_TEST_MATRIX,
        "forbidden_interpretations": S1_JV_FORBIDDEN_INTERPRETATIONS,
        "mapping_count": len(S1_JV_GEOMETRY_DIGEST_MAPPINGS),
        "unique_selection_key_count": len(mapping_keys),
        "unequal_digest_pair_count": sum(row[6] != row[7] for row in S1_JV_GEOMETRY_DIGEST_MAPPINGS),
        "finite_digest_mapping_bound": True,
        "adapters_implemented": False,
        "baseline_kernels_called": False,
        "profile_cases_executed": 0,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "research_field_steps_executed": 0,
        "corrected_adapter_implementation_authorized_next_stage": True,
        "decision": S1_JV_DECISION,
    }
    return DTS1S1JVFiniteGeometryDigestMappingContract(
        **values, contract_digest=_digest(values)
    )
