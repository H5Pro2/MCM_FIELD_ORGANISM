"""Private S1-JW adapters for six preregistered technical baselines."""

from __future__ import annotations

from dataclasses import dataclass, fields
import functools
import hashlib
import json
import math
from typing import Mapping

from .dynamic_substrate_dts1_backreaction import (
    DTS1BackreactionEdgeRate,
    DTS1BackreactionError,
    DTS1BackreactionResult,
)
from .dynamic_substrate_dts1_common_interval_materializer import (
    DTS1CommonIntervalPrivateState,
    DTS1CommonModelInvocation,
    _field_payload,
)
from .dynamic_substrate_dts1_coupled_step import (
    DTS1CoupledStepError,
    _advance_active_field,
)
from .dynamic_substrate_s1jt_finite_adapter_payload_contract import (
    S1_JT_B1_FIXED_ADAPTER_SCHEMA,
    S1_JT_B6_SPEC_DIGEST,
    S1_JT_B6_SPEC_PAYLOAD,
    S1_JT_CONFIGURATION_DIGESTS,
    S1_JT_F3_RUNTIME_RECORDS,
    build_dts1_s1jt_finite_adapter_payload_contract,
)
from .dynamic_substrate_s1jv_finite_geometry_digest_mapping_contract import (
    S1_JV_GEOMETRY_DIGEST_MAPPINGS,
    build_dts1_s1jv_finite_geometry_digest_mapping_contract,
)
from .mcm_f3_baseline_coupling import (
    MCMF3BaselineCouplingError,
    compute_mcm_f3_linear_coupled_baseline,
    compute_mcm_f3_local_leaky_baseline,
)
from .mcm_f3_coupling import MCMF3CouplingError, compute_mcm_f3_coupling
from .mcm_f3_runtime import MCMF3RuntimeError, advance_mcm_f3_shared_field
from .mcm_neuron_layer import MCMNeuronDrive, MCMNeuronOutput
from .mcm_substrate_state import (
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory_digest,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    _generator_and_boundary,
)
from .s2_reference_baselines import (
    S2ReferenceBaselineError,
    S2ReferenceModelConfig,
    S2ReferenceState,
    advance_s2_reference_model,
)
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError
from .w7m_capacity_function_matrix import W7MBaselineSpec
from .w7n_capacity_function_baselines import (
    W7NCapacityFunctionBaselineError,
    compute_w7n_coupling_baseline,
)


class DTS1PrivateBaselineAdapterError(ValueError):
    """Raised atomically before publishing an invalid adapter result."""


S1_JW_IMPLEMENTATION_ID = "dynamic-substrate.private-baseline-adapters.s1jw.v1"
S1_JW_SOURCE_S1JT_DIGEST = (
    "10a01aa9275a3bb571f3d5113126e90a0183d862c42cf1a9f8a2b58da1285d40"
)
S1_JW_SOURCE_S1JV_DIGEST = (
    "8878cc42b423cfed7721e39dc56181f870a0c76832cccee48aac592f5390fd30"
)
S1_JW_ROLES = ("B1", "B2", "B3", "B4", "B5", "B6")
S1_JW_CONFIGURATION_DIGESTS = dict(
    zip(S1_JW_ROLES, (row[1] for row in S1_JT_CONFIGURATION_DIGESTS), strict=True)
)
S1_JW_DECISION = (
    "SIX_PRIVATE_BASELINE_ADAPTERS_IMPLEMENTED_TECHNICALLY_ACCEPTED_NO_PROFILE_EXECUTION"
)

_COMMON_SUBSTRATE_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
_COMMON_AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)
_COMMON_DISSIPATION_CONFIG = NeutralFieldDissipationConfig(0.0)
_S2_CONFIG = S2ReferenceModelConfig()
_B6_SPEC_VALUES = dict(S1_JT_B6_SPEC_PAYLOAD)
_B6_SPEC_VALUES.pop("schema_id")
_B6_SPEC = W7MBaselineSpec(**_B6_SPEC_VALUES)
_F3_RECORDS = {row[0]: row for row in S1_JT_F3_RUNTIME_RECORDS}


def _canonicalize(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise DTS1PrivateBaselineAdapterError("canonical number must be finite")
        return 0.0 if value == 0.0 else value
    if isinstance(value, (tuple, list)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise DTS1PrivateBaselineAdapterError(
                "canonical mapping keys must be strings"
            )
        return {key: _canonicalize(value[key]) for key in sorted(value)}
    raise DTS1PrivateBaselineAdapterError("canonical payload contains an object")


def _digest(value: object) -> str:
    encoded = json.dumps(
        _canonicalize(value),
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1PrivateBaselineAdapterContext:
    model_role: str
    private_state: DTS1CommonIntervalPrivateState
    configuration_digest: str
    refinement: int

    def __post_init__(self) -> None:
        if self.model_role not in S1_JW_ROLES:
            raise DTS1PrivateBaselineAdapterError("adapter role is not registered")
        if (
            not isinstance(self.private_state, DTS1CommonIntervalPrivateState)
            or self.private_state.model_role != self.model_role
        ):
            raise DTS1PrivateBaselineAdapterError(
                "private state must match the adapter role"
            )
        expected = S1_JW_CONFIGURATION_DIGESTS[self.model_role]
        if self.configuration_digest != expected:
            raise DTS1PrivateBaselineAdapterError(
                "configuration digest does not match the role"
            )
        state_config = dict(self.private_state.payload)[self.private_state.payload[-1][0]]
        if state_config != expected:
            raise DTS1PrivateBaselineAdapterError(
                "private state configuration digest does not match the role"
            )
        if self.refinement not in (2, 4, 8):
            raise DTS1PrivateBaselineAdapterError(
                "refinement must be one of the three registered controls"
            )


@dataclass(frozen=True, slots=True)
class DTS1PrivateBaselineAdapterOutput:
    complete_field: SharedMCMField
    next_private_state: DTS1CommonIntervalPrivateState
    diagnostics: tuple[tuple[str, object], ...]
    output_digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.complete_field, SharedMCMField):
            raise DTS1PrivateBaselineAdapterError("output requires a complete field")
        if not isinstance(self.next_private_state, DTS1CommonIntervalPrivateState):
            raise DTS1PrivateBaselineAdapterError("output requires private state")
        diagnostics = tuple(self.diagnostics)
        if not diagnostics or any(
            not isinstance(row, tuple) or len(row) != 2 for row in diagnostics
        ):
            raise DTS1PrivateBaselineAdapterError("diagnostics must be key-value rows")
        object.__setattr__(self, "diagnostics", diagnostics)
        payload = _output_payload(
            self.next_private_state.model_role,
            self.complete_field,
            self.next_private_state,
            diagnostics,
        )
        if self.output_digest != _digest(payload):
            raise DTS1PrivateBaselineAdapterError("output digest does not match output")

    def canonical_payload(self) -> dict[str, object]:
        return _output_payload(
            self.next_private_state.model_role,
            self.complete_field,
            self.next_private_state,
            self.diagnostics,
        )


def _output_payload(role, field, state, diagnostics) -> dict[str, object]:
    return {
        "schema_id": "mcm.s1jt.complete-baseline-adapter-output.v1",
        "model_role": role,
        "complete_field": _field_payload(field),
        "next_private_state": state.canonical_payload(),
        "diagnostics": dict(diagnostics),
    }


def _mapping(invocation: DTS1CommonModelInvocation) -> tuple[object, ...]:
    if not isinstance(invocation, DTS1CommonModelInvocation):
        raise DTS1PrivateBaselineAdapterError(
            "adapter requires one four-value model invocation"
        )
    field = invocation.materialized_field
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    inventory = tuple((item.neuron_id, item.position) for item in neurons)
    matches = tuple(
        row
        for row in S1_JV_GEOMETRY_DIGEST_MAPPINGS
        if row[1] == field.field_id and row[4] == inventory
    )
    if len(matches) != 1:
        raise DTS1PrivateBaselineAdapterError(
            "field identity and node inventory select no unique digest mapping"
        )
    row = matches[0]
    if (
        field.layer.layer_id != row[2]
        or field.geometry_id != row[3]
        or tuple(item.neuron_id for item in neurons) != row[5]
        or invocation.geometry_digest != row[6]
        or mcm_substrate_edge_inventory_digest(field.layer) != row[7]
    ):
        raise DTS1PrivateBaselineAdapterError(
            "outer or internal geometry role does not match the selected mapping"
        )
    return row


def _fixed_adapter(state, row) -> DTS1BackreactionResult:
    payload = dict(state.payload)["fixed_adapter_payload"]
    if not isinstance(payload, Mapping) or set(payload) != {
        "schema_id", "backreaction_enabled", "base_rate_per_second",
        "edge_inventory_digest", "edge_rates",
    }:
        raise DTS1PrivateBaselineAdapterError("B1 payload fields are incomplete")
    schema = dict(S1_JT_B1_FIXED_ADAPTER_SCHEMA)
    expected_rows = schema["two_node_edges"] if len(row[5]) == 2 else schema["three_node_edges"]
    expected_rates = tuple(
        {
            "first_node_id": first,
            "second_node_id": second,
            "rate_per_second": rate,
        }
        for first, second, rate in expected_rows
    )
    if (
        payload["schema_id"] != schema["schema_id"]
        or payload["backreaction_enabled"] is not True
        or payload["base_rate_per_second"] != 1.0
        or payload["edge_inventory_digest"] != row[7]
        or tuple(payload["edge_rates"]) != expected_rates
    ):
        raise DTS1PrivateBaselineAdapterError("B1 payload differs from S1-JT/S1-JV")
    return DTS1BackreactionResult(
        True,
        1.0,
        tuple(DTS1BackreactionEdgeRate(**item) for item in expected_rates),
        row[7],
    )


def _b1(invocation, context, row):
    field = invocation.materialized_field
    if field.substrate is not None or field.development is not None:
        raise DTS1PrivateBaselineAdapterError("B1 field contains foreign state")
    adapter = _fixed_adapter(context.private_state, row)
    result = _advance_active_field(
        field,
        invocation.receptor_distribution,
        invocation.step_time,
        _COMMON_SUBSTRATE_CONFIG,
        _COMMON_AFTERIMAGE_CONFIG,
        _COMMON_DISSIPATION_CONFIG,
        adapter,
        invocation.step_time.elapsed_seconds,
    )
    maxima = (
        max(abs(item.activation) for item in result.layer.neurons),
        max(abs(item.afterimage) for item in result.layer.neurons),
    )
    diagnostics = (
        ("schema_id", "mcm.s1jt.diagnostics.b1-exact.v1"),
        ("method_id", "exact-spectral"),
        ("maximum_abs_activation", maxima[0]),
        ("maximum_abs_afterimage", maxima[1]),
    )
    return result, context.private_state, diagnostics


def _b2(invocation, context, row):
    field = invocation.materialized_field
    if field.substrate is not None or field.development is not None:
        raise DTS1PrivateBaselineAdapterError("B2 field contains foreign state")
    payload = dict(context.private_state.payload)["complete_L_state_payload"]
    if not isinstance(payload, Mapping) or set(payload) != {"schema_id", "entries"}:
        raise DTS1PrivateBaselineAdapterError("B2 L payload fields are incomplete")
    entries = tuple(payload["entries"])
    expected_nodes = row[5]
    if payload["schema_id"] != "mcm.s1jt.b2-private-L.v1" or tuple(
        item.get("node_id") for item in entries if isinstance(item, Mapping)
    ) != expected_nodes or any(set(item) != {"node_id", "value"} for item in entries):
        raise DTS1PrivateBaselineAdapterError("B2 L payload shape or order differs")
    development = tuple(float(item["value"]) for item in entries)
    if any(not math.isfinite(value) or abs(value) > 1.0 for value in development):
        raise DTS1PrivateBaselineAdapterError("B2 L payload left its finite domain")
    state = S2ReferenceState(
        tuple(item.activation for item in field.layer.neurons),
        tuple(item.afterimage for item in field.layer.neurons),
        development,
    )
    generator, boundary = _generator_and_boundary(
        field, invocation.receptor_distribution, _COMMON_SUBSTRATE_CONFIG
    )
    advanced = advance_s2_reference_model(
        "b2", state, generator, boundary, invocation.step_time.elapsed_seconds, _S2_CONFIG
    )
    outputs = {
        node: MCMNeuronOutput(advanced.state.activation[index], advanced.state.afterimage[index])
        for index, node in enumerate(expected_nodes)
    }

    def model_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    result = field.advance(
        invocation.receptor_distribution, model_output, step_time=invocation.step_time
    )
    next_payload = {
        "schema_id": "mcm.s1jt.b2-private-L.v1",
        "entries": tuple(
            {"node_id": node, "value": advanced.state.development[index]}
            for index, node in enumerate(expected_nodes)
        ),
    }
    next_state = DTS1CommonIntervalPrivateState(
        "B2",
        (
            ("complete_L_state_payload", next_payload),
            ("B2_configuration_digest", context.configuration_digest),
        ),
    )
    diagnostics = (
        ("schema_id", "mcm.s1jt.diagnostics.b2-exact.v1"),
        ("method_id", "exact-matrix-exponential"),
        ("partition_error", advanced.partition_error),
        ("maximum_abs_activation", max(abs(value) for value in advanced.state.activation)),
        ("maximum_abs_afterimage", max(abs(value) for value in advanced.state.afterimage)),
        ("maximum_abs_development", max(abs(value) for value in advanced.state.development)),
    )
    return result, next_state, diagnostics


def _f3(invocation, context, row):
    field = invocation.materialized_field
    if field.substrate is None or field.development is not None:
        raise DTS1PrivateBaselineAdapterError("F3 field has no isolated M state")
    embedded = dict(context.private_state.payload)["embedded_M_state_digest"]
    if embedded != field.substrate.digest() or field.substrate.edge_inventory_digest != row[7]:
        raise DTS1PrivateBaselineAdapterError("embedded M digest or geometry differs")
    runtime = _F3_RECORDS[context.model_role]
    arm = field.substrate.arm
    if (
        arm.arm_id != runtime[1]
        or arm.lambda_sm_per_second != runtime[2]
        or arm.kappa != runtime[3]
        or arm.eta != runtime[4]
        or arm.initial_total_mass != runtime[5]
    ):
        raise DTS1PrivateBaselineAdapterError("embedded M arm differs from S1-JT")
    calculators = {
        "B3": compute_mcm_f3_local_leaky_baseline,
        "B4": compute_mcm_f3_linear_coupled_baseline,
        "B5": compute_mcm_f3_coupling,
        "B6": functools.partial(compute_w7n_coupling_baseline, _B6_SPEC),
    }
    if context.model_role == "B6" and dict(context.private_state.payload)["frozen_CONST_V_spec_digest"] != S1_JT_B6_SPEC_DIGEST:
        raise DTS1PrivateBaselineAdapterError("B6 frozen specification digest differs")
    advanced = advance_mcm_f3_shared_field(
        field,
        invocation.receptor_distribution,
        invocation.step_time,
        _COMMON_SUBSTRATE_CONFIG,
        _COMMON_AFTERIMAGE_CONFIG,
        _COMMON_DISSIPATION_CONFIG,
        refinement=context.refinement,
        _coupling_calculator=calculators[context.model_role],
    )
    payload = [("embedded_M_state_digest", advanced.field.substrate.digest())]
    if context.model_role == "B6":
        payload.append(("frozen_CONST_V_spec_digest", S1_JT_B6_SPEC_DIGEST))
    payload.append((f"{context.model_role}_configuration_digest", context.configuration_digest))
    next_state = DTS1CommonIntervalPrivateState(context.model_role, tuple(payload))
    diagnostic = advanced.diagnostics
    diagnostics = (
        ("schema_id", "mcm.s1jt.diagnostics.f3-runtime.v1"),
        *((item.name, getattr(diagnostic, item.name)) for item in fields(diagnostic)),
    )
    return advanced.field, next_state, diagnostics


def advance_dts1_private_baseline(
    invocation: DTS1CommonModelInvocation,
    context: DTS1PrivateBaselineAdapterContext,
) -> DTS1PrivateBaselineAdapterOutput:
    """Advance one technical interval without orchestration or profile data."""

    try:
        if not isinstance(context, DTS1PrivateBaselineAdapterContext):
            raise DTS1PrivateBaselineAdapterError("adapter context is invalid")
        row = _mapping(invocation)
        if context.model_role == "B1":
            field, state, diagnostics = _b1(invocation, context, row)
        elif context.model_role == "B2":
            field, state, diagnostics = _b2(invocation, context, row)
        else:
            field, state, diagnostics = _f3(invocation, context, row)
        payload = _output_payload(context.model_role, field, state, diagnostics)
        return DTS1PrivateBaselineAdapterOutput(
            field, state, tuple(diagnostics), _digest(payload)
        )
    except DTS1PrivateBaselineAdapterError:
        raise
    except (
        DTS1BackreactionError,
        DTS1CoupledStepError,
        MCMF3BaselineCouplingError,
        MCMF3CouplingError,
        MCMF3RuntimeError,
        MCMSubstrateStateError,
        NeutralLocalFieldSubstrateError,
        S2ReferenceBaselineError,
        SharedMCMFieldError,
        W7NCapacityFunctionBaselineError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise DTS1PrivateBaselineAdapterError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class DTS1S1JWImplementationReceipt:
    implementation_id: str
    source_s1jt_digest: str
    source_s1jv_digest: str
    adapter_roles: tuple[str, ...]
    private_context_and_atomic_output_implemented: bool
    six_adapter_bridges_implemented: bool
    dual_geometry_digest_validation_implemented: bool
    technical_kernel_tests_present: bool
    profile_cases_executed: int
    runtime_integration_present: bool
    research_execution_permitted: bool
    research_field_steps_executed: int
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {f.name: getattr(self, f.name) for f in fields(self) if f.name != "receipt_digest"}
        if (
            self.implementation_id != S1_JW_IMPLEMENTATION_ID
            or self.source_s1jt_digest != S1_JW_SOURCE_S1JT_DIGEST
            or self.source_s1jv_digest != S1_JW_SOURCE_S1JV_DIGEST
            or self.adapter_roles != S1_JW_ROLES
            or not self.private_context_and_atomic_output_implemented
            or not self.six_adapter_bridges_implemented
            or not self.dual_geometry_digest_validation_implemented
            or not self.technical_kernel_tests_present
            or self.profile_cases_executed != 0
            or self.runtime_integration_present
            or self.research_execution_permitted
            or self.research_field_steps_executed != 0
            or self.decision != S1_JW_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1PrivateBaselineAdapterError("S1-JW receipt weakened")


def build_dts1_s1jw_implementation_receipt() -> DTS1S1JWImplementationReceipt:
    """Return acceptance metadata without invoking an adapter or kernel."""

    jt = build_dts1_s1jt_finite_adapter_payload_contract()
    jv = build_dts1_s1jv_finite_geometry_digest_mapping_contract()
    values = {
        "implementation_id": S1_JW_IMPLEMENTATION_ID,
        "source_s1jt_digest": jt.contract_digest,
        "source_s1jv_digest": jv.contract_digest,
        "adapter_roles": S1_JW_ROLES,
        "private_context_and_atomic_output_implemented": True,
        "six_adapter_bridges_implemented": True,
        "dual_geometry_digest_validation_implemented": True,
        "technical_kernel_tests_present": True,
        "profile_cases_executed": 0,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "research_field_steps_executed": 0,
        "decision": S1_JW_DECISION,
    }
    return DTS1S1JWImplementationReceipt(**values, receipt_digest=_digest(values))
