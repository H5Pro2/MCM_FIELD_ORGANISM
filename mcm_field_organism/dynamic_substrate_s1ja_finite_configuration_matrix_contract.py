"""Static S1-JA finite configuration and 24-case matrix contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_common_boundary import (
    build_dts1_s1iz_implementation_receipt,
)
from .dynamic_substrate_s1it_private_adapter_contract import (
    build_dts1_s1it_private_adapter_contract,
)


class DTS1S1JAFiniteConfigurationMatrixContractError(ValueError):
    """Raised when the finite S1-JA binding is weakened."""


S1_JA_CONTRACT_ID = "dynamic-substrate.finite-configuration-matrix.s1ja.v1"
S1_JA_SOURCE_S1IZ_DIGEST = (
    "346f4778686642b0fa907c7ee1a5c95b2b8968172efc7a4f1cf0340de0e77828"
)
S1_JA_SOURCE_S1IT_DIGEST = (
    "942373dd7605c8b8054c1b188d99fce47145d7894e7521bad81c2b9065facac4"
)
S1_JA_PROFILE_BLOCKS = (
    ("P_IE_CAUSAL_TWO_SUBSTEP", 2, 8),
    ("P_IH_ATTENUATION", 2, 8),
    ("P_IK_INTERFERENCE", 3, 6),
    ("P_IN_RELEASE_REUSE", 3, 6),
)
S1_JA_BASELINE_ROLES = (
    "B1_FIXED_PRERELEASE_ADAPTER",
    "B2_S2_LINEAR_INTEGRATOR",
    "B3_F3_LOCAL_LEAKY",
    "B4_F3_LINEAR_COUPLED",
    "B5_F3_FULL",
    "B6_CONST_V",
)
S1_JA_RAW_CONFIGURATIONS = (
    (
        "DTS1",
        "S1-HX/S1-ID/S1-IG/S1-IJ/S1-IM-fixed-synthetic-source",
        (
            ("binding_rate", 0.4),
            ("turnover_rate", 0.3),
            ("recovery_rate", 0.2),
            ("node_capacity", 1.0),
            ("response_time", 1.0),
            ("afterimage_time", 0.5),
            ("dissipation_rate", 0.0),
            ("P_IE_initial_conductive", (0.4,)),
            ("P_IE_initial_refractory_by_arm", ((0.2,), (0.8,))),
            ("P_IH_initial_conductive", (0.4,)),
            ("P_IH_initial_refractory", (0.2,)),
            ("P_IK_initial_conductive", (0.2, 0.2)),
            ("P_IK_initial_refractory", (0.1, 0.1)),
            ("P_IN_initial_conductive", (0.2, 0.2)),
            ("P_IN_initial_refractory", (0.1, 0.1)),
        ),
    ),
    (
        "B1_FIXED_PRERELEASE_ADAPTER",
        "sanitized-common-predivergence-conductive-ledgers-from-S1-ID-S1-IG-S1-IJ-S1-IM",
        (
            ("response_time", 1.0),
            ("afterimage_time", 0.5),
            ("dissipation_rate", 0.0),
            ("P_IE_fixed_conductive", (0.4,)),
            ("P_IH_fixed_conductive", (0.4,)),
            ("P_IK_fixed_conductive", (0.2, 0.2)),
            ("P_IN_fixed_conductive", (0.2, 0.2)),
            ("capacity_per_node", 1.0),
            ("free_refractory_and_postdivergence_coordinates", "excluded"),
        ),
    ),
    (
        "B2_S2_LINEAR_INTEGRATOR",
        "s2_reference_baselines.S2ReferenceModelConfig-default-v1:model-b2",
        (
            ("capacity_ratio", 8.0),
            ("coupling_rate_per_second", 0.25),
            ("afterimage_time_seconds", 0.5),
            ("leak_rate_per_second", 0.0),
            ("gain_reference_seconds", 1.0),
            ("rk4_substeps", 16),
            ("initial_L", "uniform-zero"),
        ),
    ),
    (
        "B3_F3_LOCAL_LEAKY",
        "e1_e4_f3_runners.equal-budget-arm-v1:local-leaky",
        (
            ("lambda_sm_per_second", 1.0),
            ("kappa", 0.5),
            ("eta", 1.0),
            ("initial_total_mass", 1.0),
            ("response_time", 1.0),
            ("afterimage_time", 0.5),
            ("dissipation_rate", 0.0),
            ("initial_M", "uniform-by-node-count"),
        ),
    ),
    (
        "B4_F3_LINEAR_COUPLED",
        "e1_e4_f3_runners.equal-budget-arm-v1:linear-coupled-field",
        (
            ("lambda_sm_per_second", 1.0),
            ("kappa", 0.5),
            ("eta", 1.0),
            ("initial_total_mass", 1.0),
            ("response_time", 1.0),
            ("afterimage_time", 0.5),
            ("dissipation_rate", 0.0),
            ("initial_M", "uniform-by-node-count"),
        ),
    ),
    (
        "B5_F3_FULL",
        "e1_e4_f3_runners.equal-budget-arm-v1:f3-candidate-kernel",
        (
            ("lambda_sm_per_second", 1.0),
            ("kappa", 0.5),
            ("eta", 1.0),
            ("initial_total_mass", 1.0),
            ("response_time", 1.0),
            ("afterimage_time", 0.5),
            ("dissipation_rate", 0.0),
            ("initial_M", "uniform-by-node-count"),
        ),
    ),
    (
        "B6_CONST_V",
        "w7m_capacity_function_matrix.const-v-frozen-spec-v1",
        (
            ("equation_id", "baseline.k2-f3.const-v.v1"),
            ("equation_contract", "use=compute_mcm_f3_coupling;lambda_sm=V_initial"),
            ("lambda_sm_per_second", 0.5),
            ("kappa", 0.5),
            ("eta", 1.0),
            ("initial_total_mass", 1.0),
            ("response_time", 1.0),
            ("afterimage_time", 0.5),
            ("dissipation_rate", 0.0),
            ("initial_M", "uniform-by-node-count"),
        ),
    ),
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


S1_JA_CONFIGURATION_RECORDS = tuple(
    (role, source, payload, _digest((role, source, payload)))
    for role, source, payload in S1_JA_RAW_CONFIGURATIONS
)
S1_JA_REFINEMENT_RECORDS = tuple(
    (
        role,
        (2, 4, 8),
        4,
        "same-physical-interval-no-boundary-reapplication-inside-one-interval",
    )
    for role in ("DTS1",) + S1_JA_BASELINE_ROLES
)
S1_JA_REFINEMENT_RULES = (
    "levels-two-four-eight-use-identical-start-state-duration-contact-and-event-boundaries",
    "level-four-is-the-preregistered-primary-profile-and-levels-two-and-eight-are-mandatory-controls",
    "common-S-H-boundary-is-applied-once-before-the-physical-interval-and-never-at-internal-substeps",
    "DTS1-recomputes-participation-and-adapter-from-each-closed-internal-prestate-while-B1-keeps-one-fixed-adapter",
    "all-model-owned-states-evolve-only-through-their-registered-kernels-within-the-physical-interval",
    "report-complete-signed-r2-r4-and-r4-r8-profile-residuals-without-fitting-thresholding-or-dropping-a-level",
    "S1-IY-high-level-boundary-and-interval-call-budget-excludes-private-internal-refinement-substeps",
)
S1_JA_CASE_MATRIX = tuple(
    (
        role,
        block,
        node_count,
        component_count,
        "BOUND_NOT_IMPLEMENTED_NOT_EXECUTED",
    )
    for role in S1_JA_BASELINE_ROLES
    for block, node_count, component_count in S1_JA_PROFILE_BLOCKS
)
S1_JA_MATRIX_RULES = (
    "canonical-order-is-B1-through-B6-and-within-role-P_IE-P_IH-P_IK-P_IN",
    "all-twenty-four-cases-use-the-one-role-configuration-digest-with-no-block-arm-or-refinement-fit",
    "P_IE-and-P_IH-retain-their-existing-common-exposures-and-P_IK-P_IN-use-only-S1-IX-S1-IY-boundaries",
    "each-case-must-produce-its-complete-signed-block-or-fail-the-later-atomic-audit",
    "technical-incompatibility-is-a-recorded-case-result-and-cannot-be-repaired-or-omitted",
)
S1_JA_FORBIDDEN_INTERPRETATIONS = (
    "implemented-numerically-admissible-or-executed-adapter-or-model",
    "selected-comparison-threshold-baseline-fit-baseline-closure-or-candidate-superiority",
    "physical-material-timescale-memory-learning-or-artificial-intelligence",
)
S1_JA_DECISION = "SEVEN_CONFIGURATIONS_AND_TWENTY_FOUR_BASELINE_CASES_BOUND_NO_IMPLEMENTATION_OR_EXECUTION"


@dataclass(frozen=True, slots=True)
class DTS1S1JAFiniteConfigurationMatrixContract:
    contract_id: str
    source_s1iz_digest: str
    source_s1it_digest: str
    profile_blocks: tuple[tuple[str, int, int], ...]
    baseline_roles: tuple[str, ...]
    configuration_records: tuple[tuple[str, str, tuple[tuple[str, object], ...], str], ...]
    refinement_records: tuple[tuple[str, tuple[int, ...], int, str], ...]
    refinement_rules: tuple[str, ...]
    case_matrix: tuple[tuple[str, str, int, int, str], ...]
    matrix_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    configuration_count: int
    baseline_case_count: int
    profile_component_count: int
    parameter_values_selected: bool
    configuration_digests_bound: bool
    refinements_selected: bool
    finite_case_matrix_bound: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    numerical_admissibility_proven: bool
    comparison_threshold_selected: bool
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
            self.contract_id != S1_JA_CONTRACT_ID
            or self.source_s1iz_digest != S1_JA_SOURCE_S1IZ_DIGEST
            or self.source_s1it_digest != S1_JA_SOURCE_S1IT_DIGEST
            or self.profile_blocks != S1_JA_PROFILE_BLOCKS
            or self.baseline_roles != S1_JA_BASELINE_ROLES
            or self.configuration_records != S1_JA_CONFIGURATION_RECORDS
            or self.refinement_records != S1_JA_REFINEMENT_RECORDS
            or self.refinement_rules != S1_JA_REFINEMENT_RULES
            or self.case_matrix != S1_JA_CASE_MATRIX
            or self.matrix_rules != S1_JA_MATRIX_RULES
            or self.forbidden_interpretations != S1_JA_FORBIDDEN_INTERPRETATIONS
            or self.configuration_count != 7
            or self.baseline_case_count != 24
            or self.profile_component_count != 28
            or any(
                value is not True
                for value in (
                    self.parameter_values_selected,
                    self.configuration_digests_bound,
                    self.refinements_selected,
                    self.finite_case_matrix_bound,
                    self.private_adapter_implementation_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.adapters_implemented,
                    self.baseline_models_executed,
                    self.numerical_admissibility_proven,
                    self.comparison_threshold_selected,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_JA_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JAFiniteConfigurationMatrixContractError(
                "S1-JA weakened the finite configuration and case matrix"
            )


def build_dts1_s1ja_finite_configuration_matrix_contract() -> DTS1S1JAFiniteConfigurationMatrixContract:
    """Bind seven configurations and 24 baseline cases without execution."""

    source = build_dts1_s1iz_implementation_receipt()
    adapter_source = build_dts1_s1it_private_adapter_contract()
    values = {
        "contract_id": S1_JA_CONTRACT_ID,
        "source_s1iz_digest": source.receipt_digest,
        "source_s1it_digest": adapter_source.contract_digest,
        "profile_blocks": S1_JA_PROFILE_BLOCKS,
        "baseline_roles": S1_JA_BASELINE_ROLES,
        "configuration_records": S1_JA_CONFIGURATION_RECORDS,
        "refinement_records": S1_JA_REFINEMENT_RECORDS,
        "refinement_rules": S1_JA_REFINEMENT_RULES,
        "case_matrix": S1_JA_CASE_MATRIX,
        "matrix_rules": S1_JA_MATRIX_RULES,
        "forbidden_interpretations": S1_JA_FORBIDDEN_INTERPRETATIONS,
        "configuration_count": len(S1_JA_CONFIGURATION_RECORDS),
        "baseline_case_count": len(S1_JA_CASE_MATRIX),
        "profile_component_count": sum(row[2] for row in S1_JA_PROFILE_BLOCKS),
        "parameter_values_selected": True,
        "configuration_digests_bound": True,
        "refinements_selected": True,
        "finite_case_matrix_bound": True,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "numerical_admissibility_proven": False,
        "comparison_threshold_selected": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "private_adapter_implementation_authorized_next_stage": True,
        "decision": S1_JA_DECISION,
    }
    return DTS1S1JAFiniteConfigurationMatrixContract(
        **values, contract_digest=_digest(values)
    )
