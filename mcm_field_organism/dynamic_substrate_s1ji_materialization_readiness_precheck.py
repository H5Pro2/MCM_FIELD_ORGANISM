"""Static S1-JI readiness precheck for common interval materialization."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jh_finite_common_interval_fixture_contract import (
    build_dts1_s1jh_finite_common_interval_fixture_contract,
)


class DTS1S1JIMaterializationReadinessPrecheckError(ValueError):
    """Raised when the fail-closed S1-JI finding is weakened."""


S1_JI_AUDIT_ID = "dynamic-substrate.materialization-readiness-precheck.s1ji.v1"
S1_JI_SOURCE_S1JH_DIGEST = (
    "740bcc9fe1f29258d68278ba78a58005ff46c1da548dcf3b465eb8b5f1ed9e56"
)
S1_JI_BOUND_SURFACES = (
    "seven-unique-orchestrator-sequences-and-twenty-three-envelope-fixtures",
    "two-canonical-open-line-geometries-and-six-S-H-prestate-sources",
    "two-width-specific-zero-contact-vectors-carrier-identities-and-source-windows",
    "one-profile-neutral-positive-MCMFieldStepTime-value",
    "candidate-only-P_IE-anatomy-and-P_IN-recovery-sidecars-outside-the-envelope",
    "finite-refinement-double-check-budget-and-old-field-vector-quarantine",
)
S1_JI_MISSING_MATERIALIZATION_BINDINGS = (
    (
        "RECEPTOR_DISTRIBUTION_IDENTITY",
        (
            "modality_id",
            "receptor_geometry_id",
            "dock_id",
            "carrier_to_neuron_pairs",
        ),
        "required-to-construct-and-validate-ReceptorContactFrame-DistributedReceptorContact-and-field-dock-alignment",
    ),
    (
        "FIELD_INPUT_AND_PRESTATE_API",
        (
            "complete_input_field_role",
            "prior_interval_digest_role",
            "initial-versus-carry-versus-boundary-dispatch",
            "model-owned-hidden-state-preservation-check",
        ),
        "required-to-materialize-S-H-without-creating-or-overwriting-baseline-owned-L-or-M-state",
    ),
    (
        "MODEL_FACING_INPUT_DIGEST_SCHEMA",
        (
            "canonical_field_payload",
            "canonical_distribution_payload",
            "canonical_step_time_payload",
            "geometry_digest_inclusion",
            "binary64_and-null-canonicalization",
        ),
        "required-to-produce-one-cross-model-comparable-input-digest-without-object-repr-or-process-identity",
    ),
    (
        "ATOMIC_OUTPUT_AND_ERROR_CONTRACT",
        (
            "immutable_fixture_object_schema",
            "model_facing_view_schema",
            "exception_translation",
            "no-partial-output-rule",
        ),
        "required-before-private-code-can-be-tested-fail-closed-as-one-pure-materialization",
    ),
)
S1_JI_CONSTRUCTOR_EVIDENCE = (
    "ReceptorContactFrame-requires-modality-geometry-snapshot-clock-window-carriers-and-values",
    "DistributedReceptorContact-requires-a-dock-id-in-addition-to-the-complete-frame",
    "ReceptorNeuronDockMap-requires-modality-receptor-geometry-and-carrier-to-neuron-pairs",
    "SharedMCMField-validates-distributed-docks-against-its-complete-existing-dock-map",
    "S1-JG-requires-a-canonical-input-digest-but-S1-JH-binds-no-canonical-model-facing-payload-schema",
)
S1_JI_INVALID_IMPLEMENTATION_SHORTCUTS = (
    "do-not-infer-modality-geometry-dock-or-neuron-identities-from-profile-or-sequence-labels",
    "do-not-copy-private-identifiers-from-old-candidate-audit-builders-as-implicit-common-values",
    "do-not-use-dataclass-repr-pickle-object-id-or-process-dependent-hashing",
    "do-not-drop-L-M-substrate-development-or-last-distribution-to-simplify-field-materialization",
    "do-not-implement-only-the-current-happy-path-and-defer-fail-closed-behavior",
)
S1_JI_CONSEQUENCES = (
    "zero-common-interval-fixture-or-model-facing-view-classes-are-implementation-ready",
    "zero-of-twenty-four-baseline-role-block-cases-are-unblocked",
    "all-S1-JH-values-sequences-digests-sidecars-budgets-and-quarantines-remain-bound",
    "S1-JG-information-barrier-remains-required-and-unweakened",
    "no-validity-baseline-or-candidate-result-can-be-decided",
)
S1_JI_NEXT_CONTRACT_REQUIREMENTS = (
    "bind-one-complete-profile-neutral-receptor-and-dock-identity-schema-for-each-geometry",
    "bind-the-exact-pure-materializer-input-output-and-carry-provenance-API",
    "bind-canonical-value-only-payloads-and-SHA-256-digests-for-field-distribution-time-and-model-view",
    "bind-atomic-validation-order-exception-surface-and-no-partial-output-rule",
    "retain-all-S1-JH-sequences-values-sidecars-budgets-and-claim-blocks-without-execution",
)
S1_JI_FORBIDDEN_INTERPRETATIONS = (
    "S1-JH-invalid-or-its-bound-values-rejected",
    "materializer-adapter-model-or-baseline-implemented-or-executed",
    "baseline-closure-candidate-superiority-memory-learning-or-artificial-intelligence",
)
S1_JI_DECISION = (
    "STOPP_PRIVATE_COMMON_INTERVAL_FIXTURE_IMPLEMENTATION_MATERIALIZATION_SCHEMA_INCOMPLETE"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JIMaterializationReadinessPrecheck:
    audit_id: str
    source_s1jh_digest: str
    bound_surfaces: tuple[str, ...]
    missing_materialization_bindings: tuple[tuple[str, tuple[str, ...], str], ...]
    constructor_evidence: tuple[str, ...]
    invalid_implementation_shortcuts: tuple[str, ...]
    consequences: tuple[str, ...]
    next_contract_requirements: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    missing_binding_group_count: int
    s1jh_remains_bound: bool
    information_barrier_preserved: bool
    materialization_schema_complete: bool
    common_interval_fixture_implemented: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    corrected_materialization_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_JI_AUDIT_ID
            or self.source_s1jh_digest != S1_JI_SOURCE_S1JH_DIGEST
            or self.bound_surfaces != S1_JI_BOUND_SURFACES
            or self.missing_materialization_bindings
            != S1_JI_MISSING_MATERIALIZATION_BINDINGS
            or self.constructor_evidence != S1_JI_CONSTRUCTOR_EVIDENCE
            or self.invalid_implementation_shortcuts
            != S1_JI_INVALID_IMPLEMENTATION_SHORTCUTS
            or self.consequences != S1_JI_CONSEQUENCES
            or self.next_contract_requirements != S1_JI_NEXT_CONTRACT_REQUIREMENTS
            or self.forbidden_interpretations != S1_JI_FORBIDDEN_INTERPRETATIONS
            or self.missing_binding_group_count != 4
            or self.s1jh_remains_bound is not True
            or self.information_barrier_preserved is not True
            or self.materialization_schema_complete is not False
            or self.common_interval_fixture_implemented is not False
            or self.adapters_implemented is not False
            or self.baseline_models_executed is not False
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.corrected_materialization_contract_authorized_next_stage is not True
            or self.decision != S1_JI_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1JIMaterializationReadinessPrecheckError(
                "S1-JI weakened the materialization readiness STOPP"
            )


def build_dts1_s1ji_materialization_readiness_precheck(
) -> DTS1S1JIMaterializationReadinessPrecheck:
    """Stop implementation while the pure materialization schema is incomplete."""

    source = build_dts1_s1jh_finite_common_interval_fixture_contract()
    values = {
        "audit_id": S1_JI_AUDIT_ID,
        "source_s1jh_digest": source.contract_digest,
        "bound_surfaces": S1_JI_BOUND_SURFACES,
        "missing_materialization_bindings": S1_JI_MISSING_MATERIALIZATION_BINDINGS,
        "constructor_evidence": S1_JI_CONSTRUCTOR_EVIDENCE,
        "invalid_implementation_shortcuts": S1_JI_INVALID_IMPLEMENTATION_SHORTCUTS,
        "consequences": S1_JI_CONSEQUENCES,
        "next_contract_requirements": S1_JI_NEXT_CONTRACT_REQUIREMENTS,
        "forbidden_interpretations": S1_JI_FORBIDDEN_INTERPRETATIONS,
        "missing_binding_group_count": len(S1_JI_MISSING_MATERIALIZATION_BINDINGS),
        "s1jh_remains_bound": True,
        "information_barrier_preserved": True,
        "materialization_schema_complete": False,
        "common_interval_fixture_implemented": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "corrected_materialization_contract_authorized_next_stage": True,
        "decision": S1_JI_DECISION,
    }
    return DTS1S1JIMaterializationReadinessPrecheck(
        **values, audit_digest=_digest(values)
    )
