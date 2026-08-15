"""Finite private S1-IH execution of the preregistered S1-IG audit."""

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
from .dynamic_substrate_s1if_attenuation_contract import (
    S1_IF_BASELINE_COUNTERPREDICTIONS,
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


class DTS1AttenuationAuditError(ValueError):
    """Raised when the closed S1-IH audit result is internally invalid."""


S1_IH_AUDIT_ID = "dynamic-substrate.repeated-contact-attenuation-audit.s1ih.v1"
S1_IH_SOURCE_S1IG_CONTRACT_DIGEST = (
    "f807ed35def035d4390602555520fe3df1b19f4066e572a993c18f7aac9af9cd"
)
S1_IH_CASE_IDS = (
    "C01_ACTIVE_THREE_CONTACT_ATTENUATION",
    "N01_VALUE_IDENTICAL_REPLAY",
    "N02_A0_DISABLED_CANDIDATE",
    "N03_FROZEN_PRESEQUENCE_ADAPTER",
    "N04_MATCHED_ZERO_H",
    "N05_ZERO_PARTICIPATION",
)
S1_IH_EXPECTED = (
    ("engagement_1", 0.2537769456908254),
    ("engagement_2", 0.21122499977283485),
    ("engagement_3", 0.17701921891971492),
    ("adapter_1", 1.2),
    ("adapter_2", 1.299030068130424),
    ("adapter_3", 1.362990064717202),
    ("contrast_1", 0.3653670481054693),
    ("contrast_2", 0.33091858932072243),
    ("contrast_3", 0.3104157086599864),
    ("engagement_drop_1", 0.04255194591799055),
    ("engagement_drop_2", 0.034205780853119926),
    ("contrast_drop_1", 0.034448458784746894),
    ("contrast_drop_2", 0.020502880660736023),
)
S1_IH_ROUNDOFF_FLOOR = 1.1368683772161603e-13
S1_IH_SINGLE_DIRECT_RESOURCE_CALLS = 8
S1_IH_SINGLE_TECHNICAL_FIELD_CALLS = 14
S1_IH_DOUBLE_DIRECT_RESOURCE_CALLS = 16
S1_IH_DOUBLE_TECHNICAL_FIELD_CALLS = 28
S1_IH_PASS = "PASS_DTS1_REPEATED_EQUAL_CONTACT_ATTENUATION"
S1_IH_STOPP = "STOPP_DTS1_REPEATED_EQUAL_CONTACT_ATTENUATION"

_INITIAL_S = (-1.0, 1.0)
_INITIAL_H_MAIN = (-0.2, 0.2)
_INITIAL_H_ZERO = (0.0, 0.0)
_CONTACT = (0.0, 0.0)
_CAPACITY = 1.0
_CONDUCTIVE = 0.4
_REFRACTORY = 0.2
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
        raise DTS1AttenuationAuditError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1AttenuationAuditError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise DTS1AttenuationAuditError(f"{role} must be finite and nonnegative")
    return result


@dataclass(frozen=True, slots=True)
class DTS1S1IHContactRecord:
    case_id: str
    contact_index: int
    participation: float
    pre_anatomy_vector: tuple[float, ...]
    post_anatomy_vector: tuple[float, ...]
    input_anatomy_digest: str
    output_anatomy_digest: str
    transfer_vector: tuple[float, ...]
    maximum_local_ledger_residual: float
    global_ledger_residual: float

    def __post_init__(self) -> None:
        if self.case_id not in S1_IH_CASE_IDS or self.contact_index not in (1, 2, 3):
            raise DTS1AttenuationAuditError("invalid S1-IH contact identity")
        object.__setattr__(self, "participation", _finite_nonnegative(self.participation, "participation"))
        if self.participation > 1.0:
            raise DTS1AttenuationAuditError("contact participation exceeds one")
        for role, vector in (
            ("pre_anatomy_vector", self.pre_anatomy_vector),
            ("post_anatomy_vector", self.post_anatomy_vector),
            ("transfer_vector", self.transfer_vector),
        ):
            if len(vector) not in (3, 4) or any(not math.isfinite(value) or value < 0.0 for value in vector):
                raise DTS1AttenuationAuditError(f"invalid contact {role}")
        if len(self.pre_anatomy_vector) != 4 or len(self.post_anatomy_vector) != 4 or len(self.transfer_vector) != 3:
            raise DTS1AttenuationAuditError("contact vectors are incomplete")
        for digest in (self.input_anatomy_digest, self.output_anatomy_digest):
            if not isinstance(digest, str) or len(digest) != 64:
                raise DTS1AttenuationAuditError("contact digest must be SHA-256")
        object.__setattr__(self, "maximum_local_ledger_residual", _finite_nonnegative(self.maximum_local_ledger_residual, "maximum_local_ledger_residual"))
        object.__setattr__(self, "global_ledger_residual", _finite_nonnegative(self.global_ledger_residual, "global_ledger_residual"))

    def canonical_payload(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "contact_index": self.contact_index,
            "participation": self.participation,
            "pre_anatomy_vector": list(self.pre_anatomy_vector),
            "post_anatomy_vector": list(self.post_anatomy_vector),
            "input_anatomy_digest": self.input_anatomy_digest,
            "output_anatomy_digest": self.output_anatomy_digest,
            "transfer_vector": list(self.transfer_vector),
            "maximum_local_ledger_residual": self.maximum_local_ledger_residual,
            "global_ledger_residual": self.global_ledger_residual,
        }


@dataclass(frozen=True, slots=True)
class DTS1S1IHFieldRecord:
    case_id: str
    checkpoint: int
    input_anatomy_digest: str
    output_anatomy_digest: str
    field_vector: tuple[float, ...]
    adapter_rate: float
    contrast: float
    maximum_local_ledger_residual: float
    global_ledger_residual: float

    def __post_init__(self) -> None:
        if self.case_id not in S1_IH_CASE_IDS or self.checkpoint not in (1, 2, 3):
            raise DTS1AttenuationAuditError("invalid S1-IH field identity")
        for digest in (self.input_anatomy_digest, self.output_anatomy_digest):
            if not isinstance(digest, str) or len(digest) != 64:
                raise DTS1AttenuationAuditError("field digest must be SHA-256")
        if len(self.field_vector) != 4 or any(not math.isfinite(value) for value in self.field_vector):
            raise DTS1AttenuationAuditError("field vector must contain complete finite S/H")
        object.__setattr__(self, "adapter_rate", _finite_nonnegative(self.adapter_rate, "adapter_rate"))
        object.__setattr__(self, "contrast", _finite_nonnegative(self.contrast, "contrast"))
        object.__setattr__(self, "maximum_local_ledger_residual", _finite_nonnegative(self.maximum_local_ledger_residual, "maximum_local_ledger_residual"))
        object.__setattr__(self, "global_ledger_residual", _finite_nonnegative(self.global_ledger_residual, "global_ledger_residual"))

    def canonical_payload(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "checkpoint": self.checkpoint,
            "input_anatomy_digest": self.input_anatomy_digest,
            "output_anatomy_digest": self.output_anatomy_digest,
            "field_vector": list(self.field_vector),
            "adapter_rate": self.adapter_rate,
            "contrast": self.contrast,
            "maximum_local_ledger_residual": self.maximum_local_ledger_residual,
            "global_ledger_residual": self.global_ledger_residual,
        }


@dataclass(frozen=True, slots=True)
class DTS1S1IHCaseRecord:
    case_id: str
    contact_records: tuple[DTS1S1IHContactRecord, ...]
    field_records: tuple[DTS1S1IHFieldRecord, ...]
    exact_checks: tuple[tuple[str, bool], ...]
    direct_resource_calls: int
    technical_field_calls: int

    def __post_init__(self) -> None:
        expected = {
            S1_IH_CASE_IDS[0]: (3, 3),
            S1_IH_CASE_IDS[1]: (2, 2),
            S1_IH_CASE_IDS[2]: (0, 3),
            S1_IH_CASE_IDS[3]: (0, 3),
            S1_IH_CASE_IDS[4]: (0, 3),
            S1_IH_CASE_IDS[5]: (3, 0),
        }
        if self.case_id not in expected or (len(self.contact_records), len(self.field_records)) != expected[self.case_id]:
            raise DTS1AttenuationAuditError("S1-IH case has wrong record counts")
        if (self.direct_resource_calls, self.technical_field_calls) != expected[self.case_id]:
            raise DTS1AttenuationAuditError("S1-IH case has wrong call counts")
        if not self.exact_checks or any(not isinstance(value, bool) for _, value in self.exact_checks):
            raise DTS1AttenuationAuditError("S1-IH checks must be complete booleans")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "contact_records": [record.canonical_payload() for record in self.contact_records],
            "field_records": [record.canonical_payload() for record in self.field_records],
            "exact_checks": [[name, value] for name, value in self.exact_checks],
            "direct_resource_calls": self.direct_resource_calls,
            "technical_field_calls": self.technical_field_calls,
        }


@dataclass(frozen=True, slots=True)
class _DTS1S1IHSingleAuditResult:
    case_records: tuple[DTS1S1IHCaseRecord, ...]
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
            tuple(record.case_id for record in self.case_records) != S1_IH_CASE_IDS
            or tuple(name for name, _ in self.primary_metrics) != tuple(name for name, _ in S1_IH_EXPECTED)
            or self.baseline_records != _baseline_records()
            or self.direct_resource_calls != S1_IH_SINGLE_DIRECT_RESOURCE_CALLS
            or self.technical_field_calls != S1_IH_SINGLE_TECHNICAL_FIELD_CALLS
            or self.research_field_steps != 0
            or self.decision not in (S1_IH_PASS, S1_IH_STOPP)
            or (self.decision == S1_IH_PASS) != (not self.stopp_reasons)
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1AttenuationAuditError("single S1-IH audit result is inconsistent")

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "case_records": [record.canonical_payload() for record in self.case_records],
            "primary_metrics": [list(metric) for metric in self.primary_metrics],
            "baseline_records": [list(record) for record in self.baseline_records],
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
class DTS1S1IHDoubleAuditResult:
    audit_id: str
    source_s1ig_contract_digest: str
    case_records: tuple[DTS1S1IHCaseRecord, ...]
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
            self.audit_id != S1_IH_AUDIT_ID
            or self.source_s1ig_contract_digest != S1_IH_SOURCE_S1IG_CONTRACT_DIGEST
            or tuple(record.case_id for record in self.case_records) != S1_IH_CASE_IDS
            or tuple(name for name, _ in self.primary_metrics) != tuple(name for name, _ in S1_IH_EXPECTED)
            or self.roundoff_floor != S1_IH_ROUNDOFF_FLOOR
            or self.baseline_records != _baseline_records()
            or self.repeated_receipts_identical != (self.first_receipt_digest == self.repeat_receipt_digest)
            or self.direct_resource_calls != S1_IH_DOUBLE_DIRECT_RESOURCE_CALLS
            or self.technical_field_calls != S1_IH_DOUBLE_TECHNICAL_FIELD_CALLS
            or self.research_field_steps != 0
            or self.decision not in (S1_IH_PASS, S1_IH_STOPP)
            or (self.decision == S1_IH_PASS) != (not self.stopp_reasons and self.repeated_receipts_identical)
            or self.audit_receipt_digest != _digest(payload)
        ):
            raise DTS1AttenuationAuditError("double S1-IH audit violates its boundary")

    def canonical_payload(self, *, include_digest: bool = True) -> dict[str, object]:
        payload = {
            "audit_id": self.audit_id,
            "source_s1ig_contract_digest": self.source_s1ig_contract_digest,
            "case_records": [record.canonical_payload() for record in self.case_records],
            "primary_metrics": [list(metric) for metric in self.primary_metrics],
            "roundoff_floor": self.roundoff_floor,
            "baseline_records": [list(record) for record in self.baseline_records],
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
        carrier_ids=("auditory.carrier.0", "auditory.carrier.1"),
        values=_CONTACT,
    )


def _initial_field(afterimage: tuple[float, float]) -> SharedMCMField:
    field = build_shared_mcm_field(
        (_reference_frame("s1ih.reference"),),
        {"auditory": ReceptorDockAnatomy("auditory", "dock.auditory", ((0,), (1,)))},
        sample_offsets=((-1,), (1,)),
    )
    neurons = tuple(
        replace(neuron, activation=_INITIAL_S[index], afterimage=afterimage[index])
        for index, neuron in enumerate(field.layer.neurons)
    )
    return replace(field, layer=replace(field.layer, neurons=neurons))


def _initial_anatomy(field: SharedMCMField) -> DTS1ResourceAnatomy:
    return DTS1ResourceAnatomy(
        tuple(DTS1NodeCapacity(neuron.neuron_id, _CAPACITY) for neuron in field.layer.neurons),
        (DTS1EdgeResource(*mcm_substrate_edge_inventory(field.layer)[0], _CONDUCTIVE, _REFRACTORY),),
    )


def _distribution():
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock("dock.auditory", "auditory", "auditory.line.v1"))
    return distributor.distribute(
        (_reference_frame("s1ih.zero.contact"),),
        CommonFieldTime("organism.s1ih", 0, 1),
    )


def _step() -> MCMFieldStepTime:
    return MCMFieldStepTime("organism.s1ih", 0, 1, _TICKS_PER_SECOND)


def _anatomy_payload(anatomy: DTS1ResourceAnatomy) -> dict[str, object]:
    return {
        "nodes": [[item.node_id, item.capacity] for item in anatomy.node_capacities],
        "edges": [[item.first_node_id, item.second_node_id, item.conductive_bound, item.refractory] for item in anatomy.edge_resources],
    }


def _anatomy_digest(anatomy: DTS1ResourceAnatomy) -> str:
    return _digest(_anatomy_payload(anatomy))


def _anatomy_vector(anatomy: DTS1ResourceAnatomy) -> tuple[float, ...]:
    edge = anatomy.edge_resources[0]
    free = tuple(item.free for item in anatomy.local_ledgers())
    return (edge.conductive_bound, edge.refractory, free[0], free[1])


def _field_vector(field: SharedMCMField) -> tuple[float, ...]:
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.neuron_id))
    return tuple([item.activation for item in neurons] + [item.afterimage for item in neurons])


def _contrast(field: SharedMCMField) -> float:
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.neuron_id))
    return neurons[1].activation - neurons[0].activation


def _maximum_local_residual(anatomy: DTS1ResourceAnatomy) -> float:
    return max((abs(item.residual) for item in anatomy.local_ledgers()), default=0.0)


def _resource_call(
    anatomy: DTS1ResourceAnatomy,
    participation: float,
    counter: list[int],
) -> DTS1StepResult:
    counter[0] += 1
    edge = anatomy.edge_resources[0]
    return compute_dts1_closed_prestate_step(
        anatomy,
        (DTS1EdgeParticipation(edge.first_node_id, edge.second_node_id, participation),),
        0.5,
        _DTS1_RATES,
    )


def _field_call(
    anatomy: DTS1ResourceAnatomy,
    afterimage: tuple[float, float],
    enabled: bool,
    counter: list[int],
) -> DTS1CoupledFastFieldStepResult:
    counter[0] += 1
    return advance_dts1_coupled_fast_shared_field(
        _initial_field(afterimage),
        anatomy,
        _distribution(),
        _step(),
        _SUBSTRATE_CONFIG,
        _AFTERIMAGE_CONFIG,
        _DTS1_RATES,
        _DISSIPATION_CONFIG,
        backreaction_enabled=enabled,
    )


def _contact_record(case_id: str, index: int, pre: DTS1ResourceAnatomy, result: DTS1StepResult, participation: float) -> DTS1S1IHContactRecord:
    transfer = result.edge_transfers[0]
    return DTS1S1IHContactRecord(
        case_id=case_id,
        contact_index=index,
        participation=participation,
        pre_anatomy_vector=_anatomy_vector(pre),
        post_anatomy_vector=_anatomy_vector(result.next_anatomy),
        input_anatomy_digest=_anatomy_digest(pre),
        output_anatomy_digest=_anatomy_digest(result.next_anatomy),
        transfer_vector=(transfer.engagement, transfer.turnover, transfer.recovery),
        maximum_local_ledger_residual=result.maximum_local_ledger_residual,
        global_ledger_residual=result.global_ledger_residual,
    )


def _field_record(case_id: str, checkpoint: int, pre: DTS1ResourceAnatomy, result: DTS1CoupledFastFieldStepResult) -> DTS1S1IHFieldRecord:
    return DTS1S1IHFieldRecord(
        case_id=case_id,
        checkpoint=checkpoint,
        input_anatomy_digest=_anatomy_digest(pre),
        output_anatomy_digest=_anatomy_digest(result.anatomy),
        field_vector=_field_vector(result.field),
        adapter_rate=result.applied_adapter.edge_rates[0].rate_per_second,
        contrast=_contrast(result.field),
        maximum_local_ledger_residual=_maximum_local_residual(result.anatomy),
        global_ledger_residual=abs(result.anatomy.global_residual),
    )


def _near(value: float, expected: float) -> bool:
    return abs(value - expected) <= S1_IH_ROUNDOFF_FLOOR


def _run_c01(resource_counter: list[int], field_counter: list[int]):
    case_id = S1_IH_CASE_IDS[0]
    anatomy = _initial_anatomy(_initial_field(_INITIAL_H_MAIN))
    snapshots = []
    contacts = []
    fields = []
    for index in range(1, 4):
        snapshots.append(anatomy)
        resource_result = _resource_call(anatomy, 1.0, resource_counter)
        field_result = _field_call(anatomy, _INITIAL_H_MAIN, True, field_counter)
        contacts.append(_contact_record(case_id, index, anatomy, resource_result, 1.0))
        fields.append(_field_record(case_id, index, anatomy, field_result))
        anatomy = resource_result.next_anatomy
    engagements = tuple(item.transfer_vector[0] for item in contacts)
    adapters = tuple(item.adapter_rate for item in fields)
    contrasts = tuple(item.contrast for item in fields)
    metrics = (
        ("engagement_1", engagements[0]),
        ("engagement_2", engagements[1]),
        ("engagement_3", engagements[2]),
        ("adapter_1", adapters[0]),
        ("adapter_2", adapters[1]),
        ("adapter_3", adapters[2]),
        ("contrast_1", contrasts[0]),
        ("contrast_2", contrasts[1]),
        ("contrast_3", contrasts[2]),
        ("engagement_drop_1", engagements[0] - engagements[1]),
        ("engagement_drop_2", engagements[1] - engagements[2]),
        ("contrast_drop_1", contrasts[0] - contrasts[1]),
        ("contrast_drop_2", contrasts[1] - contrasts[2]),
    )
    checks = (
        ("all_expected_values_within_floor", all(_near(value, expected) for (_, value), (_, expected) in zip(metrics, S1_IH_EXPECTED, strict=True))),
        ("engagement_strictly_decreases", engagements[0] > engagements[1] > engagements[2]),
        ("contrast_strictly_decreases", contrasts[0] > contrasts[1] > contrasts[2]),
        ("both_engagement_drops_above_floor", min(metrics[9][1], metrics[10][1]) > S1_IH_ROUNDOFF_FLOOR),
        ("both_contrast_drops_above_floor", min(metrics[11][1], metrics[12][1]) > S1_IH_ROUNDOFF_FLOOR),
        ("all_ledgers_within_floor", all(max(item.maximum_local_ledger_residual, item.global_ledger_residual) <= S1_IH_ROUNDOFF_FLOOR for item in (*contacts, *fields))),
    )
    record = DTS1S1IHCaseRecord(case_id, tuple(contacts), tuple(fields), checks, 3, 3)
    return record, metrics, tuple(snapshots), tuple(contrasts)


def _run_n01(resource_counter: list[int], field_counter: list[int]) -> DTS1S1IHCaseRecord:
    case_id = S1_IH_CASE_IDS[1]
    anatomy = _initial_anatomy(_initial_field(_INITIAL_H_MAIN))
    first_resource = _resource_call(anatomy, 1.0, resource_counter)
    second_resource = _resource_call(anatomy, 1.0, resource_counter)
    first_field = _field_call(anatomy, _INITIAL_H_MAIN, True, field_counter)
    second_field = _field_call(anatomy, _INITIAL_H_MAIN, True, field_counter)
    contacts = (
        _contact_record(case_id, 1, anatomy, first_resource, 1.0),
        _contact_record(case_id, 2, anatomy, second_resource, 1.0),
    )
    fields = (
        _field_record(case_id, 1, anatomy, first_field),
        _field_record(case_id, 2, anatomy, second_field),
    )
    checks = (
        ("resource_payload_bit_exact", contacts[0].canonical_payload() | {"contact_index": 0} == contacts[1].canonical_payload() | {"contact_index": 0}),
        ("field_payload_bit_exact", fields[0].canonical_payload() | {"checkpoint": 0} == fields[1].canonical_payload() | {"checkpoint": 0}),
    )
    return DTS1S1IHCaseRecord(case_id, contacts, fields, checks, 2, 2)


def _run_n02(snapshots: tuple[DTS1ResourceAnatomy, ...], field_counter: list[int]) -> DTS1S1IHCaseRecord:
    case_id = S1_IH_CASE_IDS[2]
    fields = tuple(_field_record(case_id, index, anatomy, _field_call(anatomy, _INITIAL_H_MAIN, False, field_counter)) for index, anatomy in enumerate(snapshots, 1))
    checks = (
        ("all_complete_fields_bit_exact", fields[0].field_vector == fields[1].field_vector == fields[2].field_vector),
        ("all_adapters_are_base_rate", tuple(item.adapter_rate for item in fields) == (1.0, 1.0, 1.0)),
        ("all_neutral_contrasts_exact", fields[0].contrast == fields[1].contrast == fields[2].contrast),
    )
    return DTS1S1IHCaseRecord(case_id, (), fields, checks, 0, 3)


def _run_n03(initial: DTS1ResourceAnatomy, field_counter: list[int]) -> DTS1S1IHCaseRecord:
    case_id = S1_IH_CASE_IDS[3]
    fields = tuple(_field_record(case_id, index, initial, _field_call(initial, _INITIAL_H_MAIN, True, field_counter)) for index in range(1, 4))
    checks = (
        ("all_complete_fields_bit_exact", fields[0].field_vector == fields[1].field_vector == fields[2].field_vector),
        ("all_initial_adapters_exact", tuple(item.adapter_rate for item in fields) == (1.2, 1.2, 1.2)),
        ("all_initial_contrasts_exact", fields[0].contrast == fields[1].contrast == fields[2].contrast),
    )
    return DTS1S1IHCaseRecord(case_id, (), fields, checks, 0, 3)


def _run_n04(snapshots: tuple[DTS1ResourceAnatomy, ...], main_contrasts: tuple[float, ...], field_counter: list[int]) -> DTS1S1IHCaseRecord:
    case_id = S1_IH_CASE_IDS[4]
    fields = tuple(_field_record(case_id, index, anatomy, _field_call(anatomy, _INITIAL_H_ZERO, True, field_counter)) for index, anatomy in enumerate(snapshots, 1))
    contrasts = tuple(item.contrast for item in fields)
    checks = (
        ("zero_H_contrasts_match_main_within_floor", all(_near(value, expected) for value, expected in zip(contrasts, main_contrasts, strict=True))),
        ("zero_H_contrasts_strictly_decrease", contrasts[0] > contrasts[1] > contrasts[2]),
        ("zero_H_drops_above_floor", min(contrasts[0] - contrasts[1], contrasts[1] - contrasts[2]) > S1_IH_ROUNDOFF_FLOOR),
    )
    return DTS1S1IHCaseRecord(case_id, (), fields, checks, 0, 3)


def _run_n05(resource_counter: list[int]) -> DTS1S1IHCaseRecord:
    case_id = S1_IH_CASE_IDS[5]
    anatomy = _initial_anatomy(_initial_field(_INITIAL_H_MAIN))
    contacts = []
    for index in range(1, 4):
        result = _resource_call(anatomy, 0.0, resource_counter)
        contacts.append(_contact_record(case_id, index, anatomy, result, 0.0))
        anatomy = result.next_anatomy
    checks = (
        ("all_engagement_exact_zero", all(item.transfer_vector[0] == 0.0 for item in contacts)),
        ("all_ledgers_within_floor", all(max(item.maximum_local_ledger_residual, item.global_ledger_residual) <= S1_IH_ROUNDOFF_FLOOR for item in contacts)),
    )
    return DTS1S1IHCaseRecord(case_id, tuple(contacts), (), checks, 3, 0)


def _baseline_records() -> tuple[tuple[str, str], ...]:
    return tuple(
        (
            name,
            "ATTENUATION_ALONE_NOT_DISTINCT_NO_EXECUTION" if name == "dynamic-two-state-e1" else "STATE_SPACE_COUNTERPREDICTION_NO_EXECUTION",
        )
        for name, _ in S1_IF_BASELINE_COUNTERPREDICTIONS
    )


def _execute_once() -> _DTS1S1IHSingleAuditResult:
    resource_counter = [0]
    field_counter = [0]
    c01, metrics, snapshots, main_contrasts = _run_c01(resource_counter, field_counter)
    cases = (
        c01,
        _run_n01(resource_counter, field_counter),
        _run_n02(snapshots, field_counter),
        _run_n03(snapshots[0], field_counter),
        _run_n04(snapshots, main_contrasts, field_counter),
        _run_n05(resource_counter),
    )
    stopp = []
    if resource_counter[0] != S1_IH_SINGLE_DIRECT_RESOURCE_CALLS:
        stopp.append("direct-resource-call-count")
    if field_counter[0] != S1_IH_SINGLE_TECHNICAL_FIELD_CALLS:
        stopp.append("technical-field-call-count")
    for case in cases:
        stopp.extend(f"{case.case_id}:{name}" for name, passed in case.exact_checks if not passed)
    for (name, observed), (_, expected) in zip(metrics, S1_IH_EXPECTED, strict=True):
        if not _near(observed, expected):
            stopp.append(f"metric:{name}")
    baseline_records = _baseline_records()
    decision = S1_IH_PASS if not stopp else S1_IH_STOPP
    payload = {
        "case_records": [record.canonical_payload() for record in cases],
        "primary_metrics": [list(metric) for metric in metrics],
        "baseline_records": [list(record) for record in baseline_records],
        "direct_resource_calls": resource_counter[0],
        "technical_field_calls": field_counter[0],
        "research_field_steps": 0,
        "stopp_reasons": list(stopp),
        "decision": decision,
    }
    return _DTS1S1IHSingleAuditResult(
        case_records=cases,
        primary_metrics=metrics,
        baseline_records=baseline_records,
        direct_resource_calls=resource_counter[0],
        technical_field_calls=field_counter[0],
        research_field_steps=0,
        stopp_reasons=tuple(stopp),
        decision=decision,
        receipt_digest=_digest(payload),
    )


def execute_dts1_s1ih_preregistered_double_audit() -> DTS1S1IHDoubleAuditResult:
    """Execute the complete preregistered double audit exactly once per call."""

    first = _execute_once()
    repeat = _execute_once()
    identical = first.receipt_digest == repeat.receipt_digest
    stopp = list(first.stopp_reasons)
    stopp.extend(reason for reason in repeat.stopp_reasons if reason not in stopp)
    if not identical:
        stopp.append("repeat-receipt-mismatch")
    decision = S1_IH_PASS if not stopp and identical else S1_IH_STOPP
    direct_resource_calls = first.direct_resource_calls + repeat.direct_resource_calls
    technical_field_calls = first.technical_field_calls + repeat.technical_field_calls
    payload = {
        "audit_id": S1_IH_AUDIT_ID,
        "source_s1ig_contract_digest": S1_IH_SOURCE_S1IG_CONTRACT_DIGEST,
        "case_records": [record.canonical_payload() for record in first.case_records],
        "primary_metrics": [list(metric) for metric in first.primary_metrics],
        "roundoff_floor": S1_IH_ROUNDOFF_FLOOR,
        "baseline_records": [list(record) for record in first.baseline_records],
        "first_receipt_digest": first.receipt_digest,
        "repeat_receipt_digest": repeat.receipt_digest,
        "repeated_receipts_identical": identical,
        "direct_resource_calls": direct_resource_calls,
        "technical_field_calls": technical_field_calls,
        "research_field_steps": 0,
        "stopp_reasons": list(stopp),
        "decision": decision,
    }
    return DTS1S1IHDoubleAuditResult(
        audit_id=S1_IH_AUDIT_ID,
        source_s1ig_contract_digest=S1_IH_SOURCE_S1IG_CONTRACT_DIGEST,
        case_records=first.case_records,
        primary_metrics=first.primary_metrics,
        roundoff_floor=S1_IH_ROUNDOFF_FLOOR,
        baseline_records=first.baseline_records,
        first_receipt_digest=first.receipt_digest,
        repeat_receipt_digest=repeat.receipt_digest,
        repeated_receipts_identical=identical,
        direct_resource_calls=direct_resource_calls,
        technical_field_calls=technical_field_calls,
        research_field_steps=0,
        stopp_reasons=tuple(stopp),
        decision=decision,
        audit_receipt_digest=_digest(payload),
    )
