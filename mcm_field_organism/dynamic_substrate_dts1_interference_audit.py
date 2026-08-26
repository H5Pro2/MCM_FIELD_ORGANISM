"""Finite private S1-IK execution of the preregistered S1-IJ audit."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math

from .dynamic_substrate_dts1_coupled_step import (
    DTS1CoupledFastFieldStepResult,
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
from .dynamic_substrate_s1ii_interference_contract import (
    S1_II_BASELINE_COUNTERPREDICTIONS,
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


class DTS1InterferenceAuditError(ValueError):
    """Raised when the closed S1-IK audit result is internally invalid."""


S1_IK_AUDIT_ID = "dynamic-substrate.local-aba-interference-audit.s1ik.v1"
S1_IK_SOURCE_S1IJ_CONTRACT_DIGEST = (
    "b24d7ab337b201e24f14abb6bd6d8735b206b51f912da00481432569ce83cb9c"
)
S1_IK_CASE_IDS = (
    "C01_ACTIVE_ABA_VERSUS_A_GAP_A",
    "N01_VALUE_IDENTICAL_ABA_REPLAY",
    "N02_B_ZERO_EQUALS_MATCHED_GAP",
    "N03_A0_DISABLED_FIELD_READOUT",
    "N04_FROZEN_PRESEQUENCE_ADAPTER",
    "N05_MATCHED_ZERO_H",
    "N06_ZERO_A_PROBE_PARTICIPATION",
)
S1_IK_EXPECTED = (
    ("middle_B_engagement_ABA", 0.21122499977283485),
    ("middle_B_engagement_gap", 0.0),
    ("prefinal_shared_free_ABA", 0.4882770296824491),
    ("prefinal_shared_free_gap", 0.5938895295688666),
    ("shared_free_deficit", 0.10561249988641752),
    ("final_A_engagement_ABA", 0.1770192189197149),
    ("final_A_engagement_gap", 0.21530781555964015),
    ("final_A_engagement_margin", 0.03828859663992526),
    ("A_edge_contrast_ABA", 0.31965910192609714),
    ("A_edge_contrast_gap", 0.30941727600747576),
    ("A_edge_contrast_margin", 0.010241825918621383),
    ("complete_main_SH_separation", 0.012414072466544523),
    ("complete_zero_H_SH_separation", 0.012414072466544523),
)
S1_IK_EXPECTED_ABA_MAIN_VECTOR = (
    -0.3285365618910417,
    -0.008877459964944538,
    0.3374140218559861,
    -0.42093511597049654,
    -0.005504159798256638,
    0.4264392757687532,
)
S1_IK_EXPECTED_GAP_MAIN_VECTOR = (
    -0.3296226851650033,
    -0.020205409157527568,
    0.34982809432253065,
    -0.4208720331765879,
    -0.012379420410438664,
    0.4332514535870263,
)
S1_IK_ROUNDOFF_FLOOR = 1.1368683772161603e-13
S1_IK_SINGLE_DIRECT_RESOURCE_CALLS = 24
S1_IK_SINGLE_TECHNICAL_FIELD_CALLS = 10
S1_IK_DOUBLE_DIRECT_RESOURCE_CALLS = 48
S1_IK_DOUBLE_TECHNICAL_FIELD_CALLS = 20
S1_IK_PASS = "PASS_DTS1_LOCAL_ABA_INTERFERENCE"
S1_IK_STOPP = "STOPP_DTS1_LOCAL_ABA_INTERFERENCE"

_INITIAL_S = (-1.0, 0.0, 1.0)
_INITIAL_H_MAIN = (-0.2, 0.0, 0.2)
_INITIAL_H_ZERO = (0.0, 0.0, 0.0)
_CONTACT = (0.0, 0.0, 0.0)
_CAPACITY = 1.0
_INITIAL_CONDUCTIVE = 0.2
_INITIAL_REFRACTORY = 0.1
_A_PARTICIPATION = (1.0, 0.0)
_B_PARTICIPATION = (0.0, 1.0)
_GAP_PARTICIPATION = (0.0, 0.0)
_TICKS_PER_SECOND = 2.0
_SUBSTRATE_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
_AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)
_DISSIPATION_CONFIG = NeutralFieldDissipationConfig(0.0)
_DTS1_RATES = DTS1StepRates(0.4, 0.3, 0.2)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_nonnegative(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise DTS1InterferenceAuditError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1InterferenceAuditError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise DTS1InterferenceAuditError(f"{role} must be finite and nonnegative")
    return result


@dataclass(frozen=True, slots=True)
class DTS1S1IKResourceStepRecord:
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
        if not isinstance(self.arm_id, str) or not self.arm_id or self.interval not in (1, 2, 3):
            raise DTS1InterferenceAuditError("invalid resource step identity")
        for digest in (self.input_anatomy_digest, self.output_anatomy_digest):
            if not isinstance(digest, str) or len(digest) != 64:
                raise DTS1InterferenceAuditError("resource digest must be SHA-256")
        for role, vector, length in (
            ("pre_anatomy_vector", self.pre_anatomy_vector, 4),
            ("post_anatomy_vector", self.post_anatomy_vector, 4),
            ("post_free_vector", self.post_free_vector, 3),
            ("transfer_vector", self.transfer_vector, 6),
        ):
            if len(vector) != length or any(not math.isfinite(value) or value < 0.0 for value in vector):
                raise DTS1InterferenceAuditError(f"invalid {role}")
        object.__setattr__(self, "maximum_local_ledger_residual", _finite_nonnegative(self.maximum_local_ledger_residual, "maximum_local_ledger_residual"))
        object.__setattr__(self, "global_ledger_residual", _finite_nonnegative(self.global_ledger_residual, "global_ledger_residual"))

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
class DTS1S1IKSequenceRecord:
    arm_id: str
    step_records: tuple[DTS1S1IKResourceStepRecord, ...]
    final_anatomy_digest: str

    def __post_init__(self) -> None:
        if len(self.step_records) != 3 or tuple(item.interval for item in self.step_records) != (1, 2, 3):
            raise DTS1InterferenceAuditError("sequence requires three ordered intervals")
        if any(item.arm_id != self.arm_id for item in self.step_records):
            raise DTS1InterferenceAuditError("sequence arm identity mismatch")
        if self.final_anatomy_digest != self.step_records[-1].output_anatomy_digest:
            raise DTS1InterferenceAuditError("sequence final anatomy mismatch")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "arm_id": self.arm_id,
            "step_records": [item.canonical_payload() for item in self.step_records],
            "final_anatomy_digest": self.final_anatomy_digest,
        }


@dataclass(frozen=True, slots=True)
class DTS1S1IKFieldRecord:
    arm_id: str
    input_anatomy_digest: str
    output_anatomy_digest: str
    field_vector: tuple[float, ...]
    adapter_rates: tuple[float, ...]
    A_edge_contrast: float
    maximum_local_ledger_residual: float
    global_ledger_residual: float

    def __post_init__(self) -> None:
        if not isinstance(self.arm_id, str) or not self.arm_id:
            raise DTS1InterferenceAuditError("field arm_id must be nonempty")
        for digest in (self.input_anatomy_digest, self.output_anatomy_digest):
            if not isinstance(digest, str) or len(digest) != 64:
                raise DTS1InterferenceAuditError("field digest must be SHA-256")
        if len(self.field_vector) != 6 or any(not math.isfinite(value) for value in self.field_vector):
            raise DTS1InterferenceAuditError("field vector requires complete finite S/H")
        if len(self.adapter_rates) != 2 or any(not math.isfinite(value) or value <= 0.0 for value in self.adapter_rates):
            raise DTS1InterferenceAuditError("field requires two positive adapter rates")
        object.__setattr__(self, "A_edge_contrast", _finite_nonnegative(self.A_edge_contrast, "A_edge_contrast"))
        object.__setattr__(self, "maximum_local_ledger_residual", _finite_nonnegative(self.maximum_local_ledger_residual, "maximum_local_ledger_residual"))
        object.__setattr__(self, "global_ledger_residual", _finite_nonnegative(self.global_ledger_residual, "global_ledger_residual"))

    def canonical_payload(self) -> dict[str, object]:
        return {
            "arm_id": self.arm_id,
            "input_anatomy_digest": self.input_anatomy_digest,
            "output_anatomy_digest": self.output_anatomy_digest,
            "field_vector": list(self.field_vector),
            "adapter_rates": list(self.adapter_rates),
            "A_edge_contrast": self.A_edge_contrast,
            "maximum_local_ledger_residual": self.maximum_local_ledger_residual,
            "global_ledger_residual": self.global_ledger_residual,
        }


@dataclass(frozen=True, slots=True)
class DTS1S1IKCaseRecord:
    case_id: str
    sequence_records: tuple[DTS1S1IKSequenceRecord, ...]
    field_records: tuple[DTS1S1IKFieldRecord, ...]
    exact_checks: tuple[tuple[str, bool], ...]
    direct_resource_calls: int
    technical_field_calls: int

    def __post_init__(self) -> None:
        expected = {
            S1_IK_CASE_IDS[0]: (2, 2, 6, 2),
            S1_IK_CASE_IDS[1]: (2, 2, 6, 2),
            S1_IK_CASE_IDS[2]: (2, 0, 6, 0),
            S1_IK_CASE_IDS[3]: (0, 2, 0, 2),
            S1_IK_CASE_IDS[4]: (0, 2, 0, 2),
            S1_IK_CASE_IDS[5]: (0, 2, 0, 2),
            S1_IK_CASE_IDS[6]: (2, 0, 6, 0),
        }
        observed = (len(self.sequence_records), len(self.field_records), self.direct_resource_calls, self.technical_field_calls)
        if self.case_id not in expected or observed != expected[self.case_id]:
            raise DTS1InterferenceAuditError("S1-IK case record counts mismatch")
        if not self.exact_checks or any(not isinstance(value, bool) for _, value in self.exact_checks):
            raise DTS1InterferenceAuditError("S1-IK checks must be complete booleans")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "sequence_records": [item.canonical_payload() for item in self.sequence_records],
            "field_records": [item.canonical_payload() for item in self.field_records],
            "exact_checks": [[name, value] for name, value in self.exact_checks],
            "direct_resource_calls": self.direct_resource_calls,
            "technical_field_calls": self.technical_field_calls,
        }


@dataclass(frozen=True, slots=True)
class _DTS1S1IKSingleAuditResult:
    case_records: tuple[DTS1S1IKCaseRecord, ...]
    primary_metrics: tuple[tuple[str, float], ...]
    baseline_records: tuple[tuple[str, str], ...]
    direct_resource_calls: int
    technical_field_calls: int
    research_field_steps: int
    stopp_reasons: tuple[str, ...]
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = self.canonical_payload(include_digest=False)
        if (
            tuple(item.case_id for item in self.case_records) != S1_IK_CASE_IDS
            or tuple(name for name, _ in self.primary_metrics) != tuple(name for name, _ in S1_IK_EXPECTED)
            or self.baseline_records != _baseline_records()
            or self.direct_resource_calls != S1_IK_SINGLE_DIRECT_RESOURCE_CALLS
            or self.technical_field_calls != S1_IK_SINGLE_TECHNICAL_FIELD_CALLS
            or self.research_field_steps != 0
            or self.decision not in (S1_IK_PASS, S1_IK_STOPP)
            or (self.decision == S1_IK_PASS) != (not self.stopp_reasons)
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1InterferenceAuditError("single S1-IK audit result is inconsistent")

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


@dataclass(frozen=True, slots=True)
class DTS1S1IKDoubleAuditResult:
    audit_id: str
    source_s1ij_contract_digest: str
    case_records: tuple[DTS1S1IKCaseRecord, ...]
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

    def __post_init__(self) -> None:
        payload = self.canonical_payload(include_digest=False)
        if (
            self.audit_id != S1_IK_AUDIT_ID
            or self.source_s1ij_contract_digest != S1_IK_SOURCE_S1IJ_CONTRACT_DIGEST
            or tuple(item.case_id for item in self.case_records) != S1_IK_CASE_IDS
            or tuple(name for name, _ in self.primary_metrics) != tuple(name for name, _ in S1_IK_EXPECTED)
            or self.roundoff_floor != S1_IK_ROUNDOFF_FLOOR
            or self.baseline_records != _baseline_records()
            or self.repeated_receipts_identical != (self.first_receipt_digest == self.repeat_receipt_digest)
            or self.direct_resource_calls != S1_IK_DOUBLE_DIRECT_RESOURCE_CALLS
            or self.technical_field_calls != S1_IK_DOUBLE_TECHNICAL_FIELD_CALLS
            or self.research_field_steps != 0
            or self.decision not in (S1_IK_PASS, S1_IK_STOPP)
            or (self.decision == S1_IK_PASS) != (not self.stopp_reasons and self.repeated_receipts_identical)
            or self.audit_receipt_digest != _digest(payload)
        ):
            raise DTS1InterferenceAuditError("double S1-IK audit violates its boundary")

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "audit_id": self.audit_id,
            "source_s1ij_contract_digest": self.source_s1ij_contract_digest,
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


def _reference_frame(snapshot_id: str) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.line.v1",
        snapshot_id=snapshot_id,
        clock_id="synthetic.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=tuple(f"auditory.carrier.{index}" for index in range(3)),
        values=_CONTACT,
    )


def _initial_field(afterimage: tuple[float, float, float]) -> SharedMCMField:
    field = build_shared_mcm_field(
        (_reference_frame("s1ik.reference"),),
        {"auditory": ReceptorDockAnatomy("auditory", "dock.auditory", ((0,), (1,), (2,)))},
        sample_offsets=((-1,), (1,)),
    )
    neurons = tuple(
        replace(item, activation=_INITIAL_S[index], afterimage=afterimage[index])
        for index, item in enumerate(field.layer.neurons)
    )
    return replace(field, layer=replace(field.layer, neurons=neurons))


def _initial_anatomy(field: SharedMCMField) -> DTS1ResourceAnatomy:
    return DTS1ResourceAnatomy(
        tuple(DTS1NodeCapacity(item.neuron_id, _CAPACITY) for item in field.layer.neurons),
        tuple(
            DTS1EdgeResource(*edge, _INITIAL_CONDUCTIVE, _INITIAL_REFRACTORY)
            for edge in mcm_substrate_edge_inventory(field.layer)
        ),
    )


def _distribution():
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock("dock.auditory", "auditory", "auditory.line.v1"))
    return distributor.distribute(
        (_reference_frame("s1ik.zero.contact"),),
        CommonFieldTime("organism.s1ik", 0, 1),
    )


def _step() -> MCMFieldStepTime:
    return MCMFieldStepTime("organism.s1ik", 0, 1, _TICKS_PER_SECOND)


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


def _shared_free(anatomy: DTS1ResourceAnatomy) -> float:
    first_nodes = set(anatomy.edge_resources[0].edge)
    shared = first_nodes.intersection(anatomy.edge_resources[1].edge)
    if len(shared) != 1:
        raise DTS1InterferenceAuditError("fixture edges must share one endpoint")
    free = {item.node_id: item.free for item in anatomy.local_ledgers()}
    return free[next(iter(shared))]


def _field_vector(field: SharedMCMField) -> tuple[float, ...]:
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.neuron_id))
    return tuple([item.activation for item in neurons] + [item.afterimage for item in neurons])


def _A_contrast(field: SharedMCMField) -> float:
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.neuron_id))
    return neurons[1].activation - neurons[0].activation


def _maximum_difference(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def _resource_call(anatomy: DTS1ResourceAnatomy, participations: tuple[float, float], counter: list[int]) -> DTS1StepResult:
    counter[0] += 1
    ledger = tuple(
        DTS1EdgeParticipation(edge.first_node_id, edge.second_node_id, value)
        for edge, value in zip(anatomy.edge_resources, participations, strict=True)
    )
    return compute_dts1_closed_prestate_step(anatomy, ledger, 0.5, _DTS1_RATES)


def _field_call(anatomy: DTS1ResourceAnatomy, afterimage: tuple[float, float, float], enabled: bool, counter: list[int]) -> DTS1CoupledFastFieldStepResult:
    counter[0] += 1
    return advance_dts1_coupled_fast_shared_field(
        _initial_field(afterimage), anatomy, _distribution(), _step(),
        _SUBSTRATE_CONFIG, _AFTERIMAGE_CONFIG, _DTS1_RATES,
        _DISSIPATION_CONFIG, backreaction_enabled=enabled,
    )


def _resource_record(arm_id: str, interval: int, pre: DTS1ResourceAnatomy, result: DTS1StepResult) -> DTS1S1IKResourceStepRecord:
    transfers = tuple(value for item in result.edge_transfers for value in (item.engagement, item.turnover, item.recovery))
    return DTS1S1IKResourceStepRecord(
        arm_id, interval, _anatomy_digest(pre), _anatomy_digest(result.next_anatomy),
        _anatomy_vector(pre), _anatomy_vector(result.next_anatomy),
        _free_vector(result.next_anatomy), transfers,
        result.maximum_local_ledger_residual, result.global_ledger_residual,
    )


def _run_sequence(arm_id: str, middle: tuple[float, float], final: tuple[float, float], counter: list[int]):
    anatomy = _initial_anatomy(_initial_field(_INITIAL_H_MAIN))
    records = []
    prestates = []
    for index, participation in enumerate((_A_PARTICIPATION, middle, final), 1):
        prestates.append(anatomy)
        result = _resource_call(anatomy, participation, counter)
        records.append(_resource_record(arm_id, index, anatomy, result))
        anatomy = result.next_anatomy
    return DTS1S1IKSequenceRecord(arm_id, tuple(records), _anatomy_digest(anatomy)), anatomy, tuple(prestates)


def _field_record(arm_id: str, pre: DTS1ResourceAnatomy, result: DTS1CoupledFastFieldStepResult) -> DTS1S1IKFieldRecord:
    return DTS1S1IKFieldRecord(
        arm_id, _anatomy_digest(pre), _anatomy_digest(result.anatomy),
        _field_vector(result.field),
        tuple(item.rate_per_second for item in result.applied_adapter.edge_rates),
        _A_contrast(result.field),
        max((abs(item.residual) for item in result.anatomy.local_ledgers()), default=0.0),
        abs(result.anatomy.global_residual),
    )


def _near(value: float, expected: float) -> bool:
    return abs(value - expected) <= S1_IK_ROUNDOFF_FLOOR


def _run_c01(resource_counter: list[int], field_counter: list[int]):
    case_id = S1_IK_CASE_IDS[0]
    aba, aba_end, aba_pre = _run_sequence("ABA", _B_PARTICIPATION, _A_PARTICIPATION, resource_counter)
    gap, gap_end, gap_pre = _run_sequence("A_GAP_A", _GAP_PARTICIPATION, _A_PARTICIPATION, resource_counter)
    aba_field = _field_record("ABA", aba_end, _field_call(aba_end, _INITIAL_H_MAIN, True, field_counter))
    gap_field = _field_record("A_GAP_A", gap_end, _field_call(gap_end, _INITIAL_H_MAIN, True, field_counter))
    metrics = (
        ("middle_B_engagement_ABA", aba.step_records[1].transfer_vector[3]),
        ("middle_B_engagement_gap", gap.step_records[1].transfer_vector[3]),
        ("prefinal_shared_free_ABA", _shared_free(aba_pre[2])),
        ("prefinal_shared_free_gap", _shared_free(gap_pre[2])),
        ("shared_free_deficit", _shared_free(gap_pre[2]) - _shared_free(aba_pre[2])),
        ("final_A_engagement_ABA", aba.step_records[2].transfer_vector[0]),
        ("final_A_engagement_gap", gap.step_records[2].transfer_vector[0]),
        ("final_A_engagement_margin", gap.step_records[2].transfer_vector[0] - aba.step_records[2].transfer_vector[0]),
        ("A_edge_contrast_ABA", aba_field.A_edge_contrast),
        ("A_edge_contrast_gap", gap_field.A_edge_contrast),
        ("A_edge_contrast_margin", aba_field.A_edge_contrast - gap_field.A_edge_contrast),
        ("complete_main_SH_separation", _maximum_difference(aba_field.field_vector, gap_field.field_vector)),
    )
    checks = (
        ("resource_and_main_metrics_match_preflight", all(_near(value, expected) for (_, value), (_, expected) in zip(metrics, S1_IK_EXPECTED[:12], strict=True))),
        ("middle_B_positive_and_gap_zero", metrics[0][1] > S1_IK_ROUNDOFF_FLOOR and metrics[1][1] == 0.0),
        ("shared_free_and_final_A_have_direction", metrics[4][1] > S1_IK_ROUNDOFF_FLOOR and metrics[7][1] > S1_IK_ROUNDOFF_FLOOR),
        ("field_direction_and_separation_above_floor", metrics[10][1] > S1_IK_ROUNDOFF_FLOOR and metrics[11][1] > S1_IK_ROUNDOFF_FLOOR),
        ("complete_main_vectors_match_preflight", all(_near(value, expected) for value, expected in zip(aba_field.field_vector, S1_IK_EXPECTED_ABA_MAIN_VECTOR, strict=True)) and all(_near(value, expected) for value, expected in zip(gap_field.field_vector, S1_IK_EXPECTED_GAP_MAIN_VECTOR, strict=True))),
    )
    record = DTS1S1IKCaseRecord(case_id, (aba, gap), (aba_field, gap_field), checks, 6, 2)
    return record, metrics, aba_end, gap_end


def _run_n01(resource_counter: list[int], field_counter: list[int]) -> DTS1S1IKCaseRecord:
    case_id = S1_IK_CASE_IDS[1]
    first, first_end, _ = _run_sequence("ABA_REPEAT", _B_PARTICIPATION, _A_PARTICIPATION, resource_counter)
    second, second_end, _ = _run_sequence("ABA_REPEAT", _B_PARTICIPATION, _A_PARTICIPATION, resource_counter)
    first_field = _field_record("ABA_REPEAT", first_end, _field_call(first_end, _INITIAL_H_MAIN, True, field_counter))
    second_field = _field_record("ABA_REPEAT", second_end, _field_call(second_end, _INITIAL_H_MAIN, True, field_counter))
    checks = (
        ("sequence_payload_bit_exact", first.canonical_payload() == second.canonical_payload()),
        ("field_payload_bit_exact", first_field.canonical_payload() == second_field.canonical_payload()),
    )
    return DTS1S1IKCaseRecord(case_id, (first, second), (first_field, second_field), checks, 6, 2)


def _run_n02(resource_counter: list[int]) -> DTS1S1IKCaseRecord:
    case_id = S1_IK_CASE_IDS[2]
    zero_b, _, _ = _run_sequence("ZERO_B_MATCHED_GAP", _GAP_PARTICIPATION, _A_PARTICIPATION, resource_counter)
    gap, _, _ = _run_sequence("ZERO_B_MATCHED_GAP", _GAP_PARTICIPATION, _A_PARTICIPATION, resource_counter)
    checks = (("zero_B_and_gap_sequences_bit_exact", zero_b.canonical_payload() == gap.canonical_payload()),)
    return DTS1S1IKCaseRecord(case_id, (zero_b, gap), (), checks, 6, 0)


def _run_n03(aba_end: DTS1ResourceAnatomy, gap_end: DTS1ResourceAnatomy, field_counter: list[int]) -> DTS1S1IKCaseRecord:
    case_id = S1_IK_CASE_IDS[3]
    aba = _field_record("ABA_A0", aba_end, _field_call(aba_end, _INITIAL_H_MAIN, False, field_counter))
    gap = _field_record("GAP_A0", gap_end, _field_call(gap_end, _INITIAL_H_MAIN, False, field_counter))
    checks = (
        ("A0_complete_fields_bit_exact", aba.field_vector == gap.field_vector),
        ("A0_adapters_are_base", aba.adapter_rates == gap.adapter_rates == (1.0, 1.0)),
    )
    return DTS1S1IKCaseRecord(case_id, (), (aba, gap), checks, 0, 2)


def _run_n04(field_counter: list[int]) -> DTS1S1IKCaseRecord:
    case_id = S1_IK_CASE_IDS[4]
    initial = _initial_anatomy(_initial_field(_INITIAL_H_MAIN))
    first = _field_record("FROZEN_1", initial, _field_call(initial, _INITIAL_H_MAIN, True, field_counter))
    second = _field_record("FROZEN_2", initial, _field_call(initial, _INITIAL_H_MAIN, True, field_counter))
    checks = (
        ("frozen_complete_fields_bit_exact", first.field_vector == second.field_vector),
        ("frozen_adapters_bit_exact", first.adapter_rates == second.adapter_rates),
    )
    return DTS1S1IKCaseRecord(case_id, (), (first, second), checks, 0, 2)


def _run_n05(aba_end: DTS1ResourceAnatomy, gap_end: DTS1ResourceAnatomy, main_fields: tuple[DTS1S1IKFieldRecord, ...], field_counter: list[int]):
    case_id = S1_IK_CASE_IDS[5]
    aba = _field_record("ABA_ZERO_H", aba_end, _field_call(aba_end, _INITIAL_H_ZERO, True, field_counter))
    gap = _field_record("GAP_ZERO_H", gap_end, _field_call(gap_end, _INITIAL_H_ZERO, True, field_counter))
    separation = _maximum_difference(aba.field_vector, gap.field_vector)
    checks = (
        ("zero_H_S_vectors_match_main", all(_near(a, b) for a, b in zip(aba.field_vector[:3], main_fields[0].field_vector[:3], strict=True)) and all(_near(a, b) for a, b in zip(gap.field_vector[:3], main_fields[1].field_vector[:3], strict=True))),
        ("zero_H_separation_matches_and_exceeds_floor", _near(separation, S1_IK_EXPECTED[-1][1]) and separation > S1_IK_ROUNDOFF_FLOOR),
    )
    return DTS1S1IKCaseRecord(case_id, (), (aba, gap), checks, 0, 2), separation


def _run_n06(resource_counter: list[int]) -> DTS1S1IKCaseRecord:
    case_id = S1_IK_CASE_IDS[6]
    aba, _, _ = _run_sequence("ABA_ZERO_FINAL_A", _B_PARTICIPATION, _GAP_PARTICIPATION, resource_counter)
    gap, _, _ = _run_sequence("GAP_ZERO_FINAL_A", _GAP_PARTICIPATION, _GAP_PARTICIPATION, resource_counter)
    checks = (("final_A_engagement_exact_zero_both_arms", aba.step_records[2].transfer_vector[0] == 0.0 and gap.step_records[2].transfer_vector[0] == 0.0),)
    return DTS1S1IKCaseRecord(case_id, (aba, gap), (), checks, 6, 0)


def _baseline_records() -> tuple[tuple[str, str], ...]:
    return tuple(
        (name, "INTERFERENCE_ALONE_NOT_DISTINCT_NO_EXECUTION" if name == "dynamic-two-state-e1" else "STATE_SPACE_COUNTERPREDICTION_NO_EXECUTION")
        for name, _ in S1_II_BASELINE_COUNTERPREDICTIONS
    )


def _execute_once() -> _DTS1S1IKSingleAuditResult:
    resource_counter = [0]
    field_counter = [0]
    c01, partial_metrics, aba_end, gap_end = _run_c01(resource_counter, field_counter)
    n01 = _run_n01(resource_counter, field_counter)
    n02 = _run_n02(resource_counter)
    n03 = _run_n03(aba_end, gap_end, field_counter)
    n04 = _run_n04(field_counter)
    n05, zero_separation = _run_n05(aba_end, gap_end, c01.field_records, field_counter)
    n06 = _run_n06(resource_counter)
    cases = (c01, n01, n02, n03, n04, n05, n06)
    metrics = partial_metrics + (("complete_zero_H_SH_separation", zero_separation),)
    stopp = []
    if resource_counter[0] != S1_IK_SINGLE_DIRECT_RESOURCE_CALLS:
        stopp.append("direct-resource-call-count")
    if field_counter[0] != S1_IK_SINGLE_TECHNICAL_FIELD_CALLS:
        stopp.append("technical-field-call-count")
    for case in cases:
        stopp.extend(f"{case.case_id}:{name}" for name, passed in case.exact_checks if not passed)
        for sequence in case.sequence_records:
            for step in sequence.step_records:
                if step.maximum_local_ledger_residual > S1_IK_ROUNDOFF_FLOOR:
                    stopp.append(f"{case.case_id}:{sequence.arm_id}:local-resource-ledger")
                if step.global_ledger_residual > S1_IK_ROUNDOFF_FLOOR:
                    stopp.append(f"{case.case_id}:{sequence.arm_id}:global-resource-ledger")
        for field in case.field_records:
            if field.maximum_local_ledger_residual > S1_IK_ROUNDOFF_FLOOR:
                stopp.append(f"{case.case_id}:{field.arm_id}:local-field-ledger")
            if field.global_ledger_residual > S1_IK_ROUNDOFF_FLOOR:
                stopp.append(f"{case.case_id}:{field.arm_id}:global-field-ledger")
    for (name, observed), (_, expected) in zip(metrics, S1_IK_EXPECTED, strict=True):
        if not _near(observed, expected):
            stopp.append(f"metric:{name}")
    baseline_records = _baseline_records()
    decision = S1_IK_PASS if not stopp else S1_IK_STOPP
    payload = {
        "case_records": [item.canonical_payload() for item in cases],
        "primary_metrics": [list(item) for item in metrics],
        "baseline_records": [list(item) for item in baseline_records],
        "direct_resource_calls": resource_counter[0],
        "technical_field_calls": field_counter[0],
        "research_field_steps": 0,
        "stopp_reasons": list(stopp),
        "decision": decision,
    }
    return _DTS1S1IKSingleAuditResult(
        cases, metrics, baseline_records, resource_counter[0], field_counter[0],
        0, tuple(stopp), decision, _digest(payload),
    )


def execute_dts1_s1ik_preregistered_double_audit() -> DTS1S1IKDoubleAuditResult:
    """Execute the complete preregistered double audit exactly once per call."""

    first = _execute_once()
    repeat = _execute_once()
    identical = first.receipt_digest == repeat.receipt_digest
    stopp = list(first.stopp_reasons)
    stopp.extend(reason for reason in repeat.stopp_reasons if reason not in stopp)
    if not identical:
        stopp.append("repeat-receipt-mismatch")
    decision = S1_IK_PASS if not stopp and identical else S1_IK_STOPP
    direct_calls = first.direct_resource_calls + repeat.direct_resource_calls
    field_calls = first.technical_field_calls + repeat.technical_field_calls
    payload = {
        "audit_id": S1_IK_AUDIT_ID,
        "source_s1ij_contract_digest": S1_IK_SOURCE_S1IJ_CONTRACT_DIGEST,
        "case_records": [item.canonical_payload() for item in first.case_records],
        "primary_metrics": [list(item) for item in first.primary_metrics],
        "roundoff_floor": S1_IK_ROUNDOFF_FLOOR,
        "baseline_records": [list(item) for item in first.baseline_records],
        "first_receipt_digest": first.receipt_digest,
        "repeat_receipt_digest": repeat.receipt_digest,
        "repeated_receipts_identical": identical,
        "direct_resource_calls": direct_calls,
        "technical_field_calls": field_calls,
        "research_field_steps": 0,
        "stopp_reasons": list(stopp),
        "decision": decision,
    }
    return DTS1S1IKDoubleAuditResult(
        S1_IK_AUDIT_ID, S1_IK_SOURCE_S1IJ_CONTRACT_DIGEST,
        first.case_records, first.primary_metrics, S1_IK_ROUNDOFF_FLOOR,
        first.baseline_records, first.receipt_digest, repeat.receipt_digest,
        identical, direct_calls, field_calls, 0, tuple(stopp), decision,
        _digest(payload),
    )
