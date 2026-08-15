"""S1-HO static implementation contract and test matrix for one DTS-1 step."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HOStepImplementationContractError(ValueError):
    """Raised when the S1-HO implementation boundary is weakened."""


S1_HO_CONTRACT_ID = "dynamic-substrate.step-implementation.s1ho.v1"
S1_HO_SOURCE_S1HN_CONTRACT_DIGEST = (
    "816313ec363b54e258e8c89f51fcd3cffb4ea1fcdccdb40702951985c2f5f62f"
)
S1_HO_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HO_TARGET_MODULE = "mcm_field_organism.dynamic_substrate_dts1_step"
S1_HO_ERROR_TYPE = "DTS1StepError(ValueError)"
S1_HO_ENTRY_POINT = (
    "compute_dts1_closed_prestate_step(anatomy, edge_participations, "
    "elapsed_time, rates)->DTS1StepResult"
)
S1_HO_INPUT_TYPES = (
    (
        "anatomy",
        "DTS1ResourceAnatomy with fixed capacities and complete edge resources",
    ),
    (
        "edge_participations",
        "one immutable canonical DTS1EdgeParticipation per anatomy edge",
    ),
    ("elapsed_time", "finite nonnegative nonboolean explicit interval"),
    (
        "rates",
        "three finite nonnegative global content-free DTS1StepRates values",
    ),
)
S1_HO_OUTPUT_TYPES = (
    ("next_anatomy", "new validated DTS1ResourceAnatomy"),
    ("edge_transfers", "canonical immutable DTS1EdgeTransfer ledger"),
    ("input_anatomy_digest", "technical SHA-256 identity"),
    ("output_anatomy_digest", "technical SHA-256 identity"),
    ("maximum_local_ledger_residual", "passive diagnostic only"),
    ("global_ledger_residual", "passive diagnostic only"),
)
S1_HO_ALGORITHM_PHASES = (
    "validate-and-canonicalize-complete-immutable-inputs",
    "derive-free-resource-from-one-closed-anatomy-prestate",
    "compute-interval-fractions-with-negative-expm1",
    "compute-all-edge-engagement-offers-from-the-closed-prestate",
    "compute-all-node-demands-with-math-fsum",
    "compute-all-local-admission-factors-before-any-transfer",
    "compute-engagement-turnover-and-recovery-ledger",
    "atomically-build-one-new-complete-anatomy",
    "validate-output-ledgers-and-build-passive-diagnostics",
)
S1_HO_FORBIDDEN_SURFACES = (
    "mutation-of-input-anatomy-or-participation-ledger",
    "stored-free-resource-or-hidden-history",
    "implicit-clock-default-step-or-call-counter",
    "field-state-layer-adapter-or-backreaction-input",
    "same-step-reuse-of-produced-resource",
    "edge-order-dependent-partial-admission",
    "post-hoc-clipping-normalization-or-state-repair",
    "filesystem-network-randomness-environment-or-process-access",
    "package-current-api-snapshot-runner-browser-audio-or-video-export",
)
S1_HO_TEST_MATRIX = (
    ("T01", "zero-interval-exact-identity-and-zero-transfer-ledger"),
    ("T02", "all-zero-rates-exact-identity"),
    ("T03", "zero-participation-blocks-only-engagement"),
    ("T04", "zero-free-endpoint-blocks-engagement"),
    ("T05", "single-edge-binding-matches-analytic-interval-fraction"),
    ("T06", "single-edge-turnover-matches-analytic-interval-fraction"),
    ("T07", "single-edge-recovery-matches-analytic-interval-fraction"),
    ("T08", "shared-node-competition-is-simultaneous-without-overdraw"),
    ("T09", "edge-declaration-order-does-not-change-result-or-digest"),
    ("T10", "local-and-global-resource-identities-remain-bounded"),
    ("T11", "new-binding-and-new-refractory-are-not-reused-same-step"),
    ("T12", "inputs-remain-unchanged-and-repeated-call-is-deterministic"),
    ("T13", "invalid-scalars-and-participations-fail-closed"),
    ("T14", "missing-duplicate-extra-or-noncanonical-edge-fails-closed"),
    ("T15", "invalid-or-overallocated-anatomy-fails-before-calculation"),
    ("T16", "step-refinement-approaches-the-s1hm-continuous-family"),
    ("T17", "module-has-no-field-runtime-io-or-public-api-reachability"),
)
S1_HO_SUCCESS_BOUNDARY = (
    "pure-step-algebra-only",
    "no-field-effect-or-functional-profile-measured",
    "no-material-parameter-corridor-selected",
    "no-runtime-or-research-execution-authorized",
)
S1_HO_DECISION = "DTS1_PURE_STEP_IMPLEMENTATION_CONTRACT_AND_TEST_MATRIX_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1HOStepImplementationContract:
    contract_id: str
    source_s1hn_contract_digest: str
    candidate_id: str
    target_module: str
    error_type: str
    entry_point: str
    input_types: tuple[tuple[str, str], ...]
    output_types: tuple[tuple[str, str], ...]
    algorithm_phases: tuple[str, ...]
    forbidden_surfaces: tuple[str, ...]
    test_matrix: tuple[tuple[str, str], ...]
    success_boundary: tuple[str, ...]
    pure_function_required: bool
    complete_edge_ledger_required: bool
    immutable_inputs_required: bool
    canonical_output_required: bool
    fail_before_output_required: bool
    diagnostics_are_passive: bool
    use_existing_s1hi_types: bool
    implementation_authorized_next_stage: bool
    parameter_values_selected: bool
    step_implementation_present: bool
    field_backreaction_selected: bool
    runtime_integration_present: bool
    functional_effect_proven: bool
    execution_permitted: bool
    field_steps_executed: int
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
            self.contract_id != S1_HO_CONTRACT_ID
            or self.source_s1hn_contract_digest
            != S1_HO_SOURCE_S1HN_CONTRACT_DIGEST
            or self.candidate_id != S1_HO_CANDIDATE_ID
            or self.target_module != S1_HO_TARGET_MODULE
            or self.error_type != S1_HO_ERROR_TYPE
            or self.entry_point != S1_HO_ENTRY_POINT
            or self.input_types != S1_HO_INPUT_TYPES
            or self.output_types != S1_HO_OUTPUT_TYPES
            or self.algorithm_phases != S1_HO_ALGORITHM_PHASES
            or self.forbidden_surfaces != S1_HO_FORBIDDEN_SURFACES
            or self.test_matrix != S1_HO_TEST_MATRIX
            or test_ids != tuple(f"T{index:02d}" for index in range(1, 18))
            or self.success_boundary != S1_HO_SUCCESS_BOUNDARY
            or any(
                value is not True
                for value in (
                    self.pure_function_required,
                    self.complete_edge_ledger_required,
                    self.immutable_inputs_required,
                    self.canonical_output_required,
                    self.fail_before_output_required,
                    self.diagnostics_are_passive,
                    self.use_existing_s1hi_types,
                    self.implementation_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.parameter_values_selected,
                    self.step_implementation_present,
                    self.field_backreaction_selected,
                    self.runtime_integration_present,
                    self.functional_effect_proven,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HO_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1HOStepImplementationContractError(
                "S1-HO weakened the pure-step implementation boundary"
            )


def build_dts1_s1ho_step_implementation_contract(
) -> DTS1S1HOStepImplementationContract:
    """Bind the future pure-step API and tests without implementing it."""

    values = {
        "contract_id": S1_HO_CONTRACT_ID,
        "source_s1hn_contract_digest": S1_HO_SOURCE_S1HN_CONTRACT_DIGEST,
        "candidate_id": S1_HO_CANDIDATE_ID,
        "target_module": S1_HO_TARGET_MODULE,
        "error_type": S1_HO_ERROR_TYPE,
        "entry_point": S1_HO_ENTRY_POINT,
        "input_types": S1_HO_INPUT_TYPES,
        "output_types": S1_HO_OUTPUT_TYPES,
        "algorithm_phases": S1_HO_ALGORITHM_PHASES,
        "forbidden_surfaces": S1_HO_FORBIDDEN_SURFACES,
        "test_matrix": S1_HO_TEST_MATRIX,
        "success_boundary": S1_HO_SUCCESS_BOUNDARY,
        "pure_function_required": True,
        "complete_edge_ledger_required": True,
        "immutable_inputs_required": True,
        "canonical_output_required": True,
        "fail_before_output_required": True,
        "diagnostics_are_passive": True,
        "use_existing_s1hi_types": True,
        "implementation_authorized_next_stage": True,
        "parameter_values_selected": False,
        "step_implementation_present": False,
        "field_backreaction_selected": False,
        "runtime_integration_present": False,
        "functional_effect_proven": False,
        "execution_permitted": False,
        "field_steps_executed": 0,
        "claims_permitted": False,
        "decision": S1_HO_DECISION,
    }
    return DTS1S1HOStepImplementationContract(
        **values,
        contract_digest=_digest(values),
    )
