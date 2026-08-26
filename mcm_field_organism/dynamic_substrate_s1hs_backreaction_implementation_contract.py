"""S1-HS static implementation contract for the pure DTS-1 backreaction."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HSBackreactionImplementationContractError(ValueError):
    """Raised when the S1-HS private implementation boundary is weakened."""


S1_HS_CONTRACT_ID = "dynamic-substrate.backreaction-implementation.s1hs.v1"
S1_HS_SOURCE_S1HR_AUDIT_DIGEST = (
    "7e5b2ce00da55279f4eabffb11396b0239a6a32f2f5dda06c1bb6744fa3679e1"
)
S1_HS_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HS_TARGET_MODULE = "mcm_field_organism.dynamic_substrate_dts1_backreaction"
S1_HS_ERROR_TYPE = "DTS1BackreactionError(ValueError)"
S1_HS_ENTRY_POINTS = (
    (
        "adapter",
        "compute_dts1_edge_rates(layer,anatomy,substrate_config,"
        "backreaction_enabled=bool)->DTS1BackreactionResult",
    ),
    (
        "generator",
        "build_dts1_diffusion_generator(layer,adapter_result)->float64-square-matrix",
    ),
)
S1_HS_ADAPTER_INPUTS = (
    ("layer", "one immutable MCMNeuronLayer with complete symmetric adjacency"),
    ("anatomy", "one immutable valid DTS1ResourceAnatomy"),
    (
        "substrate_config",
        "one existing NeutralLocalFieldSubstrateConfig supplying only r_0",
    ),
    ("backreaction_enabled", "one explicit strict boolean ablation control"),
)
S1_HS_ADAPTER_OUTPUTS = (
    ("backreaction_enabled", "echoed strict boolean control"),
    ("base_rate_per_second", "one finite positive existing neutral rate"),
    ("edge_rates", "one immutable canonical DTS1BackreactionEdgeRate per edge"),
    ("edge_inventory_digest", "existing complete MCM edge identity"),
)
S1_HS_ADAPTER_PHASES = (
    "validate-layer-anatomy-config-and-strict-boolean-control",
    "require-exact-complete-edge-inventory-and-existing-digest-identity",
    "derive-capacity-by-node-without-copying-free-resource",
    "read-only-conductive-bound-resource-from-one-closed-anatomy",
    "compute-c_e-and-active-or-ablated-rate-per-canonical-edge",
    "validate-rate-range-and-return-one-new-immutable-ledger",
)
S1_HS_GENERATOR_PHASES = (
    "validate-adapter-ledger-against-complete-layer-geometry",
    "allocate-one-zero-float64-square-matrix",
    "book-each-undirected-rate-symmetrically-once",
    "book-negative-diagonal-edge-rate-at-both-endpoints",
    "validate-finiteness-symmetry-zero-row-sum-and-nonpositive-spectrum",
    "return-new-matrix-without-boundary-source-or-state-advance",
)
S1_HS_FORBIDDEN_SURFACES = (
    "calling-or-advancing-the-dts1-resource-step",
    "mutation-of-layer-anatomy-config-or-adapter-result",
    "reading-free-or-refractory-resource-in-the-rate-formula",
    "extra-gain-threshold-sign-label-modality-or-history-input",
    "receptor-boundary-afterimage-or-external-source-booking",
    "clipping-normalization-or-repair-of-invalid-rates-or-geometry",
    "runtime-snapshot-restore-runner-browser-audio-or-video-integration",
    "package-level-or-current-api-export",
)
S1_HS_TEST_MATRIX = (
    ("T01", "heterogeneous-capacity-active-rate-matches-s1hr-formula"),
    ("T02", "ablation-returns-exact-base-rate-with-identical-anatomy"),
    ("T03", "zero-conductive-binding-is-exactly-neutral"),
    ("T04", "maximum-valid-occupancy-attains-but-does-not-exceed-two-r_0"),
    ("T05", "same-b-different-refractory-partition-has-identical-immediate-rates"),
    ("T06", "complete-layer-anatomy-edge-inventory-and-digest-are-required"),
    ("T07", "invalid-control-config-anatomy-and-rate-values-fail-closed"),
    ("T08", "input-declaration-order-does-not-change-adapter-ledger"),
    ("T09", "all-adapter-inputs-remain-unchanged"),
    ("T10", "generator-is-finite-square-float64-and-symmetric"),
    ("T11", "generator-has-zero-row-sum-and-constant-field-nullspace"),
    ("T12", "generator-is-negative-semidefinite"),
    ("T13", "each-edge-flux-is-antisymmetric-and-sum-conserving"),
    ("T14", "incomplete-duplicate-or-foreign-rate-ledger-fails-closed"),
    ("T15", "adapter-does-not-call-resource-step-or-read-field-values"),
    ("T16", "no-runtime-boundary-io-snapshot-or-public-api-path-is-added"),
)
S1_HS_SUCCESS_BOUNDARY = (
    "pure-reader-and-generator-algebra-only",
    "instantaneous-fixed-adapter-equivalence-remains-true",
    "no-dts1-or-field-state-is-advanced",
    "no-functional-profile-or-baseline-separation-is-measured",
)
S1_HS_DECISION = "DTS1_PURE_BACKREACTION_CONTRACT_AND_TEST_MATRIX_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1HSBackreactionImplementationContract:
    contract_id: str
    source_s1hr_audit_digest: str
    candidate_id: str
    target_module: str
    error_type: str
    entry_points: tuple[tuple[str, str], ...]
    adapter_inputs: tuple[tuple[str, str], ...]
    adapter_outputs: tuple[tuple[str, str], ...]
    adapter_phases: tuple[str, ...]
    generator_phases: tuple[str, ...]
    forbidden_surfaces: tuple[str, ...]
    test_matrix: tuple[tuple[str, str], ...]
    success_boundary: tuple[str, ...]
    pure_adapter_required: bool
    pure_generator_required: bool
    existing_geometry_digest_required: bool
    exact_ablation_required: bool
    immutable_inputs_required: bool
    fail_before_output_required: bool
    implementation_authorized_next_stage: bool
    backreaction_implementation_present: bool
    coupled_integrator_selected: bool
    material_rate_values_selected: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    field_steps_executed: int
    functional_effect_proven: bool
    claims_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        test_ids = tuple(test_id for test_id, _ in self.test_matrix)
        if (
            self.contract_id != S1_HS_CONTRACT_ID
            or self.source_s1hr_audit_digest
            != S1_HS_SOURCE_S1HR_AUDIT_DIGEST
            or self.candidate_id != S1_HS_CANDIDATE_ID
            or self.target_module != S1_HS_TARGET_MODULE
            or self.error_type != S1_HS_ERROR_TYPE
            or self.entry_points != S1_HS_ENTRY_POINTS
            or self.adapter_inputs != S1_HS_ADAPTER_INPUTS
            or self.adapter_outputs != S1_HS_ADAPTER_OUTPUTS
            or self.adapter_phases != S1_HS_ADAPTER_PHASES
            or self.generator_phases != S1_HS_GENERATOR_PHASES
            or self.forbidden_surfaces != S1_HS_FORBIDDEN_SURFACES
            or self.test_matrix != S1_HS_TEST_MATRIX
            or test_ids != tuple(f"T{index:02d}" for index in range(1, 17))
            or self.success_boundary != S1_HS_SUCCESS_BOUNDARY
            or any(
                value is not True
                for value in (
                    self.pure_adapter_required,
                    self.pure_generator_required,
                    self.existing_geometry_digest_required,
                    self.exact_ablation_required,
                    self.immutable_inputs_required,
                    self.fail_before_output_required,
                    self.implementation_authorized_next_stage,
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
            or self.decision != S1_HS_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1HSBackreactionImplementationContractError(
                "S1-HS weakened the private pure-backreaction boundary"
            )


def build_dts1_s1hs_backreaction_implementation_contract(
) -> DTS1S1HSBackreactionImplementationContract:
    """Bind the future pure adapter and generator without implementing them."""

    values = {
        "contract_id": S1_HS_CONTRACT_ID,
        "source_s1hr_audit_digest": S1_HS_SOURCE_S1HR_AUDIT_DIGEST,
        "candidate_id": S1_HS_CANDIDATE_ID,
        "target_module": S1_HS_TARGET_MODULE,
        "error_type": S1_HS_ERROR_TYPE,
        "entry_points": S1_HS_ENTRY_POINTS,
        "adapter_inputs": S1_HS_ADAPTER_INPUTS,
        "adapter_outputs": S1_HS_ADAPTER_OUTPUTS,
        "adapter_phases": S1_HS_ADAPTER_PHASES,
        "generator_phases": S1_HS_GENERATOR_PHASES,
        "forbidden_surfaces": S1_HS_FORBIDDEN_SURFACES,
        "test_matrix": S1_HS_TEST_MATRIX,
        "success_boundary": S1_HS_SUCCESS_BOUNDARY,
        "pure_adapter_required": True,
        "pure_generator_required": True,
        "existing_geometry_digest_required": True,
        "exact_ablation_required": True,
        "immutable_inputs_required": True,
        "fail_before_output_required": True,
        "implementation_authorized_next_stage": True,
        "backreaction_implementation_present": False,
        "coupled_integrator_selected": False,
        "material_rate_values_selected": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_HS_DECISION,
    }
    return DTS1S1HSBackreactionImplementationContract(
        **values,
        contract_digest=_digest(values),
    )
