"""S1-FZ static boundary for real common-receipt conversion and fixed adapter."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_real_wrappers import (
    E1CommonProbeFreshField,
    E1CommonProbeRealProbeOutput,
    E1CommonProbeResolvedSlot,
)
from .e1_formation_s1fy_synthetic_common_receipts import (
    E1FormationS1FYCommonProbeReceipt,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FZStaticRealReceiptBoundaryError(ValueError):
    """Raised when S1-FZ opens execution or loses receipt provenance."""


S1_FZ_AUDIT_ID = "e1.static-real-receipt-conversion-boundary.s1fz.v1"
S1_FZ_EXISTING_BRANCHES = ("neutral-p0", "frozen-e1")
S1_FZ_EXISTING_CONTEXT_TYPES = (
    "E1CommonProbeResolvedSlot",
    "E1CommonProbeFreshField",
    "E1CommonProbeRealProbeOutput",
)
S1_FZ_DIRECT_OUTPUT_MAPPING = (
    ("binding_digest", "binding_digest"),
    ("terminal_field_digest", "terminal_field_digest"),
    ("activation_vector", "activation"),
    ("afterimage_vector", "afterimage"),
    ("field_step_count", "field_step_count"),
    ("source_support_count", "source_support_count"),
    ("state_digest_before", "frozen_state_digest_before"),
    ("state_digest_after", "frozen_state_digest_after"),
    ("source_state_preserved", "frozen_state_preserved"),
    ("persistence_performed", "persistence_performed"),
)
S1_FZ_BOUND_CONTEXT_MAPPING = (
    ("refinement_id", "resolved.binding.refinement_id"),
    ("role_id", "resolved.binding.state_role-plus-bound-side"),
    ("probe_mode", "resolved.binding-mode"),
    ("probe_source_digest", "digest(resolved.probe_sequences)"),
    ("initial_field_digest", "fresh.initial_field_digest"),
    ("ordered_neuron_ids", "fresh.field.layer.neurons-order"),
    ("source_state_digest", "output.frozen_state_digest_before-or-null"),
    ("fixed_adapter_digest", "null-for-existing-branches"),
    ("kernel_name", "converter-branch-constant"),
    ("field_execution_kind", "real-in-memory-common-probe"),
    ("claims_permitted", "false-from-output-claim-flags"),
    ("receipt_digest", "digest-of-complete-common-receipt"),
)
S1_FZ_FIXED_WRAPPER_REQUIRED_OUTPUTS = (
    "binding_digest",
    "terminal_field_digest",
    "ordered_neuron_ids",
    "activation_vector",
    "afterimage_vector",
    "field_step_count",
    "source_support_count",
    "source_state_digest",
    "fixed_adapter_digest",
    "source_state_preserved",
    "persistence_performed",
    "claims_permitted",
)
S1_FZ_FIXED_WRAPPER_INVARIANTS = (
    "fresh-field-object-separated",
    "source-state-object-never-passed-to-field-kernel",
    "fixed-adapter-derived-before-probe-and-held-constant",
    "source-state-digest-attested-before-and-after-wrapper",
    "adapter-digest-attested-before-and-after-wrapper",
    "same-probe-plan-and-source-as-p0-and-frozen-e1",
    "raw-vectors-returned-in-field-neuron-order",
    "in-memory-no-persistence-no-claims",
)
S1_FZ_CHECK_NAMES = (
    "common-receipt-schema-has-twenty-two-fields",
    "existing-output-direct-fields-all-present",
    "resolved-context-carries-binding-and-probe-source",
    "fresh-context-carries-initial-field-and-neuron-order",
    "p0-and-frozen-e1-are-losslessly-convertible-with-context",
    "fixed-adapter-field-kernel-exists",
    "fixed-adapter-real-wrapper-does-not-exist",
    "audit-calls-no-probe-kernel-or-writer",
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
class E1FormationS1FZStaticRealReceiptBoundary:
    audit_id: str
    common_receipt_fields: tuple[str, ...]
    existing_real_output_fields: tuple[str, ...]
    existing_context_types: tuple[str, ...]
    existing_branches: tuple[str, ...]
    direct_output_mapping: tuple[tuple[str, str], ...]
    bound_context_mapping: tuple[tuple[str, str], ...]
    fixed_wrapper_required_outputs: tuple[str, ...]
    fixed_wrapper_invariants: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    existing_converter_lossless_with_bound_context: bool
    existing_wrapper_change_required: bool
    existing_converter_implemented: bool
    fixed_adapter_field_kernel_exists: bool
    fixed_adapter_real_wrapper_implemented: bool
    fixed_adapter_wrapper_implementation_permitted: bool
    execution_permitted: bool
    field_execution_performed: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if (
            self.audit_id != S1_FZ_AUDIT_ID
            or len(self.common_receipt_fields) != 22
            or self.existing_context_types != S1_FZ_EXISTING_CONTEXT_TYPES
            or self.existing_branches != S1_FZ_EXISTING_BRANCHES
            or self.direct_output_mapping != S1_FZ_DIRECT_OUTPUT_MAPPING
            or self.bound_context_mapping != S1_FZ_BOUND_CONTEXT_MAPPING
            or self.fixed_wrapper_required_outputs
            != S1_FZ_FIXED_WRAPPER_REQUIRED_OUTPUTS
            or self.fixed_wrapper_invariants != S1_FZ_FIXED_WRAPPER_INVARIANTS
            or tuple(name for name, _ in self.checks) != S1_FZ_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.existing_converter_lossless_with_bound_context,
                    self.fixed_adapter_field_kernel_exists,
                )
            )
            or any(
                value is not False
                for value in (
                    self.existing_wrapper_change_required,
                    self.existing_converter_implemented,
                    self.fixed_adapter_real_wrapper_implemented,
                    self.fixed_adapter_wrapper_implementation_permitted,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "EXISTING_BRANCHES_CONVERTIBLE_FIXED_WRAPPER_CONTRACT_MISSING"
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1FormationS1FZStaticRealReceiptBoundaryError(
                "S1-FZ boundary changed or opened execution"
            )


def audit_e1_formation_s1fz_static_real_receipt_boundary(
) -> E1FormationS1FZStaticRealReceiptBoundary:
    """Compare interfaces and provenance without invoking a probe kernel."""

    receipt_fields = tuple(E1FormationS1FYCommonProbeReceipt.__dataclass_fields__)
    output_fields = tuple(E1CommonProbeRealProbeOutput.__dataclass_fields__)
    resolved_fields = tuple(E1CommonProbeResolvedSlot.__dataclass_fields__)
    fresh_fields = tuple(E1CommonProbeFreshField.__dataclass_fields__)
    direct_sources = tuple(source for _, source in S1_FZ_DIRECT_OUTPUT_MAPPING)
    audit_source = inspect.getsource(
        audit_e1_formation_s1fz_static_real_receipt_boundary
    )
    forbidden_calls = {
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "advance_frozen_e1_fast_shared_field_transient",
        "advance_neutral_fast_shared_field_transient",
        "run_e1_common_probe_real_probe_wrapper",
        "open",
        "write_text",
        "write_bytes",
    }
    module_names = globals()
    fixed_wrapper_names = (
        "run_e1_common_probe_fixed_adapter_wrapper",
        "convert_e1_common_probe_real_output_to_receipt",
    )
    checks = (
        (S1_FZ_CHECK_NAMES[0], len(receipt_fields) == 22),
        (
            S1_FZ_CHECK_NAMES[1],
            all(source in output_fields for source in direct_sources),
        ),
        (
            S1_FZ_CHECK_NAMES[2],
            all(name in resolved_fields for name in ("binding", "probe_sequences")),
        ),
        (
            S1_FZ_CHECK_NAMES[3],
            all(name in fresh_fields for name in ("initial_field_digest", "field")),
        ),
        (
            S1_FZ_CHECK_NAMES[4],
            len(S1_FZ_DIRECT_OUTPUT_MAPPING) + len(S1_FZ_BOUND_CONTEXT_MAPPING)
            == len(receipt_fields),
        ),
        (
            S1_FZ_CHECK_NAMES[5],
            callable(advance_fixed_e1_adapter_fast_shared_field_transient),
        ),
        (
            S1_FZ_CHECK_NAMES[6],
            all(name not in module_names for name in fixed_wrapper_names),
        ),
        (S1_FZ_CHECK_NAMES[7], _called_names(audit_source).isdisjoint(forbidden_calls)),
    )
    values = {
        "audit_id": S1_FZ_AUDIT_ID,
        "common_receipt_fields": receipt_fields,
        "existing_real_output_fields": output_fields,
        "existing_context_types": S1_FZ_EXISTING_CONTEXT_TYPES,
        "existing_branches": S1_FZ_EXISTING_BRANCHES,
        "direct_output_mapping": S1_FZ_DIRECT_OUTPUT_MAPPING,
        "bound_context_mapping": S1_FZ_BOUND_CONTEXT_MAPPING,
        "fixed_wrapper_required_outputs": S1_FZ_FIXED_WRAPPER_REQUIRED_OUTPUTS,
        "fixed_wrapper_invariants": S1_FZ_FIXED_WRAPPER_INVARIANTS,
        "checks": checks,
        "existing_converter_lossless_with_bound_context": True,
        "existing_wrapper_change_required": False,
        "existing_converter_implemented": False,
        "fixed_adapter_field_kernel_exists": True,
        "fixed_adapter_real_wrapper_implemented": False,
        "fixed_adapter_wrapper_implementation_permitted": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "EXISTING_BRANCHES_CONVERTIBLE_FIXED_WRAPPER_CONTRACT_MISSING"
        ),
        "reason": (
            "p0-and-frozen-e1-output-plus-resolved-and-fresh-context-cover-"
            "the-common-receipt-losslessly;fixed-adapter-kernel-exists-but-"
            "its-real-wrapper-and-explicit-output-contract-do-not"
        ),
    }
    return E1FormationS1FZStaticRealReceiptBoundary(
        **values,
        audit_digest=_digest(values),
    )
