"""Private atomic M5 direct local-state REPLACE_S baseline compositor."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .field_step_time import MCMFieldStepTime
from .local_state_replace_s_compositor_core import (
    advance_fast_proposal as _advance_fast_proposal,
    canonical_digest as _digest,
    field_digest as _field_digest,
    field_time_advance_count as _field_time_advance_count,
    fast_proposal_valid as _a1_proposal_valid,
    final_identity_valid as _final_identity_valid,
    geometry_digest as _geometry_digest,
    interval_matches as _interval_matches,
    interval_payload as _interval_payload,
    materialize_replace_s as _materialize_replace_s,
)
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


CONTRACT_ID = "m5-direct-replace-s/s1qm.v1"
COMPLETED = "COMPLETED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
STATUSES = (COMPLETED, NOT_COMPUTABLE)
FAILURE_CODES = (
    "QM_INPUT_TYPE_INVALID",
    "QM_FIELD_ROLE_INVALID",
    "QM_DISTRIBUTION_OR_INTERVAL_INVALID",
    "QM_CONFIGURATION_INVALID",
    "QM_M5_PRESTATE_INVALID",
    "QM_GEOMETRY_OR_ORDER_MISMATCH",
    "QM_A1_ADVANCE_FAILED",
    "QM_A1_PROPOSAL_INVALID",
    "QM_LEAK_ADVANCE_FAILED",
    "QM_DIRECT_OUTPUT_INVALID",
    "QM_S_REPLACEMENT_FAILED",
    "QM_H_OR_PROVENANCE_CHANGED",
    "QM_FIELD_TIME_CARDINALITY_FAILED",
    "QM_ATOMIC_OUTPUT_FAILED",
)
PHASES = (
    "api_intake",
    "common_identity_validation",
    "interval_discrimination",
    "a1_fast_proposal",
    "a1_proposal_validation",
    "m5_leak_advance",
    "direct_output_validation",
    "replace_s_materialization",
    "final_field_validation",
    "atomic_receipt",
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
    leak_spec: W7MBaselineSpec,
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
            "leak_spec": _spec_payload(leak_spec),
        }
    )


@dataclass(frozen=True, slots=True)
class M5DirectReplaceSReceipt:
    contract_id: str
    interval_kind: str | None
    input_field_digest: str | None
    distribution_digest: str | None
    interval_digest: str | None
    configuration_digest: str | None
    geometry_digest: str | None
    m5_prestate_digest: str | None
    a1_proposal_digest: str | None
    m5_next_state_digest: str | None
    direct_output_digest: str | None
    state_output_identity_confirmed: bool
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
        expected = _digest(self.canonical_payload())
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
            "m5_prestate_digest": self.m5_prestate_digest,
            "a1_proposal_digest": self.a1_proposal_digest,
            "m5_next_state_digest": self.m5_next_state_digest,
            "direct_output_digest": self.direct_output_digest,
            "state_output_identity_confirmed": self.state_output_identity_confirmed,
            "final_field_digest": self.final_field_digest,
            "s_replacement_confirmed": self.s_replacement_confirmed,
            "h_identity_confirmed": self.h_identity_confirmed,
            "field_time_advance_count": self.field_time_advance_count,
            "phases": list(self.phases),
            "status": self.status,
            "failure_codes": list(self.failure_codes),
        }


@dataclass(frozen=True, slots=True)
class M5DirectReplaceSResult:
    field: SharedMCMField | str
    next_m5_state: W7NLocalBaselineState | str
    receipt: M5DirectReplaceSReceipt

    def __post_init__(self) -> None:
        if not isinstance(self.receipt, M5DirectReplaceSReceipt):
            raise ValueError("result requires one M5 receipt")
        if self.receipt.status == COMPLETED:
            if not isinstance(self.field, SharedMCMField) or not isinstance(
                self.next_m5_state, W7NLocalBaselineState
            ):
                raise ValueError("completed result requires field and M5 state")
        elif self.field != NOT_COMPUTABLE or self.next_m5_state != NOT_COMPUTABLE:
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
    m5_prestate_digest: str | None = None,
    a1_proposal_digest: str | None = None,
    m5_next_state_digest: str | None = None,
    direct_output_digest: str | None = None,
) -> M5DirectReplaceSResult:
    receipt = M5DirectReplaceSReceipt(
        contract_id=CONTRACT_ID,
        interval_kind=interval_kind,
        input_field_digest=input_field_digest,
        distribution_digest=distribution_digest,
        interval_digest=interval_digest,
        configuration_digest=configuration_digest,
        geometry_digest=geometry_digest,
        m5_prestate_digest=m5_prestate_digest,
        a1_proposal_digest=a1_proposal_digest,
        m5_next_state_digest=m5_next_state_digest,
        direct_output_digest=direct_output_digest,
        state_output_identity_confirmed=False,
        final_field_digest=None,
        s_replacement_confirmed=False,
        h_identity_confirmed=False,
        field_time_advance_count=0,
        phases=PHASES[:phase_count],
        status=NOT_COMPUTABLE,
        failure_codes=(code,),
    )
    return M5DirectReplaceSResult(NOT_COMPUTABLE, NOT_COMPUTABLE, receipt)


def _accepted_leak_spec(spec: W7MBaselineSpec) -> bool:
    adapter = build_w7m_capacity_function_matrix_adapter()
    accepted = next(item for item in adapter.baselines if item.model_id == "leak")
    return spec == accepted


def _direct_result_valid(result: object, count: int) -> bool:
    if not isinstance(result, W7NLocalBaselineResult):
        return False
    if result.state.model_id != "leak":
        return False
    if len(result.state.latent) != count or len(result.output) != count:
        return False
    if not all(math.isfinite(value) for value in (*result.state.latent, *result.output)):
        return False
    return result.output == result.state.latent


def _atomic_output_valid(
    final: SharedMCMField,
    next_state: W7NLocalBaselineState,
    receipt: M5DirectReplaceSReceipt,
) -> bool:
    return (
        receipt.status == COMPLETED
        and receipt.final_field_digest == _field_digest(final)
        and receipt.m5_next_state_digest == _state_digest(next_state)
        and receipt.state_output_identity_confirmed
        and receipt.s_replacement_confirmed
        and receipt.h_identity_confirmed
        and receipt.field_time_advance_count == 1
    )


def advance_m5_direct_replace_s(
    field,
    distribution,
    interval_input,
    neutral_substrate_config,
    fast_afterimage_config,
    leak_spec,
    m5_prestate,
    dissipation_config=None,
) -> M5DirectReplaceSResult:
    """Advance one private M5 direct local-state baseline interval atomically."""

    required_types_valid = (
        isinstance(field, SharedMCMField)
        and isinstance(distribution, ReceptorDistribution)
        and isinstance(interval_input, (MCMFieldStepTime, TransientNeuronInputSet))
        and isinstance(neutral_substrate_config, NeutralLocalFieldSubstrateConfig)
        and isinstance(fast_afterimage_config, NeutralFastAfterimageConfig)
        and isinstance(leak_spec, W7MBaselineSpec)
        and isinstance(m5_prestate, W7NLocalBaselineState)
        and (
            dissipation_config is None
            or isinstance(dissipation_config, NeutralFieldDissipationConfig)
        )
    )
    if not required_types_valid:
        return _failure("QM_INPUT_TYPE_INVALID", 1)

    interval_kind = (
        "sync" if isinstance(interval_input, MCMFieldStepTime) else "transient"
    )
    input_field_digest = _field_digest(field)
    distribution_digest = distribution.digest()
    interval_digest = _digest(_interval_payload(interval_input))
    configuration_digest = _config_digest(
        neutral_substrate_config,
        fast_afterimage_config,
        dissipation_config,
        leak_spec,
    )
    geometry_digest = _geometry_digest(field)
    m5_prestate_digest = _state_digest(m5_prestate)
    common = {
        "interval_kind": interval_kind,
        "input_field_digest": input_field_digest,
        "distribution_digest": distribution_digest,
        "interval_digest": interval_digest,
        "configuration_digest": configuration_digest,
        "geometry_digest": geometry_digest,
        "m5_prestate_digest": m5_prestate_digest,
    }

    if field.substrate is not None or field.development is not None:
        return _failure("QM_FIELD_ROLE_INVALID", 2, **common)
    if not _accepted_leak_spec(leak_spec):
        return _failure("QM_CONFIGURATION_INVALID", 2, **common)
    if m5_prestate.model_id != "leak":
        return _failure("QM_M5_PRESTATE_INVALID", 2, **common)
    if len(m5_prestate.latent) != len(field.layer.neurons):
        return _failure("QM_GEOMETRY_OR_ORDER_MISMATCH", 2, **common)
    if not _interval_matches(field, distribution, interval_input):
        return _failure("QM_DISTRIBUTION_OR_INTERVAL_INVALID", 3, **common)

    try:
        proposal = _advance_fast_proposal(
            field,
            distribution,
            interval_input,
            neutral_substrate_config,
            fast_afterimage_config,
            dissipation_config,
            advance_neutral_fast_shared_field,
            advance_neutral_fast_shared_field_transient,
        )
    except NeutralLocalFieldSubstrateError:
        return _failure("QM_A1_ADVANCE_FAILED", 4, **common)
    if not _a1_proposal_valid(field, proposal, distribution):
        return _failure("QM_A1_PROPOSAL_INVALID", 5, **common)
    a1_proposal_digest = _field_digest(proposal)

    evidence = tuple(neuron.activation for neuron in proposal.layer.neurons)
    duration_seconds = (
        interval_input.elapsed_seconds
        if isinstance(interval_input, MCMFieldStepTime)
        else interval_input.step_time.elapsed_seconds
    )
    with_proposal = {**common, "a1_proposal_digest": a1_proposal_digest}
    try:
        direct_result = advance_w7n_local_baseline(
            leak_spec,
            m5_prestate,
            evidence,
            duration_seconds,
        )
    except W7NCapacityFunctionBaselineError:
        return _failure("QM_LEAK_ADVANCE_FAILED", 6, **with_proposal)
    if not _direct_result_valid(direct_result, len(proposal.layer.neurons)):
        return _failure("QM_DIRECT_OUTPUT_INVALID", 7, **with_proposal)

    m5_next_state_digest = _state_digest(direct_result.state)
    direct_output_digest = _digest({"signed_output": list(direct_result.output)})
    with_direct = {
        **with_proposal,
        "m5_next_state_digest": m5_next_state_digest,
        "direct_output_digest": direct_output_digest,
    }
    try:
        final = _materialize_replace_s(proposal, direct_result.output)
    except (SharedMCMFieldError, TypeError, ValueError):
        return _failure("QM_S_REPLACEMENT_FAILED", 8, **with_direct)
    if not _final_identity_valid(proposal, final, direct_result.output):
        return _failure("QM_H_OR_PROVENANCE_CHANGED", 9, **with_direct)

    advance_count = _field_time_advance_count(field, final)
    if advance_count != 1:
        return _failure("QM_FIELD_TIME_CARDINALITY_FAILED", 9, **with_direct)

    receipt = M5DirectReplaceSReceipt(
        contract_id=CONTRACT_ID,
        interval_kind=interval_kind,
        input_field_digest=input_field_digest,
        distribution_digest=distribution_digest,
        interval_digest=interval_digest,
        configuration_digest=configuration_digest,
        geometry_digest=geometry_digest,
        m5_prestate_digest=m5_prestate_digest,
        a1_proposal_digest=a1_proposal_digest,
        m5_next_state_digest=m5_next_state_digest,
        direct_output_digest=direct_output_digest,
        state_output_identity_confirmed=True,
        final_field_digest=_field_digest(final),
        s_replacement_confirmed=True,
        h_identity_confirmed=True,
        field_time_advance_count=advance_count,
        phases=PHASES,
        status=COMPLETED,
        failure_codes=(),
    )
    if not _atomic_output_valid(final, direct_result.state, receipt):
        return _failure("QM_ATOMIC_OUTPUT_FAILED", 10, **with_direct)
    return M5DirectReplaceSResult(final, direct_result.state, receipt)
