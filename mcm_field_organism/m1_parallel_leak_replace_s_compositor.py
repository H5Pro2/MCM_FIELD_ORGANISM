"""Private atomic M1 parallel-leak REPLACE_S baseline compositor."""

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
from .w7m_capacity_function_matrix import W7MBaselineSpec
from .w7n_capacity_function_baselines import (
    W7NCapacityFunctionBaselineError,
    W7NLocalBaselineResult,
    W7NLocalBaselineState,
    advance_w7n_local_baseline,
    build_zero_w7n_local_baseline,
)


CONTRACT_ID = "m1-parallel-leak-replace-s/s1qr.v1"
SOURCE_S1QQ_DIGEST = (
    "141b552532f0f43449e2d92c2d09274eae6acb66b224cd287b12b3a6d8d63f3b"
)
READOUT_ID = "pointwise-equal-mean/v1"
TRACE_ORDER = ("FAST", "SLOW")
GAP_CHECKPOINTS_SECONDS = (1.0, 4.0, 8.0)
LEAK_EQUATION = "dz_i/dt=(S_i-z_i)/tau;R_i=0"

COMPLETED = "COMPLETED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
STATUSES = (COMPLETED, NOT_COMPUTABLE)
FAILURE_CODES = (
    "QR_INPUT_TYPE_INVALID",
    "QR_FIELD_ROLE_INVALID",
    "QR_DISTRIBUTION_OR_INTERVAL_INVALID",
    "QR_CONFIGURATION_INVALID",
    "QR_M1_PRESTATE_INVALID",
    "QR_GEOMETRY_OR_ORDER_MISMATCH",
    "QR_A1_ADVANCE_FAILED",
    "QR_A1_PROPOSAL_INVALID",
    "QR_FAST_ADVANCE_FAILED",
    "QR_SLOW_ADVANCE_FAILED",
    "QR_TRACE_PAIR_INVALID",
    "QR_MEAN_READOUT_INVALID",
    "QR_S_REPLACEMENT_FAILED",
    "QR_H_OR_PROVENANCE_CHANGED",
    "QR_FIELD_TIME_CARDINALITY_FAILED",
    "QR_ATOMIC_OUTPUT_FAILED",
)
PHASES = (
    "api_intake",
    "common_identity_validation",
    "interval_discrimination",
    "a1_fast_proposal",
    "a1_proposal_validation",
    "fast_trace_advance",
    "slow_trace_advance",
    "trace_pair_validation",
    "equal_mean_readout",
    "replace_s_materialization",
    "final_field_validation",
    "atomic_receipt",
)


class M1ParallelLeakCompositorError(ValueError):
    """Raised when a private M1 value violates its structural surface."""


def _spec_payload(spec: W7MBaselineSpec, role_id: str) -> dict[str, object]:
    return {
        "equation_contract": spec.equation_contract,
        "equation_id": spec.equation_id,
        "model_id": spec.model_id,
        "organism_runtime_allowed": spec.organism_runtime_allowed,
        "parameter_bindings": [list(item) for item in spec.parameter_bindings],
        "persistent_scalars_per_neuron": spec.persistent_scalars_per_neuron,
        "role_id": role_id,
    }


@dataclass(frozen=True, slots=True)
class M1ParallelLeakConfiguration:
    source_registration_digest: str
    trace_order: tuple[str, ...]
    fast_spec: W7MBaselineSpec
    slow_spec: W7MBaselineSpec
    readout_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.source_registration_digest, str):
            raise M1ParallelLeakCompositorError(
                "source registration digest must be a string"
            )
        order = tuple(self.trace_order)
        if any(not isinstance(item, str) for item in order):
            raise M1ParallelLeakCompositorError("trace order must contain strings")
        if not isinstance(self.fast_spec, W7MBaselineSpec) or not isinstance(
            self.slow_spec, W7MBaselineSpec
        ):
            raise M1ParallelLeakCompositorError(
                "M1 configuration requires two W7-M specifications"
            )
        if not isinstance(self.readout_id, str):
            raise M1ParallelLeakCompositorError("readout identity must be a string")
        object.__setattr__(self, "trace_order", order)

    def registration_payload(self) -> dict[str, object]:
        return {
            "contract_id": "m1-two-trace-time-axis/s1qq.v1",
            "gap_checkpoints_seconds": list(GAP_CHECKPOINTS_SECONDS),
            "readout_id": self.readout_id,
            "trace_specs": [
                _spec_payload(self.fast_spec, "FAST"),
                _spec_payload(self.slow_spec, "SLOW"),
            ],
        }


def build_registered_m1_parallel_leak_configuration(
) -> M1ParallelLeakConfiguration:
    """Build the exact private S1-QQ configuration without field access."""

    common = {
        "model_id": "leak",
        "equation_contract": LEAK_EQUATION,
        "persistent_scalars_per_neuron": 1,
        "organism_runtime_allowed": False,
    }
    fast = W7MBaselineSpec(
        equation_id="baseline.m1.fast-local-leak.v1",
        parameter_bindings=(("time_constant_seconds", 1.0),),
        **common,
    )
    slow = W7MBaselineSpec(
        equation_id="baseline.m1.slow-local-leak.v1",
        parameter_bindings=(("time_constant_seconds", 4.0),),
        **common,
    )
    return M1ParallelLeakConfiguration(
        SOURCE_S1QQ_DIGEST,
        TRACE_ORDER,
        fast,
        slow,
        READOUT_ID,
    )


def _configuration_valid(configuration: M1ParallelLeakConfiguration) -> bool:
    registered = build_registered_m1_parallel_leak_configuration()
    return (
        configuration == registered
        and _digest(configuration.registration_payload()) == SOURCE_S1QQ_DIGEST
    )


@dataclass(frozen=True, slots=True)
class M1ParallelLeakBankState:
    fast_state: W7NLocalBaselineState
    slow_state: W7NLocalBaselineState

    def __post_init__(self) -> None:
        if not isinstance(self.fast_state, W7NLocalBaselineState) or not isinstance(
            self.slow_state, W7NLocalBaselineState
        ):
            raise M1ParallelLeakCompositorError(
                "M1 bank requires two W7-N local states"
            )


def build_zero_m1_parallel_leak_bank(
    configuration: M1ParallelLeakConfiguration,
    location_count: int,
) -> M1ParallelLeakBankState:
    """Build two distinct registered W7-N zero states."""

    if not isinstance(configuration, M1ParallelLeakConfiguration):
        raise M1ParallelLeakCompositorError(
            "M1 zero bank requires one explicit configuration"
        )
    if not _configuration_valid(configuration):
        raise M1ParallelLeakCompositorError(
            "M1 zero bank requires the S1-QQ registration"
        )
    try:
        fast = build_zero_w7n_local_baseline(
            configuration.fast_spec, location_count
        )
        slow = build_zero_w7n_local_baseline(
            configuration.slow_spec, location_count
        )
    except W7NCapacityFunctionBaselineError as exc:
        raise M1ParallelLeakCompositorError(str(exc)) from exc
    if fast is slow:
        raise M1ParallelLeakCompositorError("M1 zero states must be distinct")
    return M1ParallelLeakBankState(fast, slow)


def _local_state_payload(state: W7NLocalBaselineState) -> dict[str, object]:
    return {"model_id": state.model_id, "latent": list(state.latent)}


def _bank_payload(state: M1ParallelLeakBankState) -> dict[str, object]:
    return {
        "trace_order": list(TRACE_ORDER),
        "fast_state": _local_state_payload(state.fast_state),
        "slow_state": _local_state_payload(state.slow_state),
    }


def _bank_digest(state: M1ParallelLeakBankState) -> str:
    return _digest(_bank_payload(state))


def _configuration_digest(
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
    m1_configuration: M1ParallelLeakConfiguration,
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
            "m1_registration": m1_configuration.registration_payload(),
            "source_registration_digest": (
                m1_configuration.source_registration_digest
            ),
        }
    )


def _prestate_valid(state: M1ParallelLeakBankState) -> bool:
    return (
        state.fast_state is not state.slow_state
        and state.fast_state.model_id == "leak"
        and state.slow_state.model_id == "leak"
        and len(state.fast_state.latent) == len(state.slow_state.latent)
    )


def _trace_result_valid(result: object, count: int) -> bool:
    if not isinstance(result, W7NLocalBaselineResult):
        return False
    if result.state.model_id != "leak":
        return False
    if len(result.state.latent) != count or len(result.output) != count:
        return False
    values = (*result.state.latent, *result.output)
    return all(math.isfinite(value) for value in values) and (
        result.output == result.state.latent
    )


def _mean_output(
    fast_output: tuple[float, ...],
    slow_output: tuple[float, ...],
) -> tuple[float, ...]:
    return tuple(
        (fast + slow) / 2.0
        for fast, slow in zip(fast_output, slow_output, strict=True)
    )


def _mean_output_valid(
    result: object,
    fast_output: tuple[float, ...],
    slow_output: tuple[float, ...],
) -> bool:
    if not isinstance(result, tuple) or len(result) != len(fast_output):
        return False
    if len(fast_output) != len(slow_output):
        return False
    if any(not isinstance(value, (int, float)) for value in result):
        return False
    if any(not math.isfinite(float(value)) or abs(float(value)) > 1.0 for value in result):
        return False
    expected = tuple(
        (fast + slow) / 2.0
        for fast, slow in zip(fast_output, slow_output, strict=True)
    )
    return result == expected


@dataclass(frozen=True, slots=True)
class M1ParallelLeakReplaceSReceipt:
    contract_id: str
    source_registration_digest: str
    interval_kind: str | None
    input_field_digest: str | None
    distribution_digest: str | None
    interval_digest: str | None
    configuration_digest: str | None
    geometry_digest: str | None
    m1_prestate_digest: str | None
    a1_proposal_digest: str | None
    fast_next_state_digest: str | None
    slow_next_state_digest: str | None
    m1_next_state_digest: str | None
    fast_output_digest: str | None
    slow_output_digest: str | None
    trace_output_identity_confirmed: bool
    mean_output_digest: str | None
    equal_mean_confirmed: bool
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
            raise M1ParallelLeakCompositorError("receipt contract identity mismatch")
        if self.source_registration_digest != SOURCE_S1QQ_DIGEST:
            raise M1ParallelLeakCompositorError(
                "receipt source registration identity mismatch"
            )
        if self.status not in STATUSES:
            raise M1ParallelLeakCompositorError("receipt status is invalid")
        if tuple(self.phases) != PHASES[: len(self.phases)]:
            raise M1ParallelLeakCompositorError(
                "receipt phases are not a canonical prefix"
            )
        if any(code not in FAILURE_CODES for code in self.failure_codes):
            raise M1ParallelLeakCompositorError(
                "receipt contains an unknown failure code"
            )
        ordered = tuple(sorted(self.failure_codes, key=FAILURE_CODES.index))
        if ordered != tuple(self.failure_codes):
            raise M1ParallelLeakCompositorError(
                "receipt failure codes are not canonical"
            )
        if self.status == COMPLETED and self.failure_codes:
            raise M1ParallelLeakCompositorError(
                "completed receipt cannot contain failures"
            )
        if self.status == NOT_COMPUTABLE and not self.failure_codes:
            raise M1ParallelLeakCompositorError(
                "failed receipt requires one failure code"
            )
        expected = _digest(self.canonical_payload())
        if self.receipt_digest and self.receipt_digest != expected:
            raise M1ParallelLeakCompositorError("receipt digest mismatch")
        object.__setattr__(self, "receipt_digest", expected)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "source_registration_digest": self.source_registration_digest,
            "interval_kind": self.interval_kind,
            "input_field_digest": self.input_field_digest,
            "distribution_digest": self.distribution_digest,
            "interval_digest": self.interval_digest,
            "configuration_digest": self.configuration_digest,
            "geometry_digest": self.geometry_digest,
            "m1_prestate_digest": self.m1_prestate_digest,
            "a1_proposal_digest": self.a1_proposal_digest,
            "fast_next_state_digest": self.fast_next_state_digest,
            "slow_next_state_digest": self.slow_next_state_digest,
            "m1_next_state_digest": self.m1_next_state_digest,
            "fast_output_digest": self.fast_output_digest,
            "slow_output_digest": self.slow_output_digest,
            "trace_output_identity_confirmed": (
                self.trace_output_identity_confirmed
            ),
            "mean_output_digest": self.mean_output_digest,
            "equal_mean_confirmed": self.equal_mean_confirmed,
            "final_field_digest": self.final_field_digest,
            "s_replacement_confirmed": self.s_replacement_confirmed,
            "h_identity_confirmed": self.h_identity_confirmed,
            "field_time_advance_count": self.field_time_advance_count,
            "phases": list(self.phases),
            "status": self.status,
            "failure_codes": list(self.failure_codes),
        }


@dataclass(frozen=True, slots=True)
class M1ParallelLeakReplaceSResult:
    field: SharedMCMField | str
    next_m1_state: M1ParallelLeakBankState | str
    receipt: M1ParallelLeakReplaceSReceipt

    def __post_init__(self) -> None:
        if not isinstance(self.receipt, M1ParallelLeakReplaceSReceipt):
            raise M1ParallelLeakCompositorError("result requires one M1 receipt")
        if self.receipt.status == COMPLETED:
            if not isinstance(self.field, SharedMCMField) or not isinstance(
                self.next_m1_state, M1ParallelLeakBankState
            ):
                raise M1ParallelLeakCompositorError(
                    "completed result requires field and M1 bank"
                )
        elif self.field != NOT_COMPUTABLE or self.next_m1_state != NOT_COMPUTABLE:
            raise M1ParallelLeakCompositorError(
                "failed result cannot publish partial state"
            )


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
    m1_prestate_digest: str | None = None,
    a1_proposal_digest: str | None = None,
    fast_next_state_digest: str | None = None,
    slow_next_state_digest: str | None = None,
    m1_next_state_digest: str | None = None,
    fast_output_digest: str | None = None,
    slow_output_digest: str | None = None,
    mean_output_digest: str | None = None,
) -> M1ParallelLeakReplaceSResult:
    receipt = M1ParallelLeakReplaceSReceipt(
        contract_id=CONTRACT_ID,
        source_registration_digest=SOURCE_S1QQ_DIGEST,
        interval_kind=interval_kind,
        input_field_digest=input_field_digest,
        distribution_digest=distribution_digest,
        interval_digest=interval_digest,
        configuration_digest=configuration_digest,
        geometry_digest=geometry_digest,
        m1_prestate_digest=m1_prestate_digest,
        a1_proposal_digest=a1_proposal_digest,
        fast_next_state_digest=fast_next_state_digest,
        slow_next_state_digest=slow_next_state_digest,
        m1_next_state_digest=m1_next_state_digest,
        fast_output_digest=fast_output_digest,
        slow_output_digest=slow_output_digest,
        trace_output_identity_confirmed=False,
        mean_output_digest=mean_output_digest,
        equal_mean_confirmed=False,
        final_field_digest=None,
        s_replacement_confirmed=False,
        h_identity_confirmed=False,
        field_time_advance_count=0,
        phases=PHASES[:phase_count],
        status=NOT_COMPUTABLE,
        failure_codes=(code,),
    )
    return M1ParallelLeakReplaceSResult(
        NOT_COMPUTABLE, NOT_COMPUTABLE, receipt
    )


def _atomic_output_valid(
    final: SharedMCMField,
    next_state: M1ParallelLeakBankState,
    receipt: M1ParallelLeakReplaceSReceipt,
) -> bool:
    return (
        receipt.status == COMPLETED
        and receipt.final_field_digest == _field_digest(final)
        and receipt.m1_next_state_digest == _bank_digest(next_state)
        and receipt.trace_output_identity_confirmed
        and receipt.equal_mean_confirmed
        and receipt.s_replacement_confirmed
        and receipt.h_identity_confirmed
        and receipt.field_time_advance_count == 1
    )


def advance_m1_parallel_leak_replace_s(
    field,
    distribution,
    interval_input,
    neutral_substrate_config,
    fast_afterimage_config,
    m1_configuration,
    m1_prestate,
    dissipation_config=None,
) -> M1ParallelLeakReplaceSResult:
    """Advance one private M1 two-trace field interval atomically."""

    required_types_valid = (
        isinstance(field, SharedMCMField)
        and isinstance(distribution, ReceptorDistribution)
        and isinstance(interval_input, (MCMFieldStepTime, TransientNeuronInputSet))
        and isinstance(neutral_substrate_config, NeutralLocalFieldSubstrateConfig)
        and isinstance(fast_afterimage_config, NeutralFastAfterimageConfig)
        and isinstance(m1_configuration, M1ParallelLeakConfiguration)
        and isinstance(m1_prestate, M1ParallelLeakBankState)
        and (
            dissipation_config is None
            or isinstance(dissipation_config, NeutralFieldDissipationConfig)
        )
    )
    if not required_types_valid:
        return _failure("QR_INPUT_TYPE_INVALID", 1)

    interval_kind = (
        "sync" if isinstance(interval_input, MCMFieldStepTime) else "transient"
    )
    input_field_digest = _field_digest(field)
    distribution_digest = distribution.digest()
    interval_digest = _digest(_interval_payload(interval_input))
    configuration_digest = _configuration_digest(
        neutral_substrate_config,
        fast_afterimage_config,
        dissipation_config,
        m1_configuration,
    )
    geometry_digest = _geometry_digest(field)
    m1_prestate_digest = _bank_digest(m1_prestate)
    common = {
        "interval_kind": interval_kind,
        "input_field_digest": input_field_digest,
        "distribution_digest": distribution_digest,
        "interval_digest": interval_digest,
        "configuration_digest": configuration_digest,
        "geometry_digest": geometry_digest,
        "m1_prestate_digest": m1_prestate_digest,
    }

    if field.substrate is not None or field.development is not None:
        return _failure("QR_FIELD_ROLE_INVALID", 2, **common)
    if not _configuration_valid(m1_configuration):
        return _failure("QR_CONFIGURATION_INVALID", 2, **common)
    if not _prestate_valid(m1_prestate):
        return _failure("QR_M1_PRESTATE_INVALID", 2, **common)
    location_count = len(field.layer.neurons)
    if (
        len(m1_prestate.fast_state.latent) != location_count
        or len(m1_prestate.slow_state.latent) != location_count
    ):
        return _failure("QR_GEOMETRY_OR_ORDER_MISMATCH", 2, **common)
    if not _interval_matches(field, distribution, interval_input):
        return _failure("QR_DISTRIBUTION_OR_INTERVAL_INVALID", 3, **common)

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
        return _failure("QR_A1_ADVANCE_FAILED", 4, **common)
    if not _a1_proposal_valid(field, proposal, distribution):
        return _failure("QR_A1_PROPOSAL_INVALID", 5, **common)
    a1_proposal_digest = _field_digest(proposal)
    with_proposal = {**common, "a1_proposal_digest": a1_proposal_digest}

    evidence = tuple(neuron.activation for neuron in proposal.layer.neurons)
    duration_seconds = (
        interval_input.elapsed_seconds
        if isinstance(interval_input, MCMFieldStepTime)
        else interval_input.step_time.elapsed_seconds
    )
    try:
        fast_result = advance_w7n_local_baseline(
            m1_configuration.fast_spec,
            m1_prestate.fast_state,
            evidence,
            duration_seconds,
        )
    except W7NCapacityFunctionBaselineError:
        return _failure("QR_FAST_ADVANCE_FAILED", 6, **with_proposal)
    fast_next_state_digest = (
        _digest(_local_state_payload(fast_result.state))
        if isinstance(fast_result, W7NLocalBaselineResult)
        else None
    )
    fast_output_digest = (
        _digest({"signed_output": list(fast_result.output)})
        if isinstance(fast_result, W7NLocalBaselineResult)
        else None
    )
    with_fast = {
        **with_proposal,
        "fast_next_state_digest": fast_next_state_digest,
        "fast_output_digest": fast_output_digest,
    }

    try:
        slow_result = advance_w7n_local_baseline(
            m1_configuration.slow_spec,
            m1_prestate.slow_state,
            evidence,
            duration_seconds,
        )
    except W7NCapacityFunctionBaselineError:
        return _failure("QR_SLOW_ADVANCE_FAILED", 7, **with_fast)

    if not _trace_result_valid(fast_result, location_count) or not (
        _trace_result_valid(slow_result, location_count)
    ):
        return _failure("QR_TRACE_PAIR_INVALID", 8, **with_fast)

    next_state = M1ParallelLeakBankState(fast_result.state, slow_result.state)
    slow_next_state_digest = _digest(_local_state_payload(slow_result.state))
    m1_next_state_digest = _bank_digest(next_state)
    slow_output_digest = _digest({"signed_output": list(slow_result.output)})
    with_traces = {
        **with_fast,
        "slow_next_state_digest": slow_next_state_digest,
        "m1_next_state_digest": m1_next_state_digest,
        "slow_output_digest": slow_output_digest,
    }

    try:
        mean_output = _mean_output(fast_result.output, slow_result.output)
    except (TypeError, ValueError, OverflowError):
        return _failure("QR_MEAN_READOUT_INVALID", 9, **with_traces)
    if not _mean_output_valid(
        mean_output, fast_result.output, slow_result.output
    ):
        return _failure("QR_MEAN_READOUT_INVALID", 9, **with_traces)
    mean_output_digest = _digest({"signed_output": list(mean_output)})
    with_mean = {**with_traces, "mean_output_digest": mean_output_digest}

    try:
        final = _materialize_replace_s(proposal, mean_output)
    except (SharedMCMFieldError, TypeError, ValueError):
        return _failure("QR_S_REPLACEMENT_FAILED", 10, **with_mean)
    if not _final_identity_valid(proposal, final, mean_output):
        return _failure("QR_H_OR_PROVENANCE_CHANGED", 11, **with_mean)
    advance_count = _field_time_advance_count(field, final)
    if advance_count != 1:
        return _failure("QR_FIELD_TIME_CARDINALITY_FAILED", 11, **with_mean)

    receipt = M1ParallelLeakReplaceSReceipt(
        contract_id=CONTRACT_ID,
        source_registration_digest=SOURCE_S1QQ_DIGEST,
        interval_kind=interval_kind,
        input_field_digest=input_field_digest,
        distribution_digest=distribution_digest,
        interval_digest=interval_digest,
        configuration_digest=configuration_digest,
        geometry_digest=geometry_digest,
        m1_prestate_digest=m1_prestate_digest,
        a1_proposal_digest=a1_proposal_digest,
        fast_next_state_digest=fast_next_state_digest,
        slow_next_state_digest=slow_next_state_digest,
        m1_next_state_digest=m1_next_state_digest,
        fast_output_digest=fast_output_digest,
        slow_output_digest=slow_output_digest,
        trace_output_identity_confirmed=True,
        mean_output_digest=mean_output_digest,
        equal_mean_confirmed=True,
        final_field_digest=_field_digest(final),
        s_replacement_confirmed=True,
        h_identity_confirmed=True,
        field_time_advance_count=advance_count,
        phases=PHASES,
        status=COMPLETED,
        failure_codes=(),
    )
    if not _atomic_output_valid(final, next_state, receipt):
        return _failure("QR_ATOMIC_OUTPUT_FAILED", 12, **with_mean)
    return M1ParallelLeakReplaceSResult(final, next_state, receipt)
