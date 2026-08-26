"""S1-GM static real batch-adapter binding and live-field carrier gap."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1gh_fresh_field_bridge import E1FormationS1GHFreshFieldBinding
from .e1_formation_s1gl_private_fixed_adapter_wrapper import (
    build_e1_formation_s1gl_synthetic_batch_receipt,
    build_e1_formation_s1gl_synthetic_terminal_output,
    run_e1_formation_s1gl_private_fixed_adapter_wrapper,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1FormationS1GMRealBatchAdapterBindingError(ValueError):
    """Raised when S1-GM hides the live-field carrier gap or opens execution."""


S1_GM_AUDIT_ID = "e1.real-batch-adapter-binding.s1gm.v1"
S1_GM_REAL_BATCH_CHAIN = (
    "receive-current-shared-field-object",
    "map-proposal-batch-to-current-field-docks",
    "project-transient-docks-to-neuron-inputs",
    "construct-empty-boundary-distribution",
    "advance-current-field-with-exact-fixed-adapter",
    "return-next-shared-field-object",
)
S1_GM_CURRENT_S1GL_BATCH_INTERFACE = (
    ("fresh", "E1FormationS1GHFreshFieldBinding"),
    ("batch", "ReceptorProposalBatch"),
    ("current_field_token_digest", "str"),
    ("return", "E1FormationS1GLSyntheticBatchReceipt"),
)
S1_GM_REQUIRED_BATCH_INTERFACE = (
    ("fresh", "E1FormationS1GHFreshFieldBinding"),
    ("batch", "ReceptorProposalBatch"),
    ("carrier", "E1FormationS1GNLiveFieldCarrier"),
    ("return", "E1FormationS1GNLiveFieldCarrierTransition"),
)
S1_GM_CURRENT_TERMINAL_INTERFACE = (
    ("fresh", "E1FormationS1GHFreshFieldBinding"),
    ("terminal_field_token_digest", "str"),
    ("return", "E1FormationS1GIFixedAdapterRealOutput"),
)
S1_GM_REQUIRED_TERMINAL_INTERFACE = (
    ("fresh", "E1FormationS1GHFreshFieldBinding"),
    ("carrier", "E1FormationS1GNLiveFieldCarrier"),
    ("return", "E1FormationS1GIFixedAdapterRealOutput"),
)
S1_GM_REQUIRED_CARRIER_FIELDS = (
    "binding_digest",
    "initial_field_digest",
    "current_field",
    "current_field_digest",
    "completed_batch_count",
    "accounted_source_support_count",
    "actual_field_steps_executed",
    "carrier_digest",
)
S1_GM_FORBIDDEN_STATE_SHORTCUTS = (
    "module-global-current-field",
    "binding-keyed-hidden-field-dictionary",
    "closure-owned-mutable-field",
    "in-place-mutation-of-s1gh-fresh-field",
    "terminal-snapshot-from-digest-token",
)
S1_GM_CHECK_NAMES = (
    "s1gl-wrapper-uses-injected-batch-and-terminal-functions",
    "s1gl-current-batch-interface-is-token-only",
    "s1gl-current-terminal-interface-is-token-only",
    "s1gh-fresh-binding-carries-initial-shared-field",
    "real-batch-chain-requires-and-returns-shared-field",
    "batch-dock-and-neuron-signatures-compatible",
    "fixed-kernel-signature-compatible-and-state-free",
    "explicit-live-field-carrier-is-minimal-missing-object",
    "audit-calls-no-field-kernel-or-writer",
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
class E1FormationS1GMRealBatchAdapterBindingAudit:
    audit_id: str
    real_batch_chain: tuple[str, ...]
    current_s1gl_batch_interface: tuple[tuple[str, str], ...]
    required_batch_interface: tuple[tuple[str, str], ...]
    current_terminal_interface: tuple[tuple[str, str], ...]
    required_terminal_interface: tuple[tuple[str, str], ...]
    required_carrier_fields: tuple[str, ...]
    forbidden_state_shortcuts: tuple[str, ...]
    wrapper_parameters: tuple[str, ...]
    current_batch_parameters: tuple[str, ...]
    current_terminal_parameters: tuple[str, ...]
    real_kernel_parameters: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    real_kernel_chain_exists: bool
    current_s1gl_interface_carries_live_field: bool
    current_s1gl_interface_directly_real_compatible: bool
    hidden_mutable_field_state_permitted: bool
    explicit_live_field_carrier_required: bool
    wrapper_interface_revision_required: bool
    live_field_carrier_implementation_permitted: bool
    real_batch_adapter_implementation_permitted: bool
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
            self.audit_id != S1_GM_AUDIT_ID
            or self.real_batch_chain != S1_GM_REAL_BATCH_CHAIN
            or self.current_s1gl_batch_interface != S1_GM_CURRENT_S1GL_BATCH_INTERFACE
            or self.required_batch_interface != S1_GM_REQUIRED_BATCH_INTERFACE
            or self.current_terminal_interface != S1_GM_CURRENT_TERMINAL_INTERFACE
            or self.required_terminal_interface != S1_GM_REQUIRED_TERMINAL_INTERFACE
            or self.required_carrier_fields != S1_GM_REQUIRED_CARRIER_FIELDS
            or self.forbidden_state_shortcuts != S1_GM_FORBIDDEN_STATE_SHORTCUTS
            or self.wrapper_parameters
            != (
                "contract",
                "bridge",
                "gate",
                "batch_kernel",
                "terminal_output_factory",
            )
            or self.current_batch_parameters
            != ("fresh", "batch", "current_field_token_digest")
            or self.current_terminal_parameters
            != ("fresh", "terminal_field_token_digest")
            or self.real_kernel_parameters
            != (
                "field",
                "fixed_adapter",
                "distribution",
                "transient_inputs",
                "substrate_config",
                "afterimage_config",
                "dissipation_config",
            )
            or tuple(name for name, _ in self.checks) != S1_GM_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.real_kernel_chain_exists,
                    self.explicit_live_field_carrier_required,
                    self.wrapper_interface_revision_required,
                    self.live_field_carrier_implementation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.current_s1gl_interface_carries_live_field,
                    self.current_s1gl_interface_directly_real_compatible,
                    self.hidden_mutable_field_state_permitted,
                    self.real_batch_adapter_implementation_permitted,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "REAL_BATCH_CHAIN_EXISTS_EXPLICIT_LIVE_FIELD_CARRIER_REQUIRED"
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1FormationS1GMRealBatchAdapterBindingError(
                "S1-GM audit changed, hid the carrier gap, or opened execution"
            )


def audit_e1_formation_s1gm_real_batch_adapter_binding(
) -> E1FormationS1GMRealBatchAdapterBindingAudit:
    """Compare synthetic injection and real field signatures without execution."""

    wrapper_parameters = tuple(
        inspect.signature(run_e1_formation_s1gl_private_fixed_adapter_wrapper).parameters
    )
    batch_parameters = tuple(
        inspect.signature(build_e1_formation_s1gl_synthetic_batch_receipt).parameters
    )
    terminal_parameters = tuple(
        inspect.signature(build_e1_formation_s1gl_synthetic_terminal_output).parameters
    )
    mapper_parameters = tuple(
        inspect.signature(map_proposal_batch_to_transient_docks).parameters
    )
    projector_parameters = tuple(
        inspect.signature(project_transient_docks_to_neuron_inputs).parameters
    )
    kernel_signature = inspect.signature(
        advance_fixed_e1_adapter_fast_shared_field_transient
    )
    kernel_parameters = tuple(kernel_signature.parameters)
    fresh_fields = tuple(E1FormationS1GHFreshFieldBinding.__dataclass_fields__)
    audit_source = inspect.getsource(
        audit_e1_formation_s1gm_real_batch_adapter_binding
    )
    forbidden_calls = {
        "map_proposal_batch_to_transient_docks",
        "project_transient_docks_to_neuron_inputs",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "open",
        "write_text",
        "write_bytes",
    }
    expected_kernel_parameters = (
        "field",
        "fixed_adapter",
        "distribution",
        "transient_inputs",
        "substrate_config",
        "afterimage_config",
        "dissipation_config",
    )
    checks = (
        (
            S1_GM_CHECK_NAMES[0],
            wrapper_parameters
            == (
                "contract",
                "bridge",
                "gate",
                "batch_kernel",
                "terminal_output_factory",
            ),
        ),
        (
            S1_GM_CHECK_NAMES[1],
            batch_parameters == ("fresh", "batch", "current_field_token_digest"),
        ),
        (
            S1_GM_CHECK_NAMES[2],
            terminal_parameters == ("fresh", "terminal_field_token_digest"),
        ),
        (
            S1_GM_CHECK_NAMES[3],
            "fresh_field" in fresh_fields
            and "initial_field_digest" in fresh_fields
            and inspect.isclass(SharedMCMField),
        ),
        (
            S1_GM_CHECK_NAMES[4],
            kernel_parameters == expected_kernel_parameters
            and kernel_signature.return_annotation in (SharedMCMField, "SharedMCMField"),
        ),
        (
            S1_GM_CHECK_NAMES[5],
            mapper_parameters == ("batch", "docks")
            and projector_parameters == ("trajectory", "docks"),
        ),
        (
            S1_GM_CHECK_NAMES[6],
            kernel_parameters == expected_kernel_parameters
            and "state" not in kernel_parameters
            and "frozen_e1_state" not in kernel_parameters,
        ),
        (
            S1_GM_CHECK_NAMES[7],
            "current_field" in S1_GM_REQUIRED_CARRIER_FIELDS
            and "current_field_digest" in S1_GM_REQUIRED_CARRIER_FIELDS
            and "current_field" not in batch_parameters
            and "carrier" not in batch_parameters,
        ),
        (
            S1_GM_CHECK_NAMES[8],
            _called_names(audit_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "audit_id": S1_GM_AUDIT_ID,
        "real_batch_chain": S1_GM_REAL_BATCH_CHAIN,
        "current_s1gl_batch_interface": S1_GM_CURRENT_S1GL_BATCH_INTERFACE,
        "required_batch_interface": S1_GM_REQUIRED_BATCH_INTERFACE,
        "current_terminal_interface": S1_GM_CURRENT_TERMINAL_INTERFACE,
        "required_terminal_interface": S1_GM_REQUIRED_TERMINAL_INTERFACE,
        "required_carrier_fields": S1_GM_REQUIRED_CARRIER_FIELDS,
        "forbidden_state_shortcuts": S1_GM_FORBIDDEN_STATE_SHORTCUTS,
        "wrapper_parameters": wrapper_parameters,
        "current_batch_parameters": batch_parameters,
        "current_terminal_parameters": terminal_parameters,
        "real_kernel_parameters": kernel_parameters,
        "checks": checks,
        "real_kernel_chain_exists": all(value for _, value in checks),
        "current_s1gl_interface_carries_live_field": False,
        "current_s1gl_interface_directly_real_compatible": False,
        "hidden_mutable_field_state_permitted": False,
        "explicit_live_field_carrier_required": True,
        "wrapper_interface_revision_required": True,
        "live_field_carrier_implementation_permitted": True,
        "real_batch_adapter_implementation_permitted": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "REAL_BATCH_CHAIN_EXISTS_EXPLICIT_LIVE_FIELD_CARRIER_REQUIRED"
        ),
        "reason": (
            "s1gl-token-only-interface-validates-control-flow-but-cannot-"
            "explicitly-pass-next-shared-field-to-next-batch-or-terminal-"
            "snapshot;hidden-closure-or-global-state-forbidden;typed-live-"
            "field-carrier-required-before-real-batch-adapter"
        ),
    }
    return E1FormationS1GMRealBatchAdapterBindingAudit(
        **values,
        audit_digest=_digest(values),
    )
