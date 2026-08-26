"""Static S1-JX sequence carry orchestration contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_private_baseline_adapters import (
    build_dts1_s1jw_implementation_receipt,
)
from .dynamic_substrate_s1ir_corrected_profile_contract import (
    S1_IR_PROFILE_BLOCKS,
    build_dts1_s1ir_corrected_profile_contract,
)
from .dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    S1_JA_BASELINE_ROLES,
    S1_JA_CASE_MATRIX,
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from .dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    S1_JK_ENVELOPE_FIXTURES,
    S1_JK_SEQUENCE_FIXTURES,
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)


class DTS1S1JXSequenceCarryOrchestrationContractError(ValueError):
    """Raised when S1-JX weakens replica isolation or atomic carry."""


S1_JX_CONTRACT_ID = "dynamic-substrate.sequence-carry-orchestration.s1jx.v1"
S1_JX_SOURCE_S1JW_DIGEST = (
    "e9569da34791c6206db876e9901f437aa0bcb676757d7e433d890b5271155117"
)
S1_JX_SOURCE_S1JK_DIGEST = (
    "64ca5b895146fef453eb27945a1074f5d2b8e4c8834a94cc6f9b0a855a61824f"
)
S1_JX_SOURCE_S1JA_DIGEST = (
    "331168f2a6f937b454742d2be57de3f022f75ca5ca521fbff31f101bd4ea1fbc"
)
S1_JX_SOURCE_S1IR_DIGEST = (
    "350de2e0abbd05d03544567b3e7aae81ef387c75c739b924deea5f726410123e"
)
S1_JX_REFINEMENT_LEVELS = (2, 4, 8)
S1_JX_PRIMARY_REFINEMENT = 4
S1_JX_ROLE_MAP = tuple(
    (long_role, f"B{index}")
    for index, long_role in enumerate(S1_JA_BASELINE_ROLES, start=1)
)
S1_JX_PROFILE_SEQUENCE_KEYS = (
    ("P_IE_CAUSAL_TWO_SUBSTEP", ("P_IE_F_HIGH", "P_IE_R_HIGH")),
    ("P_IH_ATTENUATION", ("P_IH_A_A_A",)),
    ("P_IK_INTERFERENCE", ("P_IK_A_B_A", "P_IK_A_GAP_A")),
    ("P_IN_RELEASE_REUSE", ("P_IN_RECOVERY_ON", "P_IN_RECOVERY_OFF")),
)
S1_JX_CHECKPOINT_ORDINALS = (
    ("P_IE_F_HIGH", (1, 2)),
    ("P_IE_R_HIGH", (1, 2)),
    ("P_IH_A_A_A", (1, 2, 3)),
    ("P_IK_A_B_A", (4,)),
    ("P_IK_A_GAP_A", (4,)),
    ("P_IN_RECOVERY_ON", (4,)),
    ("P_IN_RECOVERY_OFF", (4,)),
)


def _sequence_records() -> tuple[tuple[object, ...], ...]:
    checkpoint_by_key = dict(S1_JX_CHECKPOINT_ORDINALS)
    return tuple(
        (
            key,
            profile,
            geometry,
            interval_count,
            digest,
            checkpoint_by_key[key],
            tuple(row[-1] for row in S1_JK_ENVELOPE_FIXTURES if row[0] == digest),
        )
        for key, profile, geometry, interval_count, digest in S1_JK_SEQUENCE_FIXTURES
    )


S1_JX_SEQUENCE_RECORDS = _sequence_records()


def _replica_records() -> tuple[tuple[object, ...], ...]:
    role_map = dict(S1_JX_ROLE_MAP)
    keys_by_profile = dict(S1_JX_PROFILE_SEQUENCE_KEYS)
    sequence_by_key = {row[0]: row for row in S1_JX_SEQUENCE_RECORDS}
    rows = []
    for long_role, profile, _nodes, _components, _status in S1_JA_CASE_MATRIX:
        short_role = role_map[long_role]
        keys = keys_by_profile[profile]
        interval_count = sum(sequence_by_key[key][3] for key in keys)
        checkpoint_count = sum(len(sequence_by_key[key][5]) for key in keys)
        for refinement in S1_JX_REFINEMENT_LEVELS:
            rows.append(
                (
                    f"{short_role}:{profile}:r{refinement}",
                    short_role,
                    long_role,
                    profile,
                    refinement,
                    keys,
                    tuple(sequence_by_key[key][4] for key in keys),
                    interval_count,
                    checkpoint_count,
                    "BOUND_NOT_IMPLEMENTED_NOT_EXECUTED",
                )
            )
    return tuple(rows)


S1_JX_REPLICA_RECORDS = _replica_records()


def _case_records() -> tuple[tuple[object, ...], ...]:
    role_map = dict(S1_JX_ROLE_MAP)
    component_by_profile = {row[0]: row[2] for row in S1_IR_PROFILE_BLOCKS}
    return tuple(
        (
            f"C{index:02d}",
            role_map[long_role],
            long_role,
            profile,
            nodes,
            component_by_profile[profile],
            tuple(
                f"{role_map[long_role]}:{profile}:r{refinement}"
                for refinement in S1_JX_REFINEMENT_LEVELS
            ),
            "BOUND_NOT_IMPLEMENTED_NOT_EXECUTED",
        )
        for index, (long_role, profile, nodes, _components, _status) in enumerate(
            S1_JA_CASE_MATRIX, start=1
        )
    )


S1_JX_CASE_RECORDS = _case_records()
S1_JX_REPLICA_INITIALIZATION_RULES = (
    "each-role-profile-refinement-replica-starts-from-an-independent-fresh-role-owned-field-and-private-state",
    "each-independent-sequence-inside-a-replica-also-starts-from-the-same-preregistered-fresh-role-state-not-from-a-sibling-sequence",
    "B1-reconstructs-the-same-profile-bound-fixed-adapter-for-each-independent-sequence",
    "B2-starts-each-independent-sequence-with-complete-uniform-zero-L",
    "B3-through-B6-start-each-independent-sequence-with-their-own-complete-uniform-M-and-bound-arm",
    "no-DTS1-candidate-sidecar-placeholder-or-derived-coordinate-enters-any-baseline-initializer",
)
S1_JX_INTERVAL_CARRY_RULES = (
    "within-one-sequence-materialize-the-next-exact-S1-JK-envelope-in-contiguous-ordinal-order",
    "pass-the-adapter-output-complete-field-as-the-next-interval-input-field-in-the-same-sequence-and-replica",
    "pass-the-adapter-output-next-private-state-as-the-next-private-state-in-the-same-sequence-and-replica",
    "pass-the-current-envelope-digest-and-canonical-complete-output-digest-as-the-next-provenance-pair",
    "boundary-directives-replace-only-S-H-while-role-owned-L-M-or-fixed-adapter-state-remains-carried",
    "CARRY_PRIOR_SH-is-valid-only-for-the-immediately-following-envelope-of-the-same-sequence",
    "zero-contact-intervals-are-executed-and-carried-like-every-other-positive-interval",
)
S1_JX_CARRY_EXCLUSIONS = (
    "no-field-private-state-envelope-digest-output-digest-or-diagnostic-crosses-a-sequence-boundary",
    "no-state-crosses-refinement-role-profile-case-or-candidate-baseline-boundaries",
    "no-r2-output-initializes-r4-and-no-r4-output-initializes-r8",
    "no-checkpoint-diagnostic-residual-reference-or-future-output-feeds-any-later-interval",
    "no-failed-or-partial-replica-state-is-reused-repaired-retried-or-substituted",
)
S1_JX_CHECKPOINT_RULES = (
    "capture-only-after-an-envelope-whose-registered-checkpoint-boolean-is-true",
    "capture-complete-S-H-in-canonical-node-order-plus-field-private-state-and-output-digests-for-integrity",
    "P_IE-captures-both-ordinals-of-both-independent-sequences",
    "P_IH-captures-all-three-ordinals-of-its-one-carried-sequence",
    "P_IK-and-P_IN-capture-only-the-terminal-probe-of-each-independent-sequence",
    "checkpoint-capture-is-read-only-and-never-changes-carry-or-model-input",
)
S1_JX_SIGNED_COMPONENT_RULES = tuple(
    (profile, description, count)
    for profile, description, count in S1_IR_PROFILE_BLOCKS
)
S1_JX_REFINEMENT_OUTPUT_RULES = (
    "each-case-publishes-one-complete-28-independent-component-block-at-r2-r4-r8-or-no-case-output",
    "B1-and-B2-require-bit-identical-complete-replica-output-digests-across-r2-r4-r8",
    "B3-through-B6-publish-complete-signed-r2-minus-r4-and-r4-minus-r8-component-residuals",
    "primary-profile-components-are-r4-and-controls-r2-r8-cannot-be-omitted",
    "no-threshold-fit-ranking-closure-rejection-or-candidate-comparison-occurs-in-the-orchestrator",
)
S1_JX_ATOMICITY_RULES = (
    "one-invalid-envelope-materialization-adapter-output-carry-checkpoint-or-digest-invalidates-the-complete-replica",
    "one-invalid-replica-invalidates-all-three-refinements-and-the-complete-role-profile-case",
    "publish-no-partial-sequence-checkpoint-component-residual-case-or-matrix-output",
    "the-later-24-case-matrix-is-published-only-after-all-24-complete-cases-succeed",
)
S1_JX_TECHNICAL_TEST_MATRIX = tuple(
    (f"T{index:02d}", role)
    for index, role in enumerate(
        (
            "exact-S1-JW-S1-JK-S1-JA-S1-IR-source-binding",
            "seven-sequences-and-twenty-three-corrected-envelope-identities",
            "exact-profile-to-sequence-membership",
            "exact-checkpoint-ordinals-and-eleven-checkpoints-per-role-refinement",
            "six-role-four-profile-three-refinement-cardinality",
            "seventy-two-unique-replica-identities",
            "twenty-four-canonical-case-identities-and-three-replicas-each",
            "four-hundred-fourteen-planned-interval-calls",
            "fresh-role-state-per-sequence-and-no-sibling-sequence-carry",
            "field-private-state-and-two-provenance-digests-carry-together",
            "boundary-replacement-preserves-private-state",
            "zero-contact-positive-interval-carry",
            "no-cross-sequence-refinement-role-profile-or-candidate-carry",
            "registered-checkpoint-only-readout",
            "corrected-eight-eight-six-six-signed-component-order",
            "B1-B2-bit-identity-and-B3-B6-signed-refinement-residuals",
            "replica-case-and-matrix-atomic-fail-closed-publication",
            "deterministic-tamper-evident-contract",
            "no-orchestrator-adapter-profile-case-or-research-execution",
        ),
        start=1,
    )
)
S1_JX_FORBIDDEN_INTERPRETATIONS = (
    "implemented-or-executed-sequence-orchestrator-replica-case-profile-or-matrix",
    "numerical-admissibility-baseline-fit-baseline-closure-rejection-or-candidate-superiority",
    "runtime-readiness-physical-timescale-or-research-evidence",
    "memory-learning-semantics-consciousness-experience-understanding-organic-property-or-artificial-intelligence",
)
S1_JX_DECISION = (
    "FINITE_SEQUENCE_CARRY_CHECKPOINT_AND_REFINEMENT_OUTPUT_ORCHESTRATION_BOUND_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JXSequenceCarryOrchestrationContract:
    contract_id: str
    source_s1jw_digest: str
    source_s1jk_digest: str
    source_s1ja_digest: str
    source_s1ir_digest: str
    refinement_levels: tuple[int, ...]
    primary_refinement: int
    role_map: tuple[tuple[str, str], ...]
    profile_sequence_keys: tuple[tuple[str, tuple[str, ...]], ...]
    sequence_records: tuple[tuple[object, ...], ...]
    checkpoint_ordinals: tuple[tuple[str, tuple[int, ...]], ...]
    replica_records: tuple[tuple[object, ...], ...]
    case_records: tuple[tuple[object, ...], ...]
    replica_initialization_rules: tuple[str, ...]
    interval_carry_rules: tuple[str, ...]
    carry_exclusions: tuple[str, ...]
    checkpoint_rules: tuple[str, ...]
    signed_component_rules: tuple[tuple[str, str, int], ...]
    refinement_output_rules: tuple[str, ...]
    atomicity_rules: tuple[str, ...]
    technical_test_matrix: tuple[tuple[str, str], ...]
    forbidden_interpretations: tuple[str, ...]
    sequence_count: int
    envelope_count_per_role_refinement: int
    checkpoint_count_per_role_refinement: int
    replica_count: int
    case_count: int
    planned_baseline_interval_calls: int
    profile_component_count: int
    orchestration_contract_bound: bool
    orchestrator_implemented: bool
    profile_cases_executed: int
    baseline_interval_calls_executed: int
    runtime_integration_present: bool
    research_execution_permitted: bool
    research_field_steps_executed: int
    orchestrator_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {f.name: getattr(self, f.name) for f in fields(self) if f.name != "contract_digest"}
        expected = (
            self.contract_id == S1_JX_CONTRACT_ID
            and self.source_s1jw_digest == S1_JX_SOURCE_S1JW_DIGEST
            and self.source_s1jk_digest == S1_JX_SOURCE_S1JK_DIGEST
            and self.source_s1ja_digest == S1_JX_SOURCE_S1JA_DIGEST
            and self.source_s1ir_digest == S1_JX_SOURCE_S1IR_DIGEST
            and self.refinement_levels == S1_JX_REFINEMENT_LEVELS
            and self.primary_refinement == S1_JX_PRIMARY_REFINEMENT
            and self.role_map == S1_JX_ROLE_MAP
            and self.profile_sequence_keys == S1_JX_PROFILE_SEQUENCE_KEYS
            and self.sequence_records == S1_JX_SEQUENCE_RECORDS
            and self.checkpoint_ordinals == S1_JX_CHECKPOINT_ORDINALS
            and self.replica_records == S1_JX_REPLICA_RECORDS
            and self.case_records == S1_JX_CASE_RECORDS
            and self.replica_initialization_rules == S1_JX_REPLICA_INITIALIZATION_RULES
            and self.interval_carry_rules == S1_JX_INTERVAL_CARRY_RULES
            and self.carry_exclusions == S1_JX_CARRY_EXCLUSIONS
            and self.checkpoint_rules == S1_JX_CHECKPOINT_RULES
            and self.signed_component_rules == S1_JX_SIGNED_COMPONENT_RULES
            and self.refinement_output_rules == S1_JX_REFINEMENT_OUTPUT_RULES
            and self.atomicity_rules == S1_JX_ATOMICITY_RULES
            and self.technical_test_matrix == S1_JX_TECHNICAL_TEST_MATRIX
            and self.forbidden_interpretations == S1_JX_FORBIDDEN_INTERPRETATIONS
            and self.sequence_count == 7
            and self.envelope_count_per_role_refinement == 23
            and self.checkpoint_count_per_role_refinement == 11
            and self.replica_count == 72
            and self.case_count == 24
            and self.planned_baseline_interval_calls == 414
            and self.profile_component_count == 28
            and self.orchestration_contract_bound is True
            and self.orchestrator_implemented is False
            and self.profile_cases_executed == 0
            and self.baseline_interval_calls_executed == 0
            and self.runtime_integration_present is False
            and self.research_execution_permitted is False
            and self.research_field_steps_executed == 0
            and self.orchestrator_implementation_authorized_next_stage is True
            and self.decision == S1_JX_DECISION
            and self.contract_digest == _digest(payload)
        )
        if not expected:
            raise DTS1S1JXSequenceCarryOrchestrationContractError(
                "S1-JX weakened sequence carry orchestration"
            )


def build_dts1_s1jx_sequence_carry_orchestration_contract(
) -> DTS1S1JXSequenceCarryOrchestrationContract:
    """Bind finite orchestration without materializing or executing intervals."""

    jw = build_dts1_s1jw_implementation_receipt()
    jk = build_dts1_s1jk_corrected_monotonic_interval_contract()
    ja = build_dts1_s1ja_finite_configuration_matrix_contract()
    ir = build_dts1_s1ir_corrected_profile_contract()
    values = {
        "contract_id": S1_JX_CONTRACT_ID,
        "source_s1jw_digest": jw.receipt_digest,
        "source_s1jk_digest": jk.contract_digest,
        "source_s1ja_digest": ja.contract_digest,
        "source_s1ir_digest": ir.contract_digest,
        "refinement_levels": S1_JX_REFINEMENT_LEVELS,
        "primary_refinement": S1_JX_PRIMARY_REFINEMENT,
        "role_map": S1_JX_ROLE_MAP,
        "profile_sequence_keys": S1_JX_PROFILE_SEQUENCE_KEYS,
        "sequence_records": S1_JX_SEQUENCE_RECORDS,
        "checkpoint_ordinals": S1_JX_CHECKPOINT_ORDINALS,
        "replica_records": S1_JX_REPLICA_RECORDS,
        "case_records": S1_JX_CASE_RECORDS,
        "replica_initialization_rules": S1_JX_REPLICA_INITIALIZATION_RULES,
        "interval_carry_rules": S1_JX_INTERVAL_CARRY_RULES,
        "carry_exclusions": S1_JX_CARRY_EXCLUSIONS,
        "checkpoint_rules": S1_JX_CHECKPOINT_RULES,
        "signed_component_rules": S1_JX_SIGNED_COMPONENT_RULES,
        "refinement_output_rules": S1_JX_REFINEMENT_OUTPUT_RULES,
        "atomicity_rules": S1_JX_ATOMICITY_RULES,
        "technical_test_matrix": S1_JX_TECHNICAL_TEST_MATRIX,
        "forbidden_interpretations": S1_JX_FORBIDDEN_INTERPRETATIONS,
        "sequence_count": len(S1_JX_SEQUENCE_RECORDS),
        "envelope_count_per_role_refinement": sum(row[3] for row in S1_JX_SEQUENCE_RECORDS),
        "checkpoint_count_per_role_refinement": sum(len(row[5]) for row in S1_JX_SEQUENCE_RECORDS),
        "replica_count": len(S1_JX_REPLICA_RECORDS),
        "case_count": len(S1_JX_CASE_RECORDS),
        "planned_baseline_interval_calls": sum(row[7] for row in S1_JX_REPLICA_RECORDS),
        "profile_component_count": sum(row[2] for row in S1_JX_SIGNED_COMPONENT_RULES),
        "orchestration_contract_bound": True,
        "orchestrator_implemented": False,
        "profile_cases_executed": 0,
        "baseline_interval_calls_executed": 0,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "research_field_steps_executed": 0,
        "orchestrator_implementation_authorized_next_stage": True,
        "decision": S1_JX_DECISION,
    }
    return DTS1S1JXSequenceCarryOrchestrationContract(
        **values, contract_digest=_digest(values)
    )
