"""S1-FP static fresh-formation to common-probe contract."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_acceptance_contract import (
    build_e1_common_probe_acceptance_contract,
)
from .e1_e3_probe_run import E1_E3_PROBE_ABSOLUTE_TOLERANCE
from .e1_e4_execution import E1_E4_REFINEMENT_LIMIT
from .e1_confirmation_full_probe_result_audit import S1_EC24_SIGNAL_MARGIN
from .e1_formation_s1fc_state_convergence_contract import (
    S1_FC_FORMATION_ROLES,
)
from .e1_frozen_state_transfer_contract import (
    _fixed_probe_sequences,
    _probe_digest,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
    advance_frozen_e1_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest
from .neutral_local_field_substrate import (
    advance_neutral_fast_shared_field_transient,
)


class E1FormationS1FPCommonProbeContractError(ValueError):
    """Raised when S1-FP changes scope or opens execution."""


S1_FP_CONTRACT_ID = "e1.fresh-formation-common-probe-contract.s1fp.v1"
S1_FP_SOURCE_COORDINATOR_DIGEST = (
    "0779ed8e59e38454f477da23caa93b05f80d97b74288ae5ff307a2724fae594b"
)
S1_FP_SOURCE_EVALUATION_DIGEST = (
    "cbd4df8b5218b5454d276e2f2c22cd0f0f21204d1d100eeb6a72be1cc68e5f22"
)
S1_FP_REFINEMENTS = ("r2", "r4", "r8")
S1_FP_PROBE_ROLES = (
    "p0-reset-ab",
    "p0-reset-ba",
    "e1-active-ab",
    "e1-active-ba",
    "e1-probe-feedback-ablated-ab",
    "e1-probe-feedback-ablated-ba",
    "e1-formation-ablated-ab",
    "e1-formation-ablated-ba",
    "fixed-adapter-ab",
    "fixed-adapter-ba",
)
S1_FP_REQUIRED_CONTRASTS = (
    "p0-reset-order",
    "e1-active-order",
    "e1-probe-feedback-ablated-order",
    "e1-formation-ablated-order",
    "active-ab-vs-fixed-adapter-ab",
    "active-ba-vs-fixed-adapter-ba",
)
S1_FP_DECISIONS = (
    "INVALID_FRESH_FORMATION_COMMON_PROBE_CONTROLS",
    "NO_MEASURABLE_FRESH_FORMATION_COMMON_PROBE_DIFFERENCE",
    "NUMERICALLY_UNDECIDABLE_FRESH_FORMATION_COMMON_PROBE_DIFFERENCE",
    "FRESH_FORMATION_COMMON_PROBE_DIFFERENCE_FIXED_ADAPTER_EXPLAINED",
    "FRESH_FORMATION_COMMON_PROBE_DIFFERENCE_NOT_FIXED_ADAPTER_EXPLAINED",
)
S1_FP_CHECK_NAMES = (
    "s1fo-evidence-digests-bound",
    "fresh-formation-required-no-state-reuse",
    "fifteen-formation-states-bound",
    "thirty-common-probe-slots-bound",
    "one-identical-probe-source-bound",
    "fresh-object-separated-reset-field-per-slot-required",
    "formed-state-frozen-during-probe-required",
    "fixed-adapter-explanatory-baseline-required",
    "existing-acceptance-bounds-inherited-unchanged",
    "three-probe-kernel-signatures-bound",
    "builder-does-not-run-field-or-write",
    "owner-authorization-and-execution-absent",
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _called_names(source: str) -> frozenset[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return frozenset(names)


@dataclass(frozen=True, slots=True)
class E1FormationS1FPCommonProbeContract:
    contract_id: str
    source_s1fo_coordinator_digest: str
    source_s1fo_evaluation_digest: str
    source_acceptance_contract_digest: str
    refinements: tuple[str, ...]
    formation_roles: tuple[str, ...]
    probe_roles: tuple[str, ...]
    required_contrasts: tuple[str, ...]
    decisions: tuple[str, ...]
    probe_source_digest: str
    formation_state_count: int
    probe_slot_count: int
    common_observation_space: str
    absolute_control_tolerance: float
    strict_signal_margin: float
    relative_refinement_limit: float
    probe_kernels: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    fresh_formation_in_same_process_required: bool
    previous_state_or_authorization_reuse_permitted: bool
    fresh_field_per_probe_slot_required: bool
    formed_state_frozen_during_probe_required: bool
    fixed_adapter_baseline_required: bool
    probe_contract_implementation_permitted: bool
    owner_authorization_present: bool
    field_execution_permitted: bool
    persistence_permitted: bool
    automatic_retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if (
            self.contract_id != S1_FP_CONTRACT_ID
            or not _valid_digest(self.source_s1fo_coordinator_digest)
            or not _valid_digest(self.source_s1fo_evaluation_digest)
            or not _valid_digest(self.source_acceptance_contract_digest)
            or self.refinements != S1_FP_REFINEMENTS
            or self.formation_roles != S1_FC_FORMATION_ROLES
            or self.probe_roles != S1_FP_PROBE_ROLES
            or self.required_contrasts != S1_FP_REQUIRED_CONTRASTS
            or self.decisions != S1_FP_DECISIONS
            or not _valid_digest(self.probe_source_digest)
            or self.formation_state_count != 15
            or self.probe_slot_count != 30
            or self.common_observation_space
            != "post-reset-identical-probe:ordered-activation-and-afterimage"
            or self.absolute_control_tolerance != 1e-12
            or self.strict_signal_margin != 8.0
            or self.relative_refinement_limit != 0.01
            or self.probe_kernels
            != (
                "advance_neutral_fast_shared_field_transient",
                "advance_frozen_e1_fast_shared_field_transient",
                "advance_fixed_e1_adapter_fast_shared_field_transient",
            )
            or tuple(name for name, _ in self.checks) != S1_FP_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.fresh_formation_in_same_process_required,
                    self.fresh_field_per_probe_slot_required,
                    self.formed_state_frozen_during_probe_required,
                    self.fixed_adapter_baseline_required,
                    self.probe_contract_implementation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.previous_state_or_authorization_reuse_permitted,
                    self.owner_authorization_present,
                    self.field_execution_permitted,
                    self.persistence_permitted,
                    self.automatic_retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.memory_claim_permitted,
                )
            )
            or self.decision
            != "FRESH_FORMATION_COMMON_PROBE_BOUND_IMPLEMENTATION_MISSING"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1FPCommonProbeContractError(
                "S1-FP contract changed or opened execution"
            )


def audit_e1_formation_s1fp_common_probe_contract(
) -> E1FormationS1FPCommonProbeContract:
    """Bind one fresh end-to-end experiment without running any field."""

    acceptance = build_e1_common_probe_acceptance_contract()
    probe_source_digest = _probe_digest(_fixed_probe_sequences())
    builder_source = inspect.getsource(
        audit_e1_formation_s1fp_common_probe_contract
    )
    kernel_parameters = tuple(
        tuple(inspect.signature(kernel).parameters)
        for kernel in (
            advance_neutral_fast_shared_field_transient,
            advance_frozen_e1_fast_shared_field_transient,
            advance_fixed_e1_adapter_fast_shared_field_transient,
        )
    )
    forbidden_calls = {
        "run_e1_formation_s1fl_once",
        "run_small_five_arm_formation_in_memory",
        "advance_neutral_fast_shared_field_transient",
        "advance_frozen_e1_fast_shared_field_transient",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "open",
        "write_text",
        "write_bytes",
    }
    checks = (
        (
            S1_FP_CHECK_NAMES[0],
            _valid_digest(S1_FP_SOURCE_COORDINATOR_DIGEST)
            and _valid_digest(S1_FP_SOURCE_EVALUATION_DIGEST),
        ),
        (S1_FP_CHECK_NAMES[1], True),
        (
            S1_FP_CHECK_NAMES[2],
            len(S1_FP_REFINEMENTS) * len(S1_FC_FORMATION_ROLES) == 15,
        ),
        (
            S1_FP_CHECK_NAMES[3],
            len(S1_FP_REFINEMENTS) * len(S1_FP_PROBE_ROLES) == 30,
        ),
        (S1_FP_CHECK_NAMES[4], _valid_digest(probe_source_digest)),
        (S1_FP_CHECK_NAMES[5], True),
        (S1_FP_CHECK_NAMES[6], True),
        (
            S1_FP_CHECK_NAMES[7],
            {"fixed-adapter-ab", "fixed-adapter-ba"}.issubset(
                S1_FP_PROBE_ROLES
            ),
        ),
        (
            S1_FP_CHECK_NAMES[8],
            acceptance.absolute_control_tolerance
            == E1_E3_PROBE_ABSOLUTE_TOLERANCE
            and acceptance.strict_signal_margin == S1_EC24_SIGNAL_MARGIN
            and acceptance.relative_refinement_limit
            == E1_E4_REFINEMENT_LIMIT,
        ),
        (
            S1_FP_CHECK_NAMES[9],
            all(parameters for parameters in kernel_parameters)
            and "frozen_e1_state" in kernel_parameters[1]
            and "fixed_adapter" in kernel_parameters[2],
        ),
        (
            S1_FP_CHECK_NAMES[10],
            _called_names(builder_source).isdisjoint(forbidden_calls),
        ),
        (S1_FP_CHECK_NAMES[11], True),
    )
    values = {
        "contract_id": S1_FP_CONTRACT_ID,
        "source_s1fo_coordinator_digest": S1_FP_SOURCE_COORDINATOR_DIGEST,
        "source_s1fo_evaluation_digest": S1_FP_SOURCE_EVALUATION_DIGEST,
        "source_acceptance_contract_digest": acceptance.contract_digest,
        "refinements": S1_FP_REFINEMENTS,
        "formation_roles": S1_FC_FORMATION_ROLES,
        "probe_roles": S1_FP_PROBE_ROLES,
        "required_contrasts": S1_FP_REQUIRED_CONTRASTS,
        "decisions": S1_FP_DECISIONS,
        "probe_source_digest": probe_source_digest,
        "formation_state_count": 15,
        "probe_slot_count": 30,
        "common_observation_space": (
            "post-reset-identical-probe:ordered-activation-and-afterimage"
        ),
        "absolute_control_tolerance": E1_E3_PROBE_ABSOLUTE_TOLERANCE,
        "strict_signal_margin": S1_EC24_SIGNAL_MARGIN,
        "relative_refinement_limit": E1_E4_REFINEMENT_LIMIT,
        "probe_kernels": (
            "advance_neutral_fast_shared_field_transient",
            "advance_frozen_e1_fast_shared_field_transient",
            "advance_fixed_e1_adapter_fast_shared_field_transient",
        ),
        "checks": checks,
        "fresh_formation_in_same_process_required": True,
        "previous_state_or_authorization_reuse_permitted": False,
        "fresh_field_per_probe_slot_required": True,
        "formed_state_frozen_during_probe_required": True,
        "fixed_adapter_baseline_required": True,
        "probe_contract_implementation_permitted": True,
        "owner_authorization_present": False,
        "field_execution_permitted": False,
        "persistence_permitted": False,
        "automatic_retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "memory_claim_permitted": False,
        "decision": "FRESH_FORMATION_COMMON_PROBE_BOUND_IMPLEMENTATION_MISSING",
        "reason": (
            "fresh-formation-and-thirty-identical-common-probe-slots-bound;"
            "fixed-adapter-baseline-mandatory;implementation-and-execution-absent"
        ),
    }
    return E1FormationS1FPCommonProbeContract(
        **values,
        contract_digest=_digest(values),
    )
