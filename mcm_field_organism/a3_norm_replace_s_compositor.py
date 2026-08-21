"""Private atomic A3 NORM REPLACE_S baseline compositor."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math

from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    advance_neutral_fast_shared_field,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError
from .transient_neuron_input import TransientNeuronInputSet
from .w7m_capacity_function_matrix import (
    W7MBaselineSpec,
    build_w7m_capacity_function_matrix_adapter,
)
from .w7n_capacity_function_baselines import (
    W7NCapacityFunctionBaselineError,
    W7NLocalBaselineResult,
    W7NLocalBaselineState,
    advance_w7n_local_baseline,
)


CONTRACT_ID = "a3-norm-replace-s/s1qi.v1"
COMPLETED = "COMPLETED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
STATUSES = (COMPLETED, NOT_COMPUTABLE)
FAILURE_CODES = (
    "QI_INPUT_TYPE_INVALID",
    "QI_FIELD_ROLE_INVALID",
    "QI_DISTRIBUTION_OR_INTERVAL_INVALID",
    "QI_CONFIGURATION_INVALID",
    "QI_NORM_PRESTATE_INVALID",
    "QI_GEOMETRY_OR_ORDER_MISMATCH",
    "QI_A1_ADVANCE_FAILED",
    "QI_A1_PROPOSAL_INVALID",
    "QI_NORM_ADVANCE_FAILED",
    "QI_NORM_OUTPUT_INVALID",
    "QI_S_REPLACEMENT_FAILED",
    "QI_H_OR_PROVENANCE_CHANGED",
    "QI_FIELD_TIME_CARDINALITY_FAILED",
    "QI_ATOMIC_OUTPUT_FAILED",
)
PHASES = (
    "api_intake",
    "common_identity_validation",
    "interval_discrimination",
    "a1_fast_proposal",
    "a1_proposal_validation",
    "norm_advance",
    "norm_output_validation",
    "replace_s_materialization",
    "final_field_validation",
    "atomic_receipt",
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _field_payload(field: SharedMCMField) -> dict[str, object]:
    return {
        "layer_digest": field.layer.digest(),
        "docks": [
            {
                "dock_id": dock.dock_id,
                "modality_id": dock.dock_map.modality_id,
                "receptor_geometry_id": dock.dock_map.receptor_geometry_id,
                "pairs": [list(pair) for pair in dock.dock_map.pairs],
            }
            for dock in field.docks
        ],
        "last_distribution_digest": (
            None
            if field.last_distribution is None
            else field.last_distribution.digest()
        ),
        "substrate_present": field.substrate is not None,
        "development_present": field.development is not None,
    }


def _field_digest(field: SharedMCMField) -> str:
    return _digest(_field_payload(field))


def _geometry_digest(field: SharedMCMField) -> str:
    return _digest(
        {
            "field_id": field.field_id,
            "geometry_id": field.geometry_id,
            "layer_id": field.layer.layer_id,
            "nodes": [
                {
                    "neuron_id": neuron.neuron_id,
                    "position": list(neuron.position),
                    "modality_id": neuron.modality_id,
                }
                for neuron in field.layer.neurons
            ],
            "sample_offsets": [list(item) for item in field.layer.sample_offsets],
            "periodic_axes": [
                item.canonical_payload() for item in field.layer.periodic_axes
            ],
        }
    )


def _state_digest(state: W7NLocalBaselineState) -> str:
    return _digest({"model_id": state.model_id, "latent": list(state.latent)})


def _spec_payload(spec: W7MBaselineSpec) -> dict[str, object]:
    return {
        "model_id": spec.model_id,
        "equation_id": spec.equation_id,
        "equation_contract": spec.equation_contract,
        "persistent_scalars_per_neuron": spec.persistent_scalars_per_neuron,
        "parameter_bindings": [list(item) for item in spec.parameter_bindings],
        "organism_runtime_allowed": spec.organism_runtime_allowed,
    }


def _config_digest(
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
    norm_spec: W7MBaselineSpec,
) -> str:
    return _digest(
        {
            "neutral_response_seconds": substrate_config.response_time_seconds,
            "fast_afterimage_seconds": afterimage_config.time_constant_seconds,
            "dissipation_per_second": (
                None
                if dissipation_config is None
                else dissipation_config.leak_rate_per_second
            ),
            "norm_spec": _spec_payload(norm_spec),
        }
    )


def _interval_payload(
    interval_input: MCMFieldStepTime | TransientNeuronInputSet,
) -> dict[str, object]:
    step = (
        interval_input
        if isinstance(interval_input, MCMFieldStepTime)
        else interval_input.step_time
    )
    payload: dict[str, object] = {
        "kind": "sync" if isinstance(interval_input, MCMFieldStepTime) else "transient",
        "step_time": {
            "clock_id": step.clock_id,
            "start_tick": step.start_tick,
            "end_tick": step.end_tick,
            "ticks_per_second": step.ticks_per_second,
        },
    }
    if isinstance(interval_input, TransientNeuronInputSet):
        payload["neuron_inputs"] = [
            {
                "neuron_id": item.neuron_id,
                "dock_id": item.dock_id,
                "carrier_id": item.carrier_id,
                "contacts": [
                    {
                        "snapshot_id": contact.snapshot_id,
                        "source_clock_id": contact.source_clock_id,
                        "source_window_start_tick": contact.source_window_start_tick,
                        "source_window_end_tick": contact.source_window_end_tick,
                        "read_clock_id": contact.organism_read_time.clock_id,
                        "read_start_tick": contact.organism_read_time.window_start_tick,
                        "read_end_tick": contact.organism_read_time.window_end_tick,
                        "value": contact.value,
                    }
                    for contact in item.contacts
                ],
            }
            for item in interval_input.neuron_inputs
        ]
    return payload


@dataclass(frozen=True, slots=True)
class A3NormReplaceSReceipt:
    contract_id: str
    interval_kind: str | None
    input_field_digest: str | None
    distribution_digest: str | None
    interval_digest: str | None
    configuration_digest: str | None
    geometry_digest: str | None
    norm_prestate_digest: str | None
    a1_proposal_digest: str | None
    norm_next_state_digest: str | None
    norm_output_digest: str | None
    global_scale_provenance_digest: str | None
    final_field_digest: str | None
    s_replacement_confirmed: bool
    h_identity_confirmed: bool
    field_time_advance_count: int
    phases: tuple[str, ...]
    status: str
    failure_codes: tuple[str, ...]
    receipt_digest: str = ""

    def __post_init__(self) -> None:
        if self.contract_id != CONTRACT_ID:
            raise ValueError("receipt contract identity mismatch")
        if self.status not in STATUSES:
            raise ValueError("receipt status is invalid")
        if tuple(self.phases) != PHASES[: len(self.phases)]:
            raise ValueError("receipt phases are not a canonical prefix")
        if any(code not in FAILURE_CODES for code in self.failure_codes):
            raise ValueError("receipt contains an unknown failure code")
        if tuple(sorted(self.failure_codes, key=FAILURE_CODES.index)) != tuple(
            self.failure_codes
        ):
            raise ValueError("receipt failure codes are not canonical")
        if self.status == COMPLETED and self.failure_codes:
            raise ValueError("completed receipt cannot contain failures")
        if self.status == NOT_COMPUTABLE and not self.failure_codes:
            raise ValueError("failed receipt requires one failure code")
        payload = self.canonical_payload()
        expected = _digest(payload)
        if self.receipt_digest and self.receipt_digest != expected:
            raise ValueError("receipt digest mismatch")
        object.__setattr__(self, "receipt_digest", expected)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "interval_kind": self.interval_kind,
            "input_field_digest": self.input_field_digest,
            "distribution_digest": self.distribution_digest,
            "interval_digest": self.interval_digest,
            "configuration_digest": self.configuration_digest,
            "geometry_digest": self.geometry_digest,
            "norm_prestate_digest": self.norm_prestate_digest,
            "a1_proposal_digest": self.a1_proposal_digest,
            "norm_next_state_digest": self.norm_next_state_digest,
            "norm_output_digest": self.norm_output_digest,
            "global_scale_provenance_digest": self.global_scale_provenance_digest,
            "final_field_digest": self.final_field_digest,
            "s_replacement_confirmed": self.s_replacement_confirmed,
            "h_identity_confirmed": self.h_identity_confirmed,
            "field_time_advance_count": self.field_time_advance_count,
            "phases": list(self.phases),
            "status": self.status,
            "failure_codes": list(self.failure_codes),
        }


@dataclass(frozen=True, slots=True)
class A3NormReplaceSResult:
    field: SharedMCMField | str
    next_norm_state: W7NLocalBaselineState | str
    receipt: A3NormReplaceSReceipt

    def __post_init__(self) -> None:
        if not isinstance(self.receipt, A3NormReplaceSReceipt):
            raise ValueError("result requires one compositor receipt")
        if self.receipt.status == COMPLETED:
            if not isinstance(self.field, SharedMCMField) or not isinstance(
                self.next_norm_state, W7NLocalBaselineState
            ):
                raise ValueError("completed result requires field and NORM state")
        elif self.field != NOT_COMPUTABLE or self.next_norm_state != NOT_COMPUTABLE:
            raise ValueError("failed result cannot publish partial state")


def _failure(
    code: str,
    phase_count: int,
    *,
    interval_kind: str | None = None,
    input_field_digest: str | None = None,
    distribution_digest: str | None = None,
    interval_digest: str | None = None,
    configuration_digest: str | None = None,
    geometry_digest: str | None = None,
    norm_prestate_digest: str | None = None,
    a1_proposal_digest: str | None = None,
    norm_next_state_digest: str | None = None,
    norm_output_digest: str | None = None,
    global_scale_provenance_digest: str | None = None,
) -> A3NormReplaceSResult:
    receipt = A3NormReplaceSReceipt(
        contract_id=CONTRACT_ID,
        interval_kind=interval_kind,
        input_field_digest=input_field_digest,
        distribution_digest=distribution_digest,
        interval_digest=interval_digest,
        configuration_digest=configuration_digest,
        geometry_digest=geometry_digest,
        norm_prestate_digest=norm_prestate_digest,
        a1_proposal_digest=a1_proposal_digest,
        norm_next_state_digest=norm_next_state_digest,
        norm_output_digest=norm_output_digest,
        global_scale_provenance_digest=global_scale_provenance_digest,
        final_field_digest=None,
        s_replacement_confirmed=False,
        h_identity_confirmed=False,
        field_time_advance_count=0,
        phases=PHASES[:phase_count],
        status=NOT_COMPUTABLE,
        failure_codes=(code,),
    )
    return A3NormReplaceSResult(NOT_COMPUTABLE, NOT_COMPUTABLE, receipt)


def _accepted_norm_spec(spec: W7MBaselineSpec) -> bool:
    adapter = build_w7m_capacity_function_matrix_adapter()
    accepted = next(item for item in adapter.baselines if item.model_id == "norm")
    return spec == accepted


def _interval_matches(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    interval_input: MCMFieldStepTime | TransientNeuronInputSet,
) -> bool:
    step = (
        interval_input
        if isinstance(interval_input, MCMFieldStepTime)
        else interval_input.step_time
    )
    current = distribution.field_time
    if (
        step.clock_id != current.clock_id
        or step.start_tick != current.window_start_tick
        or step.end_tick != current.window_end_tick
    ):
        return False
    if isinstance(interval_input, TransientNeuronInputSet):
        if distribution.contacts:
            return False
        actual = {item.neuron_id for item in interval_input.neuron_inputs}
        if actual != set(field.layer.docked_neuron_ids):
            return False
    return True


def _a1_proposal_valid(
    before: SharedMCMField,
    proposal: object,
    distribution: ReceptorDistribution,
) -> bool:
    if not isinstance(proposal, SharedMCMField):
        return False
    if proposal.substrate is not None or proposal.development is not None:
        return False
    if proposal.layer.tick != before.layer.tick + 1:
        return False
    if proposal.last_distribution != distribution:
        return False
    if proposal.docks != before.docks:
        return False
    before_nodes = tuple(
        (item.neuron_id, item.position, item.field_id, item.geometry_id)
        for item in before.layer.neurons
    )
    proposal_nodes = tuple(
        (item.neuron_id, item.position, item.field_id, item.geometry_id)
        for item in proposal.layer.neurons
    )
    return before_nodes == proposal_nodes


def _norm_result_valid(result: object, count: int) -> bool:
    if not isinstance(result, W7NLocalBaselineResult):
        return False
    if result.state.model_id != "norm":
        return False
    if len(result.state.latent) != count or len(result.output) != count:
        return False
    return all(math.isfinite(value) for value in (*result.state.latent, *result.output))


def _materialize_replace_s(
    proposal: SharedMCMField,
    output: tuple[float, ...],
) -> SharedMCMField:
    neurons = tuple(
        replace(neuron, activation=value)
        for neuron, value in zip(proposal.layer.neurons, output, strict=True)
    )
    return SharedMCMField(
        replace(proposal.layer, neurons=neurons),
        proposal.docks,
        proposal.last_distribution,
    )


def _final_identity_valid(
    proposal: SharedMCMField,
    final: object,
    output: tuple[float, ...],
) -> bool:
    if not isinstance(final, SharedMCMField):
        return False
    if final.substrate is not None or final.development is not None:
        return False
    if final.docks != proposal.docks or final.last_distribution != proposal.last_distribution:
        return False
    if final.layer.layer_id != proposal.layer.layer_id:
        return False
    if final.layer.sample_offsets != proposal.layer.sample_offsets:
        return False
    if final.layer.periodic_axes != proposal.layer.periodic_axes:
        return False
    if len(final.layer.neurons) != len(proposal.layer.neurons):
        return False
    for proposed, completed, expected_s in zip(
        proposal.layer.neurons, final.layer.neurons, output, strict=True
    ):
        if completed.activation != expected_s:
            return False
        if replace(completed, activation=proposed.activation) != proposed:
            return False
    return True


def _field_time_advance_count(before: SharedMCMField, final: SharedMCMField) -> int:
    return final.layer.tick - before.layer.tick


def _atomic_output_valid(
    final: SharedMCMField,
    next_state: W7NLocalBaselineState,
    receipt: A3NormReplaceSReceipt,
) -> bool:
    return (
        receipt.status == COMPLETED
        and receipt.final_field_digest == _field_digest(final)
        and receipt.norm_next_state_digest == _state_digest(next_state)
        and receipt.s_replacement_confirmed
        and receipt.h_identity_confirmed
        and receipt.field_time_advance_count == 1
    )


def advance_a3_norm_replace_s(
    field,
    distribution,
    interval_input,
    neutral_substrate_config,
    fast_afterimage_config,
    norm_spec,
    norm_prestate,
    dissipation_config=None,
) -> A3NormReplaceSResult:
    """Advance one private A3 NORM baseline interval atomically."""

    required_types_valid = (
        isinstance(field, SharedMCMField)
        and isinstance(distribution, ReceptorDistribution)
        and isinstance(interval_input, (MCMFieldStepTime, TransientNeuronInputSet))
        and isinstance(neutral_substrate_config, NeutralLocalFieldSubstrateConfig)
        and isinstance(fast_afterimage_config, NeutralFastAfterimageConfig)
        and isinstance(norm_spec, W7MBaselineSpec)
        and isinstance(norm_prestate, W7NLocalBaselineState)
        and (
            dissipation_config is None
            or isinstance(dissipation_config, NeutralFieldDissipationConfig)
        )
    )
    if not required_types_valid:
        return _failure("QI_INPUT_TYPE_INVALID", 1)

    interval_kind = (
        "sync" if isinstance(interval_input, MCMFieldStepTime) else "transient"
    )
    input_field_digest = _field_digest(field)
    distribution_digest = distribution.digest()
    interval_digest = _digest(_interval_payload(interval_input))
    geometry_digest = _geometry_digest(field)
    norm_prestate_digest = _state_digest(norm_prestate)
    configuration_digest = _config_digest(
        neutral_substrate_config,
        fast_afterimage_config,
        dissipation_config,
        norm_spec,
    )
    common = {
        "interval_kind": interval_kind,
        "input_field_digest": input_field_digest,
        "distribution_digest": distribution_digest,
        "interval_digest": interval_digest,
        "configuration_digest": configuration_digest,
        "geometry_digest": geometry_digest,
        "norm_prestate_digest": norm_prestate_digest,
    }

    if field.substrate is not None or field.development is not None:
        return _failure("QI_FIELD_ROLE_INVALID", 2, **common)
    if not _accepted_norm_spec(norm_spec):
        return _failure("QI_CONFIGURATION_INVALID", 2, **common)
    if norm_prestate.model_id != "norm":
        return _failure("QI_NORM_PRESTATE_INVALID", 2, **common)
    if len(norm_prestate.latent) != len(field.layer.neurons):
        return _failure("QI_GEOMETRY_OR_ORDER_MISMATCH", 2, **common)
    if not _interval_matches(field, distribution, interval_input):
        return _failure("QI_DISTRIBUTION_OR_INTERVAL_INVALID", 3, **common)

    try:
        if isinstance(interval_input, MCMFieldStepTime):
            proposal = advance_neutral_fast_shared_field(
                field,
                distribution,
                interval_input,
                neutral_substrate_config,
                fast_afterimage_config,
                dissipation_config,
            )
        else:
            proposal = advance_neutral_fast_shared_field_transient(
                field,
                distribution,
                interval_input,
                neutral_substrate_config,
                fast_afterimage_config,
                dissipation_config,
            )
    except NeutralLocalFieldSubstrateError:
        return _failure("QI_A1_ADVANCE_FAILED", 4, **common)
    if not _a1_proposal_valid(field, proposal, distribution):
        return _failure("QI_A1_PROPOSAL_INVALID", 5, **common)
    a1_proposal_digest = _field_digest(proposal)

    evidence = tuple(neuron.activation for neuron in proposal.layer.neurons)
    duration_seconds = (
        interval_input.elapsed_seconds
        if isinstance(interval_input, MCMFieldStepTime)
        else interval_input.step_time.elapsed_seconds
    )
    with_proposal = {**common, "a1_proposal_digest": a1_proposal_digest}
    try:
        norm_result = advance_w7n_local_baseline(
            norm_spec,
            norm_prestate,
            evidence,
            duration_seconds,
        )
    except W7NCapacityFunctionBaselineError:
        return _failure("QI_NORM_ADVANCE_FAILED", 6, **with_proposal)
    if not _norm_result_valid(norm_result, len(proposal.layer.neurons)):
        return _failure("QI_NORM_OUTPUT_INVALID", 7, **with_proposal)

    norm_next_state_digest = _state_digest(norm_result.state)
    norm_output_digest = _digest({"signed_output": list(norm_result.output)})
    scale_digest = _digest(
        {
            "configuration_digest": configuration_digest,
            "complete_state_digest": norm_next_state_digest,
            "signed_output_digest": norm_output_digest,
            "location_count": len(norm_result.output),
        }
    )
    with_norm = {
        **with_proposal,
        "norm_next_state_digest": norm_next_state_digest,
        "norm_output_digest": norm_output_digest,
        "global_scale_provenance_digest": scale_digest,
    }
    try:
        final = _materialize_replace_s(proposal, norm_result.output)
    except (SharedMCMFieldError, TypeError, ValueError):
        return _failure("QI_S_REPLACEMENT_FAILED", 8, **with_norm)
    if not _final_identity_valid(proposal, final, norm_result.output):
        return _failure("QI_H_OR_PROVENANCE_CHANGED", 9, **with_norm)

    advance_count = _field_time_advance_count(field, final)
    if advance_count != 1:
        return _failure("QI_FIELD_TIME_CARDINALITY_FAILED", 9, **with_norm)

    receipt = A3NormReplaceSReceipt(
        contract_id=CONTRACT_ID,
        interval_kind=interval_kind,
        input_field_digest=input_field_digest,
        distribution_digest=distribution_digest,
        interval_digest=interval_digest,
        configuration_digest=configuration_digest,
        geometry_digest=geometry_digest,
        norm_prestate_digest=norm_prestate_digest,
        a1_proposal_digest=a1_proposal_digest,
        norm_next_state_digest=norm_next_state_digest,
        norm_output_digest=norm_output_digest,
        global_scale_provenance_digest=scale_digest,
        final_field_digest=_field_digest(final),
        s_replacement_confirmed=True,
        h_identity_confirmed=True,
        field_time_advance_count=advance_count,
        phases=PHASES,
        status=COMPLETED,
        failure_codes=(),
    )
    if not _atomic_output_valid(final, norm_result.state, receipt):
        return _failure("QI_ATOMIC_OUTPUT_FAILED", 10, **with_norm)
    return A3NormReplaceSResult(final, norm_result.state, receipt)
