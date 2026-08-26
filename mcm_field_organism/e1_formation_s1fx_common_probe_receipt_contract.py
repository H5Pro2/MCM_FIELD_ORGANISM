"""S1-FX static common receipt and fixed-adapter probe-wrapper contract."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_real_wrappers import (
    E1CommonProbeRealProbeOutput,
    run_e1_common_probe_real_probe_wrapper,
)
from .e1_formation_s1fv_live_state_ten_role_contract import (
    E1FormationS1FVLiveStateTenRoleContract,
)
from .e1_formation_s1fw_synthetic_live_state_handoff import (
    E1FormationS1FWSyntheticLiveStateHandoffResult,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FXCommonProbeReceiptContractError(ValueError):
    """Raised when S1-FX merges causal roles or opens a probe execution."""


S1_FX_CONTRACT_ID = "e1.common-probe-receipt-fixed-adapter-contract.s1fx.v1"
S1_FX_BRANCH_INVENTORY = (
    ("neutral-p0", 6, "existing-real-wrapper-plus-receipt-converter"),
    ("frozen-e1", 18, "existing-real-wrapper-plus-receipt-converter"),
    ("fixed-adapter", 6, "new-real-wrapper-plus-common-receipt"),
)
S1_FX_RECEIPT_SCHEMA = (
    "refinement_id",
    "role_id",
    "probe_mode",
    "binding_digest",
    "probe_source_digest",
    "initial_field_digest",
    "terminal_field_digest",
    "ordered_neuron_ids",
    "activation_vector",
    "afterimage_vector",
    "field_step_count",
    "source_support_count",
    "source_state_digest",
    "state_digest_before",
    "state_digest_after",
    "source_state_preserved",
    "fixed_adapter_digest",
    "kernel_name",
    "field_execution_kind",
    "persistence_performed",
    "claims_permitted",
    "receipt_digest",
)
S1_FX_CAUSAL_NULLABILITY = (
    (
        "neutral-p0",
        (
            "source_state_digest",
            "state_digest_before",
            "state_digest_after",
            "fixed_adapter_digest",
        ),
    ),
    ("frozen-e1", ("fixed_adapter_digest",)),
    ("fixed-adapter", ("state_digest_before", "state_digest_after")),
)
S1_FX_REQUIRED_WRAPPERS = (
    "convert-existing-p0-or-frozen-output-to-common-receipt",
    "run-fixed-adapter-probe-without-live-e1-state-role",
    "return-fixed-adapter-output-as-common-receipt",
)
S1_FX_CHECK_NAMES = (
    "s1fv-and-s1fw-bound-with-zero-field-steps",
    "branch-counts-cover-all-thirty-slots",
    "existing-real-output-has-required-field-and-state-evidence",
    "existing-real-probe-wrapper-signature-compatible",
    "fixed-adapter-kernel-signature-compatible",
    "receipt-keeps-frozen-state-and-fixed-adapter-evidence-separate",
    "receipt-requires-ordered-raw-vectors-and-step-accounting",
    "contract-builder-calls-no-probe-kernel-or-writer",
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
class E1FormationS1FXCommonProbeReceiptContract:
    contract_id: str
    source_s1fv_contract_digest: str
    source_s1fw_result_digest: str
    branch_inventory: tuple[tuple[str, int, str], ...]
    receipt_schema: tuple[str, ...]
    causal_nullability: tuple[tuple[str, tuple[str, ...]], ...]
    required_wrappers: tuple[str, ...]
    existing_real_output_fields: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    total_receipt_count: int
    p0_receipt_count: int
    frozen_e1_receipt_count: int
    fixed_adapter_receipt_count: int
    ordered_raw_vectors_required: bool
    source_state_digest_required_for_fixed_adapter: bool
    live_state_role_permitted_during_fixed_adapter_probe: bool
    fixed_adapter_may_be_reported_as_dynamic_e1_backreaction: bool
    common_receipt_converter_implemented: bool
    fixed_adapter_real_wrapper_implemented: bool
    synthetic_counting_implementation_permitted: bool
    real_wrapper_implementation_permitted: bool
    owner_authorization_present: bool
    execution_permitted: bool
    field_execution_performed: bool
    persistence_performed: bool
    claims_permitted: bool
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
            self.contract_id != S1_FX_CONTRACT_ID
            or self.branch_inventory != S1_FX_BRANCH_INVENTORY
            or self.receipt_schema != S1_FX_RECEIPT_SCHEMA
            or self.causal_nullability != S1_FX_CAUSAL_NULLABILITY
            or self.required_wrappers != S1_FX_REQUIRED_WRAPPERS
            or tuple(name for name, _ in self.checks) != S1_FX_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or (
                self.total_receipt_count,
                self.p0_receipt_count,
                self.frozen_e1_receipt_count,
                self.fixed_adapter_receipt_count,
            )
            != (30, 6, 18, 6)
            or any(
                value is not True
                for value in (
                    self.ordered_raw_vectors_required,
                    self.source_state_digest_required_for_fixed_adapter,
                    self.synthetic_counting_implementation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.live_state_role_permitted_during_fixed_adapter_probe,
                    self.fixed_adapter_may_be_reported_as_dynamic_e1_backreaction,
                    self.common_receipt_converter_implemented,
                    self.fixed_adapter_real_wrapper_implemented,
                    self.real_wrapper_implementation_permitted,
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "COMMON_RECEIPT_AND_FIXED_ADAPTER_WRAPPER_BOUND_IMPLEMENTATION_MISSING"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1FXCommonProbeReceiptContractError(
                "S1-FX receipt contract changed or opened execution"
            )


def prepare_e1_formation_s1fx_common_probe_receipt_contract(
    handoff_contract: E1FormationS1FVLiveStateTenRoleContract,
    handoff_result: E1FormationS1FWSyntheticLiveStateHandoffResult,
) -> E1FormationS1FXCommonProbeReceiptContract:
    """Bind a shared receipt schema without invoking any probe branch."""

    if not isinstance(
        handoff_contract, E1FormationS1FVLiveStateTenRoleContract
    ) or not isinstance(
        handoff_result, E1FormationS1FWSyntheticLiveStateHandoffResult
    ):
        raise E1FormationS1FXCommonProbeReceiptContractError(
            "S1-FX requires typed S1-FV and S1-FW inputs"
        )
    handoff_contract.__post_init__()
    handoff_result.__post_init__()
    existing_fields = tuple(E1CommonProbeRealProbeOutput.__dataclass_fields__)
    required_existing = {
        "terminal_field_digest",
        "activation",
        "afterimage",
        "field_step_count",
        "source_support_count",
        "frozen_state_digest_before",
        "frozen_state_digest_after",
        "frozen_state_preserved",
        "persistence_performed",
        "research_decision_permitted",
        "memory_claim_permitted",
        "result_digest",
    }
    builder_source = inspect.getsource(
        prepare_e1_formation_s1fx_common_probe_receipt_contract
    )
    forbidden_calls = {
        "run_e1_common_probe_real_probe_wrapper",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "advance_frozen_e1_fast_shared_field_transient",
        "advance_neutral_fast_shared_field_transient",
        "open",
        "write_text",
        "write_bytes",
    }
    checks = (
        (
            S1_FX_CHECK_NAMES[0],
            handoff_result.source_contract_digest == handoff_contract.contract_digest
            and handoff_result.field_steps_executed == 0
            and handoff_result.execution_permitted is False,
        ),
        (S1_FX_CHECK_NAMES[1], sum(item[1] for item in S1_FX_BRANCH_INVENTORY) == 30),
        (S1_FX_CHECK_NAMES[2], required_existing.issubset(existing_fields)),
        (
            S1_FX_CHECK_NAMES[3],
            tuple(inspect.signature(run_e1_common_probe_real_probe_wrapper).parameters)
            == ("resolved", "fresh", "frozen_state"),
        ),
        (
            S1_FX_CHECK_NAMES[4],
            tuple(
                inspect.signature(
                    advance_fixed_e1_adapter_fast_shared_field_transient
                ).parameters
            )
            == (
                "field",
                "fixed_adapter",
                "distribution",
                "transient_inputs",
                "substrate_config",
                "afterimage_config",
                "dissipation_config",
            ),
        ),
        (
            S1_FX_CHECK_NAMES[5],
            dict(S1_FX_CAUSAL_NULLABILITY)["frozen-e1"]
            == ("fixed_adapter_digest",)
            and dict(S1_FX_CAUSAL_NULLABILITY)["fixed-adapter"]
            == ("state_digest_before", "state_digest_after"),
        ),
        (
            S1_FX_CHECK_NAMES[6],
            all(
                role in S1_FX_RECEIPT_SCHEMA
                for role in (
                    "ordered_neuron_ids",
                    "activation_vector",
                    "afterimage_vector",
                    "field_step_count",
                )
            ),
        ),
        (S1_FX_CHECK_NAMES[7], _called_names(builder_source).isdisjoint(forbidden_calls)),
    )
    values = {
        "contract_id": S1_FX_CONTRACT_ID,
        "source_s1fv_contract_digest": handoff_contract.contract_digest,
        "source_s1fw_result_digest": handoff_result.result_digest,
        "branch_inventory": S1_FX_BRANCH_INVENTORY,
        "receipt_schema": S1_FX_RECEIPT_SCHEMA,
        "causal_nullability": S1_FX_CAUSAL_NULLABILITY,
        "required_wrappers": S1_FX_REQUIRED_WRAPPERS,
        "existing_real_output_fields": existing_fields,
        "checks": checks,
        "total_receipt_count": 30,
        "p0_receipt_count": 6,
        "frozen_e1_receipt_count": 18,
        "fixed_adapter_receipt_count": 6,
        "ordered_raw_vectors_required": True,
        "source_state_digest_required_for_fixed_adapter": True,
        "live_state_role_permitted_during_fixed_adapter_probe": False,
        "fixed_adapter_may_be_reported_as_dynamic_e1_backreaction": False,
        "common_receipt_converter_implemented": False,
        "fixed_adapter_real_wrapper_implemented": False,
        "synthetic_counting_implementation_permitted": True,
        "real_wrapper_implementation_permitted": False,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "COMMON_RECEIPT_AND_FIXED_ADAPTER_WRAPPER_BOUND_"
            "IMPLEMENTATION_MISSING"
        ),
        "reason": (
            "p0-frozen-e1-and-fixed-adapter-require-one-raw-vector-receipt;"
            "existing-wrapper-covers-first-two-branches;fixed-adapter-wrapper-"
            "and-common-converter-not-yet-implemented"
        ),
    }
    return E1FormationS1FXCommonProbeReceiptContract(
        **values,
        contract_digest=_digest(values),
    )
