"""S1-GG static binding of the real fixed-adapter probe kernel chain."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_real_wrappers import run_e1_common_probe_real_probe_wrapper
from .e1_formation_s1fi_fresh_capture_preflight import E1FormationS1FIPreparedInputs
from .e1_formation_s1fx_common_probe_receipt_contract import S1_FX_RECEIPT_SCHEMA
from .e1_formation_s1gd_fixed_adapter_invocation_binding import (
    E1FormationS1GDFixedAdapterInvocation,
)
from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    E1FormationS1GFFixedAdapterPositiveWrapperFixtureResult,
    run_e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1FormationS1GGStaticFixedAdapterRealKernelBindingError(ValueError):
    """Raised when the static real-kernel boundary changes or opens execution."""


S1_GG_AUDIT_ID = "e1.static-fixed-adapter-real-kernel-binding.s1gg.v1"
S1_GG_KERNEL_CHAIN = (
    "fresh-object-separated-shared-field",
    "map_proposal_batch_to_transient_docks",
    "project_transient_docks_to_neuron_inputs",
    "construct-empty-boundary-receptor-distribution",
    "advance_fixed_e1_adapter_fast_shared_field_transient",
    "snapshot-terminal-raw-vectors",
    "convert-to-s1fx-common-receipt",
)
S1_GG_CONFIG_BINDING = (
    ("substrate_config", "NeutralLocalFieldSubstrateConfig", "strength=1.0"),
    ("afterimage_config", "NeutralFastAfterimageConfig", "leak_rate=0.5"),
    ("dissipation_config", "None", "existing-default"),
)
S1_GG_AVAILABLE_OBJECTS = (
    "s1gd-exact-binding",
    "s1gc-exact-probe-sequences",
    "s1gc-exact-probe-plan-and-batches",
    "s1gd-source-state-for-attestation-only",
    "s1gd-fixed-adapter-for-kernel",
    "s1fi-neutral-initial-field-upstream",
)
S1_GG_MISSING_OBJECTS = (
    "six-object-separated-fresh-fields-bound-to-s1gd-invocations",
)
S1_GG_CHECK_NAMES = (
    "s1gf-positive-interface-remains-injected-and-synthetic",
    "s1gd-carries-context-state-and-fixed-adapter",
    "s1gd-carries-no-fresh-field-object",
    "s1fi-carries-neutral-initial-field-object",
    "batch-to-dock-signature-compatible",
    "dock-to-neuron-input-signature-compatible",
    "fixed-adapter-kernel-signature-compatible",
    "fixed-kernel-excludes-live-e1-state",
    "existing-wrapper-binds-config-distribution-and-snapshot-pattern",
    "s1fx-common-receipt-schema-complete",
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
class E1FormationS1GGStaticFixedAdapterRealKernelBindingAudit:
    audit_id: str
    kernel_chain: tuple[str, ...]
    config_binding: tuple[tuple[str, str, str], ...]
    available_objects: tuple[str, ...]
    missing_objects: tuple[str, ...]
    s1gf_fixture_parameters: tuple[str, ...]
    dock_mapper_parameters: tuple[str, ...]
    neuron_projector_parameters: tuple[str, ...]
    fixed_kernel_parameters: tuple[str, ...]
    common_receipt_fields: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    real_kernel_chain_compatible: bool
    exact_probe_batches_available: bool
    exact_fixed_adapter_available: bool
    source_state_attestation_available: bool
    upstream_initial_field_available: bool
    fresh_field_present_in_s1gd_invocation: bool
    fresh_field_bridge_required: bool
    fixed_adapter_real_wrapper_implemented: bool
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
            self.audit_id != S1_GG_AUDIT_ID
            or self.kernel_chain != S1_GG_KERNEL_CHAIN
            or self.config_binding != S1_GG_CONFIG_BINDING
            or self.available_objects != S1_GG_AVAILABLE_OBJECTS
            or self.missing_objects != S1_GG_MISSING_OBJECTS
            or self.s1gf_fixture_parameters
            != ("bindings", "gate", "counting_kernel")
            or self.dock_mapper_parameters != ("batch", "docks")
            or self.neuron_projector_parameters != ("trajectory", "docks")
            or self.fixed_kernel_parameters
            != (
                "field",
                "fixed_adapter",
                "distribution",
                "transient_inputs",
                "substrate_config",
                "afterimage_config",
                "dissipation_config",
            )
            or self.common_receipt_fields != S1_FX_RECEIPT_SCHEMA
            or tuple(name for name, _ in self.checks) != S1_GG_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.real_kernel_chain_compatible,
                    self.exact_probe_batches_available,
                    self.exact_fixed_adapter_available,
                    self.source_state_attestation_available,
                    self.upstream_initial_field_available,
                    self.fresh_field_bridge_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.fresh_field_present_in_s1gd_invocation,
                    self.fixed_adapter_real_wrapper_implemented,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "REAL_FIXED_ADAPTER_KERNEL_CHAIN_BOUND_FRESH_FIELD_BRIDGE_MISSING"
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1FormationS1GGStaticFixedAdapterRealKernelBindingError(
                "S1-GG audit changed, hid the fresh-field gap, or opened execution"
            )


def audit_e1_formation_s1gg_static_fixed_adapter_real_kernel_binding(
) -> E1FormationS1GGStaticFixedAdapterRealKernelBindingAudit:
    """Inspect the exact real-kernel chain without invoking any runtime path."""

    invocation_fields = tuple(
        E1FormationS1GDFixedAdapterInvocation.__dataclass_fields__
    )
    input_fields = tuple(E1FormationS1FIPreparedInputs.__dataclass_fields__)
    fixture_fields = tuple(
        E1FormationS1GFFixedAdapterPositiveWrapperFixtureResult.__dataclass_fields__
    )
    fixture_parameters = tuple(
        inspect.signature(
            run_e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture
        ).parameters
    )
    mapper_parameters = tuple(
        inspect.signature(map_proposal_batch_to_transient_docks).parameters
    )
    projector_parameters = tuple(
        inspect.signature(project_transient_docks_to_neuron_inputs).parameters
    )
    kernel_parameters = tuple(
        inspect.signature(
            advance_fixed_e1_adapter_fast_shared_field_transient
        ).parameters
    )
    existing_wrapper_source = inspect.getsource(
        run_e1_common_probe_real_probe_wrapper
    )
    audit_source = inspect.getsource(
        audit_e1_formation_s1gg_static_fixed_adapter_real_kernel_binding
    )
    forbidden_calls = {
        "map_proposal_batch_to_transient_docks",
        "project_transient_docks_to_neuron_inputs",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "advance_frozen_e1_fast_shared_field_transient",
        "advance_neutral_fast_shared_field_transient",
        "open",
        "write_text",
        "write_bytes",
    }
    required_receipt_fields = {
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
        "fixed_adapter_digest",
        "kernel_name",
        "field_execution_kind",
        "receipt_digest",
    }
    checks = (
        (
            S1_GG_CHECK_NAMES[0],
            fixture_parameters == ("bindings", "gate", "counting_kernel")
            and "actual_field_steps_executed" in fixture_fields
            and "real_kernel_called" in fixture_fields,
        ),
        (
            S1_GG_CHECK_NAMES[1],
            all(
                name in invocation_fields
                for name in ("context", "source_state", "fixed_adapter")
            ),
        ),
        (
            S1_GG_CHECK_NAMES[2],
            "fresh_field" not in invocation_fields
            and "initial_field" not in invocation_fields,
        ),
        (S1_GG_CHECK_NAMES[3], "initial_field" in input_fields),
        (S1_GG_CHECK_NAMES[4], mapper_parameters == ("batch", "docks")),
        (
            S1_GG_CHECK_NAMES[5],
            projector_parameters == ("trajectory", "docks"),
        ),
        (
            S1_GG_CHECK_NAMES[6],
            kernel_parameters
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
            S1_GG_CHECK_NAMES[7],
            "state" not in kernel_parameters
            and "frozen_e1_state" not in kernel_parameters,
        ),
        (
            S1_GG_CHECK_NAMES[8],
            all(
                token in existing_wrapper_source
                for token in (
                    "NeutralLocalFieldSubstrateConfig(1.0)",
                    "NeutralFastAfterimageConfig(0.5)",
                    "ReceptorDistribution(",
                    "CommonFieldTime(",
                    "current.snapshot()",
                )
            )
            and inspect.isclass(SharedMCMField)
            and inspect.isclass(ReceptorDistribution)
            and inspect.isclass(CommonFieldTime)
            and inspect.isclass(NeutralLocalFieldSubstrateConfig)
            and inspect.isclass(NeutralFastAfterimageConfig),
        ),
        (
            S1_GG_CHECK_NAMES[9],
            required_receipt_fields.issubset(S1_FX_RECEIPT_SCHEMA),
        ),
        (
            S1_GG_CHECK_NAMES[10],
            _called_names(audit_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "audit_id": S1_GG_AUDIT_ID,
        "kernel_chain": S1_GG_KERNEL_CHAIN,
        "config_binding": S1_GG_CONFIG_BINDING,
        "available_objects": S1_GG_AVAILABLE_OBJECTS,
        "missing_objects": S1_GG_MISSING_OBJECTS,
        "s1gf_fixture_parameters": fixture_parameters,
        "dock_mapper_parameters": mapper_parameters,
        "neuron_projector_parameters": projector_parameters,
        "fixed_kernel_parameters": kernel_parameters,
        "common_receipt_fields": S1_FX_RECEIPT_SCHEMA,
        "checks": checks,
        "real_kernel_chain_compatible": all(value for _, value in checks),
        "exact_probe_batches_available": "context" in invocation_fields,
        "exact_fixed_adapter_available": "fixed_adapter" in invocation_fields,
        "source_state_attestation_available": "source_state" in invocation_fields,
        "upstream_initial_field_available": "initial_field" in input_fields,
        "fresh_field_present_in_s1gd_invocation": False,
        "fresh_field_bridge_required": True,
        "fixed_adapter_real_wrapper_implemented": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "REAL_FIXED_ADAPTER_KERNEL_CHAIN_BOUND_FRESH_FIELD_BRIDGE_MISSING"
        ),
        "reason": (
            "batch-dock-neuron-fixed-kernel-snapshot-receipt-chain-is-"
            "signature-compatible;ten-role-invocations-carry-context-state-"
            "and-adapter-but-no-object-separated-fresh-initial-field"
        ),
    }
    return E1FormationS1GGStaticFixedAdapterRealKernelBindingAudit(
        **values,
        audit_digest=_digest(values),
    )
