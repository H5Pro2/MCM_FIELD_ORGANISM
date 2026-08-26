"""Finite private S1-IN execution of the preregistered S1-IM audit."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math

from .dynamic_substrate_dts1_backreaction import (
    DTS1BackreactionResult,
    compute_dts1_edge_rates,
)
from .dynamic_substrate_dts1_coupled_step import (
    DTS1CoupledFastFieldStepResult,
    _advance_active_field,
    advance_dts1_coupled_fast_shared_field,
)
from .dynamic_substrate_dts1_step import (
    DTS1EdgeParticipation,
    DTS1StepRates,
    DTS1StepResult,
    compute_dts1_closed_prestate_step,
)
from .dynamic_substrate_s1hi_resource_anatomy import (
    DTS1EdgeResource,
    DTS1NodeCapacity,
    DTS1ResourceAnatomy,
)
from .dynamic_substrate_s1il_release_reuse_contract import (
    S1_IL_BASELINE_COUNTERPREDICTIONS,
)
from .field_step_time import MCMFieldStepTime
from .mcm_substrate_state import mcm_substrate_edge_inventory
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)


class DTS1ReleaseReuseAuditError(ValueError):
    """Raised when the closed S1-IN audit result is internally invalid."""


S1_IN_AUDIT_ID = "dynamic-substrate.local-capacity-release-reuse-audit.s1in.v1"
S1_IN_SOURCE_S1IM_CONTRACT_DIGEST = (
    "f553533b70088766b41c79b95dee070668a4f5a827c1cb67b773c98f56fd68c2"
)
S1_IN_CASE_IDS = (
    "C01_RECOVERY_ON_VERSUS_OFF_THEN_B",
    "N01_VALUE_IDENTICAL_SEQUENCE_REPLAY",
    "N02_RECOVERY_ZERO_EQUALS_OFF",
    "N03_ZERO_REFRACTORY_SOURCE",
    "N04_ZERO_B_PROBE_PARTICIPATION",
    "N05_A0_DISABLED_FIELD_READOUT",
    "N06_FROZEN_PRERELEASE_ADAPTER",
    "N07_MATCHED_ZERO_H",
)
S1_IN_EXPECTED = (
    ("recovery_on_window_A_recovery", 0.011261744217875269),
    ("recovery_on_window_B_recovery", 0.011261744217875269),
    ("recovery_off_window_A_recovery", 0.0),
    ("recovery_off_window_B_recovery", 0.0),
    ("recovery_on_preprobe_shared_free", 0.5938895295688665),
    ("recovery_off_preprobe_shared_free", 0.5826277853509914),
    ("shared_free_release_margin", 0.01126174421787518),
    ("recovery_on_B_engagement", 0.2153078155596401),
    ("recovery_off_B_engagement", 0.21122499977283485),
    ("additional_B_engagement_margin", 0.0040828157868052495),
    ("B_edge_contrast_recovery_on", 0.3367717320392176),
    ("B_edge_contrast_recovery_off", 0.33724837238920485),
    ("B_edge_contrast_off_minus_on", 0.00047664034998723404),
    ("complete_main_SH_separation", 0.000273420770841859),
    ("complete_zero_H_SH_separation", 0.000273420770841859),
)
S1_IN_EXPECTED_ON_MAIN_VECTOR = (
    -0.33950427416406204,
    0.0013662710624220717,
    0.3381380031016397,
    -0.4271451758519227,
    0.0008376410940565081,
    0.42630753475786604,
)
S1_IN_EXPECTED_OFF_MAIN_VECTOR = (
    -0.33957447535575846,
    0.001163051483276697,
    0.3384114238724816,
    -0.42717123310618593,
    0.0007128200861448213,
    0.4264584130200409,
)
S1_IN_ROUNDOFF_FLOOR = 1.1368683772161603e-13
S1_IN_SINGLE_DIRECT_RESOURCE_CALLS = 18
S1_IN_SINGLE_TECHNICAL_FIELD_CALLS = 10
S1_IN_DOUBLE_DIRECT_RESOURCE_CALLS = 36
S1_IN_DOUBLE_TECHNICAL_FIELD_CALLS = 20
S1_IN_PASS = "PASS_DTS1_LOCAL_CAPACITY_RELEASE_AND_ADJACENT_REUSE"
S1_IN_STOPP = "STOPP_DTS1_LOCAL_CAPACITY_RELEASE_AND_ADJACENT_REUSE"

_INITIAL_S = (-1.0, 0.0, 1.0)
_INITIAL_H_MAIN = (-0.2, 0.0, 0.2)
_INITIAL_H_ZERO = (0.0, 0.0, 0.0)
_CONTACT = (0.0, 0.0, 0.0)
_A_PARTICIPATION = (1.0, 0.0)
_B_PARTICIPATION = (0.0, 1.0)
_ZERO_PARTICIPATION = (0.0, 0.0)
_SUBSTRATE_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
_AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)
_DISSIPATION_CONFIG = NeutralFieldDissipationConfig(0.0)
_RECOVERY_ON_RATES = DTS1StepRates(0.4, 0.3, 0.2)
_RECOVERY_OFF_RATES = DTS1StepRates(0.4, 0.3, 0.0)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_nonnegative(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise DTS1ReleaseReuseAuditError(f"{role} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1ReleaseReuseAuditError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise DTS1ReleaseReuseAuditError(f"{role} must be finite and nonnegative")
    return result


@dataclass(frozen=True, slots=True)
class DTS1S1INResourceStepRecord:
    arm_id: str
    interval: int
    input_anatomy_digest: str
    output_anatomy_digest: str
    pre_anatomy_vector: tuple[float, ...]
    post_anatomy_vector: tuple[float, ...]
    post_free_vector: tuple[float, ...]
    transfer_vector: tuple[float, ...]
    maximum_local_ledger_residual: float
    global_ledger_residual: float

    def __post_init__(self) -> None:
        if not self.arm_id or self.interval not in (1, 2, 3):
            raise DTS1ReleaseReuseAuditError("invalid resource record identity")
        if any(len(item) != 64 for item in (self.input_anatomy_digest, self.output_anatomy_digest)):
            raise DTS1ReleaseReuseAuditError("resource digest must be SHA-256")
        for vector, length in (
            (self.pre_anatomy_vector, 4),
            (self.post_anatomy_vector, 4),
            (self.post_free_vector, 3),
            (self.transfer_vector, 6),
        ):
            if len(vector) != length or any(not math.isfinite(value) or value < 0.0 for value in vector):
                raise DTS1ReleaseReuseAuditError("invalid resource vector")
        object.__setattr__(self, "maximum_local_ledger_residual", _finite_nonnegative(self.maximum_local_ledger_residual, "local residual"))
        object.__setattr__(self, "global_ledger_residual", _finite_nonnegative(self.global_ledger_residual, "global residual"))

    def canonical_payload(self) -> dict[str, object]:
        return {
            "arm_id": self.arm_id,
            "interval": self.interval,
            "input_anatomy_digest": self.input_anatomy_digest,
            "output_anatomy_digest": self.output_anatomy_digest,
            "pre_anatomy_vector": list(self.pre_anatomy_vector),
            "post_anatomy_vector": list(self.post_anatomy_vector),
            "post_free_vector": list(self.post_free_vector),
            "transfer_vector": list(self.transfer_vector),
            "maximum_local_ledger_residual": self.maximum_local_ledger_residual,
            "global_ledger_residual": self.global_ledger_residual,
        }


@dataclass(frozen=True, slots=True)
class DTS1S1INTraceRecord:
    arm_id: str
    step_records: tuple[DTS1S1INResourceStepRecord, ...]

    def __post_init__(self) -> None:
        if not self.step_records or any(item.arm_id != self.arm_id for item in self.step_records):
            raise DTS1ReleaseReuseAuditError("trace requires consistent nonempty records")

    def canonical_payload(self) -> dict[str, object]:
        return {"arm_id": self.arm_id, "step_records": [item.canonical_payload() for item in self.step_records]}


@dataclass(frozen=True, slots=True)
class DTS1S1INFieldRecord:
    arm_id: str
    input_anatomy_digest: str
    field_vector: tuple[float, ...]
    adapter_rates: tuple[float, ...]
    B_edge_contrast: float
    maximum_local_ledger_residual: float
    global_ledger_residual: float

    def __post_init__(self) -> None:
        if not self.arm_id or len(self.input_anatomy_digest) != 64:
            raise DTS1ReleaseReuseAuditError("invalid field identity")
        if len(self.field_vector) != 6 or any(not math.isfinite(value) for value in self.field_vector):
            raise DTS1ReleaseReuseAuditError("field vector requires complete finite S/H")
        if len(self.adapter_rates) != 2 or any(not math.isfinite(value) or value <= 0.0 for value in self.adapter_rates):
            raise DTS1ReleaseReuseAuditError("field adapter requires two rates")
        object.__setattr__(self, "B_edge_contrast", _finite_nonnegative(self.B_edge_contrast, "B contrast"))
        object.__setattr__(self, "maximum_local_ledger_residual", _finite_nonnegative(self.maximum_local_ledger_residual, "local residual"))
        object.__setattr__(self, "global_ledger_residual", _finite_nonnegative(self.global_ledger_residual, "global residual"))

    def canonical_payload(self) -> dict[str, object]:
        return {
            "arm_id": self.arm_id,
            "input_anatomy_digest": self.input_anatomy_digest,
            "field_vector": list(self.field_vector),
            "adapter_rates": list(self.adapter_rates),
            "B_edge_contrast": self.B_edge_contrast,
            "maximum_local_ledger_residual": self.maximum_local_ledger_residual,
            "global_ledger_residual": self.global_ledger_residual,
        }


@dataclass(frozen=True, slots=True)
class DTS1S1INCaseRecord:
    case_id: str
    trace_records: tuple[DTS1S1INTraceRecord, ...]
    field_records: tuple[DTS1S1INFieldRecord, ...]
    exact_checks: tuple[tuple[str, bool], ...]
    direct_resource_calls: int
    technical_field_calls: int

    def __post_init__(self) -> None:
        expected = {
            S1_IN_CASE_IDS[0]: (2, 2, 6, 2),
            S1_IN_CASE_IDS[1]: (2, 2, 6, 2),
            S1_IN_CASE_IDS[2]: (2, 0, 2, 0),
            S1_IN_CASE_IDS[3]: (2, 0, 2, 0),
            S1_IN_CASE_IDS[4]: (2, 0, 2, 0),
            S1_IN_CASE_IDS[5]: (0, 2, 0, 2),
            S1_IN_CASE_IDS[6]: (0, 2, 0, 2),
            S1_IN_CASE_IDS[7]: (0, 2, 0, 2),
        }
        observed = (len(self.trace_records), len(self.field_records), self.direct_resource_calls, self.technical_field_calls)
        if expected.get(self.case_id) != observed or not self.exact_checks:
            raise DTS1ReleaseReuseAuditError("S1-IN case structure mismatch")
        if any(not isinstance(value, bool) for _, value in self.exact_checks):
            raise DTS1ReleaseReuseAuditError("S1-IN checks must be booleans")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "trace_records": [item.canonical_payload() for item in self.trace_records],
            "field_records": [item.canonical_payload() for item in self.field_records],
            "exact_checks": [[name, value] for name, value in self.exact_checks],
            "direct_resource_calls": self.direct_resource_calls,
            "technical_field_calls": self.technical_field_calls,
        }


@dataclass(frozen=True, slots=True)
class _DTS1S1INSingleAuditResult:
    case_records: tuple[DTS1S1INCaseRecord, ...]
    primary_metrics: tuple[tuple[str, float], ...]
    baseline_records: tuple[tuple[str, str], ...]
    direct_resource_calls: int
    technical_field_calls: int
    research_field_steps: int
    stopp_reasons: tuple[str, ...]
    decision: str
    receipt_digest: str

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "case_records": [item.canonical_payload() for item in self.case_records],
            "primary_metrics": [list(item) for item in self.primary_metrics],
            "baseline_records": [list(item) for item in self.baseline_records],
            "direct_resource_calls": self.direct_resource_calls,
            "technical_field_calls": self.technical_field_calls,
            "research_field_steps": self.research_field_steps,
            "stopp_reasons": list(self.stopp_reasons),
            "decision": self.decision,
        }
        if include_digest:
            payload["receipt_digest"] = self.receipt_digest
        return payload

    def __post_init__(self) -> None:
        if (
            tuple(item.case_id for item in self.case_records) != S1_IN_CASE_IDS
            or tuple(name for name, _ in self.primary_metrics) != tuple(name for name, _ in S1_IN_EXPECTED)
            or self.baseline_records != _baseline_records()
            or self.direct_resource_calls != S1_IN_SINGLE_DIRECT_RESOURCE_CALLS
            or self.technical_field_calls != S1_IN_SINGLE_TECHNICAL_FIELD_CALLS
            or self.research_field_steps != 0
            or self.decision not in (S1_IN_PASS, S1_IN_STOPP)
            or (self.decision == S1_IN_PASS) != (not self.stopp_reasons)
            or self.receipt_digest != _digest(self.canonical_payload(include_digest=False))
        ):
            raise DTS1ReleaseReuseAuditError("single S1-IN result is inconsistent")


@dataclass(frozen=True, slots=True)
class DTS1S1INDoubleAuditResult:
    audit_id: str
    source_s1im_contract_digest: str
    case_records: tuple[DTS1S1INCaseRecord, ...]
    primary_metrics: tuple[tuple[str, float], ...]
    roundoff_floor: float
    baseline_records: tuple[tuple[str, str], ...]
    first_receipt_digest: str
    repeat_receipt_digest: str
    repeated_receipts_identical: bool
    direct_resource_calls: int
    technical_field_calls: int
    research_field_steps: int
    stopp_reasons: tuple[str, ...]
    decision: str
    audit_receipt_digest: str

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "audit_id": self.audit_id,
            "source_s1im_contract_digest": self.source_s1im_contract_digest,
            "case_records": [item.canonical_payload() for item in self.case_records],
            "primary_metrics": [list(item) for item in self.primary_metrics],
            "roundoff_floor": self.roundoff_floor,
            "baseline_records": [list(item) for item in self.baseline_records],
            "first_receipt_digest": self.first_receipt_digest,
            "repeat_receipt_digest": self.repeat_receipt_digest,
            "repeated_receipts_identical": self.repeated_receipts_identical,
            "direct_resource_calls": self.direct_resource_calls,
            "technical_field_calls": self.technical_field_calls,
            "research_field_steps": self.research_field_steps,
            "stopp_reasons": list(self.stopp_reasons),
            "decision": self.decision,
        }
        if include_digest:
            payload["audit_receipt_digest"] = self.audit_receipt_digest
        return payload

    def __post_init__(self) -> None:
        if (
            self.audit_id != S1_IN_AUDIT_ID
            or self.source_s1im_contract_digest != S1_IN_SOURCE_S1IM_CONTRACT_DIGEST
            or tuple(item.case_id for item in self.case_records) != S1_IN_CASE_IDS
            or self.roundoff_floor != S1_IN_ROUNDOFF_FLOOR
            or self.repeated_receipts_identical != (self.first_receipt_digest == self.repeat_receipt_digest)
            or self.direct_resource_calls != S1_IN_DOUBLE_DIRECT_RESOURCE_CALLS
            or self.technical_field_calls != S1_IN_DOUBLE_TECHNICAL_FIELD_CALLS
            or self.research_field_steps != 0
            or self.decision not in (S1_IN_PASS, S1_IN_STOPP)
            or (self.decision == S1_IN_PASS) != (not self.stopp_reasons and self.repeated_receipts_identical)
            or self.audit_receipt_digest != _digest(self.canonical_payload(include_digest=False))
        ):
            raise DTS1ReleaseReuseAuditError("double S1-IN result violates its boundary")


def _reference_frame(snapshot_id: str) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        "auditory", "auditory.line.v1", snapshot_id, "synthetic.source", 0, 1,
        tuple(f"auditory.carrier.{index}" for index in range(3)), _CONTACT,
    )


def _initial_field(afterimage: tuple[float, float, float]) -> SharedMCMField:
    field = build_shared_mcm_field(
        (_reference_frame("s1in.reference"),),
        {"auditory": ReceptorDockAnatomy("auditory", "dock.auditory", ((0,), (1,), (2,)))},
        sample_offsets=((-1,), (1,)),
    )
    neurons = tuple(replace(item, activation=_INITIAL_S[index], afterimage=afterimage[index]) for index, item in enumerate(field.layer.neurons))
    return replace(field, layer=replace(field.layer, neurons=neurons))


def _initial_anatomy(field: SharedMCMField) -> DTS1ResourceAnatomy:
    return DTS1ResourceAnatomy(
        tuple(DTS1NodeCapacity(item.neuron_id, 1.0) for item in field.layer.neurons),
        tuple(DTS1EdgeResource(*edge, 0.2, 0.1) for edge in mcm_substrate_edge_inventory(field.layer)),
    )


def _zero_source_anatomy(field: SharedMCMField) -> DTS1ResourceAnatomy:
    return DTS1ResourceAnatomy(
        tuple(DTS1NodeCapacity(item.neuron_id, 1.0) for item in field.layer.neurons),
        tuple(DTS1EdgeResource(*edge, 0.0, 0.0) for edge in mcm_substrate_edge_inventory(field.layer)),
    )


def _distribution():
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock("dock.auditory", "auditory", "auditory.line.v1"))
    return distributor.distribute((_reference_frame("s1in.zero.contact"),), CommonFieldTime("organism.s1in", 0, 1))


def _step_time() -> MCMFieldStepTime:
    return MCMFieldStepTime("organism.s1in", 0, 1, 2.0)


def _anatomy_payload(anatomy: DTS1ResourceAnatomy) -> dict[str, object]:
    return {
        "nodes": [[item.node_id, item.capacity] for item in anatomy.node_capacities],
        "edges": [[item.first_node_id, item.second_node_id, item.conductive_bound, item.refractory] for item in anatomy.edge_resources],
    }


def _anatomy_digest(anatomy: DTS1ResourceAnatomy) -> str:
    return _digest(_anatomy_payload(anatomy))


def _anatomy_vector(anatomy: DTS1ResourceAnatomy) -> tuple[float, ...]:
    return tuple(value for edge in anatomy.edge_resources for value in (edge.conductive_bound, edge.refractory))


def _free_vector(anatomy: DTS1ResourceAnatomy) -> tuple[float, ...]:
    return tuple(item.free for item in anatomy.local_ledgers())


def _field_vector(field: SharedMCMField) -> tuple[float, ...]:
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.neuron_id))
    return tuple([item.activation for item in neurons] + [item.afterimage for item in neurons])


def _B_contrast(field: SharedMCMField) -> float:
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.neuron_id))
    return neurons[2].activation - neurons[1].activation


def _maximum_difference(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def _resource_call(anatomy: DTS1ResourceAnatomy, participation: tuple[float, float], rates: DTS1StepRates, counter: list[int]) -> DTS1StepResult:
    counter[0] += 1
    ledger = tuple(DTS1EdgeParticipation(edge.first_node_id, edge.second_node_id, value) for edge, value in zip(anatomy.edge_resources, participation, strict=True))
    return compute_dts1_closed_prestate_step(anatomy, ledger, 0.5, rates)


def _resource_record(arm_id: str, interval: int, pre: DTS1ResourceAnatomy, result: DTS1StepResult) -> DTS1S1INResourceStepRecord:
    transfers = tuple(value for item in result.edge_transfers for value in (item.engagement, item.turnover, item.recovery))
    return DTS1S1INResourceStepRecord(
        arm_id, interval, _anatomy_digest(pre), _anatomy_digest(result.next_anatomy),
        _anatomy_vector(pre), _anatomy_vector(result.next_anatomy), _free_vector(result.next_anatomy),
        transfers, result.maximum_local_ledger_residual, result.global_ledger_residual,
    )


def _run_full_sequence(arm_id: str, window_rates: DTS1StepRates, B_participation: tuple[float, float], counter: list[int]):
    anatomy = _initial_anatomy(_initial_field(_INITIAL_H_MAIN))
    records = []
    prestates = []
    plan = ((_A_PARTICIPATION, _RECOVERY_ON_RATES), (_ZERO_PARTICIPATION, window_rates), (B_participation, _RECOVERY_ON_RATES))
    for interval, (participation, rates) in enumerate(plan, 1):
        prestates.append(anatomy)
        result = _resource_call(anatomy, participation, rates, counter)
        records.append(_resource_record(arm_id, interval, anatomy, result))
        anatomy = result.next_anatomy
    return DTS1S1INTraceRecord(arm_id, tuple(records)), anatomy, tuple(prestates)


def _single_step_trace(arm_id: str, interval: int, pre: DTS1ResourceAnatomy, participation: tuple[float, float], rates: DTS1StepRates, counter: list[int]):
    result = _resource_call(pre, participation, rates, counter)
    return DTS1S1INTraceRecord(arm_id, (_resource_record(arm_id, interval, pre, result),)), result


def _field_record(arm_id: str, anatomy: DTS1ResourceAnatomy, field: SharedMCMField, adapter: DTS1BackreactionResult) -> DTS1S1INFieldRecord:
    return DTS1S1INFieldRecord(
        arm_id, _anatomy_digest(anatomy), _field_vector(field),
        tuple(item.rate_per_second for item in adapter.edge_rates), _B_contrast(field),
        max((abs(item.residual) for item in anatomy.local_ledgers()), default=0.0), abs(anatomy.global_residual),
    )


def _dynamic_field_record(arm_id: str, anatomy: DTS1ResourceAnatomy, H: tuple[float, float, float], enabled: bool, counter: list[int]) -> DTS1S1INFieldRecord:
    counter[0] += 1
    result: DTS1CoupledFastFieldStepResult = advance_dts1_coupled_fast_shared_field(
        _initial_field(H), anatomy, _distribution(), _step_time(), _SUBSTRATE_CONFIG,
        _AFTERIMAGE_CONFIG, _RECOVERY_ON_RATES, _DISSIPATION_CONFIG,
        backreaction_enabled=enabled,
    )
    return _field_record(arm_id, anatomy, result.field, result.applied_adapter)


def _fixed_field_record(arm_id: str, anatomy: DTS1ResourceAnatomy, H: tuple[float, float, float], adapter: DTS1BackreactionResult, counter: list[int]) -> DTS1S1INFieldRecord:
    counter[0] += 1
    field = _initial_field(H)
    output = _advance_active_field(
        field, _distribution(), _step_time(), _SUBSTRATE_CONFIG, _AFTERIMAGE_CONFIG,
        _DISSIPATION_CONFIG, adapter, 0.5,
    )
    return _field_record(arm_id, anatomy, output, adapter)


def _near(value: float, expected: float) -> bool:
    return abs(value - expected) <= S1_IN_ROUNDOFF_FLOOR


def _baseline_records() -> tuple[tuple[str, str], ...]:
    return tuple(
        (name, "RELEASE_REUSE_ALONE_NOT_DISTINCT_NO_EXECUTION" if name == "dynamic-two-state-e1" else "STATE_SPACE_COUNTERPREDICTION_NO_EXECUTION")
        for name, _ in S1_IL_BASELINE_COUNTERPREDICTIONS
    )


def _run_c01(resource_counter: list[int], field_counter: list[int]):
    on, on_end, on_pre = _run_full_sequence("RECOVERY_ON", _RECOVERY_ON_RATES, _B_PARTICIPATION, resource_counter)
    off, off_end, off_pre = _run_full_sequence("RECOVERY_OFF", _RECOVERY_OFF_RATES, _B_PARTICIPATION, resource_counter)
    on_field = _dynamic_field_record("RECOVERY_ON", on_end, _INITIAL_H_MAIN, True, field_counter)
    off_field = _dynamic_field_record("RECOVERY_OFF", off_end, _INITIAL_H_MAIN, True, field_counter)
    on_window = on.step_records[1].transfer_vector
    off_window = off.step_records[1].transfer_vector
    on_free = _free_vector(on_pre[2])[1]
    off_free = _free_vector(off_pre[2])[1]
    metrics = (
        ("recovery_on_window_A_recovery", on_window[2]),
        ("recovery_on_window_B_recovery", on_window[5]),
        ("recovery_off_window_A_recovery", off_window[2]),
        ("recovery_off_window_B_recovery", off_window[5]),
        ("recovery_on_preprobe_shared_free", on_free),
        ("recovery_off_preprobe_shared_free", off_free),
        ("shared_free_release_margin", on_free - off_free),
        ("recovery_on_B_engagement", on.step_records[2].transfer_vector[3]),
        ("recovery_off_B_engagement", off.step_records[2].transfer_vector[3]),
        ("additional_B_engagement_margin", on.step_records[2].transfer_vector[3] - off.step_records[2].transfer_vector[3]),
        ("B_edge_contrast_recovery_on", on_field.B_edge_contrast),
        ("B_edge_contrast_recovery_off", off_field.B_edge_contrast),
        ("B_edge_contrast_off_minus_on", off_field.B_edge_contrast - on_field.B_edge_contrast),
        ("complete_main_SH_separation", _maximum_difference(on_field.field_vector, off_field.field_vector)),
    )
    checks = (
        ("main_metrics_match_preflight", all(_near(value, expected) for (_, value), (_, expected) in zip(metrics, S1_IN_EXPECTED[:14], strict=True))),
        ("release_positive_and_off_zero", on_window[2] > S1_IN_ROUNDOFF_FLOOR and on_window[5] > S1_IN_ROUNDOFF_FLOOR and off_window[2] == off_window[5] == 0.0),
        ("postwindow_conductive_bit_exact", on.step_records[1].post_anatomy_vector[0::2] == off.step_records[1].post_anatomy_vector[0::2]),
        ("release_and_reuse_margins_positive", metrics[6][1] > S1_IN_ROUNDOFF_FLOOR and metrics[9][1] > S1_IN_ROUNDOFF_FLOOR),
        ("main_vectors_match_preflight", all(_near(a, b) for a, b in zip(on_field.field_vector, S1_IN_EXPECTED_ON_MAIN_VECTOR, strict=True)) and all(_near(a, b) for a, b in zip(off_field.field_vector, S1_IN_EXPECTED_OFF_MAIN_VECTOR, strict=True))),
    )
    case = DTS1S1INCaseRecord(S1_IN_CASE_IDS[0], (on, off), (on_field, off_field), checks, 6, 2)
    return case, metrics, on_end, off_end, on_pre, off_pre


def _run_n01(resource_counter: list[int], field_counter: list[int]) -> DTS1S1INCaseRecord:
    first, first_end, _ = _run_full_sequence("RECOVERY_ON_REPEAT", _RECOVERY_ON_RATES, _B_PARTICIPATION, resource_counter)
    second, second_end, _ = _run_full_sequence("RECOVERY_ON_REPEAT", _RECOVERY_ON_RATES, _B_PARTICIPATION, resource_counter)
    f1 = _dynamic_field_record("RECOVERY_ON_REPEAT", first_end, _INITIAL_H_MAIN, True, field_counter)
    f2 = _dynamic_field_record("RECOVERY_ON_REPEAT", second_end, _INITIAL_H_MAIN, True, field_counter)
    checks = (("sequence_payload_bit_exact", first.canonical_payload() == second.canonical_payload()), ("field_payload_bit_exact", f1.canonical_payload() == f2.canonical_payload()))
    return DTS1S1INCaseRecord(S1_IN_CASE_IDS[1], (first, second), (f1, f2), checks, 6, 2)


def _run_n02(common: DTS1ResourceAnatomy, resource_counter: list[int]) -> DTS1S1INCaseRecord:
    first, r1 = _single_step_trace("RECOVERY_ZERO", 2, common, _ZERO_PARTICIPATION, _RECOVERY_OFF_RATES, resource_counter)
    second, r2 = _single_step_trace("RECOVERY_ZERO", 2, common, _ZERO_PARTICIPATION, _RECOVERY_OFF_RATES, resource_counter)
    checks = (("recovery_zero_equals_explicit_off_bit_exact", first.canonical_payload() == second.canonical_payload() and r1.next_anatomy == r2.next_anatomy),)
    return DTS1S1INCaseRecord(S1_IN_CASE_IDS[2], (first, second), (), checks, 2, 0)


def _run_n03(resource_counter: list[int]) -> DTS1S1INCaseRecord:
    zero = _zero_source_anatomy(_initial_field(_INITIAL_H_MAIN))
    on, r1 = _single_step_trace("ZERO_SOURCE", 2, zero, _ZERO_PARTICIPATION, _RECOVERY_ON_RATES, resource_counter)
    off, r2 = _single_step_trace("ZERO_SOURCE", 2, zero, _ZERO_PARTICIPATION, _RECOVERY_OFF_RATES, resource_counter)
    checks = (("zero_source_recovery_and_all_transfers_zero", all(value == 0.0 for trace in (on, off) for value in trace.step_records[0].transfer_vector)), ("zero_source_outputs_bit_exact", r1.next_anatomy == r2.next_anatomy))
    return DTS1S1INCaseRecord(S1_IN_CASE_IDS[3], (on, off), (), checks, 2, 0)


def _run_n04(on_pre: DTS1ResourceAnatomy, off_pre: DTS1ResourceAnatomy, resource_counter: list[int]) -> DTS1S1INCaseRecord:
    on, _ = _single_step_trace("ZERO_B_ON", 3, on_pre, _ZERO_PARTICIPATION, _RECOVERY_ON_RATES, resource_counter)
    off, _ = _single_step_trace("ZERO_B_OFF", 3, off_pre, _ZERO_PARTICIPATION, _RECOVERY_ON_RATES, resource_counter)
    checks = (("zero_B_engagement_exact_both_arms", on.step_records[0].transfer_vector[3] == 0.0 and off.step_records[0].transfer_vector[3] == 0.0),)
    return DTS1S1INCaseRecord(S1_IN_CASE_IDS[4], (on, off), (), checks, 2, 0)


def _run_n05(on_end: DTS1ResourceAnatomy, off_end: DTS1ResourceAnatomy, field_counter: list[int]) -> DTS1S1INCaseRecord:
    on = _dynamic_field_record("A0_ON", on_end, _INITIAL_H_MAIN, False, field_counter)
    off = _dynamic_field_record("A0_OFF", off_end, _INITIAL_H_MAIN, False, field_counter)
    checks = (("A0_complete_fields_bit_exact", on.field_vector == off.field_vector), ("A0_adapters_base", on.adapter_rates == off.adapter_rates == (1.0, 1.0)))
    return DTS1S1INCaseRecord(S1_IN_CASE_IDS[5], (), (on, off), checks, 0, 2)


def _run_n06(common: DTS1ResourceAnatomy, on_end: DTS1ResourceAnatomy, off_end: DTS1ResourceAnatomy, field_counter: list[int]) -> DTS1S1INCaseRecord:
    field = _initial_field(_INITIAL_H_MAIN)
    adapter = compute_dts1_edge_rates(field.layer, common, _SUBSTRATE_CONFIG, backreaction_enabled=True)
    on = _fixed_field_record("FIXED_ON", on_end, _INITIAL_H_MAIN, adapter, field_counter)
    off = _fixed_field_record("FIXED_OFF", off_end, _INITIAL_H_MAIN, adapter, field_counter)
    checks = (("fixed_complete_fields_bit_exact", on.field_vector == off.field_vector), ("fixed_adapters_bit_exact", on.adapter_rates == off.adapter_rates))
    return DTS1S1INCaseRecord(S1_IN_CASE_IDS[6], (), (on, off), checks, 0, 2)


def _run_n07(on_end: DTS1ResourceAnatomy, off_end: DTS1ResourceAnatomy, main_fields: tuple[DTS1S1INFieldRecord, ...], field_counter: list[int]):
    on = _dynamic_field_record("ZERO_H_ON", on_end, _INITIAL_H_ZERO, True, field_counter)
    off = _dynamic_field_record("ZERO_H_OFF", off_end, _INITIAL_H_ZERO, True, field_counter)
    separation = _maximum_difference(on.field_vector, off.field_vector)
    checks = (("zero_H_S_matches_main", on.field_vector[:3] == main_fields[0].field_vector[:3] and off.field_vector[:3] == main_fields[1].field_vector[:3]), ("zero_H_separation_matches_and_exceeds_floor", _near(separation, S1_IN_EXPECTED[-1][1]) and separation > S1_IN_ROUNDOFF_FLOOR))
    return DTS1S1INCaseRecord(S1_IN_CASE_IDS[7], (), (on, off), checks, 0, 2), separation


def _execute_once() -> _DTS1S1INSingleAuditResult:
    resource_counter = [0]
    field_counter = [0]
    c01, partial_metrics, on_end, off_end, on_pre, off_pre = _run_c01(resource_counter, field_counter)
    n01 = _run_n01(resource_counter, field_counter)
    common = on_pre[1]
    n02 = _run_n02(common, resource_counter)
    n03 = _run_n03(resource_counter)
    n04 = _run_n04(on_pre[2], off_pre[2], resource_counter)
    n05 = _run_n05(on_end, off_end, field_counter)
    n06 = _run_n06(common, on_end, off_end, field_counter)
    n07, zero_separation = _run_n07(on_end, off_end, c01.field_records, field_counter)
    cases = (c01, n01, n02, n03, n04, n05, n06, n07)
    metrics = partial_metrics + (("complete_zero_H_SH_separation", zero_separation),)
    stopp = []
    if resource_counter[0] != S1_IN_SINGLE_DIRECT_RESOURCE_CALLS:
        stopp.append("direct-resource-call-count")
    if field_counter[0] != S1_IN_SINGLE_TECHNICAL_FIELD_CALLS:
        stopp.append("technical-field-call-count")
    for case in cases:
        stopp.extend(f"{case.case_id}:{name}" for name, passed in case.exact_checks if not passed)
        for trace in case.trace_records:
            for step in trace.step_records:
                if step.maximum_local_ledger_residual > S1_IN_ROUNDOFF_FLOOR:
                    stopp.append(f"{case.case_id}:{trace.arm_id}:local-resource-ledger")
                if step.global_ledger_residual > S1_IN_ROUNDOFF_FLOOR:
                    stopp.append(f"{case.case_id}:{trace.arm_id}:global-resource-ledger")
        for field in case.field_records:
            if field.maximum_local_ledger_residual > S1_IN_ROUNDOFF_FLOOR:
                stopp.append(f"{case.case_id}:{field.arm_id}:local-field-ledger")
            if field.global_ledger_residual > S1_IN_ROUNDOFF_FLOOR:
                stopp.append(f"{case.case_id}:{field.arm_id}:global-field-ledger")
    for (name, observed), (_, expected) in zip(metrics, S1_IN_EXPECTED, strict=True):
        if not _near(observed, expected):
            stopp.append(f"metric:{name}")
    baselines = _baseline_records()
    decision = S1_IN_PASS if not stopp else S1_IN_STOPP
    payload = {
        "case_records": [item.canonical_payload() for item in cases],
        "primary_metrics": [list(item) for item in metrics],
        "baseline_records": [list(item) for item in baselines],
        "direct_resource_calls": resource_counter[0],
        "technical_field_calls": field_counter[0],
        "research_field_steps": 0,
        "stopp_reasons": stopp,
        "decision": decision,
    }
    return _DTS1S1INSingleAuditResult(cases, metrics, baselines, resource_counter[0], field_counter[0], 0, tuple(stopp), decision, _digest(payload))


def execute_dts1_s1in_preregistered_double_audit() -> DTS1S1INDoubleAuditResult:
    """Execute the complete preregistered double audit exactly once per call."""

    first = _execute_once()
    repeat = _execute_once()
    identical = first.receipt_digest == repeat.receipt_digest
    stopp = list(first.stopp_reasons)
    stopp.extend(reason for reason in repeat.stopp_reasons if reason not in stopp)
    if not identical:
        stopp.append("repeat-receipt-mismatch")
    decision = S1_IN_PASS if not stopp and identical else S1_IN_STOPP
    payload = {
        "audit_id": S1_IN_AUDIT_ID,
        "source_s1im_contract_digest": S1_IN_SOURCE_S1IM_CONTRACT_DIGEST,
        "case_records": [item.canonical_payload() for item in first.case_records],
        "primary_metrics": [list(item) for item in first.primary_metrics],
        "roundoff_floor": S1_IN_ROUNDOFF_FLOOR,
        "baseline_records": [list(item) for item in first.baseline_records],
        "first_receipt_digest": first.receipt_digest,
        "repeat_receipt_digest": repeat.receipt_digest,
        "repeated_receipts_identical": identical,
        "direct_resource_calls": first.direct_resource_calls + repeat.direct_resource_calls,
        "technical_field_calls": first.technical_field_calls + repeat.technical_field_calls,
        "research_field_steps": 0,
        "stopp_reasons": stopp,
        "decision": decision,
    }
    return DTS1S1INDoubleAuditResult(
        S1_IN_AUDIT_ID, S1_IN_SOURCE_S1IM_CONTRACT_DIGEST, first.case_records,
        first.primary_metrics, S1_IN_ROUNDOFF_FLOOR, first.baseline_records,
        first.receipt_digest, repeat.receipt_digest, identical,
        first.direct_resource_calls + repeat.direct_resource_calls,
        first.technical_field_calls + repeat.technical_field_calls, 0,
        tuple(stopp), decision, _digest(payload),
    )
