"""Atomic role dispatch for accepted four-node model inputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
import functools
import hashlib
import json
import math

from .a3_norm_replace_s_compositor import advance_a3_norm_replace_s
from .dynamic_substrate_dts1_backreaction import (
    DTS1BackreactionEdgeRate,
    DTS1BackreactionResult,
)
from .dynamic_substrate_dts1_coupled_step import (
    _advance_active_field,
    advance_dts1_coupled_fast_shared_field,
)
from .dynamic_substrate_dts1_step import DTS1StepRates
from .dynamic_substrate_s1jt_finite_adapter_payload_contract import (
    S1_JT_B6_SPEC_PAYLOAD,
)
from .field_step_time import MCMFieldStepTime
from .four_node_fresh_factory import (
    FourNodeFixedAdapterState,
    FourNodeIntegratorEntry,
    FourNodeIntegratorState,
    FourNodeM4FreshState,
    FourNodeSubstrateFreshState,
)
from .four_node_model_input_assembly import FourNodeModelInputAssembly
from .m1_parallel_leak_replace_s_compositor import (
    M1ParallelLeakBankState,
    advance_m1_parallel_leak_replace_s,
    build_registered_m1_parallel_leak_configuration,
)
from .m2_bounded_buffer_replace_s_compositor import (
    M2BoundedBufferState,
    advance_m2_bounded_buffer_replace_s,
    build_registered_m2_configuration,
)
from .m5_direct_replace_s_compositor import advance_m5_direct_replace_s
from .mcm_f3_baseline_coupling import (
    compute_mcm_f3_linear_coupled_baseline,
    compute_mcm_f3_local_leaky_baseline,
)
from .mcm_f3_coupling import compute_mcm_f3_coupling
from .mcm_f3_runtime import (
    advance_mcm_f3_shared_field,
    advance_mcm_f3_shared_field_transient,
)
from .mcm_neuron_layer import MCMNeuronDrive, MCMNeuronOutput
from .mcm_substrate_state import mcm_substrate_edge_inventory_digest
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    _generator_and_boundary,
    advance_neutral_fast_shared_field,
    advance_neutral_fast_shared_field_transient,
    advance_neutral_shared_field,
    advance_neutral_shared_field_transient,
)
from .receptor_distributor import ReceptorDistribution
from .s2_reference_baselines import (
    S2ReferenceModelConfig,
    S2ReferenceState,
    advance_s2_reference_model,
)
from .shared_mcm_field import SharedMCMField
from .transient_neuron_input import TransientNeuronInputSet
from .w7m_capacity_function_matrix import (
    W7MBaselineSpec,
    build_w7m_capacity_function_matrix_adapter,
)
from .w7n_capacity_function_baselines import (
    W7NLocalBaselineState,
    compute_w7n_coupling_baseline,
)


class FourNodeModelInvocationError(ValueError):
    """Raised only for an invalid outer API call, before atomic dispatch."""


COMPLETED = "COMPLETED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
SYNC = "SYNC"
TRANSIENT = "TRANSIENT"
_SUBSTRATE_ROLES = frozenset(
    {"A2_B3_LOCAL_LEAKY", "A2_B4_LINEAR_COUPLED", "A2_B5_F3_FULL", "A2_B6_CONST_V"}
)
_SYNC_ONLY = frozenset({"A2_B1_FIXED_ADAPTER", "A2_B2_INTEGRATOR", "M4_DTS1_T1"})
_COMMON_SUBSTRATE = NeutralLocalFieldSubstrateConfig(1.0)
_COMMON_AFTERIMAGE = NeutralFastAfterimageConfig(0.5)
_COMMON_DISSIPATION = NeutralFieldDissipationConfig(0.0)
_B6_VALUES = dict(S1_JT_B6_SPEC_PAYLOAD)
_B6_VALUES.pop("schema_id")
_B6_SPEC = W7MBaselineSpec(**_B6_VALUES)


def _canonical(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise FourNodeModelInvocationError("non-finite canonical value")
        return 0.0 if value == 0.0 else value
    if is_dataclass(value) and not isinstance(value, type):
        return _canonical(asdict(value))
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _canonical(value[key]) for key in sorted(value)}
    raise FourNodeModelInvocationError("canonical payload contains an object")


def _digest(value: object) -> str:
    encoded = json.dumps(
        _canonical(value), sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _field_digest(field: SharedMCMField) -> str:
    return _digest(
        {
            "layer_digest": field.layer.digest(),
            "docks": tuple(
                (dock.dock_id, dock.dock_map.modality_id, dock.dock_map.receptor_geometry_id, dock.dock_map.pairs)
                for dock in field.docks
            ),
            "last_distribution_digest": (
                None if field.last_distribution is None else field.last_distribution.digest()
            ),
            "substrate_digest": None if field.substrate is None else field.substrate.digest(),
            "development_digest": None if field.development is None else field.development.digest(),
        }
    )


def _private_digest(value: object | None) -> str | None:
    return None if value is None else _digest(value)


@dataclass(frozen=True, slots=True)
class FourNodeModelCarry:
    model_role: str
    field: SharedMCMField
    private_state_or_none: object | None
    configuration_binding_or_none: str | None
    registered_edge_inventory_digest_or_none: str | None
    native_edge_inventory_digest_or_none: str | None
    registered_geometry_digest_or_none: str | None
    native_geometry_digest_or_none: str | None
    carry_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeModelStepResult:
    status: str
    model_role: str
    interval_kind: str
    invocation_digest: str
    input_field_digest: str
    private_prestate_digest_or_none: str | None
    configuration_digest: str
    output_field_or_none: SharedMCMField | None
    next_private_state_or_none: object | None
    next_carry_or_none: FourNodeModelCarry | None
    output_field_digest_or_none: str | None
    next_private_state_digest_or_none: str | None
    native_receipt_or_diagnostics_digest_or_none: str | None
    field_time_advance_count: int
    failure_codes: tuple[str, ...]
    result_digest: str


def _source(value: FourNodeModelInputAssembly | FourNodeModelCarry):
    if isinstance(value, FourNodeModelInputAssembly):
        return (
            value.model_role,
            value.model_input_field,
            value.native_private_state_or_none,
            value.configuration_binding_or_none,
            value.registered_edge_inventory_digest_or_none,
            value.native_edge_inventory_digest_or_none,
            value.registered_geometry_digest_or_none,
            value.native_geometry_digest_or_none,
            value.assembly_digest,
        )
    if isinstance(value, FourNodeModelCarry):
        return (
            value.model_role, value.field, value.private_state_or_none,
            value.configuration_binding_or_none,
            value.registered_edge_inventory_digest_or_none,
            value.native_edge_inventory_digest_or_none,
            value.registered_geometry_digest_or_none,
            value.native_geometry_digest_or_none, value.carry_digest,
        )
    raise FourNodeModelInvocationError("MODEL_INVOCATION_SOURCE_INVALID")


def _interval(value: object) -> tuple[str, MCMFieldStepTime]:
    if isinstance(value, MCMFieldStepTime):
        return SYNC, value
    if isinstance(value, TransientNeuronInputSet):
        return TRANSIENT, value.step_time
    raise FourNodeModelInvocationError("MODEL_INVOCATION_INTERVAL_INVALID")


def _configuration_digest(role: str, binding: str | None, refinement: int | None) -> str:
    return _digest(
        {
            "role": role,
            "binding": binding,
            "neutral_response_seconds": 1.0,
            "fast_afterimage_seconds": 0.5,
            "dissipation_per_second": 0.0,
            "refinement_or_none": refinement if role in _SUBSTRATE_ROLES else None,
        }
    )


def _fixed_adapter(field: SharedMCMField, state: FourNodeFixedAdapterState):
    native_digest = mcm_substrate_edge_inventory_digest(field.layer)
    return DTS1BackreactionResult(
        state.backreaction_enabled,
        state.base_rate_per_second,
        tuple(
            DTS1BackreactionEdgeRate(item.first_node_id, item.second_node_id, item.rate_per_second)
            for item in state.edge_rates
        ),
        native_digest,
    )


def _advance_b2(field, distribution, step, state: FourNodeIntegratorState):
    order = tuple(item.neuron_id for item in field.layer.neurons)
    if tuple(item.node_id for item in state.entries) != order:
        raise ValueError("B2 node order differs")
    prestate = S2ReferenceState(
        tuple(item.activation for item in field.layer.neurons),
        tuple(item.afterimage for item in field.layer.neurons),
        tuple(item.value for item in state.entries),
    )
    generator, boundary = _generator_and_boundary(field, distribution, _COMMON_SUBSTRATE)
    advanced = advance_s2_reference_model(
        "b2", prestate, generator, boundary, step.elapsed_seconds, S2ReferenceModelConfig()
    )
    outputs = {
        node: MCMNeuronOutput(advanced.state.activation[index], advanced.state.afterimage[index])
        for index, node in enumerate(order)
    }
    def transition(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]
    next_field = field.advance(distribution, transition, step_time=step)
    next_state = FourNodeIntegratorState(
        tuple(FourNodeIntegratorEntry(node, advanced.state.development[index]) for index, node in enumerate(order))
    )
    return next_field, next_state, {"partition_error": advanced.partition_error}


def _spec(model_id: str) -> W7MBaselineSpec:
    return next(item for item in build_w7m_capacity_function_matrix_adapter().baselines if item.model_id == model_id)


def _dispatch(role, field, private, distribution, interval_input, refinement):
    transient = isinstance(interval_input, TransientNeuronInputSet)
    step = interval_input.step_time if transient else interval_input
    if role == "A0_CURRENT_CONTACT":
        result = (
            advance_neutral_shared_field_transient(field, distribution, interval_input, _COMMON_SUBSTRATE)
            if transient else advance_neutral_shared_field(field, distribution, step, _COMMON_SUBSTRATE)
        )
        return result, None, {"kernel": "neutral-current-contact"}
    if role == "A1_FAST_SH":
        result = (
            advance_neutral_fast_shared_field_transient(field, distribution, interval_input, _COMMON_SUBSTRATE, _COMMON_AFTERIMAGE, _COMMON_DISSIPATION)
            if transient else advance_neutral_fast_shared_field(field, distribution, step, _COMMON_SUBSTRATE, _COMMON_AFTERIMAGE, _COMMON_DISSIPATION)
        )
        return result, None, {"kernel": "neutral-fast-sh"}
    if role == "A2_B1_FIXED_ADAPTER":
        if not isinstance(private, FourNodeFixedAdapterState): raise ValueError("B1 state invalid")
        adapter = _fixed_adapter(field, private)
        result = _advance_active_field(field, distribution, step, _COMMON_SUBSTRATE, _COMMON_AFTERIMAGE, _COMMON_DISSIPATION, adapter, step.elapsed_seconds)
        return result, private, {"adapter": asdict(adapter)}
    if role == "A2_B2_INTEGRATOR":
        if not isinstance(private, FourNodeIntegratorState): raise ValueError("B2 state invalid")
        return _advance_b2(field, distribution, step, private)
    if role in _SUBSTRATE_ROLES:
        calculators = {
            "A2_B3_LOCAL_LEAKY": compute_mcm_f3_local_leaky_baseline,
            "A2_B4_LINEAR_COUPLED": compute_mcm_f3_linear_coupled_baseline,
            "A2_B5_F3_FULL": compute_mcm_f3_coupling,
            "A2_B6_CONST_V": functools.partial(compute_w7n_coupling_baseline, _B6_SPEC),
        }
        function = advance_mcm_f3_shared_field_transient if transient else advance_mcm_f3_shared_field
        result = function(field, distribution, interval_input, _COMMON_SUBSTRATE, _COMMON_AFTERIMAGE, _COMMON_DISSIPATION, refinement=refinement, _coupling_calculator=calculators[role])
        if not isinstance(private, FourNodeSubstrateFreshState): raise ValueError("F3 wrapper invalid")
        wrapper = FourNodeSubstrateFreshState(result.field.substrate, private.registered_edge_inventory_digest, private.native_edge_inventory_digest, private.frozen_spec_digest_or_none)
        return result.field, wrapper, asdict(result.diagnostics)
    if role == "A3_NORM":
        native = advance_a3_norm_replace_s(field, distribution, interval_input, _COMMON_SUBSTRATE, _COMMON_AFTERIMAGE, _spec("norm"), private, _COMMON_DISSIPATION)
        if native.receipt.status != "COMPLETED": raise ValueError(native.receipt.failure_codes[0])
        return native.field, native.next_norm_state, native.receipt.canonical_payload()
    if role == "M1_PARALLEL_LEAK":
        native = advance_m1_parallel_leak_replace_s(field, distribution, interval_input, _COMMON_SUBSTRATE, _COMMON_AFTERIMAGE, build_registered_m1_parallel_leak_configuration(), private, _COMMON_DISSIPATION)
        if native.receipt.status != "COMPLETED": raise ValueError(native.receipt.failure_codes[0])
        return native.field, native.next_m1_state, native.receipt.canonical_payload()
    if role in {"M2_DELAY", "M2_REPLAY"}:
        mode = "DELAY" if role == "M2_DELAY" else "REPLAY"
        native = advance_m2_bounded_buffer_replace_s(field, distribution, interval_input, _COMMON_SUBSTRATE, _COMMON_AFTERIMAGE, build_registered_m2_configuration(mode), private, _COMMON_DISSIPATION)
        if native.receipt.status != "COMPLETED": raise ValueError(native.receipt.failure_codes[0])
        return native.field, native.next_m2_state, native.receipt.canonical_payload()
    if role == "M4_DTS1_T1":
        if not isinstance(private, FourNodeM4FreshState): raise ValueError("M4 state invalid")
        rates = DTS1StepRates(binding_rate=private.rates.binding_rate, turnover_rate=private.rates.turnover_rate, recovery_rate=private.rates.recovery_rate)
        native = advance_dts1_coupled_fast_shared_field(field, private.anatomy, distribution, step, _COMMON_SUBSTRATE, _COMMON_AFTERIMAGE, rates, _COMMON_DISSIPATION, backreaction_enabled=True)
        wrapper = FourNodeM4FreshState(native.anatomy, private.rates, private.registered_edge_inventory_digest, native.anatomy.edge_inventory_digest, None)
        return native.field, wrapper, asdict(native)
    if role == "M5_DIRECT":
        native = advance_m5_direct_replace_s(field, distribution, interval_input, _COMMON_SUBSTRATE, _COMMON_AFTERIMAGE, _spec("leak"), private, _COMMON_DISSIPATION)
        if native.receipt.status != "COMPLETED": raise ValueError(native.receipt.failure_codes[0])
        return native.field, native.next_m5_state, native.receipt.canonical_payload()
    raise ValueError("model role invalid")


def _result_payload(result: FourNodeModelStepResult) -> dict[str, object]:
    return {item.name: getattr(result, item.name) for item in fields(result) if item.name not in {"output_field_or_none", "next_private_state_or_none", "next_carry_or_none", "result_digest"}}


def invoke_four_node_model(source, distribution, interval_input, *, refinement=None) -> FourNodeModelStepResult:
    role, field, private, binding, registered_edge, native_edge, registered_geometry, native_geometry, source_digest = _source(source)
    if not isinstance(distribution, ReceptorDistribution):
        raise FourNodeModelInvocationError("MODEL_INVOCATION_DISTRIBUTION_INVALID")
    interval_kind, step = _interval(interval_input)
    if interval_kind == TRANSIENT and role in _SYNC_ONLY:
        failure = "MODEL_INVOCATION_TRANSIENT_NOT_CONNECTABLE"
    elif role in _SUBSTRATE_ROLES and (isinstance(refinement, bool) or not isinstance(refinement, int) or refinement < 1):
        failure = "MODEL_INVOCATION_REFINEMENT_INVALID"
    elif role not in _SUBSTRATE_ROLES and refinement is not None:
        failure = "MODEL_INVOCATION_REFINEMENT_FORBIDDEN"
    else:
        failure = None
    input_digest = _field_digest(field)
    prestate_digest = _private_digest(private)
    config_digest = _configuration_digest(role, binding, refinement)
    invocation_digest = _digest({"source": source_digest, "distribution": distribution.digest(), "interval": interval_input, "configuration": config_digest})
    if failure is None:
        try:
            output, next_private, diagnostics = _dispatch(role, field, private, distribution, interval_input, refinement)
            output_digest = _field_digest(output)
            next_digest = _private_digest(next_private)
            diagnostics_digest = _digest(diagnostics)
            carry_values = {"role": role, "field": output_digest, "private": next_digest, "configuration": binding, "registered_edge": registered_edge, "native_edge": native_edge, "registered_geometry": registered_geometry, "native_geometry": native_geometry}
            carry = FourNodeModelCarry(role, output, next_private, binding, registered_edge, native_edge, registered_geometry, native_geometry, _digest(carry_values))
            result = FourNodeModelStepResult(COMPLETED, role, interval_kind, invocation_digest, input_digest, prestate_digest, config_digest, output, next_private, carry, output_digest, next_digest, diagnostics_digest, 1, (), "")
        except Exception as exc:
            failure = f"MODEL_KERNEL_NOT_COMPUTABLE:{type(exc).__name__}:{exc}"
    if failure is not None:
        result = FourNodeModelStepResult(NOT_COMPUTABLE, role, interval_kind, invocation_digest, input_digest, prestate_digest, config_digest, None, None, None, None, None, None, 0, (failure,), "")
    return FourNodeModelStepResult(*(
        getattr(result, item.name) if item.name != "result_digest" else _digest(_result_payload(result))
        for item in fields(result)
    ))
